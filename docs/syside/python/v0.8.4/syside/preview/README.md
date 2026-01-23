<div id="module-syside.preview" class="section">

<span id="preview-labs"></span>

# preview <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">Labs</span><a href="#module-syside.preview" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

Module implementing various proposals for how to make the Syside API more convenient and easier to pick up.

<div id="index" class="section">

## <span class="nerd-font"></span> Index<a href="#index" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

<span class="sd-summary-text"><span class="nerd-font"></span> **Classes** <a href="#syside-preview-classes-table" class="reference internal"><span class="std std-ref"></span></a></span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |
|----|----|----|
| <a href="/python/v0.8.4/syside/preview/LockedModel.md" class="reference internal" title="syside.preview.LockedModel"><span class="pre"><code class="sourceCode python">LockedModel</code></span></a> |  | A SysML v2/KerML model interface. Top level elements (typically Packages) can be accessed through the <span class="pre">`lookup`</span> method, e.g. <span class="pre">`model.lookup("PackageName")`</span>. To create a new top level package use the <span class="pre">`new_top_level_package`</span> method. |
| <a href="/python/v0.8.4/syside/preview/UnlockedModel.md" class="reference internal" title="syside.preview.UnlockedModel"><span class="pre"><code class="sourceCode python">UnlockedModel</code></span></a> |  | A SysML v2/KerML model that needs to be <span class="pre">`lock`</span>ed before access. |

</div>

</div>

<span class="sd-summary-text"><span class="nerd-font"></span> **Functions** <a href="#syside-preview-functions-table" class="reference internal"><span class="std std-ref"></span></a></span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |
|----|----|----|
| <a href="#syside.preview.empty_model" class="reference internal" title="syside.preview.empty_model"><span class="pre"><code class="sourceCode python">empty_model</code></span></a> |  | Opens an empty model, loading only standard library elements (unless <span class="pre">`include_stdlib=False`</span>). |
| <a href="#syside.preview.open_model" class="reference internal" title="syside.preview.open_model"><span class="pre"><code class="sourceCode python">open_model</code></span></a> |  | Opens a model stored in <span class="pre">`paths`</span>, which can be given as a (combination of) file and directory paths. By default the model is allowed to generate warnings (<span class="pre">`warnings_as_errors`</span>) but is not allowed to contain errors (<span class="pre">`allow_errors`</span>). |
| <a href="#syside.preview.open_model_unlocked" class="reference internal" title="syside.preview.open_model_unlocked"><span class="pre"><code class="sourceCode python">open_model_unlocked</code></span></a> |  | Opens a model stored in <span class="pre">`paths`</span>, which can be given as a (combination of) file and directory paths. By default the model is allowed to generate warnings (<span class="pre">`warnings_as_errors`</span>) but is not allowed to contain errors (<span class="pre">`allow_errors`</span>). |

</div>

</div>

</div>

------------------------------------------------------------------------

<div id="functions" class="section">

## <span class="nerd-font">󰊕</span> Functions<a href="#functions" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

<span class="sig-name descname"><span class="pre">empty_model</span></span><span class="sig-paren">(</span>*<span class="o"><span class="pre">\*</span></span>*, *<span class="n"><span class="pre">warnings_as_errors</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">False</span></span>*, *<span class="n"><span class="pre">allow_errors</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">False</span></span>*, *<span class="n"><span class="pre">include_stdlib</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">True</span></span>*, *<span class="n"><span class="pre">environment</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/Environment.md" class="reference internal" title="syside.Environment"><span class="pre">syside.Environment</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">None</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="/python/v0.8.4/syside/preview/LockedModel.md" class="reference internal" title="syside.preview.LockedModel"><span class="pre">syside.preview.LockedModel</span></a></span></span><a href="#syside.preview.empty_model" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Opens an empty model, loading only standard library elements (unless <span class="pre">`include_stdlib=False`</span>).

<span class="pre">`unlock`</span> the returned model before sharing between threads (and re-lock before use), or use a <span class="pre">`with`</span>-block to automatically unlock when exiting the block.

Parameters<span class="colon">:</span>  
- **warnings_as_errors** – if True, warnings are treated errors

- **allow_errors** – if True, tries to return a partial or invalid model even in the presence of errors

- **include_stdlib** – if False, tries to load the model without also loading the SysML v2 standard library

- **environment** – The environment to be used for the model. If this parameter is <span class="pre">`None`</span>, the default environment is used.

Returns<span class="colon">:</span>  
a <span class="pre">`LockableModel`</span> representing an empty model.

<!-- -->

<span class="sig-name descname"><span class="pre">open_model</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">paths</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">pathlib.Path</span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">Iterable</span><span class="p"><span class="pre">\[</span></span><span class="pre">pathlib.Path</span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">str</span><span class="p"><span class="pre">\]</span></span></span>*, *<span class="o"><span class="pre">\*</span></span>*, *<span class="n"><span class="pre">warnings_as_errors</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">False</span></span>*, *<span class="n"><span class="pre">allow_errors</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">False</span></span>*, *<span class="n"><span class="pre">include_stdlib</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">True</span></span>*, *<span class="n"><span class="pre">environment</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/Environment.md" class="reference internal" title="syside.Environment"><span class="pre">syside.Environment</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">None</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="/python/v0.8.4/syside/preview/LockedModel.md" class="reference internal" title="syside.preview.LockedModel"><span class="pre">syside.preview.LockedModel</span></a></span></span><a href="#syside.preview.open_model" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Opens a model stored in <span class="pre">`paths`</span>, which can be given as a (combination of) file and directory paths. By default the model is allowed to generate warnings (<span class="pre">`warnings_as_errors`</span>) but is not allowed to contain errors (<span class="pre">`allow_errors`</span>).

<span class="pre">`unlock`</span> the returned model before sharing between threads (and re-lock before use), or use a <span class="pre">`with`</span>-block to automatically unlock when exiting the block.

Parameters<span class="colon">:</span>  
- **paths** – path or sequence of paths (given as <span class="pre">`str`</span> or <span class="pre">`Path`</span>) of source files, or directories containing source files, to be included in the model

- **warnings_as_errors** – if True, warnings are treated errors

- **allow_errors** – if True, tries to return a partial or invalid model even in the presence of errors

- **include_stdlib** – if False, tries to load the model without also loading the SysML v2 standard library

- **environment** – The environment to be used for the model. If this parameter is <span class="pre">`None`</span>, the default environment is used.

Returns<span class="colon">:</span>  
a <span class="pre">`LockableModel`</span> representing the model loaded from source files given in <span class="pre">`paths`</span>

Raises<span class="colon">:</span>  
<a href="/python/v0.8.4/syside/ModelError.md" class="reference internal" title="syside.ModelError"><strong>syside.ModelError</strong></a> – if model contains errors and <span class="pre">`allow_errors`</span> is False

<!-- -->

<span class="sig-name descname"><span class="pre">open_model_unlocked</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">paths</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">pathlib.Path</span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">Iterable</span><span class="p"><span class="pre">\[</span></span><span class="pre">pathlib.Path</span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">str</span><span class="p"><span class="pre">\]</span></span></span>*, *<span class="o"><span class="pre">\*</span></span>*, *<span class="n"><span class="pre">warnings_as_errors</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">False</span></span>*, *<span class="n"><span class="pre">allow_errors</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">False</span></span>*, *<span class="n"><span class="pre">include_stdlib</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">True</span></span>*, *<span class="n"><span class="pre">environment</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/Environment.md" class="reference internal" title="syside.Environment"><span class="pre">syside.Environment</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">None</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="/python/v0.8.4/syside/preview/UnlockedModel.md" class="reference internal" title="syside.preview.UnlockedModel"><span class="pre">syside.preview.UnlockedModel</span></a></span></span><a href="#syside.preview.open_model_unlocked" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Opens a model stored in <span class="pre">`paths`</span>, which can be given as a (combination of) file and directory paths. By default the model is allowed to generate warnings (<span class="pre">`warnings_as_errors`</span>) but is not allowed to contain errors (<span class="pre">`allow_errors`</span>).

<span class="pre">`lock`</span> the returned model before access

Parameters<span class="colon">:</span>  
- **paths** – path or sequence of paths (given as <span class="pre">`str`</span> or <span class="pre">`Path`</span>) of source files, or directories containing source files, to be included in the model

- **warnings_as_errors** – if True, warnings are treated errors

- **allow_errors** – if True, tries to return a partial or invalid model even in the presence of errors

- **include_stdlib** – if False, tries to load the model without also loading the SysML v2 standard library

- **environment** – The environment to be used for the model. If this parameter is <span class="pre">`None`</span>, the default environment is used.

Returns<span class="colon">:</span>  
an <span class="pre">`UnlockedModel`</span> representing the model loaded from source files given in <span class="pre">`paths`</span>

Raises<span class="colon">:</span>  
<a href="/python/v0.8.4/syside/ModelError.md" class="reference internal" title="syside.ModelError"><strong>syside.ModelError</strong></a> – if model contains errors and <span class="pre">`allow_errors`</span> is False

<div class="toctree-wrapper compound">

</div>

</div>

</div>
