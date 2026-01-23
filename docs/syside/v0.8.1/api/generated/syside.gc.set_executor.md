<div id="syside-gc-set-executor" class="section">

# syside.gc.set\_executor[](#syside-gc-set-executor "Link to this heading")

  - <span class="sig-name descname"><span class="pre">set\_executor</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.Executor</span>](/v0.8.1/api/generated/syside.Executor.md "syside.Executor")</span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span>[](#syside.gc.set_executor "Link to this definition")  
    Assign an executor to the garbage collector. Without an executor, the garbage collector always runs on the thread that invokes it, e.g. the main thread. In addition to processing documents concurrently, documents will also be destroyed asynchronously further improving performance.

</div>
