<div id="serializationoptions" class="section">

# SerializationOptions<a href="#serializationoptions" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">SerializationOptions</span></span><a href="#syside.SerializationOptions" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Options for SysML model serialization. Attribute options are ordered in descending precedence.

<div class="align-center" align="center">

<img src="data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iZ3JhcGh2aXoiIHN0eWxlPSJ3aWR0aDogOC44NzVyZW07aGVpZ2h0OiAyLjc1cmVtOyIgdmlld2JveD0iMC4wMCAwLjAwIDE0Mi4wMCA0NC4wMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGcgY2xhc3M9ImdyYXBoIiBpZD0iZ3JhcGgwIiB0cmFuc2Zvcm09InNjYWxlKDEgMSkgcm90YXRlKDApIHRyYW5zbGF0ZSg0IDQwKSI+Cjx0aXRsZT4lMzwvdGl0bGU+CjxnIGNsYXNzPSJub2RlIiBpZD0ibm9kZTEiPgo8dGl0bGU+U2VyaWFsaXphdGlvbk9wdGlvbnM8L3RpdGxlPgo8ZyBpZD0iYV9ub2RlMSI+PGEgaHJlZj0iI3N5c2lkZS5TZXJpYWxpemF0aW9uT3B0aW9ucyI+Cjxwb2x5Z29uIHBvaW50cz0iMTM0LC0zNiAwLC0zNiAwLDAgMTM0LDAgMTM0LC0zNiIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtYmctY29sb3IpO3N0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1mZy1jb2xvcik7Ij48L3BvbHlnb24+Cjx0ZXh0IGZvbnQtZmFtaWx5PSJMZXhlbmQiIGZvbnQtc2l6ZT0iMTIuMDAiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1jb2RlLWZnLWNvbG9yKTstLW1kLWdyYXBodml6LWhvdmVyLWNvbG9yOiB2YXIoLS1tZC1ncmFwaHZpei1hLWhvdmVyLWNvbG9yKTsiIHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjY3IiB5PSItMTQuMiI+U2VyaWFsaXphdGlvbk9wdGlvbnM8L3RleHQ+Cjx0aXRsZT5zeXNpZGUuU2VyaWFsaXphdGlvbk9wdGlvbnM8L3RpdGxlPjwvYT4KPC9nPgo8L2c+CjwvZz4KPC9zdmc+" class="graphviz" />

</div>

<span class="sd-summary-text">Members defined in <a href="#syside.SerializationOptions" class="reference internal" title="syside.SerializationOptions"><span class="pre"><code class="sourceCode python">SerializationOptions</code></span></a> (10 members)</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |  |
|----|----|----|----|
| <span class="nerd-font"></span> | <a href="#syside.SerializationOptions.fail_action" class="reference internal" title="syside.SerializationOptions.fail_action"><span class="pre"><code class="sourceCode python">fail_action</code></span></a> | <span class="pre">`RW`</span> | Action to take on serialization errors. |
| <span class="nerd-font"></span> | <a href="#syside.SerializationOptions.include_default" class="reference internal" title="syside.SerializationOptions.include_default"><span class="pre"><code class="sourceCode python">include_default</code></span></a> | <span class="pre">`RW`</span> | If true, serialize attributes even if they match their default values. |
| <span class="nerd-font"></span> | <a href="#syside.SerializationOptions.include_derived" class="reference internal" title="syside.SerializationOptions.include_derived"><span class="pre"><code class="sourceCode python">include_derived</code></span></a> | <span class="pre">`RW`</span> | If true, serialize derived attributes. Corresponds to <span class="pre">`includesDerived`</span> flag in the specification (KerML 10.3, Table 13): |
| <span class="nerd-font"></span> | <a href="#syside.SerializationOptions.include_implied" class="reference internal" title="syside.SerializationOptions.include_implied"><span class="pre"><code class="sourceCode python">include_implied</code></span></a> | <span class="pre">`RW`</span> | If true, serialize implicit elements. Only for attributes that are serialized. Corresponds to <span class="pre">`includesImplied`</span> flag in the specification (KerML 10.3, Table 13): |
| <span class="nerd-font"></span> | <a href="#syside.SerializationOptions.include_optional" class="reference internal" title="syside.SerializationOptions.include_optional"><span class="pre"><code class="sourceCode python">include_optional</code></span></a> | <span class="pre">`RW`</span> | If true, non-required attributes will be serialized even if they are null or empty. |
| <span class="nerd-font"></span> | <a href="#syside.SerializationOptions.include_redefined" class="reference internal" title="syside.SerializationOptions.include_redefined"><span class="pre"><code class="sourceCode python">include_redefined</code></span></a> | <span class="pre">`RW`</span> | If true, serialize attributes even if they are redefined in the metamodel. |
| <span class="nerd-font"></span> | <a href="#syside.SerializationOptions.use_standard_names" class="reference internal" title="syside.SerializationOptions.use_standard_names"><span class="pre"><code class="sourceCode python">use_standard_names</code></span></a> | <span class="pre">`RW`</span> | If true, fields will be serialized using standard names |
| <span class="nerd-font"></span> | <a href="#syside.SerializationOptions.__init__" class="reference internal" title="syside.SerializationOptions.__init__"><span class="pre"><code class="sourceCode python"><span class="fu">__init__</span></code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.SerializationOptions.minimal" class="reference internal" title="syside.SerializationOptions.minimal"><span class="pre"><code class="sourceCode python">minimal</code></span></a> |  | Configuration that instructs the writer to produce a minimal JSON without any redundant elements. Examples of redundant information that is avoided using the minimal configuration are: |
| <span class="nerd-font"></span> | <a href="#syside.SerializationOptions.with_options" class="reference internal" title="syside.SerializationOptions.with_options"><span class="pre"><code class="sourceCode python">with_options</code></span></a> |  | Creates a copy with the specified options changed to the given ones. |

</div>

</div>

<span class="nerd-font"></span> **Attributes**

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">fail_action</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside.FailAction"><span class="pre">syside.FailAction</span></a>*<a href="#syside.SerializationOptions.fail_action" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Action to take on serialization errors.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">include_default</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*<a href="#syside.SerializationOptions.include_default" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
If true, serialize attributes even if they match their default values.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">include_derived</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*<a href="#syside.SerializationOptions.include_derived" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
If true, serialize derived attributes. Corresponds to <span class="pre">`includesDerived`</span> flag in the specification (KerML 10.3, Table 13):

> <div>
>
> Whether derived property values are included in the model interchange files.
>
> </div>

**Note:** Syside does not construct all derived properties yet. Therefore, setting <span class="pre">`options.include_derived`</span> to <span class="pre">`True`</span> may result in a JSON that does not satisfy the schema.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">include_implied</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*<a href="#syside.SerializationOptions.include_implied" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
If true, serialize implicit elements. Only for attributes that are serialized. Corresponds to <span class="pre">`includesImplied`</span> flag in the specification (KerML 10.3, Table 13):

> <div>
>
> Whether implied relationships are included in the model interchange files.
>
> </div>

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">include_optional</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*<a href="#syside.SerializationOptions.include_optional" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
If true, non-required attributes will be serialized even if they are null or empty.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">include_redefined</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*<a href="#syside.SerializationOptions.include_redefined" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
If true, serialize attributes even if they are redefined in the metamodel.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">use_standard_names</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*<a href="#syside.SerializationOptions.use_standard_names" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
If true, fields will be serialized using standard names

<span class="nerd-font"></span> **Methods**

<span class="sig-name descname"><span class="pre">\_\_init\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">use_standard_names</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">True</span></span>*, *<span class="n"><span class="pre">include_derived</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">False</span></span>*, *<span class="n"><span class="pre">include_redefined</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">False</span></span>*, *<span class="n"><span class="pre">include_default</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">False</span></span>*, *<span class="n"><span class="pre">include_optional</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">False</span></span>*, *<span class="n"><span class="pre">include_implied</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">False</span></span>*, *<span class="n"><span class="pre">fail_action</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside.FailAction"><span class="pre">syside.FailAction</span></a></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">FailAction.Diagnose</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span><a href="#syside.SerializationOptions.__init__" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

*<span class="pre">static</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">minimal</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="#syside.SerializationOptions" class="reference internal" title="syside.SerializationOptions"><span class="pre">syside.SerializationOptions</span></a></span></span><a href="#syside.SerializationOptions.minimal" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Configuration that instructs the writer to produce a minimal JSON without any redundant elements. Examples of redundant information that is avoided using the minimal configuration are:

- including fields for null values;

- including fields whose values match the default values;

- including redefined fields that are duplicates of redefining fields;

- including derived fields that can be computed from minimal JSON (for example, the result value of evaluating an expression);

- including implied relationships.

<span class="sig-name descname"><span class="pre">with_options</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">use_standard_names</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">None</span></span>*, *<span class="n"><span class="pre">include_derived</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">None</span></span>*, *<span class="n"><span class="pre">include_redefined</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">None</span></span>*, *<span class="n"><span class="pre">include_default</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">None</span></span>*, *<span class="n"><span class="pre">include_optional</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">None</span></span>*, *<span class="n"><span class="pre">include_implied</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">None</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="#syside.SerializationOptions" class="reference internal" title="syside.SerializationOptions"><span class="pre">syside.SerializationOptions</span></a></span></span><a href="#syside.SerializationOptions.with_options" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Creates a copy with the specified options changed to the given ones.

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside"><span class="pre"><code class="sourceCode python">syside</code></span></a>

  - <a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside.serialize"><span class="pre"><code class="sourceCode python">serialize</code></span></a>

- <a href="#syside.SerializationOptions" class="reference internal" title="syside.SerializationOptions"><span class="pre"><code class="sourceCode python">syside.SerializationOptions</code></span></a>

  - <a href="#syside.SerializationOptions.minimal" class="reference internal" title="syside.SerializationOptions.minimal"><span class="pre"><code class="sourceCode python">minimal</code></span></a>

  - <a href="#syside.SerializationOptions.with_options" class="reference internal" title="syside.SerializationOptions.with_options"><span class="pre"><code class="sourceCode python">with_options</code></span></a>

- <a href="/python/v0.8.4/syside/Serializer.md" class="reference internal" title="syside.Serializer"><span class="pre"><code class="sourceCode python">syside.Serializer</code></span></a>

  - <a href="/python/v0.8.4/syside/Serializer.md" class="reference internal" title="syside.Serializer.accept"><span class="pre"><code class="sourceCode python">accept</code></span></a>

- <a href="/python/v0.8.4/syside/json//README.md" class="reference internal" title="syside.json"><span class="pre"><code class="sourceCode python">syside.json</code></span></a>

  - <a href="/python/v0.8.4/syside/json//README.md" class="reference internal" title="syside.json.dumps"><span class="pre"><code class="sourceCode python">dumps</code></span></a>

</div>

</div>
