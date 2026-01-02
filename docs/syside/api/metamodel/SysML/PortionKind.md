<div id="portionkind" class="section">

<span id="metamodel-sysml-portionkind"></span>

# PortionKind[](#portionkind "Link to this heading")

`PortionKind` is defined in SysML specification on [page 320](https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=320). Excerpt from the machine readable specification:

> 
> 
> <div>
> 
> `PortionKind` is an enumeration of the specific kinds of `Occurrence` portions that can be represented by an `OccurrenceUsage`.
> 
> </div>

The following diagram shows the inheritance hierarchy of `PortionKind` according to the specification:

<div class="align-center" data-align="center">

<div class="graphviz">

![// Class: PortionKind digraph { PortionKind \[label="PortionKind (SysML)" shape=plaintext\] }](_images/graphviz-c6460a3f99f23bea5a675a7a4157834ccc905282.png)

</div>

</div>

The following table shows all attributes defined for `PortionKind` according to the specification together with the documentation from the machine readable specification. Note that in Syside API, we use snake case for attribute names instead of Pascal case used in the specification.

<div class="pst-scrollable-table-container">

Attribute

</div>

</div>

Documentation from machine readable specification

Attributes defined in [`PortionKind`](#syside.PortionKind "syside.PortionKind"):

[`Snapshot`](#syside.PortionKind.Snapshot "syside.PortionKind.Snapshot")

A snapshot of an `Occurrence` (a time slice with zero duration).

[`Timeslice`](#syside.PortionKind.Timeslice "syside.PortionKind.Timeslice")

A time slice of an `Occurrence` (a portion over time).

The following table lists Syside specific attributes available for class [`PortionKind`](#syside.PortionKind "syside.PortionKind"):

<div class="pst-scrollable-table-container">

|                  |
| ---------------- |
| Python Attribute |

</div>

  - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">PortionKind</span></span><span class="sig-paren">(</span>*<span class="o"><span class="pre">\*</span></span><span class="n"><span class="pre">args</span></span>*, *<span class="o"><span class="pre">\*\*</span></span><span class="n"><span class="pre">kwds</span></span>*<span class="sig-paren">)</span>[](#syside.PortionKind "Link to this definition")
    
      - <span class="sig-name descname"><span class="pre">Timeslice</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">0</span>*[](#syside.PortionKind.Timeslice "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">Snapshot</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">1</span>*[](#syside.PortionKind.Snapshot "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">classmethod</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">\_\_signature\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.PortionKind.__signature__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_new\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">value</span></span>*<span class="sig-paren">)</span>[](#syside.PortionKind.__new__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_repr\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.PortionKind.__repr__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_str\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.PortionKind.__str__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_dir\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.PortionKind.__dir__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_format\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">format\_spec</span></span>*<span class="sig-paren">)</span>[](#syside.PortionKind.__format__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_hash\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.PortionKind.__hash__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_reduce\_ex\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">proto</span></span>*<span class="sig-paren">)</span>[](#syside.PortionKind.__reduce_ex__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_deepcopy\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">memo</span></span>*<span class="sig-paren">)</span>[](#syside.PortionKind.__deepcopy__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_copy\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.PortionKind.__copy__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">name</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.PortionKind.name "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">value</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.PortionKind.value "Link to this definition")
