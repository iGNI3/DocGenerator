#Pydantic models for the agent pipeline — request, response, and intermediate stages.

from typing import Literal, Optional

from pydantic import BaseModel, Field


# Request / Response — API boundary
class AgentRequest(BaseModel):
    """Incoming user request."""

    request: str = Field(
        ...,
        min_length=5,
        description="Natural-language description of the document to generate.",
        examples=["Create a project plan for launching a mobile banking app."],
    )


class AgentResponse(BaseModel):
    """Final API response returned to the caller."""

    plan: "Plan"
    reflection_notes: list[str]
    summary: str
    document_url: str



# Planning stage
class TaskStep(BaseModel):
    """A single step in the agent's task list."""

    step: str
    description: str


class SectionOutline(BaseModel):
    """High-level outline entry for one document section."""

    heading: str
    purpose: str


class Plan(BaseModel):
    """Output of the planning stage (LLM call #1)."""

    doc_type: str = Field(description="Type of document, e.g. 'Project Plan'.")
    title: str = Field(description="Document title.")
    assumptions: list[str] = Field(
        default_factory=list,
        description="Assumptions the agent made due to missing info.",
    )
    task_list: list[TaskStep] = Field(
        default_factory=list,
        description="Steps the agent will take to produce the document.",
    )
    sections: list[SectionOutline] = Field(
        default_factory=list,
        description="Ordered section outline for the document.",
    )



# Writing stage
class SectionContent(BaseModel):
    """Full content for a single document section (LLM call #2 output)."""

    heading: str
    content: str = Field(description="Paragraph / bullet text for this section.")
    table: Optional[list[list[str]]] = Field(
        default=None,
        description="Optional tabular data — first row is headers.",
    )



# Reflection stage
class ReflectionResult(BaseModel):
    """Output of the self-check / reflection stage (LLM call #3)."""

    status: Literal["pass", "revise"]
    notes: list[str] = Field(
        default_factory=list,
        description="Feedback notes — empty on 'pass', actionable on 'revise'.",
    )


# Rebuild forward refs so AgentResponse can reference Plan.
AgentResponse.model_rebuild()
