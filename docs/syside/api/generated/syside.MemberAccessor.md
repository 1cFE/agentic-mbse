<div id="syside-memberaccessor" class="section">

# syside.MemberAccessor[](#syside-memberaccessor "Link to this heading")

  - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">MemberAccessor</span></span>[](#syside.MemberAccessor "Link to this definition")  
    Bases: `typing.Generic`\[`R`, `syside.M`\]
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">membership</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">syside.R</span>*[](#syside.MemberAccessor.membership "Link to this definition")  
        The `membership` of this `member` if it is not empty.
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">member\_element</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">syside.M</span>*[](#syside.MemberAccessor.member_element "Link to this definition")  
        The `member_element` of this `member` if it is not empty.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">set\_member\_element</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">element</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">syside.M</span></span>*, *<span class="n"><span class="pre">name</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.NameID</span>](/v0.8.1/api/generated/syside.NameID.md "syside.NameID")</span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">...</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.R</span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">syside.M</span><span class="p"><span class="pre">\]</span></span></span></span>[](#syside.MemberAccessor.set_member_element "Link to this definition")  
        Set a new `member_element`. `element` will only be referenced if the `membership` is `Membership`, otherwise ownership constraints apply. Replaces the previous `member_element`, which may be reused by the model if it was owned.
        
        Returns a pair of (`membership`, `member_element`) where `member_element` is `element`.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">set\_member\_element</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">element</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">syside.M</span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span></span>*, *<span class="n"><span class="pre">name</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.NameID</span>](/v0.8.1/api/generated/syside.NameID.md "syside.NameID")</span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">...</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.R</span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">syside.M</span><span class="p"><span class="pre">\]</span></span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span></span></span>  
        `set_member_element` overload that will remove the member element if `element` is `None`, otherwise the behaviour is the same.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">remove\_member\_element</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span>[](#syside.MemberAccessor.remove_member_element "Link to this definition")  
        Remove the `member_element` leaving this `member` empty. Note that not all empty `members` are valid textual syntax. This does not check that the model is left in a valid state.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_bool\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">bool</span></span></span>[](#syside.MemberAccessor.__bool__ "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">classmethod</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">\_\_class\_getitem\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">item</span></span>*<span class="sig-paren">)</span>[](#syside.MemberAccessor.__class_getitem__ "Link to this definition")

</div>
