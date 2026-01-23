<div id="extract-documentation" class="section">

# Extract Documentation[](#extract-documentation "Link to this heading")

This simple Python script uses Syside to extract information from all the doc elements present in the model and print it out in the console.

The example covers unordered iteration over elements of specific type.

<div class="admonition note">

Note

Before running this example, make sure you have activated the Syside license by running `syside-license check` according to the instructions in the [<span class="std std-ref">License Activation</span>](/v0.8.1/automator/install.md) section.

</div>

<div id="concepts-used" class="section">

## Concepts Used[](#concepts-used "Link to this heading")

  - syside.load\_model is the main function for loading the model. In the example, the parameter paths is used to specify the path to the SysMLv2 file. This parameter accepts a list of paths. load\_model also accepts parameters sysml\_source and kerml\_source that can be used to load SysMLv2 and KerML files from memory, respectively.

  - nodes method on model enables iterating over the elements of the given type. By default, it returns only the instances that match the type exactly. The behaviour can be changed to include subtypes by setting the parameter include\_subtypes to True.

  - name on element enables accessing the name of SysML element.

  - body on element enables accessing the annotation text for the comment.

</div>

<div id="interactive-version" class="section">

## Interactive version[](#interactive-version "Link to this heading")

Save the example model below to your computer and run python3 -m syside interactive path/to/downloaded/example\_model.sysml with the Syside venv activated. This drops you into an interactive Python shell that starts with a banner:

<div class="highlight-shell notranslate">

<div class="highlight">

    Welcome to isyside!
    
    This is an interactive Python shell with the loaded model accessible as `model`.
    Builtin modules:        syside
    Convenience variables:  model, diagnostics
    
    >>>

</div>

</div>

From here, you can access the model described in example\_model.sysml as model. For example

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

If a fully qualified name is needed, use qualified\_name:

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

## Example Model[](#example-model "Link to this heading")

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

## Example Script[](#example-script "Link to this heading")

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

## Output[](#output "Link to this heading")

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

## Download[](#download "Link to this heading")

Download this example [here](/v0.8.1/examples/extract_docs.zip).

</div>

</div>
