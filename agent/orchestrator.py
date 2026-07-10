#Agent Orchestrator to wire the pipeline stages together: validate → plan → write → reflect (→ revise?) → render

import asyncio
import logging
from pathlib import Path
from typing import Any, Callable

from agent.models import AgentResponse, Plan, ReflectionResult, SectionContent
from agent.planner import plan_request
from agent.reflector import self_check
from agent.renderer import render_docx
from agent.writer import generate_content

logger = logging.getLogger(__name__)

# Tool Registry
#Each tool is a named callable in the pipeline.  This registry exists so


ToolFn = Callable[..., Any]

TOOLS: dict[str, ToolFn] = {
    "plan": plan_request,
    "write": generate_content,
    "reflect": self_check,
    "render": render_docx,
}

# Ordered execution stages
PIPELINE_STAGES = ["plan", "write", "reflect", "render"]


# Pipeline runner

def _execute_pipeline(request: str, outputs_dir: Path) -> AgentResponse:
    """Synchronous pipeline execution (runs in a thread).

    Steps:
        1. **Plan** — analyse the request, produce a structured Plan.
        2. **Write** — generate full section content from the plan.
        3. **Reflect** — self-check the draft against the original request.
           If "revise", re-run the writer once.  Capped at one revision.
        4. **Render** — deterministic python-docx formatting.
    """
    logger.info("=" * 60)
    logger.info("PIPELINE START")
    logger.info("=" * 60)

    #Stage 1: Plan
    logger.info("Stage 1/4 -> PLAN")
    plan: Plan = TOOLS["plan"](request)

    _log_plan(plan)

    #Stage 2: Write
    logger.info("Stage 2/4 -> WRITE")
    sections: list[SectionContent] = TOOLS["write"](plan)

    #Stage 3: Reflect 
    logger.info("Stage 3/4 -> REFLECT")
    reflection: ReflectionResult = TOOLS["reflect"](request, sections)

    #One-shot revision if needed
    if reflection.status == "revise":
        logger.info("Reflection says REVISE -- running one corrective pass ...")
        sections = TOOLS["write"](plan, revision_notes=reflection.notes)
        logger.info("Corrective pass complete.")
    else:
        logger.info("Reflection says PASS -- no revision needed.")

    #Stage 4: Render
    logger.info("Stage 4/4 -> RENDER")
    filename: str = TOOLS["render"](plan, sections, outputs_dir)
    document_url = f"/documents/{filename}"

    #Build response
    summary = (
        f"Generated a {plan.doc_type} titled \"{plan.title}\" "
        f"with {len(sections)} sections.  "
        f"Reflection status: {reflection.status}."
    )

    logger.info("=" * 60)
    logger.info("PIPELINE COMPLETE -> %s", document_url)
    logger.info("=" * 60)

    return AgentResponse(
        plan=plan,
        reflection_notes=reflection.notes,
        summary=summary,
        document_url=document_url,
    )


async def run_agent_pipeline(
    request: str,
    outputs_dir: Path,
) -> AgentResponse:
    """Async entry point — delegates to a thread so sync LLM calls
    don't block the FastAPI event loop."""
    return await asyncio.to_thread(_execute_pipeline, request, outputs_dir)


#Logging helpers
def _log_plan(plan: Plan) -> None:
    """Pretty-print the plan to the console for demo visibility."""
    logger.info("─── PLAN ───")
    logger.info("  Doc Type   : %s", plan.doc_type)
    logger.info("  Title      : %s", plan.title)
    logger.info("  Assumptions: %d", len(plan.assumptions))
    for a in plan.assumptions:
        logger.info("    • %s", a)
    logger.info("  Task List  : %d steps", len(plan.task_list))
    for t in plan.task_list:
        logger.info("    %s — %s", t.step, t.description)
    logger.info("  Sections   : %d", len(plan.sections))
    for s in plan.sections:
        logger.info("    § %s", s.heading)
    logger.info("─── END PLAN ───")
