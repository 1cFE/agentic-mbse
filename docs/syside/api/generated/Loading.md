<div id="loading" class="section">

# Loading[](#loading "Link to this heading")

<div id="main-functions-and-objects" class="section">

## Main Functions and Objects[](#main-functions-and-objects "Link to this heading")

<div class="pst-scrollable-table-container">

|                                                                                                                             |                                                                                 |
| --------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| [`try_load_model`](/v0.8.1/api/generated/syside.try_load_model.md "syside.try_load_model")                                  | Load a SysMLv2 model.                                                           |
| [`load_model`](/v0.8.1/api/generated/syside.load_model.md "syside.load_model")                                              | Load a SysMLv2 model.                                                           |
| [`collect_files_recursively`](/v0.8.1/api/generated/syside.collect_files_recursively.md "syside.collect_files_recursively") | Recursively collect all `.sysml` and `.kerml` files in the specified directory. |
| [`Model`](/v0.8.1/api/generated/syside.Model.md "syside.Model")                                                             | A SysMLv2 model represented using abstract syntax.                              |

</div>

</div>

<div id="diagnostics" class="section">

## Diagnostics[](#diagnostics "Link to this heading")

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

<div id="advanced-pipeline-construction" class="section">

## (Advanced) Pipeline Construction[](#advanced-pipeline-construction "Link to this heading")

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

<div class="toctree-wrapper compound">

</div>

</div>

</div>
