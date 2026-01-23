<div id="syside-class-names" class="section">

# Syside Class Names<a href="#syside-class-names" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

This example shows how you can use <a href="/python/v0.8.4/syside//README.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">sexp</code></span></a> function to print the symbolic expression of the document to see what elements it contains and, most importantly, names of the Syside Python classes.

<div id="example-model" class="section">

## Example Model<a href="#example-model" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

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

## Example Script<a href="#example-script" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

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

## Output<a href="#output" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

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

## Download<a href="#download" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

Download this example <a href="/examples/class_names.zip" class="reference external">here</a>.

</div>

</div>
