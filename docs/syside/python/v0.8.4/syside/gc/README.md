<div id="module-syside.gc" class="section">

<span id="gc"></span>

# gc<a href="#module-syside.gc" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

Internal GC interface. Currently only Documents are collected by the internal garbage collector.

<div id="index" class="section">

## <span class="nerd-font"></span> Index<a href="#index" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

<span class="sd-summary-text"><span class="nerd-font"></span> **Classes** <a href="#syside-gc-classes-table" class="reference internal"><span class="std std-ref"></span></a></span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |
|----|----|----|
| <a href="/python/v0.8.4/syside/gc/Debug.md" class="reference internal" title="syside.gc.Debug"><span class="pre"><code class="sourceCode python">Debug</code></span></a> |  | Debug options for the garbage collector. |

</div>

</div>

<span class="sd-summary-text"><span class="nerd-font"></span> **Functions** <a href="#syside-gc-functions-table" class="reference internal"><span class="std std-ref"></span></a></span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |
|----|----|----|
| <a href="#syside.gc.collect" class="reference internal" title="syside.gc.collect"><span class="pre"><code class="sourceCode python">collect</code></span></a> |  | Explicitly call garbage collector once. |
| <a href="#syside.gc.disable" class="reference internal" title="syside.gc.disable"><span class="pre"><code class="sourceCode python">disable</code></span></a> |  | Disable automatic garbage collection. |
| <a href="#syside.gc.enable" class="reference internal" title="syside.gc.enable"><span class="pre"><code class="sourceCode python">enable</code></span></a> |  | Enable automatic garbage collection. |
| <a href="#syside.gc.get_count" class="reference internal" title="syside.gc.get_count"><span class="pre"><code class="sourceCode python">get_count</code></span></a> |  | Returns the number of currently tracked objects. |
| <a href="#syside.gc.get_debug" class="reference internal" title="syside.gc.get_debug"><span class="pre"><code class="sourceCode python">get_debug</code></span></a> |  | Return a copy of the current debug options of the garbage collector. |
| <a href="#syside.gc.get_executor" class="reference internal" title="syside.gc.get_executor"><span class="pre"><code class="sourceCode python">get_executor</code></span></a> |  | The executor assigned to the garbage collector. |
| <a href="#syside.gc.get_threshold" class="reference internal" title="syside.gc.get_threshold"><span class="pre"><code class="sourceCode python">get_threshold</code></span></a> |  | Return the current threshold. |
| <a href="#syside.gc.is_tracked" class="reference internal" title="syside.gc.is_tracked"><span class="pre"><code class="sourceCode python">is_tracked</code></span></a> |  | Returns <span class="pre">`True`</span> if <span class="pre">`document`</span> is tracked by the garbage collector. |
| <a href="#syside.gc.isenabled" class="reference internal" title="syside.gc.isenabled"><span class="pre"><code class="sourceCode python">isenabled</code></span></a> |  | Returns <span class="pre">`True`</span> if automatic collection is enabled. |
| <a href="#syside.gc.set_debug" class="reference internal" title="syside.gc.set_debug"><span class="pre"><code class="sourceCode python">set_debug</code></span></a> |  | Set default options for the garbage collector. By default, everything is printed to stderr. |
| <a href="#syside.gc.set_executor" class="reference internal" title="syside.gc.set_executor"><span class="pre"><code class="sourceCode python">set_executor</code></span></a> |  | Assign an executor to the garbage collector. Without an executor, the garbage collector always runs on the thread that invokes it, e.g. the main thread. In addition to processing documents concurrently, documents will also be destroyed asynchronously further improving performance. |
| <a href="#syside.gc.set_threshold" class="reference internal" title="syside.gc.set_threshold"><span class="pre"><code class="sourceCode python">set_threshold</code></span></a> |  | Set the garbage collector threshold, 0 disables collection. Negative values raise <span class="pre">`ValueError`</span>. |
| <a href="#syside.gc.track" class="reference internal" title="syside.gc.track"><span class="pre"><code class="sourceCode python">track</code></span></a> |  | Add document to garbage collector tracking list. Returns <span class="pre">`False`</span> if document was already tracked. |
| <a href="#syside.gc.untrack" class="reference internal" title="syside.gc.untrack"><span class="pre"><code class="sourceCode python">untrack</code></span></a> |  | Remove document from the garbage collector tracking list. Returns <span class="pre">`False`</span> if document was not tracked. |

</div>

</div>

</div>

------------------------------------------------------------------------

<div id="functions" class="section">

## <span class="nerd-font">󰊕</span> Functions<a href="#functions" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

<span class="sig-name descname"><span class="pre">collect</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span><a href="#syside.gc.collect" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Explicitly call garbage collector once.

<!-- -->

<span class="sig-name descname"><span class="pre">disable</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span><a href="#syside.gc.disable" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Disable automatic garbage collection.

<!-- -->

<span class="sig-name descname"><span class="pre">enable</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span><a href="#syside.gc.enable" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Enable automatic garbage collection.

<!-- -->

<span class="sig-name descname"><span class="pre">get_count</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">int</span></span></span><a href="#syside.gc.get_count" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Returns the number of currently tracked objects.

<!-- -->

<span class="sig-name descname"><span class="pre">get_debug</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="/python/v0.8.4/syside/gc/Debug.md" class="reference internal" title="syside.gc.Debug"><span class="pre">syside.gc.Debug</span></a></span></span><a href="#syside.gc.get_debug" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Return a copy of the current debug options of the garbage collector.

<!-- -->

<span class="sig-name descname"><span class="pre">get_executor</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="/python/v0.8.4/syside/Executor.md" class="reference internal" title="syside.Executor"><span class="pre">syside.Executor</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span></span></span><a href="#syside.gc.get_executor" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
The executor assigned to the garbage collector.

<!-- -->

<span class="sig-name descname"><span class="pre">get_threshold</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">int</span></span></span><a href="#syside.gc.get_threshold" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Return the current threshold.

<!-- -->

<span class="sig-name descname"><span class="pre">is_tracked</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/SharedMutex.md" class="reference internal" title="syside.SharedMutex"><span class="pre">syside.SharedMutex</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/BasicDocument.md" class="reference internal" title="syside.BasicDocument"><span class="pre">syside.BasicDocument</span></a><span class="p"><span class="pre">\]</span></span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">bool</span></span></span><a href="#syside.gc.is_tracked" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Returns <span class="pre">`True`</span> if <span class="pre">`document`</span> is tracked by the garbage collector.

<!-- -->

<span class="sig-name descname"><span class="pre">is_tracked</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/BasicDocument.md" class="reference internal" title="syside.BasicDocument"><span class="pre">syside.BasicDocument</span></a></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">bool</span></span></span>  

<!-- -->

<span class="sig-name descname"><span class="pre">isenabled</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">bool</span></span></span><a href="#syside.gc.isenabled" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Returns <span class="pre">`True`</span> if automatic collection is enabled.

<!-- -->

<span class="sig-name descname"><span class="pre">set_debug</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/gc/Debug.md" class="reference internal" title="syside.gc.Debug"><span class="pre">syside.gc.Debug</span></a></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span><a href="#syside.gc.set_debug" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Set default options for the garbage collector. By default, everything is printed to stderr.

<!-- -->

<span class="sig-name descname"><span class="pre">set_executor</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/Executor.md" class="reference internal" title="syside.Executor"><span class="pre">syside.Executor</span></a></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span><a href="#syside.gc.set_executor" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Assign an executor to the garbage collector. Without an executor, the garbage collector always runs on the thread that invokes it, e.g. the main thread. In addition to processing documents concurrently, documents will also be destroyed asynchronously further improving performance.

<!-- -->

<span class="sig-name descname"><span class="pre">set_threshold</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">int</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span><a href="#syside.gc.set_threshold" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Set the garbage collector threshold, 0 disables collection. Negative values raise <span class="pre">`ValueError`</span>.

Garbage collector will automatically run only when it tracks more than *threshold* new objects since last collection.

<!-- -->

<span class="sig-name descname"><span class="pre">track</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/SharedMutex.md" class="reference internal" title="syside.SharedMutex"><span class="pre">syside.SharedMutex</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/BasicDocument.md" class="reference internal" title="syside.BasicDocument"><span class="pre">syside.BasicDocument</span></a><span class="p"><span class="pre">\]</span></span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">bool</span></span></span><a href="#syside.gc.track" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Add document to garbage collector tracking list. Returns <span class="pre">`False`</span> if document was already tracked.

<!-- -->

<span class="sig-name descname"><span class="pre">untrack</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/SharedMutex.md" class="reference internal" title="syside.SharedMutex"><span class="pre">syside.SharedMutex</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/BasicDocument.md" class="reference internal" title="syside.BasicDocument"><span class="pre">syside.BasicDocument</span></a><span class="p"><span class="pre">\]</span></span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">bool</span></span></span><a href="#syside.gc.untrack" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Remove document from the garbage collector tracking list. Returns <span class="pre">`False`</span> if document was not tracked.

<!-- -->

<span class="sig-name descname"><span class="pre">untrack</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/BasicDocument.md" class="reference internal" title="syside.BasicDocument"><span class="pre">syside.BasicDocument</span></a></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">bool</span></span></span>  

<div class="toctree-wrapper compound">

</div>

</div>

</div>
