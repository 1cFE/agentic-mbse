# Brief: design_review — pm-registry-integrity

**Sent:** 2026-10-04 by the orchestrator. **Stage:** `/_my_design_review`. **Design:** `.project/active/pm-registry-integrity/design.md` at `HEAD`. **Spec (contract):** `spec.md` at `5c15ab1`. Write `design-review.md` beside them; do not edit the design.

## What this work is for

[AGENT, re-derived] Registry entries and their IDs are stable referents that other artifacts cite by spelling. Judge the design by whether it closes every path by which a record disappears or an ID is issued twice, and by whether the code it describes would read as if it had always been there.

## Context you need

- `briefs/design.md` is what the design stage was told, including the orchestrator's steers. The design deviated from one steer (backlog mechanism, D8) with recorded reasoning; evaluate the deviation on its merits, do not penalise it for being a deviation.
- `spec-review.md` and `spec-review-2.md` hold the probes that demonstrate each defect. Read-only fusion-tea copies are at `.orchestrate-logs/ft-snapshot/`; the E4 harness the orchestrator runs is `e4_check.py` there. The design's own check scripts are in `.orchestrate-logs/design-scratch/`.

## What I want pressure on, in priority order

1. **Does the design satisfy every spec criterion and E1 to E4 as written?** Trace each criterion to a mechanism. Flag any criterion that the design meets only on the fixtures but not on the fusion-tea copies.
2. **The backlog writer (D8).** Writing back the loaded YAML keeps everything, but check the round-trip: does the YAML dumper preserve key order, quoting, multi-line strings, and comments well enough that an untouched entry is byte-identical, or close enough that E2's "one new record" holds on real backlogs? The design claims fusion-tea's frontmatter writes back byte-identical; verify that claim against the copy, and ask what happens on a backlog with YAML comments or block scalars.
3. **The two refusal cases and the ordering guarantee.** Are they the right two? Can any write still touch a file before refusing? Check `close_item`.
4. **The ID token boundary.** Does the stated regex give the right answer for `MAG-001`, `` `SV-034` ``, `PR-1`, `SV-034a`, `SV-034-x`, an ID inside an HTML comment that spans lines, and an ID in a fenced code block? Does scanning the whole file for `G-` tokens in `OVERVIEW.md` pick up anything it should not (fusion-tea's text mentions things like "G-8 amendment")? Over-reservation is a gap, not a loss, but say if it is large.
5. **`\\|` semantics.** The design chose "does not split, reads as `\|`" on markdown-it-py's behaviour and could not run cmark-gfm. Settle it if you can from the GFM spec or cmark-gfm's source; otherwise confirm the test pins it and move on.
6. **Engineering quality.** Does the described code introduce duplication, a second source of truth, or awkward coupling? Are the new behaviours (refusing multi-line cell values, refusing `update-validation` on an unparsed row) in scope and correct?

Must-fix findings only need to be things that would make implementation produce the wrong thing or leave a loss path open. Keep nits short and separate. End with a verdict and `ARTIFACT: .project/active/pm-registry-integrity/design-review.md`.
