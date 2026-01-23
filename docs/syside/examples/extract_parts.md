<div id="extract-parts" class="section">

# Extract Parts<a href="#extract-parts" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

This simple Python script uses Syside to show:

- the ownership tree of all elements in the model

- part decomposition that are used in the model

- all parts that are typed by the <span class="pre">`Electrical`</span> part definition

- all parts that are typed by the <span class="pre">`Mechanical`</span> part definition

<div id="concepts-used" class="section">

## Concepts Used<a href="#concepts-used" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

- <a href="/python/v0.8.4/syside//README.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">load_model</code></span></a> is the main function for loading the model. In the example, the parameter <span class="pre">`paths`</span> is used to specify the path to the SysMLv2 file. This parameter accepts a list of paths. <a href="/python/v0.8.4/syside//README.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">load_model</code></span></a> also accepts parameters <span class="pre">`sysml_source`</span> and <span class="pre">`kerml_source`</span> that can be used to load SysMLv2 and KerML files from memory, respectively.

- Syside supports multithreaded access to the model. Therefore, the documents must be locked using the <a href="/python/v0.8.4/syside/SharedMutex.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">lock</code></span></a> method before accessing them.

- A <a href="/python/v0.8.4/syside/AstNode.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">try_cast(<span class="op">&lt;</span>...<span class="op">&gt;</span>)</code></span></a> is used here to assert that extracted element is of desired type.

- A <a href="/python/v0.8.4/syside/Model.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">Model</code></span></a> is SysMLv2 model represented using abstract syntax. This is the output of the function <a href="/python/v0.8.4/syside//README.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">load_model(<span class="op">&lt;</span>...<span class="op">&gt;</span>)</code></span></a>.

- A <a href="/python/v0.8.4/syside/Document.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">root_node</code></span></a> is an entry node in the tree. It can be considered as root <a href="/python/v0.8.4/syside/Namespace.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">Namespace</code></span></a>. The <a href="/python/v0.8.4/syside/Namespace.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">Namespace</code></span></a> is an <a href="/python/v0.8.4/syside/Element.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">Element</code></span></a> that contains other <a href="/python/v0.8.4/syside/Element.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">Elements</code></span></a>, that are known as <a href="/python/v0.8.4/syside/Namespace.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">members</code></span></a>.

</div>

<div id="example-model" class="section">

## Example Model<a href="#example-model" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

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

## Example Script<a href="#example-script" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

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

## Output<a href="#output" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

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

## Download<a href="#download" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

Download this example <a href="/examples/extract_parts.zip" class="reference external">here</a>.

</div>

</div>
