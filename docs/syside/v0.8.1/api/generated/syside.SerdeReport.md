<div id="syside-serdereport" class="section">

# syside.SerdeReport[](#syside-serdereport "Link to this heading")

  - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">SerdeReport</span></span>[](#syside.SerdeReport "Link to this definition")  
    Bases: `typing.Generic`\[`T`\]
    
    (De)Serialization report containing emitted messages.
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">messages</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">list</span><span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.SerdeMessage</span>](/v0.8.1/api/generated/syside.SerdeMessage.md "syside.SerdeMessage")<span class="p"><span class="pre">\[</span></span><span class="pre">syside.T</span><span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">\]</span></span>*[](#syside.SerdeReport.messages "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_bool\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">bool</span></span></span>[](#syside.SerdeReport.__bool__ "Link to this definition")  
        Returns `True` if none of the messages are errors.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">passed</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">warnings\_as\_errors</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">False</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">bool</span></span></span>[](#syside.SerdeReport.passed "Link to this definition")  
        Check if the report has no errors. If `warnings_as_errors` is `True`, also check if it contains no warnings.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_str\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">str</span></span></span>[](#syside.SerdeReport.__str__ "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">classmethod</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">\_\_class\_getitem\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">item</span></span>*<span class="sig-paren">)</span>[](#syside.SerdeReport.__class_getitem__ "Link to this definition")

</div>
