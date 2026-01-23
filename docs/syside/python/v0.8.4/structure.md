<div id="model-structure" class="section">

# Model Structure<a href="#model-structure" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

A <a href="/python/v0.8.4/syside/Document.md" class="reference internal" title="syside.Document"><span class="pre"><code class="sourceCode python">Document</code></span></a> is the smallest atomic model piece in Syside which corresponds to a single source file. For performance reasons, any <a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element"><span class="pre"><code class="sourceCode python">Elements</code></span></a> are allocated and destroyed by the owning <a href="/python/v0.8.4/syside/Document.md" class="reference internal" title="syside.Document"><span class="pre"><code class="sourceCode python">Document</code></span></a>. See <a href="/python/v0.8.4/low-level.md" class="reference internal"><span class="doc">Low-Level API</span></a> for more details.

Because Syside is developed with multithreading in mind, each <a href="/python/v0.8.4/syside/Document.md" class="reference internal" title="syside.Document"><span class="pre"><code class="sourceCode python">Document</code></span></a> is protected by a mutex even if it is a noop in single-threaded environments. This is carried over into Python to provide identical API access for potential <a href="https://docs.python.org/3/howto/free-threading-python.html" class="reference external" target="_blank">free-threaded Python</a> builds in the future.

<div class="admonition note">

Note

For ease-of-use, accessing all referenced elements and their documents does not require locking. Instead, any editor-like applications need to lock all related documents explicitly together to prevent races. This is done in Syside LSP implementation.

</div>

Locking happens through <a href="https://docs.python.org/3/reference/datamodel.html#context-managers" class="reference external" target="_blank">context manager</a> interface on <a href="/python/v0.8.4/syside/SharedMutex.md" class="reference internal" title="syside.SharedMutex"><span class="pre"><code class="sourceCode python">SharedMutex</code></span></a>:

<div class="highlight-py notranslate">

<div class="highlight">

    with mutex.lock() as doc:
        pass

</div>

</div>

Locking multiple mutexes needs <a href="https://docs.python.org/3/library/contextlib.html#contextlib.ExitStack" class="reference external" target="_blank">ExitStack</a>:

<div class="highlight-py notranslate">

<div class="highlight">

    from contextlib import ExitStack

    with ExitStack() as stack:
        documents = [stack.enter_context(mutex.lock()) for mutex in mutexes]

</div>

</div>

<div class="admonition note">

Note

<a href="/python/v0.8.4/syside/preview//README.md" class="reference internal" title="syside.preview.open_model"><span class="pre"><code class="sourceCode python">preview.open_model</code></span></a> takes care of locking mutexes but its interface may be incomplete and change more frequently.

</div>

<div class="admonition note">

Note

It is recommended to write your analysis code methods as taking <a href="/python/v0.8.4/syside/Document.md" class="reference internal" title="syside.Document"><span class="pre"><code class="sourceCode python">Documents</code></span></a> rather than <a href="/python/v0.8.4/syside/SharedMutex.md" class="reference internal" title="syside.SharedMutex"><span class="pre"><code class="sourceCode python">SharedMutex[syside.Document]</code></span></a> – locking is only needed at the script or thread entry points. This is how Syside does it internally.

</div>

<div id="types" class="section">

## Types<a href="#types" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

The model types follows KerML and SysML specifications, with types mapping one-to-one to Syside types, see <a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element"><span class="pre"><code class="sourceCode python">Element</code></span></a> and its children.

<div class="admonition note">

Note

For performance reasons, the model does not use interface base classes and multiple inheritance. While all missing specification attributes are implemented even if a corresponding class is not a base, <span class="pre">`isinstance`</span> checks may work differently than expected from the specification types. Instead, use <span class="pre">`STD`</span> class variables, e.g. <a href="/python/v0.8.4/syside/ActionUsage.md" class="reference internal" title="syside.ActionUsage.STD"><span class="pre"><code class="sourceCode python">ActionUsage.STD</code></span></a>, to match specification behaviour:

<div class="highlight-py notranslate">

<div class="highlight">

    if isinstance(element, syside.ActionUsage.STD):
        ...

</div>

</div>

For type-checking, there is a corresponding <span class="pre">`Std`</span> class type alias that is only defined during <a href="https://docs.python.org/3/library/typing.html#typing.TYPE_CHECKING" class="reference external" target="_blank">TYPE_CHECKING</a>:

<div class="highlight-py notranslate">

<div class="highlight">

    def example(element: syside.Element) -> syside.Connector.Std:
        return element.cast(syside.Connector.STD)

</div>

</div>

This distinction is required due to limitations of the Python type system which does not allow type aliases and variables to be bound to the same name.

</div>

<div id="attributes" class="section">

### Attributes<a href="#attributes" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

Throughout the API, all attributes and methods use <span class="pre">`snake_casing`</span> to match Python naming convention. This is in contrast to <span class="pre">`camelCasing`</span> used by the specification coming from Java naming conventions. For example, attribute <span class="pre">`AssertConstraintUsage::assertedConstraint`</span> is mapped to <a href="/python/v0.8.4/syside/AssertConstraintUsage.md" class="reference internal" title="syside.AssertConstraintUsage.asserted_constraint"><span class="pre"><code class="sourceCode python">AssertConstraintUsage.asserted_constraint</code></span></a>.

Additionally, even if an attribute is defined as returning something in the specification, i.e. with a multiplicity lower bound of 1, Syside usually returns an optional value. This is because for IDE analysis, even partial models are useful, and they often have syntax errors which result in required members not being present. Additionally, attributes that can return multiple values often return <a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre"><code class="sourceCode python">LazyIterator</code></span></a> instead which traverses and collects elements lazily – elements instead need to be collected by calling <a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator.collect"><span class="pre"><code class="sourceCode python">.collect()</code></span></a>, e.g. on <a href="/python/v0.8.4/syside/Namespace.md" class="reference internal" title="syside.Namespace.owned_members"><span class="pre"><code class="sourceCode python">Namespace.owned_members</code></span></a>.

Lastly, <a href="/python/v0.8.4/syside/AstNode.md" class="reference internal" title="syside.AstNode"><span class="pre"><code class="sourceCode python">AstNode</code></span></a> provides some convenience attributes:

- <a href="/python/v0.8.4/syside/AstNode.md" class="reference internal" title="syside.AstNode.cast"><span class="pre"><code class="sourceCode python">cast</code></span></a> and <a href="/python/v0.8.4/syside/AstNode.md" class="reference internal" title="syside.AstNode.try_cast"><span class="pre"><code class="sourceCode python">try_cast</code></span></a> methods for casting the node to a specific type.

- <a href="/python/v0.8.4/syside/AstNode.md" class="reference internal" title="syside.AstNode.document"><span class="pre"><code class="sourceCode python">document</code></span></a> attribute for accessing the document the node belongs to.

- <a href="/python/v0.8.4/syside/AstNode.md" class="reference internal" title="syside.AstNode.parent"><span class="pre"><code class="sourceCode python">parent</code></span></a> attribute for accessing the parent node.

- <a href="/python/v0.8.4/syside/AstNode.md" class="reference internal" title="syside.AstNode.isinstance"><span class="pre"><code class="sourceCode python"><span class="bu">isinstance</span></code></span></a> method for checking if the node is an instance of a specific type.

- <a href="/python/v0.8.4/syside/AstNode.md" class="reference internal" title="syside.AstNode.owned_elements"><span class="pre"><code class="sourceCode python">owned_elements</code></span></a> attribute for accessing the owned elements of the node.

- <a href="/python/v0.8.4/syside/AstNode.md" class="reference internal" title="syside.AstNode.cst_node"><span class="pre"><code class="sourceCode python">cst_node</code></span></a> attribute for accessing the <a href="https://en.wikipedia.org/wiki/Parse_tree" class="reference external" target="_blank">concrete syntax</a> node corresponding to the node.

  <div class="admonition warning">

  Warning

  This should not be stored for long as it may go out of scope and be deleted after a document is reparsed.

  </div>

</div>

</div>

<div id="modifications" class="section">

## Modifications<a href="#modifications" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

Syside tries to enforce the invariant that all owned relationships have at least two related elements. This is achieved by requiring the relationship type when adding any child elements or references which also allows checking that the related element type is valid for that relationship.

For convenient modification of the model, Syside provides a set of additional properties and methods on the abstract syntax classes. Most commonly used ones are:

- <a href="/python/v0.8.4/syside/Namespace.md" class="reference internal" title="syside.Namespace.children"><span class="pre"><code class="sourceCode python">Namespace.children</code></span></a> and <a href="/python/v0.8.4/syside/Dependency.md" class="reference internal" title="syside.Dependency.children"><span class="pre"><code class="sourceCode python">Dependency.children</code></span></a> (including other specific relationships) represent and allow modifying elements in the body of the element – in the textual notation, between brackets <span class="pre">`{`</span> and <span class="pre">`}`</span> and expression arguments, e.g.:

  <div class="highlight-py notranslate">

  <div class="highlight">

      mem, element = namespace.children.append(
          syside.OwningMembership, syside.Package
      )
      assert namespace.children.remove_element(element)
      assert not mem.parent

  </div>

  </div>

- <a href="/python/v0.8.4/syside/Namespace.md" class="reference internal" title="syside.Namespace.prefixes"><span class="pre"><code class="sourceCode python">Namespace.prefixes</code></span></a> and <a href="/python/v0.8.4/syside/Dependency.md" class="reference internal" title="syside.Dependency.prefixes"><span class="pre"><code class="sourceCode python">Dependency.prefixes</code></span></a> represent a group for metadata prefixes, prefixed with <span class="pre">`#`</span> in textual notation.

- <a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type.type_relationships"><span class="pre"><code class="sourceCode python">Type.type_relationships</code></span></a> represents non-specialization type relationships appearing after specialization part, including feature chaining.

- <a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type.heritage"><span class="pre"><code class="sourceCode python">Type.heritage</code></span></a> represents specialization and conjugation type relationships.

- <a href="/python/v0.8.4/syside/Connector.md" class="reference internal" title="syside.Connector.declared_ends"><span class="pre"><code class="sourceCode python">Connector.declared_ends</code></span></a> and <a href="/python/v0.8.4/syside/FlowUsage.md" class="reference internal" title="syside.FlowUsage.declared_messages"><span class="pre"><code class="sourceCode python">FlowUsage.declared_messages</code></span></a> are end features and messages before the <span class="pre">`children`</span> group. In the textual syntax they appear in the same position, hence in contrast to similar groups there are additional <a href="/python/v0.8.4/syside/ConnectorEndsAccessor.md" class="reference internal" title="syside.ConnectorEndsAccessor.try_append"><span class="pre"><code class="sourceCode python">try_append</code></span></a> and <a href="/python/v0.8.4/syside/ConnectorEndsAccessor.md" class="reference internal" title="syside.ConnectorEndsAccessor.try_insert"><span class="pre"><code class="sourceCode python">try_insert</code></span></a> methods that return <span class="pre">`None`</span> without throwing if modification failed because the slot is already occupied by another group.

- Members with specific positions in the textual syntax are often modifiable through <span class="pre">`_member`</span> properties, e.g. <a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature.feature_value_member"><span class="pre"><code class="sourceCode python">feature_value_member</code></span></a>. Commons accessors are <a href="/python/v0.8.4/syside/MemberAccessor.md" class="reference internal" title="syside.MemberAccessor"><span class="pre"><code class="sourceCode python">MemberAccessor</code></span></a> for working with non-owned member elements, <a href="/python/v0.8.4/syside/OwnedMemberAccessor.md" class="reference internal" title="syside.OwnedMemberAccessor"><span class="pre"><code class="sourceCode python">OwnedMemberAccessor</code></span></a> – for working with owned member elements, and <a href="/python/v0.8.4/syside/ChainedMemberAccessor.md" class="reference internal" title="syside.ChainedMemberAccessor"><span class="pre"><code class="sourceCode python">ChainedMemberAccessor</code></span></a> – for working with members that accept feature chains. Note that their subtypes are only used for improved IDE experience as Python does not yet support dependent generic type constraints.

- Similarly, references are modifiable through <span class="pre">`_target`</span> properties on select relationships, e.g. <a href="/python/v0.8.4/syside/Subsetting.md" class="reference internal" title="syside.Subsetting"><span class="pre"><code class="sourceCode python">Subsetting</code></span></a>. The common base class is <a href="/python/v0.8.4/syside/ReferenceAccessor.md" class="reference internal" title="syside.ReferenceAccessor"><span class="pre"><code class="sourceCode python">ReferenceAccessor</code></span></a>.

<div id="constraints" class="section">

### Constraints<a href="#constraints" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

When modifying the model, the following constraints must be satisfied:

- An element can have only a single owner. Violating this constraint raises <span class="pre">`ValueError`</span>. However, the same element can be referenced by multiple elements, e.g.:

  <div class="highlight-py notranslate">

  <div class="highlight">

      _, element = namespace.children.append(
          syside.OwningMembership, syside.Package
      )
      _, _ = namespace.children.append(syside.OwningMembership, element)  # error
      _, _ = namespace.children.append(syside.Membership, element)  # OK
      _, _ = namespace.children.append(syside.Membership, element)  # OK

  </div>

  </div>

- Moving an element from one document to another is not supported and will raise <span class="pre">`ValueError`</span>, e.g.:

  <div class="highlight-py notranslate">

  <div class="highlight">

      _, element = namespace.children.append(
          syside.OwningMembership, syside.Package
      )
      namespace.children.pop(0)

      _, _ = other.children.append(syside.OwningMembership, element)  # error
      _, _ = namespace.children.append(syside.OwningMembership, element)  # OK

  </div>

  </div>

- Adding a new owned or referenced element must satisfy the typing constraints and will raise <span class="pre">`TypeError`</span> exception if violated:

  <div class="highlight-py notranslate">

  <div class="highlight">

      _, element = namespace.children.append(
          syside.OwningMembership, syside.PartDefinition
      )  # OK
      _, _ = element.children.append(
          syside.FeatureMembership, syside.Package
      )  # error

  </div>

  </div>

- An element can be added only to an element that is not removed from the model. If this constraint is violated, a <span class="pre">`RuntimeError`</span> is raised. The problem can be fixed by adding the parent element back to the document as an owned element:

  <div class="highlight-py notranslate">

  <div class="highlight">

      _, element = namespace.children.append(
          syside.OwningMembership, syside.Package
      )
      namespace.children.pop(0)

      _, _ = element.children.append(
          syside.OwningMembership, syside.Package
      )  # error
      _, _ = namespace.children.append(syside.OwningMembership, element)  # OK
      _, _ = element.children.append(
          syside.OwningMembership, syside.Package
      )  # OK

  </div>

  </div>

- Adding an owned element to a relationship that can only reference elements will raise <span class="pre">`TypeError`</span>:

  <div class="highlight-py notranslate">

  <div class="highlight">

      _, element = namespace.children.append(
          syside.Membership, syside.Package
      )  # error
      _, element = namespace.children.append(
          syside.OwningMembership, syside.Package
      )  # OK

  </div>

  </div>

</div>

</div>

</div>
