<div id="syside-class-names" class="section">

# Syside Class Names[](#syside-class-names "Link to this heading")

This example shows how you can use `syside.sexp` function to print the symbolic expression of the document to see what elements it contains and, most importantly, names of the Syside Python classes.

<div class="admonition note">

Note

Before running this example, make sure you have activated the Syside license by running `syside-license check` according to the instructions in the [<span class="std std-ref">License Activation</span>](/v0.8.1/automator/install.md) section.

</div>

<div id="example-model" class="section">

## Example Model[](#example-model "Link to this heading")

<div class="highlight-sysml notranslate">

<div class="highlight">

    package Car {
      part def Wheel {
        doc /* This is a wheel*/
      }
      part wheels: Wheel[4] ordered;
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
    
    EXAMPLE_DIR = pathlib.Path(__file__).parent
    MODEL_FILE_PATH = EXAMPLE_DIR / "example_model.sysml"
    
    
    def main() -> None:
        (
            model,
            diagnostics,
        ) = syside.load_model(paths=[MODEL_FILE_PATH])
    
        # Only errors cause an exception. Syside may also report warnings and
        # informational messages, but not for this example.
        assert not diagnostics.contains_errors(warnings_as_errors=True)
    
        for doc in model.user_docs:
            # Since Syside is a multi-threaded application, we need to lock the
            # document to ensure that the document is not modified from another
            # thread while we are accessing it.
            with doc.lock() as locked:
                print("Model sexp:")
                print(syside.sexp(locked.root_node))
    
    
    if __name__ == "__main__":
        main()

</div>

</div>

</div>

<div id="output" class="section">

## Output[](#output "Link to this heading")

<div class="highlight-text notranslate">

<div class="highlight">

    Model sexp:
    (Namespace
      (OwningMembership
        (Package Car
          (OwningMembership
            (PartDefinition Wheel
              (Subclassification)
              (OwningMembership
                (Documentation))))
          (OwningMembership
            (PartUsage wheels
              (OwningMembership
                (MultiplicityRange
                  (Subsetting)
                  (OwningMembership
                    (LiteralInteger
                      (Subsetting)))))
              (FeatureTyping)
              (Subsetting))))))

</div>

</div>

</div>

<div id="download" class="section">

## Download[](#download "Link to this heading")

Download this example [here](/v0.8.1/examples/class_names.zip).

</div>

</div>
