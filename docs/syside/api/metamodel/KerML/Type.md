<div id="type" class="section">

<span id="metamodel-kerml-type"></span>

# Type[](#type "Link to this heading")

`Type` is defined in KerML specification on [page 52](https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=52). Excerpt from the machine readable specification:

> 
> 
> <div>
> 
> A `Type` is a `Namespace` that is the most general kind of `Element` supporting the semantics of classification. A `Type` may be a `Classifier` or a `Feature`, defining conditions on what is classified by the `Type` (see also the description of `isSufficient`).
> 
> </div>

The following diagram shows the inheritance hierarchy of `Type` according to the specification:

<div class="align-center" data-align="center">

<div class="graphviz">

![// Class: Type digraph { Type \[label="Type (KerML)" shape=plaintext\] Namespace -\> Type Namespace \[label="Namespace (KerML)" shape=plaintext\] Element -\> Namespace Element \[label="Element (KerML)" shape=plaintext\] }](_images/graphviz-6c79d15b8b7a2ca916098f07db369e1a766c1572.png)

</div>

</div>

The following table shows all attributes defined for `Type` according to the specification together with the documentation from the machine readable specification. Note that in Syside API, we use snake case for attribute names instead of Pascal case used in the specification.

<div class="pst-scrollable-table-container">

Attribute

</div>

</div>

Documentation from machine readable specification

Attributes defined in [`Type`](#syside.Type "syside.Type"):

[`differencing_types`](#syside.Type.differencing_types "syside.Type.differencing_types")

The interpretations of a `Type` with `differencingTypes` are asserted to be those of the first of those `Types`, but not including those of the remaining `Types`. For example, a `Classifier` might be the difference of a `Classifier` for people and another for people of a particular nationality, leaving people who are not of that nationality. Similarly, a feature of people might be the difference between a feature for their children and a `Classifier` for people of a particular sex, identifying their children not of that sex (because the interpretations of the children `Feature` that identify those of that sex are also interpretations of the `Classifier` for that sex).

[`directed_features`](#syside.Type.directed_features "syside.Type.directed_features")

The `features` of this `Type` that have a non-null `direction`.

[`end_features`](#syside.Type.end_features "syside.Type.end_features")

All `features` of this `Type` with `isEnd = true`.

[`features`](#syside.Type.features "syside.Type.features")

The `ownedMemberFeatures` of the `featureMemberships` of this `Type`.

[`feature_memberships`](#syside.Type.feature_memberships "syside.Type.feature_memberships")

The `FeatureMemberships` for `features` of this `Type`, which include all `ownedFeatureMemberships` and those `inheritedMemberships` that are `FeatureMemberships` (but does *not* include any `importedMemberships`).

[`inherited_features`](#syside.Type.inherited_features "syside.Type.inherited_features")

All the `memberFeatures` of the `inheritedMemberships` of this `Type` that are `FeatureMemberships`.

[`inherited_memberships`](#syside.Type.inherited_memberships "syside.Type.inherited_memberships")

All `Memberships` inherited by this `Type` via `Specialization` or `Conjugation`. These are included in the derived union for the `memberships` of the `Type`.

[`inputs`](#syside.Type.inputs "syside.Type.inputs")

All `features` related to this `Type` by `FeatureMemberships` that have `direction` `in` or `inout`.

[`intersecting_types`](#syside.Type.intersecting_types "syside.Type.intersecting_types")

The interpretations of a `Type` with `intersectingTypes` are asserted to be those in common among the `intersectingTypes`, which are the `Types` derived from the `intersectingType` of the `ownedIntersectings` of this `Type`. For example, a `Classifier` might be an intersection of `Classifiers` for people of a particular sex and of a particular nationality. Similarly, a feature for people’s children of a particular sex might be the intersection of a `Feature` for their children and a `Classifier` for people of that sex (because the interpretations of the children `Feature` that identify those of that sex are also interpretations of the Classifier for that sex).

[`is_abstract`](#syside.Type.is_abstract "syside.Type.is_abstract")

Indicates whether instances of this `Type` must also be instances of at least one of its specialized `Types`.

[`is_conjugated`](#syside.Type.is_conjugated "syside.Type.is_conjugated")

Indicates whether this `Type` has an `ownedConjugator`.

[`is_sufficient`](#syside.Type.is_sufficient "syside.Type.is_sufficient")

Whether all things that meet the classification conditions of this `Type` must be classified by the `Type`.

(A `Type` gives conditions that must be met by whatever it classifies, but when `isSufficient` is false, things may meet those conditions but still not be classified by the `Type`. For example, a Type `Car` that is not sufficient could require everything it classifies to have four wheels, but not all four wheeled things would classify as cars. However, if the `Type` `Car` were sufficient, it would classify all four-wheeled things.)

[`multiplicity`](#syside.Type.multiplicity "syside.Type.multiplicity")

An `ownedMember` of this `Type` that is a `Multiplicity`, which constraints the cardinality of the `Type`. If there is no such `ownedMember`, then the cardinality of this `Type` is constrained by all the `Multiplicity` constraints applicable to any direct supertypes.

[`outputs`](#syside.Type.outputs "syside.Type.outputs")

All `features` related to this `Type` by `FeatureMemberships` that have `direction` `out` or `inout`.

[`owned_conjugator`](#syside.Type.owned_conjugator "syside.Type.owned_conjugator")

A `Conjugation` owned by this `Type` for which the `Type` is the `originalType`.

[`owned_differencings`](#syside.Type.owned_differencings "syside.Type.owned_differencings")

The `ownedRelationships` of this `Type` that are `Differencings`, having this `Type` as their `typeDifferenced`.

[`owned_disjoinings`](#syside.Type.owned_disjoinings "syside.Type.owned_disjoinings")

The `ownedRelationships` of this `Type` that are `Disjoinings`, for which the `Type` is the `typeDisjoined` `Type`.

[`owned_end_features`](#syside.Type.owned_end_features "syside.Type.owned_end_features")

All `endFeatures` of this `Type` that are `ownedFeatures`.

[`owned_features`](#syside.Type.owned_features "syside.Type.owned_features")

The `ownedMemberFeatures` of the `ownedFeatureMemberships` of this `Type`.

[`owned_feature_memberships`](#syside.Type.owned_feature_memberships "syside.Type.owned_feature_memberships")

The `ownedMemberships` of this `Type` that are `FeatureMemberships`, for which the `Type` is the `owningType`. Each such `FeatureMembership` identifies an `ownedFeature` of the `Type`.

[`owned_intersectings`](#syside.Type.owned_intersectings "syside.Type.owned_intersectings")

The `ownedRelationships` of this `Type` that are `Intersectings`, have the `Type` as their `typeIntersected`.

[`owned_specializations`](#syside.Type.owned_specializations "syside.Type.owned_specializations")

The `ownedRelationships` of this `Type` that are `Specializations`, for which the `Type` is the `specific` `Type`.

[`owned_unionings`](#syside.Type.owned_unionings "syside.Type.owned_unionings")

The `ownedRelationships` of this `Type` that are `Unionings`, having the `Type` as their `typeUnioned`.

[`unioning_types`](#syside.Type.unioning_types "syside.Type.unioning_types")

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

The following table lists Syside specific attributes available for class [`Type`](#syside.Type "syside.Type"):

<div class="pst-scrollable-table-container">

|                                                                                                                        |
| ---------------------------------------------------------------------------------------------------------------------- |
| Python Attribute                                                                                                       |
| [`STD`](#syside.Type.STD "syside.Type.STD")                                                                            |
| [`conforms`](#syside.Type.conforms "syside.Type.conforms")                                                             |
| [`declared_multiplicity`](#syside.Type.declared_multiplicity "syside.Type.declared_multiplicity")                      |
| [`declared_multiplicity_member`](#syside.Type.declared_multiplicity_member "syside.Type.declared_multiplicity_member") |
| [`direction_of`](#syside.Type.direction_of "syside.Type.direction_of")                                                 |
| [`disjoining_types`](#syside.Type.disjoining_types "syside.Type.disjoining_types")                                     |
| [`heritage`](#syside.Type.heritage "syside.Type.heritage")                                                             |
| [`is_abstract_explicitly`](#syside.Type.is_abstract_explicitly "syside.Type.is_abstract_explicitly")                   |
| [`is_sufficient_explicitly`](#syside.Type.is_sufficient_explicitly "syside.Type.is_sufficient_explicitly")             |
| [`owned_directed_features`](#syside.Type.owned_directed_features "syside.Type.owned_directed_features")                |
| [`owned_inputs`](#syside.Type.owned_inputs "syside.Type.owned_inputs")                                                 |
| [`owned_outputs`](#syside.Type.owned_outputs "syside.Type.owned_outputs")                                              |
| [`specializes`](#syside.Type.specializes "syside.Type.specializes")                                                    |
| [`type_relationships`](#syside.Type.type_relationships "syside.Type.type_relationships")                               |

</div>

  - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">Type</span></span>[](#syside.Type "Link to this definition")
    
      - <span class="sig-name descname"><span class="pre">\_\_cpp\_name\_\_</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">'syside::sysml::Type'</span>*[](#syside.Type.__cpp_name__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">STD</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><span class="pre">type</span><span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Type</span>](#syside.Type "syside.Type")<span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="p"><span class="pre">...</span></span><span class="p"><span class="pre">\]</span></span><span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">()</span>*[](#syside.Type.STD "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">is\_abstract</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*[](#syside.Type.is_abstract "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">is\_abstract\_explicitly</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*[](#syside.Type.is_abstract_explicitly "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">is\_sufficient</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*[](#syside.Type.is_sufficient "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">is\_sufficient\_explicitly</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*[](#syside.Type.is_sufficient_explicitly "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">is\_conjugated</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*[](#syside.Type.is_conjugated "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned\_specializations</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Specialization</span>](/v0.8.1/api/metamodel/KerML/Specialization.md "syside.Specialization")<span class="p"><span class="pre">\]</span></span>*[](#syside.Type.owned_specializations "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned\_feature\_memberships</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.FeatureMembership</span>](/v0.8.1/api/metamodel/KerML/FeatureMembership.md "syside.FeatureMembership")<span class="p"><span class="pre">\]</span></span>*[](#syside.Type.owned_feature_memberships "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned\_features</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Feature</span>](/v0.8.1/api/metamodel/KerML/Feature.md "syside.Feature")<span class="p"><span class="pre">\]</span></span>*[](#syside.Type.owned_features "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">feature\_memberships</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.FeatureMembership</span>](/v0.8.1/api/metamodel/KerML/FeatureMembership.md "syside.FeatureMembership")<span class="p"><span class="pre">\]</span></span>*[](#syside.Type.feature_memberships "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">features</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Feature</span>](/v0.8.1/api/metamodel/KerML/Feature.md "syside.Feature")<span class="p"><span class="pre">\]</span></span>*[](#syside.Type.features "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned\_inputs</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Feature</span>](/v0.8.1/api/metamodel/KerML/Feature.md "syside.Feature")<span class="p"><span class="pre">\]</span></span>*[](#syside.Type.owned_inputs "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">inputs</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Feature</span>](/v0.8.1/api/metamodel/KerML/Feature.md "syside.Feature")<span class="p"><span class="pre">\]</span></span>*[](#syside.Type.inputs "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned\_outputs</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Feature</span>](/v0.8.1/api/metamodel/KerML/Feature.md "syside.Feature")<span class="p"><span class="pre">\]</span></span>*[](#syside.Type.owned_outputs "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">outputs</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Feature</span>](/v0.8.1/api/metamodel/KerML/Feature.md "syside.Feature")<span class="p"><span class="pre">\]</span></span>*[](#syside.Type.outputs "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">inherited\_memberships</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Membership</span>](/v0.8.1/api/metamodel/KerML/Membership.md "syside.Membership")<span class="p"><span class="pre">\]</span></span>*[](#syside.Type.inherited_memberships "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned\_end\_features</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Feature</span>](/v0.8.1/api/metamodel/KerML/Feature.md "syside.Feature")<span class="p"><span class="pre">\]</span></span>*[](#syside.Type.owned_end_features "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">end\_features</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Feature</span>](/v0.8.1/api/metamodel/KerML/Feature.md "syside.Feature")<span class="p"><span class="pre">\]</span></span>*[](#syside.Type.end_features "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned\_conjugator</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.Conjugation</span>](/v0.8.1/api/metamodel/KerML/Conjugation.md "syside.Conjugation")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span>*[](#syside.Type.owned_conjugator "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">inherited\_features</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Feature</span>](/v0.8.1/api/metamodel/KerML/Feature.md "syside.Feature")<span class="p"><span class="pre">\]</span></span>*[](#syside.Type.inherited_features "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">multiplicity</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.Multiplicity</span>](/v0.8.1/api/metamodel/KerML/Multiplicity.md "syside.Multiplicity")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span>*[](#syside.Type.multiplicity "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">declared\_multiplicity</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.MultiplicityRange</span>](/v0.8.1/api/metamodel/KerML/MultiplicityRange.md "syside.MultiplicityRange")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span>*[](#syside.Type.declared_multiplicity "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">declared\_multiplicity\_member</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.OwnedMultiplicityAccessor</span>](/v0.8.1/api/generated/syside.OwnedMultiplicityAccessor.md "syside.OwnedMultiplicityAccessor")*[](#syside.Type.declared_multiplicity_member "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned\_unionings</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Unioning</span>](/v0.8.1/api/metamodel/KerML/Unioning.md "syside.Unioning")<span class="p"><span class="pre">\]</span></span>*[](#syside.Type.owned_unionings "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">unioning\_types</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Type</span>](#syside.Type "syside.Type")<span class="p"><span class="pre">\]</span></span>*[](#syside.Type.unioning_types "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned\_intersectings</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Intersecting</span>](/v0.8.1/api/metamodel/KerML/Intersecting.md "syside.Intersecting")<span class="p"><span class="pre">\]</span></span>*[](#syside.Type.owned_intersectings "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">intersecting\_types</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Type</span>](#syside.Type "syside.Type")<span class="p"><span class="pre">\]</span></span>*[](#syside.Type.intersecting_types "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned\_disjoinings</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Disjoining</span>](/v0.8.1/api/metamodel/KerML/Disjoining.md "syside.Disjoining")<span class="p"><span class="pre">\]</span></span>*[](#syside.Type.owned_disjoinings "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">disjoining\_types</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Type</span>](#syside.Type "syside.Type")<span class="p"><span class="pre">\]</span></span>*[](#syside.Type.disjoining_types "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned\_differencings</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Differencing</span>](/v0.8.1/api/metamodel/KerML/Differencing.md "syside.Differencing")<span class="p"><span class="pre">\]</span></span>*[](#syside.Type.owned_differencings "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">differencing\_types</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Type</span>](#syside.Type "syside.Type")<span class="p"><span class="pre">\]</span></span>*[](#syside.Type.differencing_types "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned\_directed\_features</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Feature</span>](/v0.8.1/api/metamodel/KerML/Feature.md "syside.Feature")<span class="p"><span class="pre">\]</span></span>*[](#syside.Type.owned_directed_features "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">directed\_features</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Feature</span>](/v0.8.1/api/metamodel/KerML/Feature.md "syside.Feature")<span class="p"><span class="pre">\]</span></span>*[](#syside.Type.directed_features "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">heritage</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.Heritage</span>](/v0.8.1/api/generated/syside.Heritage.md "syside.Heritage")*[](#syside.Type.heritage "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">type\_relationships</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.TypeRelationships</span>](/v0.8.1/api/generated/syside.TypeRelationships.md "syside.TypeRelationships")*[](#syside.Type.type_relationships "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">conforms</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">Sequence</span><span class="p"><span class="pre">\[</span></span><span class="pre">str</span><span class="p"><span class="pre">\]</span></span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">bool</span></span></span>[](#syside.Type.conforms "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">conforms</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.Type</span>](#syside.Type "syside.Type")</span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">bool</span></span></span>
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">specializes</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">Sequence</span><span class="p"><span class="pre">\[</span></span><span class="pre">str</span><span class="p"><span class="pre">\]</span></span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">bool</span></span></span>[](#syside.Type.specializes "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">specializes</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.Type</span>](#syside.Type "syside.Type")</span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">bool</span></span></span>
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">direction\_of</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.Feature</span>](/v0.8.1/api/metamodel/KerML/Feature.md "syside.Feature")</span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.FeatureDirectionKind</span>](/v0.8.1/api/metamodel/KerML/FeatureDirectionKind.md "syside.FeatureDirectionKind")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span></span></span>[](#syside.Type.direction_of "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">prefixes</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.NamespacePrefixes</span>](/v0.8.1/api/generated/syside.NamespacePrefixes.md "syside.NamespacePrefixes")*[](#syside.Type.prefixes "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">children</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.NamespaceBody</span>](/v0.8.1/api/generated/syside.NamespaceBody.md "syside.NamespaceBody")*[](#syside.Type.children "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned\_memberships</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Membership</span>](/v0.8.1/api/metamodel/KerML/Membership.md "syside.Membership")<span class="p"><span class="pre">\]</span></span>*[](#syside.Type.owned_memberships "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">imported\_memberships</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Membership</span>](/v0.8.1/api/metamodel/KerML/Membership.md "syside.Membership")<span class="p"><span class="pre">\]</span></span>*[](#syside.Type.imported_memberships "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned\_members</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Element</span>](/v0.8.1/api/metamodel/KerML/Element.md "syside.Element")<span class="p"><span class="pre">\]</span></span>*[](#syside.Type.owned_members "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">memberships</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Membership</span>](/v0.8.1/api/metamodel/KerML/Membership.md "syside.Membership")<span class="p"><span class="pre">\]</span></span>*[](#syside.Type.memberships "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">members</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Element</span>](/v0.8.1/api/metamodel/KerML/Element.md "syside.Element")<span class="p"><span class="pre">\]</span></span>*[](#syside.Type.members "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned\_imports</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Import</span>](/v0.8.1/api/metamodel/KerML/Import.md "syside.Import")<span class="p"><span class="pre">\]</span></span>*[](#syside.Type.owned_imports "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_getitem\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.Element</span>](/v0.8.1/api/metamodel/KerML/Element.md "syside.Element")</span></span>[](#syside.Type.__getitem__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">get\_membership</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.Membership</span>](/v0.8.1/api/metamodel/KerML/Membership.md "syside.Membership")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span></span></span>[](#syside.Type.get_membership "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">get\_membership</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg0</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="n"><span class="pre">arg1</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.Membership</span>](/v0.8.1/api/metamodel/KerML/Membership.md "syside.Membership")</span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.Membership</span>](/v0.8.1/api/metamodel/KerML/Membership.md "syside.Membership")</span></span>
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">get\_member</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.Element</span>](/v0.8.1/api/metamodel/KerML/Element.md "syside.Element")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span></span></span>[](#syside.Type.get_member "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">get\_member</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg0</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="n"><span class="pre">arg1</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.Element</span>](/v0.8.1/api/metamodel/KerML/Element.md "syside.Element")</span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.Element</span>](/v0.8.1/api/metamodel/KerML/Element.md "syside.Element")</span></span>
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_str\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">str</span></span></span>[](#syside.Type.__str__ "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">element\_id</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">uuid.UUID</span>*[](#syside.Type.element_id "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">sema\_state</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.SemaState</span>](/v0.8.1/api/generated/syside.SemaState.md "syside.SemaState")*[](#syside.Type.sema_state "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">declared\_name</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span>*[](#syside.Type.declared_name "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">declared\_short\_name</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span>*[](#syside.Type.declared_short_name "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">name</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span>*[](#syside.Type.name "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">short\_name</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span>*[](#syside.Type.short_name "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">qualified\_name</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.QualifiedName</span>](/v0.8.1/api/generated/syside.QualifiedName.md "syside.QualifiedName")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span>*[](#syside.Type.qualified_name "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">path</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.Path</span>](/v0.8.1/api/generated/syside.Path.md "syside.Path")*[](#syside.Type.path "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">matches\_qualified\_name</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">Sequence</span><span class="p"><span class="pre">\[</span></span><span class="pre">str</span><span class="p"><span class="pre">\]</span></span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">bool</span></span></span>[](#syside.Type.matches_qualified_name "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">is\_implied\_included</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*[](#syside.Type.is_implied_included "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">is\_library\_element</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*[](#syside.Type.is_library_element "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owning\_membership</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.OwningMembership</span>](/v0.8.1/api/metamodel/KerML/OwningMembership.md "syside.OwningMembership")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span>*[](#syside.Type.owning_membership "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned\_relationships</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Relationship</span>](/v0.8.1/api/metamodel/KerML/Relationship.md "syside.Relationship")<span class="p"><span class="pre">\]</span></span>*[](#syside.Type.owned_relationships "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owning\_relationship</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.Relationship</span>](/v0.8.1/api/metamodel/KerML/Relationship.md "syside.Relationship")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span>*[](#syside.Type.owning_relationship "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owning\_namespace</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.Namespace</span>](/v0.8.1/api/metamodel/KerML/Namespace.md "syside.Namespace")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span>*[](#syside.Type.owning_namespace "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owner</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.Element</span>](/v0.8.1/api/metamodel/KerML/Element.md "syside.Element")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span>*[](#syside.Type.owner "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">scoped\_owner</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.Element</span>](/v0.8.1/api/metamodel/KerML/Element.md "syside.Element")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span>*[](#syside.Type.scoped_owner "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned\_elements</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Element</span>](/v0.8.1/api/metamodel/KerML/Element.md "syside.Element")<span class="p"><span class="pre">\]</span></span>*[](#syside.Type.owned_elements "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">documentation</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Documentation</span>](/v0.8.1/api/metamodel/KerML/Documentation.md "syside.Documentation")<span class="p"><span class="pre">\]</span></span>*[](#syside.Type.documentation "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned\_annotations</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Annotation</span>](/v0.8.1/api/metamodel/KerML/Annotation.md "syside.Annotation")<span class="p"><span class="pre">\]</span></span>*[](#syside.Type.owned_annotations "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">comments</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Comment</span>](/v0.8.1/api/metamodel/KerML/Comment.md "syside.Comment")<span class="p"><span class="pre">\]</span></span>*[](#syside.Type.comments "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">textual\_representations</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.TextualRepresentation</span>](/v0.8.1/api/metamodel/KerML/TextualRepresentation.md "syside.TextualRepresentation")<span class="p"><span class="pre">\]</span></span>*[](#syside.Type.textual_representations "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">metadata</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.MetadataFeature</span>](/v0.8.1/api/metamodel/KerML/MetadataFeature.md "syside.MetadataFeature")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span>[<span class="pre">syside.MetadataUsage</span>](/v0.8.1/api/metamodel/SysML/MetadataUsage.md "syside.MetadataUsage")<span class="p"><span class="pre">\]</span></span>*[](#syside.Type.metadata "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">alias\_ids</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">list</span><span class="p"><span class="pre">\[</span></span><span class="pre">str</span><span class="p"><span class="pre">\]</span></span>*[](#syside.Type.alias_ids "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_hash\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">int</span></span></span>[](#syside.Type.__hash__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">isinstance</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">type</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">syside.AstNode.isinstance.type</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.TNode</span><span class="p"><span class="pre">\]</span></span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">TypeGuard</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.TNode</span><span class="p"><span class="pre">\]</span></span></span></span>[](#syside.Type.isinstance "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">isinstance</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">type</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.AstNode.isinstance.type</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.TNode</span><span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="p"><span class="pre">...</span></span><span class="p"><span class="pre">\]</span></span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">TypeGuard</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.TNode</span><span class="p"><span class="pre">\]</span></span></span></span>
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">try\_cast</span></span><span class="sig-paren">(</span>*<span class="o"><span class="pre">\*</span></span><span class="n"><span class="pre">type</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">type</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.TNode</span><span class="p"><span class="pre">\]</span></span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">syside.TNode</span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span></span></span>[](#syside.Type.try_cast "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">try\_cast</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">type</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.AstNode.try\_cast.type</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.TNode</span><span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="p"><span class="pre">...</span></span><span class="p"><span class="pre">\]</span></span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">syside.TNode</span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span></span></span>
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">cast</span></span><span class="sig-paren">(</span>*<span class="o"><span class="pre">\*</span></span><span class="n"><span class="pre">type</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">type</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.TNode</span><span class="p"><span class="pre">\]</span></span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">syside.TNode</span></span></span>[](#syside.Type.cast "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">cast</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">type</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.AstNode.cast.type</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.TNode</span><span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="p"><span class="pre">...</span></span><span class="p"><span class="pre">\]</span></span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">syside.TNode</span></span></span>
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">parent</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.Element</span>](/v0.8.1/api/metamodel/KerML/Element.md "syside.Element")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span>*[](#syside.Type.parent "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">document</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.Document</span>](/v0.8.1/api/generated/syside.Document.md "syside.Document")*[](#syside.Type.document "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">cst\_node</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.CstNode</span>](/v0.8.1/api/generated/syside.CstNode.md "syside.CstNode")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span>*[](#syside.Type.cst_node "Link to this definition")
