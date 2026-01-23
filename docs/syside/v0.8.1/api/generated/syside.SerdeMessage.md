<div id="syside-serdemessage" class="section">

# syside.SerdeMessage[](#syside-serdemessage "Link to this heading")

  - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">SerdeMessage</span></span>[](#syside.SerdeMessage "Link to this definition")  
    Bases: `typing.Generic`\[`T`\]
    
    Message emitted during (de)serialization
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">context</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">syside.T</span>*[](#syside.SerdeMessage.context "Link to this definition")  
        The context that this message applies to.
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">severity</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.DiagnosticSeverity</span>](/v0.8.1/api/generated/syside.DiagnosticSeverity.md "syside.DiagnosticSeverity")*[](#syside.SerdeMessage.severity "Link to this definition")  
        The severity of the message.
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">message</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span>*[](#syside.SerdeMessage.message "Link to this definition")  
        Message contents.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_str\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">str</span></span></span>[](#syside.SerdeMessage.__str__ "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">classmethod</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">\_\_class\_getitem\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">item</span></span>*<span class="sig-paren">)</span>[](#syside.SerdeMessage.__class_getitem__ "Link to this definition")

</div>
