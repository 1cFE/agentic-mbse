"""Profile analysis: route distribution, serialization, and summary table."""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path

from agentic_mbse.extraction.types import PageDecision, PipelineProfile


def route_distribution(decisions: list[PageDecision]) -> dict[str, int]:
    """Count occurrences of each PageAction across decisions."""
    return dict(Counter(d.action.value for d in decisions))


def profile_to_dict(
    profile: PipelineProfile,
    decisions: list[PageDecision],
    page_count: int,
    elapsed_seconds: float,
) -> dict:
    """Serialize profile + route distribution to dict for JSON output."""
    return {
        "page_count": page_count,
        "elapsed_seconds": elapsed_seconds,
        "step_timing": asdict(profile),
        "route_distribution": route_distribution(decisions),
    }


@dataclass
class ProfileEntry:
    """One row in the profile summary table."""

    document: str
    pages: int
    route_dist: dict[str, int]
    elapsed: float
    profile: PipelineProfile


# Display column groupings for timing
_TIMING_GROUPS: list[tuple[str, list[str]]] = [
    ("Base", ["arxiv_shortcut", "base_extraction"]),
    ("Tables", ["table_detection", "table_filter_enhance"]),
    ("Gate", ["quality_gate", "gmft_xref", "budget_allocation"]),
    ("Claude", ["claude_enhancement"]),
    ("Post", ["route_merge", "postprocess", "assemble_result"]),
]

# Route column groupings
_KEEP_ACTIONS = {"keep", "strip_false", "strip_broken"}
_GMFT_ACTIONS = {"gmft_replace", "gmft_append"}


def _group_timing(profile: PipelineProfile) -> list[float]:
    """Collapse 11 step timings into 5 display columns."""
    d = asdict(profile)
    return [sum(d.get(k, 0.0) for k in keys) for _, keys in _TIMING_GROUPS]


def _group_routes(route_dist: dict[str, int]) -> tuple[int, int, int]:
    """Collapse route actions into KEEP, CLAUDE, GMFT display columns."""
    keep = sum(route_dist.get(a, 0) for a in _KEEP_ACTIONS)
    claude = route_dist.get("claude_replace", 0)
    gmft = sum(route_dist.get(a, 0) for a in _GMFT_ACTIONS)
    return keep, claude, gmft


def format_profile_table(entries: list[ProfileEntry]) -> str:
    """Format profile entries as a human-readable summary table."""
    if not entries:
        return ""

    # Column headers
    doc_w = max(24, max(len(e.document) for e in entries) + 2)
    timing_headers = [name for name, _ in _TIMING_GROUPS]

    header = (
        f"{'Document':<{doc_w}}"
        f"{'Pages':>6}"
        f"{'KEEP':>6}"
        f"{'CLAUDE':>8}"
        f"{'GMFT':>6}"
        f"{'Time(s)':>9}"
    )
    for th in timing_headers:
        header += f"{th:>8}"

    sep = (
        f"{'─' * doc_w}"
        f"  {'─' * 4}"
        f"  {'─' * 4}"
        f"  {'─' * 6}"
        f"  {'─' * 4}"
        f"  {'─' * 7}"
    )
    for _ in timing_headers:
        sep += f"  {'─' * 6}"

    lines = [
        "Pipeline Profile Summary",
        "=" * len(header),
        "",
        header,
        sep,
    ]

    # Accumulators for totals
    total_pages = 0
    total_keep = 0
    total_claude = 0
    total_gmft = 0
    total_elapsed = 0.0
    total_timings = [0.0] * len(timing_headers)

    for entry in entries:
        keep, claude, gmft = _group_routes(entry.route_dist)
        timings = _group_timing(entry.profile)

        total_pages += entry.pages
        total_keep += keep
        total_claude += claude
        total_gmft += gmft
        total_elapsed += entry.elapsed
        for i, t in enumerate(timings):
            total_timings[i] += t

        row = (
            f"{entry.document:<{doc_w}}"
            f"{entry.pages:>6}"
            f"{keep:>6}"
            f"{claude:>8}"
            f"{gmft:>6}"
            f"{entry.elapsed:>9.1f}"
        )
        for t in timings:
            row += f"{t:>8.1f}"
        lines.append(row)

    # Totals row
    lines.append(sep)
    totals_row = (
        f"{'Total':<{doc_w}}"
        f"{total_pages:>6}"
        f"{total_keep:>6}"
        f"{total_claude:>8}"
        f"{total_gmft:>6}"
        f"{total_elapsed:>9.1f}"
    )
    for t in total_timings:
        totals_row += f"{t:>8.1f}"
    lines.append(totals_row)

    return "\n".join(lines)


def get_profile_corpus() -> list[Path]:
    """Return paths to profile corpus PDFs.

    Dev-only: walks 4 parents up from this file to reach repo root.
    Assumes: profile.py is at src/agentic_mbse/extraction/profile.py.
    Returns [] if the directory doesn't exist (e.g., installed package).
    """
    # 4 levels: extraction/ → agentic_mbse/ → src/ → repo_root/
    corpus_dir = Path(__file__).parent.parent.parent.parent / "profile_corpus"
    if not corpus_dir.exists():
        return []
    return sorted(p for p in corpus_dir.iterdir() if p.suffix == ".pdf")
