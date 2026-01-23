<div id="chainedreferenceaccessor" class="section">

# ChainedReferenceAccessor<a href="#chainedreferenceaccessor" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">ChainedReferenceAccessor</span></span><a href="#syside.ChainedReferenceAccessor" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
<div class="align-center" align="center">

<img src="data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iZ3JhcGh2aXoiIHN0eWxlPSJ3aWR0aDogMTEuNXJlbTtoZWlnaHQ6IDcuMjVyZW07IiB2aWV3Ym94PSIwLjAwIDAuMDAgMTg0LjAwIDExNi4wMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGcgY2xhc3M9ImdyYXBoIiBpZD0iZ3JhcGgwIiB0cmFuc2Zvcm09InNjYWxlKDEgMSkgcm90YXRlKDApIHRyYW5zbGF0ZSg0IDExMikiPgo8dGl0bGU+JTM8L3RpdGxlPgo8ZyBjbGFzcz0ibm9kZSIgaWQ9Im5vZGUxIj4KPHRpdGxlPkNoYWluZWRSZWZlcmVuY2VBY2Nlc3NvcjwvdGl0bGU+CjxnIGlkPSJhX25vZGUxIj48YSBocmVmPSIjc3lzaWRlLkNoYWluZWRSZWZlcmVuY2VBY2Nlc3NvciI+Cjxwb2x5Z29uIHBvaW50cz0iMTc2LC0zNiAwLC0zNiAwLDAgMTc2LDAgMTc2LC0zNiIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtYmctY29sb3IpO3N0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1mZy1jb2xvcik7Ij48L3BvbHlnb24+Cjx0ZXh0IGZvbnQtZmFtaWx5PSJMZXhlbmQiIGZvbnQtc2l6ZT0iMTIuMDAiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1jb2RlLWZnLWNvbG9yKTstLW1kLWdyYXBodml6LWhvdmVyLWNvbG9yOiB2YXIoLS1tZC1ncmFwaHZpei1hLWhvdmVyLWNvbG9yKTsiIHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9Ijg4IiB5PSItMTQuMiI+Q2hhaW5lZFJlZmVyZW5jZUFjY2Vzc29yPC90ZXh0Pgo8dGl0bGU+c3lzaWRlLkNoYWluZWRSZWZlcmVuY2VBY2Nlc3NvcjwvdGl0bGU+PC9hPgo8L2c+CjwvZz4KPGcgY2xhc3M9Im5vZGUiIGlkPSJub2RlMiI+Cjx0aXRsZT5SZWZlcmVuY2VBY2Nlc3NvcjwvdGl0bGU+CjxnIGlkPSJhX25vZGUyIj48YSBocmVmPSIvcHl0aG9uL3YwLjguNC9zeXNpZGUvUmVmZXJlbmNlQWNjZXNzb3IubWQiPgo8cG9seWdvbiBwb2ludHM9IjE1MS41LC0xMDggMjQuNSwtMTA4IDI0LjUsLTcyIDE1MS41LC03MiAxNTEuNSwtMTA4IiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1iZy1jb2xvcik7c3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1ub2RlLWZnLWNvbG9yKTsiPjwvcG9seWdvbj4KPHRleHQgZm9udC1mYW1pbHk9IkxleGVuZCIgZm9udC1zaXplPSIxMi4wMCIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWNvZGUtZmctY29sb3IpOy0tbWQtZ3JhcGh2aXotaG92ZXItY29sb3I6IHZhcigtLW1kLWdyYXBodml6LWEtaG92ZXItY29sb3IpOyIgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iODgiIHk9Ii04Ni4yIj5SZWZlcmVuY2VBY2Nlc3NvcjwvdGV4dD4KPHRpdGxlPnN5c2lkZS5SZWZlcmVuY2VBY2Nlc3NvcjwvdGl0bGU+PC9hPgo8L2c+CjwvZz4KPGcgY2xhc3M9ImVkZ2UiIGlkPSJlZGdlMSI+Cjx0aXRsZT5SZWZlcmVuY2VBY2Nlc3Nvci0mZ3Q7Q2hhaW5lZFJlZmVyZW5jZUFjY2Vzc29yPC90aXRsZT4KPHBhdGggZD0iTTg4LC03MS43Qzg4LC02My45OCA4OCwtNTQuNzEgODgsLTQ2LjExIiBmaWxsPSJub25lIiBzdHlsZT0ic3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1lZGdlLWNvbG9yKTsiIC8+Cjxwb2x5Z29uIHBvaW50cz0iOTEuNSwtNDYuMSA4OCwtMzYuMSA4NC41LC00Ni4xIDkxLjUsLTQ2LjEiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1ncmFwaHZpei1lZGdlLWNvbG9yKTtzdHJva2U6IHZhcigtLW1kLWdyYXBodml6LWVkZ2UtY29sb3IpOyI+PC9wb2x5Z29uPgo8L2c+CjwvZz4KPC9zdmc+" class="graphviz" />

</div>

<span class="sd-summary-text"><span class="nerd-font"></span> Children</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/ChainedFeatureReference.md" class="reference internal" title="syside.ChainedFeatureReference"><span class="pre"><code class="sourceCode python">ChainedFeatureReference</code></span></a>

- <a href="/python/v0.8.4/syside/ChainedTypeReference.md" class="reference internal" title="syside.ChainedTypeReference"><span class="pre"><code class="sourceCode python">ChainedTypeReference</code></span></a>

</div>

<span class="sd-summary-text">Members defined in <a href="#syside.ChainedReferenceAccessor" class="reference internal" title="syside.ChainedReferenceAccessor"><span class="pre"><code class="sourceCode python">ChainedReferenceAccessor</code></span></a> (2 members)</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |  |
|----|----|----|----|
| <span class="nerd-font"></span> | <a href="#syside.ChainedReferenceAccessor.set_chain" class="reference internal" title="syside.ChainedReferenceAccessor.set_chain"><span class="pre"><code class="sourceCode python">set_chain</code></span></a> |  | <span class="pre">`try_set_chain`</span> but instead raises <span class="pre">`ValueError`</span> if this reference cannot be modified. |
| <span class="nerd-font"></span> | <a href="#syside.ChainedReferenceAccessor.try_set_chain" class="reference internal" title="syside.ChainedReferenceAccessor.try_set_chain"><span class="pre"><code class="sourceCode python">try_set_chain</code></span></a> |  | Try changing the referenced <span class="pre">`element`</span> to a chain of <span class="pre">`Features`</span>. Returns <span class="pre">`None`</span> if this reference cannot be modified, otherwise returns a new owned <span class="pre">`Feature`</span> that chains all <span class="pre">`Features`</span> in order. |

</div>

</div>

<span class="sd-summary-text">Members inherited from <a href="/python/v0.8.4/syside/ReferenceAccessor.md" class="reference internal" title="syside.ReferenceAccessor"><span class="pre"><code class="sourceCode python">ReferenceAccessor</code></span></a> (4 members)</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |  |
|----|----|----|----|
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/ReferenceAccessor.md" class="reference internal" title="syside.ReferenceAccessor.element"><span class="pre"><code class="sourceCode python">element</code></span></a> | <span class="pre">`R`</span> | Returns the referenced <span class="pre">`Element`</span>. This may return <span class="pre">`None`</span>, e.g. when reference resolution failed, although in most such cases a placeholder element will be returned instead. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/ReferenceAccessor.md" class="reference internal" title="syside.ReferenceAccessor.modifiable"><span class="pre"><code class="sourceCode python">modifiable</code></span></a> | <span class="pre">`R`</span> | Returns <span class="pre">`True`</span> if this reference can be modified, that is the owning <span class="pre">`Relationship`</span> is an owned member of a <span class="pre">`Namespace`</span>. Calling <span class="pre">`set`</span> methods when <span class="pre">`modifiable`</span>` `<span class="pre">`==`</span>` `<span class="pre">`False`</span> will raise <span class="pre">`ValueError`</span>. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/ReferenceAccessor.md" class="reference internal" title="syside.ReferenceAccessor.set"><span class="pre"><code class="sourceCode python"><span class="bu">set</span></code></span></a> |  | <span class="pre">`try_set`</span> but instead raises <span class="pre">`ValueError`</span> if this reference cannot be modified. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/ReferenceAccessor.md" class="reference internal" title="syside.ReferenceAccessor.try_set"><span class="pre"><code class="sourceCode python">try_set</code></span></a> |  | Try changing the referenced <span class="pre">`element`</span>. Returns <span class="pre">`None`</span> if this reference cannot be modified, otherwise returns <span class="pre">`element`</span> argument. |

</div>

</div>

<span class="nerd-font"></span> **Methods**

<span class="sig-name descname"><span class="pre">set_chain</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">Sequence</span><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature"><span class="pre">syside.Feature</span></a><span class="p"><span class="pre">\]</span></span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature"><span class="pre">syside.Feature</span></a></span></span><a href="#syside.ChainedReferenceAccessor.set_chain" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
<span class="pre">`try_set_chain`</span> but instead raises <span class="pre">`ValueError`</span> if this reference cannot be modified.

<span class="sig-name descname"><span class="pre">try_set_chain</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">Sequence</span><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature"><span class="pre">syside.Feature</span></a><span class="p"><span class="pre">\]</span></span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature"><span class="pre">syside.Feature</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span></span></span><a href="#syside.ChainedReferenceAccessor.try_set_chain" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Try changing the referenced <span class="pre">`element`</span> to a chain of <span class="pre">`Features`</span>. Returns <span class="pre">`None`</span> if this reference cannot be modified, otherwise returns a new owned <span class="pre">`Feature`</span> that chains all <span class="pre">`Features`</span> in order.

</div>
