# Spec: FORMULA Teaching Reconciliation

**Status:** Implemented (surgical stance)
**Owner:** Reid W
**Created:** 2026-07-06 09:05
**Complexity:** MEDIUM
**Branch:** `upstream-findings-sync`

> **Stance resolved (2026-07-06): SURGICAL.** Calc defs in `library/` remain the
> recommended way to express real calculations; inline FORMULA is taught as a
> convenience reserved for simple arithmetic and unit conversions. Applied across all
> surfaces below plus two that the sweep initially missed: the taxonomy row in
> `MODELING_GUIDE.md(.template)`, and the tracked install copies under `modeling_project/`
> (which, contrary to the CLAUDE.md note, are committed). The calc-output-in-arithmetic /
> self-reference / dotted-path cases are still taught as violations. Full-embrace teaching
> (a dedicated inline-FORMULA pattern doc) remains an optional future follow-up.

---

## Problem

The F6 fix (landed on this branch) changed what the V2 derived-expression check
accepts. It used to hard-FAIL any design-file `attribute X = <expr>` that referenced
another design attribute. As of sysml-codegen Item 5, a computed attribute whose
feature refs all resolve to **same-part owned siblings** is a supported FORMULA — it
generates and resolves end-to-end. The check now accepts that shape and still fails
only the genuinely-unsupported ones: a reference to a calc output inside arithmetic
(`= calc.out * 0.95`), a self-reference, or a dotted path.

The shipped **teaching docs still teach the old blanket rule**, so they now contradict
the validator — and several use the exact shape the fix accepts as their canonical
"this fails" example. A modeler following the docs would extract a working FORMULA into
a calc def to avoid a failure that no longer happens. The epic's whole premise is that
teaching and checking move in lockstep, so this is a real gap, not cosmetic.

Verified contradiction set (4 surfaces):

- **`docs/patterns/adr002-calculations.md`** — the Expression Taxonomy table lists
  `= radius * 2.0` as **FAIL**; an entire "Invalid Pattern: Derived Expression" section
  teaches `area = length * width` (same-part siblings) as a violation to extract into a
  calc def; the "Why it fails" line and Rule 3 wording follow suit.
- **`claude/skills/sysml-conventions/SKILL.md`** — the shipped skill states (line 74)
  that a design attribute depending on another attribute's value "must be expressed as a
  `calc def` … not inline," and a table row (line 150) says to extract "inline derived
  expressions" to a calc def. This is the FORMULA case, now accepted.
- **`project_templates/MODELING_PROCESS.md.template`** — a calc-placement decision tree
  routes "a derived expression (references design attrs)?" to "❌ VIOLATION — use calc
  def"; the "Key Rule" prose uses `diameter = radius * 2.0` as the canonical violation;
  two checklists assert design expressions contain "ONLY literals (no design attribute
  references)." (This template is the tool-owned edit target; the installed
  `modeling_project/MODELING_PROCESS.md` is a regenerated copy.)
- **`docs/patterns/common-mistakes.md`** — the review checklist item "No derived
  expressions in design attributes" is now overbroad.

Checked and correct, no change needed (record so a reviewer doesn't re-flag them):

- `docs/patterns/expose-pattern.md:174` — "`= power_calc.output * 1.1` is a derived
  expression, not an EXPOSE" describes a calc-output-in-arithmetic case, which still
  fails. Correct.
- `docs/patterns/plant-idiom.md:133` — only a soft cross-reference to
  adr002-calculations.md; no false claim of its own.

## Success Criteria

- [ ] Every surface in the contradiction set agrees with the validator: a same-part
      sibling FORMULA is shown as accepted, not as a failure.
- [ ] The still-failing cases (calc-output-in-arithmetic, self-reference, dotted path)
      remain taught as violations — the reconciliation narrows the rule, it does not
      delete it.
- [ ] The `MODELING_PROCESS.md.template` decision tree and "Key Rule" no longer use
      `diameter = radius * 2.0` (a now-accepted shape) as the canonical violation.
- [ ] A modeler following any of these surfaces would not be surprised by a validation
      result on a same-part FORMULA.
- [ ] `expose-pattern.md` and `plant-idiom.md` left unchanged, having been verified
      consistent.

## Known Requirements

- **[HARD]** Every shipped teaching surface that claims the validator fails a same-part
  FORMULA must be corrected to the validator's actual contract. The code already
  shipped; the docs are factually wrong until they match it.
- **[HARD]** The calc-output-in-arithmetic, self-reference, and dotted-path cases must
  still be taught as violations — they still fire (REQ-CA-06/07; codegen
  `computed_attribute_extractor.py`).
- **[HARD]** The tool-owned edit target for the process guide is
  `project_templates/MODELING_PROCESS.md.template`, not the installed
  `modeling_project/` copy (init ownership model, per CLAUDE.md).
- **[NEED]** Docs and validator agree on what passes and fails, so a modeler reading the
  guidance can predict validation results.
- **[INFERRED]** The `sysml-conventions` skill is in scope. It reads as separate from
  "docs," but it carries the same false claim and ships to target repos.

## Non-Goals

- The validator code fix and F6 itself — done on this branch.
- The deferred C7/C8 checks (`ITEM-SYNC-C7`, `ITEM-SYNC-C8`).
- The codegen inherited-attribute bug (inherited non-owned refs silently no-op in
  codegen). That is codegen's to fix; here we only avoid teaching that inherited refs
  are a working FORMULA.
- Regenerating the installed `modeling_project/MODELING_PROCESS.md` copy — that follows
  from the template on next init (see Open Questions).

## Open Questions / Deferred to design

- **The stance decision (this drives how much each file changes).** Two ways to
  reconcile:
  - *Surgical* — correct only the false "the validator fails this" claims, and keep
    steering modelers toward calc-def as the recommended pattern for real computation.
    Smaller; preserves the current teaching philosophy.
  - *Full embrace* — teach inline FORMULA computed attributes as a first-class pattern
    (when to use inline FORMULA vs calc def, with the self-ref / dotted-path /
    calc-output / inherited-attribute exclusions spelled out), likely a new
    `docs/patterns` section. Bigger; shifts the teaching stance.

  Recommendation: **surgical.** Calc-def is still sound guidance, and the epic needs
  lockstep accuracy, not a philosophy change. Full embrace is a good follow-up if we
  later decide to actively promote inline FORMULA. Note that even the surgical option
  must choose a replacement for the `diameter = radius * 2.0` canonical example — it can
  no longer stand as "the violation," so each surface needs a genuinely-failing example
  (a calc-output-in-arithmetic case) in its place.

- Whether to soften the `plant-idiom.md:133` cross-reference wording ("why derived
  expressions belong in calc defs") once adr002-calculations.md is reworded. Minor.

- Whether to regenerate the installed `modeling_project/MODELING_PROCESS.md` now or let
  the next `init` pick up the template change. Low stakes; likely leave to init.

---

## Related Artifacts

- **Epic:** UPSTREAM-FINDINGS Item 12 (sysml-codegen `.project/active/validation-sync/`)
- **Sibling items:** `ITEM-SYNC-F6` (the validator fix that created this gap, done);
  `c4-plain-subtype-instantiation` spec (same review batch)
- **Codegen ground truth:** REQ-CA-01..REQ-CA-11
  (`docs/architecture/reference/16-computed-attributes.md`);
  `src/sysml_codegen/extraction/computed_attribute_extractor.py::_classify_attribute_expression`;
  `docs/architecture/modeling-assumptions.md` §3
- **Validator contract:** `src/agentic_mbse/validation/adr002.py::check_static_expressions`
  and its `_is_supported_formula` helper (this branch)
- **Design:** `.project/active/formula-teaching-reconciliation/design.md` (to be created)

---

**Next Steps:** Resolve the stance decision above, then a light `/_my_design` (or straight
to `/_my_plan`) — the mechanism is "edit these four surfaces consistently," so most of the
work is picking the replacement examples and wording once the stance is set.
