<div id="syside-argumentsaccessor" class="section">

# syside.ArgumentsAccessor[](#syside-argumentsaccessor "Link to this heading")

  - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">ArgumentsAccessor</span></span>[](#syside.ArgumentsAccessor "Link to this definition")  
    Bases: [`LazyIterator`](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")\[[`Expression`](/v0.8.1/api/metamodel/KerML/Expression.md "syside.Expression")\]
    
      - <span class="sig-name descname"><span class="pre">append</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">syside.ArgumentsAccessor.append.M</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.FeatureValue</span>](/v0.8.1/api/metamodel/KerML/FeatureValue.md "syside.FeatureValue")<span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">syside.ArgumentsAccessor.append.M</span><span class="p"><span class="pre">\]</span></span></span></span>[](#syside.ArgumentsAccessor.append "Link to this definition")  
        Append a new invocation `argument`. This takes care of constructing any intermediate elements.
        
        Returns a pair of (`feature_value`, `argument`).
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">append</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">type</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.ArgumentsAccessor.append.M</span><span class="p"><span class="pre">\]</span></span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.FeatureValue</span>](/v0.8.1/api/metamodel/KerML/FeatureValue.md "syside.FeatureValue")<span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">syside.ArgumentsAccessor.append.M</span><span class="p"><span class="pre">\]</span></span></span></span>  
        Append a new invocation `argument` with the corresponding type. This takes care of constructing any intermediate elements.
        
        Returns a pair of (`feature_value`, `argument`).

</div>
