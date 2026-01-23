<div id="syside-build-model" class="section">

# syside.build\_model[](#syside-build-model "Link to this heading")

  - <span class="sig-name descname"><span class="pre">build\_model</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">document</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.Document</span>](/v0.8.1/api/generated/syside.Document.md "syside.Document")</span>*, *<span class="n"><span class="pre">language</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.ModelLanguage</span>](/v0.8.1/api/generated/syside.ModelLanguage.md "syside.ModelLanguage")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">None</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">list</span><span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Diagnostic</span>](/v0.8.1/api/generated/syside.Diagnostic.md "syside.Diagnostic")<span class="p"><span class="pre">\]</span></span></span></span>[](#syside.build_model "Link to this definition")  
    Build the AST for `document` from its `text_document`. Any existing model will be cleared, and the built model will not have its references linked. Instead, most references will use placeholder references that will be replaced by actual targets in linking stage. Only `sysml` and `kerml` languages are supported.
    
    This is a CST -\> AST stage in the pipeline.
    
    Raises `ValueError` if the `document` has unsupported language, or it has no associated `text_document`.

</div>
