<div id="deserializer" class="section">

# Deserializer<a href="#deserializer" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">Deserializer</span></span><a href="#syside.Deserializer" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Deserializer for SysML models. The actual deserialization input depends on used <span class="pre">`Reader`</span>.

Note that unlike <span class="pre">`Serializer`</span> deserialization cannot be completed in a single pass in general because documents may form reference cycles with each other. The typical deserialization pattern will be

<div class="highlight-python notranslate">

<div class="highlight">

    des = Deserializer(document)
    model, report = des.accept(reader, DESERIALIZE_STANDARD)
    # ... collect all valid element ids for linking
    link_report, all_linked = model.link(my_reference_resolve)

</div>

</div>

<div class="align-center" align="center">

<img src="data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iZ3JhcGh2aXoiIHN0eWxlPSJ3aWR0aDogNS42ODc1cmVtO2hlaWdodDogMi43NXJlbTsiIHZpZXdib3g9IjAuMDAgMC4wMCA5MS4wMCA0NC4wMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGcgY2xhc3M9ImdyYXBoIiBpZD0iZ3JhcGgwIiB0cmFuc2Zvcm09InNjYWxlKDEgMSkgcm90YXRlKDApIHRyYW5zbGF0ZSg0IDQwKSI+Cjx0aXRsZT4lMzwvdGl0bGU+CjxnIGNsYXNzPSJub2RlIiBpZD0ibm9kZTEiPgo8dGl0bGU+RGVzZXJpYWxpemVyPC90aXRsZT4KPGcgaWQ9ImFfbm9kZTEiPjxhIGhyZWY9IiNzeXNpZGUuRGVzZXJpYWxpemVyIj4KPHBvbHlnb24gcG9pbnRzPSI4MywtMzYgMCwtMzYgMCwwIDgzLDAgODMsLTM2IiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1iZy1jb2xvcik7c3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1ub2RlLWZnLWNvbG9yKTsiPjwvcG9seWdvbj4KPHRleHQgZm9udC1mYW1pbHk9IkxleGVuZCIgZm9udC1zaXplPSIxMi4wMCIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWNvZGUtZmctY29sb3IpOy0tbWQtZ3JhcGh2aXotaG92ZXItY29sb3I6IHZhcigtLW1kLWdyYXBodml6LWEtaG92ZXItY29sb3IpOyIgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iNDEuNSIgeT0iLTE0LjIiPkRlc2VyaWFsaXplcjwvdGV4dD4KPHRpdGxlPnN5c2lkZS5EZXNlcmlhbGl6ZXI8L3RpdGxlPjwvYT4KPC9nPgo8L2c+CjwvZz4KPC9zdmc+" class="graphviz" />

</div>

<span class="sd-summary-text">Members defined in <a href="#syside.Deserializer" class="reference internal" title="syside.Deserializer"><span class="pre"><code class="sourceCode python">Deserializer</code></span></a> (4 members)</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |  |
|----|----|----|----|
| <span class="nerd-font"></span> | <a href="#syside.Deserializer.document" class="reference internal" title="syside.Deserializer.document"><span class="pre"><code class="sourceCode python">document</code></span></a> | <span class="pre">`R`</span> | The document bound to this deserializer |
| <span class="nerd-font"></span> | <a href="#syside.Deserializer.__init__" class="reference internal" title="syside.Deserializer.__init__"><span class="pre"><code class="sourceCode python"><span class="fu">__init__</span></code></span></a> |  | Construct a new deserializer that will deserialize models into the provided <span class="pre">`document`</span>. |
| <span class="nerd-font"></span> | <a href="#syside.Deserializer.accept" class="reference internal" title="syside.Deserializer.accept"><span class="pre"><code class="sourceCode python">accept</code></span></a> |  | Accept a <span class="pre">`reader`</span> for deserialization into currently bound <span class="pre">`document`</span>. Returns the deserialized model, or raises a <span class="pre">`RuntimeError`</span>. <span class="pre">`document`</span> without a <a href="/python/v0.8.4/syside/Url.md" class="reference internal" title="syside.Url"><span class="pre"><code class="sourceCode python">Url</code></span></a> with scheme will emit a warning that relative URIs will not be resolvable. |
| <span class="nerd-font"></span> | <a href="#syside.Deserializer.reset" class="reference internal" title="syside.Deserializer.reset"><span class="pre"><code class="sourceCode python">reset</code></span></a> |  | Reset the deserializer. Rebinds to the <span class="pre">`document`</span> and resets this <span class="pre">`Deserializer`</span> for new deserialization. |

</div>

</div>

<span class="nerd-font"></span> **Attributes**

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">document</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/Document.md" class="reference internal" title="syside.Document"><span class="pre">syside.Document</span></a>*<a href="#syside.Deserializer.document" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
The document bound to this deserializer

<span class="nerd-font"></span> **Methods**

<span class="sig-name descname"><span class="pre">\_\_init\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">document</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/Document.md" class="reference internal" title="syside.Document"><span class="pre">syside.Document</span></a></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span><a href="#syside.Deserializer.__init__" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Construct a new deserializer that will deserialize models into the provided <span class="pre">`document`</span>.

<span class="sig-name descname"><span class="pre">accept</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">reader</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/Reader.md" class="reference internal" title="syside.Reader"><span class="pre">syside.Reader</span></a></span>*, *<span class="n"><span class="pre">attributes</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/AttributeMap.md" class="reference internal" title="syside.AttributeMap"><span class="pre">syside.AttributeMap</span></a></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/DeserializedModel.md" class="reference internal" title="syside.DeserializedModel"><span class="pre">syside.DeserializedModel</span></a><span class="p"><span class="pre">,</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/SerdeReport.md" class="reference internal" title="syside.SerdeReport"><span class="pre">syside.SerdeReport</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/DocumentSegment.md" class="reference internal" title="syside.DocumentSegment"><span class="pre">syside.DocumentSegment</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element"><span class="pre">syside.Element</span></a><span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">\]</span></span></span></span><a href="#syside.Deserializer.accept" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Accept a <span class="pre">`reader`</span> for deserialization into currently bound <span class="pre">`document`</span>. Returns the deserialized model, or raises a <span class="pre">`RuntimeError`</span>. <span class="pre">`document`</span> without a <a href="/python/v0.8.4/syside/Url.md" class="reference internal" title="syside.Url"><span class="pre"><code class="sourceCode python">Url</code></span></a> with scheme will emit a warning that relative URIs will not be resolvable.

Note that cross-references may not be resolved, and instead replaced by placeholder element references due to potential reference cycles between documents. Call <span class="pre">`link`</span> on the returned model when dependent documents have been loaded.

<span class="sig-name descname"><span class="pre">accept</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">document</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/Document.md" class="reference internal" title="syside.Document"><span class="pre">syside.Document</span></a></span>*, *<span class="n"><span class="pre">reader</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/Reader.md" class="reference internal" title="syside.Reader"><span class="pre">syside.Reader</span></a></span>*, *<span class="n"><span class="pre">attributes</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/AttributeMap.md" class="reference internal" title="syside.AttributeMap"><span class="pre">syside.AttributeMap</span></a></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/DeserializedModel.md" class="reference internal" title="syside.DeserializedModel"><span class="pre">syside.DeserializedModel</span></a><span class="p"><span class="pre">,</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/SerdeReport.md" class="reference internal" title="syside.SerdeReport"><span class="pre">syside.SerdeReport</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/DocumentSegment.md" class="reference internal" title="syside.DocumentSegment"><span class="pre">syside.DocumentSegment</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element"><span class="pre">syside.Element</span></a><span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">\]</span></span></span></span>  
Accept <span class="pre">`reader`</span> for deserialization into <span class="pre">`document`</span>. Equivalent to

<div class="highlight-python notranslate">

<div class="highlight">

    deserializer.reset(document)
    return deserializer.accept(reader, attributes)

</div>

</div>

Returns the deserialized model, or raises <span class="pre">`RuntimeError`</span>.

<span class="sig-name descname"><span class="pre">reset</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">document</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/Document.md" class="reference internal" title="syside.Document"><span class="pre">syside.Document</span></a></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span><a href="#syside.Deserializer.reset" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Reset the deserializer. Rebinds to the <span class="pre">`document`</span> and resets this <span class="pre">`Deserializer`</span> for new deserialization.

</div>
