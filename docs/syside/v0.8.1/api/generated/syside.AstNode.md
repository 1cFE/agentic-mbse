<div id="syside-astnode" class="section">

# syside.AstNode[](#syside-astnode "Link to this heading")

  - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">AstNode</span></span>[](#syside.AstNode "Link to this definition")
    
      - <span class="sig-name descname"><span class="pre">\_\_str\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">str</span></span></span>[](#syside.AstNode.__str__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_hash\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">int</span></span></span>[](#syside.AstNode.__hash__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">isinstance</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">type</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">syside.AstNode.isinstance.type</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.TNode</span><span class="p"><span class="pre">\]</span></span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">TypeGuard</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.TNode</span><span class="p"><span class="pre">\]</span></span></span></span>[](#syside.AstNode.isinstance "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">isinstance</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">type</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.AstNode.isinstance.type</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.TNode</span><span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="p"><span class="pre">...</span></span><span class="p"><span class="pre">\]</span></span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">TypeGuard</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.TNode</span><span class="p"><span class="pre">\]</span></span></span></span>
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">try\_cast</span></span><span class="sig-paren">(</span>*<span class="o"><span class="pre">\*</span></span><span class="n"><span class="pre">type</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">type</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.TNode</span><span class="p"><span class="pre">\]</span></span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">syside.TNode</span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span></span></span>[](#syside.AstNode.try_cast "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">try\_cast</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">type</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.AstNode.try\_cast.type</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.TNode</span><span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="p"><span class="pre">...</span></span><span class="p"><span class="pre">\]</span></span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">syside.TNode</span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span></span></span>
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">cast</span></span><span class="sig-paren">(</span>*<span class="o"><span class="pre">\*</span></span><span class="n"><span class="pre">type</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">type</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.TNode</span><span class="p"><span class="pre">\]</span></span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">syside.TNode</span></span></span>[](#syside.AstNode.cast "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">cast</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">type</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.AstNode.cast.type</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.TNode</span><span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="p"><span class="pre">...</span></span><span class="p"><span class="pre">\]</span></span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">syside.TNode</span></span></span>
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">parent</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.Element</span>](/v0.8.1/api/metamodel/KerML/Element.md "syside.Element")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span>*[](#syside.AstNode.parent "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">document</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.Document</span>](/v0.8.1/api/generated/syside.Document.md "syside.Document")*[](#syside.AstNode.document "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">cst\_node</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.CstNode</span>](/v0.8.1/api/generated/syside.CstNode.md "syside.CstNode")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span>*[](#syside.AstNode.cst_node "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned\_elements</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.LazyIterator</span>](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Element</span>](/v0.8.1/api/metamodel/KerML/Element.md "syside.Element")<span class="p"><span class="pre">\]</span></span>*[](#syside.AstNode.owned_elements "Link to this definition")  
        Returns a view into all elements directly owned by this `Element`.

</div>
