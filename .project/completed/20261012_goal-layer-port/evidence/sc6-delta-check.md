# SC6 delta check: wording changed after design review round 2

**Reviewer:** a fresh general-purpose agent dispatched by the orchestrator, 2026-10-11, which wrote none of the text. Read-only, six tool calls.

**Scope:** the changes to `docs/patterns/design-choices.md` and the three design-choice lines of `project_templates/MODELING_PROCESS.md.template` made after round 2: plan "Carried into this plan" items 1–4, and commit `f454835` ("does not count" → "cannot count"). Source: fusion-tea MR-7 at `2b1e9f9d5`, `modeling_project/REQUIREMENTS.md:87-107` (snapshot).

**Verdict: PASS.** Every change keeps MR-7's force and scope; none weakens an obligation or widens one beyond MR-7.

- **Other differences from design A1/A2:** none beyond the listed changes and one fence line.
- **Item 1** (rule 7 "must remain"; unsupported-domain "must remain explicitly unsupported"; review "must record") and **`f454835`** ("cannot count"): MR-7's own words (`REQUIREMENTS.md:99`, `:105`). Force restored.
- **Item 2** (the seed sentence forbids one direction only): faithful. MR-7 forbids setting installed equipment, inventory or capacity from required performance (`:91`) and calls operating-point calculations "not automatically violations" (`:97`); A2's "one from the other" went beyond it. Nothing MR-7 states is lost: the reverse case stays covered by "Distinguish quantities", `design-choices.md` "must not conceal automatic adequacy" and "no manufactured success".
- **Item 3** (an identity over supplied values passes step 1): agrees with `:97` and `:107`; rule 5 still requires the identity to state its independent quantities.
- **Item 4** (`---` before the grade paragraph): formatting only.

**Minor point, taken by the orchestrator.** The seed sentence said "from demand" where MR-7 (`:91`) and the template's own point-of-use row say "from required performance"; read narrowly, "demand" might not cover a calculated required area. The template now reads "from required performance". This is MR-7's wording and the point-of-use row's, so it narrows nothing and needs no further check.

**Timing.** The SC4 dry-run wheel was built at `57a61c8`, before this one-phrase change; the dry run's checks do not depend on it.
