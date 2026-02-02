"""Project Management file parsers and state derivation.

Provides typed, validated access to structured project files:
BACKLOG.md, REQUIREMENTS.md, VALIDATION_MATRIX.md, KNOWLEDGE.md,
ARCHITECTURE.md, OVERVIEW.md, and traceability_matrix.csv.

Also provides state derivation: deterministic work item state,
stage detection, epic state derivation, and WI-XXX name resolution.
"""

from agentic_mbse.pm.dashboard import generate_dashboard
from agentic_mbse.pm.parser import (
    parse_architecture,
    parse_backlog,
    parse_frontmatter,
    parse_knowledge,
    parse_overview,
    parse_requirements,
    parse_traceability,
    parse_validation_matrix,
)
from agentic_mbse.pm.state import (
    derive_project_state,
    resolve_work_item,
)
from agentic_mbse.pm.types import (
    AnalysisQuestionEntry,
    BacklogData,
    DashboardResult,
    DecisionEntry,
    DecisionStatus,
    DerivedEpicState,
    DerivedWorkItemState,
    EpicEntry,
    EpicStatus,
    GoalEntry,
    InsightEntry,
    InsightStatus,
    OverviewData,
    ParseResult,
    ParseWarning,
    Priority,
    ProjectState,
    RequirementEntry,
    StandaloneEntry,
    TraceabilityEntry,
    ValidationEntry,
    VerificationMechanism,
    VerificationStatus,
    VerificationType,
    WorkItemEntry,
    WorkItemScale,
    WorkItemStage,
    WorkItemStatus,
)

__all__ = [
    # Infrastructure
    "ParseWarning",
    "ParseResult",
    "DashboardResult",
    # Enums
    "EpicStatus",
    "WorkItemStatus",
    "WorkItemScale",
    "WorkItemStage",
    "Priority",
    "InsightStatus",
    "DecisionStatus",
    "VerificationType",
    "VerificationMechanism",
    "VerificationStatus",
    # Entity models
    "WorkItemEntry",
    "EpicEntry",
    "StandaloneEntry",
    "BacklogData",
    "RequirementEntry",
    "ValidationEntry",
    "InsightEntry",
    "DecisionEntry",
    "GoalEntry",
    "AnalysisQuestionEntry",
    "OverviewData",
    "TraceabilityEntry",
    # State derivation models
    "DerivedWorkItemState",
    "DerivedEpicState",
    "ProjectState",
    # Parsers
    "parse_frontmatter",
    "parse_backlog",
    "parse_requirements",
    "parse_validation_matrix",
    "parse_knowledge",
    "parse_architecture",
    "parse_overview",
    "parse_traceability",
    # State derivation functions
    "derive_project_state",
    "resolve_work_item",
    # Dashboard
    "generate_dashboard",
]
