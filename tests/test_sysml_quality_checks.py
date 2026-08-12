"""
Tests for SysML Quality Checks

Test suite for the 6-level SysML quality validation framework.
Follows test-first approach per plan.md.
"""

import shutil
import tempfile
from pathlib import Path

import pytest


# Test fixtures for valid/invalid SysML files
@pytest.fixture
def temp_models_dir():
    """Create temporary models directory with test files"""
    tmpdir = tempfile.mkdtemp()
    models_path = Path(tmpdir) / "models"
    models_path.mkdir()
    (models_path / "library").mkdir()
    (models_path / "designs").mkdir()
    yield models_path
    shutil.rmtree(tmpdir)


@pytest.fixture
def valid_sysml_file(temp_models_dir):
    """Create a valid SysML test file"""
    file_path = temp_models_dir / "library" / "test.sysml"
    file_path.write_text("""
        import ScalarValues::*;
        import SI::*;
        import ISQ::*;

        package TestPackage {
            calc def TestCalc {
                in x : Real;
                return y : Real;
            }
        }
    """)
    return file_path


@pytest.fixture
def invalid_sysml_file(temp_models_dir):
    """Create invalid SysML test file (syntax error)"""
    file_path = temp_models_dir / "library" / "bad.sysml"
    file_path.write_text("""
        import ScalarValues::*;
        import SI::*;
        import ISQ::*;

        package Broken {
            calc def MissingBrace
                in x : Real;
            }
        }
    """)
    return file_path


class TestCommon:
    """Tests for common.py utilities"""

    def test_discover_sysml_files(self, valid_sysml_file):
        """Test file discovery finds .sysml files recursively"""
        from agentic_mbse.validation.common import discover_sysml_files

        files = discover_sysml_files(str(valid_sysml_file.parent.parent))
        assert len(files) > 0
        assert any(f.name == "test.sysml" for f in files)

    def test_discover_empty_directory(self, temp_models_dir):
        """Test discovery handles empty directory gracefully"""
        from agentic_mbse.validation.common import discover_sysml_files

        empty_dir = temp_models_dir / "empty"
        empty_dir.mkdir()
        files = discover_sysml_files(str(empty_dir))
        assert len(files) == 0


class TestLevel1Syntax:
    """Tests for Level 1: Syntax Validation"""

    def test_valid_syntax_passes(self, valid_sysml_file):
        """Test that valid file passes syntax validation"""
        from agentic_mbse.validation.level1_syntax import validate_syntax

        result = validate_syntax(str(valid_sysml_file.parent.parent))
        assert result.success == True
        assert result.level == 1
        assert len(result.issues) == 0

    def test_invalid_syntax_fails(self, invalid_sysml_file):
        """Test that invalid file fails with diagnostics"""
        from agentic_mbse.validation.level1_syntax import validate_syntax

        result = validate_syntax(str(invalid_sysml_file.parent.parent))
        assert result.success == False
        assert len(result.issues) > 0
        assert "bad.sysml" in result.issues[0]

    def test_no_files_warning(self, temp_models_dir):
        """Test that empty directory returns success with warning"""
        from agentic_mbse.validation.level1_syntax import validate_syntax

        empty_dir = temp_models_dir / "empty"
        empty_dir.mkdir()
        result = validate_syntax(str(empty_dir))
        assert result.success == True
        assert len(result.warnings) > 0


class TestMasterOrchestrator:
    """Tests for run_all_checks.py"""

    def test_fail_fast_stops_at_first_failure(self, invalid_sysml_file):
        """Test that fail-fast mode stops at first failure"""
        from agentic_mbse.validation.runner import run_all_checks

        result = run_all_checks(
            str(invalid_sysml_file.parent.parent), fail_fast=True
        )

        # Should stop at Level 1 (syntax failure)
        assert result.total_checks == 1
        assert result.failed == 1
        assert not result.overall_success

    def test_complete_mode_runs_all_levels(self, valid_sysml_file):
        """Test that complete mode runs all levels regardless of failures"""
        from agentic_mbse.validation.runner import run_all_checks

        result = run_all_checks(
            str(valid_sysml_file.parent.parent), fail_fast=False
        )

        # Should run all implemented levels (currently just Level 1)
        assert result.total_checks >= 1

    def test_specific_level_runs_only_that_level(self, valid_sysml_file):
        """Test running specific level only"""
        from agentic_mbse.validation.runner import run_all_checks

        result = run_all_checks(
            str(valid_sysml_file.parent.parent), specific_level=1
        )

        # Should run only Level 1
        assert result.total_checks == 1
        assert result.results[0].level == 1

    def test_verbose_flag(self, valid_sysml_file):
        """Test verbose output doesn't crash"""
        from agentic_mbse.validation.runner import run_all_checks

        result = run_all_checks(str(valid_sysml_file.parent.parent), verbose=True)

        assert result is not None


class TestLevel2Structure:
    """Tests for Level 2: Structural Completeness"""

    def test_unused_definition_detected(self, temp_models_dir):
        """Test detection of unused calc definitions"""
        # Create calc def in library but no usage
        lib_file = temp_models_dir / "library" / "unused.sysml"
        lib_file.write_text("""
            import ScalarValues::*;
            import SI::*;
            import ISQ::*;

            package Library {
                calc def UnusedCalc {
                    in x : Real;
                    return y : Real;
                }
            }
        """)

        from agentic_mbse.validation.level2_structure import validate_structure

        result = validate_structure(str(temp_models_dir))

        # Should detect unused definition
        assert result.level == 2
        # Note: May have issues if check is fully implemented
        # For now, verify script doesn't crash

    def test_handles_empty_models(self, temp_models_dir):
        """Test that empty directory doesn't crash"""
        from agentic_mbse.validation.level2_structure import validate_structure

        result = validate_structure(str(temp_models_dir))
        assert result.success == True
        assert len(result.warnings) > 0  # Should warn about no files

    def test_unbound_input_detected_basic(self, temp_models_dir):
        """Basic test: unbound input should be detected"""
        # Create calc def in library
        lib_file = temp_models_dir / "library" / "calcs.sysml"
        lib_file.write_text("""
            import ScalarValues::*;

            package Library {
                calc def PowerCalc {
                    in p_input : Real;
                    return p_output : Real;
                }
            }
        """)

        # Create design with unbound calc usage
        design_file = temp_models_dir / "designs" / "design.sysml"
        design_file.write_text("""
            import ScalarValues::*;
            private import Library::PowerCalc;

            package Design {
                part system {
                    calc power : PowerCalc {
                        // p_input NOT bound - should be detected
                    }
                }
            }
        """)

        from agentic_mbse.validation.common import discover_sysml_files, load_sysml_model
        from agentic_mbse.validation.level2_structure import check_unbound_inputs

        files = discover_sysml_files(str(temp_models_dir))
        model, _ = load_sysml_model(files)

        issues = check_unbound_inputs(model)

        # Should detect unbound input
        assert len(issues) > 0
        assert "Unbound input" in issues[0].message
        assert "p_input" in issues[0].message

    def test_bound_input_passes(self, temp_models_dir):
        """Test that bound inputs do not generate issues"""
        lib_file = temp_models_dir / "library" / "calcs.sysml"
        lib_file.write_text("""
            import ScalarValues::*;

            package Library {
                calc def PowerCalc {
                    in p_input : Real;
                    return p_output : Real;
                }
            }
        """)

        design_file = temp_models_dir / "designs" / "design.sysml"
        design_file.write_text("""
            import ScalarValues::*;
            private import Library::PowerCalc;

            package Design {
                part system {
                    attribute power_in : Real = 100.0;

                    calc power : PowerCalc {
                        in p_input = power_in;  // BOUND - should pass
                    }
                }
            }
        """)

        from agentic_mbse.validation.level2_structure import validate_structure

        result = validate_structure(str(temp_models_dir))

        # Should NOT report any unbound input issues
        unbound_issues = [iss for iss in result.issues if "Unbound input" in iss]
        assert len(unbound_issues) == 0

    def test_default_value_not_required(self, temp_models_dir):
        """Test that inputs with defaults don't require bindings"""
        lib_file = temp_models_dir / "library" / "calcs.sysml"
        lib_file.write_text("""
            import ScalarValues::*;

            package Library {
                calc def PowerCalc {
                    in p_input : Real = 50.0;  // HAS DEFAULT
                    return p_output : Real;
                }
            }
        """)

        design_file = temp_models_dir / "designs" / "design.sysml"
        design_file.write_text("""
            import ScalarValues::*;
            private import Library::PowerCalc;

            package Design {
                part system {
                    calc power : PowerCalc {
                        // p_input NOT bound but has default - should pass
                    }
                }
            }
        """)

        from agentic_mbse.validation.level2_structure import validate_structure

        result = validate_structure(str(temp_models_dir))

        # Should NOT report unbound input (has default)
        unbound_issues = [iss for iss in result.issues if "Unbound input" in iss]
        assert len(unbound_issues) == 0

    def test_no_calc_usages_handles_gracefully(self, temp_models_dir):
        """Test that models without calc usages don't crash"""
        lib_file = temp_models_dir / "library" / "parts.sysml"
        lib_file.write_text("""
            import ScalarValues::*;

            package Library {
                part def Component {
                    attribute value : Real;
                }
            }
        """)

        from agentic_mbse.validation.level2_structure import validate_structure

        result = validate_structure(str(temp_models_dir))

        # Should pass with no unbound input issues
        assert result.level == 2
        # No crash, no false positives

    def test_inaccessible_calc_def_skipped(self, temp_models_dir):
        """Test that calc usages with broken references are skipped gracefully"""
        design_file = temp_models_dir / "designs" / "broken.sysml"
        design_file.write_text("""
            import ScalarValues::*;

            package Design {
                part system {
                    calc power : NonExistentCalc {
                        // Reference to undefined calc def
                    }
                }
            }
        """)

        from agentic_mbse.validation.level2_structure import validate_structure

        result = validate_structure(str(temp_models_dir))

        # Should not crash - gracefully skip broken usage
        assert result.level == 2

    def test_literal_binding_warning(self, temp_models_dir):
        """Test end-to-end detection of placeholder literal binding"""
        lib_file = temp_models_dir / "library" / "calcs.sysml"
        lib_file.write_text("""
            import ScalarValues::*;

            package Library {
                calc def SimpleCalc {
                    in attribute x : Real;
                    out attribute y : Real = x * 2;
                }
            }
        """)

        design_file = temp_models_dir / "designs" / "design.sysml"
        design_file.write_text("""
            import ScalarValues::*;
            private import Library::SimpleCalc;

            package Design {
                part test_part {
                    calc instance : SimpleCalc {
                        in x = 42.0;  // Literal placeholder
                    }
                }
            }
        """)

        from agentic_mbse.validation.level2_structure import validate_structure

        result = validate_structure(str(temp_models_dir))

        # Should have warning (not error) about literal binding
        assert any("WARN" in issue and "literal value" in issue for issue in result.issues)
        assert result.metrics["Placeholder bindings"] >= 1

    def test_valid_binding_no_issues(self, temp_models_dir):
        """Test that properly bound inputs with defined values produce no issues"""
        lib_file = temp_models_dir / "library" / "calcs.sysml"
        lib_file.write_text("""
            import ScalarValues::*;

            package Library {
                calc def SimpleCalc {
                    in attribute x : Real;
                    out attribute y : Real = x * 2;
                }
            }
        """)

        design_file = temp_models_dir / "designs" / "design.sysml"
        design_file.write_text("""
            import ScalarValues::*;
            private import Library::SimpleCalc;

            package Design {
                part test_part {
                    attribute value_defined : Real = 10.0;  // HAS VALUE

                    calc instance : SimpleCalc {
                        in x = value_defined;  // Valid binding
                    }
                }
            }
        """)

        from agentic_mbse.validation.level2_structure import validate_structure

        result = validate_structure(str(temp_models_dir))

        # Should pass with no undefined binding or unbound input issues
        assert result.success
        assert result.metrics["Unbound inputs"] == 0
        assert result.metrics["Undefined bindings"] == 0

    def test_complex_expression_undefined_attribute(self, temp_models_dir):
        """Test that complex expressions are validated for undefined references"""
        lib_file = temp_models_dir / "library" / "calcs.sysml"
        lib_file.write_text("""
            import ScalarValues::*;

            package Library {
                calc def SimpleCalc {
                    in attribute x : Real;
                    out attribute y : Real = x * 2;
                }
            }
        """)

        design_file = temp_models_dir / "designs" / "design.sysml"
        design_file.write_text("""
            import ScalarValues::*;
            private import Library::SimpleCalc;

            package Design {
                part test_part {
                    attribute a : Real = 10.0;  // DEFINED
                    attribute b : Real;  // UNDEFINED!

                    calc instance : SimpleCalc {
                        in x = a + b;  // Complex expression with undefined 'b'
                    }
                }
            }
        """)

        from agentic_mbse.validation.level2_structure import validate_structure

        result = validate_structure(str(temp_models_dir))

        # Should detect undefined 'b' even in complex expression
        assert not result.success
        assert result.metrics["Undefined bindings"] >= 1
        assert any("undefined attribute" in issue and "::b'" in issue for issue in result.issues)

    def test_complex_expression_all_defined(self, temp_models_dir):
        """Test that complex expressions pass when all references are defined"""
        lib_file = temp_models_dir / "library" / "calcs.sysml"
        lib_file.write_text("""
            import ScalarValues::*;

            package Library {
                calc def SimpleCalc {
                    in attribute x : Real;
                    out attribute y : Real = x * 2;
                }
            }
        """)

        design_file = temp_models_dir / "designs" / "design.sysml"
        design_file.write_text("""
            import ScalarValues::*;
            private import Library::SimpleCalc;

            package Design {
                part test_part {
                    attribute a : Real = 10.0;  // DEFINED
                    attribute b : Real = 5.0;  // DEFINED

                    calc instance : SimpleCalc {
                        in x = a + b;  // Complex expression - all defined
                    }
                }
            }
        """)

        from agentic_mbse.validation.level2_structure import validate_structure

        result = validate_structure(str(temp_models_dir))

        # Should pass - all references have values
        assert result.success
        assert result.metrics["Undefined bindings"] == 0


class TestLevel3Dataflow:
    """Tests for Level 3: Dataflow Integrity"""

    def test_circular_dependency_detected(self, temp_models_dir):
        """Test detection of circular dependencies"""
        # Create two files with circular imports
        file1 = temp_models_dir / "library" / "file1.sysml"
        file1.write_text("""
            import ScalarValues::*;
            import SI::*;
            import ISQ::*;

            package Pkg1 {
                public import Pkg2::*;
            }
        """)

        file2 = temp_models_dir / "library" / "file2.sysml"
        file2.write_text("""
            import ScalarValues::*;
            import SI::*;
            import ISQ::*;

            package Pkg2 {
                public import Pkg1::*;
            }
        """)

        from agentic_mbse.validation.level3_dataflow import validate_dataflow

        result = validate_dataflow(str(temp_models_dir))

        # Should detect circular dependency
        assert result.level == 3
        # May have issues if circular detection works

    def test_handles_no_dependencies(self, valid_sysml_file):
        """Test that models with no imports don't crash"""
        from agentic_mbse.validation.level3_dataflow import validate_dataflow

        result = validate_dataflow(str(valid_sysml_file.parent.parent))
        assert result.level == 3


class TestLevel4Constraints:
    """Tests for Level 4: Constraint Satisfaction"""

    def test_constraint_metrics_reported(self, temp_models_dir):
        """Test that constraint coverage metrics are reported"""
        # Create model with constraints
        file = temp_models_dir / "library" / "constraints.sysml"
        file.write_text("""
            package ConstraintTest {
                part def System {
                    attribute temp : Real;
                    constraint TempLimit { temp <= 100.0 }
                }
            }
        """)

        from agentic_mbse.validation.level4_constraints import analyze_constraints

        result = analyze_constraints(str(temp_models_dir))

        assert result.level == 4
        assert "Total constraints" in result.metrics

    def test_no_constraints_handled(self, valid_sysml_file):
        """Test that models without constraints don't crash"""
        from agentic_mbse.validation.level4_constraints import analyze_constraints

        result = analyze_constraints(str(valid_sysml_file.parent.parent))
        assert result.level == 4

    def test_direct_file_execution_resolves_its_shared_helpers(self):
        """Running the checker as a script still imports `common`, with no relative fallback."""
        import subprocess
        import sys

        from agentic_mbse.validation import level4_constraints

        completed = subprocess.run(
            [sys.executable, level4_constraints.__file__, "--help"],
            capture_output=True,
            text=True,
            check=False,
        )

        assert completed.returncode == 0, completed.stderr
        assert "Level 4" in completed.stdout
        assert "ImportError" not in completed.stderr


class TestLevel5Traceability:
    """Tests for Level 5: Traceability & Documentation"""

    def test_documentation_coverage_reported(self, temp_models_dir):
        """Test documentation coverage metrics"""
        # Create calc def with doc comment
        file = temp_models_dir / "library" / "documented.sysml"
        file.write_text("""
            package DocTest {
                doc /* This calculates something */
                calc def DocumentedCalc {
                    in x : Real;
                    return y : Real;
                }

                calc def UndocumentedCalc {
                    in x : Real;
                    return y : Real;
                }
            }
        """)

        from agentic_mbse.validation.level5_traceability import validate_traceability

        result = validate_traceability(str(temp_models_dir))

        assert result.level == 5
        assert "Total elements" in result.metrics
        assert "Documented" in result.metrics

    def test_missing_docs_reported(self, temp_models_dir):
        """Test that missing docs are reported as issues"""
        from agentic_mbse.validation.level5_traceability import validate_traceability

        result = validate_traceability(str(temp_models_dir))
        assert result.level == 5


class TestLevel4ConstraintCoverage:
    """Tests for L4 eligibility coverage (CONSTRAINT-EXEC Item 3, replacing the old 0%
    attribute-coverage placeholder)."""

    def test_coverage_metrics_reported(self, temp_models_dir):
        """Test that eligibility coverage metrics are reported in L4"""
        file = temp_models_dir / "library" / "coverage.sysml"
        file.write_text("""
            package CoverageTest {
                part def System {
                    attribute temp : Real;
                    attribute pressure : Real;
                    constraint TempLimit { temp <= 100.0 }
                }
            }
        """)

        from agentic_mbse.validation.level4_constraints import analyze_constraints

        result = analyze_constraints(str(temp_models_dir))

        assert result.level == 4
        assert "Admitted numerical" in result.metrics
        assert "Malformed numerical" in result.metrics
        assert "Non-numerical" in result.metrics
        assert "Executable share" in result.metrics


class TestEndToEnd:
    """End-to-end integration tests"""

    def test_full_quality_suite_on_existing_models(self):
        """Test full quality suite on sample models"""
        from agentic_mbse.validation.runner import run_all_checks

        # Run on sample models directory
        result = run_all_checks("tests/fixtures/sample_models/", fail_fast=False)

        # Should complete all 6 levels
        assert result.total_checks == 6

        # Verify we got results for each level
        levels_run = [r.level for r in result.results]
        assert levels_run == [1, 2, 3, 4, 5, 6]

        # At minimum, all checks should complete without exceptions
        assert len(result.results) == 6

    def test_cli_exit_codes(self):
        """Test that exit codes are correct"""
        import subprocess
        from pathlib import Path

        # Test CLI help output
        result = subprocess.run(
            ["agentic-mbse", "--help"],
            capture_output=True,
            cwd=Path(__file__).parent.parent,
        )
        assert result.returncode == 0
        assert b"validate" in result.stdout

        # Test validate on sample models
        result = subprocess.run(
            ["agentic-mbse", "validate", "tests/fixtures/sample_models/"],
            capture_output=True,
            cwd=Path(__file__).parent.parent,
        )
        # Exit code should be 0 or 1 depending on quality
        assert result.returncode in [0, 1]

    def test_complete_mode_runs_all_levels(self):
        """Test that complete mode runs all levels even with failures"""
        from agentic_mbse.validation.runner import run_all_checks

        # Run on sample models in complete mode
        result = run_all_checks("tests/fixtures/sample_models/", fail_fast=False)

        # Should run all 6 levels regardless of failures
        assert result.total_checks == 6
        assert len(result.results) == 6

        # Verify each level executed (even if some failed)
        for i, level_result in enumerate(result.results, start=1):
            assert level_result.level == i

    def test_level_6_integration(self):
        """Test Level 6 runs as part of full suite"""
        from agentic_mbse.validation.runner import run_all_checks

        result = run_all_checks("tests/fixtures/sample_models/", fail_fast=False)
        level_6_results = [r for r in result.results if r.level == 6]
        assert len(level_6_results) == 1, "Level 6 should run once in full suite"
        assert level_6_results[0].level_name == "Architecture & Pipeline Readiness"

    def test_level_6_only_mode(self):
        """Test --level=6 runs only Level 6"""
        from agentic_mbse.validation.runner import run_all_checks

        result = run_all_checks("tests/fixtures/sample_models/", specific_level=6)
        assert len(result.results) == 1
        assert result.results[0].level == 6
        assert result.results[0].level_name == "Architecture & Pipeline Readiness"

    def test_fail_fast_mode(self):
        """Test that fail-fast mode stops appropriately"""
        import shutil
        import tempfile
        from pathlib import Path

        from agentic_mbse.validation.runner import run_all_checks

        # Create temp dir with broken file
        tmpdir = tempfile.mkdtemp()
        try:
            models_path = Path(tmpdir) / "models"
            models_path.mkdir()
            broken_file = models_path / "broken.sysml"
            broken_file.write_text("package Broken { calc def MissingBrace in x : Real; }")

            # Run in fail-fast mode
            result = run_all_checks(str(models_path), fail_fast=True)

            # Should stop at Level 1 (syntax failure)
            assert result.total_checks <= 5  # May stop early
            assert result.failed >= 1  # At least one failure

        finally:
            shutil.rmtree(tmpdir)


class TestLevel6Architecture:
    """Tests for Level 6: Architecture & Pipeline Readiness validation."""

    def test_validation_codes_exist(self):
        """All L6 ValidationCode entries are defined"""
        from agentic_mbse.sysml.types import ValidationCode

        assert hasattr(ValidationCode, "L6_MISSING_QUALIFIED_NAME")
        assert hasattr(ValidationCode, "L6_INVALID_QUALIFIED_NAME")
        assert hasattr(ValidationCode, "L6_CALC_DEF_NO_OUTPUT")
        assert hasattr(ValidationCode, "L6_CALC_DEF_NO_DIRECTION")
        assert hasattr(ValidationCode, "L6_INVALID_BINDING_FORMAT")
        assert hasattr(ValidationCode, "L6_DESIGN_ATTR_INCOMPLETE")

    def test_models_report_incomplete_attrs(self):
        """Test that L6 can detect incomplete attrs"""
        from agentic_mbse.validation.level6_architecture import validate_architecture

        result = validate_architecture("tests/fixtures/sample_models/")
        assert result.level == 6
        assert result.level_name == "Architecture & Pipeline Readiness"

    def test_module_returns_quality_check_result(self):
        """validate_architecture returns QualityCheckResult"""
        from agentic_mbse.validation.common import QualityCheckResult
        from agentic_mbse.validation.level6_architecture import validate_architecture

        result = validate_architecture("tests/fixtures/sample_models/")
        assert isinstance(result, QualityCheckResult)
        assert result.level == 6
        assert result.level_name == "Architecture & Pipeline Readiness"

    def test_check_qualified_names_on_valid_model(self):
        """Valid models produce no qualified name issues"""
        from agentic_mbse.validation.level6_architecture import validate_architecture

        result = validate_architecture("tests/fixtures/sample_models/")
        qname_issues = [
            i for i in result.structured_issues if "QUALIFIED_NAME" in str(i.code)
        ]
        assert len(qname_issues) == 0, f"Unexpected issues: {qname_issues}"

    def test_metrics_include_element_counts(self):
        """Metrics include counts of checked elements"""
        from agentic_mbse.validation.level6_architecture import validate_architecture

        result = validate_architecture("tests/fixtures/sample_models/")
        assert "Calc defs checked" in result.metrics
        assert "Calc usages checked" in result.metrics
        assert result.metrics["Calc defs checked"] >= 0

    def test_check_calc_def_structure_finds_outputs(self):
        """Valid calc defs with outputs pass structure check"""
        from agentic_mbse.sysml.types import ValidationCode
        from agentic_mbse.validation.level6_architecture import validate_architecture

        result = validate_architecture("tests/fixtures/sample_models/")
        no_output_issues = [
            i
            for i in result.structured_issues
            if i.code == ValidationCode.L6_CALC_DEF_NO_OUTPUT
        ]
        assert len(no_output_issues) == 0, f"Unexpected no-output issues: {no_output_issues}"

    def test_check_binding_formats_valid(self):
        """Valid bindings pass format check"""
        from agentic_mbse.sysml.types import ValidationCode
        from agentic_mbse.validation.level6_architecture import validate_architecture

        result = validate_architecture("tests/fixtures/sample_models/")
        binding_issues = [
            i
            for i in result.structured_issues
            if i.code == ValidationCode.L6_INVALID_BINDING_FORMAT
        ]
        assert len(binding_issues) == 0, f"Unexpected binding issues: {binding_issues}"

    def test_all_checks_run(self):
        """All check functions execute and contribute to metrics"""
        from agentic_mbse.validation.level6_architecture import validate_architecture

        result = validate_architecture("tests/fixtures/sample_models/")
        assert "Calc defs checked" in result.metrics
        assert "Calc usages checked" in result.metrics
        assert result.metrics["Calc defs checked"] >= 0
        assert result.metrics["Calc usages checked"] >= 0

    def test_incomplete_design_attrs_are_errors(self):
        """Incomplete design attributes produce errors per FR-7"""
        from agentic_mbse.sysml.types import Severity, ValidationCode
        from agentic_mbse.validation.level6_architecture import validate_architecture

        result = validate_architecture("tests/fixtures/sample_models/")
        incomplete_issues = [
            i
            for i in result.structured_issues
            if i.code == ValidationCode.L6_DESIGN_ATTR_INCOMPLETE
        ]
        for issue in incomplete_issues:
            assert issue.severity == Severity.ERROR, f"Expected ERROR, got {issue.severity}"


    def test_validate_architecture_returns_result(self, tmp_path):
        """L6 orchestrator returns QualityCheckResult with level=6 for empty dir."""
        from agentic_mbse.validation.level6_architecture import validate_architecture

        result = validate_architecture(str(tmp_path))
        assert result.level == 6
        assert result.level_name == "Architecture & Pipeline Readiness"

    def test_check_manifests_no_designs_dir(self, tmp_path):
        """_check_manifests returns empty when no designs/ directory."""
        from agentic_mbse.validation.level6_architecture import _check_manifests

        issues, count = _check_manifests(str(tmp_path), None)
        assert issues == []
        assert count == 0

    def test_manifest_checks_included(self, tmp_path):
        """L6 includes manifest subsystem checks."""
        from agentic_mbse.validation.level6_architecture import validate_architecture

        # Create design with manifest
        designs_dir = tmp_path / "designs" / "test_design"
        designs_dir.mkdir(parents=True)
        manifest = designs_dir / "manifest.yaml"
        manifest.write_text('design_name: "Test"\nexpected_subsystems:\n  - subsystem1\n')

        # Create a minimal SysML file so the model loads
        lib_dir = tmp_path / "library"
        lib_dir.mkdir()
        (lib_dir / "test.sysml").write_text("package TestPkg {}")

        result = validate_architecture(str(tmp_path))
        assert result.level == 6
        assert "Manifests checked" in result.metrics
        assert result.metrics["Manifests checked"] >= 1


class TestLevel6NegativeCases:
    """Negative tests for L6 check functions and ADR-002 integration."""

    FIXTURES = "tests/fixtures/l6_negative"
    ADR002_FIXTURES = "tests/fixtures/adr002_violations"

    def test_calc_def_no_output(self):
        """Calc def with no output parameter triggers L6_CALC_DEF_NO_OUTPUT."""
        from agentic_mbse.sysml.types import Severity, ValidationCode
        from agentic_mbse.validation.level6_architecture import validate_architecture

        result = validate_architecture(self.FIXTURES)
        no_output = [
            i for i in result.structured_issues
            if i.code == ValidationCode.L6_CALC_DEF_NO_OUTPUT
        ]
        assert len(no_output) >= 1, f"Expected L6_CALC_DEF_NO_OUTPUT, got: {result.structured_issues}"
        assert no_output[0].severity == Severity.ERROR
        assert "NoOutputCalc" in no_output[0].message

    def test_calc_def_no_direction_is_dead_code(self):
        """L6_CALC_DEF_NO_DIRECTION requires member.typing which syside never sets.

        This documents that the check is currently dead code. The fixture has a
        parameter without direction (x : Real;) but syside produces members with
        has_typing=False, so the code path at level6_architecture.py:283 is never
        reached. If syside adds typing support, this test should be updated to
        assert the WARNING fires.
        """
        from agentic_mbse.sysml.types import ValidationCode
        from agentic_mbse.validation.level6_architecture import validate_architecture

        result = validate_architecture(self.FIXTURES)
        no_dir = [
            i for i in result.structured_issues
            if i.code == ValidationCode.L6_CALC_DEF_NO_DIRECTION
        ]
        # Currently 0 due to syside not exposing typing attribute
        assert len(no_dir) == 0

    def test_manifest_missing_subsystems(self):
        """Manifest with nonexistent subsystems produces failure issues."""
        from agentic_mbse.validation.level6_architecture import validate_architecture

        result = validate_architecture(self.FIXTURES)
        assert result.success is False
        assert result.metrics["Manifests checked"] >= 1
        # Manifest issues are unstructured strings
        manifest_issues = [i for i in result.issues if "Missing subsystem" in str(i)]
        assert len(manifest_issues) >= 2
        assert any("nonexistent_subsystem_alpha" in str(i) for i in manifest_issues)

    def test_manifest_invalid_yaml_fails_the_level_and_does_not_stop_the_sweep(self, tmp_path):
        """A malformed manifest is a Level 6 issue, not a silently skipped design.

        The three unusable-manifest shapes used to collapse to `None` and read the same as
        "this design has no manifest", so a design whose composition was never checked left
        Level 6 green. `load_manifest` now separates absent from invalid, and `_check_manifests`
        reports the invalid one while still visiting the design that follows it.
        """
        from agentic_mbse.validation.common import discover_sysml_files, load_sysml_model
        from agentic_mbse.validation.level6_architecture import (
            ManifestError,
            _check_manifests,
            load_manifest,
        )

        bad_design = tmp_path / "designs" / "bad_design"
        bad_design.mkdir(parents=True)
        (bad_design / "manifest.yaml").write_text(": : : not valid yaml {{[")

        # A second, well-formed design whose expectation is genuinely unmet: it must still be
        # reached and reported, which is what "one bad file must not abort the check" means.
        good_design = tmp_path / "designs" / "good_design"
        good_design.mkdir(parents=True)
        (good_design / "manifest.yaml").write_text("expected_subsystems:\n  - absent_part\n")

        (tmp_path / "test.sysml").write_text("package BadYamlTest {}")
        files = discover_sysml_files(str(tmp_path))
        model, _ = load_sysml_model(files)

        with pytest.raises(ManifestError, match="could not be read"):
            load_manifest(bad_design)

        issues, count = _check_manifests(str(tmp_path), model)
        assert count == 2
        assert any("Unusable manifest in bad_design" in issue for issue in issues)
        assert any("Missing subsystem 'absent_part' in good_design" in issue for issue in issues)

    def test_manifest_absent_is_not_an_error(self, tmp_path):
        """A design with no manifest has nothing to check — the one state that stays `None`."""
        from agentic_mbse.validation.level6_architecture import load_manifest

        design_dir = tmp_path / "designs" / "no_manifest_design"
        design_dir.mkdir(parents=True)

        assert load_manifest(design_dir) is None

    def test_manifest_valid_yaml_that_is_not_a_mapping(self, tmp_path):
        """Well-formed YAML that is a list is refused here, not subscripted by a caller."""
        from agentic_mbse.validation.level6_architecture import ManifestError, load_manifest

        design_dir = tmp_path / "designs" / "list_design"
        design_dir.mkdir(parents=True)
        (design_dir / "manifest.yaml").write_text("- alpha\n- beta\n")

        with pytest.raises(ManifestError, match="is a list, not a mapping"):
            load_manifest(design_dir)

    def test_manifest_that_is_not_utf8_is_refused_by_name(self, tmp_path):
        """A mis-encoded manifest is refused as unreadable, not returned as absent.

        `UnicodeDecodeError` is a `ValueError`, so it is neither `OSError` nor
        `yaml.YAMLError`. It still has to become a named `ManifestError` rather than escape
        raw, because `_check_manifests` loops over every design and catches that name.
        """
        from agentic_mbse.validation.level6_architecture import ManifestError, load_manifest

        design_dir = tmp_path / "designs" / "latin1_design"
        design_dir.mkdir(parents=True)
        # Valid YAML in latin-1; byte 0xE9 is not a legal UTF-8 sequence start.
        (design_dir / "manifest.yaml").write_bytes(
            "subsystems:\n  - caf\xe9\n".encode("latin-1")
        )

        with pytest.raises(ManifestError, match="could not be read"):
            load_manifest(design_dir)

    def test_manifest_read_failure_is_refused_by_name(self, tmp_path):
        """An unreadable manifest is refused as unreadable; unexpected errors are not swallowed."""
        from agentic_mbse.validation.level6_architecture import ManifestError, load_manifest

        design_dir = tmp_path / "designs" / "unreadable_design"
        design_dir.mkdir(parents=True)
        manifest = design_dir / "manifest.yaml"
        manifest.write_text("subsystems: []\n")
        manifest.chmod(0o000)
        try:
            with pytest.raises(ManifestError, match="Permission denied"):
                load_manifest(design_dir)
        finally:
            manifest.chmod(0o644)

    def test_adr002_v1_in_orchestrator(self):
        """ADR-002 V1 violations (calc def in designs/) appear in L6 result."""
        from agentic_mbse.sysml.types import ValidationCode
        from agentic_mbse.validation.level6_architecture import validate_architecture

        result = validate_architecture(self.ADR002_FIXTURES)
        v1_issues = [
            i for i in result.structured_issues
            if i.code == ValidationCode.V1_CALC_DEF_LOCATION
        ]
        assert len(v1_issues) >= 1, "Expected V1_CALC_DEF_LOCATION from adr002_violations"
        assert any("designs/" in i.message for i in v1_issues)

    def test_adr002_v2_in_orchestrator(self):
        """ADR-002 V2 violations (derived expressions) appear in L6 result."""
        from agentic_mbse.sysml.types import ValidationCode
        from agentic_mbse.validation.level6_architecture import validate_architecture

        result = validate_architecture(self.ADR002_FIXTURES)
        v2_issues = [
            i for i in result.structured_issues
            if i.code == ValidationCode.V2_DYNAMIC_EXPRESSION
        ]
        assert len(v2_issues) >= 1, "Expected V2_DYNAMIC_EXPRESSION from adr002_violations"

    def test_adr002_v4_in_orchestrator(self):
        """ADR-002 V4 violations (unsupported operators) appear in L6 result."""
        from agentic_mbse.sysml.types import ValidationCode
        from agentic_mbse.validation.level6_architecture import validate_architecture

        result = validate_architecture(self.ADR002_FIXTURES)
        v4_issues = [
            i for i in result.structured_issues
            if i.code == ValidationCode.V4_UNSUPPORTED_OPERATOR
        ]
        assert len(v4_issues) >= 1, "Expected V4_UNSUPPORTED_OPERATOR from adr002_violations"
        assert any("**" in i.message for i in v4_issues)

    def test_adr002_codes_cause_failure(self):
        """ADR-002 violations cause L6 to report success=False."""
        from agentic_mbse.validation.level6_architecture import validate_architecture

        result = validate_architecture(self.ADR002_FIXTURES)
        assert result.success is False


class TestLevelDistinctness:
    """Each level catches errors no other level does (FR-8).

    Distinctness means: there exists a fixture where exactly one level fails
    (for blocking levels) or reports unique metrics (for informational levels).
    """

    FIXTURES = "tests/fixtures/distinctness"

    def test_l1_syntax_error(self):
        """Syntax error fails L1; other levels may also fail on partial parse."""
        from agentic_mbse.validation.runner import run_all_checks

        result = run_all_checks(f"{self.FIXTURES}/l1_syntax_error", fail_fast=False)
        assert result.results[0].success is False  # L1 fails
        assert result.results[0].level == 1

    def test_l2_unbound_input_only(self):
        """Unbound input fails L2; all other levels pass."""
        from agentic_mbse.validation.runner import run_all_checks

        result = run_all_checks(f"{self.FIXTURES}/l2_unbound_input", fail_fast=False)
        assert result.results[0].success is True   # L1 passes
        assert result.results[1].success is False  # L2 fails
        assert result.results[1].metrics["Unbound inputs"] == 1
        # L3-L6 all pass
        for r in result.results[2:]:
            assert r.success is True, f"L{r.level} should pass but failed"

    def test_l3_circular_import_detected(self):
        """L3 now DETECTS the circular import (PIPELINE-TRUTH Item 4, row 5).

        The old exact-type ``Import`` query matched nothing (``Import`` is
        abstract), so the dependency graph was always empty and L3 always passed
        on a genuinely circular model — a validator that could not fail. The
        subtype-aware sweep plus package-keyed graph make the check functional:
        the PkgA <-> PkgB cycle is found and L3 fails. (This is the flip the old
        test's own docstring anticipated.)
        """
        from agentic_mbse.validation.runner import run_all_checks

        result = run_all_checks(f"{self.FIXTURES}/l3_circular_import", fail_fast=False)
        assert result.results[0].success is True  # L1 passes
        assert result.results[1].success is True  # L2 passes
        # L3 fails: the circular dependency is now detected.
        assert result.results[2].success is False
        assert result.results[2].metrics["Circular dependencies"] == 1

    def test_l4_reports_constraint_metrics(self):
        """L4 reports unique constraint + eligibility coverage metrics (informational, always
        passes)."""
        from agentic_mbse.validation.runner import run_all_checks

        result = run_all_checks(f"{self.FIXTURES}/l6_architecture", fail_fast=False)
        l4 = result.results[3]
        assert l4.level == 4
        assert l4.success is True
        assert "Total constraints" in l4.metrics
        assert "Admitted numerical" in l4.metrics
        assert "Malformed numerical" in l4.metrics
        assert "Non-numerical" in l4.metrics
        assert "Executable share" in l4.metrics

    def test_l5_reports_doc_coverage_metrics(self):
        """L5 reports unique documentation coverage metrics (informational, always passes)."""
        from agentic_mbse.validation.runner import run_all_checks

        result = run_all_checks(f"{self.FIXTURES}/l2_unbound_input", fail_fast=False)
        l5 = result.results[4]
        assert l5.level == 5
        assert l5.success is True
        assert "Total elements" in l5.metrics
        assert "Documented" in l5.metrics
        assert "Missing docs" in l5.metrics
        assert l5.metrics["Total elements"] >= 1

    def test_l6_architecture_only(self):
        """ADR-002 violation fails L6; L1-L3 pass."""
        from agentic_mbse.validation.runner import run_all_checks

        result = run_all_checks(f"{self.FIXTURES}/l6_architecture", fail_fast=False)
        # L1-L3 all pass
        for r in result.results[:3]:
            assert r.success is True, f"L{r.level} should pass but failed"
        # L6 fails (ADR-002 V1 violation)
        assert result.results[5].success is False
        assert result.results[5].level == 6
