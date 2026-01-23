<div id="environment" class="section">

# Environment<a href="#environment" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">Environment</span></span><a href="#syside.Environment" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Standard library environment for use with user models.

<div class="align-center" align="center">

<img src="data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iZ3JhcGh2aXoiIHN0eWxlPSJ3aWR0aDogNi4wNjI1cmVtO2hlaWdodDogMi43NXJlbTsiIHZpZXdib3g9IjAuMDAgMC4wMCA5Ny4wMCA0NC4wMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGcgY2xhc3M9ImdyYXBoIiBpZD0iZ3JhcGgwIiB0cmFuc2Zvcm09InNjYWxlKDEgMSkgcm90YXRlKDApIHRyYW5zbGF0ZSg0IDQwKSI+Cjx0aXRsZT4lMzwvdGl0bGU+CjxnIGNsYXNzPSJub2RlIiBpZD0ibm9kZTEiPgo8dGl0bGU+RW52aXJvbm1lbnQ8L3RpdGxlPgo8ZyBpZD0iYV9ub2RlMSI+PGEgaHJlZj0iI3N5c2lkZS5FbnZpcm9ubWVudCI+Cjxwb2x5Z29uIHBvaW50cz0iODksLTM2IDAsLTM2IDAsMCA4OSwwIDg5LC0zNiIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtYmctY29sb3IpO3N0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1mZy1jb2xvcik7Ij48L3BvbHlnb24+Cjx0ZXh0IGZvbnQtZmFtaWx5PSJMZXhlbmQiIGZvbnQtc2l6ZT0iMTIuMDAiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1jb2RlLWZnLWNvbG9yKTstLW1kLWdyYXBodml6LWhvdmVyLWNvbG9yOiB2YXIoLS1tZC1ncmFwaHZpei1hLWhvdmVyLWNvbG9yKTsiIHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjQ0LjUiIHk9Ii0xNC4yIj5FbnZpcm9ubWVudDwvdGV4dD4KPHRpdGxlPnN5c2lkZS5FbnZpcm9ubWVudDwvdGl0bGU+PC9hPgo8L2c+CjwvZz4KPC9nPgo8L3N2Zz4=" class="graphviz" />

</div>

<span class="sd-summary-text">Members defined in <a href="#syside.Environment" class="reference internal" title="syside.Environment"><span class="pre"><code class="sourceCode python">Environment</code></span></a> (4 members)</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |  |
|----|----|----|----|
| <span class="nerd-font"></span> | <a href="#syside.Environment.from_documents" class="reference internal" title="syside.Environment.from_documents"><span class="pre"><code class="sourceCode python">from_documents</code></span></a> | <span class="pre">`RW`</span> | Construct the environment from the given documents. |
| <span class="nerd-font"></span> | <a href="#syside.Environment.from_stdlib_files" class="reference internal" title="syside.Environment.from_stdlib_files"><span class="pre"><code class="sourceCode python">from_stdlib_files</code></span></a> | <span class="pre">`RW`</span> | Construct the environment from the given stdlib files. |
| <span class="nerd-font"></span> | <a href="#syside.Environment.get_default" class="reference internal" title="syside.Environment.get_default"><span class="pre"><code class="sourceCode python">get_default</code></span></a> | <span class="pre">`RW`</span> | Get a default constructed standard library environment. This will only be executed on the first call, and any subsequent calls will return a cached value. Standard library environment is cached based on the assumption that it **WILL NOT** change during runtime, saving resources when loading other models. |
| <span class="nerd-font"></span> | <a href="#syside.Environment.index" class="reference internal" title="syside.Environment.index"><span class="pre"><code class="sourceCode python">index</code></span></a> |  | Returns a copy of the environment index for use in dependent models. A copy is required so that dependent models do not affect this environment and other dependent models. |

</div>

</div>

<span class="nerd-font"></span> **Attributes**

*<span class="pre">classmethod</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">from_documents</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">documents</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">Iterable</span><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/SharedMutex.md" class="reference internal" title="syside.SharedMutex"><span class="pre">syside.SharedMutex</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Document.md" class="reference internal" title="syside.Document"><span class="pre">syside.Document</span></a><span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">\]</span></span></span>*, *<span class="n"><span class="pre">index</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/StaticIndex.md" class="reference internal" title="syside.StaticIndex"><span class="pre">syside.StaticIndex</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">None</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="#syside.Environment" class="reference internal" title="syside.Environment"><span class="pre">syside.Environment</span></a></span></span><a href="#syside.Environment.from_documents" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Construct the environment from the given documents.

Parameters<span class="colon">:</span>  
- **documents** – The documents from which to construct the SysMLv2 environment.

- **index** – The index to be used in models. If <span class="pre">`None`</span>, creates a new index. If not <span class="pre">`None`</span>, clones the index to avoid mutating the argument.

*<span class="pre">classmethod</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">from_stdlib_files</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">stdlib_files</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">list</span><span class="p"><span class="pre">\[</span></span><span class="pre">pathlib.Path</span><span class="p"><span class="pre">\]</span></span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="#syside.Environment" class="reference internal" title="syside.Environment"><span class="pre">syside.Environment</span></a></span></span><a href="#syside.Environment.from_stdlib_files" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Construct the environment from the given stdlib files.

Parameters<span class="colon">:</span>  
**stdlib_files** – The paths to SysMLv2 or KerML files representing the stdlib. These files must have correct file extensions (<span class="pre">`.sysml`</span> or <span class="pre">`.kerml`</span>).

*<span class="pre">classmethod</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">get_default</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="#syside.Environment" class="reference internal" title="syside.Environment"><span class="pre">syside.Environment</span></a></span></span><a href="#syside.Environment.get_default" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Get a default constructed standard library environment. This will only be executed on the first call, and any subsequent calls will return a cached value. Standard library environment is cached based on the assumption that it **WILL NOT** change during runtime, saving resources when loading other models.

<span class="nerd-font"></span> **Methods**

<span class="sig-name descname"><span class="pre">index</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="/python/v0.8.4/syside/StaticIndex.md" class="reference internal" title="syside.StaticIndex"><span class="pre">syside.StaticIndex</span></a></span></span><a href="#syside.Environment.index" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Returns a copy of the environment index for use in dependent models. A copy is required so that dependent models do not affect this environment and other dependent models.

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside"><span class="pre"><code class="sourceCode python">syside</code></span></a>

  - <a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside.load_model"><span class="pre"><code class="sourceCode python">load_model</code></span></a>

  - <a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside.try_load_model"><span class="pre"><code class="sourceCode python">try_load_model</code></span></a>

- <a href="/python/v0.8.4/syside/BaseModel.md" class="reference internal" title="syside.BaseModel"><span class="pre"><code class="sourceCode python">syside.BaseModel</code></span></a>

  - <a href="/python/v0.8.4/syside/BaseModel.md" class="reference internal" title="syside.BaseModel.environment"><span class="pre"><code class="sourceCode python">environment</code></span></a>

  - <a href="/python/v0.8.4/syside/BaseModel.md" class="reference internal" title="syside.BaseModel.to_environment"><span class="pre"><code class="sourceCode python">to_environment</code></span></a>

- <a href="/python/v0.8.4/syside/json//README.md" class="reference internal" title="syside.json"><span class="pre"><code class="sourceCode python">syside.json</code></span></a>

  - <a href="/python/v0.8.4/syside/json//README.md" class="reference internal" title="syside.json.loads"><span class="pre"><code class="sourceCode python">loads</code></span></a>

- <a href="/python/v0.8.4/syside/preview//README.md" class="reference internal" title="syside.preview"><span class="pre"><code class="sourceCode python">syside.preview</code></span></a>

  - <a href="/python/v0.8.4/syside/preview//README.md" class="reference internal" title="syside.preview.empty_model"><span class="pre"><code class="sourceCode python">empty_model</code></span></a>

  - <a href="/python/v0.8.4/syside/preview//README.md" class="reference internal" title="syside.preview.open_model"><span class="pre"><code class="sourceCode python">open_model</code></span></a>

  - <a href="/python/v0.8.4/syside/preview//README.md" class="reference internal" title="syside.preview.open_model_unlocked"><span class="pre"><code class="sourceCode python">open_model_unlocked</code></span></a>

</div>

</div>
