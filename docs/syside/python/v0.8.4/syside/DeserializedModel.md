<div id="deserializedmodel" class="section">

# DeserializedModel<a href="#deserializedmodel" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">DeserializedModel</span></span><a href="#syside.DeserializedModel" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
The model as it was deserialized, with references potentially unresolved.

<div class="align-center" align="center">

<img src="data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iZ3JhcGh2aXoiIHN0eWxlPSJ3aWR0aDogOC4wNjI1cmVtO2hlaWdodDogMi43NXJlbTsiIHZpZXdib3g9IjAuMDAgMC4wMCAxMjkuMDAgNDQuMDAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxnIGNsYXNzPSJncmFwaCIgaWQ9ImdyYXBoMCIgdHJhbnNmb3JtPSJzY2FsZSgxIDEpIHJvdGF0ZSgwKSB0cmFuc2xhdGUoNCA0MCkiPgo8dGl0bGU+JTM8L3RpdGxlPgo8ZyBjbGFzcz0ibm9kZSIgaWQ9Im5vZGUxIj4KPHRpdGxlPkRlc2VyaWFsaXplZE1vZGVsPC90aXRsZT4KPGcgaWQ9ImFfbm9kZTEiPjxhIGhyZWY9IiNzeXNpZGUuRGVzZXJpYWxpemVkTW9kZWwiPgo8cG9seWdvbiBwb2ludHM9IjEyMSwtMzYgMCwtMzYgMCwwIDEyMSwwIDEyMSwtMzYiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1ncmFwaHZpei1ub2RlLWJnLWNvbG9yKTtzdHJva2U6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtZmctY29sb3IpOyI+PC9wb2x5Z29uPgo8dGV4dCBmb250LWZhbWlseT0iTGV4ZW5kIiBmb250LXNpemU9IjEyLjAwIiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtY29kZS1mZy1jb2xvcik7LS1tZC1ncmFwaHZpei1ob3Zlci1jb2xvcjogdmFyKC0tbWQtZ3JhcGh2aXotYS1ob3Zlci1jb2xvcik7IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSI2MC41IiB5PSItMTQuMiI+RGVzZXJpYWxpemVkTW9kZWw8L3RleHQ+Cjx0aXRsZT5zeXNpZGUuRGVzZXJpYWxpemVkTW9kZWw8L3RpdGxlPjwvYT4KPC9nPgo8L2c+CjwvZz4KPC9zdmc+" class="graphviz" />

</div>

<span class="sd-summary-text">Members defined in <a href="#syside.DeserializedModel" class="reference internal" title="syside.DeserializedModel"><span class="pre"><code class="sourceCode python">DeserializedModel</code></span></a> (4 members)</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |  |
|----|----|----|----|
| <span class="nerd-font"></span> | <a href="#syside.DeserializedModel.document" class="reference internal" title="syside.DeserializedModel.document"><span class="pre"><code class="sourceCode python">document</code></span></a> | <span class="pre">`R`</span> | The document model was deserialized into |
| <span class="nerd-font"></span> | <a href="#syside.DeserializedModel.pending_references" class="reference internal" title="syside.DeserializedModel.pending_references"><span class="pre"><code class="sourceCode python">pending_references</code></span></a> | <span class="pre">`R`</span> | Currently unresolved pending references. These need to be resolved in a separate post-deserialization step to correctly resolve (potentially cyclical) dependencies between models. |
| <span class="nerd-font"></span> | <a href="#syside.DeserializedModel.root" class="reference internal" title="syside.DeserializedModel.root"><span class="pre"><code class="sourceCode python">root</code></span></a> | <span class="pre">`R`</span> | The root node of the deserialized model. Note that this may be an orphan node. |
| <span class="nerd-font"></span> | <a href="#syside.DeserializedModel.link" class="reference internal" title="syside.DeserializedModel.link"><span class="pre"><code class="sourceCode python">link</code></span></a> |  | Attempt to resolve any pending references using custom <span class="pre">`resolve`</span>. Signature is |

</div>

</div>

<span class="nerd-font"></span> **Attributes**

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">document</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/Document.md" class="reference internal" title="syside.Document"><span class="pre">syside.Document</span></a>*<a href="#syside.DeserializedModel.document" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
The document model was deserialized into

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">pending_references</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/ContainerView.md" class="reference internal" title="syside.ContainerView"><span class="pre">syside.ContainerView</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/PendingReference.md" class="reference internal" title="syside.PendingReference"><span class="pre">syside.PendingReference</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.DeserializedModel.pending_references" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Currently unresolved pending references. These need to be resolved in a separate post-deserialization step to correctly resolve (potentially cyclical) dependencies between models.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">root</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element"><span class="pre">syside.Element</span></a>*<a href="#syside.DeserializedModel.root" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
The root node of the deserialized model. Note that this may be an orphan node.

<span class="nerd-font"></span> **Methods**

<span class="sig-name descname"><span class="pre">link</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">resolve</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">Callable</span><span class="p"><span class="pre">\[</span></span><span class="p"><span class="pre">\[</span></span><span class="pre">str</span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">uuid.UUID</span><span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">,</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element"><span class="pre">syside.Element</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span><span class="p"><span class="pre">\]</span></span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/SerdeReport.md" class="reference internal" title="syside.SerdeReport"><span class="pre">syside.SerdeReport</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/DocumentSegment.md" class="reference internal" title="syside.DocumentSegment"><span class="pre">syside.DocumentSegment</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element"><span class="pre">syside.Element</span></a><span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">bool</span><span class="p"><span class="pre">\]</span></span></span></span><a href="#syside.DeserializedModel.link" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Attempt to resolve any pending references using custom <span class="pre">`resolve`</span>. Signature is

<div class="highlight-python notranslate">

<div class="highlight">

    def resolve(uri: str, element_id: uuid.UUID) -> Element | None: ...

</div>

</div>

Returns a pair of <span class="pre">`report`</span> and <span class="pre">`success`</span>, whether all pending references have been resolved. Use <span class="pre">`pending_references`</span> again to get references that failed to resolve.

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside"><span class="pre"><code class="sourceCode python">syside</code></span></a>

  - <a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside.deserialize"><span class="pre"><code class="sourceCode python">deserialize</code></span></a>

- <a href="/python/v0.8.4/syside/Deserializer.md" class="reference internal" title="syside.Deserializer"><span class="pre"><code class="sourceCode python">syside.Deserializer</code></span></a>

  - <a href="/python/v0.8.4/syside/Deserializer.md" class="reference internal" title="syside.Deserializer.accept"><span class="pre"><code class="sourceCode python">accept</code></span></a>

- <a href="/python/v0.8.4/syside/json//README.md" class="reference internal" title="syside.json"><span class="pre"><code class="sourceCode python">syside.json</code></span></a>

  - <a href="/python/v0.8.4/syside/json//README.md" class="reference internal" title="syside.json.loads"><span class="pre"><code class="sourceCode python">loads</code></span></a>

- <a href="/python/v0.8.4/syside/json/DeserializationError.md" class="reference internal" title="syside.json.DeserializationError"><span class="pre"><code class="sourceCode python">syside.json.DeserializationError</code></span></a>

  - <a href="/python/v0.8.4/syside/json/DeserializationError.md" class="reference internal" title="syside.json.DeserializationError.model"><span class="pre"><code class="sourceCode python">model</code></span></a>

- <a href="/python/v0.8.4/syside/json/ProjectDeserializationError.md" class="reference internal" title="syside.json.ProjectDeserializationError"><span class="pre"><code class="sourceCode python">syside.json.ProjectDeserializationError</code></span></a>

  - <a href="/python/v0.8.4/syside/json/ProjectDeserializationError.md" class="reference internal" title="syside.json.ProjectDeserializationError.models"><span class="pre"><code class="sourceCode python">models</code></span></a>

</div>

</div>
