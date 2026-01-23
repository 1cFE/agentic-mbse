<div id="syside-ide-build-range-semantic-tokens" class="section">

# syside.ide.build\_range\_semantic\_tokens[](#syside-ide-build-range-semantic-tokens "Link to this heading")

  - <span class="sig-name descname"><span class="pre">build\_range\_semantic\_tokens</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">document</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.Document</span>](/v0.8.1/api/generated/syside.Document.md "syside.Document")</span>*, *<span class="n"><span class="pre">range</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.RangeUtf8</span>](/v0.8.1/api/generated/syside.RangeUtf8.md "syside.RangeUtf8")</span>*, *<span class="n"><span class="pre">encoding</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.ide.lsp.PositionEncodingKind</span>](/v0.8.1/api/generated/syside.ide.lsp.PositionEncodingKind.md "syside.ide.lsp.PositionEncodingKind")</span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">lsp.PositionEncodingKind.Utf8</span></span>*, *<span class="n"><span class="pre">multiline\_tokens</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">True</span></span>*, *<span class="n"><span class="pre">builder</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.ide.SemanticTokensBuilder</span>](/v0.8.1/api/generated/syside.ide.SemanticTokensBuilder.md "syside.ide.SemanticTokensBuilder")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">None</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.ide.SemanticTokensBuilder</span>](/v0.8.1/api/generated/syside.ide.SemanticTokensBuilder.md "syside.ide.SemanticTokensBuilder")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span></span></span>[](#syside.ide.build_range_semantic_tokens "Link to this definition")  
    Build range document semantic tokens. Returns `builder` if successful, and `None` otherwise. Generally, `None` is returned if the `document` has nothing to highlight.
    
    The returned `builder` will contain tokens encompassing `range`. For most documents, this will be more efficient that building full semantic tokens.
    
      - Parameters<span class="colon">:</span>
        
          - **document** – The document to build range semantic tokens for.
        
          - **range** – Range that should have all tokens highlighted. Implementation may return also build tokens outside of this range.
        
          - **encoding** – The position encoding to use for semantic tokens. Use Utf32 if interacting with Python strings.
        
          - **multiline\_tokens** – Whether to keep multiline tokens as is and not split them. Generally used for language clients that do not support multiline tokens.
        
          - **builder** – The builder to collect semantic tokens into. Note that if provided, its internal state will be reset.
    
      - Returns<span class="colon">:</span>  
        Provided `builder`, or new one otherwise, if there was anything to highlight.
    
      - Raises<span class="colon">:</span>  
        **ValueError** – If `encoding != Utf8 or not multiline_tokens` and `document.text_document is None`. Utf8 encoding and `multiline_tokens` does not require a text source as all the required information is already contained in the CST.

</div>
