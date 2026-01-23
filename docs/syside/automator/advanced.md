<div id="advanced-technical-guide" class="section">

<span id="automator-advanced"></span>

# Advanced Technical Guide<a href="#advanced-technical-guide" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

This section covers advanced technical aspects of Syside Automator for power users who need deeper understanding when building custom applications or scripting heavily using the library.

It details key implementation aspects including multithreading considerations, expression evaluation, formatting options, and JSON serialization features.

**Learn more:**

- <a href="#automator-multithreading" class="reference internal"><span class="std std-ref">Multithreading</span></a>: Considerations for multithreading

- <a href="#automator-expression-evaluation" class="reference internal"><span class="std std-ref">Expression Evaluation</span></a>: Capabilities of implemented expression evaluation

- <a href="#automator-formatting" class="reference internal"><span class="std std-ref">Formatting</span></a>: Formatting options

- <a href="#automator-json-exports-imports" class="reference internal"><span class="std std-ref">JSON Exports and Imports Labs</span></a>: JSON serialization features

<div id="multithreading" class="section">

<span id="automator-multithreading"></span>

## Multithreading<a href="#multithreading" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

On modern computers, multithreading is necessary to achieve high performance and Syside here is no exception. Syside supports internal and external multithreading:

- Internal multithreading: Syside uses multithreading internally when loading and validating models, which is not visible to the user except for the CPU usage.

- External multithreading: Syside was designed to be used in multithreaded environments. While Python still uses a global interpreter lock (GIL), there is an ongoing effort to remove it. Therefore, the Syside API already exposes necessary locks for building multithreaded applications based on Syside once Python removes the GIL.

When using Syside in a multithreaded environment, the following guidelines should be followed:

- Access to <a href="/python/v0.8.4/syside/Document.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">Documents</code></span></a> and <a href="/python/v0.8.4/syside/TextDocument.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">TextDocuments</code></span></a> should be synchronized

- Linked elements allow unsynchronized access to their owning documents for performance

- Users who want to modify model <a href="/python/v0.8.4/syside/Document.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">Documents</code></span></a> should do so in a single-thread, or manually lock all dependent <a href="/python/v0.8.4/syside/Document.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">Documents</code></span></a> including transitive dependants.

</div>

<div id="expression-evaluation" class="section">

<span id="automator-expression-evaluation"></span>

## Expression Evaluation<a href="#expression-evaluation" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

As part of semantic resolution, minimal expression evaluation is implemented. It covers most arithmetic expressions and some standard library functions, enough to parse the standard library and accompanying examples. Currently, the following are not yet supported:

- arbitrary user defined functions and expressions.

Evaluation is implemented to work on a read-only model so it is not allowed to construct new elements. As a side effect, this reduces the memory usage as models parsed from syntactically valid source files cannot have orphan elements. Rather than constructing orphan literal expression elements, evaluation returns the values directly.

Most SysML operators are supported, however a few are not:

- <span class="pre">`all`</span>, type extent

- <span class="pre">`~`</span>, undefined by KerML specification

Quantity expressions, e.g. <span class="pre">`10`</span>` `<span class="pre">`[kg]`</span>, received initial evaluation support in v0.8.2 which needs to be enabled manually by passing <span class="pre">`experimental_quantities=True`</span> to <a href="/python/v0.8.4/syside/Compiler.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">Compiler.evaluate</code></span></a> and

<a href="/python/v0.8.4/syside/ConstructorExpression.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">ConstructorExpressions</code></span></a> return their owned return parameters (<a href="/python/v0.8.4/syside/InvocationExpression.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">InvocationExpressions</code></span></a> – themselves prior to v0.8) because they implicitly conform to the constructed object. This means that its arguments are not evaluated eagerly. Given an <a href="/python/v0.8.4/syside/Feature.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">owning_type</code></span></a> with a <a href="/python/v0.8.4/syside/Type.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">feature</code></span></a> that evaluated to a constructor expression <span class="pre">`value`</span>, its arguments can be evaluated as:

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

Before v0.8, constructor expressions could only be inferred as <a href="/python/v0.8.4/syside/InvocationExpression.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">InvocationExpressions</code></span></a> that invoked a <a href="/python/v0.8.4/syside/Type.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">Type</code></span></a> that was neither a subtype of <a href="/python/v0.8.4/syside/Behavior.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">Behavior</code></span></a> nor <a href="/python/v0.8.4/syside/Step.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">Step</code></span></a>, e.g. <span class="pre">`not`</span>` `<span class="pre">`isinstance(expr.types.at(0),`</span>` `<span class="pre">`(*syside.Behavior.STD,`</span>` `<span class="pre">`*syside.Step.STD))`</span>.

</div>

In addition, currently supported standard library functions include:

- <span class="pre">`NumericalFunctions::product`</span>

- <span class="pre">`NumericalFunctions::sum`</span>

- <span class="pre">`SequenceFunctions::notEmpty`</span>

- <span class="pre">`SequenceFunctions::isEmpty`</span>

- <span class="pre">`SequenceFunctions::size`</span>

- <span class="pre">`SequenceFunctions::includes`</span>

- <span class="pre">`SequenceFunctions::excludes`</span>

- <span class="pre">`StringFunctions::Length`</span>

- <span class="pre">`StringFunctions::Substring`</span>

Support for more standard library functions will be added in future updates.

</div>

<div id="formatting" class="section">

<span id="automator-formatting"></span>

## Formatting<a href="#formatting" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

Syside provides an AST-based formatter that ensures consistent code style across source files. The formatter:

- Enforces consistent indentation and token usage (e.g., <span class="pre">`:>>`</span> vs <span class="pre">`redefines`</span>)

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

<div id="json-exports-and-imports-labs" class="section">

<span id="automator-json-exports-imports"></span>

## JSON Exports and Imports <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">Labs</span><a href="#json-exports-and-imports-labs" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

Syside also supports bi-directional JSON serialization. Serialization produces a mostly specification compliant JSON with a few minor differences:

- not all implicit elements are constructed which will fail for attributes that are defined as non-null in the standard JSON schema, e.g. <span class="pre">`Function::result`</span>;

- references can be serialized with relative <span class="pre">`@uri`</span> field for references to elements from other documents by passing <span class="pre">`include_cross_ref_uris=True`</span> (default) to <a href="/python/v0.8.4/syside/json//README.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">json.dumps</code></span></a>. This brings JSON exports in-line with corresponding XMI exports used by the Pilot implementation where references are always exported as <span class="pre">`<relative`</span>` `<span class="pre">`URI>#<element`</span>` `<span class="pre">`id>`</span>. Additionally, such exports enable much faster deserialization because cross references are transparent and do not require searching the world for their resolution.

<div class="admonition warning">

Warning

JSON export and import implementations in Syside and Pilot implementation target different use cases and, therefore, JSONs exported by one cannot be imported by another without additional processing. More specifically:

1.  Syside JSON support is primarily intended for use in project interchange files (.kpar) as described in clause 10 of KerML specification.

2.  Pilot implementation JSON support targets the model server API described in “Systems Modeling Application Programming Interface (API) and Services” specification.

We are working on bringing support of API-specific JSONs to Syside. Also, it is likely that Pilot implementation will support project interchange files in the near future.

</div>

JSON deserialization (import) works on the same JSON files as were exported. However, in the interest of keeping the initial implementation simple there are a few limitations:

- root node is inferred as:

  - the first <span class="pre">`Namespace`</span> without an owning relationship,

  - the last ancestor of the first element in the array following either owning namespaces, owning related elements, or owning relationships,

  - the first element in the array otherwise;

- references to elements from other <a href="/python/v0.8.4/syside/Document.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">Documents</code></span></a> may contain a <span class="pre">`@uri`</span> field. The URI of the <a href="/python/v0.8.4/syside/Document.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">Document</code></span></a> model is deserialized into will be used to resolve relative URI references, otherwise an empty URI will be passed to the resolver callback;

- deserialization may be lossy because the specification dumps all owned elements into <a href="/python/v0.8.4/syside/Element.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">owned_relationships</code></span></a> and <a href="/python/v0.8.4/syside/Relationship.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">owned_related_elements</code></span></a> attributes which lose the more fine grained information stored in the model by Syside. For example, <a href="/python/v0.8.4/syside/SendActionUsage.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">SendActionUsage</code></span></a> <span class="pre">`receiver`</span>, <span class="pre">`payload`</span>, and <span class="pre">`sender`</span> are all parameters to <a href="/python/v0.8.4/syside/ReferenceUsage.md" class="apiref reference external"><span class="pre"><code class="sourceCode python">ReferenceUsage</code></span></a>, only disambiguated by their relative position, so if one is missing the others may be deserialized into different members.position, so if one is missing the others may be deserialized into different members.

Note that deserialization ignores majority of fields present in the JSON schema, including all derived fields with the exception of <span class="pre">`name`</span> and <span class="pre">`shortName`</span>. Therefore users may wish to export JSONs with minimal export options to reduce memory usage and improve performance.

<div class="admonition warning">

Warning

JSONs typically take 100-1000 times more space than the original textual notation and are opaque to human readers. Therefore, we recommend using textual notation instead of JSON whenever possible.

</div>

</div>

</div>
