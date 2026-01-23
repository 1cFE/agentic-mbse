<div id="version-history" class="section">

# Version History<a href="#version-history" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

This page contains notable changes that affect the API with more details than provided by the changelogs.

<div id="v0-8-4" class="section">

## v0.8.4<a href="#v0-8-4" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

- Extended visualization to handle more cases and render more details.

- Added <a href="/python/v0.8.4/syside/Stdlib.md" class="reference internal" title="syside.Stdlib.update"><span class="pre"><code class="sourceCode python">Stdlib.update</code></span></a>.

- Added <a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside.NamePreference"><span class="pre"><code class="sourceCode python">NamePreference</code></span></a> and <a href="/python/v0.8.4/syside/ReferencePrinter.md" class="reference internal" title="syside.ReferencePrinter"><span class="pre"><code class="sourceCode python">ReferencePrinter</code></span></a> to customize how synthetic references are printed.

</div>

<div id="v0-8-3" class="section">

## v0.8.3<a href="#v0-8-3" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

- Added a very early implementation for model visualization, <a href="/python/v0.8.4/syside/experimental/viz//README.md" class="reference internal" title="syside.experimental.viz"><span class="pre"><code class="sourceCode python">experimental.viz</code></span></a>. This can generate DOT output through <a href="/python/v0.8.4/syside/experimental/viz/dot//README.md" class="reference internal" title="syside.experimental.viz.dot"><span class="pre"><code class="sourceCode python">experimental.viz.dot</code></span></a>.

</div>

<div id="v0-8-2" class="section">

## v0.8.2<a href="#v0-8-2" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

- Added methods to extract related elements without clearing their subtrees:

  - <a href="/python/v0.8.4/syside/ChildrenNodes.md" class="reference internal" title="syside.ChildrenNodes.extract"><span class="pre"><code class="sourceCode python">ChildrenNodes.extract</code></span></a>

  - <a href="/python/v0.8.4/syside/ChildrenNodes.md" class="reference internal" title="syside.ChildrenNodes.extract_with_relationship"><span class="pre"><code class="sourceCode python">ChildrenNodes.extract_with_relationship</code></span></a>

  - <a href="/python/v0.8.4/syside/ChildrenNodes.md" class="reference internal" title="syside.ChildrenNodes.extract_element"><span class="pre"><code class="sourceCode python">ChildrenNodes.extract_element</code></span></a>

  - <a href="/python/v0.8.4/syside/RelationshipBody.md" class="reference internal" title="syside.RelationshipBody.extract"><span class="pre"><code class="sourceCode python">RelationshipBody.extract</code></span></a>

  - <a href="/python/v0.8.4/syside/RelationshipBody.md" class="reference internal" title="syside.RelationshipBody.extract_element"><span class="pre"><code class="sourceCode python">RelationshipBody.extract_element</code></span></a>

  - <a href="/python/v0.8.4/syside/MemberAccessor.md" class="reference internal" title="syside.MemberAccessor.extract_member_element"><span class="pre"><code class="sourceCode python">MemberAccessor.extract_member_element</code></span></a>

  - <a href="/python/v0.8.4/syside/ConnectorEndsAccessor.md" class="reference internal" title="syside.ConnectorEndsAccessor.extract"><span class="pre"><code class="sourceCode python">ConnectorEndsAccessor.extract</code></span></a>

  - <a href="/python/v0.8.4/syside/ParameterAccessor.md" class="reference internal" title="syside.ParameterAccessor.extract_argument"><span class="pre"><code class="sourceCode python">ParameterAccessor.extract_argument</code></span></a>

  While these methods will return the extracted element as an orphan which allows it to be reparented, they still do not allow the element to be moved to another document.

- Added <span class="pre">`experimental_quantities`</span> option to <a href="/python/v0.8.4/syside/Compiler.md" class="reference internal" title="syside.Compiler.evaluate"><span class="pre"><code class="sourceCode python">Compiler.evaluate</code></span></a> and <a href="/python/v0.8.4/syside/Compiler.md" class="reference internal" title="syside.Compiler.evaluate_feature"><span class="pre"><code class="sourceCode python">Compiler.evaluate_feature</code></span></a>.

- Added <span class="pre">`pydevd`</span> plugin for custom debugger visualizers which greatly improves debugging experience by eagerly evaluating <a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre"><code class="sourceCode python">LazyIterator</code></span></a> and hiding internal methods. More visualizers to come in future releases.

- Added automatic crash upload which is enabled by default. While this will allow us to receive and act upon crashes faster, it can be disabled with <a href="/python/v0.8.4/syside/debug//README.md" class="reference internal" title="syside.debug.set_crash_report_upload"><span class="pre"><code class="sourceCode python">debug.set_crash_report_upload(<span class="va">False</span>)</code></span></a>.

- <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">Labs</span> Added <a href="/python/v0.8.4/syside/json//README.md" class="reference internal" title="syside.json.loads"><span class="pre"><code class="sourceCode python">json.loads</code></span></a> overload for project loading that will attempt to resolve references similarly to <a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside.load_model"><span class="pre"><code class="sourceCode python">load_model</code></span></a>.

</div>

<div id="v0-8-1" class="section">

## v0.8.1<a href="#v0-8-1" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

- Added missing <span class="pre">`environment`</span> arguments to <a href="/python/v0.8.4/syside/preview//README.md" class="reference internal" title="syside.preview.open_model"><span class="pre"><code class="sourceCode python">preview.open_model</code></span></a> and <a href="/python/v0.8.4/syside/preview//README.md" class="reference internal" title="syside.preview.open_model_unlocked"><span class="pre"><code class="sourceCode python">preview.open_model_unlocked</code></span></a>. This allows existing models to be used as dependencies.

</div>

<div id="v0-8-0" class="section">

## v0.8.0<a href="#v0-8-0" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

Version v0.8.0 updates SysML support including changes from:

- <a href="https://github.com/Systems-Modeling/SysML-v2-Release/releases/tag/2025-07" class="reference external" target="_blank">2025-07</a>

- <a href="https://github.com/Systems-Modeling/SysML-v2-Release/releases/tag/2025-06" class="reference external" target="_blank">2025-06</a>

- <a href="https://github.com/Systems-Modeling/SysML-v2-Release/releases/tag/2025-04" class="reference external" target="_blank">2025-04</a>

- <a href="https://github.com/Systems-Modeling/SysML-v2-Release/releases/tag/2025-02" class="reference external" target="_blank">2025-02</a>

Most notable changes:

- Removed implicit <a href="/python/v0.8.4/syside/SubjectMembership.md" class="reference internal" title="syside.SubjectMembership"><span class="pre"><code class="sourceCode python">SubjectMemberships</code></span></a> and <a href="/python/v0.8.4/syside/ObjectiveMembership.md" class="reference internal" title="syside.ObjectiveMembership"><span class="pre"><code class="sourceCode python">ObjectiveMemberships</code></span></a> from <span class="pre">`requirements`</span> and <span class="pre">`cases`</span>.

- <a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature.is_constant"><span class="pre"><code class="sourceCode python">Feature.is_constant</code></span></a> replaces <span class="pre">`Feature.is_read_only`</span>.

- Added <a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature.is_variable"><span class="pre"><code class="sourceCode python">Feature.is_variable</code></span></a>.

- Added <a href="/python/v0.8.4/syside/ConstructorExpression.md" class="reference internal" title="syside.ConstructorExpression"><span class="pre"><code class="sourceCode python">ConstructorExpressions</code></span></a> which replace <a href="/python/v0.8.4/syside/InvocationExpression.md" class="reference internal" title="syside.InvocationExpression"><span class="pre"><code class="sourceCode python">InvocationExpressions</code></span></a> that invoke non-<a href="/python/v0.8.4/syside/Step.md" class="reference internal" title="syside.Step"><span class="pre"><code class="sourceCode python">Step</code></span></a>, non-<a href="/python/v0.8.4/syside/Behavior.md" class="reference internal" title="syside.Behavior"><span class="pre"><code class="sourceCode python">Behavior</code></span></a> types. While the syntax is similar with former needing a <span class="pre">`new`</span> keyword prefix, parse trees are different:

  <div class="pst-scrollable-table-container">

  <table class="table">
  <colgroup>
  <col style="width: 50%" />
  <col style="width: 50%" />
  </colgroup>
  <tbody>
  <tr class="row-odd">
  <td><div class="highlight-sysml notranslate">
  <div class="highlight">
  <pre><code>attribute x = Type(2);</code></pre>
  </div>
  </div></td>
  <td><div class="highlight-text notranslate">
  <div class="highlight">
  <pre><code>Namespace [0, 0] - [1, 0]
    children: OwningMembership [0, 0] - [0, 22]
      target: AttributeUsage [0, 0] - [0, 22]
        attribute [0, 0] - [0, 9]
        declared_name: NAME [0, 10] - [0, 11]
        value: FeatureValue [0, 12] - [0, 21]
          = [0, 12] - [0, 13]
          target: InvocationExpression [0, 14] - [0, 21]
            children: Membership [0, 14] - [0, 18]
              target: TypeReference [0, 14] - [0, 18]
                parts: NAME [0, 14] - [0, 18]
            ( [0, 18] - [0, 19]
            children: ParameterMembership [0, 19] - [0, 20]
              target: Feature [0, 19] - [0, 20]
                value: FeatureValue [0, 19] - [0, 20]
                  target: LiteralInteger [0, 19] - [0, 20]
                    literal: DECIMAL_VALUE [0, 19] - [0, 20]
            ) [0, 20] - [0, 21]
        ; [0, 21] - [0, 22]</code></pre>
  </div>
  </div></td>
  </tr>
  <tr class="row-even">
  <td><div class="highlight-sysml notranslate">
  <div class="highlight">
  <pre><code>attribute x = new Type(2);</code></pre>
  </div>
  </div></td>
  <td><div class="highlight-text notranslate">
  <div class="highlight">
  <pre><code>Namespace [0, 0] - [1, 0]
    children: OwningMembership [0, 0] - [0, 26]
      target: AttributeUsage [0, 0] - [0, 26]
        attribute [0, 0] - [0, 9]
        declaredName: NAME [0, 10] - [0, 11]
        value: FeatureValue [0, 12] - [0, 25]
          = [0, 12] - [0, 13]
          target: ConstructorExpression [0, 14] - [0, 25]
            new [0, 14] - [0, 17]
            children: Membership [0, 18] - [0, 22]
              target: TypeReference [0, 18] - [0, 22]
                parts: NAME [0, 18] - [0, 22]
            children: ReturnParameterMembership [0, 22] - [0, 25]
              target: Feature [0, 22] - [0, 25]
                ( [0, 22] - [0, 23]
                children: ParameterMembership [0, 23] - [0, 24]
                  target: Feature [0, 23] - [0, 24]
                    value: FeatureValue [0, 23] - [0, 24]
                      target: LiteralInteger [0, 23] - [0, 24]
                        literal: DECIMAL_VALUE [0, 23] - [0, 24]
                ) [0, 24] - [0, 25]
        ; [0, 25] - [0, 26]</code></pre>
  </div>
  </div></td>
  </tr>
  </tbody>
  </table>

  </div>

  Note that the type constructed by <a href="/python/v0.8.4/syside/ConstructorExpression.md" class="reference internal" title="syside.ConstructorExpression"><span class="pre"><code class="sourceCode python">ConstructorExpression</code></span></a> is now a <span class="pre">`member`</span> in <a href="/python/v0.8.4/syside/Namespace.md" class="reference internal" title="syside.Namespace.children"><span class="pre"><code class="sourceCode python">Namespace.children</code></span></a>, and arguments are parsed into a <span class="pre">`return`</span> <a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature"><span class="pre"><code class="sourceCode python">Feature</code></span></a>.

- Renamed some classes, and related <span class="pre">`snaked_cased`</span> attribute names:

  - <span class="pre">`ItemFeature`</span> renamed to <a href="/python/v0.8.4/syside/PayloadFeature.md" class="reference internal" title="syside.PayloadFeature"><span class="pre"><code class="sourceCode python">PayloadFeature</code></span></a>, <span class="pre">`item_feature`</span> to <span class="pre">`payload_feature`</span>.

  - <span class="pre">`ItemFlow`</span> renamed to <a href="/python/v0.8.4/syside/Flow.md" class="reference internal" title="syside.Flow"><span class="pre"><code class="sourceCode python">Flow</code></span></a>, <span class="pre">`item_flow`</span> to <span class="pre">`flow`</span>.

  - <span class="pre">`FlowConnectionUsage`</span> and <span class="pre">`FlowConnectionDefinition`</span> renamed to <a href="/python/v0.8.4/syside/FlowUsage.md" class="reference internal" title="syside.FlowUsage"><span class="pre"><code class="sourceCode python">FlowUsage</code></span></a> and <a href="/python/v0.8.4/syside/FlowDefinition.md" class="reference internal" title="syside.FlowDefinition"><span class="pre"><code class="sourceCode python">FlowDefinition</code></span></a> respectively, <span class="pre">`flow_connection`</span> to <span class="pre">`flow`</span>.

- Removed <span class="pre">`Featuring`</span> and <span class="pre">`LifeClass`</span> types - these were not representable in textual syntax anyway, but <a href="/python/v0.8.4/syside/FeatureMembership.md" class="reference internal" title="syside.FeatureMembership"><span class="pre"><code class="sourceCode python">FeatureMembership</code></span></a> and <a href="/python/v0.8.4/syside/TypeFeaturing.md" class="reference internal" title="syside.TypeFeaturing"><span class="pre"><code class="sourceCode python">TypeFeaturing</code></span></a> lost inherited members from <span class="pre">`Featuring`</span>.

- <span class="pre">`MetadataAccessExpression.set_referenced_element`</span> was fixed in the specification to be referenced through <a href="/python/v0.8.4/syside/Membership.md" class="reference internal" title="syside.Membership"><span class="pre"><code class="sourceCode python">Membership</code></span></a>, available through <a href="/python/v0.8.4/syside/MetadataAccessExpression.md" class="reference internal" title="syside.MetadataAccessExpression.referenced_element"><span class="pre"><code class="sourceCode python">MetadataAccessExpression.referenced_element</code></span></a>.

- Added <a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element.path"><span class="pre"><code class="sourceCode python">Element.path</code></span></a>, and extended deterministic element ID generation to user models. However, also note:

  - <a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element.path"><span class="pre"><code class="sourceCode python">Element.path</code></span></a> does not yet work for elements without <a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element.qualified_name"><span class="pre"><code class="sourceCode python">qualified_name</code></span></a> due to performance concerns. This should be fixed in a future release.

  - User element ID generation may be changed in a future version if we can improve performance.

- Added previously missed standard attributes:

  - <a href="/python/v0.8.4/syside/Definition.md" class="reference internal" title="syside.Definition.owned_analysis_cases"><span class="pre"><code class="sourceCode python">Definition.owned_analysis_cases</code></span></a>

  - <a href="/python/v0.8.4/syside/Definition.md" class="reference internal" title="syside.Definition.owned_requirements"><span class="pre"><code class="sourceCode python">Definition.owned_requirements</code></span></a>

  - <a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element.alias_ids"><span class="pre"><code class="sourceCode python">Element.alias_ids</code></span></a> (currently a view into an empty container only)

  - <a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature.chaining_features"><span class="pre"><code class="sourceCode python">Feature.chaining_features</code></span></a>

  - <a href="/python/v0.8.4/syside/Namespace.md" class="reference internal" title="syside.Namespace.imported_memberships"><span class="pre"><code class="sourceCode python">Namespace.imported_memberships</code></span></a>

  - <a href="/python/v0.8.4/syside/ViewUsage.md" class="reference internal" title="syside.ViewUsage.view_rendering"><span class="pre"><code class="sourceCode python">ViewUsage.view_rendering</code></span></a>

Other non-model changes include:

- Increased default <a href="/python/v0.8.4/syside/PrinterConfig.md" class="reference internal" title="syside.PrinterConfig.line_width"><span class="pre"><code class="sourceCode python">PrinterConfig.line_width</code></span></a> to 100 from 80 to match <span class="pre">`rustfmt`</span> and produce fewer line breaks, this works better with modern monitors.

- Improved deserialization to defer unresolved references without <span class="pre">`@uri`</span> instead of emitting an error. Unresolved owned elements still emit errors.

</div>

<div id="v0-7-2" class="section">

## v0.7.2<a href="#v0-7-2" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

- Added:

  > <div>
  >
  > - <a href="/python/v0.8.4/syside/ChainedChildrenNodes.md" class="reference internal" title="syside.ChainedChildrenNodes.append_chain"><span class="pre"><code class="sourceCode python">ChainedChildrenNodes.append_chain</code></span></a>
  >
  > - <a href="/python/v0.8.4/syside/ChainedChildrenNodes.md" class="reference internal" title="syside.ChainedChildrenNodes.insert_chain"><span class="pre"><code class="sourceCode python">ChainedChildrenNodes.insert_chain</code></span></a>
  >
  > - <a href="/python/v0.8.4/syside/ChainedChildrenNodes.md" class="reference internal" title="syside.ChainedChildrenNodes.replace_chain_at"><span class="pre"><code class="sourceCode python">ChainedChildrenNodes.replace_chain_at</code></span></a>
  >
  > </div>

</div>

<div id="v0-6-4" class="section">

## v0.6.4<a href="#v0-6-4" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

- Added <span class="pre">`print_references`</span> option to print references with <a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside.sexp"><span class="pre"><code class="sourceCode python">sexp</code></span></a>

</div>

<div id="v0-6-3" class="section">

## v0.6.3<a href="#v0-6-3" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

- Added constructor methods <span class="pre">`from_...`</span> to <a href="/python/v0.8.4/syside/DocumentSegment.md" class="reference internal" title="syside.DocumentSegment"><span class="pre"><code class="sourceCode python">DocumentSegment</code></span></a>

</div>

<div id="v0-6-0" class="section">

## v0.6.0<a href="#v0-6-0" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

Initial public release.

</div>

</div>
