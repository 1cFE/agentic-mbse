<div id="objectivemembership" class="section">

<span id="metamodel-sysml-objectivemembership"></span>

# ObjectiveMembership[](#objectivemembership "Link to this heading")

`ObjectiveMembership` is defined in SysML specification on [page 404](https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=404). Excerpt from the machine readable specification:

> 
> 
> <div>
> 
> An `ObjectiveMembership` is a `FeatureMembership` that indicates that its `ownedObjectiveRequirement` is the objective `RequirementUsage` for its `owningType`, which must be a `CaseDefinition` or `CaseUsage`.
> 
> </div>

The following diagram shows the inheritance hierarchy of `ObjectiveMembership` according to the specification:

<div class="align-center" data-align="center">

<div class="graphviz">

![// Class: ObjectiveMembership digraph { ObjectiveMembership \[label="ObjectiveMembership (SysML)" shape=plaintext\] FeatureMembership -\> ObjectiveMembership FeatureMembership \[label="FeatureMembership (KerML)" shape=plaintext\] OwningMembership -\> FeatureMembership OwningMembership \[label="OwningMembership (KerML)" shape=plaintext\] Membership -\> OwningMembership Membership \[label="Membership (KerML)" shape=plaintext\] Relationship -\> Membership Relationship \[label="Relationship (KerML)" shape=plaintext\] Element -\> Relationship Element \[label="Element (KerML)" shape=plaintext\] }](_images/graphviz-9f07ee0a2c4605cb848a420a164acbe0d4fd51ab.png)

</div>

</div>

The following table shows all attributes defined for `ObjectiveMembership` according to the specification together with the documentation from the machine readable specification. Note that in Syside API, we use snake case for attribute names instead of Pascal case used in the specification.

<div class="pst-scrollable-table-container">

Attribute

</div>

</div>

Documentation from machine readable specification

Attributes defined in [`ObjectiveMembership`](#syside.ObjectiveMembership "syside.ObjectiveMembership"):

[`owned_objective_requirement`](#syside.ObjectiveMembership.owned_objective_requirement "syside.ObjectiveMembership.owned_objective_requirement")

The RequirementUsage that is the `ownedMemberFeature` of this RequirementUsage.

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

The following table lists Syside specific attributes available for class [`ObjectiveMembership`](#syside.ObjectiveMembership "syside.ObjectiveMembership"):

<div class="pst-scrollable-table-container">

|                                                                           |
| ------------------------------------------------------------------------- |
| Python Attribute                                                          |
| [`STD`](#syside.ObjectiveMembership.STD "syside.ObjectiveMembership.STD") |

</div>

  - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">ObjectiveMembership</span></span>[](#syside.ObjectiveMembership "Link to this definition")
    
      - <span class="sig-name descname"><span class="pre">\_\_cpp\_name\_\_</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">'syside::sysml::ObjectiveMembership'</span>*[](#syside.ObjectiveMembership.__cpp_name__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">STD</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><span class="pre">type</span><span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.ObjectiveMembership</span>](#syside.ObjectiveMembership "syside.ObjectiveMembership")<span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="p"><span class="pre">...</span></span><span class="p"><span class="pre">\]</span></span><span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">()</span>*[](#syside.ObjectiveMembership.STD "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned\_objective\_requirement</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.RequirementUsage</span>](/v0.8.1/api/metamodel/SysML/RequirementUsage.md "syside.RequirementUsage")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span>*[](#syside.ObjectiveMembership.owned_objective_requirement "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owning\_type</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.Type</span>](/v0.8.1/api/metamodel/KerML/Type.md "syside.Type")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span>*[](#syside.ObjectiveMembership.owning_type "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned\_member\_feature</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.Feature</span>](/v0.8.1/api/metamodel/KerML/Feature.md "syside.Feature")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span>*[](#syside.ObjectiveMembership.owned_member_feature "Link to this definition")
