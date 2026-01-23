<div id="containerview" class="section">

# ContainerView<a href="#containerview" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">ContainerView</span></span><a href="#syside.ContainerView" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
An immutable view into a native random-access container. Implements Sequence protocol.

<div class="align-center" align="center">

<img src="data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iZ3JhcGh2aXoiIHN0eWxlPSJ3aWR0aDogNi44MTI1cmVtO2hlaWdodDogMi43NXJlbTsiIHZpZXdib3g9IjAuMDAgMC4wMCAxMDkuMDAgNDQuMDAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxnIGNsYXNzPSJncmFwaCIgaWQ9ImdyYXBoMCIgdHJhbnNmb3JtPSJzY2FsZSgxIDEpIHJvdGF0ZSgwKSB0cmFuc2xhdGUoNCA0MCkiPgo8dGl0bGU+JTM8L3RpdGxlPgo8ZyBjbGFzcz0ibm9kZSIgaWQ9Im5vZGUxIj4KPHRpdGxlPkNvbnRhaW5lclZpZXc8L3RpdGxlPgo8ZyBpZD0iYV9ub2RlMSI+PGEgaHJlZj0iI3N5c2lkZS5Db250YWluZXJWaWV3Ij4KPHBvbHlnb24gcG9pbnRzPSIxMDEsLTM2IDAsLTM2IDAsMCAxMDEsMCAxMDEsLTM2IiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1iZy1jb2xvcik7c3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1ub2RlLWZnLWNvbG9yKTsiPjwvcG9seWdvbj4KPHRleHQgZm9udC1mYW1pbHk9IkxleGVuZCIgZm9udC1zaXplPSIxMi4wMCIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWNvZGUtZmctY29sb3IpOy0tbWQtZ3JhcGh2aXotaG92ZXItY29sb3I6IHZhcigtLW1kLWdyYXBodml6LWEtaG92ZXItY29sb3IpOyIgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iNTAuNSIgeT0iLTE0LjIiPkNvbnRhaW5lclZpZXc8L3RleHQ+Cjx0aXRsZT5zeXNpZGUuQ29udGFpbmVyVmlldzwvdGl0bGU+PC9hPgo8L2c+CjwvZz4KPC9nPgo8L3N2Zz4=" class="graphviz" />

</div>

<span class="sd-summary-text"><span class="nerd-font"></span> Children</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/DependencyEnds.md" class="reference internal" title="syside.DependencyEnds"><span class="pre"><code class="sourceCode python">DependencyEnds</code></span></a>

- <a href="/python/v0.8.4/syside/RelationshipBody.md" class="reference internal" title="syside.RelationshipBody"><span class="pre"><code class="sourceCode python">RelationshipBody</code></span></a>

</div>

<span class="sd-summary-text">Members defined in <a href="#syside.ContainerView" class="reference internal" title="syside.ContainerView"><span class="pre"><code class="sourceCode python">ContainerView</code></span></a> (11 members)</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |  |
|----|----|----|----|
| <span class="nerd-font"></span> | <a href="#syside.ContainerView.__bool__" class="reference internal" title="syside.ContainerView.__bool__"><span class="pre"><code class="sourceCode python"><span class="fu">__bool__</span></code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.ContainerView.__contains__" class="reference internal" title="syside.ContainerView.__contains__"><span class="pre"><code class="sourceCode python"><span class="fu">__contains__</span></code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.ContainerView.__getitem__" class="reference internal" title="syside.ContainerView.__getitem__"><span class="pre"><code class="sourceCode python"><span class="fu">__getitem__</span></code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.ContainerView.__iter__" class="reference internal" title="syside.ContainerView.__iter__"><span class="pre"><code class="sourceCode python"><span class="fu">__iter__</span></code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.ContainerView.__len__" class="reference internal" title="syside.ContainerView.__len__"><span class="pre"><code class="sourceCode python"><span class="fu">__len__</span></code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.ContainerView.__reversed__" class="reference internal" title="syside.ContainerView.__reversed__"><span class="pre"><code class="sourceCode python"><span class="fu">__reversed__</span></code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.ContainerView.__str__" class="reference internal" title="syside.ContainerView.__str__"><span class="pre"><code class="sourceCode python"><span class="fu">__str__</span></code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.ContainerView.at" class="reference internal" title="syside.ContainerView.at"><span class="pre"><code class="sourceCode python">at</code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.ContainerView.count" class="reference internal" title="syside.ContainerView.count"><span class="pre"><code class="sourceCode python">count</code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.ContainerView.empty" class="reference internal" title="syside.ContainerView.empty"><span class="pre"><code class="sourceCode python">empty</code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.ContainerView.index" class="reference internal" title="syside.ContainerView.index"><span class="pre"><code class="sourceCode python">index</code></span></a> |  |  |

</div>

</div>

<span class="nerd-font"></span> **Methods**

<span class="sig-name descname"><span class="pre">\_\_bool\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">bool</span></span></span><a href="#syside.ContainerView.__bool__" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">\_\_contains\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">value</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">object</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">bool</span></span></span><a href="#syside.ContainerView.__contains__" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">\_\_getitem\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">index</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">int</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">syside.T</span></span></span><a href="#syside.ContainerView.__getitem__" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">\_\_getitem\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">index</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">slice</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">list</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.T</span><span class="p"><span class="pre">\]</span></span></span></span>  

<span class="sig-name descname"><span class="pre">\_\_iter\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">Iterator</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.T</span><span class="p"><span class="pre">\]</span></span></span></span><a href="#syside.ContainerView.__iter__" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">\_\_len\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">int</span></span></span><a href="#syside.ContainerView.__len__" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">\_\_reversed\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">Iterator</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.T</span><span class="p"><span class="pre">\]</span></span></span></span><a href="#syside.ContainerView.__reversed__" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">\_\_str\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">str</span></span></span><a href="#syside.ContainerView.__str__" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">at</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">int</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">syside.T</span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span></span></span><a href="#syside.ContainerView.at" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">at</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg0</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">int</span></span>*, *<span class="n"><span class="pre">arg1</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">syside.T</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">syside.T</span></span></span>  

<span class="sig-name descname"><span class="pre">count</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">value</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">syside.T</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">int</span></span></span><a href="#syside.ContainerView.count" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">empty</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">bool</span></span></span><a href="#syside.ContainerView.empty" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">index</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">value</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">syside.T</span></span>*, *<span class="n"><span class="pre">start</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">int</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">0</span></span>*, *<span class="n"><span class="pre">stop</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">int</span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">None</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">int</span></span></span><a href="#syside.ContainerView.index" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/AnnotatingElement.md" class="reference internal" title="syside.AnnotatingElement"><span class="pre"><code class="sourceCode python">syside.AnnotatingElement</code></span></a>

  - <a href="/python/v0.8.4/syside/AnnotatingElement.md" class="reference internal" title="syside.AnnotatingElement.annotated_elements"><span class="pre"><code class="sourceCode python">annotated_elements</code></span></a>

  - <a href="/python/v0.8.4/syside/AnnotatingElement.md" class="reference internal" title="syside.AnnotatingElement.annotations"><span class="pre"><code class="sourceCode python">annotations</code></span></a>

  - <a href="/python/v0.8.4/syside/AnnotatingElement.md" class="reference internal" title="syside.AnnotatingElement.owned_annotating_relationships"><span class="pre"><code class="sourceCode python">owned_annotating_relationships</code></span></a>

- <a href="/python/v0.8.4/syside/Annotation.md" class="reference internal" title="syside.Annotation"><span class="pre"><code class="sourceCode python">syside.Annotation</code></span></a>

  - <a href="/python/v0.8.4/syside/Annotation.md" class="reference internal" title="syside.Annotation.sources"><span class="pre"><code class="sourceCode python">sources</code></span></a>

  - <a href="/python/v0.8.4/syside/Annotation.md" class="reference internal" title="syside.Annotation.targets"><span class="pre"><code class="sourceCode python">targets</code></span></a>

- <a href="/python/v0.8.4/syside/CompilationReport.md" class="reference internal" title="syside.CompilationReport"><span class="pre"><code class="sourceCode python">syside.CompilationReport</code></span></a>

  - <a href="/python/v0.8.4/syside/CompilationReport.md" class="reference internal" title="syside.CompilationReport.diagnostics"><span class="pre"><code class="sourceCode python">diagnostics</code></span></a>

- <a href="/python/v0.8.4/syside/Dependency.md" class="reference internal" title="syside.Dependency"><span class="pre"><code class="sourceCode python">syside.Dependency</code></span></a>

  - <a href="/python/v0.8.4/syside/Dependency.md" class="reference internal" title="syside.Dependency.sources"><span class="pre"><code class="sourceCode python">sources</code></span></a>

  - <a href="/python/v0.8.4/syside/Dependency.md" class="reference internal" title="syside.Dependency.targets"><span class="pre"><code class="sourceCode python">targets</code></span></a>

- <a href="/python/v0.8.4/syside/DeserializedModel.md" class="reference internal" title="syside.DeserializedModel"><span class="pre"><code class="sourceCode python">syside.DeserializedModel</code></span></a>

  - <a href="/python/v0.8.4/syside/DeserializedModel.md" class="reference internal" title="syside.DeserializedModel.pending_references"><span class="pre"><code class="sourceCode python">pending_references</code></span></a>

- <a href="/python/v0.8.4/syside/Diagnostic.md" class="reference internal" title="syside.Diagnostic"><span class="pre"><code class="sourceCode python">syside.Diagnostic</code></span></a>

  - <a href="/python/v0.8.4/syside/Diagnostic.md" class="reference internal" title="syside.Diagnostic.related_information"><span class="pre"><code class="sourceCode python">related_information</code></span></a>

- <a href="/python/v0.8.4/syside/DiagnosticResults.md" class="reference internal" title="syside.DiagnosticResults"><span class="pre"><code class="sourceCode python">syside.DiagnosticResults</code></span></a>

  - <a href="/python/v0.8.4/syside/DiagnosticResults.md" class="reference internal" title="syside.DiagnosticResults.parser"><span class="pre"><code class="sourceCode python">parser</code></span></a>

  - <a href="/python/v0.8.4/syside/DiagnosticResults.md" class="reference internal" title="syside.DiagnosticResults.sema"><span class="pre"><code class="sourceCode python">sema</code></span></a>

  - <a href="/python/v0.8.4/syside/DiagnosticResults.md" class="reference internal" title="syside.DiagnosticResults.validation"><span class="pre"><code class="sourceCode python">validation</code></span></a>

- <a href="/python/v0.8.4/syside/ExecutionResult.md" class="reference internal" title="syside.ExecutionResult"><span class="pre"><code class="sourceCode python">syside.ExecutionResult</code></span></a>

  - <a href="/python/v0.8.4/syside/ExecutionResult.md" class="reference internal" title="syside.ExecutionResult.diagnostics"><span class="pre"><code class="sourceCode python">diagnostics</code></span></a>

  - <a href="/python/v0.8.4/syside/ExecutionResult.md" class="reference internal" title="syside.ExecutionResult.documents"><span class="pre"><code class="sourceCode python">documents</code></span></a>

  - <a href="/python/v0.8.4/syside/ExecutionResult.md" class="reference internal" title="syside.ExecutionResult.times"><span class="pre"><code class="sourceCode python">times</code></span></a>

- <a href="/python/v0.8.4/syside/Import.md" class="reference internal" title="syside.Import"><span class="pre"><code class="sourceCode python">syside.Import</code></span></a>

  - <a href="/python/v0.8.4/syside/Import.md" class="reference internal" title="syside.Import.sources"><span class="pre"><code class="sourceCode python">sources</code></span></a>

  - <a href="/python/v0.8.4/syside/Import.md" class="reference internal" title="syside.Import.targets"><span class="pre"><code class="sourceCode python">targets</code></span></a>

- <a href="/python/v0.8.4/syside/Membership.md" class="reference internal" title="syside.Membership"><span class="pre"><code class="sourceCode python">syside.Membership</code></span></a>

  - <a href="/python/v0.8.4/syside/Membership.md" class="reference internal" title="syside.Membership.sources"><span class="pre"><code class="sourceCode python">sources</code></span></a>

  - <a href="/python/v0.8.4/syside/Membership.md" class="reference internal" title="syside.Membership.targets"><span class="pre"><code class="sourceCode python">targets</code></span></a>

- <a href="/python/v0.8.4/syside/MetadataFeature.md" class="reference internal" title="syside.MetadataFeature"><span class="pre"><code class="sourceCode python">syside.MetadataFeature</code></span></a>

  - <a href="/python/v0.8.4/syside/MetadataFeature.md" class="reference internal" title="syside.MetadataFeature.annotated_elements"><span class="pre"><code class="sourceCode python">annotated_elements</code></span></a>

  - <a href="/python/v0.8.4/syside/MetadataFeature.md" class="reference internal" title="syside.MetadataFeature.annotations"><span class="pre"><code class="sourceCode python">annotations</code></span></a>

  - <a href="/python/v0.8.4/syside/MetadataFeature.md" class="reference internal" title="syside.MetadataFeature.owned_annotating_relationships"><span class="pre"><code class="sourceCode python">owned_annotating_relationships</code></span></a>

- <a href="/python/v0.8.4/syside/MetadataUsage.md" class="reference internal" title="syside.MetadataUsage"><span class="pre"><code class="sourceCode python">syside.MetadataUsage</code></span></a>

  - <a href="/python/v0.8.4/syside/MetadataUsage.md" class="reference internal" title="syside.MetadataUsage.annotated_elements"><span class="pre"><code class="sourceCode python">annotated_elements</code></span></a>

  - <a href="/python/v0.8.4/syside/MetadataUsage.md" class="reference internal" title="syside.MetadataUsage.annotations"><span class="pre"><code class="sourceCode python">annotations</code></span></a>

  - <a href="/python/v0.8.4/syside/MetadataUsage.md" class="reference internal" title="syside.MetadataUsage.owned_annotating_relationships"><span class="pre"><code class="sourceCode python">owned_annotating_relationships</code></span></a>

- <a href="/python/v0.8.4/syside/Relationship.md" class="reference internal" title="syside.Relationship"><span class="pre"><code class="sourceCode python">syside.Relationship</code></span></a>

  - <a href="/python/v0.8.4/syside/Relationship.md" class="reference internal" title="syside.Relationship.sources"><span class="pre"><code class="sourceCode python">sources</code></span></a>

  - <a href="/python/v0.8.4/syside/Relationship.md" class="reference internal" title="syside.Relationship.targets"><span class="pre"><code class="sourceCode python">targets</code></span></a>

- <a href="/python/v0.8.4/syside/Stdlib.md" class="reference internal" title="syside.Stdlib"><span class="pre"><code class="sourceCode python">syside.Stdlib</code></span></a>

  - <a href="/python/v0.8.4/syside/Stdlib.md" class="reference internal" title="syside.Stdlib.implicit_supertypes"><span class="pre"><code class="sourceCode python">implicit_supertypes</code></span></a>

  - <a href="/python/v0.8.4/syside/Stdlib.md" class="reference internal" title="syside.Stdlib.metaclasses"><span class="pre"><code class="sourceCode python">metaclasses</code></span></a>

  - <a href="/python/v0.8.4/syside/Stdlib.md" class="reference internal" title="syside.Stdlib.operator_functions"><span class="pre"><code class="sourceCode python">operator_functions</code></span></a>

- <a href="/python/v0.8.4/syside/ide/SemanticTokensBuilder.md" class="reference internal" title="syside.ide.SemanticTokensBuilder"><span class="pre"><code class="sourceCode python">syside.ide.SemanticTokensBuilder</code></span></a>

  - <a href="/python/v0.8.4/syside/ide/SemanticTokensBuilder.md" class="reference internal" title="syside.ide.SemanticTokensBuilder.absolute_tokens"><span class="pre"><code class="sourceCode python">absolute_tokens</code></span></a>

  - <a href="/python/v0.8.4/syside/ide/SemanticTokensBuilder.md" class="reference internal" title="syside.ide.SemanticTokensBuilder.delta_tokens"><span class="pre"><code class="sourceCode python">delta_tokens</code></span></a>

  - <a href="/python/v0.8.4/syside/ide/SemanticTokensBuilder.md" class="reference internal" title="syside.ide.SemanticTokensBuilder.previous_tokens"><span class="pre"><code class="sourceCode python">previous_tokens</code></span></a>

- <a href="/python/v0.8.4/syside/ide/lsp/SemanticTokens.md" class="reference internal" title="syside.ide.lsp.SemanticTokens"><span class="pre"><code class="sourceCode python">syside.ide.lsp.SemanticTokens</code></span></a>

  - <a href="/python/v0.8.4/syside/ide/lsp/SemanticTokens.md" class="reference internal" title="syside.ide.lsp.SemanticTokens.data"><span class="pre"><code class="sourceCode python">data</code></span></a>

- <a href="/python/v0.8.4/syside/ide/lsp/SemanticTokensDelta.md" class="reference internal" title="syside.ide.lsp.SemanticTokensDelta"><span class="pre"><code class="sourceCode python">syside.ide.lsp.SemanticTokensDelta</code></span></a>

  - <a href="/python/v0.8.4/syside/ide/lsp/SemanticTokensDelta.md" class="reference internal" title="syside.ide.lsp.SemanticTokensDelta.edits"><span class="pre"><code class="sourceCode python">edits</code></span></a>

- <a href="/python/v0.8.4/syside/ide/lsp/SemanticTokensEdit.md" class="reference internal" title="syside.ide.lsp.SemanticTokensEdit"><span class="pre"><code class="sourceCode python">syside.ide.lsp.SemanticTokensEdit</code></span></a>

  - <a href="/python/v0.8.4/syside/ide/lsp/SemanticTokensEdit.md" class="reference internal" title="syside.ide.lsp.SemanticTokensEdit.data"><span class="pre"><code class="sourceCode python">data</code></span></a>

</div>

</div>
