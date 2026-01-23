<div id="syside-referenceaccessor" class="section">

# syside.ReferenceAccessor[](#syside-referenceaccessor "Link to this heading")

  - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">ReferenceAccessor</span></span>[](#syside.ReferenceAccessor "Link to this definition")  
    Bases: `typing.Generic`\[`syside.M`\]
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">element</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.Element</span>](/v0.8.1/api/metamodel/KerML/Element.md "syside.Element")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span>*[](#syside.ReferenceAccessor.element "Link to this definition")  
        Returns the referenced `Element`. This may return `None`, e.g. when reference resolution failed, although in most such cases a placeholder element will be returned instead.
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">modifiable</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*[](#syside.ReferenceAccessor.modifiable "Link to this definition")  
        Returns `True` if this reference can be modified, that is the owning `Relationship` is an owned member of a `Namespace`. Calling `set` methods when `modifiable == False` will raise `ValueError`.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">try\_set</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">element</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">syside.M</span></span>*, *<span class="n"><span class="pre">name</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.NameID</span>](/v0.8.1/api/generated/syside.NameID.md "syside.NameID")</span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">...</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">syside.M</span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span></span></span>[](#syside.ReferenceAccessor.try_set "Link to this definition")  
        Try changing the referenced `element`. Returns `None` if this reference cannot be modified, otherwise returns `element` argument.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">set</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">element</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">syside.M</span></span>*, *<span class="n"><span class="pre">name</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.NameID</span>](/v0.8.1/api/generated/syside.NameID.md "syside.NameID")</span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">...</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">syside.M</span></span></span>[](#syside.ReferenceAccessor.set "Link to this definition")  
        `try_set` but instead raises `ValueError` if this reference cannot be modified.
    
    <!-- end list -->
    
      - *<span class="pre">classmethod</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">\_\_class\_getitem\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">item</span></span>*<span class="sig-paren">)</span>[](#syside.ReferenceAccessor.__class_getitem__ "Link to this definition")

</div>
