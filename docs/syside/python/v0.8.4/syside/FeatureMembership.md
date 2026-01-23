<div id="featuremembership-sysml" class="section">

# FeatureMembership <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span><a href="#featuremembership-sysml" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">FeatureMembership</span></span><a href="#syside.FeatureMembership" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`FeatureMembership`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> A <span class="pre">`FeatureMembership`</span> is an <span class="pre">`OwningMembership`</span> between an <span class="pre">`owned_member_feature`</span> and an <span class="pre">`owning_type`</span>. If the <span class="pre">`owned_member_feature`</span> has <span class="pre">`is_variable`</span>` `<span class="pre">`=`</span>` `<span class="pre">`false`</span>, then the <span class="pre">`FeatureMembership`</span> implies that the <span class="pre">`owning_type`</span> is also a <span class="pre">`featuring_type`</span> of the <span class="pre">`owned_member_feature`</span>. If the <span class="pre">`owned_member_feature`</span> has <span class="pre">`is_variable`</span>` `<span class="pre">`=`</span>` `<span class="pre">`true`</span>, then the <span class="pre">`FeatureMembership`</span> implies that the <span class="pre">`owned_member_feature`</span> is featured by the <span class="pre">`snapshots`</span> of the <span class="pre">`owning_type`</span>, which must specialize the Kernel Semantic Library base class <span class="pre">`Occurrence`</span>.
>
> </div>

For language description, see section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=56" class="reference external" target="_blank">7.3.2.6</a> of the KerML specification. For more details on the model, see section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=168" class="reference external" target="_blank">8.3.3.1.6</a> of the KerML specification.

<div class="align-center" align="center">

<img src="data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iZ3JhcGh2aXoiIHN0eWxlPSJ3aWR0aDogOC43NXJlbTtoZWlnaHQ6IDI1LjI1cmVtOyIgdmlld2JveD0iMC4wMCAwLjAwIDE0MC4wMCA0MDQuMDAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxnIGNsYXNzPSJncmFwaCIgaWQ9ImdyYXBoMCIgdHJhbnNmb3JtPSJzY2FsZSgxIDEpIHJvdGF0ZSgwKSB0cmFuc2xhdGUoNCA0MDApIj4KPHRpdGxlPiUzPC90aXRsZT4KPGcgY2xhc3M9Im5vZGUiIGlkPSJub2RlMSI+Cjx0aXRsZT5GZWF0dXJlTWVtYmVyc2hpcDwvdGl0bGU+CjxnIGlkPSJhX25vZGUxIj48YSBocmVmPSIjc3lzaWRlLkZlYXR1cmVNZW1iZXJzaGlwIj4KPHBvbHlnb24gcG9pbnRzPSIxMzIsLTM2IDAsLTM2IDAsMCAxMzIsMCAxMzIsLTM2IiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1iZy1jb2xvcik7c3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1ub2RlLWZnLWNvbG9yKTsiPjwvcG9seWdvbj4KPHRleHQgZm9udC1mYW1pbHk9IkxleGVuZCIgZm9udC1zaXplPSIxMi4wMCIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWNvZGUtZmctY29sb3IpOy0tbWQtZ3JhcGh2aXotaG92ZXItY29sb3I6IHZhcigtLW1kLWdyYXBodml6LWEtaG92ZXItY29sb3IpOyIgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iNjYiIHk9Ii0xNC4yIj5GZWF0dXJlTWVtYmVyc2hpcDwvdGV4dD4KPHRpdGxlPnN5c2lkZS5GZWF0dXJlTWVtYmVyc2hpcDwvdGl0bGU+PC9hPgo8L2c+CjwvZz4KPGcgY2xhc3M9Im5vZGUiIGlkPSJub2RlMiI+Cjx0aXRsZT5Pd25pbmdNZW1iZXJzaGlwPC90aXRsZT4KPGcgaWQ9ImFfbm9kZTIiPjxhIGhyZWY9Ii9weXRob24vdjAuOC40L3N5c2lkZS9Pd25pbmdNZW1iZXJzaGlwLm1kIj4KPHBvbHlnb24gcG9pbnRzPSIxMzIsLTEwOCAwLC0xMDggMCwtNzIgMTMyLC03MiAxMzIsLTEwOCIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtYmctY29sb3IpO3N0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1mZy1jb2xvcik7Ij48L3BvbHlnb24+Cjx0ZXh0IGZvbnQtZmFtaWx5PSJMZXhlbmQiIGZvbnQtc2l6ZT0iMTIuMDAiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1jb2RlLWZnLWNvbG9yKTstLW1kLWdyYXBodml6LWhvdmVyLWNvbG9yOiB2YXIoLS1tZC1ncmFwaHZpei1hLWhvdmVyLWNvbG9yKTsiIHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjY2IiB5PSItODYuMiI+T3duaW5nTWVtYmVyc2hpcDwvdGV4dD4KPHRpdGxlPnN5c2lkZS5Pd25pbmdNZW1iZXJzaGlwPC90aXRsZT48L2E+CjwvZz4KPC9nPgo8ZyBjbGFzcz0iZWRnZSIgaWQ9ImVkZ2UxIj4KPHRpdGxlPk93bmluZ01lbWJlcnNoaXAtJmd0O0ZlYXR1cmVNZW1iZXJzaGlwPC90aXRsZT4KPHBhdGggZD0iTTY2LC03MS43QzY2LC02My45OCA2NiwtNTQuNzEgNjYsLTQ2LjExIiBmaWxsPSJub25lIiBzdHlsZT0ic3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1lZGdlLWNvbG9yKTsiIC8+Cjxwb2x5Z29uIHBvaW50cz0iNjkuNSwtNDYuMSA2NiwtMzYuMSA2Mi41LC00Ni4xIDY5LjUsLTQ2LjEiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1ncmFwaHZpei1lZGdlLWNvbG9yKTtzdHJva2U6IHZhcigtLW1kLWdyYXBodml6LWVkZ2UtY29sb3IpOyI+PC9wb2x5Z29uPgo8L2c+CjxnIGNsYXNzPSJub2RlIiBpZD0ibm9kZTMiPgo8dGl0bGU+TWVtYmVyc2hpcDwvdGl0bGU+CjxnIGlkPSJhX25vZGUzIj48YSBocmVmPSIvcHl0aG9uL3YwLjguNC9zeXNpZGUvTWVtYmVyc2hpcC5tZCI+Cjxwb2x5Z29uIHBvaW50cz0iMTA5LjUsLTE4MCAyMi41LC0xODAgMjIuNSwtMTQ0IDEwOS41LC0xNDQgMTA5LjUsLTE4MCIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtYmctY29sb3IpO3N0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1mZy1jb2xvcik7Ij48L3BvbHlnb24+Cjx0ZXh0IGZvbnQtZmFtaWx5PSJMZXhlbmQiIGZvbnQtc2l6ZT0iMTIuMDAiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1jb2RlLWZnLWNvbG9yKTstLW1kLWdyYXBodml6LWhvdmVyLWNvbG9yOiB2YXIoLS1tZC1ncmFwaHZpei1hLWhvdmVyLWNvbG9yKTsiIHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjY2IiB5PSItMTU4LjIiPk1lbWJlcnNoaXA8L3RleHQ+Cjx0aXRsZT5zeXNpZGUuTWVtYmVyc2hpcDwvdGl0bGU+PC9hPgo8L2c+CjwvZz4KPGcgY2xhc3M9ImVkZ2UiIGlkPSJlZGdlMiI+Cjx0aXRsZT5NZW1iZXJzaGlwLSZndDtPd25pbmdNZW1iZXJzaGlwPC90aXRsZT4KPHBhdGggZD0iTTY2LC0xNDMuN0M2NiwtMTM1Ljk4IDY2LC0xMjYuNzEgNjYsLTExOC4xMSIgZmlsbD0ibm9uZSIgc3R5bGU9InN0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotZWRnZS1jb2xvcik7IiAvPgo8cG9seWdvbiBwb2ludHM9IjY5LjUsLTExOC4xIDY2LC0xMDguMSA2Mi41LC0xMTguMSA2OS41LC0xMTguMSIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWdyYXBodml6LWVkZ2UtY29sb3IpO3N0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotZWRnZS1jb2xvcik7Ij48L3BvbHlnb24+CjwvZz4KPGcgY2xhc3M9Im5vZGUiIGlkPSJub2RlNCI+Cjx0aXRsZT5SZWxhdGlvbnNoaXA8L3RpdGxlPgo8ZyBpZD0iYV9ub2RlNCI+PGEgaHJlZj0iL3B5dGhvbi92MC44LjQvc3lzaWRlL1JlbGF0aW9uc2hpcC5tZCI+Cjxwb2x5Z29uIHBvaW50cz0iMTA5LjUsLTI1MiAyMi41LC0yNTIgMjIuNSwtMjE2IDEwOS41LC0yMTYgMTA5LjUsLTI1MiIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtYmctY29sb3IpO3N0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1mZy1jb2xvcik7Ij48L3BvbHlnb24+Cjx0ZXh0IGZvbnQtZmFtaWx5PSJMZXhlbmQiIGZvbnQtc2l6ZT0iMTIuMDAiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1jb2RlLWZnLWNvbG9yKTstLW1kLWdyYXBodml6LWhvdmVyLWNvbG9yOiB2YXIoLS1tZC1ncmFwaHZpei1hLWhvdmVyLWNvbG9yKTsiIHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjY2IiB5PSItMjMwLjIiPlJlbGF0aW9uc2hpcDwvdGV4dD4KPHRpdGxlPnN5c2lkZS5SZWxhdGlvbnNoaXA8L3RpdGxlPjwvYT4KPC9nPgo8L2c+CjxnIGNsYXNzPSJlZGdlIiBpZD0iZWRnZTMiPgo8dGl0bGU+UmVsYXRpb25zaGlwLSZndDtNZW1iZXJzaGlwPC90aXRsZT4KPHBhdGggZD0iTTY2LC0yMTUuN0M2NiwtMjA3Ljk4IDY2LC0xOTguNzEgNjYsLTE5MC4xMSIgZmlsbD0ibm9uZSIgc3R5bGU9InN0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotZWRnZS1jb2xvcik7IiAvPgo8cG9seWdvbiBwb2ludHM9IjY5LjUsLTE5MC4xIDY2LC0xODAuMSA2Mi41LC0xOTAuMSA2OS41LC0xOTAuMSIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWdyYXBodml6LWVkZ2UtY29sb3IpO3N0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotZWRnZS1jb2xvcik7Ij48L3BvbHlnb24+CjwvZz4KPGcgY2xhc3M9Im5vZGUiIGlkPSJub2RlNSI+Cjx0aXRsZT5FbGVtZW50PC90aXRsZT4KPGcgaWQ9ImFfbm9kZTUiPjxhIGhyZWY9Ii9weXRob24vdjAuOC40L3N5c2lkZS9FbGVtZW50Lm1kIj4KPHBvbHlnb24gcG9pbnRzPSI5NywtMzI0IDM1LC0zMjQgMzUsLTI4OCA5NywtMjg4IDk3LC0zMjQiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1ncmFwaHZpei1ub2RlLWJnLWNvbG9yKTtzdHJva2U6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtZmctY29sb3IpOyI+PC9wb2x5Z29uPgo8dGV4dCBmb250LWZhbWlseT0iTGV4ZW5kIiBmb250LXNpemU9IjEyLjAwIiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtY29kZS1mZy1jb2xvcik7LS1tZC1ncmFwaHZpei1ob3Zlci1jb2xvcjogdmFyKC0tbWQtZ3JhcGh2aXotYS1ob3Zlci1jb2xvcik7IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSI2NiIgeT0iLTMwMi4yIj5FbGVtZW50PC90ZXh0Pgo8dGl0bGU+c3lzaWRlLkVsZW1lbnQ8L3RpdGxlPjwvYT4KPC9nPgo8L2c+CjxnIGNsYXNzPSJlZGdlIiBpZD0iZWRnZTQiPgo8dGl0bGU+RWxlbWVudC0mZ3Q7UmVsYXRpb25zaGlwPC90aXRsZT4KPHBhdGggZD0iTTY2LC0yODcuN0M2NiwtMjc5Ljk4IDY2LC0yNzAuNzEgNjYsLTI2Mi4xMSIgZmlsbD0ibm9uZSIgc3R5bGU9InN0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotZWRnZS1jb2xvcik7IiAvPgo8cG9seWdvbiBwb2ludHM9IjY5LjUsLTI2Mi4xIDY2LC0yNTIuMSA2Mi41LC0yNjIuMSA2OS41LC0yNjIuMSIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWdyYXBodml6LWVkZ2UtY29sb3IpO3N0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotZWRnZS1jb2xvcik7Ij48L3BvbHlnb24+CjwvZz4KPGcgY2xhc3M9Im5vZGUiIGlkPSJub2RlNiI+Cjx0aXRsZT5Bc3ROb2RlPC90aXRsZT4KPGcgaWQ9ImFfbm9kZTYiPjxhIGhyZWY9Ii9weXRob24vdjAuOC40L3N5c2lkZS9Bc3ROb2RlLm1kIj4KPHBvbHlnb24gcG9pbnRzPSI5OSwtMzk2IDMzLC0zOTYgMzMsLTM2MCA5OSwtMzYwIDk5LC0zOTYiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1ncmFwaHZpei1ub2RlLWJnLWNvbG9yKTtzdHJva2U6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtZmctY29sb3IpOyI+PC9wb2x5Z29uPgo8dGV4dCBmb250LWZhbWlseT0iTGV4ZW5kIiBmb250LXNpemU9IjEyLjAwIiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtY29kZS1mZy1jb2xvcik7LS1tZC1ncmFwaHZpei1ob3Zlci1jb2xvcjogdmFyKC0tbWQtZ3JhcGh2aXotYS1ob3Zlci1jb2xvcik7IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSI2NiIgeT0iLTM3NC4yIj5Bc3ROb2RlPC90ZXh0Pgo8dGl0bGU+c3lzaWRlLkFzdE5vZGU8L3RpdGxlPjwvYT4KPC9nPgo8L2c+CjxnIGNsYXNzPSJlZGdlIiBpZD0iZWRnZTUiPgo8dGl0bGU+QXN0Tm9kZS0mZ3Q7RWxlbWVudDwvdGl0bGU+CjxwYXRoIGQ9Ik02NiwtMzU5LjdDNjYsLTM1MS45OCA2NiwtMzQyLjcxIDY2LC0zMzQuMTEiIGZpbGw9Im5vbmUiIHN0eWxlPSJzdHJva2U6IHZhcigtLW1kLWdyYXBodml6LWVkZ2UtY29sb3IpOyIgLz4KPHBvbHlnb24gcG9pbnRzPSI2OS41LC0zMzQuMSA2NiwtMzI0LjEgNjIuNSwtMzM0LjEgNjkuNSwtMzM0LjEiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1ncmFwaHZpei1lZGdlLWNvbG9yKTtzdHJva2U6IHZhcigtLW1kLWdyYXBodml6LWVkZ2UtY29sb3IpOyI+PC9wb2x5Z29uPgo8L2c+CjwvZz4KPC9zdmc+" class="graphviz" />

</div>

<span class="sd-summary-text"><span class="nerd-font"></span> Children</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/EndFeatureMembership.md" class="reference internal" title="syside.EndFeatureMembership"><span class="pre"><code class="sourceCode python">EndFeatureMembership</code></span></a>

- <a href="/python/v0.8.4/syside/ObjectiveMembership.md" class="reference internal" title="syside.ObjectiveMembership"><span class="pre"><code class="sourceCode python">ObjectiveMembership</code></span></a>

- <a href="/python/v0.8.4/syside/ParameterMembership.md" class="reference internal" title="syside.ParameterMembership"><span class="pre"><code class="sourceCode python">ParameterMembership</code></span></a>

  - <a href="/python/v0.8.4/syside/ActorMembership.md" class="reference internal" title="syside.ActorMembership"><span class="pre"><code class="sourceCode python">ActorMembership</code></span></a>

  - <a href="/python/v0.8.4/syside/ReturnParameterMembership.md" class="reference internal" title="syside.ReturnParameterMembership"><span class="pre"><code class="sourceCode python">ReturnParameterMembership</code></span></a>

  - <a href="/python/v0.8.4/syside/StakeholderMembership.md" class="reference internal" title="syside.StakeholderMembership"><span class="pre"><code class="sourceCode python">StakeholderMembership</code></span></a>

  - <a href="/python/v0.8.4/syside/SubjectMembership.md" class="reference internal" title="syside.SubjectMembership"><span class="pre"><code class="sourceCode python">SubjectMembership</code></span></a>

- <a href="/python/v0.8.4/syside/RequirementConstraintMembership.md" class="reference internal" title="syside.RequirementConstraintMembership"><span class="pre"><code class="sourceCode python">RequirementConstraintMembership</code></span></a>

  - <a href="/python/v0.8.4/syside/FramedConcernMembership.md" class="reference internal" title="syside.FramedConcernMembership"><span class="pre"><code class="sourceCode python">FramedConcernMembership</code></span></a>

  - <a href="/python/v0.8.4/syside/RequirementVerificationMembership.md" class="reference internal" title="syside.RequirementVerificationMembership"><span class="pre"><code class="sourceCode python">RequirementVerificationMembership</code></span></a>

- <a href="/python/v0.8.4/syside/ResultExpressionMembership.md" class="reference internal" title="syside.ResultExpressionMembership"><span class="pre"><code class="sourceCode python">ResultExpressionMembership</code></span></a>

- <a href="/python/v0.8.4/syside/StateSubactionMembership.md" class="reference internal" title="syside.StateSubactionMembership"><span class="pre"><code class="sourceCode python">StateSubactionMembership</code></span></a>

- <a href="/python/v0.8.4/syside/TransitionFeatureMembership.md" class="reference internal" title="syside.TransitionFeatureMembership"><span class="pre"><code class="sourceCode python">TransitionFeatureMembership</code></span></a>

- <a href="/python/v0.8.4/syside/ViewRenderingMembership.md" class="reference internal" title="syside.ViewRenderingMembership"><span class="pre"><code class="sourceCode python">ViewRenderingMembership</code></span></a>

</div>

<span class="sd-summary-text">Members defined in <a href="#syside.FeatureMembership" class="reference internal" title="syside.FeatureMembership"><span class="pre"><code class="sourceCode python">FeatureMembership</code></span></a> (3 members)</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |  |
|----|----|----|----|
| <span class="nerd-font"></span> | <a href="#syside.FeatureMembership.STD" class="reference internal" title="syside.FeatureMembership.STD"><span class="pre"><code class="sourceCode python">STD</code></span></a> | <span class="pre">`R`</span> |  |
| <span class="nerd-font"></span> | <a href="#syside.FeatureMembership.owned_member_feature" class="reference internal" title="syside.FeatureMembership.owned_member_feature"><span class="pre"><code class="sourceCode python">owned_member_feature</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_member_feature`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.FeatureMembership.owning_type" class="reference internal" title="syside.FeatureMembership.owning_type"><span class="pre"><code class="sourceCode python">owning_type</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owning_type`</span> defined in the KerML specification. |

</div>

</div>

<span class="sd-summary-text">Members inherited from <a href="/python/v0.8.4/syside/OwningMembership.md" class="reference internal" title="syside.OwningMembership"><span class="pre"><code class="sourceCode python">OwningMembership</code></span></a> (4 members)</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |  |
|----|----|----|----|
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/OwningMembership.md" class="reference internal" title="syside.OwningMembership.owned_member_element"><span class="pre"><code class="sourceCode python">owned_member_element</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_member_element`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/OwningMembership.md" class="reference internal" title="syside.OwningMembership.owned_member_element_id"><span class="pre"><code class="sourceCode python">owned_member_element_id</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_member_element_id`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/OwningMembership.md" class="reference internal" title="syside.OwningMembership.owned_member_name"><span class="pre"><code class="sourceCode python">owned_member_name</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_member_name`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/OwningMembership.md" class="reference internal" title="syside.OwningMembership.owned_member_short_name"><span class="pre"><code class="sourceCode python">owned_member_short_name</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_member_short_name`</span> defined in the KerML specification. |

</div>

</div>

<span class="sd-summary-text">Members inherited from <a href="/python/v0.8.4/syside/Membership.md" class="reference internal" title="syside.Membership"><span class="pre"><code class="sourceCode python">Membership</code></span></a> (10 members)</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |  |
|----|----|----|----|
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Membership.md" class="reference internal" title="syside.Membership.children"><span class="pre"><code class="sourceCode python">children</code></span></a> | <span class="pre">`R`</span> | The elements enclosed by curly brackets in textual syntax. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Membership.md" class="reference internal" title="syside.Membership.is_initial_node"><span class="pre"><code class="sourceCode python">is_initial_node</code></span></a> | <span class="pre">`RW`</span> | Returns <span class="pre">`True`</span> if this <span class="pre">`Membership`</span> was parsed from <span class="pre">`InitialNode`</span> syntax rule. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Membership.md" class="reference internal" title="syside.Membership.member_element"><span class="pre"><code class="sourceCode python">member_element</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`member_element`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Membership.md" class="reference internal" title="syside.Membership.member_element_id"><span class="pre"><code class="sourceCode python">member_element_id</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`member_element_id`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Membership.md" class="reference internal" title="syside.Membership.member_name"><span class="pre"><code class="sourceCode python">member_name</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`member_name`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Membership.md" class="reference internal" title="syside.Membership.member_short_name"><span class="pre"><code class="sourceCode python">member_short_name</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`member_short_name`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Membership.md" class="reference internal" title="syside.Membership.membership_owning_namespace"><span class="pre"><code class="sourceCode python">membership_owning_namespace</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`membership_owning_namespace`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Membership.md" class="reference internal" title="syside.Membership.owning_related_element"><span class="pre"><code class="sourceCode python">owning_related_element</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owning_related_element`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Membership.md" class="reference internal" title="syside.Membership.sources"><span class="pre"><code class="sourceCode python">sources</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`source`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Membership.md" class="reference internal" title="syside.Membership.targets"><span class="pre"><code class="sourceCode python">targets</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`target`</span> defined in the KerML specification. |

</div>

</div>

<span class="sd-summary-text">Members inherited from <a href="/python/v0.8.4/syside/Relationship.md" class="reference internal" title="syside.Relationship"><span class="pre"><code class="sourceCode python">Relationship</code></span></a> (9 members)</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |  |
|----|----|----|----|
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Relationship.md" class="reference internal" title="syside.Relationship.first_source"><span class="pre"><code class="sourceCode python">first_source</code></span></a> | <span class="pre">`R`</span> | Convenience method for sources\[0\]. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Relationship.md" class="reference internal" title="syside.Relationship.first_target"><span class="pre"><code class="sourceCode python">first_target</code></span></a> | <span class="pre">`R`</span> | Convenience method for targets\[0\]. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Relationship.md" class="reference internal" title="syside.Relationship.is_implied"><span class="pre"><code class="sourceCode python">is_implied</code></span></a> | <span class="pre">`RW`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`is_implied`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Relationship.md" class="reference internal" title="syside.Relationship.is_visibility_implied"><span class="pre"><code class="sourceCode python">is_visibility_implied</code></span></a> | <span class="pre">`R`</span> | Returns <span class="pre">`True`</span> if this <span class="pre">`Relationship`</span> is using implicit visibility. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Relationship.md" class="reference internal" title="syside.Relationship.owned_related_elements"><span class="pre"><code class="sourceCode python">owned_related_elements</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_related_element`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Relationship.md" class="reference internal" title="syside.Relationship.related_elements"><span class="pre"><code class="sourceCode python">related_elements</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`related_element`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Relationship.md" class="reference internal" title="syside.Relationship.visibility"><span class="pre"><code class="sourceCode python">visibility</code></span></a> | <span class="pre">`RW`</span> | The visibility level of the related elements from this <span class="pre">`Relationship`</span> relative to the <span class="pre">`owning_related_element`</span>. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Relationship.md" class="reference internal" title="syside.Relationship.reset_visibility"><span class="pre"><code class="sourceCode python">reset_visibility</code></span></a> |  | Reset visibility to its implicit value. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/Relationship.md" class="reference internal" title="syside.Relationship.try_set_visibility"><span class="pre"><code class="sourceCode python">try_set_visibility</code></span></a> |  | Non-throwing alternative to <span class="pre">`visibility`</span> setter. |

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

<span class="sig-name descname"><span class="pre">STD</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><span class="pre">type</span><span class="p"><span class="pre">\[</span></span><a href="#syside.FeatureMembership" class="reference internal" title="syside.FeatureMembership"><span class="pre">syside.FeatureMembership</span></a><span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="p"><span class="pre">...</span></span><span class="p"><span class="pre">\]</span></span><span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">()</span>*<a href="#syside.FeatureMembership.STD" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned_member_feature</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature"><span class="pre">syside.Feature</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span>*<a href="#syside.FeatureMembership.owned_member_feature" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owned_member_feature`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The <span class="pre">`Feature`</span> that this <span class="pre">`FeatureMembership`</span> relates to its <span class="pre">`owning_type`</span>, making it an <span class="pre">`owned_feature`</span> of the <span class="pre">`owning_type`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=168" class="reference external" target="_blank">8.3.3.1.6</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owning_type</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type"><span class="pre">syside.Type</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span>*<a href="#syside.FeatureMembership.owning_type" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owning_type`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The <span class="pre">`Type`</span> that owns this <span class="pre">`FeatureMembership`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=169" class="reference external" target="_blank">8.3.3.1.6</a> of the KerML specification for more details.

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature"><span class="pre"><code class="sourceCode python">syside.Feature</code></span></a>

  - <a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature.owning_feature_membership"><span class="pre"><code class="sourceCode python">owning_feature_membership</code></span></a>

- <a href="#syside.FeatureMembership" class="reference internal" title="syside.FeatureMembership"><span class="pre"><code class="sourceCode python">syside.FeatureMembership</code></span></a>

  - <a href="#syside.FeatureMembership.STD" class="reference internal" title="syside.FeatureMembership.STD"><span class="pre"><code class="sourceCode python">STD</code></span></a>

- <a href="/python/v0.8.4/syside/FlowDefinition.md" class="reference internal" title="syside.FlowDefinition"><span class="pre"><code class="sourceCode python">syside.FlowDefinition</code></span></a>

  - <a href="/python/v0.8.4/syside/FlowDefinition.md" class="reference internal" title="syside.FlowDefinition.flow_ends"><span class="pre"><code class="sourceCode python">flow_ends</code></span></a>

- <a href="/python/v0.8.4/syside/PayloadFeatureAccessor.md" class="reference internal" title="syside.PayloadFeatureAccessor"><span class="pre"><code class="sourceCode python">syside.PayloadFeatureAccessor</code></span></a>

  - <a href="/python/v0.8.4/syside/PayloadFeatureAccessor.md" class="reference internal" title="syside.PayloadFeatureAccessor.set_member_element"><span class="pre"><code class="sourceCode python">set_member_element</code></span></a>

- <a href="/python/v0.8.4/syside/ReferenceUsageAccessor.md" class="reference internal" title="syside.ReferenceUsageAccessor"><span class="pre"><code class="sourceCode python">syside.ReferenceUsageAccessor</code></span></a>

  - <a href="/python/v0.8.4/syside/ReferenceUsageAccessor.md" class="reference internal" title="syside.ReferenceUsageAccessor.set_member_element"><span class="pre"><code class="sourceCode python">set_member_element</code></span></a>

- <a href="/python/v0.8.4/syside/ReferentAccessor.md" class="reference internal" title="syside.ReferentAccessor"><span class="pre"><code class="sourceCode python">syside.ReferentAccessor</code></span></a>

  - <a href="/python/v0.8.4/syside/ReferentAccessor.md" class="reference internal" title="syside.ReferentAccessor.set_owned_expression"><span class="pre"><code class="sourceCode python">set_owned_expression</code></span></a>

- <a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type"><span class="pre"><code class="sourceCode python">syside.Type</code></span></a>

  - <a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type.feature_memberships"><span class="pre"><code class="sourceCode python">feature_memberships</code></span></a>

  - <a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type.owned_feature_memberships"><span class="pre"><code class="sourceCode python">owned_feature_memberships</code></span></a>

</div>

</div>
