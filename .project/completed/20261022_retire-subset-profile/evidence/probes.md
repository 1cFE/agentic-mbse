# Probes: what the generator does with the three structural limits

Run 2026-10-21 with `uv run sysml-codegen check --models <probe folder>` from the sysml-codegen worktree `/home/reid/src/subset-conformance/sysml-codegen` at `529830cf` (branch `subset-profile-screen`, before any Phase 1 edit), license sourced. Each model is `probes/<name>/model.sysml`; the full `check` output is beside it in `check.txt`. Exit codes: 0 builds, 1 refused.

| probe | what the model does | exit | generator answer |
|---|---|---|---|
| a `a_assert_in_calc_usage` | `assert constraint` inside a calc usage owned by a part | 1 | `SI_CONSTRAINT_UNATTACHED`, reason `elaboration_constraint_owner_unmapped` ("constraint owner does not match a supported mapped metatype: probe_a::Host::doubled") |
| b `b_assert_on_part` | the same assert on the part itself | 0 | builds (3 modules) |
| c `c_mult_star` | part usage `kids : Child[*]` | 1 | `SI_MULTIPLICITY_UNRESOLVED`, reason `occurrence_multiplicity_upper_unresolved` ("upper multiplicity on 'kids' is not a known finite integer") |
| d `d_mult_zero_star` | part usage `kids : Child[0..*]` | 1 | `SI_MULTIPLICITY_UNRESOLVED`, reason `occurrence_multiplicity_upper_unresolved` |
| e `e_mult_exact_3` | part usage `kids : Child[3]` | 0 | builds (3 modules); `generate` expands `host__kids[0..2]` |
| f1 `f1_mult_package_attr_N` | `kids : Child[N]` with `attribute N : Integer = 3;` at package level | 1 | `SI_MULTIPLICITY_UNRESOLVED`, reason `occurrence_multiplicity_upper_unresolved` (reference `'N'`) |
| f2 `f2_mult_part_attr_child_count` | `kids : Child[child_count]` with `attribute child_count : Integer = 3;` in the owning part def | 0 | builds (3 modules); `generate` expands `host__kids[0..2]`, same as `[3]` |
| g1 `g1_calc_sequence_input_bound_to_sequence_attr` | calc def `in x : Real[0..*] ordered nonunique`, used from a part with `in x = loads`, where `attribute loads : Real[3] = (1.0, 2.0, 3.0)` | 1 | `SI_EDGE_DANGLING`, reason `graph_computed_ir_unsupported`, on `probe_g__host__loads` (the attribute, see g4) |
| g2 `g2_calc_sequence_input_bound_to_scalar` | the same sequence-typed input bound to one scalar attribute (`in x = load`) | 0 | builds (1 module) |
| g3 `g3_calc_sequence_input_bound_to_tuple` | the same input bound to a tuple expression `in x = (a, b)` | 1 | `SI_EXPRESSION_SOURCE_UNSUPPORTED`, reason `binding_source_form_unsupported` ("unsupported exact source form expression_source ('a, b')") |
| g4 `g4_sequence_attr_without_calc` | `attribute loads : Real[3] = (1.0, 2.0, 3.0)` in a part, no calc reads it | 1 | `SI_EDGE_DANGLING`, reason `graph_computed_ir_unsupported`, on `probe_g4__host__loads` |
| h `h_calc_single_input` | calc def `in x : Real`, used from a part with a single value | 0 | builds (1 module) |

## What this means for the guidance

- **Asserts (a, b).** As expected: an `assert constraint` inside a calc usage is refused; on the part it builds.
- **Part multiplicity (c-f2).** Open bounds (`[*]`, `[0..*]`) are refused. An exact literal builds. An attribute-valued bound builds when the attribute is declared in the owning part def (`[child_count]`), and is refused when the attribute is at package level (`[N]`). So for D-d: "exact" means a literal or an Integer attribute of the owning part def with a literal value; a package-level attribute does not count. Not checked: an attribute inherited from a supertype, an attribute computed by an expression, or a bound set in a redefinition.
- **Calc inputs (g1-g4, h). Surprise.** The generator does not refuse the sequence-typed input declaration itself: g2 (a `Real[0..*] ordered nonunique` input bound to one scalar) builds. What it refuses is any sequence value reaching the input: a tuple-valued attribute is refused on its own (g4, even with no calc reading it), and a tuple expression in the binding is refused (g3). The Item 2a case `binding-source__scalar_actual__owner_instantiated` (sequence input with `sum`, bound to a scalar) is stored as `generated` too, with a `compile_invocation` stub on the result. So the accurate limit is "a calculation input receives one value; do not pass a sequence (a tuple-valued attribute or a tuple expression)", not "do not declare a sequence input". The guidance's wording should follow that.
