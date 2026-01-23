<div id="serdereport" class="section">

# SerdeReport<a href="#serdereport" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">SerdeReport</span></span><span class="sig-paren">\[</span>*<span class="n"><span class="pre">T</span></span>*<span class="sig-paren">\]</span><a href="#syside.SerdeReport" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
(De)Serialization report containing emitted messages.

<div class="align-center" align="center">

<img src="data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iZ3JhcGh2aXoiIHN0eWxlPSJ3aWR0aDogNi4xMjVyZW07aGVpZ2h0OiAyLjc1cmVtOyIgdmlld2JveD0iMC4wMCAwLjAwIDk4LjAwIDQ0LjAwIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPgo8ZyBjbGFzcz0iZ3JhcGgiIGlkPSJncmFwaDAiIHRyYW5zZm9ybT0ic2NhbGUoMSAxKSByb3RhdGUoMCkgdHJhbnNsYXRlKDQgNDApIj4KPHRpdGxlPiUzPC90aXRsZT4KPGcgY2xhc3M9Im5vZGUiIGlkPSJub2RlMSI+Cjx0aXRsZT5TZXJkZVJlcG9ydDwvdGl0bGU+CjxnIGlkPSJhX25vZGUxIj48YSBocmVmPSIjc3lzaWRlLlNlcmRlUmVwb3J0Ij4KPHBvbHlnb24gcG9pbnRzPSI5MCwtMzYgMCwtMzYgMCwwIDkwLDAgOTAsLTM2IiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1iZy1jb2xvcik7c3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1ub2RlLWZnLWNvbG9yKTsiPjwvcG9seWdvbj4KPHRleHQgZm9udC1mYW1pbHk9IkxleGVuZCIgZm9udC1zaXplPSIxMi4wMCIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWNvZGUtZmctY29sb3IpOy0tbWQtZ3JhcGh2aXotaG92ZXItY29sb3I6IHZhcigtLW1kLWdyYXBodml6LWEtaG92ZXItY29sb3IpOyIgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iNDUiIHk9Ii0xNC4yIj5TZXJkZVJlcG9ydDwvdGV4dD4KPHRpdGxlPnN5c2lkZS5TZXJkZVJlcG9ydDwvdGl0bGU+PC9hPgo8L2c+CjwvZz4KPC9nPgo8L3N2Zz4=" class="graphviz" />

</div>

<span class="sd-summary-text">Members defined in <a href="#syside.SerdeReport" class="reference internal" title="syside.SerdeReport"><span class="pre"><code class="sourceCode python">SerdeReport</code></span></a> (4 members)</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |  |
|----|----|----|----|
| <span class="nerd-font"></span> | <a href="#syside.SerdeReport.messages" class="reference internal" title="syside.SerdeReport.messages"><span class="pre"><code class="sourceCode python">messages</code></span></a> | <span class="pre">`R`</span> |  |
| <span class="nerd-font"></span> | <a href="#syside.SerdeReport.__bool__" class="reference internal" title="syside.SerdeReport.__bool__"><span class="pre"><code class="sourceCode python"><span class="fu">__bool__</span></code></span></a> |  | Returns <span class="pre">`True`</span> if none of the messages are errors. |
| <span class="nerd-font"></span> | <a href="#syside.SerdeReport.__str__" class="reference internal" title="syside.SerdeReport.__str__"><span class="pre"><code class="sourceCode python"><span class="fu">__str__</span></code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.SerdeReport.passed" class="reference internal" title="syside.SerdeReport.passed"><span class="pre"><code class="sourceCode python">passed</code></span></a> |  | Check if the report has no errors. If <span class="pre">`warnings_as_errors`</span> is <span class="pre">`True`</span>, also check if it contains no warnings. |

</div>

</div>

<span class="nerd-font"></span> **Attributes**

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">messages</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">list</span><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/SerdeMessage.md" class="reference internal" title="syside.SerdeMessage"><span class="pre">syside.SerdeMessage</span></a><span class="p"><span class="pre">\[</span></span><span class="pre">syside.T</span><span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">\]</span></span>*<a href="#syside.SerdeReport.messages" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="nerd-font"></span> **Methods**

<span class="sig-name descname"><span class="pre">\_\_bool\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">bool</span></span></span><a href="#syside.SerdeReport.__bool__" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Returns <span class="pre">`True`</span> if none of the messages are errors.

<span class="sig-name descname"><span class="pre">\_\_str\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">str</span></span></span><a href="#syside.SerdeReport.__str__" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">passed</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">warnings_as_errors</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">False</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">bool</span></span></span><a href="#syside.SerdeReport.passed" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Check if the report has no errors. If <span class="pre">`warnings_as_errors`</span> is <span class="pre">`True`</span>, also check if it contains no warnings.

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside"><span class="pre"><code class="sourceCode python">syside</code></span></a>

  - <a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside.deserialize"><span class="pre"><code class="sourceCode python">deserialize</code></span></a>

  - <a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside.serialize"><span class="pre"><code class="sourceCode python">serialize</code></span></a>

- <a href="/python/v0.8.4/syside/DeserializedModel.md" class="reference internal" title="syside.DeserializedModel"><span class="pre"><code class="sourceCode python">syside.DeserializedModel</code></span></a>

  - <a href="/python/v0.8.4/syside/DeserializedModel.md" class="reference internal" title="syside.DeserializedModel.link"><span class="pre"><code class="sourceCode python">link</code></span></a>

- <a href="/python/v0.8.4/syside/Deserializer.md" class="reference internal" title="syside.Deserializer"><span class="pre"><code class="sourceCode python">syside.Deserializer</code></span></a>

  - <a href="/python/v0.8.4/syside/Deserializer.md" class="reference internal" title="syside.Deserializer.accept"><span class="pre"><code class="sourceCode python">accept</code></span></a>

- <a href="/python/v0.8.4/syside/Serializer.md" class="reference internal" title="syside.Serializer"><span class="pre"><code class="sourceCode python">syside.Serializer</code></span></a>

  - <a href="/python/v0.8.4/syside/Serializer.md" class="reference internal" title="syside.Serializer.accept"><span class="pre"><code class="sourceCode python">accept</code></span></a>

- <a href="/python/v0.8.4/syside/json//README.md" class="reference internal" title="syside.json"><span class="pre"><code class="sourceCode python">syside.json</code></span></a>

  - <a href="/python/v0.8.4/syside/json//README.md" class="reference internal" title="syside.json.DeserializationReport"><span class="pre"><code class="sourceCode python">DeserializationReport</code></span></a>

- <a href="/python/v0.8.4/syside/json/SerializationError.md" class="reference internal" title="syside.json.SerializationError"><span class="pre"><code class="sourceCode python">syside.json.SerializationError</code></span></a>

  - <a href="/python/v0.8.4/syside/json/SerializationError.md" class="reference internal" title="syside.json.SerializationError.report"><span class="pre"><code class="sourceCode python">report</code></span></a>

</div>

</div>
