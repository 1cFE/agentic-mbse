# C3 evidence: shipped guidance can't silently teach a construct the generator refuses

Captured 2026-10-15T13:56Z. agentic-mbse `d546a00f` (shipped asset dirs `skills agents adapters project_templates docs` clean; the tree is dirty only in `.project/`, `.gitignore` and this folder). sysml-codegen `b5663c07`, clean. SysIDE 0.8.4. Scratch: `/tmp/claude-1000/-home-reid-src-agentic-mbse/8cecfa0f-3dca-4be9-bcbc-86b4acc4ae95/scratchpad/c3/`.

## Re-run (from the agentic-mbse root)

```bash
uv run python .project/concepts/convince-me-exec-subset/evidence/03-fences.py        # inventory + parse  -> 03-inventory.{csv,log}
uv run python .project/concepts/convince-me-exec-subset/evidence/03-elaborate.py     # generate + L6      -> 03-elaboration.{log,json}
uv run python .project/concepts/convince-me-exec-subset/evidence/03-make-manifest.py # honest categories  -> 03-manifest.yaml
uv run pytest -q -p no:cacheprovider .project/concepts/convince-me-exec-subset/evidence/03-harness-test.py   # -> 03-harness-baseline.log
bash .project/concepts/convince-me-exec-subset/evidence/03-controls.sh               # sabotage           -> 03-control-*.log
```

## Files

- `03-fences.py`: a fence scanner modelled on CommonMark that recurses into non-SysML fences, so it catches nested template fences. It writes the stable id `path#heading-anchor@sha256[:12]`, and loads each fence standalone and wrapped in a package with standard imports.
- `03-contexts/`: the prelude and harness files that make 5 fences runnable. A prelude supplies the definitions a fence names. A harness supplies the instantiation and bindings.
- `03-elaborate.py`: runs the real `sysml-codegen generate` and `agentic-mbse validate --level=6` on every complete fence and every context case.
- `03-manifest.yaml`: one entry per fence. Its categories are `fragment`, `definition`, `executable`, `native-only` and `negative`.
- `03-harness-test.py`: the prototype contract test.

## Results

- **212 shipped fences across 22 files.** 4 are nested inside another fence. The 12 vendored reference fences are excluded.
- **Only 41 of 212 (19%) load with zero errors, alone or wrapped.** 116 parse but name definitions they don't include, and 55 don't parse standalone.
- **26 of 212 (12%) get a generator verdict today:** 9 executable, 14 native-only and 3 negative. 17 are clean definitions with nothing to generate, and 169 are hash-pinned fragments.
- **20 generator runs refused or errored, and L6 reported nothing on 8 of them.** The 8 are f060, f064, f071, f081, f123 and f132; f060 and f071 were silent with and without their context.
- **The baseline harness passes:** 213 of 213.
- **All three controls fail the harness, as intended:**
  - (a) Relabelling the calc-owned assert example as executable fails with `SI_CONSTRAINT_UNATTACHED`.
  - (b) A one-character fragment edit fails, because the content is no longer in the manifest and the manifest entry has gone stale.
  - (c) Swapping a checked example for an unchecked one fails, even though the fence count stays at 212.

## Audit clarification (2026-10-15)

The 26 generation verdicts comprise 9 executable, 14 native-only and 3 negative entries. The remaining entries comprise 17 checked definitions and 169 hash-pinned fragments; they are not all hash-only. The initial parser inventory loads 41 fences cleanly, which measures standalone/import-wrapped syntax completeness rather than executable coverage. Text-name output checks are prototype approximations, not semantic omission proofs.
