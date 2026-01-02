<div id="extract-parts" class="section">

# Extract Parts[](#extract-parts "Link to this heading")

This simple Python script uses Syside to show:

  - the ownership tree of all elements in the model

  - part decomposition that are used in the model

  - all parts that are typed by the `Electrical` part definition

  - all parts that are typed by the `Mechanical` part definition

<div class="admonition note">

Note

Before running this example, make sure you have activated the Syside license by running `syside-license check` according to the instructions in the [<span class="std std-ref">License Activation</span>](/v0.8.1/automator/install.md) section.

</div>

<div id="concepts-used" class="section">

## Concepts Used[](#concepts-used "Link to this heading")

  - `syside.load_model` is the main function for loading the model. In the example, the parameter `paths` is used to specify the path to the SysMLv2 file. This parameter accepts a list of paths. `load_model` also accepts parameters `sysml_source` and `kerml_source` that can be used to load SysMLv2 and KerML files from memory, respectively.

  - Syside supports multithreaded access to the model. Therefore, the documents must be locked using the `lock` method before accessing them.

  - A `try_cast` is used here to assert that extracted element is of desired type.

  - A `Model` is SysMLv2 model represented using abstract syntax. This is the output of the function `load_model(<...>)`

  - A `root_node` is an entry node in the tree. It can be considered as root `Namespace`. The `Namespace` is an `Element` that contains other `Elements`, that are known as `members`.

</div>

<div id="example-model" class="section">

## Example Model[](#example-model "Link to this heading")

<div class="highlight-sysml notranslate">

<div class="highlight">

    package 'Part Tree Example' {
      part def Electrical;
      part def Mechanical;
    
      part Automobile {
        part 'Drive Train' {
          part Battery : Electrical;
          part Motor : Electrical;
        }
    
        part Chassis {
          part Suspension : Mechanical;
          part Body : Mechanical;
        }
      }
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
    
    
    def walk_ownership_tree(element: syside.Element, level: int = 0) -> None:
        """
        Prints out all elements in a model in a tree-like format, where child
        elements appear indented under their parent elements. For example:
    
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
    
    
    def show_part_decomposition(
        element: syside.Element, part_level: int = 0
    ) -> None:
        """
        Prints out a hierarchical view of parts in a model, with indentation
        showing parent-child relationships. The function calls itself repeatedly
        to handle nested parts at deeper levels.
    
        For example, if a car has an engine and wheels, it would print:
        Car
          Engine
          Wheels
    
        Args:
            element: The model element to start printing from
            part_level: How many levels of indentation to use (increases for
            nested parts)
        """
        if element.try_cast(syside.PartUsage):  # Check if element is a part usage
            print("  " * part_level, element.name)
            new_part_level = part_level + 1
        else:
            new_part_level = part_level
        # Recursively call show_part_decomposition() for each owned element
        # (child element).
        element.owned_elements.for_each(
            lambda owned_element: show_part_decomposition(
                owned_element, new_part_level
            )
        )
    
    
    def show_parts_of_type(model: syside.Model, part_type: str) -> None:
        for part in model.nodes(syside.PartUsage):
            for element in part.heritage.elements:
                if element.try_cast(syside.PartDefinition):
                    if element.declared_name == part_type:
                        print("- ", part.name)
    
    
    def main() -> None:
        (model, diagnostics) = syside.load_model([MODEL_FILE_PATH])
    
        # Only errors cause an exception. Syside may also report warnings and
        # informational messages, but not for this example.
        assert not diagnostics.contains_errors(warnings_as_errors=True)
    
        print("\nWalk the ownership tree printing all elements.")
        for doc in model.user_docs:
            # Since Syside is a multi-threaded application, we need to lock the
            # document to ensure that the document is not modified from another
            # thread while we are accessing it.
            with doc.lock() as locked:
                walk_ownership_tree(locked.root_node)
    
        print("\nShow part decomposition.")
        for doc in model.user_docs:
            with doc.lock() as locked:
                show_part_decomposition(locked.root_node)
    
        print("\nShow all electrical parts.")
        show_parts_of_type(model, "Electrical")
    
        print("\nShow all mechanical parts.")
        show_parts_of_type(model, "Mechanical")
    
    
    if __name__ == "__main__":
        main()

</div>

</div>

</div>

<div id="output" class="section">

## Output[](#output "Link to this heading")

<div class="highlight-text notranslate">

<div class="highlight">

    Walk the ownership tree printing all elements.
     anonymous element
       Part Tree Example
         Electrical
         Mechanical
         Automobile
           Drive Train
             Battery
             Motor
           Chassis
             Suspension
             Body
    
    Show part decomposition.
     Automobile
       Drive Train
         Battery
         Motor
       Chassis
         Suspension
         Body
    
    Show all electrical parts.
    -  Battery
    -  Motor
    
    Show all mechanical parts.
    -  Suspension
    -  Body

</div>

</div>

</div>

<div id="download" class="section">

## Download[](#download "Link to this heading")

Download this example [here](/v0.8.1/examples/extract_parts.zip).

</div>

</div>
