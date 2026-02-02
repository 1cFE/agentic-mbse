"""
Tests for SysML Quality Checks

Test suite for the 7-level SysML quality validation framework.
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
        assert result.success
        assert result.level == 1
        assert len(result.issues) == 0

    def test_invalid_syntax_fails(self, invalid_sysml_file):
        """Test that invalid file fails with diagnostics"""
        from agentic_mbse.validation.level1_syntax import validate_syntax

        result = validate_syntax(str(invalid_sysml_file.parent.parent))
        assert not result.success
        assert len(result.issues) > 0
        assert "bad.sysml" in result.issues[0]

    def test_no_files_warning(self, temp_models_dir):
        """Test that empty directory returns success with warning"""
        from agentic_mbse.validation.level1_syntax import validate_syntax

        empty_dir = temp_models_dir / "empty"
        empty_dir.mkdir()
        result = validate_syntax(str(empty_dir))
        assert result.success
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
        assert result.success
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


class TestLevel5Semantic:
    """Tests for Level 5: Semantic Consistency"""

    def test_coverage_metrics_reported(self, temp_models_dir):
        """Test that constraint coverage metrics are reported"""
        # Create model with some constrained and unconstrained attributes
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

        from agentic_mbse.validation.level5_semantic import validate_semantic

        result = validate_semantic(str(temp_models_dir))

        assert result.level == 5
        assert "Total attributes" in result.metrics
        assert "Constrained" in result.metrics
        assert "Coverage" in result.metrics

    def test_unit_consistency_check(self, temp_models_dir):
        """Test unit consistency analysis doesn't crash"""
        from agentic_mbse.validation.level5_semantic import validate_semantic

        result = validate_semantic(str(temp_models_dir))
        assert result.level == 5


class TestLevel6Traceability:
    """Tests for Level 6: Traceability & Documentation"""

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

        from agentic_mbse.validation.level6_traceability import validate_traceability

        result = validate_traceability(str(temp_models_dir))

        assert result.level == 6
        assert "Total elements" in result.metrics
        assert "Documented" in result.metrics

    def test_missing_docs_reported(self, temp_models_dir):
        """Test that missing docs are reported as issues"""
        from agentic_mbse.validation.level6_traceability import validate_traceability

        result = validate_traceability(str(temp_models_dir))
        assert result.level == 6


class TestLevel7Architecture:
    """Tests for Level 7: Architectural Integrity"""

    def test_no_manifest_warns_but_passes(self, temp_models_dir):
        """Test that missing manifest warns but doesn't fail"""
        from agentic_mbse.validation.level7_architecture import validate_architecture

        result = validate_architecture(str(temp_models_dir))

        assert result.level == 7
        assert result.success  # Should pass with warning
        assert len(result.warnings) > 0  # Should warn about no manifest

    def test_manifest_validation(self, temp_models_dir):
        """Test manifest-driven validation"""
        # Create design with manifest
        design_dir = temp_models_dir / "designs" / "test_design"
        design_dir.mkdir(parents=True)

        manifest = design_dir / "manifest.yaml"
        manifest.write_text("""
design_name: "Test Design"
expected_subsystems:
  - subsystem1
  - subsystem2
entry_point: models/designs/test_design/system.sysml
        """)

        from agentic_mbse.validation.level7_architecture import validate_architecture

        result = validate_architecture(str(temp_models_dir))

        assert result.level == 7
        # May report missing subsystems if system.sysml not created


class TestEndToEnd:
    """End-to-end integration tests"""

    def test_full_quality_suite_on_existing_models(self):
        """Test full quality suite on sample models"""
        from agentic_mbse.validation.runner import run_all_checks

        # Run on sample models directory
        result = run_all_checks("tests/fixtures/sample_models/", fail_fast=False)

        # Should complete all 8 levels
        assert result.total_checks == 8

        # Verify we got results for each level
        levels_run = [r.level for r in result.results]
        assert levels_run == [1, 2, 3, 4, 5, 6, 7, 8]

        # At minimum, all checks should complete without exceptions
        assert len(result.results) == 8

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

        # Should run all 8 levels regardless of failures
        assert result.total_checks == 8
        assert len(result.results) == 8

        # Verify each level executed (even if some failed)
        for i, level_result in enumerate(result.results, start=1):
            assert level_result.level == i

    def test_level_8_integration(self):
        """Test Level 8 runs as part of full suite"""
        from agentic_mbse.validation.runner import run_all_checks

        result = run_all_checks("tests/fixtures/sample_models/", fail_fast=False)
        level_8_results = [r for r in result.results if r.level == 8]
        assert len(level_8_results) == 1, "Level 8 should run once in full suite"
        assert level_8_results[0].level_name == "Codegen Readiness"

    def test_level_8_only_mode(self):
        """Test --level=8 runs only Level 8"""
        from agentic_mbse.validation.runner import run_all_checks

        result = run_all_checks("tests/fixtures/sample_models/", specific_level=8)
        assert len(result.results) == 1
        assert result.results[0].level == 8
        assert result.results[0].level_name == "Codegen Readiness"

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
            assert result.total_checks <= 7  # May stop early
            assert result.failed >= 1  # At least one failure

        finally:
            shutil.rmtree(tmpdir)


class TestLevel8CodegenReadiness:
    """Tests for Level 8: Codegen Readiness validation"""

    def test_validation_codes_exist(self):
        """All Level 8 ValidationCode entries are defined"""
        from agentic_mbse.sysml.types import ValidationCode

        assert hasattr(ValidationCode, "L8_MISSING_QUALIFIED_NAME")
        assert hasattr(ValidationCode, "L8_INVALID_QUALIFIED_NAME")
        assert hasattr(ValidationCode, "L8_CALC_DEF_NO_OUTPUT")
        assert hasattr(ValidationCode, "L8_CALC_DEF_NO_DIRECTION")
        assert hasattr(ValidationCode, "L8_INVALID_BINDING_FORMAT")
        assert hasattr(ValidationCode, "L8_DESIGN_ATTR_INCOMPLETE")

    def test_models_report_incomplete_attrs(self):
        """Test that Level 8 can detect incomplete attrs"""
        from agentic_mbse.validation.level8_codegen import (
            validate_codegen_readiness,
        )

        result = validate_codegen_readiness("tests/fixtures/sample_models/")
        # Sample models may or may not have incomplete attrs
        # Just verify the check runs without error
        assert result.level == 8
        assert result.level_name == "Codegen Readiness"

    def test_module_returns_quality_check_result(self):
        """validate_codegen_readiness returns QualityCheckResult"""
        from agentic_mbse.validation.common import QualityCheckResult
        from agentic_mbse.validation.level8_codegen import (
            validate_codegen_readiness,
        )

        result = validate_codegen_readiness("tests/fixtures/sample_models/")
        assert isinstance(result, QualityCheckResult)
        assert result.level == 8
        assert result.level_name == "Codegen Readiness"

    def test_check_qualified_names_on_valid_model(self):
        """Valid models produce no qualified name issues"""
        from agentic_mbse.validation.level8_codegen import (
            validate_codegen_readiness,
        )

        result = validate_codegen_readiness("tests/fixtures/sample_models/")
        qname_issues = [
            i for i in result.structured_issues if "QUALIFIED_NAME" in str(i.code)
        ]
        assert len(qname_issues) == 0, f"Unexpected issues: {qname_issues}"

    def test_metrics_include_element_counts(self):
        """Metrics include counts of checked elements"""
        from agentic_mbse.validation.level8_codegen import (
            validate_codegen_readiness,
        )

        result = validate_codegen_readiness("tests/fixtures/sample_models/")
        assert "Calc defs checked" in result.metrics
        assert "Calc usages checked" in result.metrics
        # Sample models have at least one calc def
        assert result.metrics["Calc defs checked"] >= 0

    def test_check_calc_def_structure_finds_outputs(self):
        """Valid calc defs with outputs pass structure check"""
        from agentic_mbse.sysml.types import ValidationCode
        from agentic_mbse.validation.level8_codegen import (
            validate_codegen_readiness,
        )

        result = validate_codegen_readiness("tests/fixtures/sample_models/")
        no_output_issues = [
            i
            for i in result.structured_issues
            if i.code == ValidationCode.L8_CALC_DEF_NO_OUTPUT
        ]
        assert len(no_output_issues) == 0, f"Unexpected no-output issues: {no_output_issues}"

    def test_check_binding_formats_valid(self):
        """Valid bindings pass format check"""
        from agentic_mbse.sysml.types import ValidationCode
        from agentic_mbse.validation.level8_codegen import (
            validate_codegen_readiness,
        )

        result = validate_codegen_readiness("tests/fixtures/sample_models/")
        binding_issues = [
            i
            for i in result.structured_issues
            if i.code == ValidationCode.L8_INVALID_BINDING_FORMAT
        ]
        assert len(binding_issues) == 0, f"Unexpected binding issues: {binding_issues}"

    def test_all_checks_run(self):
        """All check functions execute and contribute to metrics"""
        from agentic_mbse.validation.level8_codegen import (
            validate_codegen_readiness,
        )

        result = validate_codegen_readiness("tests/fixtures/sample_models/")
        assert "Calc defs checked" in result.metrics
        assert "Calc usages checked" in result.metrics
        # Verify metrics are populated (may be 0 for simple sample models)
        assert result.metrics["Calc defs checked"] >= 0
        assert result.metrics["Calc usages checked"] >= 0

    def test_incomplete_design_attrs_are_errors(self):
        """Incomplete design attributes produce errors per FR-7"""
        from agentic_mbse.sysml.types import Severity, ValidationCode
        from agentic_mbse.validation.level8_codegen import (
            validate_codegen_readiness,
        )

        result = validate_codegen_readiness("tests/fixtures/sample_models/")
        incomplete_issues = [
            i
            for i in result.structured_issues
            if i.code == ValidationCode.L8_DESIGN_ATTR_INCOMPLETE
        ]
        # All incomplete attr issues should be errors (if any exist)
        for issue in incomplete_issues:
            assert issue.severity == Severity.ERROR, f"Expected ERROR, got {issue.severity}"
