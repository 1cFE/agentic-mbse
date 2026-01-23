<div id="graph" class="section">

# Graph<a href="#graph" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">Graph</span></span><a href="#syside.experimental.viz.Graph" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Data structure for SysML graphs.

Attributes and methods will be added as internal API stabilizes.

<div class="align-center" align="center">

<img src="data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iZ3JhcGh2aXoiIHN0eWxlPSJ3aWR0aDogMy43NXJlbTtoZWlnaHQ6IDEuODc1cmVtOyIgdmlld2JveD0iMC4wMCAwLjAwIDYwLjAwIDMwLjAwIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPgo8ZyBjbGFzcz0iZ3JhcGgiIGlkPSJncmFwaDAiIHRyYW5zZm9ybT0ic2NhbGUoMSAxKSByb3RhdGUoMCkgdHJhbnNsYXRlKDQgMjYpIj4KPHRpdGxlPiUzPC90aXRsZT4KPGcgaWQ9ImFfZ3JhcGgwIj48YSBocmVmPSIjc3lzaWRlLmV4cGVyaW1lbnRhbC52aXouR3JhcGgiPgo8dGV4dCBmb250LWZhbWlseT0iTGV4ZW5kIiBmb250LXNpemU9IjEyLjAwIiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtY29kZS1mZy1jb2xvcik7LS1tZC1ncmFwaHZpei1ob3Zlci1jb2xvcjogdmFyKC0tbWQtZ3JhcGh2aXotYS1ob3Zlci1jb2xvcik7IiB0ZXh0LWFuY2hvcj0ic3RhcnQiIHg9IjgiIHk9Ii03LjIiPkdyYXBoPC90ZXh0Pgo8dGl0bGU+c3lzaWRlLmV4cGVyaW1lbnRhbC52aXouR3JhcGg8L3RpdGxlPjwvYT4KPC9nPgo8L2c+Cjwvc3ZnPg==" class="graphviz" />

</div>

<span class="sd-summary-text">Members defined in <a href="#syside.experimental.viz.Graph" class="reference internal" title="syside.experimental.viz.Graph"><span class="pre"><code class="sourceCode python">Graph</code></span></a> (2 members)</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |  |
|----|----|----|----|
| <span class="nerd-font"></span> | <a href="#syside.experimental.viz.Graph.__init__" class="reference internal" title="syside.experimental.viz.Graph.__init__"><span class="pre"><code class="sourceCode python"><span class="fu">__init__</span></code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.experimental.viz.Graph.clear" class="reference internal" title="syside.experimental.viz.Graph.clear"><span class="pre"><code class="sourceCode python">clear</code></span></a> |  | Clear all nodes and edges. |

</div>

</div>

<span class="nerd-font"></span> **Methods**

<span class="sig-name descname"><span class="pre">\_\_init\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span><a href="#syside.experimental.viz.Graph.__init__" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">clear</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span><a href="#syside.experimental.viz.Graph.clear" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Clear all nodes and edges.

Note that node and edge ids will be reused in an unspecified order.

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/experimental/viz//README.md" class="reference internal" title="syside.experimental.viz"><span class="pre"><code class="sourceCode python">syside.experimental.viz</code></span></a>

  - <a href="/python/v0.8.4/syside/experimental/viz//README.md" class="reference internal" title="syside.experimental.viz.transform_to"><span class="pre"><code class="sourceCode python">transform_to</code></span></a>

- <a href="/python/v0.8.4/syside/experimental/viz/dot//README.md" class="reference internal" title="syside.experimental.viz.dot"><span class="pre"><code class="sourceCode python">syside.experimental.viz.dot</code></span></a>

  - <a href="/python/v0.8.4/syside/experimental/viz/dot//README.md" class="reference internal" title="syside.experimental.viz.dot.render_interconnection"><span class="pre"><code class="sourceCode python">render_interconnection</code></span></a>

  - <a href="/python/v0.8.4/syside/experimental/viz/dot//README.md" class="reference internal" title="syside.experimental.viz.dot.render_interconnection_body"><span class="pre"><code class="sourceCode python">render_interconnection_body</code></span></a>

  - <a href="/python/v0.8.4/syside/experimental/viz/dot//README.md" class="reference internal" title="syside.experimental.viz.dot.render_nested"><span class="pre"><code class="sourceCode python">render_nested</code></span></a>

  - <a href="/python/v0.8.4/syside/experimental/viz/dot//README.md" class="reference internal" title="syside.experimental.viz.dot.render_nested_body"><span class="pre"><code class="sourceCode python">render_nested_body</code></span></a>

- <a href="/python/v0.8.4/syside/experimental/viz/dot/InterconnectionRenderer.md" class="reference internal" title="syside.experimental.viz.dot.InterconnectionRenderer"><span class="pre"><code class="sourceCode python">syside.experimental.viz.dot.InterconnectionRenderer</code></span></a>

  - <a href="/python/v0.8.4/syside/experimental/viz/dot/InterconnectionRenderer.md" class="reference internal" title="syside.experimental.viz.dot.InterconnectionRenderer.render"><span class="pre"><code class="sourceCode python">render</code></span></a>

  - <a href="/python/v0.8.4/syside/experimental/viz/dot/InterconnectionRenderer.md" class="reference internal" title="syside.experimental.viz.dot.InterconnectionRenderer.render_body"><span class="pre"><code class="sourceCode python">render_body</code></span></a>

- <a href="/python/v0.8.4/syside/experimental/viz/dot/NestedRenderer.md" class="reference internal" title="syside.experimental.viz.dot.NestedRenderer"><span class="pre"><code class="sourceCode python">syside.experimental.viz.dot.NestedRenderer</code></span></a>

  - <a href="/python/v0.8.4/syside/experimental/viz/dot/NestedRenderer.md" class="reference internal" title="syside.experimental.viz.dot.NestedRenderer.render"><span class="pre"><code class="sourceCode python">render</code></span></a>

  - <a href="/python/v0.8.4/syside/experimental/viz/dot/NestedRenderer.md" class="reference internal" title="syside.experimental.viz.dot.NestedRenderer.render_body"><span class="pre"><code class="sourceCode python">render_body</code></span></a>

</div>

</div>
