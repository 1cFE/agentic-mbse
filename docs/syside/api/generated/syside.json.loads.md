<div id="syside-json-loads" class="section">

# syside.json.loads[](#syside-json-loads "Link to this heading")

  - <span class="sig-name descname"><span class="pre">loads</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">s</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="n"><span class="pre">document</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.Document</span>](/v0.8.1/api/generated/syside.Document.md "syside.Document")</span>*, *<span class="n"><span class="pre">attributes</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.AttributeMap</span>](/v0.8.1/api/generated/syside.AttributeMap.md "syside.AttributeMap")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">None</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.DeserializedModel</span>](/v0.8.1/api/generated/syside.DeserializedModel.md "syside.DeserializedModel")</span></span>[<span class="viewcode-link"><span class="pre">\[source\]</span></span>](/v0.8.1/_modules/syside/json.md)[](#syside.json.loads "Link to this definition")  
    Deserialize a model from `s` into an already existing `document`.
    
    Root node will be inferred as:
    
    1.  The first `Namespace` (not subtype) without an owning relationship.
    
    2.  The first `Element` that has no serialized owning related element or owning relationship, starting from the first element in the JSON array, and following owning elements up.
    
    3.  The first element in the array otherwise.
    
    <!-- end list -->
    
      - Parameters<span class="colon">:</span>
        
          - **s** – The string contained serialized SysML model in JSON array.
        
          - **document** – The document the model will be deserialized into.
        
          - **attributes** – Attribute mapping of `s`. If none provided, this will attempt to infer a corresponding mapping or raise a `ValueError`.
    
      - Returns<span class="colon">:</span>  
        Model deserialized from JSON array. Note that references into other documents will not be resolved, users will need to resolve them by calling `link` on the returned model. See also [`IdMap`](/v0.8.1/api/generated/syside.IdMap.md "syside.IdMap").

<!-- end list -->

  - <span class="sig-name descname"><span class="pre">loads</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">s</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="n"><span class="pre">document</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.Url</span>](/v0.8.1/api/generated/syside.Url.md "syside.Url")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">str</span></span>*, *<span class="n"><span class="pre">attributes</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.AttributeMap</span>](/v0.8.1/api/generated/syside.AttributeMap.md "syside.AttributeMap")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">None</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.DeserializedModel</span>](/v0.8.1/api/generated/syside.DeserializedModel.md "syside.DeserializedModel")<span class="p"><span class="pre">,</span></span><span class="w"> </span>[<span class="pre">syside.SharedMutex</span>](/v0.8.1/api/generated/syside.SharedMutex.md "syside.SharedMutex")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Document</span>](/v0.8.1/api/generated/syside.Document.md "syside.Document")<span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">\]</span></span></span></span>[<span class="viewcode-link"><span class="pre">\[source\]</span></span>](/v0.8.1/_modules/syside/json.md)  
    Create a new `document` and deserialize a model from `s` into it.
    
    Root node will be inferred as:
    
    1.  The first `Namespace` (not subtype) without an owning relationship.
    
    2.  The first `Element` that has no serialized owning related element or owning relationship, starting from the first element in the JSON array, and following owning elements up.
    
    3.  The first element in the array otherwise.
    
    <!-- end list -->
    
      - Parameters<span class="colon">:</span>
        
          - **s** – The string contained serialized SysML model in JSON array.
        
          - **document** – A URI in the form of [`Url`](/v0.8.1/api/generated/syside.Url.md "syside.Url") or a string, new document will be created with. If URI path has no extension, or the extension does not match `sysml` or `kerml`, `ValueError` is raised.
        
          - **attributes** – Attribute mapping of `s`. If none provided, this will attempt to infer a corresponding mapping or raise a `ValueError`.
    
      - Returns<span class="colon">:</span>  
        Model deserialized from JSON array and the newly created document. Note that references into other documents will not be resolved, users will need to resolve them by calling `link` on the returned model. See also [`IdMap`](/v0.8.1/api/generated/syside.IdMap.md "syside.IdMap").

</div>
