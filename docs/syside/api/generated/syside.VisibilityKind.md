<div id="syside-visibilitykind" class="section">

# syside.VisibilityKind[](#syside-visibilitykind "Link to this heading")

  - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">VisibilityKind</span></span><span class="sig-paren">(</span>*<span class="o"><span class="pre">\*</span></span><span class="n"><span class="pre">args</span></span>*, *<span class="o"><span class="pre">\*\*</span></span><span class="n"><span class="pre">kwds</span></span>*<span class="sig-paren">)</span>[](#syside.VisibilityKind "Link to this definition")  
    Bases: `enum.Enum`
    
    Implementation of `VisibilityKind` defined in the KerML specification.
    
    **Specification**:
    
    > 
    > 
    > <div>
    > 
    > `VisibilityKind` is an enumeration whose literals specify the visibility of a `Membership` of an `Element` in a `Namespace` outside of that `Namespace`. Note that “visibility” specifically restricts whether an `Element` in a `Namespace` may be referenced by name from outside the `Namespace` and only otherwise restricts access to an `Element` as provided by specific constraints in the abstract syntax (e.g., preventing the import or inheritance of private `Elements`).
    > 
    > </div>
    
    For language description, see section [7.2.5.2](https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=47) of the KerML specification. For more details on the model, see section [8.3.2.4.7](https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=161) of the KerML specification.
    
    Initialization
    
      - <span class="sig-name descname"><span class="pre">Private</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">0</span>*[](#syside.VisibilityKind.Private "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">Protected</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">1</span>*[](#syside.VisibilityKind.Protected "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">Public</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">2</span>*[](#syside.VisibilityKind.Public "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">classmethod</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">\_\_signature\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.VisibilityKind.__signature__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_new\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">value</span></span>*<span class="sig-paren">)</span>[](#syside.VisibilityKind.__new__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_repr\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.VisibilityKind.__repr__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_str\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.VisibilityKind.__str__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_dir\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.VisibilityKind.__dir__ "Link to this definition")  
        Returns public methods and other interesting attributes.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_format\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">format\_spec</span></span>*<span class="sig-paren">)</span>[](#syside.VisibilityKind.__format__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_hash\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.VisibilityKind.__hash__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_reduce\_ex\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">proto</span></span>*<span class="sig-paren">)</span>[](#syside.VisibilityKind.__reduce_ex__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_deepcopy\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">memo</span></span>*<span class="sig-paren">)</span>[](#syside.VisibilityKind.__deepcopy__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_copy\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.VisibilityKind.__copy__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">name</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.VisibilityKind.name "Link to this definition")  
        The name of the Enum member.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">value</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.VisibilityKind.value "Link to this definition")  
        The value of the Enum member.

</div>
