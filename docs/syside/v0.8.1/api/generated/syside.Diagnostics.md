<div id="syside-diagnostics" class="section">

# syside.Diagnostics[](#syside-diagnostics "Link to this heading")

  - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">Diagnostics</span></span>[](#syside.Diagnostics "Link to this definition")  
    All model diagnostics.
    
      - <span class="sig-name descname"><span class="pre">parser</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">list</span><span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.DiagnosticMessage</span>](/v0.8.1/api/generated/syside.DiagnosticMessage.md "syside.DiagnosticMessage")<span class="p"><span class="pre">\]</span></span><span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">None</span>*[](#syside.Diagnostics.parser "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">validation</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">list</span><span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.DiagnosticMessage</span>](/v0.8.1/api/generated/syside.DiagnosticMessage.md "syside.DiagnosticMessage")<span class="p"><span class="pre">\]</span></span><span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">None</span>*[](#syside.Diagnostics.validation "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">sema</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">list</span><span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.DiagnosticMessage</span>](/v0.8.1/api/generated/syside.DiagnosticMessage.md "syside.DiagnosticMessage")<span class="p"><span class="pre">\]</span></span><span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">None</span>*[](#syside.Diagnostics.sema "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">all</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">Generator</span><span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.DiagnosticMessage</span>](/v0.8.1/api/generated/syside.DiagnosticMessage.md "syside.DiagnosticMessage")<span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">None</span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">None</span><span class="p"><span class="pre">\]</span></span>*[](#syside.Diagnostics.all "Link to this definition")  
        Iterate over all diagnostics.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">all\_with\_severity</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">severity</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.DiagnosticSeverity</span>](/v0.8.1/api/generated/syside.DiagnosticSeverity.md "syside.DiagnosticSeverity")</span>*, *<span class="n"><span class="pre">include\_higher\_severity</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">False</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">Generator</span><span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.DiagnosticMessage</span>](/v0.8.1/api/generated/syside.DiagnosticMessage.md "syside.DiagnosticMessage")<span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">None</span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">None</span><span class="p"><span class="pre">\]</span></span></span></span>[](#syside.Diagnostics.all_with_severity "Link to this definition")  
        Iterate over all diagnostics with the given severity.
        
          - Parameters<span class="colon">:</span>
            
              - **severity** – The severity of diagnostics to iterate over.
            
              - **include\_higher\_severity** – Whether to include diagnostics that are of higher severity than the given one.
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">errors</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">Generator</span><span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.DiagnosticMessage</span>](/v0.8.1/api/generated/syside.DiagnosticMessage.md "syside.DiagnosticMessage")<span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">None</span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">None</span><span class="p"><span class="pre">\]</span></span>*[](#syside.Diagnostics.errors "Link to this definition")  
        Iterate over all diagnostics with error severity.
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">warnings</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">Generator</span><span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.DiagnosticMessage</span>](/v0.8.1/api/generated/syside.DiagnosticMessage.md "syside.DiagnosticMessage")<span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">None</span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">None</span><span class="p"><span class="pre">\]</span></span>*[](#syside.Diagnostics.warnings "Link to this definition")  
        Iterate over all diagnostics with warning severity.
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">infos</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">Generator</span><span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.DiagnosticMessage</span>](/v0.8.1/api/generated/syside.DiagnosticMessage.md "syside.DiagnosticMessage")<span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">None</span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">None</span><span class="p"><span class="pre">\]</span></span>*[](#syside.Diagnostics.infos "Link to this definition")  
        Iterate over all diagnostics with information severity.
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">hints</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">Generator</span><span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.DiagnosticMessage</span>](/v0.8.1/api/generated/syside.DiagnosticMessage.md "syside.DiagnosticMessage")<span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">None</span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">None</span><span class="p"><span class="pre">\]</span></span>*[](#syside.Diagnostics.hints "Link to this definition")  
        Iterate over all diagnostics with hint severity.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">contains\_errors</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">warnings\_as\_errors</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">False</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">bool</span></span></span>[](#syside.Diagnostics.contains_errors "Link to this definition")  
        Checks whether any of the diagnostics contain errors.
        
          - Parameters<span class="colon">:</span>  
            **warnings\_as\_errors** – Treat warnings as errors.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_str\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">str</span></span></span>[](#syside.Diagnostics.__str__ "Link to this definition")

</div>
