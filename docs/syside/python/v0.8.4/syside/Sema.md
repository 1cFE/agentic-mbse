<div id="sema" class="section">

# Sema<a href="#sema" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">Sema</span></span><a href="#syside.Sema" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Semantic resolver for SysML. This is responsible for linking references and resolving semantic rules in the pipeline.

<div class="align-center" align="center">

<img src="data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iZ3JhcGh2aXoiIHN0eWxlPSJ3aWR0aDogMy44NzVyZW07aGVpZ2h0OiAyLjc1cmVtOyIgdmlld2JveD0iMC4wMCAwLjAwIDYyLjAwIDQ0LjAwIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPgo8ZyBjbGFzcz0iZ3JhcGgiIGlkPSJncmFwaDAiIHRyYW5zZm9ybT0ic2NhbGUoMSAxKSByb3RhdGUoMCkgdHJhbnNsYXRlKDQgNDApIj4KPHRpdGxlPiUzPC90aXRsZT4KPGcgY2xhc3M9Im5vZGUiIGlkPSJub2RlMSI+Cjx0aXRsZT5TZW1hPC90aXRsZT4KPGcgaWQ9ImFfbm9kZTEiPjxhIGhyZWY9IiNzeXNpZGUuU2VtYSI+Cjxwb2x5Z29uIHBvaW50cz0iNTQsLTM2IDAsLTM2IDAsMCA1NCwwIDU0LC0zNiIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtYmctY29sb3IpO3N0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1mZy1jb2xvcik7Ij48L3BvbHlnb24+Cjx0ZXh0IGZvbnQtZmFtaWx5PSJMZXhlbmQiIGZvbnQtc2l6ZT0iMTIuMDAiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1jb2RlLWZnLWNvbG9yKTstLW1kLWdyYXBodml6LWhvdmVyLWNvbG9yOiB2YXIoLS1tZC1ncmFwaHZpei1hLWhvdmVyLWNvbG9yKTsiIHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjI3IiB5PSItMTQuMiI+U2VtYTwvdGV4dD4KPHRpdGxlPnN5c2lkZS5TZW1hPC90aXRsZT48L2E+CjwvZz4KPC9nPgo8L2c+Cjwvc3ZnPg==" class="graphviz" />

</div>

<span class="sd-summary-text">Members defined in <a href="#syside.Sema" class="reference internal" title="syside.Sema"><span class="pre"><code class="sourceCode python">Sema</code></span></a> (2 members)</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |  |
|----|----|----|----|
| <span class="nerd-font"></span> | <a href="#syside.Sema.__init__" class="reference internal" title="syside.Sema.__init__"><span class="pre"><code class="sourceCode python"><span class="fu">__init__</span></code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.Sema.resolve" class="reference internal" title="syside.Sema.resolve"><span class="pre"><code class="sourceCode python">resolve</code></span></a> |  | Link and resolve semantic rules for <span class="pre">`documents`</span>. Any documents that have already been resolved will be skipped, inferred by <span class="pre">`build_state`</span>` `<span class="pre">`>=`</span>` `<span class="pre">`BuildState.Built`</span>. For references to be resolved correctly, they either have to point to elements in unresolved <span class="pre">`documents`</span>, or elements indexed in <span class="pre">`index`</span>. Similarly, semantic rules depend on all the required elements cached by <span class="pre">`stdlib`</span>. |

</div>

</div>

<span class="nerd-font"></span> **Methods**

<span class="sig-name descname"><span class="pre">\_\_init\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span><a href="#syside.Sema.__init__" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">resolve</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">documents</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">Sequence</span><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/SharedMutex.md" class="reference internal" title="syside.SharedMutex"><span class="pre">syside.SharedMutex</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Document.md" class="reference internal" title="syside.Document"><span class="pre">syside.Document</span></a><span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">\]</span></span></span>*, *<span class="n"><span class="pre">index</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/StaticIndex.md" class="reference internal" title="syside.StaticIndex"><span class="pre">syside.StaticIndex</span></a></span>*, *<span class="n"><span class="pre">stdlib</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/Stdlib.md" class="reference internal" title="syside.Stdlib"><span class="pre">syside.Stdlib</span></a></span>*, *<span class="n"><span class="pre">reporter</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">Callable</span><span class="p"><span class="pre">\[</span></span><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Document.md" class="reference internal" title="syside.Document"><span class="pre">syside.Document</span></a><span class="p"><span class="pre">,</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/Diagnostic.md" class="reference internal" title="syside.Diagnostic"><span class="pre">syside.Diagnostic</span></a><span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">None</span><span class="p"><span class="pre">\]</span></span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">...</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span><a href="#syside.Sema.resolve" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Link and resolve semantic rules for <span class="pre">`documents`</span>. Any documents that have already been resolved will be skipped, inferred by <span class="pre">`build_state`</span>` `<span class="pre">`>=`</span>` `<span class="pre">`BuildState.Built`</span>. For references to be resolved correctly, they either have to point to elements in unresolved <span class="pre">`documents`</span>, or elements indexed in <span class="pre">`index`</span>. Similarly, semantic rules depend on all the required elements cached by <span class="pre">`stdlib`</span>.

<span class="pre">`reporter`</span> can be used to override default behaviour of how diagnostics are emitted. By default, they are printed to stdout.

</div>
