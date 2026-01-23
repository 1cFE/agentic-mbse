<div id="relationshipbody" class="section">

# RelationshipBody<a href="#relationshipbody" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">RelationshipBody</span></span><a href="#syside.RelationshipBody" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Container for relationship bodies. Works similarly to <span class="pre">`ChildrenNodes`</span> except relationships are not needed and all elements are taken ownership off.

TODO: add insert and replace methods.

<div class="align-center" align="center">

<img src="data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iZ3JhcGh2aXoiIHN0eWxlPSJ3aWR0aDogNy44MTI1cmVtO2hlaWdodDogNy4yNXJlbTsiIHZpZXdib3g9IjAuMDAgMC4wMCAxMjUuMDAgMTE2LjAwIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPgo8ZyBjbGFzcz0iZ3JhcGgiIGlkPSJncmFwaDAiIHRyYW5zZm9ybT0ic2NhbGUoMSAxKSByb3RhdGUoMCkgdHJhbnNsYXRlKDQgMTEyKSI+Cjx0aXRsZT4lMzwvdGl0bGU+CjxnIGNsYXNzPSJub2RlIiBpZD0ibm9kZTEiPgo8dGl0bGU+UmVsYXRpb25zaGlwQm9keTwvdGl0bGU+CjxnIGlkPSJhX25vZGUxIj48YSBocmVmPSIjc3lzaWRlLlJlbGF0aW9uc2hpcEJvZHkiPgo8cG9seWdvbiBwb2ludHM9IjExNywtMzYgMCwtMzYgMCwwIDExNywwIDExNywtMzYiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1ncmFwaHZpei1ub2RlLWJnLWNvbG9yKTtzdHJva2U6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtZmctY29sb3IpOyI+PC9wb2x5Z29uPgo8dGV4dCBmb250LWZhbWlseT0iTGV4ZW5kIiBmb250LXNpemU9IjEyLjAwIiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtY29kZS1mZy1jb2xvcik7LS1tZC1ncmFwaHZpei1ob3Zlci1jb2xvcjogdmFyKC0tbWQtZ3JhcGh2aXotYS1ob3Zlci1jb2xvcik7IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSI1OC41IiB5PSItMTQuMiI+UmVsYXRpb25zaGlwQm9keTwvdGV4dD4KPHRpdGxlPnN5c2lkZS5SZWxhdGlvbnNoaXBCb2R5PC90aXRsZT48L2E+CjwvZz4KPC9nPgo8ZyBjbGFzcz0ibm9kZSIgaWQ9Im5vZGUyIj4KPHRpdGxlPkNvbnRhaW5lclZpZXc8L3RpdGxlPgo8ZyBpZD0iYV9ub2RlMiI+PGEgaHJlZj0iL3B5dGhvbi92MC44LjQvc3lzaWRlL0NvbnRhaW5lclZpZXcubWQiPgo8cG9seWdvbiBwb2ludHM9IjEwOSwtMTA4IDgsLTEwOCA4LC03MiAxMDksLTcyIDEwOSwtMTA4IiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1iZy1jb2xvcik7c3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1ub2RlLWZnLWNvbG9yKTsiPjwvcG9seWdvbj4KPHRleHQgZm9udC1mYW1pbHk9IkxleGVuZCIgZm9udC1zaXplPSIxMi4wMCIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWNvZGUtZmctY29sb3IpOy0tbWQtZ3JhcGh2aXotaG92ZXItY29sb3I6IHZhcigtLW1kLWdyYXBodml6LWEtaG92ZXItY29sb3IpOyIgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iNTguNSIgeT0iLTg2LjIiPkNvbnRhaW5lclZpZXc8L3RleHQ+Cjx0aXRsZT5zeXNpZGUuQ29udGFpbmVyVmlldzwvdGl0bGU+PC9hPgo8L2c+CjwvZz4KPGcgY2xhc3M9ImVkZ2UiIGlkPSJlZGdlMSI+Cjx0aXRsZT5Db250YWluZXJWaWV3LSZndDtSZWxhdGlvbnNoaXBCb2R5PC90aXRsZT4KPHBhdGggZD0iTTU4LjUsLTcxLjdDNTguNSwtNjMuOTggNTguNSwtNTQuNzEgNTguNSwtNDYuMTEiIGZpbGw9Im5vbmUiIHN0eWxlPSJzdHJva2U6IHZhcigtLW1kLWdyYXBodml6LWVkZ2UtY29sb3IpOyIgLz4KPHBvbHlnb24gcG9pbnRzPSI2MiwtNDYuMSA1OC41LC0zNi4xIDU1LC00Ni4xIDYyLC00Ni4xIiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtZ3JhcGh2aXotZWRnZS1jb2xvcik7c3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1lZGdlLWNvbG9yKTsiPjwvcG9seWdvbj4KPC9nPgo8L2c+Cjwvc3ZnPg==" class="graphviz" />

</div>

<span class="sd-summary-text">Members defined in <a href="#syside.RelationshipBody" class="reference internal" title="syside.RelationshipBody"><span class="pre"><code class="sourceCode python">RelationshipBody</code></span></a> (7 members)</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |  |
|----|----|----|----|
| <span class="nerd-font"></span> | <a href="#syside.RelationshipBody.append" class="reference internal" title="syside.RelationshipBody.append"><span class="pre"><code class="sourceCode python">append</code></span></a> |  | Append an owned related element. Returns newly constructed related element. |
| <span class="nerd-font"></span> | <a href="#syside.RelationshipBody.append_annotation" class="reference internal" title="syside.RelationshipBody.append_annotation"><span class="pre"><code class="sourceCode python">append_annotation</code></span></a> |  | Append an owned annotation to an annotating element. Returns a pair of newly constructed (annotation, annotating element). |
| <span class="nerd-font"></span> | <a href="#syside.RelationshipBody.clear" class="reference internal" title="syside.RelationshipBody.clear"><span class="pre"><code class="sourceCode python">clear</code></span></a> |  | Removes and releases all elements in this container. Afterwards, <span class="pre">`len`</span> is 0. |
| <span class="nerd-font"></span> | <a href="#syside.RelationshipBody.extract" class="reference internal" title="syside.RelationshipBody.extract"><span class="pre"><code class="sourceCode python">extract</code></span></a> |  | Extracts a related element at the specified index from the model tree and returns it. |
| <span class="nerd-font"></span> | <a href="#syside.RelationshipBody.extract_element" class="reference internal" title="syside.RelationshipBody.extract_element"><span class="pre"><code class="sourceCode python">extract_element</code></span></a> |  | Extracts a related element from the model tree. |
| <span class="nerd-font"></span> | <a href="#syside.RelationshipBody.pop" class="reference internal" title="syside.RelationshipBody.pop"><span class="pre"><code class="sourceCode python">pop</code></span></a> |  | Removes a related element at the specified index from the model tree and returns it. |
| <span class="nerd-font"></span> | <a href="#syside.RelationshipBody.remove_element" class="reference internal" title="syside.RelationshipBody.remove_element"><span class="pre"><code class="sourceCode python">remove_element</code></span></a> |  | Removes a related element from the model tree. Returns <span class="pre">`True`</span> if the element was removed, otherwise <span class="pre">`False`</span>. |

</div>

</div>

<span class="sd-summary-text">Members inherited from <a href="/python/v0.8.4/syside/ContainerView.md" class="reference internal" title="syside.ContainerView"><span class="pre"><code class="sourceCode python">ContainerView</code></span></a> (11 members)</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |  |
|----|----|----|----|
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/ContainerView.md" class="reference internal" title="syside.ContainerView.__bool__"><span class="pre"><code class="sourceCode python"><span class="fu">__bool__</span></code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/ContainerView.md" class="reference internal" title="syside.ContainerView.__contains__"><span class="pre"><code class="sourceCode python"><span class="fu">__contains__</span></code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/ContainerView.md" class="reference internal" title="syside.ContainerView.__getitem__"><span class="pre"><code class="sourceCode python"><span class="fu">__getitem__</span></code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/ContainerView.md" class="reference internal" title="syside.ContainerView.__iter__"><span class="pre"><code class="sourceCode python"><span class="fu">__iter__</span></code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/ContainerView.md" class="reference internal" title="syside.ContainerView.__len__"><span class="pre"><code class="sourceCode python"><span class="fu">__len__</span></code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/ContainerView.md" class="reference internal" title="syside.ContainerView.__reversed__"><span class="pre"><code class="sourceCode python"><span class="fu">__reversed__</span></code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/ContainerView.md" class="reference internal" title="syside.ContainerView.__str__"><span class="pre"><code class="sourceCode python"><span class="fu">__str__</span></code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/ContainerView.md" class="reference internal" title="syside.ContainerView.at"><span class="pre"><code class="sourceCode python">at</code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/ContainerView.md" class="reference internal" title="syside.ContainerView.count"><span class="pre"><code class="sourceCode python">count</code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/ContainerView.md" class="reference internal" title="syside.ContainerView.empty"><span class="pre"><code class="sourceCode python">empty</code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/ContainerView.md" class="reference internal" title="syside.ContainerView.index"><span class="pre"><code class="sourceCode python">index</code></span></a> |  |  |

</div>

</div>

<span class="nerd-font"></span> **Methods**

<span class="sig-name descname"><span class="pre">append</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">element</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">type</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.TElement</span><span class="p"><span class="pre">\]</span></span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">syside.TElement</span></span></span><a href="#syside.RelationshipBody.append" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Append an owned related element. Returns newly constructed related element.

<span class="sig-name descname"><span class="pre">append</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">element</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">syside.TElement</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">syside.TElement</span></span></span>  
Append an owned existing related element. Returns the same related element.

<span class="sig-name descname"><span class="pre">append_annotation</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">element</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">type</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.RelationshipBody.append_annotation.M</span><span class="p"><span class="pre">\]</span></span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Annotation.md" class="reference internal" title="syside.Annotation"><span class="pre">syside.Annotation</span></a><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">syside.RelationshipBody.append_annotation.M</span><span class="p"><span class="pre">\]</span></span></span></span><a href="#syside.RelationshipBody.append_annotation" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Append an owned annotation to an annotating element. Returns a pair of newly constructed (annotation, annotating element).

<span class="sig-name descname"><span class="pre">append_annotation</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">element</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">syside.RelationshipBody.append_annotation.M</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Annotation.md" class="reference internal" title="syside.Annotation"><span class="pre">syside.Annotation</span></a><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">syside.RelationshipBody.append_annotation.M</span><span class="p"><span class="pre">\]</span></span></span></span>  
Append an owned annotation to an existing annotating element. Returns a pair of (annotation, annotating element) where only the annotation is newly constructed.

<span class="sig-name descname"><span class="pre">clear</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span><a href="#syside.RelationshipBody.clear" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Removes and releases all elements in this container. Afterwards, <span class="pre">`len`</span> is 0.

<span class="sig-name descname"><span class="pre">extract</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">index</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">int</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">-1</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element"><span class="pre">syside.Element</span></a></span></span><a href="#syside.RelationshipBody.extract" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Extracts a related element at the specified index from the model tree and returns it.

Note that it is up to the user to ensure that the returned orphan element is not leaked.

Raises <span class="pre">`IndexError`</span> if index is out of bounds.

<span class="sig-name descname"><span class="pre">extract_element</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">syside.RelationshipBody.extract_element.T</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">syside.RelationshipBody.extract_element.T</span></span></span><a href="#syside.RelationshipBody.extract_element" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Extracts a related element from the model tree.

Note that it is up to the user to ensure that the returned orphan element is not leaked.

Raises <span class="pre">`ValueError`</span> if there is no such element.

<span class="sig-name descname"><span class="pre">pop</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">index</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">int</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">-1</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element"><span class="pre">syside.Element</span></a></span></span><a href="#syside.RelationshipBody.pop" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Removes a related element at the specified index from the model tree and returns it.

<span class="sig-name descname"><span class="pre">remove_element</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element"><span class="pre">syside.Element</span></a></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">bool</span></span></span><a href="#syside.RelationshipBody.remove_element" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Removes a related element from the model tree. Returns <span class="pre">`True`</span> if the element was removed, otherwise <span class="pre">`False`</span>.

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/Conjugation.md" class="reference internal" title="syside.Conjugation"><span class="pre"><code class="sourceCode python">syside.Conjugation</code></span></a>

  - <a href="/python/v0.8.4/syside/Conjugation.md" class="reference internal" title="syside.Conjugation.children"><span class="pre"><code class="sourceCode python">children</code></span></a>

- <a href="/python/v0.8.4/syside/Dependency.md" class="reference internal" title="syside.Dependency"><span class="pre"><code class="sourceCode python">syside.Dependency</code></span></a>

  - <a href="/python/v0.8.4/syside/Dependency.md" class="reference internal" title="syside.Dependency.children"><span class="pre"><code class="sourceCode python">children</code></span></a>

- <a href="/python/v0.8.4/syside/Disjoining.md" class="reference internal" title="syside.Disjoining"><span class="pre"><code class="sourceCode python">syside.Disjoining</code></span></a>

  - <a href="/python/v0.8.4/syside/Disjoining.md" class="reference internal" title="syside.Disjoining.children"><span class="pre"><code class="sourceCode python">children</code></span></a>

- <a href="/python/v0.8.4/syside/FeatureInverting.md" class="reference internal" title="syside.FeatureInverting"><span class="pre"><code class="sourceCode python">syside.FeatureInverting</code></span></a>

  - <a href="/python/v0.8.4/syside/FeatureInverting.md" class="reference internal" title="syside.FeatureInverting.children"><span class="pre"><code class="sourceCode python">children</code></span></a>

- <a href="/python/v0.8.4/syside/Import.md" class="reference internal" title="syside.Import"><span class="pre"><code class="sourceCode python">syside.Import</code></span></a>

  - <a href="/python/v0.8.4/syside/Import.md" class="reference internal" title="syside.Import.children"><span class="pre"><code class="sourceCode python">children</code></span></a>

- <a href="/python/v0.8.4/syside/Membership.md" class="reference internal" title="syside.Membership"><span class="pre"><code class="sourceCode python">syside.Membership</code></span></a>

  - <a href="/python/v0.8.4/syside/Membership.md" class="reference internal" title="syside.Membership.children"><span class="pre"><code class="sourceCode python">children</code></span></a>

- <a href="/python/v0.8.4/syside/Specialization.md" class="reference internal" title="syside.Specialization"><span class="pre"><code class="sourceCode python">syside.Specialization</code></span></a>

  - <a href="/python/v0.8.4/syside/Specialization.md" class="reference internal" title="syside.Specialization.children"><span class="pre"><code class="sourceCode python">children</code></span></a>

</div>

</div>
