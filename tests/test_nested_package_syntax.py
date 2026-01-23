"""
Tests for Package Declaration Syntax Support

This test suite documents which package declaration syntaxes are valid SysML v2.

KEY FINDINGS:
- Simple names work: `package SimplePackage { }`
- Hierarchical nesting works: `package A { package B { } }`
- Qualified names DO NOT work: `package A::B::C { }` → syntax error

The syntax `package A::B::C { }` is INVALID per the SysML v2 specification itself,
not just unsupported by syside. The grammar rule is:

    PackageDeclaration = 'package' Identification

Where `Identification` accepts only a simple NAME, not a QualifiedName.
The `::` operator is only valid for REFERENCES (imports), not DECLARATIONS.

See: SysML v2 Specification Part 1, section 8.2.2.5 (lines 10297-10298)

Created: 2026-01-23
"""

import pytest
from pathlib import Path
import tempfile
import shutil


@pytest.fixture
def temp_models_dir():
    """Create temporary models directory with test files"""
    tmpdir = tempfile.mkdtemp()
    models_path = Path(tmpdir) / "models"
    models_path.mkdir()
    (models_path / "library").mkdir()
    yield models_path
    shutil.rmtree(tmpdir)


class TestSupportedPackageSyntax:
    """Tests for package declaration syntaxes that ARE supported"""

    def test_simple_package_parses(self, temp_models_dir):
        """Simple package declaration parses successfully"""
        file_path = temp_models_dir / "library" / "simple.sysml"
        file_path.write_text("""
            package SimplePackage {
                part def 'Test Part' {
                    attribute x : ScalarValues::Real;
                }
            }
        """)

        from agentic_mbse.validation.level1_syntax import validate_syntax

        result = validate_syntax(str(temp_models_dir))
        assert result.success, f"Simple package failed to parse: {result.issues}"

    def test_hierarchical_nesting_parses(self, temp_models_dir):
        """Hierarchical nesting `package A { package B { } }` parses successfully"""
        file_path = temp_models_dir / "library" / "nested.sysml"
        file_path.write_text("""
            package OuterPackage {
                package InnerPackage {
                    part def 'Test Part';
                }
            }
        """)

        from agentic_mbse.validation.level1_syntax import validate_syntax

        result = validate_syntax(str(temp_models_dir))
        assert result.success, f"Hierarchical nesting failed to parse: {result.issues}"

    def test_deep_hierarchical_nesting_parses(self, temp_models_dir):
        """Deep hierarchical nesting works"""
        file_path = temp_models_dir / "library" / "deep.sysml"
        file_path.write_text("""
            package Level1 {
                package Level2 {
                    package Level3 {
                        part def 'Deep Part';
                    }
                }
            }
        """)

        from agentic_mbse.validation.level1_syntax import validate_syntax

        result = validate_syntax(str(temp_models_dir))
        assert result.success, f"Deep nesting failed to parse: {result.issues}"

    def test_underscore_separated_names_parse(self, temp_models_dir):
        """Underscore-separated names (recommended alternative) parse successfully"""
        file_path = temp_models_dir / "library" / "underscore.sysml"
        file_path.write_text("""
            package Foundation_Types {
                attribute def 'Mass';
                attribute def 'Temperature';
            }

            package Foundation_Units {
                attribute def 'Kilogram';
                attribute def 'Kelvin';
            }

            package Foundation_Materials {
                part def 'Steel';
                part def 'Aluminum';
            }
        """)

        from agentic_mbse.validation.level1_syntax import validate_syntax

        result = validate_syntax(str(temp_models_dir))
        assert result.success, f"Underscore-separated names failed to parse: {result.issues}"

    def test_qualified_names_in_imports_work(self, temp_models_dir):
        """The `::` operator works for IMPORTS (references), just not declarations"""
        file_path = temp_models_dir / "library" / "imports.sysml"
        file_path.write_text("""
            import ScalarValues::*;
            import SI::*;

            package TestImports {
                part def 'Test Part' {
                    attribute mass : ScalarValues::Real;
                }
            }
        """)

        from agentic_mbse.validation.level1_syntax import validate_syntax

        result = validate_syntax(str(temp_models_dir))
        assert result.success, f"Qualified names in imports failed: {result.issues}"


class TestUnsupportedPackageSyntax:
    """Tests documenting package declaration syntaxes that are NOT supported by syside"""

    def test_qualified_name_package_fails(self, temp_models_dir):
        """Qualified name `package A::B::C { }` is NOT supported - syntax error at `::`"""
        file_path = temp_models_dir / "library" / "qualified.sysml"
        file_path.write_text("""
            package MyProject::Library::Components {
                part def 'Test Part';
            }
        """)

        from agentic_mbse.validation.level1_syntax import validate_syntax

        result = validate_syntax(str(temp_models_dir))
        # This SHOULD fail - document the limitation
        assert not result.success, "Qualified name syntax unexpectedly succeeded"
        assert any(":" in issue for issue in result.issues), "Error should mention unexpected ':'"

    def test_two_level_qualified_name_fails(self, temp_models_dir):
        """Even two-level qualified names `package A::B { }` fail"""
        file_path = temp_models_dir / "library" / "two_level.sysml"
        file_path.write_text("""
            package Project::Library {
                part def 'Simple Part';
            }
        """)

        from agentic_mbse.validation.level1_syntax import validate_syntax

        result = validate_syntax(str(temp_models_dir))
        assert not result.success, "Two-level qualified name unexpectedly succeeded"

    def test_foundation_pattern_with_colons_fails(self, temp_models_dir):
        """Customer pattern `Foundation::Types` does NOT work"""
        file_path = temp_models_dir / "library" / "foundation.sysml"
        file_path.write_text("""
            package Foundation::Types {
                attribute def 'Mass';
            }
        """)

        from agentic_mbse.validation.level1_syntax import validate_syntax

        result = validate_syntax(str(temp_models_dir))
        assert not result.success, "Foundation::Types syntax unexpectedly succeeded"


class TestRecommendedPatterns:
    """Tests for patterns we recommend to customers"""

    def test_recommended_multi_file_pattern(self, temp_models_dir):
        """Recommended pattern: unique names + aggregator package"""
        # File 1: Library package with unique name
        lib_file = temp_models_dir / "library" / "foundation_types.sysml"
        lib_file.write_text("""
            package Foundation_Types {
                attribute def 'Mass';
                attribute def 'Temperature';
            }
        """)

        # File 2: Another unique package
        units_file = temp_models_dir / "library" / "foundation_units.sysml"
        units_file.write_text("""
            package Foundation_Units {
                attribute def 'Kilogram';
            }
        """)

        # File 3: Aggregator that re-exports
        agg_file = temp_models_dir / "library" / "foundation.sysml"
        agg_file.write_text("""
            package Foundation {
                public import Foundation_Types::*;
                public import Foundation_Units::*;
            }
        """)

        from agentic_mbse.validation.level1_syntax import validate_syntax

        result = validate_syntax(str(temp_models_dir))
        assert result.success, f"Recommended pattern failed: {result.issues}"

    def test_recommended_single_file_nested_pattern(self, temp_models_dir):
        """Recommended pattern: hierarchical nesting in single file"""
        file_path = temp_models_dir / "library" / "foundation.sysml"
        file_path.write_text("""
            package Foundation {
                package Types {
                    attribute def 'Mass';
                    attribute def 'Temperature';
                }

                package Units {
                    attribute def 'Kilogram';
                    attribute def 'Kelvin';
                }

                package Materials {
                    part def 'Steel';
                    part def 'Aluminum';
                }
            }
        """)

        from agentic_mbse.validation.level1_syntax import validate_syntax

        result = validate_syntax(str(temp_models_dir))
        assert result.success, f"Hierarchical single-file pattern failed: {result.issues}"
