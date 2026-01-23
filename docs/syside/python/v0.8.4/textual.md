<div id="textual-notation" class="section">

# Textual Notation<a href="#textual-notation" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

<div id="loading-a-model" class="section">

## Loading a Model<a href="#loading-a-model" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

In Syside, a model is represented using <a href="/python/v0.8.4/syside/Model.md" class="reference internal" title="syside.Model"><span class="pre"><code class="sourceCode python">Model</code></span></a> class. It can be loaded using <a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside.try_load_model"><span class="pre"><code class="sourceCode python">try_load_model</code></span></a> or <a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside.load_model"><span class="pre"><code class="sourceCode python">load_model</code></span></a> functions, which take a list of KerML and SysML v2 files as input and return a tuple of <a href="/python/v0.8.4/syside/Model.md" class="reference internal" title="syside.Model"><span class="pre"><code class="sourceCode python">Model</code></span></a> and <a href="/python/v0.8.4/syside/Diagnostics.md" class="reference internal" title="syside.Diagnostics"><span class="pre"><code class="sourceCode python">Diagnostics</code></span></a> instances:

<div class="highlight-py notranslate">

<div class="highlight">

    model, diagnostics = syside.load_model(paths)

</div>

</div>

<div class="admonition note">

Note

Files can be collected using <a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside.collect_files_recursively"><span class="pre"><code class="sourceCode python">collect_files_recursively</code></span></a> function, which collects all files in a directory recursively.

</div>

Additionally, models can be loaded directly from source strings:

<div class="highlight-py notranslate">

<div class="highlight">

    model, diagnostics = syside.load_model(sysml_source="package P;")

</div>

</div>

<div class="highlight-py notranslate">

<div class="highlight">

    model, diagnostics = syside.load_model(kerml_source="package P;")

</div>

</div>

The key difference between <a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside.load_model"><span class="pre"><code class="sourceCode python">load_model</code></span></a> and <a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside.try_load_model"><span class="pre"><code class="sourceCode python">try_load_model</code></span></a> is that the former raises a <a href="/python/v0.8.4/syside/ModelError.md" class="reference internal" title="syside.ModelError"><span class="pre"><code class="sourceCode python">ModelError</code></span></a> exception if the model contains errors, or warnings with <span class="pre">`warnings_as_errors=True`</span>, while the latter produces some model even for files with errors. Both functions return a <a href="/python/v0.8.4/syside/Diagnostics.md" class="reference internal" title="syside.Diagnostics"><span class="pre"><code class="sourceCode python">Diagnostics</code></span></a> object containing the errors, warnings, and informational messages found when loading the model. <a href="/python/v0.8.4/syside/Diagnostic.md" class="reference internal" title="syside.Diagnostic"><span class="pre"><code class="sourceCode python">Diagnostic</code></span></a> is modelled after LSP <a href="https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#diagnostic" class="reference external" target="_blank">Diagnostic</a>.

Additionally, models can be loaded with different <a href="/python/v0.8.4/syside/Environment.md" class="reference internal" title="syside.Environment"><span class="pre"><code class="sourceCode python">Environments</code></span></a> which are used as model dependencies. If an <a href="/python/v0.8.4/syside/Environment.md" class="reference internal" title="syside.Environment"><span class="pre"><code class="sourceCode python">Environment</code></span></a> is not provided, it defaults to the bundled standard library environment. Other <span class="pre">`models`</span> can be used as dependencies:

<div class="highlight-py notranslate">

<div class="highlight">

    dependent_model, diagnostics = syside.load_model(
        sysml_source="private import P;",
        environment=syside.Environment.from_documents(
            model.all_docs, model.index
        ),
    )

</div>

</div>

For details on model structure, see <a href="/python/v0.8.4/structure.md" class="reference internal"><span class="doc">Model Structure</span></a>. For low-level details, see <a href="/python/v0.8.4/low-level.md" class="reference internal"><span class="doc">Low-Level API</span></a>.

</div>

<div id="exporting" class="section">

## Exporting<a href="#exporting" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

A SysML model rooted at <span class="pre">`element`</span> can be printed with <span class="pre">`syside.pprint(element)`</span>, or with

<div class="highlight-py notranslate">

<div class="highlight">

    cfg = syside.PrinterConfig()  # optional
    options = syside.FormatOptions()  # optional
    # change format options here
    printer = syside.ModelPrinter.sysml(format=options)  # optional
    text: str = syside.pprint(element, printer=printer, config=cfg)

</div>

</div>

where

- <a href="/python/v0.8.4/syside/PrinterConfig.md" class="reference internal" title="syside.PrinterConfig"><span class="pre"><code class="sourceCode python">PrinterConfig</code></span></a> controls the text formatting options.

- <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions"><span class="pre"><code class="sourceCode python">FormatOptions</code></span></a> controls the textual syntax output options. Both KerML and SysML have multiple ways to write the same models, therefore it contains a lot of configuration options. By default, the options are set to preserve the original source text formatting but can be overridden, e.g. replace all <span class="pre">`redefines`</span> with <span class="pre">`:>>`</span> by setting <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.declaration_redefinition"><span class="pre"><code class="sourceCode python">options.declaration_redefinition.preserve</code></span></a> to <span class="pre">`False`</span> and <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.declaration_redefinition"><span class="pre"><code class="sourceCode python">options.declaration_redefinition.fallback</code></span></a> to <a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside.KwToken"><span class="pre"><code class="sourceCode python">KwToken.Token</code></span></a>.

- <a href="/python/v0.8.4/syside/ModelPrinter.md" class="reference internal" title="syside.ModelPrinter"><span class="pre"><code class="sourceCode python">ModelPrinter</code></span></a> converts model elements into the textual syntax. <a href="/python/v0.8.4/syside/ModelPrinter.md" class="reference internal" title="syside.ModelPrinter.kerml"><span class="pre"><code class="sourceCode python">kerml</code></span></a> and <a href="/python/v0.8.4/syside/ModelPrinter.md" class="reference internal" title="syside.ModelPrinter.sysml"><span class="pre"><code class="sourceCode python">sysml</code></span></a> static methods are used to select the output language of the printer.

- <a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside.pprint"><span class="pre"><code class="sourceCode python">pprint</code></span></a> converts <span class="pre">`element`</span> into the textual syntax in a single function.

If exporting multiple models back into the textual syntax, prefer reusing <a href="/python/v0.8.4/syside/ModelPrinter.md" class="reference internal" title="syside.ModelPrinter"><span class="pre"><code class="sourceCode python">ModelPrinter</code></span></a> for best performance. Note that <a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside.pprint"><span class="pre"><code class="sourceCode python">pprint</code></span></a> has some limitations, see its documentation.

</div>

<div id="s-expressions" class="section">

## S-expressions<a href="#s-expressions" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

<a href="https://en.wikipedia.org/wiki/S-expression" class="reference external" target="_blank">S-expressions</a> can be used to quickly print the model structure to a simple text format. This is most useful for debugging that the model has the expected structure.

<div class="highlight-py notranslate">

<div class="highlight">

    print(syside.sexp(element, print_references=True))

</div>

</div>

See <a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside.sexp"><span class="pre"><code class="sourceCode python">sexp</code></span></a> for more details. Note that <span class="pre">`print_references`</span> is available from Syside v0.6.4, and prints the referenced but not owned element strings for non-owning binary relationships.

</div>

</div>
