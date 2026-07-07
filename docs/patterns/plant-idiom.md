# The Plant Idiom: Cross-Part Calc Wiring

How a design wires calculations across nested parts. These are the shapes codegen
supports for building a plant model out of reusable part defs, each carrying its own
template calcs. Covers cross-part chains, retyping, EXPOSE surfacing, and sibling
disambiguation.

Reference fixtures live in the sysml-codegen repo under `tests/fixtures/`; each shape
below names the fixture that exercises it.

## The core shape

A plant is a part with nested parts. Each nested part def owns *template calcs* — calc
usages that compute the part's outputs from its attributes. When the plant instantiates
the nested part, each template calc becomes an instance-scoped calc that runs in the
pipeline.

```sysml
part def Coil {
    attribute radius : Real = 0.5;

    // Template calc: computes volume from the coil's own radius.
    calc volume_calc : VolumeCalc {
        in radius = radius;          // design-attribute binding (see below)
    }
}

part def Plant {
    part coil : Coil;                // instantiating Coil brings volume_calc into the pipeline
}
```

Reference: `ife_plant` (a full plant with drivers, coils, and chambers).

## Design-attribute bindings (`in x = x`)

A template calc binds its input to a same-named attribute on the owning part:
`in radius = radius`. This reads as self-referential but is not — the left `radius` is
the calc's input parameter, the right `radius` is the part's attribute. The attribute is
the value source.

This is a **supported** shape. The validator (L2 self-named-binding check) FAILs a
`in x = x` binding *only* when the owning part carries no feature named `x` at all — a
true dead-end where the value has nowhere to come from. An attribute named `x` (even a
bare literal), a sibling calc output named `x`, or an inherited attribute named `x` all
cover it.

Reference: `ife_plant` carries ~21 of these; the true dead-end is the agentic-mbse
`item12/self_named_deadend` fixture.

## Retyping to pull in a subtype's calcs (D2)

A design may retype a nested part usage to a subtype to pull in the subtype's template
calcs, while keeping the base def's calcs:

```sysml
// Library: subtype specializes the base and adds its own calc.
part def 'Base Driver' {
    attribute bank_energy : Real = 10000000.0;
    calc base_power_calc : DriverPowerCalc { in bank_energy = bank_energy; }
}
part def 'Hif Driver' :> 'Base Driver' {           // subtype specializes base (`:>`)
    attribute cost_per_joule : Real = 5.0;
    calc hif_cost_calc : HifCostCalc {
        in cost_per_joule = cost_per_joule;
        in bank_energy = bank_energy;              // binds against an INHERITED attribute
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

```sysml
part def RescuePlant {
    calc source_calc : SourceCalc { in raw = raw_flow; }

    // EXPOSE: surface the upstream calc output under a stable name.
    attribute throughput : Real = source_calc.throughput;

    calc sink_calc : SinkCalc {
        in throughput = throughput;   // covered by the EXPOSE attribute above
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
