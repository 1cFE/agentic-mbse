<div id="module-syside.json" class="section">

<span id="json-labs"></span>

# json <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">Labs</span><a href="#module-syside.json" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

Convenience module intending to match the standard library <span class="pre">`json`</span> module.

<div id="index" class="section">

## <span class="nerd-font"></span> Index<a href="#index" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

<span class="sd-summary-text"><span class="nerd-font"></span> **Classes** <a href="#syside-json-classes-table" class="reference internal"><span class="std std-ref"></span></a></span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |
|----|----|----|
| <a href="/python/v0.8.4/syside/json/DeserializationError.md" class="reference internal" title="syside.json.DeserializationError"><span class="pre"><code class="sourceCode python">DeserializationError</code></span></a> |  | Error deserializing document from SysML v2 JSON. |
| <a href="/python/v0.8.4/syside/json/ProjectDeserializationError.md" class="reference internal" title="syside.json.ProjectDeserializationError"><span class="pre"><code class="sourceCode python">ProjectDeserializationError</code></span></a> |  | Error deserializing project from SysML v2 JSON. |
| <a href="/python/v0.8.4/syside/json/SerdeError.md" class="reference internal" title="syside.json.SerdeError"><span class="pre"><code class="sourceCode python">SerdeError</code></span></a> |  | Class for exceptions from serialization and deserialization |
| <a href="/python/v0.8.4/syside/json/SerdeWarning.md" class="reference internal" title="syside.json.SerdeWarning"><span class="pre"><code class="sourceCode python">SerdeWarning</code></span></a> |  | Class for warnings from serialization and deserialization |
| <a href="/python/v0.8.4/syside/json/SerializationError.md" class="reference internal" title="syside.json.SerializationError"><span class="pre"><code class="sourceCode python">SerializationError</code></span></a> |  | Error serializing element to SysML v2 JSON. |

</div>

</div>

<span class="sd-summary-text"><span class="nerd-font"></span> **Attributes** <a href="#syside-json-attributes-table" class="reference internal"><span class="std std-ref"></span></a></span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |
|----|----|----|
| <a href="#syside.json.DeserializationReport" class="reference internal" title="syside.json.DeserializationReport"><span class="pre"><code class="sourceCode python">DeserializationReport</code></span></a> |  |  |
| <a href="#syside.json.JsonSourceInto" class="reference internal" title="syside.json.JsonSourceInto"><span class="pre"><code class="sourceCode python">JsonSourceInto</code></span></a> |  |  |
| <a href="#syside.json.JsonSourceNew" class="reference internal" title="syside.json.JsonSourceNew"><span class="pre"><code class="sourceCode python">JsonSourceNew</code></span></a> |  |  |

</div>

</div>

<span class="sd-summary-text"><span class="nerd-font"></span> **Functions** <a href="#syside-json-functions-table" class="reference internal"><span class="std std-ref"></span></a></span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |
|----|----|----|
| <a href="#syside.json.dumps" class="reference internal" title="syside.json.dumps"><span class="pre"><code class="sourceCode python">dumps</code></span></a> |  | Serialize <span class="pre">`element`</span> to a SysML v2 JSON <span class="pre">`str`</span>. |
| <a href="#syside.json.loads" class="reference internal" title="syside.json.loads"><span class="pre"><code class="sourceCode python">loads</code></span></a> |  |  |

</div>

</div>

</div>

------------------------------------------------------------------------

<div id="attributes" class="section">

## <span class="nerd-font"></span> Attributes<a href="#attributes" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

*<span class="pre">type</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">DeserializationReport</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/SerdeReport.md" class="reference internal" title="syside.SerdeReport"><span class="pre">syside.SerdeReport</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element"><span class="pre">syside.Element</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/DocumentSegment.md" class="reference internal" title="syside.DocumentSegment"><span class="pre">syside.DocumentSegment</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.json.DeserializationReport" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<!-- -->

*<span class="pre">type</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">JsonSourceInto</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Document.md" class="reference internal" title="syside.Document"><span class="pre">syside.Document</span></a><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">str</span><span class="p"><span class="pre">\]</span></span>*<a href="#syside.json.JsonSourceInto" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<!-- -->

*<span class="pre">type</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">JsonSourceNew</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/Url.md" class="reference internal" title="syside.Url"><span class="pre">syside.Url</span></a><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">str</span><span class="p"><span class="pre">\]</span></span>*<a href="#syside.json.JsonSourceNew" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="#module-syside.json" class="reference internal" title="syside.json"><span class="pre"><code class="sourceCode python">syside.json</code></span></a>

  - <a href="#syside.json.loads" class="reference internal" title="syside.json.loads"><span class="pre"><code class="sourceCode python">loads</code></span></a>

</div>

</div>

<div id="functions" class="section">

## <span class="nerd-font">󰊕</span> Functions<a href="#functions" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

<span class="sig-name descname"><span class="pre">dumps</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">element</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element"><span class="pre">syside.Element</span></a></span>*, *<span class="n"><span class="pre">options</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/SerializationOptions.md" class="reference internal" title="syside.SerializationOptions"><span class="pre">syside.SerializationOptions</span></a></span>*, *<span class="n"><span class="pre">indent</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">int</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">2</span></span>*, *<span class="n"><span class="pre">use_spaces</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">True</span></span>*, *<span class="n"><span class="pre">final_new_line</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">True</span></span>*, *<span class="n"><span class="pre">include_cross_ref_uris</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">True</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">str</span></span></span><a href="/python/v0.8.4/_modules/syside/json.md" class="reference internal"><span class="viewcode-link"><span class="pre">[source]</span></span></a><a href="#syside.json.dumps" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Serialize <span class="pre">`element`</span> to a SysML v2 JSON <span class="pre">`str`</span>.

See the documentation of the <a href="/python/v0.8.4/syside/SerializationOptions.md" class="reference internal" title="syside.SerializationOptions"><span class="pre"><code class="sourceCode python">SerializationOptions</code></span></a> class for documentation of the possible options. The options object constructed with <a href="/python/v0.8.4/syside/SerializationOptions.md" class="reference internal" title="syside.SerializationOptions.minimal"><span class="pre"><code class="sourceCode python">SerializationOptions.minimal</code></span></a> instructs to produce a minimal JSON without any redundant elements that results in significantly smaller JSONs. Examples of redundant information that is avoided using minimal configuration are:

- including fields for null values;

- including fields whose values match the default values;

- including redefined fields that are duplicates of redefining fields;

- including derived fields that can be computed from minimal JSON (for example, the result value of evaluating an expression);

- including implied relationships.

<div class="admonition note">

Note

Syside does not construct all derived properties yet. Therefore, setting <span class="pre">`options.include_derived`</span> to <span class="pre">`True`</span> may result in a JSON that does not satisfy the schema.

</div>

Parameters<span class="colon">:</span>  
- **element** – The SysML v2 element to be serialized to SysML v2 JSON.

- **options** – The serialization options to use when serializing SysML v2 to JSON.

- **indent** – How many space or tab characters to use for indenting the JSON.

- **use_spaces** – Whether use spaces or tabs for indentation.

- **final_new_line** – Whether to add a newline character at the end of the generated string.

- **include_cross_ref_uris** – Whether to add potentially relative URIs as <span class="pre">`@uri`</span> property to references of Elements from documents other than the one owning <span class="pre">`element`</span>. Note that while such references are non-standard, they match the behaviour of XMI exports in Pilot implementation which use relative URIs for references instead of plain element IDs.

Returns<span class="colon">:</span>  
<span class="pre">`element`</span> serialized as JSON.

<!-- -->

<span class="sig-name descname"><span class="pre">loads</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">s</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="n"><span class="pre">document</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/Document.md" class="reference internal" title="syside.Document"><span class="pre">syside.Document</span></a></span>*, *<span class="n"><span class="pre">attributes</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/AttributeMap.md" class="reference internal" title="syside.AttributeMap"><span class="pre">syside.AttributeMap</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">None</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="/python/v0.8.4/syside/DeserializedModel.md" class="reference internal" title="syside.DeserializedModel"><span class="pre">syside.DeserializedModel</span></a></span></span><a href="/python/v0.8.4/_modules/syside/json.md" class="reference internal"><span class="viewcode-link"><span class="pre">[source]</span></span></a><a href="#syside.json.loads" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Deserialize a model from <span class="pre">`s`</span> into an already existing <span class="pre">`document`</span>.

Root node will be inferred as:

1.  The first <span class="pre">`Namespace`</span> (not subtype) without an owning relationship.

2.  The first <span class="pre">`Element`</span> that has no serialized owning related element or owning relationship, starting from the first element in the JSON array, and following owning elements up.

3.  The first element in the array otherwise.

Parameters<span class="colon">:</span>  
- **s** – The string contained serialized SysML model in JSON array.

- **document** – The document the model will be deserialized into.

- **attributes** – Attribute mapping of <span class="pre">`s`</span>. If none provided, this will attempt to infer a corresponding mapping or raise a <span class="pre">`ValueError`</span>.

Returns<span class="colon">:</span>  
Model deserialized from JSON array. Note that references into other documents will not be resolved, users will need to resolve them by calling <span class="pre">`link`</span> on the returned model. See also <a href="/python/v0.8.4/syside/IdMap.md" class="reference internal" title="syside.IdMap"><span class="pre"><code class="sourceCode python">IdMap</code></span></a>.

<!-- -->

<span class="sig-name descname"><span class="pre">loads</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">s</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="n"><span class="pre">document</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/Url.md" class="reference internal" title="syside.Url"><span class="pre">syside.Url</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">str</span></span>*, *<span class="n"><span class="pre">attributes</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/AttributeMap.md" class="reference internal" title="syside.AttributeMap"><span class="pre">syside.AttributeMap</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">None</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/DeserializedModel.md" class="reference internal" title="syside.DeserializedModel"><span class="pre">syside.DeserializedModel</span></a><span class="p"><span class="pre">,</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/SharedMutex.md" class="reference internal" title="syside.SharedMutex"><span class="pre">syside.SharedMutex</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Document.md" class="reference internal" title="syside.Document"><span class="pre">syside.Document</span></a><span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">\]</span></span></span></span><a href="/python/v0.8.4/_modules/syside/json.md" class="reference internal"><span class="viewcode-link"><span class="pre">[source]</span></span></a>  
Create a new <span class="pre">`document`</span> and deserialize a model from <span class="pre">`s`</span> into it.

Root node will be inferred as:

1.  The first <span class="pre">`Namespace`</span> (not subtype) without an owning relationship.

2.  The first <span class="pre">`Element`</span> that has no serialized owning related element or owning relationship, starting from the first element in the JSON array, and following owning elements up.

3.  The first element in the array otherwise.

Parameters<span class="colon">:</span>  
- **s** – The string contained serialized SysML model in JSON array.

- **document** – A URI in the form of <a href="/python/v0.8.4/syside/Url.md" class="reference internal" title="syside.Url"><span class="pre"><code class="sourceCode python">Url</code></span></a> or a string, new document will be created with. If URI path has no extension, or the extension does not match <span class="pre">`sysml`</span> or <span class="pre">`kerml`</span>, <span class="pre">`ValueError`</span> is raised.

- **attributes** – Attribute mapping of <span class="pre">`s`</span>. If none provided, this will attempt to infer a corresponding mapping or raise a <span class="pre">`ValueError`</span>.

Returns<span class="colon">:</span>  
Model deserialized from JSON array and the newly created document. Note that references into other documents will not be resolved, users will need to resolve them by calling <span class="pre">`link`</span> on the returned model. See also <a href="/python/v0.8.4/syside/IdMap.md" class="reference internal" title="syside.IdMap"><span class="pre"><code class="sourceCode python">IdMap</code></span></a>.

<!-- -->

<span class="sig-name descname"><span class="pre">loads</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">s</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">Iterable</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.json.JsonSourceNew</span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">syside.json.JsonSourceInto</span><span class="p"><span class="pre">\]</span></span></span>*, *<span class="o"><span class="pre">/</span></span>*, *<span class="n"><span class="pre">environment</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/Environment.md" class="reference internal" title="syside.Environment"><span class="pre">syside.Environment</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">None</span></span>*, *<span class="n"><span class="pre">resolve</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">Callable</span><span class="p"><span class="pre">\[</span></span><span class="p"><span class="pre">\[</span></span><span class="pre">str</span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">uuid.UUID</span><span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">,</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element"><span class="pre">syside.Element</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span><span class="p"><span class="pre">\]</span></span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">None</span></span>*, *<span class="n"><span class="pre">attributes</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/AttributeMap.md" class="reference internal" title="syside.AttributeMap"><span class="pre">syside.AttributeMap</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">None</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/BaseModel.md" class="reference internal" title="syside.BaseModel"><span class="pre">syside.BaseModel</span></a><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">list</span><span class="p"><span class="pre">\[</span></span><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/DeserializedModel.md" class="reference internal" title="syside.DeserializedModel"><span class="pre">syside.DeserializedModel</span></a><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">syside.json.DeserializationReport</span><span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">\]</span></span></span></span><a href="/python/v0.8.4/_modules/syside/json.md" class="reference internal"><span class="viewcode-link"><span class="pre">[source]</span></span></a>  
Deserialize a project of multiple documents from <span class="pre">`s`</span>.

This is effectively calling <span class="pre">`loads(src,`</span>` `<span class="pre">`document,`</span>` `<span class="pre">`attributes)`</span>` `<span class="pre">`for`</span>` `<span class="pre">`document,`</span>` `<span class="pre">`src`</span>` `<span class="pre">`in`</span>` `<span class="pre">`s`</span> and performing the link step afterwards. See also other overloads of <span class="pre">`loads`</span>.

Parameters<span class="colon">:</span>  
- **s** – Projects sources to deserialize from. If providing a URL string or a <span class="pre">`Url`</span>, new documents will be created for corresponding sources, otherwise deserialization will be performed into the provided <span class="pre">`Documents`</span>.

- **environment** – <span class="pre">`Environment`</span> this project depends on. Defaults to the bundled standard library. The <span class="pre">`environment`</span> will be used to attempt to resolve missing references in the deserialized project.

- **resolve** – User-provided reference resolution callback that takes priority over <span class="pre">`environment`</span>. See <a href="/python/v0.8.4/syside/DeserializedModel.md" class="reference internal" title="syside.DeserializedModel.link"><span class="pre"><code class="sourceCode python">DeserializedModel.link</code></span></a> for more details.

- **attributes** – Attribute mapping of <span class="pre">`s`</span>. If none provided, this will attempt to infer a corresponding mapping or raise a <span class="pre">`ValueError`</span>.

Returns<span class="colon">:</span>  
A tuple of project deserialized from JSON sources, and deserialization results

Raises<span class="colon">:</span>  
<a href="/python/v0.8.4/syside/json/ProjectDeserializationError.md" class="reference internal" title="syside.json.ProjectDeserializationError"><strong>ProjectDeserializationError</strong></a> – If either the deserialization or the reference resolution had errors.

<div class="toctree-wrapper compound">

</div>

</div>

</div>
