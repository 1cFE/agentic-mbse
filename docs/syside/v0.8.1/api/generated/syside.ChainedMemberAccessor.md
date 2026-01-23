<div id="syside-chainedmemberaccessor" class="section">

# syside.ChainedMemberAccessor[](#syside-chainedmemberaccessor "Link to this heading")

  - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">ChainedMemberAccessor</span></span>[](#syside.ChainedMemberAccessor "Link to this definition")  
    Bases: [`MemberAccessor`](/v0.8.1/api/generated/syside.MemberAccessor.md "syside.MemberAccessor")\[`syside.ChainedMemberAccessor.R`, `syside.ChainedMemberAccessor.M`\]
    
      - <span class="sig-name descname"><span class="pre">set\_member\_element\_chain</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">Sequence</span><span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Feature</span>](/v0.8.1/api/metamodel/KerML/Feature.md "syside.Feature")<span class="p"><span class="pre">\]</span></span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.OwningMembership</span>](/v0.8.1/api/metamodel/KerML/OwningMembership.md "syside.OwningMembership")<span class="p"><span class="pre">,</span></span><span class="w"> </span>[<span class="pre">syside.Feature</span>](/v0.8.1/api/metamodel/KerML/Feature.md "syside.Feature")<span class="p"><span class="pre">\]</span></span></span></span>[](#syside.ChainedMemberAccessor.set_member_element_chain "Link to this definition")  
        Set the reference to a chain of `Features`. Replaces the previous `member_element`.
        
        Returns a pair of (`membership`, `member_element`) where `member_element` is the `Feature` with owned `FeatureChainings` to the provided `Features` with order preserved.

</div>
