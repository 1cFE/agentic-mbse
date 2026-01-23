<div id="actionusage" class="section">

<span id="metamodel-sysml-actionusage"></span>

# ActionUsage[](#actionusage "Link to this heading")

`ActionUsage` is defined in SysML specification on [page 346](https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=346). Excerpt from the machine readable specification:

> 
> 
> <div>
> 
> An `ActionUsage` is a `Usage` that is also a `Step`, and, so, is typed by a `Behavior`. Nominally, if the type is an `ActionDefinition`, an `ActionUsage` is a `Usage` of that `ActionDefinition` within a system. However, other kinds of kernel `Behaviors` are also allowed, to permit use of `Behaviors` from the Kernel Model Libraries.
> 
> </div>

The following diagram shows the inheritance hierarchy of `ActionUsage` according to the specification:

<div class="align-center" data-align="center">

<div class="graphviz">

![// Class: ActionUsage digraph { ActionUsage \[label="ActionUsage (SysML)" shape=plaintext\] OccurrenceUsage -\> ActionUsage Step -\> ActionUsage OccurrenceUsage \[label="OccurrenceUsage (SysML)" shape=plaintext\] Usage -\> OccurrenceUsage Step \[label="Step (KerML)" shape=plaintext\] Feature -\> Step Usage \[label="Usage (SysML)" shape=plaintext\] Feature -\> Usage Feature \[label="Feature (KerML)" shape=plaintext\] Type -\> Feature Type \[label="Type (KerML)" shape=plaintext\] Namespace -\> Type Namespace \[label="Namespace (KerML)" shape=plaintext\] Element -\> Namespace Element \[label="Element (KerML)" shape=plaintext\] }](_images/graphviz-b3f0584a68d40ea0dece7d8e76c641cb6ef8fe70.png)

</div>

</div>

The following table shows all attributes defined for `ActionUsage` according to the specification together with the documentation from the machine readable specification. Note that in Syside API, we use snake case for attribute names instead of Pascal case used in the specification.

<div class="pst-scrollable-table-container">

Attribute

</div>

</div>

Documentation from machine readable specification

Attributes defined in [`ActionUsage`](#syside.ActionUsage "syside.ActionUsage"):

[`action_definitions`](#syside.ActionUsage.action_definitions "syside.ActionUsage.action_definitions")

The `Behaviors` that are the `types` of this `ActionUsage`. Nominally, these would be `ActionDefinitions`, but other kinds of Kernel `Behaviors` are also allowed, to permit use of `Behaviors` from the Kernel Model Libraries.

Attributes defined in [`OccurrenceUsage`](/v0.8.1/api/metamodel/SysML/OccurrenceUsage.md "syside.OccurrenceUsage"):

[`individual_definition`](/v0.8.1/api/metamodel/SysML/OccurrenceUsage.md "syside.OccurrenceUsage.individual_definition")

The at most one `occurrenceDefinition` that has `isIndividual = true`.

[`is_individual`](/v0.8.1/api/metamodel/SysML/OccurrenceUsage.md "syside.OccurrenceUsage.is_individual")

Whether this `OccurrenceUsage` represents the usage of the specific individual represented by its `individualDefinition`.

[`occurrence_definitions`](/v0.8.1/api/metamodel/SysML/OccurrenceUsage.md "syside.OccurrenceUsage.occurrence_definitions")

The `Classes` that are the types of this `OccurrenceUsage`. Nominally, these are `OccurrenceDefinitions`, but other kinds of kernel `Classes` are also allowed, to permit use of `Classes` from the Kernel Model Libraries.

[`portion_kind`](/v0.8.1/api/metamodel/SysML/OccurrenceUsage.md "syside.OccurrenceUsage.portion_kind")

The kind of temporal portion (time slice or snapshot) is represented by this `OccurrenceUsage`. If `portionKind` is not null, then the `owningType` of the `OccurrenceUsage` must be non-null, and the `OccurrenceUsage` represents portions of the featuring instance of the `owningType`.

Attributes defined in [`Step`](/v0.8.1/api/metamodel/KerML/Step.md "syside.Step"):

[`behaviors`](/v0.8.1/api/metamodel/KerML/Step.md "syside.Step.behaviors")

The `Behaviors` that type this `Step`.

[`parameters`](/v0.8.1/api/metamodel/KerML/Step.md "syside.Step.parameters")

The `parameters` of this `Step`, which are defined as its `directedFeatures`, whose values are passed into and/or out of a performance of the `Step`.

Attributes defined in [`Usage`](/v0.8.1/api/metamodel/SysML/Usage.md "syside.Usage"):

[`definitions`](/v0.8.1/api/metamodel/SysML/Usage.md "syside.Usage.definitions")

The `Classifiers` that are the types of this `Usage`. Nominally, these are `Definitions`, but other kinds of Kernel `Classifiers` are also allowed, to permit use of `Classifiers` from the Kernel Model Libraries.

[`directed_usages`](/v0.8.1/api/metamodel/SysML/Usage.md "syside.Usage.directed_usages")

The `usages` of this `Usage` that are `directedFeatures`.

[`is_reference`](/v0.8.1/api/metamodel/SysML/Usage.md "syside.Usage.is_reference")

Whether this `Usage` is a referential `Usage`, that is, it has `isComposite = false`.

[`is_variation`](/v0.8.1/api/metamodel/SysML/Usage.md "syside.Usage.is_variation")

Whether this `Usage` is for a variation point or not. If true, then all the `memberships` of the `Usage` must be `VariantMemberships`.

[`may_time_vary`](/v0.8.1/api/metamodel/SysML/Usage.md "syside.Usage.may_time_vary")

Whether this `Usage` may be time varying (that is, whether it is featured by the snapshots of its `owningType`, rather than being featured by the `owningType` itself). However, if `isConstant` is also true, then the value of the `Usage` is nevertheless constant over the entire duration of an instance of its `owningType` (that is, it has the same value on all snapshots).

The property `mayTimeVary` redefines the KerML property `Feature::isVariable`, making it derived. The property `isConstant` is inherited from `Feature`.

[`nested_actions`](/v0.8.1/api/metamodel/SysML/Usage.md "syside.Usage.nested_actions")

The `ActionUsages` that are `nestedUsages` of this `Usage`.

[`nested_allocations`](/v0.8.1/api/metamodel/SysML/Usage.md "syside.Usage.nested_allocations")

The `AllocationUsages` that are `nestedUsages` of this `Usage`.

[`nested_analysis_cases`](/v0.8.1/api/metamodel/SysML/Usage.md "syside.Usage.nested_analysis_cases")

The `AnalysisCaseUsages` that are `nestedUsages` of this `Usage`.

[`nested_attributes`](/v0.8.1/api/metamodel/SysML/Usage.md "syside.Usage.nested_attributes")

The code\>AttributeUsages that are `nestedUsages` of this `Usage`.

[`nested_calculations`](/v0.8.1/api/metamodel/SysML/Usage.md "syside.Usage.nested_calculations")

The `CalculationUsage` that are `nestedUsages` of this `Usage`.

[`nested_cases`](/v0.8.1/api/metamodel/SysML/Usage.md "syside.Usage.nested_cases")

The `CaseUsages` that are `nestedUsages` of this `Usage`.

[`nested_concerns`](/v0.8.1/api/metamodel/SysML/Usage.md "syside.Usage.nested_concerns")

The `ConcernUsages` that are `nestedUsages` of this `Usage`.

[`nested_connections`](/v0.8.1/api/metamodel/SysML/Usage.md "syside.Usage.nested_connections")

The `ConnectorAsUsages` that are `nestedUsages` of this `Usage`. Note that this list includes `BindingConnectorAsUsages`, `SuccessionAsUsages`, and `FlowUsages` because these are `ConnectorAsUsages` even though they are not `ConnectionUsages`.

[`nested_constraints`](/v0.8.1/api/metamodel/SysML/Usage.md "syside.Usage.nested_constraints")

The `ConstraintUsages` that are `nestedUsages` of this `Usage`.

[`nested_enumerations`](/v0.8.1/api/metamodel/SysML/Usage.md "syside.Usage.nested_enumerations")

The code\>EnumerationUsages that are `nestedUsages` of this `Usage`.

[`nested_flows`](/v0.8.1/api/metamodel/SysML/Usage.md "syside.Usage.nested_flows")

The code\>FlowUsages that are `nestedUsages` of this `Usage`.

[`nested_interfaces`](/v0.8.1/api/metamodel/SysML/Usage.md "syside.Usage.nested_interfaces")

The `InterfaceUsages` that are `nestedUsages` of this `Usage`.

[`nested_items`](/v0.8.1/api/metamodel/SysML/Usage.md "syside.Usage.nested_items")

The `ItemUsages` that are `nestedUsages` of this `Usage`.

[`nested_metadata`](/v0.8.1/api/metamodel/SysML/Usage.md "syside.Usage.nested_metadata")

The `MetadataUsages` that are `nestedUsages` of this of this `Usage`.

[`nested_occurrences`](/v0.8.1/api/metamodel/SysML/Usage.md "syside.Usage.nested_occurrences")

The `OccurrenceUsages` that are `nestedUsages` of this `Usage`.

[`nested_parts`](/v0.8.1/api/metamodel/SysML/Usage.md "syside.Usage.nested_parts")

The `PartUsages` that are `nestedUsages` of this `Usage`.

[`nested_ports`](/v0.8.1/api/metamodel/SysML/Usage.md "syside.Usage.nested_ports")

The `PortUsages` that are `nestedUsages` of this `Usage`.

[`nested_references`](/v0.8.1/api/metamodel/SysML/Usage.md "syside.Usage.nested_references")

The `ReferenceUsages` that are `nestedUsages` of this `Usage`.

[`nested_renderings`](/v0.8.1/api/metamodel/SysML/Usage.md "syside.Usage.nested_renderings")

The `RenderingUsages` that are `nestedUsages` of this `Usage`.

[`nested_requirements`](/v0.8.1/api/metamodel/SysML/Usage.md "syside.Usage.nested_requirements")

The `RequirementUsages` that are `nestedUsages` of this `Usage`.

[`nested_states`](/v0.8.1/api/metamodel/SysML/Usage.md "syside.Usage.nested_states")

The `StateUsages` that are `nestedUsages` of this `Usage`.

[`nested_transitions`](/v0.8.1/api/metamodel/SysML/Usage.md "syside.Usage.nested_transitions")

The `TransitionUsages` that are `nestedUsages` of this `Usage`.

[`nested_usages`](/v0.8.1/api/metamodel/SysML/Usage.md "syside.Usage.nested_usages")

The `Usages` that are `ownedFeatures` of this `Usage`.

[`nested_use_cases`](/v0.8.1/api/metamodel/SysML/Usage.md "syside.Usage.nested_use_cases")

The `UseCaseUsages` that are `nestedUsages` of this `Usage`.

[`nested_verification_cases`](/v0.8.1/api/metamodel/SysML/Usage.md "syside.Usage.nested_verification_cases")

The `VerificationCaseUsages` that are `nestedUsages` of this `Usage`.

[`nested_views`](/v0.8.1/api/metamodel/SysML/Usage.md "syside.Usage.nested_views")

The `ViewUsages` that are `nestedUsages` of this `Usage`.

[`nested_viewpoints`](/v0.8.1/api/metamodel/SysML/Usage.md "syside.Usage.nested_viewpoints")

The `ViewpointUsages` that are `nestedUsages` of this `Usage`.

[`owning_definition`](/v0.8.1/api/metamodel/SysML/Usage.md "syside.Usage.owning_definition")

The `Definition` that owns this `Usage` (if any).

[`owning_usage`](/v0.8.1/api/metamodel/SysML/Usage.md "syside.Usage.owning_usage")

The `Usage` in which this `Usage` is nested (if any).

[`usages`](/v0.8.1/api/metamodel/SysML/Usage.md "syside.Usage.usages")

The `Usages` that are `features` of this `Usage` (not necessarily owned).

[`variants`](/v0.8.1/api/metamodel/SysML/Usage.md "syside.Usage.variants")

The `Usages` which represent the variants of this `Usage` as a variation point `Usage`, if `isVariation = true`. If `isVariation = false`, then there must be no `variants`.

[`variant_memberships`](/v0.8.1/api/metamodel/SysML/Usage.md "syside.Usage.variant_memberships")

The `ownedMemberships` of this `Usage` that are `VariantMemberships`. If `isVariation = true`, then this must be all `memberships` of the `Usage`. If `isVariation = false`, then `variantMembership`must be empty.

Attributes defined in [`Feature`](/v0.8.1/api/metamodel/KerML/Feature.md "syside.Feature"):

[`cross_feature`](/v0.8.1/api/metamodel/KerML/Feature.md "syside.Feature.cross_feature")

The second `chainingFeature` of the `crossedFeature` of the `ownedCrossSubsetting` of this `Feature`, if it has one. Semantically, the values of the `crossFeature` of an end `Feature` must include all values of the end `Feature` obtained when navigating from values of the other end `Features` of the same `owningType`.

[`direction`](/v0.8.1/api/metamodel/KerML/Feature.md "syside.Feature.direction")

Indicates how values of this `Feature` are determined or used (as specified for the `FeatureDirectionKind`).

[`end_owning_type`](/v0.8.1/api/metamodel/KerML/Feature.md "syside.Feature.end_owning_type")

The `Type` that is related to this `Feature` by an `EndFeatureMembership` in which the `Feature` is an `ownedMemberFeature`.

[`feature_target`](/v0.8.1/api/metamodel/KerML/Feature.md "syside.Feature.feature_target")

The last of the `chainingFeatures` of this `Feature`, if it has any. Otherwise, this `Feature` itself.

[`featuring_types`](/v0.8.1/api/metamodel/KerML/Feature.md "syside.Feature.featuring_types")

`Types` that feature this `Feature`, such that any instance in the domain of the `Feature` must be classified by all of these `Types`, including at least all the `featuringTypes` of its `typeFeaturings`. If the `Feature` is chained, then the `featuringTypes` of the first `Feature` in the chain are also `featuringTypes` of the chained `Feature`.

[`is_composite`](/v0.8.1/api/metamodel/KerML/Feature.md "syside.Feature.is_composite")

Whether the `Feature` is a composite `feature` of its `featuringType`. If so, the values of the `Feature` cannot exist after its featuring instance no longer does and cannot be values of another composite feature that is not on the same featuring instance.

[`is_constant`](/v0.8.1/api/metamodel/KerML/Feature.md "syside.Feature.is_constant")

If `isVariable` is true, then whether the value of this `Feature` nevertheless does not change over all `snapshots` of its `owningType`.

[`is_derived`](/v0.8.1/api/metamodel/KerML/Feature.md "syside.Feature.is_derived")

Whether the values of this `Feature` can always be computed from the values of other `Features`.

[`is_end`](/v0.8.1/api/metamodel/KerML/Feature.md "syside.Feature.is_end")

Whether or not this `Feature` is an end `Feature`. An end `Feature` always has multiplicity 1, mapping each of its domain instances to a single co-domain instance. However, it may have a `crossFeature`, in which case values of the `crossFeature` must be the same as those found by navigation across instances of the `owningType` from values of other end `Features` to values of this Feature. If the `owningType` has *n* end `Features`, then the multiplicity, ordering, and uniqueness declared for the `crossFeature` of any one of these end `Features` constrains the cardinality, ordering, and uniqueness of the collection of values of that `Feature` reached by navigation when the values of the other *n-1* end `Features` are held fixed.

[`is_nonunique`](/v0.8.1/api/metamodel/KerML/Feature.md "syside.Feature.is_nonunique")

[`is_ordered`](/v0.8.1/api/metamodel/KerML/Feature.md "syside.Feature.is_ordered")

Whether an order exists for the values of this `Feature` or not.

[`is_portion`](/v0.8.1/api/metamodel/KerML/Feature.md "syside.Feature.is_portion")

Whether the values of this `Feature` are contained in the space and time of instances of the domain of the `Feature` and represent the same thing as those instances.

[`is_unique`](/v0.8.1/api/metamodel/KerML/Feature.md "syside.Feature.is_unique")

Whether or not values for this `Feature` must have no duplicates or not.

[`is_variable`](/v0.8.1/api/metamodel/KerML/Feature.md "syside.Feature.is_variable")

Whether the value of this `Feature` might vary over time. That is, whether the `Feature` may have a different value for each `snapshot` of an `owningType` that is an `Occurrence`.

[`owned_cross_subsetting`](/v0.8.1/api/metamodel/KerML/Feature.md "syside.Feature.owned_cross_subsetting")

The one `ownedSubsetting` of this `Feature`, if any, that is a `CrossSubsetting}, for which the Feature is the crossingFeature.`

[`owned_feature_chainings`](/v0.8.1/api/metamodel/KerML/Feature.md "syside.Feature.owned_feature_chainings")

The `ownedRelationships` of this `Feature` that are `FeatureChainings`, for which the `Feature` will be the `featureChained`.

[`owned_feature_invertings`](/v0.8.1/api/metamodel/KerML/Feature.md "syside.Feature.owned_feature_invertings")

The `ownedRelationships` of this `Feature` that are `FeatureInvertings` and for which the `Feature` is the `featureInverted`.

[`owned_redefinitions`](/v0.8.1/api/metamodel/KerML/Feature.md "syside.Feature.owned_redefinitions")

The `ownedSubsettings` of this `Feature` that are `Redefinitions`, for which the `Feature` is the `redefiningFeature`.

[`owned_reference_subsetting`](/v0.8.1/api/metamodel/KerML/Feature.md "syside.Feature.owned_reference_subsetting")

The one `ownedSubsetting` of this `Feature`, if any, that is a `ReferenceSubsetting`, for which the `Feature` is the `referencingFeature`.

[`owned_subsettings`](/v0.8.1/api/metamodel/KerML/Feature.md "syside.Feature.owned_subsettings")

The `ownedSpecializations` of this `Feature` that are `Subsettings`, for which the `Feature` is the `subsettingFeature`.

[`owned_type_featurings`](/v0.8.1/api/metamodel/KerML/Feature.md "syside.Feature.owned_type_featurings")

The `ownedRelationships` of this `Feature` that are `TypeFeaturings` and for which the `Feature` is the `featureOfType`.

[`owned_typings`](/v0.8.1/api/metamodel/KerML/Feature.md "syside.Feature.owned_typings")

The `ownedSpecializations` of this `Feature` that are `FeatureTypings`, for which the `Feature` is the `typedFeature`.

[`owning_feature_membership`](/v0.8.1/api/metamodel/KerML/Feature.md "syside.Feature.owning_feature_membership")

The `FeatureMembership` that owns this `Feature` as an `ownedMemberFeature`, determining its `owningType`.

[`owning_type`](/v0.8.1/api/metamodel/KerML/Feature.md "syside.Feature.owning_type")

The `Type` that is the `owningType` of the `owningFeatureMembership` of this `Feature`.

[`types`](/v0.8.1/api/metamodel/KerML/Feature.md "syside.Feature.types")

`Types` that restrict the values of this `Feature`, such that the values must be instances of all the `types`. The types of a `Feature` are derived from its `typings` and the `types` of its `subsettings`. If the `Feature` is chained, then the `types` of the last `Feature` in the chain are also `types` of the chained `Feature`.

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

The following table lists Syside specific attributes available for class [`ActionUsage`](#syside.ActionUsage "syside.ActionUsage"):

<div class="pst-scrollable-table-container">

|                                                                                                  |
| ------------------------------------------------------------------------------------------------ |
| Python Attribute                                                                                 |
| [`STD`](#syside.ActionUsage.STD "syside.ActionUsage.STD")                                        |
| [`owned_parameters`](#syside.ActionUsage.owned_parameters "syside.ActionUsage.owned_parameters") |

</div>

  - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">ActionUsage</span></span>[](#syside.ActionUsage "Link to this definition")
    
      - <span class="sig-name descname"><span class="pre">\_\_cpp\_name\_\_</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">'syside::sysml::ActionUsage'</span>*[](#syside.ActionUsage.__cpp_name__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">STD</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><span class="pre">Union</span><span class="p"><span class="pre">\[</span></span><span class="pre">type</span><span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.ActionUsage</span>](#syside.ActionUsage "syside.ActionUsage")<span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">type</span><span class="p"><span class="pre">\[</span></span>[<span class="pre">FlowUsage</span>](/v0.8.1/api/metamodel/SysML/FlowUsage.md "syside.FlowUsage")<span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="p"><span class="pre">...</span></span><span class="p"><span class="pre">\]</span></span><span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">()</span>*[](#syside.ActionUsage.STD "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">behaviors</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Behavior</span>](/v0.8.1/api/metamodel/KerML/Behavior.md "syside.Behavior")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span>[<span class="pre">syside.ActionDefinition</span>](/v0.8.1/api/metamodel/SysML/ActionDefinition.md "syside.ActionDefinition")<span class="p"><span class="pre">\]</span></span>*[](#syside.ActionUsage.behaviors "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned\_parameters</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Feature</span>](/v0.8.1/api/metamodel/KerML/Feature.md "syside.Feature")<span class="p"><span class="pre">\]</span></span>*[](#syside.ActionUsage.owned_parameters "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">parameters</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Feature</span>](/v0.8.1/api/metamodel/KerML/Feature.md "syside.Feature")<span class="p"><span class="pre">\]</span></span>*[](#syside.ActionUsage.parameters "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">action\_definitions</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Behavior</span>](/v0.8.1/api/metamodel/KerML/Behavior.md "syside.Behavior")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span>[<span class="pre">syside.ActionDefinition</span>](/v0.8.1/api/metamodel/SysML/ActionDefinition.md "syside.ActionDefinition")<span class="p"><span class="pre">\]</span></span>*[](#syside.ActionUsage.action_definitions "Link to this definition")
