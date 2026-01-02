<div id="featurevalue" class="section">

<span id="metamodel-kerml-featurevalue"></span>

# FeatureValue[](#featurevalue "Link to this heading")

`FeatureValue` is defined in KerML specification on [page 254](https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=254). Excerpt from the machine readable specification:

> 
> 
> <div>
> 
> A `FeatureValue` is a `Membership` that identifies a particular member `Expression` that provides the value of the `Feature` that owns the `FeatureValue`. The value is specified as either a bound value or an initial value, and as either a concrete or default value. A `Feature` can have at most one `FeatureValue`.
> 
> The result of the `value` `Expression` is bound to the `featureWithValue` using a `BindingConnector`. If `isInitial = false`, then the `featuringType` of the `BindingConnector` is the same as the `featuringType` of the `featureWithValue`. If `isInitial = true`, then the `featuringType` of the `BindingConnector` is restricted to its `startShot`.
> 
> If `isDefault = false`, then the above semantics of the `FeatureValue` are realized for the given `featureWithValue`. Otherwise, the semantics are realized for any individual of the `featuringType` of the `featureWithValue`, unless another value is explicitly given for the `featureWithValue` for that individual.
> 
> </div>

The following diagram shows the inheritance hierarchy of `FeatureValue` according to the specification:

<div class="align-center" data-align="center">

<div class="graphviz">

![// Class: FeatureValue digraph { FeatureValue \[label="FeatureValue (KerML)" shape=plaintext\] OwningMembership -\> FeatureValue OwningMembership \[label="OwningMembership (KerML)" shape=plaintext\] Membership -\> OwningMembership Membership \[label="Membership (KerML)" shape=plaintext\] Relationship -\> Membership Relationship \[label="Relationship (KerML)" shape=plaintext\] Element -\> Relationship Element \[label="Element (KerML)" shape=plaintext\] }](_images/graphviz-7cb95ac6d46a9b52a376ba733fb771ed047a6afb.png)

</div>

</div>

The following table shows all attributes defined for `FeatureValue` according to the specification together with the documentation from the machine readable specification. Note that in Syside API, we use snake case for attribute names instead of Pascal case used in the specification.

<div class="pst-scrollable-table-container">

Attribute

</div>

</div>

Documentation from machine readable specification

Attributes defined in [`FeatureValue`](#syside.FeatureValue "syside.FeatureValue"):

[`feature_with_value`](#syside.FeatureValue.feature_with_value "syside.FeatureValue.feature_with_value")

The Feature to be provided a value.

The `Feature` to be provided a value.

[`is_default`](#syside.FeatureValue.is_default "syside.FeatureValue.is_default")

Whether this `FeatureValue` is a concrete specification of the bound or initial value of the `featureWithValue`, or just a default value that may be overridden.

[`is_initial`](#syside.FeatureValue.is_initial "syside.FeatureValue.is_initial")

Whether this `FeatureValue` specifies a bound value or an initial value for the `featureWithValue`.

[`value`](#syside.FeatureValue.value "syside.FeatureValue.value")

The Expression that provides the value as a result.

The `Expression` that provides the value of the `featureWithValue` as its `result`.

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

The following table lists Syside specific attributes available for class [`FeatureValue`](#syside.FeatureValue "syside.FeatureValue"):

<div class="pst-scrollable-table-container">

|                                                             |
| ----------------------------------------------------------- |
| Python Attribute                                            |
| [`STD`](#syside.FeatureValue.STD "syside.FeatureValue.STD") |

</div>

  - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">FeatureValue</span></span>[](#syside.FeatureValue "Link to this definition")
    
      - <span class="sig-name descname"><span class="pre">\_\_cpp\_name\_\_</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">'syside::sysml::FeatureValue'</span>*[](#syside.FeatureValue.__cpp_name__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">STD</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><span class="pre">type</span><span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.FeatureValue</span>](#syside.FeatureValue "syside.FeatureValue")<span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="p"><span class="pre">...</span></span><span class="p"><span class="pre">\]</span></span><span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">()</span>*[](#syside.FeatureValue.STD "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">is\_initial</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*[](#syside.FeatureValue.is_initial "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">is\_default</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*[](#syside.FeatureValue.is_default "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">feature\_with\_value</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.Feature</span>](/v0.8.1/api/metamodel/KerML/Feature.md "syside.Feature")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span>*[](#syside.FeatureValue.feature_with_value "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">value</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.Expression</span>](/v0.8.1/api/metamodel/KerML/Expression.md "syside.Expression")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span>*[](#syside.FeatureValue.value "Link to this definition")
