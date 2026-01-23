<div id="changes-in-practice" class="section">

<span id="syside-preview-examples"></span>

# Changes in Practice<a href="#changes-in-practice" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

Here we demonstrate how <span class="pre">`syside.preview`</span> functionalities could be used in practice. This is meant to give an idea of what was the goal behind the changes as well as show some practical applications.

<div id="loading-a-package" class="section">

## Loading a package<a href="#loading-a-package" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

The proposed changes allow for a more straightforward way of loading a package that does not involve manual locking of the document for multi-threading. It also allows for a slightly more intuitive way of checking for errors in the model by hiding the diagnostic messages.

<div class="tab-set docutils">

<span class="pre">`syside`</span>

<div class="tab-content docutils">

<div class="highlight-python notranslate">

<div class="highlight">

    import syside

    EXAMPLE_DIR = pathlib.Path(__file__).parent
    MODEL_FILE_PATH = EXAMPLE_DIR / "example_model.sysml"

    (model, diagnostics) = syside.load_model(paths=[MODEL_FILE_PATH])

    # Only errors cause an exception. Syside may also report warnings and
    # informational messages, but not for this example. As a result, manually
    # checking for warnings and informational messages is required.
    assert list(diagnostics.all) == [], "No warnings and no informational messages."

    for doc in model.user_docs:
    # Since Syside is a multi-threaded application, we need to lock the document
    # to ensure that the document is not modified from another thread while we are
    # accessing it.
        with doc.lock() as locked:
            print("Model sexp:")
            print(syside.sexp(locked.root_node))

</div>

</div>

</div>

<span class="pre">`syside.preview`</span>

<div class="tab-content docutils">

<div class="highlight-python notranslate">

<div class="highlight">

    import syside.preview as syside

    EXAMPLE_DIR = pathlib.Path(__file__).parent
    MODEL_FILE_PATH = EXAMPLE_DIR / "example_model.sysml"

    with syside.open_model(paths=[MODEL_FILE_PATH], warnings_as_errors=True) as model:
        # Either get by package name
        variant_1 = model.lookup('Car')
        # Or fetch by filename
        variant_2 = list(model.top_elements_from(EXAMPLE_DIR / "example_model.sysml"))

        # Check that both variants are the same
        assert([variant_1] == variant_2)

        print(syside.sexp(variant_1))

</div>

</div>

</div>

</div>

</div>

<div id="creating-a-package" class="section">

## Creating a package<a href="#creating-a-package" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

Currently, creating a new SysML v2 package is more complicated than it should be. The following example demonstrates how to create a new package called “Requirements” and how easier it is to do so in <span class="pre">`syside.preview`</span>.

<div class="tab-set docutils">

<span class="pre">`syside`</span>

<div class="tab-content docutils">

<div class="highlight-python notranslate">

<div class="highlight">

    import syside

    # Create an empty model (containing only standard library)
    model_document = syside.Document.create_st(
        syside.DocumentOptions(
            url=syside.Url("memory://requirements.sysml"), language="sysml"
        )
    )

    # Since Syside is a multi-threaded application, we need to lock the document
    # to ensure that the document is not modified from another thread while we are
    # accessing or modifying it.
    with model_document.lock() as model:
        # The document corresponds to a single root namespace.
        root_namespace = model.root_node

        # Add an owned requirements package to the root namespace.
        requirements_package = root_namespace.children.append(
            syside.OwningMembership, syside.Package
        )
        requirements_package.declared_name = "Requirements"

</div>

</div>

</div>

<span class="pre">`syside.preview`</span>

<div class="tab-content docutils">

<div class="highlight-python notranslate">

<div class="highlight">

    import syside.preview as syside

    # Create an empty model (containing only standard library)
    with syside.empty_model() as model:
        # Add an owned requirements package to the root namespace.
        requirements_package = model.new_top_level_package("Requirements")

</div>

</div>

</div>

</div>

</div>

</div>
