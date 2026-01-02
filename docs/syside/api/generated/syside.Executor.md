<div id="syside-executor" class="section">

# syside.Executor[](#syside-executor "Link to this heading")

  - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">Executor</span></span>[](#syside.Executor "Link to this definition")  
    Initialization
    
    Default constructor using as many workers as possible
    
      - <span class="sig-name descname"><span class="pre">run</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">schedule</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.Schedule</span>](/v0.8.1/api/generated/syside.Schedule.md "syside.Schedule")</span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.ExecutionResult</span>](/v0.8.1/api/generated/syside.ExecutionResult.md "syside.ExecutionResult")</span></span>[](#syside.Executor.run "Link to this definition")  
        Execute a schedule. Note that schedules are consumed and trying to access them again will result in an error
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">run</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">schedule</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.IOSchedule</span>](/v0.8.1/api/generated/syside.IOSchedule.md "syside.IOSchedule")</span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.IOSchedule</span>](/v0.8.1/api/generated/syside.IOSchedule.md "syside.IOSchedule")<span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">list</span><span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.SharedMutex</span>](/v0.8.1/api/generated/syside.SharedMutex.md "syside.SharedMutex")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.TextDocument</span>](/v0.8.1/api/generated/syside.TextDocument.md "syside.TextDocument")<span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">\]</span></span></span></span>
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">num\_workers</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">int</span>*[](#syside.Executor.num_workers "Link to this definition")  
        Returns the number of worker threads associated with this executor.

</div>
