<div id="transitionfeaturekind" class="section">

<span id="metamodel-sysml-transitionfeaturekind"></span>

# TransitionFeatureKind[](#transitionfeaturekind "Link to this heading")

`TransitionFeatureKind` is defined in SysML specification on [page 373](https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=373). Excerpt from the machine readable specification:

> 
> 
> <div>
> 
> A `TransitionActionKind` indicates whether the `transitionFeature` of a `TransitionFeatureMembership` is a trigger, guard or effect.
> 
> </div>

The following diagram shows the inheritance hierarchy of `TransitionFeatureKind` according to the specification:

<div class="align-center" data-align="center">

<div class="graphviz">

![// Class: TransitionFeatureKind digraph { TransitionFeatureKind \[label="TransitionFeatureKind (SysML)" shape=plaintext\] }](_images/graphviz-21d8c09c5056aa4096b5c1920e98d88797922ab1.png)

</div>

</div>

The following table shows all attributes defined for `TransitionFeatureKind` according to the specification together with the documentation from the machine readable specification. Note that in Syside API, we use snake case for attribute names instead of Pascal case used in the specification.

<div class="pst-scrollable-table-container">

Attribute

</div>

</div>

Documentation from machine readable specification

Attributes defined in [`TransitionFeatureKind`](#syside.TransitionFeatureKind "syside.TransitionFeatureKind"):

[`Effect`](#syside.TransitionFeatureKind.Effect "syside.TransitionFeatureKind.Effect")

Indicates that the `transitionFeature` of a `TransitionFeatureMembership` is an `effectAction`.

[`Guard`](#syside.TransitionFeatureKind.Guard "syside.TransitionFeatureKind.Guard")

Indicates that the `transitionFeature` of a `TransitionFeatureMembership` is a `guardExpression`.

[`Trigger`](#syside.TransitionFeatureKind.Trigger "syside.TransitionFeatureKind.Trigger")

Indicates that the `transitionFeature` of a `TransitionFeatureMembership` is a `triggerAction`.

The following table lists Syside specific attributes available for class [`TransitionFeatureKind`](#syside.TransitionFeatureKind "syside.TransitionFeatureKind"):

<div class="pst-scrollable-table-container">

|                  |
| ---------------- |
| Python Attribute |

</div>

  - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">TransitionFeatureKind</span></span><span class="sig-paren">(</span>*<span class="o"><span class="pre">\*</span></span><span class="n"><span class="pre">args</span></span>*, *<span class="o"><span class="pre">\*\*</span></span><span class="n"><span class="pre">kwds</span></span>*<span class="sig-paren">)</span>[](#syside.TransitionFeatureKind "Link to this definition")
    
      - <span class="sig-name descname"><span class="pre">Trigger</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">0</span>*[](#syside.TransitionFeatureKind.Trigger "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">Guard</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">1</span>*[](#syside.TransitionFeatureKind.Guard "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">Effect</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">2</span>*[](#syside.TransitionFeatureKind.Effect "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">classmethod</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">\_\_signature\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.TransitionFeatureKind.__signature__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_new\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">value</span></span>*<span class="sig-paren">)</span>[](#syside.TransitionFeatureKind.__new__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_repr\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.TransitionFeatureKind.__repr__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_str\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.TransitionFeatureKind.__str__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_dir\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.TransitionFeatureKind.__dir__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_format\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">format\_spec</span></span>*<span class="sig-paren">)</span>[](#syside.TransitionFeatureKind.__format__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_hash\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.TransitionFeatureKind.__hash__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_reduce\_ex\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">proto</span></span>*<span class="sig-paren">)</span>[](#syside.TransitionFeatureKind.__reduce_ex__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_deepcopy\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">memo</span></span>*<span class="sig-paren">)</span>[](#syside.TransitionFeatureKind.__deepcopy__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_copy\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.TransitionFeatureKind.__copy__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">name</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.TransitionFeatureKind.name "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">value</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.TransitionFeatureKind.value "Link to this definition")
