<div id="parametermembership" class="section">

<span id="metamodel-kerml-parametermembership"></span>

# ParameterMembership[](#parametermembership "Link to this heading")

`ParameterMembership` is defined in KerML specification on [page 222](https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=222). Excerpt from the machine readable specification:

> 
> 
> <div>
> 
> A `ParameterMembership` is a `FeatureMembership` that identifies its `memberFeature` as a parameter, which is always owned, and must have a `direction`. A `ParameterMembership` must be owned by a `Behavior`, a `Step`, or the `result` parameter of a `ConstructorExpression`.
> 
> </div>

The following diagram shows the inheritance hierarchy of `ParameterMembership` according to the specification:

<div class="align-center" data-align="center">

<div class="graphviz">

![// Class: ParameterMembership digraph { ParameterMembership \[label="ParameterMembership (KerML)" shape=plaintext\] FeatureMembership -\> ParameterMembership FeatureMembership \[label="FeatureMembership (KerML)" shape=plaintext\] OwningMembership -\> FeatureMembership OwningMembership \[label="OwningMembership (KerML)" shape=plaintext\] Membership -\> OwningMembership Membership \[label="Membership (KerML)" shape=plaintext\] Relationship -\> Membership Relationship \[label="Relationship (KerML)" shape=plaintext\] Element -\> Relationship Element \[label="Element (KerML)" shape=plaintext\] }](_images/graphviz-6c923f7b4cb682469ce87f38b67da91071426b3f.png)

</div>

</div>

The following table shows all attributes defined for `ParameterMembership` according to the specification together with the documentation from the machine readable specification. Note that in Syside API, we use snake case for attribute names instead of Pascal case used in the specification.

<div class="pst-scrollable-table-container">

Attribute

</div>

</div>

Documentation from machine readable specification

Attributes defined in [`ParameterMembership`](#syside.ParameterMembership "syside.ParameterMembership"):

[`owned_member_parameter`](#syside.ParameterMembership.owned_member_parameter "syside.ParameterMembership.owned_member_parameter")

The `Feature` that is identified as a `parameter` by this `ParameterMembership`.

Attributes defined in [`FeatureMembership`](/v0.8.1/api/metamodel/KerML/FeatureMembership.md "syside.FeatureMembership"):

[`owned_member_feature`](/v0.8.1/api/metamodel/KerML/FeatureMembership.md "syside.FeatureMembership.owned_member_feature")

The `Feature` that this `FeatureMembership` relates to its `owningType`, making it an `ownedFeature` of the `owningType`.

[`owning_type`](/v0.8.1/api/metamodel/KerML/FeatureMembership.md "syside.FeatureMembership.owning_type")

The `Type` that owns this `FeatureMembership`.

Attributes defined in [`OwningMembership`](/v0.8.1/api/metamodel/KerML/OwningMembership.md "syside.OwningMembership"):

[`owned_member_element`](/v0.8.1/api/metamodel/KerML/OwningMembership.md "syside.OwningMembership.owned_member_element")

The `Element` that becomes an `ownedMember` of the `membershipOwningNamespace` due to this `OwningMembership`.

[`owned_member_element_id`](/v0.8.1/api/metamodel/KerML/OwningMembership.md "syside.OwningMembership.owned_member_element_id")

The `elementId` of the `ownedMemberElement`.

[`owned_member_name`](/v0.8.1/api/metamodel/KerML/OwningMembership.md "syside.OwningMembership.owned_member_name")

The `name` of the `ownedMemberElement`.

[`owned_member_short_name`](/v0.8.1/api/metamodel/KerML/OwningMembership.md "syside.OwningMembership.owned_member_short_name")

The `shortName` of the `ownedMemberElement`.

Attributes defined in [`Membership`](/v0.8.1/api/metamodel/KerML/Membership.md "syside.Membership"):

[`member_element`](/v0.8.1/api/metamodel/KerML/Membership.md "syside.Membership.member_element")

The `Element` that becomes a `member` of the `membershipOwningNamespace` due to this `Membership`.

[`member_element_id`](/v0.8.1/api/metamodel/KerML/Membership.md "syside.Membership.member_element_id")

The `elementId` of the `memberElement`.

[`member_name`](/v0.8.1/api/metamodel/KerML/Membership.md "syside.Membership.member_name")

The name of the `memberElement` relative to the `membershipOwningNamespace`.

[`member_short_name`](/v0.8.1/api/metamodel/KerML/Membership.md "syside.Membership.member_short_name")

The short name of the `memberElement` relative to the `membershipOwningNamespace`.

[`membership_owning_namespace`](/v0.8.1/api/metamodel/KerML/Membership.md "syside.Membership.membership_owning_namespace")

The `Namespace` of which the `memberElement` becomes a `member` due to this `Membership`.

`visibility`

Whether or not the `Membership` of the `memberElement` in the `membershipOwningNamespace` is publicly visible outside that `Namespace`.

Attributes defined in [`Relationship`](/v0.8.1/api/metamodel/KerML/Relationship.md "syside.Relationship"):

[`is_implied`](/v0.8.1/api/metamodel/KerML/Relationship.md "syside.Relationship.is_implied")

Whether this Relationship was generated by tooling to meet semantic rules, rather than being directly created by a modeler.

[`owned_related_elements`](/v0.8.1/api/metamodel/KerML/Relationship.md "syside.Relationship.owned_related_elements")

The relatedElements of this Relationship that are owned by the Relationship.

[`owning_related_element`](/v0.8.1/api/metamodel/KerML/Relationship.md "syside.Relationship.owning_related_element")

The relatedElement of this Relationship that owns the Relationship, if any.

[`related_elements`](/v0.8.1/api/metamodel/KerML/Relationship.md "syside.Relationship.related_elements")

The Elements that are related by this Relationship, derived as the union of the `source` and `target` Elements of the Relationship.

[`sources`](/v0.8.1/api/metamodel/KerML/Relationship.md "syside.Relationship.sources")

The `relatedElements from which this Relationship is considered to be directed.`

[`targets`](/v0.8.1/api/metamodel/KerML/Relationship.md "syside.Relationship.targets")

The `relatedElements` to which this Relationship is considered to be directed.

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

The following table lists Syside specific attributes available for class [`ParameterMembership`](#syside.ParameterMembership "syside.ParameterMembership"):

<div class="pst-scrollable-table-container">

|                                                                                                                           |
| ------------------------------------------------------------------------------------------------------------------------- |
| Python Attribute                                                                                                          |
| [`STD`](#syside.ParameterMembership.STD "syside.ParameterMembership.STD")                                                 |
| [`parameter_direction`](#syside.ParameterMembership.parameter_direction "syside.ParameterMembership.parameter_direction") |

</div>

  - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">ParameterMembership</span></span>[](#syside.ParameterMembership "Link to this definition")
    
      - <span class="sig-name descname"><span class="pre">\_\_cpp\_name\_\_</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">'syside::sysml::ParameterMembership'</span>*[](#syside.ParameterMembership.__cpp_name__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">STD</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><span class="pre">type</span><span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.ParameterMembership</span>](#syside.ParameterMembership "syside.ParameterMembership")<span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="p"><span class="pre">...</span></span><span class="p"><span class="pre">\]</span></span><span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">()</span>*[](#syside.ParameterMembership.STD "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned\_member\_parameter</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.Feature</span>](/v0.8.1/api/metamodel/KerML/Feature.md "syside.Feature")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span>*[](#syside.ParameterMembership.owned_member_parameter "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">parameter\_direction</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.FeatureDirectionKind</span>](/v0.8.1/api/metamodel/KerML/FeatureDirectionKind.md "syside.FeatureDirectionKind")</span></span>[](#syside.ParameterMembership.parameter_direction "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owning\_type</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.Type</span>](/v0.8.1/api/metamodel/KerML/Type.md "syside.Type")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span>*[](#syside.ParameterMembership.owning_type "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned\_member\_feature</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.Feature</span>](/v0.8.1/api/metamodel/KerML/Feature.md "syside.Feature")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span>*[](#syside.ParameterMembership.owned_member_feature "Link to this definition")
