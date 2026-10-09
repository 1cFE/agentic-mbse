# SC11 audit scope (design D11)

**Who:** a fresh non-author agent, through the orchestrator's audit stage. **What it updates:** the native audit's verdict (`.project/active/native-skills/audit.md:3`, "Needs Work") gets a dated update citing this audit (plan 8.7, after the audit returns).

## In scope

1. **The installer as it now stands: native remediation A–K and this item together.**
   - `git diff 88e2489 HEAD -- src/agentic_mbse/cli/__init__.py src/agentic_mbse/cli/installation.py pyproject.toml` (fork to now). `src/agentic_mbse/cli/pm_cli.py` also differs from the fork, but by `main`'s own changes; leave it out.
   - The A–K checklist: `.project/active/native-skills/remediation.md`.
   - This item's installer changes, by commit: `b961e56` (the tree is the inventory: `is_source_checkout`, `bundle_kind`, `hooks/`, `--list` by kind, a missing data root now raises), `0d01117` (legacy adoption: `legacy_link_target`, its call in `Installer.permit`, `expose_to_claude`, the Adopted report), and the report-once step (an adopted entry is listed only under Adopted, via `Installer.report`).
   - Points to press: the predicate accepts exactly absolute, `.`/`..`-free, mirrored link text whose root is a source checkout, and never normalizes or reads the referent (I3); adoption is reachable only for entries derived from the source tree (I2); nothing writes through a link (I1); `permit`'s order (manifest/desired, then adoption, then force/decide).
2. **The tests that pin it:** `tests/test_installation.py`, `tests/test_cli.py`, `tests/test_packaged_guidance_contract.py`, `tests/test_shipped_text.py`, `tests/helpers/shipped.py`. Check that expectations derive from the tree (I4), that the predicate table includes the rows a normalizing implementation would wrongly accept, and that the `docs` wheel case is a strict xfail with a stated reason (a known packaging gap filed as a follow-up, not this item's).
3. **The content tooling:** `evidence/adaptations.yaml` (17 entries; A1 is flagged for review: it changes onboard's context file to `modeling_project/OVERVIEW.md` plus the current entry file), and `evidence/reconcile.py`'s `write` transform and `check` comparison. `check` must share no envelope or adaptation code with `write`.
4. **The content evidence:** `evidence/check.txt` (0 mismatches over 55 files), `evidence/check-negative.txt` (a changed body byte, a count + 1 and an extra bundle file each exit 1), `evidence/check-rows.md`, `evidence/dispositions.md`, and the discovery probes `evidence/probe-fresh-{claude,codex,both}.json` and `evidence/probe-b2-*.json`.
5. **The fusion-tea switch-over:** `evidence/fusion-tea-target-owned.patch`, `.project/active/wrap-split-migration-ledger.md` (Item 1 section), `evidence/rehearsal.md` with its raw outputs in `evidence/rehearsal/`, and `evidence/fusion-tea-runbook.md`. Check that the B4 classification in `rehearsal.md` holds against `*-provenance.txt`, and that the runbook presents both parked owner choices without deciding them.

## Out of scope

- Body text beyond the adaptation list. SC2 makes it mechanical: `check` proves every shipped file equals `main` plus the reviewed list.
- `main`'s pre-existing lint and type findings (`evidence/lint-parity.md` shows parity).

## Follow-ups for close

- Tidy `--dev`'s `.gitignore` list: it still names `.claude/commands/` and `.claude/.tool-hashes.json`, which the installer no longer writes (design Non-Goals).
- This repo's tracked init scaffold (`modeling_project/`, `work/`, `knowledge/`, `data/`) and its stale tool-owned template copies (R7).
- The wheel omits `docs/syside/python/v0.8.4/syside/` (340 files): older than this item, filed by the orchestrator; the strict xfail flips when it is fixed.
- **`init --dev` hides every shipped skill from Codex.** In the `--dev` rehearsal, Codex 0.160.0 listed none of the 25 shipped skills: each `.agents/skills/<n>/SKILL.md` is a file link to an absolute path outside the project. It predates this item (native `86921f9` links the same way), and SC7's plain-`init` probes pass. Whether SC6's "every install path still works" should cover it is for the orchestrator or owner (plan, Phase 7 notes). Evidence: `evidence/rehearsal/dev-probe.json`.
- **The report lists unchanged files as Updated.** `Installer.write` rewrites and reports every existing managed file (`installation.py:159-169`), so a second run reports Updated (46) while git status is unchanged. Older than this item.
- Fixed during this item, by the orchestrator: the rehearsal copy script `make-copy.sh` re-pointed only `.claude/` links and missed fusion-tea's `work/backlog/epic_template.md`, an absolute link into the live checkout. It now re-points every link into the live checkout.
