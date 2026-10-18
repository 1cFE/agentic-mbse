# Repository baseline at `ebb3d467`

Recorded 2026-10-18 for Item 3 Phase 1 (plan Step 1a). This list is the green rule's reference for every later phase: a later phase may not add a test failure, mypy error or ruff finding that is not listed here.

- **Source identity.** `git diff --stat ebb3d467 HEAD -- src tests pyproject.toml uv.lock` was empty (HEAD `0d69c883`), so the checkout was used. The suite was run in the checkout with the Phase 1 edits set aside (the first run overlapped with edits and was discarded; a `git archive` export run added 8 environment-only failures from console-script paths, so it was not used).
- **SYSIDE_LICENSE_KEY:** present in `.env`.

## `uv run pytest tests/`

6 failed, 3947 passed, 8 skipped, 17 deselected, 1 xfailed, 6 warnings in 110.08s (0:01:50)

Failing test ids (none touch validation; they are pandoc, equation-detection and index-script tests):

- `tests/test_check.py::TestProbePandoc::test_reports_length_of_converted_markdown`
- `tests/test_check.py::TestProbePandoc::test_conversion_error`
- `tests/test_check.py::TestRunCheck::test_capability_predicts_whether_extract_substitutes[identified-with-html]`
- `tests/test_equations.py::TestDetectEquations::test_returns_detected_equations`
- `tests/test_index.py::TestScriptBackwardCompat::test_generate_index_script_runs`
- `tests/test_index.py::TestScriptBackwardCompat::test_read_section_script_runs`

## `uv run mypy src/`

Found 97 errors in 19 files (checked 89 source files)

```text
src/agentic_mbse/extraction/postprocess.py:104: error: Returning Any from function declared to return "str"  [no-any-return]
src/agentic_mbse/extraction/postprocess.py:332: error: Returning Any from function declared to return "str"  [no-any-return]
src/agentic_mbse/extraction/postprocess.py:333: error: Returning Any from function declared to return "str"  [no-any-return]
src/agentic_mbse/extraction/postprocess.py:360: error: Returning Any from function declared to return "str"  [no-any-return]
src/agentic_mbse/extraction/equations.py:44: error: Cannot find implementation or library stub for module named "docling_ibm_models.layoutmodel.layout_predictor"  [import-not-found]
src/agentic_mbse/extraction/equations.py:55: error: Cannot find implementation or library stub for module named "huggingface_hub"  [import-not-found]
src/agentic_mbse/extraction/equations.py:141: error: Skipping analyzing "pymupdf": module is installed, but missing library stubs or py.typed marker  [import-untyped]
src/agentic_mbse/extraction/equations.py:154: error: Cannot find implementation or library stub for module named "PIL"  [import-not-found]
src/agentic_mbse/extraction/http.py:62: error: Returning Any from function declared to return "str | None"  [no-any-return]
src/agentic_mbse/extraction/tables.py:161: error: Library stubs not installed for "pandas"  [import-untyped]
src/agentic_mbse/extraction/tables.py:361: error: Cannot find implementation or library stub for module named "gmft.auto"  [import-not-found]
src/agentic_mbse/extraction/tables.py:362: error: Cannot find implementation or library stub for module named "gmft.pdf_bindings.pdfium"  [import-not-found]
src/agentic_mbse/extraction/tables.py:432: error: Cannot find implementation or library stub for module named "gmft.detectors.img2table"  [import-not-found]
src/agentic_mbse/sysml/helpers.py:39: error: Returning Any from function declared to return "str | None"  [no-any-return]
src/agentic_mbse/sysml/helpers.py:122: error: Returning Any from function declared to return "str"  [no-any-return]
src/agentic_mbse/sysml/helpers.py:133: error: Returning Any from function declared to return "str"  [no-any-return]
src/agentic_mbse/extraction/base.py:119: error: Returning Any from function declared to return "bool"  [no-any-return]
src/agentic_mbse/extraction/base.py:175: error: Unused "type: ignore" comment  [unused-ignore]
src/agentic_mbse/extraction/base.py:193: error: Unused "type: ignore" comment  [unused-ignore]
src/agentic_mbse/extraction/pymupdf_backend.py:95: error: Skipping analyzing "pymupdf4llm.helpers.pymupdf_rag": module is installed, but missing library stubs or py.typed marker  [import-untyped]
src/agentic_mbse/extraction/docling_backend.py:25: error: Unused "type: ignore" comment  [unused-ignore]
src/agentic_mbse/extraction/docling_backend.py:25: error: Cannot find implementation or library stub for module named "docling.datamodel.base_models"  [import-not-found]
src/agentic_mbse/extraction/docling_backend.py:26: error: Unused "type: ignore" comment  [unused-ignore]
src/agentic_mbse/extraction/docling_backend.py:26: error: Cannot find implementation or library stub for module named "docling.datamodel.pipeline_options"  [import-not-found]
src/agentic_mbse/extraction/docling_backend.py:29: error: Unused "type: ignore" comment  [unused-ignore]
src/agentic_mbse/extraction/docling_backend.py:29: error: Cannot find implementation or library stub for module named "docling.document_converter"  [import-not-found]
src/agentic_mbse/extraction/docling_backend.py:136: error: Returning Any from function declared to return "ExtractionResult"  [no-any-return]
src/agentic_mbse/sysml/binding.py:215: error: Returning Any from function declared to return "str | None"  [no-any-return]
src/agentic_mbse/sysml/binding.py:223: error: Returning Any from function declared to return "str | None"  [no-any-return]
src/agentic_mbse/extraction/check.py:102: error: Cannot find implementation or library stub for module named "gmft.auto"  [import-not-found]
src/agentic_mbse/extraction/check.py:107: error: Cannot find implementation or library stub for module named "gmft.detectors.img2table"  [import-not-found]
src/agentic_mbse/extraction/check.py:112: error: Cannot find implementation or library stub for module named "docling"  [import-not-found]
src/agentic_mbse/extraction/html_sanitize.py:55: error: Library stubs not installed for "lxml"  [import-untyped]
src/agentic_mbse/extraction/html_sanitize.py:74: error: Argument 1 to "search" of "Pattern" has incompatible type "str | AttributeValueList | None"; expected "str"  [arg-type]
src/agentic_mbse/extraction/html_sanitize.py:79: error: Argument 1 to "search" of "Pattern" has incompatible type "str | AttributeValueList | None"; expected "str"  [arg-type]
src/agentic_mbse/validation/common.py:203: error: Unused "type: ignore" comment  [unused-ignore]
src/agentic_mbse/validation/level5_traceability.py:27: error: Cannot find implementation or library stub for module named "common"  [import-not-found]
src/agentic_mbse/validation/level5_traceability.py:27: error: Name "EXIT_FAILURE" already defined (possibly by an import)  [no-redef]
src/agentic_mbse/validation/level5_traceability.py:27: error: Name "EXIT_SUCCESS" already defined (possibly by an import)  [no-redef]
src/agentic_mbse/validation/level5_traceability.py:27: error: Name "QualityCheckResult" already defined (possibly by an import)  [no-redef]
src/agentic_mbse/validation/level5_traceability.py:27: error: Name "discover_sysml_files" already defined (possibly by an import)  [no-redef]
src/agentic_mbse/validation/level5_traceability.py:27: error: Name "get_element_location" already defined (possibly by an import)  [no-redef]
src/agentic_mbse/validation/level5_traceability.py:27: error: Name "get_qualified_name" already defined (possibly by an import)  [no-redef]
src/agentic_mbse/validation/level5_traceability.py:27: error: Name "load_sysml_model" already defined (possibly by an import)  [no-redef]
src/agentic_mbse/validation/level5_traceability.py:27: error: Name "print_header" already defined (possibly by an import)  [no-redef]
src/agentic_mbse/validation/level5_traceability.py:27: error: Name "print_result" already defined (possibly by an import)  [no-redef]
src/agentic_mbse/validation/level3_dataflow.py:27: error: Cannot find implementation or library stub for module named "common"  [import-not-found]
src/agentic_mbse/validation/level3_dataflow.py:27: error: Name "EXIT_FAILURE" already defined (possibly by an import)  [no-redef]
src/agentic_mbse/validation/level3_dataflow.py:27: error: Name "EXIT_SUCCESS" already defined (possibly by an import)  [no-redef]
src/agentic_mbse/validation/level3_dataflow.py:27: error: Name "QualityCheckResult" already defined (possibly by an import)  [no-redef]
src/agentic_mbse/validation/level3_dataflow.py:27: error: Name "discover_sysml_files" already defined (possibly by an import)  [no-redef]
src/agentic_mbse/validation/level3_dataflow.py:27: error: Name "load_sysml_model" already defined (possibly by an import)  [no-redef]
src/agentic_mbse/validation/level3_dataflow.py:27: error: Name "print_header" already defined (possibly by an import)  [no-redef]
src/agentic_mbse/validation/level3_dataflow.py:27: error: Name "print_result" already defined (possibly by an import)  [no-redef]
src/agentic_mbse/validation/level2_structure.py:43: error: Cannot find implementation or library stub for module named "common"  [import-not-found]
src/agentic_mbse/validation/level2_structure.py:43: error: Name "EXIT_FAILURE" already defined (possibly by an import)  [no-redef]
src/agentic_mbse/validation/level2_structure.py:43: error: Name "EXIT_SUCCESS" already defined (possibly by an import)  [no-redef]
src/agentic_mbse/validation/level2_structure.py:43: error: Name "QualityCheckResult" already defined (possibly by an import)  [no-redef]
src/agentic_mbse/validation/level2_structure.py:43: error: Name "discover_sysml_files" already defined (possibly by an import)  [no-redef]
src/agentic_mbse/validation/level2_structure.py:43: error: Name "get_element_location" already defined (possibly by an import)  [no-redef]
src/agentic_mbse/validation/level2_structure.py:43: error: Name "get_qualified_name" already defined (possibly by an import)  [no-redef]
src/agentic_mbse/validation/level2_structure.py:43: error: Name "load_sysml_model" already defined (possibly by an import)  [no-redef]
src/agentic_mbse/validation/level2_structure.py:43: error: Name "print_header" already defined (possibly by an import)  [no-redef]
src/agentic_mbse/validation/level2_structure.py:43: error: Name "print_result" already defined (possibly by an import)  [no-redef]
src/agentic_mbse/validation/level2_structure.py:232: error: Need type annotation for "inputs" (hint: "inputs: list[<type>] = ...")  [var-annotated]
src/agentic_mbse/validation/level1_syntax.py:23: error: Cannot find implementation or library stub for module named "common"  [import-not-found]
src/agentic_mbse/validation/level1_syntax.py:23: error: Name "EXIT_FAILURE" already defined (possibly by an import)  [no-redef]
src/agentic_mbse/validation/level1_syntax.py:23: error: Name "EXIT_SUCCESS" already defined (possibly by an import)  [no-redef]
src/agentic_mbse/validation/level1_syntax.py:23: error: Name "QualityCheckResult" already defined (possibly by an import)  [no-redef]
src/agentic_mbse/validation/level1_syntax.py:23: error: Name "discover_sysml_files" already defined (possibly by an import)  [no-redef]
src/agentic_mbse/validation/level1_syntax.py:23: error: Name "print_header" already defined (possibly by an import)  [no-redef]
src/agentic_mbse/validation/level1_syntax.py:23: error: Name "print_result" already defined (possibly by an import)  [no-redef]
src/agentic_mbse/validation/adr002.py:31: error: Cannot find implementation or library stub for module named "common"  [import-not-found]
src/agentic_mbse/validation/adr002.py:31: error: Name "get_element_location" already defined (possibly by an import)  [no-redef]
src/agentic_mbse/validation/adr002.py:31: error: Name "get_qualified_name" already defined (possibly by an import)  [no-redef]
src/agentic_mbse/validation/runner.py:31: error: Cannot find implementation or library stub for module named "common"  [import-not-found]
src/agentic_mbse/validation/runner.py:31: error: Name "EXIT_FAILURE" already defined (possibly by an import)  [no-redef]
src/agentic_mbse/validation/runner.py:31: error: Name "EXIT_SUCCESS" already defined (possibly by an import)  [no-redef]
src/agentic_mbse/validation/runner.py:31: error: Name "AggregatedResult" already defined (possibly by an import)  [no-redef]
src/agentic_mbse/validation/runner.py:31: error: Name "QualityCheckResult" already defined (possibly by an import)  [no-redef]
src/agentic_mbse/validation/runner.py:31: error: Name "print_result" already defined (possibly by an import)  [no-redef]
src/agentic_mbse/validation/runner.py:38: error: Cannot find implementation or library stub for module named "level1_syntax"  [import-not-found]
src/agentic_mbse/validation/runner.py:38: error: Name "validate_syntax" already defined (possibly by an import)  [no-redef]
src/agentic_mbse/validation/runner.py:39: error: Cannot find implementation or library stub for module named "level2_structure"  [import-not-found]
src/agentic_mbse/validation/runner.py:39: error: Name "validate_structure" already defined (possibly by an import)  [no-redef]
src/agentic_mbse/validation/runner.py:40: error: Cannot find implementation or library stub for module named "level3_dataflow"  [import-not-found]
src/agentic_mbse/validation/runner.py:40: error: Name "validate_dataflow" already defined (possibly by an import)  [no-redef]
src/agentic_mbse/validation/runner.py:41: error: Cannot find implementation or library stub for module named "level4_constraints"  [import-not-found]
src/agentic_mbse/validation/runner.py:41: error: Name "analyze_constraints" already defined (possibly by an import)  [no-redef]
src/agentic_mbse/validation/runner.py:42: error: Cannot find implementation or library stub for module named "level5_traceability"  [import-not-found]
src/agentic_mbse/validation/runner.py:42: error: Name "validate_traceability" already defined (possibly by an import)  [no-redef]
src/agentic_mbse/validation/runner.py:43: error: Cannot find implementation or library stub for module named "level6_architecture"  [import-not-found]
src/agentic_mbse/validation/runner.py:43: error: Name "validate_architecture" already defined (possibly by an import)  [no-redef]
src/agentic_mbse/cli/extract_cli.py:134: error: Unexpected keyword argument "timeout" for "extract"  [call-arg]
src/agentic_mbse/cli/extract_cli.py:139: error: Unexpected keyword argument "timeout" for "extract"  [call-arg]
src/agentic_mbse/cli/extract_cli.py:48: error: Unused "type: ignore" comment  [unused-ignore]
src/agentic_mbse/cli/extract_cli.py:48: error: Cannot find implementation or library stub for module named "docling"  [import-not-found]
```

## `uv run ruff check src/ tests/`

Found 118 errors (108 auto-fixable). The listing below is `ruff check --output-format concise`; line numbers are at `ebb3d467`.

```text
src/agentic_mbse/extraction/index.py:146:5: N806 Variable `_UNNUMBERED_RE` in function should be lowercase
tests/conftest.py:2:1: I001 [*] Import block is un-sorted or un-formatted
tests/corpus/claude_extract_experiment.py:38:1: I001 [*] Import block is un-sorted or un-formatted
tests/corpus/experiment.py:41:8: F401 [*] `traceback` imported but unused
tests/corpus/experiment.py:210:9: I001 [*] Import block is un-sorted or un-formatted
tests/corpus/experiment.py:328:5: I001 [*] Import block is un-sorted or un-formatted
tests/corpus/pipelines/detection_v2_phase1.py:232:5: F841 Local variable `track1_data` is assigned to but never used
tests/corpus/pipelines/detection_v2_phase1.py:254:11: F541 [*] f-string without any placeholders
tests/corpus/pipelines/detection_v2_phase1.py:259:11: F541 [*] f-string without any placeholders
tests/corpus/pipelines/detection_v2_phase1.py:264:11: F541 [*] f-string without any placeholders
tests/corpus/pipelines/h1_pymupdf_gmft.py:21:1: I001 [*] Import block is un-sorted or un-formatted
tests/corpus/pipelines/h1_pymupdf_gmft.py:23:5: F401 [*] `shared.BEST_V1_PARAMS` imported but unused
tests/corpus/pipelines/h1_pymupdf_gmft.py:35:5: F401 [*] `shared.load_papers` imported but unused
tests/corpus/pipelines/h1_pymupdf_gmft.py:181:11: F541 [*] f-string without any placeholders
tests/corpus/pipelines/h1_pymupdf_gmft.py:187:11: F541 [*] f-string without any placeholders
tests/corpus/pipelines/h1_pymupdf_gmft.py:195:11: F541 [*] f-string without any placeholders
tests/corpus/pipelines/h1_pymupdf_gmft.py:220:5: F841 Local variable `scores` is assigned to but never used
tests/corpus/pipelines/h1_pymupdf_gmft.py:252:11: F541 [*] f-string without any placeholders
tests/corpus/pipelines/h1_pymupdf_gmft.py:269:11: F541 [*] f-string without any placeholders
tests/corpus/pipelines/h3_pymupdf_claude_eq.py:38:5: F401 [*] `shared.load_papers` imported but unused
tests/corpus/pipelines/h3_pymupdf_claude_eq.py:206:11: F541 [*] f-string without any placeholders
tests/corpus/pipelines/h3_pymupdf_claude_eq.py:212:11: F541 [*] f-string without any placeholders
tests/corpus/pipelines/h3_pymupdf_claude_eq.py:245:15: F541 [*] f-string without any placeholders
tests/corpus/pipelines/h3_pymupdf_claude_eq.py:248:15: F541 [*] f-string without any placeholders
tests/corpus/pipelines/h3_pymupdf_claude_eq.py:278:11: F541 [*] f-string without any placeholders
tests/corpus/pipelines/h3_pymupdf_claude_eq.py:292:21: F541 [*] f-string without any placeholders
tests/corpus/pipelines/h3_pymupdf_claude_eq.py:345:5: F841 Local variable `scores` is assigned to but never used
tests/corpus/pipelines/h3_pymupdf_claude_eq.py:400:11: F541 [*] f-string without any placeholders
tests/corpus/pipelines/h3_pymupdf_claude_eq.py:404:15: F541 [*] f-string without any placeholders
tests/corpus/pipelines/h3_pymupdf_claude_eq.py:433:11: F541 [*] f-string without any placeholders
tests/corpus/pipelines/h5_quality_gated.py:31:1: I001 [*] Import block is un-sorted or un-formatted
tests/corpus/pipelines/h5_quality_gated.py:51:5: F401 [*] `shared.filter_gmft_tables` imported but unused
tests/corpus/pipelines/h5_quality_gated.py:53:5: F401 [*] `shared.load_papers` imported but unused
tests/corpus/pipelines/h5_quality_gated.py:54:5: F401 [*] `shared.replace_tables` imported but unused
tests/corpus/pipelines/h5_quality_gated.py:85:11: F541 [*] f-string without any placeholders
tests/corpus/pipelines/h5_quality_gated.py:91:11: F541 [*] f-string without any placeholders
tests/corpus/pipelines/h5_quality_gated.py:99:11: F541 [*] f-string without any placeholders
tests/corpus/pipelines/h5_quality_gated.py:132:11: F541 [*] f-string without any placeholders
tests/corpus/pipelines/h5_quality_gated.py:157:15: F541 [*] f-string without any placeholders
tests/corpus/pipelines/h5_quality_gated.py:187:11: F541 [*] f-string without any placeholders
tests/corpus/pipelines/h5_quality_gated.py:243:21: F541 [*] f-string without any placeholders
tests/corpus/pipelines/h5_quality_gated.py:295:5: F841 Local variable `scores` is assigned to but never used
tests/corpus/pipelines/h5_quality_gated.py:351:11: F541 [*] f-string without any placeholders
tests/corpus/pipelines/h5_quality_gated.py:355:15: F541 [*] f-string without any placeholders
tests/corpus/pipelines/h5_quality_gated.py:382:11: F541 [*] f-string without any placeholders
tests/corpus/pipelines/h6_pandoc_shortcut.py:15:8: F401 [*] `json` imported but unused
tests/corpus/pipelines/h6_pandoc_shortcut.py:29:5: F401 [*] `shared.PAPERS_JSONL` imported but unused
tests/corpus/pipelines/h6_pandoc_shortcut.py:164:15: F541 [*] f-string without any placeholders
tests/corpus/pipelines/h6_pandoc_shortcut.py:201:11: F541 [*] f-string without any placeholders
tests/corpus/pipelines/h6_pandoc_shortcut.py:207:11: F541 [*] f-string without any placeholders
tests/corpus/pipelines/h6_pandoc_shortcut.py:230:5: F841 Local variable `scores` is assigned to but never used
tests/corpus/pipelines/h6_pandoc_shortcut.py:238:13: F541 [*] f-string without any placeholders
tests/corpus/pipelines/h6_pandoc_shortcut.py:239:13: F541 [*] f-string without any placeholders
tests/corpus/pipelines/h6_pandoc_shortcut.py:279:11: F541 [*] f-string without any placeholders
tests/corpus/pipelines/h6_pandoc_shortcut.py:301:11: F541 [*] f-string without any placeholders
tests/corpus/pipelines/quality_gate.py:14:1: I001 [*] Import block is un-sorted or un-formatted
tests/corpus/pipelines/shared.py:10:8: F401 [*] `time` imported but unused
tests/corpus/pipelines/shared.py:17:1: I001 [*] Import block is un-sorted or un-formatted
tests/corpus/pipelines/track0_detection.py:17:44: F401 [*] `dataclasses.field` imported but unused
tests/corpus/pipelines/track0_detection.py:23:20: F401 [*] `shared.CORPUS_DIR` imported but unused
tests/corpus/pipelines/track0_detection.py:23:56: F401 [*] `shared.load_papers` imported but unused
tests/corpus/pipelines/track0_detection.py:415:11: F541 [*] f-string without any placeholders
tests/corpus/pipelines/track0_detection.py:429:11: F541 [*] f-string without any placeholders
tests/corpus/pipelines/track0_detection.py:443:11: F541 [*] f-string without any placeholders
tests/corpus/pipelines/track0_detection.py:457:11: F541 [*] f-string without any placeholders
tests/corpus/pipelines/track0_detection.py:552:11: F541 [*] f-string without any placeholders
tests/corpus/pipelines/track0_detection.py:565:15: F541 [*] f-string without any placeholders
tests/corpus/pipelines/track1_cropped_extraction.py:27:1: I001 [*] Import block is un-sorted or un-formatted
tests/corpus/pipelines/track1_cropped_extraction.py:27:65: F401 [*] `shared.load_papers` imported but unused
tests/corpus/pipelines/track1_cropped_extraction.py:145:28: F541 [*] f-string without any placeholders
tests/corpus/pipelines/track1_cropped_extraction.py:434:11: F541 [*] f-string without any placeholders
tests/corpus/pipelines/track1_cropped_extraction.py:439:15: F541 [*] f-string without any placeholders
tests/corpus/pipelines/track1_cropped_extraction.py:457:15: F541 [*] f-string without any placeholders
tests/corpus/pipelines/track2_vote_resolve.py:19:25: F401 [*] `dataclasses.asdict` imported but unused
tests/corpus/pipelines/track2_vote_resolve.py:19:33: F401 [*] `dataclasses.dataclass` imported but unused
tests/corpus/pipelines/track2_vote_resolve.py:25:1: I001 [*] Import block is un-sorted or un-formatted
tests/corpus/pipelines/track2_vote_resolve.py:265:15: F541 [*] f-string without any placeholders
tests/corpus/pipelines/track2_vote_resolve.py:336:11: F541 [*] f-string without any placeholders
tests/corpus/pipelines/track2_vote_resolve.py:379:11: F541 [*] f-string without any placeholders
tests/corpus/pipelines/track2_vote_resolve.py:381:11: F541 [*] f-string without any placeholders
tests/corpus/pipelines/track2_vote_resolve.py:392:15: F541 [*] f-string without any placeholders
tests/corpus/pipelines/track3_sequential_review.py:27:1: I001 [*] Import block is un-sorted or un-formatted
tests/corpus/pipelines/track3_sequential_review.py:263:15: F541 [*] f-string without any placeholders
tests/corpus/pipelines/track3_sequential_review.py:423:15: F541 [*] f-string without any placeholders
tests/corpus/pipelines/track3_sequential_review.py:460:11: F541 [*] f-string without any placeholders
tests/corpus/pipelines/track3_sequential_review.py:464:15: F541 [*] f-string without any placeholders
tests/corpus/pipelines/track3_sequential_review.py:480:15: F541 [*] f-string without any placeholders
tests/test_claude_enhance.py:3:1: I001 [*] Import block is un-sorted or un-formatted
tests/test_helpers.py:2:1: I001 [*] Import block is un-sorted or un-formatted
tests/test_helpers.py:4:8: F401 [*] `pytest` imported but unused
tests/test_helpers.py:37:1: W293 [*] Blank line contains whitespace
tests/test_helpers.py:61:1: W293 [*] Blank line contains whitespace
tests/test_helpers.py:64:1: W293 [*] Blank line contains whitespace
tests/test_helpers.py:71:1: W293 [*] Blank line contains whitespace
tests/test_helpers.py:74:1: W293 [*] Blank line contains whitespace
tests/test_helpers.py:85:1: W293 [*] Blank line contains whitespace
tests/test_helpers.py:93:1: W293 [*] Blank line contains whitespace
tests/test_helpers.py:101:1: W293 [*] Blank line contains whitespace
tests/test_helpers.py:105:1: W293 [*] Blank line contains whitespace
tests/test_helpers.py:117:1: W293 [*] Blank line contains whitespace
tests/test_helpers.py:126:1: W293 [*] Blank line contains whitespace
tests/test_helpers.py:134:1: W293 [*] Blank line contains whitespace
tests/test_helpers.py:148:1: W293 [*] Blank line contains whitespace
tests/test_helpers.py:158:1: W293 [*] Blank line contains whitespace
tests/test_helpers.py:170:1: W293 [*] Blank line contains whitespace
tests/test_helpers.py:179:1: W293 [*] Blank line contains whitespace
tests/test_helpers.py:186:1: W293 [*] Blank line contains whitespace
tests/test_nested_package_syntax.py:24:1: I001 [*] Import block is un-sorted or un-formatted
tests/test_pm_dashboard.py:8:5: F401 [*] `agentic_mbse.pm.dashboard._format_date` imported but unused
tests/test_pm_dashboard.py:9:5: F401 [*] `agentic_mbse.pm.dashboard._format_item_line` imported but unused
tests/test_pm_dashboard.py:10:5: F401 [*] `agentic_mbse.pm.dashboard._format_item_status` imported but unused
tests/test_pm_dashboard.py:11:5: F401 [*] `agentic_mbse.pm.dashboard._has_file_not_found` imported but unused
tests/test_pm_dashboard.py:23:5: F401 [*] `agentic_mbse.pm.types.ParseWarning` imported but unused
tests/test_sysml_quality_checks.py:94:16: E712 Avoid equality comparisons to `True`; use `result.success:` for truth checks
tests/test_sysml_quality_checks.py:103:16: E712 Avoid equality comparisons to `False`; use `not result.success:` for false checks
tests/test_sysml_quality_checks.py:114:16: E712 Avoid equality comparisons to `True`; use `result.success:` for truth checks
tests/test_sysml_quality_checks.py:200:16: E712 Avoid equality comparisons to `True`; use `result.success:` for truth checks
tests/test_validation/test_quality_check_result.py:6:1: I001 [*] Import block is un-sorted or un-formatted
```
