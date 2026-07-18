"""PIPELINE-TRUTH Item 4 — subtype-aware validator fixes (rows 5/6/7/8, D7).

Live syside tests (license-gated). Each changed diagnostic has a fires-on-shape
test with an independently-anchored expectation and a silent-on-clean test.
Fixtures live under tests/fixtures/item4_subtype/.
"""

from pathlib import Path

import pytest

from agentic_mbse.sysml.graph import detect_cycles
from agentic_mbse.sysml.syside_adapter import SysideAdapter
from agentic_mbse.sysml.types import Severity, ValidationCode
from agentic_mbse.validation.level3_dataflow import build_dependency_graph
from agentic_mbse.validation.level4_constraints import analyze_constraints
from agentic_mbse.validation.level6_architecture import (
    check_constraint_executability,
)

FIX = Path(__file__).parent.parent / "fixtures" / "item4_subtype"


def _load(*rel: str):
    model, _diags = SysideAdapter.load_model([FIX / r for r in rel])
    return model


# --- Row 5: level3 import dependency graph + circular check ------------------


class TestLevel3ImportSweep:
    def test_seeded_circular_import_fails(self):
        """The circular fixture yields a non-empty graph AND a detected cycle —
        the first time this check can fail (was always {} -> always passed)."""
        graph = build_dependency_graph(_load("circular_imports.sysml"))
        assert graph != {}
        # Independently anchored: the two packages import each other.
        assert graph == {"PkgOne": ["PkgTwo"], "PkgTwo": ["PkgOne"]}
        cycles = detect_cycles(graph)
        assert cycles, "circular import must be detected"

    def test_acyclic_import_passes(self):
        """Silent-on-clean: acyclic imports give a non-empty graph, no cycle."""
        graph = build_dependency_graph(_load("acyclic_imports.sysml"))
        assert graph == {"PkgApp": ["PkgLib"]}
        assert detect_cycles(graph) == []


# --- Row 6: level4 constraint count sees the assert, excludes requirement ----


class TestLevel4ConstraintCount:
    def test_counts_assert_excludes_requirement(self):
        """analyze_constraints counts assert + plain (2), not the requirement."""
        result = analyze_constraints(str(FIX / "l4_constraints"))
        # Independent anchor: the fixture declares exactly one assert
        # (affordable) and one plain constraint (positive_cost); the requirement
        # (widget_req) is requirement-side and excluded.
        assert result.metrics["Total constraints"] == 2

    def test_clean_model_counts_zero(self):
        """Silent-on-clean: a model with no constraints counts zero."""
        result = analyze_constraints(str(FIX / "l4_clean"))
        assert result.metrics["Total constraints"] == 0


# --- Row 7 + D7: level6 non-executable WARN fires on assert, fails loud ------


class TestLevel6NonExecutableWarn:
    """CONSTRAINT-EXEC Item 3 superseded row 7's blanket WARN with per-construct eligibility
    diagnostics: `affordable` (`cost <= budget`) and `positive_cost` (`cost > 0.0`) are both
    clean, unitless Real comparisons — admitted, not blocked — so they no longer warn."""

    def test_admitted_asserts_are_silent(self):
        """Independent anchor: fixture has assert `affordable` and plain `positive_cost`
        (both clean Real comparisons, now admitted) and requirement `widget_budget`
        (unassessed). None of the three should warn."""
        issues = check_constraint_executability(_load("constraints.sysml"))
        warned = {i.element_name.split("::")[-1] for i in issues}
        assert issues == []
        assert "affordable" not in warned
        assert "positive_cost" not in warned
        assert "widget_budget" not in warned

    def test_blocked_construct_errors(self):
        """A feature chain in a numerical comparison fires one named error."""
        issues = check_constraint_executability(_load("l6_ineligible/blocked.sysml"))
        errors = [i for i in issues if i.code == ValidationCode.L6_CONSTRAINT_MALFORMED_NUMERICAL]
        assert len(errors) == 1
        assert errors[0].severity == Severity.ERROR
        assert errors[0].element_name.split("::")[-1] == "chained_limit"
        assert "block_feature_chain" in errors[0].message

    def test_clean_model_silent(self):
        """Silent-on-clean: no constraints -> no WARN."""
        issues = check_constraint_executability(_load("l4_clean/model.sysml"))
        assert issues == []

    def test_fails_loud_on_extraction_error(self):
        """D7: an extraction error is raised, not swallowed to [] (which would
        mask the row-7 fix by reporting 'zero constraints')."""

        class _BrokenModel:
            def elements(self, *args, **kwargs):
                raise RuntimeError("injected extraction failure")

        with pytest.raises(RuntimeError, match="injected extraction failure"):
            check_constraint_executability(_BrokenModel())


# --- Row 8: AttributeUsage sweeps stay exact-type (opt-OUT) ------------------


class TestRow8EnumStaysExact:
    def test_exact_attribute_sweep_excludes_enum_usages(self):
        """EnumerationUsage <: AttributeUsage. The exact-type AttributeUsage
        query (used by all 5 attribute sites) must NOT sweep the enum members;
        include_subtypes would. This pins the opt-OUT decision."""
        model = _load("enum_attr.sysml")
        exact = list(SysideAdapter.elements_of_type(model, "AttributeUsage"))
        swept = list(SysideAdapter.elements_of_type(model, "AttributeUsage", include_subtypes=True))
        exact_types = {type(e).__name__ for e in exact}
        swept_types = {type(e).__name__ for e in swept}
        assert exact_types == {"AttributeUsage"}
        assert "EnumerationUsage" in swept_types  # only visible when swept
