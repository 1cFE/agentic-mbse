<div id="value-rollup-with-unit-conversion-labs" class="section">

# Value Rollup with Unit Conversion <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">Labs</span><a href="#value-rollup-with-unit-conversion-labs" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

<div class="caution admonition">

Experimental feature

This example uses experimental unit conversion functionality. Enable with <span class="pre">`experimental_quantities=True`</span>.

</div>

This example demonstrates recursive value aggregation with automatic unit conversion using <span class="pre">`Compiler.evaluate_feature()`</span>. It showcases two rollup scenarios:

1.  **Mass Rollup** - Aggregating mass from vehicle components

2.  **Power Rollup** - Calculating total power consumption for an aircraft

Both examples use the subsetting pattern where child components declare membership using <span class="pre">`subsets`</span> relationships, and the Python API builds explicit lists to enable expression evaluation. It is worth noting that subsetting pattern could lead to multiple possible values.

<div class="note admonition">

Ambiguous subset definition example

A vehicle electrical system has a main bus and an emergency bus (subset of main). Emergency loads (fuelPump 8A) subset emergencyBus.loads. Regular loads (headlights 10A) subset mainBus.loads.

When calculating mainBus.totalCurrent, there is ambiguity on how the emergency loads should be included. Since emergencyBus subsets mainBus, the answer could be: - 10A (only explicit mainBus loads) - 18A (mainBus loads + emergency loads, transitively)

Both interpretations are valid. However, undersizing a battery based on 10A would lead to system failure.

<div class="highlight-sysml notranslate">

<div class="highlight">

    part vehicle {
        part mainBus : ElectricalBus;
        part emergencyBus : ElectricalBus subsets mainBus;

        part fuelPump : ElectricalLoad subsets emergencyBus.loads { current = 8A }
        part headlights : ElectricalLoad subsets mainBus.loads { current = 10A }

        // mainBus.totalCurrent = 10A or 18A?
        // Need explicit: mainBus.loads = (fuelPump, headlights)
    }

</div>

</div>

</div>

<div id="mass-rollup-example" class="section">

## Mass Rollup Example<a href="#mass-rollup-example" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

The vehicle mass rollup calculates total mass by aggregating values from nested components, each specifying mass in different units (kg, tonne, g):

<div class="highlight-text notranslate">

<div class="highlight">

    vehicle
    ├── chassis (100 kg)
    │   ├── drivetrain (1 tonne)
    │   └── suspension (200 kg)
    └── engine (500000 g)

</div>

</div>

</div>

<div id="power-rollup-example" class="section">

## Power Rollup Example<a href="#power-rollup-example" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

The aircraft power rollup calculates total power consumption from powered subsystems, demonstrating selective aggregation where only powered components (those subsetting <span class="pre">`poweredSubsystems`</span>) contribute to the total:

<div class="highlight-text notranslate">

<div class="highlight">

    aircraft (20 W)
    ├── avionics (15 W)
    │   ├── navigationSystem (10 W)
    │   │   ├── gps (5 W)
    │   │   ├── imu (300 mW)
    │   │   ├── altimeter (100 mW)
    │   │   └── magnetometer (80 mW)
    │   ├── radar (120 W)
    │   └── autopilot (35 W)
    └── propulsion (1.2 kW)

</div>

</div>

Note that structural components like wings or fuselage would not contribute to power consumption, as they don’t subset <span class="pre">`poweredSubsystems`</span>.

</div>

<div id="building-explicit-subset-lists" class="section">

## Building Explicit Subset Lists<a href="#building-explicit-subset-lists" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

The subsetting pattern (<span class="pre">`part`</span>` `<span class="pre">`chassis`</span>` `<span class="pre">`subsets`</span>` `<span class="pre">`subcomponents`</span>) requires explicit lists for expression evaluation. The example includes a helper function that programmatically builds these lists:

<div class="highlight-python notranslate">

<div class="highlight">

    build_explicit_subset_list(
        element=root_element,
        part_def=rollup_type,
        subsetting_collection=subparts_collection,
    )

</div>

</div>

This converts implicit subsetting relationships into explicit comma-separated lists in memory, enabling the rollup expressions to evaluate correctly.

<div class="admonition note">

Note

Explicit subset lists are needed because SysML v2 specification defines subsetting as a relationship between collections, not a specification of which elements belong to each subset. Without explicit membership, value calculations cannot determine which elements to aggregate.

</div>

</div>

<div id="evaluating-with-unit-conversion" class="section">

## Evaluating with Unit Conversion<a href="#evaluating-with-unit-conversion" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

The rollup expressions are evaluated using:

<div class="highlight-python notranslate">

<div class="highlight">

    compiler = syside.Compiler()
    value, report = compiler.evaluate_feature(
        feature=rollup_attribute,  # Attribute to calculate
        scope=root_element,  # Evaluate in context of this part
        stdlib=model.environment.lib,  # Standard library for evaluation
        experimental_quantities=True,  # Enable automatic unit conversion
    )

</div>

</div>

The compiler converts all units to SI base units and returns scalar values:

- **Mass rollup**: <span class="pre">`1800.0`</span> (kg)

- **Power rollup**: <span class="pre">`1405.48`</span> (W)

</div>

<div id="example-model" class="section">

## Example Model<a href="#example-model" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

<div class="highlight-sysml notranslate">

<div class="highlight">

    package VehicleMassRollup {
      private import ScalarValues::*;
      private import NumericalFunctions::*;
      private import SI::*;

      part def MassedThing {
        part subcomponents : MassedThing [*] default null;

        attribute ownMass : MassValue default 0 [kg];
        attribute totalMass : MassValue  = ownMass + sum(subcomponents.totalMass);
      }

      part vehicle : MassedThing {
        // Explicit definition of subsetted parts
        part redefines subcomponents = (chassis, engine);

        part chassis subsets subcomponents {
          attribute redefines ownMass = 100 [kg];

          // part redefines subpart = (drivetrain, suspension);

          part drivetrain subsets subcomponents {
            attribute redefines ownMass = 1 [tonne];
          }

          part suspension subsets subcomponents {
            attribute redefines ownMass = 200 [kg];
          }
        }

        part engine subsets subcomponents {
          attribute redefines ownMass = 500000 [g];
        }
      }
    }

    package AircraftPowerRollup {
      private import ScalarValues::*;
      private import NumericalFunctions::sum;
      private import SI::*;

      part def PoweredComponent {
        part poweredSubsystems : PoweredComponent [*] default null;

        attribute power : PowerValue default 0 [W];
        attribute totalPower : PowerValue = power + sum(poweredSubsystems.totalPower);
      }

      part def CompositeSubsystem specializes PoweredComponent {
        part flightComputer : PoweredComponent {
          attribute redefines power = 25 [W];
        }
        part navigationSystem : PoweredComponent {
          attribute redefines power = 10 [W];

          part gps : PoweredComponent subsets poweredSubsystems {
            attribute redefines power = 5 [W];
          }

          part imu : PoweredComponent subsets poweredSubsystems {
            attribute redefines power = 300 [milli * W];
          }

          part altimeter : PoweredComponent subsets poweredSubsystems {
            attribute redefines power = 100 [milli * W];
          }

          part magnetometer : PoweredComponent subsets poweredSubsystems {
            attribute redefines power = 80 [milli * W];
          }
        }
      }

      part aircraft : PoweredComponent {
        attribute redefines power = 20 [W];

        part avionics : CompositeSubsystem subsets poweredSubsystems {
          attribute redefines power = 15 [W];
          part redefines navigationSystem subsets poweredSubsystems;

          part radar subsets poweredSubsystems {
            attribute redefines power = 120 [W];
          }

          part autopilot subsets poweredSubsystems {
            attribute redefines power = 35 [W];
          }
        }

        part propulsion subsets poweredSubsystems {
          attribute redefines power = 1.2 [kW];
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


    def build_explicit_subset_list(
        element: syside.PartUsage,
        part_def: syside.PartDefinition,
        subsetting_collection: syside.PartUsage,
    ) -> None:
        """
        Recursively builds explicit subset lists for parts using the subsetting pattern.

        Creates an in-memory explicit list from subsetting relationships:
            part <element> subsets <subsetting_collection> { ... }
        becomes:
            part redefines <subsetting_collection> = (<element>, ...)

        Args:
            element: SysML element to process
            part_def: Part definition type to match when filtering
            subsetting_collection: The feature being subsetted
        """

        if (
            part_def not in element.part_definitions.collect()
            or element.name == subsetting_collection.name
        ):
            return

        build_list = True

        # Check if subsetting part has been explicitly redefined with a value
        collection_name = subsetting_collection.name
        if collection_name is not None:
            subpart_usage = element.get_member(collection_name)
            if subpart_usage is not None and hasattr(
                subpart_usage, "feature_value_expression"
            ):
                compiler = syside.Compiler()
                subpart_value, _ = compiler.evaluate(
                    subpart_usage.feature_value_expression
                )
                if subpart_value is not None:
                    build_list = False

        # Build list if subpart value is not defined
        if build_list:
            list_items = [
                x
                for x in element.members.collect()
                if isinstance(x, syside.PartUsage)
                and subsetting_collection
                in [
                    y.subsetted_feature
                    for y in x.heritage.relationships
                    if type(y) is syside.Subsetting
                ]
            ]

            # Only create the explicit list if we found subsetting parts
            if len(list_items) > 0:
                # Create a new redefinition of subsetting_collection
                _, subpart = element.children.append(
                    syside.FeatureMembership, syside.PartUsage
                )
                subpart.heritage.append(syside.Redefinition, subsetting_collection)

                # Create a comma-separated list expression
                _, operator_exp = subpart.feature_value_member.set_member_element(
                    syside.OperatorExpression
                )

                operator_exp.try_set_operator(syside.ExplicitOperator.Comma)

                # Add each part that subsets the collection to the list
                for item in list_items:
                    _, expr = operator_exp.arguments.append(
                        syside.FeatureReferenceExpression
                    )
                    expr.referent_member.set_member_element(item)

        # Recursively process all child parts
        for child in element.members.collect():
            if type(child) is syside.PartUsage:
                build_explicit_subset_list(child, part_def, subsetting_collection)


    def rollup_values(
        document: syside.Document,
        stdlib: syside.Stdlib,
        package_name: str,
        rollup_part_def: str,
        subparts_collection_name: str,
        rollup_attribute_name: str,
        root_element_name: str,
    ) -> syside.Value | None:
        try:
            package = document.root_node[package_name].cast(syside.Package)
            rollup_type = package[rollup_part_def].cast(syside.PartDefinition)
            subparts_collection = rollup_type[subparts_collection_name].cast(
                syside.PartUsage
            )
            rollup_attribute = rollup_type[rollup_attribute_name].cast(
                syside.Feature
            )
            root_element = package[root_element_name].cast(syside.PartUsage)
        except KeyError as err:
            print(
                f"At least one of the required elements do not exist in the {package_name} definitions: {err}"
            )
            exit(1)

        # Build explicit subset lists for all parts that use the subsetting pattern
        build_explicit_subset_list(
            element=root_element,
            part_def=rollup_type,
            subsetting_collection=subparts_collection,
        )

        # Evaluate the expression with automatic unit conversion
        compiler = syside.Compiler()
        value, report = compiler.evaluate_feature(
            feature=rollup_attribute,
            scope=root_element,
            stdlib=stdlib,
            experimental_quantities=True,  # Enables automatic unit conversion
        )

        if report.fatal:
            print(report.diagnostics)
            exit(1)

        return value


    def main() -> None:
        model, _ = syside.load_model(paths=[MODEL_FILE_PATH])

        with model.user_docs[0].lock() as locked:
            mass_rollup_result = rollup_values(
                document=locked,
                stdlib=model.environment.lib,
                package_name="VehicleMassRollup",
                rollup_part_def="MassedThing",
                subparts_collection_name="subcomponents",
                rollup_attribute_name="totalMass",
                root_element_name="vehicle",
            )
            # Evaluates to 1,800.00 kg
            print(f"Calculated total mass: {mass_rollup_result:,.2f} kg")

            power_rollup_result = rollup_values(
                document=locked,
                stdlib=model.environment.lib,
                package_name="AircraftPowerRollup",
                rollup_part_def="PoweredComponent",
                subparts_collection_name="poweredSubsystems",
                rollup_attribute_name="totalPower",
                root_element_name="aircraft",
            )
            # Evaluates to 1,405.48 W
            print(f"Calculated total power: {power_rollup_result:,.2f} W")


    if __name__ == "__main__":
        main()

</div>

</div>

</div>

<div id="output" class="section">

## Output<a href="#output" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

<div class="highlight-text notranslate">

<div class="highlight">

    Calculated total mass: 1,800.00 kg
    Calculated total power: 1,405.48 W

</div>

</div>

</div>

<div id="download" class="section">

## Download<a href="#download" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

Download this example <a href="/examples/unit_evaluation.zip" class="reference external">here</a>.

</div>

</div>
