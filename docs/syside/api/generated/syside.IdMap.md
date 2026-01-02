<div id="syside-idmap" class="section">

# syside.IdMap[](#syside-idmap "Link to this heading")

  - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">IdMap</span></span>[](#syside.IdMap "Link to this definition")  
    `DeserializedModel` compatible mapping for elements. This will typically be used for linking pending references:
    
    <div class="highlight-python notranslate">
    
    <div class="highlight">
    
        map = IdMap()
        models_reports = [
            deserializer.accept(document, my_reader(input), DESERIALIZE_STANDARD)
            for document, input in zip(documents, inputs)
        ]
        for document in documents:
            map.insert_or_assign(document)
        reports_linked = [model.link(map) for model, _ in models_reports]
    
    </div>
    
    </div>
    
    Initialization
    
      - <span class="sig-name descname"><span class="pre">insert\_or\_assign</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">document</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.Document</span>](/v0.8.1/api/generated/syside.Document.md "syside.Document")</span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><span class="pre">int</span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">bool</span><span class="p"><span class="pre">\]</span></span></span></span>[](#syside.IdMap.insert_or_assign "Link to this definition")  
        Insert all elements from `document` into this map.
        
        Returns the number of elements inserted, and `True` if insertion took place, `False` if `document` was already mapped.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">try\_insert</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">document</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.Document</span>](/v0.8.1/api/generated/syside.Document.md "syside.Document")</span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><span class="pre">int</span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">bool</span><span class="p"><span class="pre">\]</span></span></span></span>[](#syside.IdMap.try_insert "Link to this definition")  
        Try insert all elements from `document` into this map.
        
        Returns the number of elements inserted, and `True` if insertion took place. This will not override already mapped document elements.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">erase</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">document</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.Document</span>](/v0.8.1/api/generated/syside.Document.md "syside.Document")</span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">int</span></span></span>[](#syside.IdMap.erase "Link to this definition")  
        Erase all elements assigned to `document` from this map.
        
        Returns the number of elements erased.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">erase</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">uri</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">int</span></span></span>  
        Erase all elements assigned to document with `uri` from this map.
        
        Returns the number of elements erased.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">clear</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span>[](#syside.IdMap.clear "Link to this definition")  
        Clear all mapped elements.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">reserve</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">n</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">int</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span>[](#syside.IdMap.reserve "Link to this definition")  
        Reserve space for `n` document mappings.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">find</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">uri</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="n"><span class="pre">id</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">uuid.UUID</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.Element</span>](/v0.8.1/api/metamodel/KerML/Element.md "syside.Element")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span></span></span>[](#syside.IdMap.find "Link to this definition")  
        Find an element at document with `uri` that has `id`.
        
        Returns the element found if any.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">search</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">id</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">uuid.UUID</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.Element</span>](/v0.8.1/api/metamodel/KerML/Element.md "syside.Element")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span></span></span>[](#syside.IdMap.search "Link to this definition")  
        Search across all registered documents for a matching id. This has complexity O(n) since it searches each document separately.
        
        Returns the element found if any.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_call\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">uri</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="n"><span class="pre">id</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">uuid.UUID</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.Element</span>](/v0.8.1/api/metamodel/KerML/Element.md "syside.Element")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span></span></span>[](#syside.IdMap.__call__ "Link to this definition")  
        Short-hand for `find` or `search`. Will fall back to `search` if `uri` is empty.

</div>
