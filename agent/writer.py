# Writer using LLM.
# Takes the plan's section outline and generates full content for all
# sections in one shot. Returns SectionContent objects with text + optional tables.

import json
import logging

from agent.llm_client import call_llm_json
from agent.models import Plan, SectionContent

logger = logging.getLogger(__name__)

# System prompt
WRITER_SYSTEM_PROMPT = """\
You are a professional business writer.  You will receive a document plan
containing a title, document type, assumptions, and section outline.

For each section in the outline, produce concise, high-quality, professional content that includes:
- **content**: 1–2 paragraphs of dense, well-written prose.  Use bullet points
  (prefixed with "• ") where a list is more natural than prose. Keep the overall text concise.
- **table** (optional): if the section benefits from tabular data (e.g.
  timelines, role matrices, risk registers, budgets), include a
  `"table"` field — a list of lists where the first sub-list is headers.
  If not appropriate for the section, omit the field or set it to null.

Where the original request lacks specific data, use realistic illustrative
figures and clearly mark them as *"[Illustrative]"* or *"[Assumed]"*.

Respond with ONLY valid JSON — no markdown fences, no prose.  The JSON
must be an array matching this schema:

[
  {
    "heading": "<section heading from the outline>",
    "content": "<full paragraph / bullet text>",
    "table": [["Header1", "Header2"], ["row1col1", "row1col2"]] | null
  },
  ...
]

Produce content for ALL sections in the outline, in the same order.
"""


def _build_user_prompt(plan: Plan, extra_instructions: str | None = None) -> str:
    """Format the plan into a user prompt for the writer LLM call."""
    outline = json.dumps(
        {
            "doc_type": plan.doc_type,
            "title": plan.title,
            "assumptions": plan.assumptions,
            "sections": [s.model_dump() for s in plan.sections],
        },
        indent=2,
    )
    prompt = f"Document plan:\n\n{outline}"
    if extra_instructions:
        prompt += f"\n\nAdditional instructions from the reviewer:\n{extra_instructions}"
    return prompt


def generate_content(
    plan: Plan,
    revision_notes: list[str] | None = None,
) -> list[SectionContent]:
    """Generate full content for every section in the plan.

    Args:
        plan: The document plan from the planner stage.
        revision_notes: Optional feedback from the reflector to incorporate.

    Returns:
        Ordered list of SectionContent, one per section in the plan.
    """
    extra = "\n".join(f"- {n}" for n in revision_notes) if revision_notes else None
    logger.info("Generating content for %d sections", len(plan.sections))

    data = call_llm_json(
        system_prompt=WRITER_SYSTEM_PROMPT,
        user_prompt=_build_user_prompt(plan, extra),
        temperature=0.4,
        max_tokens=6000,
    )

    # The LLM should return a list; handle if it wraps it in a key.
    if isinstance(data, dict):
        data = data.get("sections", data.get("content", []))

    if not isinstance(data, list):
        raise ValueError(f"Expected a JSON array from writer, got {type(data).__name__}.")

    sections: list[SectionContent] = []
    for idx, item in enumerate(data):
        try:
            sections.append(SectionContent.model_validate(item))
        except Exception as exc:
            logger.warning("Section %d validation failed, skipping: %s", idx, exc)

    logger.info("Generated content for %d / %d sections", len(sections), len(plan.sections))
    return sections
