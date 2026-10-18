# sysml-codegen guidance-contract evidence (I8)

**Result: pass, 9 of 9, at both requested sysml-codegen revisions, against this branch's guidance.** Run 2026-10-18 at agentic-mbse `positional-binding-check` `60c75af3` (the Phase 8 guidance commit).

## How it was run

- sysml-codegen's `origin/main` is `b5663c07e987a892e27d21e68cec40d0656574ee`: the local ref and `git ls-remote origin refs/heads/main` agree, and nothing was fetched. So the two requested revisions are one commit. Each was still exported separately with `git archive` into `/tmp/pb-codegen/origin-main/` and `/tmp/pb-codegen/b5663c07/`.
- The test ran from each export: `tests/conformance/test_self_binding_guidance_contract.py`, with `PYTHONDONTWRITEBYTECODE=1` and `-p no:cacheprovider`. Nothing ran inside the sysml-codegen checkout, which another agent is using at `8396cb23`. Its HEAD and status were recorded before and after: unchanged, clean.
- **Interpreter:** this checkout's `.venv` (`/home/reid/src/agentic-mbse/.venv/bin/python`), not sysml-codegen's `.venv`. Using codegen's environment would mean running from its checkout. Both environments import agentic-mbse as an editable install of this checkout, so the agentic tree the test reads is the same; the run records it.
- **Import path, proven:** `agentic_mbse.__file__` is `/home/reid/src/agentic-mbse/src/agentic_mbse/__init__.py`, and the test's own `agentic_source_root()` (from the export's `tests/helpers/source_roots.py`) returns `/home/reid/src/agentic-mbse`.

## Captured output

```text
## sysml-codegen checkout before: HEAD 8396cb230448ea151b08e2d5bb55d65817261cef; status lines 0
origin/main (local ref): b5663c07e987a892e27d21e68cec40d0656574ee
origin main (ls-remote): b5663c07e987a892e27d21e68cec40d0656574ee
agentic-mbse: branch positional-binding-check HEAD 60c75af3c1f19845018bafffc55118f78ac21f0a

### export origin-main
interpreter /home/reid/src/agentic-mbse/.venv/bin/python
agentic_mbse.__file__ /home/reid/src/agentic-mbse/src/agentic_mbse/__init__.py
agentic_source_root() /home/reid/src/agentic-mbse
test file /tmp/pb-codegen/origin-main/tests/conformance/test_self_binding_guidance_contract.py
tests/conformance/test_self_binding_guidance_contract.py::test_exactly_one_authoritative_copy_across_all_instruction_trees PASSED [ 11%]
tests/conformance/test_self_binding_guidance_contract.py::test_marked_examples_carry_valid_labels PASSED [ 22%]
tests/conformance/test_self_binding_guidance_contract.py::test_pinned_examples_match_their_cited_fixture_sources PASSED [ 33%]
tests/conformance/test_self_binding_guidance_contract.py::test_one_pinned_example_pins_the_refusal PASSED [ 44%]
tests/conformance/test_self_binding_guidance_contract.py::test_zero_unmarked_self_named_examples_across_all_trees PASSED [ 55%]
tests/conformance/test_self_binding_guidance_contract.py::test_qualified_inventory_matches_the_reviewed_dispositions PASSED [ 66%]
tests/conformance/test_self_binding_guidance_contract.py::test_the_three_deliberate_negatives_remain PASSED [ 77%]
tests/conformance/test_self_binding_guidance_contract.py::test_summary_surfaces_point_at_the_authoritative_copy PASSED [ 88%]
tests/conformance/test_self_binding_guidance_contract.py::test_dot_claude_tree_still_has_no_binding_instruction_surface PASSED [100%]
============================== 9 passed in 0.12s ===============================

### export b5663c07
interpreter /home/reid/src/agentic-mbse/.venv/bin/python
agentic_mbse.__file__ /home/reid/src/agentic-mbse/src/agentic_mbse/__init__.py
agentic_source_root() /home/reid/src/agentic-mbse
test file /tmp/pb-codegen/b5663c07/tests/conformance/test_self_binding_guidance_contract.py
tests/conformance/test_self_binding_guidance_contract.py::test_exactly_one_authoritative_copy_across_all_instruction_trees PASSED [ 11%]
tests/conformance/test_self_binding_guidance_contract.py::test_marked_examples_carry_valid_labels PASSED [ 22%]
tests/conformance/test_self_binding_guidance_contract.py::test_pinned_examples_match_their_cited_fixture_sources PASSED [ 33%]
tests/conformance/test_self_binding_guidance_contract.py::test_one_pinned_example_pins_the_refusal PASSED [ 44%]
tests/conformance/test_self_binding_guidance_contract.py::test_zero_unmarked_self_named_examples_across_all_trees PASSED [ 55%]
tests/conformance/test_self_binding_guidance_contract.py::test_qualified_inventory_matches_the_reviewed_dispositions PASSED [ 66%]
tests/conformance/test_self_binding_guidance_contract.py::test_the_three_deliberate_negatives_remain PASSED [ 77%]
tests/conformance/test_self_binding_guidance_contract.py::test_summary_surfaces_point_at_the_authoritative_copy PASSED [ 88%]
tests/conformance/test_self_binding_guidance_contract.py::test_dot_claude_tree_still_has_no_binding_instruction_surface PASSED [100%]
============================== 9 passed in 0.10s ===============================

### what the .claude scan reads in /home/reid/src/agentic-mbse (regular files, symlinks skipped)
56
symlinks: 0
no .agentic-mbse/install.json (no agentic-mbse install in this checkout)
## sysml-codegen checkout after: HEAD 8396cb230448ea151b08e2d5bb55d65817261cef; status lines 0
```

## What the `.claude/` scan saw

The test's last rule reads every regular file under `<agentic root>/.claude/` (symlinks skipped) and fails on any line matching `\bin\s+[\w']+\s*=`. In this checkout it saw 56 regular files and no symlinks: 29 personal workflow commands, 6 rules, 4 scripts, `settings.json`, `.agentic-pack-vendored`, 14 files of four personal skills and one example agent. None has a matching line. **This checkout has no agentic-mbse install**: there is no `.agentic-mbse/install.json`, and none of the shipped skills or roles is under `.claude/`. `.claude/.agentic-pack-vendored` was written today (17:52) by another tool.

Plan Phase 8 step 3 said to re-run `install-commands --assistant claude --link-mode symlink` here first. **Not done**, because the install the plan assumed is not present, and adding one would change local state another tool manages. Instead, both install modes were tested on scratch exports (next section).

## Supporting runs, from scratch exports of agentic-mbse

Each run points `PYTHONPATH` at an export's `src/`, so the test reads that export, not this checkout. Run from the `b5663c07` codegen export.

**Base `ccd57d83`, before this item's edits: 1 failure.**

```text
### agentic-mbse ccd57d83 (base, before this item's guidance edits)
agentic_mbse.__file__ /tmp/pb-codegen/am-base/src/agentic_mbse/__init__.py
E   AssertionError: ['project_templates/MODELING_PROCESS.md.template']
FAILED tests/conformance/test_self_binding_guidance_contract.py::test_zero_unmarked_self_named_examples_across_all_trees
========================= 1 failed, 8 passed in 0.08s ==========================
```

That failure is on `main`. Commit `06ac41de` (#17) had dropped the `;` from MODELING_PROCESS's self-named warning so it reads as prose. `312d16a5` (goal-layer-port, merged to `main`) put it back. Phase 8 removes it again; the line is otherwise unchanged.

**This HEAD with each install mode:**

```text
### agentic-mbse HEAD 60c75af3, install-commands --assistant claude --link-mode symlink (into the export)
install exit 0
.claude regular files: 7; symlinks: 28
agentic_mbse.__file__ /tmp/pb-codegen/am-symlink/src/agentic_mbse/__init__.py
============================== 9 passed in 0.07s ===============================

### agentic-mbse HEAD 60c75af3, install-commands --assistant claude --link-mode copy (into the export)
install exit 0
.claude regular files: 41; symlinks: 0
agentic_mbse.__file__ /tmp/pb-codegen/am-copy/src/agentic_mbse/__init__.py
E   AssertionError: ['.claude/skills/sysml-conventions/SKILL.md']
FAILED tests/conformance/test_self_binding_guidance_contract.py::test_dot_claude_tree_still_has_no_binding_instruction_surface
========================= 1 failed, 8 passed in 0.10s ==========================
```

- Symlink mode (what `.project/CURRENT_WORK.md` says this checkout uses): 9 of 9 pass. Skills install as links, which the scan skips; the 7 regular files are the five rendered roles (including `sysml-expert.md` with this item's sentence), the formatter hook and `settings.json`, with no matching line.
- Copy mode: the `.claude` rule fails on `.claude/skills/sysml-conventions/SKILL.md`. **This predates the item**: the same copy-mode run on `ccd57d83` also fails this rule (and the MODELING_PROCESS one); that skill already had 11 matching lines at `ccd57d83`. So a copy-mode install in this checkout breaks codegen's test regardless of this item. That is an owner observation, not something this item changed.
