<div id="syside-gc-set-threshold" class="section">

# syside.gc.set\_threshold[](#syside-gc-set-threshold "Link to this heading")

  - <span class="sig-name descname"><span class="pre">set\_threshold</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">int</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span>[](#syside.gc.set_threshold "Link to this definition")  
    Set the garbage collector threshold, 0 disables collection. Negative values raise `ValueError`.
    
    Garbage collector will automatically run only when it tracks more than *threshold* new objects since last collection.

</div>
