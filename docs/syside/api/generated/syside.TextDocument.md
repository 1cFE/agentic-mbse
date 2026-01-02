<div id="syside-textdocument" class="section">

# syside.TextDocument[](#syside-textdocument "Link to this heading")

  - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">TextDocument</span></span>[](#syside.TextDocument "Link to this definition")
    
      - *<span class="pre">static</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">create\_st</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.SharedMutex</span>](/v0.8.1/api/generated/syside.SharedMutex.md "syside.SharedMutex")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.TextDocument</span>](#syside.TextDocument "syside.TextDocument")<span class="p"><span class="pre">\]</span></span></span></span>[](#syside.TextDocument.create_st "Link to this definition")  
        Create an empty TextDocument for single-threaded applications
    
    <!-- end list -->
    
      - *<span class="pre">static</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">create\_st</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">url</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.Url</span>](/v0.8.1/api/generated/syside.Url.md "syside.Url")</span>*, *<span class="n"><span class="pre">language</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="n"><span class="pre">content</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="n"><span class="pre">version</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">int</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">0</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.SharedMutex</span>](/v0.8.1/api/generated/syside.SharedMutex.md "syside.SharedMutex")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.TextDocument</span>](#syside.TextDocument "syside.TextDocument")<span class="p"><span class="pre">\]</span></span></span></span>
    
    <!-- end list -->
    
      - *<span class="pre">static</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">create\_mt</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.SharedMutex</span>](/v0.8.1/api/generated/syside.SharedMutex.md "syside.SharedMutex")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.TextDocument</span>](#syside.TextDocument "syside.TextDocument")<span class="p"><span class="pre">\]</span></span></span></span>[](#syside.TextDocument.create_mt "Link to this definition")  
        Create an empty TextDocument for multi-threaded applications
    
    <!-- end list -->
    
      - *<span class="pre">static</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">create\_mt</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">url</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.Url</span>](/v0.8.1/api/generated/syside.Url.md "syside.Url")</span>*, *<span class="n"><span class="pre">language</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="n"><span class="pre">content</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="n"><span class="pre">version</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">int</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">0</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.SharedMutex</span>](/v0.8.1/api/generated/syside.SharedMutex.md "syside.SharedMutex")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.TextDocument</span>](#syside.TextDocument "syside.TextDocument")<span class="p"><span class="pre">\]</span></span></span></span>
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">url</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.Url</span>](/v0.8.1/api/generated/syside.Url.md "syside.Url")*[](#syside.TextDocument.url "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">language\_id</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span>*[](#syside.TextDocument.language_id "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">version</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">int</span>*[](#syside.TextDocument.version "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">text</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span>*[](#syside.TextDocument.text "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">get\_text</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">range</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.RangeUtf8</span>](/v0.8.1/api/generated/syside.RangeUtf8.md "syside.RangeUtf8")</span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">str</span></span></span>[](#syside.TextDocument.get_text "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">get\_text</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">range</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.RangeUtf16</span>](/v0.8.1/api/generated/syside.RangeUtf16.md "syside.RangeUtf16")</span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">str</span></span></span>
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">get\_text</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">range</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.RangeUtf32</span>](/v0.8.1/api/generated/syside.RangeUtf32.md "syside.RangeUtf32")</span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">str</span></span></span>
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">offset\_at</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">position</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.PositionUtf8</span>](/v0.8.1/api/generated/syside.PositionUtf8.md "syside.PositionUtf8")</span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">int</span></span></span>[](#syside.TextDocument.offset_at "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">offset\_at</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">position</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.PositionUtf16</span>](/v0.8.1/api/generated/syside.PositionUtf16.md "syside.PositionUtf16")</span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">int</span></span></span>
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">offset\_at</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">position</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.PositionUtf32</span>](/v0.8.1/api/generated/syside.PositionUtf32.md "syside.PositionUtf32")</span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">int</span></span></span>
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">utf8\_position\_at</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">offset</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">int</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.PositionUtf8</span>](/v0.8.1/api/generated/syside.PositionUtf8.md "syside.PositionUtf8")</span></span>[](#syside.TextDocument.utf8_position_at "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">utf16\_position\_at</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">offset</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">int</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.PositionUtf16</span>](/v0.8.1/api/generated/syside.PositionUtf16.md "syside.PositionUtf16")</span></span>[](#syside.TextDocument.utf16_position_at "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">utf32\_position\_at</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">offset</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">int</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.PositionUtf32</span>](/v0.8.1/api/generated/syside.PositionUtf32.md "syside.PositionUtf32")</span></span>[](#syside.TextDocument.utf32_position_at "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">line\_count</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">int</span>*[](#syside.TextDocument.line_count "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">update</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">changes</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">Sequence</span><span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.TextDocumentEditUtf8</span>](/v0.8.1/api/generated/syside.TextDocumentEditUtf8.md "syside.TextDocumentEditUtf8")<span class="p"><span class="pre">\]</span></span></span>*, *<span class="n"><span class="pre">version</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">int</span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">None</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span>[](#syside.TextDocument.update "Link to this definition")

</div>
