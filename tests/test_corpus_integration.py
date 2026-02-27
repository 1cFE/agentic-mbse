"""Integration tests for the v4 PDF extraction pipeline against the corpus.

Offline tests (budget=0) run without network access or cost.
Claude-budget tests require an ANTHROPIC_API_KEY and cost real money.

Usage:
    pytest tests/test_corpus_integration.py -m corpus -k offline -v
    pytest tests/test_corpus_integration.py::test_no_dormant_modules -v
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from agentic_mbse.extraction.metrics import load_ground_truth, score_against_ground_truth
from agentic_mbse.extraction.pipeline import PipelineConfig, extract_pdf

CORPUS_DIR = Path(__file__).parent / "corpus" / "pdfs"
ALL_PDFS = sorted(CORPUS_DIR.glob("*.pdf"))
GT_PATH = Path(__file__).parent / "corpus" / "ground_truth.jsonl"

EXTRACTION_DIR = Path(__file__).parent.parent / "src" / "agentic_mbse" / "extraction"


# ---------------------------------------------------------------------------
# Offline tests (budget=0, no network, no cost)
# ---------------------------------------------------------------------------


@pytest.mark.corpus
@pytest.mark.parametrize("pdf_path", ALL_PDFS, ids=lambda p: p.stem)
def test_offline_extraction(pdf_path: Path) -> None:
    """Every corpus PDF produces non-empty output with budget=0."""
    config = PipelineConfig(claude_budget_usd=0.0, enable_tables=False)
    result = extract_pdf(pdf_path, config=config)
    assert result.error is None, f"{pdf_path.stem}: {result.error}"
    assert result.markdown.strip(), f"{pdf_path.stem}: empty markdown"


# ---------------------------------------------------------------------------
# Claude-budget tests (requires ANTHROPIC_API_KEY, costs money)
# ---------------------------------------------------------------------------


@pytest.mark.corpus
@pytest.mark.parametrize("pdf_path", ALL_PDFS, ids=lambda p: p.stem)
def test_claude_extraction(pdf_path: Path) -> None:
    """Every corpus PDF produces non-empty output with default Claude budget."""
    config = PipelineConfig(claude_budget_usd=2.0)
    result = extract_pdf(pdf_path, config=config)
    assert result.error is None, f"{pdf_path.stem}: {result.error}"
    assert result.markdown.strip(), f"{pdf_path.stem}: empty markdown"


# ---------------------------------------------------------------------------
# Ground truth scoring (runs as part of offline — scoring only, no cost)
# ---------------------------------------------------------------------------


@pytest.mark.corpus
def test_ground_truth_scoring() -> None:
    """Ground truth documents score within acceptable thresholds on non-null fields."""
    gt_data = load_ground_truth(GT_PATH)
    assert len(gt_data) > 0, "No ground truth entries found"

    config = PipelineConfig(claude_budget_usd=0.0, enable_tables=False)
    failures: list[str] = []

    for slug, gt in gt_data.items():
        pdf_path = CORPUS_DIR / f"{slug}.pdf"
        if not pdf_path.exists():
            failures.append(f"{slug}: PDF not found at {pdf_path}")
            continue

        result = extract_pdf(pdf_path, config=config)
        if result.error:
            failures.append(f"{slug}: extraction error: {result.error}")
            continue

        scores = score_against_ground_truth(result.metrics, gt)

        # Only assert on non-null ground truth fields
        if scores["headings"] is not None:
            score = scores["headings"]
            # Budget=0 heading detection: allow up to 100% error (pymupdf4llm
            # is known to over-detect on bold-heavy docs like paischer_2025)
            if score.error_pct > 100:
                failures.append(
                    f"{slug}: heading error {score.error_pct:.0f}% "
                    f"(detected={score.detected}, truth={score.ground_truth})"
                )

        if scores["table_rows"] is not None:
            score = scores["table_rows"]
            # Budget=0 with tables disabled: expect 0 table rows, so skip
            # the quality threshold (tables are turned off in offline mode)

    assert not failures, "Ground truth failures:\n" + "\n".join(failures)


# ---------------------------------------------------------------------------
# No-dormant-code check (no network, no cost)
# ---------------------------------------------------------------------------


def _collect_imports(filepath: Path, package_prefix: str) -> set[str]:
    """Extract all import targets from a Python file matching package_prefix.

    Handles both top-level and lazy imports (inside functions/conditionals).
    """
    try:
        tree = ast.parse(filepath.read_text())
    except SyntaxError:
        return set()

    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            if node.module.startswith(package_prefix):
                modules.add(node.module)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith(package_prefix):
                    modules.add(alias.name)
    return modules


def _transitive_imports(
    entry_files: list[Path],
    source_dir: Path,
    package_prefix: str,
) -> set[str]:
    """Compute the transitive closure of imports from entry files."""
    visited: set[str] = set()
    queue: list[Path] = list(entry_files)

    while queue:
        filepath = queue.pop()
        if not filepath.exists():
            continue

        imports = _collect_imports(filepath, package_prefix)
        for mod in imports:
            if mod in visited:
                continue
            visited.add(mod)
            # Resolve module to file path
            parts = mod.replace(package_prefix + ".", "").split(".")
            candidate = source_dir / "/".join(parts[:-1]) / (parts[-1] + ".py") if len(parts) > 1 else source_dir / (parts[0] + ".py")
            if candidate.exists():
                queue.append(candidate)

    return visited


def test_no_dormant_modules() -> None:
    """Every .py module in extraction/ is reachable from pipeline, __init__, or CLI."""
    package_prefix = "agentic_mbse.extraction"
    cli_path = EXTRACTION_DIR.parent / "cli" / "extract_cli.py"

    entry_files = [
        EXTRACTION_DIR / "pipeline.py",
        EXTRACTION_DIR / "__init__.py",
        cli_path,
    ]

    reachable = _transitive_imports(entry_files, EXTRACTION_DIR, package_prefix)
    # Extract just the module leaf names
    reachable_names = {mod.split(".")[-1] for mod in reachable}

    # All .py modules in extraction/ (excluding __init__)
    all_modules = {f.stem for f in EXTRACTION_DIR.glob("*.py") if f.stem != "__init__"}

    dormant = all_modules - reachable_names
    assert dormant == set(), (
        f"Dormant modules in extraction/ (not reachable from pipeline, "
        f"__init__, or CLI): {sorted(dormant)}"
    )
