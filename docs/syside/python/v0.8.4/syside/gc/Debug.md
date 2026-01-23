<div id="debug" class="section">

# Debug<a href="#debug" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">Debug</span></span><a href="#syside.gc.Debug" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Debug options for the garbage collector.

<div class="align-center" align="center">

<img src="data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iZ3JhcGh2aXoiIHN0eWxlPSJ3aWR0aDogMy44NzVyZW07aGVpZ2h0OiAyLjc1cmVtOyIgdmlld2JveD0iMC4wMCAwLjAwIDYyLjAwIDQ0LjAwIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPgo8ZyBjbGFzcz0iZ3JhcGgiIGlkPSJncmFwaDAiIHRyYW5zZm9ybT0ic2NhbGUoMSAxKSByb3RhdGUoMCkgdHJhbnNsYXRlKDQgNDApIj4KPHRpdGxlPiUzPC90aXRsZT4KPGcgY2xhc3M9Im5vZGUiIGlkPSJub2RlMSI+Cjx0aXRsZT5EZWJ1ZzwvdGl0bGU+CjxnIGlkPSJhX25vZGUxIj48YSBocmVmPSIjc3lzaWRlLmdjLkRlYnVnIj4KPHBvbHlnb24gcG9pbnRzPSI1NCwtMzYgMCwtMzYgMCwwIDU0LDAgNTQsLTM2IiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1iZy1jb2xvcik7c3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1ub2RlLWZnLWNvbG9yKTsiPjwvcG9seWdvbj4KPHRleHQgZm9udC1mYW1pbHk9IkxleGVuZCIgZm9udC1zaXplPSIxMi4wMCIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWNvZGUtZmctY29sb3IpOy0tbWQtZ3JhcGh2aXotaG92ZXItY29sb3I6IHZhcigtLW1kLWdyYXBodml6LWEtaG92ZXItY29sb3IpOyIgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iMjciIHk9Ii0xNC4yIj5EZWJ1ZzwvdGV4dD4KPHRpdGxlPnN5c2lkZS5nYy5EZWJ1ZzwvdGl0bGU+PC9hPgo8L2c+CjwvZz4KPC9nPgo8L3N2Zz4=" class="graphviz" />

</div>

<span class="sd-summary-text">Members defined in <a href="#syside.gc.Debug" class="reference internal" title="syside.gc.Debug"><span class="pre"><code class="sourceCode python">Debug</code></span></a> (5 members)</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |  |
|----|----|----|----|
| <span class="nerd-font"></span> | <a href="#syside.gc.Debug.collected" class="reference internal" title="syside.gc.Debug.collected"><span class="pre"><code class="sourceCode python">collected</code></span></a> | <span class="pre">`RW`</span> | Print collected documents during collection. |
| <span class="nerd-font"></span> | <a href="#syside.gc.Debug.reachable" class="reference internal" title="syside.gc.Debug.reachable"><span class="pre"><code class="sourceCode python">reachable</code></span></a> | <span class="pre">`RW`</span> | Print reachable documents during collection. |
| <span class="nerd-font"></span> | <a href="#syside.gc.Debug.stats" class="reference internal" title="syside.gc.Debug.stats"><span class="pre"><code class="sourceCode python">stats</code></span></a> | <span class="pre">`RW`</span> | Print statistics summary during collection. |
| <span class="nerd-font"></span> | <a href="#syside.gc.Debug.unreachable" class="reference internal" title="syside.gc.Debug.unreachable"><span class="pre"><code class="sourceCode python">unreachable</code></span></a> | <span class="pre">`RW`</span> | Print unreachable documents during collection. |
| <span class="nerd-font"></span> | <a href="#syside.gc.Debug.__init__" class="reference internal" title="syside.gc.Debug.__init__"><span class="pre"><code class="sourceCode python"><span class="fu">__init__</span></code></span></a> |  |  |

</div>

</div>

<span class="nerd-font"></span> **Attributes**

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">collected</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*<a href="#syside.gc.Debug.collected" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Print collected documents during collection.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">reachable</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*<a href="#syside.gc.Debug.reachable" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Print reachable documents during collection.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">stats</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*<a href="#syside.gc.Debug.stats" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Print statistics summary during collection.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">unreachable</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*<a href="#syside.gc.Debug.unreachable" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Print unreachable documents during collection.

<span class="nerd-font"></span> **Methods**

<span class="sig-name descname"><span class="pre">\_\_init\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">stats</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">False</span></span>*, *<span class="n"><span class="pre">collected</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">False</span></span>*, *<span class="n"><span class="pre">reachable</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">False</span></span>*, *<span class="n"><span class="pre">unreachable</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">False</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span><a href="#syside.gc.Debug.__init__" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/gc//README.md" class="reference internal" title="syside.gc"><span class="pre"><code class="sourceCode python">syside.gc</code></span></a>

  - <a href="/python/v0.8.4/syside/gc//README.md" class="reference internal" title="syside.gc.get_debug"><span class="pre"><code class="sourceCode python">get_debug</code></span></a>

  - <a href="/python/v0.8.4/syside/gc//README.md" class="reference internal" title="syside.gc.set_debug"><span class="pre"><code class="sourceCode python">set_debug</code></span></a>

</div>

</div>
