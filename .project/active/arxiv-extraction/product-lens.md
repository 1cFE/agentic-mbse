# Product-lens ledger: ARXIV-EXTRACTION

## 2026-10-18 · design review of `design.md`

**Lens source:** the lens script (`~/.claude/scripts/product-lens.md`) could not be read in this session (permission denied), so no lens subagent ran. The reviewer derived the point independently from the sources below. Treat this entry as a reviewer derivation, not a lens run.

**Sources:** owner goal as relayed by the orchestrator `[OWNER]` and recorded in `spec.md` Problem `[NEED]`; spec `R1`–`R5`; `spec_review.md` Resolutions. No `.project/product/` ledger and no `.project/adr/` exist in this worktree.

**Point (derived):** a consumer runs `extract` with Pandoc on PATH and no workarounds, and gets the right paper, its figures on disk, and nothing but the paper. When the shortcut does not fire or falls back, the consumer can see why.

**Design's point:** matches (design.md "The Point" states the same test).

**Findings:**
- DO (owner `[NEED]`): no citation substitution. Covered by D1/D2 and Invariants 4–5. Disposition: met.
- DO (owner `[NEED]`): no missing figures. Covered by D7/D8 for both routes. Disposition: met, with one gap: the PDF route's image base URL is not pinned down (see design review M2).
- DO (owner `[NEED]`): no arXiv chrome. Covered by D4. Disposition: met on the primary path. A double failure on the web route (article conversion fails, trafilatura short) still reaches `_fallback_pandoc` over the whole page (see design review m5). Lower authority edge, visible disposition only.
- DON'T (owner reserved): settle the default-on gate. Design keeps it provisional and a one-line flip (D10). Disposition: respected.
- DON'T (owner reserved): remove or rename public `PipelineConfig` fields or CLI flags. Design only adds (Invariant 9). Disposition: respected.

**Structural smells:** consumer compensating for a producer guarantee: not fired (the work removes consumer compensation). Invariant ownership moved without saying so: not fired (image persistence and identity ownership moves are stated in D3, D2).

**Gate:** CLEAR.

## audit — 2026-10-18 — rev 373a34df

**Point (re-derived):** A downstream consumer (personal-os `kg add`) can keep Pandoc on PATH and drop both of its workarounds: hiding Pandoc for PDFs, and stripping `data:` image links. Every `extract` gives the right paper (never a cited one), all of its figures saved locally, and nothing but the paper. No public `PipelineConfig` field or CLI flag is removed or renamed, and the shortcut ships on by default. [source: owner Need in `~/personal-os/queue/2026-10-18-agentic-mbse-arxiv-pdf-shortcut-drops-figures-and.md` ("drops … inline base64 icon images … Then personal-os kg add can put pandoc back on PATH and stop stripping data: images"); grade: owner]

**Falsifier:** With Pandoc on PATH and no workarounds, any one of these shows the point violated. (a) A PDF that cites arXiv:X on page 1 comes out as paper X. (b) An image ref in `output.md` has no local file. (c) Chrome strings or `data:image` links appear in `output.md`.

**Findings:**
- audit-F1 [DON'T] The output still carries 12 `data:image/svg+xml;base64` links, about 32k chars, on both routes for 2610.14224. They are the title graphic and the C1–C8 component icons. The owner named "stop stripping data: images" as the done-condition. The spec's `[INFERRED]` rule keeps in-article data URIs (`spec.md:77`, design invariant 6). That rule rests on an investigation line, "All 16 sat in chrome" (`spec.md:29`), which the auditor found false: 12 of the base run's 16 SVG data URIs are byte-identical to the in-article ones kept now. This premise conflict was never surfaced to the owner. — owner Need (owner) — disposition: BLOCK until the owner rules: accept them, externalize them to `images/`, or drop them.
- audit-F2 [DO] A failed image download keeps its remote ref and warns, and programmatic use without `extracted_images_dir` keeps refs as written. Both are spec-sanctioned (R1) and documented. — (AGENT) — disposition: accepted per spec.
- audit-F3 [DO] The title logo PNG sits inside an in-article SVG data URI and is never saved. It is decoration. — (AGENT) — disposition: fold into the F1 ruling.
- audit-F4 [DON'T] On the PDF-URL route, the frontmatter source names the PDF while the hash covers the fetched HTML. This precedence predates the branch (verified at `8b027bbc`). — (INHERITED) — disposition: DEFERRED to the extraction-provenance work.

**Smells:** Smell 3 (a special category exempts a case whose user-visible meaning is unchanged) fired on F1: to the consumer, "inside the article" `data:` links look the same as the icons it reported. No other smell fired. Both routes are tested independently.

**Gate:** BLOCKED (audit-F1). F2 is accepted, F3 is folded into F1, F4 is deferred.
