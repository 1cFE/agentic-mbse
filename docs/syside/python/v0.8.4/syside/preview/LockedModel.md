<div id="lockedmodel" class="section">

# LockedModel<a href="#lockedmodel" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">LockedModel</span></span><a href="#syside.preview.LockedModel" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
A SysML v2/KerML model interface. Top level elements (typically Packages) can be accessed through the <span class="pre">`lookup`</span> method, e.g. <span class="pre">`model.lookup("PackageName")`</span>. To create a new top level package use the <span class="pre">`new_top_level_package`</span> method.

The object is invalidated once <span class="pre">`unlock`</span>ed, either explicitly or by leaving the outermost <span class="pre">`with`</span>-block when used as a context manager.

Note that <span class="pre">`LockedModel`</span> is generally not intended to be instantiated directly. Ideally, use either <span class="pre">`open_model`</span> or <span class="pre">`empty_model`</span>. Alternatively, instantiate <span class="pre">`UnlockedModel`</span> and use <span class="pre">`UnlockedModel.lock`</span>.

<div class="highlight-python notranslate">

<div class="highlight">

    model : LockedModel = empty_model()

    ## Alternatively
    unlocked_model = open_model_unlocked(...)

    model : LockedModel = unlocked_model.lock()

</div>

</div>

<div class="align-center" align="center">

<img src="data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iZ3JhcGh2aXoiIHN0eWxlPSJ3aWR0aDogNi4zMTI1cmVtO2hlaWdodDogMi43NXJlbTsiIHZpZXdib3g9IjAuMDAgMC4wMCAxMDEuMDAgNDQuMDAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxnIGNsYXNzPSJncmFwaCIgaWQ9ImdyYXBoMCIgdHJhbnNmb3JtPSJzY2FsZSgxIDEpIHJvdGF0ZSgwKSB0cmFuc2xhdGUoNCA0MCkiPgo8dGl0bGU+JTM8L3RpdGxlPgo8ZyBjbGFzcz0ibm9kZSIgaWQ9Im5vZGUxIj4KPHRpdGxlPkxvY2tlZE1vZGVsPC90aXRsZT4KPGcgaWQ9ImFfbm9kZTEiPjxhIGhyZWY9IiNzeXNpZGUucHJldmlldy5Mb2NrZWRNb2RlbCI+Cjxwb2x5Z29uIHBvaW50cz0iOTMsLTM2IDAsLTM2IDAsMCA5MywwIDkzLC0zNiIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtYmctY29sb3IpO3N0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1mZy1jb2xvcik7Ij48L3BvbHlnb24+Cjx0ZXh0IGZvbnQtZmFtaWx5PSJMZXhlbmQiIGZvbnQtc2l6ZT0iMTIuMDAiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1jb2RlLWZnLWNvbG9yKTstLW1kLWdyYXBodml6LWhvdmVyLWNvbG9yOiB2YXIoLS1tZC1ncmFwaHZpei1hLWhvdmVyLWNvbG9yKTsiIHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjQ2LjUiIHk9Ii0xNC4yIj5Mb2NrZWRNb2RlbDwvdGV4dD4KPHRpdGxlPnN5c2lkZS5wcmV2aWV3LkxvY2tlZE1vZGVsPC90aXRsZT48L2E+CjwvZz4KPC9nPgo8L2c+Cjwvc3ZnPg==" class="graphviz" />

</div>

<span class="sd-summary-text">Members defined in <a href="#syside.preview.LockedModel" class="reference internal" title="syside.preview.LockedModel"><span class="pre"><code class="sourceCode python">LockedModel</code></span></a> (9 members)</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |  |
|----|----|----|----|
| <span class="nerd-font"></span> | <a href="#syside.preview.LockedModel.diagnostics" class="reference internal" title="syside.preview.LockedModel.diagnostics"><span class="pre"><code class="sourceCode python">diagnostics</code></span></a> | <span class="pre">`R`</span> | Diagnostics generated when the model was loaded. |
| <span class="nerd-font"></span> | <a href="#syside.preview.LockedModel.lookup" class="reference internal" title="syside.preview.LockedModel.lookup"><span class="pre"><code class="sourceCode python">lookup</code></span></a> |  | If <span class="pre">`path`</span> is empty, yields the (unique) top-level owned member element with name <span class="pre">`name`</span> if it exists, otherwise returns <span class="pre">`None`</span>. Note that elements other than owned member elements, such as imported or inherited ones, are not taken into account. |
| <span class="nerd-font"></span> | <a href="#syside.preview.LockedModel.new_top_level_library_package" class="reference internal" title="syside.preview.LockedModel.new_top_level_library_package"><span class="pre"><code class="sourceCode python">new_top_level_library_package</code></span></a> |  | Creates a (named) new top level package. |
| <span class="nerd-font"></span> | <a href="#syside.preview.LockedModel.new_top_level_package" class="reference internal" title="syside.preview.LockedModel.new_top_level_package"><span class="pre"><code class="sourceCode python">new_top_level_package</code></span></a> |  | Creates a (named) new top level package. |
| <span class="nerd-font"></span> | <a href="#syside.preview.LockedModel.top_elements" class="reference internal" title="syside.preview.LockedModel.top_elements"><span class="pre"><code class="sourceCode python">top_elements</code></span></a> |  | Yields all top level named elements (typically Packages) that are owned members of a root namespace in the model. Note that imported members are not taken into account. |
| <span class="nerd-font"></span> | <a href="#syside.preview.LockedModel.top_elements_from" class="reference internal" title="syside.preview.LockedModel.top_elements_from"><span class="pre"><code class="sourceCode python">top_elements_from</code></span></a> |  | Yields top level owned member elements (typically Packages) loaded from the specified path(or from files below that path if it is a directory). Note that imported members are not taken into account. |
| <span class="nerd-font"></span> | <a href="#syside.preview.LockedModel.top_named_elements" class="reference internal" title="syside.preview.LockedModel.top_named_elements"><span class="pre"><code class="sourceCode python">top_named_elements</code></span></a> |  | Yields all named top level named elements (typically Packages) that are owned members of a root namespace in the model, together with (one of) their names. Note that imported members are not taken into account. |
| <span class="nerd-font"></span> | <a href="#syside.preview.LockedModel.top_names" class="reference internal" title="syside.preview.LockedModel.top_names"><span class="pre"><code class="sourceCode python">top_names</code></span></a> |  | Yields names of all top level named elements (typically Packages) that are owned members of a root namespace in the model. Note that imported members are not taken into account. |
| <span class="nerd-font"></span> | <a href="#syside.preview.LockedModel.unlock" class="reference internal" title="syside.preview.LockedModel.unlock"><span class="pre"><code class="sourceCode python">unlock</code></span></a> |  | Unlocks the model, freeing it up for others to lock. |

</div>

</div>

<span class="nerd-font"></span> **Attributes**

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">diagnostics</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/Diagnostics.md" class="reference internal" title="syside.Diagnostics"><span class="pre">syside.Diagnostics</span></a>*<a href="#syside.preview.LockedModel.diagnostics" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Diagnostics generated when the model was loaded.

<span class="nerd-font"></span> **Methods**

<span class="sig-name descname"><span class="pre">lookup</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">name</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="o"><span class="pre">\*</span></span><span class="n"><span class="pre">path</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element"><span class="pre">syside.Element</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span></span></span><a href="#syside.preview.LockedModel.lookup" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
If <span class="pre">`path`</span> is empty, yields the (unique) top-level owned member element with name <span class="pre">`name`</span> if it exists, otherwise returns <span class="pre">`None`</span>. Note that elements other than owned member elements, such as imported or inherited ones, are not taken into account.

Otherwise <span class="pre">`.lookup(name,`</span>` `<span class="pre">`name,`</span>` `<span class="pre">`path1,`</span>` `<span class="pre">`...,`</span>` `<span class="pre">`pathn)`</span> is equal to <span class="pre">`.lookup(name).lookup(path1).[...].lookup(pathn)`</span>, unless any intermediate value is <span class="pre">`None`</span>. If any intermediate value is <span class="pre">`None`</span> the whole expression evaluates to <span class="pre">`None`</span>.

Parameters<span class="colon">:</span>  
- **name** – name of element to find

- **path** – sequence of names to (recursively) lookup

Returns<span class="colon">:</span>  
(unique) element with name <span class="pre">`name`</span> or None (if not found)

Raises<span class="colon">:</span>  
- **RuntimeError** – if used after unlocking

- **TypeError** – if trying to recursively look-up into a non-<span class="pre">`Namespace`</span> element.

- **NameError** – if the name is ambiguous.

<span class="sig-name descname"><span class="pre">new_top_level_library_package</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">name</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="/python/v0.8.4/syside/LibraryPackage.md" class="reference internal" title="syside.LibraryPackage"><span class="pre">syside.LibraryPackage</span></a></span></span><a href="#syside.preview.LockedModel.new_top_level_library_package" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Creates a (named) new top level package.

Parameters<span class="colon">:</span>  
**name** – name of the new package

Returns<span class="colon">:</span>  
a new <span class="pre">`syside.LibraryPackage`</span> named <span class="pre">`name`</span> (in a new global namespace)

Raises<span class="colon">:</span>  
**RuntimeError** – if used after unlocking

<span class="sig-name descname"><span class="pre">new_top_level_package</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">name</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="/python/v0.8.4/syside/Package.md" class="reference internal" title="syside.Package"><span class="pre">syside.Package</span></a></span></span><a href="#syside.preview.LockedModel.new_top_level_package" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Creates a (named) new top level package.

Parameters<span class="colon">:</span>  
**name** – name of the new package

Returns<span class="colon">:</span>  
a new <span class="pre">`syside.Package`</span> named <span class="pre">`name`</span> (in a new global namespace)

Raises<span class="colon">:</span>  
**RuntimeError** – if used after unlocking

<span class="sig-name descname"><span class="pre">top_elements</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">Iterator</span><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element"><span class="pre">syside.Element</span></a><span class="p"><span class="pre">\]</span></span></span></span><a href="#syside.preview.LockedModel.top_elements" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Yields all top level named elements (typically Packages) that are owned members of a root namespace in the model. Note that imported members are not taken into account.

Returns<span class="colon">:</span>  
sequence of top level elements

Raises<span class="colon">:</span>  
**RuntimeError** – if used after unlocking

<span class="sig-name descname"><span class="pre">top_elements_from</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">path</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">pathlib.Path</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">Iterator</span><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element"><span class="pre">syside.Element</span></a><span class="p"><span class="pre">\]</span></span></span></span><a href="#syside.preview.LockedModel.top_elements_from" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Yields top level owned member elements (typically Packages) loaded from the specified path(or from files below that path if it is a directory). Note that imported members are not taken into account.

Parameters<span class="colon">:</span>  
**path** – source file or directory path to return elements loaded from

Returns<span class="colon">:</span>  
sequence of (top) model elements loaded from source file(s) matching <span class="pre">`path`</span>

Raises<span class="colon">:</span>  
**RuntimeError** – if used after unlocking

<span class="sig-name descname"><span class="pre">top_named_elements</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">Iterator</span><span class="p"><span class="pre">\[</span></span><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><span class="pre">str</span><span class="p"><span class="pre">,</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element"><span class="pre">syside.Element</span></a><span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">\]</span></span></span></span><a href="#syside.preview.LockedModel.top_named_elements" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Yields all named top level named elements (typically Packages) that are owned members of a root namespace in the model, together with (one of) their names. Note that imported members are not taken into account.

Prefers name over short name.

Returns<span class="colon">:</span>  
sequence of (name, element) pairs of named top level elements

Raises<span class="colon">:</span>  
**RuntimeError** – if used after unlocking

<span class="sig-name descname"><span class="pre">top_names</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">Iterator</span><span class="p"><span class="pre">\[</span></span><span class="pre">str</span><span class="p"><span class="pre">\]</span></span></span></span><a href="#syside.preview.LockedModel.top_names" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Yields names of all top level named elements (typically Packages) that are owned members of a root namespace in the model. Note that imported members are not taken into account.

Prefers name over short name.

Returns<span class="colon">:</span>  
sequence of names of named top level elements

Raises<span class="colon">:</span>  
**RuntimeError** – if used after unlocking

<span class="sig-name descname"><span class="pre">unlock</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="/python/v0.8.4/syside/preview/UnlockedModel.md" class="reference internal" title="syside.preview.UnlockedModel"><span class="pre">syside.preview.UnlockedModel</span></a></span></span><a href="#syside.preview.LockedModel.unlock" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Unlocks the model, freeing it up for others to lock.

Returns<span class="colon">:</span>  
<span class="pre">`UnlockedModel`</span> that can be used to re-acquire access to the model

Raises<span class="colon">:</span>  
**RuntimeError** – if used after unlocking

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/preview//README.md" class="reference internal" title="syside.preview"><span class="pre"><code class="sourceCode python">syside.preview</code></span></a>

  - <a href="/python/v0.8.4/syside/preview//README.md" class="reference internal" title="syside.preview.empty_model"><span class="pre"><code class="sourceCode python">empty_model</code></span></a>

  - <a href="/python/v0.8.4/syside/preview//README.md" class="reference internal" title="syside.preview.open_model"><span class="pre"><code class="sourceCode python">open_model</code></span></a>

</div>

</div>
