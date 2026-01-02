<div id="advanced-technical-guide" class="section">

<span id="automator-advanced"></span>

# Advanced Technical Guide[](#advanced-technical-guide "Link to this heading")

This section covers advanced technical aspects of Syside Automator for power users who need deeper understanding when building custom applications or scripting heavily using the library.

It details key implementation aspects including multithreading considerations, expression evaluation, formatting options, and JSON serialization features.

**Learn more:**

  - [<span class="std std-ref">Multithreading</span>](#automator-multithreading): Considerations for multithreading

  - [<span class="std std-ref">Expression Evaluation</span>](#automator-expression-evaluation): Capabilities of implemented expression evaluation

  - [<span class="std std-ref">Formatting</span>](#automator-formatting): Formatting options

  - [<span class="std std-ref">JSON Exports and Imports</span>](#automator-json-exports-imports): JSON serialization features

<div id="multithreading" class="section">

<span id="automator-multithreading"></span>

## Multithreading[](#multithreading "Link to this heading")

On modern computers, multithreading is necessary to achieve high performance and Syside here is no exception. Syside supports internal and external multithreading:

  - Internal multithreading: Syside uses multithreading internally when loading and validating models, which is not visible to the user except for the CPU usage.

  - External multithreading: Syside was designed to be used in multithreaded environments. While Python still uses a global interpreter lock (GIL), there is an ongoing effort to remove it. Therefore, the Syside API already exposes necessary locks for building multithreaded applications based on Syside once Python removes the GIL.

When using Syside in a multithreaded environment, the following guidelines should be followed:

  - Access to [`Documents`](/v0.8.1/api/generated/syside.Document.md "syside.Document") and [`TextDocuments`](/v0.8.1/api/generated/syside.TextDocument.md "syside.TextDocument") should be synchronized

  - Linked elements allow unsynchronized access to their owning documents for performance

  - Users who want to modify model [`Documents`](/v0.8.1/api/generated/syside.Document.md "syside.Document") should do so in a single-thread, or manually lock all dependent [`Documents`](/v0.8.1/api/generated/syside.Document.md "syside.Document") including transitive dependants.

</div>

<div id="expression-evaluation" class="section">

<span id="automator-expression-evaluation"></span>

## Expression Evaluation[](#expression-evaluation "Link to this heading")

As part of semantic resolution, minimal expression evaluation is implemented. It covers most arithmetic expressions and some standard library functions, enough to parse the standard library and accompanying examples. Currently, the following are not yet supported:

  - arbitrary user defined functions and expressions,

  - quantities and units.

Evaluation is implemented to work on a read-only model so it is not allowed to construct new elements. As a side effect, this reduces the memory usage as models parsed from syntactically valid source files cannot have orphan elements. Rather than constructing orphan literal expression elements, evaluation returns the values directly.

Most SysML operators are supported, however a few are not:

  - `[`, undefined by KerML specification, quantity declaration in SysML

  - `all`, type extent

  - `~`, undefined by KerML specification

[`ConstructorExpressions`](/v0.8.1/api/metamodel/KerML/ConstructorExpression.md "syside.ConstructorExpression") return their owned return parameters ([`InvocationExpressions`](/v0.8.1/api/metamodel/KerML/InvocationExpression.md "syside.InvocationExpression") – themselves prior to v0.8) because they implicitly conform to the constructed object. This means that its arguments are not evaluated eagerly. Given an [`owning_type`](/v0.8.1/api/metamodel/KerML/Feature.md "syside.Feature.owning_type") with a [`feature`](/v0.8.1/api/metamodel/KerML/Type.md "syside.Type.features") that evaluated to a constructor expression `value`, its arguments can be evaluated as:

<div class="highlight-python notranslate">

<div class="highlight">

    compiler = syside.Compiler()
    for parameter in value.owned_inputs.collect():
        expr = parameter.feature_value_expression
        if not expr:
            # should not be executed in a valid model
            print(f"{parameter} has no feature value")
        else:
            result, report = compiler.evaluate(expr, scope=owning_type)
            if not report:
                print(f"{parameter} failed to evaluate: {report.diagnostics}")
            elif isinstance(result, str):
                print(f'{parameter} = "{result}"')
            else:
                print(f"{parameter} = {result}")

</div>

</div>

<div class="admonition note">

Note

Before v0.8, constructor expressions could only be inferred as [`InvocationExpressions`](/v0.8.1/api/metamodel/KerML/InvocationExpression.md "syside.InvocationExpression") that invoked a [`Type`](/v0.8.1/api/metamodel/KerML/Type.md "syside.Type") that was neither a subtype of [`Behavior`](/v0.8.1/api/metamodel/KerML/Behavior.md "syside.Behavior") nor [`Step`](/v0.8.1/api/metamodel/KerML/Step.md "syside.Step"), e.g. `not isinstance(expr.types.at(0), (*syside.Behavior.STD, *syside.Step.STD))`.

</div>

In addition, currently supported standard library functions include:

  - `NumericalFunctions::product`

  - `NumericalFunctions::sum`

  - `SequenceFunctions::notEmpty`

  - `SequenceFunctions::isEmpty`

  - `SequenceFunctions::size`

  - `SequenceFunctions::includes`

  - `SequenceFunctions::excludes`

  - `StringFunctions::Length`

  - `StringFunctions::Substring`

Support for more standard library functions will be added in future updates.

</div>

<div id="formatting" class="section">

<span id="automator-formatting"></span>

## Formatting[](#formatting "Link to this heading")

Syside provides an AST-based formatter that ensures consistent code style across source files. The formatter:

  - Enforces consistent indentation and token usage (e.g., `:>>` vs `redefines`)

  - Converts in-memory models to textual syntax, even without original source text

  - Supports format ignore pragmas to preserve specific formatting

<div class="admonition note">

Note

The formatter verifies that models contain all required elements but does not validate the generated syntax.

</div>

Example of format ignore pragma usage:

<div class="highlight-sysml notranslate">

<div class="highlight">

    package P {
        part def PartDef;
    
        // syside-format ignore
        part 'my unformatted AST' : PartDef {
    }
    }

</div>

</div>

The pragma preserves the formatting of the AST it is attached to, while maintaining consistent indentation for the rest of the file.

</div>

<div id="json-exports-and-imports" class="section">

<span id="automator-json-exports-imports"></span>

## JSON Exports and Imports[](#json-exports-and-imports "Link to this heading")

Syside also supports bi-directional JSON serialization. Serialization produces a mostly specification compliant JSON with a few minor differences:

  - not all implicit elements are constructed which will fail for attributes that are defined as non-null in the standard JSON schema, e.g. `Function::result`;

  - references can be serialized with relative `@uri` field for references to elements from other documents by passing `include_cross_ref_uris=True` (default) to [`json.dumps`](/v0.8.1/api/generated/syside.json.dumps.md "syside.json.dumps"). This brings JSON exports in-line with corresponding XMI exports used by the Pilot implementation where references are always exported as `<relative URI>#<element id>`. Additionally, such exports enable much faster deserialization because cross references are transparent and do not require searching the world for their resolution.

<div class="admonition warning">

Warning

JSON export and import implementations in Syside and Pilot implementation target different use cases and, therefore, JSONs exported by one cannot be imported by another without additional processing. More specifically:

1.  Syside JSON support is primarily intended for use in project interchange files (.kpar) as described in clause 10 of KerML specification.

2.  Pilot implementation JSON support targets the model server API described in “Systems Modeling Application Programming Interface (API) and Services” specification.

We are working on bringing support of API-specific JSONs to Syside. Also, it is likely that Pilot implementation will support project interchange files in the near future.

</div>

JSON deserialization (import) works on the same JSON files as were exported. However, in the interest of keeping the initial implementation simple there are a few limitations:

  - root node is inferred as:
    
      - the first `Namespace` without an owning relationship,
    
      - the last ancestor of the first element in the array following either owning namespaces, owning related elements, or owning relationships,
    
      - the first element in the array otherwise;

  - references to elements from other [`Documents`](/v0.8.1/api/generated/syside.Document.md "syside.Document") may contain a `@uri` field. The URI of the [`Document`](/v0.8.1/api/generated/syside.Document.md "syside.Document") model is deserialized into will be used to resolve relative URI references, otherwise an empty URI will be passed to the resolver callback;

  - deserialization may be lossy because the specification dumps all owned elements into [`owned_relationships`](/v0.8.1/api/metamodel/KerML/Element.md "syside.Element.owned_relationships") and [`owned_related_elements`](/v0.8.1/api/metamodel/KerML/Relationship.md "syside.Relationship.owned_related_elements") attributes which lose the more fine grained information stored in the model by Syside. For example, [`SendActionUsage`](/v0.8.1/api/metamodel/SysML/SendActionUsage.md "syside.SendActionUsage") `receiver`, `payload`, and `sender` are all parameters to [`ReferenceUsage`](/v0.8.1/api/metamodel/SysML/ReferenceUsage.md "syside.ReferenceUsage"), only disambiguated by their relative position, so if one is missing the others may be deserialized into different members.position, so if one is missing the others may be deserialized into different members.

Note that deserialization ignores majority of fields present in the JSON schema, including all derived fields with the exception of `name` and `shortName`. Therefore users may wish to export JSONs with minimal export options to reduce memory usage and improve performance.

<div class="admonition warning">

Warning

JSONs typically take 100-1000 times more space than the original textual notation and are opaque to human readers. Therefore, we recommend using textual notation instead of JSON whenever possible.

</div>

</div>

</div>
