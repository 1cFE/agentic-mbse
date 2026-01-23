<div id="json-import" class="section">

# JSON Import[](#json-import "Link to this heading")

This example illustrated importing SysML v2 model from a JSON file by deserializing it. The main function of interest is [`syside.json.loads`](/v0.8.1/api/generated/syside.json.loads.md "syside.json.loads"), which takes a JSON array `s` and a `document` of class [`Document`](/v0.8.1/api/generated/syside.Document.md "syside.Document") that the deserialized model will be stored in. The [`syside.json.loads`](/v0.8.1/api/generated/syside.json.loads.md "syside.json.loads") function returns the deserialized model which can then be used as if it was imported from a `.sysml` file.

<div class="admonition note">

Note

Before running this example, make sure you have activated the Syside license by running `syside-license check` according to the instructions in the [<span class="std std-ref">License Activation</span>](/v0.8.1/automator/install.md) section.

</div>

<div id="concepts-used" class="section">

## Concepts Used[](#concepts-used "Link to this heading")

  - A [`Model`](/v0.8.1/api/generated/syside.Model.md "syside.Model") is a SysMLv2 model represented using abstract syntax. This is the output of the function [`syside.load_model`](/v0.8.1/api/generated/syside.load_model.md "syside.load_model").

  - The `syside.json` module for serializing to SysML v2 JSON.

  - `walk_ownership_tree` is a function that prints out elements in a model in a tree-like format. In this example it is used to show that the model has been successfully deserialized from JSON format.

</div>

<div id="example-script" class="section">

## Example Script[](#example-script "Link to this heading")

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

## Output[](#output "Link to this heading")

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

## Download[](#download "Link to this heading")

Download this example [here](/v0.8.1/examples/json_loads.zip).

</div>

</div>
