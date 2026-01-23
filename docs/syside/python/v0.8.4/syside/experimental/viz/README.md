<div id="module-syside.experimental.viz" class="section">

<span id="viz-labs"></span>

# viz <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">Labs</span><a href="#module-syside.experimental.viz" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

Submodule for generating SysML visualizations.

Note that this any features in this module are still in very early stages and subject to change. Features will be extended and more implemented in future versions.

Currently implemented:

- hierarchical nodes and edges

- binary edges

- n-ary edges

- metadata prefixes

- annotating elements

- DOT nested and interconnection diagrams

- edges from <span class="pre">`Types`</span>, e.g. <span class="pre">`Connections`</span>, <span class="pre">`Flows`</span>

- rendering common <span class="pre">`Type`</span> declarations, including heritage, and feature values

To be implemented:

- rendering type-specific declarations, e.g. connectors

- inserting cross-referenced elements

- inserting and modifying nodes and edges manually

- more rendered graph types

- more render targets

- embedded hyperlinks

- semantically highlighted SysML text

- styling

- layouting

<div id="index" class="section">

## <span class="nerd-font"></span> Index<a href="#index" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

<span class="sd-summary-text"><span class="nerd-font"></span> **Submodules** <a href="#syside-experimental-viz-submodules-table" class="reference internal"><span class="std std-ref"></span></a></span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |
|----|----|----|
| <a href="/python/v0.8.4/syside/experimental/viz/dot//README.md" class="reference internal" title="syside.experimental.viz.dot"><span class="pre"><code class="sourceCode python">dot</code></span></a> | <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">Labs</span> | Submodule for rendering DOT graphs. |

</div>

</div>

<span class="sd-summary-text"><span class="nerd-font"></span> **Classes** <a href="#syside-experimental-viz-classes-table" class="reference internal"><span class="std std-ref"></span></a></span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |
|----|----|----|
| <a href="/python/v0.8.4/syside/experimental/viz/Graph.md" class="reference internal" title="syside.experimental.viz.Graph"><span class="pre"><code class="sourceCode python">Graph</code></span></a> |  | Data structure for SysML graphs. |
| <a href="/python/v0.8.4/syside/experimental/viz/TransformationContext.md" class="reference internal" title="syside.experimental.viz.TransformationContext"><span class="pre"><code class="sourceCode python">TransformationContext</code></span></a> |  | Reusable context for transforming SysML models into graphs. |

</div>

</div>

<span class="sd-summary-text"><span class="nerd-font"></span> **Functions** <a href="#syside-experimental-viz-functions-table" class="reference internal"><span class="std std-ref"></span></a></span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |
|----|----|----|
| <a href="#syside.experimental.viz.transform_to" class="reference internal" title="syside.experimental.viz.transform_to"><span class="pre"><code class="sourceCode python">transform_to</code></span></a> |  | Insert model rooted at <span class="pre">`root`</span> to <span class="pre">`graph`</span>. Note that edges between different root subtrees may not be created. |

</div>

</div>

</div>

------------------------------------------------------------------------

<div id="functions" class="section">

## <span class="nerd-font">󰊕</span> Functions<a href="#functions" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

<span class="sig-name descname"><span class="pre">transform_to</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">graph</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/experimental/viz/Graph.md" class="reference internal" title="syside.experimental.viz.Graph"><span class="pre">syside.experimental.viz.Graph</span></a></span>*, *<span class="n"><span class="pre">root</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/Namespace.md" class="reference internal" title="syside.Namespace"><span class="pre">syside.Namespace</span></a></span>*, *<span class="o"><span class="pre">\*</span></span>*, *<span class="n"><span class="pre">context</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/experimental/viz/TransformationContext.md" class="reference internal" title="syside.experimental.viz.TransformationContext"><span class="pre">syside.experimental.viz.TransformationContext</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">None</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span><a href="#syside.experimental.viz.transform_to" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Insert model rooted at <span class="pre">`root`</span> to <span class="pre">`graph`</span>. Note that edges between different root subtrees may not be created.

If calling this repeatedly, prefer passing in a <span class="pre">`context`</span> to improve performance.

<div class="toctree-wrapper compound">

</div>

<div class="toctree-wrapper compound">

</div>

</div>

</div>
