<div id="definition-sysml" class="section">

# Definition <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span><a href="#definition-sysml" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">Definition</span></span><a href="#syside.Definition" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`Definition`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> A <span class="pre">`Definition`</span> is a <span class="pre">`Classifier`</span> of <span class="pre">`Usages`</span>. The actual kinds of <span class="pre">`Definition`</span> that may appear in a model are given by the subclasses of <span class="pre">`Definition`</span> (possibly as extended with user-defined <span class="pre">`SemanticMetadata`</span>).
>
> Normally, a <span class="pre">`Definition`</span> has owned Usages that model <span class="pre">`features`</span> of the thing being defined. A <span class="pre">`Definition`</span> may also have other <span class="pre">`Definitions`</span> nested in it, but this has no semantic significance, other than the nested scoping resulting from the <span class="pre">`Definition`</span> being considered as a <span class="pre">`Namespace`</span> for any nested <span class="pre">`Definitions`</span>.
>
> However, if a <span class="pre">`Definition`</span> has <span class="pre">`is_variation`</span> = <span class="pre">`true`</span>, then it represents a *variation point* <span class="pre">`Definition`</span>. In this case, all of its <span class="pre">`members`</span> must be <span class="pre">`variant`</span> <span class="pre">`Usages`</span>, related to the <span class="pre">`Definition`</span> by <span class="pre">`VariantMembership`</span> <span class="pre">`Relationships`</span>. Rather than being <span class="pre">`features`</span> of the <span class="pre">`Definition`</span>, <span class="pre">`variant`</span> <span class="pre">`Usages`</span> model different concrete alternatives that can be chosen to fill in for an abstract <span class="pre">`Usage`</span> of the variation point <span class="pre">`Definition`</span>.
>
> </div>

For language description, see section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=61" class="reference external" target="_blank">7.6</a> of the SysML specification. For more details on the model, see section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=295" class="reference external" target="_blank">8.3.6.2</a> of the SysML specification.

<div class="align-center" align="center">

<img src="data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iZ3JhcGh2aXoiIHN0eWxlPSJ3aWR0aDogNS43NXJlbTtoZWlnaHQ6IDI1LjI1cmVtOyIgdmlld2JveD0iMC4wMCAwLjAwIDkyLjAwIDQwNC4wMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGcgY2xhc3M9ImdyYXBoIiBpZD0iZ3JhcGgwIiB0cmFuc2Zvcm09InNjYWxlKDEgMSkgcm90YXRlKDApIHRyYW5zbGF0ZSg0IDQwMCkiPgo8dGl0bGU+JTM8L3RpdGxlPgo8ZyBjbGFzcz0ibm9kZSIgaWQ9Im5vZGUxIj4KPHRpdGxlPkRlZmluaXRpb248L3RpdGxlPgo8ZyBpZD0iYV9ub2RlMSI+PGEgaHJlZj0iI3N5c2lkZS5EZWZpbml0aW9uIj4KPHBvbHlnb24gcG9pbnRzPSI3OCwtMzYgNiwtMzYgNiwwIDc4LDAgNzgsLTM2IiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1iZy1jb2xvcik7c3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1ub2RlLWZnLWNvbG9yKTsiPjwvcG9seWdvbj4KPHRleHQgZm9udC1mYW1pbHk9IkxleGVuZCIgZm9udC1zaXplPSIxMi4wMCIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWNvZGUtZmctY29sb3IpOy0tbWQtZ3JhcGh2aXotaG92ZXItY29sb3I6IHZhcigtLW1kLWdyYXBodml6LWEtaG92ZXItY29sb3IpOyIgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iNDIiIHk9Ii0xNC4yIj5EZWZpbml0aW9uPC90ZXh0Pgo8dGl0bGU+c3lzaWRlLkRlZmluaXRpb248L3RpdGxlPjwvYT4KPC9nPgo8L2c+CjxnIGNsYXNzPSJub2RlIiBpZD0ibm9kZTIiPgo8dGl0bGU+Q2xhc3NpZmllcjwvdGl0bGU+CjxnIGlkPSJhX25vZGUyIj48YSBocmVmPSIvcHl0aG9uL3YwLjguNC9zeXNpZGUvQ2xhc3NpZmllci5tZCI+Cjxwb2x5Z29uIHBvaW50cz0iNzYuNSwtMTA4IDcuNSwtMTA4IDcuNSwtNzIgNzYuNSwtNzIgNzYuNSwtMTA4IiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1iZy1jb2xvcik7c3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1ub2RlLWZnLWNvbG9yKTsiPjwvcG9seWdvbj4KPHRleHQgZm9udC1mYW1pbHk9IkxleGVuZCIgZm9udC1zaXplPSIxMi4wMCIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWNvZGUtZmctY29sb3IpOy0tbWQtZ3JhcGh2aXotaG92ZXItY29sb3I6IHZhcigtLW1kLWdyYXBodml6LWEtaG92ZXItY29sb3IpOyIgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iNDIiIHk9Ii04Ni4yIj5DbGFzc2lmaWVyPC90ZXh0Pgo8dGl0bGU+c3lzaWRlLkNsYXNzaWZpZXI8L3RpdGxlPjwvYT4KPC9nPgo8L2c+CjxnIGNsYXNzPSJlZGdlIiBpZD0iZWRnZTEiPgo8dGl0bGU+Q2xhc3NpZmllci0mZ3Q7RGVmaW5pdGlvbjwvdGl0bGU+CjxwYXRoIGQ9Ik00MiwtNzEuN0M0MiwtNjMuOTggNDIsLTU0LjcxIDQyLC00Ni4xMSIgZmlsbD0ibm9uZSIgc3R5bGU9InN0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotZWRnZS1jb2xvcik7IiAvPgo8cG9seWdvbiBwb2ludHM9IjQ1LjUsLTQ2LjEgNDIsLTM2LjEgMzguNSwtNDYuMSA0NS41LC00Ni4xIiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtZ3JhcGh2aXotZWRnZS1jb2xvcik7c3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1lZGdlLWNvbG9yKTsiPjwvcG9seWdvbj4KPC9nPgo8ZyBjbGFzcz0ibm9kZSIgaWQ9Im5vZGUzIj4KPHRpdGxlPlR5cGU8L3RpdGxlPgo8ZyBpZD0iYV9ub2RlMyI+PGEgaHJlZj0iL3B5dGhvbi92MC44LjQvc3lzaWRlL1R5cGUubWQiPgo8cG9seWdvbiBwb2ludHM9IjY5LC0xODAgMTUsLTE4MCAxNSwtMTQ0IDY5LC0xNDQgNjksLTE4MCIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtYmctY29sb3IpO3N0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1mZy1jb2xvcik7Ij48L3BvbHlnb24+Cjx0ZXh0IGZvbnQtZmFtaWx5PSJMZXhlbmQiIGZvbnQtc2l6ZT0iMTIuMDAiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1jb2RlLWZnLWNvbG9yKTstLW1kLWdyYXBodml6LWhvdmVyLWNvbG9yOiB2YXIoLS1tZC1ncmFwaHZpei1hLWhvdmVyLWNvbG9yKTsiIHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjQyIiB5PSItMTU4LjIiPlR5cGU8L3RleHQ+Cjx0aXRsZT5zeXNpZGUuVHlwZTwvdGl0bGU+PC9hPgo8L2c+CjwvZz4KPGcgY2xhc3M9ImVkZ2UiIGlkPSJlZGdlMiI+Cjx0aXRsZT5UeXBlLSZndDtDbGFzc2lmaWVyPC90aXRsZT4KPHBhdGggZD0iTTQyLC0xNDMuN0M0MiwtMTM1Ljk4IDQyLC0xMjYuNzEgNDIsLTExOC4xMSIgZmlsbD0ibm9uZSIgc3R5bGU9InN0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotZWRnZS1jb2xvcik7IiAvPgo8cG9seWdvbiBwb2ludHM9IjQ1LjUsLTExOC4xIDQyLC0xMDguMSAzOC41LC0xMTguMSA0NS41LC0xMTguMSIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWdyYXBodml6LWVkZ2UtY29sb3IpO3N0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotZWRnZS1jb2xvcik7Ij48L3BvbHlnb24+CjwvZz4KPGcgY2xhc3M9Im5vZGUiIGlkPSJub2RlNCI+Cjx0aXRsZT5OYW1lc3BhY2U8L3RpdGxlPgo8ZyBpZD0iYV9ub2RlNCI+PGEgaHJlZj0iL3B5dGhvbi92MC44LjQvc3lzaWRlL05hbWVzcGFjZS5tZCI+Cjxwb2x5Z29uIHBvaW50cz0iODQsLTI1MiAwLC0yNTIgMCwtMjE2IDg0LC0yMTYgODQsLTI1MiIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtYmctY29sb3IpO3N0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1mZy1jb2xvcik7Ij48L3BvbHlnb24+Cjx0ZXh0IGZvbnQtZmFtaWx5PSJMZXhlbmQiIGZvbnQtc2l6ZT0iMTIuMDAiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1jb2RlLWZnLWNvbG9yKTstLW1kLWdyYXBodml6LWhvdmVyLWNvbG9yOiB2YXIoLS1tZC1ncmFwaHZpei1hLWhvdmVyLWNvbG9yKTsiIHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjQyIiB5PSItMjMwLjIiPk5hbWVzcGFjZTwvdGV4dD4KPHRpdGxlPnN5c2lkZS5OYW1lc3BhY2U8L3RpdGxlPjwvYT4KPC9nPgo8L2c+CjxnIGNsYXNzPSJlZGdlIiBpZD0iZWRnZTMiPgo8dGl0bGU+TmFtZXNwYWNlLSZndDtUeXBlPC90aXRsZT4KPHBhdGggZD0iTTQyLC0yMTUuN0M0MiwtMjA3Ljk4IDQyLC0xOTguNzEgNDIsLTE5MC4xMSIgZmlsbD0ibm9uZSIgc3R5bGU9InN0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotZWRnZS1jb2xvcik7IiAvPgo8cG9seWdvbiBwb2ludHM9IjQ1LjUsLTE5MC4xIDQyLC0xODAuMSAzOC41LC0xOTAuMSA0NS41LC0xOTAuMSIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWdyYXBodml6LWVkZ2UtY29sb3IpO3N0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotZWRnZS1jb2xvcik7Ij48L3BvbHlnb24+CjwvZz4KPGcgY2xhc3M9Im5vZGUiIGlkPSJub2RlNSI+Cjx0aXRsZT5FbGVtZW50PC90aXRsZT4KPGcgaWQ9ImFfbm9kZTUiPjxhIGhyZWY9Ii9weXRob24vdjAuOC40L3N5c2lkZS9FbGVtZW50Lm1kIj4KPHBvbHlnb24gcG9pbnRzPSI3MywtMzI0IDExLC0zMjQgMTEsLTI4OCA3MywtMjg4IDczLC0zMjQiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1ncmFwaHZpei1ub2RlLWJnLWNvbG9yKTtzdHJva2U6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtZmctY29sb3IpOyI+PC9wb2x5Z29uPgo8dGV4dCBmb250LWZhbWlseT0iTGV4ZW5kIiBmb250LXNpemU9IjEyLjAwIiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtY29kZS1mZy1jb2xvcik7LS1tZC1ncmFwaHZpei1ob3Zlci1jb2xvcjogdmFyKC0tbWQtZ3JhcGh2aXotYS1ob3Zlci1jb2xvcik7IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSI0MiIgeT0iLTMwMi4yIj5FbGVtZW50PC90ZXh0Pgo8dGl0bGU+c3lzaWRlLkVsZW1lbnQ8L3RpdGxlPjwvYT4KPC9nPgo8L2c+CjxnIGNsYXNzPSJlZGdlIiBpZD0iZWRnZTQiPgo8dGl0bGU+RWxlbWVudC0mZ3Q7TmFtZXNwYWNlPC90aXRsZT4KPHBhdGggZD0iTTQyLC0yODcuN0M0MiwtMjc5Ljk4IDQyLC0yNzAuNzEgNDIsLTI2Mi4xMSIgZmlsbD0ibm9uZSIgc3R5bGU9InN0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotZWRnZS1jb2xvcik7IiAvPgo8cG9seWdvbiBwb2ludHM9IjQ1LjUsLTI2Mi4xIDQyLC0yNTIuMSAzOC41LC0yNjIuMSA0NS41LC0yNjIuMSIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWdyYXBodml6LWVkZ2UtY29sb3IpO3N0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotZWRnZS1jb2xvcik7Ij48L3BvbHlnb24+CjwvZz4KPGcgY2xhc3M9Im5vZGUiIGlkPSJub2RlNiI+Cjx0aXRsZT5Bc3ROb2RlPC90aXRsZT4KPGcgaWQ9ImFfbm9kZTYiPjxhIGhyZWY9Ii9weXRob24vdjAuOC40L3N5c2lkZS9Bc3ROb2RlLm1kIj4KPHBvbHlnb24gcG9pbnRzPSI3NSwtMzk2IDksLTM5NiA5LC0zNjAgNzUsLTM2MCA3NSwtMzk2IiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1iZy1jb2xvcik7c3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1ub2RlLWZnLWNvbG9yKTsiPjwvcG9seWdvbj4KPHRleHQgZm9udC1mYW1pbHk9IkxleGVuZCIgZm9udC1zaXplPSIxMi4wMCIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWNvZGUtZmctY29sb3IpOy0tbWQtZ3JhcGh2aXotaG92ZXItY29sb3I6IHZhcigtLW1kLWdyYXBodml6LWEtaG92ZXItY29sb3IpOyIgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iNDIiIHk9Ii0zNzQuMiI+QXN0Tm9kZTwvdGV4dD4KPHRpdGxlPnN5c2lkZS5Bc3ROb2RlPC90aXRsZT48L2E+CjwvZz4KPC9nPgo8ZyBjbGFzcz0iZWRnZSIgaWQ9ImVkZ2U1Ij4KPHRpdGxlPkFzdE5vZGUtJmd0O0VsZW1lbnQ8L3RpdGxlPgo8cGF0aCBkPSJNNDIsLTM1OS43QzQyLC0zNTEuOTggNDIsLTM0Mi43MSA0MiwtMzM0LjExIiBmaWxsPSJub25lIiBzdHlsZT0ic3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1lZGdlLWNvbG9yKTsiIC8+Cjxwb2x5Z29uIHBvaW50cz0iNDUuNSwtMzM0LjEgNDIsLTMyNC4xIDM4LjUsLTMzNC4xIDQ1LjUsLTMzNC4xIiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtZ3JhcGh2aXotZWRnZS1jb2xvcik7c3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1lZGdlLWNvbG9yKTsiPjwvcG9seWdvbj4KPC9nPgo8L2c+Cjwvc3ZnPg==" class="graphviz" />

</div>

<span class="sd-summary-text"><span class="nerd-font"></span> Children</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/AttributeDefinition.md" class="reference internal" title="syside.AttributeDefinition"><span class="pre"><code class="sourceCode python">AttributeDefinition</code></span></a>

  - <a href="/python/v0.8.4/syside/EnumerationDefinition.md" class="reference internal" title="syside.EnumerationDefinition"><span class="pre"><code class="sourceCode python">EnumerationDefinition</code></span></a>

- <a href="/python/v0.8.4/syside/OccurrenceDefinition.md" class="reference internal" title="syside.OccurrenceDefinition"><span class="pre"><code class="sourceCode python">OccurrenceDefinition</code></span></a>

  - <a href="/python/v0.8.4/syside/ActionDefinition.md" class="reference internal" title="syside.ActionDefinition"><span class="pre"><code class="sourceCode python">ActionDefinition</code></span></a>

    - <a href="/python/v0.8.4/syside/CalculationDefinition.md" class="reference internal" title="syside.CalculationDefinition"><span class="pre"><code class="sourceCode python">CalculationDefinition</code></span></a>

      - <a href="/python/v0.8.4/syside/CaseDefinition.md" class="reference internal" title="syside.CaseDefinition"><span class="pre"><code class="sourceCode python">CaseDefinition</code></span></a>

        - <a href="/python/v0.8.4/syside/AnalysisCaseDefinition.md" class="reference internal" title="syside.AnalysisCaseDefinition"><span class="pre"><code class="sourceCode python">AnalysisCaseDefinition</code></span></a>

        - <a href="/python/v0.8.4/syside/UseCaseDefinition.md" class="reference internal" title="syside.UseCaseDefinition"><span class="pre"><code class="sourceCode python">UseCaseDefinition</code></span></a>

        - <a href="/python/v0.8.4/syside/VerificationCaseDefinition.md" class="reference internal" title="syside.VerificationCaseDefinition"><span class="pre"><code class="sourceCode python">VerificationCaseDefinition</code></span></a>

    - <a href="/python/v0.8.4/syside/FlowDefinition.md" class="reference internal" title="syside.FlowDefinition"><span class="pre"><code class="sourceCode python">FlowDefinition</code></span></a>

    - <a href="/python/v0.8.4/syside/StateDefinition.md" class="reference internal" title="syside.StateDefinition"><span class="pre"><code class="sourceCode python">StateDefinition</code></span></a>

  - <a href="/python/v0.8.4/syside/ConstraintDefinition.md" class="reference internal" title="syside.ConstraintDefinition"><span class="pre"><code class="sourceCode python">ConstraintDefinition</code></span></a>

    - <a href="/python/v0.8.4/syside/RequirementDefinition.md" class="reference internal" title="syside.RequirementDefinition"><span class="pre"><code class="sourceCode python">RequirementDefinition</code></span></a>

      - <a href="/python/v0.8.4/syside/ConcernDefinition.md" class="reference internal" title="syside.ConcernDefinition"><span class="pre"><code class="sourceCode python">ConcernDefinition</code></span></a>

      - <a href="/python/v0.8.4/syside/ViewpointDefinition.md" class="reference internal" title="syside.ViewpointDefinition"><span class="pre"><code class="sourceCode python">ViewpointDefinition</code></span></a>

  - <a href="/python/v0.8.4/syside/ItemDefinition.md" class="reference internal" title="syside.ItemDefinition"><span class="pre"><code class="sourceCode python">ItemDefinition</code></span></a>

    - <a href="/python/v0.8.4/syside/MetadataDefinition.md" class="reference internal" title="syside.MetadataDefinition"><span class="pre"><code class="sourceCode python">MetadataDefinition</code></span></a>

    - <a href="/python/v0.8.4/syside/PartDefinition.md" class="reference internal" title="syside.PartDefinition"><span class="pre"><code class="sourceCode python">PartDefinition</code></span></a>

      - <a href="/python/v0.8.4/syside/ConnectionDefinition.md" class="reference internal" title="syside.ConnectionDefinition"><span class="pre"><code class="sourceCode python">ConnectionDefinition</code></span></a>

        - <a href="/python/v0.8.4/syside/AllocationDefinition.md" class="reference internal" title="syside.AllocationDefinition"><span class="pre"><code class="sourceCode python">AllocationDefinition</code></span></a>

        - <a href="/python/v0.8.4/syside/InterfaceDefinition.md" class="reference internal" title="syside.InterfaceDefinition"><span class="pre"><code class="sourceCode python">InterfaceDefinition</code></span></a>

      - <a href="/python/v0.8.4/syside/RenderingDefinition.md" class="reference internal" title="syside.RenderingDefinition"><span class="pre"><code class="sourceCode python">RenderingDefinition</code></span></a>

      - <a href="/python/v0.8.4/syside/ViewDefinition.md" class="reference internal" title="syside.ViewDefinition"><span class="pre"><code class="sourceCode python">ViewDefinition</code></span></a>

  - <a href="/python/v0.8.4/syside/PortDefinition.md" class="reference internal" title="syside.PortDefinition"><span class="pre"><code class="sourceCode python">PortDefinition</code></span></a>

    - <a href="/python/v0.8.4/syside/ConjugatedPortDefinition.md" class="reference internal" title="syside.ConjugatedPortDefinition"><span class="pre"><code class="sourceCode python">ConjugatedPortDefinition</code></span></a>

</div>

<span class="sd-summary-text">Members defined in <a href="#syside.Definition" class="reference internal" title="syside.Definition"><span class="pre"><code class="sourceCode python">Definition</code></span></a> (34 members)</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |  |
|----|----|----|----|
| <span class="nerd-font"></span> | <a href="#syside.Definition.STD" class="reference internal" title="syside.Definition.STD"><span class="pre"><code class="sourceCode python">STD</code></span></a> | <span class="pre">`R`</span> |  |
| <span class="nerd-font"></span> | <a href="#syside.Definition.directed_usages" class="reference internal" title="syside.Definition.directed_usages"><span class="pre"><code class="sourceCode python">directed_usages</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`directed_usage`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Definition.is_variation" class="reference internal" title="syside.Definition.is_variation"><span class="pre"><code class="sourceCode python">is_variation</code></span></a> | <span class="pre">`RW`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`is_variation`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Definition.owned_actions" class="reference internal" title="syside.Definition.owned_actions"><span class="pre"><code class="sourceCode python">owned_actions</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_action`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Definition.owned_allocations" class="reference internal" title="syside.Definition.owned_allocations"><span class="pre"><code class="sourceCode python">owned_allocations</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_allocation`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Definition.owned_analysis_cases" class="reference internal" title="syside.Definition.owned_analysis_cases"><span class="pre"><code class="sourceCode python">owned_analysis_cases</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_analysis_case`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Definition.owned_attributes" class="reference internal" title="syside.Definition.owned_attributes"><span class="pre"><code class="sourceCode python">owned_attributes</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_attribute`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Definition.owned_calculations" class="reference internal" title="syside.Definition.owned_calculations"><span class="pre"><code class="sourceCode python">owned_calculations</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_calculation`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Definition.owned_cases" class="reference internal" title="syside.Definition.owned_cases"><span class="pre"><code class="sourceCode python">owned_cases</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_case`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Definition.owned_concerns" class="reference internal" title="syside.Definition.owned_concerns"><span class="pre"><code class="sourceCode python">owned_concerns</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_concern`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Definition.owned_connections" class="reference internal" title="syside.Definition.owned_connections"><span class="pre"><code class="sourceCode python">owned_connections</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_connection`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Definition.owned_constraints" class="reference internal" title="syside.Definition.owned_constraints"><span class="pre"><code class="sourceCode python">owned_constraints</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_constraint`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Definition.owned_enumerations" class="reference internal" title="syside.Definition.owned_enumerations"><span class="pre"><code class="sourceCode python">owned_enumerations</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_enumeration`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Definition.owned_flows" class="reference internal" title="syside.Definition.owned_flows"><span class="pre"><code class="sourceCode python">owned_flows</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_flow`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Definition.owned_interfaces" class="reference internal" title="syside.Definition.owned_interfaces"><span class="pre"><code class="sourceCode python">owned_interfaces</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_interface`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Definition.owned_items" class="reference internal" title="syside.Definition.owned_items"><span class="pre"><code class="sourceCode python">owned_items</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_item`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Definition.owned_metadata" class="reference internal" title="syside.Definition.owned_metadata"><span class="pre"><code class="sourceCode python">owned_metadata</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_metadata`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Definition.owned_occurrences" class="reference internal" title="syside.Definition.owned_occurrences"><span class="pre"><code class="sourceCode python">owned_occurrences</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_occurrence`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Definition.owned_parts" class="reference internal" title="syside.Definition.owned_parts"><span class="pre"><code class="sourceCode python">owned_parts</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_part`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Definition.owned_ports" class="reference internal" title="syside.Definition.owned_ports"><span class="pre"><code class="sourceCode python">owned_ports</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_port`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Definition.owned_references" class="reference internal" title="syside.Definition.owned_references"><span class="pre"><code class="sourceCode python">owned_references</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_reference`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Definition.owned_renderings" class="reference internal" title="syside.Definition.owned_renderings"><span class="pre"><code class="sourceCode python">owned_renderings</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_rendering`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Definition.owned_requirements" class="reference internal" title="syside.Definition.owned_requirements"><span class="pre"><code class="sourceCode python">owned_requirements</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_requirement`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Definition.owned_states" class="reference internal" title="syside.Definition.owned_states"><span class="pre"><code class="sourceCode python">owned_states</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_state`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Definition.owned_transitions" class="reference internal" title="syside.Definition.owned_transitions"><span class="pre"><code class="sourceCode python">owned_transitions</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_transition`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Definition.owned_usages" class="reference internal" title="syside.Definition.owned_usages"><span class="pre"><code class="sourceCode python">owned_usages</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_usage`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Definition.owned_use_cases" class="reference internal" title="syside.Definition.owned_use_cases"><span class="pre"><code class="sourceCode python">owned_use_cases</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_use_case`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Definition.owned_verification_cases" class="reference internal" title="syside.Definition.owned_verification_cases"><span class="pre"><code class="sourceCode python">owned_verification_cases</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_verification_case`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Definition.owned_viewpoints" class="reference internal" title="syside.Definition.owned_viewpoints"><span class="pre"><code class="sourceCode python">owned_viewpoints</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_viewpoint`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Definition.owned_views" class="reference internal" title="syside.Definition.owned_views"><span class="pre"><code class="sourceCode python">owned_views</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_view`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Definition.usages" class="reference internal" title="syside.Definition.usages"><span class="pre"><code class="sourceCode python">usages</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`usage`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Definition.variant_memberships" class="reference internal" title="syside.Definition.variant_memberships"><span class="pre"><code class="sourceCode python">variant_memberships</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`variant_membership`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Definition.variants" class="reference internal" title="syside.Definition.variants"><span class="pre"><code class="sourceCode python">variants</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`variant`</span> defined in the SysML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Definition.try_set_is_variation" class="reference internal" title="syside.Definition.try_set_is_variation"><span class="pre"><code class="sourceCode python">try_set_is_variation</code></span></a> |  | Try setting <span class="pre">`is_variation`</span>. For types that are implicitly variations, this will return <span class="pre">`False`</span> instead of throwing <span class="pre">`TypeError`</span> when using <span class="pre">`is_variation`</span> setter. |

</div>

</div>

<span class="sd-summary-text">Members inherited from <a href="/python/v0.8.4/syside/Classifier.md" class="reference internal" title="syside.Classifier"><span class="pre"><code class="sourceCode python">Classifier</code></span></a> (2 members)</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |  |
|----|----|----|----|
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Classifier.md" class="reference internal" title="syside.Classifier.owned_subclassification_types"><span class="pre"><code class="sourceCode python">owned_subclassification_types</code></span></a> | <span class="pre">`R`</span> | The <span class="pre">`Classifiers`</span> related to this <span class="pre">`Classifier`</span> by <span class="pre">`owned_subclassifications`</span>. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Classifier.md" class="reference internal" title="syside.Classifier.owned_subclassifications"><span class="pre"><code class="sourceCode python">owned_subclassifications</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_subclassification`</span> defined in the KerML specification. |

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

<span class="sig-name descname"><span class="pre">STD</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><span class="pre">type</span><span class="p"><span class="pre">\[</span></span><a href="#syside.Definition" class="reference internal" title="syside.Definition"><span class="pre">syside.Definition</span></a><span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="p"><span class="pre">...</span></span><span class="p"><span class="pre">\]</span></span><span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">()</span>*<a href="#syside.Definition.STD" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">directed_usages</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Usage.md" class="reference internal" title="syside.Usage"><span class="pre">syside.Usage</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Definition.directed_usages" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`directed_usage`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> The <span class="pre">`usages`</span> of this <span class="pre">`Definition`</span> that are <span class="pre">`directed_features`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=296" class="reference external" target="_blank">8.3.6.2</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">is_variation</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*<a href="#syside.Definition.is_variation" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`is_variation`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> Whether this <span class="pre">`Definition`</span> is for a variation point or not. If true, then all the <span class="pre">`memberships`</span> of the <span class="pre">`Definition`</span> must be <span class="pre">`VariantMemberships`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=296" class="reference external" target="_blank">8.3.6.2</a> of the SysML specification for more details.

The setter will throw <span class="pre">`TypeError`</span> on types that are implicitly variations already, e.g. <span class="pre">`EnumerationDefinition`</span>. Use <span class="pre">`try_set_is_variation`</span> instead for a non-throwing behaviour.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned_actions</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/ActionUsage.md" class="reference internal" title="syside.ActionUsage"><span class="pre">syside.ActionUsage</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/FlowUsage.md" class="reference internal" title="syside.FlowUsage"><span class="pre">syside.FlowUsage</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Definition.owned_actions" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owned_action`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> The <span class="pre">`ActionUsages`</span> that are <span class="pre">`owned_usages`</span> of this <span class="pre">`Definition`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=296" class="reference external" target="_blank">8.3.6.2</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned_allocations</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/AllocationUsage.md" class="reference internal" title="syside.AllocationUsage"><span class="pre">syside.AllocationUsage</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Definition.owned_allocations" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owned_allocation`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> The <span class="pre">`AllocationUsages`</span> that are <span class="pre">`owned_usages`</span> of this <span class="pre">`Definition`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=296" class="reference external" target="_blank">8.3.6.2</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned_analysis_cases</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/AnalysisCaseUsage.md" class="reference internal" title="syside.AnalysisCaseUsage"><span class="pre">syside.AnalysisCaseUsage</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Definition.owned_analysis_cases" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owned_analysis_case`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> The <span class="pre">`AnalysisCaseUsages`</span> that are <span class="pre">`owned_usages`</span> of this <span class="pre">`Definition`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=296" class="reference external" target="_blank">8.3.6.2</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned_attributes</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/AttributeUsage.md" class="reference internal" title="syside.AttributeUsage"><span class="pre">syside.AttributeUsage</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Definition.owned_attributes" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owned_attribute`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> The <span class="pre">`AttributeUsages`</span> that are <span class="pre">`owned_usages`</span> of this <span class="pre">`Definition`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=296" class="reference external" target="_blank">8.3.6.2</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned_calculations</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/CalculationUsage.md" class="reference internal" title="syside.CalculationUsage"><span class="pre">syside.CalculationUsage</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Definition.owned_calculations" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owned_calculation`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> The <span class="pre">`CalculationUsages`</span> that are <span class="pre">`owned_usages`</span> of this <span class="pre">`Definition`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=296" class="reference external" target="_blank">8.3.6.2</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned_cases</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/CaseUsage.md" class="reference internal" title="syside.CaseUsage"><span class="pre">syside.CaseUsage</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Definition.owned_cases" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owned_case`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> The code\>CaseUsages that are <span class="pre">`owned_usages`</span> of this <span class="pre">`Definition`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=296" class="reference external" target="_blank">8.3.6.2</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned_concerns</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/ConcernUsage.md" class="reference internal" title="syside.ConcernUsage"><span class="pre">syside.ConcernUsage</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Definition.owned_concerns" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owned_concern`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> The <span class="pre">`ConcernUsages`</span> that are <span class="pre">`owned_usages`</span> of this <span class="pre">`Definition`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=296" class="reference external" target="_blank">8.3.6.2</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned_connections</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/ConnectorAsUsage.md" class="reference internal" title="syside.ConnectorAsUsage"><span class="pre">syside.ConnectorAsUsage</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Definition.owned_connections" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owned_connection`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> The <span class="pre">`ConnectorAsUsages`</span> that are <span class="pre">`owned_usages`</span> of this <span class="pre">`Definition`</span>. Note that this list includes <span class="pre">`BindingConnectorAsUsages`</span>, <span class="pre">`SuccessionAsUsages`</span>, and <span class="pre">`FlowUsages`</span> because these are <span class="pre">`ConnectorAsUsages`</span> even though they are not <span class="pre">`ConnectionUsages`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=296" class="reference external" target="_blank">8.3.6.2</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned_constraints</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/ConstraintUsage.md" class="reference internal" title="syside.ConstraintUsage"><span class="pre">syside.ConstraintUsage</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Definition.owned_constraints" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owned_constraint`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> The <span class="pre">`ConstraintUsages`</span> that are <span class="pre">`owned_usages`</span> of this <span class="pre">`Definition`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=297" class="reference external" target="_blank">8.3.6.2</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned_enumerations</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/EnumerationUsage.md" class="reference internal" title="syside.EnumerationUsage"><span class="pre">syside.EnumerationUsage</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Definition.owned_enumerations" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owned_enumeration`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> The <span class="pre">`EnumerationUsages`</span> that are <span class="pre">`owned_usages`</span> of this <span class="pre">`Definition`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=297" class="reference external" target="_blank">8.3.6.2</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned_flows</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/FlowUsage.md" class="reference internal" title="syside.FlowUsage"><span class="pre">syside.FlowUsage</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Definition.owned_flows" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owned_flow`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> The <span class="pre">`FlowUsages`</span> that are <span class="pre">`owned_usages`</span> of this <span class="pre">`Definition`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=297" class="reference external" target="_blank">8.3.6.2</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned_interfaces</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/InterfaceUsage.md" class="reference internal" title="syside.InterfaceUsage"><span class="pre">syside.InterfaceUsage</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Definition.owned_interfaces" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owned_interface`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> The <span class="pre">`InterfaceUsages`</span> that are <span class="pre">`owned_usages`</span> of this <span class="pre">`Definition`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=297" class="reference external" target="_blank">8.3.6.2</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned_items</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/ItemUsage.md" class="reference internal" title="syside.ItemUsage"><span class="pre">syside.ItemUsage</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Definition.owned_items" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owned_item`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> The <span class="pre">`ItemUsages`</span> that are <span class="pre">`owned_usages`</span> of this <span class="pre">`Definition`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=297" class="reference external" target="_blank">8.3.6.2</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned_metadata</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/MetadataUsage.md" class="reference internal" title="syside.MetadataUsage"><span class="pre">syside.MetadataUsage</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Definition.owned_metadata" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owned_metadata`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> The <span class="pre">`MetadataUsages`</span> that are <span class="pre">`owned_usages`</span> of this <span class="pre">`Definition`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=297" class="reference external" target="_blank">8.3.6.2</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned_occurrences</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/OccurrenceUsage.md" class="reference internal" title="syside.OccurrenceUsage"><span class="pre">syside.OccurrenceUsage</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Definition.owned_occurrences" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owned_occurrence`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> The <span class="pre">`OccurrenceUsages`</span> that are <span class="pre">`owned_usages`</span> of this <span class="pre">`Definition`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=297" class="reference external" target="_blank">8.3.6.2</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned_parts</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/PartUsage.md" class="reference internal" title="syside.PartUsage"><span class="pre">syside.PartUsage</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/ConnectionUsage.md" class="reference internal" title="syside.ConnectionUsage"><span class="pre">syside.ConnectionUsage</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Definition.owned_parts" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owned_part`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> The <span class="pre">`PartUsages`</span> that are <span class="pre">`owned_usages`</span> of this <span class="pre">`Definition`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=297" class="reference external" target="_blank">8.3.6.2</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned_ports</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/PortUsage.md" class="reference internal" title="syside.PortUsage"><span class="pre">syside.PortUsage</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Definition.owned_ports" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owned_port`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> The <span class="pre">`PortUsages`</span> that are <span class="pre">`owned_usages`</span> of this <span class="pre">`Definition`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=297" class="reference external" target="_blank">8.3.6.2</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned_references</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/ReferenceUsage.md" class="reference internal" title="syside.ReferenceUsage"><span class="pre">syside.ReferenceUsage</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Definition.owned_references" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owned_reference`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> The <span class="pre">`ReferenceUsages`</span> that are <span class="pre">`owned_usages`</span> of this <span class="pre">`Definition`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=297" class="reference external" target="_blank">8.3.6.2</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned_renderings</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/RenderingUsage.md" class="reference internal" title="syside.RenderingUsage"><span class="pre">syside.RenderingUsage</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Definition.owned_renderings" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owned_rendering`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> The <span class="pre">`RenderingUsages`</span> that are <span class="pre">`owned_usages`</span> of this <span class="pre">`Definition`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=297" class="reference external" target="_blank">8.3.6.2</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned_requirements</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/RequirementUsage.md" class="reference internal" title="syside.RequirementUsage"><span class="pre">syside.RequirementUsage</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Definition.owned_requirements" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owned_requirement`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> The <span class="pre">`RequirementUsages`</span> that are <span class="pre">`owned_usages`</span> of this <span class="pre">`Definition`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=297" class="reference external" target="_blank">8.3.6.2</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned_states</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/StateUsage.md" class="reference internal" title="syside.StateUsage"><span class="pre">syside.StateUsage</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Definition.owned_states" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owned_state`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> The <span class="pre">`StateUsages`</span> that are <span class="pre">`owned_usages`</span> of this <span class="pre">`Definition`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=297" class="reference external" target="_blank">8.3.6.2</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned_transitions</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/TransitionUsage.md" class="reference internal" title="syside.TransitionUsage"><span class="pre">syside.TransitionUsage</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Definition.owned_transitions" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owned_transition`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> The <span class="pre">`TransitionUsages`</span> that are <span class="pre">`owned_usages`</span> of this <span class="pre">`Definition`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=298" class="reference external" target="_blank">8.3.6.2</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned_usages</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Usage.md" class="reference internal" title="syside.Usage"><span class="pre">syside.Usage</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Definition.owned_usages" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owned_usage`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> The <span class="pre">`Usages`</span> that are <span class="pre">`owned_features`</span> of this <span class="pre">`Definition`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=298" class="reference external" target="_blank">8.3.6.2</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned_use_cases</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/UseCaseUsage.md" class="reference internal" title="syside.UseCaseUsage"><span class="pre">syside.UseCaseUsage</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Definition.owned_use_cases" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owned_use_case`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> The <span class="pre">`UseCaseUsages`</span> that are <span class="pre">`owned_usages`</span> of this <span class="pre">`Definition`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=298" class="reference external" target="_blank">8.3.6.2</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned_verification_cases</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/VerificationCaseUsage.md" class="reference internal" title="syside.VerificationCaseUsage"><span class="pre">syside.VerificationCaseUsage</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Definition.owned_verification_cases" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owned_verification_case`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> The <span class="pre">`VerificationCaseUsages`</span> that are <span class="pre">`owned_usages`</span> of this <span class="pre">`Definition`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=298" class="reference external" target="_blank">8.3.6.2</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned_viewpoints</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/ViewpointUsage.md" class="reference internal" title="syside.ViewpointUsage"><span class="pre">syside.ViewpointUsage</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Definition.owned_viewpoints" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owned_viewpoint`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> The <span class="pre">`ViewpointUsages`</span> that are <span class="pre">`owned_usages`</span> of this <span class="pre">`Definition`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=298" class="reference external" target="_blank">8.3.6.2</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned_views</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/ViewUsage.md" class="reference internal" title="syside.ViewUsage"><span class="pre">syside.ViewUsage</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Definition.owned_views" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owned_view`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> The <span class="pre">`ViewUsages`</span> that are <span class="pre">`owned_usages`</span> of this <span class="pre">`Definition`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=298" class="reference external" target="_blank">8.3.6.2</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">usages</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Usage.md" class="reference internal" title="syside.Usage"><span class="pre">syside.Usage</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Definition.usages" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`usage`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> The <span class="pre">`Usages`</span> that are <span class="pre">`features`</span> of this <span class="pre">`Definition`</span> (not necessarily owned).
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=298" class="reference external" target="_blank">8.3.6.2</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">variant_memberships</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/VariantMembership.md" class="reference internal" title="syside.VariantMembership"><span class="pre">syside.VariantMembership</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Definition.variant_memberships" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`variant_membership`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> The <span class="pre">`owned_memberships`</span> of this <span class="pre">`Definition`</span> that are <span class="pre">`VariantMemberships`</span>. If <span class="pre">`is_variation`</span> = true, then this must be all <span class="pre">`owned_memberships`</span> of the <span class="pre">`Definition`</span>. If <span class="pre">`is_variation`</span> = false, then <span class="pre">`variant_membership`</span>must be empty.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=298" class="reference external" target="_blank">8.3.6.2</a> of the SysML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">variants</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Usage.md" class="reference internal" title="syside.Usage"><span class="pre">syside.Usage</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Definition.variants" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`variant`</span> defined in the SysML specification.

**Specification**:

> <div>
>
> The <span class="pre">`Usages`</span> which represent the variants of this <span class="pre">`Definition`</span> as a variation point <span class="pre">`Definition`</span>, if <span class="pre">`is_variation`</span> = true. If <span class="pre">`is_variation`</span>` `<span class="pre">`=`</span>` `<span class="pre">`false`</span>, the there must be no <span class="pre">`variants`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/2a-OMG_Systems_Modeling_Language.pdf#page=298" class="reference external" target="_blank">8.3.6.2</a> of the SysML specification for more details.

<span class="nerd-font"></span> **Methods**

<span class="sig-name descname"><span class="pre">try_set_is_variation</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">bool</span></span></span><a href="#syside.Definition.try_set_is_variation" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Try setting <span class="pre">`is_variation`</span>. For types that are implicitly variations, this will return <span class="pre">`False`</span> instead of throwing <span class="pre">`TypeError`</span> when using <span class="pre">`is_variation`</span> setter.

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="#syside.Definition" class="reference internal" title="syside.Definition"><span class="pre"><code class="sourceCode python">syside.Definition</code></span></a>

  - <a href="#syside.Definition.STD" class="reference internal" title="syside.Definition.STD"><span class="pre"><code class="sourceCode python">STD</code></span></a>

- <a href="/python/v0.8.4/syside/Usage.md" class="reference internal" title="syside.Usage"><span class="pre"><code class="sourceCode python">syside.Usage</code></span></a>

  - <a href="/python/v0.8.4/syside/Usage.md" class="reference internal" title="syside.Usage.owning_definition"><span class="pre"><code class="sourceCode python">owning_definition</code></span></a>

</div>

</div>
