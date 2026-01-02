<div id="syside-messages" class="section">

# syside.Messages[](#syside-messages "Link to this heading")

  - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">Messages</span></span>[](#syside.Messages "Link to this definition")  
    Bases: [`syside.ConnectorEndsAccessor`](/v0.8.1/api/generated/syside.ConnectorEndsAccessor.md "syside.ConnectorEndsAccessor")\[[`ParameterMembership`](/v0.8.1/api/metamodel/KerML/ParameterMembership.md "syside.ParameterMembership"), [`syside.EventOccurrenceUsage`](/v0.8.1/api/metamodel/SysML/EventOccurrenceUsage.md "syside.EventOccurrenceUsage")\]
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">modifiable</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*[](#syside.Messages.modifiable "Link to this definition")  
        Returns `True` if the contents of this accessor can be modified. In such a case, `try_` methods will return values, and corresponding modification methods will not raise `ValueErrors`.
        
        `False` is returned when the corresponding textual syntax position is already occupied by other elements, e.g. `FlowUsage` `declared_messages` and `declared_ends` share the same position.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">try\_append</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg0</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">syside.M</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.R</span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">syside.M</span><span class="p"><span class="pre">\]</span></span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span></span></span>[](#syside.Messages.try_append "Link to this definition")  
        Try appending a new `Feature`. Ownership constraints apply.
        
        Returns a pair of (`membership`, `feature`) where `feature` is the argument passed in if the contents can be modified. Note that generally empty `Features` are not syntactically correct, and the correct syntax depends on the owner type.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">try\_append</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.R</span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">syside.M</span><span class="p"><span class="pre">\]</span></span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span></span></span>  
        Try appending a new default constructed `Feature` with type inferred from the corresponding member type in the textual syntax dependent on the owner of this accessor.
        
        Returns a pair of (`membership`, `feature`) if the contents can be modified. Note that generally empty `Features` are not syntactically correct, and the correct syntax depends on the owner type.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">try\_insert</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg0</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">int</span></span>*, *<span class="n"><span class="pre">arg1</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">syside.M</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.R</span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">syside.M</span><span class="p"><span class="pre">\]</span></span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span></span></span>[](#syside.Messages.try_insert "Link to this definition")  
        Try inserting a new `Feature` at the specified index. Ownership constraints apply.
        
        Returns a pair of (`membership`, `feature`) where `feature` is the argument passed in if the contents can be modified. Note that generally empty `Features` are not syntactically correct, and the correct syntax depends on the owner type.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">try\_insert</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg0</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">int</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.R</span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">syside.M</span><span class="p"><span class="pre">\]</span></span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span></span></span>  
        Try inserting a new default constructed `Feature` at the index specified with type inferred from the corresponding member type in the textual syntax dependent on the owner of this accessor.
        
        Returns a pair of (`membership`, `feature`) if the contents can be modified. Note that generally empty `Features` are not syntactically correct, and the correct syntax depends on the owner type.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">append</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg0</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">syside.M</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.R</span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">syside.M</span><span class="p"><span class="pre">\]</span></span></span></span>[](#syside.Messages.append "Link to this definition")  
        Same as `try_append` but will raise `ValueError` if the contents cannot be modified.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">append</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.R</span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">syside.M</span><span class="p"><span class="pre">\]</span></span></span></span>
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">insert</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg0</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">int</span></span>*, *<span class="n"><span class="pre">arg1</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">syside.M</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.R</span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">syside.M</span><span class="p"><span class="pre">\]</span></span></span></span>[](#syside.Messages.insert "Link to this definition")  
        Same as `insert` but will raise `ValueError` if the contents cannot be modified.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">insert</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg0</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">int</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.R</span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">syside.M</span><span class="p"><span class="pre">\]</span></span></span></span>
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">clear</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span>[](#syside.Messages.clear "Link to this definition")  
        Clear the contents accessed by this accessor. Does nothing if the contents cannot be modified.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">erase</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">int</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span>[](#syside.Messages.erase "Link to this definition")  
        Erase `Feature` at the specified index. Raises `ValueError` if the index is out of bounds.
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">relationships</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.ContainerView</span>](/v0.8.1/api/generated/syside.ContainerView.md "syside.ContainerView")<span class="p"><span class="pre">\[</span></span><span class="pre">syside.R</span><span class="p"><span class="pre">\]</span></span>*[](#syside.Messages.relationships "Link to this definition")  
        The relationships in this container.
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">elements</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.ContainerView</span>](/v0.8.1/api/generated/syside.ContainerView.md "syside.ContainerView")<span class="p"><span class="pre">\[</span></span><span class="pre">syside.M</span><span class="p"><span class="pre">\]</span></span>*[](#syside.Messages.elements "Link to this definition")  
        The related elements in this container.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_len\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">int</span></span></span>[](#syside.Messages.__len__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_bool\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">bool</span></span></span>[](#syside.Messages.__bool__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_getitem\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">int</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">Tuple</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.R</span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">syside.M</span><span class="p"><span class="pre">\]</span></span></span></span>[](#syside.Messages.__getitem__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">at</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">int</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">Tuple</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.R</span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">syside.M</span><span class="p"><span class="pre">\]</span></span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span></span></span>[](#syside.Messages.at "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">classmethod</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">\_\_class\_getitem\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">item</span></span>*<span class="sig-paren">)</span>[](#syside.Messages.__class_getitem__ "Link to this definition")

</div>
