<div id="diagnosticresults" class="section">

# DiagnosticResults<a href="#diagnosticresults" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">DiagnosticResults</span></span><a href="#syside.DiagnosticResults" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
<div class="align-center" align="center">

<img src="data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iZ3JhcGh2aXoiIHN0eWxlPSJ3aWR0aDogNy45Mzc1cmVtO2hlaWdodDogMi43NXJlbTsiIHZpZXdib3g9IjAuMDAgMC4wMCAxMjcuMDAgNDQuMDAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxnIGNsYXNzPSJncmFwaCIgaWQ9ImdyYXBoMCIgdHJhbnNmb3JtPSJzY2FsZSgxIDEpIHJvdGF0ZSgwKSB0cmFuc2xhdGUoNCA0MCkiPgo8dGl0bGU+JTM8L3RpdGxlPgo8ZyBjbGFzcz0ibm9kZSIgaWQ9Im5vZGUxIj4KPHRpdGxlPkRpYWdub3N0aWNSZXN1bHRzPC90aXRsZT4KPGcgaWQ9ImFfbm9kZTEiPjxhIGhyZWY9IiNzeXNpZGUuRGlhZ25vc3RpY1Jlc3VsdHMiPgo8cG9seWdvbiBwb2ludHM9IjExOSwtMzYgMCwtMzYgMCwwIDExOSwwIDExOSwtMzYiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1ncmFwaHZpei1ub2RlLWJnLWNvbG9yKTtzdHJva2U6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtZmctY29sb3IpOyI+PC9wb2x5Z29uPgo8dGV4dCBmb250LWZhbWlseT0iTGV4ZW5kIiBmb250LXNpemU9IjEyLjAwIiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtY29kZS1mZy1jb2xvcik7LS1tZC1ncmFwaHZpei1ob3Zlci1jb2xvcjogdmFyKC0tbWQtZ3JhcGh2aXotYS1ob3Zlci1jb2xvcik7IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSI1OS41IiB5PSItMTQuMiI+RGlhZ25vc3RpY1Jlc3VsdHM8L3RleHQ+Cjx0aXRsZT5zeXNpZGUuRGlhZ25vc3RpY1Jlc3VsdHM8L3RpdGxlPjwvYT4KPC9nPgo8L2c+CjwvZz4KPC9zdmc+" class="graphviz" />

</div>

<span class="sd-summary-text">Members defined in <a href="#syside.DiagnosticResults" class="reference internal" title="syside.DiagnosticResults"><span class="pre"><code class="sourceCode python">DiagnosticResults</code></span></a> (6 members)</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |  |
|----|----|----|----|
| <span class="nerd-font"></span> | <a href="#syside.DiagnosticResults.empty" class="reference internal" title="syside.DiagnosticResults.empty"><span class="pre"><code class="sourceCode python">empty</code></span></a> | <span class="pre">`R`</span> | Returns True if all diagnostic categories are empty |
| <span class="nerd-font"></span> | <a href="#syside.DiagnosticResults.parser" class="reference internal" title="syside.DiagnosticResults.parser"><span class="pre"><code class="sourceCode python">parser</code></span></a> | <span class="pre">`R`</span> |  |
| <span class="nerd-font"></span> | <a href="#syside.DiagnosticResults.sema" class="reference internal" title="syside.DiagnosticResults.sema"><span class="pre"><code class="sourceCode python">sema</code></span></a> | <span class="pre">`R`</span> |  |
| <span class="nerd-font"></span> | <a href="#syside.DiagnosticResults.validation" class="reference internal" title="syside.DiagnosticResults.validation"><span class="pre"><code class="sourceCode python">validation</code></span></a> | <span class="pre">`R`</span> |  |
| <span class="nerd-font"></span> | <a href="#syside.DiagnosticResults.__bool__" class="reference internal" title="syside.DiagnosticResults.__bool__"><span class="pre"><code class="sourceCode python"><span class="fu">__bool__</span></code></span></a> |  | Returns True if there are no Error diagnostics |
| <span class="nerd-font"></span> | <a href="#syside.DiagnosticResults.passed" class="reference internal" title="syside.DiagnosticResults.passed"><span class="pre"><code class="sourceCode python">passed</code></span></a> |  |  |

</div>

</div>

<span class="nerd-font"></span> **Attributes**

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">empty</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*<a href="#syside.DiagnosticResults.empty" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Returns True if all diagnostic categories are empty

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">parser</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/ContainerView.md" class="reference internal" title="syside.ContainerView"><span class="pre">syside.ContainerView</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Diagnostic.md" class="reference internal" title="syside.Diagnostic"><span class="pre">syside.Diagnostic</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.DiagnosticResults.parser" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">sema</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/ContainerView.md" class="reference internal" title="syside.ContainerView"><span class="pre">syside.ContainerView</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Diagnostic.md" class="reference internal" title="syside.Diagnostic"><span class="pre">syside.Diagnostic</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.DiagnosticResults.sema" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">validation</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/ContainerView.md" class="reference internal" title="syside.ContainerView"><span class="pre">syside.ContainerView</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Diagnostic.md" class="reference internal" title="syside.Diagnostic"><span class="pre">syside.Diagnostic</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.DiagnosticResults.validation" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="nerd-font"></span> **Methods**

<span class="sig-name descname"><span class="pre">\_\_bool\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">bool</span></span></span><a href="#syside.DiagnosticResults.__bool__" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Returns True if there are no Error diagnostics

<span class="sig-name descname"><span class="pre">passed</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">warnings_as_errors</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">False</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">bool</span></span></span><a href="#syside.DiagnosticResults.passed" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/ExecutionResult.md" class="reference internal" title="syside.ExecutionResult"><span class="pre"><code class="sourceCode python">syside.ExecutionResult</code></span></a>

  - <a href="/python/v0.8.4/syside/ExecutionResult.md" class="reference internal" title="syside.ExecutionResult.diagnostics"><span class="pre"><code class="sourceCode python">diagnostics</code></span></a>

</div>

</div>
