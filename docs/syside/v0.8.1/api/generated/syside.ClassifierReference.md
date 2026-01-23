<div id="syside-classifierreference" class="section">

# syside.ClassifierReference[](#syside-classifierreference "Link to this heading")

  - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">ClassifierReference</span></span>[](#syside.ClassifierReference "Link to this definition")  
    Bases: [`ReferenceAccessor`](/v0.8.1/api/generated/syside.ReferenceAccessor.md "syside.ReferenceAccessor")\[[`syside.Classifier`](/v0.8.1/api/metamodel/KerML/Classifier.md "syside.Classifier")\]
    
      - <span class="sig-name descname"><span class="pre">try\_set</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">element</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">syside.ClassifierReference.try\_set.M</span></span>*, *<span class="n"><span class="pre">name</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.NameID</span>](/v0.8.1/api/generated/syside.NameID.md "syside.NameID")</span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">...</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">syside.ClassifierReference.try\_set.M</span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span></span></span>[](#syside.ClassifierReference.try_set "Link to this definition")  
        Try changing the referenced `element`. Returns `None` if this reference cannot be modified, otherwise returns `element` argument.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">set</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">element</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">syside.ClassifierReference.set.M</span></span>*, *<span class="n"><span class="pre">name</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.NameID</span>](/v0.8.1/api/generated/syside.NameID.md "syside.NameID")</span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">...</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">syside.ClassifierReference.set.M</span></span></span>[](#syside.ClassifierReference.set "Link to this definition")  
        `try_set` but instead raises `ValueError` if this reference cannot be modified.

</div>
