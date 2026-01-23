<div id="package" class="section">

<span id="metamodel-kerml-package"></span>

# Package[](#package "Link to this heading")

`Package` is defined in KerML specification on [page 264](https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=264). Excerpt from the machine readable specification:

> 
> 
> <div>
> 
> A `Package` is a `Namespace` used to group `Elements`, without any instance-level semantics. It may have one or more model-level evaluable `filterCondition` `Expressions` used to filter its `importedMemberships`. Any imported `member` must meet all of the `filterConditions`.
> 
> </div>

The following diagram shows the inheritance hierarchy of `Package` according to the specification:

<div class="align-center" data-align="center">

<div class="graphviz">

![// Class: Package digraph { Package \[label="Package (KerML)" shape=plaintext\] Namespace -\> Package Namespace \[label="Namespace (KerML)" shape=plaintext\] Element -\> Namespace Element \[label="Element (KerML)" shape=plaintext\] }](_images/graphviz-50b17c5323274c473193d62c288e2ae6d22631e1.png)

</div>

</div>

The following table shows all attributes defined for `Package` according to the specification together with the documentation from the machine readable specification. Note that in Syside API, we use snake case for attribute names instead of Pascal case used in the specification.

<div class="pst-scrollable-table-container">

Attribute

</div>

</div>

Documentation from machine readable specification

Attributes defined in [`Package`](#syside.Package "syside.Package"):

[`filter_conditions`](#syside.Package.filter_conditions "syside.Package.filter_conditions")

The model-level evaluable `Boolean`-valued `Expression` used to filter the `members` of this `Package`, which are owned by the `Package` are via `ElementFilterMemberships`.

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

The following table lists Syside specific attributes available for class [`Package`](#syside.Package "syside.Package"):

<div class="pst-scrollable-table-container">

|                                                   |
| ------------------------------------------------- |
| Python Attribute                                  |
| [`STD`](#syside.Package.STD "syside.Package.STD") |

</div>

  - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">Package</span></span>[](#syside.Package "Link to this definition")
    
      - <span class="sig-name descname"><span class="pre">\_\_cpp\_name\_\_</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">'syside::sysml::Package'</span>*[](#syside.Package.__cpp_name__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">STD</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><span class="pre">type</span><span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Package</span>](#syside.Package "syside.Package")<span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="p"><span class="pre">...</span></span><span class="p"><span class="pre">\]</span></span><span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">()</span>*[](#syside.Package.STD "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">filter\_conditions</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.ElementFilterMembership</span>](/v0.8.1/api/metamodel/KerML/ElementFilterMembership.md "syside.ElementFilterMembership")<span class="p"><span class="pre">\]</span></span>*[](#syside.Package.filter_conditions "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">prefixes</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.NamespacePrefixes</span>](/v0.8.1/api/generated/syside.NamespacePrefixes.md "syside.NamespacePrefixes")*[](#syside.Package.prefixes "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">children</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.NamespaceBody</span>](/v0.8.1/api/generated/syside.NamespaceBody.md "syside.NamespaceBody")*[](#syside.Package.children "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned\_memberships</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Membership</span>](/v0.8.1/api/metamodel/KerML/Membership.md "syside.Membership")<span class="p"><span class="pre">\]</span></span>*[](#syside.Package.owned_memberships "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">imported\_memberships</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Membership</span>](/v0.8.1/api/metamodel/KerML/Membership.md "syside.Membership")<span class="p"><span class="pre">\]</span></span>*[](#syside.Package.imported_memberships "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned\_members</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Element</span>](/v0.8.1/api/metamodel/KerML/Element.md "syside.Element")<span class="p"><span class="pre">\]</span></span>*[](#syside.Package.owned_members "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">memberships</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Membership</span>](/v0.8.1/api/metamodel/KerML/Membership.md "syside.Membership")<span class="p"><span class="pre">\]</span></span>*[](#syside.Package.memberships "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">members</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Element</span>](/v0.8.1/api/metamodel/KerML/Element.md "syside.Element")<span class="p"><span class="pre">\]</span></span>*[](#syside.Package.members "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned\_imports</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Import</span>](/v0.8.1/api/metamodel/KerML/Import.md "syside.Import")<span class="p"><span class="pre">\]</span></span>*[](#syside.Package.owned_imports "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_getitem\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.Element</span>](/v0.8.1/api/metamodel/KerML/Element.md "syside.Element")</span></span>[](#syside.Package.__getitem__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">get\_membership</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.Membership</span>](/v0.8.1/api/metamodel/KerML/Membership.md "syside.Membership")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span></span></span>[](#syside.Package.get_membership "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">get\_membership</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg0</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="n"><span class="pre">arg1</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.Membership</span>](/v0.8.1/api/metamodel/KerML/Membership.md "syside.Membership")</span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.Membership</span>](/v0.8.1/api/metamodel/KerML/Membership.md "syside.Membership")</span></span>
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">get\_member</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.Element</span>](/v0.8.1/api/metamodel/KerML/Element.md "syside.Element")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span></span></span>[](#syside.Package.get_member "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">get\_member</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg0</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="n"><span class="pre">arg1</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.Element</span>](/v0.8.1/api/metamodel/KerML/Element.md "syside.Element")</span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.Element</span>](/v0.8.1/api/metamodel/KerML/Element.md "syside.Element")</span></span>
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_str\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">str</span></span></span>[](#syside.Package.__str__ "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">element\_id</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">uuid.UUID</span>*[](#syside.Package.element_id "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">sema\_state</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.SemaState</span>](/v0.8.1/api/generated/syside.SemaState.md "syside.SemaState")*[](#syside.Package.sema_state "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">declared\_name</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span>*[](#syside.Package.declared_name "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">declared\_short\_name</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span>*[](#syside.Package.declared_short_name "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">name</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span>*[](#syside.Package.name "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">short\_name</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span>*[](#syside.Package.short_name "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">qualified\_name</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.QualifiedName</span>](/v0.8.1/api/generated/syside.QualifiedName.md "syside.QualifiedName")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span>*[](#syside.Package.qualified_name "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">path</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.Path</span>](/v0.8.1/api/generated/syside.Path.md "syside.Path")*[](#syside.Package.path "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">matches\_qualified\_name</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">Sequence</span><span class="p"><span class="pre">\[</span></span><span class="pre">str</span><span class="p"><span class="pre">\]</span></span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">bool</span></span></span>[](#syside.Package.matches_qualified_name "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">is\_implied\_included</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*[](#syside.Package.is_implied_included "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">is\_library\_element</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*[](#syside.Package.is_library_element "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owning\_membership</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.OwningMembership</span>](/v0.8.1/api/metamodel/KerML/OwningMembership.md "syside.OwningMembership")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span>*[](#syside.Package.owning_membership "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned\_relationships</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Relationship</span>](/v0.8.1/api/metamodel/KerML/Relationship.md "syside.Relationship")<span class="p"><span class="pre">\]</span></span>*[](#syside.Package.owned_relationships "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owning\_relationship</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.Relationship</span>](/v0.8.1/api/metamodel/KerML/Relationship.md "syside.Relationship")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span>*[](#syside.Package.owning_relationship "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owning\_namespace</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.Namespace</span>](/v0.8.1/api/metamodel/KerML/Namespace.md "syside.Namespace")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span>*[](#syside.Package.owning_namespace "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owner</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.Element</span>](/v0.8.1/api/metamodel/KerML/Element.md "syside.Element")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span>*[](#syside.Package.owner "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">scoped\_owner</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.Element</span>](/v0.8.1/api/metamodel/KerML/Element.md "syside.Element")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span>*[](#syside.Package.scoped_owner "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned\_elements</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Element</span>](/v0.8.1/api/metamodel/KerML/Element.md "syside.Element")<span class="p"><span class="pre">\]</span></span>*[](#syside.Package.owned_elements "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">documentation</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Documentation</span>](/v0.8.1/api/metamodel/KerML/Documentation.md "syside.Documentation")<span class="p"><span class="pre">\]</span></span>*[](#syside.Package.documentation "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned\_annotations</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Annotation</span>](/v0.8.1/api/metamodel/KerML/Annotation.md "syside.Annotation")<span class="p"><span class="pre">\]</span></span>*[](#syside.Package.owned_annotations "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">comments</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Comment</span>](/v0.8.1/api/metamodel/KerML/Comment.md "syside.Comment")<span class="p"><span class="pre">\]</span></span>*[](#syside.Package.comments "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">textual\_representations</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.TextualRepresentation</span>](/v0.8.1/api/metamodel/KerML/TextualRepresentation.md "syside.TextualRepresentation")<span class="p"><span class="pre">\]</span></span>*[](#syside.Package.textual_representations "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">metadata</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.MetadataFeature</span>](/v0.8.1/api/metamodel/KerML/MetadataFeature.md "syside.MetadataFeature")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span>[<span class="pre">syside.MetadataUsage</span>](/v0.8.1/api/metamodel/SysML/MetadataUsage.md "syside.MetadataUsage")<span class="p"><span class="pre">\]</span></span>*[](#syside.Package.metadata "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">alias\_ids</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">list</span><span class="p"><span class="pre">\[</span></span><span class="pre">str</span><span class="p"><span class="pre">\]</span></span>*[](#syside.Package.alias_ids "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_hash\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">int</span></span></span>[](#syside.Package.__hash__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">isinstance</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">type</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">syside.AstNode.isinstance.type</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.TNode</span><span class="p"><span class="pre">\]</span></span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">TypeGuard</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.TNode</span><span class="p"><span class="pre">\]</span></span></span></span>[](#syside.Package.isinstance "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">isinstance</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">type</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.AstNode.isinstance.type</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.TNode</span><span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="p"><span class="pre">...</span></span><span class="p"><span class="pre">\]</span></span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">TypeGuard</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.TNode</span><span class="p"><span class="pre">\]</span></span></span></span>
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">try\_cast</span></span><span class="sig-paren">(</span>*<span class="o"><span class="pre">\*</span></span><span class="n"><span class="pre">type</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">type</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.TNode</span><span class="p"><span class="pre">\]</span></span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">syside.TNode</span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span></span></span>[](#syside.Package.try_cast "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">try\_cast</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">type</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.AstNode.try\_cast.type</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.TNode</span><span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="p"><span class="pre">...</span></span><span class="p"><span class="pre">\]</span></span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">syside.TNode</span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span></span></span>
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">cast</span></span><span class="sig-paren">(</span>*<span class="o"><span class="pre">\*</span></span><span class="n"><span class="pre">type</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">type</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.TNode</span><span class="p"><span class="pre">\]</span></span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">syside.TNode</span></span></span>[](#syside.Package.cast "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">cast</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">type</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.AstNode.cast.type</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.TNode</span><span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="p"><span class="pre">...</span></span><span class="p"><span class="pre">\]</span></span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">syside.TNode</span></span></span>
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">parent</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.Element</span>](/v0.8.1/api/metamodel/KerML/Element.md "syside.Element")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span>*[](#syside.Package.parent "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">document</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.Document</span>](/v0.8.1/api/generated/syside.Document.md "syside.Document")*[](#syside.Package.document "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">cst\_node</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.CstNode</span>](/v0.8.1/api/generated/syside.CstNode.md "syside.CstNode")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span>*[](#syside.Package.cst_node "Link to this definition")
