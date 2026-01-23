<div id="deltasemantictoken" class="section">

# DeltaSemanticToken<a href="#deltasemantictoken" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">DeltaSemanticToken</span></span><a href="#syside.ide.DeltaSemanticToken" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Semantic token using delta encoded positions.

<div class="align-center" align="center">

<img src="data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iZ3JhcGh2aXoiIHN0eWxlPSJ3aWR0aDogOS4wcmVtO2hlaWdodDogMi43NXJlbTsiIHZpZXdib3g9IjAuMDAgMC4wMCAxNDQuMDAgNDQuMDAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxnIGNsYXNzPSJncmFwaCIgaWQ9ImdyYXBoMCIgdHJhbnNmb3JtPSJzY2FsZSgxIDEpIHJvdGF0ZSgwKSB0cmFuc2xhdGUoNCA0MCkiPgo8dGl0bGU+JTM8L3RpdGxlPgo8ZyBjbGFzcz0ibm9kZSIgaWQ9Im5vZGUxIj4KPHRpdGxlPkRlbHRhU2VtYW50aWNUb2tlbjwvdGl0bGU+CjxnIGlkPSJhX25vZGUxIj48YSBocmVmPSIjc3lzaWRlLmlkZS5EZWx0YVNlbWFudGljVG9rZW4iPgo8cG9seWdvbiBwb2ludHM9IjEzNiwtMzYgMCwtMzYgMCwwIDEzNiwwIDEzNiwtMzYiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1ncmFwaHZpei1ub2RlLWJnLWNvbG9yKTtzdHJva2U6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtZmctY29sb3IpOyI+PC9wb2x5Z29uPgo8dGV4dCBmb250LWZhbWlseT0iTGV4ZW5kIiBmb250LXNpemU9IjEyLjAwIiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtY29kZS1mZy1jb2xvcik7LS1tZC1ncmFwaHZpei1ob3Zlci1jb2xvcjogdmFyKC0tbWQtZ3JhcGh2aXotYS1ob3Zlci1jb2xvcik7IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSI2OCIgeT0iLTE0LjIiPkRlbHRhU2VtYW50aWNUb2tlbjwvdGV4dD4KPHRpdGxlPnN5c2lkZS5pZGUuRGVsdGFTZW1hbnRpY1Rva2VuPC90aXRsZT48L2E+CjwvZz4KPC9nPgo8L2c+Cjwvc3ZnPg==" class="graphviz" />

</div>

<span class="sd-summary-text">Members defined in <a href="#syside.ide.DeltaSemanticToken" class="reference internal" title="syside.ide.DeltaSemanticToken"><span class="pre"><code class="sourceCode python">DeltaSemanticToken</code></span></a> (7 members)</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |  |
|----|----|----|----|
| <span class="nerd-font"></span> | <a href="#syside.ide.DeltaSemanticToken.delta_character" class="reference internal" title="syside.ide.DeltaSemanticToken.delta_character"><span class="pre"><code class="sourceCode python">delta_character</code></span></a> | <span class="pre">`RW`</span> | Character where the token starts if <span class="pre">`line`</span>` `<span class="pre">`!=`</span>` `<span class="pre">`0`</span>, else the number of characters after the previous semantic token start character. |
| <span class="nerd-font"></span> | <a href="#syside.ide.DeltaSemanticToken.delta_line" class="reference internal" title="syside.ide.DeltaSemanticToken.delta_line"><span class="pre"><code class="sourceCode python">delta_line</code></span></a> | <span class="pre">`RW`</span> | Number of lines after the previous semantic token start line. |
| <span class="nerd-font"></span> | <a href="#syside.ide.DeltaSemanticToken.length" class="reference internal" title="syside.ide.DeltaSemanticToken.length"><span class="pre"><code class="sourceCode python">length</code></span></a> | <span class="pre">`RW`</span> | Number of bytes this token extends. |
| <span class="nerd-font"></span> | <a href="#syside.ide.DeltaSemanticToken.modifiers" class="reference internal" title="syside.ide.DeltaSemanticToken.modifiers"><span class="pre"><code class="sourceCode python">modifiers</code></span></a> | <span class="pre">`RW`</span> | Set of semantic token modifiers. |
| <span class="nerd-font"></span> | <a href="#syside.ide.DeltaSemanticToken.type" class="reference internal" title="syside.ide.DeltaSemanticToken.type"><span class="pre"><code class="sourceCode python"><span class="bu">type</span></code></span></a> | <span class="pre">`RW`</span> | Encoded semantic token type. |
| <span class="nerd-font"></span> | <a href="#syside.ide.DeltaSemanticToken.__init__" class="reference internal" title="syside.ide.DeltaSemanticToken.__init__"><span class="pre"><code class="sourceCode python"><span class="fu">__init__</span></code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.ide.DeltaSemanticToken.__str__" class="reference internal" title="syside.ide.DeltaSemanticToken.__str__"><span class="pre"><code class="sourceCode python"><span class="fu">__str__</span></code></span></a> |  |  |

</div>

</div>

<span class="nerd-font"></span> **Attributes**

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">delta_character</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">int</span>*<a href="#syside.ide.DeltaSemanticToken.delta_character" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Character where the token starts if <span class="pre">`line`</span>` `<span class="pre">`!=`</span>` `<span class="pre">`0`</span>, else the number of characters after the previous semantic token start character.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">delta_line</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">int</span>*<a href="#syside.ide.DeltaSemanticToken.delta_line" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Number of lines after the previous semantic token start line.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">length</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">int</span>*<a href="#syside.ide.DeltaSemanticToken.length" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Number of bytes this token extends.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">modifiers</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/ide/SemanticTokenModifiersSet.md" class="reference internal" title="syside.ide.SemanticTokenModifiersSet"><span class="pre">syside.ide.SemanticTokenModifiersSet</span></a>*<a href="#syside.ide.DeltaSemanticToken.modifiers" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Set of semantic token modifiers.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">type</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">int</span>*<a href="#syside.ide.DeltaSemanticToken.type" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Encoded semantic token type.

<span class="nerd-font"></span> **Methods**

<span class="sig-name descname"><span class="pre">\_\_init\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">delta_line</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">int</span></span>*, *<span class="n"><span class="pre">delta_character</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">int</span></span>*, *<span class="n"><span class="pre">length</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">int</span></span>*, *<span class="n"><span class="pre">type</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">int</span></span>*, *<span class="n"><span class="pre">modifiers</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/ide/SemanticTokenModifiersSet.md" class="reference internal" title="syside.ide.SemanticTokenModifiersSet"><span class="pre">syside.ide.SemanticTokenModifiersSet</span></a></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span><a href="#syside.ide.DeltaSemanticToken.__init__" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">\_\_str\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">str</span></span></span><a href="#syside.ide.DeltaSemanticToken.__str__" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/ide/SemanticTokensBuilder.md" class="reference internal" title="syside.ide.SemanticTokensBuilder"><span class="pre"><code class="sourceCode python">syside.ide.SemanticTokensBuilder</code></span></a>

  - <a href="/python/v0.8.4/syside/ide/SemanticTokensBuilder.md" class="reference internal" title="syside.ide.SemanticTokensBuilder.delta_tokens"><span class="pre"><code class="sourceCode python">delta_tokens</code></span></a>

  - <a href="/python/v0.8.4/syside/ide/SemanticTokensBuilder.md" class="reference internal" title="syside.ide.SemanticTokensBuilder.previous_tokens"><span class="pre"><code class="sourceCode python">previous_tokens</code></span></a>

</div>

</div>
