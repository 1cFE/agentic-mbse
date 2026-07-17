"""CONSTRAINT-EXEC remediation F4 — Level 4 population reconciliation.

Live syside tests. The legacy "Total constraints" count excludes the requirement
subtree (Item 4 semantics, EXCLUDED_CONSTRAINT_TYPES), while the eligibility
metrics classify every extracted ConstraintUsage including SatisfyRequirementUsage.
The eligibility block therefore carries its own denominator ("Constraint usages
assessed (incl. satisfy)"), and the categories must sum to it — not to the legacy
total. Fixtures live under tests/fixtures/constraint_fact_shapes/.
"""

import shutil
from pathlib import Path

from agentic_mbse.validation.level4_constraints import analyze_constraints

FIX = Path(__file__).parent.parent / "fixtures" / "constraint_fact_shapes"

ASSESSED_KEY = "Constraint usages assessed (incl. satisfy)"
CATEGORY_KEYS = (
    "Eligible (admitted)",
    "Ineligible (blocked)",
    "Unassessed (satisfy/require/plain)",
)


def _category_sum(metrics: dict) -> int:
    return sum(metrics[key] for key in CATEGORY_KEYS)


class TestLevel4PopulationReconciliation:
    def test_single_file_categories_sum_to_assessed_denominator(self, tmp_path):
        """source_forms.sysml alone: the 12-vs-13 case. One satisfy usage is
        classified by the profile but excluded from the legacy count."""
        shutil.copy(FIX / "source_forms.sysml", tmp_path)
        metrics = analyze_constraints(str(tmp_path)).metrics

        assert _category_sum(metrics) == metrics[ASSESSED_KEY]
        # The two denominators are deliberately different populations:
        # legacy excludes the requirement subtree, assessed includes satisfy.
        assert metrics["Total constraints"] == 12
        assert metrics[ASSESSED_KEY] == 13

    def test_fixture_dir_categories_sum_to_assessed_denominator(self):
        """Whole fixture dir (source_forms + type_units): the 27-vs-28 case."""
        metrics = analyze_constraints(str(FIX)).metrics

        assert _category_sum(metrics) == metrics[ASSESSED_KEY]
        assert metrics["Total constraints"] == 27
        assert metrics[ASSESSED_KEY] == 28
