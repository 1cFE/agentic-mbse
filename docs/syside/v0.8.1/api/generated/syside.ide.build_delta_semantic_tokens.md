<div id="syside-ide-build-delta-semantic-tokens" class="section">

# syside.ide.build\_delta\_semantic\_tokens[](#syside-ide-build-delta-semantic-tokens "Link to this heading")

  - <span class="sig-name descname"><span class="pre">build\_delta\_semantic\_tokens</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">document</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.Document</span>](/v0.8.1/api/generated/syside.Document.md "syside.Document")</span>*, *<span class="n"><span class="pre">id</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">int</span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">str</span></span>*, *<span class="n"><span class="pre">encoding</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.ide.lsp.PositionEncodingKind</span>](/v0.8.1/api/generated/syside.ide.lsp.PositionEncodingKind.md "syside.ide.lsp.PositionEncodingKind")</span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">lsp.PositionEncodingKind.Utf8</span></span>*, *<span class="n"><span class="pre">multiline\_tokens</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">True</span></span>*, *<span class="n"><span class="pre">builder</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.ide.SemanticTokensBuilder</span>](/v0.8.1/api/generated/syside.ide.SemanticTokensBuilder.md "syside.ide.SemanticTokensBuilder")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">None</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.ide.SemanticTokensBuilder</span>](/v0.8.1/api/generated/syside.ide.SemanticTokensBuilder.md "syside.ide.SemanticTokensBuilder")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span></span></span>[](#syside.ide.build_delta_semantic_tokens "Link to this definition")  
    Build full document semantic tokens for edits. Returns `builder` if successful, and `None` otherwise. Generally, `None` is returned if the `document` has nothing to highlight.
    
    Internally calls [`SemanticTokensBuilder.previous_result`](/v0.8.1/api/generated/syside.ide.SemanticTokensBuilder.md "syside.ide.SemanticTokensBuilder.previous_result") before building tokens.
    
      - Parameters<span class="colon">:</span>
        
          - **document** – The document to build full semantic tokens for.
        
          - **id** – Previous result id. `previous_result` is called first, and if the `id` matches `builder` id the returned `builder` can be used to build edits.
        
          - **encoding** – The position encoding to use for semantic tokens. Use Utf32 if interacting with Python strings.
        
          - **multiline\_tokens** – Whether to keep multiline tokens as is and not split them. Generally used for language clients that do not support multiline tokens.
        
          - **builder** – The builder to collect semantic tokens into. Note that if provided, its internal state will be reset.
    
      - Returns<span class="colon">:</span>  
        Provided `builder`, or new one otherwise, if there was anything to highlight.
    
      - Raises<span class="colon">:</span>  
        **ValueError** – If `encoding != Utf8 or not multiline_tokens` and `document.text_document is None`. Utf8 encoding and `multiline_tokens` does not require a text source as all the required information is already contained in the CST.

</div>
