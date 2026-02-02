"""Pydantic models and enums for PM file parsing.

All entity models, enums, and the ParseResult/ParseWarning infrastructure
used by the parser module. No parsing logic lives here.
"""

from enum import Enum
from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ParseWarning(BaseModel):
    """A non-fatal issue encountered during parsing."""

    file: str
    location: str  # line number, field name, row index, etc.
    message: str


class ParseResult(BaseModel, Generic[T]):
    """Result of a parse operation: data + accumulated warnings."""

    data: T
    warnings: list[ParseWarning] = Field(default_factory=list)


# --- Enums ---


class EpicStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"


class WorkItemStatus(str, Enum):
    BACKLOG = "backlog"
    ACTIVE = "active"
    PAUSED = "paused"
    ABANDONED = "abandoned"
    FAILED = "failed"
    COMPLETED = "completed"


class WorkItemScale(str, Enum):
    TRIVIAL = "trivial"
    STANDARD = "standard"


class Priority(str, Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"


class InsightStatus(str, Enum):
    CAPTURED = "captured"
    ADDRESSED = "addressed"
    SUPERSEDED = "superseded"


class DecisionStatus(str, Enum):
    ACTIVE = "active"
    REVISED = "revised"
    SUPERSEDED = "superseded"


class VerificationType(str, Enum):
    REASONABLENESS = "reasonableness"
    BASELINE = "baseline"
    PHYSICAL = "physical"
    RELATIONSHIP = "relationship"
    ROLLUP = "rollup"


class VerificationMechanism(str, Enum):
    MODEL = "model"
    TEST = "test"
    MANUAL = "manual"


class VerificationStatus(str, Enum):
    PASSING = "passing"
    FAILING = "failing"
    PENDING = "pending"


# --- Entity models ---


class WorkItemEntry(BaseModel):
    id: str  # WI-XXX
    name: str
    scale: WorkItemScale
    status: WorkItemStatus
    completed: str | None = None  # YYYY-MM-DD or None


class EpicEntry(BaseModel):
    name: str
    goal: str | None = None  # G-XXX or None
    priority: Priority
    status: EpicStatus
    file: str  # relative path
    items: list[WorkItemEntry] = Field(default_factory=list)


class StandaloneEntry(BaseModel):
    id: str  # WI-XXX
    name: str
    scale: WorkItemScale
    priority: Priority
    status: WorkItemStatus
    completed: str | None = None


class BacklogData(BaseModel):
    epics: list[EpicEntry] = Field(default_factory=list)
    standalone: list[StandaloneEntry] = Field(default_factory=list)


class RequirementEntry(BaseModel):
    id: str  # PR-XXX
    requirement: str
    source: str
    enforcement: str
    validation_method: str


class ValidationEntry(BaseModel):
    id: str  # SV-XXX
    description: str
    type: VerificationType
    mechanism: VerificationMechanism
    expected: str
    tolerance: str
    source: str
    test: str
    status: VerificationStatus


class InsightEntry(BaseModel):
    id: str  # DI-XXX
    title: str
    source: str
    rationale: str | None = None
    context: str
    model_implications: str
    analysis_implications: str
    status: InsightStatus
    superseded_by: str | None = None
    supersedes: str | None = None


class DecisionEntry(BaseModel):
    id: str  # AD-XXX
    title: str
    decision: str
    rationale: str
    date: str
    status: DecisionStatus


class GoalEntry(BaseModel):
    id: str  # G-XXX
    goal: str
    priority: str
    status: str
    source: str
    traced_requirements: str


class AnalysisQuestionEntry(BaseModel):
    id: str  # AQ-XXX
    question: str
    implies: str
    source: str
    status: str


class OverviewData(BaseModel):
    goals: list[GoalEntry] = Field(default_factory=list)
    questions: list[AnalysisQuestionEntry] = Field(default_factory=list)


class TraceabilityEntry(BaseModel):
    element: str
    file: str
    type: str
    knowledge: list[str] = Field(default_factory=list)
    requirement: list[str] = Field(default_factory=list)
    source_type: str
    source_document: str
    source_location: str
    confidence: str
    assumptions: str
    last_verified: str
