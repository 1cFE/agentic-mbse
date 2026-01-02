<div id="syside-model" class="section">

# syside.Model[](#syside-model "Link to this heading")

  - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">Model</span></span>[](#syside.Model "Link to this definition")  
    A SysMLv2 model represented using abstract syntax.
    
      - <span class="sig-name descname"><span class="pre">result</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.ExecutionResult</span>](/v0.8.1/api/generated/syside.ExecutionResult.md "syside.ExecutionResult")<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">None</span>*[](#syside.Model.result "Link to this definition")  
        The model build result as returned by core module.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">environment</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.Environment</span>](/v0.8.1/api/generated/syside.Environment.md "syside.Environment")<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">None</span>*[](#syside.Model.environment "Link to this definition")  
        The environment this model was built in
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">documents</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">list</span><span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.SharedMutex</span>](/v0.8.1/api/generated/syside.SharedMutex.md "syside.SharedMutex")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Document</span>](/v0.8.1/api/generated/syside.Document.md "syside.Document")<span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">\]</span></span><span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">None</span>*[](#syside.Model.documents "Link to this definition")  
        Documents as part of this model.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">lib</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.Stdlib</span>](/v0.8.1/api/generated/syside.Stdlib.md "syside.Stdlib")<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">None</span>*[](#syside.Model.lib "Link to this definition")  
        Standard library cache
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">index</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.StaticIndex</span>](/v0.8.1/api/generated/syside.StaticIndex.md "syside.StaticIndex")<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">None</span>*[](#syside.Model.index "Link to this definition")  
        Index of exported symbols
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">all\_docs</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">list</span><span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.SharedMutex</span>](/v0.8.1/api/generated/syside.SharedMutex.md "syside.SharedMutex")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Document</span>](/v0.8.1/api/generated/syside.Document.md "syside.Document")<span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">\]</span></span>*[](#syside.Model.all_docs "Link to this definition")  
        All built documents, including standard library.
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">stdlib\_docs</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">list</span><span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.SharedMutex</span>](/v0.8.1/api/generated/syside.SharedMutex.md "syside.SharedMutex")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Document</span>](/v0.8.1/api/generated/syside.Document.md "syside.Document")<span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">\]</span></span>*[](#syside.Model.stdlib_docs "Link to this definition")  
        Environment documents as part of this model. Prefer accessing documents through ‘environment’ instead
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">user\_docs</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">list</span><span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.SharedMutex</span>](/v0.8.1/api/generated/syside.SharedMutex.md "syside.SharedMutex")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Document</span>](/v0.8.1/api/generated/syside.Document.md "syside.Document")<span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">\]</span></span>*[](#syside.Model.user_docs "Link to this definition")  
        User documents built as part of this model. Prefer ‘documents’ instead.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">uris</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">considered\_document\_kinds</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.DocumentKind</span>](/v0.8.1/api/generated/syside.DocumentKind.md "syside.DocumentKind")</span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">DocumentKind.MODEL</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">Iterable</span><span class="p"><span class="pre">\[</span></span><span class="pre">str</span><span class="p"><span class="pre">\]</span></span></span></span>[](#syside.Model.uris "Link to this definition")  
        Return URIs of documents.
        
          - Parameters<span class="colon">:</span>  
            **considered\_document\_kinds** – What document kinds to consider. By default returns only documents created for this model.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">nodes</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">node\_kind</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">type</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.TElement</span><span class="p"><span class="pre">\]</span></span></span>*, *<span class="n"><span class="pre">include\_subtypes</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">False</span></span>*, *<span class="n"><span class="pre">considered\_document\_kinds</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.DocumentKind</span>](/v0.8.1/api/generated/syside.DocumentKind.md "syside.DocumentKind")</span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">DocumentKind.MODEL</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">Iterable</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.TElement</span><span class="p"><span class="pre">\]</span></span></span></span>[](#syside.Model.nodes "Link to this definition")  
        Iterate over all nodes of the given kind.
        
          - Parameters<span class="colon">:</span>
            
              - **node\_kind** – What kind of nodes to return.
            
              - **include\_subtypes** – Whether to consider subtypes.
            
              - **considered\_document\_kinds** – What document kinds to consider. By default returns only documents created for this model.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">elements</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">node\_kind</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">type</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.TElement</span><span class="p"><span class="pre">\]</span></span></span>*, *<span class="n"><span class="pre">include\_subtypes</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">False</span></span>*, *<span class="n"><span class="pre">considered\_document\_kinds</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.DocumentKind</span>](/v0.8.1/api/generated/syside.DocumentKind.md "syside.DocumentKind")</span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">DocumentKind.MODEL</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">Iterable</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.TElement</span><span class="p"><span class="pre">\]</span></span></span></span>[](#syside.Model.elements "Link to this definition")  
        An alias for nodes.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">to\_environment</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.Environment</span>](/v0.8.1/api/generated/syside.Environment.md "syside.Environment")</span></span>[](#syside.Model.to_environment "Link to this definition")  
        Convert this model to `Environment` for building other dependent models.

</div>
