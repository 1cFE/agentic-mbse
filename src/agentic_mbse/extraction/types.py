"""Pipeline data types for the v4 PDF extraction pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from agentic_mbse.extraction.metrics import ExtractionMetrics


class PageAction(str, Enum):
    KEEP = "keep"
    GMFT_REPLACE = "gmft_replace"
    GMFT_APPEND = "gmft_append"
    STRIP_FALSE = "strip_false"
    STRIP_BROKEN = "strip_broken"
    CLAUDE_REPLACE = "claude_replace"


@dataclass
class PageResult:
    page_num: int  # 0-indexed
    markdown: str


@dataclass
class DetectedTable:
    markdown: str
    confidence: float
    num_rows: int
    num_cols: int
    avg_cell_length: float
    image_path: Path | None = None
    extraction_failed: bool = False
    detector: str = "gmft"
    source: str = "gmft"


@dataclass
class PageAssessment:
    page_num: int
    needs_claude: bool = False
    needs_gmft: bool = False
    reasons: list[str] = field(default_factory=list)
    severity: float = 0.0
    math_garble_score: float = 0.0
    table_anomaly: bool = False
    heading_anomaly: bool = False
    low_text_density: bool = False


@dataclass
class PageDecision:
    page_num: int
    action: PageAction
    reasons: list[str] = field(default_factory=list)
    details: dict[str, float | bool | str | list[str]] = field(default_factory=dict)


@dataclass
class CostRecord:
    page_num: int
    cost_usd: float
    input_tokens: int = 0
    output_tokens: int = 0
    model: str = ""
    elapsed_seconds: float = 0.0
    table_index: int | None = None


@dataclass
class PipelineResult:
    markdown: str
    metrics: ExtractionMetrics
    decisions: list[PageDecision] = field(default_factory=list)
    cost: list[CostRecord] = field(default_factory=list)
    total_cost_usd: float = 0.0
    source: str = ""
    elapsed_seconds: float = 0.0
    error: str | None = None
