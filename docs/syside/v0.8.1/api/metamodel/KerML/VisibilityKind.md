<div id="visibilitykind" class="section">

<span id="metamodel-kerml-visibilitykind"></span>

# VisibilityKind[](#visibilitykind "Link to this heading")

`VisibilityKind` is defined in KerML specification on [page 161](https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=161). Excerpt from the machine readable specification:

> 
> 
> <div>
> 
> `VisibilityKind` is an enumeration whose literals specify the visibility of a `Membership` of an `Element` in a `Namespace` outside of that `Namespace`. Note that “visibility” specifically restricts whether an `Element` in a `Namespace` may be referenced by name from outside the `Namespace` and only otherwise restricts access to an `Element` as provided by specific constraints in the abstract syntax (e.g., preventing the import or inheritance of private `Elements`).
> 
> </div>

The following diagram shows the inheritance hierarchy of `VisibilityKind` according to the specification:

<div class="align-center" data-align="center">

<div class="graphviz">

![// Class: VisibilityKind digraph { VisibilityKind \[label="VisibilityKind (KerML)" shape=plaintext\] }](_images/graphviz-f0b5930604898ad2a2c34a8b7d5937d02225c891.png)

</div>

</div>

The following table shows all attributes defined for `VisibilityKind` according to the specification together with the documentation from the machine readable specification. Note that in Syside API, we use snake case for attribute names instead of Pascal case used in the specification.

<div class="pst-scrollable-table-container">

Attribute

</div>

</div>

Documentation from machine readable specification

Attributes defined in [`VisibilityKind`](#syside.VisibilityKind "syside.VisibilityKind"):

[`Private`](#syside.VisibilityKind.Private "syside.VisibilityKind.Private")

Indicates a `Membership` is not visible outside its owning `Namespace`.

[`Protected`](#syside.VisibilityKind.Protected "syside.VisibilityKind.Protected")

An intermediate level of visibility between `public` and `private`. By default, it is equivalent to `private` for the purposes of normal access to and import of `Elements` from a `Namespace`. However, other `Relationships` may be specified to include `Memberships` with `protected` visibility in the list of `memberships` for a `Namespace` (e.g., `Specialization`).

[`Public`](#syside.VisibilityKind.Public "syside.VisibilityKind.Public")

Indicates that a `Membership` is publicly visible outside its owning `Namespace`.

The following table lists Syside specific attributes available for class [`VisibilityKind`](#syside.VisibilityKind "syside.VisibilityKind"):

<div class="pst-scrollable-table-container">

|                  |
| ---------------- |
| Python Attribute |

</div>

  - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">VisibilityKind</span></span><span class="sig-paren">(</span>*<span class="o"><span class="pre">\*</span></span><span class="n"><span class="pre">args</span></span>*, *<span class="o"><span class="pre">\*\*</span></span><span class="n"><span class="pre">kwds</span></span>*<span class="sig-paren">)</span>[](#syside.VisibilityKind "Link to this definition")
    
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
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">value</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.VisibilityKind.value "Link to this definition")
