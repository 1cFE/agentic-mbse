<div id="jsonreader" class="section">

# JsonReader<a href="#jsonreader" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">JsonReader</span></span><a href="#syside.JsonReader" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Unbound reader for JSON deserialization

<div class="align-center" align="center">

<img src="data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iZ3JhcGh2aXoiIHN0eWxlPSJ3aWR0aDogNS44NzVyZW07aGVpZ2h0OiAyLjc1cmVtOyIgdmlld2JveD0iMC4wMCAwLjAwIDk0LjAwIDQ0LjAwIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPgo8ZyBjbGFzcz0iZ3JhcGgiIGlkPSJncmFwaDAiIHRyYW5zZm9ybT0ic2NhbGUoMSAxKSByb3RhdGUoMCkgdHJhbnNsYXRlKDQgNDApIj4KPHRpdGxlPiUzPC90aXRsZT4KPGcgY2xhc3M9Im5vZGUiIGlkPSJub2RlMSI+Cjx0aXRsZT5Kc29uUmVhZGVyPC90aXRsZT4KPGcgaWQ9ImFfbm9kZTEiPjxhIGhyZWY9IiNzeXNpZGUuSnNvblJlYWRlciI+Cjxwb2x5Z29uIHBvaW50cz0iODYsLTM2IDAsLTM2IDAsMCA4NiwwIDg2LC0zNiIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtYmctY29sb3IpO3N0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1mZy1jb2xvcik7Ij48L3BvbHlnb24+Cjx0ZXh0IGZvbnQtZmFtaWx5PSJMZXhlbmQiIGZvbnQtc2l6ZT0iMTIuMDAiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1jb2RlLWZnLWNvbG9yKTstLW1kLWdyYXBodml6LWhvdmVyLWNvbG9yOiB2YXIoLS1tZC1ncmFwaHZpei1hLWhvdmVyLWNvbG9yKTsiIHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjQzIiB5PSItMTQuMiI+SnNvblJlYWRlcjwvdGV4dD4KPHRpdGxlPnN5c2lkZS5Kc29uUmVhZGVyPC90aXRsZT48L2E+CjwvZz4KPC9nPgo8L2c+Cjwvc3ZnPg==" class="graphviz" />

</div>

<span class="sd-summary-text">Members defined in <a href="#syside.JsonReader" class="reference internal" title="syside.JsonReader"><span class="pre"><code class="sourceCode python">JsonReader</code></span></a> (3 members)</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |  |
|----|----|----|----|
| <span class="nerd-font"></span> | <a href="#syside.JsonReader.is_bound" class="reference internal" title="syside.JsonReader.is_bound"><span class="pre"><code class="sourceCode python">is_bound</code></span></a> | <span class="pre">`R`</span> | Whether there currently is a reader bound to this resource. |
| <span class="nerd-font"></span> | <a href="#syside.JsonReader.__init__" class="reference internal" title="syside.JsonReader.__init__"><span class="pre"><code class="sourceCode python"><span class="fu">__init__</span></code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.JsonReader.bind" class="reference internal" title="syside.JsonReader.bind"><span class="pre"><code class="sourceCode python">bind</code></span></a> |  | Bind a serialized JSON string for reading. |

</div>

</div>

<span class="nerd-font"></span> **Attributes**

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">is_bound</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*<a href="#syside.JsonReader.is_bound" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Whether there currently is a reader bound to this resource.

<span class="nerd-font"></span> **Methods**

<span class="sig-name descname"><span class="pre">\_\_init\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span><a href="#syside.JsonReader.__init__" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">bind</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">s</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="#syside.JsonReader" class="reference internal" title="syside.JsonReader"><span class="pre">syside.JsonReader</span></a></span></span><a href="#syside.JsonReader.bind" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Bind a serialized JSON string for reading.

Note that only one reader can be bound at a time, binding again will raise <span class="pre">`ValueError`</span>. Suggested usage is through a context manager:

<div class="highlight-python notranslate">

<div class="highlight">

    with reader.bind(json_str) as json:
        model, report = deserializer.accept(json, syside.DESERIALIZE_STANDARD)

</div>

</div>

The reader will attempt to infer the root node as:

1.  The first <span class="pre">`Namespace`</span> (not subtype) without an owning relationship.

2.  The first <span class="pre">`Element`</span> that has no serialized owning related element or owning relationship, starting from the first element in the JSON array, and following owning elements up.

3.  The first element in the array otherwise.

</div>
