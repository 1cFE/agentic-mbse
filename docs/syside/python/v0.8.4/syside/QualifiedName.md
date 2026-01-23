<div id="qualifiedname" class="section">

# QualifiedName<a href="#qualifiedname" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">QualifiedName</span></span><a href="#syside.QualifiedName" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
A sequence of qualified name segments that stringifies with unrestricted names as needed. Unlike string, this allows querying segments in a qualified name without having to parse it again, and is cheaper to construct as string conversion is performed only when needed.

<div class="align-center" align="center">

<img src="data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iZ3JhcGh2aXoiIHN0eWxlPSJ3aWR0aDogNy4wNjI1cmVtO2hlaWdodDogMi43NXJlbTsiIHZpZXdib3g9IjAuMDAgMC4wMCAxMTMuMDAgNDQuMDAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxnIGNsYXNzPSJncmFwaCIgaWQ9ImdyYXBoMCIgdHJhbnNmb3JtPSJzY2FsZSgxIDEpIHJvdGF0ZSgwKSB0cmFuc2xhdGUoNCA0MCkiPgo8dGl0bGU+JTM8L3RpdGxlPgo8ZyBjbGFzcz0ibm9kZSIgaWQ9Im5vZGUxIj4KPHRpdGxlPlF1YWxpZmllZE5hbWU8L3RpdGxlPgo8ZyBpZD0iYV9ub2RlMSI+PGEgaHJlZj0iI3N5c2lkZS5RdWFsaWZpZWROYW1lIj4KPHBvbHlnb24gcG9pbnRzPSIxMDUsLTM2IDAsLTM2IDAsMCAxMDUsMCAxMDUsLTM2IiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1iZy1jb2xvcik7c3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1ub2RlLWZnLWNvbG9yKTsiPjwvcG9seWdvbj4KPHRleHQgZm9udC1mYW1pbHk9IkxleGVuZCIgZm9udC1zaXplPSIxMi4wMCIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWNvZGUtZmctY29sb3IpOy0tbWQtZ3JhcGh2aXotaG92ZXItY29sb3I6IHZhcigtLW1kLWdyYXBodml6LWEtaG92ZXItY29sb3IpOyIgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iNTIuNSIgeT0iLTE0LjIiPlF1YWxpZmllZE5hbWU8L3RleHQ+Cjx0aXRsZT5zeXNpZGUuUXVhbGlmaWVkTmFtZTwvdGl0bGU+PC9hPgo8L2c+CjwvZz4KPC9nPgo8L3N2Zz4=" class="graphviz" />

</div>

<span class="sd-summary-text">Members defined in <a href="#syside.QualifiedName" class="reference internal" title="syside.QualifiedName"><span class="pre"><code class="sourceCode python">QualifiedName</code></span></a> (17 members)</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |  |
|----|----|----|----|
| <span class="nerd-font"></span> | <a href="#syside.QualifiedName.__bool__" class="reference internal" title="syside.QualifiedName.__bool__"><span class="pre"><code class="sourceCode python"><span class="fu">__bool__</span></code></span></a> |  | Check whether the vector is nonempty |
| <span class="nerd-font"></span> | <a href="#syside.QualifiedName.__contains__" class="reference internal" title="syside.QualifiedName.__contains__"><span class="pre"><code class="sourceCode python"><span class="fu">__contains__</span></code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.QualifiedName.__delitem__" class="reference internal" title="syside.QualifiedName.__delitem__"><span class="pre"><code class="sourceCode python"><span class="fu">__delitem__</span></code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.QualifiedName.__getitem__" class="reference internal" title="syside.QualifiedName.__getitem__"><span class="pre"><code class="sourceCode python"><span class="fu">__getitem__</span></code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.QualifiedName.__init__" class="reference internal" title="syside.QualifiedName.__init__"><span class="pre"><code class="sourceCode python"><span class="fu">__init__</span></code></span></a> |  | Default constructor |
| <span class="nerd-font"></span> | <a href="#syside.QualifiedName.__iter__" class="reference internal" title="syside.QualifiedName.__iter__"><span class="pre"><code class="sourceCode python"><span class="fu">__iter__</span></code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.QualifiedName.__len__" class="reference internal" title="syside.QualifiedName.__len__"><span class="pre"><code class="sourceCode python"><span class="fu">__len__</span></code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.QualifiedName.__repr__" class="reference internal" title="syside.QualifiedName.__repr__"><span class="pre"><code class="sourceCode python"><span class="fu">__repr__</span></code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.QualifiedName.__setitem__" class="reference internal" title="syside.QualifiedName.__setitem__"><span class="pre"><code class="sourceCode python"><span class="fu">__setitem__</span></code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.QualifiedName.__str__" class="reference internal" title="syside.QualifiedName.__str__"><span class="pre"><code class="sourceCode python"><span class="fu">__str__</span></code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.QualifiedName.append" class="reference internal" title="syside.QualifiedName.append"><span class="pre"><code class="sourceCode python">append</code></span></a> |  | Append arg to the end of the list. |
| <span class="nerd-font"></span> | <a href="#syside.QualifiedName.clear" class="reference internal" title="syside.QualifiedName.clear"><span class="pre"><code class="sourceCode python">clear</code></span></a> |  | Remove all items from list. |
| <span class="nerd-font"></span> | <a href="#syside.QualifiedName.count" class="reference internal" title="syside.QualifiedName.count"><span class="pre"><code class="sourceCode python">count</code></span></a> |  | Return number of occurrences of arg. |
| <span class="nerd-font"></span> | <a href="#syside.QualifiedName.extend" class="reference internal" title="syside.QualifiedName.extend"><span class="pre"><code class="sourceCode python">extend</code></span></a> |  | Extend self by appending elements from arg. |
| <span class="nerd-font"></span> | <a href="#syside.QualifiedName.insert" class="reference internal" title="syside.QualifiedName.insert"><span class="pre"><code class="sourceCode python">insert</code></span></a> |  | Insert object arg1 before index arg0. |
| <span class="nerd-font"></span> | <a href="#syside.QualifiedName.pop" class="reference internal" title="syside.QualifiedName.pop"><span class="pre"><code class="sourceCode python">pop</code></span></a> |  | Remove and return item at index (default last). |
| <span class="nerd-font"></span> | <a href="#syside.QualifiedName.remove" class="reference internal" title="syside.QualifiedName.remove"><span class="pre"><code class="sourceCode python">remove</code></span></a> |  | Remove first occurrence of arg. |

</div>

</div>

<span class="nerd-font"></span> **Methods**

<span class="sig-name descname"><span class="pre">\_\_bool\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">bool</span></span></span><a href="#syside.QualifiedName.__bool__" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Check whether the vector is nonempty

<span class="sig-name descname"><span class="pre">\_\_contains\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">bool</span></span></span><a href="#syside.QualifiedName.__contains__" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">\_\_contains\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">object</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">bool</span></span></span>  

<span class="sig-name descname"><span class="pre">\_\_delitem\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">int</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span><a href="#syside.QualifiedName.__delitem__" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">\_\_delitem\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">slice</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span>  

<span class="sig-name descname"><span class="pre">\_\_getitem\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">index</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">int</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">str</span></span></span><a href="#syside.QualifiedName.__getitem__" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">\_\_getitem\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">index</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">slice</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="#syside.QualifiedName" class="reference internal" title="syside.QualifiedName"><span class="pre">syside.QualifiedName</span></a></span></span>  

<span class="sig-name descname"><span class="pre">\_\_init\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span><a href="#syside.QualifiedName.__init__" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Default constructor

<span class="sig-name descname"><span class="pre">\_\_init\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="#syside.QualifiedName" class="reference internal" title="syside.QualifiedName"><span class="pre">syside.QualifiedName</span></a></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span>  
Copy constructor

<span class="sig-name descname"><span class="pre">\_\_init\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">Iterable</span><span class="p"><span class="pre">\[</span></span><span class="pre">str</span><span class="p"><span class="pre">\]</span></span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span>  
Construct from an iterable object

<span class="sig-name descname"><span class="pre">\_\_iter\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">Iterator</span><span class="p"><span class="pre">\[</span></span><span class="pre">str</span><span class="p"><span class="pre">\]</span></span></span></span><a href="#syside.QualifiedName.__iter__" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">\_\_len\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">int</span></span></span><a href="#syside.QualifiedName.__len__" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">\_\_repr\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">str</span></span></span><a href="#syside.QualifiedName.__repr__" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">\_\_setitem\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg0</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">int</span></span>*, *<span class="n"><span class="pre">arg1</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span><a href="#syside.QualifiedName.__setitem__" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">\_\_setitem\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg0</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">slice</span></span>*, *<span class="n"><span class="pre">arg1</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="#syside.QualifiedName" class="reference internal" title="syside.QualifiedName"><span class="pre">syside.QualifiedName</span></a></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span>  

<span class="sig-name descname"><span class="pre">\_\_str\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">str</span></span></span><a href="#syside.QualifiedName.__str__" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">append</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span><a href="#syside.QualifiedName.append" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Append arg to the end of the list.

<span class="sig-name descname"><span class="pre">clear</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span><a href="#syside.QualifiedName.clear" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Remove all items from list.

<span class="sig-name descname"><span class="pre">count</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">int</span></span></span><a href="#syside.QualifiedName.count" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Return number of occurrences of arg.

<span class="sig-name descname"><span class="pre">extend</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="#syside.QualifiedName" class="reference internal" title="syside.QualifiedName"><span class="pre">syside.QualifiedName</span></a></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span><a href="#syside.QualifiedName.extend" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Extend self by appending elements from arg.

<span class="sig-name descname"><span class="pre">insert</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg0</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">int</span></span>*, *<span class="n"><span class="pre">arg1</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span><a href="#syside.QualifiedName.insert" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Insert object arg1 before index arg0.

<span class="sig-name descname"><span class="pre">pop</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">index</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">int</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">-1</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">str</span></span></span><a href="#syside.QualifiedName.pop" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Remove and return item at index (default last).

<span class="sig-name descname"><span class="pre">remove</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span><a href="#syside.QualifiedName.remove" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Remove first occurrence of arg.

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element"><span class="pre"><code class="sourceCode python">syside.Element</code></span></a>

  - <a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element.qualified_name"><span class="pre"><code class="sourceCode python">qualified_name</code></span></a>

- <a href="#syside.QualifiedName" class="reference internal" title="syside.QualifiedName"><span class="pre"><code class="sourceCode python">syside.QualifiedName</code></span></a>

  - <a href="#syside.QualifiedName.__getitem__" class="reference internal" title="syside.QualifiedName.__getitem__"><span class="pre"><code class="sourceCode python"><span class="fu">__getitem__</span></code></span></a>

  - <a href="#syside.QualifiedName.__init__" class="reference internal" title="syside.QualifiedName.__init__"><span class="pre"><code class="sourceCode python"><span class="fu">__init__</span></code></span></a>

  - <a href="#syside.QualifiedName.__setitem__" class="reference internal" title="syside.QualifiedName.__setitem__"><span class="pre"><code class="sourceCode python"><span class="fu">__setitem__</span></code></span></a>

  - <a href="#syside.QualifiedName.extend" class="reference internal" title="syside.QualifiedName.extend"><span class="pre"><code class="sourceCode python">extend</code></span></a>

</div>

</div>
