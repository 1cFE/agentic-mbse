<div id="exporting" class="section">

# Exporting[](#exporting "Link to this heading")

<div id="pretty-printing-sysml-and-kerml" class="section">

## Pretty Printing SysML and KerML[](#pretty-printing-sysml-and-kerml "Link to this heading")

<div class="pst-scrollable-table-container">

|                                                                                               |                                                            |
| --------------------------------------------------------------------------------------------- | ---------------------------------------------------------- |
| [`pprint`](/v0.8.1/api/generated/syside.pprint.md "syside.pprint")                            | Prints model subtree starting at `root` to textual syntax. |
| [`FormatOptions`](/v0.8.1/api/generated/syside.FormatOptions.md "syside.FormatOptions")       |                                                            |
| [`FormatPreserved`](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved") |                                                            |
| [`ModelPrinter`](/v0.8.1/api/generated/syside.ModelPrinter.md "syside.ModelPrinter")          |                                                            |
| [`PrinterConfig`](/v0.8.1/api/generated/syside.PrinterConfig.md "syside.PrinterConfig")       |                                                            |
| [`PrintMode`](/v0.8.1/api/generated/syside.PrintMode.md "syside.PrintMode")                   |                                                            |
| [`AlwaysNever`](/v0.8.1/api/generated/syside.AlwaysNever.md "syside.AlwaysNever")             |                                                            |
| [`FloatFormat`](/v0.8.1/api/generated/syside.FloatFormat.md "syside.FloatFormat")             |                                                            |
| [`KwToken`](/v0.8.1/api/generated/syside.KwToken.md "syside.KwToken")                         |                                                            |
| [`LineEnd`](/v0.8.1/api/generated/syside.LineEnd.md "syside.LineEnd")                         |                                                            |
| [`MultiOrder`](/v0.8.1/api/generated/syside.MultiOrder.md "syside.MultiOrder")                |                                                            |
| [`MultiPlacement`](/v0.8.1/api/generated/syside.MultiPlacement.md "syside.MultiPlacement")    |                                                            |
| [`NullFormat`](/v0.8.1/api/generated/syside.NullFormat.md "syside.NullFormat")                |                                                            |
| [`OperatorBreak`](/v0.8.1/api/generated/syside.OperatorBreak.md "syside.OperatorBreak")       |                                                            |
| [`OptionalKw`](/v0.8.1/api/generated/syside.OptionalKw.md "syside.OptionalKw")                |                                                            |
| [`OptionalKwToken`](/v0.8.1/api/generated/syside.OptionalKwToken.md "syside.OptionalKwToken") |                                                            |
| [`OptionalToken`](/v0.8.1/api/generated/syside.OptionalToken.md "syside.OptionalToken")       |                                                            |

</div>

</div>

<div id="json-serialization" class="section">

## JSON Serialization[](#json-serialization "Link to this heading")

<div class="pst-scrollable-table-container">

|                                                                                                                        |                                                           |
| ---------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------- |
| [`SerializationError`](/v0.8.1/api/generated/syside.json.SerializationError.md "syside.json.SerializationError")       | Error serializing element to SysML v2 JSON.               |
| [`DeserializationError`](/v0.8.1/api/generated/syside.json.DeserializationError.md "syside.json.DeserializationError") | Error serializing element to SysML v2 JSON.               |
| [`SerdeWarning`](/v0.8.1/api/generated/syside.json.SerdeWarning.md "syside.json.SerdeWarning")                         | Class for warnings from serialization and deserialization |
| [`dumps`](/v0.8.1/api/generated/syside.json.dumps.md "syside.json.dumps")                                              | Serialize `element` to a SysML v2 JSON `str`.             |
| [`loads`](/v0.8.1/api/generated/syside.json.loads.md "syside.json.loads")                                              | loads implementation                                      |

</div>

</div>

<div id="advanced-formatting" class="section">

## (Advanced) Formatting[](#advanced-formatting "Link to this heading")

<div class="pst-scrollable-table-container">

|                                                                                                                       |  |
| --------------------------------------------------------------------------------------------------------------------- |  |
| [`DiagnosticContext`](/v0.8.1/api/generated/syside.DiagnosticContext.md "syside.DiagnosticContext")                   |  |
| [`DiagnosticFormatOptions`](/v0.8.1/api/generated/syside.DiagnosticFormatOptions.md "syside.DiagnosticFormatOptions") |  |
| [`TreeDrawing`](/v0.8.1/api/generated/syside.TreeDrawing.md "syside.TreeDrawing")                                     |  |
| [`format_diagnostics`](/v0.8.1/api/generated/syside.format_diagnostics.md "syside.format_diagnostics")                |  |

</div>

</div>

<div id="advanced-serialization-low-level" class="section">

## (Advanced) Serialization Low Level[](#advanced-serialization-low-level "Link to this heading")

<div class="pst-scrollable-table-container">

|                                                                                                              |                                                                                                                                  |
| ------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------- |
| [`serialize`](/v0.8.1/api/generated/syside.serialize.md "syside.serialize")                                  | Convenience function for serialization. Prefer using `Serializer` to avoid allocations when doing repeated serializations.       |
| [`deserialize`](/v0.8.1/api/generated/syside.deserialize.md "syside.deserialize")                            | Convenience function for deserialization. Prefer using `Deserializer` to avoid allocations when doing repeated deserializations. |
| [`Writer`](/v0.8.1/api/generated/syside.Writer.md "syside.Writer")                                           | Abstract base class for serialization writer implementations.                                                                    |
| [`Serializer`](/v0.8.1/api/generated/syside.Serializer.md "syside.Serializer")                               | Serializer for SysML models. The actual serialization output depends on used `Writer`.                                           |
| [`Reader`](/v0.8.1/api/generated/syside.Reader.md "syside.Reader")                                           | Abstract base class for all deserialization readers.                                                                             |
| [`Deserializer`](/v0.8.1/api/generated/syside.Deserializer.md "syside.Deserializer")                         | Deserializer for SysML models. The actual deserialization input depends on used `Reader`.                                        |
| [`FailAction`](/v0.8.1/api/generated/syside.FailAction.md "syside.FailAction")                               | Action taken when a serialization error is encountered.                                                                          |
| [`SerdeMessage`](/v0.8.1/api/generated/syside.SerdeMessage.md "syside.SerdeMessage")                         | Message emitted during (de)serialization                                                                                         |
| [`SerializationOptions`](/v0.8.1/api/generated/syside.SerializationOptions.md "syside.SerializationOptions") | Options for SysML model serialization. Attribute options are ordered in descending precedence.                                   |
| [`SerdeReport`](/v0.8.1/api/generated/syside.SerdeReport.md "syside.SerdeReport")                            | (De)Serialization report containing emitted messages.                                                                            |
| [`DeserializedModel`](/v0.8.1/api/generated/syside.DeserializedModel.md "syside.DeserializedModel")          | The model as it was deserialized, with references potentially unresolved.                                                        |
| [`PendingReference`](/v0.8.1/api/generated/syside.PendingReference.md "syside.PendingReference")             | Reference that has yet to be linked.                                                                                             |
| [`IdMap`](/v0.8.1/api/generated/syside.IdMap.md "syside.IdMap")                                              | `DeserializedModel` compatible mapping for elements. This will typically be used for linking pending references:                 |

</div>

</div>

<div id="advanced-json-low-level" class="section">

## (Advanced) JSON Low Level[](#advanced-json-low-level "Link to this heading")

<div class="pst-scrollable-table-container">

|                                                                                                              |                                                            |
| ------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------- |
| [`JsonStringWriter`](/v0.8.1/api/generated/syside.JsonStringWriter.md "syside.JsonStringWriter")             | Serialization writer that outputs JSON string              |
| [`JsonReader`](/v0.8.1/api/generated/syside.JsonReader.md "syside.JsonReader")                               | Unbound reader for JSON deserialization                    |
| [`JsonStringOptions`](/v0.8.1/api/generated/syside.JsonStringOptions.md "syside.JsonStringOptions")          | Options for serialization writer to JSON strings           |
| [`AttributeMap`](/v0.8.1/api/generated/syside.AttributeMap.md "syside.AttributeMap")                         | Internal opaque type for deserialization attribute mapping |
| [`DESERIALIZE_INTERNAL`](/v0.8.1/api/generated/syside.DESERIALIZE_INTERNAL.md "syside.DESERIALIZE_INTERNAL") |                                                            |
| [`DESERIALIZE_STANDARD`](/v0.8.1/api/generated/syside.DESERIALIZE_STANDARD.md "syside.DESERIALIZE_STANDARD") |                                                            |

</div>

<div class="toctree-wrapper compound">

</div>

</div>

</div>
