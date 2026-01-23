<div id="syside-documentsegment" class="section">

# syside.DocumentSegment[](#syside-documentsegment "Link to this heading")

  - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">DocumentSegment</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">range</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.RangeUtf8</span>](/v0.8.1/api/generated/syside.RangeUtf8.md "syside.RangeUtf8")</span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">...</span></span>*, *<span class="n"><span class="pre">offset</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">int</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">0</span></span>*, *<span class="n"><span class="pre">end</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">int</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">0</span></span>*<span class="sig-paren">)</span>[](#syside.DocumentSegment "Link to this definition")  
    Initialization
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">range</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.RangeUtf8</span>](/v0.8.1/api/generated/syside.RangeUtf8.md "syside.RangeUtf8")*[](#syside.DocumentSegment.range "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">offset</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">int</span>*[](#syside.DocumentSegment.offset "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">end</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">int</span>*[](#syside.DocumentSegment.end "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">static</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">from\_cst</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.CstNode</span>](/v0.8.1/api/generated/syside.CstNode.md "syside.CstNode")</span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.DocumentSegment</span>](#syside.DocumentSegment "syside.DocumentSegment")</span></span>[](#syside.DocumentSegment.from_cst "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">static</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">from\_cst\_start</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.CstNode</span>](/v0.8.1/api/generated/syside.CstNode.md "syside.CstNode")</span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.DocumentSegment</span>](#syside.DocumentSegment "syside.DocumentSegment")</span></span>[](#syside.DocumentSegment.from_cst_start "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">static</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">from\_cst\_end</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.CstNode</span>](/v0.8.1/api/generated/syside.CstNode.md "syside.CstNode")</span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.DocumentSegment</span>](#syside.DocumentSegment "syside.DocumentSegment")</span></span>[](#syside.DocumentSegment.from_cst_end "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">static</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">from\_node</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.AstNode</span>](/v0.8.1/api/generated/syside.AstNode.md "syside.AstNode")</span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.DocumentSegment</span>](#syside.DocumentSegment "syside.DocumentSegment")</span></span>[](#syside.DocumentSegment.from_node "Link to this definition")  
        Construct `DocumentSegment` from the nearest CST node that contains `node`.
    
    <!-- end list -->
    
      - *<span class="pre">static</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">from\_node\_field</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">node</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.AstNode</span>](/v0.8.1/api/generated/syside.AstNode.md "syside.AstNode")</span>*, *<span class="n"><span class="pre">field</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="n"><span class="pre">index</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">int</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">0</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.DocumentSegment</span>](#syside.DocumentSegment "syside.DocumentSegment")</span></span>[](#syside.DocumentSegment.from_node_field "Link to this definition")  
        Construct `DocumentSegment` from a `tree-sitter` field named `field` at `index`. If `node` does not contain a CST node with a matching `field`, the nearest CST segment is returned instead.
    
    <!-- end list -->
    
      - *<span class="pre">static</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">from\_node\_symbol</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">node</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.AstNode</span>](/v0.8.1/api/generated/syside.AstNode.md "syside.AstNode")</span>*, *<span class="n"><span class="pre">symbol</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="n"><span class="pre">index</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">int</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">0</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.DocumentSegment</span>](#syside.DocumentSegment "syside.DocumentSegment")</span></span>[](#syside.DocumentSegment.from_node_symbol "Link to this definition")  
        Construct `DocumentSegment` from a `tree-sitter` symbol named `symbol` at `index`. If `node` does not contain a CST node with a matching `symbol`, the nearest CST segment is returned instead.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_eq\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">object</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">bool</span></span></span>[](#syside.DocumentSegment.__eq__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_ne\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">object</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">bool</span></span></span>[](#syside.DocumentSegment.__ne__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_cpp\_name\_\_</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">'syside::DocumentSegment'</span>*[](#syside.DocumentSegment.__cpp_name__ "Link to this definition")

</div>
