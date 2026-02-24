"""Pipeline budget allocation for the v4 PDF extraction pipeline.

Stub module — only contains EnhancerBudget and allocate_budget().
The full orchestration logic (extract_pdf, PipelineConfig) will be
added in Item 3.
"""

from __future__ import annotations

from dataclasses import dataclass

from agentic_mbse.extraction.types import PageAssessment


@dataclass
class EnhancerBudget:
    total_usd: float
    cost_per_page_usd: float

    @property
    def max_pages(self) -> int:
        if self.cost_per_page_usd <= 0:
            return 0
        return int(self.total_usd / self.cost_per_page_usd)


def allocate_budget(
    assessments: list[PageAssessment],
    budget: EnhancerBudget,
    needs_field: str = "needs_claude",
) -> set[int]:
    """Select pages for enhancement within a dollar budget.

    Sorts eligible pages by severity (highest first) and takes the top N
    that fit within the budget.

    Args:
        assessments: All page assessments from the document.
        budget: Dollar budget and per-page cost.
        needs_field: Assessment attribute to check for eligibility.
            Defaults to "needs_claude". Use "needs_gmft" for table budgets.

    Returns:
        Set of 0-indexed page numbers selected for enhancement.
    """
    eligible = [a for a in assessments if getattr(a, needs_field, False)]
    ranked = sorted(eligible, key=lambda a: a.severity, reverse=True)
    selected = ranked[: budget.max_pages]
    return {a.page_num for a in selected}
