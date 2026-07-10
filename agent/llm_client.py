#LLM client for agents that handles retries, model fallback, and JSON parsing.



import json
import logging
import os
import re
import time
from typing import Any

import httpx
from openai import OpenAI

from agent.providers import ProviderConfig, ProviderType, detect_provider

logger = logging.getLogger(__name__)


# Configuration
MAX_RETRIES = 3
BACKOFF_BASE_SECONDS = 1.5

# Client factories (cached per provider)
_openai_clients: dict[str, OpenAI] = {}


def _get_openai_client(config: ProviderConfig) -> OpenAI:
    """Return a cached OpenAI-compatible client for the given provider."""
    cache_key = config.name
    if cache_key not in _openai_clients:
        api_key = os.getenv(config.api_key_env)
        if not api_key:
            raise RuntimeError(f"{config.api_key_env} is not set.")
        _openai_clients[cache_key] = OpenAI(
            api_key=api_key,
            base_url=config.base_url,
        )
    return _openai_clients[cache_key]


# Response cleaning
# Matches fences at the start/end of the whole response

_CODE_FENCE_FULL_RE = re.compile(
    r"^```(?:json)?\s*\n?(.*?)```\s*$",
    re.DOTALL,
)
# Matches fences anywhere (e.g. prose before the fence)
_CODE_FENCE_ANYWHERE_RE = re.compile(
    r"```(?:json)?\s*\n?(.*?)```",
    re.DOTALL,
)


def strip_code_fences(text: str) -> str:
    """Remove markdown code fences wrapping JSON output.

    Handles both clean fence-only responses and responses with prose
    before the fenced block.
    """
    text = text.strip()
    # Try full-match first (cleanest case)
    match = _CODE_FENCE_FULL_RE.match(text)
    if match:
        return match.group(1).strip()
    # Try extracting from anywhere in the response
    match = _CODE_FENCE_ANYWHERE_RE.search(text)
    if match:
        return match.group(1).strip()
    return text

# Provider-specific call implementations
def _call_openai_compatible(
    config: ProviderConfig,
    model: str,
    system_prompt: str,
    user_prompt: str,
    temperature: float,
    max_tokens: int,
) -> str:
    """Send a chat completion via the OpenAI-compatible API."""
    client = _get_openai_client(config)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content


def _call_anthropic(
    config: ProviderConfig,
    model: str,
    system_prompt: str,
    user_prompt: str,
    temperature: float,
    max_tokens: int,
) -> str:
    """Send a message via the Anthropic Messages API (native httpx)."""
    api_key = os.getenv(config.api_key_env)
    if not api_key:
        raise RuntimeError(f"{config.api_key_env} is not set.")

    response = httpx.post(
        f"{config.base_url}/v1/messages",
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_prompt}],
        },
        timeout=60.0,
    )
    response.raise_for_status()
    data = response.json()
    # Anthropic returns content as a list of blocks
    return "".join(
        block["text"] for block in data["content"] if block["type"] == "text"
    )


# Dispatch table — maps ProviderType to its call implementation
_CALL_DISPATCH = {
    ProviderType.OPENAI_COMPATIBLE: _call_openai_compatible,
    ProviderType.ANTHROPIC: _call_anthropic,
}


# Core call with retry + model fallback
def call_llm(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.4,
    max_tokens: int = 4096,
) -> str:
    """Send a chat completion with retry, backoff, and model fallback.

    Auto-detects the provider from the environment (or uses the
    ``LLM_PROVIDER`` override).  Tries the primary model first, then
    falls back to the provider's secondary model if all retries fail.

    Returns:
        Raw text content from the assistant message.

    Raises:
        RuntimeError: If all attempts are exhausted.
    """
    config = detect_provider()
    call_fn = _CALL_DISPATCH.get(config.provider_type)
    if call_fn is None:
        # Fall back to OpenAI-compatible for unknown types
        call_fn = _call_openai_compatible

    models_to_try = [config.default_model]
    if config.fallback_model:
        models_to_try.append(config.fallback_model)

    # Allow env-var model override
    model_override = os.getenv("LLM_MODEL")
    if model_override:
        models_to_try = [model_override]

    last_error: Exception | None = None

    for model in models_to_try:
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                logger.info(
                    "LLM call → provider=%s  model=%s  attempt=%d/%d",
                    config.name,
                    model,
                    attempt,
                    MAX_RETRIES,
                )
                content = call_fn(
                    config, model, system_prompt, user_prompt,
                    temperature, max_tokens,
                )
                logger.info("LLM responded (%d chars)", len(content))
                return content

            except Exception as exc:
                last_error = exc
                is_rate_limit = any(
                    k in str(exc).lower() or k in type(exc).__name__.lower()
                    for k in ("429", "rate", "quota", "resource_exhausted", "resourcelimit")
                )
                wait = BACKOFF_BASE_SECONDS * (2 ** (attempt - 1))
                if is_rate_limit:
                    match = re.search(r"retry(?:ing)? in (\d+(?:\.\d+)?)s", str(exc), re.IGNORECASE)
                    if not match:
                        match = re.search(r"retryDelay: '(\d+)s'", str(exc), re.IGNORECASE)
                    if match:
                        wait = float(match.group(1)) + 1.5  # Add safety buffer
                    else:
                        wait = 60.0
                logger.warning(
                    "LLM call failed (provider=%s model=%s attempt=%d): %s "
                    "— retrying in %.1fs",
                    config.name,
                    model,
                    attempt,
                    exc,
                    wait,
                )
                time.sleep(wait)

        logger.warning("Retries exhausted for model=%s, trying fallback.", model)

    raise RuntimeError(
        f"All LLM attempts failed ({config.name}). Last error: {last_error}"
    ) from last_error


# JSON-specific helper
def call_llm_json(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.3,
    max_tokens: int = 4096,
) -> dict[str, Any] | list[Any]:
    """Call the LLM and parse the response as JSON.

    Strips code fences automatically.  On parse failure, sends one
    corrective re-prompt before raising.
    """
    raw = call_llm(system_prompt, user_prompt, temperature, max_tokens)
    cleaned = strip_code_fences(raw)

    try:
        return json.loads(cleaned, strict=False)
    except json.JSONDecodeError as exc:
        logger.warning("Initial JSON parse failed — sending corrective re-prompt. Error: %s", exc)

    # Corrective re-prompt
    correction_prompt = (
        "Your previous response was not valid JSON.  Return ONLY valid JSON "
        "with no markdown fences, no commentary, and no trailing text.  "
        "Here is the content to re-format:\n\n" + raw
    )
    raw_retry = call_llm(system_prompt, correction_prompt, temperature=0.1, max_tokens=max_tokens)
    cleaned_retry = strip_code_fences(raw_retry)

    try:
        return json.loads(cleaned_retry, strict=False)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"LLM did not return valid JSON after corrective re-prompt.  "
            f"Raw output:\n{raw_retry[:500]}"
        ) from exc
