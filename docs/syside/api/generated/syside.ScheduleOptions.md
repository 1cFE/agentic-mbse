<div id="syside-scheduleoptions" class="section">

# syside.ScheduleOptions[](#syside-scheduleoptions "Link to this heading")

  - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">ScheduleOptions</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">validation\_timing</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.ValidationTiming</span>](/v0.8.1/api/generated/syside.ValidationTiming.md "syside.ValidationTiming")</span>*, *<span class="n"><span class="pre">cutoff</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.BuildState</span>](/v0.8.1/api/generated/syside.BuildState.md "syside.BuildState")</span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">BuildState.Validated</span></span>*, *<span class="n"><span class="pre">force\_revalidation</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">False</span></span>*, *<span class="n"><span class="pre">attach\_comments</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">False</span></span>*, *<span class="n"><span class="pre">validation\_tier</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.DocumentTier</span>](/v0.8.1/api/generated/syside.DocumentTier.md "syside.DocumentTier")</span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">DocumentTier.Project</span></span>*<span class="sig-paren">)</span>[](#syside.ScheduleOptions "Link to this definition")  
    Initialization
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">validation\_timing</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.ValidationTiming</span>](/v0.8.1/api/generated/syside.ValidationTiming.md "syside.ValidationTiming")*[](#syside.ScheduleOptions.validation_timing "Link to this definition")  
        Which validations to run.
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">validation\_tier</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.DocumentTier</span>](/v0.8.1/api/generated/syside.DocumentTier.md "syside.DocumentTier")*[](#syside.ScheduleOptions.validation_tier "Link to this definition")  
        Lowest tier of documents to validate. For example, `Projects` will validate only project documents, while `StandardLibrary` - everything.
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">cutoff</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.BuildState</span>](/v0.8.1/api/generated/syside.BuildState.md "syside.BuildState")*[](#syside.ScheduleOptions.cutoff "Link to this definition")  
        The last stage in the pipeline that will be executed. Any stages higher than `cutoff` will be ignored.
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">force\_revalidation</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*[](#syside.ScheduleOptions.force_revalidation "Link to this definition")  
        If true, validated documents will be validated again.
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">attach\_comments</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*[](#syside.ScheduleOptions.attach_comments "Link to this definition")  
        If true, comments will be attached. Mainly useful for formatters.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_cpp\_name\_\_</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">'syside::ScheduleOptions'</span>*[](#syside.ScheduleOptions.__cpp_name__ "Link to this definition")

</div>
