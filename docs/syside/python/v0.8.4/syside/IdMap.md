<div id="idmap" class="section">

# IdMap<a href="#idmap" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">IdMap</span></span><a href="#syside.IdMap" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
<span class="pre">`DeserializedModel`</span> compatible mapping for elements. This will typically be used for linking pending references:

<div class="highlight-python notranslate">

<div class="highlight">

    map = IdMap()
    models_reports = [
        deserializer.accept(document, my_reader(input), DESERIALIZE_STANDARD)
        for document, input in zip(documents, inputs)
    ]
    for document in documents:
        map.insert_or_assign(document)
    reports_linked = [model.link(map) for model, _ in models_reports]

</div>

</div>

<div class="align-center" align="center">

<img src="data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iZ3JhcGh2aXoiIHN0eWxlPSJ3aWR0aDogMy45Mzc1cmVtO2hlaWdodDogMi43NXJlbTsiIHZpZXdib3g9IjAuMDAgMC4wMCA2My4wMCA0NC4wMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGcgY2xhc3M9ImdyYXBoIiBpZD0iZ3JhcGgwIiB0cmFuc2Zvcm09InNjYWxlKDEgMSkgcm90YXRlKDApIHRyYW5zbGF0ZSg0IDQwKSI+Cjx0aXRsZT4lMzwvdGl0bGU+CjxnIGNsYXNzPSJub2RlIiBpZD0ibm9kZTEiPgo8dGl0bGU+SWRNYXA8L3RpdGxlPgo8ZyBpZD0iYV9ub2RlMSI+PGEgaHJlZj0iI3N5c2lkZS5JZE1hcCI+Cjxwb2x5Z29uIHBvaW50cz0iNTUsLTM2IDAsLTM2IDAsMCA1NSwwIDU1LC0zNiIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtYmctY29sb3IpO3N0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1mZy1jb2xvcik7Ij48L3BvbHlnb24+Cjx0ZXh0IGZvbnQtZmFtaWx5PSJMZXhlbmQiIGZvbnQtc2l6ZT0iMTIuMDAiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1jb2RlLWZnLWNvbG9yKTstLW1kLWdyYXBodml6LWhvdmVyLWNvbG9yOiB2YXIoLS1tZC1ncmFwaHZpei1hLWhvdmVyLWNvbG9yKTsiIHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjI3LjUiIHk9Ii0xNC4yIj5JZE1hcDwvdGV4dD4KPHRpdGxlPnN5c2lkZS5JZE1hcDwvdGl0bGU+PC9hPgo8L2c+CjwvZz4KPC9nPgo8L3N2Zz4=" class="graphviz" />

</div>

<span class="sd-summary-text">Members defined in <a href="#syside.IdMap" class="reference internal" title="syside.IdMap"><span class="pre"><code class="sourceCode python">IdMap</code></span></a> (9 members)</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |  |
|----|----|----|----|
| <span class="nerd-font"></span> | <a href="#syside.IdMap.__call__" class="reference internal" title="syside.IdMap.__call__"><span class="pre"><code class="sourceCode python"><span class="fu">__call__</span></code></span></a> |  | Short-hand for <span class="pre">`find`</span> or <span class="pre">`search`</span>. Will fall back to <span class="pre">`search`</span> if <span class="pre">`uri`</span> is empty. |
| <span class="nerd-font"></span> | <a href="#syside.IdMap.__init__" class="reference internal" title="syside.IdMap.__init__"><span class="pre"><code class="sourceCode python"><span class="fu">__init__</span></code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.IdMap.clear" class="reference internal" title="syside.IdMap.clear"><span class="pre"><code class="sourceCode python">clear</code></span></a> |  | Clear all mapped elements. |
| <span class="nerd-font"></span> | <a href="#syside.IdMap.erase" class="reference internal" title="syside.IdMap.erase"><span class="pre"><code class="sourceCode python">erase</code></span></a> |  | Erase all elements assigned to <span class="pre">`document`</span> from this map. |
| <span class="nerd-font"></span> | <a href="#syside.IdMap.find" class="reference internal" title="syside.IdMap.find"><span class="pre"><code class="sourceCode python">find</code></span></a> |  | Find an element at document with <span class="pre">`uri`</span> that has <span class="pre">`id`</span>. |
| <span class="nerd-font"></span> | <a href="#syside.IdMap.insert_or_assign" class="reference internal" title="syside.IdMap.insert_or_assign"><span class="pre"><code class="sourceCode python">insert_or_assign</code></span></a> |  | Insert all elements from <span class="pre">`document`</span> into this map. |
| <span class="nerd-font"></span> | <a href="#syside.IdMap.reserve" class="reference internal" title="syside.IdMap.reserve"><span class="pre"><code class="sourceCode python">reserve</code></span></a> |  | Reserve space for <span class="pre">`n`</span> document mappings. |
| <span class="nerd-font"></span> | <a href="#syside.IdMap.search" class="reference internal" title="syside.IdMap.search"><span class="pre"><code class="sourceCode python">search</code></span></a> |  | Search across all registered documents for a matching id. This has complexity O(n) since it searches each document separately. |
| <span class="nerd-font"></span> | <a href="#syside.IdMap.try_insert" class="reference internal" title="syside.IdMap.try_insert"><span class="pre"><code class="sourceCode python">try_insert</code></span></a> |  | Try insert all elements from <span class="pre">`document`</span> into this map. |

</div>

</div>

<span class="nerd-font"></span> **Methods**

<span class="sig-name descname"><span class="pre">\_\_call\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">uri</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="n"><span class="pre">id</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">uuid.UUID</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element"><span class="pre">syside.Element</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span></span></span><a href="#syside.IdMap.__call__" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Short-hand for <span class="pre">`find`</span> or <span class="pre">`search`</span>. Will fall back to <span class="pre">`search`</span> if <span class="pre">`uri`</span> is empty.

<span class="sig-name descname"><span class="pre">\_\_init\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span><a href="#syside.IdMap.__init__" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">clear</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span><a href="#syside.IdMap.clear" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Clear all mapped elements.

<span class="sig-name descname"><span class="pre">erase</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">document</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/Document.md" class="reference internal" title="syside.Document"><span class="pre">syside.Document</span></a></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">int</span></span></span><a href="#syside.IdMap.erase" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Erase all elements assigned to <span class="pre">`document`</span> from this map.

Returns the number of elements erased.

<span class="sig-name descname"><span class="pre">erase</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">uri</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">int</span></span></span>  
Erase all elements assigned to document with <span class="pre">`uri`</span> from this map.

Returns the number of elements erased.

<span class="sig-name descname"><span class="pre">find</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">uri</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="n"><span class="pre">id</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">uuid.UUID</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element"><span class="pre">syside.Element</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span></span></span><a href="#syside.IdMap.find" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Find an element at document with <span class="pre">`uri`</span> that has <span class="pre">`id`</span>.

Returns the element found if any.

<span class="sig-name descname"><span class="pre">insert_or_assign</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">document</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/Document.md" class="reference internal" title="syside.Document"><span class="pre">syside.Document</span></a></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><span class="pre">int</span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">bool</span><span class="p"><span class="pre">\]</span></span></span></span><a href="#syside.IdMap.insert_or_assign" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Insert all elements from <span class="pre">`document`</span> into this map.

Returns the number of elements inserted, and <span class="pre">`True`</span> if insertion took place, <span class="pre">`False`</span> if <span class="pre">`document`</span> was already mapped.

<span class="sig-name descname"><span class="pre">reserve</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">n</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">int</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span><a href="#syside.IdMap.reserve" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Reserve space for <span class="pre">`n`</span> document mappings.

<span class="sig-name descname"><span class="pre">search</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">id</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">uuid.UUID</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element"><span class="pre">syside.Element</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span></span></span><a href="#syside.IdMap.search" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Search across all registered documents for a matching id. This has complexity O(n) since it searches each document separately.

Returns the element found if any.

<span class="sig-name descname"><span class="pre">try_insert</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">document</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/Document.md" class="reference internal" title="syside.Document"><span class="pre">syside.Document</span></a></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><span class="pre">int</span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">bool</span><span class="p"><span class="pre">\]</span></span></span></span><a href="#syside.IdMap.try_insert" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Try insert all elements from <span class="pre">`document`</span> into this map.

Returns the number of elements inserted, and <span class="pre">`True`</span> if insertion took place. This will not override already mapped document elements.

</div>
