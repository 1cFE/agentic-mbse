<div id="querying" class="section">

# Querying[](#querying "Link to this heading")

<div id="main-helper-classes-for-querying" class="section">

## Main Helper Classes for Querying[](#main-helper-classes-for-querying "Link to this heading")

<div class="pst-scrollable-table-container">

|                                                                          |                                                                                                                                          |
| ------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------- |
| [`AstNode`](/v0.8.1/api/generated/syside.AstNode.md "syside.AstNode")    |                                                                                                                                          |
| [`CstNode`](/v0.8.1/api/generated/syside.CstNode.md "syside.CstNode")    |                                                                                                                                          |
| [`Document`](/v0.8.1/api/generated/syside.Document.md "syside.Document") |                                                                                                                                          |
| [`Url`](/v0.8.1/api/generated/syside.Url.md "syside.Url")                | `URL` as described using the [Uniform Resource Identifier (URI)](https://datatracker.ietf.org/doc/html/rfc3986) specification (RFC3986). |
| [`Heritage`](/v0.8.1/api/generated/syside.Heritage.md "syside.Heritage") |                                                                                                                                          |

</div>

</div>

<div id="containers" class="section">

## Containers[](#containers "Link to this heading")

<div class="pst-scrollable-table-container">

|                                                                                                              |                                                                                                                                                                                                                                                                              |
| ------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`ContainerView`](/v0.8.1/api/generated/syside.ContainerView.md "syside.ContainerView")                      | An immutable view into a native random-access container. Implements Sequence protocol.                                                                                                                                                                                       |
| [`ChildrenNodesView`](/v0.8.1/api/generated/syside.ChildrenNodesView.md "syside.ChildrenNodesView")          | A view to a container of children nodes.                                                                                                                                                                                                                                     |
| [`ChildrenNodes`](/v0.8.1/api/generated/syside.ChildrenNodes.md "syside.ChildrenNodes")                      | Container that stores a vector of children nodes.                                                                                                                                                                                                                            |
| [`OwnedChildrenNodes`](/v0.8.1/api/generated/syside.OwnedChildrenNodes.md "syside.OwnedChildrenNodes")       | Container that stores a vector of potentially owned children nodes.                                                                                                                                                                                                          |
| [`ChainedChildrenNodes`](/v0.8.1/api/generated/syside.ChainedChildrenNodes.md "syside.ChainedChildrenNodes") | Container that stores a vector of children nodes that may own feature chainings.                                                                                                                                                                                             |
| [`LazyIterator`](/v0.8.1/api/generated/syside.LazyIterator.md "syside.LazyIterator")                         |                                                                                                                                                                                                                                                                              |
| [`VisitAction`](/v0.8.1/api/generated/syside.VisitAction.md "syside.VisitAction")                            |                                                                                                                                                                                                                                                                              |
| [`SharedMutex`](/v0.8.1/api/generated/syside.SharedMutex.md "syside.SharedMutex")                            |                                                                                                                                                                                                                                                                              |
| [`WriteLocked`](/v0.8.1/api/generated/syside.WriteLocked.md "syside.WriteLocked")                            |                                                                                                                                                                                                                                                                              |
| [`Stream`](/v0.8.1/api/generated/syside.Stream.md "syside.Stream")                                           |                                                                                                                                                                                                                                                                              |
| [`QualifiedName`](/v0.8.1/api/generated/syside.QualifiedName.md "syside.QualifiedName")                      | A sequence of qualified name segments that stringifies with unrestricted names as needed. Unlike string, this allows querying segments in a qualified name without having to parse it again, and is cheaper to construct as string conversion is performed only when needed. |
| [`TypeGuard`](/v0.8.1/api/generated/syside.TypeGuard.md "syside.TypeGuard")                                  | The type used in a type check expression, e.g. `istype`, `hastype`. The actual expression result type is `ScalarValues::Boolean`.                                                                                                                                            |

</div>

</div>

<div id="enumerations" class="section">

## Enumerations[](#enumerations "Link to this heading")

<div class="pst-scrollable-table-container">

|                                                                                                                            |                                                                                   |
| -------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| [`ExplicitOperator`](/v0.8.1/api/generated/syside.ExplicitOperator.md "syside.ExplicitOperator")                           |                                                                                   |
| [`FeatureDirectionKind`](/v0.8.1/api/metamodel/KerML/FeatureDirectionKind.md "syside.FeatureDirectionKind")                | Implementation of `FeatureDirectionKind` defined in the KerML specification.      |
| [`Operator`](/v0.8.1/api/generated/syside.Operator.md "syside.Operator")                                                   |                                                                                   |
| [`PortionKind`](/v0.8.1/api/metamodel/SysML/PortionKind.md "syside.PortionKind")                                           | Implementation of `PortionKind` defined in the SysML specification.               |
| [`RequirementConstraintKind`](/v0.8.1/api/metamodel/SysML/RequirementConstraintKind.md "syside.RequirementConstraintKind") | Implementation of `RequirementConstraintKind` defined in the SysML specification. |
| [`StateSubactionKind`](/v0.8.1/api/metamodel/SysML/StateSubactionKind.md "syside.StateSubactionKind")                      | Implementation of `StateSubactionKind` defined in the SysML specification.        |
| [`TransitionFeatureKind`](/v0.8.1/api/metamodel/SysML/TransitionFeatureKind.md "syside.TransitionFeatureKind")             | Implementation of `TransitionFeatureKind` defined in the SysML specification.     |
| [`TriggerKind`](/v0.8.1/api/metamodel/SysML/TriggerKind.md "syside.TriggerKind")                                           | Implementation of `TriggerKind` defined in the SysML specification.               |
| [`VisibilityKind`](/v0.8.1/api/metamodel/KerML/VisibilityKind.md "syside.VisibilityKind")                                  | Implementation of `VisibilityKind` defined in the KerML specification.            |
| [`NameID`](/v0.8.1/api/generated/syside.NameID.md "syside.NameID")                                                         |                                                                                   |

</div>

</div>

<div id="compiler" class="section">

## Compiler[](#compiler "Link to this heading")

<div class="pst-scrollable-table-container">

|                                                                                                     |  |
| --------------------------------------------------------------------------------------------------- |  |
| [`Compiler`](/v0.8.1/api/generated/syside.Compiler.md "syside.Compiler")                            |  |
| [`CompilationReport`](/v0.8.1/api/generated/syside.CompilationReport.md "syside.CompilationReport") |  |
| [`BoundMetaclass`](/v0.8.1/api/generated/syside.BoundMetaclass.md "syside.BoundMetaclass")          |  |
| [`Infinity`](/v0.8.1/api/generated/syside.Infinity.md "syside.Infinity")                            |  |

</div>

</div>

<div id="urls" class="section">

## Urls[](#urls "Link to this heading")

<div class="pst-scrollable-table-container">

|                                                                                         |                                                                                                                                                                                                         |
| --------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`Url`](/v0.8.1/api/generated/syside.Url.md "syside.Url")                               | `URL` as described using the [Uniform Resource Identifier (URI)](https://datatracker.ietf.org/doc/html/rfc3986) specification (RFC3986).                                                                |
| [`make_file_url`](/v0.8.1/api/generated/syside.make_file_url.md "syside.make_file_url") | Construct a `Url` for a filesystem path with the `file:` scheme. This correctly handles Windows and Posix paths, normalizes Windows drive letters to uppercase, and percent escapes Unicode characters. |
| [`decode_path`](/v0.8.1/api/generated/syside.decode_path.md "syside.decode_path")       | Decode a filesystem path from a `Url`. This correctly handles Windows and Posix paths using `file://` scheme and returns other `Urls` as is.                                                            |
| [`EncodingOpts`](/v0.8.1/api/generated/syside.EncodingOpts.md "syside.EncodingOpts")    | Percent-encoding options                                                                                                                                                                                |
| [`HostType`](/v0.8.1/api/generated/syside.HostType.md "syside.HostType")                |                                                                                                                                                                                                         |
| [`IPv4Address`](/v0.8.1/api/generated/syside.IPv4Address.md "syside.IPv4Address")       |                                                                                                                                                                                                         |
| [`IPv6Address`](/v0.8.1/api/generated/syside.IPv6Address.md "syside.IPv6Address")       |                                                                                                                                                                                                         |
| [`Scheme`](/v0.8.1/api/generated/syside.Scheme.md "syside.Scheme")                      |                                                                                                                                                                                                         |

</div>

</div>

<div id="paths" class="section">

## Paths[](#paths "Link to this heading")

<div class="pst-scrollable-table-container">

|                                                                                                   |                                                                                                                                                                                                                                                                             |
| ------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`Path`](/v0.8.1/api/generated/syside.Path.md "syside.Path")                                      | A sequence of path segments that stringifies with unrestricted names as needed. Similar to `QualifiedName` but may contain indices to unnamed elements, that are printed literally with `/` separator instead.                                                              |
| [`append`](/v0.8.1/api/generated/syside.Path.md "syside.Path.append")                             | Append arg to the end of the list.                                                                                                                                                                                                                                          |
| [`clear`](/v0.8.1/api/generated/syside.Path.md "syside.Path.clear")                               | Remove all items from list.                                                                                                                                                                                                                                                 |
| [`count`](/v0.8.1/api/generated/syside.Path.md "syside.Path.count")                               | Return number of occurrences of arg.                                                                                                                                                                                                                                        |
| [`extend`](/v0.8.1/api/generated/syside.Path.md "syside.Path.extend")                             | Extend self by appending elements from arg.                                                                                                                                                                                                                                 |
| [`index`](/v0.8.1/api/generated/syside.Path.md "syside.Path.index")                               | S.index(value, \[start, \[stop\]\]) -\> integer – return first index of value. Raises ValueError if the value is not present.                                                                                                                                               |
| [`insert`](/v0.8.1/api/generated/syside.Path.md "syside.Path.insert")                             | Insert object arg1 before index arg0.                                                                                                                                                                                                                                       |
| [`pop`](/v0.8.1/api/generated/syside.Path.md "syside.Path.pop")                                   | Remove and return item at index (default last).                                                                                                                                                                                                                             |
| [`remove`](/v0.8.1/api/generated/syside.Path.md "syside.Path.remove")                             | Remove first occurrence of arg.                                                                                                                                                                                                                                             |
| [`to_owning_membership`](/v0.8.1/api/generated/syside.Path.md "syside.Path.to_owning_membership") | If this is true, this path is to the owning membership of the element the segments would resolve to. This is a flag rather than a segment since owning memberships can effectively only ever be the last segment. When formatted, this will add `/owningMembership` suffix. |

</div>

</div>

<div id="advanced-documents" class="section">

## (Advanced) Documents[](#advanced-documents "Link to this heading")

<div class="pst-scrollable-table-container">

|                                                                                               |                      |
| --------------------------------------------------------------------------------------------- | -------------------- |
| [`BasicDocument`](/v0.8.1/api/generated/syside.BasicDocument.md "syside.BasicDocument")       |                      |
| [`DocumentID`](/v0.8.1/api/generated/syside.DocumentID.md "syside.DocumentID")                |                      |
| [`DocumentOptions`](/v0.8.1/api/generated/syside.DocumentOptions.md "syside.DocumentOptions") |                      |
| [`FieldId`](/v0.8.1/api/generated/syside.FieldId.md "syside.FieldId")                         |                      |
| [`IndexedSymbol`](/v0.8.1/api/generated/syside.IndexedSymbol.md "syside.IndexedSymbol")       |                      |
| [`LibraryID`](/v0.8.1/api/generated/syside.LibraryID.md "syside.LibraryID")                   |                      |
| [`StateId`](/v0.8.1/api/generated/syside.StateId.md "syside.StateId")                         |                      |
| [`Symbol`](/v0.8.1/api/generated/syside.Symbol.md "syside.Symbol")                            |                      |
| [`BuildState`](/v0.8.1/api/generated/syside.BuildState.md "syside.BuildState")                | Document build state |
| [`DocumentState`](/v0.8.1/api/generated/syside.DocumentState.md "syside.DocumentState")       |                      |
| [`DocumentTier`](/v0.8.1/api/generated/syside.DocumentTier.md "syside.DocumentTier")          |                      |
| [`DocumentVersion`](/v0.8.1/api/generated/syside.DocumentVersion.md "syside.DocumentVersion") |                      |

</div>

</div>

<div id="advanced-text-documents" class="section">

## (Advanced) Text Documents[](#advanced-text-documents "Link to this heading")

<div class="pst-scrollable-table-container">

|                                                                                                                       |  |
| --------------------------------------------------------------------------------------------------------------------- |  |
| [`TextDocument`](/v0.8.1/api/generated/syside.TextDocument.md "syside.TextDocument")                                  |  |
| [`TextDocuments`](/v0.8.1/api/generated/syside.TextDocuments.md "syside.TextDocuments")                               |  |
| [`PositionUtf16`](/v0.8.1/api/generated/syside.PositionUtf16.md "syside.PositionUtf16")                               |  |
| [`PositionUtf8`](/v0.8.1/api/generated/syside.PositionUtf8.md "syside.PositionUtf8")                                  |  |
| [`PositionUtf32`](/v0.8.1/api/generated/syside.PositionUtf32.md "syside.PositionUtf32")                               |  |
| [`RangeUtf16`](/v0.8.1/api/generated/syside.RangeUtf16.md "syside.RangeUtf16")                                        |  |
| [`RangeUtf8`](/v0.8.1/api/generated/syside.RangeUtf8.md "syside.RangeUtf8")                                           |  |
| [`RangeUtf32`](/v0.8.1/api/generated/syside.RangeUtf32.md "syside.RangeUtf32")                                        |  |
| [`TextDocumentEditUtf16`](/v0.8.1/api/generated/syside.TextDocumentEditUtf16.md "syside.TextDocumentEditUtf16")       |  |
| [`TextDocumentEditUtf8`](/v0.8.1/api/generated/syside.TextDocumentEditUtf8.md "syside.TextDocumentEditUtf8")          |  |
| [`TextDocumentEditUtf32`](/v0.8.1/api/generated/syside.TextDocumentEditUtf32.md "syside.TextDocumentEditUtf32")       |  |
| [`TextEdit`](/v0.8.1/api/generated/syside.TextEdit.md "syside.TextEdit")                                              |  |
| [`TextDocumentSaveReason`](/v0.8.1/api/generated/syside.TextDocumentSaveReason.md "syside.TextDocumentSaveReason")    |  |
| [`TextDocumentData`](/v0.8.1/api/generated/syside.TextDocumentData.md "syside.TextDocumentData")                      |  |
| [`PartialTextDocumentData`](/v0.8.1/api/generated/syside.PartialTextDocumentData.md "syside.PartialTextDocumentData") |  |

</div>

<div class="toctree-wrapper compound">

</div>

</div>

</div>
