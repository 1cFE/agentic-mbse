<div id="syside-relationshipbody" class="section">

# syside.RelationshipBody[](#syside-relationshipbody "Link to this heading")

  - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">RelationshipBody</span></span>[](#syside.RelationshipBody "Link to this definition")  
    Bases: [`syside.ContainerView`](/v0.8.1/api/generated/syside.ContainerView.md "syside.ContainerView")\[[`syside.Element`](/v0.8.1/api/metamodel/KerML/Element.md "syside.Element")\]
    
    Container for relationship bodies. Works similarly to `ChildrenNodes` except relationships are not needed and all elements are taken ownership off.
    
    TODO: add insert and replace methods.
    
      - <span class="sig-name descname"><span class="pre">append</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">element</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">type</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.TElement</span><span class="p"><span class="pre">\]</span></span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">syside.TElement</span></span></span>[](#syside.RelationshipBody.append "Link to this definition")  
        Append an owned related element. Returns newly constructed related element.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">append</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">element</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">syside.TElement</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">syside.TElement</span></span></span>  
        Append an owned existing related element. Returns the same related element.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">append\_annotation</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">element</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">type</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.RelationshipBody.append\_annotation.M</span><span class="p"><span class="pre">\]</span></span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Annotation</span>](/v0.8.1/api/metamodel/KerML/Annotation.md "syside.Annotation")<span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">syside.RelationshipBody.append\_annotation.M</span><span class="p"><span class="pre">\]</span></span></span></span>[](#syside.RelationshipBody.append_annotation "Link to this definition")  
        Append an owned annotation to an annotating element. Returns a pair of newly constructed (annotation, annotating element).
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">append\_annotation</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">element</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">syside.RelationshipBody.append\_annotation.M</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Annotation</span>](/v0.8.1/api/metamodel/KerML/Annotation.md "syside.Annotation")<span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">syside.RelationshipBody.append\_annotation.M</span><span class="p"><span class="pre">\]</span></span></span></span>  
        Append an owned annotation to an existing annotating element. Returns a pair of (annotation, annotating element) where only the annotation is newly constructed.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">pop</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">index</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">int</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">-1</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.Element</span>](/v0.8.1/api/metamodel/KerML/Element.md "syside.Element")</span></span>[](#syside.RelationshipBody.pop "Link to this definition")  
        Removes a related element at the specified index from the model tree and returns it.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">remove\_element</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.Element</span>](/v0.8.1/api/metamodel/KerML/Element.md "syside.Element")</span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">bool</span></span></span>[](#syside.RelationshipBody.remove_element "Link to this definition")  
        Removes a related element from the model tree. Returns `True` if the element was removed, otherwise `False`.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">clear</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span>[](#syside.RelationshipBody.clear "Link to this definition")  
        Removes and releases all elements in this container. Afterwards, `len` is 0.

</div>
