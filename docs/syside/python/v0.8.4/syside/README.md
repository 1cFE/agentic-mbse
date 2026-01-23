<div id="module-syside" class="section">

<span id="syside"></span>

# syside<a href="#module-syside" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

**Native Syside module for Python.**

Internally, Syside uses <span class="pre">`snake_case`</span> for all non-type symbols, e.g. attributes and functions, whereas the specification and the Pilot implementation both use <span class="pre">`camelCase`</span> instead. <span class="pre">`snake_case`</span> was chosen because it integrates far better into Python - the programming language that Syside uses.

Additionally, Syside does not use multiple inheritance to implement the standard model and instead uses sum-types where appropriate (<span class="pre">`typing.Union`</span> in Python). This improves performance as methods and attributes can be inlined and are not required to be accessed through interfaces (no pointer chasing), reduces memory usage as unused members need not be stored (e.g. <span class="pre">`Relationship`</span> interface for <span class="pre">`Associations`</span>), and improves usability by allowing more flexible constraints on element types.

Usability is further improved by storing child elements in separate members based on their position in the textual syntax. This is in comparison to the Pilot implementation, which only uses two such members, <span class="pre">`ownedRelationship`</span> and <span class="pre">`ownedRelatedElement`</span>. Syside implementation allows direct access to most special members without resorting to filtering every time, improving performance. Moreover, modifying and inserting such members does not require potentially expensive reshuffling of children arrays.

Lastly, because textual source files may contain syntax errors, all model elements may return optional elements, even if the corresponding attribute in the specification expects a non-null element. This also allows elements to be default constructible.

**Additional Notes**

- For performance reasons, elements and their groups are stored as specific members in AST nodes based on their position in textual syntax which also makes mutation easier. Notably:

  - <span class="pre">`prefixes`</span> - group for metadata prefixes, prefixed with <span class="pre">`#`</span> in textual notation

  - <span class="pre">`heritage`</span> - type specializations and conjugations

  - <span class="pre">`type_relationships`</span> - non-specialization type relationships appearing after specialization part, including feature chaining

  - <span class="pre">`children`</span> - elements in the children block (in-between brackets <span class="pre">`{`</span> and <span class="pre">`}`</span>) in textual notation, and expression arguments

  - <span class="pre">`declared_ends`</span>, <span class="pre">`declared_messages`</span> - end features and messages before the children block. In the textual syntax they appear in the same position, hence in contrast to similar groups there are additional <span class="pre">`try_append`</span> and <span class="pre">`try_insert`</span> methods that return <span class="pre">`None`</span> without throwing if modification failed because the slot is already occupied by either ends or messages.

- Due to parser limitations, argument member references are parsed as argument members instead. This has little effect on analysis as intermediate <span class="pre">`FeatureReferenceExpression`</span> and <span class="pre">`OwningMembership`</span> are excluded from the expression tree.

- Elements can only be owned nodes in the same document to satisfy tree constraints, elements can be referenced by any appropriate element. Violating this constraint raises <span class="pre">`ValueError`</span>. Similarly, trying to steal ownership also raises <span class="pre">`ValueError`</span>.

- Relationship ends cannot generally be modified unless they are member elements, and only a few allow this dependent on the textual syntax (KerML only but there are currently no checks that models constructed are actually representable in chosen textual syntax beyond some simple checks during printing).

**Model Modifications**

Adding new owned or referenced <span class="pre">`Elements`</span> to a model can raise:

- <span class="pre">`TypeError`</span>:

  - if the relationship type is not allowed by the container/setter as this violates internal invariants.

  - if the element type is not allowed by the container/setter as this violates internal invariants.

  - if the element type is not allowed by the relationship as this violates internal invariants.

  - if the element is owned but the relationship instead only references related element to prevent orphan elements.

- <span class="pre">`ValueError`</span>:

  - if taking ownership of an element from another document as this violates internal invariants.

  - if stealing ownership of the element as there is no good default behaviour on what should happen, remove the element from the model first before trying to re-parent it.

- <span class="pre">`RuntimeError`</span>:

  - if the parent <span class="pre">`Element`</span> has been removed from the model. This can be fixed by adding the <span class="pre">`Element`</span> back into the model as an owned element.

<div id="index" class="section">

## <span class="nerd-font"></span> Index<a href="#index" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

<span class="sd-summary-text"><span class="nerd-font"></span> **Submodules** <a href="#syside-submodules-table" class="reference internal"><span class="std std-ref"></span></a></span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |
|----|----|----|
| <a href="/python/v0.8.4/syside/debug//README.md" class="reference internal" title="syside.debug"><span class="pre"><code class="sourceCode python">debug</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/experimental//README.md" class="reference internal" title="syside.experimental"><span class="pre"><code class="sourceCode python">experimental</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">Labs</span> | Umbrella submodule for all experimental implementations. |
| <a href="/python/v0.8.4/syside/gc//README.md" class="reference internal" title="syside.gc"><span class="pre"><code class="sourceCode python">gc</code></span></a> |  | Internal GC interface. Currently only Documents are collected by the internal garbage collector. |
| <a href="/python/v0.8.4/syside/ide//README.md" class="reference internal" title="syside.ide"><span class="pre"><code class="sourceCode python">ide</code></span></a> |  | Submodule for IDE related functions. |
| <a href="/python/v0.8.4/syside/json//README.md" class="reference internal" title="syside.json"><span class="pre"><code class="sourceCode python">json</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">Labs</span> | Convenience module intending to match the standard library <span class="pre">`json`</span> module. |
| <a href="/python/v0.8.4/syside/version//README.md" class="reference internal" title="syside.version"><span class="pre"><code class="sourceCode python">version</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/preview//README.md" class="reference internal" title="syside.preview"><span class="pre"><code class="sourceCode python">preview</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">Labs</span> | Module implementing various proposals for how to make the Syside API more convenient and easier to pick up. |

</div>

</div>

<span class="sd-summary-text"><span class="nerd-font"></span> **Classes** <a href="#syside-classes-table" class="reference internal"><span class="std std-ref"></span></a></span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |
|----|----|----|
| <a href="/python/v0.8.4/syside/AcceptActionUsage.md" class="reference internal" title="syside.AcceptActionUsage"><span class="pre"><code class="sourceCode python">AcceptActionUsage</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`AcceptActionUsage`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/ActionDefinition.md" class="reference internal" title="syside.ActionDefinition"><span class="pre"><code class="sourceCode python">ActionDefinition</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`ActionDefinition`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/ActionParameterAccessor.md" class="reference internal" title="syside.ActionParameterAccessor"><span class="pre"><code class="sourceCode python">ActionParameterAccessor</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/ActionUsage.md" class="reference internal" title="syside.ActionUsage"><span class="pre"><code class="sourceCode python">ActionUsage</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`ActionUsage`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/ActorMembership.md" class="reference internal" title="syside.ActorMembership"><span class="pre"><code class="sourceCode python">ActorMembership</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`ActorMembership`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/AllocationDefinition.md" class="reference internal" title="syside.AllocationDefinition"><span class="pre"><code class="sourceCode python">AllocationDefinition</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`AllocationDefinition`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/AllocationUsage.md" class="reference internal" title="syside.AllocationUsage"><span class="pre"><code class="sourceCode python">AllocationUsage</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`AllocationUsage`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/AnalysisCaseDefinition.md" class="reference internal" title="syside.AnalysisCaseDefinition"><span class="pre"><code class="sourceCode python">AnalysisCaseDefinition</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`AnalysisCaseDefinition`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/AnalysisCaseUsage.md" class="reference internal" title="syside.AnalysisCaseUsage"><span class="pre"><code class="sourceCode python">AnalysisCaseUsage</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`AnalysisCaseUsage`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/AnnotatingElement.md" class="reference internal" title="syside.AnnotatingElement"><span class="pre"><code class="sourceCode python">AnnotatingElement</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`AnnotatingElement`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/Annotation.md" class="reference internal" title="syside.Annotation"><span class="pre"><code class="sourceCode python">Annotation</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`Annotation`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/Annotations.md" class="reference internal" title="syside.Annotations"><span class="pre"><code class="sourceCode python">Annotations</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/ArgumentsAccessor.md" class="reference internal" title="syside.ArgumentsAccessor"><span class="pre"><code class="sourceCode python">ArgumentsAccessor</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/AssertConstraintUsage.md" class="reference internal" title="syside.AssertConstraintUsage"><span class="pre"><code class="sourceCode python">AssertConstraintUsage</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`AssertConstraintUsage`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/AssignmentActionUsage.md" class="reference internal" title="syside.AssignmentActionUsage"><span class="pre"><code class="sourceCode python">AssignmentActionUsage</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`AssignmentActionUsage`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/Association.md" class="reference internal" title="syside.Association"><span class="pre"><code class="sourceCode python">Association</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`Association`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/AssociationStructure.md" class="reference internal" title="syside.AssociationStructure"><span class="pre"><code class="sourceCode python">AssociationStructure</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`AssociationStructure`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/AstNode.md" class="reference internal" title="syside.AstNode"><span class="pre"><code class="sourceCode python">AstNode</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/AttributeDefinition.md" class="reference internal" title="syside.AttributeDefinition"><span class="pre"><code class="sourceCode python">AttributeDefinition</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`AttributeDefinition`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/AttributeMap.md" class="reference internal" title="syside.AttributeMap"><span class="pre"><code class="sourceCode python">AttributeMap</code></span></a> |  | Internal opaque type for deserialization attribute mapping |
| <a href="/python/v0.8.4/syside/AttributeUsage.md" class="reference internal" title="syside.AttributeUsage"><span class="pre"><code class="sourceCode python">AttributeUsage</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`AttributeUsage`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/BaseModel.md" class="reference internal" title="syside.BaseModel"><span class="pre"><code class="sourceCode python">BaseModel</code></span></a> |  | A SysMLv2 model represented using abstract syntax. |
| <a href="/python/v0.8.4/syside/BasicDocument.md" class="reference internal" title="syside.BasicDocument"><span class="pre"><code class="sourceCode python">BasicDocument</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/Behavior.md" class="reference internal" title="syside.Behavior"><span class="pre"><code class="sourceCode python">Behavior</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`Behavior`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/BindingConnector.md" class="reference internal" title="syside.BindingConnector"><span class="pre"><code class="sourceCode python">BindingConnector</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`BindingConnector`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/BindingConnectorAsUsage.md" class="reference internal" title="syside.BindingConnectorAsUsage"><span class="pre"><code class="sourceCode python">BindingConnectorAsUsage</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`BindingConnectorAsUsage`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/BooleanExpression.md" class="reference internal" title="syside.BooleanExpression"><span class="pre"><code class="sourceCode python">BooleanExpression</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`BooleanExpression`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/BoundMetaclass.md" class="reference internal" title="syside.BoundMetaclass"><span class="pre"><code class="sourceCode python">BoundMetaclass</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/CalculationDefinition.md" class="reference internal" title="syside.CalculationDefinition"><span class="pre"><code class="sourceCode python">CalculationDefinition</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`CalculationDefinition`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/CalculationUsage.md" class="reference internal" title="syside.CalculationUsage"><span class="pre"><code class="sourceCode python">CalculationUsage</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`CalculationUsage`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/CaseDefinition.md" class="reference internal" title="syside.CaseDefinition"><span class="pre"><code class="sourceCode python">CaseDefinition</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`CaseDefinition`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/CaseUsage.md" class="reference internal" title="syside.CaseUsage"><span class="pre"><code class="sourceCode python">CaseUsage</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`CaseUsage`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/ChainedChildrenNodes.md" class="reference internal" title="syside.ChainedChildrenNodes"><span class="pre"><code class="sourceCode python">ChainedChildrenNodes</code></span></a> |  | Container that stores a vector of children nodes that may own feature chainings. |
| <a href="/python/v0.8.4/syside/ChainedFeatureMemberAccessor.md" class="reference internal" title="syside.ChainedFeatureMemberAccessor"><span class="pre"><code class="sourceCode python">ChainedFeatureMemberAccessor</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/ChainedFeatureReference.md" class="reference internal" title="syside.ChainedFeatureReference"><span class="pre"><code class="sourceCode python">ChainedFeatureReference</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/ChainedMemberAccessor.md" class="reference internal" title="syside.ChainedMemberAccessor"><span class="pre"><code class="sourceCode python">ChainedMemberAccessor</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/ChainedReferenceAccessor.md" class="reference internal" title="syside.ChainedReferenceAccessor"><span class="pre"><code class="sourceCode python">ChainedReferenceAccessor</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/ChainedTypeReference.md" class="reference internal" title="syside.ChainedTypeReference"><span class="pre"><code class="sourceCode python">ChainedTypeReference</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/ChildrenNodes.md" class="reference internal" title="syside.ChildrenNodes"><span class="pre"><code class="sourceCode python">ChildrenNodes</code></span></a> |  | Container that stores a vector of children nodes. |
| <a href="/python/v0.8.4/syside/ChildrenNodesView.md" class="reference internal" title="syside.ChildrenNodesView"><span class="pre"><code class="sourceCode python">ChildrenNodesView</code></span></a> |  | A view to a container of children nodes. |
| <a href="/python/v0.8.4/syside/Class.md" class="reference internal" title="syside.Class"><span class="pre"><code class="sourceCode python">Class</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`Class`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/Classifier.md" class="reference internal" title="syside.Classifier"><span class="pre"><code class="sourceCode python">Classifier</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`Classifier`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/ClassifierReference.md" class="reference internal" title="syside.ClassifierReference"><span class="pre"><code class="sourceCode python">ClassifierReference</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/CodeDescription.md" class="reference internal" title="syside.CodeDescription"><span class="pre"><code class="sourceCode python">CodeDescription</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/CollectExpression.md" class="reference internal" title="syside.CollectExpression"><span class="pre"><code class="sourceCode python">CollectExpression</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`CollectExpression`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/Comment.md" class="reference internal" title="syside.Comment"><span class="pre"><code class="sourceCode python">Comment</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`Comment`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/CompilationReport.md" class="reference internal" title="syside.CompilationReport"><span class="pre"><code class="sourceCode python">CompilationReport</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/Compiler.md" class="reference internal" title="syside.Compiler"><span class="pre"><code class="sourceCode python">Compiler</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/ConcernDefinition.md" class="reference internal" title="syside.ConcernDefinition"><span class="pre"><code class="sourceCode python">ConcernDefinition</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`ConcernDefinition`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/ConcernUsage.md" class="reference internal" title="syside.ConcernUsage"><span class="pre"><code class="sourceCode python">ConcernUsage</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`ConcernUsage`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/ConjugatedPortDefinition.md" class="reference internal" title="syside.ConjugatedPortDefinition"><span class="pre"><code class="sourceCode python">ConjugatedPortDefinition</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`ConjugatedPortDefinition`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/ConjugatedPortTyping.md" class="reference internal" title="syside.ConjugatedPortTyping"><span class="pre"><code class="sourceCode python">ConjugatedPortTyping</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`ConjugatedPortTyping`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/Conjugation.md" class="reference internal" title="syside.Conjugation"><span class="pre"><code class="sourceCode python">Conjugation</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`Conjugation`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/ConnectionDefinition.md" class="reference internal" title="syside.ConnectionDefinition"><span class="pre"><code class="sourceCode python">ConnectionDefinition</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`ConnectionDefinition`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/ConnectionUsage.md" class="reference internal" title="syside.ConnectionUsage"><span class="pre"><code class="sourceCode python">ConnectionUsage</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`ConnectionUsage`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/Connector.md" class="reference internal" title="syside.Connector"><span class="pre"><code class="sourceCode python">Connector</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`Connector`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/ConnectorAsUsage.md" class="reference internal" title="syside.ConnectorAsUsage"><span class="pre"><code class="sourceCode python">ConnectorAsUsage</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`ConnectorAsUsage`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/ConnectorAsUsageEnds.md" class="reference internal" title="syside.ConnectorAsUsageEnds"><span class="pre"><code class="sourceCode python">ConnectorAsUsageEnds</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/ConnectorEnds.md" class="reference internal" title="syside.ConnectorEnds"><span class="pre"><code class="sourceCode python">ConnectorEnds</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/ConnectorEndsAccessor.md" class="reference internal" title="syside.ConnectorEndsAccessor"><span class="pre"><code class="sourceCode python">ConnectorEndsAccessor</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/ConstraintDefinition.md" class="reference internal" title="syside.ConstraintDefinition"><span class="pre"><code class="sourceCode python">ConstraintDefinition</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`ConstraintDefinition`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/ConstraintUsage.md" class="reference internal" title="syside.ConstraintUsage"><span class="pre"><code class="sourceCode python">ConstraintUsage</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`ConstraintUsage`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/ConstructorExpression.md" class="reference internal" title="syside.ConstructorExpression"><span class="pre"><code class="sourceCode python">ConstructorExpression</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`ConstructorExpression`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/ContainerView.md" class="reference internal" title="syside.ContainerView"><span class="pre"><code class="sourceCode python">ContainerView</code></span></a> |  | An immutable view into a native random-access container. Implements Sequence protocol. |
| <a href="/python/v0.8.4/syside/ControlNode.md" class="reference internal" title="syside.ControlNode"><span class="pre"><code class="sourceCode python">ControlNode</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`ControlNode`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/CrossSubsetting.md" class="reference internal" title="syside.CrossSubsetting"><span class="pre"><code class="sourceCode python">CrossSubsetting</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`CrossSubsetting`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/CstNode.md" class="reference internal" title="syside.CstNode"><span class="pre"><code class="sourceCode python">CstNode</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/DataType.md" class="reference internal" title="syside.DataType"><span class="pre"><code class="sourceCode python">DataType</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`DataType`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/DecisionNode.md" class="reference internal" title="syside.DecisionNode"><span class="pre"><code class="sourceCode python">DecisionNode</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`DecisionNode`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/Definition.md" class="reference internal" title="syside.Definition"><span class="pre"><code class="sourceCode python">Definition</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`Definition`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/Dependency.md" class="reference internal" title="syside.Dependency"><span class="pre"><code class="sourceCode python">Dependency</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`Dependency`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/DependencyEnds.md" class="reference internal" title="syside.DependencyEnds"><span class="pre"><code class="sourceCode python">DependencyEnds</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/DependencyPrefixes.md" class="reference internal" title="syside.DependencyPrefixes"><span class="pre"><code class="sourceCode python">DependencyPrefixes</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/DeserializedModel.md" class="reference internal" title="syside.DeserializedModel"><span class="pre"><code class="sourceCode python">DeserializedModel</code></span></a> |  | The model as it was deserialized, with references potentially unresolved. |
| <a href="/python/v0.8.4/syside/Deserializer.md" class="reference internal" title="syside.Deserializer"><span class="pre"><code class="sourceCode python">Deserializer</code></span></a> |  | Deserializer for SysML models. The actual deserialization input depends on used <span class="pre">`Reader`</span>. |
| <a href="/python/v0.8.4/syside/Diagnostic.md" class="reference internal" title="syside.Diagnostic"><span class="pre"><code class="sourceCode python">Diagnostic</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/DiagnosticContext.md" class="reference internal" title="syside.DiagnosticContext"><span class="pre"><code class="sourceCode python">DiagnosticContext</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/DiagnosticFormatOptions.md" class="reference internal" title="syside.DiagnosticFormatOptions"><span class="pre"><code class="sourceCode python">DiagnosticFormatOptions</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/DiagnosticMessage.md" class="reference internal" title="syside.DiagnosticMessage"><span class="pre"><code class="sourceCode python">DiagnosticMessage</code></span></a> |  | A diagnostic providing information about a model. |
| <a href="/python/v0.8.4/syside/DiagnosticRelatedInformation.md" class="reference internal" title="syside.DiagnosticRelatedInformation"><span class="pre"><code class="sourceCode python">DiagnosticRelatedInformation</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/DiagnosticResults.md" class="reference internal" title="syside.DiagnosticResults"><span class="pre"><code class="sourceCode python">DiagnosticResults</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/Diagnostics.md" class="reference internal" title="syside.Diagnostics"><span class="pre"><code class="sourceCode python">Diagnostics</code></span></a> |  | All model diagnostics. |
| <a href="/python/v0.8.4/syside/Differencing.md" class="reference internal" title="syside.Differencing"><span class="pre"><code class="sourceCode python">Differencing</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`Differencing`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/Disjoining.md" class="reference internal" title="syside.Disjoining"><span class="pre"><code class="sourceCode python">Disjoining</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`Disjoining`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/Document.md" class="reference internal" title="syside.Document"><span class="pre"><code class="sourceCode python">Document</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/DocumentID.md" class="reference internal" title="syside.DocumentID"><span class="pre"><code class="sourceCode python">DocumentID</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/DocumentOptions.md" class="reference internal" title="syside.DocumentOptions"><span class="pre"><code class="sourceCode python">DocumentOptions</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/DocumentSegment.md" class="reference internal" title="syside.DocumentSegment"><span class="pre"><code class="sourceCode python">DocumentSegment</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/DocumentTimes.md" class="reference internal" title="syside.DocumentTimes"><span class="pre"><code class="sourceCode python">DocumentTimes</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/DocumentVersion.md" class="reference internal" title="syside.DocumentVersion"><span class="pre"><code class="sourceCode python">DocumentVersion</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/Documentation.md" class="reference internal" title="syside.Documentation"><span class="pre"><code class="sourceCode python">Documentation</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`Documentation`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/EffectAccessor.md" class="reference internal" title="syside.EffectAccessor"><span class="pre"><code class="sourceCode python">EffectAccessor</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element"><span class="pre"><code class="sourceCode python">Element</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`Element`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/ElementAccessor.md" class="reference internal" title="syside.ElementAccessor"><span class="pre"><code class="sourceCode python">ElementAccessor</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/ElementFilterMembership.md" class="reference internal" title="syside.ElementFilterMembership"><span class="pre"><code class="sourceCode python">ElementFilterMembership</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`ElementFilterMembership`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/EncodingOpts.md" class="reference internal" title="syside.EncodingOpts"><span class="pre"><code class="sourceCode python">EncodingOpts</code></span></a> |  | Percent-encoding options |
| <a href="/python/v0.8.4/syside/EndFeatureMembership.md" class="reference internal" title="syside.EndFeatureMembership"><span class="pre"><code class="sourceCode python">EndFeatureMembership</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`EndFeatureMembership`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/EnumerationDefinition.md" class="reference internal" title="syside.EnumerationDefinition"><span class="pre"><code class="sourceCode python">EnumerationDefinition</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`EnumerationDefinition`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/EnumerationUsage.md" class="reference internal" title="syside.EnumerationUsage"><span class="pre"><code class="sourceCode python">EnumerationUsage</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`EnumerationUsage`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/Environment.md" class="reference internal" title="syside.Environment"><span class="pre"><code class="sourceCode python">Environment</code></span></a> |  | Standard library environment for use with user models. |
| <a href="/python/v0.8.4/syside/EventOccurrenceUsage.md" class="reference internal" title="syside.EventOccurrenceUsage"><span class="pre"><code class="sourceCode python">EventOccurrenceUsage</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`EventOccurrenceUsage`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/ExecutionResult.md" class="reference internal" title="syside.ExecutionResult"><span class="pre"><code class="sourceCode python">ExecutionResult</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/Executor.md" class="reference internal" title="syside.Executor"><span class="pre"><code class="sourceCode python">Executor</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/ExhibitStateUsage.md" class="reference internal" title="syside.ExhibitStateUsage"><span class="pre"><code class="sourceCode python">ExhibitStateUsage</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`ExhibitStateUsage`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/Expose.md" class="reference internal" title="syside.Expose"><span class="pre"><code class="sourceCode python">Expose</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`Expose`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/Expression.md" class="reference internal" title="syside.Expression"><span class="pre"><code class="sourceCode python">Expression</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`Expression`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/ExpressionParameterAccessor.md" class="reference internal" title="syside.ExpressionParameterAccessor"><span class="pre"><code class="sourceCode python">ExpressionParameterAccessor</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature"><span class="pre"><code class="sourceCode python">Feature</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`Feature`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/FeatureChainExpression.md" class="reference internal" title="syside.FeatureChainExpression"><span class="pre"><code class="sourceCode python">FeatureChainExpression</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`FeatureChainExpression`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/FeatureChaining.md" class="reference internal" title="syside.FeatureChaining"><span class="pre"><code class="sourceCode python">FeatureChaining</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`FeatureChaining`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/FeatureInverting.md" class="reference internal" title="syside.FeatureInverting"><span class="pre"><code class="sourceCode python">FeatureInverting</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`FeatureInverting`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/FeatureMembership.md" class="reference internal" title="syside.FeatureMembership"><span class="pre"><code class="sourceCode python">FeatureMembership</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`FeatureMembership`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/FeatureReference.md" class="reference internal" title="syside.FeatureReference"><span class="pre"><code class="sourceCode python">FeatureReference</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/FeatureReferenceExpression.md" class="reference internal" title="syside.FeatureReferenceExpression"><span class="pre"><code class="sourceCode python">FeatureReferenceExpression</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`FeatureReferenceExpression`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/FeatureTyping.md" class="reference internal" title="syside.FeatureTyping"><span class="pre"><code class="sourceCode python">FeatureTyping</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`FeatureTyping`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/FeatureValue.md" class="reference internal" title="syside.FeatureValue"><span class="pre"><code class="sourceCode python">FeatureValue</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`FeatureValue`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/FeatureValueAccessor.md" class="reference internal" title="syside.FeatureValueAccessor"><span class="pre"><code class="sourceCode python">FeatureValueAccessor</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/FieldId.md" class="reference internal" title="syside.FieldId"><span class="pre"><code class="sourceCode python">FieldId</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/Flow.md" class="reference internal" title="syside.Flow"><span class="pre"><code class="sourceCode python">Flow</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`Flow`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/FlowDefinition.md" class="reference internal" title="syside.FlowDefinition"><span class="pre"><code class="sourceCode python">FlowDefinition</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`FlowDefinition`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/FlowEnd.md" class="reference internal" title="syside.FlowEnd"><span class="pre"><code class="sourceCode python">FlowEnd</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`FlowEnd`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/FlowUsage.md" class="reference internal" title="syside.FlowUsage"><span class="pre"><code class="sourceCode python">FlowUsage</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`FlowUsage`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/ForLoopActionUsage.md" class="reference internal" title="syside.ForLoopActionUsage"><span class="pre"><code class="sourceCode python">ForLoopActionUsage</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`ForLoopActionUsage`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/ForkNode.md" class="reference internal" title="syside.ForkNode"><span class="pre"><code class="sourceCode python">ForkNode</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`ForkNode`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions"><span class="pre"><code class="sourceCode python">FormatOptions</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/FormatPreserved.md" class="reference internal" title="syside.FormatPreserved"><span class="pre"><code class="sourceCode python">FormatPreserved</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/FramedConcernMembership.md" class="reference internal" title="syside.FramedConcernMembership"><span class="pre"><code class="sourceCode python">FramedConcernMembership</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`FramedConcernMembership`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/Function.md" class="reference internal" title="syside.Function"><span class="pre"><code class="sourceCode python">Function</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`Function`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/GuardAccessor.md" class="reference internal" title="syside.GuardAccessor"><span class="pre"><code class="sourceCode python">GuardAccessor</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/Heritage.md" class="reference internal" title="syside.Heritage"><span class="pre"><code class="sourceCode python">Heritage</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/IOSchedule.md" class="reference internal" title="syside.IOSchedule"><span class="pre"><code class="sourceCode python">IOSchedule</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/IPv4Address.md" class="reference internal" title="syside.IPv4Address"><span class="pre"><code class="sourceCode python">IPv4Address</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/IPv6Address.md" class="reference internal" title="syside.IPv6Address"><span class="pre"><code class="sourceCode python">IPv6Address</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/IdMap.md" class="reference internal" title="syside.IdMap"><span class="pre"><code class="sourceCode python">IdMap</code></span></a> |  | <span class="pre">`DeserializedModel`</span> compatible mapping for elements. This will typically be used for linking pending references: |
| <a href="/python/v0.8.4/syside/IfActionUsage.md" class="reference internal" title="syside.IfActionUsage"><span class="pre"><code class="sourceCode python">IfActionUsage</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`IfActionUsage`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/Import.md" class="reference internal" title="syside.Import"><span class="pre"><code class="sourceCode python">Import</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`Import`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/IncludeUseCaseUsage.md" class="reference internal" title="syside.IncludeUseCaseUsage"><span class="pre"><code class="sourceCode python">IncludeUseCaseUsage</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`IncludeUseCaseUsage`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/IndexExpression.md" class="reference internal" title="syside.IndexExpression"><span class="pre"><code class="sourceCode python">IndexExpression</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`IndexExpression`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/IndexedSymbol.md" class="reference internal" title="syside.IndexedSymbol"><span class="pre"><code class="sourceCode python">IndexedSymbol</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/Infinity.md" class="reference internal" title="syside.Infinity"><span class="pre"><code class="sourceCode python">Infinity</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/InstantiationExpression.md" class="reference internal" title="syside.InstantiationExpression"><span class="pre"><code class="sourceCode python">InstantiationExpression</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`InstantiationExpression`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/Interaction.md" class="reference internal" title="syside.Interaction"><span class="pre"><code class="sourceCode python">Interaction</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`Interaction`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/InterfaceDefinition.md" class="reference internal" title="syside.InterfaceDefinition"><span class="pre"><code class="sourceCode python">InterfaceDefinition</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`InterfaceDefinition`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/InterfaceUsage.md" class="reference internal" title="syside.InterfaceUsage"><span class="pre"><code class="sourceCode python">InterfaceUsage</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`InterfaceUsage`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/Intersecting.md" class="reference internal" title="syside.Intersecting"><span class="pre"><code class="sourceCode python">Intersecting</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`Intersecting`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/Invariant.md" class="reference internal" title="syside.Invariant"><span class="pre"><code class="sourceCode python">Invariant</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`Invariant`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/InvocationExpression.md" class="reference internal" title="syside.InvocationExpression"><span class="pre"><code class="sourceCode python">InvocationExpression</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`InvocationExpression`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/ItemDefinition.md" class="reference internal" title="syside.ItemDefinition"><span class="pre"><code class="sourceCode python">ItemDefinition</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`ItemDefinition`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/ItemUsage.md" class="reference internal" title="syside.ItemUsage"><span class="pre"><code class="sourceCode python">ItemUsage</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`ItemUsage`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/JoinNode.md" class="reference internal" title="syside.JoinNode"><span class="pre"><code class="sourceCode python">JoinNode</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`JoinNode`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/JsonReader.md" class="reference internal" title="syside.JsonReader"><span class="pre"><code class="sourceCode python">JsonReader</code></span></a> |  | Unbound reader for JSON deserialization |
| <a href="/python/v0.8.4/syside/JsonStringOptions.md" class="reference internal" title="syside.JsonStringOptions"><span class="pre"><code class="sourceCode python">JsonStringOptions</code></span></a> |  | Options for serialization writer to JSON strings |
| <a href="/python/v0.8.4/syside/JsonStringWriter.md" class="reference internal" title="syside.JsonStringWriter"><span class="pre"><code class="sourceCode python">JsonStringWriter</code></span></a> |  | Serialization writer that outputs JSON string |
| <a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre"><code class="sourceCode python">LazyIterator</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/LibraryID.md" class="reference internal" title="syside.LibraryID"><span class="pre"><code class="sourceCode python">LibraryID</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/LibraryPackage.md" class="reference internal" title="syside.LibraryPackage"><span class="pre"><code class="sourceCode python">LibraryPackage</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`LibraryPackage`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/LiteralBoolean.md" class="reference internal" title="syside.LiteralBoolean"><span class="pre"><code class="sourceCode python">LiteralBoolean</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`LiteralBoolean`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/LiteralExpression.md" class="reference internal" title="syside.LiteralExpression"><span class="pre"><code class="sourceCode python">LiteralExpression</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`LiteralExpression`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/LiteralInfinity.md" class="reference internal" title="syside.LiteralInfinity"><span class="pre"><code class="sourceCode python">LiteralInfinity</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`LiteralInfinity`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/LiteralInteger.md" class="reference internal" title="syside.LiteralInteger"><span class="pre"><code class="sourceCode python">LiteralInteger</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`LiteralInteger`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/LiteralRational.md" class="reference internal" title="syside.LiteralRational"><span class="pre"><code class="sourceCode python">LiteralRational</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`LiteralRational`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/LiteralString.md" class="reference internal" title="syside.LiteralString"><span class="pre"><code class="sourceCode python">LiteralString</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`LiteralString`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/LoopActionUsage.md" class="reference internal" title="syside.LoopActionUsage"><span class="pre"><code class="sourceCode python">LoopActionUsage</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`LoopActionUsage`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/MemberAccessor.md" class="reference internal" title="syside.MemberAccessor"><span class="pre"><code class="sourceCode python">MemberAccessor</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/Membership.md" class="reference internal" title="syside.Membership"><span class="pre"><code class="sourceCode python">Membership</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`Membership`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/MembershipExpose.md" class="reference internal" title="syside.MembershipExpose"><span class="pre"><code class="sourceCode python">MembershipExpose</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`MembershipExpose`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/MembershipImport.md" class="reference internal" title="syside.MembershipImport"><span class="pre"><code class="sourceCode python">MembershipImport</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`MembershipImport`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/MergeNode.md" class="reference internal" title="syside.MergeNode"><span class="pre"><code class="sourceCode python">MergeNode</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`MergeNode`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/Messages.md" class="reference internal" title="syside.Messages"><span class="pre"><code class="sourceCode python">Messages</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/Metaclass.md" class="reference internal" title="syside.Metaclass"><span class="pre"><code class="sourceCode python">Metaclass</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`Metaclass`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/MetadataAccessExpression.md" class="reference internal" title="syside.MetadataAccessExpression"><span class="pre"><code class="sourceCode python">MetadataAccessExpression</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`MetadataAccessExpression`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/MetadataDefinition.md" class="reference internal" title="syside.MetadataDefinition"><span class="pre"><code class="sourceCode python">MetadataDefinition</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`MetadataDefinition`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/MetadataFeature.md" class="reference internal" title="syside.MetadataFeature"><span class="pre"><code class="sourceCode python">MetadataFeature</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`MetadataFeature`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/MetadataUsage.md" class="reference internal" title="syside.MetadataUsage"><span class="pre"><code class="sourceCode python">MetadataUsage</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`MetadataUsage`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/Model.md" class="reference internal" title="syside.Model"><span class="pre"><code class="sourceCode python">Model</code></span></a> |  | A SysMLv2 model represented using abstract syntax. |
| <a href="/python/v0.8.4/syside/ModelError.md" class="reference internal" title="syside.ModelError"><span class="pre"><code class="sourceCode python">ModelError</code></span></a> |  | An exception thrown when model contains errors. |
| <a href="/python/v0.8.4/syside/ModelPrinter.md" class="reference internal" title="syside.ModelPrinter"><span class="pre"><code class="sourceCode python">ModelPrinter</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/Multiplicity.md" class="reference internal" title="syside.Multiplicity"><span class="pre"><code class="sourceCode python">Multiplicity</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`Multiplicity`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/MultiplicityRange.md" class="reference internal" title="syside.MultiplicityRange"><span class="pre"><code class="sourceCode python">MultiplicityRange</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`MultiplicityRange`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/Namespace.md" class="reference internal" title="syside.Namespace"><span class="pre"><code class="sourceCode python">Namespace</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`Namespace`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/NamespaceBody.md" class="reference internal" title="syside.NamespaceBody"><span class="pre"><code class="sourceCode python">NamespaceBody</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/NamespaceExpose.md" class="reference internal" title="syside.NamespaceExpose"><span class="pre"><code class="sourceCode python">NamespaceExpose</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`NamespaceExpose`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/NamespaceImport.md" class="reference internal" title="syside.NamespaceImport"><span class="pre"><code class="sourceCode python">NamespaceImport</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`NamespaceImport`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/NamespacePrefixes.md" class="reference internal" title="syside.NamespacePrefixes"><span class="pre"><code class="sourceCode python">NamespacePrefixes</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/NullExpression.md" class="reference internal" title="syside.NullExpression"><span class="pre"><code class="sourceCode python">NullExpression</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`NullExpression`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/ObjectiveMembership.md" class="reference internal" title="syside.ObjectiveMembership"><span class="pre"><code class="sourceCode python">ObjectiveMembership</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`ObjectiveMembership`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/OccurrenceDefinition.md" class="reference internal" title="syside.OccurrenceDefinition"><span class="pre"><code class="sourceCode python">OccurrenceDefinition</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`OccurrenceDefinition`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/OccurrenceUsage.md" class="reference internal" title="syside.OccurrenceUsage"><span class="pre"><code class="sourceCode python">OccurrenceUsage</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`OccurrenceUsage`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/OperatorExpression.md" class="reference internal" title="syside.OperatorExpression"><span class="pre"><code class="sourceCode python">OperatorExpression</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`OperatorExpression`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/OwnedChildrenNodes.md" class="reference internal" title="syside.OwnedChildrenNodes"><span class="pre"><code class="sourceCode python">OwnedChildrenNodes</code></span></a> |  | Container that stores a vector of potentially owned children nodes. |
| <a href="/python/v0.8.4/syside/OwnedExpressionAccessor.md" class="reference internal" title="syside.OwnedExpressionAccessor"><span class="pre"><code class="sourceCode python">OwnedExpressionAccessor</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/OwnedFeatureAccessor.md" class="reference internal" title="syside.OwnedFeatureAccessor"><span class="pre"><code class="sourceCode python">OwnedFeatureAccessor</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/OwnedMemberAccessor.md" class="reference internal" title="syside.OwnedMemberAccessor"><span class="pre"><code class="sourceCode python">OwnedMemberAccessor</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/OwnedMultiplicityAccessor.md" class="reference internal" title="syside.OwnedMultiplicityAccessor"><span class="pre"><code class="sourceCode python">OwnedMultiplicityAccessor</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/OwnedSuccessionAccessor.md" class="reference internal" title="syside.OwnedSuccessionAccessor"><span class="pre"><code class="sourceCode python">OwnedSuccessionAccessor</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/OwningMembership.md" class="reference internal" title="syside.OwningMembership"><span class="pre"><code class="sourceCode python">OwningMembership</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`OwningMembership`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/Package.md" class="reference internal" title="syside.Package"><span class="pre"><code class="sourceCode python">Package</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`Package`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/ParameterAccessor.md" class="reference internal" title="syside.ParameterAccessor"><span class="pre"><code class="sourceCode python">ParameterAccessor</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/ParameterMembership.md" class="reference internal" title="syside.ParameterMembership"><span class="pre"><code class="sourceCode python">ParameterMembership</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`ParameterMembership`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/PartDefinition.md" class="reference internal" title="syside.PartDefinition"><span class="pre"><code class="sourceCode python">PartDefinition</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`PartDefinition`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/PartUsage.md" class="reference internal" title="syside.PartUsage"><span class="pre"><code class="sourceCode python">PartUsage</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`PartUsage`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/PartialTextDocumentData.md" class="reference internal" title="syside.PartialTextDocumentData"><span class="pre"><code class="sourceCode python">PartialTextDocumentData</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/Path.md" class="reference internal" title="syside.Path"><span class="pre"><code class="sourceCode python">Path</code></span></a> |  | A sequence of path segments that stringifies with unrestricted names as needed. Similar to <span class="pre">`QualifiedName`</span> but may contain indices to unnamed elements, that are printed literally with <span class="pre">`/`</span> separator instead. |
| <a href="/python/v0.8.4/syside/PayloadFeature.md" class="reference internal" title="syside.PayloadFeature"><span class="pre"><code class="sourceCode python">PayloadFeature</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`PayloadFeature`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/PayloadFeatureAccessor.md" class="reference internal" title="syside.PayloadFeatureAccessor"><span class="pre"><code class="sourceCode python">PayloadFeatureAccessor</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/PendingReference.md" class="reference internal" title="syside.PendingReference"><span class="pre"><code class="sourceCode python">PendingReference</code></span></a> |  | Reference that has yet to be linked. |
| <a href="/python/v0.8.4/syside/PerformActionUsage.md" class="reference internal" title="syside.PerformActionUsage"><span class="pre"><code class="sourceCode python">PerformActionUsage</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`PerformActionUsage`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/Pipeline.md" class="reference internal" title="syside.Pipeline"><span class="pre"><code class="sourceCode python">Pipeline</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/PipelineOptions.md" class="reference internal" title="syside.PipelineOptions"><span class="pre"><code class="sourceCode python">PipelineOptions</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/PortConjugation.md" class="reference internal" title="syside.PortConjugation"><span class="pre"><code class="sourceCode python">PortConjugation</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`PortConjugation`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/PortDefinition.md" class="reference internal" title="syside.PortDefinition"><span class="pre"><code class="sourceCode python">PortDefinition</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`PortDefinition`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/PortUsage.md" class="reference internal" title="syside.PortUsage"><span class="pre"><code class="sourceCode python">PortUsage</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`PortUsage`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/PositionUtf16.md" class="reference internal" title="syside.PositionUtf16"><span class="pre"><code class="sourceCode python">PositionUtf16</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/PositionUtf32.md" class="reference internal" title="syside.PositionUtf32"><span class="pre"><code class="sourceCode python">PositionUtf32</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/PositionUtf8.md" class="reference internal" title="syside.PositionUtf8"><span class="pre"><code class="sourceCode python">PositionUtf8</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/Predicate.md" class="reference internal" title="syside.Predicate"><span class="pre"><code class="sourceCode python">Predicate</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`Predicate`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/PrinterConfig.md" class="reference internal" title="syside.PrinterConfig"><span class="pre"><code class="sourceCode python">PrinterConfig</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/QualifiedName.md" class="reference internal" title="syside.QualifiedName"><span class="pre"><code class="sourceCode python">QualifiedName</code></span></a> |  | A sequence of qualified name segments that stringifies with unrestricted names as needed. Unlike string, this allows querying segments in a qualified name without having to parse it again, and is cheaper to construct as string conversion is performed only when needed. |
| <a href="/python/v0.8.4/syside/RangeUtf16.md" class="reference internal" title="syside.RangeUtf16"><span class="pre"><code class="sourceCode python">RangeUtf16</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/RangeUtf32.md" class="reference internal" title="syside.RangeUtf32"><span class="pre"><code class="sourceCode python">RangeUtf32</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/RangeUtf8.md" class="reference internal" title="syside.RangeUtf8"><span class="pre"><code class="sourceCode python">RangeUtf8</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/Reader.md" class="reference internal" title="syside.Reader"><span class="pre"><code class="sourceCode python">Reader</code></span></a> |  | Abstract base class for all deserialization readers. |
| <a href="/python/v0.8.4/syside/Redefinition.md" class="reference internal" title="syside.Redefinition"><span class="pre"><code class="sourceCode python">Redefinition</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`Redefinition`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/ReferenceAccessor.md" class="reference internal" title="syside.ReferenceAccessor"><span class="pre"><code class="sourceCode python">ReferenceAccessor</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/ReferenceParameterAccessor.md" class="reference internal" title="syside.ReferenceParameterAccessor"><span class="pre"><code class="sourceCode python">ReferenceParameterAccessor</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/ReferencePrinter.md" class="reference internal" title="syside.ReferencePrinter"><span class="pre"><code class="sourceCode python">ReferencePrinter</code></span></a> |  | An opaque reference print function that will be called only for synthetic references. |
| <a href="/python/v0.8.4/syside/ReferenceSubsetting.md" class="reference internal" title="syside.ReferenceSubsetting"><span class="pre"><code class="sourceCode python">ReferenceSubsetting</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`ReferenceSubsetting`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/ReferenceUsage.md" class="reference internal" title="syside.ReferenceUsage"><span class="pre"><code class="sourceCode python">ReferenceUsage</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`ReferenceUsage`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/ReferenceUsageAccessor.md" class="reference internal" title="syside.ReferenceUsageAccessor"><span class="pre"><code class="sourceCode python">ReferenceUsageAccessor</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/ReferentAccessor.md" class="reference internal" title="syside.ReferentAccessor"><span class="pre"><code class="sourceCode python">ReferentAccessor</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/Relationship.md" class="reference internal" title="syside.Relationship"><span class="pre"><code class="sourceCode python">Relationship</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`Relationship`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/RelationshipBody.md" class="reference internal" title="syside.RelationshipBody"><span class="pre"><code class="sourceCode python">RelationshipBody</code></span></a> |  | Container for relationship bodies. Works similarly to <span class="pre">`ChildrenNodes`</span> except relationships are not needed and all elements are taken ownership off. |
| <a href="/python/v0.8.4/syside/RenderingDefinition.md" class="reference internal" title="syside.RenderingDefinition"><span class="pre"><code class="sourceCode python">RenderingDefinition</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`RenderingDefinition`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/RenderingUsage.md" class="reference internal" title="syside.RenderingUsage"><span class="pre"><code class="sourceCode python">RenderingUsage</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`RenderingUsage`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/RequirementConstraintMembership.md" class="reference internal" title="syside.RequirementConstraintMembership"><span class="pre"><code class="sourceCode python">RequirementConstraintMembership</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`RequirementConstraintMembership`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/RequirementDefinition.md" class="reference internal" title="syside.RequirementDefinition"><span class="pre"><code class="sourceCode python">RequirementDefinition</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`RequirementDefinition`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/RequirementUsage.md" class="reference internal" title="syside.RequirementUsage"><span class="pre"><code class="sourceCode python">RequirementUsage</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`RequirementUsage`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/RequirementVerificationMembership.md" class="reference internal" title="syside.RequirementVerificationMembership"><span class="pre"><code class="sourceCode python">RequirementVerificationMembership</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`RequirementVerificationMembership`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/ResultExpressionAccessor.md" class="reference internal" title="syside.ResultExpressionAccessor"><span class="pre"><code class="sourceCode python">ResultExpressionAccessor</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/ResultExpressionMembership.md" class="reference internal" title="syside.ResultExpressionMembership"><span class="pre"><code class="sourceCode python">ResultExpressionMembership</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`ResultExpressionMembership`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/ReturnParameterMembership.md" class="reference internal" title="syside.ReturnParameterMembership"><span class="pre"><code class="sourceCode python">ReturnParameterMembership</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`ReturnParameterMembership`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/SatisfactionSubjectAccessor.md" class="reference internal" title="syside.SatisfactionSubjectAccessor"><span class="pre"><code class="sourceCode python">SatisfactionSubjectAccessor</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/SatisfyRequirementUsage.md" class="reference internal" title="syside.SatisfyRequirementUsage"><span class="pre"><code class="sourceCode python">SatisfyRequirementUsage</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`SatisfyRequirementUsage`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/Schedule.md" class="reference internal" title="syside.Schedule"><span class="pre"><code class="sourceCode python">Schedule</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/ScheduleError.md" class="reference internal" title="syside.ScheduleError"><span class="pre"><code class="sourceCode python">ScheduleError</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/ScheduleOptions.md" class="reference internal" title="syside.ScheduleOptions"><span class="pre"><code class="sourceCode python">ScheduleOptions</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/SelectExpression.md" class="reference internal" title="syside.SelectExpression"><span class="pre"><code class="sourceCode python">SelectExpression</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`SelectExpression`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/Sema.md" class="reference internal" title="syside.Sema"><span class="pre"><code class="sourceCode python">Sema</code></span></a> |  | Semantic resolver for SysML. This is responsible for linking references and resolving semantic rules in the pipeline. |
| <a href="/python/v0.8.4/syside/SendActionUsage.md" class="reference internal" title="syside.SendActionUsage"><span class="pre"><code class="sourceCode python">SendActionUsage</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`SendActionUsage`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/SerdeMessage.md" class="reference internal" title="syside.SerdeMessage"><span class="pre"><code class="sourceCode python">SerdeMessage</code></span></a> |  | Message emitted during (de)serialization |
| <a href="/python/v0.8.4/syside/SerdeReport.md" class="reference internal" title="syside.SerdeReport"><span class="pre"><code class="sourceCode python">SerdeReport</code></span></a> |  | (De)Serialization report containing emitted messages. |
| <a href="/python/v0.8.4/syside/SerializationOptions.md" class="reference internal" title="syside.SerializationOptions"><span class="pre"><code class="sourceCode python">SerializationOptions</code></span></a> |  | Options for SysML model serialization. Attribute options are ordered in descending precedence. |
| <a href="/python/v0.8.4/syside/Serializer.md" class="reference internal" title="syside.Serializer"><span class="pre"><code class="sourceCode python">Serializer</code></span></a> |  | Serializer for SysML models. The actual serialization output depends on used <span class="pre">`Writer`</span>. |
| <a href="/python/v0.8.4/syside/SexpOptions.md" class="reference internal" title="syside.SexpOptions"><span class="pre"><code class="sourceCode python">SexpOptions</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/SharedMutex.md" class="reference internal" title="syside.SharedMutex"><span class="pre"><code class="sourceCode python">SharedMutex</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/Specialization.md" class="reference internal" title="syside.Specialization"><span class="pre"><code class="sourceCode python">Specialization</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`Specialization`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/StageTimes.md" class="reference internal" title="syside.StageTimes"><span class="pre"><code class="sourceCode python">StageTimes</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/StakeholderMembership.md" class="reference internal" title="syside.StakeholderMembership"><span class="pre"><code class="sourceCode python">StakeholderMembership</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`StakeholderMembership`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/StateDefinition.md" class="reference internal" title="syside.StateDefinition"><span class="pre"><code class="sourceCode python">StateDefinition</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`StateDefinition`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/StateId.md" class="reference internal" title="syside.StateId"><span class="pre"><code class="sourceCode python">StateId</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/StateSubactionMembership.md" class="reference internal" title="syside.StateSubactionMembership"><span class="pre"><code class="sourceCode python">StateSubactionMembership</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`StateSubactionMembership`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/StateUsage.md" class="reference internal" title="syside.StateUsage"><span class="pre"><code class="sourceCode python">StateUsage</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`StateUsage`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/StaticIndex.md" class="reference internal" title="syside.StaticIndex"><span class="pre"><code class="sourceCode python">StaticIndex</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/Stdlib.md" class="reference internal" title="syside.Stdlib"><span class="pre"><code class="sourceCode python">Stdlib</code></span></a> |  | Cache of standard library elements used by sema. |
| <a href="/python/v0.8.4/syside/Step.md" class="reference internal" title="syside.Step"><span class="pre"><code class="sourceCode python">Step</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`Step`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/Stream.md" class="reference internal" title="syside.Stream"><span class="pre"><code class="sourceCode python">Stream</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/Structure.md" class="reference internal" title="syside.Structure"><span class="pre"><code class="sourceCode python">Structure</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`Structure`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/Subclassification.md" class="reference internal" title="syside.Subclassification"><span class="pre"><code class="sourceCode python">Subclassification</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`Subclassification`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/SubjectMembership.md" class="reference internal" title="syside.SubjectMembership"><span class="pre"><code class="sourceCode python">SubjectMembership</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`SubjectMembership`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/Subsetting.md" class="reference internal" title="syside.Subsetting"><span class="pre"><code class="sourceCode python">Subsetting</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`Subsetting`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/Succession.md" class="reference internal" title="syside.Succession"><span class="pre"><code class="sourceCode python">Succession</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`Succession`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/SuccessionAsUsage.md" class="reference internal" title="syside.SuccessionAsUsage"><span class="pre"><code class="sourceCode python">SuccessionAsUsage</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`SuccessionAsUsage`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/SuccessionFlow.md" class="reference internal" title="syside.SuccessionFlow"><span class="pre"><code class="sourceCode python">SuccessionFlow</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`SuccessionFlow`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/SuccessionFlowUsage.md" class="reference internal" title="syside.SuccessionFlowUsage"><span class="pre"><code class="sourceCode python">SuccessionFlowUsage</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`SuccessionFlowUsage`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/Symbol.md" class="reference internal" title="syside.Symbol"><span class="pre"><code class="sourceCode python">Symbol</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/TargetFeatureAccessor.md" class="reference internal" title="syside.TargetFeatureAccessor"><span class="pre"><code class="sourceCode python">TargetFeatureAccessor</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/TerminateActionUsage.md" class="reference internal" title="syside.TerminateActionUsage"><span class="pre"><code class="sourceCode python">TerminateActionUsage</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`TerminateActionUsage`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/TextDocument.md" class="reference internal" title="syside.TextDocument"><span class="pre"><code class="sourceCode python">TextDocument</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/TextDocumentData.md" class="reference internal" title="syside.TextDocumentData"><span class="pre"><code class="sourceCode python">TextDocumentData</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/TextDocumentEditUtf16.md" class="reference internal" title="syside.TextDocumentEditUtf16"><span class="pre"><code class="sourceCode python">TextDocumentEditUtf16</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/TextDocumentEditUtf32.md" class="reference internal" title="syside.TextDocumentEditUtf32"><span class="pre"><code class="sourceCode python">TextDocumentEditUtf32</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/TextDocumentEditUtf8.md" class="reference internal" title="syside.TextDocumentEditUtf8"><span class="pre"><code class="sourceCode python">TextDocumentEditUtf8</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/TextDocuments.md" class="reference internal" title="syside.TextDocuments"><span class="pre"><code class="sourceCode python">TextDocuments</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/TextEdit.md" class="reference internal" title="syside.TextEdit"><span class="pre"><code class="sourceCode python">TextEdit</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/TextualRepresentation.md" class="reference internal" title="syside.TextualRepresentation"><span class="pre"><code class="sourceCode python">TextualRepresentation</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`TextualRepresentation`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/TransitionFeatureMembership.md" class="reference internal" title="syside.TransitionFeatureMembership"><span class="pre"><code class="sourceCode python">TransitionFeatureMembership</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`TransitionFeatureMembership`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/TransitionSourceAccessor.md" class="reference internal" title="syside.TransitionSourceAccessor"><span class="pre"><code class="sourceCode python">TransitionSourceAccessor</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/TransitionUsage.md" class="reference internal" title="syside.TransitionUsage"><span class="pre"><code class="sourceCode python">TransitionUsage</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`TransitionUsage`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/TriggerAccessor.md" class="reference internal" title="syside.TriggerAccessor"><span class="pre"><code class="sourceCode python">TriggerAccessor</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/TriggerInvocationExpression.md" class="reference internal" title="syside.TriggerInvocationExpression"><span class="pre"><code class="sourceCode python">TriggerInvocationExpression</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`TriggerInvocationExpression`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type"><span class="pre"><code class="sourceCode python">Type</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`Type`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/TypeFeaturing.md" class="reference internal" title="syside.TypeFeaturing"><span class="pre"><code class="sourceCode python">TypeFeaturing</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`TypeFeaturing`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/TypeGuard.md" class="reference internal" title="syside.TypeGuard"><span class="pre"><code class="sourceCode python">TypeGuard</code></span></a> |  | The type used in a type check expression, e.g. <span class="pre">`istype`</span>, <span class="pre">`hastype`</span>. The actual expression result type is <span class="pre">`ScalarValues::Boolean`</span>. |
| <a href="/python/v0.8.4/syside/TypeReference.md" class="reference internal" title="syside.TypeReference"><span class="pre"><code class="sourceCode python">TypeReference</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/TypeRelationships.md" class="reference internal" title="syside.TypeRelationships"><span class="pre"><code class="sourceCode python">TypeRelationships</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/UnexpectedDifferentReference.md" class="reference internal" title="syside.UnexpectedDifferentReference"><span class="pre"><code class="sourceCode python">UnexpectedDifferentReference</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/Unioning.md" class="reference internal" title="syside.Unioning"><span class="pre"><code class="sourceCode python">Unioning</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`Unioning`</span> defined in the KerML specification. |
| <a href="/python/v0.8.4/syside/Url.md" class="reference internal" title="syside.Url"><span class="pre"><code class="sourceCode python">Url</code></span></a> |  | <span class="pre">`URL`</span> as described using the <a href="https://datatracker.ietf.org/doc/html/rfc3986" class="reference external" target="_blank">Uniform Resource Identifier (URI)</a> specification (RFC3986). |
| <a href="/python/v0.8.4/syside/Usage.md" class="reference internal" title="syside.Usage"><span class="pre"><code class="sourceCode python">Usage</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`Usage`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/UseCaseDefinition.md" class="reference internal" title="syside.UseCaseDefinition"><span class="pre"><code class="sourceCode python">UseCaseDefinition</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`UseCaseDefinition`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/UseCaseUsage.md" class="reference internal" title="syside.UseCaseUsage"><span class="pre"><code class="sourceCode python">UseCaseUsage</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`UseCaseUsage`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/VariantMembership.md" class="reference internal" title="syside.VariantMembership"><span class="pre"><code class="sourceCode python">VariantMembership</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`VariantMembership`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/VerificationCaseDefinition.md" class="reference internal" title="syside.VerificationCaseDefinition"><span class="pre"><code class="sourceCode python">VerificationCaseDefinition</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`VerificationCaseDefinition`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/VerificationCaseUsage.md" class="reference internal" title="syside.VerificationCaseUsage"><span class="pre"><code class="sourceCode python">VerificationCaseUsage</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`VerificationCaseUsage`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/ViewDefinition.md" class="reference internal" title="syside.ViewDefinition"><span class="pre"><code class="sourceCode python">ViewDefinition</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`ViewDefinition`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/ViewRenderingMembership.md" class="reference internal" title="syside.ViewRenderingMembership"><span class="pre"><code class="sourceCode python">ViewRenderingMembership</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`ViewRenderingMembership`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/ViewUsage.md" class="reference internal" title="syside.ViewUsage"><span class="pre"><code class="sourceCode python">ViewUsage</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`ViewUsage`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/ViewpointDefinition.md" class="reference internal" title="syside.ViewpointDefinition"><span class="pre"><code class="sourceCode python">ViewpointDefinition</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`ViewpointDefinition`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/ViewpointUsage.md" class="reference internal" title="syside.ViewpointUsage"><span class="pre"><code class="sourceCode python">ViewpointUsage</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`ViewpointUsage`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/WhileLoopActionUsage.md" class="reference internal" title="syside.WhileLoopActionUsage"><span class="pre"><code class="sourceCode python">WhileLoopActionUsage</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`WhileLoopActionUsage`</span> defined in the SysML specification. |
| <a href="/python/v0.8.4/syside/WriteLocked.md" class="reference internal" title="syside.WriteLocked"><span class="pre"><code class="sourceCode python">WriteLocked</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/Writer.md" class="reference internal" title="syside.Writer"><span class="pre"><code class="sourceCode python">Writer</code></span></a> |  | Abstract base class for serialization writer implementations. |

</div>

</div>

<span class="sd-summary-text"><span class="nerd-font"></span> **Attributes** <a href="#syside-attributes-table" class="reference internal"><span class="std std-ref"></span></a></span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |
|----|----|----|
| <a href="#syside.DESERIALIZE_INTERNAL" class="reference internal" title="syside.DESERIALIZE_INTERNAL"><span class="pre"><code class="sourceCode python">DESERIALIZE_INTERNAL</code></span></a> | <span class="pre">`R`</span> |  |
| <a href="#syside.DESERIALIZE_STANDARD" class="reference internal" title="syside.DESERIALIZE_STANDARD"><span class="pre"><code class="sourceCode python">DESERIALIZE_STANDARD</code></span></a> | <span class="pre">`R`</span> |  |
| <a href="#syside.M" class="reference internal" title="syside.M"><span class="pre"><code class="sourceCode python">M</code></span></a> | <span class="pre">`R`</span> |  |
| <a href="#syside.R" class="reference internal" title="syside.R"><span class="pre"><code class="sourceCode python">R</code></span></a> | <span class="pre">`R`</span> |  |
| <a href="#syside.T" class="reference internal" title="syside.T"><span class="pre"><code class="sourceCode python">T</code></span></a> | <span class="pre">`R`</span> |  |
| <a href="#syside.TElement" class="reference internal" title="syside.TElement"><span class="pre"><code class="sourceCode python">TElement</code></span></a> | <span class="pre">`R`</span> |  |
| <a href="#syside.TNode" class="reference internal" title="syside.TNode"><span class="pre"><code class="sourceCode python">TNode</code></span></a> | <span class="pre">`R`</span> |  |
| <a href="#syside.U" class="reference internal" title="syside.U"><span class="pre"><code class="sourceCode python">U</code></span></a> | <span class="pre">`R`</span> |  |
| <a href="#syside.Value" class="reference internal" title="syside.Value"><span class="pre"><code class="sourceCode python">Value</code></span></a> |  |  |

</div>

</div>

<span class="sd-summary-text"><span class="nerd-font"></span> **Functions** <a href="#syside-functions-table" class="reference internal"><span class="std std-ref"></span></a></span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |
|----|----|----|
| <a href="#syside.build_model" class="reference internal" title="syside.build_model"><span class="pre"><code class="sourceCode python">build_model</code></span></a> |  | Build the AST for <span class="pre">`document`</span> from its <span class="pre">`text_document`</span>. Any existing model will be cleared, and the built model will not have its references linked. Instead, most references will use placeholder references that will be replaced by actual targets in linking stage. Only <span class="pre">`sysml`</span> and <span class="pre">`kerml`</span> languages are supported. |
| <a href="#syside.collect_exports" class="reference internal" title="syside.collect_exports"><span class="pre"><code class="sourceCode python">collect_exports</code></span></a> |  | Collect and cache symbols exported by <span class="pre">`document`</span>. This must be called before the <span class="pre">`document`</span> is indexed, otherwise wrong or no symbols may be indexed. Returns the number of symbols cached. |
| <a href="#syside.collect_files_recursively" class="reference internal" title="syside.collect_files_recursively"><span class="pre"><code class="sourceCode python">collect_files_recursively</code></span></a> |  | Recursively collect all <span class="pre">`.sysml`</span> and <span class="pre">`.kerml`</span> files in the specified directory. |
| <a href="#syside.decode_path" class="reference internal" title="syside.decode_path"><span class="pre"><code class="sourceCode python">decode_path</code></span></a> |  | Decode a filesystem path from a <span class="pre">`Url`</span>. This correctly handles Windows and Posix paths using <span class="pre">`file://`</span> scheme and returns other <span class="pre">`Urls`</span> as is. |
| <a href="#syside.deserialize" class="reference internal" title="syside.deserialize"><span class="pre"><code class="sourceCode python">deserialize</code></span></a> |  | Convenience function for deserialization. Prefer using <span class="pre">`Deserializer`</span> to avoid allocations when doing repeated deserializations. |
| <a href="#syside.format_diagnostics" class="reference internal" title="syside.format_diagnostics"><span class="pre"><code class="sourceCode python">format_diagnostics</code></span></a> |  |  |
| <a href="#syside.get_default_executor" class="reference internal" title="syside.get_default_executor"><span class="pre"><code class="sourceCode python">get_default_executor</code></span></a> |  | Get a default initialized <span class="pre">`Executor`</span> for running schedules. Default executor will use half the logical cores that are available on the current machine. An executor is just a thread pool so there is no reason for constructing and destroying one all the time. |
| <a href="#syside.load_model" class="reference internal" title="syside.load_model"><span class="pre"><code class="sourceCode python">load_model</code></span></a> |  | Load a SysMLv2 model. |
| <a href="#syside.make_file_url" class="reference internal" title="syside.make_file_url"><span class="pre"><code class="sourceCode python">make_file_url</code></span></a> |  | Construct a <span class="pre">`Url`</span> for a filesystem path with the <span class="pre">`file:`</span> scheme. This correctly handles Windows and Posix paths, normalizes Windows drive letters to uppercase, and percent escapes Unicode characters. |
| <a href="#syside.make_pipeline" class="reference internal" title="syside.make_pipeline"><span class="pre"><code class="sourceCode python">make_pipeline</code></span></a> |  |  |
| <a href="#syside.pprint" class="reference internal" title="syside.pprint"><span class="pre"><code class="sourceCode python">pprint</code></span></a> |  | Prints model subtree starting at <span class="pre">`root`</span> to textual syntax. |
| <a href="#syside.sema_reset" class="reference internal" title="syside.sema_reset"><span class="pre"><code class="sourceCode python">sema_reset</code></span></a> |  | Reset semantic state of <span class="pre">`element`</span>. This will typically remove any implied relationships, and reverse a few other changes made by sema. After this completes, <span class="pre">`element.sema_state`</span>` `<span class="pre">`==`</span>` `<span class="pre">`SemaState.None`</span>. |
| <a href="#syside.serialize" class="reference internal" title="syside.serialize"><span class="pre"><code class="sourceCode python">serialize</code></span></a> |  | Convenience function for serialization. Prefer using <span class="pre">`Serializer`</span> to avoid allocations when doing repeated serializations. |
| <a href="#syside.sexp" class="reference internal" title="syside.sexp"><span class="pre"><code class="sourceCode python">sexp</code></span></a> |  | Generate a minimal S-expression of owned elements rooted at <span class="pre">`root`</span>, useful for debugging. |
| <a href="#syside.try_load_model" class="reference internal" title="syside.try_load_model"><span class="pre"><code class="sourceCode python">try_load_model</code></span></a> |  | Load a SysMLv2 model. |

</div>

</div>

<span class="sd-summary-text"><span class="nerd-font"></span> **Enumerations** <a href="#syside-enumerations-table" class="reference internal"><span class="std std-ref"></span></a></span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |
|----|----|----|
| <a href="#syside.AlwaysNever" class="reference internal" title="syside.AlwaysNever"><span class="pre"><code class="sourceCode python">AlwaysNever</code></span></a> |  |  |
| <a href="#syside.BuildState" class="reference internal" title="syside.BuildState"><span class="pre"><code class="sourceCode python">BuildState</code></span></a> |  | Document build state |
| <a href="#syside.DiagnosticSeverity" class="reference internal" title="syside.DiagnosticSeverity"><span class="pre"><code class="sourceCode python">DiagnosticSeverity</code></span></a> |  |  |
| <a href="#syside.DocumentKind" class="reference internal" title="syside.DocumentKind"><span class="pre"><code class="sourceCode python">DocumentKind</code></span></a> |  | Is this a model-created document? |
| <a href="#syside.DocumentState" class="reference internal" title="syside.DocumentState"><span class="pre"><code class="sourceCode python">DocumentState</code></span></a> |  |  |
| <a href="#syside.DocumentTier" class="reference internal" title="syside.DocumentTier"><span class="pre"><code class="sourceCode python">DocumentTier</code></span></a> |  |  |
| <a href="#syside.ExplicitOperator" class="reference internal" title="syside.ExplicitOperator"><span class="pre"><code class="sourceCode python">ExplicitOperator</code></span></a> |  |  |
| <a href="#syside.FailAction" class="reference internal" title="syside.FailAction"><span class="pre"><code class="sourceCode python">FailAction</code></span></a> |  | Action taken when a serialization error is encountered. |
| <a href="#syside.FeatureDirectionKind" class="reference internal" title="syside.FeatureDirectionKind"><span class="pre"><code class="sourceCode python">FeatureDirectionKind</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`FeatureDirectionKind`</span> defined in the KerML specification. |
| <a href="#syside.FloatFormat" class="reference internal" title="syside.FloatFormat"><span class="pre"><code class="sourceCode python">FloatFormat</code></span></a> |  |  |
| <a href="#syside.HostType" class="reference internal" title="syside.HostType"><span class="pre"><code class="sourceCode python">HostType</code></span></a> |  |  |
| <a href="#syside.ImplicitSpecializationKind" class="reference internal" title="syside.ImplicitSpecializationKind"><span class="pre"><code class="sourceCode python">ImplicitSpecializationKind</code></span></a> |  |  |
| <a href="#syside.KwToken" class="reference internal" title="syside.KwToken"><span class="pre"><code class="sourceCode python">KwToken</code></span></a> |  |  |
| <a href="#syside.LineEnd" class="reference internal" title="syside.LineEnd"><span class="pre"><code class="sourceCode python">LineEnd</code></span></a> |  |  |
| <a href="#syside.ModelLanguage" class="reference internal" title="syside.ModelLanguage"><span class="pre"><code class="sourceCode python">ModelLanguage</code></span></a> |  |  |
| <a href="#syside.MultiOrder" class="reference internal" title="syside.MultiOrder"><span class="pre"><code class="sourceCode python">MultiOrder</code></span></a> |  |  |
| <a href="#syside.MultiPlacement" class="reference internal" title="syside.MultiPlacement"><span class="pre"><code class="sourceCode python">MultiPlacement</code></span></a> |  |  |
| <a href="#syside.NameID" class="reference internal" title="syside.NameID"><span class="pre"><code class="sourceCode python">NameID</code></span></a> |  |  |
| <a href="#syside.NamePreference" class="reference internal" title="syside.NamePreference"><span class="pre"><code class="sourceCode python">NamePreference</code></span></a> |  |  |
| <a href="#syside.NullFormat" class="reference internal" title="syside.NullFormat"><span class="pre"><code class="sourceCode python">NullFormat</code></span></a> |  |  |
| <a href="#syside.Operator" class="reference internal" title="syside.Operator"><span class="pre"><code class="sourceCode python">Operator</code></span></a> |  |  |
| <a href="#syside.OperatorBreak" class="reference internal" title="syside.OperatorBreak"><span class="pre"><code class="sourceCode python">OperatorBreak</code></span></a> |  |  |
| <a href="#syside.OptionalKw" class="reference internal" title="syside.OptionalKw"><span class="pre"><code class="sourceCode python">OptionalKw</code></span></a> |  |  |
| <a href="#syside.OptionalKwToken" class="reference internal" title="syside.OptionalKwToken"><span class="pre"><code class="sourceCode python">OptionalKwToken</code></span></a> |  |  |
| <a href="#syside.OptionalToken" class="reference internal" title="syside.OptionalToken"><span class="pre"><code class="sourceCode python">OptionalToken</code></span></a> |  |  |
| <a href="#syside.PortionKind" class="reference internal" title="syside.PortionKind"><span class="pre"><code class="sourceCode python">PortionKind</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`PortionKind`</span> defined in the SysML specification. |
| <a href="#syside.PrintMode" class="reference internal" title="syside.PrintMode"><span class="pre"><code class="sourceCode python">PrintMode</code></span></a> |  |  |
| <a href="#syside.RequirementConstraintKind" class="reference internal" title="syside.RequirementConstraintKind"><span class="pre"><code class="sourceCode python">RequirementConstraintKind</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`RequirementConstraintKind`</span> defined in the SysML specification. |
| <a href="#syside.Scheme" class="reference internal" title="syside.Scheme"><span class="pre"><code class="sourceCode python">Scheme</code></span></a> |  |  |
| <a href="#syside.SemaState" class="reference internal" title="syside.SemaState"><span class="pre"><code class="sourceCode python">SemaState</code></span></a> |  | Semantic resolution state of <span class="pre">`Elements`</span>. Sema will use this information to discard duplicate work, e.g. when resolving elements in a group of related documents. |
| <a href="#syside.StateSubactionKind" class="reference internal" title="syside.StateSubactionKind"><span class="pre"><code class="sourceCode python">StateSubactionKind</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`StateSubactionKind`</span> defined in the SysML specification. |
| <a href="#syside.TextDocumentSaveReason" class="reference internal" title="syside.TextDocumentSaveReason"><span class="pre"><code class="sourceCode python">TextDocumentSaveReason</code></span></a> |  |  |
| <a href="#syside.TransitionFeatureKind" class="reference internal" title="syside.TransitionFeatureKind"><span class="pre"><code class="sourceCode python">TransitionFeatureKind</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`TransitionFeatureKind`</span> defined in the SysML specification. |
| <a href="#syside.TreeDrawing" class="reference internal" title="syside.TreeDrawing"><span class="pre"><code class="sourceCode python">TreeDrawing</code></span></a> |  |  |
| <a href="#syside.TriggerKind" class="reference internal" title="syside.TriggerKind"><span class="pre"><code class="sourceCode python">TriggerKind</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`TriggerKind`</span> defined in the SysML specification. |
| <a href="#syside.ValidationTiming" class="reference internal" title="syside.ValidationTiming"><span class="pre"><code class="sourceCode python">ValidationTiming</code></span></a> |  |  |
| <a href="#syside.VisibilityKind" class="reference internal" title="syside.VisibilityKind"><span class="pre"><code class="sourceCode python">VisibilityKind</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`VisibilityKind`</span> defined in the KerML specification. |
| <a href="#syside.VisitAction" class="reference internal" title="syside.VisitAction"><span class="pre"><code class="sourceCode python">VisitAction</code></span></a> |  |  |

</div>

</div>

</div>

------------------------------------------------------------------------

<div id="attributes" class="section">

## <span class="nerd-font"></span> Attributes<a href="#attributes" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

<span class="sig-name descname"><span class="pre">DESERIALIZE_INTERNAL</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/AttributeMap.md" class="reference internal" title="syside.AttributeMap"><span class="pre">syside.AttributeMap</span></a><span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">Ellipsis</span>*<a href="#syside.DESERIALIZE_INTERNAL" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<!-- -->

<span class="sig-name descname"><span class="pre">DESERIALIZE_STANDARD</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/AttributeMap.md" class="reference internal" title="syside.AttributeMap"><span class="pre">syside.AttributeMap</span></a><span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">Ellipsis</span>*<a href="#syside.DESERIALIZE_STANDARD" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<!-- -->

<span class="sig-name descname"><span class="pre">M</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">TypeVar("M",</span> <span class="pre">bound=syside.Element)</span>*<a href="#syside.M" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<!-- -->

<span class="sig-name descname"><span class="pre">R</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">TypeVar("R",</span> <span class="pre">bound=syside.Relationship)</span>*<a href="#syside.R" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<!-- -->

<span class="sig-name descname"><span class="pre">T</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">TypeVar("T")</span>*<a href="#syside.T" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<!-- -->

<span class="sig-name descname"><span class="pre">TElement</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">TypeVar("TElement",</span> <span class="pre">bound=syside.Element)</span>*<a href="#syside.TElement" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<!-- -->

<span class="sig-name descname"><span class="pre">TNode</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">TypeVar("TNode",</span> <span class="pre">bound=syside.AstNode)</span>*<a href="#syside.TNode" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<!-- -->

<span class="sig-name descname"><span class="pre">U</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">TypeVar("U",</span> <span class="pre">covariant=True)</span>*<a href="#syside.U" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<!-- -->

*<span class="pre">type</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">Value</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">int</span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">float</span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">bool</span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/Infinity.md" class="reference internal" title="syside.Infinity"><span class="pre">syside.Infinity</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">range</span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element"><span class="pre">syside.Element</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/BoundMetaclass.md" class="reference internal" title="syside.BoundMetaclass"><span class="pre">syside.BoundMetaclass</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">list</span><span class="p"><span class="pre">\[</span></span><span class="pre">Value</span><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Value" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/Compiler.md" class="reference internal" title="syside.Compiler"><span class="pre"><code class="sourceCode python">syside.Compiler</code></span></a>

  - <a href="/python/v0.8.4/syside/Compiler.md" class="reference internal" title="syside.Compiler.evaluate"><span class="pre"><code class="sourceCode python">evaluate</code></span></a>

  - <a href="/python/v0.8.4/syside/Compiler.md" class="reference internal" title="syside.Compiler.evaluate_feature"><span class="pre"><code class="sourceCode python">evaluate_feature</code></span></a>

</div>

</div>

<div id="functions" class="section">

## <span class="nerd-font">󰊕</span> Functions<a href="#functions" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

<span class="sig-name descname"><span class="pre">build_model</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">document</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/Document.md" class="reference internal" title="syside.Document"><span class="pre">syside.Document</span></a></span>*, *<span class="n"><span class="pre">language</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="#syside.ModelLanguage" class="reference internal" title="syside.ModelLanguage"><span class="pre">syside.ModelLanguage</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">None</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">list</span><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Diagnostic.md" class="reference internal" title="syside.Diagnostic"><span class="pre">syside.Diagnostic</span></a><span class="p"><span class="pre">\]</span></span></span></span><a href="#syside.build_model" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Build the AST for <span class="pre">`document`</span> from its <span class="pre">`text_document`</span>. Any existing model will be cleared, and the built model will not have its references linked. Instead, most references will use placeholder references that will be replaced by actual targets in linking stage. Only <span class="pre">`sysml`</span> and <span class="pre">`kerml`</span> languages are supported.

This is a CST -\> AST stage in the pipeline.

Raises <span class="pre">`ValueError`</span> if the <span class="pre">`document`</span> has unsupported language, or it has no associated <span class="pre">`text_document`</span>.

<!-- -->

<span class="sig-name descname"><span class="pre">collect_exports</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">document</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/Document.md" class="reference internal" title="syside.Document"><span class="pre">syside.Document</span></a></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">int</span></span></span><a href="#syside.collect_exports" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Collect and cache symbols exported by <span class="pre">`document`</span>. This must be called before the <span class="pre">`document`</span> is indexed, otherwise wrong or no symbols may be indexed. Returns the number of symbols cached.

<!-- -->

<span class="sig-name descname"><span class="pre">collect_files_recursively</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">directory_path</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">os.PathLike</span><span class="p"><span class="pre">\[</span></span><span class="pre">Any</span><span class="p"><span class="pre">\]</span></span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">list</span><span class="p"><span class="pre">\[</span></span><span class="pre">pathlib.Path</span><span class="p"><span class="pre">\]</span></span></span></span><a href="#syside.collect_files_recursively" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Recursively collect all <span class="pre">`.sysml`</span> and <span class="pre">`.kerml`</span> files in the specified directory.

<!-- -->

<span class="sig-name descname"><span class="pre">decode_path</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg0</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/Url.md" class="reference internal" title="syside.Url"><span class="pre">syside.Url</span></a></span>*, *<span class="n"><span class="pre">options</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/EncodingOpts.md" class="reference internal" title="syside.EncodingOpts"><span class="pre">syside.EncodingOpts</span></a></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">...</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">str</span></span></span><a href="#syside.decode_path" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Decode a filesystem path from a <span class="pre">`Url`</span>. This correctly handles Windows and Posix paths using <span class="pre">`file://`</span> scheme and returns other <span class="pre">`Urls`</span> as is.

<!-- -->

<span class="sig-name descname"><span class="pre">deserialize</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">document</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/Document.md" class="reference internal" title="syside.Document"><span class="pre">syside.Document</span></a></span>*, *<span class="n"><span class="pre">reader</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/Reader.md" class="reference internal" title="syside.Reader"><span class="pre">syside.Reader</span></a></span>*, *<span class="n"><span class="pre">attributes</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/AttributeMap.md" class="reference internal" title="syside.AttributeMap"><span class="pre">syside.AttributeMap</span></a></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/DeserializedModel.md" class="reference internal" title="syside.DeserializedModel"><span class="pre">syside.DeserializedModel</span></a><span class="p"><span class="pre">,</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/SerdeReport.md" class="reference internal" title="syside.SerdeReport"><span class="pre">syside.SerdeReport</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/DocumentSegment.md" class="reference internal" title="syside.DocumentSegment"><span class="pre">syside.DocumentSegment</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element"><span class="pre">syside.Element</span></a><span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">\]</span></span></span></span><a href="#syside.deserialize" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Convenience function for deserialization. Prefer using <span class="pre">`Deserializer`</span> to avoid allocations when doing repeated deserializations.

<!-- -->

<span class="sig-name descname"><span class="pre">format_diagnostics</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">errors</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">Sequence</span><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Diagnostic.md" class="reference internal" title="syside.Diagnostic"><span class="pre">syside.Diagnostic</span></a><span class="p"><span class="pre">\]</span></span></span>*, *<span class="n"><span class="pre">context</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/DiagnosticContext.md" class="reference internal" title="syside.DiagnosticContext"><span class="pre">syside.DiagnosticContext</span></a></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">...</span></span>*, *<span class="n"><span class="pre">options</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/DiagnosticFormatOptions.md" class="reference internal" title="syside.DiagnosticFormatOptions"><span class="pre">syside.DiagnosticFormatOptions</span></a></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">...</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">str</span></span></span><a href="#syside.format_diagnostics" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<!-- -->

<span class="sig-name descname"><span class="pre">get_default_executor</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="/python/v0.8.4/syside/Executor.md" class="reference internal" title="syside.Executor"><span class="pre">syside.Executor</span></a></span></span><a href="#syside.get_default_executor" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Get a default initialized <span class="pre">`Executor`</span> for running schedules. Default executor will use half the logical cores that are available on the current machine. An executor is just a thread pool so there is no reason for constructing and destroying one all the time.

<!-- -->

<span class="sig-name descname"><span class="pre">load_model</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">paths</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">Iterable</span><span class="p"><span class="pre">\[</span></span><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">os.PathLike</span><span class="p"><span class="pre">\[</span></span><span class="pre">Any</span><span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">\]</span></span></span>*, *<span class="o"><span class="pre">\*</span></span>*, *<span class="n"><span class="pre">environment</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/Environment.md" class="reference internal" title="syside.Environment"><span class="pre">syside.Environment</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">None</span></span>*, *<span class="n"><span class="pre">sysml_source</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">None</span></span>*, *<span class="n"><span class="pre">kerml_source</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">None</span></span>*, *<span class="n"><span class="pre">warnings_as_errors</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">False</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Model.md" class="reference internal" title="syside.Model"><span class="pre">syside.Model</span></a><span class="p"><span class="pre">,</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/Diagnostics.md" class="reference internal" title="syside.Diagnostics"><span class="pre">syside.Diagnostics</span></a><span class="p"><span class="pre">\]</span></span></span></span><a href="#syside.load_model" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<!-- -->

<span class="sig-name descname"><span class="pre">load_model</span></span><span class="sig-paren">(</span>*<span class="o"><span class="pre">\*</span></span>*, *<span class="n"><span class="pre">sysml_source</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="n"><span class="pre">kerml_source</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">...</span></span>*, *<span class="n"><span class="pre">environment</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/Environment.md" class="reference internal" title="syside.Environment"><span class="pre">syside.Environment</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">None</span></span>*, *<span class="n"><span class="pre">warnings_as_errors</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">False</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Model.md" class="reference internal" title="syside.Model"><span class="pre">syside.Model</span></a><span class="p"><span class="pre">,</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/Diagnostics.md" class="reference internal" title="syside.Diagnostics"><span class="pre">syside.Diagnostics</span></a><span class="p"><span class="pre">\]</span></span></span></span>  

<!-- -->

<span class="sig-name descname"><span class="pre">load_model</span></span><span class="sig-paren">(</span>*<span class="o"><span class="pre">\*</span></span>*, *<span class="n"><span class="pre">kerml_source</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="n"><span class="pre">sysml_source</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">...</span></span>*, *<span class="n"><span class="pre">environment</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/Environment.md" class="reference internal" title="syside.Environment"><span class="pre">syside.Environment</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">None</span></span>*, *<span class="n"><span class="pre">warnings_as_errors</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">False</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Model.md" class="reference internal" title="syside.Model"><span class="pre">syside.Model</span></a><span class="p"><span class="pre">,</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/Diagnostics.md" class="reference internal" title="syside.Diagnostics"><span class="pre">syside.Diagnostics</span></a><span class="p"><span class="pre">\]</span></span></span></span>  
Load a SysMLv2 model.

At least one of <span class="pre">`paths`</span>, <span class="pre">`sysml_source`</span>, and <span class="pre">`kerml_source`</span> must not be none.

Parameters<span class="colon">:</span>  
- **paths** – The paths to SysMLv2 or KerML files to load. These files must have correct file extensions (<span class="pre">`.sysml`</span> or <span class="pre">`.kerml`</span>).

- **environment** – The environment to be used for the model. If this parameter is left to <span class="pre">`None`</span>, uses the default environment. sysml_source: A SysMLv2 source to be loaded as an in-memory file. kerml_source: A KerML source to be loaded as an in-memory file.

Returns<span class="colon">:</span>  
Model and Diagnostics pair.

Raises<span class="colon">:</span>  
<a href="/python/v0.8.4/syside/ModelError.md" class="reference internal" title="syside.ModelError"><strong>ModelError</strong></a> – If returned diagnostics contain errors, or if <span class="pre">`warnings_as_errors`</span> is <span class="pre">`True`</span>, if diagnostics contain errors or warnings.

<!-- -->

<span class="sig-name descname"><span class="pre">make_file_url</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg0</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="n"><span class="pre">options</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/EncodingOpts.md" class="reference internal" title="syside.EncodingOpts"><span class="pre">syside.EncodingOpts</span></a></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">...</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="/python/v0.8.4/syside/Url.md" class="reference internal" title="syside.Url"><span class="pre">syside.Url</span></a></span></span><a href="#syside.make_file_url" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Construct a <span class="pre">`Url`</span> for a filesystem path with the <span class="pre">`file:`</span> scheme. This correctly handles Windows and Posix paths, normalizes Windows drive letters to uppercase, and percent escapes Unicode characters.

<!-- -->

<span class="sig-name descname"><span class="pre">make_file_url</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg0</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">os.PathLike</span><span class="p"><span class="pre">\[</span></span><span class="pre">AnyStr</span><span class="p"><span class="pre">\]</span></span></span>*, *<span class="n"><span class="pre">options</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/EncodingOpts.md" class="reference internal" title="syside.EncodingOpts"><span class="pre">syside.EncodingOpts</span></a></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">...</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="/python/v0.8.4/syside/Url.md" class="reference internal" title="syside.Url"><span class="pre">syside.Url</span></a></span></span>  

<!-- -->

<span class="sig-name descname"><span class="pre">make_pipeline</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/PipelineOptions.md" class="reference internal" title="syside.PipelineOptions"><span class="pre">syside.PipelineOptions</span></a></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="/python/v0.8.4/syside/Pipeline.md" class="reference internal" title="syside.Pipeline"><span class="pre">syside.Pipeline</span></a></span></span><a href="#syside.make_pipeline" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<!-- -->

<span class="sig-name descname"><span class="pre">pprint</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg0</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element"><span class="pre">syside.Element</span></a></span>*, *<span class="n"><span class="pre">printer</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/ModelPrinter.md" class="reference internal" title="syside.ModelPrinter"><span class="pre">syside.ModelPrinter</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">None</span></span>*, *<span class="n"><span class="pre">config</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/PrinterConfig.md" class="reference internal" title="syside.PrinterConfig"><span class="pre">syside.PrinterConfig</span></a></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">...</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">str</span></span></span><a href="#syside.pprint" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Prints model subtree starting at <span class="pre">`root`</span> to textual syntax.

**NOTE** This performs very little checking that the given model can be represented in textual syntax, besides checking for elements that are missing. This has no effect when used as a formatter on a model parsed without syntax errors but programmatic models are not guaranteed to be valid textual syntax. In addition, it does not check that references are reachable from their scopes so parsing the printed model can fail to find them again. Otherwise, clearly unreachable references, such as when one of their ancestors is anonymous, will raise errors.

Only the first import from any parent namespaces that would shorten the printed reference is used. This does not apply to imports themselves to prevent reference resolution errors due to multiple or cyclical imports. Additionally, references relative to left-hand side expression result types, such as those from <span class="pre">`FeatureChainExpressions`</span>, are assumed to be directly or indirectly accessible so only their short or regular name is printed.

<!-- -->

<span class="sig-name descname"><span class="pre">sema_reset</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">element</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element"><span class="pre">syside.Element</span></a></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span><a href="#syside.sema_reset" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Reset semantic state of <span class="pre">`element`</span>. This will typically remove any implied relationships, and reverse a few other changes made by sema. After this completes, <span class="pre">`element.sema_state`</span>` `<span class="pre">`==`</span>` `<span class="pre">`SemaState.None`</span>.

<!-- -->

<span class="sig-name descname"><span class="pre">sema_reset</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">document</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/Document.md" class="reference internal" title="syside.Document"><span class="pre">syside.Document</span></a></span>*, *<span class="n"><span class="pre">reporter</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">Callable</span><span class="p"><span class="pre">\[</span></span><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element"><span class="pre">syside.Element</span></a><span class="p"><span class="pre">,</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/UnexpectedDifferentReference.md" class="reference internal" title="syside.UnexpectedDifferentReference"><span class="pre">syside.UnexpectedDifferentReference</span></a><span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">None</span><span class="p"><span class="pre">\]</span></span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">None</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span>  
Reset semantic state of <span class="pre">`document`</span>. This will call <span class="pre">`sema_reset`</span> on all owned elements, and additionally reset all resolved references back to unresolved state. While resetting references, if the resolved reference does not match the current reference, <span class="pre">`reporter`</span> will be called with the element the reference applies to and <span class="pre">`UnexpectedDifferentReference`</span> that was found. By default, <span class="pre">`reporter`</span> will print such errors to <span class="pre">`stderr`</span>.

After this completes, <span class="pre">`document.build_state`</span>` `<span class="pre">`==`</span>` `<span class="pre">`BuildState.Indexed`</span>.

<!-- -->

<span class="sig-name descname"><span class="pre">serialize</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">root</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element"><span class="pre">syside.Element</span></a></span>*, *<span class="n"><span class="pre">writer</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/Writer.md" class="reference internal" title="syside.Writer"><span class="pre">syside.Writer</span></a><span class="p"><span class="pre">\[</span></span><span class="pre">syside.T</span><span class="p"><span class="pre">\]</span></span></span>*, *<span class="n"><span class="pre">options</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/SerializationOptions.md" class="reference internal" title="syside.SerializationOptions"><span class="pre">syside.SerializationOptions</span></a></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">...</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="/python/v0.8.4/syside/SerdeReport.md" class="reference internal" title="syside.SerdeReport"><span class="pre">syside.SerdeReport</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element"><span class="pre">syside.Element</span></a><span class="p"><span class="pre">\]</span></span></span></span><a href="#syside.serialize" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Convenience function for serialization. Prefer using <span class="pre">`Serializer`</span> to avoid allocations when doing repeated serializations.

<!-- -->

<span class="sig-name descname"><span class="pre">serialize</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">root</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element"><span class="pre">syside.Element</span></a></span>*, *<span class="n"><span class="pre">writer</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/Writer.md" class="reference internal" title="syside.Writer"><span class="pre">syside.Writer</span></a><span class="p"><span class="pre">\[</span></span><span class="pre">syside.T</span><span class="p"><span class="pre">\]</span></span></span>*, *<span class="n"><span class="pre">use_standard_names</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">True</span></span>*, *<span class="n"><span class="pre">include_derived</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">False</span></span>*, *<span class="n"><span class="pre">include_redefined</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">False</span></span>*, *<span class="n"><span class="pre">include_default</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">False</span></span>*, *<span class="n"><span class="pre">include_optional</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">False</span></span>*, *<span class="n"><span class="pre">include_implied</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">False</span></span>*, *<span class="n"><span class="pre">fail_action</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="#syside.FailAction" class="reference internal" title="syside.FailAction"><span class="pre">syside.FailAction</span></a></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">FailAction.Diagnose</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="/python/v0.8.4/syside/SerdeReport.md" class="reference internal" title="syside.SerdeReport"><span class="pre">syside.SerdeReport</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element"><span class="pre">syside.Element</span></a><span class="p"><span class="pre">\]</span></span></span></span>  

<!-- -->

<span class="sig-name descname"><span class="pre">sexp</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">root</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element"><span class="pre">syside.Element</span></a></span>*, *<span class="n"><span class="pre">options</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/SexpOptions.md" class="reference internal" title="syside.SexpOptions"><span class="pre">syside.SexpOptions</span></a></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">...</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">str</span></span></span><a href="#syside.sexp" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Generate a minimal S-expression of owned elements rooted at <span class="pre">`root`</span>, useful for debugging.

<!-- -->

<span class="sig-name descname"><span class="pre">sexp</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">root</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element"><span class="pre">syside.Element</span></a></span>*, *<span class="n"><span class="pre">indent</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">int</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">2</span></span>*, *<span class="n"><span class="pre">include_implicit</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">True</span></span>*, *<span class="n"><span class="pre">print_references</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">False</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">str</span></span></span>  

<!-- -->

<span class="sig-name descname"><span class="pre">try_load_model</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">paths</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">Iterable</span><span class="p"><span class="pre">\[</span></span><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">os.PathLike</span><span class="p"><span class="pre">\[</span></span><span class="pre">Any</span><span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">\]</span></span></span>*, *<span class="o"><span class="pre">\*</span></span>*, *<span class="n"><span class="pre">environment</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/Environment.md" class="reference internal" title="syside.Environment"><span class="pre">syside.Environment</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">None</span></span>*, *<span class="n"><span class="pre">sysml_source</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">None</span></span>*, *<span class="n"><span class="pre">kerml_source</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">None</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Model.md" class="reference internal" title="syside.Model"><span class="pre">syside.Model</span></a><span class="p"><span class="pre">,</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/Diagnostics.md" class="reference internal" title="syside.Diagnostics"><span class="pre">syside.Diagnostics</span></a><span class="p"><span class="pre">\]</span></span></span></span><a href="#syside.try_load_model" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<!-- -->

<span class="sig-name descname"><span class="pre">try_load_model</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">paths</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">Iterable</span><span class="p"><span class="pre">\[</span></span><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">os.PathLike</span><span class="p"><span class="pre">\[</span></span><span class="pre">Any</span><span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">\]</span></span></span>*, *<span class="n"><span class="pre">environment</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/Environment.md" class="reference internal" title="syside.Environment"><span class="pre">syside.Environment</span></a></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Model.md" class="reference internal" title="syside.Model"><span class="pre">syside.Model</span></a><span class="p"><span class="pre">,</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/Diagnostics.md" class="reference internal" title="syside.Diagnostics"><span class="pre">syside.Diagnostics</span></a><span class="p"><span class="pre">\]</span></span></span></span>  

<!-- -->

<span class="sig-name descname"><span class="pre">try_load_model</span></span><span class="sig-paren">(</span>*<span class="o"><span class="pre">\*</span></span>*, *<span class="n"><span class="pre">sysml_source</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="n"><span class="pre">kerml_source</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">...</span></span>*, *<span class="n"><span class="pre">environment</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/Environment.md" class="reference internal" title="syside.Environment"><span class="pre">syside.Environment</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">None</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Model.md" class="reference internal" title="syside.Model"><span class="pre">syside.Model</span></a><span class="p"><span class="pre">,</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/Diagnostics.md" class="reference internal" title="syside.Diagnostics"><span class="pre">syside.Diagnostics</span></a><span class="p"><span class="pre">\]</span></span></span></span>  

<!-- -->

<span class="sig-name descname"><span class="pre">try_load_model</span></span><span class="sig-paren">(</span>*<span class="o"><span class="pre">\*</span></span>*, *<span class="n"><span class="pre">kerml_source</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="n"><span class="pre">sysml_source</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">...</span></span>*, *<span class="n"><span class="pre">environment</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/Environment.md" class="reference internal" title="syside.Environment"><span class="pre">syside.Environment</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">None</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Model.md" class="reference internal" title="syside.Model"><span class="pre">syside.Model</span></a><span class="p"><span class="pre">,</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/Diagnostics.md" class="reference internal" title="syside.Diagnostics"><span class="pre">syside.Diagnostics</span></a><span class="p"><span class="pre">\]</span></span></span></span>  
Load a SysMLv2 model.

At least one of <span class="pre">`paths`</span>, <span class="pre">`sysml_source`</span>, and <span class="pre">`kerml_source`</span> must not be none.

Parameters<span class="colon">:</span>  
- **paths** – The paths to SysMLv2 or KerML files to load. These files must have correct file extensions (<span class="pre">`.sysml`</span> or <span class="pre">`.kerml`</span>).

- **environment** – The environment to be used for the model. If this parameter is left to <span class="pre">`None`</span>, uses the default environment.

- **sysml_source** – A SysMLv2 source to be loaded as an in-memory file.

- **kerml_source** – A KerML source to be loaded as an in-memory file.

Returns<span class="colon">:</span>  
Model and Diagnostics pair. Note that models may only be partial if parsing failed, however even a partial model may be of interest for analysis.

</div>

<div id="enumerations" class="section">

## <span class="nerd-font"></span> Enumerations<a href="#enumerations" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">AlwaysNever</span></span><a href="#syside.AlwaysNever" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
<div class="pst-scrollable-table-container">

|  |  |
|----|----|
| <span class="pre">`Always`</span> <a href="#syside-alwaysnever-always" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Never`</span> <a href="#syside-alwaysnever-never" class="reference internal"><span class="std std-ref"></span></a> |  |

</div>

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions"><span class="pre"><code class="sourceCode python">syside.FormatOptions</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.attribute_usage_reference_keyword"><span class="pre"><code class="sourceCode python">attribute_usage_reference_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.binary_allocation_usages"><span class="pre"><code class="sourceCode python">binary_allocation_usages</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.binary_binding_connectors"><span class="pre"><code class="sourceCode python">binary_binding_connectors</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.binary_connection_usages"><span class="pre"><code class="sourceCode python">binary_connection_usages</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.binary_connectors"><span class="pre"><code class="sourceCode python">binary_connectors</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.binary_interface_usages"><span class="pre"><code class="sourceCode python">binary_interface_usages</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.binary_successions"><span class="pre"><code class="sourceCode python">binary_successions</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.connection_usage_reference_keyword"><span class="pre"><code class="sourceCode python">connection_usage_reference_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.connector_as_usage_reference_keyword"><span class="pre"><code class="sourceCode python">connector_as_usage_reference_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.empty_namespace_brackets"><span class="pre"><code class="sourceCode python">empty_namespace_brackets</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.enum_member_keyword"><span class="pre"><code class="sourceCode python">enum_member_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.event_occurrence_reference_keyword"><span class="pre"><code class="sourceCode python">event_occurrence_reference_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.exhibit_state_reference_keyword"><span class="pre"><code class="sourceCode python">exhibit_state_reference_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.include_use_case_reference_keyword"><span class="pre"><code class="sourceCode python">include_use_case_reference_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.interface_port_keyword"><span class="pre"><code class="sourceCode python">interface_port_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.invariant_true_keyword"><span class="pre"><code class="sourceCode python">invariant_true_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.metadata_body_feature_keyword"><span class="pre"><code class="sourceCode python">metadata_body_feature_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.perform_action_reference_keyword"><span class="pre"><code class="sourceCode python">perform_action_reference_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.port_usage_reference_keyword"><span class="pre"><code class="sourceCode python">port_usage_reference_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.public_keyword"><span class="pre"><code class="sourceCode python">public_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.satisfy_requirement_assert_keyword"><span class="pre"><code class="sourceCode python">satisfy_requirement_assert_keyword</code></span></a>

</div>

<!-- -->

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">BuildState</span></span><a href="#syside.BuildState" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Document build state

<div class="pst-scrollable-table-container">

|  |  |  |
|----|----|----|
| <span class="pre">`none`</span> <a href="#syside-buildstate-none" class="reference internal"><span class="std std-ref"></span></a> | = 0 | Document has only been created |
| <span class="pre">`Changed`</span> <a href="#syside-buildstate-changed" class="reference internal"><span class="std std-ref"></span></a> | = 1 | Document content has changed |
| <span class="pre">`Parsed`</span> <a href="#syside-buildstate-parsed" class="reference internal"><span class="std std-ref"></span></a> | = 2 | Document content was parsed |
| <span class="pre">`Indexed`</span> <a href="#syside-buildstate-indexed" class="reference internal"><span class="std std-ref"></span></a> | = 3 | Document global and local exports have been indexed |
| <span class="pre">`Built`</span> <a href="#syside-buildstate-built" class="reference internal"><span class="std std-ref"></span></a> | = 4 | Model has been built and linked |
| <span class="pre">`Validated`</span> <a href="#syside-buildstate-validated" class="reference internal"><span class="std std-ref"></span></a> | = 5 | Model has been validated |

</div>

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/BasicDocument.md" class="reference internal" title="syside.BasicDocument"><span class="pre"><code class="sourceCode python">syside.BasicDocument</code></span></a>

  - <a href="/python/v0.8.4/syside/BasicDocument.md" class="reference internal" title="syside.BasicDocument.build_state"><span class="pre"><code class="sourceCode python">build_state</code></span></a>

- <a href="/python/v0.8.4/syside/ScheduleOptions.md" class="reference internal" title="syside.ScheduleOptions"><span class="pre"><code class="sourceCode python">syside.ScheduleOptions</code></span></a>

  - <a href="/python/v0.8.4/syside/ScheduleOptions.md" class="reference internal" title="syside.ScheduleOptions.__init__"><span class="pre"><code class="sourceCode python"><span class="fu">__init__</span></code></span></a>

  - <a href="/python/v0.8.4/syside/ScheduleOptions.md" class="reference internal" title="syside.ScheduleOptions.cutoff"><span class="pre"><code class="sourceCode python">cutoff</code></span></a>

</div>

<!-- -->

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">DiagnosticSeverity</span></span><a href="#syside.DiagnosticSeverity" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
<div class="pst-scrollable-table-container">

|  |  |  |
|----|----|----|
| <span class="pre">`Error`</span> <a href="#syside-diagnosticseverity-error" class="reference internal"><span class="std std-ref"></span></a> | = 1 |  |
| <span class="pre">`Warning`</span> <a href="#syside-diagnosticseverity-warning" class="reference internal"><span class="std std-ref"></span></a> | = 2 |  |
| <span class="pre">`Information`</span> <a href="#syside-diagnosticseverity-information" class="reference internal"><span class="std std-ref"></span></a> | = 3 |  |
| <span class="pre">`Hint`</span> <a href="#syside-diagnosticseverity-hint" class="reference internal"><span class="std std-ref"></span></a> | = 4 |  |

</div>

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/Diagnostic.md" class="reference internal" title="syside.Diagnostic"><span class="pre"><code class="sourceCode python">syside.Diagnostic</code></span></a>

  - <a href="/python/v0.8.4/syside/Diagnostic.md" class="reference internal" title="syside.Diagnostic.__init__"><span class="pre"><code class="sourceCode python"><span class="fu">__init__</span></code></span></a>

  - <a href="/python/v0.8.4/syside/Diagnostic.md" class="reference internal" title="syside.Diagnostic.severity"><span class="pre"><code class="sourceCode python">severity</code></span></a>

- <a href="/python/v0.8.4/syside/Diagnostics.md" class="reference internal" title="syside.Diagnostics"><span class="pre"><code class="sourceCode python">syside.Diagnostics</code></span></a>

  - <a href="/python/v0.8.4/syside/Diagnostics.md" class="reference internal" title="syside.Diagnostics.all_with_severity"><span class="pre"><code class="sourceCode python">all_with_severity</code></span></a>

- <a href="/python/v0.8.4/syside/SerdeMessage.md" class="reference internal" title="syside.SerdeMessage"><span class="pre"><code class="sourceCode python">syside.SerdeMessage</code></span></a>

  - <a href="/python/v0.8.4/syside/SerdeMessage.md" class="reference internal" title="syside.SerdeMessage.severity"><span class="pre"><code class="sourceCode python">severity</code></span></a>

</div>

<!-- -->

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">DocumentKind</span></span><a href="#syside.DocumentKind" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Is this a model-created document?

<div class="pst-scrollable-table-container">

|  |  |
|----|----|
| <span class="pre">`MODEL`</span> <a href="#syside-documentkind-model" class="reference internal"><span class="std std-ref"></span></a> | Is this a model-created document? |
| <span class="pre">`ENVIRONMENT`</span> <a href="#syside-documentkind-environment" class="reference internal"><span class="std std-ref"></span></a> | Is this a model-created document? |
| <span class="pre">`ALL`</span> <a href="#syside-documentkind-all" class="reference internal"><span class="std std-ref"></span></a> | Is this a model-created document? |
| <span class="pre">`USER`</span> <a href="#syside-documentkind-user" class="reference internal"><span class="std std-ref"></span></a> | Is this a model-created document? |
| <span class="pre">`STDLIB`</span> <a href="#syside-documentkind-stdlib" class="reference internal"><span class="std std-ref"></span></a> | Is this a model-created document? |

</div>

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/BaseModel.md" class="reference internal" title="syside.BaseModel"><span class="pre"><code class="sourceCode python">syside.BaseModel</code></span></a>

  - <a href="/python/v0.8.4/syside/BaseModel.md" class="reference internal" title="syside.BaseModel.elements"><span class="pre"><code class="sourceCode python">elements</code></span></a>

  - <a href="/python/v0.8.4/syside/BaseModel.md" class="reference internal" title="syside.BaseModel.nodes"><span class="pre"><code class="sourceCode python">nodes</code></span></a>

  - <a href="/python/v0.8.4/syside/BaseModel.md" class="reference internal" title="syside.BaseModel.uris"><span class="pre"><code class="sourceCode python">uris</code></span></a>

</div>

<!-- -->

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">DocumentState</span></span><a href="#syside.DocumentState" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
<div class="pst-scrollable-table-container">

|  |  |  |
|----|----|----|
| <span class="pre">`Created`</span> <a href="#syside-documentstate-created" class="reference internal"><span class="std std-ref"></span></a> | = 0 | Document has been created |
| <span class="pre">`Building`</span> <a href="#syside-documentstate-building" class="reference internal"><span class="std std-ref"></span></a> | = 1 | Document is being built |
| <span class="pre">`Completed`</span> <a href="#syside-documentstate-completed" class="reference internal"><span class="std std-ref"></span></a> | = 2 | Document was built successfully |
| <span class="pre">`Cancelled`</span> <a href="#syside-documentstate-cancelled" class="reference internal"><span class="std std-ref"></span></a> | = 3 | Document building was cancelled |
| <span class="pre">`Error`</span> <a href="#syside-documentstate-error" class="reference internal"><span class="std std-ref"></span></a> | = 4 | Document building errored |

</div>

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/BasicDocument.md" class="reference internal" title="syside.BasicDocument"><span class="pre"><code class="sourceCode python">syside.BasicDocument</code></span></a>

  - <a href="/python/v0.8.4/syside/BasicDocument.md" class="reference internal" title="syside.BasicDocument.document_state"><span class="pre"><code class="sourceCode python">document_state</code></span></a>

</div>

<!-- -->

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">DocumentTier</span></span><a href="#syside.DocumentTier" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
<div class="pst-scrollable-table-container">

|  |  |
|----|----|
| <span class="pre">`StandardLibrary`</span> <a href="#syside-documenttier-standardlibrary" class="reference internal"><span class="std std-ref"></span></a> | Document is a part of standard library. Assume that such documents change very rarely, or only change with new tool versions. |
| <span class="pre">`External`</span> <a href="#syside-documenttier-external" class="reference internal"><span class="std std-ref"></span></a> | Document is imported from a third-party library. Assume that they do not change unless the third-party library is updated. |
| <span class="pre">`Project`</span> <a href="#syside-documenttier-project" class="reference internal"><span class="std std-ref"></span></a> | Document is a part of the current project and may be edited at any time. |

</div>

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/BasicDocument.md" class="reference internal" title="syside.BasicDocument"><span class="pre"><code class="sourceCode python">syside.BasicDocument</code></span></a>

  - <a href="/python/v0.8.4/syside/BasicDocument.md" class="reference internal" title="syside.BasicDocument.change_document_tier"><span class="pre"><code class="sourceCode python">change_document_tier</code></span></a>

  - <a href="/python/v0.8.4/syside/BasicDocument.md" class="reference internal" title="syside.BasicDocument.document_tier"><span class="pre"><code class="sourceCode python">document_tier</code></span></a>

- <a href="/python/v0.8.4/syside/Document.md" class="reference internal" title="syside.Document"><span class="pre"><code class="sourceCode python">syside.Document</code></span></a>

  - <a href="/python/v0.8.4/syside/Document.md" class="reference internal" title="syside.Document.create_mt"><span class="pre"><code class="sourceCode python">create_mt</code></span></a>

  - <a href="/python/v0.8.4/syside/Document.md" class="reference internal" title="syside.Document.create_st"><span class="pre"><code class="sourceCode python">create_st</code></span></a>

- <a href="/python/v0.8.4/syside/DocumentOptions.md" class="reference internal" title="syside.DocumentOptions"><span class="pre"><code class="sourceCode python">syside.DocumentOptions</code></span></a>

  - <a href="/python/v0.8.4/syside/DocumentOptions.md" class="reference internal" title="syside.DocumentOptions.__init__"><span class="pre"><code class="sourceCode python"><span class="fu">__init__</span></code></span></a>

  - <a href="/python/v0.8.4/syside/DocumentOptions.md" class="reference internal" title="syside.DocumentOptions.tier"><span class="pre"><code class="sourceCode python">tier</code></span></a>

- <a href="/python/v0.8.4/syside/IOSchedule.md" class="reference internal" title="syside.IOSchedule"><span class="pre"><code class="sourceCode python">syside.IOSchedule</code></span></a>

  - <a href="/python/v0.8.4/syside/IOSchedule.md" class="reference internal" title="syside.IOSchedule.add_file"><span class="pre"><code class="sourceCode python">add_file</code></span></a>

  - <a href="/python/v0.8.4/syside/IOSchedule.md" class="reference internal" title="syside.IOSchedule.add_source"><span class="pre"><code class="sourceCode python">add_source</code></span></a>

- <a href="/python/v0.8.4/syside/ScheduleOptions.md" class="reference internal" title="syside.ScheduleOptions"><span class="pre"><code class="sourceCode python">syside.ScheduleOptions</code></span></a>

  - <a href="/python/v0.8.4/syside/ScheduleOptions.md" class="reference internal" title="syside.ScheduleOptions.__init__"><span class="pre"><code class="sourceCode python"><span class="fu">__init__</span></code></span></a>

  - <a href="/python/v0.8.4/syside/ScheduleOptions.md" class="reference internal" title="syside.ScheduleOptions.validation_tier"><span class="pre"><code class="sourceCode python">validation_tier</code></span></a>

</div>

<!-- -->

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">ExplicitOperator</span></span><a href="#syside.ExplicitOperator" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
<div class="pst-scrollable-table-container">

|  |  |
|----|----|
| <span class="pre">`If`</span> <a href="#syside-explicitoperator-if" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`NullCoalescing`</span> <a href="#syside-explicitoperator-nullcoalescing" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Implies`</span> <a href="#syside-explicitoperator-implies" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`LogicalOr`</span> <a href="#syside-explicitoperator-logicalor" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Or`</span> <a href="#syside-explicitoperator-or" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Xor`</span> <a href="#syside-explicitoperator-xor" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`LogicalAnd`</span> <a href="#syside-explicitoperator-logicaland" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`And`</span> <a href="#syside-explicitoperator-and" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Equals`</span> <a href="#syside-explicitoperator-equals" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Same`</span> <a href="#syside-explicitoperator-same" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`NotEquals`</span> <a href="#syside-explicitoperator-notequals" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`NotSame`</span> <a href="#syside-explicitoperator-notsame" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`IsType`</span> <a href="#syside-explicitoperator-istype" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`HasType`</span> <a href="#syside-explicitoperator-hastype" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`At`</span> <a href="#syside-explicitoperator-at" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`AtAt`</span> <a href="#syside-explicitoperator-atat" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`As`</span> <a href="#syside-explicitoperator-as" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Meta`</span> <a href="#syside-explicitoperator-meta" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Less`</span> <a href="#syside-explicitoperator-less" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`LessEqual`</span> <a href="#syside-explicitoperator-lessequal" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Greater`</span> <a href="#syside-explicitoperator-greater" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`GreaterEqual`</span> <a href="#syside-explicitoperator-greaterequal" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Range`</span> <a href="#syside-explicitoperator-range" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Plus`</span> <a href="#syside-explicitoperator-plus" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Minus`</span> <a href="#syside-explicitoperator-minus" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Multiply`</span> <a href="#syside-explicitoperator-multiply" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Divide`</span> <a href="#syside-explicitoperator-divide" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Modulo`</span> <a href="#syside-explicitoperator-modulo" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`ExponentStar`</span> <a href="#syside-explicitoperator-exponentstar" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`ExponentCaret`</span> <a href="#syside-explicitoperator-exponentcaret" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Conjugation`</span> <a href="#syside-explicitoperator-conjugation" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Not`</span> <a href="#syside-explicitoperator-not" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`All`</span> <a href="#syside-explicitoperator-all" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Quantity`</span> <a href="#syside-explicitoperator-quantity" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Comma`</span> <a href="#syside-explicitoperator-comma" class="reference internal"><span class="std std-ref"></span></a> |  |

</div>

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/OperatorExpression.md" class="reference internal" title="syside.OperatorExpression"><span class="pre"><code class="sourceCode python">syside.OperatorExpression</code></span></a>

  - <a href="/python/v0.8.4/syside/OperatorExpression.md" class="reference internal" title="syside.OperatorExpression.try_set_operator"><span class="pre"><code class="sourceCode python">try_set_operator</code></span></a>

</div>

<!-- -->

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">FailAction</span></span><a href="#syside.FailAction" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Action taken when a serialization error is encountered.

<div class="pst-scrollable-table-container">

|  |  |
|----|----|
| <span class="pre">`Fail`</span> <a href="#syside-failaction-fail" class="reference internal"><span class="std std-ref"></span></a> | Stop serialization on the first error. |
| <span class="pre">`Diagnose`</span> <a href="#syside-failaction-diagnose" class="reference internal"><span class="std std-ref"></span></a> | Continue diagnosing errors but stop serialization. |
| <span class="pre">`Ignore`</span> <a href="#syside-failaction-ignore" class="reference internal"><span class="std std-ref"></span></a> | Ignore errors and continue serialization. |

</div>

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="#module-syside" class="reference internal" title="syside"><span class="pre"><code class="sourceCode python">syside</code></span></a>

  - <a href="#syside.serialize" class="reference internal" title="syside.serialize"><span class="pre"><code class="sourceCode python">serialize</code></span></a>

- <a href="/python/v0.8.4/syside/SerializationOptions.md" class="reference internal" title="syside.SerializationOptions"><span class="pre"><code class="sourceCode python">syside.SerializationOptions</code></span></a>

  - <a href="/python/v0.8.4/syside/SerializationOptions.md" class="reference internal" title="syside.SerializationOptions.__init__"><span class="pre"><code class="sourceCode python"><span class="fu">__init__</span></code></span></a>

  - <a href="/python/v0.8.4/syside/SerializationOptions.md" class="reference internal" title="syside.SerializationOptions.fail_action"><span class="pre"><code class="sourceCode python">fail_action</code></span></a>

- <a href="/python/v0.8.4/syside/Serializer.md" class="reference internal" title="syside.Serializer"><span class="pre"><code class="sourceCode python">syside.Serializer</code></span></a>

  - <a href="/python/v0.8.4/syside/Serializer.md" class="reference internal" title="syside.Serializer.accept"><span class="pre"><code class="sourceCode python">accept</code></span></a>

</div>

<!-- -->

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">FeatureDirectionKind</span></span><a href="#syside.FeatureDirectionKind" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
<span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span>

Implementation of <span class="pre">`FeatureDirectionKind`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> <span class="pre">`FeatureDirectionKind`</span> enumerates the possible kinds of <span class="pre">`direction`</span> that a <span class="pre">`Feature`</span> may be given as a member of a <span class="pre">`Type`</span>.
>
> </div>

For language description, see section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=59" class="reference external" target="_blank">7.3.4.2</a> of the KerML specification. For more details on the model, see section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=168" class="reference external" target="_blank">8.3.3.1.5</a> of the KerML specification.

<div class="pst-scrollable-table-container">

|  |  |
|----|----|
| <span class="pre">`In`</span> <a href="#syside-featuredirectionkind-in" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Inout`</span> <a href="#syside-featuredirectionkind-inout" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Out`</span> <a href="#syside-featuredirectionkind-out" class="reference internal"><span class="std std-ref"></span></a> |  |

</div>

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature"><span class="pre"><code class="sourceCode python">syside.Feature</code></span></a>

  - <a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature.direction"><span class="pre"><code class="sourceCode python">direction</code></span></a>

  - <a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature.explicit_direction"><span class="pre"><code class="sourceCode python">explicit_direction</code></span></a>

- <a href="/python/v0.8.4/syside/ParameterMembership.md" class="reference internal" title="syside.ParameterMembership"><span class="pre"><code class="sourceCode python">syside.ParameterMembership</code></span></a>

  - <a href="/python/v0.8.4/syside/ParameterMembership.md" class="reference internal" title="syside.ParameterMembership.parameter_direction"><span class="pre"><code class="sourceCode python">parameter_direction</code></span></a>

- <a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type"><span class="pre"><code class="sourceCode python">syside.Type</code></span></a>

  - <a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type.direction_of"><span class="pre"><code class="sourceCode python">direction_of</code></span></a>

</div>

<!-- -->

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">FloatFormat</span></span><a href="#syside.FloatFormat" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
<div class="pst-scrollable-table-container">

|  |  |
|----|----|
| <span class="pre">`none`</span> <a href="#syside-floatformat-none" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Exp`</span> <a href="#syside-floatformat-exp" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Prec`</span> <a href="#syside-floatformat-prec" class="reference internal"><span class="std std-ref"></span></a> |  |

</div>

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions"><span class="pre"><code class="sourceCode python">syside.FormatOptions</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.literal_real"><span class="pre"><code class="sourceCode python">literal_real</code></span></a>

</div>

<!-- -->

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">HostType</span></span><a href="#syside.HostType" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
<div class="pst-scrollable-table-container">

|  |  |
|----|----|
| <span class="pre">`none`</span> <a href="#syside-hosttype-none" class="reference internal"><span class="std std-ref"></span></a> | No host is specified. |
| <span class="pre">`Name`</span> <a href="#syside-hosttype-name" class="reference internal"><span class="std std-ref"></span></a> | A host is specified by reg-name. |
| <span class="pre">`IPv4`</span> <a href="#syside-hosttype-ipv4" class="reference internal"><span class="std std-ref"></span></a> | A host is specified by ipv4_address. |
| <span class="pre">`IPv6`</span> <a href="#syside-hosttype-ipv6" class="reference internal"><span class="std std-ref"></span></a> | A host is specified by ipv6_address. |
| <span class="pre">`IPvFuture`</span> <a href="#syside-hosttype-ipvfuture" class="reference internal"><span class="std std-ref"></span></a> | A host is specified by IPvFuture. |

</div>

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/Url.md" class="reference internal" title="syside.Url"><span class="pre"><code class="sourceCode python">syside.Url</code></span></a>

  - <a href="/python/v0.8.4/syside/Url.md" class="reference internal" title="syside.Url.host_type"><span class="pre"><code class="sourceCode python">host_type</code></span></a>

</div>

<!-- -->

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">ImplicitSpecializationKind</span></span><a href="#syside.ImplicitSpecializationKind" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
<div class="pst-scrollable-table-container">

|  |  |
|----|----|
| <span class="pre">`AccessedFeature`</span> <a href="#syside-implicitspecializationkind-accessedfeature" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`ActionTransition`</span> <a href="#syside-implicitspecializationkind-actiontransition" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`After`</span> <a href="#syside-implicitspecializationkind-after" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`AnnotatedElement`</span> <a href="#syside-implicitspecializationkind-annotatedelement" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Assumption`</span> <a href="#syside-implicitspecializationkind-assumption" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`At`</span> <a href="#syside-implicitspecializationkind-at" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Base`</span> <a href="#syside-implicitspecializationkind-base" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`BaseType`</span> <a href="#syside-implicitspecializationkind-basetype" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Binary`</span> <a href="#syside-implicitspecializationkind-binary" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`BinaryObject`</span> <a href="#syside-implicitspecializationkind-binaryobject" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`CaseActor`</span> <a href="#syside-implicitspecializationkind-caseactor" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`CheckedConstraint`</span> <a href="#syside-implicitspecializationkind-checkedconstraint" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Classifier`</span> <a href="#syside-implicitspecializationkind-classifier" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Concern`</span> <a href="#syside-implicitspecializationkind-concern" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`DataValue`</span> <a href="#syside-implicitspecializationkind-datavalue" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Decision`</span> <a href="#syside-implicitspecializationkind-decision" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Do`</span> <a href="#syside-implicitspecializationkind-do" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Effect`</span> <a href="#syside-implicitspecializationkind-effect" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`EnclosedPerformance`</span> <a href="#syside-implicitspecializationkind-enclosedperformance" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Entry`</span> <a href="#syside-implicitspecializationkind-entry" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`ExclusiveState`</span> <a href="#syside-implicitspecializationkind-exclusivestate" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Exit`</span> <a href="#syside-implicitspecializationkind-exit" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Feature`</span> <a href="#syside-implicitspecializationkind-feature" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`FeatureWrite`</span> <a href="#syside-implicitspecializationkind-featurewrite" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Flow`</span> <a href="#syside-implicitspecializationkind-flow" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Guard`</span> <a href="#syside-implicitspecializationkind-guard" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`IfThenElse`</span> <a href="#syside-implicitspecializationkind-ifthenelse" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`IncomingTransfer`</span> <a href="#syside-implicitspecializationkind-incomingtransfer" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Life`</span> <a href="#syside-implicitspecializationkind-life" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`LoopVariable`</span> <a href="#syside-implicitspecializationkind-loopvariable" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Merge`</span> <a href="#syside-implicitspecializationkind-merge" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Message`</span> <a href="#syside-implicitspecializationkind-message" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Negated`</span> <a href="#syside-implicitspecializationkind-negated" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Object`</span> <a href="#syside-implicitspecializationkind-object" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Occurrence`</span> <a href="#syside-implicitspecializationkind-occurrence" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`OwnedAction`</span> <a href="#syside-implicitspecializationkind-ownedaction" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`OwnedPerformance`</span> <a href="#syside-implicitspecializationkind-ownedperformance" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`OwnedPort`</span> <a href="#syside-implicitspecializationkind-ownedport" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Participant`</span> <a href="#syside-implicitspecializationkind-participant" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Payload`</span> <a href="#syside-implicitspecializationkind-payload" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`PerformedAction`</span> <a href="#syside-implicitspecializationkind-performedaction" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Portion`</span> <a href="#syside-implicitspecializationkind-portion" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Requirement`</span> <a href="#syside-implicitspecializationkind-requirement" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`RequirementActor`</span> <a href="#syside-implicitspecializationkind-requirementactor" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`RequirementStakeholder`</span> <a href="#syside-implicitspecializationkind-requirementstakeholder" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Satisfied`</span> <a href="#syside-implicitspecializationkind-satisfied" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Snapshot`</span> <a href="#syside-implicitspecializationkind-snapshot" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`SourceOutput`</span> <a href="#syside-implicitspecializationkind-sourceoutput" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`StartingAt`</span> <a href="#syside-implicitspecializationkind-startingat" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`StateTransition`</span> <a href="#syside-implicitspecializationkind-statetransition" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`SubAnalysisCase`</span> <a href="#syside-implicitspecializationkind-subanalysiscase" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`SubUseCase`</span> <a href="#syside-implicitspecializationkind-subusecase" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`SubVerificationCase`</span> <a href="#syside-implicitspecializationkind-subverificationcase" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Subaction`</span> <a href="#syside-implicitspecializationkind-subaction" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Subcalculation`</span> <a href="#syside-implicitspecializationkind-subcalculation" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Subcase`</span> <a href="#syside-implicitspecializationkind-subcase" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Subitem`</span> <a href="#syside-implicitspecializationkind-subitem" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Subobject`</span> <a href="#syside-implicitspecializationkind-subobject" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Suboccurrence`</span> <a href="#syside-implicitspecializationkind-suboccurrence" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Subpart`</span> <a href="#syside-implicitspecializationkind-subpart" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Subperformance`</span> <a href="#syside-implicitspecializationkind-subperformance" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Subport`</span> <a href="#syside-implicitspecializationkind-subport" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Subrendering`</span> <a href="#syside-implicitspecializationkind-subrendering" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Subrequirement`</span> <a href="#syside-implicitspecializationkind-subrequirement" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Substate`</span> <a href="#syside-implicitspecializationkind-substate" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Subview`</span> <a href="#syside-implicitspecializationkind-subview" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Target`</span> <a href="#syside-implicitspecializationkind-target" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`TargetInput`</span> <a href="#syside-implicitspecializationkind-targetinput" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Timeslice`</span> <a href="#syside-implicitspecializationkind-timeslice" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`TransitionLink`</span> <a href="#syside-implicitspecializationkind-transitionlink" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Trigger`</span> <a href="#syside-implicitspecializationkind-trigger" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Verification`</span> <a href="#syside-implicitspecializationkind-verification" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`ViewRendering`</span> <a href="#syside-implicitspecializationkind-viewrendering" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`When`</span> <a href="#syside-implicitspecializationkind-when" class="reference internal"><span class="std std-ref"></span></a> |  |

</div>

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/Stdlib.md" class="reference internal" title="syside.Stdlib"><span class="pre"><code class="sourceCode python">syside.Stdlib</code></span></a>

  - <a href="/python/v0.8.4/syside/Stdlib.md" class="reference internal" title="syside.Stdlib.implicit_supertype_for"><span class="pre"><code class="sourceCode python">implicit_supertype_for</code></span></a>

</div>

<!-- -->

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">KwToken</span></span><a href="#syside.KwToken" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
<div class="pst-scrollable-table-container">

|  |  |
|----|----|
| <span class="pre">`Token`</span> <a href="#syside-kwtoken-token" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Keyword`</span> <a href="#syside-kwtoken-keyword" class="reference internal"><span class="std std-ref"></span></a> |  |

</div>

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions"><span class="pre"><code class="sourceCode python">syside.FormatOptions</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.declaration_conjugated_port_typing"><span class="pre"><code class="sourceCode python">declaration_conjugated_port_typing</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.declaration_conjugation"><span class="pre"><code class="sourceCode python">declaration_conjugation</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.declaration_cross_subsetting"><span class="pre"><code class="sourceCode python">declaration_cross_subsetting</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.declaration_feature_typing"><span class="pre"><code class="sourceCode python">declaration_feature_typing</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.declaration_redefinition"><span class="pre"><code class="sourceCode python">declaration_redefinition</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.declaration_reference_subsetting"><span class="pre"><code class="sourceCode python">declaration_reference_subsetting</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.declaration_specialization"><span class="pre"><code class="sourceCode python">declaration_specialization</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.declaration_subclassification"><span class="pre"><code class="sourceCode python">declaration_subclassification</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.declaration_subsetting"><span class="pre"><code class="sourceCode python">declaration_subsetting</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.metadata_feature_keyword"><span class="pre"><code class="sourceCode python">metadata_feature_keyword</code></span></a>

</div>

<!-- -->

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">LineEnd</span></span><a href="#syside.LineEnd" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
<div class="pst-scrollable-table-container">

|  |  |
|----|----|
| <span class="pre">`LF`</span> <a href="#syside-lineend-lf" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`CRLF`</span> <a href="#syside-lineend-crlf" class="reference internal"><span class="std std-ref"></span></a> |  |

</div>

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/PrinterConfig.md" class="reference internal" title="syside.PrinterConfig"><span class="pre"><code class="sourceCode python">syside.PrinterConfig</code></span></a>

  - <a href="/python/v0.8.4/syside/PrinterConfig.md" class="reference internal" title="syside.PrinterConfig.__init__"><span class="pre"><code class="sourceCode python"><span class="fu">__init__</span></code></span></a>

  - <a href="/python/v0.8.4/syside/PrinterConfig.md" class="reference internal" title="syside.PrinterConfig.line_end"><span class="pre"><code class="sourceCode python">line_end</code></span></a>

</div>

<!-- -->

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">ModelLanguage</span></span><a href="#syside.ModelLanguage" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
<div class="pst-scrollable-table-container">

|  |  |
|----|----|
| <span class="pre">`KerML`</span> <a href="#syside-modellanguage-kerml" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`SysML`</span> <a href="#syside-modellanguage-sysml" class="reference internal"><span class="std std-ref"></span></a> |  |

</div>

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="#module-syside" class="reference internal" title="syside"><span class="pre"><code class="sourceCode python">syside</code></span></a>

  - <a href="#syside.build_model" class="reference internal" title="syside.build_model"><span class="pre"><code class="sourceCode python">build_model</code></span></a>

- <a href="/python/v0.8.4/syside/Document.md" class="reference internal" title="syside.Document"><span class="pre"><code class="sourceCode python">syside.Document</code></span></a>

  - <a href="/python/v0.8.4/syside/Document.md" class="reference internal" title="syside.Document.create_mt"><span class="pre"><code class="sourceCode python">create_mt</code></span></a>

  - <a href="/python/v0.8.4/syside/Document.md" class="reference internal" title="syside.Document.create_st"><span class="pre"><code class="sourceCode python">create_st</code></span></a>

  - <a href="/python/v0.8.4/syside/Document.md" class="reference internal" title="syside.Document.parse_string_mt"><span class="pre"><code class="sourceCode python">parse_string_mt</code></span></a>

  - <a href="/python/v0.8.4/syside/Document.md" class="reference internal" title="syside.Document.parse_string_st"><span class="pre"><code class="sourceCode python">parse_string_st</code></span></a>

</div>

<!-- -->

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">MultiOrder</span></span><a href="#syside.MultiOrder" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
<div class="pst-scrollable-table-container">

|  |  |
|----|----|
| <span class="pre">`Ordered`</span> <a href="#syside-multiorder-ordered" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Nonunique`</span> <a href="#syside-multiorder-nonunique" class="reference internal"><span class="std std-ref"></span></a> |  |

</div>

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions"><span class="pre"><code class="sourceCode python">syside.FormatOptions</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.ordered_nonunique_priority"><span class="pre"><code class="sourceCode python">ordered_nonunique_priority</code></span></a>

</div>

<!-- -->

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">MultiPlacement</span></span><a href="#syside.MultiPlacement" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
<div class="pst-scrollable-table-container">

|  |  |
|----|----|
| <span class="pre">`First`</span> <a href="#syside-multiplacement-first" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`FirstSpecialization`</span> <a href="#syside-multiplacement-firstspecialization" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Last`</span> <a href="#syside-multiplacement-last" class="reference internal"><span class="std std-ref"></span></a> |  |

</div>

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions"><span class="pre"><code class="sourceCode python">syside.FormatOptions</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.multiplicity_placement"><span class="pre"><code class="sourceCode python">multiplicity_placement</code></span></a>

</div>

<!-- -->

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">NameID</span></span><a href="#syside.NameID" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
<div class="pst-scrollable-table-container">

|  |  |
|----|----|
| <span class="pre">`Regular`</span> <a href="#syside-nameid-regular" class="reference internal"><span class="std std-ref"></span></a> | Reference element by its regular ID |
| <span class="pre">`Short`</span> <a href="#syside-nameid-short" class="reference internal"><span class="std std-ref"></span></a> | Reference element by its short ID |

</div>

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/DependencyEnds.md" class="reference internal" title="syside.DependencyEnds"><span class="pre"><code class="sourceCode python">syside.DependencyEnds</code></span></a>

  - <a href="/python/v0.8.4/syside/DependencyEnds.md" class="reference internal" title="syside.DependencyEnds.append"><span class="pre"><code class="sourceCode python">append</code></span></a>

  - <a href="/python/v0.8.4/syside/DependencyEnds.md" class="reference internal" title="syside.DependencyEnds.replace_at"><span class="pre"><code class="sourceCode python">replace_at</code></span></a>

</div>

<!-- -->

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">NamePreference</span></span><a href="#syside.NamePreference" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
<div class="pst-scrollable-table-container">

|  |  |
|----|----|
| <span class="pre">`Automatic`</span> <a href="#syside-namepreference-automatic" class="reference internal"><span class="std std-ref"></span></a> | Implementation defined name preference |
| <span class="pre">`Regular`</span> <a href="#syside-namepreference-regular" class="reference internal"><span class="std std-ref"></span></a> | Prefer regular name, otherwise fall back to short name |
| <span class="pre">`Short`</span> <a href="#syside-namepreference-short" class="reference internal"><span class="std std-ref"></span></a> | Prefer short name, otherwise fall back to regular name |
| <span class="pre">`Shortest`</span> <a href="#syside-namepreference-shortest" class="reference internal"><span class="std std-ref"></span></a> | Prefer shortest name |
| <span class="pre">`Longest`</span> <a href="#syside-namepreference-longest" class="reference internal"><span class="std std-ref"></span></a> | Prefer longest name (for completeness) |

</div>

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/ReferencePrinter.md" class="reference internal" title="syside.ReferencePrinter"><span class="pre"><code class="sourceCode python">syside.ReferencePrinter</code></span></a>

  - <a href="/python/v0.8.4/syside/ReferencePrinter.md" class="reference internal" title="syside.ReferencePrinter.__init__"><span class="pre"><code class="sourceCode python"><span class="fu">__init__</span></code></span></a>

</div>

<!-- -->

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">NullFormat</span></span><a href="#syside.NullFormat" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
<div class="pst-scrollable-table-container">

|  |  |
|----|----|
| <span class="pre">`Null`</span> <a href="#syside-nullformat-null" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Brackets`</span> <a href="#syside-nullformat-brackets" class="reference internal"><span class="std std-ref"></span></a> |  |

</div>

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions"><span class="pre"><code class="sourceCode python">syside.FormatOptions</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.null_expression"><span class="pre"><code class="sourceCode python">null_expression</code></span></a>

</div>

<!-- -->

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">Operator</span></span><a href="#syside.Operator" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
<div class="pst-scrollable-table-container">

|  |  |
|----|----|
| <span class="pre">`If`</span> <a href="#syside-operator-if" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`NullCoalescing`</span> <a href="#syside-operator-nullcoalescing" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Implies`</span> <a href="#syside-operator-implies" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`LogicalOr`</span> <a href="#syside-operator-logicalor" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Or`</span> <a href="#syside-operator-or" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Xor`</span> <a href="#syside-operator-xor" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`LogicalAnd`</span> <a href="#syside-operator-logicaland" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`And`</span> <a href="#syside-operator-and" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Equals`</span> <a href="#syside-operator-equals" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Same`</span> <a href="#syside-operator-same" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`NotEquals`</span> <a href="#syside-operator-notequals" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`NotSame`</span> <a href="#syside-operator-notsame" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`IsType`</span> <a href="#syside-operator-istype" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`HasType`</span> <a href="#syside-operator-hastype" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`At`</span> <a href="#syside-operator-at" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`AtAt`</span> <a href="#syside-operator-atat" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`As`</span> <a href="#syside-operator-as" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Meta`</span> <a href="#syside-operator-meta" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Less`</span> <a href="#syside-operator-less" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`LessEqual`</span> <a href="#syside-operator-lessequal" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Greater`</span> <a href="#syside-operator-greater" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`GreaterEqual`</span> <a href="#syside-operator-greaterequal" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Range`</span> <a href="#syside-operator-range" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Plus`</span> <a href="#syside-operator-plus" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Minus`</span> <a href="#syside-operator-minus" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Multiply`</span> <a href="#syside-operator-multiply" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Divide`</span> <a href="#syside-operator-divide" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Modulo`</span> <a href="#syside-operator-modulo" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`ExponentStar`</span> <a href="#syside-operator-exponentstar" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`ExponentCaret`</span> <a href="#syside-operator-exponentcaret" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Conjugation`</span> <a href="#syside-operator-conjugation" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Not`</span> <a href="#syside-operator-not" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`All`</span> <a href="#syside-operator-all" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Quantity`</span> <a href="#syside-operator-quantity" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Comma`</span> <a href="#syside-operator-comma" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Dot`</span> <a href="#syside-operator-dot" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Collect`</span> <a href="#syside-operator-collect" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Index`</span> <a href="#syside-operator-index" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Select`</span> <a href="#syside-operator-select" class="reference internal"><span class="std std-ref"></span></a> |  |

</div>

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/OperatorExpression.md" class="reference internal" title="syside.OperatorExpression"><span class="pre"><code class="sourceCode python">syside.OperatorExpression</code></span></a>

  - <a href="/python/v0.8.4/syside/OperatorExpression.md" class="reference internal" title="syside.OperatorExpression.operator"><span class="pre"><code class="sourceCode python">operator</code></span></a>

- <a href="/python/v0.8.4/syside/Stdlib.md" class="reference internal" title="syside.Stdlib"><span class="pre"><code class="sourceCode python">syside.Stdlib</code></span></a>

  - <a href="/python/v0.8.4/syside/Stdlib.md" class="reference internal" title="syside.Stdlib.operator_function_for"><span class="pre"><code class="sourceCode python">operator_function_for</code></span></a>

</div>

<!-- -->

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">OperatorBreak</span></span><a href="#syside.OperatorBreak" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
<div class="pst-scrollable-table-container">

|  |  |
|----|----|
| <span class="pre">`Before`</span> <a href="#syside-operatorbreak-before" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`After`</span> <a href="#syside-operatorbreak-after" class="reference internal"><span class="std std-ref"></span></a> |  |

</div>

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions"><span class="pre"><code class="sourceCode python">syside.FormatOptions</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.operator_break"><span class="pre"><code class="sourceCode python">operator_break</code></span></a>

</div>

<!-- -->

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">OptionalKw</span></span><a href="#syside.OptionalKw" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
<div class="pst-scrollable-table-container">

|  |  |
|----|----|
| <span class="pre">`Always`</span> <a href="#syside-optionalkw-always" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`AsNeeded`</span> <a href="#syside-optionalkw-asneeded" class="reference internal"><span class="std std-ref"></span></a> |  |

</div>

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions"><span class="pre"><code class="sourceCode python">syside.FormatOptions</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.action_node_keyword"><span class="pre"><code class="sourceCode python">action_node_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.allocation_usage_keyword"><span class="pre"><code class="sourceCode python">allocation_usage_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.assert_constraint_usage_keyword"><span class="pre"><code class="sourceCode python">assert_constraint_usage_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.binary_binding_connector_of_keyword"><span class="pre"><code class="sourceCode python">binary_binding_connector_of_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.binary_connectors_from_keyword"><span class="pre"><code class="sourceCode python">binary_connectors_from_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.binary_succession_first_keyword"><span class="pre"><code class="sourceCode python">binary_succession_first_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.binding_connector_as_usage_keyword"><span class="pre"><code class="sourceCode python">binding_connector_as_usage_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.comment_about_break"><span class="pre"><code class="sourceCode python">comment_about_break</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.comment_keyword"><span class="pre"><code class="sourceCode python">comment_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.conjugation_keyword"><span class="pre"><code class="sourceCode python">conjugation_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.connection_usage_keyword"><span class="pre"><code class="sourceCode python">connection_usage_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.dependency_from_keyword"><span class="pre"><code class="sourceCode python">dependency_from_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.disjoining_keyword"><span class="pre"><code class="sourceCode python">disjoining_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.event_occurrence_keyword"><span class="pre"><code class="sourceCode python">event_occurrence_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.exhibit_state_usage_keyword"><span class="pre"><code class="sourceCode python">exhibit_state_usage_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.feature_keyword"><span class="pre"><code class="sourceCode python">feature_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.feature_value_equals"><span class="pre"><code class="sourceCode python">feature_value_equals</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.featuring_of_keyword"><span class="pre"><code class="sourceCode python">featuring_of_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.flow_from_keyword"><span class="pre"><code class="sourceCode python">flow_from_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.flow_usage_from_keyword"><span class="pre"><code class="sourceCode python">flow_usage_from_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.framed_concern_keyword"><span class="pre"><code class="sourceCode python">framed_concern_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.include_use_case_usage_keyword"><span class="pre"><code class="sourceCode python">include_use_case_usage_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.interface_usage_connect_keyword"><span class="pre"><code class="sourceCode python">interface_usage_connect_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.inverting_keyword"><span class="pre"><code class="sourceCode python">inverting_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.occurrence_keyword"><span class="pre"><code class="sourceCode python">occurrence_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.perform_action_usage_keyword"><span class="pre"><code class="sourceCode python">perform_action_usage_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.reference_usage_keyword"><span class="pre"><code class="sourceCode python">reference_usage_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.satisfy_requirement_keyword"><span class="pre"><code class="sourceCode python">satisfy_requirement_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.specialization_keyword_feature_typing"><span class="pre"><code class="sourceCode python">specialization_keyword_feature_typing</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.specialization_keyword_redefinition"><span class="pre"><code class="sourceCode python">specialization_keyword_redefinition</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.specialization_keyword_specialization"><span class="pre"><code class="sourceCode python">specialization_keyword_specialization</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.specialization_keyword_subclassification"><span class="pre"><code class="sourceCode python">specialization_keyword_subclassification</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.specialization_keyword_subsetting"><span class="pre"><code class="sourceCode python">specialization_keyword_subsetting</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.succession_as_usage_keyword"><span class="pre"><code class="sourceCode python">succession_as_usage_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.succession_flow_from_keyword"><span class="pre"><code class="sourceCode python">succession_flow_from_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.succession_flow_usage_from_keyword"><span class="pre"><code class="sourceCode python">succession_flow_usage_from_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.textual_representation_keyword"><span class="pre"><code class="sourceCode python">textual_representation_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.textual_representation_language_break"><span class="pre"><code class="sourceCode python">textual_representation_language_break</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.transition_usage_first_keyword"><span class="pre"><code class="sourceCode python">transition_usage_first_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.transition_usage_keyword"><span class="pre"><code class="sourceCode python">transition_usage_keyword</code></span></a>

</div>

<!-- -->

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">OptionalKwToken</span></span><a href="#syside.OptionalKwToken" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
<div class="pst-scrollable-table-container">

|  |  |
|----|----|
| <span class="pre">`Token`</span> <a href="#syside-optionalkwtoken-token" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Keyword`</span> <a href="#syside-optionalkwtoken-keyword" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`none`</span> <a href="#syside-optionalkwtoken-none" class="reference internal"><span class="std std-ref"></span></a> |  |

</div>

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions"><span class="pre"><code class="sourceCode python">syside.FormatOptions</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.metadata_body_feature_redefines"><span class="pre"><code class="sourceCode python">metadata_body_feature_redefines</code></span></a>

</div>

<!-- -->

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">OptionalToken</span></span><a href="#syside.OptionalToken" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
<div class="pst-scrollable-table-container">

|  |  |
|----|----|
| <span class="pre">`Never`</span> <a href="#syside-optionaltoken-never" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Always`</span> <a href="#syside-optionaltoken-always" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`OnBreak`</span> <a href="#syside-optionaltoken-onbreak" class="reference internal"><span class="std std-ref"></span></a> |  |

</div>

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions"><span class="pre"><code class="sourceCode python">syside.FormatOptions</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.element_filter_parenthesize"><span class="pre"><code class="sourceCode python">element_filter_parenthesize</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.if_parenthesize_condition"><span class="pre"><code class="sourceCode python">if_parenthesize_condition</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.sequence_expression_trailing_comma"><span class="pre"><code class="sourceCode python">sequence_expression_trailing_comma</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.transition_usage_parenthesize_guard"><span class="pre"><code class="sourceCode python">transition_usage_parenthesize_guard</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.while_loop_parenthesize_condition"><span class="pre"><code class="sourceCode python">while_loop_parenthesize_condition</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.while_loop_parenthesize_until"><span class="pre"><code class="sourceCode python">while_loop_parenthesize_until</code></span></a>

</div>

<!-- -->

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">PortionKind</span></span><a href="#syside.PortionKind" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
<span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span>

Implementation of <span class="pre">`PortionKind`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> <span class="pre">`PortionKind`</span> is an enumeration of the specific kinds of <span class="pre">`Occurrence`</span> portions that can be represented by an <span class="pre">`OccurrenceUsage`</span>.
>
> </div>

For language description, see section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=84" class="reference external" target="_blank">7.9.3</a> of the SysML specification. For more details on the model, see section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=320" class="reference external" target="_blank">8.3.9.5</a> of the SysML specification.

<div class="pst-scrollable-table-container">

|  |  |
|----|----|
| <span class="pre">`Timeslice`</span> <a href="#syside-portionkind-timeslice" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Snapshot`</span> <a href="#syside-portionkind-snapshot" class="reference internal"><span class="std std-ref"></span></a> |  |

</div>

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/ConnectionUsage.md" class="reference internal" title="syside.ConnectionUsage"><span class="pre"><code class="sourceCode python">syside.ConnectionUsage</code></span></a>

  - <a href="/python/v0.8.4/syside/ConnectionUsage.md" class="reference internal" title="syside.ConnectionUsage.portion_kind"><span class="pre"><code class="sourceCode python">portion_kind</code></span></a>

- <a href="/python/v0.8.4/syside/FlowUsage.md" class="reference internal" title="syside.FlowUsage"><span class="pre"><code class="sourceCode python">syside.FlowUsage</code></span></a>

  - <a href="/python/v0.8.4/syside/FlowUsage.md" class="reference internal" title="syside.FlowUsage.portion_kind"><span class="pre"><code class="sourceCode python">portion_kind</code></span></a>

- <a href="/python/v0.8.4/syside/OccurrenceUsage.md" class="reference internal" title="syside.OccurrenceUsage"><span class="pre"><code class="sourceCode python">syside.OccurrenceUsage</code></span></a>

  - <a href="/python/v0.8.4/syside/OccurrenceUsage.md" class="reference internal" title="syside.OccurrenceUsage.portion_kind"><span class="pre"><code class="sourceCode python">portion_kind</code></span></a>

</div>

<!-- -->

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">PrintMode</span></span><a href="#syside.PrintMode" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
<div class="pst-scrollable-table-container">

|  |  |
|----|----|
| <span class="pre">`KerML`</span> <a href="#syside-printmode-kerml" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`SysML`</span> <a href="#syside-printmode-sysml" class="reference internal"><span class="std std-ref"></span></a> |  |

</div>

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/ModelPrinter.md" class="reference internal" title="syside.ModelPrinter"><span class="pre"><code class="sourceCode python">syside.ModelPrinter</code></span></a>

  - <a href="/python/v0.8.4/syside/ModelPrinter.md" class="reference internal" title="syside.ModelPrinter.mode"><span class="pre"><code class="sourceCode python">mode</code></span></a>

</div>

<!-- -->

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">RequirementConstraintKind</span></span><a href="#syside.RequirementConstraintKind" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
<span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span>

Implementation of <span class="pre">`RequirementConstraintKind`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> A <span class="pre">`RequirementConstraintKind`</span> indicates whether a <span class="pre">`ConstraintUsage`</span> is an assumption or a requirement in a <span class="pre">`RequirementDefinition`</span> or <span class="pre">`RequirementUsage`</span>.
>
> </div>

For language description, see section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=164" class="reference external" target="_blank">7.21.2</a> of the SysML specification. For more details on the model, see section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=389" class="reference external" target="_blank">8.3.21.6</a> of the SysML specification.

<div class="pst-scrollable-table-container">

|  |  |
|----|----|
| <span class="pre">`Assumption`</span> <a href="#syside-requirementconstraintkind-assumption" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Requirement`</span> <a href="#syside-requirementconstraintkind-requirement" class="reference internal"><span class="std std-ref"></span></a> |  |

</div>

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/RequirementConstraintMembership.md" class="reference internal" title="syside.RequirementConstraintMembership"><span class="pre"><code class="sourceCode python">syside.RequirementConstraintMembership</code></span></a>

  - <a href="/python/v0.8.4/syside/RequirementConstraintMembership.md" class="reference internal" title="syside.RequirementConstraintMembership.kind"><span class="pre"><code class="sourceCode python">kind</code></span></a>

  - <a href="/python/v0.8.4/syside/RequirementConstraintMembership.md" class="reference internal" title="syside.RequirementConstraintMembership.try_set_kind"><span class="pre"><code class="sourceCode python">try_set_kind</code></span></a>

</div>

<!-- -->

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">Scheme</span></span><a href="#syside.Scheme" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
<div class="pst-scrollable-table-container">

<table class="table">
<colgroup>
<col style="width: 50%" />
<col style="width: 50%" />
</colgroup>
<tbody>
<tr class="row-odd">
<td><p><span class="pre"><code class="docutils literal notranslate">none</code></span> <a href="#syside-scheme-none" class="reference internal"><span class="std std-ref"></span></a></p></td>
<td><p>Indicates that no scheme is present</p></td>
</tr>
<tr class="row-even">
<td><p><span class="pre"><code class="docutils literal notranslate">Unknown</code></span> <a href="#syside-scheme-unknown" class="reference internal"><span class="std std-ref"></span></a></p></td>
<td><p>Indicates the scheme is not a well-known scheme</p></td>
</tr>
<tr class="row-odd">
<td><p><span class="pre"><code class="docutils literal notranslate">Ftp</code></span> <a href="#syside-scheme-ftp" class="reference internal"><span class="std std-ref"></span></a></p></td>
<td><p>File Transfer Protocol (FTP)</p>
<p>FTP is a standard communication protocol used for the transfer of computer files from a server to a client on a computer network.</p></td>
</tr>
<tr class="row-even">
<td><p><span class="pre"><code class="docutils literal notranslate">File</code></span> <a href="#syside-scheme-file" class="reference internal"><span class="std std-ref"></span></a></p></td>
<td><p>File URI Scheme</p>
<p>The File URI Scheme is typically used to retrieve files from within one’s own computer.</p></td>
</tr>
<tr class="row-odd">
<td><p><span class="pre"><code class="docutils literal notranslate">Http</code></span> <a href="#syside-scheme-http" class="reference internal"><span class="std std-ref"></span></a></p></td>
<td><p>The Hypertext Transfer Protocol URI Scheme</p>
<p>URLs of this type indicate a resource which is interacted with using the HTTP protocol.</p></td>
</tr>
<tr class="row-even">
<td><p><span class="pre"><code class="docutils literal notranslate">Https</code></span> <a href="#syside-scheme-https" class="reference internal"><span class="std std-ref"></span></a></p></td>
<td><p>The Secure Hypertext Transfer Protocol URI Scheme</p>
<p>URLs of this type indicate a resource which is interacted with using the Secure HTTP protocol.</p></td>
</tr>
<tr class="row-odd">
<td><p><span class="pre"><code class="docutils literal notranslate">Ws</code></span> <a href="#syside-scheme-ws" class="reference internal"><span class="std std-ref"></span></a></p></td>
<td><p>The WebSocket URI Scheme</p>
<p>URLs of this type indicate a resource which is interacted with using the WebSocket protocol.</p></td>
</tr>
<tr class="row-even">
<td><p><span class="pre"><code class="docutils literal notranslate">Wss</code></span> <a href="#syside-scheme-wss" class="reference internal"><span class="std std-ref"></span></a></p></td>
<td><p>The Secure WebSocket URI Scheme</p>
<p>URLs of this type indicate a resource which is interacted with using the Secure WebSocket protocol.</p></td>
</tr>
</tbody>
</table>

</div>

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/Url.md" class="reference internal" title="syside.Url"><span class="pre"><code class="sourceCode python">syside.Url</code></span></a>

  - <a href="/python/v0.8.4/syside/Url.md" class="reference internal" title="syside.Url.scheme_id"><span class="pre"><code class="sourceCode python">scheme_id</code></span></a>

  - <a href="/python/v0.8.4/syside/Url.md" class="reference internal" title="syside.Url.set_scheme_id"><span class="pre"><code class="sourceCode python">set_scheme_id</code></span></a>

</div>

<!-- -->

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">SemaState</span></span><a href="#syside.SemaState" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Semantic resolution state of <span class="pre">`Elements`</span>. Sema will use this information to discard duplicate work, e.g. when resolving elements in a group of related documents.

<div class="pst-scrollable-table-container">

|  |  |
|----|----|
| <span class="pre">`none`</span> <a href="#syside-semastate-none" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Active`</span> <a href="#syside-semastate-active" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Resolved`</span> <a href="#syside-semastate-resolved" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Cached`</span> <a href="#syside-semastate-cached" class="reference internal"><span class="std std-ref"></span></a> |  |

</div>

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element"><span class="pre"><code class="sourceCode python">syside.Element</code></span></a>

  - <a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element.sema_state"><span class="pre"><code class="sourceCode python">sema_state</code></span></a>

</div>

<!-- -->

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">StateSubactionKind</span></span><a href="#syside.StateSubactionKind" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
<span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span>

Implementation of <span class="pre">`StateSubactionKind`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> A <span class="pre">`StateSubactionKind`</span> indicates whether the <span class="pre">`action`</span> of a StateSubactionMembership is an entry, do or exit action.
>
> </div>

For language description, see section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=149" class="reference external" target="_blank">7.18.2</a> of the SysML specification. For more details on the model, see section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=367" class="reference external" target="_blank">8.3.18.3</a> of the SysML specification.

<div class="pst-scrollable-table-container">

|  |  |
|----|----|
| <span class="pre">`Entry`</span> <a href="#syside-statesubactionkind-entry" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Do`</span> <a href="#syside-statesubactionkind-do" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Exit`</span> <a href="#syside-statesubactionkind-exit" class="reference internal"><span class="std std-ref"></span></a> |  |

</div>

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/StateSubactionMembership.md" class="reference internal" title="syside.StateSubactionMembership"><span class="pre"><code class="sourceCode python">syside.StateSubactionMembership</code></span></a>

  - <a href="/python/v0.8.4/syside/StateSubactionMembership.md" class="reference internal" title="syside.StateSubactionMembership.kind"><span class="pre"><code class="sourceCode python">kind</code></span></a>

</div>

<!-- -->

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">TextDocumentSaveReason</span></span><a href="#syside.TextDocumentSaveReason" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
<div class="pst-scrollable-table-container">

|  |  |
|----|----|
| <span class="pre">`Manual`</span> <a href="#syside-textdocumentsavereason-manual" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`AfterDelay`</span> <a href="#syside-textdocumentsavereason-afterdelay" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`FocusOut`</span> <a href="#syside-textdocumentsavereason-focusout" class="reference internal"><span class="std std-ref"></span></a> |  |

</div>

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/TextDocuments.md" class="reference internal" title="syside.TextDocuments"><span class="pre"><code class="sourceCode python">syside.TextDocuments</code></span></a>

  - <a href="/python/v0.8.4/syside/TextDocuments.md" class="reference internal" title="syside.TextDocuments.will_save"><span class="pre"><code class="sourceCode python">will_save</code></span></a>

  - <a href="/python/v0.8.4/syside/TextDocuments.md" class="reference internal" title="syside.TextDocuments.will_save_wait_until"><span class="pre"><code class="sourceCode python">will_save_wait_until</code></span></a>

</div>

<!-- -->

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">TransitionFeatureKind</span></span><a href="#syside.TransitionFeatureKind" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
<span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span>

Implementation of <span class="pre">`TransitionFeatureKind`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> A <span class="pre">`TransitionActionKind`</span> indicates whether the <span class="pre">`transition_feature`</span> of a <span class="pre">`TransitionFeatureMembership`</span> is a trigger, guard or effect.
>
> </div>

For language description, see section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=150" class="reference external" target="_blank">7.18.3</a> of the SysML specification. For more details on the model, see section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=373" class="reference external" target="_blank">8.3.18.7</a> of the SysML specification.

<div class="pst-scrollable-table-container">

|  |  |
|----|----|
| <span class="pre">`Trigger`</span> <a href="#syside-transitionfeaturekind-trigger" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Guard`</span> <a href="#syside-transitionfeaturekind-guard" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Effect`</span> <a href="#syside-transitionfeaturekind-effect" class="reference internal"><span class="std std-ref"></span></a> |  |

</div>

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/TransitionFeatureMembership.md" class="reference internal" title="syside.TransitionFeatureMembership"><span class="pre"><code class="sourceCode python">syside.TransitionFeatureMembership</code></span></a>

  - <a href="/python/v0.8.4/syside/TransitionFeatureMembership.md" class="reference internal" title="syside.TransitionFeatureMembership.kind"><span class="pre"><code class="sourceCode python">kind</code></span></a>

</div>

<!-- -->

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">TreeDrawing</span></span><a href="#syside.TreeDrawing" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
<div class="pst-scrollable-table-container">

|  |  |
|----|----|
| <span class="pre">`No`</span> <a href="#syside-treedrawing-no" class="reference internal"><span class="std std-ref"></span></a> | No tree is drawn |
| <span class="pre">`Ascii`</span> <a href="#syside-treedrawing-ascii" class="reference internal"><span class="std std-ref"></span></a> | Use ASCII symbols for drawing |
| <span class="pre">`Unicode`</span> <a href="#syside-treedrawing-unicode" class="reference internal"><span class="std std-ref"></span></a> | Use unicode symbols for drawing |

</div>

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/DiagnosticFormatOptions.md" class="reference internal" title="syside.DiagnosticFormatOptions"><span class="pre"><code class="sourceCode python">syside.DiagnosticFormatOptions</code></span></a>

  - <a href="/python/v0.8.4/syside/DiagnosticFormatOptions.md" class="reference internal" title="syside.DiagnosticFormatOptions.__init__"><span class="pre"><code class="sourceCode python"><span class="fu">__init__</span></code></span></a>

  - <a href="/python/v0.8.4/syside/DiagnosticFormatOptions.md" class="reference internal" title="syside.DiagnosticFormatOptions.draw_tree"><span class="pre"><code class="sourceCode python">draw_tree</code></span></a>

</div>

<!-- -->

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">TriggerKind</span></span><a href="#syside.TriggerKind" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
<span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span>

Implementation of <span class="pre">`TriggerKind`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> <span class="pre">`TriggerKind`</span> enumerates the kinds of triggers that can be represented by a <span class="pre">`TriggerInvocationExpression`</span>.
>
> </div>

For language description, see section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=150" class="reference external" target="_blank">7.18.3</a> of the SysML specification. For more details on the model, see section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=363" class="reference external" target="_blank">8.3.17.18</a> of the SysML specification.

<div class="pst-scrollable-table-container">

|  |  |
|----|----|
| <span class="pre">`When`</span> <a href="#syside-triggerkind-when" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`At`</span> <a href="#syside-triggerkind-at" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`After`</span> <a href="#syside-triggerkind-after" class="reference internal"><span class="std std-ref"></span></a> |  |

</div>

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/TriggerInvocationExpression.md" class="reference internal" title="syside.TriggerInvocationExpression"><span class="pre"><code class="sourceCode python">syside.TriggerInvocationExpression</code></span></a>

  - <a href="/python/v0.8.4/syside/TriggerInvocationExpression.md" class="reference internal" title="syside.TriggerInvocationExpression.kind"><span class="pre"><code class="sourceCode python">kind</code></span></a>

</div>

<!-- -->

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">ValidationTiming</span></span><a href="#syside.ValidationTiming" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
<div class="pst-scrollable-table-container">

|  |  |
|----|----|
| <span class="pre">`OnType`</span> <a href="#syside-validationtiming-ontype" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`OnSave`</span> <a href="#syside-validationtiming-onsave" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Manual`</span> <a href="#syside-validationtiming-manual" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Never`</span> <a href="#syside-validationtiming-never" class="reference internal"><span class="std std-ref"></span></a> |  |

</div>

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/ScheduleOptions.md" class="reference internal" title="syside.ScheduleOptions"><span class="pre"><code class="sourceCode python">syside.ScheduleOptions</code></span></a>

  - <a href="/python/v0.8.4/syside/ScheduleOptions.md" class="reference internal" title="syside.ScheduleOptions.__init__"><span class="pre"><code class="sourceCode python"><span class="fu">__init__</span></code></span></a>

  - <a href="/python/v0.8.4/syside/ScheduleOptions.md" class="reference internal" title="syside.ScheduleOptions.validation_timing"><span class="pre"><code class="sourceCode python">validation_timing</code></span></a>

</div>

<!-- -->

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">VisibilityKind</span></span><a href="#syside.VisibilityKind" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
<span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span>

Implementation of <span class="pre">`VisibilityKind`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> <span class="pre">`VisibilityKind`</span> is an enumeration whose literals specify the visibility of a <span class="pre">`Membership`</span> of an <span class="pre">`Element`</span> in a <span class="pre">`Namespace`</span> outside of that <span class="pre">`Namespace`</span>. Note that “visibility” specifically restricts whether an <span class="pre">`Element`</span> in a <span class="pre">`Namespace`</span> may be referenced by name from outside the <span class="pre">`Namespace`</span> and only otherwise restricts access to an <span class="pre">`Element`</span> as provided by specific constraints in the abstract syntax (e.g., preventing the import or inheritance of private <span class="pre">`Elements`</span>).
>
> </div>

For language description, see section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=47" class="reference external" target="_blank">7.2.5.2</a> of the KerML specification. For more details on the model, see section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=161" class="reference external" target="_blank">8.3.2.4.7</a> of the KerML specification.

<div class="pst-scrollable-table-container">

|  |  |
|----|----|
| <span class="pre">`Private`</span> <a href="#syside-visibilitykind-private" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Protected`</span> <a href="#syside-visibilitykind-protected" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Public`</span> <a href="#syside-visibilitykind-public" class="reference internal"><span class="std std-ref"></span></a> |  |

</div>

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/Relationship.md" class="reference internal" title="syside.Relationship"><span class="pre"><code class="sourceCode python">syside.Relationship</code></span></a>

  - <a href="/python/v0.8.4/syside/Relationship.md" class="reference internal" title="syside.Relationship.try_set_visibility"><span class="pre"><code class="sourceCode python">try_set_visibility</code></span></a>

  - <a href="/python/v0.8.4/syside/Relationship.md" class="reference internal" title="syside.Relationship.visibility"><span class="pre"><code class="sourceCode python">visibility</code></span></a>

</div>

<!-- -->

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">VisitAction</span></span><a href="#syside.VisitAction" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
<div class="pst-scrollable-table-container">

|  |  |
|----|----|
| <span class="pre">`Continue`</span> <a href="#syside-visitaction-continue" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Stop`</span> <a href="#syside-visitaction-stop" class="reference internal"><span class="std std-ref"></span></a> |  |

</div>

<div class="toctree-wrapper compound">

</div>

<div class="toctree-wrapper compound">

</div>

</div>

</div>
