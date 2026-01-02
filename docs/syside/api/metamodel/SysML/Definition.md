<div id="definition" class="section">

<span id="metamodel-sysml-definition"></span>

# Definition[](#definition "Link to this heading")

`Definition` is defined in SysML specification on [page 61](https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=61). Excerpt from the machine readable specification:

> 
> 
> <div>
> 
> A `Definition` is a `Classifier` of `Usages`. The actual kinds of `Definition` that may appear in a model are given by the subclasses of `Definition` (possibly as extended with user-defined `SemanticMetadata`).
> 
> Normally, a `Definition` has owned Usages that model `features` of the thing being defined. A `Definition` may also have other `Definitions` nested in it, but this has no semantic significance, other than the nested scoping resulting from the `Definition` being considered as a `Namespace` for any nested `Definitions`.
> 
> However, if a `Definition` has `isVariation` = `true`, then it represents a *variation point* `Definition`. In this case, all of its `members` must be `variant` `Usages`, related to the `Definition` by `VariantMembership` `Relationships`. Rather than being `features` of the `Definition`, `variant` `Usages` model different concrete alternatives that can be chosen to fill in for an abstract `Usage` of the variation point `Definition`.
> 
> </div>

The following diagram shows the inheritance hierarchy of `Definition` according to the specification:

<div class="align-center" data-align="center">

<div class="graphviz">

![// Class: Definition digraph { Definition \[label="Definition (SysML)" shape=plaintext\] Classifier -\> Definition Classifier \[label="Classifier (KerML)" shape=plaintext\] Type -\> Classifier Type \[label="Type (KerML)" shape=plaintext\] Namespace -\> Type Namespace \[label="Namespace (KerML)" shape=plaintext\] Element -\> Namespace Element \[label="Element (KerML)" shape=plaintext\] }](_images/graphviz-1018cf128ae20e98a25f42840af92eb5fbe7dade.png)

</div>

</div>

The following table shows all attributes defined for `Definition` according to the specification together with the documentation from the machine readable specification. Note that in Syside API, we use snake case for attribute names instead of Pascal case used in the specification.

<div class="pst-scrollable-table-container">

Attribute

</div>

</div>

Documentation from machine readable specification

Attributes defined in [`Definition`](#syside.Definition "syside.Definition"):

[`directed_usages`](#syside.Definition.directed_usages "syside.Definition.directed_usages")

The `usages` of this `Definition` that are `directedFeatures`.

[`is_variation`](#syside.Definition.is_variation "syside.Definition.is_variation")

Whether this `Definition` is for a variation point or not. If true, then all the `memberships` of the `Definition` must be `VariantMemberships`.

[`owned_actions`](#syside.Definition.owned_actions "syside.Definition.owned_actions")

The `ActionUsages` that are `ownedUsages` of this `Definition`.

[`owned_allocations`](#syside.Definition.owned_allocations "syside.Definition.owned_allocations")

The `AllocationUsages` that are `ownedUsages` of this `Definition`.

[`owned_attributes`](#syside.Definition.owned_attributes "syside.Definition.owned_attributes")

The `AttributeUsages` that are `ownedUsages` of this `Definition`.

[`owned_calculations`](#syside.Definition.owned_calculations "syside.Definition.owned_calculations")

The `CalculationUsages` that are `ownedUsages` of this `Definition`.

[`owned_cases`](#syside.Definition.owned_cases "syside.Definition.owned_cases")

The code\>CaseUsages that are `ownedUsages` of this `Definition`.

[`owned_concerns`](#syside.Definition.owned_concerns "syside.Definition.owned_concerns")

The `ConcernUsages` that are `ownedUsages` of this `Definition`.

[`owned_connections`](#syside.Definition.owned_connections "syside.Definition.owned_connections")

The `ConnectorAsUsages` that are `ownedUsages` of this `Definition`. Note that this list includes `BindingConnectorAsUsages`, `SuccessionAsUsages`, and `FlowUsages` because these are `ConnectorAsUsages` even though they are not `ConnectionUsages`.

[`owned_constraints`](#syside.Definition.owned_constraints "syside.Definition.owned_constraints")

The `ConstraintUsages` that are `ownedUsages` of this `Definition`.

[`owned_enumerations`](#syside.Definition.owned_enumerations "syside.Definition.owned_enumerations")

The `EnumerationUsages` that are `ownedUsages` of this `Definition`.

[`owned_flows`](#syside.Definition.owned_flows "syside.Definition.owned_flows")

The `FlowUsages` that are `ownedUsages` of this `Definition`.

[`owned_interfaces`](#syside.Definition.owned_interfaces "syside.Definition.owned_interfaces")

The `InterfaceUsages` that are `ownedUsages` of this `Definition`.

[`owned_items`](#syside.Definition.owned_items "syside.Definition.owned_items")

The `ItemUsages` that are `ownedUsages` of this `Definition`.

[`owned_metadata`](#syside.Definition.owned_metadata "syside.Definition.owned_metadata")

The `MetadataUsages` that are `ownedUsages` of this `Definition`.

[`owned_occurrences`](#syside.Definition.owned_occurrences "syside.Definition.owned_occurrences")

The `OccurrenceUsages` that are `ownedUsages` of this `Definition`.

[`owned_parts`](#syside.Definition.owned_parts "syside.Definition.owned_parts")

The `PartUsages` that are `ownedUsages` of this `Definition`.

[`owned_ports`](#syside.Definition.owned_ports "syside.Definition.owned_ports")

The `PortUsages` that are `ownedUsages` of this `Definition`.

[`owned_references`](#syside.Definition.owned_references "syside.Definition.owned_references")

The `ReferenceUsages` that are `ownedUsages` of this `Definition`.

[`owned_renderings`](#syside.Definition.owned_renderings "syside.Definition.owned_renderings")

The `RenderingUsages` that are `ownedUsages` of this `Definition`.

[`owned_states`](#syside.Definition.owned_states "syside.Definition.owned_states")

The `StateUsages` that are `ownedUsages` of this `Definition`.

[`owned_transitions`](#syside.Definition.owned_transitions "syside.Definition.owned_transitions")

The `TransitionUsages` that are `ownedUsages` of this `Definition`.

[`owned_usages`](#syside.Definition.owned_usages "syside.Definition.owned_usages")

The `Usages` that are `ownedFeatures` of this `Definition`.

[`owned_use_cases`](#syside.Definition.owned_use_cases "syside.Definition.owned_use_cases")

The `UseCaseUsages` that are `ownedUsages` of this `Definition`.

[`owned_verification_cases`](#syside.Definition.owned_verification_cases "syside.Definition.owned_verification_cases")

The `VerificationCaseUsages` that are `ownedUsages` of this `Definition`.

[`owned_views`](#syside.Definition.owned_views "syside.Definition.owned_views")

The `ViewUsages` that are `ownedUsages` of this `Definition`.

[`owned_viewpoints`](#syside.Definition.owned_viewpoints "syside.Definition.owned_viewpoints")

The `ViewpointUsages` that are `ownedUsages` of this `Definition`.

[`usages`](#syside.Definition.usages "syside.Definition.usages")

The `Usages` that are `features` of this `Definition` (not necessarily owned).

[`variants`](#syside.Definition.variants "syside.Definition.variants")

The `Usages` which represent the variants of this `Definition` as a variation point `Definition`, if `isVariation` = true. If `isVariation = false`, the there must be no `variants`.

[`variant_memberships`](#syside.Definition.variant_memberships "syside.Definition.variant_memberships")

The `ownedMemberships` of this `Definition` that are `VariantMemberships`. If `isVariation` = true, then this must be all `ownedMemberships` of the `Definition`. If `isVariation` = false, then `variantMembership`must be empty.

Attributes defined in [`Classifier`](/v0.8.1/api/metamodel/KerML/Classifier.md "syside.Classifier"):

[`owned_subclassifications`](/v0.8.1/api/metamodel/KerML/Classifier.md "syside.Classifier.owned_subclassifications")

The `ownedSpecializations` of this `Classifier` that are `Subclassifications`, for which this `Classifier` is the `subclassifier`.

Attributes defined in [`Type`](/v0.8.1/api/metamodel/KerML/Type.md "syside.Type"):

[`differencing_types`](/v0.8.1/api/metamodel/KerML/Type.md "syside.Type.differencing_types")

The interpretations of a `Type` with `differencingTypes` are asserted to be those of the first of those `Types`, but not including those of the remaining `Types`. For example, a `Classifier` might be the difference of a `Classifier` for people and another for people of a particular nationality, leaving people who are not of that nationality. Similarly, a feature of people might be the difference between a feature for their children and a `Classifier` for people of a particular sex, identifying their children not of that sex (because the interpretations of the children `Feature` that identify those of that sex are also interpretations of the `Classifier` for that sex).

[`directed_features`](/v0.8.1/api/metamodel/KerML/Type.md "syside.Type.directed_features")

The `features` of this `Type` that have a non-null `direction`.

[`end_features`](/v0.8.1/api/metamodel/KerML/Type.md "syside.Type.end_features")

All `features` of this `Type` with `isEnd = true`.

[`features`](/v0.8.1/api/metamodel/KerML/Type.md "syside.Type.features")

The `ownedMemberFeatures` of the `featureMemberships` of this `Type`.

[`feature_memberships`](/v0.8.1/api/metamodel/KerML/Type.md "syside.Type.feature_memberships")

The `FeatureMemberships` for `features` of this `Type`, which include all `ownedFeatureMemberships` and those `inheritedMemberships` that are `FeatureMemberships` (but does *not* include any `importedMemberships`).

[`inherited_features`](/v0.8.1/api/metamodel/KerML/Type.md "syside.Type.inherited_features")

All the `memberFeatures` of the `inheritedMemberships` of this `Type` that are `FeatureMemberships`.

[`inherited_memberships`](/v0.8.1/api/metamodel/KerML/Type.md "syside.Type.inherited_memberships")

All `Memberships` inherited by this `Type` via `Specialization` or `Conjugation`. These are included in the derived union for the `memberships` of the `Type`.

[`inputs`](/v0.8.1/api/metamodel/KerML/Type.md "syside.Type.inputs")

All `features` related to this `Type` by `FeatureMemberships` that have `direction` `in` or `inout`.

[`intersecting_types`](/v0.8.1/api/metamodel/KerML/Type.md "syside.Type.intersecting_types")

The interpretations of a `Type` with `intersectingTypes` are asserted to be those in common among the `intersectingTypes`, which are the `Types` derived from the `intersectingType` of the `ownedIntersectings` of this `Type`. For example, a `Classifier` might be an intersection of `Classifiers` for people of a particular sex and of a particular nationality. Similarly, a feature for people’s children of a particular sex might be the intersection of a `Feature` for their children and a `Classifier` for people of that sex (because the interpretations of the children `Feature` that identify those of that sex are also interpretations of the Classifier for that sex).

[`is_abstract`](/v0.8.1/api/metamodel/KerML/Type.md "syside.Type.is_abstract")

Indicates whether instances of this `Type` must also be instances of at least one of its specialized `Types`.

[`is_conjugated`](/v0.8.1/api/metamodel/KerML/Type.md "syside.Type.is_conjugated")

Indicates whether this `Type` has an `ownedConjugator`.

[`is_sufficient`](/v0.8.1/api/metamodel/KerML/Type.md "syside.Type.is_sufficient")

Whether all things that meet the classification conditions of this `Type` must be classified by the `Type`.

(A `Type` gives conditions that must be met by whatever it classifies, but when `isSufficient` is false, things may meet those conditions but still not be classified by the `Type`. For example, a Type `Car` that is not sufficient could require everything it classifies to have four wheels, but not all four wheeled things would classify as cars. However, if the `Type` `Car` were sufficient, it would classify all four-wheeled things.)

[`multiplicity`](/v0.8.1/api/metamodel/KerML/Type.md "syside.Type.multiplicity")

An `ownedMember` of this `Type` that is a `Multiplicity`, which constraints the cardinality of the `Type`. If there is no such `ownedMember`, then the cardinality of this `Type` is constrained by all the `Multiplicity` constraints applicable to any direct supertypes.

[`outputs`](/v0.8.1/api/metamodel/KerML/Type.md "syside.Type.outputs")

All `features` related to this `Type` by `FeatureMemberships` that have `direction` `out` or `inout`.

[`owned_conjugator`](/v0.8.1/api/metamodel/KerML/Type.md "syside.Type.owned_conjugator")

A `Conjugation` owned by this `Type` for which the `Type` is the `originalType`.

[`owned_differencings`](/v0.8.1/api/metamodel/KerML/Type.md "syside.Type.owned_differencings")

The `ownedRelationships` of this `Type` that are `Differencings`, having this `Type` as their `typeDifferenced`.

[`owned_disjoinings`](/v0.8.1/api/metamodel/KerML/Type.md "syside.Type.owned_disjoinings")

The `ownedRelationships` of this `Type` that are `Disjoinings`, for which the `Type` is the `typeDisjoined` `Type`.

[`owned_end_features`](/v0.8.1/api/metamodel/KerML/Type.md "syside.Type.owned_end_features")

All `endFeatures` of this `Type` that are `ownedFeatures`.

[`owned_features`](/v0.8.1/api/metamodel/KerML/Type.md "syside.Type.owned_features")

The `ownedMemberFeatures` of the `ownedFeatureMemberships` of this `Type`.

[`owned_feature_memberships`](/v0.8.1/api/metamodel/KerML/Type.md "syside.Type.owned_feature_memberships")

The `ownedMemberships` of this `Type` that are `FeatureMemberships`, for which the `Type` is the `owningType`. Each such `FeatureMembership` identifies an `ownedFeature` of the `Type`.

[`owned_intersectings`](/v0.8.1/api/metamodel/KerML/Type.md "syside.Type.owned_intersectings")

The `ownedRelationships` of this `Type` that are `Intersectings`, have the `Type` as their `typeIntersected`.

[`owned_specializations`](/v0.8.1/api/metamodel/KerML/Type.md "syside.Type.owned_specializations")

The `ownedRelationships` of this `Type` that are `Specializations`, for which the `Type` is the `specific` `Type`.

[`owned_unionings`](/v0.8.1/api/metamodel/KerML/Type.md "syside.Type.owned_unionings")

The `ownedRelationships` of this `Type` that are `Unionings`, having the `Type` as their `typeUnioned`.

[`unioning_types`](/v0.8.1/api/metamodel/KerML/Type.md "syside.Type.unioning_types")

The interpretations of a `Type` with `unioningTypes` are asserted to be the same as those of all the `unioningTypes` together, which are the `Types` derived from the `unioningType` of the `ownedUnionings` of this `Type`. For example, a `Classifier` for people might be the union of `Classifiers` for all the sexes. Similarly, a feature for people’s children might be the union of features dividing them in the same ways as people in general.

Attributes defined in [`Namespace`](/v0.8.1/api/metamodel/KerML/Namespace.md "syside.Namespace"):

[`members`](/v0.8.1/api/metamodel/KerML/Namespace.md "syside.Namespace.members")

The set of all member `Elements` of this `Namespace`, which are the `memberElements` of all `memberships` of the `Namespace`.

[`memberships`](/v0.8.1/api/metamodel/KerML/Namespace.md "syside.Namespace.memberships")

All `Memberships` in this `Namespace`, including (at least) the union of `ownedMemberships` and `importedMemberships`.

[`owned_imports`](/v0.8.1/api/metamodel/KerML/Namespace.md "syside.Namespace.owned_imports")

The `ownedRelationships` of this `Namespace` that are `Imports`, for which the `Namespace` is the `importOwningNamespace`.

[`owned_members`](/v0.8.1/api/metamodel/KerML/Namespace.md "syside.Namespace.owned_members")

The owned `members` of this `Namespace`, which are the `ownedMemberElements` of the `ownedMemberships` of the `Namespace`.

[`owned_memberships`](/v0.8.1/api/metamodel/KerML/Namespace.md "syside.Namespace.owned_memberships")

The `ownedRelationships` of this `Namespace` that are `Memberships`, for which the `Namespace` is the `membershipOwningNamespace`.

Attributes defined in [`Element`](/v0.8.1/api/metamodel/KerML/Element.md "syside.Element"):

[`declared_name`](/v0.8.1/api/metamodel/KerML/Element.md "syside.Element.declared_name")

The declared name of this `Element`.

[`declared_short_name`](/v0.8.1/api/metamodel/KerML/Element.md "syside.Element.declared_short_name")

An optional alternative name for the `Element` that is intended to be shorter or in some way more succinct than its primary `name`. It may act as a modeler-specified identifier for the `Element`, though it is then the responsibility of the modeler to maintain the uniqueness of this identifier within a model or relative to some other context.

[`documentation`](/v0.8.1/api/metamodel/KerML/Element.md "syside.Element.documentation")

The Documentation owned by this Element.

[`element_id`](/v0.8.1/api/metamodel/KerML/Element.md "syside.Element.element_id")

The globally unique identifier for this Element. This is intended to be set by tooling, and it must not change during the lifetime of the Element.

[`is_implied_included`](/v0.8.1/api/metamodel/KerML/Element.md "syside.Element.is_implied_included")

Whether all necessary implied Relationships have been included in the `ownedRelationships` of this Element. This property may be true, even if there are not actually any `ownedRelationships` with `isImplied = true`, meaning that no such Relationships are actually implied for this Element. However, if it is false, then `ownedRelationships` may *not* contain any implied Relationships. That is, either *all* required implied Relationships must be included, or none of them.

[`is_library_element`](/v0.8.1/api/metamodel/KerML/Element.md "syside.Element.is_library_element")

Whether this Element is contained in the ownership tree of a library model.

[`name`](/v0.8.1/api/metamodel/KerML/Element.md "syside.Element.name")

The name to be used for this `Element` during name resolution within its `owningNamespace`. This is derived using the `effectiveName()` operation. By default, it is the same as the `declaredName`, but this is overridden for certain kinds of `Elements` to compute a `name` even when the `declaredName` is null.

[`owned_annotations`](/v0.8.1/api/metamodel/KerML/Element.md "syside.Element.owned_annotations")

The `ownedRelationships` of this `Element` that are `Annotations`, for which this `Element` is the `annotatedElement`.

[`owned_elements`](/v0.8.1/api/metamodel/KerML/Element.md "syside.Element.owned_elements")

The Elements owned by this Element, derived as the ownedRelatedElements of the ownedRelationships of this Element.

[`owned_relationships`](/v0.8.1/api/metamodel/KerML/Element.md "syside.Element.owned_relationships")

The Relationships for which this Element is the owningRelatedElement.

[`owner`](/v0.8.1/api/metamodel/KerML/Element.md "syside.Element.owner")

The owner of this Element, derived as the `owningRelatedElement` of the `owningRelationship` of this Element, if any.

[`owning_membership`](/v0.8.1/api/metamodel/KerML/Element.md "syside.Element.owning_membership")

The `owningRelationship` of this `Element`, if that `Relationship` is a `Membership`.

[`owning_namespace`](/v0.8.1/api/metamodel/KerML/Element.md "syside.Element.owning_namespace")

The `Namespace` that owns this `Element`, which is the `membershipOwningNamespace` of the `owningMembership` of this `Element`, if any.

[`owning_relationship`](/v0.8.1/api/metamodel/KerML/Element.md "syside.Element.owning_relationship")

The Relationship for which this Element is an ownedRelatedElement, if any.

[`qualified_name`](/v0.8.1/api/metamodel/KerML/Element.md "syside.Element.qualified_name")

The full ownership-qualified name of this `Element`, represented in a form that is valid according to the KerML textual concrete syntax for qualified names (including use of unrestricted name notation and escaped characters, as necessary). The `qualifiedName` is null if this `Element` has no `owningNamespace` or if there is not a complete ownership chain of named `Namespaces` from a root `Namespace` to this `Element`. If the `owningNamespace` has other `Elements` with the same name as this one, then the `qualifiedName` is null for all such `Elements` other than the first.

[`short_name`](/v0.8.1/api/metamodel/KerML/Element.md "syside.Element.short_name")

The short name to be used for this `Element` during name resolution within its `owningNamespace`. This is derived using the `effectiveShortName()` operation. By default, it is the same as the `declaredShortName`, but this is overridden for certain kinds of `Elements` to compute a `shortName` even when the `declaredName` is null.

[`textual_representations`](/v0.8.1/api/metamodel/KerML/Element.md "syside.Element.textual_representations")

The `TextualRepresentations` that annotate this `Element`.

The following table lists Syside specific attributes available for class [`Definition`](#syside.Definition "syside.Definition"):

<div class="pst-scrollable-table-container">

|                                                                                                            |
| ---------------------------------------------------------------------------------------------------------- |
| Python Attribute                                                                                           |
| [`STD`](#syside.Definition.STD "syside.Definition.STD")                                                    |
| [`owned_analysis_cases`](#syside.Definition.owned_analysis_cases "syside.Definition.owned_analysis_cases") |
| [`owned_requirements`](#syside.Definition.owned_requirements "syside.Definition.owned_requirements")       |
| [`try_set_is_variation`](#syside.Definition.try_set_is_variation "syside.Definition.try_set_is_variation") |

</div>

  - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">Definition</span></span>[](#syside.Definition "Link to this definition")
    
      - <span class="sig-name descname"><span class="pre">\_\_cpp\_name\_\_</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">'syside::sysml::Definition'</span>*[](#syside.Definition.__cpp_name__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">STD</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><span class="pre">type</span><span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Definition</span>](#syside.Definition "syside.Definition")<span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="p"><span class="pre">...</span></span><span class="p"><span class="pre">\]</span></span><span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">()</span>*[](#syside.Definition.STD "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">is\_variation</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*[](#syside.Definition.is_variation "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">try\_set\_is\_variation</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">bool</span></span></span>[](#syside.Definition.try_set_is_variation "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">variants</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Usage</span>](/v0.8.1/api/metamodel/SysML/Usage.md "syside.Usage")<span class="p"><span class="pre">\]</span></span>*[](#syside.Definition.variants "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">variant\_memberships</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.VariantMembership</span>](/v0.8.1/api/metamodel/SysML/VariantMembership.md "syside.VariantMembership")<span class="p"><span class="pre">\]</span></span>*[](#syside.Definition.variant_memberships "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">usages</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Usage</span>](/v0.8.1/api/metamodel/SysML/Usage.md "syside.Usage")<span class="p"><span class="pre">\]</span></span>*[](#syside.Definition.usages "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">directed\_usages</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Usage</span>](/v0.8.1/api/metamodel/SysML/Usage.md "syside.Usage")<span class="p"><span class="pre">\]</span></span>*[](#syside.Definition.directed_usages "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned\_usages</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Usage</span>](/v0.8.1/api/metamodel/SysML/Usage.md "syside.Usage")<span class="p"><span class="pre">\]</span></span>*[](#syside.Definition.owned_usages "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned\_references</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.ReferenceUsage</span>](/v0.8.1/api/metamodel/SysML/ReferenceUsage.md "syside.ReferenceUsage")<span class="p"><span class="pre">\]</span></span>*[](#syside.Definition.owned_references "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned\_attributes</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.AttributeUsage</span>](/v0.8.1/api/metamodel/SysML/AttributeUsage.md "syside.AttributeUsage")<span class="p"><span class="pre">\]</span></span>*[](#syside.Definition.owned_attributes "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned\_enumerations</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.EnumerationUsage</span>](/v0.8.1/api/metamodel/SysML/EnumerationUsage.md "syside.EnumerationUsage")<span class="p"><span class="pre">\]</span></span>*[](#syside.Definition.owned_enumerations "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned\_occurrences</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.OccurrenceUsage</span>](/v0.8.1/api/metamodel/SysML/OccurrenceUsage.md "syside.OccurrenceUsage")<span class="p"><span class="pre">\]</span></span>*[](#syside.Definition.owned_occurrences "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned\_items</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.ItemUsage</span>](/v0.8.1/api/metamodel/SysML/ItemUsage.md "syside.ItemUsage")<span class="p"><span class="pre">\]</span></span>*[](#syside.Definition.owned_items "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned\_parts</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.PartUsage</span>](/v0.8.1/api/metamodel/SysML/PartUsage.md "syside.PartUsage")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span>[<span class="pre">syside.ConnectionUsage</span>](/v0.8.1/api/metamodel/SysML/ConnectionUsage.md "syside.ConnectionUsage")<span class="p"><span class="pre">\]</span></span>*[](#syside.Definition.owned_parts "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned\_ports</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.PortUsage</span>](/v0.8.1/api/metamodel/SysML/PortUsage.md "syside.PortUsage")<span class="p"><span class="pre">\]</span></span>*[](#syside.Definition.owned_ports "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned\_connections</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.ConnectorAsUsage</span>](/v0.8.1/api/metamodel/SysML/ConnectorAsUsage.md "syside.ConnectorAsUsage")<span class="p"><span class="pre">\]</span></span>*[](#syside.Definition.owned_connections "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned\_flows</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.FlowUsage</span>](/v0.8.1/api/metamodel/SysML/FlowUsage.md "syside.FlowUsage")<span class="p"><span class="pre">\]</span></span>*[](#syside.Definition.owned_flows "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned\_interfaces</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.InterfaceUsage</span>](/v0.8.1/api/metamodel/SysML/InterfaceUsage.md "syside.InterfaceUsage")<span class="p"><span class="pre">\]</span></span>*[](#syside.Definition.owned_interfaces "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned\_allocations</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.AllocationUsage</span>](/v0.8.1/api/metamodel/SysML/AllocationUsage.md "syside.AllocationUsage")<span class="p"><span class="pre">\]</span></span>*[](#syside.Definition.owned_allocations "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned\_actions</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.ActionUsage</span>](/v0.8.1/api/metamodel/SysML/ActionUsage.md "syside.ActionUsage")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span>[<span class="pre">syside.FlowUsage</span>](/v0.8.1/api/metamodel/SysML/FlowUsage.md "syside.FlowUsage")<span class="p"><span class="pre">\]</span></span>*[](#syside.Definition.owned_actions "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned\_states</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.StateUsage</span>](/v0.8.1/api/metamodel/SysML/StateUsage.md "syside.StateUsage")<span class="p"><span class="pre">\]</span></span>*[](#syside.Definition.owned_states "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned\_transitions</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.TransitionUsage</span>](/v0.8.1/api/metamodel/SysML/TransitionUsage.md "syside.TransitionUsage")<span class="p"><span class="pre">\]</span></span>*[](#syside.Definition.owned_transitions "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned\_calculations</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.CalculationUsage</span>](/v0.8.1/api/metamodel/SysML/CalculationUsage.md "syside.CalculationUsage")<span class="p"><span class="pre">\]</span></span>*[](#syside.Definition.owned_calculations "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned\_constraints</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.ConstraintUsage</span>](/v0.8.1/api/metamodel/SysML/ConstraintUsage.md "syside.ConstraintUsage")<span class="p"><span class="pre">\]</span></span>*[](#syside.Definition.owned_constraints "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned\_concerns</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.ConcernUsage</span>](/v0.8.1/api/metamodel/SysML/ConcernUsage.md "syside.ConcernUsage")<span class="p"><span class="pre">\]</span></span>*[](#syside.Definition.owned_concerns "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned\_cases</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.CaseUsage</span>](/v0.8.1/api/metamodel/SysML/CaseUsage.md "syside.CaseUsage")<span class="p"><span class="pre">\]</span></span>*[](#syside.Definition.owned_cases "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned\_verification\_cases</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.VerificationCaseUsage</span>](/v0.8.1/api/metamodel/SysML/VerificationCaseUsage.md "syside.VerificationCaseUsage")<span class="p"><span class="pre">\]</span></span>*[](#syside.Definition.owned_verification_cases "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned\_use\_cases</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.UseCaseUsage</span>](/v0.8.1/api/metamodel/SysML/UseCaseUsage.md "syside.UseCaseUsage")<span class="p"><span class="pre">\]</span></span>*[](#syside.Definition.owned_use_cases "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned\_views</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.ViewUsage</span>](/v0.8.1/api/metamodel/SysML/ViewUsage.md "syside.ViewUsage")<span class="p"><span class="pre">\]</span></span>*[](#syside.Definition.owned_views "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned\_viewpoints</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.ViewpointUsage</span>](/v0.8.1/api/metamodel/SysML/ViewpointUsage.md "syside.ViewpointUsage")<span class="p"><span class="pre">\]</span></span>*[](#syside.Definition.owned_viewpoints "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned\_renderings</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.RenderingUsage</span>](/v0.8.1/api/metamodel/SysML/RenderingUsage.md "syside.RenderingUsage")<span class="p"><span class="pre">\]</span></span>*[](#syside.Definition.owned_renderings "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned\_metadata</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.MetadataUsage</span>](/v0.8.1/api/metamodel/SysML/MetadataUsage.md "syside.MetadataUsage")<span class="p"><span class="pre">\]</span></span>*[](#syside.Definition.owned_metadata "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned\_analysis\_cases</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.AnalysisCaseUsage</span>](/v0.8.1/api/metamodel/SysML/AnalysisCaseUsage.md "syside.AnalysisCaseUsage")<span class="p"><span class="pre">\]</span></span>*[](#syside.Definition.owned_analysis_cases "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned\_requirements</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.RequirementUsage</span>](/v0.8.1/api/metamodel/SysML/RequirementUsage.md "syside.RequirementUsage")<span class="p"><span class="pre">\]</span></span>*[](#syside.Definition.owned_requirements "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned\_subclassifications</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Subclassification</span>](/v0.8.1/api/metamodel/KerML/Subclassification.md "syside.Subclassification")<span class="p"><span class="pre">\]</span></span>*[](#syside.Definition.owned_subclassifications "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned\_subclassification\_types</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Classifier</span>](/v0.8.1/api/metamodel/KerML/Classifier.md "syside.Classifier")<span class="p"><span class="pre">\]</span></span>*[](#syside.Definition.owned_subclassification_types "Link to this definition")
