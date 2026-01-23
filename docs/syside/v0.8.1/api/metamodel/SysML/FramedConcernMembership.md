<div id="framedconcernmembership" class="section">

<span id="metamodel-sysml-framedconcernmembership"></span>

# FramedConcernMembership[](#framedconcernmembership "Link to this heading")

`FramedConcernMembership` is defined in SysML specification on [page 389](https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=389). Excerpt from the machine readable specification:

> 
> 
> <div>
> 
> A `FramedConcernMembership` is a `RequirementConstraintMembership` for a framed `ConcernUsage` of a `RequirementDefinition` or `RequirementUsage`.
> 
> </div>

The following diagram shows the inheritance hierarchy of `FramedConcernMembership` according to the specification:

<div class="align-center" data-align="center">

<div class="graphviz">

![// Class: FramedConcernMembership digraph { FramedConcernMembership \[label="FramedConcernMembership (SysML)" shape=plaintext\] RequirementConstraintMembership -\> FramedConcernMembership RequirementConstraintMembership \[label="RequirementConstraintMembership (SysML)" shape=plaintext\] FeatureMembership -\> RequirementConstraintMembership FeatureMembership \[label="FeatureMembership (KerML)" shape=plaintext\] OwningMembership -\> FeatureMembership OwningMembership \[label="OwningMembership (KerML)" shape=plaintext\] Membership -\> OwningMembership Membership \[label="Membership (KerML)" shape=plaintext\] Relationship -\> Membership Relationship \[label="Relationship (KerML)" shape=plaintext\] Element -\> Relationship Element \[label="Element (KerML)" shape=plaintext\] }](_images/graphviz-b26cd2ad6b1c9d0fe28cdc1ebd55d4064af1c5c2.png)

</div>

</div>

The following table shows all attributes defined for `FramedConcernMembership` according to the specification together with the documentation from the machine readable specification. Note that in Syside API, we use snake case for attribute names instead of Pascal case used in the specification.

<div class="pst-scrollable-table-container">

Attribute

</div>

</div>

Documentation from machine readable specification

Attributes defined in [`FramedConcernMembership`](#syside.FramedConcernMembership "syside.FramedConcernMembership"):

[`owned_concern`](#syside.FramedConcernMembership.owned_concern "syside.FramedConcernMembership.owned_concern")

The `ConcernUsage` that is the `ownedConstraint` of this `FramedConcernMembership`.

[`referenced_concern`](#syside.FramedConcernMembership.referenced_concern "syside.FramedConcernMembership.referenced_concern")

The `ConcernUsage` that is referenced through this `FramedConcernMembership`. It is the `referencedConstraint` of the `FramedConcernMembership` considered as a `RequirementConstraintMembership`, which must be a `ConcernUsage`.

Attributes defined in [`RequirementConstraintMembership`](/v0.8.1/api/metamodel/SysML/RequirementConstraintMembership.md "syside.RequirementConstraintMembership"):

[`kind`](/v0.8.1/api/metamodel/SysML/RequirementConstraintMembership.md "syside.RequirementConstraintMembership.kind")

Whether the `RequirementConstraintMembership` is for an assumed or required `ConstraintUsage`.

[`owned_constraint`](/v0.8.1/api/metamodel/SysML/RequirementConstraintMembership.md "syside.RequirementConstraintMembership.owned_constraint")

The `ConstraintUsage` that is the `ownedMemberFeature` of this `RequirementConstraintMembership`.

[`referenced_constraint`](/v0.8.1/api/metamodel/SysML/RequirementConstraintMembership.md "syside.RequirementConstraintMembership.referenced_constraint")

The `ConstraintUsage` that is referenced through this `RequirementConstraintMembership`. It is the `referencedFeature` of the `ownedReferenceSubsetting` of the `ownedConstraint`, if there is one, and, otherwise, the `ownedConstraint` itself.

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

The following table lists Syside specific attributes available for class [`FramedConcernMembership`](#syside.FramedConcernMembership "syside.FramedConcernMembership"):

<div class="pst-scrollable-table-container">

|                                                                                   |
| --------------------------------------------------------------------------------- |
| Python Attribute                                                                  |
| [`STD`](#syside.FramedConcernMembership.STD "syside.FramedConcernMembership.STD") |

</div>

  - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">FramedConcernMembership</span></span>[](#syside.FramedConcernMembership "Link to this definition")
    
      - <span class="sig-name descname"><span class="pre">\_\_cpp\_name\_\_</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">'syside::sysml::FramedConcernMembership'</span>*[](#syside.FramedConcernMembership.__cpp_name__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">STD</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><span class="pre">type</span><span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.FramedConcernMembership</span>](#syside.FramedConcernMembership "syside.FramedConcernMembership")<span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="p"><span class="pre">...</span></span><span class="p"><span class="pre">\]</span></span><span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">()</span>*[](#syside.FramedConcernMembership.STD "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned\_concern</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.ConcernUsage</span>](/v0.8.1/api/metamodel/SysML/ConcernUsage.md "syside.ConcernUsage")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span>*[](#syside.FramedConcernMembership.owned_concern "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">referenced\_concern</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.ConcernUsage</span>](/v0.8.1/api/metamodel/SysML/ConcernUsage.md "syside.ConcernUsage")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span>*[](#syside.FramedConcernMembership.referenced_concern "Link to this definition")
