<div id="argumentsaccessor" class="section">

# ArgumentsAccessor<a href="#argumentsaccessor" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">ArgumentsAccessor</span></span><a href="#syside.ArgumentsAccessor" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
<div class="align-center" align="center">

<img src="data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iZ3JhcGh2aXoiIHN0eWxlPSJ3aWR0aDogOC43NXJlbTtoZWlnaHQ6IDcuMjVyZW07IiB2aWV3Ym94PSIwLjAwIDAuMDAgMTQwLjAwIDExNi4wMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGcgY2xhc3M9ImdyYXBoIiBpZD0iZ3JhcGgwIiB0cmFuc2Zvcm09InNjYWxlKDEgMSkgcm90YXRlKDApIHRyYW5zbGF0ZSg0IDExMikiPgo8dGl0bGU+JTM8L3RpdGxlPgo8ZyBjbGFzcz0ibm9kZSIgaWQ9Im5vZGUxIj4KPHRpdGxlPkFyZ3VtZW50c0FjY2Vzc29yPC90aXRsZT4KPGcgaWQ9ImFfbm9kZTEiPjxhIGhyZWY9IiNzeXNpZGUuQXJndW1lbnRzQWNjZXNzb3IiPgo8cG9seWdvbiBwb2ludHM9IjEzMiwtMzYgMCwtMzYgMCwwIDEzMiwwIDEzMiwtMzYiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1ncmFwaHZpei1ub2RlLWJnLWNvbG9yKTtzdHJva2U6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtZmctY29sb3IpOyI+PC9wb2x5Z29uPgo8dGV4dCBmb250LWZhbWlseT0iTGV4ZW5kIiBmb250LXNpemU9IjEyLjAwIiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtY29kZS1mZy1jb2xvcik7LS1tZC1ncmFwaHZpei1ob3Zlci1jb2xvcjogdmFyKC0tbWQtZ3JhcGh2aXotYS1ob3Zlci1jb2xvcik7IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSI2NiIgeT0iLTE0LjIiPkFyZ3VtZW50c0FjY2Vzc29yPC90ZXh0Pgo8dGl0bGU+c3lzaWRlLkFyZ3VtZW50c0FjY2Vzc29yPC90aXRsZT48L2E+CjwvZz4KPC9nPgo8ZyBjbGFzcz0ibm9kZSIgaWQ9Im5vZGUyIj4KPHRpdGxlPkxhenlJdGVyYXRvcjwvdGl0bGU+CjxnIGlkPSJhX25vZGUyIj48YSBocmVmPSIvcHl0aG9uL3YwLjguNC9zeXNpZGUvTGF6eUl0ZXJhdG9yLm1kIj4KPHBvbHlnb24gcG9pbnRzPSIxMTAuNSwtMTA4IDIxLjUsLTEwOCAyMS41LC03MiAxMTAuNSwtNzIgMTEwLjUsLTEwOCIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtYmctY29sb3IpO3N0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1mZy1jb2xvcik7Ij48L3BvbHlnb24+Cjx0ZXh0IGZvbnQtZmFtaWx5PSJMZXhlbmQiIGZvbnQtc2l6ZT0iMTIuMDAiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1jb2RlLWZnLWNvbG9yKTstLW1kLWdyYXBodml6LWhvdmVyLWNvbG9yOiB2YXIoLS1tZC1ncmFwaHZpei1hLWhvdmVyLWNvbG9yKTsiIHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjY2IiB5PSItODYuMiI+TGF6eUl0ZXJhdG9yPC90ZXh0Pgo8dGl0bGU+c3lzaWRlLkxhenlJdGVyYXRvcjwvdGl0bGU+PC9hPgo8L2c+CjwvZz4KPGcgY2xhc3M9ImVkZ2UiIGlkPSJlZGdlMSI+Cjx0aXRsZT5MYXp5SXRlcmF0b3ItJmd0O0FyZ3VtZW50c0FjY2Vzc29yPC90aXRsZT4KPHBhdGggZD0iTTY2LC03MS43QzY2LC02My45OCA2NiwtNTQuNzEgNjYsLTQ2LjExIiBmaWxsPSJub25lIiBzdHlsZT0ic3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1lZGdlLWNvbG9yKTsiIC8+Cjxwb2x5Z29uIHBvaW50cz0iNjkuNSwtNDYuMSA2NiwtMzYuMSA2Mi41LC00Ni4xIDY5LjUsLTQ2LjEiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1ncmFwaHZpei1lZGdlLWNvbG9yKTtzdHJva2U6IHZhcigtLW1kLWdyYXBodml6LWVkZ2UtY29sb3IpOyI+PC9wb2x5Z29uPgo8L2c+CjwvZz4KPC9zdmc+" class="graphviz" />

</div>

<span class="sd-summary-text">Members defined in <a href="#syside.ArgumentsAccessor" class="reference internal" title="syside.ArgumentsAccessor"><span class="pre"><code class="sourceCode python">ArgumentsAccessor</code></span></a> (1 member)</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |  |
|----|----|----|----|
| <span class="nerd-font"></span> | <a href="#syside.ArgumentsAccessor.append" class="reference internal" title="syside.ArgumentsAccessor.append"><span class="pre"><code class="sourceCode python">append</code></span></a> |  | Append a new invocation <span class="pre">`argument`</span>. This takes care of constructing any intermediate elements. |

</div>

</div>

<span class="sd-summary-text">Members inherited from <a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre"><code class="sourceCode python">LazyIterator</code></span></a> (7 members)</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |  |
|----|----|----|----|
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator.__bool__"><span class="pre"><code class="sourceCode python"><span class="fu">__bool__</span></code></span></a> |  | Returns <span class="pre">`True`</span> if this range is not empty. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator.__getitem__"><span class="pre"><code class="sourceCode python"><span class="fu">__getitem__</span></code></span></a> |  | Get value at index, This is computed lazily. Throws <span class="pre">`IndexError`</span> on out of bounds. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator.at"><span class="pre"><code class="sourceCode python">at</code></span></a> |  | Get value at index. This is computed lazily. Returns <span class="pre">`None`</span> for out of bounds index. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator.collect"><span class="pre"><code class="sourceCode python">collect</code></span></a> |  | Collect all items into a <span class="pre">`list`</span>. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator.count"><span class="pre"><code class="sourceCode python">count</code></span></a> |  | Count the number of items in this range. This is computed lazily. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator.empty"><span class="pre"><code class="sourceCode python">empty</code></span></a> |  | Check if this range is empty. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator.for_each"><span class="pre"><code class="sourceCode python">for_each</code></span></a> |  | Lazily visit each item in this range. Visitation is stopped on returning <span class="pre">`False`</span> or <span class="pre">`VisitAction.Stop`</span>; |

</div>

</div>

<span class="nerd-font"></span> **Methods**

<span class="sig-name descname"><span class="pre">append</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">syside.ArgumentsAccessor.append.M</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/FeatureValue.md" class="reference internal" title="syside.FeatureValue"><span class="pre">syside.FeatureValue</span></a><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">syside.ArgumentsAccessor.append.M</span><span class="p"><span class="pre">\]</span></span></span></span><a href="#syside.ArgumentsAccessor.append" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Append a new invocation <span class="pre">`argument`</span>. This takes care of constructing any intermediate elements.

Returns a pair of (<span class="pre">`feature_value`</span>, <span class="pre">`argument`</span>).

<span class="sig-name descname"><span class="pre">append</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">type</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.ArgumentsAccessor.append.M</span><span class="p"><span class="pre">\]</span></span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/FeatureValue.md" class="reference internal" title="syside.FeatureValue"><span class="pre">syside.FeatureValue</span></a><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">syside.ArgumentsAccessor.append.M</span><span class="p"><span class="pre">\]</span></span></span></span>  
Append a new invocation <span class="pre">`argument`</span> with the corresponding type. This takes care of constructing any intermediate elements.

Returns a pair of (<span class="pre">`feature_value`</span>, <span class="pre">`argument`</span>).

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/InstantiationExpression.md" class="reference internal" title="syside.InstantiationExpression"><span class="pre"><code class="sourceCode python">syside.InstantiationExpression</code></span></a>

  - <a href="/python/v0.8.4/syside/InstantiationExpression.md" class="reference internal" title="syside.InstantiationExpression.arguments"><span class="pre"><code class="sourceCode python">arguments</code></span></a>

</div>

</div>
