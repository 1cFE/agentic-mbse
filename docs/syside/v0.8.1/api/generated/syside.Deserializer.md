<div id="syside-deserializer" class="section">

# syside.Deserializer[](#syside-deserializer "Link to this heading")

  - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">Deserializer</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">document</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.Document</span>](/v0.8.1/api/generated/syside.Document.md "syside.Document")</span>*<span class="sig-paren">)</span>[](#syside.Deserializer "Link to this definition")  
    Deserializer for SysML models. The actual deserialization input depends on used `Reader`.
    
    Note that unlike `Serializer` deserialization cannot be completed in a single pass in general because documents may form reference cycles with each other. The typical deserialization pattern will be
    
    <div class="highlight-python notranslate">
    
    <div class="highlight">
    
        des = Deserializer(document)
        model, report = des.accept(reader, DESERIALIZE_STANDARD)
        # ... collect all valid element ids for linking
        link_report, all_linked = model.link(my_reference_resolve)
    
    </div>
    
    </div>
    
    Initialization
    
    Construct a new deserializer that will deserialize models into the provided `document`.
    
      - <span class="sig-name descname"><span class="pre">accept</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">reader</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.Reader</span>](/v0.8.1/api/generated/syside.Reader.md "syside.Reader")</span>*, *<span class="n"><span class="pre">attributes</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.AttributeMap</span>](/v0.8.1/api/generated/syside.AttributeMap.md "syside.AttributeMap")</span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.DeserializedModel</span>](/v0.8.1/api/generated/syside.DeserializedModel.md "syside.DeserializedModel")<span class="p"><span class="pre">,</span></span><span class="w"> </span>[<span class="pre">syside.SerdeReport</span>](/v0.8.1/api/generated/syside.SerdeReport.md "syside.SerdeReport")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.DocumentSegment</span>](/v0.8.1/api/generated/syside.DocumentSegment.md "syside.DocumentSegment")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span>[<span class="pre">syside.Element</span>](/v0.8.1/api/metamodel/KerML/Element.md "syside.Element")<span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">\]</span></span></span></span>[](#syside.Deserializer.accept "Link to this definition")  
        Accept a `reader` for deserialization into currently bound `document`. Returns the deserialized model, or raises a `RuntimeError`. `document` without a [`Url`](/v0.8.1/api/generated/syside.Url.md "syside.Url") with scheme will emit a warning that relative URIs will not be resolvable.
        
        Note that cross-references may not be resolved, and instead replaced by placeholder element references due to potential reference cycles between documents. Call `link` on the returned model when dependent documents have been loaded.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">accept</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">document</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.Document</span>](/v0.8.1/api/generated/syside.Document.md "syside.Document")</span>*, *<span class="n"><span class="pre">reader</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.Reader</span>](/v0.8.1/api/generated/syside.Reader.md "syside.Reader")</span>*, *<span class="n"><span class="pre">attributes</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.AttributeMap</span>](/v0.8.1/api/generated/syside.AttributeMap.md "syside.AttributeMap")</span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.DeserializedModel</span>](/v0.8.1/api/generated/syside.DeserializedModel.md "syside.DeserializedModel")<span class="p"><span class="pre">,</span></span><span class="w"> </span>[<span class="pre">syside.SerdeReport</span>](/v0.8.1/api/generated/syside.SerdeReport.md "syside.SerdeReport")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.DocumentSegment</span>](/v0.8.1/api/generated/syside.DocumentSegment.md "syside.DocumentSegment")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span>[<span class="pre">syside.Element</span>](/v0.8.1/api/metamodel/KerML/Element.md "syside.Element")<span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">\]</span></span></span></span>  
        Accept `reader` for deserialization into `document`. Equivalent to
        
        <div class="highlight-python notranslate">
        
        <div class="highlight">
        
            deserializer.reset(document)
            return deserializer.accept(reader, attributes)
        
        </div>
        
        </div>
        
        Returns the deserialized model, or raises `RuntimeError`.
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">document</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.Document</span>](/v0.8.1/api/generated/syside.Document.md "syside.Document")*[](#syside.Deserializer.document "Link to this definition")  
        The document bound to this deserializer
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">reset</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">document</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.Document</span>](/v0.8.1/api/generated/syside.Document.md "syside.Document")</span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span>[](#syside.Deserializer.reset "Link to this definition")  
        Reset the deserializer. Rebinds to the `document` and resets this `Deserializer` for new deserialization.

</div>
