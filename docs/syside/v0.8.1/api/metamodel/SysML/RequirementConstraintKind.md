<div id="requirementconstraintkind" class="section">

<span id="metamodel-sysml-requirementconstraintkind"></span>

# RequirementConstraintKind[](#requirementconstraintkind "Link to this heading")

`RequirementConstraintKind` is defined in SysML specification on [page 389](https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=389). Excerpt from the machine readable specification:

> 
> 
> <div>
> 
> A `RequirementConstraintKind` indicates whether a `ConstraintUsage` is an assumption or a requirement in a `RequirementDefinition` or `RequirementUsage`.
> 
> </div>

The following diagram shows the inheritance hierarchy of `RequirementConstraintKind` according to the specification:

<div class="align-center" data-align="center">

<div class="graphviz">

![// Class: RequirementConstraintKind digraph { RequirementConstraintKind \[label="RequirementConstraintKind (SysML)" shape=plaintext\] }](_images/graphviz-6f906900ec3c5031a65de5a35ae39d9912877253.png)

</div>

</div>

The following table shows all attributes defined for `RequirementConstraintKind` according to the specification together with the documentation from the machine readable specification. Note that in Syside API, we use snake case for attribute names instead of Pascal case used in the specification.

<div class="pst-scrollable-table-container">

Attribute

</div>

</div>

Documentation from machine readable specification

Attributes defined in [`RequirementConstraintKind`](#syside.RequirementConstraintKind "syside.RequirementConstraintKind"):

[`Assumption`](#syside.RequirementConstraintKind.Assumption "syside.RequirementConstraintKind.Assumption")

Indicates that a member `ConstraintUsage` of a `RequirementDefinition` or `RequirementUsage` represents an assumption.

[`Requirement`](#syside.RequirementConstraintKind.Requirement "syside.RequirementConstraintKind.Requirement")

Indicates that a member `ConstraintUsage` of a `RequirementDefinition` or `RequirementUsage`represents an requirement.

The following table lists Syside specific attributes available for class [`RequirementConstraintKind`](#syside.RequirementConstraintKind "syside.RequirementConstraintKind"):

<div class="pst-scrollable-table-container">

|                  |
| ---------------- |
| Python Attribute |

</div>

  - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">RequirementConstraintKind</span></span><span class="sig-paren">(</span>*<span class="o"><span class="pre">\*</span></span><span class="n"><span class="pre">args</span></span>*, *<span class="o"><span class="pre">\*\*</span></span><span class="n"><span class="pre">kwds</span></span>*<span class="sig-paren">)</span>[](#syside.RequirementConstraintKind "Link to this definition")
    
      - <span class="sig-name descname"><span class="pre">Assumption</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">0</span>*[](#syside.RequirementConstraintKind.Assumption "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">Requirement</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">1</span>*[](#syside.RequirementConstraintKind.Requirement "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">classmethod</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">\_\_signature\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.RequirementConstraintKind.__signature__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_new\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">value</span></span>*<span class="sig-paren">)</span>[](#syside.RequirementConstraintKind.__new__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_repr\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.RequirementConstraintKind.__repr__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_str\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.RequirementConstraintKind.__str__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_dir\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.RequirementConstraintKind.__dir__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_format\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">format\_spec</span></span>*<span class="sig-paren">)</span>[](#syside.RequirementConstraintKind.__format__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_hash\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.RequirementConstraintKind.__hash__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_reduce\_ex\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">proto</span></span>*<span class="sig-paren">)</span>[](#syside.RequirementConstraintKind.__reduce_ex__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_deepcopy\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">memo</span></span>*<span class="sig-paren">)</span>[](#syside.RequirementConstraintKind.__deepcopy__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_copy\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.RequirementConstraintKind.__copy__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">name</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.RequirementConstraintKind.name "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">value</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.RequirementConstraintKind.value "Link to this definition")
