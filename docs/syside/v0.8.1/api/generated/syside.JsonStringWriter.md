<div id="syside-jsonstringwriter" class="section">

# syside.JsonStringWriter[](#syside-jsonstringwriter "Link to this heading")

  - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">JsonStringWriter</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.JsonStringOptions</span>](/v0.8.1/api/generated/syside.JsonStringOptions.md "syside.JsonStringOptions")</span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">...</span></span>*<span class="sig-paren">)</span>[](#syside.JsonStringWriter "Link to this definition")  
    Bases: [`Writer`](/v0.8.1/api/generated/syside.Writer.md "syside.Writer")\[`str`\]
    
    Serialization writer that outputs JSON string
    
    Initialization
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">partial\_result</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span>*[](#syside.JsonStringWriter.partial_result "Link to this definition")  
        Currently written text. May be incomplete JSON string.
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">result</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span>*[](#syside.JsonStringWriter.result "Link to this definition")  
        Result of serialization. Guaranteed to be valid JSON string.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">clear</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span>[](#syside.JsonStringWriter.clear "Link to this definition")  
        Clear result. This is called automatically when serialization starts.
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">options</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.JsonStringOptions</span>](/v0.8.1/api/generated/syside.JsonStringOptions.md "syside.JsonStringOptions")*[](#syside.JsonStringWriter.options "Link to this definition")  
        Currently set options. Note that this returns a copy of the options.

</div>
