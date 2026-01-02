<div id="requirements-from-excel-spreadsheet" class="section">

# Requirements from Excel Spreadsheet[](#requirements-from-excel-spreadsheet "Link to this heading")

This simple Python script uses Syside and Pandas to load a list of requirements from an Excel file `requirements.xlsx` and store them into a SysML v2 file `requirements.sysml`.

<div class="admonition note">

Note

Before running this example, make sure you have activated the Syside license by running `syside-license check` according to the instructions in the [<span class="std std-ref">License Activation</span>](/v0.8.1/automator/install.md) section.

</div>

<div id="additional-dependencies" class="section">

## Additional Dependencies[](#additional-dependencies "Link to this heading")

This example additionally requires `pandas` and `openpyxl` Python packages that can installed using `pip`. If you are using a virtual environment, ensure that you install the packages into the same `.venv` where Syside Automator is installed.

<div class="highlight-shell notranslate">

<div class="highlight">

    pip install pandas openpyxl

</div>

</div>

</div>

<div id="concepts-used" class="section">

## Concepts Used[](#concepts-used "Link to this heading")

  - `syside.Document.create_st` is a function for creating a SysML document. The caller needs to specify the URL of the created document (we use `memory://` to indicate that the file is completely in memory) and whether the file is `sysml` or `kerml`.

  - Syside supports multithreaded access to the model. Therefore, the documents must be locked using the `lock` method before accessing them.

  - New elements can be created by adding them with `append` to the containing namespace.

  - Writing to `body` field of the documentation element updates its text.

  - Function `pprint` pretty prints an element (a concept of abstract syntax) to textual notation.

</div>

<div id="excel-file-contents" class="section">

## Excel File Contents[](#excel-file-contents "Link to this heading")

The Excel file `requirements.xlsx` has the following contents:

<div class="pst-scrollable-table-container">

| ID    | REQUIREMENT                                                                                                                                                  |
| ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| RQ-01 | The fridge shall maintain an internal temperature between 1°C and 4°C (34°F and 39°F) for food preservation.                                                 |
| RQ-02 | The freezer compartment shall maintain a temperature of -18°C (0°F) or below for long-term storage of frozen items.                                          |
| RQ-03 | The fridge shall meet or exceed Energy Star efficiency standards, consuming no more than 400 kWh per year.                                                   |
| RQ-04 | The fridge shall have an automatic defrosting system to prevent the buildup of frost inside the freezer.                                                     |
| RQ-05 | The fridge doors shall have magnetic gaskets to ensure an airtight seal and prevent energy loss.                                                             |
| RQ-06 | The operational noise of the fridge shall not exceed 40 dB(A) under normal conditions.                                                                       |
| RQ-07 | The fridge shall provide adjustable shelves to accommodate a variety of food sizes and configurations.                                                       |
| RQ-08 | The fridge shall include a digital temperature control system with an accuracy of ±1°C.                                                                      |
| RQ-09 | The fridge shall feature a humidity-controlled drawer to extend the freshness of perishable items like fruits and vegetables.                                |
| RQ-10 | The fridge shall be equipped with energy-efficient LED lighting that illuminates all compartments.                                                           |
| RQ-11 | The fridge shall have a built-in water and ice dispenser capable of dispensing both cubed and crushed ice.                                                   |
| RQ-12 | The fridge shall support Wi-Fi connectivity, enabling remote temperature monitoring and control via a mobile app.                                            |
| RQ-13 | The fridge shall include an audible alarm system to notify users if the door is left open for more than 2 minutes.                                           |
| RQ-14 | The fridge shall provide a minimum storage capacity of 20 cubic feet, including separate compartments for dairy, meat, and produce.                          |
| RQ-15 | The fridge shall include a backup battery or auxiliary power system capable of maintaining critical temperatures for at least 4 hours during a power outage. |

</div>

</div>

<div id="example-script" class="section">

## Example Script[](#example-script "Link to this heading")

<div class="highlight-python notranslate">

<div class="highlight">

    import pathlib
    import pandas as pd
    import syside
    
    EXAMPLE_DIR = pathlib.Path(__file__).parent
    REQUIREMENTS_EXCEL = EXAMPLE_DIR / "requirements.xlsx"
    REQUIREMENTS_SYSML = EXAMPLE_DIR / "requirements.sysml"
    
    
    def main() -> None:
        # Load requirements from Excel using Pandas.
        df = pd.read_excel(REQUIREMENTS_EXCEL)
    
        # Create a SysMLv2 document in memory.
        model_document = syside.Document.create_st(
            syside.DocumentOptions(
                url=syside.Url("memory://requirements.sysml"), language="sysml"
            )
        )
    
        # Since Syside is a multi-threaded application, we need to lock the
        # document to ensure that the document is not modified from another
        # thread while we are accessing or modifying it.
        with model_document.lock() as model:
            # The document corresponds to a single root namespace.
            root_namespace = model.root_node
    
            # Add an owned requirements package to the root namespace.
            requirements_package = root_namespace.children.append(
                syside.OwningMembership, syside.Package
            )[1]
            requirements_package.declared_name = "Requirements"
    
            # Create a SysML requirement for each row in Excel.
            for _, row in df.iterrows():
                req_id = row["ID"]
                req_doc = row["REQUIREMENT"]
                print(f"Creating requirement {req_id}: {req_doc}")
    
                requirement = requirements_package.children.append(
                    syside.OwningMembership, syside.RequirementDefinition
                )[1]
                requirement.declared_name = req_id
                documentation = requirement.children.append(
                    syside.OwningMembership, syside.Documentation
                )[1]
                documentation.body = req_doc
    
            # Pretty print abstract syntax to textual notation.
            printer_cfg = syside.PrinterConfig(line_width=80, tab_width=2)
            printer = syside.ModelPrinter.sysml()
            sysml_text = syside.pprint(root_namespace, printer, printer_cfg)
    
        print(f"Created SysML model:\n{sysml_text}")
    
        # Write textual notation to a file.
        with open("requirements.sysml", "w", encoding="utf-8") as fp:
            fp.write(sysml_text)
    
    
    if __name__ == "__main__":
        main()

</div>

</div>

</div>

<div id="output" class="section">

## Output[](#output "Link to this heading")

<div class="highlight-text notranslate">

<div class="highlight">

    Creating requirement RQ-01: The fridge shall maintain an internal temperature between 1°C and 4°C (34°F and 39°F) for food preservation.
    Creating requirement RQ-02: The freezer compartment shall maintain a temperature of -18°C (0°F) or below for long-term storage of frozen items.
    Creating requirement RQ-03: The fridge shall meet or exceed Energy Star efficiency standards, consuming no more than 400 kWh per year.
    Creating requirement RQ-04: The fridge shall have an automatic defrosting system to prevent the buildup of frost inside the freezer.
    Creating requirement RQ-05: The fridge doors shall have magnetic gaskets to ensure an airtight seal and prevent energy loss.
    Creating requirement RQ-06: The operational noise of the fridge shall not exceed 40 dB(A) under normal conditions.
    Creating requirement RQ-07: The fridge shall provide adjustable shelves to accommodate a variety of food sizes and configurations.
    Creating requirement RQ-08: The fridge shall include a digital temperature control system with an accuracy of ±1°C.
    Creating requirement RQ-09: The fridge shall feature a humidity-controlled drawer to extend the freshness of perishable items like fruits and vegetables.
    Creating requirement RQ-10: The fridge shall be equipped with energy-efficient LED lighting that illuminates all compartments.
    Creating requirement RQ-11: The fridge shall have a built-in water and ice dispenser capable of dispensing both cubed and crushed ice.
    Creating requirement RQ-12: The fridge shall support Wi-Fi connectivity, enabling remote temperature monitoring and control via a mobile app.
    Creating requirement RQ-13: The fridge shall include an audible alarm system to notify users if the door is left open for more than 2 minutes.
    Creating requirement RQ-14: The fridge shall provide a minimum storage capacity of 20 cubic feet, including separate compartments for dairy, meat, and produce.
    Creating requirement RQ-15: The fridge shall include a backup battery or auxiliary power system capable of maintaining critical temperatures for at least 4 hours during a power outage.
    Created SysML model:
    package Requirements {
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

<div id="download" class="section">

## Download[](#download "Link to this heading")

Download this example [here](/v0.8.1/examples/reqs_from_excel.zip).

</div>

</div>
