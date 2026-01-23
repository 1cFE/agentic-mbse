<div id="triggerkind" class="section">

<span id="metamodel-sysml-triggerkind"></span>

# TriggerKind[](#triggerkind "Link to this heading")

`TriggerKind` is defined in SysML specification on [page 363](https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=363). Excerpt from the machine readable specification:

> 
> 
> <div>
> 
> `TriggerKind` enumerates the kinds of triggers that can be represented by a `TriggerInvocationExpression`.
> 
> </div>

The following diagram shows the inheritance hierarchy of `TriggerKind` according to the specification:

<div class="align-center" data-align="center">

<div class="graphviz">

![// Class: TriggerKind digraph { TriggerKind \[label="TriggerKind (SysML)" shape=plaintext\] }](_images/graphviz-4553f00b94ea3b6fc53ab6fa91964aab4d638301.png)

</div>

</div>

The following table shows all attributes defined for `TriggerKind` according to the specification together with the documentation from the machine readable specification. Note that in Syside API, we use snake case for attribute names instead of Pascal case used in the specification.

<div class="pst-scrollable-table-container">

Attribute

</div>

</div>

Documentation from machine readable specification

Attributes defined in [`TriggerKind`](#syside.TriggerKind "syside.TriggerKind"):

[`After`](#syside.TriggerKind.After "syside.TriggerKind.After")

Indicates a *relative time trigger*, corresponding to the `TriggerAfter` `Function` from the `Triggers` model in the `Kernel Semantic Library.`

[`At`](#syside.TriggerKind.At "syside.TriggerKind.At")

Indicates an *absolute time trigger*, corresponding to the `TriggerAt` `Function` from the `Triggers` model in the Kernel Semantic Library.

[`When`](#syside.TriggerKind.When "syside.TriggerKind.When")

Indicates a *change trigger*, corresponding to the `TriggerWhen` `Function` from the `Triggers` model in the Kernel Semantic Library.

The following table lists Syside specific attributes available for class [`TriggerKind`](#syside.TriggerKind "syside.TriggerKind"):

<div class="pst-scrollable-table-container">

|                  |
| ---------------- |
| Python Attribute |

</div>

  - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">TriggerKind</span></span><span class="sig-paren">(</span>*<span class="o"><span class="pre">\*</span></span><span class="n"><span class="pre">args</span></span>*, *<span class="o"><span class="pre">\*\*</span></span><span class="n"><span class="pre">kwds</span></span>*<span class="sig-paren">)</span>[](#syside.TriggerKind "Link to this definition")
    
      - <span class="sig-name descname"><span class="pre">When</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">0</span>*[](#syside.TriggerKind.When "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">At</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">1</span>*[](#syside.TriggerKind.At "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">After</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">2</span>*[](#syside.TriggerKind.After "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">classmethod</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">\_\_signature\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.TriggerKind.__signature__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_new\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">value</span></span>*<span class="sig-paren">)</span>[](#syside.TriggerKind.__new__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_repr\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.TriggerKind.__repr__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_str\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.TriggerKind.__str__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_dir\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.TriggerKind.__dir__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_format\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">format\_spec</span></span>*<span class="sig-paren">)</span>[](#syside.TriggerKind.__format__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_hash\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.TriggerKind.__hash__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_reduce\_ex\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">proto</span></span>*<span class="sig-paren">)</span>[](#syside.TriggerKind.__reduce_ex__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_deepcopy\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">memo</span></span>*<span class="sig-paren">)</span>[](#syside.TriggerKind.__deepcopy__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_copy\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.TriggerKind.__copy__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">name</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.TriggerKind.name "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">value</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.TriggerKind.value "Link to this definition")
