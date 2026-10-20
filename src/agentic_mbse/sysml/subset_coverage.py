"""What the subset profile has no rule for yet: the coverage limit a `clear` verdict carries.

`clear` means only "no refusals found by the implemented rules" (ADR 0001 invariant 2). This
module names what the rules do not cover, so L6 can print it beside the verdict and record it in
the JSON report (Item 3 design D11). It has its own version, separate from
`SUBSET_PROFILE_VERSION`, so changing the list never moves the profile's version or digest.

The two lists are copied from the inventories (this repo's `tests/fixtures/subset_profile/inventory/`
and, for codegen sites, sysml-codegen's site account):

- `NO_RULE_FAMILIES`: the matrix rows (`matrix.toml`) whose class is `tracked_gap` and whose
  outcome is `refused`. The generator refuses these shapes and no rule reports them.
- `FOLLOW_UP_SITES`: the site-account rows with disposition `explicit_follow_up`: raise sites
  whose refusals the contract does not report yet. agentic-mbse's shared evidence walkers come
  from this repo's `site_account.csv`; sysml-codegen's sites come from codegen's own account
  (`tests/expectations/subset_profile/site_account.csv` there), which holds them since
  EXEC-SUBSET-CONTRACT Item 2a moved them.

A test pins the content to `SUBSET_COVERAGE_VERSION` by digest and checks the families and the
agentic-mbse sites against the inventory; a sysml-codegen conformance test, run by the pre-merge
gate, checks the codegen sites against codegen's account. Changing either list means bumping
the version.
"""

SUBSET_COVERAGE_VERSION = "subset-coverage/v2"

NO_RULE_FAMILIES: tuple[str, ...] = (
    "DEEP-QUALIFIED-WIRING",
    "ES-002",
    "ES-008",
    "ES-009",
    "ES-010-REFUSAL",
    "CALC-DEF-BARE-RESULT",
)

FOLLOW_UP_SITES: tuple[str, ...] = (
    "agentic_mbse/sysml/constraint_extraction.py::_expression_ir::shared-evidence::EXPRESSION_DEPTH_EXHAUSTED::1",
    "agentic_mbse/sysml/constraint_extraction.py::_reference_node::shared-evidence::RESOLVED_TARGET_MISSING::1",
    "agentic_mbse/sysml/expression.py::get_reference_name::shared-evidence::RESOLVED_TARGET_MISSING::1",
    "agentic_mbse/sysml/expression.py::reconstruct_expression::shared-evidence::EXPRESSION_DEPTH_EXHAUSTED::1",
    "agentic_mbse/sysml/expression.py::traverse_expression::shared-evidence::EXPRESSION_DEPTH_EXHAUSTED::1",
    "agentic_mbse/sysml/reference_use.py::_chain_head_segments::shared-evidence::EXPRESSION_KIND_UNSUPPORTED::1",
    "agentic_mbse/sysml/reference_use.py::_chain_head_segments::shared-evidence::RESOLVED_TARGET_MISSING::1",
    "agentic_mbse/sysml/reference_use.py::_chain_head_segments::shared-evidence::RESOLVED_TARGET_MISSING::2",
    "agentic_mbse/sysml/reference_use.py::_chain_use::shared-evidence::RESOLVED_LEAF_MISSING::1",
    "agentic_mbse/sysml/reference_use.py::_chain_use::shared-evidence::RESOLVED_TARGET_MISSING::1",
    "agentic_mbse/sysml/reference_use.py::_invocations::shared-evidence::EXPRESSION_DEPTH_EXHAUSTED::1",
    "agentic_mbse/sysml/reference_use.py::_walk::shared-evidence::EXPRESSION_DEPTH_EXHAUSTED::1",
    "agentic_mbse/sysml/subset_extraction.py::_conditionals::shared-evidence::EXPRESSION_DEPTH_EXHAUSTED::1",
    "agentic_mbse/sysml/syside_adapter.py::SysideAdapter.authored_text::shared-evidence::RESOLVED_TARGET_MISSING::1",
    "sysml_codegen/elaboration/elaborate.py::_EffectiveInputFormalSelector.effective_input_formals::coded::SI_REDEFINITION_INVALID::1",
    "sysml_codegen/elaboration/elaborate.py::_ExactElaborator._apply_deep_literal_redefinitions::coded::OVERRIDE_TARGET_MISSING::1",
    "sysml_codegen/elaboration/elaborate.py::_ExactElaborator._apply_deep_literal_redefinitions::coded::OVERRIDE_TARGET_MISSING::2",
    "sysml_codegen/elaboration/elaborate.py::_ExactElaborator._build_calculation_nodes::coded::SI_EDGE_DANGLING::1",
    "sysml_codegen/elaboration/elaborate.py::_ExactElaborator._build_calculation_nodes::coded::SI_REDEFINITION_INVALID::1",
    "sysml_codegen/elaboration/elaborate.py::_ExactElaborator._build_value_nodes::coded::SI_REDEFINITION_INVALID::1",
    "sysml_codegen/elaboration/elaborate.py::_ExactElaborator._calculation_input_attribute::coded::SI_EDGE_DANGLING::3",
    "sysml_codegen/elaboration/elaborate.py::_ExactElaborator._collect_bound_members::coded::SI_EDGE_DANGLING::1",
    "sysml_codegen/elaboration/elaborate.py::_ExactElaborator._constraint_metadata::coded::SI_EDGE_DANGLING::1",
    "sysml_codegen/elaboration/elaborate.py::_ExactElaborator._effective_formal_for_member::coded::SI_EDGE_DANGLING::1",
    "sysml_codegen/elaboration/elaborate.py::_ExactElaborator._feature_python_type::coded::SI_EDGE_DANGLING::1",
    "sysml_codegen/elaboration/elaborate.py::_ExactElaborator._feature_python_type::coded::SI_EDGE_DANGLING::2",
    "sysml_codegen/elaboration/elaborate.py::_ExactElaborator._feature_python_type::coded::SI_EDGE_DANGLING::3",
    "sysml_codegen/elaboration/elaborate.py::_ExactElaborator._index_calculation_payloads::coded::SI_ID_MISSING::1",
    "sysml_codegen/elaboration/elaborate.py::_ExactElaborator._index_calculation_payloads::coded::SI_ID_MISSING::2",
    "sysml_codegen/elaboration/elaborate.py::_ExactElaborator._index_constraint_associations::coded::SI_EDGE_DANGLING::1",
    "sysml_codegen/elaboration/elaborate.py::_ExactElaborator._index_constraint_associations::coded::SI_EDGE_DANGLING::2",
    "sysml_codegen/elaboration/elaborate.py::_ExactElaborator._index_constraint_associations::coded::SI_EDGE_DANGLING::6",
    "sysml_codegen/elaboration/elaborate.py::_ExactElaborator._output_ports::coded::SI_EDGE_DANGLING::1",
    "sysml_codegen/elaboration/elaborate.py::_ExactElaborator._resolve_bindings::coded::SI_EDGE_DANGLING::1",
    "sysml_codegen/elaboration/elaborate.py::_ExactElaborator._resolve_calculation_output::coded::SI_OCCURRENCE_AMBIGUOUS::1",
    "sysml_codegen/elaboration/elaborate.py::_ExactElaborator._resolve_semantic_reference::coded::SI_OCCURRENCE_MISSING::1",
    "sysml_codegen/elaboration/elaborate.py::_ExactElaborator._resolve_semantic_reference::coded::SI_OCCURRENCE_MISSING::2",
    "sysml_codegen/elaboration/elaborate.py::_ExactElaborator._typed_definition::coded::SI_TYPE_INVALID::1",
    "sysml_codegen/elaboration/expression_evidence.py::ExpressionEvidenceInventory.__init__::free-text::ExpressionInventoryError::1",
    "sysml_codegen/elaboration/graph.py::InstanceGraph._expression_reference_count::unrecognized::UnsupportedExpressionIRError::1",
    "sysml_codegen/elaboration/graph.py::InstanceGraph._validate_occurrences::coded::SI_EDGE_DANGLING::1",
    "sysml_codegen/elaboration/identity.py::declaration_id_for::coded-fixed::SI_ID_MISSING|SI_ID_UNSTABLE::1",
    "sysml_codegen/elaboration/occurrence.py::FeatureSlotIndex._root_of::coded-fixed::SI_REDEFINITION_INVALID::2",
    "sysml_codegen/elaboration/occurrence.py::FeatureSlotIndex.effective_declaration::coded-fixed::SI_REDEFINITION_INVALID::3",
    "sysml_codegen/elaboration/occurrence.py::OccurrenceIndex.resolve_address::coded::SI_OCCURRENCE_AMBIGUOUS::1",
    "sysml_codegen/elaboration/occurrence.py::OccurrenceIndex.resolve_address::coded::SI_OCCURRENCE_AMBIGUOUS::2",
    "sysml_codegen/elaboration/occurrence.py::OccurrenceIndex.resolve_address::coded::SI_OCCURRENCE_MISSING::1",
    "sysml_codegen/elaboration/occurrence.py::OccurrenceIndex.resolve_address::coded::SI_OCCURRENCE_MISSING::2",
    "sysml_codegen/elaboration/occurrence.py::_effective_type::coded-fixed::SI_REDEFINITION_INVALID::1",
    "sysml_codegen/elaboration/occurrence.py::build_feature_slot_index::coded-fixed::SI_REDEFINITION_INVALID::2",
    "sysml_codegen/elaboration/occurrence.py::build_occurrence_index.add_usage::coded-fixed::SI_REDEFINITION_INVALID::1",
    "sysml_codegen/elaboration/occurrence.py::build_occurrence_index.native_child_declarations::coded-fixed::SI_REDEFINITION_INVALID::1",
    "sysml_codegen/elaboration/project.py::_Projection._compile_computed_expression.render::coded::SI_SNAPSHOT_INVALID::5",
    "sysml_codegen/extraction/binding_source.py::bound_formal::coded::RESOLVED_TARGET_MISSING::1",
    "sysml_codegen/extraction/binding_source.py::exact_path_from_relationship::coded::RESOLVED_TARGET_MISSING::3",
    "sysml_codegen/extraction/calc_compat_renderer.py::_render::free-text::CompilationError::1",
    "sysml_codegen/extraction/calc_compat_renderer.py::_render::free-text::CompilationError::2",
    "sysml_codegen/extraction/calc_compat_renderer.py::_render_literal::free-text::CompilationError::1",
    "sysml_codegen/extraction/calc_compat_renderer.py::_render_operator::free-text::CompilationError::1",
    "sysml_codegen/extraction/calc_compat_renderer.py::_render_operator::free-text::CompilationError::2",
    "sysml_codegen/extraction/calc_compat_renderer.py::_render_operator::free-text::CompilationError::3",
    "sysml_codegen/extraction/calc_compat_renderer.py::_render_reference::free-text::CompilationError::1",
    "sysml_codegen/extraction/calc_compat_renderer.py::_render_reference::free-text::CompilationError::2",
    "sysml_codegen/extraction/calc_compat_renderer.py::render_calc_expression::free-text::CompilationError::1",
    "sysml_codegen/extraction/expression_compiler.py::_exact_reference_ids::free-text::CompilationError::1",
    "sysml_codegen/extraction/expression_compiler.py::compile_calc_def_exact.add_node::free-text::CompilationError::1",
    "sysml_codegen/extraction/extractor.py::SysMLDataExtractor._extract_attribute::coded-fixed::SI_TYPE_INVALID::1",
    "sysml_codegen/extraction/extractor.py::SysMLDataExtractor._extract_attribute::coded-fixed::SI_TYPE_INVALID::2",
    "sysml_codegen/extraction/extractor.py::SysMLDataExtractor._extract_calculation_definition::coded-fixed::SI_EVIDENCE_INCOMPLETE::1",
    "sysml_codegen/generation/predicate_compiler.py::_compile_reference::free-text::PredicateCompileError::2",
)
