<div id="syside-ide-lsp-semantictokens" class="section">

# syside.ide.lsp.SemanticTokens[](#syside-ide-lsp-semantictokens "Link to this heading")

  - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">SemanticTokens</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">result\_id</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">None</span></span>*, *<span class="n"><span class="pre">data</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">Sequence</span><span class="p"><span class="pre">\[</span></span><span class="pre">int</span><span class="p"><span class="pre">\]</span></span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">\[\]</span></span>*<span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokens "Link to this definition")  
    Initialization
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">result\_id</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span>*[](#syside.ide.lsp.SemanticTokens.result_id "Link to this definition")  
        An optional result id. If provided and clients support delta updating the client will include the result id in the next semantic token request. A server can then instead of computing all semantic tokens again simply send a delta.
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">data</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.ContainerView</span>](/v0.8.1/api/generated/syside.ContainerView.md "syside.ContainerView")<span class="p"><span class="pre">\[</span></span><span class="pre">int</span><span class="p"><span class="pre">\]</span></span>*[](#syside.ide.lsp.SemanticTokens.data "Link to this definition")  
        The actual tokens.

</div>
