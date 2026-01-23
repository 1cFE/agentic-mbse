<div id="expression-evaluation" class="section">

# Expression Evaluation<a href="#expression-evaluation" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

As part of semantic resolution, minimal expression evaluation is implemented. It covers most arithmetic expressions and some standard library functions, enough to parse the standard library and accompanying examples. Currently, the following are not yet supported:

- arbitrary user defined functions and expressions

Evaluation is implemented to work on a read-only model so it is not allowed to construct new elements. As a side effect, this reduces the memory usage as models parsed from syntactically valid source files cannot have orphan elements. Rather than constructing orphan literal expression elements, evaluation returns the values directly, see <a href="/python/v0.8.4/syside/Compiler.md" class="reference internal" title="syside.Compiler.evaluate"><span class="pre"><code class="sourceCode python">Compiler.evaluate</code></span></a> and <a href="/python/v0.8.4/syside/Compiler.md" class="reference internal" title="syside.Compiler.evaluate_feature"><span class="pre"><code class="sourceCode python">Compiler.evaluate_feature</code></span></a>. In both cases, <span class="pre">`stdlib`</span> parameter is used to accelerate internal conformance checks, and <span class="pre">`scope`</span> – to change the scope that expressions are evaluated in, equivalent to Python <span class="pre">`self`</span>. The <a href="/python/v0.8.4/syside/Compiler.md" class="reference internal" title="syside.Compiler"><span class="pre"><code class="sourceCode python">Compiler</code></span></a> is non-recursive and supports terminating evaluation after a number of <a href="/python/v0.8.4/syside/Compiler.md" class="reference internal" title="syside.Compiler.max_steps"><span class="pre"><code class="sourceCode python">max_steps</code></span></a>, e.g. if the expression is an infinite loop. For the common use case of evaluating member access, use <a href="/python/v0.8.4/syside/Compiler.md" class="reference internal" title="syside.Compiler.evaluate_feature"><span class="pre"><code class="sourceCode python">Compiler.evaluate_feature</code></span></a>:

<div class="highlight-py notranslate">

<div class="highlight">

    result, report = compiler.evaluate_feature(
        feature=feature, scope=owning_type
    )

</div>

</div>

Which is equivalent to evaluating <span class="pre">`owning_type.feature`</span> in SysML. Note that this will take redefinitions of <span class="pre">`feature`</span> in <span class="pre">`owning_type`</span> into account.

Most SysML operators are supported, however a few are not:

- <span class="pre">`all`</span>, type extent

- <span class="pre">`~`</span>, undefined by KerML specification

<div class="hint admonition">

<span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">Labs</span>

Quantity expressions, e.g. <span class="pre">`10`</span>` `<span class="pre">`[kg]`</span>, received initial evaluation support in v0.8.2 which needs to be enabled manually by passing <span class="pre">`experimental_quantities=True`</span> to <a href="/python/v0.8.4/syside/Compiler.md" class="reference internal" title="syside.Compiler.evaluate"><span class="pre"><code class="sourceCode python">Compiler.evaluate</code></span></a> and <a href="/python/v0.8.4/syside/Compiler.md" class="reference internal" title="syside.Compiler.evaluate_feature"><span class="pre"><code class="sourceCode python">Compiler.evaluate_feature</code></span></a>.

</div>

<a href="/python/v0.8.4/syside/ConstructorExpression.md" class="reference internal" title="syside.ConstructorExpression"><span class="pre"><code class="sourceCode python">ConstructorExpressions</code></span></a> return their owned return parameters (<a href="/python/v0.8.4/syside/InvocationExpression.md" class="reference internal" title="syside.InvocationExpression"><span class="pre"><code class="sourceCode python">InvocationExpressions</code></span></a> – themselves prior to v0.8) because they implicitly conform to the constructed object.

This means that their arguments are not evaluated eagerly. Given an <a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature.owning_type"><span class="pre"><code class="sourceCode python">owning_type</code></span></a> with a <a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type.features"><span class="pre"><code class="sourceCode python">feature</code></span></a> that evaluated to a constructor expression <span class="pre">`value`</span>, their arguments can be evaluated as:

<div class="highlight-py notranslate">

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

Before v0.8, constructor expressions could only be inferred as <a href="/python/v0.8.4/syside/InvocationExpression.md" class="reference internal" title="syside.InvocationExpression"><span class="pre"><code class="sourceCode python">InvocationExpressions</code></span></a> that invoked a <a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type"><span class="pre"><code class="sourceCode python">Type</code></span></a> that was neither a subtype of <a href="/python/v0.8.4/syside/Behavior.md" class="reference internal" title="syside.Behavior"><span class="pre"><code class="sourceCode python">Behavior</code></span></a> nor <a href="/python/v0.8.4/syside/Step.md" class="reference internal" title="syside.Step"><span class="pre"><code class="sourceCode python">Step</code></span></a>, e.g. <span class="pre">`not`</span>` `<span class="pre">`isinstance(expr.types.at(0),`</span>` `<span class="pre">`(*syside.Behavior.STD,`</span>` `<span class="pre">`*syside.Step.STD))`</span>.

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
