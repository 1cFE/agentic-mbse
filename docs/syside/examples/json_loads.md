<div id="json-import-labs" class="section">

# JSON Import <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">Labs</span><a href="#json-import-labs" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

This example illustrated importing SysML v2 model from a JSON file by deserializing it. The main function of interest is <a href="/python/v0.8.4/syside/json//README.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">json.loads</code></span></a>, which takes a JSON array <span class="pre">`s`</span> and a <span class="pre">`document`</span> of class <a href="/python/v0.8.4/syside/Document.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">Document</code></span></a> that the deserialized model will be stored in. The <a href="/python/v0.8.4/syside/json//README.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">json.loads</code></span></a> function returns the deserialized model which can then be used as if it was imported from a <span class="pre">`.sysml`</span> file.

<div id="concepts-used" class="section">

## Concepts Used<a href="#concepts-used" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

- A <a href="/python/v0.8.4/syside/Model.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">Model</code></span></a> is a SysMLv2 model represented using abstract syntax. This is the output of the function <a href="/python/v0.8.4/syside//README.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">load_model</code></span></a>.

- The <span class="pre">`syside.json`</span> module for serializing to SysML v2 JSON.

- <span class="pre">`walk_ownership_tree`</span> is a function that prints out elements in a model in a tree-like format. In this example it is used to show that the model has been successfully deserialized from JSON format.

</div>

<div id="example-script" class="section">

## Example Script<a href="#example-script" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

<div class="highlight-python notranslate">

<div class="highlight">

    import pathlib
    import syside

    EXAMPLE_DIR = pathlib.Path(__file__).parent
    MODEL_FILE_PATH = EXAMPLE_DIR / "example_model_3.sysml"
    # The deserialized model will be stored in a document with MODEL_PATH path.
    # The MODEL_PATH does not necessarily need to exist on the local file system.
    MODEL_PATH = "file://" + str(MODEL_FILE_PATH)


    def walk_ownership_tree(element: syside.Element, level: int = 0) -> None:
        """
        Prints out all elements in a model in a tree-like format, where
        child elements appear indented under their parent elements. For
        example:

        Parent
          Child1
          Child2
            Grandchild

        Args:
            element: The model element to start printing from
            level: How many levels to indent (increases for nested elements)
        """
        if element.name is not None:
            print("  " * level, element.name)
        else:
            print("  " * level, "anonymous element")
        # Recursively call walk_ownership_tree() for each owned element
        # (child element).
        element.owned_elements.for_each(
            lambda owned_element: walk_ownership_tree(owned_element, level + 1)
        )


    def main() -> None:
        with open("example_json.json", "r") as f:
            json_import = f.read()
        deserialized_model, _ = syside.json.loads(json_import, MODEL_PATH)

        walk_ownership_tree(deserialized_model.document.root_node)


    if __name__ == "__main__":
        main()

</div>

</div>

</div>

<div id="output" class="section">

## Output<a href="#output" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

<div class="highlight-text notranslate">

<div class="highlight">

    anonymous element
      JSON Export Example
        Electrical
        Mechanical
        Automobile
          Drive Train
          Chassis

</div>

</div>

</div>

<div id="download" class="section">

## Download<a href="#download" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

Download this example <a href="/examples/json_loads.zip" class="reference external">here</a>.

</div>

</div>
