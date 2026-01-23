<div id="scheduleoptions" class="section">

# ScheduleOptions<a href="#scheduleoptions" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">ScheduleOptions</span></span><a href="#syside.ScheduleOptions" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
<div class="align-center" align="center">

<img src="data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iZ3JhcGh2aXoiIHN0eWxlPSJ3aWR0aDogNy42MjVyZW07aGVpZ2h0OiAyLjc1cmVtOyIgdmlld2JveD0iMC4wMCAwLjAwIDEyMi4wMCA0NC4wMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGcgY2xhc3M9ImdyYXBoIiBpZD0iZ3JhcGgwIiB0cmFuc2Zvcm09InNjYWxlKDEgMSkgcm90YXRlKDApIHRyYW5zbGF0ZSg0IDQwKSI+Cjx0aXRsZT4lMzwvdGl0bGU+CjxnIGNsYXNzPSJub2RlIiBpZD0ibm9kZTEiPgo8dGl0bGU+U2NoZWR1bGVPcHRpb25zPC90aXRsZT4KPGcgaWQ9ImFfbm9kZTEiPjxhIGhyZWY9IiNzeXNpZGUuU2NoZWR1bGVPcHRpb25zIj4KPHBvbHlnb24gcG9pbnRzPSIxMTQsLTM2IDAsLTM2IDAsMCAxMTQsMCAxMTQsLTM2IiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1iZy1jb2xvcik7c3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1ub2RlLWZnLWNvbG9yKTsiPjwvcG9seWdvbj4KPHRleHQgZm9udC1mYW1pbHk9IkxleGVuZCIgZm9udC1zaXplPSIxMi4wMCIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWNvZGUtZmctY29sb3IpOy0tbWQtZ3JhcGh2aXotaG92ZXItY29sb3I6IHZhcigtLW1kLWdyYXBodml6LWEtaG92ZXItY29sb3IpOyIgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iNTciIHk9Ii0xNC4yIj5TY2hlZHVsZU9wdGlvbnM8L3RleHQ+Cjx0aXRsZT5zeXNpZGUuU2NoZWR1bGVPcHRpb25zPC90aXRsZT48L2E+CjwvZz4KPC9nPgo8L2c+Cjwvc3ZnPg==" class="graphviz" />

</div>

<span class="sd-summary-text">Members defined in <a href="#syside.ScheduleOptions" class="reference internal" title="syside.ScheduleOptions"><span class="pre"><code class="sourceCode python">ScheduleOptions</code></span></a> (6 members)</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |  |
|----|----|----|----|
| <span class="nerd-font"></span> | <a href="#syside.ScheduleOptions.attach_comments" class="reference internal" title="syside.ScheduleOptions.attach_comments"><span class="pre"><code class="sourceCode python">attach_comments</code></span></a> | <span class="pre">`RW`</span> | If true, comments will be attached. Mainly useful for formatters. |
| <span class="nerd-font"></span> | <a href="#syside.ScheduleOptions.cutoff" class="reference internal" title="syside.ScheduleOptions.cutoff"><span class="pre"><code class="sourceCode python">cutoff</code></span></a> | <span class="pre">`RW`</span> | The last stage in the pipeline that will be executed. Any stages higher than <span class="pre">`cutoff`</span> will be ignored. |
| <span class="nerd-font"></span> | <a href="#syside.ScheduleOptions.force_revalidation" class="reference internal" title="syside.ScheduleOptions.force_revalidation"><span class="pre"><code class="sourceCode python">force_revalidation</code></span></a> | <span class="pre">`RW`</span> | If true, validated documents will be validated again. |
| <span class="nerd-font"></span> | <a href="#syside.ScheduleOptions.validation_tier" class="reference internal" title="syside.ScheduleOptions.validation_tier"><span class="pre"><code class="sourceCode python">validation_tier</code></span></a> | <span class="pre">`RW`</span> | Lowest tier of documents to validate. For example, <span class="pre">`Projects`</span> will validate only project documents, while <span class="pre">`StandardLibrary`</span> - everything. |
| <span class="nerd-font"></span> | <a href="#syside.ScheduleOptions.validation_timing" class="reference internal" title="syside.ScheduleOptions.validation_timing"><span class="pre"><code class="sourceCode python">validation_timing</code></span></a> | <span class="pre">`RW`</span> | Which validations to run. |
| <span class="nerd-font"></span> | <a href="#syside.ScheduleOptions.__init__" class="reference internal" title="syside.ScheduleOptions.__init__"><span class="pre"><code class="sourceCode python"><span class="fu">__init__</span></code></span></a> |  |  |

</div>

</div>

<span class="nerd-font"></span> **Attributes**

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">attach_comments</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*<a href="#syside.ScheduleOptions.attach_comments" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
If true, comments will be attached. Mainly useful for formatters.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">cutoff</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside.BuildState"><span class="pre">syside.BuildState</span></a>*<a href="#syside.ScheduleOptions.cutoff" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
The last stage in the pipeline that will be executed. Any stages higher than <span class="pre">`cutoff`</span> will be ignored.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">force_revalidation</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*<a href="#syside.ScheduleOptions.force_revalidation" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
If true, validated documents will be validated again.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">validation_tier</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside.DocumentTier"><span class="pre">syside.DocumentTier</span></a>*<a href="#syside.ScheduleOptions.validation_tier" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Lowest tier of documents to validate. For example, <span class="pre">`Projects`</span> will validate only project documents, while <span class="pre">`StandardLibrary`</span> - everything.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">validation_timing</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside.ValidationTiming"><span class="pre">syside.ValidationTiming</span></a>*<a href="#syside.ScheduleOptions.validation_timing" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Which validations to run.

<span class="nerd-font"></span> **Methods**

<span class="sig-name descname"><span class="pre">\_\_init\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">validation_timing</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside.ValidationTiming"><span class="pre">syside.ValidationTiming</span></a></span>*, *<span class="n"><span class="pre">cutoff</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside.BuildState"><span class="pre">syside.BuildState</span></a></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">BuildState.Validated</span></span>*, *<span class="n"><span class="pre">force_revalidation</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">False</span></span>*, *<span class="n"><span class="pre">attach_comments</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">False</span></span>*, *<span class="n"><span class="pre">validation_tier</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside.DocumentTier"><span class="pre">syside.DocumentTier</span></a></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">DocumentTier.Project</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span><a href="#syside.ScheduleOptions.__init__" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/Pipeline.md" class="reference internal" title="syside.Pipeline"><span class="pre"><code class="sourceCode python">syside.Pipeline</code></span></a>

  - <a href="/python/v0.8.4/syside/Pipeline.md" class="reference internal" title="syside.Pipeline.schedule"><span class="pre"><code class="sourceCode python">schedule</code></span></a>

</div>

</div>
