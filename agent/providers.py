# Provider configs and auto-detection logic


import logging
import os
from dataclasses import dataclass
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


# Provider type enum
class ProviderType(str, Enum):
    """Identifies how the provider's API should be called."""

    OPENAI_COMPATIBLE = "openai_compatible"
    ANTHROPIC = "anthropic"


# Provider configuration
@dataclass(frozen=True)
class ProviderConfig:
    """Immutable configuration for a single LLM provider."""

    name: str
    provider_type: ProviderType
    api_key_env: str
    base_url: str
    default_model: str
    fallback_model: Optional[str] = None


# Registry to add new providers here
PROVIDER_REGISTRY: dict[str, ProviderConfig] = {
    "groq": ProviderConfig(
        name="Groq",
        provider_type=ProviderType.OPENAI_COMPATIBLE,
        api_key_env="GROQ_API_KEY",
        base_url="https://api.groq.com/openai/v1",
        default_model="llama-3.3-70b-versatile",
        fallback_model="llama-3.1-8b-instant",
    ),
    "openai": ProviderConfig(
        name="OpenAI",
        provider_type=ProviderType.OPENAI_COMPATIBLE,
        api_key_env="OPENAI_API_KEY",
        base_url="https://api.openai.com/v1",
        default_model="gpt-4o",
        fallback_model="gpt-4o-mini",
    ),
    "google": ProviderConfig(
        name="Google Gemini",
        provider_type=ProviderType.OPENAI_COMPATIBLE,
        api_key_env="GOOGLE_API_KEY",
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        default_model="gemini-3.1-flash-lite",
        fallback_model=None,
    ),
    "anthropic": ProviderConfig(
        name="Anthropic",
        provider_type=ProviderType.ANTHROPIC,
        api_key_env="ANTHROPIC_API_KEY",
        base_url="https://api.anthropic.com",
        default_model="claude-sonnet-4-20250514",
        fallback_model="claude-haiku-3-5-20241022",
    ),
    "openrouter": ProviderConfig(
        name="OpenRouter",
        provider_type=ProviderType.OPENAI_COMPATIBLE,
        api_key_env="OPENROUTER_API_KEY",
        base_url="https://openrouter.ai/api/v1",
        default_model="meta-llama/llama-3.3-70b-instruct",
        fallback_model="meta-llama/llama-3.1-8b-instruct",
    ),
    "deepinfra": ProviderConfig(
        name="DeepInfra",
        provider_type=ProviderType.OPENAI_COMPATIBLE,
        api_key_env="DEEPINFRA_API_KEY",
        base_url="https://api.deepinfra.com/v1/openai",
        default_model="meta-llama/Llama-3.3-70B-Instruct",
        fallback_model="meta-llama/Llama-3.1-8B-Instruct",
    ),
}

# Auto-detection priority (checked in order)
_DETECTION_ORDER = ["groq", "openai", "google", "anthropic", "openrouter", "deepinfra"]


# Detection
def detect_provider() -> ProviderConfig:
    """Resolve the active LLM provider.

    Resolution order:
        1. Explicit ``LLM_PROVIDER`` env var (e.g. ``LLM_PROVIDER=google``).
        2. First provider whose API key is found in the environment.

    Raises:
        RuntimeError: If no provider can be resolved.
    """
    # 1. Explicit override
    explicit = os.getenv("LLM_PROVIDER", "").lower().strip()
    if explicit:
        if explicit not in PROVIDER_REGISTRY:
            available = ", ".join(PROVIDER_REGISTRY.keys())
            raise RuntimeError(
                f"Unknown LLM_PROVIDER='{explicit}'. Choose from: {available}"
            )
        config = PROVIDER_REGISTRY[explicit]
        api_key = os.getenv(config.api_key_env)
        if not api_key:
            raise RuntimeError(
                f"LLM_PROVIDER={explicit} but {config.api_key_env} is not set."
            )
        logger.info("Using explicitly configured provider: %s", config.name)
        return config

    # 2. Auto-detect from environment
    for key in _DETECTION_ORDER:
        config = PROVIDER_REGISTRY[key]
        if os.getenv(config.api_key_env):
            logger.info("Auto-detected provider: %s (via %s)", config.name, config.api_key_env)
            return config

    # 3. Nothing found
    key_list = ", ".join(
        f"{c.api_key_env} ({c.name})" for c in PROVIDER_REGISTRY.values()
    )
    raise RuntimeError(f"No LLM API key found. Set one of: {key_list}")
