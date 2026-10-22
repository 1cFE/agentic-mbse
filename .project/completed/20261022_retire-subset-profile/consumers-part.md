# Part 5: consumers (fusion-tea, dc3)

Answer: neither consumer imports or configures the subset profile. No `execution-target` setting, no `[tool.agentic-mbse]` table, no import of `subset_profile`, `subset_facts`, `subset_extraction` or `occurrence_extraction`, and no `L2_POSITIONAL` or subset L6 codes in either.

Checkouts found (find under /home/reid, depth 4): only `/home/reid/src/fusion-tea` and `/home/reid/src/dc3`. No `/home/reid/1cfe/fusion-tea`.

## fusion-tea (/home/reid/src/fusion-tea, branch main, HEAD f96ad312c)

- Dependencies: `pyproject.toml:8` `agentic-mbse[extract-full,web]==0.1.3`, `:10` `sysml-codegen==0.1.1`; sources are git pins, `pyproject.toml:36` agentic-mbse rev 443388823f0d (commit dated 2026-08-18, "fix: map return-parameter membership"), `:37` sysml-codegen rev 8a758e92. `uv.lock:46-48` and `:3155-3157` match.
- The pinned agentic-mbse commit 443388823 contains no `subset*` or `occurrence*` module under `src/agentic_mbse/sysml/` (checked with `git ls-tree`). So fusion-tea cannot be using the profile today.
- No `[tool.agentic-mbse]` section in pyproject.toml.
- Python imports of agentic_mbse are only `syside_adapter` and `validation.common`, all under `archive/models/tests/...` (e.g. `archive/models/tests/solar_battery/validate_ast.py:853-854`).
- `.claude/skills/` holds only browser-inspect, concept-research-navigation, narrate-goal, run-goal, run-study (no agentic-mbse modelling skills installed); none mention the profile.
- The broad grep for `L6_` hit only a huge JSON evidence file (`exploration/component_alternatives/studies/20260926-.../evidence/validation-detail.json`); the targeted profile-term grep found zero files.

## dc3 (/home/reid/src/dc3, branch goal/study-ready-baseline, HEAD 60b44d5 "Note agentic-mbse GENERATOR-SUBSET-PATTERNS filing (incl. U8 positional binding)")

- Dependencies: `pyproject.toml:7` `agentic-mbse[extract-full,web]==0.1.3`, `:8` `sysml-codegen==0.1.1`; sources are editable path deps, `pyproject.toml:25` `../agentic-mbse`, `:26` `../sysml-codegen` (`uv.lock:35-37`, `:3342-3344`). So dc3 runs whatever is checked out at /home/reid/src/agentic-mbse (currently branch shipped-example-contract) and /home/reid/src/sysml-codegen (currently branch adr-0012-occurrence-summary-amendment), not the subset-conformance worktree. Retiring the profile in agentic-mbse changes dc3's `validate` output directly once that checkout moves.
- No `[tool.agentic-mbse]` section, so no `execution-target` set.
- Python imports: `agentic_mbse.sysml.syside_adapter` and `agentic_mbse.sysml.reference_use` (e.g. `tests/models/test_path_efficiency.py:13-14`, `tests/models/test_generated_parity.py:15`, `scripts/models/evaluate_sites.py:4`). `reference_use.py` imports errors, data_models, invocation_allowlist and syside_adapter only, not the copy's modules.
- L6 codes appear only in captured validate output (e.g. `work/orchestration/goals/conversion-path-efficiency/evidence/T-008-independent-validation.txt:76-89`), the older L6 code list; no subset-contract codes.
- Prose that states the generator limits by hand (relevant as prior art for the replacement guidance):
  - `work/learnings/RAW_LEARNINGS.md:162`: "Write models in the generator subset from the start: part-owned numeric assertions, fixed-arity calcs, exact design counts, `sum` only, min = (a+b-((a-b)^2)^0.5)/2, compose by specialized part defs, Strings as metadata only."
  - `work/orchestration/goals/study-ready-baseline/trail.md:334` and `learnings.md:47` (L-005) say the same.
  - `models/README.md:194`: "The whole tree generates with `sysml-codegen generate` and passes validate L1–L6."
- Installed skills: `.claude/skills/*` are symlinks to `.agents/skills/*` (copies). grep -R over them found no mention of execution-target, subset profile or `sysml-codegen check`. `.agents/skills/run-study/integration-guide.md:207` mentions `sysml-codegen generate --smart-regen`; `.claude/commands/teax-completion.md:45,57` mention `sysml-codegen generate`. `.agentic-mbse/patterns/constraints.md:523` mentions "executable-profile eligibility counts" via `validate --level=4` (installed pattern doc; worth checking against the agentic-mbse source pattern doc).

Not checked: other machines or clones outside /home/reid at depth 4; git history of either consumer.
