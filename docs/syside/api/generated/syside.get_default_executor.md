<div id="syside-get-default-executor" class="section">

# syside.get\_default\_executor[](#syside-get-default-executor "Link to this heading")

  - <span class="sig-name descname"><span class="pre">get\_default\_executor</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.Executor</span>](/v0.8.1/api/generated/syside.Executor.md "syside.Executor")</span></span>[](#syside.get_default_executor "Link to this definition")  
    Get a default initialized `Executor` for running schedules. Default executor will use half the logical cores that are available on the current machine. An executor is just a thread pool so there is no reason for constructing and destroying one all the time.

</div>
