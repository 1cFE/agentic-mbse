# Brief: design — pm-registry-integrity

**Sent:** 2026-10-04 by the orchestrator. **Stage:** `/_my_design`. **Spec:** `.project/active/pm-registry-integrity/spec.md` at `5c15ab1` (contract; two review rounds closed). Write `design.md` beside it.

## What this work is for

[AGENT, re-derived] Registry entries and their IDs are stable referents that other artifacts cite by spelling. Every design decision should be defensible as "this keeps a record from disappearing or an ID from being issued twice." A design that satisfies the tests but adds a third way to split a table row, or a second place that knows how IDs are numbered, has missed the point.

## Read first

- The spec. Its six criteria and E1 to E4 are the contract. `[AGENT]` items there are orchestrator decisions with reasoning; challenge them only by re-deriving against that reasoning, and say so in the design if you do.
- `spec-review.md` and `spec-review-2.md` for the evidence behind the contract, especially the per-registry exposure table and the probes. Rerun `.orchestrate-logs/spec-review-scratch/probe.py` and `sr2_probe.py` if you want to see the failures live.
- `briefs/spec_review.md` for the verified fusion-tea facts. Read-only copies of fusion-tea's registry files are at `.orchestrate-logs/ft-snapshot/`. You cannot read fusion-tea itself.
- The E4 harness the orchestrator will run after implementation: `.orchestrate-logs/ft-snapshot/e4_check.py`. Design so that it passes; do not edit it.

## Orchestrator steers (execution detail, `[AGENT]`; deviate with recorded reasoning)

- **One cell splitter.** A single function implements GFM row splitting with `\|` as a literal pipe, and both `parser.py:109` and `update_validation` (`operations.py:1148`) call it. The matching writer-side escape lives beside it, and `_format_table_row` (`operations.py:194`) uses it. Read and write are inverses by construction, not by convention.
- **One ID discovery function.** Allocation for all seven prefixes goes through one path that scans the registry file for same-prefix tokens outside HTML comments, and `_next_id` takes its maximum from that scan together with parsed records. Define the token boundary precisely (what `MAG-001`, `` `SV-034` ``, `PR-1`, `SV-034a` and `SV-034-x` each count as) and pin it with tests. Keep allocation strictly above the max.
- **The backlog writer keeps what it cannot validate.** Decide the mechanism: the parser retains the raw mapping for every work item it rejects, and the writer re-emits those alongside the typed ones. Malformed YAML refuses. Say precisely which other failures refuse, and make the refusal happen before any file is touched so `close_item` cannot half-close (spec criterion 5).
- **`\\|` semantics.** Pick the GFM reading, state it in one line, and pin it with a test. Do not spend design time on it beyond that.
- **Diagnostics.** A record whose ID was reserved but whose content was rejected should say so in its warning. This is allowed by E3's clarification.

## Quality bar

Clean, well-factored Python that reads as if it had always been there. No new module unless the shared splitter and the ID scan genuinely do not belong in `parser.py` and `operations.py`; if you add one, justify it in a sentence. Type-annotated, mypy-clean, ruff-clean. Tests go in the existing `tests/test_pm_*.py` files next to the behaviour they pin, unless a new file is clearly better. Note the E1 fixture labels are reversed from fusion-tea by design.

## Decisions that are yours

Everything the spec lists under Open Questions. Record each in the design with the alternatives you rejected and why, one or two lines each. If you hit a question the spec and this brief cannot settle, make the call, mark it `[AGENT]`, and continue; do not stop to ask unless proceeding under any assumption would be unsafe.

When done, end with `ARTIFACT: .project/active/pm-registry-integrity/design.md`.
