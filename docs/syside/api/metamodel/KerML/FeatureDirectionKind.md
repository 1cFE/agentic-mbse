<div id="featuredirectionkind" class="section">

<span id="metamodel-kerml-featuredirectionkind"></span>

# FeatureDirectionKind[](#featuredirectionkind "Link to this heading")

`FeatureDirectionKind` is defined in KerML specification on [page 168](https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=168). Excerpt from the machine readable specification:

> 
> 
> <div>
> 
> `FeatureDirectionKind` enumerates the possible kinds of `direction` that a `Feature` may be given as a member of a `Type`.
> 
> </div>

The following diagram shows the inheritance hierarchy of `FeatureDirectionKind` according to the specification:

<div class="align-center" data-align="center">

<div class="graphviz">

![// Class: FeatureDirectionKind digraph { FeatureDirectionKind \[label="FeatureDirectionKind (KerML)" shape=plaintext\] }](_images/graphviz-b006a41c82d0c236434335ad7c77d97d6f75e68d.png)

</div>

</div>

The following table shows all attributes defined for `FeatureDirectionKind` according to the specification together with the documentation from the machine readable specification. Note that in Syside API, we use snake case for attribute names instead of Pascal case used in the specification.

<div class="pst-scrollable-table-container">

Attribute

</div>

</div>

Documentation from machine readable specification

Attributes defined in [`FeatureDirectionKind`](#syside.FeatureDirectionKind "syside.FeatureDirectionKind"):

[`In`](#syside.FeatureDirectionKind.In "syside.FeatureDirectionKind.In")

Values of the `Feature` on each instance of its domain are determined externally to that instance and used internally.

[`Inout`](#syside.FeatureDirectionKind.Inout "syside.FeatureDirectionKind.Inout")

Values of the `Feature` on each instance are determined either as *in* or *out* directions, or both.

[`Out`](#syside.FeatureDirectionKind.Out "syside.FeatureDirectionKind.Out")

Values of the `Feature` on each instance of its domain are determined internally to that instance and used externally.

The following table lists Syside specific attributes available for class [`FeatureDirectionKind`](#syside.FeatureDirectionKind "syside.FeatureDirectionKind"):

<div class="pst-scrollable-table-container">

|                  |
| ---------------- |
| Python Attribute |

</div>

  - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">FeatureDirectionKind</span></span><span class="sig-paren">(</span>*<span class="o"><span class="pre">\*</span></span><span class="n"><span class="pre">args</span></span>*, *<span class="o"><span class="pre">\*\*</span></span><span class="n"><span class="pre">kwds</span></span>*<span class="sig-paren">)</span>[](#syside.FeatureDirectionKind "Link to this definition")
    
      - <span class="sig-name descname"><span class="pre">In</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">0</span>*[](#syside.FeatureDirectionKind.In "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">Inout</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">1</span>*[](#syside.FeatureDirectionKind.Inout "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">Out</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">2</span>*[](#syside.FeatureDirectionKind.Out "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">classmethod</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">\_\_signature\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.FeatureDirectionKind.__signature__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_new\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">value</span></span>*<span class="sig-paren">)</span>[](#syside.FeatureDirectionKind.__new__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_repr\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.FeatureDirectionKind.__repr__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_str\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.FeatureDirectionKind.__str__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_dir\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.FeatureDirectionKind.__dir__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_format\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">format\_spec</span></span>*<span class="sig-paren">)</span>[](#syside.FeatureDirectionKind.__format__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_hash\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.FeatureDirectionKind.__hash__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_reduce\_ex\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">proto</span></span>*<span class="sig-paren">)</span>[](#syside.FeatureDirectionKind.__reduce_ex__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_deepcopy\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">memo</span></span>*<span class="sig-paren">)</span>[](#syside.FeatureDirectionKind.__deepcopy__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_copy\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.FeatureDirectionKind.__copy__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">name</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.FeatureDirectionKind.name "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">value</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.FeatureDirectionKind.value "Link to this definition")
