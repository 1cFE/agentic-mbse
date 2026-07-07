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
