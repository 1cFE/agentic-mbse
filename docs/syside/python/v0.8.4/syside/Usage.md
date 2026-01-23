<div id="usage-sysml" class="section">

# Usage <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span><a href="#usage-sysml" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">Usage</span></span><a href="#syside.Usage" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`Usage`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> A <span class="pre">`Usage`</span> is a usage of a <span class="pre">`Definition`</span>.
>
> A <span class="pre">`Usage`</span> may have <span class="pre">`nested_usages`</span> that model <span class="pre">`features`</span> that apply in the context of the <span class="pre">`owning_usage`</span>. A <span class="pre">`Usage`</span> may also have <span class="pre">`Definitions`</span> nested in it, but this has no semantic significance, other than the nested scoping resulting from the <span class="pre">`Usage`</span> being considered as a <span class="pre">`Namespace`</span> for any nested <span class="pre">`Definitions`</span>.
>
> However, if a <span class="pre">`Usage`</span> has <span class="pre">`is_variation`</span>` `<span class="pre">`=`</span>` `<span class="pre">`true`</span>, then it represents a *variation point* <span class="pre">`Usage`</span>. In this case, all of its <span class="pre">`members`</span> must be <span class="pre">`variant`</span> <span class="pre">`Usages`</span>, related to the <span class="pre">`Usage`</span> by <span class="pre">`VariantMembership`</span> <span class="pre">`Relationships`</span>. Rather than being <span class="pre">`features`</span> of the <span class="pre">`Usage`</span>, <span class="pre">`variant`</span> <span class="pre">`Usages`</span> model different concrete alternatives that can be chosen to fill in for the variation point <span class="pre">`Usage`</span>.
>
> </div>

For language description, see section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=61" class="reference external" target="_blank">7.6</a> of the SysML specification. For more details on the model, see section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=303" class="reference external" target="_blank">8.3.6.4</a> of the SysML specification.

<div class="align-center" align="center">

<img src="data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iZ3JhcGh2aXoiIHN0eWxlPSJ3aWR0aDogNS43NXJlbTtoZWlnaHQ6IDI1LjI1cmVtOyIgdmlld2JveD0iMC4wMCAwLjAwIDkyLjAwIDQwNC4wMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGcgY2xhc3M9ImdyYXBoIiBpZD0iZ3JhcGgwIiB0cmFuc2Zvcm09InNjYWxlKDEgMSkgcm90YXRlKDApIHRyYW5zbGF0ZSg0IDQwMCkiPgo8dGl0bGU+JTM8L3RpdGxlPgo8ZyBjbGFzcz0ibm9kZSIgaWQ9Im5vZGUxIj4KPHRpdGxlPlVzYWdlPC90aXRsZT4KPGcgaWQ9ImFfbm9kZTEiPjxhIGhyZWY9IiNzeXNpZGUuVXNhZ2UiPgo8cG9seWdvbiBwb2ludHM9IjY5LC0zNiAxNSwtMzYgMTUsMCA2OSwwIDY5LC0zNiIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtYmctY29sb3IpO3N0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1mZy1jb2xvcik7Ij48L3BvbHlnb24+Cjx0ZXh0IGZvbnQtZmFtaWx5PSJMZXhlbmQiIGZvbnQtc2l6ZT0iMTIuMDAiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1jb2RlLWZnLWNvbG9yKTstLW1kLWdyYXBodml6LWhvdmVyLWNvbG9yOiB2YXIoLS1tZC1ncmFwaHZpei1hLWhvdmVyLWNvbG9yKTsiIHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjQyIiB5PSItMTQuMiI+VXNhZ2U8L3RleHQ+Cjx0aXRsZT5zeXNpZGUuVXNhZ2U8L3RpdGxlPjwvYT4KPC9nPgo8L2c+CjxnIGNsYXNzPSJub2RlIiBpZD0ibm9kZTIiPgo8dGl0bGU+RmVhdHVyZTwvdGl0bGU+CjxnIGlkPSJhX25vZGUyIj48YSBocmVmPSIvcHl0aG9uL3YwLjguNC9zeXNpZGUvRmVhdHVyZS5tZCI+Cjxwb2x5Z29uIHBvaW50cz0iNzIsLTEwOCAxMiwtMTA4IDEyLC03MiA3MiwtNzIgNzIsLTEwOCIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtYmctY29sb3IpO3N0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1mZy1jb2xvcik7Ij48L3BvbHlnb24+Cjx0ZXh0IGZvbnQtZmFtaWx5PSJMZXhlbmQiIGZvbnQtc2l6ZT0iMTIuMDAiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1jb2RlLWZnLWNvbG9yKTstLW1kLWdyYXBodml6LWhvdmVyLWNvbG9yOiB2YXIoLS1tZC1ncmFwaHZpei1hLWhvdmVyLWNvbG9yKTsiIHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjQyIiB5PSItODYuMiI+RmVhdHVyZTwvdGV4dD4KPHRpdGxlPnN5c2lkZS5GZWF0dXJlPC90aXRsZT48L2E+CjwvZz4KPC9nPgo8ZyBjbGFzcz0iZWRnZSIgaWQ9ImVkZ2UxIj4KPHRpdGxlPkZlYXR1cmUtJmd0O1VzYWdlPC90aXRsZT4KPHBhdGggZD0iTTQyLC03MS43QzQyLC02My45OCA0MiwtNTQuNzEgNDIsLTQ2LjExIiBmaWxsPSJub25lIiBzdHlsZT0ic3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1lZGdlLWNvbG9yKTsiIC8+Cjxwb2x5Z29uIHBvaW50cz0iNDUuNSwtNDYuMSA0MiwtMzYuMSAzOC41LC00Ni4xIDQ1LjUsLTQ2LjEiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1ncmFwaHZpei1lZGdlLWNvbG9yKTtzdHJva2U6IHZhcigtLW1kLWdyYXBodml6LWVkZ2UtY29sb3IpOyI+PC9wb2x5Z29uPgo8L2c+CjxnIGNsYXNzPSJub2RlIiBpZD0ibm9kZTMiPgo8dGl0bGU+VHlwZTwvdGl0bGU+CjxnIGlkPSJhX25vZGUzIj48YSBocmVmPSIvcHl0aG9uL3YwLjguNC9zeXNpZGUvVHlwZS5tZCI+Cjxwb2x5Z29uIHBvaW50cz0iNjksLTE4MCAxNSwtMTgwIDE1LC0xNDQgNjksLTE0NCA2OSwtMTgwIiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1iZy1jb2xvcik7c3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1ub2RlLWZnLWNvbG9yKTsiPjwvcG9seWdvbj4KPHRleHQgZm9udC1mYW1pbHk9IkxleGVuZCIgZm9udC1zaXplPSIxMi4wMCIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWNvZGUtZmctY29sb3IpOy0tbWQtZ3JhcGh2aXotaG92ZXItY29sb3I6IHZhcigtLW1kLWdyYXBodml6LWEtaG92ZXItY29sb3IpOyIgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iNDIiIHk9Ii0xNTguMiI+VHlwZTwvdGV4dD4KPHRpdGxlPnN5c2lkZS5UeXBlPC90aXRsZT48L2E+CjwvZz4KPC9nPgo8ZyBjbGFzcz0iZWRnZSIgaWQ9ImVkZ2UyIj4KPHRpdGxlPlR5cGUtJmd0O0ZlYXR1cmU8L3RpdGxlPgo8cGF0aCBkPSJNNDIsLTE0My43QzQyLC0xMzUuOTggNDIsLTEyNi43MSA0MiwtMTE4LjExIiBmaWxsPSJub25lIiBzdHlsZT0ic3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1lZGdlLWNvbG9yKTsiIC8+Cjxwb2x5Z29uIHBvaW50cz0iNDUuNSwtMTE4LjEgNDIsLTEwOC4xIDM4LjUsLTExOC4xIDQ1LjUsLTExOC4xIiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtZ3JhcGh2aXotZWRnZS1jb2xvcik7c3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1lZGdlLWNvbG9yKTsiPjwvcG9seWdvbj4KPC9nPgo8ZyBjbGFzcz0ibm9kZSIgaWQ9Im5vZGU0Ij4KPHRpdGxlPk5hbWVzcGFjZTwvdGl0bGU+CjxnIGlkPSJhX25vZGU0Ij48YSBocmVmPSIvcHl0aG9uL3YwLjguNC9zeXNpZGUvTmFtZXNwYWNlLm1kIj4KPHBvbHlnb24gcG9pbnRzPSI4NCwtMjUyIDAsLTI1MiAwLC0yMTYgODQsLTIxNiA4NCwtMjUyIiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1iZy1jb2xvcik7c3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1ub2RlLWZnLWNvbG9yKTsiPjwvcG9seWdvbj4KPHRleHQgZm9udC1mYW1pbHk9IkxleGVuZCIgZm9udC1zaXplPSIxMi4wMCIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWNvZGUtZmctY29sb3IpOy0tbWQtZ3JhcGh2aXotaG92ZXItY29sb3I6IHZhcigtLW1kLWdyYXBodml6LWEtaG92ZXItY29sb3IpOyIgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iNDIiIHk9Ii0yMzAuMiI+TmFtZXNwYWNlPC90ZXh0Pgo8dGl0bGU+c3lzaWRlLk5hbWVzcGFjZTwvdGl0bGU+PC9hPgo8L2c+CjwvZz4KPGcgY2xhc3M9ImVkZ2UiIGlkPSJlZGdlMyI+Cjx0aXRsZT5OYW1lc3BhY2UtJmd0O1R5cGU8L3RpdGxlPgo8cGF0aCBkPSJNNDIsLTIxNS43QzQyLC0yMDcuOTggNDIsLTE5OC43MSA0MiwtMTkwLjExIiBmaWxsPSJub25lIiBzdHlsZT0ic3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1lZGdlLWNvbG9yKTsiIC8+Cjxwb2x5Z29uIHBvaW50cz0iNDUuNSwtMTkwLjEgNDIsLTE4MC4xIDM4LjUsLTE5MC4xIDQ1LjUsLTE5MC4xIiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtZ3JhcGh2aXotZWRnZS1jb2xvcik7c3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1lZGdlLWNvbG9yKTsiPjwvcG9seWdvbj4KPC9nPgo8ZyBjbGFzcz0ibm9kZSIgaWQ9Im5vZGU1Ij4KPHRpdGxlPkVsZW1lbnQ8L3RpdGxlPgo8ZyBpZD0iYV9ub2RlNSI+PGEgaHJlZj0iL3B5dGhvbi92MC44LjQvc3lzaWRlL0VsZW1lbnQubWQiPgo8cG9seWdvbiBwb2ludHM9IjczLC0zMjQgMTEsLTMyNCAxMSwtMjg4IDczLC0yODggNzMsLTMyNCIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtYmctY29sb3IpO3N0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1mZy1jb2xvcik7Ij48L3BvbHlnb24+Cjx0ZXh0IGZvbnQtZmFtaWx5PSJMZXhlbmQiIGZvbnQtc2l6ZT0iMTIuMDAiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1jb2RlLWZnLWNvbG9yKTstLW1kLWdyYXBodml6LWhvdmVyLWNvbG9yOiB2YXIoLS1tZC1ncmFwaHZpei1hLWhvdmVyLWNvbG9yKTsiIHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjQyIiB5PSItMzAyLjIiPkVsZW1lbnQ8L3RleHQ+Cjx0aXRsZT5zeXNpZGUuRWxlbWVudDwvdGl0bGU+PC9hPgo8L2c+CjwvZz4KPGcgY2xhc3M9ImVkZ2UiIGlkPSJlZGdlNCI+Cjx0aXRsZT5FbGVtZW50LSZndDtOYW1lc3BhY2U8L3RpdGxlPgo8cGF0aCBkPSJNNDIsLTI4Ny43QzQyLC0yNzkuOTggNDIsLTI3MC43MSA0MiwtMjYyLjExIiBmaWxsPSJub25lIiBzdHlsZT0ic3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1lZGdlLWNvbG9yKTsiIC8+Cjxwb2x5Z29uIHBvaW50cz0iNDUuNSwtMjYyLjEgNDIsLTI1Mi4xIDM4LjUsLTI2Mi4xIDQ1LjUsLTI2Mi4xIiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtZ3JhcGh2aXotZWRnZS1jb2xvcik7c3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1lZGdlLWNvbG9yKTsiPjwvcG9seWdvbj4KPC9nPgo8ZyBjbGFzcz0ibm9kZSIgaWQ9Im5vZGU2Ij4KPHRpdGxlPkFzdE5vZGU8L3RpdGxlPgo8ZyBpZD0iYV9ub2RlNiI+PGEgaHJlZj0iL3B5dGhvbi92MC44LjQvc3lzaWRlL0FzdE5vZGUubWQiPgo8cG9seWdvbiBwb2ludHM9Ijc1LC0zOTYgOSwtMzk2IDksLTM2MCA3NSwtMzYwIDc1LC0zOTYiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1ncmFwaHZpei1ub2RlLWJnLWNvbG9yKTtzdHJva2U6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtZmctY29sb3IpOyI+PC9wb2x5Z29uPgo8dGV4dCBmb250LWZhbWlseT0iTGV4ZW5kIiBmb250LXNpemU9IjEyLjAwIiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtY29kZS1mZy1jb2xvcik7LS1tZC1ncmFwaHZpei1ob3Zlci1jb2xvcjogdmFyKC0tbWQtZ3JhcGh2aXotYS1ob3Zlci1jb2xvcik7IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSI0MiIgeT0iLTM3NC4yIj5Bc3ROb2RlPC90ZXh0Pgo8dGl0bGU+c3lzaWRlLkFzdE5vZGU8L3RpdGxlPjwvYT4KPC9nPgo8L2c+CjxnIGNsYXNzPSJlZGdlIiBpZD0iZWRnZTUiPgo8dGl0bGU+QXN0Tm9kZS0mZ3Q7RWxlbWVudDwvdGl0bGU+CjxwYXRoIGQ9Ik00MiwtMzU5LjdDNDIsLTM1MS45OCA0MiwtMzQyLjcxIDQyLC0zMzQuMTEiIGZpbGw9Im5vbmUiIHN0eWxlPSJzdHJva2U6IHZhcigtLW1kLWdyYXBodml6LWVkZ2UtY29sb3IpOyIgLz4KPHBvbHlnb24gcG9pbnRzPSI0NS41LC0zMzQuMSA0MiwtMzI0LjEgMzguNSwtMzM0LjEgNDUuNSwtMzM0LjEiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1ncmFwaHZpei1lZGdlLWNvbG9yKTtzdHJva2U6IHZhcigtLW1kLWdyYXBodml6LWVkZ2UtY29sb3IpOyI+PC9wb2x5Z29uPgo8L2c+CjwvZz4KPC9zdmc+" class="graphviz" />

</div>

<span class="sd-summary-text"><span class="nerd-font"></span> Children</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/AttributeUsage.md" class="reference internal" title="syside.AttributeUsage"><span class="pre"><code class="sourceCode python">AttributeUsage</code></span></a>

  - <a href="/python/v0.8.4/syside/EnumerationUsage.md" class="reference internal" title="syside.EnumerationUsage"><span class="pre"><code class="sourceCode python">EnumerationUsage</code></span></a>

- <a href="/python/v0.8.4/syside/ConnectorAsUsage.md" class="reference internal" title="syside.ConnectorAsUsage"><span class="pre"><code class="sourceCode python">ConnectorAsUsage</code></span></a>

  - <a href="/python/v0.8.4/syside/BindingConnectorAsUsage.md" class="reference internal" title="syside.BindingConnectorAsUsage"><span class="pre"><code class="sourceCode python">BindingConnectorAsUsage</code></span></a>

  - <a href="/python/v0.8.4/syside/ConnectionUsage.md" class="reference internal" title="syside.ConnectionUsage"><span class="pre"><code class="sourceCode python">ConnectionUsage</code></span></a>

    - <a href="/python/v0.8.4/syside/AllocationUsage.md" class="reference internal" title="syside.AllocationUsage"><span class="pre"><code class="sourceCode python">AllocationUsage</code></span></a>

    - <a href="/python/v0.8.4/syside/InterfaceUsage.md" class="reference internal" title="syside.InterfaceUsage"><span class="pre"><code class="sourceCode python">InterfaceUsage</code></span></a>

  - <a href="/python/v0.8.4/syside/FlowUsage.md" class="reference internal" title="syside.FlowUsage"><span class="pre"><code class="sourceCode python">FlowUsage</code></span></a>

    - <a href="/python/v0.8.4/syside/SuccessionFlowUsage.md" class="reference internal" title="syside.SuccessionFlowUsage"><span class="pre"><code class="sourceCode python">SuccessionFlowUsage</code></span></a>

  - <a href="/python/v0.8.4/syside/SuccessionAsUsage.md" class="reference internal" title="syside.SuccessionAsUsage"><span class="pre"><code class="sourceCode python">SuccessionAsUsage</code></span></a>

- <a href="/python/v0.8.4/syside/OccurrenceUsage.md" class="reference internal" title="syside.OccurrenceUsage"><span class="pre"><code class="sourceCode python">OccurrenceUsage</code></span></a>

  - <a href="/python/v0.8.4/syside/ActionUsage.md" class="reference internal" title="syside.ActionUsage"><span class="pre"><code class="sourceCode python">ActionUsage</code></span></a>

    - <a href="/python/v0.8.4/syside/AcceptActionUsage.md" class="reference internal" title="syside.AcceptActionUsage"><span class="pre"><code class="sourceCode python">AcceptActionUsage</code></span></a>

    - <a href="/python/v0.8.4/syside/AssignmentActionUsage.md" class="reference internal" title="syside.AssignmentActionUsage"><span class="pre"><code class="sourceCode python">AssignmentActionUsage</code></span></a>

    - <a href="/python/v0.8.4/syside/CalculationUsage.md" class="reference internal" title="syside.CalculationUsage"><span class="pre"><code class="sourceCode python">CalculationUsage</code></span></a>

      - <a href="/python/v0.8.4/syside/CaseUsage.md" class="reference internal" title="syside.CaseUsage"><span class="pre"><code class="sourceCode python">CaseUsage</code></span></a>

        - <a href="/python/v0.8.4/syside/AnalysisCaseUsage.md" class="reference internal" title="syside.AnalysisCaseUsage"><span class="pre"><code class="sourceCode python">AnalysisCaseUsage</code></span></a>

        - <a href="/python/v0.8.4/syside/UseCaseUsage.md" class="reference internal" title="syside.UseCaseUsage"><span class="pre"><code class="sourceCode python">UseCaseUsage</code></span></a>

          - <a href="/python/v0.8.4/syside/IncludeUseCaseUsage.md" class="reference internal" title="syside.IncludeUseCaseUsage"><span class="pre"><code class="sourceCode python">IncludeUseCaseUsage</code></span></a>

        - <a href="/python/v0.8.4/syside/VerificationCaseUsage.md" class="reference internal" title="syside.VerificationCaseUsage"><span class="pre"><code class="sourceCode python">VerificationCaseUsage</code></span></a>

    - <a href="/python/v0.8.4/syside/ControlNode.md" class="reference internal" title="syside.ControlNode"><span class="pre"><code class="sourceCode python">ControlNode</code></span></a>

      - <a href="/python/v0.8.4/syside/DecisionNode.md" class="reference internal" title="syside.DecisionNode"><span class="pre"><code class="sourceCode python">DecisionNode</code></span></a>

      - <a href="/python/v0.8.4/syside/ForkNode.md" class="reference internal" title="syside.ForkNode"><span class="pre"><code class="sourceCode python">ForkNode</code></span></a>

      - <a href="/python/v0.8.4/syside/JoinNode.md" class="reference internal" title="syside.JoinNode"><span class="pre"><code class="sourceCode python">JoinNode</code></span></a>

      - <a href="/python/v0.8.4/syside/MergeNode.md" class="reference internal" title="syside.MergeNode"><span class="pre"><code class="sourceCode python">MergeNode</code></span></a>

    - <a href="/python/v0.8.4/syside/IfActionUsage.md" class="reference internal" title="syside.IfActionUsage"><span class="pre"><code class="sourceCode python">IfActionUsage</code></span></a>

    - <a href="/python/v0.8.4/syside/LoopActionUsage.md" class="reference internal" title="syside.LoopActionUsage"><span class="pre"><code class="sourceCode python">LoopActionUsage</code></span></a>

      - <a href="/python/v0.8.4/syside/ForLoopActionUsage.md" class="reference internal" title="syside.ForLoopActionUsage"><span class="pre"><code class="sourceCode python">ForLoopActionUsage</code></span></a>

      - <a href="/python/v0.8.4/syside/WhileLoopActionUsage.md" class="reference internal" title="syside.WhileLoopActionUsage"><span class="pre"><code class="sourceCode python">WhileLoopActionUsage</code></span></a>

    - <a href="/python/v0.8.4/syside/PerformActionUsage.md" class="reference internal" title="syside.PerformActionUsage"><span class="pre"><code class="sourceCode python">PerformActionUsage</code></span></a>

    - <a href="/python/v0.8.4/syside/SendActionUsage.md" class="reference internal" title="syside.SendActionUsage"><span class="pre"><code class="sourceCode python">SendActionUsage</code></span></a>

    - <a href="/python/v0.8.4/syside/StateUsage.md" class="reference internal" title="syside.StateUsage"><span class="pre"><code class="sourceCode python">StateUsage</code></span></a>

      - <a href="/python/v0.8.4/syside/ExhibitStateUsage.md" class="reference internal" title="syside.ExhibitStateUsage"><span class="pre"><code class="sourceCode python">ExhibitStateUsage</code></span></a>

    - <a href="/python/v0.8.4/syside/TerminateActionUsage.md" class="reference internal" title="syside.TerminateActionUsage"><span class="pre"><code class="sourceCode python">TerminateActionUsage</code></span></a>

    - <a href="/python/v0.8.4/syside/TransitionUsage.md" class="reference internal" title="syside.TransitionUsage"><span class="pre"><code class="sourceCode python">TransitionUsage</code></span></a>

  - <a href="/python/v0.8.4/syside/ConstraintUsage.md" class="reference internal" title="syside.ConstraintUsage"><span class="pre"><code class="sourceCode python">ConstraintUsage</code></span></a>

    - <a href="/python/v0.8.4/syside/AssertConstraintUsage.md" class="reference internal" title="syside.AssertConstraintUsage"><span class="pre"><code class="sourceCode python">AssertConstraintUsage</code></span></a>

    - <a href="/python/v0.8.4/syside/RequirementUsage.md" class="reference internal" title="syside.RequirementUsage"><span class="pre"><code class="sourceCode python">RequirementUsage</code></span></a>

      - <a href="/python/v0.8.4/syside/ConcernUsage.md" class="reference internal" title="syside.ConcernUsage"><span class="pre"><code class="sourceCode python">ConcernUsage</code></span></a>

      - <a href="/python/v0.8.4/syside/SatisfyRequirementUsage.md" class="reference internal" title="syside.SatisfyRequirementUsage"><span class="pre"><code class="sourceCode python">SatisfyRequirementUsage</code></span></a>

      - <a href="/python/v0.8.4/syside/ViewpointUsage.md" class="reference internal" title="syside.ViewpointUsage"><span class="pre"><code class="sourceCode python">ViewpointUsage</code></span></a>

  - <a href="/python/v0.8.4/syside/EventOccurrenceUsage.md" class="reference internal" title="syside.EventOccurrenceUsage"><span class="pre"><code class="sourceCode python">EventOccurrenceUsage</code></span></a>

  - <a href="/python/v0.8.4/syside/ItemUsage.md" class="reference internal" title="syside.ItemUsage"><span class="pre"><code class="sourceCode python">ItemUsage</code></span></a>

    - <a href="/python/v0.8.4/syside/MetadataUsage.md" class="reference internal" title="syside.MetadataUsage"><span class="pre"><code class="sourceCode python">MetadataUsage</code></span></a>

    - <a href="/python/v0.8.4/syside/PartUsage.md" class="reference internal" title="syside.PartUsage"><span class="pre"><code class="sourceCode python">PartUsage</code></span></a>

      - <a href="/python/v0.8.4/syside/RenderingUsage.md" class="reference internal" title="syside.RenderingUsage"><span class="pre"><code class="sourceCode python">RenderingUsage</code></span></a>

      - <a href="/python/v0.8.4/syside/ViewUsage.md" class="reference internal" title="syside.ViewUsage"><span class="pre"><code class="sourceCode python">ViewUsage</code></span></a>

  - <a href="/python/v0.8.4/syside/PortUsage.md" class="reference internal" title="syside.PortUsage"><span class="pre"><code class="sourceCode python">PortUsage</code></span></a>

- <a href="/python/v0.8.4/syside/ReferenceUsage.md" class="reference internal" title="syside.ReferenceUsage"><span class="pre"><code class="sourceCode python">ReferenceUsage</code></span></a>

</div>

<span class="sd-summary-text">Members defined in <a href="#syside.Usage" class="reference internal" title="syside.Usage"><span class="pre"><code class="sourceCode python">Usage</code></span></a> (39 members)</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |  |
|----|----|----|----|
| <span class="nerd-font"></span> | <a href="#syside.Usage.STD" class="reference internal" title="syside.Usage.STD"><span class="pre"><code class="sourceCode python">STD</code></span></a> | <span class="pre">`R`</span> |  |
| <span class="nerd-font"></span> | <a href="#syside.Usage.definitions" class="reference internal" title="syside.Usage.definitions"><span class="pre"><code class="sourceCode python">definitions</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`definition`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Usage.directed_usages" class="reference internal" title="syside.Usage.directed_usages"><span class="pre"><code class="sourceCode python">directed_usages</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`directed_usage`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Usage.is_reference" class="reference internal" title="syside.Usage.is_reference"><span class="pre"><code class="sourceCode python">is_reference</code></span></a> | <span class="pre">`RW`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`is_reference`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Usage.is_reference_explicitly" class="reference internal" title="syside.Usage.is_reference_explicitly"><span class="pre"><code class="sourceCode python">is_reference_explicitly</code></span></a> | <span class="pre">`R`</span> | Returns <span class="pre">`True`</span> if this <span class="pre">`Usage`</span> was explicitly declared as <span class="pre">`ref`</span> in the textual syntax. |
| <span class="nerd-font"></span> | <a href="#syside.Usage.is_variation" class="reference internal" title="syside.Usage.is_variation"><span class="pre"><code class="sourceCode python">is_variation</code></span></a> | <span class="pre">`RW`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`is_variation`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Usage.may_time_vary" class="reference internal" title="syside.Usage.may_time_vary"><span class="pre"><code class="sourceCode python">may_time_vary</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`may_time_vary`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Usage.nested_actions" class="reference internal" title="syside.Usage.nested_actions"><span class="pre"><code class="sourceCode python">nested_actions</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`nested_action`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Usage.nested_allocations" class="reference internal" title="syside.Usage.nested_allocations"><span class="pre"><code class="sourceCode python">nested_allocations</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`nested_allocation`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Usage.nested_analysis_cases" class="reference internal" title="syside.Usage.nested_analysis_cases"><span class="pre"><code class="sourceCode python">nested_analysis_cases</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`nested_analysis_case`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Usage.nested_attributes" class="reference internal" title="syside.Usage.nested_attributes"><span class="pre"><code class="sourceCode python">nested_attributes</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`nested_attribute`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Usage.nested_calculations" class="reference internal" title="syside.Usage.nested_calculations"><span class="pre"><code class="sourceCode python">nested_calculations</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`nested_calculation`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Usage.nested_cases" class="reference internal" title="syside.Usage.nested_cases"><span class="pre"><code class="sourceCode python">nested_cases</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`nested_case`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Usage.nested_concerns" class="reference internal" title="syside.Usage.nested_concerns"><span class="pre"><code class="sourceCode python">nested_concerns</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`nested_concern`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Usage.nested_connections" class="reference internal" title="syside.Usage.nested_connections"><span class="pre"><code class="sourceCode python">nested_connections</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`nested_connection`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Usage.nested_constraints" class="reference internal" title="syside.Usage.nested_constraints"><span class="pre"><code class="sourceCode python">nested_constraints</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`nested_constraint`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Usage.nested_enumerations" class="reference internal" title="syside.Usage.nested_enumerations"><span class="pre"><code class="sourceCode python">nested_enumerations</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`nested_enumeration`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Usage.nested_flows" class="reference internal" title="syside.Usage.nested_flows"><span class="pre"><code class="sourceCode python">nested_flows</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`nested_flow`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Usage.nested_interfaces" class="reference internal" title="syside.Usage.nested_interfaces"><span class="pre"><code class="sourceCode python">nested_interfaces</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`nested_interface`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Usage.nested_items" class="reference internal" title="syside.Usage.nested_items"><span class="pre"><code class="sourceCode python">nested_items</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`nested_item`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Usage.nested_metadata" class="reference internal" title="syside.Usage.nested_metadata"><span class="pre"><code class="sourceCode python">nested_metadata</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`nested_metadata`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Usage.nested_occurrences" class="reference internal" title="syside.Usage.nested_occurrences"><span class="pre"><code class="sourceCode python">nested_occurrences</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`nested_occurrence`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Usage.nested_parts" class="reference internal" title="syside.Usage.nested_parts"><span class="pre"><code class="sourceCode python">nested_parts</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`nested_part`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Usage.nested_ports" class="reference internal" title="syside.Usage.nested_ports"><span class="pre"><code class="sourceCode python">nested_ports</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`nested_port`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Usage.nested_references" class="reference internal" title="syside.Usage.nested_references"><span class="pre"><code class="sourceCode python">nested_references</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`nested_reference`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Usage.nested_renderings" class="reference internal" title="syside.Usage.nested_renderings"><span class="pre"><code class="sourceCode python">nested_renderings</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`nested_rendering`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Usage.nested_requirements" class="reference internal" title="syside.Usage.nested_requirements"><span class="pre"><code class="sourceCode python">nested_requirements</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`nested_requirement`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Usage.nested_states" class="reference internal" title="syside.Usage.nested_states"><span class="pre"><code class="sourceCode python">nested_states</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`nested_state`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Usage.nested_transitions" class="reference internal" title="syside.Usage.nested_transitions"><span class="pre"><code class="sourceCode python">nested_transitions</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`nested_transition`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Usage.nested_usages" class="reference internal" title="syside.Usage.nested_usages"><span class="pre"><code class="sourceCode python">nested_usages</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`nested_usage`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Usage.nested_use_cases" class="reference internal" title="syside.Usage.nested_use_cases"><span class="pre"><code class="sourceCode python">nested_use_cases</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`nested_use_case`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Usage.nested_verification_cases" class="reference internal" title="syside.Usage.nested_verification_cases"><span class="pre"><code class="sourceCode python">nested_verification_cases</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`nested_verification_case`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Usage.nested_viewpoints" class="reference internal" title="syside.Usage.nested_viewpoints"><span class="pre"><code class="sourceCode python">nested_viewpoints</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`nested_viewpoint`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Usage.nested_views" class="reference internal" title="syside.Usage.nested_views"><span class="pre"><code class="sourceCode python">nested_views</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`nested_view`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Usage.owning_definition" class="reference internal" title="syside.Usage.owning_definition"><span class="pre"><code class="sourceCode python">owning_definition</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owning_definition`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Usage.owning_usage" class="reference internal" title="syside.Usage.owning_usage"><span class="pre"><code class="sourceCode python">owning_usage</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owning_usage`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Usage.usages" class="reference internal" title="syside.Usage.usages"><span class="pre"><code class="sourceCode python">usages</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`usage`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Usage.variant_memberships" class="reference internal" title="syside.Usage.variant_memberships"><span class="pre"><code class="sourceCode python">variant_memberships</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`variant_membership`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Usage.variants" class="reference internal" title="syside.Usage.variants"><span class="pre"><code class="sourceCode python">variants</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`variant`</span> defined in the SysML specification. |

</div>

</div>

<span class="sd-summary-text">Members inherited from <a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature"><span class="pre"><code class="sourceCode python">Feature</code></span></a> (44 members)</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |  |
|----|----|----|----|
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature.basic_feature"><span class="pre"><code class="sourceCode python">basic_feature</code></span></a> | <span class="pre">`R`</span> | The <span class="pre">`last_chaining_feature`</span> if one exists, otherwise this <span class="pre">`Feature`</span>. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature.chaining_features"><span class="pre"><code class="sourceCode python">chaining_features</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`chaining_feature`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature.cross_feature"><span class="pre"><code class="sourceCode python">cross_feature</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`cross_feature`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature.direction"><span class="pre"><code class="sourceCode python">direction</code></span></a> | <span class="pre">`RW`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`direction`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature.end_owning_type"><span class="pre"><code class="sourceCode python">end_owning_type</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`end_owning_type`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature.explicit_direction"><span class="pre"><code class="sourceCode python">explicit_direction</code></span></a> | <span class="pre">`R`</span> | Returns the direction this <span class="pre">`Feature`</span> has been declared with in the textual syntax. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature.feature_target"><span class="pre"><code class="sourceCode python">feature_target</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`feature_target`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature.feature_value"><span class="pre"><code class="sourceCode python">feature_value</code></span></a> | <span class="pre">`R`</span> | The <span class="pre">`FeatureValue`</span> owned by this <span class="pre">`Feature`</span> if any. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature.feature_value_expression"><span class="pre"><code class="sourceCode python">feature_value_expression</code></span></a> | <span class="pre">`R`</span> | The feature value <span class="pre">`Expression`</span> of this <span class="pre">`Feature`</span> if any. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature.feature_value_member"><span class="pre"><code class="sourceCode python">feature_value_member</code></span></a> | <span class="pre">`R`</span> | Syside specific accessor for manipulating <span class="pre">`feature_value`</span>. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature.featuring_types"><span class="pre"><code class="sourceCode python">featuring_types</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`featuring_type`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature.first_chaining_feature"><span class="pre"><code class="sourceCode python">first_chaining_feature</code></span></a> | <span class="pre">`R`</span> | The related <span class="pre">`Feature`</span> related by the first <span class="pre">`owned_feature_chaining`</span> if any. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature.is_composite"><span class="pre"><code class="sourceCode python">is_composite</code></span></a> | <span class="pre">`RW`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`is_composite`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature.is_composite_explicitly"><span class="pre"><code class="sourceCode python">is_composite_explicitly</code></span></a> | <span class="pre">`R`</span> | Returns <span class="pre">`True`</span> if this <span class="pre">`Feature`</span> has been declared <span class="pre">`composite`</span> in the textual syntax. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature.is_constant"><span class="pre"><code class="sourceCode python">is_constant</code></span></a> | <span class="pre">`RW`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`is_constant`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature.is_constant_explicitly"><span class="pre"><code class="sourceCode python">is_constant_explicitly</code></span></a> | <span class="pre">`R`</span> | Returns <span class="pre">`True`</span> if this <span class="pre">`Feature`</span> has been declared <span class="pre">`constant`</span> in the textual syntax. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature.is_derived"><span class="pre"><code class="sourceCode python">is_derived</code></span></a> | <span class="pre">`RW`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`is_derived`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature.is_end"><span class="pre"><code class="sourceCode python">is_end</code></span></a> | <span class="pre">`RW`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`is_end`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature.is_end_explicitly"><span class="pre"><code class="sourceCode python">is_end_explicitly</code></span></a> | <span class="pre">`R`</span> | Returns <span class="pre">`True`</span> if this <span class="pre">`Feature`</span> has been declared <span class="pre">`end`</span> in the textual syntax. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature.is_nonunique"><span class="pre"><code class="sourceCode python">is_nonunique</code></span></a> | <span class="pre">`RW`</span> |  |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature.is_ordered"><span class="pre"><code class="sourceCode python">is_ordered</code></span></a> | <span class="pre">`RW`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`is_ordered`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature.is_portion"><span class="pre"><code class="sourceCode python">is_portion</code></span></a> | <span class="pre">`RW`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`is_portion`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature.is_read_only"><span class="pre"><code class="sourceCode python">is_read_only</code></span></a> | <span class="pre">`RW`</span> | Alias for is_constant. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature.is_unique"><span class="pre"><code class="sourceCode python">is_unique</code></span></a> | <span class="pre">`RW`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`is_unique`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature.is_variable"><span class="pre"><code class="sourceCode python">is_variable</code></span></a> | <span class="pre">`RW`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`is_variable`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature.is_variable_explicitly"><span class="pre"><code class="sourceCode python">is_variable_explicitly</code></span></a> | <span class="pre">`R`</span> | Returns <span class="pre">`True`</span> if this <span class="pre">`Feature`</span> has been declared <span class="pre">`variable`</span> in the textual syntax. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature.last_chaining_feature"><span class="pre"><code class="sourceCode python">last_chaining_feature</code></span></a> | <span class="pre">`R`</span> | The related <span class="pre">`Feature`</span> related by the last <span class="pre">`owned_feature_chaining`</span> if any. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature.owned_cross_feature"><span class="pre"><code class="sourceCode python">owned_cross_feature</code></span></a> | <span class="pre">`R`</span> | The member <span class="pre">`Feature`</span> that is declared before any prefixes in the textual syntax. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature.owned_cross_feature_member"><span class="pre"><code class="sourceCode python">owned_cross_feature_member</code></span></a> | <span class="pre">`R`</span> | Syside specific accessor for either owned crossing_feature or crossing_multiplicity. This is the member <span class="pre">`Feature`</span> that is declared before any prefixes in the textual syntax. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature.owned_cross_subsetting"><span class="pre"><code class="sourceCode python">owned_cross_subsetting</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_cross_subsetting`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature.owned_feature_chainings"><span class="pre"><code class="sourceCode python">owned_feature_chainings</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_feature_chaining`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature.owned_feature_invertings"><span class="pre"><code class="sourceCode python">owned_feature_invertings</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_feature_inverting`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature.owned_redefinitions"><span class="pre"><code class="sourceCode python">owned_redefinitions</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_redefinition`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature.owned_reference_subsetting"><span class="pre"><code class="sourceCode python">owned_reference_subsetting</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_reference_subsetting`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature.owned_subsettings"><span class="pre"><code class="sourceCode python">owned_subsettings</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_subsetting`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature.owned_type_featurings"><span class="pre"><code class="sourceCode python">owned_type_featurings</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_type_featuring`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature.owned_typings"><span class="pre"><code class="sourceCode python">owned_typings</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_typing`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature.owning_feature_membership"><span class="pre"><code class="sourceCode python">owning_feature_membership</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owning_feature_membership`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature.owning_type"><span class="pre"><code class="sourceCode python">owning_type</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owning_type`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature.referenced_feature"><span class="pre"><code class="sourceCode python">referenced_feature</code></span></a> | <span class="pre">`R`</span> | Returns the <span class="pre">`Feature`</span> this <span class="pre">`Feature`</span> references through <span class="pre">`ReferenceSubsetting`</span> if any. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature.referenced_feature_target"><span class="pre"><code class="sourceCode python">referenced_feature_target</code></span></a> | <span class="pre">`R`</span> | Returns the <span class="pre">`feature_target`</span> of <span class="pre">`referenced_feature`</span>, i.e. <span class="pre">`referenced_feature.feature_target`</span>. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature.types"><span class="pre"><code class="sourceCode python">types</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`type`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature.find_owned_cross_feature"><span class="pre"><code class="sourceCode python">find_owned_cross_feature</code></span></a> |  | Find the owned cross feature by potentially checking children. This is needed for spec that defined owned cross feature as the first member feature that is not a MetadataFeature or Multiplicity of an end feature. Since SysML does not allow member features (member keyword in KerML), this is equivalent to owned_cross_feature in SysML. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature.try_set_is_variable"><span class="pre"><code class="sourceCode python">try_set_is_variable</code></span></a> |  | Non-raising variant of <span class="pre">`is_variable`</span> setter that returns <span class="pre">`False`</span> on <span class="pre">`Usages`</span> without modifying <span class="pre">`is_variable`</span>. |

</div>

</div>

<span class="sd-summary-text">Members inherited from <a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type"><span class="pre"><code class="sourceCode python">Type</code></span></a> (37 members)</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |  |
|----|----|----|----|
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type.declared_multiplicity"><span class="pre"><code class="sourceCode python">declared_multiplicity</code></span></a> | <span class="pre">`R`</span> | The owned multiplicity that is declared before the children block in the textual syntax. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type.declared_multiplicity_member"><span class="pre"><code class="sourceCode python">declared_multiplicity_member</code></span></a> | <span class="pre">`R`</span> | Syside specific accessor for manipulating <span class="pre">`declared_multiplicity`</span>. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type.differencing_types"><span class="pre"><code class="sourceCode python">differencing_types</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`differencing_type`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type.directed_features"><span class="pre"><code class="sourceCode python">directed_features</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`directed_feature`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type.disjoining_types"><span class="pre"><code class="sourceCode python">disjoining_types</code></span></a> | <span class="pre">`R`</span> | The types that related to this <span class="pre">`Type`</span> through <span class="pre">`owned_disjoinings`</span>. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type.end_features"><span class="pre"><code class="sourceCode python">end_features</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`end_feature`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type.feature_memberships"><span class="pre"><code class="sourceCode python">feature_memberships</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`feature_membership`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type.features"><span class="pre"><code class="sourceCode python">features</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`feature`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type.heritage"><span class="pre"><code class="sourceCode python">heritage</code></span></a> | <span class="pre">`R`</span> | The specializations and conjugations owned by this <span class="pre">`Type`</span>. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type.inherited_features"><span class="pre"><code class="sourceCode python">inherited_features</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`inherited_feature`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type.inherited_memberships"><span class="pre"><code class="sourceCode python">inherited_memberships</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`inherited_membership`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type.inputs"><span class="pre"><code class="sourceCode python">inputs</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`input`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type.intersecting_types"><span class="pre"><code class="sourceCode python">intersecting_types</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`intersecting_type`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type.is_abstract"><span class="pre"><code class="sourceCode python">is_abstract</code></span></a> | <span class="pre">`RW`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`is_abstract`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type.is_abstract_explicitly"><span class="pre"><code class="sourceCode python">is_abstract_explicitly</code></span></a> | <span class="pre">`R`</span> | Returns <span class="pre">`True`</span> if this <span class="pre">`Type`</span> was declared as <span class="pre">`abstract`</span> in the textual syntax. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type.is_conjugated"><span class="pre"><code class="sourceCode python">is_conjugated</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`is_conjugated`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type.is_sufficient"><span class="pre"><code class="sourceCode python">is_sufficient</code></span></a> | <span class="pre">`RW`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`is_sufficient`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type.is_sufficient_explicitly"><span class="pre"><code class="sourceCode python">is_sufficient_explicitly</code></span></a> | <span class="pre">`R`</span> | Returns <span class="pre">`True`</span> if this <span class="pre">`Type`</span> was declared as <span class="pre">`sufficient`</span> in the textual syntax. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type.multiplicity"><span class="pre"><code class="sourceCode python">multiplicity</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`multiplicity`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type.outputs"><span class="pre"><code class="sourceCode python">outputs</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`output`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type.owned_conjugator"><span class="pre"><code class="sourceCode python">owned_conjugator</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_conjugator`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type.owned_differencings"><span class="pre"><code class="sourceCode python">owned_differencings</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_differencing`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type.owned_directed_features"><span class="pre"><code class="sourceCode python">owned_directed_features</code></span></a> | <span class="pre">`R`</span> | The <span class="pre">`directed_features`</span> that are owned by this <span class="pre">`Type`</span>. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type.owned_disjoinings"><span class="pre"><code class="sourceCode python">owned_disjoinings</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_disjoining`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type.owned_end_features"><span class="pre"><code class="sourceCode python">owned_end_features</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_end_feature`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type.owned_feature_memberships"><span class="pre"><code class="sourceCode python">owned_feature_memberships</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_feature_membership`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type.owned_features"><span class="pre"><code class="sourceCode python">owned_features</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_feature`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type.owned_inputs"><span class="pre"><code class="sourceCode python">owned_inputs</code></span></a> | <span class="pre">`R`</span> | The <span class="pre">`inputs`</span> that are owned by this <span class="pre">`Type`</span>. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type.owned_intersectings"><span class="pre"><code class="sourceCode python">owned_intersectings</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_intersecting`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type.owned_outputs"><span class="pre"><code class="sourceCode python">owned_outputs</code></span></a> | <span class="pre">`R`</span> | The <span class="pre">`outputs`</span> that are owned by this <span class="pre">`Type`</span>. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type.owned_specializations"><span class="pre"><code class="sourceCode python">owned_specializations</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_specialization`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type.owned_unionings"><span class="pre"><code class="sourceCode python">owned_unionings</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_unioning`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type.type_relationships"><span class="pre"><code class="sourceCode python">type_relationships</code></span></a> | <span class="pre">`R`</span> | The other type, feature relationships and <span class="pre">`FeatureChainings`</span> owned by this <span class="pre">`Type`</span>. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type.unioning_types"><span class="pre"><code class="sourceCode python">unioning_types</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`unioning_type`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type.conforms"><span class="pre"><code class="sourceCode python">conforms</code></span></a> |  | Returns <span class="pre">`True`</span> if this <span class="pre">`Type`</span> directly or indirectly specializes another <span class="pre">`Type`</span> while following <span class="pre">`FeatureChainings`</span>. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type.direction_of"><span class="pre"><code class="sourceCode python">direction_of</code></span></a> |  | Returns the direction of a <span class="pre">`Feature`</span> in this <span class="pre">`Type`</span>. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type.specializes"><span class="pre"><code class="sourceCode python">specializes</code></span></a> |  | Returns <span class="pre">`True`</span> if this <span class="pre">`Type`</span> directly or indirectly specializes another <span class="pre">`Type`</span> while ignoring <span class="pre">`FeatureChainings`</span>. |

</div>

</div>

<span class="sd-summary-text">Members inherited from <a href="/python/v0.8.4/syside/Namespace.md" class="reference internal" title="syside.Namespace"><span class="pre"><code class="sourceCode python">Namespace</code></span></a> (11 members)</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |  |
|----|----|----|----|
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Namespace.md" class="reference internal" title="syside.Namespace.children"><span class="pre"><code class="sourceCode python">children</code></span></a> | <span class="pre">`R`</span> | The elements enclosed by curly brackets in textual syntax. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Namespace.md" class="reference internal" title="syside.Namespace.imported_memberships"><span class="pre"><code class="sourceCode python">imported_memberships</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`imported_membership`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Namespace.md" class="reference internal" title="syside.Namespace.members"><span class="pre"><code class="sourceCode python">members</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`member`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Namespace.md" class="reference internal" title="syside.Namespace.memberships"><span class="pre"><code class="sourceCode python">memberships</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`membership`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Namespace.md" class="reference internal" title="syside.Namespace.owned_imports"><span class="pre"><code class="sourceCode python">owned_imports</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_import`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Namespace.md" class="reference internal" title="syside.Namespace.owned_members"><span class="pre"><code class="sourceCode python">owned_members</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_member`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Namespace.md" class="reference internal" title="syside.Namespace.owned_memberships"><span class="pre"><code class="sourceCode python">owned_memberships</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_membership`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Namespace.md" class="reference internal" title="syside.Namespace.prefixes"><span class="pre"><code class="sourceCode python">prefixes</code></span></a> | <span class="pre">`R`</span> | Metadata prefixes, prefixed with <span class="pre">`#`</span> in textual syntax. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Namespace.md" class="reference internal" title="syside.Namespace.__getitem__"><span class="pre"><code class="sourceCode python"><span class="fu">__getitem__</span></code></span></a> |  | Access owned named members by name. Throws <span class="pre">`KeyError`</span> if a member with such name does not exist. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Namespace.md" class="reference internal" title="syside.Namespace.get_member"><span class="pre"><code class="sourceCode python">get_member</code></span></a> |  | Non-throwing variant of <span class="pre">`__getitem__`</span>. Returns None if a named member was not found. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Namespace.md" class="reference internal" title="syside.Namespace.get_membership"><span class="pre"><code class="sourceCode python">get_membership</code></span></a> |  | Access owned memberships by name. Returns None if an owned member or membership with such name does not exist. |

</div>

</div>

<span class="sd-summary-text">Members inherited from <a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element"><span class="pre"><code class="sourceCode python">Element</code></span></a> (25 members)</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |  |
|----|----|----|----|
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element.alias_ids"><span class="pre"><code class="sourceCode python">alias_ids</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`alias_ids`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element.comments"><span class="pre"><code class="sourceCode python">comments</code></span></a> | <span class="pre">`R`</span> | The owned <span class="pre">`Comments`</span> related by <span class="pre">`owned_relationships`</span>. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element.declared_name"><span class="pre"><code class="sourceCode python">declared_name</code></span></a> | <span class="pre">`RW`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`declared_name`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element.declared_short_name"><span class="pre"><code class="sourceCode python">declared_short_name</code></span></a> | <span class="pre">`RW`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`declared_short_name`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element.documentation"><span class="pre"><code class="sourceCode python">documentation</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`documentation`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element.element_id"><span class="pre"><code class="sourceCode python">element_id</code></span></a> | <span class="pre">`RW`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`element_id`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element.is_implied_included"><span class="pre"><code class="sourceCode python">is_implied_included</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`is_implied_included`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element.is_library_element"><span class="pre"><code class="sourceCode python">is_library_element</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`is_library_element`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element.metadata"><span class="pre"><code class="sourceCode python">metadata</code></span></a> | <span class="pre">`R`</span> | The owned metadata related by <span class="pre">`owned_relationships`</span>. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element.name"><span class="pre"><code class="sourceCode python">name</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`name`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element.owned_annotations"><span class="pre"><code class="sourceCode python">owned_annotations</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_annotation`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element.owned_elements"><span class="pre"><code class="sourceCode python">owned_elements</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_element`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element.owned_relationships"><span class="pre"><code class="sourceCode python">owned_relationships</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_relationship`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element.owner"><span class="pre"><code class="sourceCode python">owner</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owner`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element.owning_membership"><span class="pre"><code class="sourceCode python">owning_membership</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owning_membership`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element.owning_namespace"><span class="pre"><code class="sourceCode python">owning_namespace</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owning_namespace`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element.owning_relationship"><span class="pre"><code class="sourceCode python">owning_relationship</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owning_relationship`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element.path"><span class="pre"><code class="sourceCode python">path</code></span></a> | <span class="pre">`R`</span> | Return a unique description of the location of this <span class="pre">`Element`</span> in the containment structure rooted in a root <span class="pre">`Namespace`</span>. In most cases the segments will be identical to <span class="pre">`QualifiedName`</span>. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element.qualified_name"><span class="pre"><code class="sourceCode python">qualified_name</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`qualified_name`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element.scoped_owner"><span class="pre"><code class="sourceCode python">scoped_owner</code></span></a> | <span class="pre">`R`</span> | The owner of this <span class="pre">`Element`</span> as the parent of <span class="pre">`owning_membership`</span> or <span class="pre">`owning_relationship`</span> otherwise. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element.sema_state"><span class="pre"><code class="sourceCode python">sema_state</code></span></a> | <span class="pre">`RW`</span> | The state of semantic resolution for this <span class="pre">`Element`</span>. Based on this, sema may skip elements to avoid duplicate work, e.g. when resolving elements in a group of related documents. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element.short_name"><span class="pre"><code class="sourceCode python">short_name</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`short_name`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element.textual_representations"><span class="pre"><code class="sourceCode python">textual_representations</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`textual_representation`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element.__str__"><span class="pre"><code class="sourceCode python"><span class="fu">__str__</span></code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element.matches_qualified_name"><span class="pre"><code class="sourceCode python">matches_qualified_name</code></span></a> |  | Check if the qualified name of this <span class="pre">`Element`</span> matches the provided segments of a qualified name. |

</div>

</div>

<span class="sd-summary-text">Members inherited from <a href="/python/v0.8.4/syside/AstNode.md" class="reference internal" title="syside.AstNode"><span class="pre"><code class="sourceCode python">AstNode</code></span></a> (7 members)</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |  |
|----|----|----|----|
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/AstNode.md" class="reference internal" title="syside.AstNode.cst_node"><span class="pre"><code class="sourceCode python">cst_node</code></span></a> | <span class="pre">`R`</span> |  |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/AstNode.md" class="reference internal" title="syside.AstNode.document"><span class="pre"><code class="sourceCode python">document</code></span></a> | <span class="pre">`R`</span> |  |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/AstNode.md" class="reference internal" title="syside.AstNode.parent"><span class="pre"><code class="sourceCode python">parent</code></span></a> | <span class="pre">`R`</span> |  |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/AstNode.md" class="reference internal" title="syside.AstNode.__hash__"><span class="pre"><code class="sourceCode python"><span class="fu">__hash__</span></code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/AstNode.md" class="reference internal" title="syside.AstNode.cast"><span class="pre"><code class="sourceCode python">cast</code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/AstNode.md" class="reference internal" title="syside.AstNode.isinstance"><span class="pre"><code class="sourceCode python"><span class="bu">isinstance</span></code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/AstNode.md" class="reference internal" title="syside.AstNode.try_cast"><span class="pre"><code class="sourceCode python">try_cast</code></span></a> |  |  |

</div>

</div>

<span class="nerd-font"></span> **Attributes**

<span class="sig-name descname"><span class="pre">STD</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><span class="pre">type</span><span class="p"><span class="pre">\[</span></span><a href="#syside.Usage" class="reference internal" title="syside.Usage"><span class="pre">syside.Usage</span></a><span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="p"><span class="pre">...</span></span><span class="p"><span class="pre">\]</span></span><span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">()</span>*<a href="#syside.Usage.STD" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">definitions</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Classifier.md" class="reference internal" title="syside.Classifier"><span class="pre">syside.Classifier</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Usage.definitions" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`definition`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> The <span class="pre">`Classifiers`</span> that are the types of this <span class="pre">`Usage`</span>. Nominally, these are <span class="pre">`Definitions`</span>, but other kinds of Kernel <span class="pre">`Classifiers`</span> are also allowed, to permit use of <span class="pre">`Classifiers`</span> from the Kernel Model Libraries.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=303" class="reference external" target="_blank">8.3.6.4</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">directed_usages</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="#syside.Usage" class="reference internal" title="syside.Usage"><span class="pre">syside.Usage</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Usage.directed_usages" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`directed_usage`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> The <span class="pre">`usages`</span> of this <span class="pre">`Usage`</span> that are <span class="pre">`directed_features`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=303" class="reference external" target="_blank">8.3.6.4</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">is_reference</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*<a href="#syside.Usage.is_reference" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`is_reference`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> Whether this <span class="pre">`Usage`</span> is a referential <span class="pre">`Usage`</span>, that is, it has <span class="pre">`is_composite`</span>` `<span class="pre">`=`</span>` `<span class="pre">`false`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=303" class="reference external" target="_blank">8.3.6.4</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">is_reference_explicitly</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*<a href="#syside.Usage.is_reference_explicitly" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Returns <span class="pre">`True`</span> if this <span class="pre">`Usage`</span> was explicitly declared as <span class="pre">`ref`</span> in the textual syntax.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">is_variation</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*<a href="#syside.Usage.is_variation" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`is_variation`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> Whether this <span class="pre">`Usage`</span> is for a variation point or not. If true, then all the <span class="pre">`memberships`</span> of the <span class="pre">`Usage`</span> must be <span class="pre">`VariantMemberships`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=303" class="reference external" target="_blank">8.3.6.4</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">may_time_vary</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*<a href="#syside.Usage.may_time_vary" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`may_time_vary`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> Whether this <span class="pre">`Usage`</span> may be time varying (that is, whether it is featured by the snapshots of its <span class="pre">`owning_type`</span>, rather than being featured by the <span class="pre">`owning_type`</span> itself). However, if <span class="pre">`is_constant`</span> is also true, then the value of the <span class="pre">`Usage`</span> is nevertheless constant over the entire duration of an instance of its <span class="pre">`owning_type`</span> (that is, it has the same value on all snapshots).
>
> The property <span class="pre">`may_time_vary`</span> redefines the KerML property <span class="pre">`Feature::is_variable`</span>, making it derived. The property <span class="pre">`is_constant`</span> is inherited from <span class="pre">`Feature`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=303" class="reference external" target="_blank">8.3.6.4</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">nested_actions</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/ActionUsage.md" class="reference internal" title="syside.ActionUsage"><span class="pre">syside.ActionUsage</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/FlowUsage.md" class="reference internal" title="syside.FlowUsage"><span class="pre">syside.FlowUsage</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Usage.nested_actions" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`nested_action`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> The <span class="pre">`ActionUsages`</span> that are <span class="pre">`nested_usages`</span> of this <span class="pre">`Usage`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=303" class="reference external" target="_blank">8.3.6.4</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">nested_allocations</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/AllocationUsage.md" class="reference internal" title="syside.AllocationUsage"><span class="pre">syside.AllocationUsage</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Usage.nested_allocations" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`nested_allocation`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> The <span class="pre">`AllocationUsages`</span> that are <span class="pre">`nested_usages`</span> of this <span class="pre">`Usage`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=304" class="reference external" target="_blank">8.3.6.4</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">nested_analysis_cases</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/AnalysisCaseUsage.md" class="reference internal" title="syside.AnalysisCaseUsage"><span class="pre">syside.AnalysisCaseUsage</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Usage.nested_analysis_cases" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`nested_analysis_case`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> The <span class="pre">`AnalysisCaseUsages`</span> that are <span class="pre">`nested_usages`</span> of this <span class="pre">`Usage`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=304" class="reference external" target="_blank">8.3.6.4</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">nested_attributes</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/AttributeUsage.md" class="reference internal" title="syside.AttributeUsage"><span class="pre">syside.AttributeUsage</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Usage.nested_attributes" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`nested_attribute`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> The code\>AttributeUsages that are <span class="pre">`nested_usages`</span> of this <span class="pre">`Usage`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=304" class="reference external" target="_blank">8.3.6.4</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">nested_calculations</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/CalculationUsage.md" class="reference internal" title="syside.CalculationUsage"><span class="pre">syside.CalculationUsage</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Usage.nested_calculations" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`nested_calculation`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> The <span class="pre">`CalculationUsage`</span> that are <span class="pre">`nested_usages`</span> of this <span class="pre">`Usage`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=304" class="reference external" target="_blank">8.3.6.4</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">nested_cases</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/CaseUsage.md" class="reference internal" title="syside.CaseUsage"><span class="pre">syside.CaseUsage</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Usage.nested_cases" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`nested_case`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> The <span class="pre">`CaseUsages`</span> that are <span class="pre">`nested_usages`</span> of this <span class="pre">`Usage`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=304" class="reference external" target="_blank">8.3.6.4</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">nested_concerns</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/ConcernUsage.md" class="reference internal" title="syside.ConcernUsage"><span class="pre">syside.ConcernUsage</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Usage.nested_concerns" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`nested_concern`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> The <span class="pre">`ConcernUsages`</span> that are <span class="pre">`nested_usages`</span> of this <span class="pre">`Usage`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=304" class="reference external" target="_blank">8.3.6.4</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">nested_connections</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/ConnectorAsUsage.md" class="reference internal" title="syside.ConnectorAsUsage"><span class="pre">syside.ConnectorAsUsage</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Usage.nested_connections" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`nested_connection`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> The <span class="pre">`ConnectorAsUsages`</span> that are <span class="pre">`nested_usages`</span> of this <span class="pre">`Usage`</span>. Note that this list includes <span class="pre">`BindingConnectorAsUsages`</span>, <span class="pre">`SuccessionAsUsages`</span>, and <span class="pre">`FlowUsages`</span> because these are <span class="pre">`ConnectorAsUsages`</span> even though they are not <span class="pre">`ConnectionUsages`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=304" class="reference external" target="_blank">8.3.6.4</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">nested_constraints</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/ConstraintUsage.md" class="reference internal" title="syside.ConstraintUsage"><span class="pre">syside.ConstraintUsage</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Usage.nested_constraints" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`nested_constraint`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> The <span class="pre">`ConstraintUsages`</span> that are <span class="pre">`nested_usages`</span> of this <span class="pre">`Usage`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=304" class="reference external" target="_blank">8.3.6.4</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">nested_enumerations</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/EnumerationUsage.md" class="reference internal" title="syside.EnumerationUsage"><span class="pre">syside.EnumerationUsage</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Usage.nested_enumerations" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`nested_enumeration`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> The code\>EnumerationUsages that are <span class="pre">`nested_usages`</span> of this <span class="pre">`Usage`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=304" class="reference external" target="_blank">8.3.6.4</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">nested_flows</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/FlowUsage.md" class="reference internal" title="syside.FlowUsage"><span class="pre">syside.FlowUsage</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Usage.nested_flows" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`nested_flow`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> The code\>FlowUsages that are <span class="pre">`nested_usages`</span> of this <span class="pre">`Usage`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=304" class="reference external" target="_blank">8.3.6.4</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">nested_interfaces</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/InterfaceUsage.md" class="reference internal" title="syside.InterfaceUsage"><span class="pre">syside.InterfaceUsage</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Usage.nested_interfaces" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`nested_interface`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> The <span class="pre">`InterfaceUsages`</span> that are <span class="pre">`nested_usages`</span> of this <span class="pre">`Usage`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=304" class="reference external" target="_blank">8.3.6.4</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">nested_items</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/ItemUsage.md" class="reference internal" title="syside.ItemUsage"><span class="pre">syside.ItemUsage</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Usage.nested_items" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`nested_item`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> The <span class="pre">`ItemUsages`</span> that are <span class="pre">`nested_usages`</span> of this <span class="pre">`Usage`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=304" class="reference external" target="_blank">8.3.6.4</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">nested_metadata</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/MetadataUsage.md" class="reference internal" title="syside.MetadataUsage"><span class="pre">syside.MetadataUsage</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Usage.nested_metadata" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`nested_metadata`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> The <span class="pre">`MetadataUsages`</span> that are <span class="pre">`nested_usages`</span> of this of this <span class="pre">`Usage`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=304" class="reference external" target="_blank">8.3.6.4</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">nested_occurrences</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/OccurrenceUsage.md" class="reference internal" title="syside.OccurrenceUsage"><span class="pre">syside.OccurrenceUsage</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Usage.nested_occurrences" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`nested_occurrence`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> The <span class="pre">`OccurrenceUsages`</span> that are <span class="pre">`nested_usages`</span> of this <span class="pre">`Usage`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=305" class="reference external" target="_blank">8.3.6.4</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">nested_parts</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/PartUsage.md" class="reference internal" title="syside.PartUsage"><span class="pre">syside.PartUsage</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/ConnectionUsage.md" class="reference internal" title="syside.ConnectionUsage"><span class="pre">syside.ConnectionUsage</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Usage.nested_parts" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`nested_part`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> The <span class="pre">`PartUsages`</span> that are <span class="pre">`nested_usages`</span> of this <span class="pre">`Usage`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=305" class="reference external" target="_blank">8.3.6.4</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">nested_ports</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/PortUsage.md" class="reference internal" title="syside.PortUsage"><span class="pre">syside.PortUsage</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Usage.nested_ports" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`nested_port`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> The <span class="pre">`PortUsages`</span> that are <span class="pre">`nested_usages`</span> of this <span class="pre">`Usage`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=305" class="reference external" target="_blank">8.3.6.4</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">nested_references</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/ReferenceUsage.md" class="reference internal" title="syside.ReferenceUsage"><span class="pre">syside.ReferenceUsage</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Usage.nested_references" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`nested_reference`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> The <span class="pre">`ReferenceUsages`</span> that are <span class="pre">`nested_usages`</span> of this <span class="pre">`Usage`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=305" class="reference external" target="_blank">8.3.6.4</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">nested_renderings</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/RenderingUsage.md" class="reference internal" title="syside.RenderingUsage"><span class="pre">syside.RenderingUsage</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Usage.nested_renderings" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`nested_rendering`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> The <span class="pre">`RenderingUsages`</span> that are <span class="pre">`nested_usages`</span> of this <span class="pre">`Usage`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=305" class="reference external" target="_blank">8.3.6.4</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">nested_requirements</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/RequirementUsage.md" class="reference internal" title="syside.RequirementUsage"><span class="pre">syside.RequirementUsage</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Usage.nested_requirements" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`nested_requirement`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> The <span class="pre">`RequirementUsages`</span> that are <span class="pre">`nested_usages`</span> of this <span class="pre">`Usage`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=305" class="reference external" target="_blank">8.3.6.4</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">nested_states</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/StateUsage.md" class="reference internal" title="syside.StateUsage"><span class="pre">syside.StateUsage</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Usage.nested_states" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`nested_state`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> The <span class="pre">`StateUsages`</span> that are <span class="pre">`nested_usages`</span> of this <span class="pre">`Usage`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=305" class="reference external" target="_blank">8.3.6.4</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">nested_transitions</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/TransitionUsage.md" class="reference internal" title="syside.TransitionUsage"><span class="pre">syside.TransitionUsage</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Usage.nested_transitions" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`nested_transition`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> The <span class="pre">`TransitionUsages`</span> that are <span class="pre">`nested_usages`</span> of this <span class="pre">`Usage`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=305" class="reference external" target="_blank">8.3.6.4</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">nested_usages</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="#syside.Usage" class="reference internal" title="syside.Usage"><span class="pre">syside.Usage</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Usage.nested_usages" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`nested_usage`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> The <span class="pre">`Usages`</span> that are <span class="pre">`owned_features`</span> of this <span class="pre">`Usage`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=305" class="reference external" target="_blank">8.3.6.4</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">nested_use_cases</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/UseCaseUsage.md" class="reference internal" title="syside.UseCaseUsage"><span class="pre">syside.UseCaseUsage</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Usage.nested_use_cases" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`nested_use_case`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> The <span class="pre">`UseCaseUsages`</span> that are <span class="pre">`nested_usages`</span> of this <span class="pre">`Usage`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=305" class="reference external" target="_blank">8.3.6.4</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">nested_verification_cases</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/VerificationCaseUsage.md" class="reference internal" title="syside.VerificationCaseUsage"><span class="pre">syside.VerificationCaseUsage</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Usage.nested_verification_cases" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`nested_verification_case`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> The <span class="pre">`VerificationCaseUsages`</span> that are <span class="pre">`nested_usages`</span> of this <span class="pre">`Usage`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=305" class="reference external" target="_blank">8.3.6.4</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">nested_viewpoints</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/ViewpointUsage.md" class="reference internal" title="syside.ViewpointUsage"><span class="pre">syside.ViewpointUsage</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Usage.nested_viewpoints" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`nested_viewpoint`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> The <span class="pre">`ViewpointUsages`</span> that are <span class="pre">`nested_usages`</span> of this <span class="pre">`Usage`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=305" class="reference external" target="_blank">8.3.6.4</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">nested_views</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/ViewUsage.md" class="reference internal" title="syside.ViewUsage"><span class="pre">syside.ViewUsage</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Usage.nested_views" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`nested_view`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> The <span class="pre">`ViewUsages`</span> that are <span class="pre">`nested_usages`</span> of this <span class="pre">`Usage`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=305" class="reference external" target="_blank">8.3.6.4</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owning_definition</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/Definition.md" class="reference internal" title="syside.Definition"><span class="pre">syside.Definition</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span>*<a href="#syside.Usage.owning_definition" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owning_definition`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> The <span class="pre">`Definition`</span> that owns this <span class="pre">`Usage`</span> (if any).
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=305" class="reference external" target="_blank">8.3.6.4</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owning_usage</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="#syside.Usage" class="reference internal" title="syside.Usage"><span class="pre">syside.Usage</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span>*<a href="#syside.Usage.owning_usage" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owning_usage`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> The <span class="pre">`Usage`</span> in which this <span class="pre">`Usage`</span> is nested (if any).
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=306" class="reference external" target="_blank">8.3.6.4</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">usages</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="#syside.Usage" class="reference internal" title="syside.Usage"><span class="pre">syside.Usage</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Usage.usages" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`usage`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> The <span class="pre">`Usages`</span> that are <span class="pre">`features`</span> of this <span class="pre">`Usage`</span> (not necessarily owned).
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=306" class="reference external" target="_blank">8.3.6.4</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">variant_memberships</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/VariantMembership.md" class="reference internal" title="syside.VariantMembership"><span class="pre">syside.VariantMembership</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Usage.variant_memberships" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`variant_membership`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> The <span class="pre">`owned_memberships`</span> of this <span class="pre">`Usage`</span> that are <span class="pre">`VariantMemberships`</span>. If <span class="pre">`is_variation`</span>` `<span class="pre">`=`</span>` `<span class="pre">`true`</span>, then this must be all <span class="pre">`memberships`</span> of the <span class="pre">`Usage`</span>. If <span class="pre">`is_variation`</span>` `<span class="pre">`=`</span>` `<span class="pre">`false`</span>, then <span class="pre">`variant_membership`</span>must be empty.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=306" class="reference external" target="_blank">8.3.6.4</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">variants</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="#syside.Usage" class="reference internal" title="syside.Usage"><span class="pre">syside.Usage</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Usage.variants" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`variant`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> The <span class="pre">`Usages`</span> which represent the variants of this <span class="pre">`Usage`</span> as a variation point <span class="pre">`Usage`</span>, if <span class="pre">`is_variation`</span>` `<span class="pre">`=`</span>` `<span class="pre">`true`</span>. If <span class="pre">`is_variation`</span>` `<span class="pre">`=`</span>` `<span class="pre">`false`</span>, then there must be no <span class="pre">`variants`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=306" class="reference external" target="_blank">8.3.6.4</a> of the SysML specification for more details.

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/CaseDefinition.md" class="reference internal" title="syside.CaseDefinition"><span class="pre"><code class="sourceCode python">syside.CaseDefinition</code></span></a>

  - <a href="/python/v0.8.4/syside/CaseDefinition.md" class="reference internal" title="syside.CaseDefinition.subject_parameter"><span class="pre"><code class="sourceCode python">subject_parameter</code></span></a>

- <a href="/python/v0.8.4/syside/CaseUsage.md" class="reference internal" title="syside.CaseUsage"><span class="pre"><code class="sourceCode python">syside.CaseUsage</code></span></a>

  - <a href="/python/v0.8.4/syside/CaseUsage.md" class="reference internal" title="syside.CaseUsage.subject_parameter"><span class="pre"><code class="sourceCode python">subject_parameter</code></span></a>

- <a href="/python/v0.8.4/syside/ConnectionDefinition.md" class="reference internal" title="syside.ConnectionDefinition"><span class="pre"><code class="sourceCode python">syside.ConnectionDefinition</code></span></a>

  - <a href="/python/v0.8.4/syside/ConnectionDefinition.md" class="reference internal" title="syside.ConnectionDefinition.connection_ends"><span class="pre"><code class="sourceCode python">connection_ends</code></span></a>

- <a href="/python/v0.8.4/syside/Definition.md" class="reference internal" title="syside.Definition"><span class="pre"><code class="sourceCode python">syside.Definition</code></span></a>

  - <a href="/python/v0.8.4/syside/Definition.md" class="reference internal" title="syside.Definition.directed_usages"><span class="pre"><code class="sourceCode python">directed_usages</code></span></a>

  - <a href="/python/v0.8.4/syside/Definition.md" class="reference internal" title="syside.Definition.owned_usages"><span class="pre"><code class="sourceCode python">owned_usages</code></span></a>

  - <a href="/python/v0.8.4/syside/Definition.md" class="reference internal" title="syside.Definition.usages"><span class="pre"><code class="sourceCode python">usages</code></span></a>

  - <a href="/python/v0.8.4/syside/Definition.md" class="reference internal" title="syside.Definition.variants"><span class="pre"><code class="sourceCode python">variants</code></span></a>

- <a href="/python/v0.8.4/syside/FlowDefinition.md" class="reference internal" title="syside.FlowDefinition"><span class="pre"><code class="sourceCode python">syside.FlowDefinition</code></span></a>

  - <a href="/python/v0.8.4/syside/FlowDefinition.md" class="reference internal" title="syside.FlowDefinition.flow_ends"><span class="pre"><code class="sourceCode python">flow_ends</code></span></a>

- <a href="/python/v0.8.4/syside/RequirementDefinition.md" class="reference internal" title="syside.RequirementDefinition"><span class="pre"><code class="sourceCode python">syside.RequirementDefinition</code></span></a>

  - <a href="/python/v0.8.4/syside/RequirementDefinition.md" class="reference internal" title="syside.RequirementDefinition.subject_parameter"><span class="pre"><code class="sourceCode python">subject_parameter</code></span></a>

- <a href="/python/v0.8.4/syside/RequirementUsage.md" class="reference internal" title="syside.RequirementUsage"><span class="pre"><code class="sourceCode python">syside.RequirementUsage</code></span></a>

  - <a href="/python/v0.8.4/syside/RequirementUsage.md" class="reference internal" title="syside.RequirementUsage.subject_parameter"><span class="pre"><code class="sourceCode python">subject_parameter</code></span></a>

- <a href="#syside.Usage" class="reference internal" title="syside.Usage"><span class="pre"><code class="sourceCode python">syside.Usage</code></span></a>

  - <a href="#syside.Usage.STD" class="reference internal" title="syside.Usage.STD"><span class="pre"><code class="sourceCode python">STD</code></span></a>

  - <a href="#syside.Usage.directed_usages" class="reference internal" title="syside.Usage.directed_usages"><span class="pre"><code class="sourceCode python">directed_usages</code></span></a>

  - <a href="#syside.Usage.nested_usages" class="reference internal" title="syside.Usage.nested_usages"><span class="pre"><code class="sourceCode python">nested_usages</code></span></a>

  - <a href="#syside.Usage.owning_usage" class="reference internal" title="syside.Usage.owning_usage"><span class="pre"><code class="sourceCode python">owning_usage</code></span></a>

  - <a href="#syside.Usage.usages" class="reference internal" title="syside.Usage.usages"><span class="pre"><code class="sourceCode python">usages</code></span></a>

  - <a href="#syside.Usage.variants" class="reference internal" title="syside.Usage.variants"><span class="pre"><code class="sourceCode python">variants</code></span></a>

- <a href="/python/v0.8.4/syside/VariantMembership.md" class="reference internal" title="syside.VariantMembership"><span class="pre"><code class="sourceCode python">syside.VariantMembership</code></span></a>

  - <a href="/python/v0.8.4/syside/VariantMembership.md" class="reference internal" title="syside.VariantMembership.owned_variant_usage"><span class="pre"><code class="sourceCode python">owned_variant_usage</code></span></a>

</div>

</div>
