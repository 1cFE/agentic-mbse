"""Project Management file parsers, state derivation, and operations.

Provides typed, validated access to structured project files:
BACKLOG.md, REQUIREMENTS.md, VALIDATION_MATRIX.md, KNOWLEDGE.md,
ARCHITECTURE.md, OVERVIEW.md, and traceability_matrix.csv.

Also provides state derivation: deterministic work item state,
stage detection, epic state derivation, and WI-XXX name resolution.

Operations (D4.4): deterministic mutation functions for all structured
project files. Each operation validates inputs, computes changes in
memory, and writes atomically.
"""

from agentic_mbse.pm.dashboard import generate_dashboard
from agentic_mbse.pm.operations import (
    add_epic,
    add_insight,
    add_item,
    add_validation,
    approve_research,
    close_item,
    get_status,
    impact_query,
    promote_requirement,
    register_decision,
    register_intent,
    save_research,
    supersede_insight,
    trace_element,
    update_validation,
)
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
    GoalInput,
    ImpactResult,
    InsightEntry,
    InsightInput,
    InsightStatus,
    OperationResult,
    OverviewData,
    ParseResult,
    ParseWarning,
    Priority,
    ProjectState,
    QuestionInput,
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
    "OperationResult",
    "ImpactResult",
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
    # Operation input types
    "InsightInput",
    "GoalInput",
    "QuestionInput",
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
    # Operations
    "add_epic",
    "add_insight",
    "save_research",
    "approve_research",
    "promote_requirement",
    "register_decision",
    "add_validation",
    "trace_element",
    "impact_query",
    "register_intent",
    "add_item",
    "close_item",
    "update_validation",
    "get_status",
    "supersede_insight",
]
