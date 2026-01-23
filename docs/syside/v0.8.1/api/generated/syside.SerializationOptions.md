<div id="syside-serializationoptions" class="section">

# syside.SerializationOptions[](#syside-serializationoptions "Link to this heading")

  - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">SerializationOptions</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">use\_standard\_names</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">True</span></span>*, *<span class="n"><span class="pre">include\_derived</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">False</span></span>*, *<span class="n"><span class="pre">include\_redefined</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">False</span></span>*, *<span class="n"><span class="pre">include\_default</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">False</span></span>*, *<span class="n"><span class="pre">include\_optional</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">False</span></span>*, *<span class="n"><span class="pre">include\_implied</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">False</span></span>*, *<span class="n"><span class="pre">fail\_action</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.FailAction</span>](/v0.8.1/api/generated/syside.FailAction.md "syside.FailAction")</span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">FailAction.Diagnose</span></span>*<span class="sig-paren">)</span>[](#syside.SerializationOptions "Link to this definition")  
    Options for SysML model serialization. Attribute options are ordered in descending precedence.
    
    Initialization
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">use\_standard\_names</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*[](#syside.SerializationOptions.use_standard_names "Link to this definition")  
        If true, fields will be serialized using standard names
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">include\_derived</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*[](#syside.SerializationOptions.include_derived "Link to this definition")  
        If true, serialize derived attributes. Corresponds to `includesDerived` flag in the specification (KerML 10.3, Table 13):
        
        > 
        > 
        > <div>
        > 
        > Whether derived property values are included in the model interchange files.
        > 
        > </div>
        
        **Note:** SysIDE does not construct all derived properties yet. Therefore, setting `options.include_derived` to `True` may result in a JSON that does not satisfy the schema.
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">include\_redefined</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*[](#syside.SerializationOptions.include_redefined "Link to this definition")  
        If true, serialize attributes even if they are redefined in the metamodel.
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">include\_default</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*[](#syside.SerializationOptions.include_default "Link to this definition")  
        If true, serialize attributes even if they match their default values.
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">include\_optional</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*[](#syside.SerializationOptions.include_optional "Link to this definition")  
        If true, non-required attributes will be serialized even if they are null or empty.
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">include\_implied</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*[](#syside.SerializationOptions.include_implied "Link to this definition")  
        If true, serialize implicit elements. Only for attributes that are serialized. Corresponds to `includesImplied` flag in the specification (KerML 10.3, Table 13):
        
        > 
        > 
        > <div>
        > 
        > Whether implied relationships are included in the model interchange files.
        > 
        > </div>
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">fail\_action</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FailAction</span>](/v0.8.1/api/generated/syside.FailAction.md "syside.FailAction")*[](#syside.SerializationOptions.fail_action "Link to this definition")  
        Action to take on serialization errors.
    
    <!-- end list -->
    
      - *<span class="pre">static</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">minimal</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.SerializationOptions</span>](#syside.SerializationOptions "syside.SerializationOptions")</span></span>[](#syside.SerializationOptions.minimal "Link to this definition")  
        Configuration that instructs the writer to produce a minimal JSON without any redundant elements. Examples of redundant information that is avoided using the minimal configuration are:
        
          - including fields for null values;
        
          - including fields whose values match the default values;
        
          - including redefined fields that are duplicates of redefining fields;
        
          - including derived fields that can be computed from minimal JSON (for example, the result value of evaluating an expression);
        
          - including implied relationships.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">with\_options</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">use\_standard\_names</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">None</span></span>*, *<span class="n"><span class="pre">include\_derived</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">None</span></span>*, *<span class="n"><span class="pre">include\_redefined</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">None</span></span>*, *<span class="n"><span class="pre">include\_default</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">None</span></span>*, *<span class="n"><span class="pre">include\_optional</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">None</span></span>*, *<span class="n"><span class="pre">include\_implied</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">None</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.SerializationOptions</span>](#syside.SerializationOptions "syside.SerializationOptions")</span></span>[](#syside.SerializationOptions.with_options "Link to this definition")  
        Creates a copy with the specified options changed to the given ones.

</div>
