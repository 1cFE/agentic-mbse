<div id="module-syside.ide.lsp" class="section">

<span id="lsp"></span>

# lsp<a href="#module-syside.ide.lsp" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

LSP structures and types.

<div id="index" class="section">

## <span class="nerd-font"></span> Index<a href="#index" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

<span class="sd-summary-text"><span class="nerd-font"></span> **Classes** <a href="#syside-ide-lsp-classes-table" class="reference internal"><span class="std std-ref"></span></a></span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |
|----|----|----|
| <a href="/python/v0.8.4/syside/ide/lsp/SemanticTokens.md" class="reference internal" title="syside.ide.lsp.SemanticTokens"><span class="pre"><code class="sourceCode python">SemanticTokens</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/ide/lsp/SemanticTokensDelta.md" class="reference internal" title="syside.ide.lsp.SemanticTokensDelta"><span class="pre"><code class="sourceCode python">SemanticTokensDelta</code></span></a> |  |  |
| <a href="/python/v0.8.4/syside/ide/lsp/SemanticTokensEdit.md" class="reference internal" title="syside.ide.lsp.SemanticTokensEdit"><span class="pre"><code class="sourceCode python">SemanticTokensEdit</code></span></a> |  |  |

</div>

</div>

<span class="sd-summary-text"><span class="nerd-font"></span> **Enumerations** <a href="#syside-ide-lsp-enumerations-table" class="reference internal"><span class="std std-ref"></span></a></span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |
|----|----|----|
| <a href="#syside.ide.lsp.PositionEncodingKind" class="reference internal" title="syside.ide.lsp.PositionEncodingKind"><span class="pre"><code class="sourceCode python">PositionEncodingKind</code></span></a> |  | LSP position encoding kind. Note that Syside uses Utf-8 internally so it will incur no performance penalty. Other encodings will require lazy conversions, however allocations will be avoided whenever possible. |
| <a href="#syside.ide.lsp.SemanticTokenModifiers" class="reference internal" title="syside.ide.lsp.SemanticTokenModifiers"><span class="pre"><code class="sourceCode python">SemanticTokenModifiers</code></span></a> |  | LSP defined semantic token modifiers. Technically, this is not a flag enum but <span class="pre">`nanobind`</span> does not permit arbitrary values otherwise. |
| <a href="#syside.ide.lsp.SemanticTokenTypes" class="reference internal" title="syside.ide.lsp.SemanticTokenTypes"><span class="pre"><code class="sourceCode python">SemanticTokenTypes</code></span></a> |  | LSP defined semantic token types. Technically, this is not a flag enum but <span class="pre">`nanobind`</span> does not permit arbitrary values otherwise. |

</div>

</div>

</div>

------------------------------------------------------------------------

<div id="enumerations" class="section">

## <span class="nerd-font"></span> Enumerations<a href="#enumerations" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">PositionEncodingKind</span></span><a href="#syside.ide.lsp.PositionEncodingKind" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
LSP position encoding kind. Note that Syside uses Utf-8 internally so it will incur no performance penalty. Other encodings will require lazy conversions, however allocations will be avoided whenever possible.

For Python strings, use Utf32 encoding as that is what is used for string indexing and slicing.

See <a href="https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#positionEncodingKind" class="reference external" target="_blank">LSP specification</a> for more details.

<div class="pst-scrollable-table-container">

|  |  |
|----|----|
| <span class="pre">`Utf8`</span> <a href="#syside-ide-lsp-positionencodingkind-utf8" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Utf16`</span> <a href="#syside-ide-lsp-positionencodingkind-utf16" class="reference internal"><span class="std std-ref"></span></a> |  |
| <span class="pre">`Utf32`</span> <a href="#syside-ide-lsp-positionencodingkind-utf32" class="reference internal"><span class="std std-ref"></span></a> |  |

</div>

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/ide//README.md" class="reference internal" title="syside.ide"><span class="pre"><code class="sourceCode python">syside.ide</code></span></a>

  - <a href="/python/v0.8.4/syside/ide//README.md" class="reference internal" title="syside.ide.build_delta_semantic_tokens"><span class="pre"><code class="sourceCode python">build_delta_semantic_tokens</code></span></a>

  - <a href="/python/v0.8.4/syside/ide//README.md" class="reference internal" title="syside.ide.build_full_semantic_tokens"><span class="pre"><code class="sourceCode python">build_full_semantic_tokens</code></span></a>

  - <a href="/python/v0.8.4/syside/ide//README.md" class="reference internal" title="syside.ide.build_range_semantic_tokens"><span class="pre"><code class="sourceCode python">build_range_semantic_tokens</code></span></a>

</div>

<!-- -->

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">SemanticTokenModifiers</span></span><a href="#syside.ide.lsp.SemanticTokenModifiers" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
LSP defined semantic token modifiers. Technically, this is not a flag enum but <span class="pre">`nanobind`</span> does not permit arbitrary values otherwise.

See <a href="https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#semanticTokenModifiers" class="reference external" target="_blank">LSP specification</a> and <a href="https://code.visualstudio.com/api/language-extensions/semantic-highlight-guide#standard-token-types-and-modifiers" class="reference external" target="_blank">VS Code docs</a> for more details.

<div class="pst-scrollable-table-container">

|  |  |  |
|----|----|----|
| <span class="pre">`Declaration`</span> <a href="#syside-ide-lsp-semantictokenmodifiers-declaration" class="reference internal"><span class="std std-ref"></span></a> | = 0 |  |
| <span class="pre">`Definition`</span> <a href="#syside-ide-lsp-semantictokenmodifiers-definition" class="reference internal"><span class="std std-ref"></span></a> | = 1 |  |
| <span class="pre">`Readonly`</span> <a href="#syside-ide-lsp-semantictokenmodifiers-readonly" class="reference internal"><span class="std std-ref"></span></a> | = 2 |  |
| <span class="pre">`Static`</span> <a href="#syside-ide-lsp-semantictokenmodifiers-static" class="reference internal"><span class="std std-ref"></span></a> | = 3 |  |
| <span class="pre">`Deprecated`</span> <a href="#syside-ide-lsp-semantictokenmodifiers-deprecated" class="reference internal"><span class="std std-ref"></span></a> | = 4 |  |
| <span class="pre">`Abstract`</span> <a href="#syside-ide-lsp-semantictokenmodifiers-abstract" class="reference internal"><span class="std std-ref"></span></a> | = 5 |  |
| <span class="pre">`Async`</span> <a href="#syside-ide-lsp-semantictokenmodifiers-async" class="reference internal"><span class="std std-ref"></span></a> | = 6 |  |
| <span class="pre">`Modification`</span> <a href="#syside-ide-lsp-semantictokenmodifiers-modification" class="reference internal"><span class="std std-ref"></span></a> | = 7 |  |
| <span class="pre">`Documentation`</span> <a href="#syside-ide-lsp-semantictokenmodifiers-documentation" class="reference internal"><span class="std std-ref"></span></a> | = 8 |  |
| <span class="pre">`DefaultLibrary`</span> <a href="#syside-ide-lsp-semantictokenmodifiers-defaultlibrary" class="reference internal"><span class="std std-ref"></span></a> | = 9 |  |

</div>

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/ide/SemanticTokenModifiersSet.md" class="reference internal" title="syside.ide.SemanticTokenModifiersSet"><span class="pre"><code class="sourceCode python">syside.ide.SemanticTokenModifiersSet</code></span></a>

  - <a href="/python/v0.8.4/syside/ide/SemanticTokenModifiersSet.md" class="reference internal" title="syside.ide.SemanticTokenModifiersSet.__getitem__"><span class="pre"><code class="sourceCode python"><span class="fu">__getitem__</span></code></span></a>

  - <a href="/python/v0.8.4/syside/ide/SemanticTokenModifiersSet.md" class="reference internal" title="syside.ide.SemanticTokenModifiersSet.__setitem__"><span class="pre"><code class="sourceCode python"><span class="fu">__setitem__</span></code></span></a>

</div>

<!-- -->

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">SemanticTokenTypes</span></span><a href="#syside.ide.lsp.SemanticTokenTypes" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
LSP defined semantic token types. Technically, this is not a flag enum but <span class="pre">`nanobind`</span> does not permit arbitrary values otherwise.

See <a href="https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#semanticTokenTypes" class="reference external" target="_blank">LSP specification</a> and <a href="https://code.visualstudio.com/api/language-extensions/semantic-highlight-guide#standard-token-types-and-modifiers" class="reference external" target="_blank">VS Code docs</a> for more details.

<div class="pst-scrollable-table-container">

|  |  |  |
|----|----|----|
| <span class="pre">`Namespace`</span> <a href="#syside-ide-lsp-semantictokentypes-namespace" class="reference internal"><span class="std std-ref"></span></a> | = 0 |  |
| <span class="pre">`Type`</span> <a href="#syside-ide-lsp-semantictokentypes-type" class="reference internal"><span class="std std-ref"></span></a> | = 1 |  |
| <span class="pre">`Class`</span> <a href="#syside-ide-lsp-semantictokentypes-class" class="reference internal"><span class="std std-ref"></span></a> | = 2 |  |
| <span class="pre">`Enum`</span> <a href="#syside-ide-lsp-semantictokentypes-enum" class="reference internal"><span class="std std-ref"></span></a> | = 3 |  |
| <span class="pre">`Interface`</span> <a href="#syside-ide-lsp-semantictokentypes-interface" class="reference internal"><span class="std std-ref"></span></a> | = 4 |  |
| <span class="pre">`Struct`</span> <a href="#syside-ide-lsp-semantictokentypes-struct" class="reference internal"><span class="std std-ref"></span></a> | = 5 |  |
| <span class="pre">`TypeParameter`</span> <a href="#syside-ide-lsp-semantictokentypes-typeparameter" class="reference internal"><span class="std std-ref"></span></a> | = 6 |  |
| <span class="pre">`Parameter`</span> <a href="#syside-ide-lsp-semantictokentypes-parameter" class="reference internal"><span class="std std-ref"></span></a> | = 7 |  |
| <span class="pre">`Variable`</span> <a href="#syside-ide-lsp-semantictokentypes-variable" class="reference internal"><span class="std std-ref"></span></a> | = 8 |  |
| <span class="pre">`Property`</span> <a href="#syside-ide-lsp-semantictokentypes-property" class="reference internal"><span class="std std-ref"></span></a> | = 9 |  |
| <span class="pre">`EnumMember`</span> <a href="#syside-ide-lsp-semantictokentypes-enummember" class="reference internal"><span class="std std-ref"></span></a> | = 10 |  |
| <span class="pre">`Event`</span> <a href="#syside-ide-lsp-semantictokentypes-event" class="reference internal"><span class="std std-ref"></span></a> | = 11 |  |
| <span class="pre">`Function`</span> <a href="#syside-ide-lsp-semantictokentypes-function" class="reference internal"><span class="std std-ref"></span></a> | = 12 |  |
| <span class="pre">`Method`</span> <a href="#syside-ide-lsp-semantictokentypes-method" class="reference internal"><span class="std std-ref"></span></a> | = 13 |  |
| <span class="pre">`Macro`</span> <a href="#syside-ide-lsp-semantictokentypes-macro" class="reference internal"><span class="std std-ref"></span></a> | = 14 |  |
| <span class="pre">`Keyword`</span> <a href="#syside-ide-lsp-semantictokentypes-keyword" class="reference internal"><span class="std std-ref"></span></a> | = 15 |  |
| <span class="pre">`Modifier`</span> <a href="#syside-ide-lsp-semantictokentypes-modifier" class="reference internal"><span class="std std-ref"></span></a> | = 16 |  |
| <span class="pre">`Comment`</span> <a href="#syside-ide-lsp-semantictokentypes-comment" class="reference internal"><span class="std std-ref"></span></a> | = 17 |  |
| <span class="pre">`String`</span> <a href="#syside-ide-lsp-semantictokentypes-string" class="reference internal"><span class="std std-ref"></span></a> | = 18 |  |
| <span class="pre">`Number`</span> <a href="#syside-ide-lsp-semantictokentypes-number" class="reference internal"><span class="std std-ref"></span></a> | = 19 |  |
| <span class="pre">`Regexp`</span> <a href="#syside-ide-lsp-semantictokentypes-regexp" class="reference internal"><span class="std std-ref"></span></a> | = 20 |  |
| <span class="pre">`Operator`</span> <a href="#syside-ide-lsp-semantictokentypes-operator" class="reference internal"><span class="std std-ref"></span></a> | = 21 |  |
| <span class="pre">`Decorator`</span> <a href="#syside-ide-lsp-semantictokentypes-decorator" class="reference internal"><span class="std std-ref"></span></a> | = 22 |  |

</div>

<div class="toctree-wrapper compound">

</div>

</div>

</div>
