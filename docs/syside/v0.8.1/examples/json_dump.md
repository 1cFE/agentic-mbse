<div id="json-export" class="section">

# JSON Export[](#json-export "Link to this heading")

This example illustrates exporting the root namespace loaded from a file to the SysML v2 JSON serialization format. The main function of interest is `syside.json.dumps`, which takes an `Element` and generates a string representation of a SysML v2 JSON serialization. The serialization includes the element and (recursively) all its owned members. Typically, as in this example, you would serialize the root namespace of a loaded document.

<div class="admonition note">

Note

Before running this example, make sure you have activated the Syside license by running `syside-license check` according to the instructions in the [<span class="std std-ref">License Activation</span>](/v0.8.1/automator/install.md) section.

</div>

<div id="example-model" class="section">

## Example Model[](#example-model "Link to this heading")

<div class="highlight-sysml notranslate">

<div class="highlight">

    package 'JSON Export Example' {
      part def Electrical;
      part def Mechanical;
    
      part Automobile {
        part 'Drive Train' : Electrical;
        part Chassis : Mechanical;
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
    
    
    def main() -> None:
        (model, diagnostics) = syside.try_load_model([MODEL_FILE_PATH])
    
        # Only errors cause an exception. Syside may also report warnings and
        # informational messages, but not for this example.
        assert not diagnostics.contains_errors(warnings_as_errors=True)
    
        # Export the model to JSON
        assert len(model.user_docs) == 1
    
        with model.user_docs[0].lock() as locked:
            print(
                syside.json.dumps(
                    locked.root_node, syside.SerializationOptions.minimal()
                )
            )
    
    
    if __name__ == "__main__":
        main()

</div>

</div>

</div>

<div id="output" class="section">

## Output[](#output "Link to this heading")

<div class="highlight-text notranslate">

<div class="highlight">

    [
      {
        "@type": "Namespace",
        "@id": "152f4f90-24ad-43f0-9fc0-c58eccf681c5",
        "elementId": "152f4f90-24ad-43f0-9fc0-c58eccf681c5",
        "ownedRelationship": [
          { "@id": "0a680cbf-b149-5715-8acd-2ce5ab495768" }
        ]
      },
      {
        "@type": "OwningMembership",
        "@id": "0a680cbf-b149-5715-8acd-2ce5ab495768",
        "elementId": "0a680cbf-b149-5715-8acd-2ce5ab495768",
        "owningRelatedElement": { "@id": "152f4f90-24ad-43f0-9fc0-c58eccf681c5" },
        "memberElement": { "@id": "f20f3ad6-71e5-580d-bef8-22f8b3084bae" },
        "memberName": "JSON Export Example",
        "ownedRelatedElement": [
          { "@id": "f20f3ad6-71e5-580d-bef8-22f8b3084bae" }
        ]
      },
      {
        "@type": "Package",
        "@id": "f20f3ad6-71e5-580d-bef8-22f8b3084bae",
        "elementId": "f20f3ad6-71e5-580d-bef8-22f8b3084bae",
        "declaredName": "JSON Export Example",
        "owningRelationship": { "@id": "0a680cbf-b149-5715-8acd-2ce5ab495768" },
        "ownedRelationship": [
          { "@id": "61bdbd4a-dc8e-59e5-85ae-2d0a35ecf30b" },
          { "@id": "bd235a9c-2698-5574-9a01-d972c7ee778a" },
          { "@id": "f43d85c4-3605-57a8-bf7a-2421596cf4b4" }
        ]
      },
      {
        "@type": "OwningMembership",
        "@id": "61bdbd4a-dc8e-59e5-85ae-2d0a35ecf30b",
        "elementId": "61bdbd4a-dc8e-59e5-85ae-2d0a35ecf30b",
        "owningRelatedElement": { "@id": "f20f3ad6-71e5-580d-bef8-22f8b3084bae" },
        "memberElement": { "@id": "59009c6d-ed8e-5e5f-95c4-2d91f3730a15" },
        "memberName": "Electrical",
        "ownedRelatedElement": [
          { "@id": "59009c6d-ed8e-5e5f-95c4-2d91f3730a15" }
        ]
      },
      {
        "@type": "PartDefinition",
        "@id": "59009c6d-ed8e-5e5f-95c4-2d91f3730a15",
        "elementId": "59009c6d-ed8e-5e5f-95c4-2d91f3730a15",
        "declaredName": "Electrical",
        "owningRelationship": { "@id": "61bdbd4a-dc8e-59e5-85ae-2d0a35ecf30b" },
        "isVariation": false
      },
      {
        "@type": "OwningMembership",
        "@id": "bd235a9c-2698-5574-9a01-d972c7ee778a",
        "elementId": "bd235a9c-2698-5574-9a01-d972c7ee778a",
        "owningRelatedElement": { "@id": "f20f3ad6-71e5-580d-bef8-22f8b3084bae" },
        "memberElement": { "@id": "787ad28e-fbef-50ca-af0c-bef7f6ac65eb" },
        "memberName": "Mechanical",
        "ownedRelatedElement": [
          { "@id": "787ad28e-fbef-50ca-af0c-bef7f6ac65eb" }
        ]
      },
      {
        "@type": "PartDefinition",
        "@id": "787ad28e-fbef-50ca-af0c-bef7f6ac65eb",
        "elementId": "787ad28e-fbef-50ca-af0c-bef7f6ac65eb",
        "declaredName": "Mechanical",
        "owningRelationship": { "@id": "bd235a9c-2698-5574-9a01-d972c7ee778a" },
        "isVariation": false
      },
      {
        "@type": "OwningMembership",
        "@id": "f43d85c4-3605-57a8-bf7a-2421596cf4b4",
        "elementId": "f43d85c4-3605-57a8-bf7a-2421596cf4b4",
        "owningRelatedElement": { "@id": "f20f3ad6-71e5-580d-bef8-22f8b3084bae" },
        "memberElement": { "@id": "bac7b912-5575-5f6a-9df6-cced858dcda1" },
        "memberName": "Automobile",
        "ownedRelatedElement": [
          { "@id": "bac7b912-5575-5f6a-9df6-cced858dcda1" }
        ]
      },
      {
        "@type": "PartUsage",
        "@id": "bac7b912-5575-5f6a-9df6-cced858dcda1",
        "elementId": "bac7b912-5575-5f6a-9df6-cced858dcda1",
        "declaredName": "Automobile",
        "owningRelationship": { "@id": "f43d85c4-3605-57a8-bf7a-2421596cf4b4" },
        "isVariation": false,
        "ownedRelationship": [
          { "@id": "76080b80-74de-5f5f-be1c-8cb46b523f8d" },
          { "@id": "0d015b91-eaf5-51fe-9a8e-7becc647bd0b" }
        ]
      },
      {
        "@type": "FeatureMembership",
        "@id": "76080b80-74de-5f5f-be1c-8cb46b523f8d",
        "elementId": "76080b80-74de-5f5f-be1c-8cb46b523f8d",
        "owningRelatedElement": { "@id": "bac7b912-5575-5f6a-9df6-cced858dcda1" },
        "memberElement": { "@id": "46f32266-d488-50d1-abe0-988d5245f25d" },
        "memberName": "Drive Train",
        "ownedRelatedElement": [
          { "@id": "46f32266-d488-50d1-abe0-988d5245f25d" }
        ]
      },
      {
        "@type": "PartUsage",
        "@id": "46f32266-d488-50d1-abe0-988d5245f25d",
        "elementId": "46f32266-d488-50d1-abe0-988d5245f25d",
        "declaredName": "Drive Train",
        "owningRelationship": { "@id": "76080b80-74de-5f5f-be1c-8cb46b523f8d" },
        "isComposite": true,
        "isVariable": true,
        "isVariation": false,
        "ownedRelationship": [
          { "@id": "5d629737-2332-44c8-8d7f-eab312b83b19" }
        ]
      },
      {
        "@type": "FeatureTyping",
        "@id": "5d629737-2332-44c8-8d7f-eab312b83b19",
        "elementId": "5d629737-2332-44c8-8d7f-eab312b83b19",
        "owningRelatedElement": { "@id": "46f32266-d488-50d1-abe0-988d5245f25d" },
        "general": { "@id": "59009c6d-ed8e-5e5f-95c4-2d91f3730a15" },
        "specific": { "@id": "46f32266-d488-50d1-abe0-988d5245f25d" },
        "type": { "@id": "59009c6d-ed8e-5e5f-95c4-2d91f3730a15" },
        "typedFeature": { "@id": "46f32266-d488-50d1-abe0-988d5245f25d" }
      },
      {
        "@type": "FeatureMembership",
        "@id": "0d015b91-eaf5-51fe-9a8e-7becc647bd0b",
        "elementId": "0d015b91-eaf5-51fe-9a8e-7becc647bd0b",
        "owningRelatedElement": { "@id": "bac7b912-5575-5f6a-9df6-cced858dcda1" },
        "memberElement": { "@id": "ae75c320-492a-509b-86f3-f983173d050d" },
        "memberName": "Chassis",
        "ownedRelatedElement": [
          { "@id": "ae75c320-492a-509b-86f3-f983173d050d" }
        ]
      },
      {
        "@type": "PartUsage",
        "@id": "ae75c320-492a-509b-86f3-f983173d050d",
        "elementId": "ae75c320-492a-509b-86f3-f983173d050d",
        "declaredName": "Chassis",
        "owningRelationship": { "@id": "0d015b91-eaf5-51fe-9a8e-7becc647bd0b" },
        "isComposite": true,
        "isVariable": true,
        "isVariation": false,
        "ownedRelationship": [
          { "@id": "b436fe52-ee79-437f-877c-0a186e39b925" }
        ]
      },
      {
        "@type": "FeatureTyping",
        "@id": "b436fe52-ee79-437f-877c-0a186e39b925",
        "elementId": "b436fe52-ee79-437f-877c-0a186e39b925",
        "owningRelatedElement": { "@id": "ae75c320-492a-509b-86f3-f983173d050d" },
        "general": { "@id": "787ad28e-fbef-50ca-af0c-bef7f6ac65eb" },
        "specific": { "@id": "ae75c320-492a-509b-86f3-f983173d050d" },
        "type": { "@id": "787ad28e-fbef-50ca-af0c-bef7f6ac65eb" },
        "typedFeature": { "@id": "ae75c320-492a-509b-86f3-f983173d050d" }
      }
    ]

</div>

</div>

</div>

<div id="download" class="section">

## Download[](#download "Link to this heading")

Download this example [here](/v0.8.1/examples/json_dump.zip).

</div>

</div>
