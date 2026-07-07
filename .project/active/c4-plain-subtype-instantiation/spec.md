# Spec: C4 Plain-Subtype Instantiation — correct docstring, lock in behavior with the missing test

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-06 08:39
**Complexity:** LOW
**Branch:** `upstream-findings-sync`

---

## Problem

The Item 12 review flagged `check_calc_bearing_instantiation`
(`src/agentic_mbse/validation/level6_architecture.py:631`) as a false L6 FAIL. On
investigation it is **not** a false positive — the check's behavior is correct. The
real defects are a wrong docstring and a missing test.

The check FAILs a calc-bearing part def whose simple name appears in no part usage's
resolved type set (`.types`). Its docstring claims `.types` "includes the full
supertype chain AND any retype target." The first half is empirically false. Live
syside repro: for `part thing : SubHolder` where `SubHolder :> BaseHolder`,
`thing.types` is `['SubHolder', 'Part', 'Item', 'Object', 'Occurrence', 'Anything']`
— the direct type plus the KerML built-in roots, but **not** the user-defined
intermediate `BaseHolder`.

That omission is the *correct* behavior, and this is the crux the review resolved.
sysml-codegen deliberately does **not** walk plain-subtype inheritance: a calc-bearing
base instantiated only through a plain subtype has its inherited template calc dropped
at extraction. This is pinned, not incidental —
`_build_part_usage_index` keys a plain `part x : Sub` under `Sub` only
(`usage_extractor.py:277-278`), `_find_instantiation_paths` recurses through nesting
not supertypes, and the exact shape is the negative test
`test_plain_sibling_not_reached_by_supertype_template`
(`tests/conformance/test_type_indexing.py:111-117`, `retype_model` Shape 5), backed by
REQ-EXT-13/14 (`docs/architecture/reference/01-extraction.md:24-25`). Retype (`:>>`)
and direct instantiation *do* carry the base into `.types`, so codegen expands the
template — and the check correctly passes those.

So the check's FAIL exactly mirrors codegen's drop. The danger is the docstring: if a
future reader "fixed" the check to actually walk the full supertype chain — as the
docstring implies it already does — the check would start **passing** plain-subtype
bases that codegen drops, silently reintroducing the trap. And today the one path that
proves the check is right (plain-subtype-only) is untested: the `retype_instantiation`
fixture instantiates its base `IfeDriver` directly via `Facility.driver`, so it never
isolates plain subtyping.

## Success Criteria

- [ ] The docstring describes the real `.types` semantics: direct type +
      retype-inherited typings + KerML built-in roots, but **not** plain-subtype
      supertypes — and states that this omission is correct because codegen mirrors it
      (cite sysml-codegen REQ-EXT-13/14).
- [ ] A new fixture instantiates a calc-bearing base **only** via a plain subtype
      (`part x : Sub`, `Sub :> Base`, with no direct instantiation and no `:>>` retype
      reaching `Base`), and a test asserts `L6_CALC_DEF_NO_INSTANTIATION` fires (ERROR)
      on the base.
- [ ] `test_c4_no_instantiation_fails` and `test_c4_retype_counts_as_instantiation`
      still pass — behavior is unchanged, only documented and now covered.
- [ ] Full suite still green (`uv run pytest tests/`).

## Known Requirements

- **[HARD]** The check must keep FAILing a calc-bearing base instantiated only via
  plain subtype (no direct instantiation, no retype reaching it). Forced by
  sysml-codegen: it drops the inherited template calc in exactly this case
  (REQ-EXT-13/14; `test_plain_sibling_not_reached_by_supertype_template`). Current
  behavior is correct and must be preserved.
- **[HARD]** The check must keep NOT firing when the base is reachable by direct
  instantiation OR by a `:>>` retype usage. In both, the instantiating usage's
  `.types` carries the base and codegen expands the template. Current behavior; must be
  preserved.
- **[NEED]** The corrected docstring must make the "why it's correct" explicit enough
  that a future maintainer does not replace `.types` with a transitive-supertype walk —
  the tempting change that would break the check.
- **[INFERRED]** The fix adds a plain-subtype fixture and test; the user described the
  gap, the fixture/test is the implied deliverable.

## Non-Goals

- **Do NOT change the check to walk the transitive supertype chain.** That would make
  it pass plain-subtype-only bases that codegen drops — a behavior regression, and the
  exact bug class this item exists to prevent. This is the tempting-but-wrong "fix."
- Not fixing F6 (`ITEM-SYNC-F6`) or any other L6 false-positive family — separate items.
- Not touching the C6 / findings-2-3 calc-def-owner skips — already fixed on this branch.

## Open Questions / Deferred to design

- Should the FAIL message and suggestion be reworded to name the plain-subtype trap
  specifically ("instantiated only via plain subtype; codegen drops the inherited calc
  — retype the usage or instantiate the base directly")? Improves the modeler's fix
  path but is a wording choice — defer to design/implementation.
- Whether to add a short note to the plant-idiom pattern doc
  (`docs/patterns/plant-idiom.md`) teaching that plain subtyping does not inherit
  template calcs (retype does). Candidate, not required — defer.

---

## Related Artifacts

- **Epic:** UPSTREAM-FINDINGS Item 12 (sysml-codegen `.project/active/validation-sync/`)
- **Sibling defects:** `ITEM-SYNC-F6` in `.project/backlog/BACKLOG.md`; C6 / findings-2-3
  calc-def-owner skips (fixed on `upstream-findings-sync`)
- **Codegen evidence:** sysml-codegen `usage_extractor.py:267-305,308-364,465-474`;
  `tests/conformance/test_type_indexing.py:111-117`; `retype_model` fixture Shape 5;
  REQ-EXT-13/14 (`docs/architecture/reference/01-extraction.md:24-25`);
  `docs/architecture/modeling-assumptions.md` "Not covered" note (~line 316-320)
- **Design:** `.project/active/c4-plain-subtype-instantiation/design.md` (to be created)

---

**Next Steps:** LOW complexity — this may not need a full `/_my_design`. Consider
`/_my_plan` straight to implementation, or `/_my_quick_edit` if scoped tightly.
