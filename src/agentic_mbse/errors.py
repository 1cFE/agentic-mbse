"""Error classes for agentic-mbse."""

from enum import Enum

SEMANTIC_EVIDENCE_API_VERSION = "semantic-evidence/v2"

__all__ = [
    "AgenticMBSEError",
    "ModelLoadError",
    "ValidationError",
    "ConfigurationError",
    "AdapterError",
    "SEMANTIC_EVIDENCE_API_VERSION",
    "SemanticEvidenceCode",
    "SemanticEvidenceError",
]


class AgenticMBSEError(Exception):
    """Base error for agentic-mbse package."""

    pass


class SemanticEvidenceCode(str, Enum):
    """Closed failure vocabulary for incomplete parser evidence."""

    METATYPE_CHECK_FAILED = "METATYPE_CHECK_FAILED"
    EXPRESSION_KIND_UNSUPPORTED = "EXPRESSION_KIND_UNSUPPORTED"
    OPERAND_ITERATION_FAILED = "OPERAND_ITERATION_FAILED"
    EXPRESSION_DEPTH_EXHAUSTED = "EXPRESSION_DEPTH_EXHAUSTED"
    RESOLVED_TARGET_MISSING = "RESOLVED_TARGET_MISSING"
    DOCUMENT_TIER_MISSING = "DOCUMENT_TIER_MISSING"
    DOCUMENT_TIER_UNKNOWN = "DOCUMENT_TIER_UNKNOWN"
    RESOLVED_LEAF_MISSING = "RESOLVED_LEAF_MISSING"
    INDEXED_REFERENCE_UNSUPPORTED = "INDEXED_REFERENCE_UNSUPPORTED"


class SemanticEvidenceError(AgenticMBSEError):
    """A named failure to obtain exact semantic evidence from SysIDE."""

    def __init__(
        self,
        code: SemanticEvidenceCode,
        operation: str,
        detail: str,
        *,
        location: tuple[str, int] | None = None,
        reference: str | None = None,
        cause: BaseException | None = None,
    ) -> None:
        if code.value in detail:
            raise ValueError("semantic evidence detail must not contain its code")
        self.code = code
        self.operation = operation
        self.detail = detail
        self.location = location
        self.reference = reference
        self.cause = cause
        super().__init__(f"{operation}: {detail}")


class ModelLoadError(AgenticMBSEError):
    """Failed to load SysML model."""

    def __init__(self, path: str, reason: str):
        self.path = path
        self.reason = reason
        super().__init__(f"Failed to load model from {path}: {reason}")


class ValidationError(AgenticMBSEError):
    """Validation check failed."""

    def __init__(self, level: int, message: str):
        self.level = level
        super().__init__(f"Level {level} validation failed: {message}")


class ConfigurationError(AgenticMBSEError):
    """Invalid configuration."""

    def __init__(self, config_path: str, message: str):
        self.config_path = config_path
        super().__init__(f"Configuration error in {config_path}: {message}")


class AdapterError(AgenticMBSEError):
    """Syside adapter error."""

    def __init__(self, operation: str, message: str):
        self.operation = operation
        super().__init__(f"Adapter error during {operation}: {message}")
