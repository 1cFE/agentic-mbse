<div id="unlockedmodel" class="section">

# UnlockedModel<a href="#unlockedmodel" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">UnlockedModel</span></span><a href="#syside.preview.UnlockedModel" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
A SysML v2/KerML model that needs to be <span class="pre">`lock`</span>ed before access.

Note that <span class="pre">`UnlockedModel`</span> is generally not intended to be instantiated directly. Ideally, use <span class="pre">`open_model_unlocked`</span> or <span class="pre">`LockedModel.unlock`</span> on a previously acquired <span class="pre">`LockedModel`</span>.

<div class="highlight-python notranslate">

<div class="highlight">

    model : UnlockedModel = open_model_unlocked("file.sysml")

    ## Alternatively
    locked_model : LockedModel = open_model("file.sysml")
    ...
    model = locked_model.unlock()

</div>

</div>

<div class="align-center" align="center">

<img src="data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iZ3JhcGh2aXoiIHN0eWxlPSJ3aWR0aDogNy4xMjVyZW07aGVpZ2h0OiAyLjc1cmVtOyIgdmlld2JveD0iMC4wMCAwLjAwIDExNC4wMCA0NC4wMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGcgY2xhc3M9ImdyYXBoIiBpZD0iZ3JhcGgwIiB0cmFuc2Zvcm09InNjYWxlKDEgMSkgcm90YXRlKDApIHRyYW5zbGF0ZSg0IDQwKSI+Cjx0aXRsZT4lMzwvdGl0bGU+CjxnIGNsYXNzPSJub2RlIiBpZD0ibm9kZTEiPgo8dGl0bGU+VW5sb2NrZWRNb2RlbDwvdGl0bGU+CjxnIGlkPSJhX25vZGUxIj48YSBocmVmPSIjc3lzaWRlLnByZXZpZXcuVW5sb2NrZWRNb2RlbCI+Cjxwb2x5Z29uIHBvaW50cz0iMTA2LC0zNiAwLC0zNiAwLDAgMTA2LDAgMTA2LC0zNiIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtYmctY29sb3IpO3N0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1mZy1jb2xvcik7Ij48L3BvbHlnb24+Cjx0ZXh0IGZvbnQtZmFtaWx5PSJMZXhlbmQiIGZvbnQtc2l6ZT0iMTIuMDAiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1jb2RlLWZnLWNvbG9yKTstLW1kLWdyYXBodml6LWhvdmVyLWNvbG9yOiB2YXIoLS1tZC1ncmFwaHZpei1hLWhvdmVyLWNvbG9yKTsiIHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjUzIiB5PSItMTQuMiI+VW5sb2NrZWRNb2RlbDwvdGV4dD4KPHRpdGxlPnN5c2lkZS5wcmV2aWV3LlVubG9ja2VkTW9kZWw8L3RpdGxlPjwvYT4KPC9nPgo8L2c+CjwvZz4KPC9zdmc+" class="graphviz" />

</div>

<span class="sd-summary-text">Members defined in <a href="#syside.preview.UnlockedModel" class="reference internal" title="syside.preview.UnlockedModel"><span class="pre"><code class="sourceCode python">UnlockedModel</code></span></a> (1 member)</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |  |
|----|----|----|----|
| <span class="nerd-font"></span> | <a href="#syside.preview.UnlockedModel.lock" class="reference internal" title="syside.preview.UnlockedModel.lock"><span class="pre"><code class="sourceCode python">lock</code></span></a> |  | Locks the model, allowing access. |

</div>

</div>

<span class="nerd-font"></span> **Methods**

<span class="sig-name descname"><span class="pre">lock</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="/python/v0.8.4/syside/preview/LockedModel.md" class="reference internal" title="syside.preview.LockedModel"><span class="pre">syside.preview.LockedModel</span></a></span></span><a href="#syside.preview.UnlockedModel.lock" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Locks the model, allowing access.

Returns<span class="colon">:</span>  
a <span class="pre">`LockedModel`</span> that allows access to model elements.

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/preview//README.md" class="reference internal" title="syside.preview"><span class="pre"><code class="sourceCode python">syside.preview</code></span></a>

  - <a href="/python/v0.8.4/syside/preview//README.md" class="reference internal" title="syside.preview.open_model_unlocked"><span class="pre"><code class="sourceCode python">open_model_unlocked</code></span></a>

- <a href="/python/v0.8.4/syside/preview/LockedModel.md" class="reference internal" title="syside.preview.LockedModel"><span class="pre"><code class="sourceCode python">syside.preview.LockedModel</code></span></a>

  - <a href="/python/v0.8.4/syside/preview/LockedModel.md" class="reference internal" title="syside.preview.LockedModel.unlock"><span class="pre"><code class="sourceCode python">unlock</code></span></a>

</div>

</div>
