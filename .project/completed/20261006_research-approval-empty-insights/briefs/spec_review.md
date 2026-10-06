# Brief: spec_review — research-approval-empty-insights

**Sent:** 2026-10-05 by the orchestrator. **Stage:** `/_my_spec_review`. **Target:** `.project/active/research-approval-empty-insights/spec.md`.

## What this work is for

[AGENT, re-derived from the spec, backlog item, and product lens] A user can approve a research report and accept none of its insight candidates. That is a normal outcome: a source-registration round, a bounded negative result, or confirmation of existing knowledge. Today the tool refuses that approval, so the operator moves the file from `knowledge/research/pending/` to `approved/` by hand. The outcome to serve is "research approved with no new insight goes through the supported operation." Accepting `--insights '[]'` is the mechanism. Review the spec against the outcome, not against "the function accepts an empty list."

## Owner rulings (2026-10-05, in the Align exchange)

- [OWNER] No reserved gates. The orchestrator decides and records.
- [OWNER] Stage subagents run on Opus 5.5.
- The owner was asked whether the backlog Goal is their own stated need and did not say so. Every success criterion therefore stays `[INHERITED]` or `[INFERRED]`. Do not upgrade any to `[NEED]`.

## Orchestrator decisions (execution detail, recorded so the trail shows them)

- [AGENT] Branch is `research-approval-empty-insights`, cut from `main` at `c37ff53` (PR #15 merged). The spec header's `harness-right-size` is stale.
- [AGENT] "Existing valid pending document" in criterion 1 means the two checks the operation already makes: the path is under `knowledge/research/pending/` and the file exists. This item adds no content validation.
- [AGENT] Planned stages after this review: revise spec → `design` → `plan` → `implement` → `audit`. `design_review` runs only if the design turns up a real decision.

## Facts verified by the orchestrator (2026-10-05, at `c37ff53`)

- The refusal is one guard: `src/agentic_mbse/pm/operations.py:936` returns `success=False, message="No insights provided"` when the list is empty. The function starts at `operations.py:910`. The spec's `operations.py:635` pointer is stale.
- CLI registration is at `src/agentic_mbse/cli/pm_cli.py:559`, with `--insights` `required=True`. The handler is at `pm_cli.py:346`. The spec's `pm_cli.py:562` pointer is stale.
- The CLI already separates the three caller errors from explicit emptiness before the operation runs (`pm_cli.py:56`): malformed JSON, a non-array, and an invalid item each print an error and return the usage exit code. `[]` passes validation and reaches the operation, which then refuses it.
- The CLI prints only `result.message` plus warnings (`pm_cli.py:78`). `files_modified` and `ids_assigned` reach Python callers only. So "CLI guidance" in criterion 4 is the message text; the changed-files and assigned-IDs claims are observable only through the direct Python result.
- On success today the result always lists `knowledge/KNOWLEDGE.md` in `files_modified` and the message ends `Created insights: {id_list}` (`operations.py:993`). With zero insights both would be wrong.
- Today the operation parses `KNOWLEDGE.md` before building entries (`operations.py:943`) and passes its warnings through. The spec does not say whether a zero-insight approval should read the knowledge file at all.
- Two shipped docs describe the command as always producing insights: `claude/commands/research.md:77` ("structured JSON of approved DI-XXX entries", then "assigns DI-XXX IDs ... Report the assigned IDs") and `claude/skills/toolkit-awareness/SKILL.md:90`. The spec's `research.md:65` pointer is to the Approve/Skip review step; the call instruction is at `:77`.
- The spec's non-goal "repairing the separate registry ID-allocation defect" refers to work that merged in PR #15. It is no longer a live defect.
- `.project/CURRENT_WORK.md` still names the checkout `pm-registry-integrity`, not yet merged. That is stale.

## Points I want the review to attack

- Criterion 4 mixes two observers. Split what the CLI user sees (message, exit code) from what a Python caller sees (`files_modified`, `ids_assigned`), so design cannot satisfy it with a message change alone.
- "Leaves the knowledge registry unchanged" — is byte-identical `KNOWLEDGE.md` the test, and should the spec say whether a missing or unparseable `KNOWLEDGE.md` may block a zero-insight approval? An approval that mints nothing has no reason to depend on that file. Say whether this belongs in the spec or is fairly left to design.
- The shipped `/research` command text is the path by which an agent learns to pass `[]`. The spec lists it as an open question ("whether command instructions need a short clarification"). If the command never tells the agent that skip-all is `--insights '[]'`, the fix does not reach the user. Should that be a success criterion?
- Criterion 2: "omitting `--insights` remains a caller error" is true at the CLI. For the direct Python operation, `insights` is a required keyword argument. Is there anything for the spec to say about `None`?
- Criterion 3's "without moving research or mutating knowledge" on invalid requests: is a partial-failure case reachable (insights appended, then the move fails)? The spec parks transactional behavior as out of scope. Check that parking is honest, not hiding a regression risk this change creates.
- Standard devil's-advocate pass per your command: faithfulness of the `[INHERITED]` tags to `.project/backlog/BACKLOG.md` (item at line 77), stale pointers, sizing (backlog says 0.5 day; spec says LOW).

Keep the review proportionate. This is a small repair; findings that would widen it need a strong reason.
