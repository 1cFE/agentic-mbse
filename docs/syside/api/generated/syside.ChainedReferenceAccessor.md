<div id="syside-chainedreferenceaccessor" class="section">

# syside.ChainedReferenceAccessor[](#syside-chainedreferenceaccessor "Link to this heading")

  - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">ChainedReferenceAccessor</span></span>[](#syside.ChainedReferenceAccessor "Link to this definition")  
    Bases: [`ReferenceAccessor`](/v0.8.1/api/generated/syside.ReferenceAccessor.md "syside.ReferenceAccessor")\[`M`\]
    
      - <span class="sig-name descname"><span class="pre">try\_set\_chain</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">Sequence</span><span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Feature</span>](/v0.8.1/api/metamodel/KerML/Feature.md "syside.Feature")<span class="p"><span class="pre">\]</span></span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.Feature</span>](/v0.8.1/api/metamodel/KerML/Feature.md "syside.Feature")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span></span></span>[](#syside.ChainedReferenceAccessor.try_set_chain "Link to this definition")  
        Try changing the referenced `element` to a chain of `Features`. Returns `None` if this reference cannot be modified, otherwise returns a new owned `Feature` that chains all `Features` in order.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">set\_chain</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">Sequence</span><span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Feature</span>](/v0.8.1/api/metamodel/KerML/Feature.md "syside.Feature")<span class="p"><span class="pre">\]</span></span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.Feature</span>](/v0.8.1/api/metamodel/KerML/Feature.md "syside.Feature")</span></span>[](#syside.ChainedReferenceAccessor.set_chain "Link to this definition")  
        `try_set_chain` but instead raises `ValueError` if this reference cannot be modified.

</div>
