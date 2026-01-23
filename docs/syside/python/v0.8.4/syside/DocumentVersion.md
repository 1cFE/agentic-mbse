<div id="documentversion" class="section">

# DocumentVersion<a href="#documentversion" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">DocumentVersion</span></span><a href="#syside.DocumentVersion" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
<div class="align-center" align="center">

<img src="data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iZ3JhcGh2aXoiIHN0eWxlPSJ3aWR0aDogNy45Mzc1cmVtO2hlaWdodDogMi43NXJlbTsiIHZpZXdib3g9IjAuMDAgMC4wMCAxMjcuMDAgNDQuMDAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxnIGNsYXNzPSJncmFwaCIgaWQ9ImdyYXBoMCIgdHJhbnNmb3JtPSJzY2FsZSgxIDEpIHJvdGF0ZSgwKSB0cmFuc2xhdGUoNCA0MCkiPgo8dGl0bGU+JTM8L3RpdGxlPgo8ZyBjbGFzcz0ibm9kZSIgaWQ9Im5vZGUxIj4KPHRpdGxlPkRvY3VtZW50VmVyc2lvbjwvdGl0bGU+CjxnIGlkPSJhX25vZGUxIj48YSBocmVmPSIjc3lzaWRlLkRvY3VtZW50VmVyc2lvbiI+Cjxwb2x5Z29uIHBvaW50cz0iMTE5LC0zNiAwLC0zNiAwLDAgMTE5LDAgMTE5LC0zNiIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtYmctY29sb3IpO3N0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1mZy1jb2xvcik7Ij48L3BvbHlnb24+Cjx0ZXh0IGZvbnQtZmFtaWx5PSJMZXhlbmQiIGZvbnQtc2l6ZT0iMTIuMDAiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1jb2RlLWZnLWNvbG9yKTstLW1kLWdyYXBodml6LWhvdmVyLWNvbG9yOiB2YXIoLS1tZC1ncmFwaHZpei1hLWhvdmVyLWNvbG9yKTsiIHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjU5LjUiIHk9Ii0xNC4yIj5Eb2N1bWVudFZlcnNpb248L3RleHQ+Cjx0aXRsZT5zeXNpZGUuRG9jdW1lbnRWZXJzaW9uPC90aXRsZT48L2E+CjwvZz4KPC9nPgo8L2c+Cjwvc3ZnPg==" class="graphviz" />

</div>

<span class="sd-summary-text">Members defined in <a href="#syside.DocumentVersion" class="reference internal" title="syside.DocumentVersion"><span class="pre"><code class="sourceCode python">DocumentVersion</code></span></a> (5 members)</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |  |
|----|----|----|----|
| <span class="nerd-font"></span> | <a href="#syside.DocumentVersion.sema" class="reference internal" title="syside.DocumentVersion.sema"><span class="pre"><code class="sourceCode python">sema</code></span></a> | <span class="pre">`RW`</span> | The sema version of the <span class="pre">`document`</span>. This is separate from <span class="pre">`source`</span> since <span class="pre">`sema`</span> may be recomputed after one of the dependencies has changed. May also be reset to 0 on source changes. Most similar to patch version in semantic versioning scheme. |
| <span class="nerd-font"></span> | <a href="#syside.DocumentVersion.source" class="reference internal" title="syside.DocumentVersion.source"><span class="pre"><code class="sourceCode python">source</code></span></a> | <span class="pre">`RW`</span> | The version of the source <span class="pre">`TextDocument`</span> the document was built from. Always 0 if there is no actual source associated. Takes priority over <span class="pre">`sema`</span>. |
| <span class="nerd-font"></span> | <a href="#syside.DocumentVersion.__init__" class="reference internal" title="syside.DocumentVersion.__init__"><span class="pre"><code class="sourceCode python"><span class="fu">__init__</span></code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.DocumentVersion.__int__" class="reference internal" title="syside.DocumentVersion.__int__"><span class="pre"><code class="sourceCode python"><span class="fu">__int__</span></code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.DocumentVersion.__str__" class="reference internal" title="syside.DocumentVersion.__str__"><span class="pre"><code class="sourceCode python"><span class="fu">__str__</span></code></span></a> |  |  |

</div>

</div>

<span class="nerd-font"></span> **Attributes**

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">sema</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">int</span>*<a href="#syside.DocumentVersion.sema" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
The sema version of the <span class="pre">`document`</span>. This is separate from <span class="pre">`source`</span> since <span class="pre">`sema`</span> may be recomputed after one of the dependencies has changed. May also be reset to 0 on source changes. Most similar to patch version in semantic versioning scheme.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">source</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">int</span>*<a href="#syside.DocumentVersion.source" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
The version of the source <span class="pre">`TextDocument`</span> the document was built from. Always 0 if there is no actual source associated. Takes priority over <span class="pre">`sema`</span>.

<span class="nerd-font"></span> **Methods**

<span class="sig-name descname"><span class="pre">\_\_init\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">source</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">int</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">0</span></span>*, *<span class="n"><span class="pre">sema</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">int</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">0</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span><a href="#syside.DocumentVersion.__init__" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">\_\_int\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">int</span></span></span><a href="#syside.DocumentVersion.__int__" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">\_\_str\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">str</span></span></span><a href="#syside.DocumentVersion.__str__" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/BasicDocument.md" class="reference internal" title="syside.BasicDocument"><span class="pre"><code class="sourceCode python">syside.BasicDocument</code></span></a>

  - <a href="/python/v0.8.4/syside/BasicDocument.md" class="reference internal" title="syside.BasicDocument.version"><span class="pre"><code class="sourceCode python">version</code></span></a>

</div>

</div>
