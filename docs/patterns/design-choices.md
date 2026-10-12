# Design Choices: Evaluate the Supplied Design

A model evaluates the design it is given. Choosing that design (which equipment is installed, how much inventory, what capacity) is a separate decision. This document is the rule for keeping the two apart, and the evidence that shows they were kept apart.

## When to Use This Document

Read it before designing, changing or reviewing:
- which quantities a model or analysis takes as chosen inputs and which it calculates
- a binding that sets installed equipment, inventory or capacity
- a sizing, selection or search policy
- an operating-point closure
- a cost that scales with demand

## Core Principle

Physical relationships and performance limits evaluate a design. A policy that chooses a design is something else, and the two stay separate. A calculation or binding must not silently remove a design choice by setting installed equipment, inventory or capacity from required performance. Once a model sizes a component from demand, it has decided which design parameters are free and which are derived, and every use of the model inherits that decision without having made it.

## The Rule

1. **Evaluate the supplied design.** Keep physical demand, installed design or capacity, and any suggested design separate. When the supplied design is insufficient, report the shortfall; do not enlarge the design automatically.
2. **Keep selection policies separate and visible.** An explicitly authorized sizing or search analysis may propose a design. Its policy must stay separately identifiable, and the design it selects must be evaluable without rerunning the policy. Implementation convenience does not authorize hiding a design-selection rule inside a physical component.
3. **State what each analysis specifies and what it solves for.** Each analysis's contract must say which quantities it takes as given and which it calculates, with the authority for each. An existing calculation direction, a reference design or a quality target is not authority to fix that choice for every use of the component.
4. **Document calculation direction.** A numerical routine may have directional inputs and outputs. Document how its direction relates to the supported analysis and to the design choices available. This rule does not require an acausal solver, and it does not require every related quantity to be specifiable at once.
5. **Balances and identities are not automatically violations.** Ordinary physical balances, geometry identities and operating-point calculations must state the independent quantities they selected and their assumptions. A calculated requirement is not evidence of installed capacity, and it is not permission to bind installed capacity to it.
6. **Report empirical validity separately from physical adequacy.** An evaluation outside a performance model's empirically supported domain is a limitation of that model. It is neither a failed physical constraint nor permission to extrapolate silently. An invalid or unsupported evaluation is never reported as a pass.
7. **Inventory and cost follow the selected design.** A supplied equipment choice must remain the basis of its represented inventory and cost. A cost proxy that scales equipment cost with demand, instead of costing the installed equipment, must say which demand-matched equipment it assumes and that installed capacity was not evaluated. It must not be presented as a fully evaluated chosen design.

The rule applies to direct edits and to patterns inherited from existing code, not only to new work. Existing code, agreement with a reference, and passing scores do not waive it. Skipping or combining stages does not waive its evidence or its review.

## What to Record

In the existing spec, design or goal record, list the affected quantities, units, physical relationships, current and proposed roles (chosen, calculated, requirement, installed capacity, policy-selected), the binding location, and the authority for any role change. A small change can use a short paragraph; several changed choices need a table. Call out any parameter that leaves the public interface or becomes a calculated binding. Defaults, mode switches and multipliers must not conceal automatic adequacy.

- The spec names the design choices the consumer must keep.
- The design records the affected roles, physical relationships, selection policies, authority and actual binding paths.
- The implementation keeps those choices through every supported execution route and through downstream costs.
- The handoff carries this evidence. A repair is not complete on scores or baseline reproduction alone.

## Review

“Process Selection” in `modeling_project/MODELING_PROCESS.md` routes design-choice changes to focused independent design review. That review inspects the actual equations and bindings, including downstream part attributes and cost consumers. It checks the bindings themselves, not names such as `required`, `selected` or `sizing_mode`.

## Acceptance

For each repaired or introduced capacity or fit relationship, use the supported execution route to exercise an insufficient and a sufficient supplied design within the performance model's domain. Check that the selected design is unchanged, the constraint result changes meaningfully, and inventory and cost follow the selected design. Where the intended interface lets demand vary while hardware is held fixed, test that separately. An unsupported-domain case must remain explicitly unsupported, with no manufactured success. For an operating-point closure or a cost proxy where these tests do not apply, record why and check its stated assumptions instead.

A review must record compliance for the affected scope as compliant, violated or unverified, with evidence. Unknown compliance does not count as completed remediation.

## Validated Pattern

A sump basin and a drain pump. The library calculates the flow the pump must remove; the design decides which pump is installed. Reference fixture: agentic-mbse `tests/fixtures/sump_pump/`.

**Wrong: the pump is sized from demand.** ADR-002 allows this placement (a library calc, exposed in the design), and every validation level passes. The design is still selected inside the model: installed capacity follows required flow, and exposing `sizing_margin` does not make it a choice.

```sysml
// library
calc def PumpSizing {
    in required_flow : Real;
    in margin : Real;
    return capacity : Real = required_flow * margin;
}

// design, inside part station
part pump : DrainPump {
    attribute sizing_margin : Real = 1.2;
    calc sizing : PumpSizing {
        in required_flow = demand.required_flow;
        in margin = sizing_margin;
    }
    :>> installed_flow_capacity = sizing.capacity;
}
```

**Right: the design supplies the pump, and a check reports fit.** Installed capacity is a value the design owns. Required flow comes from a library calc. A one-sided `assert constraint` reports whether the supplied pump is enough and changes nothing: the feasibility-gate move in [constraints.md](constraints.md).

```sysml
// library
constraint def CapacityCoversDemand {
    in installed : Real;
    in required : Real;
    installed >= required
}

// design, inside part station
part pump : DrainPump {
    :>> installed_flow_capacity = 0.25 [m^3/s];
}
calc demand : RequiredPumpFlow {
    in inflow = basin.design_inflow;
    in allowed_rise_rate = basin.allowed_rise_rate;
    in basin_area = basin.area;
}
attribute required_flow : Real = demand.required_flow;
assert constraint pump_fit : CapacityCoversDemand {
    in installed = pump.installed_flow_capacity;
    in required = required_flow;
}
```

To try another pump, change the supplied value. An insufficient pump fails `pump_fit`; nothing enlarges it.

## Examples

| Authored | Reading |
|---|---|
| `capacity = required_flow * margin`, bound as installed capacity | An automatic design-selection rule, even when `margin` is exposed |
| `required_area` compared with an independently selected installed area | Preserves the distinction; the comparison reports fit |
| `volume = area * length` | A geometry identity, not an automatic adequacy rule |
| A calculated required flow | Not evidence of installed pump capacity |
| A calculated required exchanger area | Not permission to bind it to installed exchanger area |

## Common Mistakes

**Replacing one hidden fixed choice with another.** Swapping one margin for another, or for a sizing mode that is on by default, leaves the design selected inside the model. Make the installed value a supplied input and report the shortfall.

**Reading compliance off names.** An attribute called `selected` can still be bound to demand. Inspect the binding.

## Related Patterns

- [constraints.md](constraints.md), “When should you write an equality at all?” (equality intent): the constraint-side sibling. An exact equality over a parameter meant to vary deletes a degree of freedom; a binding that sets installed capacity from demand deletes a design choice. Both keep the design space open.
- [adr002-calculations.md](adr002-calculations.md): placement and role are separate checks. An EXPOSE that ADR-002 allows can still bind installed capacity to demand.
- [semantic-operators.md](semantic-operators.md): a `default :=` margin can hide automatic adequacy behind a value that looks overridable.
- [plant-idiom.md](plant-idiom.md), “Binding a modelled value into a calculation”: how to write a binding once its role is decided.

## Verification

`agentic-mbse validate` cannot see this rule: both forms above pass all six levels. Check by hand:

1. For each installed capacity, equipment or inventory attribute the change touches, read its value expression. A supplied value passes. An identity over supplied values, such as `volume = area * length`, passes. An expression that reaches a demand or requirement quantity, directly, through a calc output or through a margin, is a selection rule. It needs an authorized, separately identifiable policy.
2. Run the Acceptance tests through the supported execution route, and record compliance as Acceptance says.

---

`[AGENT]` (obligations ratified by owner, 2026-09-20; generalization 2026-10-11, at the owner's direction). The *need* for this rule is owner-stated (2026-09-20): “As soon as you start introducing ‘sizing’, then you are basically pre-defining which design parameters are ‘free’ and which are ‘derived’. this is explicitly what we wanted to avoid.” The obligations are agent-written applications of that principle, ratified when the owner asked for their enforcement. This document is the one statement of the rule. A project requirement that applies it cites this document and states only the project's own application.
