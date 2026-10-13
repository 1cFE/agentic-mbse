# Adoption runbook step 5 (design DD14): the route modules import the installed study package.
#
# Each study_route.py imports scripts.study, which read coverage would then see as a read of
# fusion-tea's own files rather than of the installed tools (B8). The rewrite changes the import
# line and nothing else; prose that names scripts/study/ is left as written history.
#
# The nine files, from CONSUMER_SURFACE.md lines 43, 50, 57, 62, 67, 72, 89, 97 and 106 at
# fusion-tea b06585709 (the design, amended at 1f69dd7, counts nine). Name the nine files, never
# a pathspec glob: git's `*` crosses `/`, so a glob would also match the route copies inside
# committed records (<record>/results/sources/, <record>/preparation/), which must never change.
# Apply from fusion-tea's root:
#
#   ROUTES=(
#     exploration/aries_integrated/studies/study_route.py
#     exploration/component_alternatives/studies/study_route.py
#     exploration/costed_loop_brayton/studies/study_route.py
#     exploration/exchanger_architecture/thermal_requirements/studies/study_route.py
#     exploration/ife_e2e/studies/study_route.py
#     exploration/magnet_materials/studies/study_route.py
#     exploration/stellarator_e2e/studies/study_route.py
#     exploration/stellarator_materials/studies/study_route.py
#     exploration/whole_plant_conversion/studies/study_route.py
#   )
#   sed -i -f routes.sed "${ROUTES[@]}"
#
# Check: git grep -n 'from scripts.study' -- "${ROUTES[@]}" prints nothing.
s/^from scripts\.study import /from sysml_codegen.study import /
