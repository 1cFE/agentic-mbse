<div id="first-example" class="section">

<span id="automator-first-example"></span>

# First Example<a href="#first-example" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

This guide provides a practical introduction to Syside Automator through a hands-on example.

You’ll learn how to load and validate SysML v2 models, extract and analyze model elements, and modify models programmatically.

<div id="getting-started" class="section">

## Getting Started<a href="#getting-started" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

Let’s begin by creating a simple SysML v2 model that we’ll use throughout this example. This model represents a basic automobile structure with electrical and mechanical components.

Create a new file named <span class="pre">`example_model.sysml`</span> and paste the following model:

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

<div id="model-validation" class="section">

## Model Validation<a href="#model-validation" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

Before working with the model, it’s important to validate it. To validate your model, open a terminal in the directory containing your model and run:

<div class="highlight-bash notranslate">

<div class="highlight">

    python -m syside check example_model.sysml

</div>

</div>

This command will check for any semantic errors or warnings in your model. After running, you should see the following output:

<div class="highlight-bash notranslate">

<div class="highlight">

    Checks passed!

</div>

</div>

<div class="admonition note">

Note

More about interactive Syside Automator usage can be found in the <a href="/automator/interactive.md" class="reference internal"><span class="std std-ref">Interactive Version</span></a> section.

</div>

</div>

<div id="basic-model-analysis" class="section">

## Basic Model Analysis<a href="#basic-model-analysis" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

Let’s create a Python script to analyze our model. We’ll start by creating a simple script that prints all elements in a tree-like structure.

Create a new file right next to the <span class="pre">`example_model.sysml`</span> file named <span class="pre">`analyze_model.py`</span> with the following code:

<div class="highlight-py notranslate">

<div class="highlight">

    import syside

    # Load the model - this is the first step for any Syside Automator script
    (model, diagnostics) = syside.load_model(["example_model.sysml"])


    def walk_ownership_tree(element: syside.Element, level: int = 0) -> None:
        """Recursively print all elements in the model."""
        if element.name is not None:
            print("  " * level, element.name)
        else:
            print("  " * level, "anonymous element")
        # Recursive walk through child elements
        for child in element.owned_elements.collect():
            walk_ownership_tree(child, level + 1)


    # Process each document in the model
    for document_resource in model.documents:
        with document_resource.lock() as document:
            print("Walking the ownership tree printing all elements:")
            walk_ownership_tree(document.root_node)

</div>

</div>

Run the script by running the following command in the terminal:

<div class="highlight-bash notranslate">

<div class="highlight">

    python analyze_model.py

</div>

</div>

When you run this script, you’ll see the following output:

<div class="highlight-text notranslate">

<div class="highlight">

    Walking the ownership tree printing all elements:
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

</div>

</div>

</div>

<div id="working-with-part-types" class="section">

## Working with Part Types<a href="#working-with-part-types" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

Our model defines two types of parts: <span class="pre">`Electrical`</span> and <span class="pre">`Mechanical`</span>. Let’s enhance our script to identify and display parts by their type.

Add the following function to your script right after the <span class="pre">`walk_ownership_tree`</span> function:

<div class="highlight-py notranslate">

<div class="highlight">

    def show_parts_of_type(model: syside.Model, part_type: str) -> None:
        """Display all parts of a specific type in the model."""
        for part in model.nodes(syside.PartUsage):
            for element in part.heritage.elements:
                if element.try_cast(syside.PartDefinition):
                    if element.declared_name == part_type:
                        print("- ", part.name)


    print("\nElectrical parts in the model:")
    show_parts_of_type(model, "Electrical")

    print("\nMechanical parts in the model:")
    show_parts_of_type(model, "Mechanical")

</div>

</div>

This will output:

<div class="highlight-text notranslate">

<div class="highlight">

    Electrical parts in the model:
    -  Battery
    -  Motor

    Mechanical parts in the model:
    -  Suspension
    -  Body

</div>

</div>

</div>

<div id="enhancing-the-model" class="section">

## Enhancing the Model<a href="#enhancing-the-model" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

Let’s make our model more realistic by adding a mass requirement. We’ll modify the model to include mass attributes for each part and add a requirement that the total mass must not exceed 500 kg.

Update your <span class="pre">`example_model.sysml`</span> file with this enhanced version:

<div class="highlight-sysml notranslate">

<div class="highlight">

    package 'Part Tree Example' {
        private import ScalarValues;
        part def Electrical {
            attribute Mass;
        }
        part def Mechanical {
            attribute Mass;
        }

        part Automobile {
            part 'Drive Train' {
                part Battery : Electrical {
                    attribute redefines Mass = 150;
                }
                part Motor : Electrical {
                    attribute redefines Mass = 200;
                }
                attribute DriveTrainMass = Battery.Mass + Motor.Mass;
            }
            part Chassis {
                part Suspension : Mechanical {
                    attribute redefines Mass = 100;
                }
                part Body : Mechanical {
                    attribute redefines Mass = 150;
                }
                attribute ChassisMass = Suspension.Mass + Body.Mass;
            }
            attribute TotalMass = 'Drive Train'.DriveTrainMass + 'Chassis'.ChassisMass;
        }

        requirement def MassLimitation {
            doc /* Total mass of the Automobile must not
                exceed 500 */
            attribute MassActual = Automobile.TotalMass;
            attribute MassLimit = 500;
        }
    }

</div>

</div>

</div>

<div id="validating-requirements" class="section">

## Validating Requirements<a href="#validating-requirements" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

Now let’s create a script to validate our mass requirement. Add the following code to your Python script:

<div class="highlight-py notranslate">

<div class="highlight">

    def show_part_decomposition(
        element: syside.Element, part_level: int = 0
    ) -> None:
        """Display a clean part decomposition tree."""
        if element.try_cast(syside.PartUsage):
            print("  " * part_level, element.name)
            new_part_level = part_level + 1
        else:
            new_part_level = part_level
        for child in element.owned_elements.collect():
            show_part_decomposition(child, new_part_level)


    # Find total mass and mass requirement:
    for attribute in model.nodes(syside.AttributeUsage):
        if attribute.name == "MassActual":
            assert attribute.feature_value_expression is not None
            evaluation = syside.Compiler().evaluate(
                attribute.feature_value_expression
            )
            if evaluation[1].fatal:
                print(f"Error evaluating {attribute.name}")
            else:
                total_mass = evaluation[0]
        if attribute.name == "MassLimit":
            assert attribute.feature_value_expression is not None
            evaluation = syside.Compiler().evaluate(
                attribute.feature_value_expression
            )
            if evaluation[1].fatal:
                print(f"Error evaluating {attribute.name}")
            else:
                mass_limit = evaluation[0]

    # Display results
    print("\nPart decomposition:")
    for doc in model.user_docs:
        with doc.lock() as locked:
            show_part_decomposition(locked.root_node)

    print(f"\nTotal mass: {total_mass} kg")
    if isinstance(total_mass, (int, float)) and isinstance(
        mass_limit, (int, float)
    ):
        if total_mass <= mass_limit:
            print("✓ Mass requirement met")
        else:
            print("✗ Mass requirement not met")
    else:
        print("✗ Cannot compare mass values - invalid types")

</div>

</div>

When you run this script, you’ll see:

<div class="highlight-text notranslate">

<div class="highlight">

    Part decomposition:
    Automobile
      Drive Train
        Battery
        Motor
      Chassis
        Suspension
        Body

    Total mass: 600 kg
    ✗ Mass requirement not met

</div>

</div>

</div>

<div id="summary" class="section">

## Summary<a href="#summary" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

In this example, we’ve learned how to:

1.  Create and validate a SysML v2 model

2.  Load and analyze models using Syside Automator

3.  Extract and display model elements

4.  Work with part types and hierarchies

5.  Add attributes and requirements to models

6.  Validate requirements programmatically

The example demonstrates that our automobile design exceeds the mass requirement by 100 kg. To meet the requirement, you would need to reduce the mass of some components or redesign the system.

</div>

<div id="next-steps" class="section">

## Next Steps<a href="#next-steps" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

- Try modifying the mass values to meet the requirement

- Check out the <a href="/examples//README.md" class="reference internal"><span class="std std-ref">Examples Collection</span></a> section for more Automator applications

</div>

</div>
