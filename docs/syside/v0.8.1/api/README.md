<div id="api-reference" class="section">

<span id="api-ref"></span>

# API Reference[](#api-reference "Link to this heading")

[<span class="std std-ref">The previous section</span>](/v0.8.1/examples//README.md) showed examples of what can be achieved using Syside Automator. This section describes the Python API provided by Syside Automator that enables building such and more complicated workflows.

A typical workflow using Syside Automator will consist of some subset of the following steps, each of which is described in more detail in the following sections:

1.  [<span class="std std-ref">Loading a model</span>](#api-ref-loading-model) from KerML and SysML v2 textual notation files and converting them into abstract syntax.

2.  [<span class="std std-ref">Querying the abstract syntax</span>](#api-ref-abstract-syntax-querying) of the model.

3.  [<span class="std std-ref">Modifying the abstract syntax</span>](#api-ref-abstract-syntax-modifying) of the model.

4.  [<span class="std std-ref">Exporting the abstract syntax</span>](#api-ref-exporting-model) into textual notation or JSON format.

<div id="loading-a-model" class="section">

<span id="api-ref-loading-model"></span>

## Loading a Model[](#loading-a-model "Link to this heading")

In Syside, a model is represented using [`Model`](/v0.8.1/api/generated/syside.Model.md "syside.Model") class. It can be loaded using [`try_load_model`](/v0.8.1/api/generated/syside.try_load_model.md "syside.try_load_model") or [`load_model`](/v0.8.1/api/generated/syside.load_model.md "syside.load_model") functions, which take a list of KerML and SysML v2 files as input and return a [`Model`](/v0.8.1/api/generated/syside.Model.md "syside.Model") instance. The files can be collected by using [`collect_files_recursively`](/v0.8.1/api/generated/syside.collect_files_recursively.md "syside.collect_files_recursively") function, which is a convenience function that collects all files in a directory recursively. The key difference between [`load_model`](/v0.8.1/api/generated/syside.load_model.md "syside.load_model") and [`try_load_model`](/v0.8.1/api/generated/syside.try_load_model.md "syside.try_load_model") is that the former raises a [`ModelError`](/v0.8.1/api/generated/syside.ModelError.md "syside.ModelError") exception if the model contains errors while the latter produces some model even for files with errors. Both functions return a [`diagnostics`](/v0.8.1/api/generated/syside.Diagnostics.md "syside.Diagnostics") object containing the errors, warnings, and informational messages found when loading the model.

<div id="table-main-functions-and-objects" class="section">

### Table: Main Functions and Objects[](#table-main-functions-and-objects "Link to this heading")

The following table lists the functions and objects related to loading SysML models:

<div class="pst-scrollable-table-container">

|                                                                                                                             |                                                                                 |
| --------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| [`try_load_model`](/v0.8.1/api/generated/syside.try_load_model.md "syside.try_load_model")                                  | Load a SysMLv2 model.                                                           |
| [`load_model`](/v0.8.1/api/generated/syside.load_model.md "syside.load_model")                                              | Load a SysMLv2 model.                                                           |
| [`collect_files_recursively`](/v0.8.1/api/generated/syside.collect_files_recursively.md "syside.collect_files_recursively") | Recursively collect all `.sysml` and `.kerml` files in the specified directory. |
| [`Model`](/v0.8.1/api/generated/syside.Model.md "syside.Model")                                                             | A SysMLv2 model represented using abstract syntax.                              |

</div>

</div>

<div id="table-diagnostics" class="section">

### Table: Diagnostics[](#table-diagnostics "Link to this heading")

Loading a model can result in errors, warnings, and informational messages, which are reported using diagnostics. The following table lists the diagnostic-related objects:

<div class="pst-scrollable-table-container">

|                                                                                                                                      |                                                   |
| ------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------- |
| [`ModelError`](/v0.8.1/api/generated/syside.ModelError.md "syside.ModelError")                                                       | An exception thrown when model contains errors.   |
| [`Diagnostics`](/v0.8.1/api/generated/syside.Diagnostics.md "syside.Diagnostics")                                                    | All model diagnostics.                            |
| [`Diagnostic`](/v0.8.1/api/generated/syside.Diagnostic.md "syside.Diagnostic")                                                       |                                                   |
| [`DiagnosticMessage`](/v0.8.1/api/generated/syside.DiagnosticMessage.md "syside.DiagnosticMessage")                                  | A diagnostic providing information about a model. |
| [`DiagnosticSeverity`](/v0.8.1/api/generated/syside.DiagnosticSeverity.md "syside.DiagnosticSeverity")                               |                                                   |
| [`DiagnosticRelatedInformation`](/v0.8.1/api/generated/syside.DiagnosticRelatedInformation.md "syside.DiagnosticRelatedInformation") |                                                   |
| [`DocumentSegment`](/v0.8.1/api/generated/syside.DocumentSegment.md "syside.DocumentSegment")                                        |                                                   |
| [`CodeDescription`](/v0.8.1/api/generated/syside.CodeDescription.md "syside.CodeDescription")                                        |                                                   |

</div>

</div>

<div id="table-advanced-pipeline-construction" class="section">

### Table: (Advanced) Pipeline Construction[](#table-advanced-pipeline-construction "Link to this heading")

If [`load_model`](/v0.8.1/api/generated/syside.load_model.md "syside.load_model") is not flexible enough for your use case, the following table lists the lower level primitives that can be used to build a custom model loading pipeline:

<div class="pst-scrollable-table-container">

|                                                                                                                                      |                                                                                                                                                                                                                                                                                                                          |
| ------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [`get_default_executor`](/v0.8.1/api/generated/syside.get_default_executor.md "syside.get_default_executor")                         | Get a default initialized `Executor` for running schedules. Default executor will use half the logical cores that are available on the current machine. An executor is just a thread pool so there is no reason for constructing and destroying one all the time.                                                        |
| [`Environment`](/v0.8.1/api/generated/syside.Environment.md "syside.Environment")                                                    | Standard library environment for use with user models.                                                                                                                                                                                                                                                                   |
| [`Executor`](/v0.8.1/api/generated/syside.Executor.md "syside.Executor")                                                             |                                                                                                                                                                                                                                                                                                                          |
| [`ExecutionResult`](/v0.8.1/api/generated/syside.ExecutionResult.md "syside.ExecutionResult")                                        |                                                                                                                                                                                                                                                                                                                          |
| [`IOSchedule`](/v0.8.1/api/generated/syside.IOSchedule.md "syside.IOSchedule")                                                       |                                                                                                                                                                                                                                                                                                                          |
| [`Schedule`](/v0.8.1/api/generated/syside.Schedule.md "syside.Schedule")                                                             |                                                                                                                                                                                                                                                                                                                          |
| [`ScheduleError`](/v0.8.1/api/generated/syside.ScheduleError.md "syside.ScheduleError")                                              |                                                                                                                                                                                                                                                                                                                          |
| [`ScheduleOptions`](/v0.8.1/api/generated/syside.ScheduleOptions.md "syside.ScheduleOptions")                                        |                                                                                                                                                                                                                                                                                                                          |
| [`ValidationTiming`](/v0.8.1/api/generated/syside.ValidationTiming.md "syside.ValidationTiming")                                     |                                                                                                                                                                                                                                                                                                                          |
| [`DiagnosticResults`](/v0.8.1/api/generated/syside.DiagnosticResults.md "syside.DiagnosticResults")                                  |                                                                                                                                                                                                                                                                                                                          |
| [`Pipeline`](/v0.8.1/api/generated/syside.Pipeline.md "syside.Pipeline")                                                             |                                                                                                                                                                                                                                                                                                                          |
| [`PipelineOptions`](/v0.8.1/api/generated/syside.PipelineOptions.md "syside.PipelineOptions")                                        |                                                                                                                                                                                                                                                                                                                          |
| [`DocumentTimes`](/v0.8.1/api/generated/syside.DocumentTimes.md "syside.DocumentTimes")                                              |                                                                                                                                                                                                                                                                                                                          |
| [`DocumentKind`](/v0.8.1/api/generated/syside.DocumentKind.md "syside.DocumentKind")                                                 | Is this a model-created document?                                                                                                                                                                                                                                                                                        |
| [`StageTimes`](/v0.8.1/api/generated/syside.StageTimes.md "syside.StageTimes")                                                       |                                                                                                                                                                                                                                                                                                                          |
| [`build_model`](/v0.8.1/api/generated/syside.build_model.md "syside.build_model")                                                    | Build the AST for `document` from its `text_document`. Any existing model will be cleared, and the built model will not have its references linked. Instead, most references will use placeholder references that will be replaced by actual targets in linking stage. Only `sysml` and `kerml` languages are supported. |
| [`collect_exports`](/v0.8.1/api/generated/syside.collect_exports.md "syside.collect_exports")                                        | Collect and cache symbols exported by `document`. This must be called before the `document` is indexed, otherwise wrong or no symbols may be indexed. Returns the number of symbols cached.                                                                                                                              |
| [`make_pipeline`](/v0.8.1/api/generated/syside.make_pipeline.md "syside.make_pipeline")                                              |                                                                                                                                                                                                                                                                                                                          |
| [`sema_reset`](/v0.8.1/api/generated/syside.sema_reset.md "syside.sema_reset")                                                       | Reset semantic state of `element`. This will typically remove any implied relationships, and reverse a few other changes made by sema. After this completes, `element.sema_state == SemaState.None`.                                                                                                                     |
| [`Sema`](/v0.8.1/api/generated/syside.Sema.md "syside.Sema")                                                                         | Semantic resolver for SysML. This is responsible for linking references and resolving semantic rules in the pipeline.                                                                                                                                                                                                    |
| [`StaticIndex`](/v0.8.1/api/generated/syside.StaticIndex.md "syside.StaticIndex")                                                    |                                                                                                                                                                                                                                                                                                                          |
| [`Stdlib`](/v0.8.1/api/generated/syside.Stdlib.md "syside.Stdlib")                                                                   | Cache of standard library elements used by sema.                                                                                                                                                                                                                                                                         |
| [`SemaState`](/v0.8.1/api/generated/syside.SemaState.md "syside.SemaState")                                                          | Semantic resolution state of `Elements`. Sema will use this information to discard duplicate work, e.g. when resolving elements in a group of related documents.                                                                                                                                                         |
| [`ModelLanguage`](/v0.8.1/api/generated/syside.ModelLanguage.md "syside.ModelLanguage")                                              |                                                                                                                                                                                                                                                                                                                          |
| [`ImplicitSpecializationKind`](/v0.8.1/api/generated/syside.ImplicitSpecializationKind.md "syside.ImplicitSpecializationKind")       |                                                                                                                                                                                                                                                                                                                          |
| [`UnexpectedDifferentReference`](/v0.8.1/api/generated/syside.UnexpectedDifferentReference.md "syside.UnexpectedDifferentReference") |                                                                                                                                                                                                                                                                                                                          |

</div>

</div>

</div>

<div id="querying-the-abstract-syntax" class="section">

<span id="api-ref-abstract-syntax-querying"></span>

## Querying the Abstract Syntax[](#querying-the-abstract-syntax "Link to this heading")

When Syside loads a SysML model from textual notation, it converts it into *abstract syntax* as defined in the specification. SysML v2 abstract syntax is based on object-oriented principles and, therefore, can be modeled using Python classes. Page [<span class="std std-ref">Metamodel (Abstract Syntax)</span>](/v0.8.1/api/sysml.metamodel.md) shows a list of all element kinds defined in KerML and SysML v2 specifications and to which Python classes they are mapped. The Python classes were created based on the specification by following these principles:

  - The Syside Automator API uses Python convention for class and attribute names instead of the Java convention used in the specification. For example, attribute `assertedConstraint` on `AssertConstraintUsage` is mapped to [`asserted_constraint`](/v0.8.1/api/metamodel/SysML/AssertConstraintUsage.md "syside.AssertConstraintUsage.asserted_constraint").

  - According to the specification, a SysML v2 model is a set of *root namespaces*, which are namespaces that have no owner. Since root namespaces do not have names, there is no direct way of selecting a specific namespace. For this reason, Syside design exploits the KerML clause 10 that defines that each root namespace corresponds to a single file and shows a model as a collection of [`documents`](/v0.8.1/api/generated/syside.Document.md "syside.Document"). The documents are divided into two groups: documents that are part of the standard library documents and documents that are not. The former can be accessed through field [`stdlib_docs`](/v0.8.1/api/generated/syside.Model.md "syside.Model.stdlib_docs") and the latter through field [`user_docs`](/v0.8.1/api/generated/syside.Model.md "syside.Model.user_docs").

  - Since [`try_load_model`](/v0.8.1/api/generated/syside.try_load_model.md "syside.try_load_model") can produce a model even if the model contains errors, most attributes are defined as potentially returning `None` even if according to the specification they are required.

  - All Python classes modeling abstract syntax are subclasses of [`AstNode`](/v0.8.1/api/generated/syside.AstNode.md "syside.AstNode"), which provides several methods and fields that are often useful for querying the abstract syntax:
    
      - [`cast`](/v0.8.1/api/generated/syside.AstNode.md "syside.AstNode.cast") and [`try_cast`](/v0.8.1/api/generated/syside.AstNode.md "syside.AstNode.try_cast") methods for casting the node to a specific type (discussed below).
    
      - [`document`](/v0.8.1/api/generated/syside.AstNode.md "syside.AstNode.document") attribute for accessing the document the node belongs to.
    
      - [`parent`](/v0.8.1/api/generated/syside.AstNode.md "syside.AstNode.parent") attribute for accessing the parent node.
    
      - [`isinstance`](/v0.8.1/api/generated/syside.AstNode.md "syside.AstNode.isinstance") method for checking if the node is an instance of a specific type.
    
      - [`owned_elements`](/v0.8.1/api/generated/syside.AstNode.md "syside.AstNode.owned_elements") attribute for accessing the owned elements of the node.
    
      - [`cst_node`](/v0.8.1/api/generated/syside.AstNode.md "syside.AstNode.cst_node") attribute for accessing the concrete syntax node corresponding to the abstract syntax node.

  - The specification uses multiple inheritance extensively, modelling which in Python is challenging. For this reason, a class corresponding to a SysML element (for example, `AssertConstraintUsage`) that according to the specification specializes two other elements (`ConstraintUsage` and `Invariant`) will show only one class as a base class (in this case, `ConstraintUsage`).
    
    When using static type checkers such as [mypy](https://mypy-lang.org/) and [Pyright](https://microsoft.github.io/pyright/), the behavior of the specification can be emulated by casting elements to standard conforming unions which are declared as `STD` class variables on every element, e.g. [`Connector.STD`](/v0.8.1/api/metamodel/KerML/Connector.md "syside.Connector.STD"). Also be aware that `mypy` uses joins to infer generic types, reducing them to the most-derived common base type, while `pyright` correctly infers the generic union types.
    
    Example of casting an `element` to a standard conforming type:
    
    <div class="highlight-python notranslate">
    
    <div class="highlight">
    
        element: syside.Element
        connector = element.cast(syside.Connector.STD)
        typing.reveal_type(connector)  # pyright: syside.Connector | syside.ConnectorAsUsage
    
    </div>
    
    </div>
    
    For type hints, a similar `Std` type alias can be used, however it is only defined during type checking so cannot be used at runtime. This distinction is required due to limitations of the Python type system which does not allow type aliases and variables to be bound to the same name. Example of using standard type aliases:
    
    <div class="highlight-python notranslate">
    
    <div class="highlight">
    
        def example(element: syside.Element) -> syside.Connector.Std:
            return element.cast(syside.Connector.STD)
    
    </div>
    
    </div>

<div id="table-main-helper-classes-for-querying" class="section">

### Table: Main Helper Classes for Querying[](#table-main-helper-classes-for-querying "Link to this heading")

The following classes are likely to be needed when working with querying models written in textual notation:

  - [`AstNode`](/v0.8.1/api/generated/syside.AstNode.md "syside.AstNode") is a base class for all classes representing abstract syntax.

  - [`CstNode`](/v0.8.1/api/generated/syside.CstNode.md "syside.CstNode") is a class providing information about the text from which the node was parsed. An instance of this class can be obtained using [`cst_node`](/v0.8.1/api/generated/syside.AstNode.md "syside.AstNode.cst_node") attribute of [`AstNode`](/v0.8.1/api/generated/syside.AstNode.md "syside.AstNode") class.

  - [`Document`](/v0.8.1/api/generated/syside.Document.md "syside.Document") is a class representing a document in the model. A document of an abstract syntax node can be obtained using [`document`](/v0.8.1/api/generated/syside.AstNode.md "syside.AstNode.document") attribute of [`AstNode`](/v0.8.1/api/generated/syside.AstNode.md "syside.AstNode") class. An element representing the root namespace can be obtained by using [`root_node`](/v0.8.1/api/generated/syside.Document.md "syside.Document.root_node") attribute. [`Document`](/v0.8.1/api/generated/syside.Document.md "syside.Document") class also provides two methods for obtaining all elements of specific kind present in the document: [`all_elements`](/v0.8.1/api/generated/syside.Document.md "syside.Document.nodes") and [`all_nodes`](/v0.8.1/api/generated/syside.Document.md "syside.Document.all_nodes"). The former returns all elements of a given kind excluding subtypes, while the latter returns all elements of a given kind including subtypes. This functionality is also exposed on [`Model`](/v0.8.1/api/generated/syside.Model.md "syside.Model") class as method [`all_elements`](/v0.8.1/api/generated/syside.Model.md "syside.Model.nodes").

  - [`Url`](/v0.8.1/api/generated/syside.Url.md "syside.Url") is a class representing an URL of a document, which typically corresponds to a file path. An URL of a document can be obtained using [`url`](/v0.8.1/api/generated/syside.Document.md "syside.Document.url") attribute of [`Document`](/v0.8.1/api/generated/syside.Document.md "syside.Document") class.

  - [`Heritage`](/v0.8.1/api/generated/syside.Heritage.md "syside.Heritage") is a class containing type specializations and conjugations of a [`type`](/v0.8.1/api/metamodel/KerML/Type.md "syside.Type"). It can be obtained using [`heritage`](/v0.8.1/api/metamodel/KerML/Type.md "syside.Type.heritage") attribute of [`Type`](/v0.8.1/api/metamodel/KerML/Type.md "syside.Type") class.

</div>

<div id="table-abstract-syntax" class="section">

### Table: Abstract Syntax[](#table-abstract-syntax "Link to this heading")

The table with all classes modelling the abstract syntax can be found on page [<span class="std std-ref">Metamodel (Abstract Syntax)</span>](/v0.8.1/api/sysml.metamodel.md).

</div>

<div id="table-containers" class="section">

### Table: Containers[](#table-containers "Link to this heading")

The following table shows container classes that are used in Python classes modelling the abstract syntax:

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

<div id="table-compiler" class="section">

### Table: Compiler[](#table-compiler "Link to this heading")

The following table shows the classes related to the compiler:

<div class="pst-scrollable-table-container">

|                                                                                                     |  |
| --------------------------------------------------------------------------------------------------- |  |
| [`Compiler`](/v0.8.1/api/generated/syside.Compiler.md "syside.Compiler")                            |  |
| [`CompilationReport`](/v0.8.1/api/generated/syside.CompilationReport.md "syside.CompilationReport") |  |
| [`BoundMetaclass`](/v0.8.1/api/generated/syside.BoundMetaclass.md "syside.BoundMetaclass")          |  |
| [`Infinity`](/v0.8.1/api/generated/syside.Infinity.md "syside.Infinity")                            |  |

</div>

</div>

<div id="table-urls" class="section">

### Table: Urls[](#table-urls "Link to this heading")

Internally, documents are referenced by their Urls. We provide Url bindings as well.

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

<div id="table-paths" class="section">

### Table: Paths[](#table-paths "Link to this heading")

A **path** is a generalization of a [`QualifiedName`](/v0.8.1/api/generated/syside.QualifiedName.md "syside.QualifiedName") that can reference also anonymous elements.

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

<div id="table-advanced-documents" class="section">

### Table: (Advanced) Documents[](#table-advanced-documents "Link to this heading")

The following table shows additional classes related to documents, which may be needed for advanced use cases:

<div class="pst-scrollable-table-container">

|                                                                                               |                      |
| --------------------------------------------------------------------------------------------- | -------------------- |
| [`Document`](/v0.8.1/api/generated/syside.Document.md "syside.Document")                      |                      |
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

<div id="table-advanced-text-documents" class="section">

### Table: (Advanced) Text Documents[](#table-advanced-text-documents "Link to this heading")

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

</div>

</div>

<div id="modifying-the-abstract-syntax" class="section">

<span id="api-ref-abstract-syntax-modifying"></span>

## Modifying the Abstract Syntax[](#modifying-the-abstract-syntax "Link to this heading")

For convenient modification of the abstract syntax, Syside provides a set of additional properties and methods on the abstract syntax classes. Most commonly used ones are:

  - [`children`](/v0.8.1/api/metamodel/KerML/Namespace.md "syside.Namespace.children") is a property defined on class [`Namespace`](/v0.8.1/api/metamodel/KerML/Namespace.md "syside.Namespace") that represents and allows modifying elements in the body of the element (in textual notation, between brackets `{` and `}`) and expression arguments.

  - [`prefixes`](/v0.8.1/api/metamodel/KerML/Namespace.md "syside.Namespace.prefixes") is a property defined on class [`Namespace`](/v0.8.1/api/metamodel/KerML/Namespace.md "syside.Namespace") that represents a group for metadata prefixes, prefixed with `#` in textual notation.

  - [`type_relationships`](/v0.8.1/api/metamodel/KerML/Type.md "syside.Type.type_relationships") is a property defined on class [`Type`](/v0.8.1/api/metamodel/KerML/Type.md "syside.Type") that represents non-specialization type relationships appearing after specialization part, including feature chaining.

  - [`declared_ends`](/v0.8.1/api/metamodel/KerML/Connector.md "syside.Connector.declared_ends") and `declared_messages` are end features and messages before the children block. In the textual syntax they appear in the same position, hence in contrast to similar groups there are additional `try_append` and `try_insert` methods that return `None` without throwing if modification failed because the slot is already occupied by block.

  - Accessors are used to provide mutable access to specific attributes of an element. For example, attribute [`receiver_member`](/v0.8.1/api/metamodel/SysML/AcceptActionUsage.md "syside.AcceptActionUsage.receiver_member") on [`AcceptActionUsage`](/v0.8.1/api/metamodel/SysML/AcceptActionUsage.md "syside.AcceptActionUsage") is an accessor of type [`ParameterAccessor`](/v0.8.1/api/generated/syside.ParameterAccessor.md "syside.ParameterAccessor") that allows modifying the `receiver`. The receivers can be seen in the list of Syside specific attributes on the page of the corresponding element. They are typically indicated by `_member` or `_target` suffixes.

When modifying the abstract syntax, the following constraints must be observed:

  - An element can have only a single owner. Violating this constraint raises `ValueError` exception. However, the same element can be referenced by multiple elements.

  - Moving an element from one document to another is not supported and will raise `ValueError` exception.

  - Stealing ownership of an element is not allowed because the desired semantics are unclear. Remove the element from the model first before re-parenting it.

  - Adding a new owned or referenced element must satisfy the typing constraints and will raise `TypeError` exception if violated.

  - An element can be added only to an element that is not removed from the model. If this constraint is violated, a `RuntimeError` exception is raised. The problem can be fixed by adding the parent element back to the document as an owned element.

<div id="table-helper-classes" class="section">

### Table: Helper Classes[](#table-helper-classes "Link to this heading")

The following table shows the helper classes for modifying the abstract syntax:

<div class="pst-scrollable-table-container">

|                                                                                                     |  |
| --------------------------------------------------------------------------------------------------- |  |
| [`ConnectorEnds`](/v0.8.1/api/generated/syside.ConnectorEnds.md "syside.ConnectorEnds")             |  |
| [`TypeRelationships`](/v0.8.1/api/generated/syside.TypeRelationships.md "syside.TypeRelationships") |  |

</div>

</div>

<div id="table-member-accessors" class="section">

### Table: Member Accessors[](#table-member-accessors "Link to this heading")

The following table gives the list of accessor classes:

<div class="pst-scrollable-table-container">

|                                                                                                                                      |  |
| ------------------------------------------------------------------------------------------------------------------------------------ |  |
| [`ElementAccessor`](/v0.8.1/api/generated/syside.ElementAccessor.md "syside.ElementAccessor")                                        |  |
| [`MemberAccessor`](/v0.8.1/api/generated/syside.MemberAccessor.md "syside.MemberAccessor")                                           |  |
| [`OwnedMemberAccessor`](/v0.8.1/api/generated/syside.OwnedMemberAccessor.md "syside.OwnedMemberAccessor")                            |  |
| [`ChainedMemberAccessor`](/v0.8.1/api/generated/syside.ChainedMemberAccessor.md "syside.ChainedMemberAccessor")                      |  |
| [`ParameterAccessor`](/v0.8.1/api/generated/syside.ParameterAccessor.md "syside.ParameterAccessor")                                  |  |
| [`ReferentAccessor`](/v0.8.1/api/generated/syside.ReferentAccessor.md "syside.ReferentAccessor")                                     |  |
| [`SatisfactionSubjectAccessor`](/v0.8.1/api/generated/syside.SatisfactionSubjectAccessor.md "syside.SatisfactionSubjectAccessor")    |  |
| [`ActionParameterAccessor`](/v0.8.1/api/generated/syside.ActionParameterAccessor.md "syside.ActionParameterAccessor")                |  |
| [`ChainedFeatureMemberAccessor`](/v0.8.1/api/generated/syside.ChainedFeatureMemberAccessor.md "syside.ChainedFeatureMemberAccessor") |  |
| [`ArgumentsAccessor`](/v0.8.1/api/generated/syside.ArgumentsAccessor.md "syside.ArgumentsAccessor")                                  |  |
| [`EffectAccessor`](/v0.8.1/api/generated/syside.EffectAccessor.md "syside.EffectAccessor")                                           |  |
| [`ExpressionParameterAccessor`](/v0.8.1/api/generated/syside.ExpressionParameterAccessor.md "syside.ExpressionParameterAccessor")    |  |
| [`FeatureValueAccessor`](/v0.8.1/api/generated/syside.FeatureValueAccessor.md "syside.FeatureValueAccessor")                         |  |
| [`GuardAccessor`](/v0.8.1/api/generated/syside.GuardAccessor.md "syside.GuardAccessor")                                              |  |
| [`OwnedExpressionAccessor`](/v0.8.1/api/generated/syside.OwnedExpressionAccessor.md "syside.OwnedExpressionAccessor")                |  |
| [`OwnedFeatureAccessor`](/v0.8.1/api/generated/syside.OwnedFeatureAccessor.md "syside.OwnedFeatureAccessor")                         |  |
| [`OwnedMultiplicityAccessor`](/v0.8.1/api/generated/syside.OwnedMultiplicityAccessor.md "syside.OwnedMultiplicityAccessor")          |  |
| [`OwnedSuccessionAccessor`](/v0.8.1/api/generated/syside.OwnedSuccessionAccessor.md "syside.OwnedSuccessionAccessor")                |  |
| [`PayloadFeatureAccessor`](/v0.8.1/api/generated/syside.PayloadFeatureAccessor.md "syside.PayloadFeatureAccessor")                   |  |
| [`ReferenceParameterAccessor`](/v0.8.1/api/generated/syside.ReferenceParameterAccessor.md "syside.ReferenceParameterAccessor")       |  |
| [`ReferenceUsageAccessor`](/v0.8.1/api/generated/syside.ReferenceUsageAccessor.md "syside.ReferenceUsageAccessor")                   |  |
| [`ResultExpressionAccessor`](/v0.8.1/api/generated/syside.ResultExpressionAccessor.md "syside.ResultExpressionAccessor")             |  |
| [`TargetFeatureAccessor`](/v0.8.1/api/generated/syside.TargetFeatureAccessor.md "syside.TargetFeatureAccessor")                      |  |
| [`TransitionSourceAccessor`](/v0.8.1/api/generated/syside.TransitionSourceAccessor.md "syside.TransitionSourceAccessor")             |  |
| [`TriggerAccessor`](/v0.8.1/api/generated/syside.TriggerAccessor.md "syside.TriggerAccessor")                                        |  |

</div>

</div>

<div id="table-reference-accessors" class="section">

### Table: Reference Accessors[](#table-reference-accessors "Link to this heading")

<div class="pst-scrollable-table-container">

|                                                                                                                          |  |
| ------------------------------------------------------------------------------------------------------------------------ |  |
| [`ReferenceAccessor`](/v0.8.1/api/generated/syside.ReferenceAccessor.md "syside.ReferenceAccessor")                      |  |
| [`ChainedReferenceAccessor`](/v0.8.1/api/generated/syside.ChainedReferenceAccessor.md "syside.ChainedReferenceAccessor") |  |
| [`ChainedFeatureReference`](/v0.8.1/api/generated/syside.ChainedFeatureReference.md "syside.ChainedFeatureReference")    |  |
| [`ChainedTypeReference`](/v0.8.1/api/generated/syside.ChainedTypeReference.md "syside.ChainedTypeReference")             |  |
| [`ClassifierReference`](/v0.8.1/api/generated/syside.ClassifierReference.md "syside.ClassifierReference")                |  |
| [`FeatureReference`](/v0.8.1/api/generated/syside.FeatureReference.md "syside.FeatureReference")                         |  |
| [`TypeReference`](/v0.8.1/api/generated/syside.TypeReference.md "syside.TypeReference")                                  |  |

</div>

</div>

<div id="table-containers-accessors" class="section">

### Table: Containers Accessors[](#table-containers-accessors "Link to this heading")

<div class="pst-scrollable-table-container">

|                                                                                                                 |                                                                                                                                                     |
| --------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`Annotations`](/v0.8.1/api/generated/syside.Annotations.md "syside.Annotations")                               |                                                                                                                                                     |
| [`ConnectorEndsAccessor`](/v0.8.1/api/generated/syside.ConnectorEndsAccessor.md "syside.ConnectorEndsAccessor") |                                                                                                                                                     |
| [`ConnectorAsUsageEnds`](/v0.8.1/api/generated/syside.ConnectorAsUsageEnds.md "syside.ConnectorAsUsageEnds")    |                                                                                                                                                     |
| [`ConnectorEnds`](/v0.8.1/api/generated/syside.ConnectorEnds.md "syside.ConnectorEnds")                         |                                                                                                                                                     |
| [`DependencyEnds`](/v0.8.1/api/generated/syside.DependencyEnds.md "syside.DependencyEnds")                      |                                                                                                                                                     |
| [`DependencyPrefixes`](/v0.8.1/api/generated/syside.DependencyPrefixes.md "syside.DependencyPrefixes")          |                                                                                                                                                     |
| [`Heritage`](/v0.8.1/api/generated/syside.Heritage.md "syside.Heritage")                                        |                                                                                                                                                     |
| [`Messages`](/v0.8.1/api/generated/syside.Messages.md "syside.Messages")                                        |                                                                                                                                                     |
| [`NamespaceBody`](/v0.8.1/api/generated/syside.NamespaceBody.md "syside.NamespaceBody")                         |                                                                                                                                                     |
| [`NamespacePrefixes`](/v0.8.1/api/generated/syside.NamespacePrefixes.md "syside.NamespacePrefixes")             |                                                                                                                                                     |
| [`RelationshipBody`](/v0.8.1/api/generated/syside.RelationshipBody.md "syside.RelationshipBody")                | Container for relationship bodies. Works similarly to `ChildrenNodes` except relationships are not needed and all elements are taken ownership off. |
| [`TypeRelationships`](/v0.8.1/api/generated/syside.TypeRelationships.md "syside.TypeRelationships")             |                                                                                                                                                     |

</div>

</div>

</div>

<div id="exporting-to-textual-notation-or-json" class="section">

<span id="api-ref-exporting-model"></span>

## Exporting to Textual Notation or JSON[](#exporting-to-textual-notation-or-json "Link to this heading")

Syside provides two ways of exporting the modified abstract syntax:

  - [`pprint`](/v0.8.1/api/generated/syside.pprint.md "syside.pprint") function for pretty printing the abstract syntax in textual notation.

  - [`json.dumps`](/v0.8.1/api/generated/syside.json.dumps.md "syside.json.dumps") function for serializing the abstract syntax into JSON format.

<div id="table-pretty-printing-sysml-and-kerml" class="section">

### Table: Pretty Printing SysML and KerML[](#table-pretty-printing-sysml-and-kerml "Link to this heading")

The following table shows the classes and functions related to pretty printing SysML and KerML in textual notation:

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

<div id="table-json-serialization" class="section">

### Table: JSON Serialization[](#table-json-serialization "Link to this heading")

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

<div id="table-advanced-formatting" class="section">

### Table: (Advanced) Formatting[](#table-advanced-formatting "Link to this heading")

<div class="pst-scrollable-table-container">

|                                                                                                                       |  |
| --------------------------------------------------------------------------------------------------------------------- |  |
| [`DiagnosticContext`](/v0.8.1/api/generated/syside.DiagnosticContext.md "syside.DiagnosticContext")                   |  |
| [`DiagnosticFormatOptions`](/v0.8.1/api/generated/syside.DiagnosticFormatOptions.md "syside.DiagnosticFormatOptions") |  |
| [`TreeDrawing`](/v0.8.1/api/generated/syside.TreeDrawing.md "syside.TreeDrawing")                                     |  |
| [`format_diagnostics`](/v0.8.1/api/generated/syside.format_diagnostics.md "syside.format_diagnostics")                |  |

</div>

</div>

<div id="table-advanced-serialization-low-level" class="section">

### Table: (Advanced) Serialization Low Level[](#table-advanced-serialization-low-level "Link to this heading")

The following table shows the classes and functions related to serialization:

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

<div id="table-advanced-json-low-level" class="section">

### Table: (Advanced) JSON Low Level[](#table-advanced-json-low-level "Link to this heading")

The following table shows the classes and functions related to JSON serialization:

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

</div>
