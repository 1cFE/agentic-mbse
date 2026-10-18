Plan ARXIV-EXTRACTION from .project/active/arxiv-extraction/design.md (spec.md, spec_review.md, design_review.md in the same folder). Write plan.md beside it with phases and checkboxes.

Guidance:
- [OWNER] Goal: consumers keep Pandoc on PATH safely and drop their workarounds. [OWNER] Reserved gates: default-on is open (keep the one-constant flip); no removal/rename of public PipelineConfig fields or CLI flags.
- [AGENT] Phase 1 builds the trimmed real fixture from .project/active/arxiv-extraction/ref/2610.14224.html (untracked source; the committed fixture goes under tests/) and the Pandoc-free selection test, so the paper boundary is locked first. Generated PDF fixtures per the spike (.project/active/arxiv-extraction/spike-margin-stamp.md).
- [AGENT] Order phases so each lands green and is independently committable: shared module + refactor of existing behavior with existing tests passing before new behavior; then identity; then opt-out/CLI; then images; then warnings; then docs and --check. Adjust if the design implies a better order.
- [AGENT] Test-first per phase. Green = focused extraction tests (test_pandoc_convert.py, test_pipeline.py, test_web_backend.py, test_extract_cli.py, plus new test files) pass, `uv run ruff check`, `uv run ruff format --check` and `uv run mypy src/` clean on touched files, and no new failures in `uv run pytest tests/` versus the base 8b027bbc. Record the baseline failure set in phase 0.
- Include the live Harness² check (https://arxiv.org/html/2610.14224 and its PDF) as a final, recorded, non-blocking step.
End with ARTIFACT: <path>.
