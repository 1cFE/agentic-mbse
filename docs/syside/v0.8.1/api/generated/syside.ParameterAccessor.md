<div id="syside-parameteraccessor" class="section">

# syside.ParameterAccessor[](#syside-parameteraccessor "Link to this heading")

  - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">ParameterAccessor</span></span>[](#syside.ParameterAccessor "Link to this definition")  
    Bases: [`syside.OwnedMemberAccessor`](/v0.8.1/api/generated/syside.OwnedMemberAccessor.md "syside.OwnedMemberAccessor")\[[`ParameterMembership`](/v0.8.1/api/metamodel/KerML/ParameterMembership.md "syside.ParameterMembership"), [`ReferenceUsage`](/v0.8.1/api/metamodel/SysML/ReferenceUsage.md "syside.ReferenceUsage")\]
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">argument</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.Expression</span>](/v0.8.1/api/metamodel/KerML/Expression.md "syside.Expression")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span>*[](#syside.ParameterAccessor.argument "Link to this definition")  
        The `argument` accessible by this `parameter`.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">set\_argument</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">expression</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">syside.ParameterAccessor.set\_argument.M</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.FeatureValue</span>](/v0.8.1/api/metamodel/KerML/FeatureValue.md "syside.FeatureValue")<span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">syside.ParameterAccessor.set\_argument.M</span><span class="p"><span class="pre">\]</span></span></span></span>[](#syside.ParameterAccessor.set_argument "Link to this definition")  
        Set the `argument` to an owned `expression`. Ownership constraints apply. An empty parameter will be constructed if there is none.
        
        Returns a pair of (`feature_value`, `argument`).
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">set\_argument</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">expression</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">syside.ParameterAccessor.set\_argument.M</span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.FeatureValue</span>](/v0.8.1/api/metamodel/KerML/FeatureValue.md "syside.FeatureValue")<span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">syside.ParameterAccessor.set\_argument.M</span><span class="p"><span class="pre">\]</span></span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span></span></span>  
        `set_argument` overload that will instead remove the argument if `expression is None` and return `None`. Otherwise behaviour is the same.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">set\_argument</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">expression</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">type</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.ParameterAccessor.set\_argument.M</span><span class="p"><span class="pre">\]</span></span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.FeatureValue</span>](/v0.8.1/api/metamodel/KerML/FeatureValue.md "syside.FeatureValue")<span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">syside.ParameterAccessor.set\_argument.M</span><span class="p"><span class="pre">\]</span></span></span></span>  
        Set the `argument` to an empty `Expression` with the corresponding type. An empty parameter will be constructed if there is none.
        
        Returns a pair of (`feature_value`, `argument`).
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">remove\_argument</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span>[](#syside.ParameterAccessor.remove_argument "Link to this definition")  
        Remove the `argument` while leaving `parameter` intact. Does nothing if there is no `argument`.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">set\_member\_element</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">element</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">syside.ParameterAccessor.set\_member\_element.M</span></span>*, *<span class="n"><span class="pre">name</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.NameID</span>](/v0.8.1/api/generated/syside.NameID.md "syside.NameID")</span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">...</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.ParameterMembership</span>](/v0.8.1/api/metamodel/KerML/ParameterMembership.md "syside.ParameterMembership")<span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">syside.ParameterAccessor.set\_member\_element.M</span><span class="p"><span class="pre">\]</span></span></span></span>[](#syside.ParameterAccessor.set_member_element "Link to this definition")  
        Set a new *owned* `member_element`, ownership constraints apply. Replaces the previous `member_element`, which may be reused by the model. `name_id` has no effect since the `element` is always taken ownership of.
        
        Returns a pair of (`membership`, `member_element`) where `member_element` is `element`.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">set\_member\_element</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">element</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">syside.ParameterAccessor.set\_member\_element.M</span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span></span>*, *<span class="n"><span class="pre">name</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.NameID</span>](/v0.8.1/api/generated/syside.NameID.md "syside.NameID")</span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">...</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.ParameterMembership</span>](/v0.8.1/api/metamodel/KerML/ParameterMembership.md "syside.ParameterMembership")<span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">syside.ParameterAccessor.set\_member\_element.M</span><span class="p"><span class="pre">\]</span></span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span></span></span>  
        `set_member_element` overload that will remove the member element if `element` is `None`, otherwise the behaviour is the same.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">set\_member\_element</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">element</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">type</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.ParameterAccessor.set\_member\_element.M</span><span class="p"><span class="pre">\]</span></span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.ParameterMembership</span>](/v0.8.1/api/metamodel/KerML/ParameterMembership.md "syside.ParameterMembership")<span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">syside.ParameterAccessor.set\_member\_element.M</span><span class="p"><span class="pre">\]</span></span></span></span>  
        Constructs a new empty `member_element` with the provided type. Replaces the previous `member_element`. Because a new element is always constructed, ownership constraints do not apply.
        
        Returns a pair of (`membership`, `member_element`).
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">add\_member\_element</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.R</span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">syside.M</span><span class="p"><span class="pre">\]</span></span></span></span>[](#syside.ParameterAccessor.add_member_element "Link to this definition")  
        Constructs a new `member_element` with the default type if this `member` is empty, otherwise does nothing.
        
        Returns a pair of (`membership`, `member_element`)
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">membership</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">syside.R</span>*[](#syside.ParameterAccessor.membership "Link to this definition")  
        The `membership` of this `member` if it is not empty.
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">member\_element</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">syside.M</span>*[](#syside.ParameterAccessor.member_element "Link to this definition")  
        The `member_element` of this `member` if it is not empty.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">remove\_member\_element</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span>[](#syside.ParameterAccessor.remove_member_element "Link to this definition")  
        Remove the `member_element` leaving this `member` empty. Note that not all empty `members` are valid textual syntax. This does not check that the model is left in a valid state.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_bool\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">bool</span></span></span>[](#syside.ParameterAccessor.__bool__ "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">classmethod</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">\_\_class\_getitem\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">item</span></span>*<span class="sig-paren">)</span>[](#syside.ParameterAccessor.__class_getitem__ "Link to this definition")

</div>
