<div id="syside-deserializedmodel" class="section">

# syside.DeserializedModel[](#syside-deserializedmodel "Link to this heading")

  - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">DeserializedModel</span></span>[](#syside.DeserializedModel "Link to this definition")  
    The model as it was deserialized, with references potentially unresolved.
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">document</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.Document</span>](/v0.8.1/api/generated/syside.Document.md "syside.Document")*[](#syside.DeserializedModel.document "Link to this definition")  
        The document model was deserialized into
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">root</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.Element</span>](/v0.8.1/api/metamodel/KerML/Element.md "syside.Element")*[](#syside.DeserializedModel.root "Link to this definition")  
        The root node of the deserialized model. Note that this may be an orphan node.
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">pending\_references</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.ContainerView</span>](/v0.8.1/api/generated/syside.ContainerView.md "syside.ContainerView")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.PendingReference</span>](/v0.8.1/api/generated/syside.PendingReference.md "syside.PendingReference")<span class="p"><span class="pre">\]</span></span>*[](#syside.DeserializedModel.pending_references "Link to this definition")  
        Currently unresolved pending references. These need to be resolved in a separate post-deserialization step to correctly resolve (potentially cyclical) dependencies between models.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">link</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">resolve</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">Callable</span><span class="p"><span class="pre">\[</span></span><span class="p"><span class="pre">\[</span></span><span class="pre">str</span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">uuid.UUID</span><span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">,</span></span><span class="w"> </span>[<span class="pre">syside.Element</span>](/v0.8.1/api/metamodel/KerML/Element.md "syside.Element")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span><span class="p"><span class="pre">\]</span></span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.SerdeReport</span>](/v0.8.1/api/generated/syside.SerdeReport.md "syside.SerdeReport")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.DocumentSegment</span>](/v0.8.1/api/generated/syside.DocumentSegment.md "syside.DocumentSegment")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span>[<span class="pre">syside.Element</span>](/v0.8.1/api/metamodel/KerML/Element.md "syside.Element")<span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">bool</span><span class="p"><span class="pre">\]</span></span></span></span>[](#syside.DeserializedModel.link "Link to this definition")  
        Attempt to resolve any pending references using custom `resolve`. Signature is
        
        <div class="highlight-python notranslate">
        
        <div class="highlight">
        
            def resolve(uri: str, element_id: uuid.UUID) -> Element | None: ...
        
        </div>
        
        </div>
        
        Returns a pair of `report` and `success`, whether all pending references have been resolved. Use `pending_references` again to get references that failed to resolve.

</div>
