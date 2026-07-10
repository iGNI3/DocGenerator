# Reflector to review drafted content against the original request and returns pass/revise.

import logging

from agent.llm_client import call_llm_json
from agent.models import ReflectionResult, SectionContent

logger = logging.getLogger(__name__)

# System prompt
REFLECTOR_SYSTEM_PROMPT = """\
You are a quality-assurance reviewer for an autonomous document-generation
agent.  You will receive:

1. The original user request.
2. The drafted document content (section headings + text).

Evaluate whether the draft:
- Fully addresses the user request (no dropped requirements).
- Makes reasonable assumptions (not fabricating false precision).
- Has professional tone and logical flow.
- Includes appropriate detail for the document type.

Respond with ONLY valid JSON — no markdown fences, no prose:

{
  "status": "pass" | "revise",
  "notes": [
    "<actionable feedback string>",
    ...
  ]
}

Use "pass" if the draft is adequate.  Use "revise" if there are concrete,
fixable gaps — and make each note specific and actionable.
"""


def self_check(
    request: str,
    sections: list[SectionContent],
) -> ReflectionResult:
    """Review drafted content against the original user request.

    Args:
        request: The original natural-language request.
        sections: The drafted section content to review.

    Returns:
        A ReflectionResult with pass/revise status and notes.
    """
    # Build a readable summary of the draft for the reviewer
    draft_summary = "\n\n".join(
        f"## {s.heading}\n{s.content}" for s in sections
    )

    user_prompt = (
        f"Original user request:\n\"{request}\"\n\n"
        f"Drafted document content:\n\n{draft_summary}"
    )

    logger.info("Running reflection / self-check …")

    data = call_llm_json(
        system_prompt=REFLECTOR_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        temperature=0.2,
        max_tokens=1024,
    )

    try:
        result = ReflectionResult.model_validate(data)
    except Exception as exc:
        logger.warning(
            "Reflection validation failed (%s) — defaulting to 'pass'.",
            exc,
        )
        result = ReflectionResult(status="pass", notes=[str(exc)])

    logger.info(
        "Reflection result: status=%s, notes=%d",
        result.status,
        len(result.notes),
    )
    for note in result.notes:
        logger.info("  → %s", note)

    return result
