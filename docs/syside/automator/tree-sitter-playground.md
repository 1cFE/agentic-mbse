<div id="sysml-syntax-explorer" class="section">

# SysML Syntax Explorer<a href="#sysml-syntax-explorer" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

The SysML Syntax Explorer is a browser-based tool to visualize how Syside parses SysML v2 code. It displays code as an interactive concrete syntax tree (CST) structure, revealing the underlying hierarchy of declarations, expressions, and other language constructs. Use this tool to accelerate Syside Automator script development to quickly identify any elements of interest and how to parse them.

- <a href="#how-to-use-the-syntax-explorer" class="reference internal">How to Use the Syntax Explorer</a>

- <a href="#practical-examples" class="reference internal">Practical Examples</a>

<div class="admonition-privacy admonition">

Privacy

The Syntax Explorer runs entirely in your browser. No code is transmitted to any server, and nothing is logged or stored. Safe for use with proprietary models.

</div>

<div id="how-to-use-the-syntax-explorer" class="section">

## How to Use the Syntax Explorer<a href="#how-to-use-the-syntax-explorer" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

Enter or paste SysML v2 code in the <span class="guilabel">Code</span> editor panel. The syntax tree will appear immediately in the <span class="guilabel">Tree</span> panel and update in real-time as you type.

You can click any node in the tree to highlight the corresponding code, or click code in the editor to jump to its location in the tree.

Language Selection  
Use the language dropdown to switch between SysML v2 and KerML parsing modes.

Anonymous Nodes  
Enable this option to show unnamed syntax nodes in the tree. This is helpful when you need to understand the complete parse structure including implicit elements like punctuation and keywords.

Query Editor  
You can open the query editor to write tree-sitter query patterns that match specific syntax elements. Queries use tree-sitter’s S-expression syntax to select nodes by type.

For example, this query highlights all identifiers:

<div class="highlight-scheme notranslate">

<div class="highlight">

    (NAME) @module

</div>

</div>

Matched elements will be highlighted in the code editor. For more details on query syntax, see the <a href="https://tree-sitter.github.io/tree-sitter/using-parsers#pattern-matching-with-queries" class="reference external" target="_blank">tree-sitter query documentation</a>.

Accessibility  
When using queries, use this toggle to switch between color-based and marker-based highlighting for better visual distinction of matched elements.

Open in New Tab  
Opens the explorer as a standalone page for full-screen usage.

<div class="admonition note">

Note

Your current code and queries will not transfer to the new window.

</div>

</div>

<div id="practical-examples" class="section">

## Practical Examples<a href="#practical-examples" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

Copy the following code snippets into the <span class="guilabel">Code</span> window above to explore the insights described below.

<div id="extracting-model-data" class="section">

### Extracting Model Data<a href="#extracting-model-data" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

Attribute Declarations  
<div class="highlight-sysml notranslate">

<div class="highlight">

    part def Vehicle {
        attribute mass : Real;
        attribute 'max speed' : Real;
    }

</div>

</div>

The tree shows how attributes nest within definitions and how quoted names are tokenized differently from unquoted identifiers.

Expression Parsing  
<div class="highlight-sysml notranslate">

<div class="highlight">

    attribute totalCost = baseCost + quantity * unitPrice;

</div>

</div>

The tree reveals operator precedence: <span class="pre">`quantity`</span>` `<span class="pre">`*`</span>` `<span class="pre">`unitPrice`</span> groups first as a subtree before the addition operation.

Feature Chains/Navigation  
<div class="highlight-sysml notranslate">

<div class="highlight">

    attribute distance = vehicle.wheel.diameter * 3.14;

</div>

</div>

The expression <span class="pre">`vehicle.wheel.diameter`</span> creates nested levels in the tree: <span class="pre">`vehicle`</span> contains <span class="pre">`wheel`</span>, which contains <span class="pre">`diameter`</span>. Scripts analyzing these chains must traverse each level separately.

</div>

<div id="tracking-dependencies" class="section">

### Tracking Dependencies<a href="#tracking-dependencies" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

Import Statements  
The tree distinguishes wildcard imports (<span class="pre">`*`</span>) from specific element imports—useful when tracking dependencies.

<div class="highlight-sysml notranslate">

<div class="highlight">

    import ScalarValues::*;
    import VehicleLibrary::Vehicle;

</div>

</div>

Binding Connectors  
The bind keyword creates a distinct statement type with separate left/right subtrees—different from assignment expressions despite similar syntax.

<div class="highlight-sysml notranslate">

<div class="highlight">

    bind actualMass = vehicle.mass;

</div>

</div>

</div>

<div id="working-with-documentation" class="section">

### Working with Documentation<a href="#working-with-documentation" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

Comments vs Documentation  
<div class="highlight-sysml notranslate">

<div class="highlight">

    // This is a comment
    doc /* This is documentation */
    part def Example;

</div>

</div>

Line comments (<span class="pre">`//`</span>) appear as note nodes in the tree, while block comments inside doc statements parse as documentation body text attached to elements.

Metadata Attachment  
<div class="highlight-sysml notranslate">

<div class="highlight">

    #myTool::customMetadata
    part def Component {
        doc /* This is a component */
    }

</div>

</div>

The tree shows where metadata annotations attach relative to their target elements and how documentation comments are structured.

</div>

<div id="understanding-logic-constraints" class="section">

### Understanding Logic & Constraints<a href="#understanding-logic-constraints" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

Constraints and Assertions  
<div class="highlight-sysml notranslate">

<div class="highlight">

    constraint def MassLimit {
        attribute maxMass: Real;
        assert constraint { mass <= maxMass }
    }

</div>

</div>

When extracting constraint logic, the tree reveals that assert blocks nest the boolean expression several levels deep and not at the constraint definition level.

Collection Syntax  
<div class="highlight-sysml notranslate">

<div class="highlight">

    attribute values: Real[0..*] = (1.0, 2.0, 3.0);

</div>

</div>

Multiplicity bounds and collection literals appear as distinct subtrees in the parsed structure.

</div>

</div>

</div>
