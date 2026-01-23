<div id="syside-environment" class="section">

# syside.Environment[](#syside-environment "Link to this heading")

  - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">Environment</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">documents</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">list</span><span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.SharedMutex</span>](/v0.8.1/api/generated/syside.SharedMutex.md "syside.SharedMutex")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Document</span>](/v0.8.1/api/generated/syside.Document.md "syside.Document")<span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">\]</span></span></span>*, *<span class="n"><span class="pre">index</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.StaticIndex</span>](/v0.8.1/api/generated/syside.StaticIndex.md "syside.StaticIndex")</span>*, *<span class="n"><span class="pre">lib</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.Stdlib</span>](/v0.8.1/api/generated/syside.Stdlib.md "syside.Stdlib")</span>*, *<span class="n"><span class="pre">result</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.ExecutionResult</span>](/v0.8.1/api/generated/syside.ExecutionResult.md "syside.ExecutionResult")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span></span>*<span class="sig-paren">)</span>[](#syside.Environment "Link to this definition")  
    Standard library environment for use with user models.
    
    Initialization
    
      - <span class="sig-name descname"><span class="pre">documents</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">list</span><span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.SharedMutex</span>](/v0.8.1/api/generated/syside.SharedMutex.md "syside.SharedMutex")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Document</span>](/v0.8.1/api/generated/syside.Document.md "syside.Document")<span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">\]</span></span><span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">None</span>*[](#syside.Environment.documents "Link to this definition")  
        Documents in this environment
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">lib</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.Stdlib</span>](/v0.8.1/api/generated/syside.Stdlib.md "syside.Stdlib")<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">None</span>*[](#syside.Environment.lib "Link to this definition")  
        Standard library cache
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">result</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.ExecutionResult</span>](/v0.8.1/api/generated/syside.ExecutionResult.md "syside.ExecutionResult")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span><span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">None</span>*[](#syside.Environment.result "Link to this definition")  
        Result of parsing documents in this environment
    
    <!-- end list -->
    
      - *<span class="pre">classmethod</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">get\_default</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.Environment</span>](#syside.Environment "syside.Environment")</span></span>[](#syside.Environment.get_default "Link to this definition")  
        Get a default constructed standard library environment. This will only be executed on the first call, and any subsequent calls will return a cached value. Standard library environment is cached based on the assumption that it **WILL NOT** change during runtime, saving resources when loading other models.
    
    <!-- end list -->
    
      - *<span class="pre">classmethod</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">from\_stdlib\_files</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">stdlib\_files</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">list</span><span class="p"><span class="pre">\[</span></span><span class="pre">pathlib.Path</span><span class="p"><span class="pre">\]</span></span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.Environment</span>](#syside.Environment "syside.Environment")</span></span>[](#syside.Environment.from_stdlib_files "Link to this definition")  
        Construct the environment from the given stdlib files.
        
          - Parameters<span class="colon">:</span>  
            **stdlib\_files** – The paths to SysMLv2 or KerML files representing the stdlib. These files must have correct file extensions (`.sysml` or `.kerml`).
    
    <!-- end list -->
    
      - *<span class="pre">classmethod</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">from\_documents</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">documents</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">Iterable</span><span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.SharedMutex</span>](/v0.8.1/api/generated/syside.SharedMutex.md "syside.SharedMutex")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Document</span>](/v0.8.1/api/generated/syside.Document.md "syside.Document")<span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">\]</span></span></span>*, *<span class="n"><span class="pre">index</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.StaticIndex</span>](/v0.8.1/api/generated/syside.StaticIndex.md "syside.StaticIndex")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">None</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.Environment</span>](#syside.Environment "syside.Environment")</span></span>[](#syside.Environment.from_documents "Link to this definition")  
        Construct the environment from the given documents.
        
          - Parameters<span class="colon">:</span>
            
              - **documents** – The documents from which to construct the SysMLv2 environment.
            
              - **index** – The index to be used in models. If `None`, creates a new index. If not `None`, clones the index to avoid mutating the argument.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">index</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.StaticIndex</span>](/v0.8.1/api/generated/syside.StaticIndex.md "syside.StaticIndex")</span></span>[](#syside.Environment.index "Link to this definition")  
        Returns a copy of the environment index for use in dependent models. A copy is required so that dependent models do not affect this environment and other dependent models.

</div>
