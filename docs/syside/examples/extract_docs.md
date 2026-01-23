<div id="extract-documentation" class="section">

# Extract Documentation<a href="#extract-documentation" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

This simple Python script uses Syside to extract information from all the doc elements present in the model and print it out in the console.

The example covers unordered iteration over elements of specific type.

<div id="concepts-used" class="section">

## Concepts Used<a href="#concepts-used" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

- <a href="/python/v0.8.4/syside//README.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">load_model</code></span></a> is the main function for loading the model. In the example, the parameter paths is used to specify the path to the SysMLv2 file. This parameter accepts a list of paths. <a href="/python/v0.8.4/syside//README.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">load_model</code></span></a> also accepts parameters sysml_source and kerml_source that can be used to load SysMLv2 and KerML files from memory, respectively.

- <a href="/python/v0.8.4/syside/Model.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">.nodes</code></span></a> method on <a href="/python/v0.8.4/syside/Model.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">model</code></span></a> enables iterating over the elements of the given type. By default, it returns only the instances that match the type exactly. The behaviour can be changed to include subtypes by setting the parameter include_subtypes to True.

- <a href="/python/v0.8.4/syside/Element.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">.name</code></span></a> on <a href="/python/v0.8.4/syside/Element.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">element</code></span></a> enables accessing the name of SysML element.

- <a href="/python/v0.8.4/syside/Documentation.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">.body</code></span></a> on <a href="/python/v0.8.4/syside/Documentation.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">documentation</code></span></a> enables accessing the annotation text for the comment.

</div>

<div id="interactive-version" class="section">

## Interactive version<a href="#interactive-version" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

Save the example model below to your computer and run python3 -m syside interactive path/to/downloaded/example_model.sysml with the Syside venv activated. This drops you into an interactive Python shell that starts with a banner:

<div class="highlight-shell notranslate">

<div class="highlight">

    Welcome to isyside!

    This is an interactive Python shell with the loaded model accessible as `model`.
    Builtin modules:        syside
    Convenience variables:  model, diagnostics

    >>>

</div>

</div>

From here, you can access the model described in example_model.sysml as model. For example

<div class="highlight-python notranslate">

<div class="highlight">

    model.nodes(syside.Documentation)

</div>

</div>

gives an iterator over all documentation elements in the model. We can use this to create a list of all documentation elements

<div class="highlight-python notranslate">

<div class="highlight">

    >>> doc_elements = list(model.nodes(syside.Documentation))
    >>>

</div>

</div>

These elements might have names of their own

<div class="highlight-python notranslate">

<div class="highlight">

    >>> doc_elements[2].name
    'Document1'
    >>>

</div>

</div>

or may be anonymous

<div class="highlight-python notranslate">

<div class="highlight">

    >>> doc_elements[1].name
    >>>

</div>

</div>

and will typically have a body

<div class="highlight-python notranslate">

<div class="highlight">

    >>> doc_elements[0].body
    'This is documentation of the owning\npackage.'
    >>> doc_elements[1].body
    'This is documentation of Automobile alias.'
    >>> doc_elements[2].body
    'This is documentation of Automobile.'
    >>>

</div>

</div>

The text in the body concerns the element that \_owns\_ the documentation element. This \_owning\_ element can be accessed through owner

<div class="highlight-python notranslate">

<div class="highlight">

    >>> doc_elements[2].owner.name
    'Automobile'
    >>>

</div>

</div>

If a fully qualified name is needed, use qualified_name:

<div class="highlight-python notranslate">

<div class="highlight">

    >>> qn = doc_elements[2].owner.qualified_name
    >>> qn
    syside.core.QualifiedName(['Documentation Example', 'Automobile'])
    >>> str(qn)
    "'Documentation Example'::Automobile"
    >>>

</div>

</div>

</div>

<div id="example-model" class="section">

## Example Model<a href="#example-model" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

<div class="highlight-sysml notranslate">

<div class="highlight">

    package 'Documentation Example' {
      doc
      /*
       * This is documentation of the owning
       * package.
       */

      part def Automobile {
        doc Document1
        /*
         * This is documentation of Automobile.
         */
      }

      alias Car for Automobile {
        doc
        /*
         * This is documentation of Automobile alias.
         */
      }
      alias Torque for ISQ::TorqueValue;
    }

</div>

</div>

</div>

<div id="example-script" class="section">

## Example Script<a href="#example-script" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

<div class="highlight-python notranslate">

<div class="highlight">

    import pathlib
    import syside
    import syside.helpers

    EXAMPLE_DIR = pathlib.Path(__file__).parent
    MODEL_FILE_PATH = EXAMPLE_DIR / "example_model.sysml"


    def main() -> None:
        # Load the model. Model can also be loaded by giving its path as a string
        # like syside.load_model("example_model.sysml")
        # However, we recommend using this approach to ensure that the model is
        # found even when the script is run from a different directory.
        (model, diagnostics) = syside.load_model(paths=[MODEL_FILE_PATH])

        # Only errors cause an exception. Syside may also report warnings and
        # informational messages, but not for this example.
        assert not diagnostics.contains_errors(warnings_as_errors=True)

        for element in model.nodes(syside.Documentation):
            assert (
                element.owner is not None
                and element.owner.qualified_name is not None
            ), (
                "In this example, all documentation elements are owned by elements \
            with names."
            )

            # Obtain qualified name
            about = str(element.owner.qualified_name)

            # Print out to the output
            if element.name:
                print(
                    f"There is a documentation element called {element.name}, "
                    f"which is about {about}, and it says: {element.body}"
                )
            else:
                print(
                    f"There is an unnamed documentation element about {about}, "
                    f"and it says: {element.body}"
                )


    if __name__ == "__main__":
        main()

</div>

</div>

</div>

<div id="output" class="section">

## Output<a href="#output" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

<div class="highlight-text notranslate">

<div class="highlight">

    There is an unnamed documentation element about 'Documentation Example', and it says: This is documentation of the owning
    package.
    There is an unnamed documentation element about 'Documentation Example'::Car, and it says: This is documentation of Automobile alias.
    There is a documentation element called Document1, which is about 'Documentation Example'::Automobile, and it says: This is documentation of Automobile.

</div>

</div>

</div>

<div id="download" class="section">

## Download<a href="#download" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

Download this example <a href="/examples/extract_docs.zip" class="reference external">here</a>.

</div>

</div>
