<div id="semantictokensbuilder" class="section">

# SemanticTokensBuilder<a href="#semantictokensbuilder" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">SemanticTokensBuilder</span></span><a href="#syside.ide.SemanticTokensBuilder" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Helper for building LSP compatible semantic tokens.

<div class="align-center" align="center">

<img src="data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iZ3JhcGh2aXoiIHN0eWxlPSJ3aWR0aDogMTAuMDYyNXJlbTtoZWlnaHQ6IDIuNzVyZW07IiB2aWV3Ym94PSIwLjAwIDAuMDAgMTYxLjAwIDQ0LjAwIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPgo8ZyBjbGFzcz0iZ3JhcGgiIGlkPSJncmFwaDAiIHRyYW5zZm9ybT0ic2NhbGUoMSAxKSByb3RhdGUoMCkgdHJhbnNsYXRlKDQgNDApIj4KPHRpdGxlPiUzPC90aXRsZT4KPGcgY2xhc3M9Im5vZGUiIGlkPSJub2RlMSI+Cjx0aXRsZT5TZW1hbnRpY1Rva2Vuc0J1aWxkZXI8L3RpdGxlPgo8ZyBpZD0iYV9ub2RlMSI+PGEgaHJlZj0iI3N5c2lkZS5pZGUuU2VtYW50aWNUb2tlbnNCdWlsZGVyIj4KPHBvbHlnb24gcG9pbnRzPSIxNTMsLTM2IDAsLTM2IDAsMCAxNTMsMCAxNTMsLTM2IiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1iZy1jb2xvcik7c3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1ub2RlLWZnLWNvbG9yKTsiPjwvcG9seWdvbj4KPHRleHQgZm9udC1mYW1pbHk9IkxleGVuZCIgZm9udC1zaXplPSIxMi4wMCIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWNvZGUtZmctY29sb3IpOy0tbWQtZ3JhcGh2aXotaG92ZXItY29sb3I6IHZhcigtLW1kLWdyYXBodml6LWEtaG92ZXItY29sb3IpOyIgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iNzYuNSIgeT0iLTE0LjIiPlNlbWFudGljVG9rZW5zQnVpbGRlcjwvdGV4dD4KPHRpdGxlPnN5c2lkZS5pZGUuU2VtYW50aWNUb2tlbnNCdWlsZGVyPC90aXRsZT48L2E+CjwvZz4KPC9nPgo8L2c+Cjwvc3ZnPg==" class="graphviz" />

</div>

<span class="sd-summary-text">Members defined in <a href="#syside.ide.SemanticTokensBuilder" class="reference internal" title="syside.ide.SemanticTokensBuilder"><span class="pre"><code class="sourceCode python">SemanticTokensBuilder</code></span></a> (10 members)</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |  |
|----|----|----|----|
| <span class="nerd-font"></span> | <a href="#syside.ide.SemanticTokensBuilder.absolute_tokens" class="reference internal" title="syside.ide.SemanticTokensBuilder.absolute_tokens"><span class="pre"><code class="sourceCode python">absolute_tokens</code></span></a> | <span class="pre">`R`</span> | Get all collected absolute semantic tokens. Note that this may require decoding delta tokens first. |
| <span class="nerd-font"></span> | <a href="#syside.ide.SemanticTokensBuilder.can_build_edits" class="reference internal" title="syside.ide.SemanticTokensBuilder.can_build_edits"><span class="pre"><code class="sourceCode python">can_build_edits</code></span></a> | <span class="pre">`R`</span> | Returns <span class="pre">`true`</span> if <span class="pre">`build_edits`</span> would return delta to the previous result. |
| <span class="nerd-font"></span> | <a href="#syside.ide.SemanticTokensBuilder.delta_tokens" class="reference internal" title="syside.ide.SemanticTokensBuilder.delta_tokens"><span class="pre"><code class="sourceCode python">delta_tokens</code></span></a> | <span class="pre">`R`</span> | Get all collected delta semantic tokens. Note that in case tokens were appended out of order, an encoding may take place. |
| <span class="nerd-font"></span> | <a href="#syside.ide.SemanticTokensBuilder.id" class="reference internal" title="syside.ide.SemanticTokensBuilder.id"><span class="pre"><code class="sourceCode python"><span class="bu">id</span></code></span></a> | <span class="pre">`R`</span> | Randomly generated ID of this builder. |
| <span class="nerd-font"></span> | <a href="#syside.ide.SemanticTokensBuilder.previous_tokens" class="reference internal" title="syside.ide.SemanticTokensBuilder.previous_tokens"><span class="pre"><code class="sourceCode python">previous_tokens</code></span></a> | <span class="pre">`R`</span> | Get previously built tokens as delta tokens. Must call <span class="pre">`previous_result`</span> to make this available. |
| <span class="nerd-font"></span> | <a href="#syside.ide.SemanticTokensBuilder.__init__" class="reference internal" title="syside.ide.SemanticTokensBuilder.__init__"><span class="pre"><code class="sourceCode python"><span class="fu">__init__</span></code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.ide.SemanticTokensBuilder.append" class="reference internal" title="syside.ide.SemanticTokensBuilder.append"><span class="pre"><code class="sourceCode python">append</code></span></a> |  | Append a new semantic token. |
| <span class="nerd-font"></span> | <a href="#syside.ide.SemanticTokensBuilder.build" class="reference internal" title="syside.ide.SemanticTokensBuilder.build"><span class="pre"><code class="sourceCode python">build</code></span></a> |  | Build currently collected semantic tokens into LSP compatible format. |
| <span class="nerd-font"></span> | <a href="#syside.ide.SemanticTokensBuilder.build_edits" class="reference internal" title="syside.ide.SemanticTokensBuilder.build_edits"><span class="pre"><code class="sourceCode python">build_edits</code></span></a> |  | Build currently collected semantic tokens into LSP compatible format. If <span class="pre">`can_build_edits`</span>, a delta to the <span class="pre">`previous_tokens`</span> will be returned which will usually be smaller than the full tokens. |
| <span class="nerd-font"></span> | <a href="#syside.ide.SemanticTokensBuilder.previous_result" class="reference internal" title="syside.ide.SemanticTokensBuilder.previous_result"><span class="pre"><code class="sourceCode python">previous_result</code></span></a> |  | Move the contents of this builder to previous result and reset the state. If id does not match <span class="pre">`id`</span>, current tokens are discarded instead. This must be called before building edits. |

</div>

</div>

<span class="nerd-font"></span> **Attributes**

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">absolute_tokens</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/ContainerView.md" class="reference internal" title="syside.ContainerView"><span class="pre">syside.ContainerView</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/ide/AbsoluteSemanticToken.md" class="reference internal" title="syside.ide.AbsoluteSemanticToken"><span class="pre">syside.ide.AbsoluteSemanticToken</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.ide.SemanticTokensBuilder.absolute_tokens" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Get all collected absolute semantic tokens. Note that this may require decoding delta tokens first.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">can_build_edits</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*<a href="#syside.ide.SemanticTokensBuilder.can_build_edits" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Returns <span class="pre">`true`</span> if <span class="pre">`build_edits`</span> would return delta to the previous result.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">delta_tokens</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/ContainerView.md" class="reference internal" title="syside.ContainerView"><span class="pre">syside.ContainerView</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/ide/DeltaSemanticToken.md" class="reference internal" title="syside.ide.DeltaSemanticToken"><span class="pre">syside.ide.DeltaSemanticToken</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.ide.SemanticTokensBuilder.delta_tokens" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Get all collected delta semantic tokens. Note that in case tokens were appended out of order, an encoding may take place.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">id</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">int</span>*<a href="#syside.ide.SemanticTokensBuilder.id" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Randomly generated ID of this builder.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">previous_tokens</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/ContainerView.md" class="reference internal" title="syside.ContainerView"><span class="pre">syside.ContainerView</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/ide/DeltaSemanticToken.md" class="reference internal" title="syside.ide.DeltaSemanticToken"><span class="pre">syside.ide.DeltaSemanticToken</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.ide.SemanticTokensBuilder.previous_tokens" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Get previously built tokens as delta tokens. Must call <span class="pre">`previous_result`</span> to make this available.

<span class="nerd-font"></span> **Methods**

<span class="sig-name descname"><span class="pre">\_\_init\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span><a href="#syside.ide.SemanticTokensBuilder.__init__" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">append</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/ide/AbsoluteSemanticToken.md" class="reference internal" title="syside.ide.AbsoluteSemanticToken"><span class="pre">syside.ide.AbsoluteSemanticToken</span></a></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span><a href="#syside.ide.SemanticTokensBuilder.append" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Append a new semantic token.

<span class="sig-name descname"><span class="pre">build</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="/python/v0.8.4/syside/ide/lsp/SemanticTokens.md" class="reference internal" title="syside.ide.lsp.SemanticTokens"><span class="pre">syside.ide.lsp.SemanticTokens</span></a></span></span><a href="#syside.ide.SemanticTokensBuilder.build" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Build currently collected semantic tokens into LSP compatible format.

<span class="sig-name descname"><span class="pre">build_edits</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="/python/v0.8.4/syside/ide/lsp/SemanticTokens.md" class="reference internal" title="syside.ide.lsp.SemanticTokens"><span class="pre">syside.ide.lsp.SemanticTokens</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/ide/lsp/SemanticTokensDelta.md" class="reference internal" title="syside.ide.lsp.SemanticTokensDelta"><span class="pre">syside.ide.lsp.SemanticTokensDelta</span></a></span></span><a href="#syside.ide.SemanticTokensBuilder.build_edits" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Build currently collected semantic tokens into LSP compatible format. If <span class="pre">`can_build_edits`</span>, a delta to the <span class="pre">`previous_tokens`</span> will be returned which will usually be smaller than the full tokens.

<span class="sig-name descname"><span class="pre">previous_result</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">int</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span><a href="#syside.ide.SemanticTokensBuilder.previous_result" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Move the contents of this builder to previous result and reset the state. If id does not match <span class="pre">`id`</span>, current tokens are discarded instead. This must be called before building edits.

<span class="sig-name descname"><span class="pre">previous_result</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span>  
Overload of <span class="pre">`previous_result`</span> that will parse the provided id to int.

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/ide//README.md" class="reference internal" title="syside.ide"><span class="pre"><code class="sourceCode python">syside.ide</code></span></a>

  - <a href="/python/v0.8.4/syside/ide//README.md" class="reference internal" title="syside.ide.build_delta_semantic_tokens"><span class="pre"><code class="sourceCode python">build_delta_semantic_tokens</code></span></a>

  - <a href="/python/v0.8.4/syside/ide//README.md" class="reference internal" title="syside.ide.build_full_semantic_tokens"><span class="pre"><code class="sourceCode python">build_full_semantic_tokens</code></span></a>

  - <a href="/python/v0.8.4/syside/ide//README.md" class="reference internal" title="syside.ide.build_range_semantic_tokens"><span class="pre"><code class="sourceCode python">build_range_semantic_tokens</code></span></a>

</div>

</div>
