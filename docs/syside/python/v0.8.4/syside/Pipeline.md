<div id="pipeline" class="section">

# Pipeline<a href="#pipeline" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">Pipeline</span></span><a href="#syside.Pipeline" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
<div class="align-center" align="center">

<img src="data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iZ3JhcGh2aXoiIHN0eWxlPSJ3aWR0aDogNC4zMTI1cmVtO2hlaWdodDogMi43NXJlbTsiIHZpZXdib3g9IjAuMDAgMC4wMCA2OS4wMCA0NC4wMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGcgY2xhc3M9ImdyYXBoIiBpZD0iZ3JhcGgwIiB0cmFuc2Zvcm09InNjYWxlKDEgMSkgcm90YXRlKDApIHRyYW5zbGF0ZSg0IDQwKSI+Cjx0aXRsZT4lMzwvdGl0bGU+CjxnIGNsYXNzPSJub2RlIiBpZD0ibm9kZTEiPgo8dGl0bGU+UGlwZWxpbmU8L3RpdGxlPgo8ZyBpZD0iYV9ub2RlMSI+PGEgaHJlZj0iI3N5c2lkZS5QaXBlbGluZSI+Cjxwb2x5Z29uIHBvaW50cz0iNjEsLTM2IDAsLTM2IDAsMCA2MSwwIDYxLC0zNiIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtYmctY29sb3IpO3N0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1mZy1jb2xvcik7Ij48L3BvbHlnb24+Cjx0ZXh0IGZvbnQtZmFtaWx5PSJMZXhlbmQiIGZvbnQtc2l6ZT0iMTIuMDAiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1jb2RlLWZnLWNvbG9yKTstLW1kLWdyYXBodml6LWhvdmVyLWNvbG9yOiB2YXIoLS1tZC1ncmFwaHZpei1hLWhvdmVyLWNvbG9yKTsiIHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjMwLjUiIHk9Ii0xNC4yIj5QaXBlbGluZTwvdGV4dD4KPHRpdGxlPnN5c2lkZS5QaXBlbGluZTwvdGl0bGU+PC9hPgo8L2c+CjwvZz4KPC9nPgo8L3N2Zz4=" class="graphviz" />

</div>

<span class="sd-summary-text">Members defined in <a href="#syside.Pipeline" class="reference internal" title="syside.Pipeline"><span class="pre"><code class="sourceCode python">Pipeline</code></span></a> (1 member)</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |  |
|----|----|----|----|
| <span class="nerd-font"></span> | <a href="#syside.Pipeline.schedule" class="reference internal" title="syside.Pipeline.schedule"><span class="pre"><code class="sourceCode python">schedule</code></span></a> |  | Schedule <span class="pre">`documents`</span> for building with this <span class="pre">`Pipeline`</span>. <span class="pre">`documents`</span> with <span class="pre">`build_state`</span> equal or greater to the state at the end of particular pipeline stage will not be scheduled for that stage. For example, a document with <span class="pre">`build_state`</span>` `<span class="pre">`>=`</span>` `<span class="pre">`BuildState.Parsed`</span> will not be scheduled for parsing. |

</div>

</div>

<span class="nerd-font"></span> **Methods**

<span class="sig-name descname"><span class="pre">schedule</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">documents</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">Sequence</span><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/SharedMutex.md" class="reference internal" title="syside.SharedMutex"><span class="pre">syside.SharedMutex</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/BasicDocument.md" class="reference internal" title="syside.BasicDocument"><span class="pre">syside.BasicDocument</span></a><span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">\]</span></span></span>*, *<span class="n"><span class="pre">options</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/ScheduleOptions.md" class="reference internal" title="syside.ScheduleOptions"><span class="pre">syside.ScheduleOptions</span></a></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">...</span></span>*, *<span class="n"><span class="pre">invalidated</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">Sequence</span><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/SharedMutex.md" class="reference internal" title="syside.SharedMutex"><span class="pre">syside.SharedMutex</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/BasicDocument.md" class="reference internal" title="syside.BasicDocument"><span class="pre">syside.BasicDocument</span></a><span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">\]</span></span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">\[\]</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="/python/v0.8.4/syside/Schedule.md" class="reference internal" title="syside.Schedule"><span class="pre">syside.Schedule</span></a></span></span><a href="#syside.Pipeline.schedule" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Schedule <span class="pre">`documents`</span> for building with this <span class="pre">`Pipeline`</span>. <span class="pre">`documents`</span> with <span class="pre">`build_state`</span> equal or greater to the state at the end of particular pipeline stage will not be scheduled for that stage. For example, a document with <span class="pre">`build_state`</span>` `<span class="pre">`>=`</span>` `<span class="pre">`BuildState.Parsed`</span> will not be scheduled for parsing.

Pipeline also accepts additional <span class="pre">`invalidated`</span> documents that will have their semantic states reset. These documents will then pass through sema and validation stages as normal. This should typically be used for documents that have had their dependencies modified. Any documents for which <span class="pre">`build_state`</span>` `<span class="pre">`<`</span>` `<span class="pre">`BuildState.Built`</span> will not be invalidated as there should be nothing to invalidate.

The returned schedule should be executed on an <span class="pre">`Executor`</span>:

<div class="highlight-python notranslate">

<div class="highlight">

    executor = syside.Executor(...)
    schedule = pipeline.schedule(...)
    ...
    result = executor.run(schedule)

</div>

</div>

Note that pipeline will skip indexing certain URLs that are used by IDEs to display virtual documents:

- <span class="pre">`git*://*`</span>, e.g. used by VS Code to display <span class="pre">`git`</span> diffs

- <span class="pre">`vscode*://*`</span>, e.g. used by VS Code to display editor previews

- <span class="pre">`<scheme>[:|://]`</span> (URL with scheme only), e.g. used by Neovim for new unnamed buffers

The first two patterns additionally skip validation since those virtual documents are never a part of the workspace. Indexing is skipped only for known URL patterns to avoid unexpected behaviour. However, prefer using common schemes such as <span class="pre">`file`</span> or <span class="pre">`http[s]`</span> to ensure that the documents are handled correctly as more URL patterns may be added as more IDEs are tested.

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside"><span class="pre"><code class="sourceCode python">syside</code></span></a>

  - <a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside.make_pipeline"><span class="pre"><code class="sourceCode python">make_pipeline</code></span></a>

</div>

</div>
