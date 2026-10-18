# Reliable arXiv extraction: right paper, every figure saved, no page chrome

## Summary

`extract` can now run with Pandoc on PATH. It returns the right paper, saves all its figures locally, and leaves out arXiv's page chrome. A downstream consumer (personal-os `kg add`) no longer needs to hide Pandoc for PDFs or strip `data:` image links.

Before this branch:

- The PDF pipeline swapped in arXiv HTML whenever any arXiv ID appeared on page 1, so a PDF that *cited* a paper came out as that paper.
- The swap skipped image download.
- The direct arXiv HTML route converted the whole page: issue dialog, navigation, footer, funder logos, UI icons.

Now:

- **Identity needs the paper's own evidence.** The PDF shortcut fires only on the rotated left-margin arXiv stamp or an arxiv.org source URL. Citations never trigger it. A stamp and URL that name different papers warn as a conflict.
- **Only the article is converted.** Both routes select the single `<article class="ltx_document">` through one module, `src/agentic_mbse/extraction/arxiv_html.py`. Any other page shape fails closed with `ArxivConversionError`, and the whole-page Pandoc fallback no longer runs for arXiv.
- **Every figure is saved under `images/`.** That includes LaTeXML SVG `<object>` figures, which Pandoc used to drop (4 of 9 on 2610.14224), and in-article `data:` images, which are written out as content-hash-named files. LaTeXML listing download buttons are removed; the listing text stays.
- **New flags.** `--arxiv-shortcut` / `--no-arxiv-shortcut` control the shortcut. `extract --check` applies the same identity rule and opt-out.
- **Every fallback warns** in the result, in `metrics.json`, and on stderr.

Live check on 2610.14224, both routes: 0 `data:` links, and 31 of 31 image refs point at saved files.

## Behaviour changes callers can see

- `pandoc_convert.convert_arxiv_html` raises `ArxivConversionError` where it raised `subprocess.CalledProcessError` (or let `TimeoutExpired` escape). Pandoc missing still raises `FileNotFoundError`. Signature and return type are unchanged.
- Web-route warnings go to stderr only, no longer also to stdout.
- Fewer PDFs take the shortcut. A PDF with no stamp and no arxiv.org source URL gets normal PDF extraction.
- A PDF URL inside `--urls-from` used to recurse forever (`RecursionError`); it now extracts.
- `metrics.json` carries `image_count` on the PDF route, and `warnings` on both routes.

## Open owner decision

Should the arXiv shortcut stay on by default? The owner reserved this call (spec R3). It ships on as a provisional default (`ARXIV_SHORTCUT_DEFAULT = True`, `src/agentic_mbse/extraction/pandoc_convert.py:22`). Flipping it is that line plus one docs sentence. `--html-path` works either way.

## Known follow-ups (non-blocking)

- The title logo PNG sits inside an in-article SVG and is not saved separately (decoration).
- On the PDF-URL route, frontmatter `source` names the PDF while the hash covers the fetched HTML. This predates the branch; deferred to the extraction-provenance work.

## Checks

- `uv run pytest tests/`: 2929 passed, 3 failed, 1 skipped. The 3 failures are the known environmental baseline: PIL missing (`test_equations.py`) and two hard-coded paths in `test_index.py`.
- `uv run ruff check` on the changed Python files: clean.
- `uv run ruff format --check`: the lines this branch added are formatted. Seven touched files still carry formatting drift that predates the branch; it was left alone to keep the diff focused.
- `uv run mypy src/`: 97 errors, same as the base.
- Not run: the slow corpus tests (`-m slow`). arXiv layouts beyond the three saved reference pages are untested.

## Review trail

Spec, design, plan, two audit rounds, and the product lens are in `.project/completed/20261018_arxiv-extraction/`.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
