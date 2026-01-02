<div id="syside-ide-semantictokensbuilder" class="section">

# syside.ide.SemanticTokensBuilder[](#syside-ide-semantictokensbuilder "Link to this heading")

  - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">SemanticTokensBuilder</span></span>[](#syside.ide.SemanticTokensBuilder "Link to this definition")  
    Helper for building LSP compatible semantic tokens.
    
    Initialization
    
      - <span class="sig-name descname"><span class="pre">append</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.ide.AbsoluteSemanticToken</span>](/v0.8.1/api/generated/syside.ide.AbsoluteSemanticToken.md "syside.ide.AbsoluteSemanticToken")</span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span>[](#syside.ide.SemanticTokensBuilder.append "Link to this definition")  
        Append a new semantic token.
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">id</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">int</span>*[](#syside.ide.SemanticTokensBuilder.id "Link to this definition")  
        Randomly generated ID of this builder.
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">absolute\_tokens</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.ContainerView</span>](/v0.8.1/api/generated/syside.ContainerView.md "syside.ContainerView")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.ide.AbsoluteSemanticToken</span>](/v0.8.1/api/generated/syside.ide.AbsoluteSemanticToken.md "syside.ide.AbsoluteSemanticToken")<span class="p"><span class="pre">\]</span></span>*[](#syside.ide.SemanticTokensBuilder.absolute_tokens "Link to this definition")  
        Get all collected absolute semantic tokens. Note that this may require decoding delta tokens first.
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">delta\_tokens</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.ContainerView</span>](/v0.8.1/api/generated/syside.ContainerView.md "syside.ContainerView")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.ide.DeltaSemanticToken</span>](/v0.8.1/api/generated/syside.ide.DeltaSemanticToken.md "syside.ide.DeltaSemanticToken")<span class="p"><span class="pre">\]</span></span>*[](#syside.ide.SemanticTokensBuilder.delta_tokens "Link to this definition")  
        Get all collected delta semantic tokens. Note that in case tokens were appended out of order, an encoding may take place.
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">previous\_tokens</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.ContainerView</span>](/v0.8.1/api/generated/syside.ContainerView.md "syside.ContainerView")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.ide.DeltaSemanticToken</span>](/v0.8.1/api/generated/syside.ide.DeltaSemanticToken.md "syside.ide.DeltaSemanticToken")<span class="p"><span class="pre">\]</span></span>*[](#syside.ide.SemanticTokensBuilder.previous_tokens "Link to this definition")  
        Get previously built tokens as delta tokens. Must call `previous_result` to make this available.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">previous\_result</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">int</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span>[](#syside.ide.SemanticTokensBuilder.previous_result "Link to this definition")  
        Move the contents of this builder to previous result and reset the state. If id does not match `id`, current tokens are discarded instead. This must be called before building edits.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">previous\_result</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span>  
        Overload of `previous_result` that will parse the provided id to int.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">build</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.ide.lsp.SemanticTokens</span>](/v0.8.1/api/generated/syside.ide.lsp.SemanticTokens.md "syside.ide.lsp.SemanticTokens")</span></span>[](#syside.ide.SemanticTokensBuilder.build "Link to this definition")  
        Build currently collected semantic tokens into LSP compatible format.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">build\_edits</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.ide.lsp.SemanticTokens</span>](/v0.8.1/api/generated/syside.ide.lsp.SemanticTokens.md "syside.ide.lsp.SemanticTokens")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span>[<span class="pre">syside.ide.lsp.SemanticTokensDelta</span>](/v0.8.1/api/generated/syside.ide.lsp.SemanticTokensDelta.md "syside.ide.lsp.SemanticTokensDelta")</span></span>[](#syside.ide.SemanticTokensBuilder.build_edits "Link to this definition")  
        Build currently collected semantic tokens into LSP compatible format. If `can_build_edits`, a delta to the `previous_tokens` will be returned which will usually be smaller than the full tokens.
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">can\_build\_edits</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*[](#syside.ide.SemanticTokensBuilder.can_build_edits "Link to this definition")  
        Returns `true` if `build_edits` would return delta to the previous result.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_cpp\_name\_\_</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">'syside::ide::SemanticTokensBuilder'</span>*[](#syside.ide.SemanticTokensBuilder.__cpp_name__ "Link to this definition")

</div>
