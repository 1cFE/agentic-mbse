<div id="extra" class="section">

# Extra[](#extra "Link to this heading")

<div id="syside-ide" class="section">

## Syside IDE[](#syside-ide "Link to this heading")

<div class="pst-scrollable-table-container">

|                                                                                                                                                      |                                                                                                                                                                                                                   |
| ---------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`syside.ide.AbsoluteSemanticToken`](/v0.8.1/api/generated/syside.ide.AbsoluteSemanticToken.md "syside.ide.AbsoluteSemanticToken")                   | Semantic token using absolute positions.                                                                                                                                                                          |
| [`syside.ide.DeltaSemanticToken`](/v0.8.1/api/generated/syside.ide.DeltaSemanticToken.md "syside.ide.DeltaSemanticToken")                            | Semantic token using delta encoded positions.                                                                                                                                                                     |
| [`syside.ide.SemanticTokenModifiersSet`](/v0.8.1/api/generated/syside.ide.SemanticTokenModifiersSet.md "syside.ide.SemanticTokenModifiersSet")       | Fixed-size bitset of SemanticTokenModifiers for easier use with LSP serialization.                                                                                                                                |
| [`syside.ide.SemanticTokensBuilder`](/v0.8.1/api/generated/syside.ide.SemanticTokensBuilder.md "syside.ide.SemanticTokensBuilder")                   | Helper for building LSP compatible semantic tokens.                                                                                                                                                               |
| [`syside.ide.build_full_semantic_tokens`](/v0.8.1/api/generated/syside.ide.build_full_semantic_tokens.md "syside.ide.build_full_semantic_tokens")    | Build full document semantic tokens. Returns `builder` if successful, and `None` otherwise. Generally, `None` is returned if the `document` has nothing to highlight.                                             |
| [`syside.ide.build_delta_semantic_tokens`](/v0.8.1/api/generated/syside.ide.build_delta_semantic_tokens.md "syside.ide.build_delta_semantic_tokens") | Build full document semantic tokens for edits. Returns `builder` if successful, and `None` otherwise. Generally, `None` is returned if the `document` has nothing to highlight.                                   |
| [`syside.ide.build_range_semantic_tokens`](/v0.8.1/api/generated/syside.ide.build_range_semantic_tokens.md "syside.ide.build_range_semantic_tokens") | Build range document semantic tokens. Returns `builder` if successful, and `None` otherwise. Generally, `None` is returned if the `document` has nothing to highlight.                                            |
| [`syside.ide.lsp.PositionEncodingKind`](/v0.8.1/api/generated/syside.ide.lsp.PositionEncodingKind.md "syside.ide.lsp.PositionEncodingKind")          | LSP position encoding kind. Note that SysIDE uses Utf-8 internally so it will incur no performance penalty. Other encodings will require lazy conversions, however allocations will be avoided whenever possible. |
| [`syside.ide.lsp.SemanticTokenModifiers`](/v0.8.1/api/generated/syside.ide.lsp.SemanticTokenModifiers.md "syside.ide.lsp.SemanticTokenModifiers")    | LSP defined semantic token modifiers. Technically, this is not a flag enum but `nanobind` does not permit arbitrary values otherwise.                                                                             |
| [`syside.ide.lsp.SemanticTokenTypes`](/v0.8.1/api/generated/syside.ide.lsp.SemanticTokenTypes.md "syside.ide.lsp.SemanticTokenTypes")                | LSP defined semantic token types. Technically, this is not a flag enum but `nanobind` does not permit arbitrary values otherwise.                                                                                 |
| [`syside.ide.lsp.SemanticTokens`](/v0.8.1/api/generated/syside.ide.lsp.SemanticTokens.md "syside.ide.lsp.SemanticTokens")                            |                                                                                                                                                                                                                   |
| [`syside.ide.lsp.SemanticTokensDelta`](/v0.8.1/api/generated/syside.ide.lsp.SemanticTokensDelta.md "syside.ide.lsp.SemanticTokensDelta")             |                                                                                                                                                                                                                   |
| [`syside.ide.lsp.SemanticTokensEdit`](/v0.8.1/api/generated/syside.ide.lsp.SemanticTokensEdit.md "syside.ide.lsp.SemanticTokensEdit")                |                                                                                                                                                                                                                   |

</div>

</div>

<div id="s-expressions" class="section">

## S-Expressions[](#s-expressions "Link to this heading")

<div class="pst-scrollable-table-container">

|                                                                                   |                                                                                           |
| --------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| [`sexp`](/v0.8.1/api/generated/syside.sexp.md "syside.sexp")                      | Generate a minimal S-expression of owned elements rooted at `root`, useful for debugging. |
| [`SexpOptions`](/v0.8.1/api/generated/syside.SexpOptions.md "syside.SexpOptions") |                                                                                           |

</div>

</div>

<div id="syside-debug" class="section">

## `syside.debug`[](#syside-debug "Link to this heading")

<div class="pst-scrollable-table-container">

|                                                                                                                              |  |
| ---------------------------------------------------------------------------------------------------------------------------- |  |
| [`syside.debug.set_leak_warnings`](/v0.8.1/api/generated/syside.debug.set_leak_warnings.md "syside.debug.set_leak_warnings") |  |

</div>

</div>

<div id="syside-gc" class="section">

## `syside.gc`[](#syside-gc "Link to this heading")

Internal GC interface. Currently only Documents are collected by the internal garbage collector.

<div class="pst-scrollable-table-container">

|                                                                                                         |                                                                                                                                                                                                                                                                                           |
| ------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`syside.gc.Debug`](/v0.8.1/api/generated/syside.gc.Debug.md "syside.gc.Debug")                         | Debug options for the garbage collector.                                                                                                                                                                                                                                                  |
| [`syside.gc.collect`](/v0.8.1/api/generated/syside.gc.collect.md "syside.gc.collect")                   | Explicitly call garbage collector once.                                                                                                                                                                                                                                                   |
| [`syside.gc.disable`](/v0.8.1/api/generated/syside.gc.disable.md "syside.gc.disable")                   | Disable automatic garbage collection.                                                                                                                                                                                                                                                     |
| [`syside.gc.enable`](/v0.8.1/api/generated/syside.gc.enable.md "syside.gc.enable")                      | Enable automatic garbage collection.                                                                                                                                                                                                                                                      |
| [`syside.gc.get_count`](/v0.8.1/api/generated/syside.gc.get_count.md "syside.gc.get_count")             | Returns the number of currently tracked objects.                                                                                                                                                                                                                                          |
| [`syside.gc.get_debug`](/v0.8.1/api/generated/syside.gc.get_debug.md "syside.gc.get_debug")             | Return a copy of the current debug options of the garbage collector.                                                                                                                                                                                                                      |
| [`syside.gc.get_executor`](/v0.8.1/api/generated/syside.gc.get_executor.md "syside.gc.get_executor")    | The executor assigned to the garbage collector.                                                                                                                                                                                                                                           |
| [`syside.gc.get_threshold`](/v0.8.1/api/generated/syside.gc.get_threshold.md "syside.gc.get_threshold") | Return the current threshold.                                                                                                                                                                                                                                                             |
| [`syside.gc.is_tracked`](/v0.8.1/api/generated/syside.gc.is_tracked.md "syside.gc.is_tracked")          | Returns `True` if `document` is tracked by the garbage collector.                                                                                                                                                                                                                         |
| [`syside.gc.isenabled`](/v0.8.1/api/generated/syside.gc.isenabled.md "syside.gc.isenabled")             | Returns `True` if automatic collection is enabled.                                                                                                                                                                                                                                        |
| [`syside.gc.set_debug`](/v0.8.1/api/generated/syside.gc.set_debug.md "syside.gc.set_debug")             | Set default options for the garbage collector. By default, everything is printed to stderr.                                                                                                                                                                                               |
| [`syside.gc.set_executor`](/v0.8.1/api/generated/syside.gc.set_executor.md "syside.gc.set_executor")    | Assign an executor to the garbage collector. Without an executor, the garbage collector always runs on the thread that invokes it, e.g. the main thread. In addition to processing documents concurrently, documents will also be destroyed asynchronously further improving performance. |
| [`syside.gc.set_threshold`](/v0.8.1/api/generated/syside.gc.set_threshold.md "syside.gc.set_threshold") | Set the garbage collector threshold, 0 disables collection. Negative values raise `ValueError`.                                                                                                                                                                                           |
| [`syside.gc.track`](/v0.8.1/api/generated/syside.gc.track.md "syside.gc.track")                         | Add document to garbage collector tracking list. Returns `False` if document was already tracked.                                                                                                                                                                                         |
| [`syside.gc.untrack`](/v0.8.1/api/generated/syside.gc.untrack.md "syside.gc.untrack")                   | Remove document from the garbage collector tracking list. Returns `False` if document was not tracked.                                                                                                                                                                                    |

</div>

</div>

<div id="syside-version" class="section">

## `syside.version`[](#syside-version "Link to this heading")

<div class="pst-scrollable-table-container">

|                                                                                                            |                                   |
| ---------------------------------------------------------------------------------------------------------- | --------------------------------- |
| [`syside.version.major`](/v0.8.1/api/generated/syside.version.major.md "syside.version.major")             |                                   |
| [`syside.version.minor`](/v0.8.1/api/generated/syside.version.minor.md "syside.version.minor")             |                                   |
| [`syside.version.patch`](/v0.8.1/api/generated/syside.version.patch.md "syside.version.patch")             |                                   |
| [`syside.version.sha`](/v0.8.1/api/generated/syside.version.sha.md "syside.version.sha")                   |                                   |
| [`syside.version.timestamp`](/v0.8.1/api/generated/syside.version.timestamp.md "syside.version.timestamp") |                                   |
| [`syside.version.date`](/v0.8.1/api/generated/syside.version.date.md "syside.version.date")                | Datetime of when SysIDE was built |

</div>

<div class="toctree-wrapper compound">

</div>

</div>

</div>
