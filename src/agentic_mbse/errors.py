"""Error classes for agentic-mbse."""

__all__ = [
    "AgenticMBSEError",
    "ModelLoadError",
    "ValidationError",
    "ConfigurationError",
    "AdapterError",
]


class AgenticMBSEError(Exception):
    """Base error for agentic-mbse package."""

    pass


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
