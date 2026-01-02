<div id="syside-ioschedule" class="section">

# syside.IOSchedule[](#syside-ioschedule "Link to this heading")

  - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">IOSchedule</span></span>[](#syside.IOSchedule "Link to this definition")
    
      - *<span class="pre">static</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">make\_empty\_schedule</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">multithreaded</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">False</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.IOSchedule</span>](#syside.IOSchedule "syside.IOSchedule")</span></span>[](#syside.IOSchedule.make_empty_schedule "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">text\_documents</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.TextDocuments</span>](/v0.8.1/api/generated/syside.TextDocuments.md "syside.TextDocuments")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span>*[](#syside.IOSchedule.text_documents "Link to this definition")  
        `TextDocuments` that new text files will be opened in
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">is\_multithreaded</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*[](#syside.IOSchedule.is_multithreaded "Link to this definition")  
        If true, new text documents will be constructed for multithreaded application, otherwise - single threaded. Only has effect if no `TextDocuments` is set.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">set\_multithreaded</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.IOSchedule</span>](#syside.IOSchedule "syside.IOSchedule")</span></span>[](#syside.IOSchedule.set_multithreaded "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">assign\_text\_documents</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.TextDocuments</span>](/v0.8.1/api/generated/syside.TextDocuments.md "syside.TextDocuments")</span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.IOSchedule</span>](#syside.IOSchedule "syside.IOSchedule")</span></span>[](#syside.IOSchedule.assign_text_documents "Link to this definition")  
        Set `TextDocuments` that new text files will be opened in
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">add\_file</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">path</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">os.PathLike</span><span class="p"><span class="pre">\[</span></span><span class="pre">AnyStr</span><span class="p"><span class="pre">\]</span></span></span>*, *<span class="n"><span class="pre">language</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="n"><span class="pre">tier</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.DocumentTier</span>](/v0.8.1/api/generated/syside.DocumentTier.md "syside.DocumentTier")</span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">DocumentTier.Project</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.IOSchedule</span>](#syside.IOSchedule "syside.IOSchedule")</span></span>[](#syside.IOSchedule.add_file "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">add\_source</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">url</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.Url</span>](/v0.8.1/api/generated/syside.Url.md "syside.Url")</span>*, *<span class="n"><span class="pre">contents</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="n"><span class="pre">language</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="n"><span class="pre">tier</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.DocumentTier</span>](/v0.8.1/api/generated/syside.DocumentTier.md "syside.DocumentTier")</span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">DocumentTier.Project</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.IOSchedule</span>](#syside.IOSchedule "syside.IOSchedule")</span></span>[](#syside.IOSchedule.add_source "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">size</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">int</span>*[](#syside.IOSchedule.size "Link to this definition")  
        Returns the number of currently scheduled documents
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">set\_completion\_callback</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">Callable</span><span class="p"><span class="pre">\[</span></span><span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.SharedMutex</span>](/v0.8.1/api/generated/syside.SharedMutex.md "syside.SharedMutex")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.TextDocument</span>](/v0.8.1/api/generated/syside.TextDocument.md "syside.TextDocument")<span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">,</span></span><span class="w"> </span>[<span class="pre">syside.IOSchedule</span>](#syside.IOSchedule "syside.IOSchedule")<span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">None</span><span class="p"><span class="pre">\]</span></span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.IOSchedule</span>](#syside.IOSchedule "syside.IOSchedule")</span></span>[](#syside.IOSchedule.set_completion_callback "Link to this definition")  
        Set completion callback that will be invoked when a text document is ready. The second callback argument contains the index of the document, and order between add\_\* is preserved. Note that this may be called from multiple other threads so this should be thread-safe, e.g. by sizing a result buffer to size() before executing this schedule and only modifying the element at the callback index.
        
        On a single-thread executor, only the first enqueued unique source will invoke this callback. On multithreaded executors, any one of duplicated sources may invoke this callback, however it is unspecified which. Deduplication is performed based on resolved absolute URLs.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_cpp\_name\_\_</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">'syside::IOSchedule'</span>*[](#syside.IOSchedule.__cpp_name__ "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">CallbackData</span></span>[](#syside.IOSchedule.CallbackData "Link to this definition")
        
          - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">index</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">int</span>*[](#syside.IOSchedule.CallbackData.index "Link to this definition")  
            The index of the associated text document. Matches the order it was added to the schedule.
        
        <!-- end list -->
        
          - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">tier</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.DocumentTier</span>](/v0.8.1/api/generated/syside.DocumentTier.md "syside.DocumentTier")*[](#syside.IOSchedule.CallbackData.tier "Link to this definition")  
            Tier the text document was added with.

</div>
