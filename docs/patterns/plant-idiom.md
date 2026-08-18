# The Plant Idiom: Cross-Part Calc Wiring

How a design wires calculations across nested parts. These are the shapes codegen
supports for building a plant model out of reusable part defs, each carrying its own
template calcs. Covers cross-part chains, retyping, EXPOSE surfacing, and sibling
disambiguation.

Reference fixtures live in the sysml-codegen repo under `tests/fixtures/`; each shape
below names the fixture that exercises it.

## Supported reference shapes and their required context

The parser's resolved element is the identity authority for every shape. A spelling alone does
not select a value. The elaborator combines that identity with the consumer occurrence and the
modeled containment domain.

| Authored shape | Meaning | Context required |
|---|---|---|
| bare `value` | one resolved feature in the current semantic scope | the consumer occurrence and the feature's semantic owner |
| owner-qualified `Owner::value` | the exact resolved feature owned by a usage or definition | the owner class, the consumer occurrence, and its modeled lineage/domain |
| feature chain `part.value` | the resolved chain root followed by its exact resolved members | the root occurrence address plus every resolved member in order |
| package-owned reference | a feature owned directly by a package | the exact package anchor; only the supported direct one-step case omits an occurrence prefix |
| definition-domain reference | a definition-owned feature used inside an occurrence of that definition | the consumer's own occurrence lineage; descendants and siblings are not substitutes |
| plural occurrence | one modeled feature materialized more than once | the exact occurrence index from the consumer domain; an unindexed plural result refuses as ambiguous |

The semantic owner class is one input to this derivation. It does not determine the result by
itself. A missing target, missing document tier, broken operand traversal, or incomplete resolved
chain is ill-formed evidence and fails by name. An indexed reference is different: it is valid
SysML evidence whose code-generation meaning is not implemented yet, so it is refused as the
valid-but-unsupported indexed form rather than reclassified as malformed.

## The core shape

A plant is a part with nested parts. Each nested part def owns *template calcs* — calc
usages that compute the part's outputs from its attributes. When the plant instantiates
the nested part, each template calc becomes an instance-scoped calc that runs in the
pipeline.

```sysml
part def Coil {
    attribute radius : Real = 0.5;

    // Template calc: computes volume from the coil's own radius. The parameter and the
    // attribute must not share a name — see "Binding a modelled value" below.
    calc volume_calc : VolumeCalc {
        in radius_in = radius;
    }
}

part def Plant {
    part coil : Coil;                // instantiating Coil brings volume_calc into the pipeline
}
```

Reference: `fusion_tea` binds this way throughout (`in beam_energy_mj_in = beam_energy_mj`,
`in availability_in = availability`) and is one of the fixtures the exact route elaborates.
`ife_plant` is a fuller plant — drivers, coils and chambers — but it is written with
self-named bindings and the exact route refuses it, so read it for structure, not for the
binding form.

## Binding a modelled value into a calculation — match the form to where the value lives

<!-- @authoritative calculation-binding-rule -->
This section is the one authoritative copy of the calculation-binding rule; agent
skills and project templates carry a summary and point here. The rule: **a
calculation input binds to the modelled value its resolved reference names** —
never to a name coincidence, and never to a same-named outer feature standing in
for the one you wrote. Pick the authoring form by where the value lives.

Each pinned example below is an excerpt of the named sysml-codegen fixture, and a
conformance test compares them (`test_self_binding_guidance_contract.py`); the
`owner-class` label says which resolution route governs it.

### The value is an attribute on the part that owns the calculation → make the names differ (D-5)

Rename the calculation input and bind it bare. The bare reference then lands on
the outer attribute, and a public mutation of that attribute reaches the calc.
This is the ratified form for the local situation and what the migrated
fusion-tea customer model uses throughout.

<!-- @pinned fixture=tests/fixtures/fusion_tea/designs/generic_ife/ife_plant.sysml owner-class=n/a outcome=generates -->
```sysml
in availability_in = availability;
in gain_in = gain;
```

The other accepted spelling renames the attribute instead, so the calc input
keeps its library name:

<!-- @pinned fixture=tests/fixtures/wi014_toy/toy_plant.sysml owner-class=n/a outcome=generates -->
```sysml
attribute plant_length : Real = 4.0;
in length = plant_length;
```

### The value lives on another part → name the occurrence path (D-7)

The reference lands on that occurrence's feature — the nested driver's own
`cost_per_joule`, not a name lookup in the consumer's scope.

<!-- @pinned fixture=tests/fixtures/fusion_tea/designs/generic_ife/ife_plant.sysml owner-class=n/a outcome=generates -->
```sysml
in driver_cost_constant = driver.cost_per_joule;
in target_cost_constant = target_factory.cost_per_target;
```

### Qualifying by owner (D-6) — the behavior follows who owns the resolved feature

An owner-qualified reference is supported, but two owner classes resolve by
different routes. Check which one you are writing.

**The leaf is owned by a part usage → the exact usage anchors.** SysIDE resolves
a usage-qualified reference to the exact feature owned by that usage, and the
elaborator honors that owner (`qualified-reference-occurrence-anchoring`, landed
2026-08-15; pinned by `tests/conformance/test_usage_owned_reference_anchoring.py`).

<!-- @pinned fixture=tests/fixtures/usage_owned_reference_consumers/model.sysml owner-class=usage outcome=generates -->
```sysml
part comp_a : 'Component' { :>> length = 3.0; }
calc area_calc : AreaCalculation {
    in length_in = comp_a::length;
}
```

An unindexed reference to an **arrayed** usage owner's leaf is deliberately
scalar and refuses with `SI_OCCURRENCE_AMBIGUOUS`; the author-facing diagnostic
work for arrayed owners is owned by `[ANCHORING-ARRAYED-DIAGNOSTIC]`, not by
this rule.

**The leaf is owned by a part definition → it must map through the consumer's
own occurrence lineage.** SysIDE's resolved structure is authoritative. If the
lineage carries no occurrence of that feature, codegen refuses with
`SI_OCCURRENCE_MISSING`; it does not search descendants or siblings to invent
one.

Inside the definition, each occurrence reads its own value — two occurrences are
not ambiguous when the consumer sits inside them:

<!-- @pinned fixture=tests/fixtures/def_qual_two_occ_inside/model.sysml owner-class=definition outcome=generates -->
```sysml
part def 'Plant' {
    attribute availability : Real default 0.85;
    calc revenue_calc : Revenue {
        in availability = 'Plant'::availability;
    }
}
```

Above the definition, neither occurrence is on the consumer's lineage, so the
route refuses. The number of descendants does not change that result:

<!-- @pinned fixture=tests/fixtures/def_qual_two_occ_above/model.sysml owner-class=definition outcome=refused:SI_OCCURRENCE_MISSING -->
```sysml
part def 'Fleet' {
    part plant_a : 'Plant' { :>> availability = 0.11; }
    part plant_b : 'Plant' { :>> availability = 0.99; }
    calc revenue_calc : Revenue {
        in availability = 'Plant'::availability;
    }
}
```

With no local occurrence, a single feature under a sibling subtree still does
not qualify. Use D-7's explicit occurrence path when the value lives on another
part.

<!-- @pinned fixture=tests/fixtures/def_qual_sibling_scope/model.sysml owner-class=definition outcome=refused:SI_OCCURRENCE_MISSING -->
```sysml
part def 'Power Block' {
    calc cost_calc : UnitCost {
        in unit_cost = 'Unit'::cost;
    }
}
```

### The refused form: `in x = x` binds the calculation input to itself

A template calc that binds `in radius = radius` reads as if the right `radius`
were the owning part's attribute. It is not. The reference resolves to the
calc's own input parameter, so the attribute's value never reaches the calc and
the calculation computes on a default — legal SysML, silently inert.

**This shape is refused on both validation paths.** The L2 self-named-binding
check FAILs it (`L2_SELF_NAMED_BINDING`, compared by referent identity, not by
name), and elaboration refuses the model with `SI_SELF_BINDING` before
generation. A same-named attribute in the owning part, a sibling calc output,
and an inherited attribute are all irrelevant: a self-binding is never
reinterpreted as an outer reference (D-4 [OWNER-VERBATIM 2026-08-05]; the
lifecycle contract's blocking-diagnostics clause and violation table).

<!-- @pinned fixture=tests/fixtures/self_named_binding_trap/library.sysml owner-class=n/a outcome=refused:SI_SELF_BINDING -->
```sysml
calc avail_calc : AvailabilityCalc {
    in availability = availability;
}
```

Nor can redefinition rescue it from inside the calc: after `redefines`, a name
resolves through the owning type's supertypes with the owner's own namespace
excluded (KerML §7.3.4.5; §8.2.3.5.1 describes the abstract-syntax mechanism),
so a `:>>` inside the calc usage cannot name the enclosing part's attribute.

Reference: the agentic-mbse `item12` fixtures. `self_named_deadend` (no
same-named feature), `self_named_trap` (a covering attribute) and
`self_named_rescue` (a sibling calc output) all fail identically, and
`usage_qualified_local` pins that the supported owner-qualified spellings are
not flagged. In the codegen corpus the exact route still refuses `ife_plant`
(21 self-named bindings) — read it for structure, not for the binding form.

## Retyping to pull in a subtype's calcs (D2)

A design may retype a nested part usage to a subtype to pull in the subtype's template
calcs, while keeping the base def's calcs:

<!-- @measured evidence="D-5 rename pinned by fusion_tea (spike row 2); the inherited-attribute D-5 variant is measured behavior without a pinned fixture" owner-class=n/a outcome=generates -->
```sysml
// Library: subtype specializes the base and adds its own calc.
part def 'Base Driver' {
    attribute bank_energy : Real = 10000000.0;
    calc base_power_calc : DriverPowerCalc { in bank_energy_in = bank_energy; }
}
part def 'Hif Driver' :> 'Base Driver' {           // subtype specializes base (`:>`)
    attribute cost_per_joule : Real = 5.0;
    calc hif_cost_calc : HifCostCalc {
        in cost_per_joule_in = cost_per_joule;
        in bank_energy_in = bank_energy;           // D-5 on an INHERITED attribute
    }
}

// Design: retype the nested driver to the subtype.
part plant {
    part :>> driver : 'Hif Driver';                // retype (`:>>` with a subtype)
}
```

Retyping counts as instantiation: `'Hif Driver'`'s `hif_cost_calc` AND the inherited
`base_power_calc` both instantiate. The validator's calc-bearing-no-instantiation check
(L6) treats a retype target as instantiated, so neither is reported as dropped.

Two rules to get right:
- The subtype should **specialize** the base def (`part def 'Hif Driver' :> 'Base Driver'`),
  not just share a name.
- A calc that replaces an inherited one reuses its name (same-QN redefinition), so the
  subtype's version wins.

Reference: `ife_plant` (driver retyped to `'Hif Driver'`, shape 3).

## Def-owned design attributes (D8)

A design attribute may be owned directly by a part def (not by a nested usage). It
resolves the same way — the matcher finds it on the def. No special handling is needed;
`attribute radius : Real = 0.5` on `part def Coil` is a first-class value source for a
template calc binding.

## The whole-plant value idiom (the headline)

A plant supplies a value to a nested part's calc in one of four ways. All four resolve
end-to-end — the value reaches the calc input with no bridge attribute. Pick by where the
value lives and whether you are also swapping the part's type.

**(a) Subtype-def literal reached through a usage-level retype.** The value lives on a
`:>>` in the *subtype def*; the design retypes the nested usage to that subtype, and the
literal is consumed cross-part.

```sysml
// Library: the subtype def carries the value.
part def 'Hif Driver' :> 'Ife Driver' {
    :>> efficiency = 0.35;                 // subtype-def literal
}
// Design: retype the usage to pull the subtype (and its value) in.
part hif_plant : 'IFE Power Plant' {
    part :>> driver : 'Hif Driver';        // usage-level retype
}
```

**(b) Bare no-retype override block.** The design keeps the part's type and overrides one
of its attributes with a bare `:>>` inside a `part :>> name { ... }` block.

```sysml
part hif_plant : 'IFE Power Plant' {
    part :>> target_factory {
        :>> cost_per_target = 10.0;        // bare :>> literal, no retype
    }
}
```

**(c) One-hop dotted override on a plain cross-part attribute.** The design reaches one
level down with a dotted `:>>` on the usage.

```sysml
part hif_plant : 'IFE Power Plant' {
    :>> chamber.cost_per_unit = 7.0;       // usage-level dotted override, one hop
}
```

**(d) In-part inherited-attr redefine.** A calc binds an inherited attribute
(`in flow_rate = throughput`), and the same def redefines that attribute below the binding.
Order does not matter — the redefine is seen even when it sits after the binding.

```sysml
part def 'Flow Sub' :> 'Flow Base' {       // 'Flow Base' declares `throughput`
    calc flow_calc : FlowCalc {
        in flow_rate = throughput;         // binds the inherited attribute...
    }
    :>> throughput = 8.0;                  // ...redefined below the binding
}
```

### Three rules that govern all four

- **Precedence — most specific wins:** *usage override (`:>>` on the usage) > specialized-def
  `:>>` > base-def value.* A `:>>` in the design (a/b/c) beats a subtype-def `:>>`, which beats
  the base def's declared value.
- **Entry points key by the source attribute's qualified name.** Renaming an input per
  consumer still collapses to **one** parameter (the calc inputs share the source attribute's
  QN), and one attribute feeding N consumers is **one** channel, not N. This is why the JSON
  input file has one key per source attribute, regardless of how many calcs read it.
- **Only LITERAL values propagate this way.** A `:>>` whose RHS is a chain or a computed
  expression does **not** silently vanish — it falls to the uncovered-parameter diagnostic, so
  the modeler sees an unresolved input rather than a wrong number. (And a value written as
  `attribute :>> attr = <expr>` is dropped at extraction — see semantic-operators.md and the
  L6 `attribute :>>`-with-expression warning.)

Reference fixtures: `plant_values` (all four mechanisms a/b/c/d, plus the fusion-tea vendored
plant as the real-scale exemplar), `plant_value_shapes` (the secondary shapes and their
observed labels), `spec_chain_twolevel` (the two-level specialization that mechanism (a) rides on).

## Cross-part chains and EXPOSE

A calc in one part can consume a calc output from another part. The value crosses the
boundary through an EXPOSE — a named attribute that surfaces the upstream output:

<!-- @measured evidence="EXPOSE surfacing measured by the expose-pattern fixtures; the refused self-named variant of this exact shape is pinned by self_named_rescue" owner-class=n/a outcome=generates -->
```sysml
part def RescuePlant {
    calc source_calc : SourceCalc { in raw = raw_flow; }

    // EXPOSE: surface the upstream calc output under a stable name.
    attribute throughput : Real = source_calc.throughput;

    calc sink_calc : SinkCalc {
        in throughput_in = throughput;   // D-5; the EXPOSE attribute supplies the value
    }
}
```

Multi-hop EXPOSE (through a nested part) and part-def-level EXPOSE (expanded per instance)
are both supported. See `expose-pattern.md` for how an EXPOSE name surfaces as an output.

Reference: `spec_chain_channel`, `spec_chain_twolevel` (cross-part chains through nested
parts).

## Secondary shapes and their limits

Beyond the four core mechanisms, a handful of syntactic shapes resolve — some cleanly, some
only partially. The `plant_value_shapes` fixture pins each shape's *observed* behavior, so
teach the ones that work and treat the rest as known-incomplete rather than as targets.

**Shapes that resolve correctly (teach these):**
- Bare `default 10.0` with no `:=` — a plain design-attribute default.
- Quoted enum def with a usage-level quoted `:>>` (`:>> wall = 'Wall Kind'::liquid_wall`).
- A quoted output-parameter name (`out attribute 'net cost'` de-quotes to `net_cost`).
- Style-E mixed outputs — a calc def with both `out attribute` and `return` members.
- A 5-deep specialization chain with abstract ends (`abstract part def 'Chain L1'` … `L5`).

**Shapes that are DEGRADED (document, do not rely on):**
- An attribute-def-typed attribute set by *nested* `:>>` (the `'Econ Param' { :>> value = … }`
  shape): the nested value does not reach a cross-part calc input.
- An inherited attribute redefined *below* an in-part binding: resolves for the local calc but
  degrades across a part boundary.

Reference: `plant_value_shapes` (every shape above, each labelled at capture).

### The indexed form is valid SysML, and not implemented

An authored index selects one occurrence by position:

```sysml
part cells : Cell[3];
attribute picked : Real = cells#(2).mass;   // refused, not reinterpreted
```

This is well-formed SysML and the parser resolves it. What is not implemented is generating
code for it, so the toolchain refuses it **by name** rather than choosing an occurrence on the
author's behalf. Agentic raises `SemanticEvidenceError` with
`INDEXED_REFERENCE_UNSUPPORTED`; codegen surfaces the same refusal as
`SI_INDEXED_SOURCE_UNSUPPORTED`, carrying the authored reference and its `file:line`.

The refusal is structural, not a check that could be forgotten. `inspect_reference_uses`
returns a closed union, and the indexed variant carries no resolved path at all — so there is
nothing for a downstream consumer to read while ignoring the index. Dropping the `#(2)` and
wiring `cells[0].mass` would be a different expression than the one written, which is the
class of substitution this toolchain exists to prevent.

To model per-occurrence values today, name the occurrence instead of indexing it — give the
part its own usage and reference that usage by name.

### Non-float entry points are now diagnosed (Item 5)

An entry point must be float-valued. A bool/string/enum-typed entry point (the `wall_type`
idiom — an enum-valued attribute one hop from a calc input) is no longer silently omitted:
codegen diagnoses it. Model guidance: **keep entry points float-valued**; carry a categorical
choice as a separate design decision, not as a calc input. Reference: `plant_value_shapes`
(the `wall` attribute).

### Keep cross-part chains shallow (D3)

A cross-part reference that must resolve to a value should be **one hop**. A multi-hop dot
chain — `station.array.derived_calc.derived_value` — truncates: extraction keeps only the
first segment of the `source_path`, so the deep reference does not resolve to the intended
producer. Item 5 turned the worst multi-hop case into a loud reject (D3-2) rather than a
silent mis-wire, but the rule stands: **keep cross-part references to one hop**; surface a
deep value through an intermediate EXPOSE attribute instead. Reference: `deep_cross_scope_probe`.

### Aggregation operators (Item 5)

In an aggregation expression, `^` is exponentiation and now maps to Python `**`. Earlier it
was silently passed through as Python bitwise-XOR — a wrong number with no diagnostic. An
operator with no valid translation now marks the aggregation unsupported (a warning) instead
of emitting a silent mistranslation.

## Sibling disambiguation

Two same-type sibling parts on a plant each produce their own instance-scoped calc, so a
part-def-level EXPOSE reaching a calc output resolves per instance — the two siblings do
not collide. Bindings disambiguate by instance scope (the owning part usage), not by type.

Reference: `sibling_channel_ambiguity` (two same-type siblings), `wi014_toy` (minimal
two-hop shape).

## Related

- `expose-pattern.md` — EXPOSE surfacing details.
- `semantic-operators.md` — `:>` vs `:>>` vs `=`, redefinition precedence, the bare-`:>>`
  value idiom.
- `adr002-calculations.md` — inline FORMULA vs calc def, and which derived expressions
  (calc-output arithmetic, self-reference, dotted path) still belong in calc defs.
