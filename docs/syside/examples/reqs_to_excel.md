<div id="requirements-to-excel-spreadsheet" class="section">

# Requirements to Excel Spreadsheet<a href="#requirements-to-excel-spreadsheet" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

This simple Python script uses Syside and Pandas to load the requirements from SysML v2 file <span class="pre">`requirements.sysml`</span> and store them into an Excel file <span class="pre">`requirements.xlsx`</span>.

<div id="additional-dependencies" class="section">

## Additional Dependencies<a href="#additional-dependencies" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

This example additionally requires <span class="pre">`pandas`</span> and <span class="pre">`openpyxl`</span> Python packages that can installed using <span class="pre">`pip`</span>. If you are using a virtual environment, ensure that you install the packages into the same <span class="pre">`.venv`</span> where Syside Automator is installed.

<div class="highlight-shell notranslate">

<div class="highlight">

    pip install pandas openpyxl

</div>

</div>

</div>

<div id="example-model" class="section">

## Example Model<a href="#example-model" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

<div class="highlight-sysml notranslate">

<div class="highlight">

    package 'Requirements Example' {
      requirement def 'RQ-01' {
        doc
        /* The fridge shall maintain an internal temperature between 1°C and 4°C (34°F and 39°F) for food preservation. */
      }
      requirement def 'RQ-02' {
        doc
        /* The freezer compartment shall maintain a temperature of -18°C (0°F) or below for long-term storage of frozen items. */
      }
      requirement def 'RQ-03' {
        doc
        /* The fridge shall meet or exceed Energy Star efficiency standards, consuming no more than 400 kWh per year. */
      }
      requirement def 'RQ-04' {
        doc
        /* The fridge shall have an automatic defrosting system to prevent the buildup of frost inside the freezer. */
      }
      requirement def 'RQ-05' {
        doc
        /* The fridge doors shall have magnetic gaskets to ensure an airtight seal and prevent energy loss. */
      }
      requirement def 'RQ-06' {
        doc
        /* The operational noise of the fridge shall not exceed 40 dB(A) under normal conditions. */
      }
      requirement def 'RQ-07' {
        doc
        /* The fridge shall provide adjustable shelves to accommodate a variety of food sizes and configurations. */
      }
      requirement def 'RQ-08' {
        doc
        /* The fridge shall include a digital temperature control system with an accuracy of ±1°C. */
      }
      requirement def 'RQ-09' {
        doc
        /* The fridge shall feature a humidity-controlled drawer to extend the freshness of perishable items like fruits and vegetables. */
      }
      requirement def 'RQ-10' {
        doc
        /* The fridge shall be equipped with energy-efficient LED lighting that illuminates all compartments. */
      }
      requirement def 'RQ-11' {
        doc
        /* The fridge shall have a built-in water and ice dispenser capable of dispensing both cubed and crushed ice. */
      }
      requirement def 'RQ-12' {
        doc
        /* The fridge shall support Wi-Fi connectivity, enabling remote temperature monitoring and control via a mobile app. */
      }
      requirement def 'RQ-13' {
        doc
        /* The fridge shall include an audible alarm system to notify users if the door is left open for more than 2 minutes. */
      }
      requirement def 'RQ-14' {
        doc
        /* The fridge shall provide a minimum storage capacity of 20 cubic feet, including separate compartments for dairy, meat, and produce. */
      }
      requirement def 'RQ-15' {
        doc
        /* The fridge shall include a backup battery or auxiliary power system capable of maintaining critical temperatures for at least 4 hours during a power outage. */
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
    import pandas as pd
    import syside

    EXAMPLE_DIR = pathlib.Path(__file__).parent
    REQUIREMENTS_EXCEL = EXAMPLE_DIR / "requirements.xlsx"
    REQUIREMENTS_SYSML = EXAMPLE_DIR / "example_model.sysml"


    def main() -> None:
        # Load model.
        model, diagnostics = syside.load_model([REQUIREMENTS_SYSML])

        assert not diagnostics.contains_errors(warnings_as_errors=True)

        # Populate the data frame.
        data = []
        for requirement in model.nodes(syside.RequirementDefinition):
            for doc in requirement.documentation.collect():
                print(f"Adding requirement {requirement.declared_name}: {doc.body}")
                data.append(
                    {
                        "ID": requirement.declared_name,
                        "REQUIREMENT": doc.body,
                    }
                )
        df = pd.DataFrame(data)

        # Save the dataframe to the Excel file.
        df.to_excel(REQUIREMENTS_EXCEL, index=False)


    if __name__ == "__main__":
        main()

</div>

</div>

</div>

<div id="output" class="section">

## Output<a href="#output" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

<div class="highlight-text notranslate">

<div class="highlight">

    Adding requirement RQ-01: The fridge shall maintain an internal temperature between 1°C and 4°C (34°F and 39°F) for food preservation.
    Adding requirement RQ-02: The freezer compartment shall maintain a temperature of -18°C (0°F) or below for long-term storage of frozen items.
    Adding requirement RQ-03: The fridge shall meet or exceed Energy Star efficiency standards, consuming no more than 400 kWh per year.
    Adding requirement RQ-04: The fridge shall have an automatic defrosting system to prevent the buildup of frost inside the freezer.
    Adding requirement RQ-05: The fridge doors shall have magnetic gaskets to ensure an airtight seal and prevent energy loss.
    Adding requirement RQ-06: The operational noise of the fridge shall not exceed 40 dB(A) under normal conditions.
    Adding requirement RQ-07: The fridge shall provide adjustable shelves to accommodate a variety of food sizes and configurations.
    Adding requirement RQ-08: The fridge shall include a digital temperature control system with an accuracy of ±1°C.
    Adding requirement RQ-09: The fridge shall feature a humidity-controlled drawer to extend the freshness of perishable items like fruits and vegetables.
    Adding requirement RQ-10: The fridge shall be equipped with energy-efficient LED lighting that illuminates all compartments.
    Adding requirement RQ-11: The fridge shall have a built-in water and ice dispenser capable of dispensing both cubed and crushed ice.
    Adding requirement RQ-12: The fridge shall support Wi-Fi connectivity, enabling remote temperature monitoring and control via a mobile app.
    Adding requirement RQ-13: The fridge shall include an audible alarm system to notify users if the door is left open for more than 2 minutes.
    Adding requirement RQ-14: The fridge shall provide a minimum storage capacity of 20 cubic feet, including separate compartments for dairy, meat, and produce.
    Adding requirement RQ-15: The fridge shall include a backup battery or auxiliary power system capable of maintaining critical temperatures for at least 4 hours during a power outage.

</div>

</div>

</div>

<div id="download" class="section">

## Download<a href="#download" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

Download this example <a href="/examples/reqs_to_excel.zip" class="reference external">here</a>.

</div>

</div>
