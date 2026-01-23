<div id="syside-basicdocument" class="section">

# syside.BasicDocument[](#syside-basicdocument "Link to this heading")

  - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">BasicDocument</span></span>[](#syside.BasicDocument "Link to this definition")
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">text\_document</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.SharedMutex</span>](/v0.8.1/api/generated/syside.SharedMutex.md "syside.SharedMutex")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.TextDocument</span>](/v0.8.1/api/generated/syside.TextDocument.md "syside.TextDocument")<span class="p"><span class="pre">\]</span></span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span>*[](#syside.BasicDocument.text_document "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">url</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.Url</span>](/v0.8.1/api/generated/syside.Url.md "syside.Url")*[](#syside.BasicDocument.url "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">build\_state</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.BuildState</span>](/v0.8.1/api/generated/syside.BuildState.md "syside.BuildState")*[](#syside.BasicDocument.build_state "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">document\_state</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.DocumentState</span>](/v0.8.1/api/generated/syside.DocumentState.md "syside.DocumentState")*[](#syside.BasicDocument.document_state "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">document\_tier</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.DocumentTier</span>](/v0.8.1/api/generated/syside.DocumentTier.md "syside.DocumentTier")*[](#syside.BasicDocument.document_tier "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">change\_document\_tier</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.DocumentTier</span>](/v0.8.1/api/generated/syside.DocumentTier.md "syside.DocumentTier")</span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span>[](#syside.BasicDocument.change_document_tier "Link to this definition")  
        Set `document_tier` to another value. This is a method rather than a function because tier should not change throughout document lifetime. Nevertheless, this is still useful in cases where a document has just been constructed and its attributes need to be changed.
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">language</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span>*[](#syside.BasicDocument.language "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">version</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.DocumentVersion</span>](/v0.8.1/api/generated/syside.DocumentVersion.md "syside.DocumentVersion")*[](#syside.BasicDocument.version "Link to this definition")  
        The version of the last build. This corresponds to the version of `TextDocument` this was built from.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">increment\_version</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span>[](#syside.BasicDocument.increment_version "Link to this definition")  
        Increment sema version. Source version is automatically handled by source parser.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_hash\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">int</span></span></span>[](#syside.BasicDocument.__hash__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_cpp\_name\_\_</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">'syside::BasicDocument'</span>*[](#syside.BasicDocument.__cpp_name__ "Link to this definition")

</div>
