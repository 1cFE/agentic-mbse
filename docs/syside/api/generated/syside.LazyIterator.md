<div id="syside-lazyiterator" class="section">

# syside.LazyIterator[](#syside-lazyiterator "Link to this heading")

  - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">LazyIterator</span></span>[](#syside.LazyIterator "Link to this definition")  
    Bases: `typing.Generic`\[`T`\]
    
      - <span class="sig-name descname"><span class="pre">at</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg0</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">int</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">syside.T</span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span></span></span>[](#syside.LazyIterator.at "Link to this definition")  
        Get value at index. This is computed lazily. Returns `None` for out of bounds index.
        
        Notes:
        
          - Has complexity O(n) so should be used sparingly.
        
          - Only positive indices are allowed since size is unknown.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_getitem\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg0</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">int</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">syside.T</span></span></span>[](#syside.LazyIterator.__getitem__ "Link to this definition")  
        Get value at index, This is computed lazily. Throws `IndexError` on out of bounds.
        
        Notes:
        
          - Has complexity O(n) so should be used sparingly.
        
          - Only positive indices are allowed since size is unknown.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">empty</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">bool</span></span></span>[](#syside.LazyIterator.empty "Link to this definition")  
        Check if this range is empty.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_bool\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">bool</span></span></span>[](#syside.LazyIterator.__bool__ "Link to this definition")  
        Returns `True` if this range is not empty.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">count</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">int</span></span></span>[](#syside.LazyIterator.count "Link to this definition")  
        Count the number of items in this range. This is computed lazily.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">collect</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">list</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.T</span><span class="p"><span class="pre">\]</span></span></span></span>[](#syside.LazyIterator.collect "Link to this definition")  
        Collect all items into a `list`.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">for\_each</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg0</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">Callable</span><span class="p"><span class="pre">\[</span></span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.T</span><span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">None</span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">bool</span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span>[<span class="pre">syside.VisitAction</span>](/v0.8.1/api/generated/syside.VisitAction.md "syside.VisitAction")<span class="p"><span class="pre">\]</span></span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span>[](#syside.LazyIterator.for_each "Link to this definition")  
        Lazily visit each item in this range. Visitation is stopped on returning `False` or `VisitAction.Stop`;
    
    <!-- end list -->
    
      - *<span class="pre">classmethod</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">\_\_class\_getitem\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">item</span></span>*<span class="sig-paren">)</span>[](#syside.LazyIterator.__class_getitem__ "Link to this definition")

</div>
