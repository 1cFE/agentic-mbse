<div id="syside-referentaccessor" class="section">

# syside.ReferentAccessor[](#syside-referentaccessor "Link to this heading")

  - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">ReferentAccessor</span></span>[](#syside.ReferentAccessor "Link to this definition")  
    Bases: [`syside.MemberAccessor`](/v0.8.1/api/generated/syside.MemberAccessor.md "syside.MemberAccessor")\[[`syside.Membership`](/v0.8.1/api/metamodel/KerML/Membership.md "syside.Membership"), [`syside.Feature`](/v0.8.1/api/metamodel/KerML/Feature.md "syside.Feature")\]
    
      - <span class="sig-name descname"><span class="pre">set\_member\_element</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">element</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">syside.ReferentAccessor.set\_member\_element.M</span></span>*, *<span class="n"><span class="pre">name</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.NameID</span>](/v0.8.1/api/generated/syside.NameID.md "syside.NameID")</span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">...</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Membership</span>](/v0.8.1/api/metamodel/KerML/Membership.md "syside.Membership")<span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">syside.ReferentAccessor.set\_member\_element.M</span><span class="p"><span class="pre">\]</span></span></span></span>[](#syside.ReferentAccessor.set_member_element "Link to this definition")  
        Set a new `member_element`. `element` will only be referenced if the `membership` is `Membership`, otherwise ownership constraints apply. Replaces the previous `member_element`, which may be reused by the model if it was owned.
        
        Returns a pair of (`membership`, `member_element`) where `member_element` is `element`.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">set\_member\_element</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">element</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">syside.ReferentAccessor.set\_member\_element.M</span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span></span>*, *<span class="n"><span class="pre">name</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.NameID</span>](/v0.8.1/api/generated/syside.NameID.md "syside.NameID")</span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">...</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Membership</span>](/v0.8.1/api/metamodel/KerML/Membership.md "syside.Membership")<span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">syside.ReferentAccessor.set\_member\_element.M</span><span class="p"><span class="pre">\]</span></span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span></span></span>  
        `set_member_element` overload that will remove the member element if `element` is `None`, otherwise the behaviour is the same.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">set\_owned\_expression</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">syside.ReferentAccessor.set\_owned\_expression.M</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.FeatureMembership</span>](/v0.8.1/api/metamodel/KerML/FeatureMembership.md "syside.FeatureMembership")<span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">syside.ReferentAccessor.set\_owned\_expression.M</span><span class="p"><span class="pre">\]</span></span></span></span>[](#syside.ReferentAccessor.set_owned_expression "Link to this definition")  
        Set the referent to an owned `Expression`. Ownership constraints apply.
        
        Returns a pair of (`feature_membership`, `referent`).
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">set\_owned\_expression</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">type</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.ReferentAccessor.set\_owned\_expression.M</span><span class="p"><span class="pre">\]</span></span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.FeatureMembership</span>](/v0.8.1/api/metamodel/KerML/FeatureMembership.md "syside.FeatureMembership")<span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">syside.ReferentAccessor.set\_owned\_expression.M</span><span class="p"><span class="pre">\]</span></span></span></span>  
        Set the referent to an empty `Expression` with the corresponding tye.
        
        Returns a pair of (`feature_membership`, `referent`). Note that empty `Expressions` may not be representable in textual syntax.
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">membership</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">syside.R</span>*[](#syside.ReferentAccessor.membership "Link to this definition")  
        The `membership` of this `member` if it is not empty.
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">member\_element</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">syside.M</span>*[](#syside.ReferentAccessor.member_element "Link to this definition")  
        The `member_element` of this `member` if it is not empty.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">remove\_member\_element</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span>[](#syside.ReferentAccessor.remove_member_element "Link to this definition")  
        Remove the `member_element` leaving this `member` empty. Note that not all empty `members` are valid textual syntax. This does not check that the model is left in a valid state.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_bool\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">bool</span></span></span>[](#syside.ReferentAccessor.__bool__ "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">classmethod</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">\_\_class\_getitem\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">item</span></span>*<span class="sig-paren">)</span>[](#syside.ReferentAccessor.__class_getitem__ "Link to this definition")

</div>
