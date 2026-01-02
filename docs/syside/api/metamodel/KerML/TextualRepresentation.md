<div id="textualrepresentation" class="section">

<span id="metamodel-kerml-textualrepresentation"></span>

# TextualRepresentation[](#textualrepresentation "Link to this heading")

`TextualRepresentation` is defined in KerML specification on [page 108](https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=108). Excerpt from the machine readable specification:

> 
> 
> <div>
> 
> A `TextualRepresentation` is an `AnnotatingElement` whose `body` represents the `representedElement` in a given `language`. The `representedElement` must be the `owner` of the `TextualRepresentation`. The named `language` can be a natural language, in which case the `body` is an informal representation, or an artificial language, in which case the `body` is expected to be a formal, machine-parsable representation.
> 
> If the named `language` of a `TextualRepresentation` is machine-parsable, then the `body` text should be legal input text as defined for that `language`. The interpretation of the named language string shall be case insensitive. The following `language` names are defined to correspond to the given standard languages:
> 
> <div class="pst-scrollable-table-container">
> 
> |         |                            |
> | ------- | -------------------------- |
> | `kerml` | Kernel Modeling Language   |
> | `ocl`   | Object Constraint Language |
> | `alf`   | Action Language for fUML   |
> 

> </div>
> 
> Other specifications may define specific `language` strings, other than those shown above, to be used to indicate the use of languages from those specifications in KerML `TextualRepresentation`.
> 
> If the `language` of a `TextualRepresentation` is “`kerml`”, then the `body` text shall be a legal representation of the `representedElement` in the KerML textual concrete syntax. A conforming tool can use such a `TextualRepresentation` `Annotation` to record the original KerML concrete syntax text from which an `Element` was parsed. In this case, it is a tool responsibility to ensure that the `body` of the `TextualRepresentation` remains correct (or the Annotation is removed) if the annotated `Element` changes other than by re-parsing the `body` text.
> 
> An `Element` with a `TextualRepresentation` in a language other than KerML is essentially a semantically “opaque” `Element` specified in the other language. However, a conforming KerML tool may interpret such an element consistently with the specification of the named language.
> 
> </div>

The following diagram shows the inheritance hierarchy of `TextualRepresentation` according to the specification:

<div class="align-center" data-align="center">

<div class="graphviz">

![// Class: TextualRepresentation digraph { TextualRepresentation \[label="TextualRepresentation (KerML)" shape=plaintext\] AnnotatingElement -\> TextualRepresentation AnnotatingElement \[label="AnnotatingElement (KerML)" shape=plaintext\] Element -\> AnnotatingElement Element \[label="Element (KerML)" shape=plaintext\] }](_images/graphviz-ab35538f581f4f9ed516779819afaf1164f45451.png)

</div>

</div>

The following table shows all attributes defined for `TextualRepresentation` according to the specification together with the documentation from the machine readable specification. Note that in Syside API, we use snake case for attribute names instead of Pascal case used in the specification.

<div class="pst-scrollable-table-container">

Attribute

</div>

</div>

Documentation from machine readable specification

Attributes defined in [`TextualRepresentation`](#syside.TextualRepresentation "syside.TextualRepresentation"):

[`body`](#syside.TextualRepresentation.body "syside.TextualRepresentation.body")

The textual representation of the `representedElement` in the given `language`.

[`language`](#syside.TextualRepresentation.language "syside.TextualRepresentation.language")

The natural or artificial language in which the `body` text is written.

[`represented_element`](#syside.TextualRepresentation.represented_element "syside.TextualRepresentation.represented_element")

The `Element` that is represented by this `TextualRepresentation`.

Attributes defined in [`AnnotatingElement`](/v0.8.1/api/metamodel/KerML/AnnotatingElement.md "syside.AnnotatingElement"):

[`annotated_elements`](/v0.8.1/api/metamodel/KerML/AnnotatingElement.md "syside.AnnotatingElement.annotated_elements")

The `Elements` that are annotated by this `AnnotatingElement`. If `annotation` is not empty, these are the `annotatedElements` of the `annotations`. If `annotation` is empty, then it is the `owningNamespace` of the `AnnotatingElement`.

[`annotations`](/v0.8.1/api/metamodel/KerML/AnnotatingElement.md "syside.AnnotatingElement.annotations")

The `Annotations` that relate this `AnnotatingElement` to its `annotatedElements`. This includes the `owningAnnotatingRelationship` (if any) followed by all the `ownedAnnotatingRelationships`.

[`owned_annotating_relationships`](/v0.8.1/api/metamodel/KerML/AnnotatingElement.md "syside.AnnotatingElement.owned_annotating_relationships")

The `ownedRelationships` of this `AnnotatingElement` that are `Annotations`, for which this `AnnotatingElement` is the `annotatingElement`.

[`owning_annotating_relationship`](/v0.8.1/api/metamodel/KerML/AnnotatingElement.md "syside.AnnotatingElement.owning_annotating_relationship")

The `owningRelationship` of this `AnnotatingRelationship`, if it is an `Annotation`

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

The following table lists Syside specific attributes available for class [`TextualRepresentation`](#syside.TextualRepresentation "syside.TextualRepresentation"):

<div class="pst-scrollable-table-container">

|                                                                               |
| ----------------------------------------------------------------------------- |
| Python Attribute                                                              |
| [`STD`](#syside.TextualRepresentation.STD "syside.TextualRepresentation.STD") |

</div>

  - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">TextualRepresentation</span></span>[](#syside.TextualRepresentation "Link to this definition")
    
      - <span class="sig-name descname"><span class="pre">\_\_cpp\_name\_\_</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">'syside::sysml::TextualRepresentation'</span>*[](#syside.TextualRepresentation.__cpp_name__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">STD</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><span class="pre">type</span><span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.TextualRepresentation</span>](#syside.TextualRepresentation "syside.TextualRepresentation")<span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="p"><span class="pre">...</span></span><span class="p"><span class="pre">\]</span></span><span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">()</span>*[](#syside.TextualRepresentation.STD "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">language</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span>*[](#syside.TextualRepresentation.language "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">body</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span>*[](#syside.TextualRepresentation.body "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">represented\_element</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.Element</span>](/v0.8.1/api/metamodel/KerML/Element.md "syside.Element")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span>*[](#syside.TextualRepresentation.represented_element "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">annotations</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.ContainerView</span>](/v0.8.1/api/generated/syside.ContainerView.md "syside.ContainerView")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Annotation</span>](/v0.8.1/api/metamodel/KerML/Annotation.md "syside.Annotation")<span class="p"><span class="pre">\]</span></span>*[](#syside.TextualRepresentation.annotations "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">annotated\_elements</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.ContainerView</span>](/v0.8.1/api/generated/syside.ContainerView.md "syside.ContainerView")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Element</span>](/v0.8.1/api/metamodel/KerML/Element.md "syside.Element")<span class="p"><span class="pre">\]</span></span>*[](#syside.TextualRepresentation.annotated_elements "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned\_annotating\_relationships</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.ContainerView</span>](/v0.8.1/api/generated/syside.ContainerView.md "syside.ContainerView")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Annotation</span>](/v0.8.1/api/metamodel/KerML/Annotation.md "syside.Annotation")<span class="p"><span class="pre">\]</span></span>*[](#syside.TextualRepresentation.owned_annotating_relationships "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owning\_annotating\_relationship</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.Annotation</span>](/v0.8.1/api/metamodel/KerML/Annotation.md "syside.Annotation")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span>*[](#syside.TextualRepresentation.owning_annotating_relationship "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">about</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.Annotations</span>](/v0.8.1/api/generated/syside.Annotations.md "syside.Annotations")*[](#syside.TextualRepresentation.about "Link to this definition")
