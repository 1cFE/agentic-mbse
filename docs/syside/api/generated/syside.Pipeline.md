<div id="syside-pipeline" class="section">

# syside.Pipeline[](#syside-pipeline "Link to this heading")

  - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">Pipeline</span></span>[](#syside.Pipeline "Link to this definition")
    
      - <span class="sig-name descname"><span class="pre">schedule</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">documents</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">Sequence</span><span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.SharedMutex</span>](/v0.8.1/api/generated/syside.SharedMutex.md "syside.SharedMutex")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.BasicDocument</span>](/v0.8.1/api/generated/syside.BasicDocument.md "syside.BasicDocument")<span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">\]</span></span></span>*, *<span class="n"><span class="pre">options</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.ScheduleOptions</span>](/v0.8.1/api/generated/syside.ScheduleOptions.md "syside.ScheduleOptions")</span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">...</span></span>*, *<span class="n"><span class="pre">invalidated</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">Sequence</span><span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.SharedMutex</span>](/v0.8.1/api/generated/syside.SharedMutex.md "syside.SharedMutex")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.BasicDocument</span>](/v0.8.1/api/generated/syside.BasicDocument.md "syside.BasicDocument")<span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">\]</span></span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">\[\]</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.Schedule</span>](/v0.8.1/api/generated/syside.Schedule.md "syside.Schedule")</span></span>[](#syside.Pipeline.schedule "Link to this definition")  
        Schedule `documents` for building with this `Pipeline`. `documents` with `build_state` equal or greater to the state at the end of particular pipeline stage will not be scheduled for that stage. For example, a document with `build_state >= BuildState.Parsed` will not be scheduled for parsing.
        
        Pipeline also accepts additional `invalidated` documents that will have their semantic states reset. These documents will then pass through sema and validation stages as normal. This should typically be used for documents that have had their dependencies modified. Any documents for which `build_state < BuildState.Built` will not be invalidated as there should be nothing to invalidate.
        
        The returned schedule should be executed on an `Executor`:
        
        <div class="highlight-python notranslate">
        
        <div class="highlight">
        
            executor = syside.Executor(...)
            schedule = pipeline.schedule(...)
            ...
            result = executor.run(schedule)
        
        </div>
        
        </div>
        
        Note that pipeline will skip indexing certain URLs that are used by IDEs to display virtual documents:
        
          - `git*://*`, e.g. used by VS Code to display `git` diffs
        
          - `vscode*://*`, e.g. used by VS Code to display editor previews
        
          - `<scheme>[:|://]` (URL with scheme only), e.g. used by Neovim for new unnamed buffers
        
        The first two patterns additionally skip validation since those virtual documents are never a part of the workspace. Indexing is skipped only for known URL patterns to avoid unexpected behaviour. However, prefer using common schemes such as `file` or `http[s]` to ensure that the documents are handled correctly as more URL patterns may be added as more IDEs are tested.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_cpp\_name\_\_</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">'syside::Pipeline'</span>*[](#syside.Pipeline.__cpp_name__ "Link to this definition")

</div>
