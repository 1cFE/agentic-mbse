"""The research seam's source registry: one checked door into a target's `knowledge/`.

The names below are the Python contract. The `agentic-mbse research` CLI is the
contract for everything else.
"""

from agentic_mbse.research.manifest import load_manifest_rows
from agentic_mbse.research.paths import RegistryPaths, default_paths
from agentic_mbse.research.sources import (
    KeyedFileSource,
    LocalPdfSource,
    SourceMetadata,
    UrlSource,
)

__all__ = [
    "KeyedFileSource",
    "LocalPdfSource",
    "RegistryPaths",
    "SourceMetadata",
    "UrlSource",
    "default_paths",
    "load_manifest_rows",
]
