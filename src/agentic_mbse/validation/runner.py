#!/usr/bin/env python3
"""
Master Quality Check Orchestrator

Runs all 6 quality levels in sequence with configurable behavior.
"""

import argparse
import sys
from pathlib import Path

# Import all level checkers
try:
    from .common import (
        EXIT_FAILURE,
        EXIT_SUCCESS,
        AggregatedResult,
        print_result,
    )
    from .level1_syntax import validate_syntax
    from .level2_structure import validate_structure
    from .level3_dataflow import validate_dataflow
    from .level4_constraints import analyze_constraints
    from .level5_traceability import validate_traceability
    from .level6_architecture import validate_architecture
except ImportError:
    # Handle direct execution (not as package)
    from common import (
        EXIT_FAILURE,
        EXIT_SUCCESS,
        AggregatedResult,
        print_result,
    )
    from level1_syntax import validate_syntax
    from level2_structure import validate_structure
    from level3_dataflow import validate_dataflow
    from level4_constraints import analyze_constraints
    from level5_traceability import validate_traceability
    from level6_architecture import validate_architecture


# Registry of all quality checks
# Levels 1-6 implemented (complete quality pyramid)
QUALITY_CHECKS = [
    ("Level 1: Syntax Validation", validate_syntax),
    ("Level 2: Structural Completeness", validate_structure),
    ("Level 3: Dependency Integrity", validate_dataflow),
    ("Level 4: Constraint Coverage", analyze_constraints),
    ("Level 5: Traceability & Documentation", validate_traceability),
    ("Level 6: Architecture & Pipeline Readiness", validate_architecture),
]


def run_all_checks(
    models_path: str,
    fail_fast: bool = True,
    specific_level: int | None = None,
    verbose: bool = False,
) -> AggregatedResult:
    """
    Run all quality checks

    Args:
        models_path: Path to models directory
        fail_fast: Stop at first failure (default True)
        specific_level: Run only this level (1-6), or None for all
        verbose: Show detailed output

    Returns:
        AggregatedResult with all check results
    """
    results = []

    # Determine which checks to run
    if specific_level is not None:
        if specific_level < 1 or specific_level > 6:
            raise ValueError(f"Level must be 1-6, got {specific_level}")
        if specific_level > len(QUALITY_CHECKS):
            raise ValueError(
                f"Level {specific_level} not yet implemented (only {len(QUALITY_CHECKS)} levels available)"
            )
        checks_to_run = [QUALITY_CHECKS[specific_level - 1]]
    else:
        checks_to_run = QUALITY_CHECKS

    print(f"\n{'='*70}")
    print("SysML Quality Validation")
    print(f"Models path: {models_path}")
    print(f"Mode: {'Fail-fast' if fail_fast else 'Complete'}")
    if specific_level:
        print(f"Running: Level {specific_level} only")
    print(f"{'='*70}")

    # Run checks
    for name, check_func in checks_to_run:
        if verbose:
            print(f"\nRunning: {name}...")

        try:
            result = check_func(models_path)
            results.append(result)

            # Print result
            print_result(result)

            # Fail-fast mode: stop on first failure
            if fail_fast and not result.success:
                print(f"\n❌ Stopping at first failure (Level {result.level})")
                print("   Use --complete to run all levels regardless of failures")
                break

        except Exception as e:
            print(f"\n❌ Error running {name}: {e}")
            if verbose:
                import traceback

                traceback.print_exc()

            # Treat exceptions as failures
            if fail_fast:
                break

    # Calculate aggregate stats
    passed = sum(1 for r in results if r.success)
    failed = sum(1 for r in results if not r.success)

    aggregated = AggregatedResult(
        results=results, total_checks=len(results), passed=passed, failed=failed
    )

    # Print summary
    print(f"\n{'='*70}")
    print("Summary")
    print(f"{'='*70}")
    print(f"Checks run: {aggregated.total_checks}")
    print(f"✅ Passed: {aggregated.passed}")
    print(f"❌ Failed: {aggregated.failed}")

    if aggregated.overall_success:
        print("\n✅ All quality checks passed!")
    else:
        print("\n❌ Quality checks failed")
        print("   Review issues above and fix before proceeding")

    return aggregated


def main() -> int:
    """Entry point"""
    parser = argparse.ArgumentParser(
        description="SysML Quality Validation - Run all 6 quality levels",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quick validation (fail-fast, default)
  python run_all_checks.py models/

  # Complete validation (run all levels)
  python run_all_checks.py --complete models/

  # Run specific level only
  python run_all_checks.py --level=1 models/

  # Verbose output
  python run_all_checks.py --verbose --complete models/
        """,
    )

    parser.add_argument(
        "path",
        nargs="?",
        default="models",
        help="Path to models directory (default: models)",
    )

    parser.add_argument(
        "--complete",
        action="store_true",
        help="Run all levels regardless of failures (default: fail-fast)",
    )

    parser.add_argument(
        "--level",
        type=int,
        choices=range(1, 7),
        metavar="N",
        help="Run only level N (1-6)",
    )

    parser.add_argument(
        "--verbose", action="store_true", help="Verbose output with detailed diagnostics"
    )

    args = parser.parse_args()

    # Validate path
    if not Path(args.path).exists():
        print(f"Error: Path does not exist: {args.path}")
        return EXIT_FAILURE

    # Run checks
    fail_fast = not args.complete
    result = run_all_checks(
        models_path=args.path,
        fail_fast=fail_fast,
        specific_level=args.level,
        verbose=args.verbose,
    )

    return EXIT_SUCCESS if result.overall_success else EXIT_FAILURE


if __name__ == "__main__":
    sys.exit(main())
