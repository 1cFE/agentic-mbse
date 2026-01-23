<div id="semantictokenmodifiersset" class="section">

# SemanticTokenModifiersSet<a href="#semantictokenmodifiersset" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">SemanticTokenModifiersSet</span></span><a href="#syside.ide.SemanticTokenModifiersSet" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Fixed-size bitset of SemanticTokenModifiers for easier use with LSP serialization.

<div class="align-center" align="center">

<img src="data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iZ3JhcGh2aXoiIHN0eWxlPSJ3aWR0aDogMTEuNjg3NXJlbTtoZWlnaHQ6IDIuNzVyZW07IiB2aWV3Ym94PSIwLjAwIDAuMDAgMTg3LjAwIDQ0LjAwIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPgo8ZyBjbGFzcz0iZ3JhcGgiIGlkPSJncmFwaDAiIHRyYW5zZm9ybT0ic2NhbGUoMSAxKSByb3RhdGUoMCkgdHJhbnNsYXRlKDQgNDApIj4KPHRpdGxlPiUzPC90aXRsZT4KPGcgY2xhc3M9Im5vZGUiIGlkPSJub2RlMSI+Cjx0aXRsZT5TZW1hbnRpY1Rva2VuTW9kaWZpZXJzU2V0PC90aXRsZT4KPGcgaWQ9ImFfbm9kZTEiPjxhIGhyZWY9IiNzeXNpZGUuaWRlLlNlbWFudGljVG9rZW5Nb2RpZmllcnNTZXQiPgo8cG9seWdvbiBwb2ludHM9IjE3OSwtMzYgMCwtMzYgMCwwIDE3OSwwIDE3OSwtMzYiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1ncmFwaHZpei1ub2RlLWJnLWNvbG9yKTtzdHJva2U6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtZmctY29sb3IpOyI+PC9wb2x5Z29uPgo8dGV4dCBmb250LWZhbWlseT0iTGV4ZW5kIiBmb250LXNpemU9IjEyLjAwIiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtY29kZS1mZy1jb2xvcik7LS1tZC1ncmFwaHZpei1ob3Zlci1jb2xvcjogdmFyKC0tbWQtZ3JhcGh2aXotYS1ob3Zlci1jb2xvcik7IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSI4OS41IiB5PSItMTQuMiI+U2VtYW50aWNUb2tlbk1vZGlmaWVyc1NldDwvdGV4dD4KPHRpdGxlPnN5c2lkZS5pZGUuU2VtYW50aWNUb2tlbk1vZGlmaWVyc1NldDwvdGl0bGU+PC9hPgo8L2c+CjwvZz4KPC9nPgo8L3N2Zz4=" class="graphviz" />

</div>

<span class="sd-summary-text">Members defined in <a href="#syside.ide.SemanticTokenModifiersSet" class="reference internal" title="syside.ide.SemanticTokenModifiersSet"><span class="pre"><code class="sourceCode python">SemanticTokenModifiersSet</code></span></a> (6 members)</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |  |
|----|----|----|----|
| <span class="nerd-font"></span> | <a href="#syside.ide.SemanticTokenModifiersSet.__getitem__" class="reference internal" title="syside.ide.SemanticTokenModifiersSet.__getitem__"><span class="pre"><code class="sourceCode python"><span class="fu">__getitem__</span></code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.ide.SemanticTokenModifiersSet.__init__" class="reference internal" title="syside.ide.SemanticTokenModifiersSet.__init__"><span class="pre"><code class="sourceCode python"><span class="fu">__init__</span></code></span></a> |  | Construct an empty set. |
| <span class="nerd-font"></span> | <a href="#syside.ide.SemanticTokenModifiersSet.__int__" class="reference internal" title="syside.ide.SemanticTokenModifiersSet.__int__"><span class="pre"><code class="sourceCode python"><span class="fu">__int__</span></code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.ide.SemanticTokenModifiersSet.__len__" class="reference internal" title="syside.ide.SemanticTokenModifiersSet.__len__"><span class="pre"><code class="sourceCode python"><span class="fu">__len__</span></code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.ide.SemanticTokenModifiersSet.__setitem__" class="reference internal" title="syside.ide.SemanticTokenModifiersSet.__setitem__"><span class="pre"><code class="sourceCode python"><span class="fu">__setitem__</span></code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.ide.SemanticTokenModifiersSet.__str__" class="reference internal" title="syside.ide.SemanticTokenModifiersSet.__str__"><span class="pre"><code class="sourceCode python"><span class="fu">__str__</span></code></span></a> |  |  |

</div>

</div>

<span class="nerd-font"></span> **Methods**

<span class="sig-name descname"><span class="pre">\_\_getitem\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/ide/lsp//README.md" class="reference internal" title="syside.ide.lsp.SemanticTokenModifiers"><span class="pre">syside.ide.lsp.SemanticTokenModifiers</span></a></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">bool</span></span></span><a href="#syside.ide.SemanticTokenModifiersSet.__getitem__" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">\_\_getitem\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">int</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">bool</span></span></span>  

<span class="sig-name descname"><span class="pre">\_\_init\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span><a href="#syside.ide.SemanticTokenModifiersSet.__init__" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Construct an empty set.

<span class="sig-name descname"><span class="pre">\_\_init\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">int</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span>  
Construct set from an unsigned integer.

<span class="sig-name descname"><span class="pre">\_\_int\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">int</span></span></span><a href="#syside.ide.SemanticTokenModifiersSet.__int__" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

*<span class="pre">static</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">\_\_len\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">int</span></span></span><a href="#syside.ide.SemanticTokenModifiersSet.__len__" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">\_\_setitem\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg0</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/ide/lsp//README.md" class="reference internal" title="syside.ide.lsp.SemanticTokenModifiers"><span class="pre">syside.ide.lsp.SemanticTokenModifiers</span></a></span>*, *<span class="n"><span class="pre">arg1</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span><a href="#syside.ide.SemanticTokenModifiersSet.__setitem__" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">\_\_setitem\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg0</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">int</span></span>*, *<span class="n"><span class="pre">arg1</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span>  

<span class="sig-name descname"><span class="pre">\_\_str\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">str</span></span></span><a href="#syside.ide.SemanticTokenModifiersSet.__str__" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/ide/AbsoluteSemanticToken.md" class="reference internal" title="syside.ide.AbsoluteSemanticToken"><span class="pre"><code class="sourceCode python">syside.ide.AbsoluteSemanticToken</code></span></a>

  - <a href="/python/v0.8.4/syside/ide/AbsoluteSemanticToken.md" class="reference internal" title="syside.ide.AbsoluteSemanticToken.__init__"><span class="pre"><code class="sourceCode python"><span class="fu">__init__</span></code></span></a>

  - <a href="/python/v0.8.4/syside/ide/AbsoluteSemanticToken.md" class="reference internal" title="syside.ide.AbsoluteSemanticToken.modifiers"><span class="pre"><code class="sourceCode python">modifiers</code></span></a>

- <a href="/python/v0.8.4/syside/ide/DeltaSemanticToken.md" class="reference internal" title="syside.ide.DeltaSemanticToken"><span class="pre"><code class="sourceCode python">syside.ide.DeltaSemanticToken</code></span></a>

  - <a href="/python/v0.8.4/syside/ide/DeltaSemanticToken.md" class="reference internal" title="syside.ide.DeltaSemanticToken.__init__"><span class="pre"><code class="sourceCode python"><span class="fu">__init__</span></code></span></a>

  - <a href="/python/v0.8.4/syside/ide/DeltaSemanticToken.md" class="reference internal" title="syside.ide.DeltaSemanticToken.modifiers"><span class="pre"><code class="sourceCode python">modifiers</code></span></a>

</div>

</div>
