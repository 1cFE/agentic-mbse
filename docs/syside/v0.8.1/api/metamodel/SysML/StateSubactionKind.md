<div id="statesubactionkind" class="section">

<span id="metamodel-sysml-statesubactionkind"></span>

# StateSubactionKind[](#statesubactionkind "Link to this heading")

`StateSubactionKind` is defined in SysML specification on [page 367](https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=367). Excerpt from the machine readable specification:

> 
> 
> <div>
> 
> A `StateSubactionKind` indicates whether the `action` of a StateSubactionMembership is an entry, do or exit action.
> 
> </div>

The following diagram shows the inheritance hierarchy of `StateSubactionKind` according to the specification:

<div class="align-center" data-align="center">

<div class="graphviz">

![// Class: StateSubactionKind digraph { StateSubactionKind \[label="StateSubactionKind (SysML)" shape=plaintext\] }](_images/graphviz-0fbc32bccb396c781a46bdab3d7b3fc298b38834.png)

</div>

</div>

The following table shows all attributes defined for `StateSubactionKind` according to the specification together with the documentation from the machine readable specification. Note that in Syside API, we use snake case for attribute names instead of Pascal case used in the specification.

<div class="pst-scrollable-table-container">

Attribute

</div>

</div>

Documentation from machine readable specification

Attributes defined in [`StateSubactionKind`](#syside.StateSubactionKind "syside.StateSubactionKind"):

[`Do`](#syside.StateSubactionKind.Do "syside.StateSubactionKind.Do")

Indicates that the `action` of a `StateSubactionMembership` is a `doAction`.

[`Entry`](#syside.StateSubactionKind.Entry "syside.StateSubactionKind.Entry")

Indicates that the `action` of a `StateSubactionMembership` is an `entryAction`.

[`Exit`](#syside.StateSubactionKind.Exit "syside.StateSubactionKind.Exit")

Indicates that the `action` of a `StateSubactionMembership` is an `exitAction`.

The following table lists Syside specific attributes available for class [`StateSubactionKind`](#syside.StateSubactionKind "syside.StateSubactionKind"):

<div class="pst-scrollable-table-container">

|                  |
| ---------------- |
| Python Attribute |

</div>

  - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">StateSubactionKind</span></span><span class="sig-paren">(</span>*<span class="o"><span class="pre">\*</span></span><span class="n"><span class="pre">args</span></span>*, *<span class="o"><span class="pre">\*\*</span></span><span class="n"><span class="pre">kwds</span></span>*<span class="sig-paren">)</span>[](#syside.StateSubactionKind "Link to this definition")
    
      - <span class="sig-name descname"><span class="pre">Entry</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">0</span>*[](#syside.StateSubactionKind.Entry "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">Do</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">1</span>*[](#syside.StateSubactionKind.Do "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">Exit</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">2</span>*[](#syside.StateSubactionKind.Exit "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">classmethod</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">\_\_signature\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.StateSubactionKind.__signature__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_new\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">value</span></span>*<span class="sig-paren">)</span>[](#syside.StateSubactionKind.__new__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_repr\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.StateSubactionKind.__repr__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_str\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.StateSubactionKind.__str__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_dir\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.StateSubactionKind.__dir__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_format\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">format\_spec</span></span>*<span class="sig-paren">)</span>[](#syside.StateSubactionKind.__format__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_hash\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.StateSubactionKind.__hash__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_reduce\_ex\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">proto</span></span>*<span class="sig-paren">)</span>[](#syside.StateSubactionKind.__reduce_ex__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_deepcopy\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">memo</span></span>*<span class="sig-paren">)</span>[](#syside.StateSubactionKind.__deepcopy__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_copy\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.StateSubactionKind.__copy__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">name</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.StateSubactionKind.name "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">value</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.StateSubactionKind.value "Link to this definition")
