<div id="nestedrenderer" class="section">

# NestedRenderer<a href="#nestedrenderer" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">NestedRenderer</span></span><a href="#syside.experimental.viz.dot.NestedRenderer" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
A reusable nested renderer to DOT graph.

Note that due to <span class="pre">`dot`</span> limitations, some labels may not be centred.

<div class="align-center" align="center">

<img src="data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iZ3JhcGh2aXoiIHN0eWxlPSJ3aWR0aDogNy4zNzVyZW07aGVpZ2h0OiAyLjc1cmVtOyIgdmlld2JveD0iMC4wMCAwLjAwIDExOC4wMCA0NC4wMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGcgY2xhc3M9ImdyYXBoIiBpZD0iZ3JhcGgwIiB0cmFuc2Zvcm09InNjYWxlKDEgMSkgcm90YXRlKDApIHRyYW5zbGF0ZSg0IDQwKSI+Cjx0aXRsZT4lMzwvdGl0bGU+CjxnIGNsYXNzPSJub2RlIiBpZD0ibm9kZTEiPgo8dGl0bGU+TmVzdGVkUmVuZGVyZXI8L3RpdGxlPgo8ZyBpZD0iYV9ub2RlMSI+PGEgaHJlZj0iI3N5c2lkZS5leHBlcmltZW50YWwudml6LmRvdC5OZXN0ZWRSZW5kZXJlciI+Cjxwb2x5Z29uIHBvaW50cz0iMTEwLC0zNiAwLC0zNiAwLDAgMTEwLDAgMTEwLC0zNiIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtYmctY29sb3IpO3N0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1mZy1jb2xvcik7Ij48L3BvbHlnb24+Cjx0ZXh0IGZvbnQtZmFtaWx5PSJMZXhlbmQiIGZvbnQtc2l6ZT0iMTIuMDAiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1jb2RlLWZnLWNvbG9yKTstLW1kLWdyYXBodml6LWhvdmVyLWNvbG9yOiB2YXIoLS1tZC1ncmFwaHZpei1hLWhvdmVyLWNvbG9yKTsiIHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjU1IiB5PSItMTQuMiI+TmVzdGVkUmVuZGVyZXI8L3RleHQ+Cjx0aXRsZT5zeXNpZGUuZXhwZXJpbWVudGFsLnZpei5kb3QuTmVzdGVkUmVuZGVyZXI8L3RpdGxlPjwvYT4KPC9nPgo8L2c+CjwvZz4KPC9zdmc+" class="graphviz" />

</div>

<span class="sd-summary-text">Members defined in <a href="#syside.experimental.viz.dot.NestedRenderer" class="reference internal" title="syside.experimental.viz.dot.NestedRenderer"><span class="pre"><code class="sourceCode python">NestedRenderer</code></span></a> (4 members)</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |  |
|----|----|----|----|
| <span class="nerd-font"></span> | <a href="#syside.experimental.viz.dot.NestedRenderer.indent" class="reference internal" title="syside.experimental.viz.dot.NestedRenderer.indent"><span class="pre"><code class="sourceCode python">indent</code></span></a> | <span class="pre">`RW`</span> | Indentation level |
| <span class="nerd-font"></span> | <a href="#syside.experimental.viz.dot.NestedRenderer.__init__" class="reference internal" title="syside.experimental.viz.dot.NestedRenderer.__init__"><span class="pre"><code class="sourceCode python"><span class="fu">__init__</span></code></span></a> |  | <span class="pre">`NestedRenderer`</span> constructor. |
| <span class="nerd-font"></span> | <a href="#syside.experimental.viz.dot.NestedRenderer.render" class="reference internal" title="syside.experimental.viz.dot.NestedRenderer.render"><span class="pre"><code class="sourceCode python">render</code></span></a> |  | Render a self-contained nested diagram. |
| <span class="nerd-font"></span> | <a href="#syside.experimental.viz.dot.NestedRenderer.render_body" class="reference internal" title="syside.experimental.viz.dot.NestedRenderer.render_body"><span class="pre"><code class="sourceCode python">render_body</code></span></a> |  | Render only the contents of a nested diagram, i.e. without the surrounding <span class="pre">`digraph`</span>. This can be useful if you want to add your own options to the rendered diagram, or insert its contents to another diagram. Note that there needs to be a <span class="pre">`compound=true`</span> statement in the root scope to correctly clip edges to nodes with nested children. |

</div>

</div>

<span class="nerd-font"></span> **Attributes**

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">indent</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">int</span>*<a href="#syside.experimental.viz.dot.NestedRenderer.indent" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Indentation level

<span class="nerd-font"></span> **Methods**

<span class="sig-name descname"><span class="pre">\_\_init\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">indent</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">int</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">0</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span><a href="#syside.experimental.viz.dot.NestedRenderer.__init__" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
<span class="pre">`NestedRenderer`</span> constructor.

<span class="pre">`indent`</span> argument controls initial indentation, this is primarily useful when combining multiple renderers.

<span class="sig-name descname"><span class="pre">render</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/experimental/viz/Graph.md" class="reference internal" title="syside.experimental.viz.Graph"><span class="pre">syside.experimental.viz.Graph</span></a></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">str</span></span></span><a href="#syside.experimental.viz.dot.NestedRenderer.render" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Render a self-contained nested diagram.

<span class="sig-name descname"><span class="pre">render_body</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/experimental/viz/Graph.md" class="reference internal" title="syside.experimental.viz.Graph"><span class="pre">syside.experimental.viz.Graph</span></a></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">str</span></span></span><a href="#syside.experimental.viz.dot.NestedRenderer.render_body" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Render only the contents of a nested diagram, i.e. without the surrounding <span class="pre">`digraph`</span>. This can be useful if you want to add your own options to the rendered diagram, or insert its contents to another diagram. Note that there needs to be a <span class="pre">`compound=true`</span> statement in the root scope to correctly clip edges to nodes with nested children.

</div>
