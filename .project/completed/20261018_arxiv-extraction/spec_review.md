# Spec Review: Reliable arXiv extraction (ARXIV-EXTRACTION)

**Spec:** `.project/active/arxiv-extraction/spec.md`
**Contract:** `claude-pack/commands/_my_spec.md` (not in this worktree; grade vocabulary taken from the review command)
**Review File:** `.project/active/arxiv-extraction/spec_review.md`
**Date:** 2026-10-18

---

## Reality Check

**Sound.** The spec is about the right work item, and its Problem section holds up against the code. The shortcut runs before anything else and returns early, before PDF image extraction (`pipeline.py:380-386`). Detection takes the first `arXiv:NNNN.NNNNN` anywhere in page-1 text (`pandoc_convert.py:89`). `convert_arxiv_html` downloads no images. The web route converts the whole sanitized page. Its fallback only logs (`web_backend.py:416`), and its returned warnings come only from image downloads (`web_backend.py:490-495`). No opt-out flag exists. `git diff 517f3e11 8b027bbc` over the extraction sources and `extract_cli.py` is empty, so the evidence carries over to this base.

The faults are in grading, in testability, and in a few places the spec doesn't reach. Targeted edits can fix them.

---

## Audit

Findings marked **[must-fix]** block the spec from serving as the design contract. Findings marked **[suggestion]** would improve it but don't block.

### Lens 1 — Faithfulness

**L1-1 · Direct claim [must-fix]:** The spec has no grade markers. Every requirement is agent-derived from the personal-os queue report. Only some of them restate evidence the investigation reproduced. The goal the owner stated on 2026-10-18 is: keep Pandoc on PATH safely, with no citation substitution, no missing figures and no arXiv chrome, so that consumers' workarounds become unnecessary. That goal is the only `[NEED]`. The spec should tag each requirement:
- `[NEED]` for that goal.
- `[INFERRED]` for the mechanisms derived from it: the opt-out flag, cleanup scope, fallback warnings, the embedded-figure guard.
- `[HARD]` only where an existing interface forces it, such as keeping `--html-path` as an override or keeping raw-byte hashing.
- `[INHERITED]` for anything taken from the queue report, citing the report.

**L1-2 · Direct claim [must-fix]:** R3 decides a question the owner reserved. "Enabled by default for backward compatibility" is written as settled. The owner reserved that call. The spec should state the default as an open owner decision, or record the owner's answer. It should not carry an agent's call as settled.

On the other reserved question: the spec does **not** force removing or renaming any public `PipelineConfig` field or CLI flag. R3 only adds things. `arxiv_html_path` / `--html-path` keep their meaning (R2's last sentence). No owner action is needed on renames.

**L1-3 · Direct claim:** The code-facing claims check out:
- Early return before image extraction: true.
- No image download on the shortcut: true. `PipelineResult.image_count` is left at 0.
- Whole-page web conversion: true.
- Fallback logged but missing from returned warnings: true.
- No CLI disable: true. There is no programmatic disable either, short of hiding Pandoc.

The spec correctly narrows the report's "silent fallback" claim. No corrections needed.

**L1-4 · Rewrite request [suggestion]:** The Completion section leaves out part of the owner's success test. It names citation substitution and missing figures. It omits "no arXiv chrome" and the consumer's data-image stripping workaround. The completion statement should restate all three outcomes, so it matches the goal the owner set.

### Lens 2 — Problem & Approach

**L2-1 · If-then tradeoff [must-fix in wording, design keeps the mechanism]:** R2 leaves room for the orchestrator's stamp hypothesis. The hypothesis says arXiv-served PDFs carry a vertical left-margin stamp, `arXiv:NNNN.NNNNNvN [cat] date`, on page 1. Design Question 1 keeps the choice of evidence open, and nothing in R2 rules a stamp out. But R2 is not testable as written, for three reasons:
- **"Conflicting evidence" is undefined.** One reading is a stamp ID that disagrees with a prose ID. Another is two different stamps. Another is a stamp that disagrees with Creator metadata. A test for "conflicting IDs" can't be written until the spec names the conflict, or at least says what a conservative outcome looks like (no substitution).
- **The expected outcome for "an arXiv-origin PDF citing another ID" is unstated.** If the PDF's own ID is identifiable (from a stamp, say), should the shortcut fire for the paper's *own* ID, or decline? These lead to different tests.
- **"Genuine paper with its own arXiv identifier" is ambiguous.** It could mean a stamped arXiv download. It could mean an author or publisher PDF that mentions its own arXiv ID in prose. Under a stamp-based design, the second case becomes a false negative.

There is also a tradeoff to make explicit. Any design that needs strong evidence will stop substituting for real arXiv papers that lack it. That includes publisher versions, author builds, and PDFs whose stamp text pymupdf can't read. That outcome is right **if** the owner values safety over shortcut hit rate, and the stated goal suggests they do. The spec should say outright that false negatives are acceptable and fall through to normal PDF extraction, so design doesn't try to recover them.

**L2-2 · Question to the user [suggestion]:** Two kinds of identity evidence are missing from the spec's framing, and design should hear about both:
- **The source URL.** `_extract_pdf_url` knows `fetched.final_url`. A PDF fetched from `arxiv.org/pdf/<id>` is very strong evidence for that ID.
- **A post-fetch check.** After fetching, compare the HTML title with the PDF's page-1 text. This catches a bad identification even when the stamp heuristic is wrong.

Does the owner want R2 to name these as allowed evidence, or leave them entirely to design? (They are allowed now, just not mentioned.)

**L2-3 · Direct claim [must-fix]:** The spec misses a third consumer of `detect_arxiv_id`: `extract --check`. `check.py:328-346` (`probe_pandoc`) calls `detect_arxiv_id`, `check_arxiv_html` and `convert_arxiv_html` directly, without going through the pipeline. Two problems follow:
- If R2 changes only the pipeline, `--check` will keep reporting "arXiv ID detected" for citations, and will fetch and convert the cited paper.
- R3 covers "every CLI path that uses the PDF pipeline", and `--check` does not use the pipeline. So whether the opt-out applies to `--check` is undefined.

The spec should say whether `--check`'s probe follows R2's identity rule and R3's opt-out. A related bug sits in the same probe: `md = convert_arxiv_html(html_url)` gets back a `(markdown, bytes)` tuple, so `len(md)` always reports "2 chars". It's not in scope, but design will run into it.

**L2-4 · Direct claim:** The work item is sized about right. R1-R3 are the core of the owner's goal. R4 is the "no chrome" outcome. R5 is small. Splitting isn't warranted. The two Pandoc conversion paths are duplicates (`convert_arxiv_html` and `_extract_with_arxiv_pandoc`), and the comments warn that their flags must stay in sync. "Share where practical" in Scope is the right level. Don't promote it to a requirement.

### Lens 3 — Pipeline Risk

**L3-1 · Direct claim [must-fix]:** R1 says failures "MUST be observable", but the PDF route has no channel for that. `PipelineResult` (`types.py:108-124`) has no `warnings` field. The PDF CLI path writes `metrics.json` straight from `result.metrics.to_dict()` (`extract_cli.py`, PDF branch) and prints no warnings (`_print_pipeline_summary`). The web route uses returned `warnings`, `metrics.json["warnings"]` and CLI output. R1 should define "observable" the same way R5 does: in the returned result, persisted with the output, and printed by the CLI. Otherwise design could satisfy R1 with a log line. Design Question 3 hints at this, but the requirement should fix the outcome.

**L3-2 · Direct claim [must-fix]:** R1 doesn't cover `--html-path`. "A successful PDF HTML shortcut… MUST download the paper's externally referenced images" includes the explicit `--html-path` case. A saved arXiv HTML file has relative asset refs like `2610.14224v1/x1.png`, and the code has no page URL to resolve them against (the web route uses `urljoin(final_url, …)`, `web_backend.py:99`). The spec should state the expected behavior for a local HTML source. Options include: resolve against arxiv.org using the asset-path ID, keep remote/relative refs with a warning, or mark it out of scope. Without that, R1 can't be met for this input, or two engineers will meet it differently.

**L3-3 · Rewrite request [must-fix]:** "Repeated references… MUST be handled consistently across routes" doesn't say what correct looks like. Today the web route downloads the same URL twice and saves `x1.png` and `x1_2.png` (`web_backend.py:110-118`). Is that consistent and acceptable, or should one URL map to one file? The requirement should state the result for each case:
- the same URL referenced twice;
- two different URLs that share a basename;
- a failed download.

The invariant already implied is the testable core: every rewritten reference points at an existing file, and every failed one keeps its remote URL.

**L3-4 · If-then tradeoff [suggestion — gold-plating watch]:** R4 is broad, but most of its breadth is test expectations, not extra mechanism. The investigation found all 16 data-image refs in chrome *outside* the paper (dialog, nav, footer, funder logos). If design selects the LaTeXML article container, most of R4 follows from that one step. The proportionality risk lies in two clauses:
- **"Remove UI data-image icons by their page context; do not blanket-delete…"** This names a mechanism. Turning it into an outcome would leave room for a container-only design.
- **The "legitimate embedded figures survive" acceptance row.** This builds a fixture for a case nobody has observed: LaTeXML papers with data-URI figures. The guard is right **if** such papers exist. Otherwise it is speculative.

The suggested trim is an outcome: "No UI image references remain, and no paper figure is removed." Keep the embedded-figure fixture only if the spec can point to a real instance.

**L3-5 · Rewrite request [must-fix]:** R4's fallback boundary is ambiguous for the PDF route. "Use the existing route fallback with an observable diagnostic" means trafilatura for the web route. For the PDF shortcut, the existing fallback is normal PDF extraction. But one could also read it as "convert the full page and warn". The spec should name the fallback for each route.

**L3-6 · Rewrite request [suggestion]:** Silent shortcut failures stay silent. R5 says PDF shortcut failure "continues to normal PDF extraction" and asks for no diagnostic. Today the cause is logged only at `debug` (`pipeline.py:225`). That includes an explicit `--html-path` being ignored because Pandoc is missing (`pipeline.py:188-189`). An override the user asked for and then silently dropped deserves at least a returned warning. This helps the owner's goal: when the shortcut doesn't fire, the consumer should be able to tell why.

**L3-7 · Rewrite request [must-fix]:** "Real small PDF fixtures" (acceptance table, R2 row) is ambiguous. Does it mean committed arXiv-downloaded PDFs, which bring licensing and size concerns, or PDFs generated in the test? Generated PDFs can carry a rotated margin stamp written with pymupdf's text rotation. The spec should require real PDF bytes parsed by the real detector, and leave the fixtures' origin to design. Generated fixtures are probably the right answer for the stamp case.

**L3-8 · Rewrite request [suggestion]:** The live-run row says "optional", but Completion says "all… acceptance criteria above are implemented and verified". The spec should say whether the live run gates completion. This matters because a live Harness² run with Pandoc on PATH and no data-image stripping is the closest thing to the owner's actual success test (see L1-4).

### Lens 4 — Hygiene

**L4-1 · Rewrite request [suggestion]:** R1's last sentence ("Preserve paper figure captions, tables and mathematical content through cleanup") repeats R4's preserve list. Keep it in one place.

### Lens 5 — Reader Comprehension

**L5-1 · Rewrite request [suggestion]:** The spec reads well overall. One term needs defining. "The shortcut" is used throughout but never introduced. A single sentence in Problem would help a reader who doesn't know `_try_arxiv_shortcut`: "the shortcut = replacing PDF extraction with conversion of the arXiv HTML version when an ID is detected."

---

## Engagement Summary

**Overall take:** The diagnosis is right and checked against the code, and the requirement set fits the owner's goal. But no requirement is graded, R3 decides the owner's reserved default, and R1, R2 and R4 each have a sentence two engineers would build differently. None of this needs a rework. It needs one revision pass.

**Here's what I need you to weigh in on:**

1. **[L1-2]** Decide whether the arXiv shortcut stays **on by default**, or record that this is still open. The spec currently says "on" as if it were settled. (Nothing in the spec forces a rename or removal of existing fields or flags.)
2. **[L2-1, L3-7]** Confirm that R2 should name the conservative outcomes: false negatives on genuine papers are acceptable, and ambiguous identity falls back to PDF extraction. Also confirm the expected outcome for "an arXiv PDF citing another ID", and what counts as "conflicting". The stamp hypothesis fits the spec as written. It is not decided.
3. **[L2-3]** Decide whether `extract --check`'s Pandoc probe follows R2's identity rule and R3's opt-out. It's a separate code path the spec doesn't mention.
4. **[L3-1, L3-3]** Define "observable" for PDF-route image failures (returned result, persisted output, CLI), and state the expected handling of repeated references.
5. **[L3-2]** State what R1 requires when the HTML source is a local `--html-path` file with no page URL.
6. **[L3-4]** Decide whether R4 keeps the "embedded data-image figure" guard and fixture, or trims it to an outcome. This is the main gold-plating risk.
7. **[L1-1]** Have the spec agent add grade markers. Only the owner's stated goal is a `[NEED]`. The rest is `[INFERRED]`, `[HARD]` or `[INHERITED]`, with sources cited.

---

## Resolutions

Recorded by the orchestrator on 2026-10-18. Grades: `[OWNER]` = owner said it at Align; `[AGENT]` = orchestrator's call under its delegated authority (challengeable on evidence).

- **L1-2 (default-on)** — `[OWNER]` reserved this for the owner; still **open**. Spec should state the default as an open owner gate, with "on" as the provisional default so design and implementation can proceed (the choice is one default value plus docs). Do not mark it settled.
- **L2-1, L3-7 (R2 outcomes)** — `[AGENT]` Yes: identity is conservative. False negatives on genuine papers are acceptable; anything ambiguous goes to normal PDF extraction. IDs found only in body prose are never identity evidence. An arXiv-origin PDF citing another ID substitutes only if its own-ID evidence (e.g. the margin stamp, or the arxiv.org source URL it was fetched from) names the substituted ID. "Conflicting" = two trusted sources name different IDs (ignoring version suffix), or more than one candidate in a trusted position; conflict → PDF extraction. Design chooses the exact evidence set; the stamp hypothesis needs verification against real PDFs before it is relied on.
- **L2-3 (`extract --check`)** — `[AGENT]` Yes: `--check` must follow R2 and R3 so it predicts what `extract` will do. Fix the "2 chars" tuple-length bug in passing.
- **L3-1, L3-3 (observable; repeats)** — `[AGENT]` Observable means: in the returned result's warnings, in the persisted warnings/metrics written alongside output (same mechanism the web route uses, extended to PDF results), and printed to stderr by the CLI. Repeated references to one URL are downloaded once and every occurrence is rewritten to the same local file; if the download fails, every occurrence stays remote and one warning is emitted.
- **L3-2 (local `--html-path`)** — `[AGENT]` Absolute http(s) image URLs are downloaded. Relative paths resolve against `<base href>` if present, otherwise against the HTML file's directory (copy the file if it exists). Anything unresolvable stays as written, with a warning. No guessing a remote arXiv base.
- **L3-4 (R4 embedded-figure guard)** — `[AGENT]` Trim to an outcome: cleanup removes nothing inside the recognized paper container for being a data URI; UI icons go because they sit in removed chrome. Keep one small embedded image inside the article in the fixture as a single assertion; no separate mechanism requirement.
- **L1-1 (grades)** — `[AGENT]` Yes, add grade markers. Only the owner's goal (Pandoc safe on PATH; consumer workarounds unnecessary) is `[NEED]`.
- **L3-6 (silent fallbacks)** — `[AGENT]` Accept: shortcut failures and an ignored `--html-path` produce warnings.
- **L2-2 (more evidence)** — `[AGENT]` Accept the arxiv.org source URL as candidate evidence. A post-fetch title cross-check is a design option, not a requirement.
- **L1-4, L3-8 (completion)** — `[AGENT]` Add "no arXiv chrome" to Completion. The live Harness² run is a required recorded check at audit when network is available; if unavailable, record that and do not block.

---

**Verdict:** Revise
**Next Steps:** Once resolutions are recorded, re-run `/_my_spec` (or return to the spec-agent session) and point it at this review to incorporate. The reviewer does not edit the spec.
