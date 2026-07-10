# Planner to analyses user's request and returns a structured Plan (doc type, title, assumptions, task list, section outline).

import json
import logging

from agent.llm_client import call_llm_json
from agent.models import Plan

logger = logging.getLogger(__name__)

# System prompt — forces JSON-only output matching the Plan schema
PLANNER_SYSTEM_PROMPT = """\
You are an autonomous document-generation agent.  Given a user request,
decide:

1. **doc_type** — what type of business document best satisfies it
   (e.g. "Project Plan", "Business Report", "Status Update Memo",
   "Proposal", "Strategy Brief").
2. **title** — a professional title for the document.
3. **assumptions** — any assumptions you must make because the request
   is vague, missing data, or ambiguous.  Be explicit.
4. **task_list** — the concrete steps you (the agent) will take to
   produce this document.  Each entry has a short "step" label and a
   "description".
5. **sections** — an ordered outline of the document's sections.  Each
   entry has a "heading" and a short "purpose". Limit the sections to a concise and professional structure, between 4 to 8 sections (do NOT exceed 8 sections).

Respond with ONLY valid JSON — no markdown fences, no prose before or
after.  The JSON must match this schema exactly:

{
  "doc_type": "<string>",
  "title": "<string>",
  "assumptions": ["<string>", ...],
  "task_list": [{"step": "<string>", "description": "<string>"}, ...],
  "sections": [{"heading": "<string>", "purpose": "<string>"}, ...]
}
"""


def plan_request(request: str) -> Plan:
    """Generate a structured plan from a natural-language request.

    Args:
        request: The raw user request text.

    Returns:
        A validated Plan model.

    Raises:
        ValueError: If the LLM output cannot be parsed into a valid Plan.
    """
    logger.info("Planning document for request: %s", request[:80])

    data = call_llm_json(
        system_prompt=PLANNER_SYSTEM_PROMPT,
        user_prompt=request,
        temperature=0.3,
    )

    try:
        plan = Plan.model_validate(data)
    except Exception as exc:
        logger.error("Plan validation failed: %s\nRaw data: %s", exc, json.dumps(data, indent=2)[:500])
        raise ValueError(f"LLM returned data that does not match the Plan schema: {exc}") from exc

    logger.info(
        "Plan created — type=%s, title=%s, sections=%d, assumptions=%d",
        plan.doc_type,
        plan.title,
        len(plan.sections),
        len(plan.assumptions),
    )
    return plan
