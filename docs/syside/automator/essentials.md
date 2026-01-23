<div id="essentials" class="section">

<span id="automator-essentials"></span>

# Essentials<a href="#essentials" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

This section provides an overview of how models are structured in Syside Automator as well first step on importing model into Python.

Basic knowledge of SysML v2 is assumed. For those unfamiliar with the language, we recommend reviewing the <a href="https://github.com/Systems-Modeling/SysML-v2-Release/blob/master/doc/Intro%20to%20the%20SysML%20v2%20Language-Textual%20Notation.pdf" class="reference external" target="_blank">SysML v2 specification</a>.

**Learn about:**

- <a href="#automator-importing" class="reference internal"><span class="std std-ref">Model Import</span></a>: First step to start with Automator

- <a href="#automator-elements-relationships" class="reference internal"><span class="std std-ref">Elements and Relationships</span></a>: Understand elements and relationships

- <a href="#automator-element-types" class="reference internal"><span class="std std-ref">Element Types</span></a>: Learn about the element types

- <a href="#automator-working-with-elements" class="reference internal"><span class="std std-ref">Working with Elements</span></a>: Basic example of reading elements

<div id="model-import" class="section">

<span id="automator-importing"></span>

## Model Import<a href="#model-import" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

Importing the model is the first step to working with it in Python.

The easiest way to import a SysML v2 model written in textual notation into Python is to use <a href="/python/v0.8.4/syside//README.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">load_model</code></span></a> function. This function returns two important objects:

1.  <a href="/python/v0.8.4/syside/Model.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">Model</code></span></a> class instance containing all information from model defined by <span class="pre">`.sysml`</span> files, including elements, relationships, and their properties. Each <span class="pre">`.sysml`</span> file becomes an instance of class <a href="/python/v0.8.4/syside/Document.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">Document</code></span></a> and is stored in <a href="/python/v0.8.4/syside/Model.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">Model.user_docs</code></span></a> attribute

2.  <a href="/python/v0.8.4/syside/Diagnostics.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">Diagnostics</code></span></a> class instance which contains any non-critical warnings that were found in the model

Example:

<div class="highlight-python notranslate">

<div class="highlight">

    import syside

    model, diagnostics = syside.load_model(["path_to_model.sysml"])

</div>

</div>

<div class="admonition note">

Note

Standard SysML v2 libraries are also imported when constructing a <a href="/python/v0.8.4/syside/Model.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">Model</code></span></a>, but they are stored in <a href="/python/v0.8.4/syside/Model.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">Model.all_docs</code></span></a> rather than <a href="/python/v0.8.4/syside/Model.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">Model.user_docs</code></span></a> since most users won’t need to access them directly.

</div>

<div class="admonition note">

Note

If the loaded model contains errors, <a href="/python/v0.8.4/syside//README.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">load_model</code></span></a> function will raise an exception. If you need to be able to load a model with errors, you can use <a href="/python/v0.8.4/syside//README.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">try_load_model</code></span></a> function instead. In that case, the <a href="/python/v0.8.4/syside/Diagnostics.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">diagnostics</code></span></a> will contain the errors and warnings found in the model.

</div>

</div>

<div id="elements-and-relationships" class="section">

<span id="automator-elements-relationships"></span>

## Elements and Relationships<a href="#elements-and-relationships" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

In SysML v2, a <a href="/python/v0.8.4/syside/Document.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">Document</code></span></a> is constructed from <a href="/python/v0.8.4/syside/Element.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">Element</code></span></a> (also known as <span class="pre">`nodes`</span>). An <a href="/python/v0.8.4/syside/Element.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">Element</code></span></a> is a uniquely identified constituent of a model that can have <a href="/python/v0.8.4/syside/Relationship.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">Relationships</code></span></a> with other <a href="/python/v0.8.4/syside/Element.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">Elements</code></span></a>.

Consider this example:

<div class="highlight-sysml notranslate">

<div class="highlight">

    part wheel{
       part wheel_rim;
       part tyre;
    }

</div>

</div>

Here, we have three unique elements: <span class="pre">`wheel`</span>, <span class="pre">`wheel_rim`</span>, and <span class="pre">`tyre`</span>. In Python, these elements are represented as objects with properties assigned via attributes, such as <a href="/python/v0.8.4/syside/Element.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">.name</code></span></a>.

Elements can be identified in several ways:

- <a href="/python/v0.8.4/syside/Element.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">.name</code></span></a> – basic element name

- <a href="/python/v0.8.4/syside/Element.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">.qualified_name</code></span></a> – includes hierarchy information

- <a href="/python/v0.8.4/syside/Element.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">.short_name</code></span></a> – SysML v2 short names, in textual notation defined between <span class="pre">`<`</span> and <span class="pre">`>`</span> characters

- <a href="/python/v0.8.4/syside/Element.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">.declared_name</code></span></a> – explicitly declared names

Note that the hierarchy is maintained through relationships. In the example, <span class="pre">`wheel`</span> owns <span class="pre">`wheel_rim`</span> and <span class="pre">`tyre`</span>, representing that the wheel is composed of these parts.

<div class="admonition tip">

Tip

For deeper exploration of <a href="/python/v0.8.4/syside/Element.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">Element</code></span></a> and other <span class="pre">`nodes`</span>:

- Refer to the SysML v2 Language Specification Document

- Use a Python debugger (e.g., through Visual Studio Code)

- Utilize <a href="/python/v0.8.4/syside//README.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">sexp</code></span></a> to explore model nodes

</div>

</div>

<div id="element-types" class="section">

<span id="automator-element-types"></span>

## Element Types<a href="#element-types" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

Elements can be of different types and have hierarchical relationships. For example:

<div class="highlight-sysml notranslate">

<div class="highlight">

    part wheel{
       attribute mass;
       action rotate;
    }

</div>

</div>

In this case:

- <span class="pre">`wheel`</span> is a <a href="/python/v0.8.4/syside/PartUsage.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">PartUsage</code></span></a>

- <span class="pre">`mass`</span> is a <a href="/python/v0.8.4/syside/AttributeUsage.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">AttributeUsage</code></span></a>

- <span class="pre">`rotate`</span> is a <a href="/python/v0.8.4/syside/ActionUsage.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">ActionUsage</code></span></a>

</div>

<div id="working-with-elements" class="section">

<span id="automator-working-with-elements"></span>

## Working with Elements<a href="#working-with-elements" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

Let’s explore how to work with elements using a basic example.

**Example Model**: copy this model into your <span class="pre">`.sysml`</span> file locally.

<div class="highlight-sysml notranslate">

<div class="highlight">

    part wheel{
       part wheel_rim{
           part metal;
           attribute diameter;
           attribute mass = 5;
       }
       part tyre{
           part rubber;
           attribute diameter;
           attribute mass = 10;
       }
       attribute mass = wheel_rim.mass + tyre.mass;
    }

</div>

</div>

<div id="accessing-elements" class="section">

### Accessing Elements<a href="#accessing-elements" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

To iterate over elements of a specific type, adjust the path and the name of the model, and run the code:

<div class="highlight-py notranslate">

<div class="highlight">

    import syside

    model, diagnostics = syside.load_model(["path_to_model.sysml"])

    for element in model.elements(syside.PartUsage):
        print(element.name)

</div>

</div>

Executing the code above will print the following:

<div class="highlight-text notranslate">

<div class="highlight">

    wheel
    wheel_rim
    tyre
    metal
    rubber

</div>

</div>

</div>

<div id="navigating-hierarchy" class="section">

### Navigating Hierarchy<a href="#navigating-hierarchy" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

To access elements owned by a specific part (e.g. <span class="pre">`tyre`</span>), replace the <span class="pre">`for`</span> loop with:

<div class="highlight-py notranslate">

<div class="highlight">

    for element in model.nodes(syside.PartUsage):
        if element.name == "tyre":
            for owned_element in element.owned_elements.collect():
                print(owned_element.name)

</div>

</div>

Executing the code above will print the following:

<div class="highlight-text notranslate">

<div class="highlight">

    rubber
    diameter
    mass

</div>

</div>

------------------------------------------------------------------------

Similarly, we can move ‘up’ the hierarchy using <a href="/python/v0.8.4/syside/Element.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">.owner</code></span></a> attributes instead of <a href="/python/v0.8.4/syside/Element.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">.owned_elements</code></span></a>:

<div class="highlight-py notranslate">

<div class="highlight">

    for element in model.nodes(syside.PartUsage):
        if element.name == "tyre" and element.owner is not None:
            print(element.owner.name)

</div>

</div>

Executing the code above will print the following:

<div class="highlight-text notranslate">

<div class="highlight">

    wheel

</div>

</div>

</div>

<div id="working-with-values" class="section">

### Working with Values<a href="#working-with-values" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

When assigning something to an <a href="/python/v0.8.4/syside/Element.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">Element</code></span></a>, the structure will depend on what data type was assigned. The most general way of dealing with this is to use the <a href="/python/v0.8.4/syside/Compiler.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">Compiler</code></span></a> to evaluate the expression that was assigned to element:

<div class="highlight-py notranslate">

<div class="highlight">

    for attr_element in model.nodes(syside.AttributeUsage):
        if attr_element.name == "mass":
            expression = attr_element.feature_value_expression
            assert expression is not None
            evaluation = syside.Compiler().evaluate(expression)
            if evaluation[1].fatal:
                print(f"Error evaluating {attr_element.name}")
            else:
                value = evaluation[0]
            assert attr_element.owner is not None
            print(f"Mass of {attr_element.owner.name} = {value}")

</div>

</div>

Note that <a href="/python/v0.8.4/syside/Compiler.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">Compiler.evaluate</code></span></a> returns a tuple with two elements: the first is the evaluation result, and the second is the evaluation report. It is good practice to check if the evaluation succeeded before using the result. Executing the code above will print the following:

<div class="highlight-text notranslate">

<div class="highlight">

    Mass of wheel = 15
    Mass of wheel_rim = 5
    Mass of tyre = 10

</div>

</div>

<div class="admonition note">

Note

The <a href="/python/v0.8.4/syside/Compiler.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">Compiler</code></span></a> is the most general way of dealing with expression evaluation, since the output is dependent on the expression – in above example it returned a number, but in the case of <span class="pre">`item`</span>` `<span class="pre">`driver`</span>` `<span class="pre">`=`</span>` `<span class="pre">`John`</span> it would return the <a href="/python/v0.8.4/syside/ReferenceUsage.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">ReferenceUsage</code></span></a> instance of <span class="pre">`John`</span>. At the moment, <a href="/python/v0.8.4/syside/Compiler.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">Compiler</code></span></a> supports evaluation of *model level evaluable* expressions, as defined in the specification.

</div>

</div>

</div>

<div id="next-steps" class="section">

## Next Steps<a href="#next-steps" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

Now that you understand the basics of Syside Automator’s model structure, you can proceed to the <a href="/automator/first_example.md" class="reference internal"><span class="std std-ref">First Example</span></a> section for hands-on example.

</div>

</div>
