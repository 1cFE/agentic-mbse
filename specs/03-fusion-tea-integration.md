# Spec 03: Fusion-tea Integration

## Priority: LAST — Only after extraction quality is proven and routing works

## Problem

fusion-tea's `scripts/zotero_ingest.py` calls `agentic-mbse extract` via subprocess. Phase 4 of the original design calls for switching to the `SourceRouter` Python API. But this only makes sense if the doc_ingest pipeline produces results as good as or better than the current pipeline.

## Prerequisites

- [ ] Spec 00 test harness shows quality parity with baseline (fusion-tea extractions)
- [ ] Spec 01 extraction pipeline is wired in and measured
- [ ] Spec 02 source discovery works on at least some of our test DOIs

## What Changes In fusion-tea

### 1. Replace subprocess calls with Python API

Current (`zotero_ingest.py:95-98`):
```python
subprocess.run(["uv", "run", "agentic-mbse", "extract", pdf_path, "--output", output_dir, ...])
```

New:
```python
from doc_ingest.source_router import SourceRouter
from doc_ingest.types import DocumentIdentifiers

router = create_pipeline(output_dir)
result = router.extract(
    DocumentIdentifiers(doi=doi, local_path=str(pdf_path)),
    output_dir=output_dir,
)
```

### 2. Use provenance for manifest

Current: Writes to `MANIFEST.jsonl` with basic metadata.
New: Include outcome, failure_category, converter_used from provenance.

### 3. Auto-generate triage report

After batch run: call `_generate_triage_report(output_dir, report_path)`.

## What We Don't Know

- Whether the Python API import path works from fusion-tea (it's a separate repo — may need `pip install -e ../agentic-mbse_doc-ingest`)
- Whether the provenance format is compatible with fusion-tea's existing MANIFEST.jsonl consumers
- Whether the existing `--enhance` / `--structure-only` flags from the old CLI need equivalents in the new API

## Acceptance Criteria

- [ ] `python scripts/zotero_ingest.py --dry-run` still works (no import errors)
- [ ] End-to-end: ingest 1 paper via Zotero API, produces output.md + provenance.json
- [ ] Quality is >= existing extractions (measured by test harness)
- [ ] MANIFEST.jsonl includes outcome/failure_category fields
- [ ] Triage report generated after batch run with failures
