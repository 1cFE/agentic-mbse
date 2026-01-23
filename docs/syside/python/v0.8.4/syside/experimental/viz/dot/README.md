<div id="module-syside.experimental.viz.dot" class="section">

<span id="dot-labs"></span>

# dot <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">Labs</span><a href="#module-syside.experimental.viz.dot" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

Submodule for rendering DOT graphs.

<div id="index" class="section">

## <span class="nerd-font"></span> Index<a href="#index" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

<span class="sd-summary-text"><span class="nerd-font"></span> **Classes** <a href="#syside-experimental-viz-dot-classes-table" class="reference internal"><span class="std std-ref"></span></a></span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |
|----|----|----|
| <a href="/python/v0.8.4/syside/experimental/viz/dot/InterconnectionRenderer.md" class="reference internal" title="syside.experimental.viz.dot.InterconnectionRenderer"><span class="pre"><code class="sourceCode python">InterconnectionRenderer</code></span></a> |  | A reusable interconnection renderer to DOT graph. |
| <a href="/python/v0.8.4/syside/experimental/viz/dot/NestedRenderer.md" class="reference internal" title="syside.experimental.viz.dot.NestedRenderer"><span class="pre"><code class="sourceCode python">NestedRenderer</code></span></a> |  | A reusable nested renderer to DOT graph. |

</div>

</div>

<span class="sd-summary-text"><span class="nerd-font"></span> **Functions** <a href="#syside-experimental-viz-dot-functions-table" class="reference internal"><span class="std std-ref"></span></a></span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |
|----|----|----|
| <a href="#syside.experimental.viz.dot.render_interconnection" class="reference internal" title="syside.experimental.viz.dot.render_interconnection"><span class="pre"><code class="sourceCode python">render_interconnection</code></span></a> |  | Render a self-contained interconnection diagram. |
| <a href="#syside.experimental.viz.dot.render_interconnection_body" class="reference internal" title="syside.experimental.viz.dot.render_interconnection_body"><span class="pre"><code class="sourceCode python">render_interconnection_body</code></span></a> |  | Render only the contents of an interconnection diagram, i.e. without the surrounding <span class="pre">`digraph`</span>. This can be useful if you want to add your own options to the rendered diagram, or insert its contents to another diagram. |
| <a href="#syside.experimental.viz.dot.render_nested" class="reference internal" title="syside.experimental.viz.dot.render_nested"><span class="pre"><code class="sourceCode python">render_nested</code></span></a> |  | Render a self-contained nested diagram. |
| <a href="#syside.experimental.viz.dot.render_nested_body" class="reference internal" title="syside.experimental.viz.dot.render_nested_body"><span class="pre"><code class="sourceCode python">render_nested_body</code></span></a> |  | Render only the contents of a nested diagram, i.e. without the surrounding <span class="pre">`digraph`</span>. This can be useful if you want to add your own options to the rendered diagram, or insert its contents to another diagram. Note that there needs to be a <span class="pre">`compound=true`</span> statement in the root scope to correctly clip edges to nodes with nested children. |

</div>

</div>

</div>

------------------------------------------------------------------------

<div id="functions" class="section">

## <span class="nerd-font">󰊕</span> Functions<a href="#functions" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

<span class="sig-name descname"><span class="pre">render_interconnection</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">graph</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/experimental/viz/Graph.md" class="reference internal" title="syside.experimental.viz.Graph"><span class="pre">syside.experimental.viz.Graph</span></a></span>*, *<span class="n"><span class="pre">indent</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">int</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">0</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">str</span></span></span><a href="#syside.experimental.viz.dot.render_interconnection" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Render a self-contained interconnection diagram.

If rendering multiple diagrams, prefer reusing <span class="pre">`InterconnectionRenderer`</span> instead to improve performance.

<!-- -->

<span class="sig-name descname"><span class="pre">render_interconnection_body</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">graph</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/experimental/viz/Graph.md" class="reference internal" title="syside.experimental.viz.Graph"><span class="pre">syside.experimental.viz.Graph</span></a></span>*, *<span class="n"><span class="pre">indent</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">int</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">0</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">str</span></span></span><a href="#syside.experimental.viz.dot.render_interconnection_body" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Render only the contents of an interconnection diagram, i.e. without the surrounding <span class="pre">`digraph`</span>. This can be useful if you want to add your own options to the rendered diagram, or insert its contents to another diagram.

If rendering multiple diagrams, prefer reusing <span class="pre">`InterconnectionRenderer`</span> instead to improve performance.

<!-- -->

<span class="sig-name descname"><span class="pre">render_nested</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">graph</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/experimental/viz/Graph.md" class="reference internal" title="syside.experimental.viz.Graph"><span class="pre">syside.experimental.viz.Graph</span></a></span>*, *<span class="n"><span class="pre">indent</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">int</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">0</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">str</span></span></span><a href="#syside.experimental.viz.dot.render_nested" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Render a self-contained nested diagram.

If rendering multiple diagrams, prefer reusing <span class="pre">`NestedRenderer`</span> instead to improve performance.

<!-- -->

<span class="sig-name descname"><span class="pre">render_nested_body</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">graph</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/experimental/viz/Graph.md" class="reference internal" title="syside.experimental.viz.Graph"><span class="pre">syside.experimental.viz.Graph</span></a></span>*, *<span class="n"><span class="pre">indent</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">int</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">0</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">str</span></span></span><a href="#syside.experimental.viz.dot.render_nested_body" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Render only the contents of a nested diagram, i.e. without the surrounding <span class="pre">`digraph`</span>. This can be useful if you want to add your own options to the rendered diagram, or insert its contents to another diagram. Note that there needs to be a <span class="pre">`compound=true`</span> statement in the root scope to correctly clip edges to nodes with nested children.

If rendering multiple diagrams, prefer reusing <span class="pre">`NestedRenderer`</span> instead to improve performance.

<div class="toctree-wrapper compound">

</div>

</div>

</div>
