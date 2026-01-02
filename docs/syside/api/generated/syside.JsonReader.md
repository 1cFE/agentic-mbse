<div id="syside-jsonreader" class="section">

# syside.JsonReader[](#syside-jsonreader "Link to this heading")

  - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">JsonReader</span></span>[](#syside.JsonReader "Link to this definition")  
    Unbound reader for JSON deserialization
    
    Initialization
    
      - <span class="sig-name descname"><span class="pre">bind</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">s</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.JsonReader</span>](#syside.JsonReader "syside.JsonReader")</span></span>[](#syside.JsonReader.bind "Link to this definition")  
        Bind a serialized JSON string for reading.
        
        Note that only one reader can be bound at a time, binding again will raise `ValueError`. Suggested usage is through a context manager:
        
        <div class="highlight-python notranslate">
        
        <div class="highlight">
        
            with reader.bind(json_str) as json:
                model, report = deserializer.accept(json, syside.DESERIALIZE_STANDARD)
        
        </div>
        
        </div>
        
        The reader will attempt to infer the root node as:
        
        1.  The first `Namespace` (not subtype) without an owning relationship.
        
        2.  The first `Element` that has no serialized owning related element or owning relationship, starting from the first element in the JSON array, and following owning elements up.
        
        3.  The first element in the array otherwise.
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">is\_bound</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*[](#syside.JsonReader.is_bound "Link to this definition")  
        Whether there currently is a reader bound to this resource.
    
    <!-- end list -->
    
      - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">StrReader</span></span>[](#syside.JsonReader.StrReader "Link to this definition")  
        Bases: [`syside.Reader`](/v0.8.1/api/generated/syside.Reader.md "syside.Reader")
        
        Bound reader for JSON deserialization that can be used together with `Deserializer`.
        
        Resource usage can be controlled through context manager.
        
          - <span class="sig-name descname"><span class="pre">unbind</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span>[](#syside.JsonReader.StrReader.unbind "Link to this definition")  
            Unbind this reader explicitly, allowing resources to be reused for other reads.
            
            Attempting to use this for deserialization again will raise `RuntimeError`.
        
        <!-- end list -->
        
          - <span class="sig-name descname"><span class="pre">attribute\_hint</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.AttributeMap</span>](/v0.8.1/api/generated/syside.AttributeMap.md "syside.AttributeMap")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span></span></span>[](#syside.JsonReader.StrReader.attribute_hint "Link to this definition")  
            Get a hint for deserialization attributes.
        
        <!-- end list -->
        
          - <span class="sig-name descname"><span class="pre">\_\_enter\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.JsonReader</span>](#syside.JsonReader "syside.JsonReader")</span></span>[](#syside.JsonReader.StrReader.__enter__ "Link to this definition")
        
        <!-- end list -->
        
          - <span class="sig-name descname"><span class="pre">\_\_exit\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">exc\_type</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">type</span><span class="p"><span class="pre">\[</span></span><span class="pre">BaseException</span><span class="p"><span class="pre">\]</span></span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span></span>*, *<span class="n"><span class="pre">exc</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">BaseException</span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span></span>*, *<span class="n"><span class="pre">traceback</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">types.TracebackType</span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span>[](#syside.JsonReader.StrReader.__exit__ "Link to this definition")

</div>
