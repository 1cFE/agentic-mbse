<div id="path" class="section">

# Path<a href="#path" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">Path</span></span><a href="#syside.Path" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
A sequence of path segments that stringifies with unrestricted names as needed. Similar to <span class="pre">`QualifiedName`</span> but may contain indices to unnamed elements, that are printed literally with <span class="pre">`/`</span> separator instead.

Note that indices are expected to use 1-based indexing according to the specification.

<div class="align-center" align="center">

<img src="data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iZ3JhcGh2aXoiIHN0eWxlPSJ3aWR0aDogMy44NzVyZW07aGVpZ2h0OiAyLjc1cmVtOyIgdmlld2JveD0iMC4wMCAwLjAwIDYyLjAwIDQ0LjAwIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPgo8ZyBjbGFzcz0iZ3JhcGgiIGlkPSJncmFwaDAiIHRyYW5zZm9ybT0ic2NhbGUoMSAxKSByb3RhdGUoMCkgdHJhbnNsYXRlKDQgNDApIj4KPHRpdGxlPiUzPC90aXRsZT4KPGcgY2xhc3M9Im5vZGUiIGlkPSJub2RlMSI+Cjx0aXRsZT5QYXRoPC90aXRsZT4KPGcgaWQ9ImFfbm9kZTEiPjxhIGhyZWY9IiNzeXNpZGUuUGF0aCI+Cjxwb2x5Z29uIHBvaW50cz0iNTQsLTM2IDAsLTM2IDAsMCA1NCwwIDU0LC0zNiIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtYmctY29sb3IpO3N0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1mZy1jb2xvcik7Ij48L3BvbHlnb24+Cjx0ZXh0IGZvbnQtZmFtaWx5PSJMZXhlbmQiIGZvbnQtc2l6ZT0iMTIuMDAiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1jb2RlLWZnLWNvbG9yKTstLW1kLWdyYXBodml6LWhvdmVyLWNvbG9yOiB2YXIoLS1tZC1ncmFwaHZpei1hLWhvdmVyLWNvbG9yKTsiIHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjI3IiB5PSItMTQuMiI+UGF0aDwvdGV4dD4KPHRpdGxlPnN5c2lkZS5QYXRoPC90aXRsZT48L2E+CjwvZz4KPC9nPgo8L2c+Cjwvc3ZnPg==" class="graphviz" />

</div>

<span class="sd-summary-text">Members defined in <a href="#syside.Path" class="reference internal" title="syside.Path"><span class="pre"><code class="sourceCode python">Path</code></span></a> (18 members)</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |  |
|----|----|----|----|
| <span class="nerd-font"></span> | <a href="#syside.Path.to_owning_membership" class="reference internal" title="syside.Path.to_owning_membership"><span class="pre"><code class="sourceCode python">to_owning_membership</code></span></a> | <span class="pre">`RW`</span> | If this is true, this path is to the owning membership of the element the segments would resolve to. This is a flag rather than a segment since owning memberships can effectively only ever be the last segment. When formatted, this will add <span class="pre">`/owningMembership`</span> suffix. |
| <span class="nerd-font"></span> | <a href="#syside.Path.__bool__" class="reference internal" title="syside.Path.__bool__"><span class="pre"><code class="sourceCode python"><span class="fu">__bool__</span></code></span></a> |  | Check whether the vector is nonempty |
| <span class="nerd-font"></span> | <a href="#syside.Path.__contains__" class="reference internal" title="syside.Path.__contains__"><span class="pre"><code class="sourceCode python"><span class="fu">__contains__</span></code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.Path.__delitem__" class="reference internal" title="syside.Path.__delitem__"><span class="pre"><code class="sourceCode python"><span class="fu">__delitem__</span></code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.Path.__getitem__" class="reference internal" title="syside.Path.__getitem__"><span class="pre"><code class="sourceCode python"><span class="fu">__getitem__</span></code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.Path.__init__" class="reference internal" title="syside.Path.__init__"><span class="pre"><code class="sourceCode python"><span class="fu">__init__</span></code></span></a> |  | Default constructor |
| <span class="nerd-font"></span> | <a href="#syside.Path.__iter__" class="reference internal" title="syside.Path.__iter__"><span class="pre"><code class="sourceCode python"><span class="fu">__iter__</span></code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.Path.__len__" class="reference internal" title="syside.Path.__len__"><span class="pre"><code class="sourceCode python"><span class="fu">__len__</span></code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.Path.__repr__" class="reference internal" title="syside.Path.__repr__"><span class="pre"><code class="sourceCode python"><span class="fu">__repr__</span></code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.Path.__setitem__" class="reference internal" title="syside.Path.__setitem__"><span class="pre"><code class="sourceCode python"><span class="fu">__setitem__</span></code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.Path.__str__" class="reference internal" title="syside.Path.__str__"><span class="pre"><code class="sourceCode python"><span class="fu">__str__</span></code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.Path.append" class="reference internal" title="syside.Path.append"><span class="pre"><code class="sourceCode python">append</code></span></a> |  | Append arg to the end of the list. |
| <span class="nerd-font"></span> | <a href="#syside.Path.clear" class="reference internal" title="syside.Path.clear"><span class="pre"><code class="sourceCode python">clear</code></span></a> |  | Remove all items from list. |
| <span class="nerd-font"></span> | <a href="#syside.Path.count" class="reference internal" title="syside.Path.count"><span class="pre"><code class="sourceCode python">count</code></span></a> |  | Return number of occurrences of arg. |
| <span class="nerd-font"></span> | <a href="#syside.Path.extend" class="reference internal" title="syside.Path.extend"><span class="pre"><code class="sourceCode python">extend</code></span></a> |  | Extend self by appending elements from arg. |
| <span class="nerd-font"></span> | <a href="#syside.Path.insert" class="reference internal" title="syside.Path.insert"><span class="pre"><code class="sourceCode python">insert</code></span></a> |  | Insert object arg1 before index arg0. |
| <span class="nerd-font"></span> | <a href="#syside.Path.pop" class="reference internal" title="syside.Path.pop"><span class="pre"><code class="sourceCode python">pop</code></span></a> |  | Remove and return item at index (default last). |
| <span class="nerd-font"></span> | <a href="#syside.Path.remove" class="reference internal" title="syside.Path.remove"><span class="pre"><code class="sourceCode python">remove</code></span></a> |  | Remove first occurrence of arg. |

</div>

</div>

<span class="nerd-font"></span> **Attributes**

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">to_owning_membership</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*<a href="#syside.Path.to_owning_membership" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
If this is true, this path is to the owning membership of the element the segments would resolve to. This is a flag rather than a segment since owning memberships can effectively only ever be the last segment. When formatted, this will add <span class="pre">`/owningMembership`</span> suffix.

<span class="nerd-font"></span> **Methods**

<span class="sig-name descname"><span class="pre">\_\_bool\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">bool</span></span></span><a href="#syside.Path.__bool__" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Check whether the vector is nonempty

<span class="sig-name descname"><span class="pre">\_\_contains\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">int</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">bool</span></span></span><a href="#syside.Path.__contains__" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">\_\_contains\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">object</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">bool</span></span></span>  

<span class="sig-name descname"><span class="pre">\_\_delitem\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">int</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span><a href="#syside.Path.__delitem__" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">\_\_delitem\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">slice</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span>  

<span class="sig-name descname"><span class="pre">\_\_getitem\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">index</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">int</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">int</span></span></span><a href="#syside.Path.__getitem__" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">\_\_getitem\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">index</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">slice</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="#syside.Path" class="reference internal" title="syside.Path"><span class="pre">syside.Path</span></a></span></span>  

<span class="sig-name descname"><span class="pre">\_\_init\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span><a href="#syside.Path.__init__" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Default constructor

<span class="sig-name descname"><span class="pre">\_\_init\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="#syside.Path" class="reference internal" title="syside.Path"><span class="pre">syside.Path</span></a></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span>  
Copy constructor

<span class="sig-name descname"><span class="pre">\_\_init\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">Iterable</span><span class="p"><span class="pre">\[</span></span><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">int</span><span class="p"><span class="pre">\]</span></span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span>  
Construct from an iterable object

<span class="sig-name descname"><span class="pre">\_\_iter\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">Iterator</span><span class="p"><span class="pre">\[</span></span><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">int</span><span class="p"><span class="pre">\]</span></span></span></span><a href="#syside.Path.__iter__" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">\_\_len\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">int</span></span></span><a href="#syside.Path.__len__" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">\_\_repr\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">str</span></span></span><a href="#syside.Path.__repr__" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">\_\_setitem\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg0</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">int</span></span>*, *<span class="n"><span class="pre">arg1</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">int</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span><a href="#syside.Path.__setitem__" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">\_\_setitem\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg0</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">slice</span></span>*, *<span class="n"><span class="pre">arg1</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="#syside.Path" class="reference internal" title="syside.Path"><span class="pre">syside.Path</span></a></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span>  

<span class="sig-name descname"><span class="pre">\_\_str\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">str</span></span></span><a href="#syside.Path.__str__" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">append</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">int</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span><a href="#syside.Path.append" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Append arg to the end of the list.

<span class="sig-name descname"><span class="pre">clear</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span><a href="#syside.Path.clear" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Remove all items from list.

<span class="sig-name descname"><span class="pre">count</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">int</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">int</span></span></span><a href="#syside.Path.count" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Return number of occurrences of arg.

<span class="sig-name descname"><span class="pre">extend</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="#syside.Path" class="reference internal" title="syside.Path"><span class="pre">syside.Path</span></a></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span><a href="#syside.Path.extend" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Extend self by appending elements from arg.

<span class="sig-name descname"><span class="pre">insert</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg0</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">int</span></span>*, *<span class="n"><span class="pre">arg1</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">int</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span><a href="#syside.Path.insert" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Insert object arg1 before index arg0.

<span class="sig-name descname"><span class="pre">pop</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">index</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">int</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">-1</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">int</span></span></span><a href="#syside.Path.pop" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Remove and return item at index (default last).

<span class="sig-name descname"><span class="pre">remove</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">int</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span><a href="#syside.Path.remove" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Remove first occurrence of arg.

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element"><span class="pre"><code class="sourceCode python">syside.Element</code></span></a>

  - <a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element.path"><span class="pre"><code class="sourceCode python">path</code></span></a>

- <a href="#syside.Path" class="reference internal" title="syside.Path"><span class="pre"><code class="sourceCode python">syside.Path</code></span></a>

  - <a href="#syside.Path.__getitem__" class="reference internal" title="syside.Path.__getitem__"><span class="pre"><code class="sourceCode python"><span class="fu">__getitem__</span></code></span></a>

  - <a href="#syside.Path.__init__" class="reference internal" title="syside.Path.__init__"><span class="pre"><code class="sourceCode python"><span class="fu">__init__</span></code></span></a>

  - <a href="#syside.Path.__setitem__" class="reference internal" title="syside.Path.__setitem__"><span class="pre"><code class="sourceCode python"><span class="fu">__setitem__</span></code></span></a>

  - <a href="#syside.Path.extend" class="reference internal" title="syside.Path.extend"><span class="pre"><code class="sourceCode python">extend</code></span></a>

</div>

</div>
