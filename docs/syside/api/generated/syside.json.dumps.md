<div id="syside-json-dumps" class="section">

# syside.json.dumps[](#syside-json-dumps "Link to this heading")

  - <span class="sig-name descname"><span class="pre">dumps</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">element</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.Element</span>](/v0.8.1/api/metamodel/KerML/Element.md "syside.Element")</span>*, *<span class="n"><span class="pre">options</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.SerializationOptions</span>](/v0.8.1/api/generated/syside.SerializationOptions.md "syside.SerializationOptions")</span>*, *<span class="n"><span class="pre">indent</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">int</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">2</span></span>*, *<span class="n"><span class="pre">use\_spaces</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">True</span></span>*, *<span class="n"><span class="pre">final\_new\_line</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">True</span></span>*, *<span class="n"><span class="pre">include\_cross\_ref\_uris</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">True</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">str</span></span></span>[<span class="viewcode-link"><span class="pre">\[source\]</span></span>](/v0.8.1/_modules/syside/json.md)[](#syside.json.dumps "Link to this definition")  
    Serialize `element` to a SysML v2 JSON `str`.
    
    See the documentation of the [`SerializationOptions`](/v0.8.1/api/generated/syside.SerializationOptions.md "syside.SerializationOptions") class for documentation of the possible options. The options object constructed with [`SerializationOptions.minimal`](/v0.8.1/api/generated/syside.SerializationOptions.md "syside.SerializationOptions.minimal") instructs to produce a minimal JSON without any redundant elements that results in significantly smaller JSONs. Examples of redundant information that is avoided using minimal configuration are:
    
      - including fields for null values;
    
      - including fields whose values match the default values;
    
      - including redefined fields that are duplicates of redefining fields;
    
      - including derived fields that can be computed from minimal JSON (for example, the result value of evaluating an expression);
    
      - including implied relationships.
    
    <div class="admonition note">
    
    Note
    
    SysIDE does not construct all derived properties yet. Therefore, setting `options.include_derived` to `True` may result in a JSON that does not satisfy the schema.
    
    </div>
    
      - Parameters<span class="colon">:</span>
        
          - **element** – The SysML v2 element to be serialized to SysML v2 JSON.
        
          - **options** – The serialization options to use when serializing SysML v2 to JSON.
        
          - **indent** – How many space or tab characters to use for indenting the JSON.
        
          - **use\_spaces** – Whether use spaces or tabs for indentation.
        
          - **final\_new\_line** – Whether to add a newline character at the end of the generated string.
        
          - **include\_cross\_ref\_uris** – Whether to add potentially relative URIs as `@uri` property to references of Elements from documents other than the one owning `element`. Note that while such references are non-standard, they match the behaviour of XMI exports in Pilot implementation which use relative URIs for references instead of plain element IDs.
    
      - Returns<span class="colon">:</span>  
        `element` serialized as JSON.

</div>
