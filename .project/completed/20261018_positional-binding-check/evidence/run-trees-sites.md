# Mutation and stale sites (written before each check runs)

Selected by `scripts/positional_binding/run_trees.py` from source text alone, by the rules in design Appendix B.

- **Mutation site** (chosen before the check runs): `models/designs/aries_cs_integrated/plant.sysml` usage line 19 (type `'Fusion Source Selector'`), inputs `calculated_power_in` (line 20) and `reference_power_in` (line 21), in the order the definition declares them. Swapped.
- **Stale site** (chosen before the check runs): pin `aries_constituent_inventory::behind_divertor::recipe | fraction_1_in | sector_constituent_inventory::'Three Constituent Recipe Summary'::fraction_2_in`, `models/designs/aries_cs_transfer/constituent_inventory.sysml:138`, rewritten from `in fraction_1_in = lipb.volume_fraction;` to `in :>> fraction_1_in = lipb.volume_fraction;`.
