<div id="syside-diagnostic" class="section">

# syside.Diagnostic[](#syside-diagnostic "Link to this heading")

  - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">Diagnostic</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">segment</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.DocumentSegment</span>](/v0.8.1/api/generated/syside.DocumentSegment.md "syside.DocumentSegment")</span>*, *<span class="n"><span class="pre">code</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">str</span></span>*, *<span class="n"><span class="pre">message</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="n"><span class="pre">severity</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.DiagnosticSeverity</span>](/v0.8.1/api/generated/syside.DiagnosticSeverity.md "syside.DiagnosticSeverity")</span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">DiagnosticSeverity.Error</span></span>*<span class="sig-paren">)</span>[](#syside.Diagnostic "Link to this definition")  
    Initialization
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">segment</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.DocumentSegment</span>](/v0.8.1/api/generated/syside.DocumentSegment.md "syside.DocumentSegment")*[](#syside.Diagnostic.segment "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">code</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">str</span>*[](#syside.Diagnostic.code "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">message</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span>*[](#syside.Diagnostic.message "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">severity</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.DiagnosticSeverity</span>](/v0.8.1/api/generated/syside.DiagnosticSeverity.md "syside.DiagnosticSeverity")*[](#syside.Diagnostic.severity "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">is\_unnecessary</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*[](#syside.Diagnostic.is_unnecessary "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">is\_deprecated</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*[](#syside.Diagnostic.is_deprecated "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">code\_description</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.CodeDescription</span>](/v0.8.1/api/generated/syside.CodeDescription.md "syside.CodeDescription")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span>*[](#syside.Diagnostic.code_description "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">source</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span>*[](#syside.Diagnostic.source "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">related\_information</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.ContainerView</span>](/v0.8.1/api/generated/syside.ContainerView.md "syside.ContainerView")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.DiagnosticRelatedInformation</span>](/v0.8.1/api/generated/syside.DiagnosticRelatedInformation.md "syside.DiagnosticRelatedInformation")<span class="p"><span class="pre">\]</span></span>*[](#syside.Diagnostic.related_information "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">append\_related\_information</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.DiagnosticRelatedInformation</span>](/v0.8.1/api/generated/syside.DiagnosticRelatedInformation.md "syside.DiagnosticRelatedInformation")</span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span>[](#syside.Diagnostic.append_related_information "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_str\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">str</span></span></span>[](#syside.Diagnostic.__str__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_eq\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">object</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">bool</span></span></span>[](#syside.Diagnostic.__eq__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_ne\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">object</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">bool</span></span></span>[](#syside.Diagnostic.__ne__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_cpp\_name\_\_</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">'syside::Diagnostic'</span>*[](#syside.Diagnostic.__cpp_name__ "Link to this definition")

</div>
