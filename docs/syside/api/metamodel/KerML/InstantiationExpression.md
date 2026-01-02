<div id="instantiationexpression" class="section">

<span id="metamodel-kerml-instantiationexpression"></span>

# InstantiationExpression[](#instantiationexpression "Link to this heading")

`InstantiationExpression` is defined in KerML specification on [page 238](https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=238). Excerpt from the machine readable specification:

> 
> 
> <div>
> 
> An `InstantiationExpression` is an `Expression` that instantiates its `instantiatedType`, binding some or all of the `features` of that `Type` to the `results` of its `arguments`.
> 
> `InstantiationExpression` is abstract, with concrete subclasses `InvocationExpression` and `ConstructorExpression`.
> 
> </div>

The following diagram shows the inheritance hierarchy of `InstantiationExpression` according to the specification:

<div class="align-center" data-align="center">

<div class="graphviz">

![// Class: InstantiationExpression digraph { InstantiationExpression \[label="InstantiationExpression (KerML)" shape=plaintext\] Expression -\> InstantiationExpression Expression \[label="Expression (KerML)" shape=plaintext\] Step -\> Expression Step \[label="Step (KerML)" shape=plaintext\] Feature -\> Step Feature \[label="Feature (KerML)" shape=plaintext\] Type -\> Feature Type \[label="Type (KerML)" shape=plaintext\] Namespace -\> Type Namespace \[label="Namespace (KerML)" shape=plaintext\] Element -\> Namespace Element \[label="Element (KerML)" shape=plaintext\] }](_images/graphviz-5ffb2700e4a6f2ccfd37557f00f06f1a747b5646.png)

</div>

</div>

The following table shows all attributes defined for `InstantiationExpression` according to the specification together with the documentation from the machine readable specification. Note that in Syside API, we use snake case for attribute names instead of Pascal case used in the specification.

<div class="pst-scrollable-table-container">

Attribute

</div>

</div>

Documentation from machine readable specification

Attributes defined in [`InstantiationExpression`](#syside.InstantiationExpression "syside.InstantiationExpression"):

[`arguments`](#syside.InstantiationExpression.arguments "syside.InstantiationExpression.arguments")

The `Expressions` whose `results` are bound to `features` of the `instantiatedType`. The `arguments` are ordered consistent with the order of the `features`, though they may not be one-to-one with all the `features`.

**Note.** The derivation of `argument` is given in the concrete subclasses of `InstantiationExpression`.

[`instantiated_type`](#syside.InstantiationExpression.instantiated_type "syside.InstantiationExpression.instantiated_type")

The `Type` that is being instantiated.

Attributes defined in [`Expression`](/v0.8.1/api/metamodel/KerML/Expression.md "syside.Expression"):

[`function`](/v0.8.1/api/metamodel/KerML/Expression.md "syside.Expression.function")

The `Function` that types this `Expression`.

This is the Function that types the Expression.

[`is_model_level_evaluable`](/v0.8.1/api/metamodel/KerML/Expression.md "syside.Expression.is_model_level_evaluable")

Whether this `Expression` meets the constraints necessary to be evaluated at *model level*, that is, using metadata within the model.

[`result`](/v0.8.1/api/metamodel/KerML/Expression.md "syside.Expression.result")

An `output` `parameter` of the `Expression` whose value is the result of the `Expression`. The result of an `Expression` is either inherited from its `function` or it is related to the `Expression` via a `ReturnParameterMembership`, in which case it redefines the `result` `parameter` of its `function`.

Attributes defined in [`Step`](/v0.8.1/api/metamodel/KerML/Step.md "syside.Step"):

[`behaviors`](/v0.8.1/api/metamodel/KerML/Step.md "syside.Step.behaviors")

The `Behaviors` that type this `Step`.

[`parameters`](/v0.8.1/api/metamodel/KerML/Step.md "syside.Step.parameters")

The `parameters` of this `Step`, which are defined as its `directedFeatures`, whose values are passed into and/or out of a performance of the `Step`.

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

The following table lists Syside specific attributes available for class [`InstantiationExpression`](#syside.InstantiationExpression "syside.InstantiationExpression"):

<div class="pst-scrollable-table-container">

|                                                                                                                                                              |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Python Attribute                                                                                                                                             |
| [`STD`](#syside.InstantiationExpression.STD "syside.InstantiationExpression.STD")                                                                            |
| [`instantiated_type_membership`](#syside.InstantiationExpression.instantiated_type_membership "syside.InstantiationExpression.instantiated_type_membership") |

</div>

  - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">InstantiationExpression</span></span>[](#syside.InstantiationExpression "Link to this definition")
    
      - <span class="sig-name descname"><span class="pre">\_\_cpp\_name\_\_</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">'syside::sysml::InstantiationExpression'</span>*[](#syside.InstantiationExpression.__cpp_name__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">STD</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><span class="pre">type</span><span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.InstantiationExpression</span>](#syside.InstantiationExpression "syside.InstantiationExpression")<span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="p"><span class="pre">...</span></span><span class="p"><span class="pre">\]</span></span><span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">()</span>*[](#syside.InstantiationExpression.STD "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">arguments</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.ArgumentsAccessor</span>](/v0.8.1/api/generated/syside.ArgumentsAccessor.md "syside.ArgumentsAccessor")*[](#syside.InstantiationExpression.arguments "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">instantiated\_type</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.Type</span>](/v0.8.1/api/metamodel/KerML/Type.md "syside.Type")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span>*[](#syside.InstantiationExpression.instantiated_type "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">instantiated\_type\_membership</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.Membership</span>](/v0.8.1/api/metamodel/KerML/Membership.md "syside.Membership")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span>*[](#syside.InstantiationExpression.instantiated_type_membership "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">cached\_result\_type</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">None</span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span>[<span class="pre">syside.Type</span>](/v0.8.1/api/metamodel/KerML/Type.md "syside.Type")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span>[<span class="pre">syside.TypeGuard</span>](/v0.8.1/api/generated/syside.TypeGuard.md "syside.TypeGuard")*[](#syside.InstantiationExpression.cached_result_type "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">is\_model\_level\_evaluable</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*[](#syside.InstantiationExpression.is_model_level_evaluable "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">function</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.Function</span>](/v0.8.1/api/metamodel/KerML/Function.md "syside.Function")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span>[<span class="pre">syside.CalculationDefinition</span>](/v0.8.1/api/metamodel/SysML/CalculationDefinition.md "syside.CalculationDefinition")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span>[<span class="pre">syside.ConstraintDefinition</span>](/v0.8.1/api/metamodel/SysML/ConstraintDefinition.md "syside.ConstraintDefinition")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span>*[](#syside.InstantiationExpression.function "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">result</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.Feature</span>](/v0.8.1/api/metamodel/KerML/Feature.md "syside.Feature")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span>*[](#syside.InstantiationExpression.result "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">result\_expression</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.Expression</span>](/v0.8.1/api/metamodel/KerML/Expression.md "syside.Expression")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span>*[](#syside.InstantiationExpression.result_expression "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">result\_expression\_member</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.ResultExpressionAccessor</span>](/v0.8.1/api/generated/syside.ResultExpressionAccessor.md "syside.ResultExpressionAccessor")*[](#syside.InstantiationExpression.result_expression_member "Link to this definition")
