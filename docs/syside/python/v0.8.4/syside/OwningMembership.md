<div id="owningmembership-sysml" class="section">

# OwningMembership <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span><a href="#owningmembership-sysml" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">OwningMembership</span></span><a href="#syside.OwningMembership" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`OwningMembership`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> An <span class="pre">`OwningMembership`</span> is a <span class="pre">`Membership`</span> that owns its <span class="pre">`member_element`</span> as a <span class="pre">`owned_related_element`</span>. The <span class="pre">`owned_member_element`</span> becomes an <span class="pre">`owned_member`</span> of the <span class="pre">`membership_owning_namespace`</span>.
>
> </div>

For language description, see section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=46" class="reference external" target="_blank">7.2.5</a> of the KerML specification. For more details on the model, see section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=161" class="reference external" target="_blank">8.3.2.4.8</a> of the KerML specification.

<div class="align-center" align="center">

<img src="data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iZ3JhcGh2aXoiIHN0eWxlPSJ3aWR0aDogOC43NXJlbTtoZWlnaHQ6IDIwLjc1cmVtOyIgdmlld2JveD0iMC4wMCAwLjAwIDE0MC4wMCAzMzIuMDAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxnIGNsYXNzPSJncmFwaCIgaWQ9ImdyYXBoMCIgdHJhbnNmb3JtPSJzY2FsZSgxIDEpIHJvdGF0ZSgwKSB0cmFuc2xhdGUoNCAzMjgpIj4KPHRpdGxlPiUzPC90aXRsZT4KPGcgY2xhc3M9Im5vZGUiIGlkPSJub2RlMSI+Cjx0aXRsZT5Pd25pbmdNZW1iZXJzaGlwPC90aXRsZT4KPGcgaWQ9ImFfbm9kZTEiPjxhIGhyZWY9IiNzeXNpZGUuT3duaW5nTWVtYmVyc2hpcCI+Cjxwb2x5Z29uIHBvaW50cz0iMTMyLC0zNiAwLC0zNiAwLDAgMTMyLDAgMTMyLC0zNiIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtYmctY29sb3IpO3N0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1mZy1jb2xvcik7Ij48L3BvbHlnb24+Cjx0ZXh0IGZvbnQtZmFtaWx5PSJMZXhlbmQiIGZvbnQtc2l6ZT0iMTIuMDAiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1jb2RlLWZnLWNvbG9yKTstLW1kLWdyYXBodml6LWhvdmVyLWNvbG9yOiB2YXIoLS1tZC1ncmFwaHZpei1hLWhvdmVyLWNvbG9yKTsiIHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjY2IiB5PSItMTQuMiI+T3duaW5nTWVtYmVyc2hpcDwvdGV4dD4KPHRpdGxlPnN5c2lkZS5Pd25pbmdNZW1iZXJzaGlwPC90aXRsZT48L2E+CjwvZz4KPC9nPgo8ZyBjbGFzcz0ibm9kZSIgaWQ9Im5vZGUyIj4KPHRpdGxlPk1lbWJlcnNoaXA8L3RpdGxlPgo8ZyBpZD0iYV9ub2RlMiI+PGEgaHJlZj0iL3B5dGhvbi92MC44LjQvc3lzaWRlL01lbWJlcnNoaXAubWQiPgo8cG9seWdvbiBwb2ludHM9IjEwOS41LC0xMDggMjIuNSwtMTA4IDIyLjUsLTcyIDEwOS41LC03MiAxMDkuNSwtMTA4IiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1iZy1jb2xvcik7c3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1ub2RlLWZnLWNvbG9yKTsiPjwvcG9seWdvbj4KPHRleHQgZm9udC1mYW1pbHk9IkxleGVuZCIgZm9udC1zaXplPSIxMi4wMCIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWNvZGUtZmctY29sb3IpOy0tbWQtZ3JhcGh2aXotaG92ZXItY29sb3I6IHZhcigtLW1kLWdyYXBodml6LWEtaG92ZXItY29sb3IpOyIgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iNjYiIHk9Ii04Ni4yIj5NZW1iZXJzaGlwPC90ZXh0Pgo8dGl0bGU+c3lzaWRlLk1lbWJlcnNoaXA8L3RpdGxlPjwvYT4KPC9nPgo8L2c+CjxnIGNsYXNzPSJlZGdlIiBpZD0iZWRnZTEiPgo8dGl0bGU+TWVtYmVyc2hpcC0mZ3Q7T3duaW5nTWVtYmVyc2hpcDwvdGl0bGU+CjxwYXRoIGQ9Ik02NiwtNzEuN0M2NiwtNjMuOTggNjYsLTU0LjcxIDY2LC00Ni4xMSIgZmlsbD0ibm9uZSIgc3R5bGU9InN0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotZWRnZS1jb2xvcik7IiAvPgo8cG9seWdvbiBwb2ludHM9IjY5LjUsLTQ2LjEgNjYsLTM2LjEgNjIuNSwtNDYuMSA2OS41LC00Ni4xIiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtZ3JhcGh2aXotZWRnZS1jb2xvcik7c3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1lZGdlLWNvbG9yKTsiPjwvcG9seWdvbj4KPC9nPgo8ZyBjbGFzcz0ibm9kZSIgaWQ9Im5vZGUzIj4KPHRpdGxlPlJlbGF0aW9uc2hpcDwvdGl0bGU+CjxnIGlkPSJhX25vZGUzIj48YSBocmVmPSIvcHl0aG9uL3YwLjguNC9zeXNpZGUvUmVsYXRpb25zaGlwLm1kIj4KPHBvbHlnb24gcG9pbnRzPSIxMDkuNSwtMTgwIDIyLjUsLTE4MCAyMi41LC0xNDQgMTA5LjUsLTE0NCAxMDkuNSwtMTgwIiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1iZy1jb2xvcik7c3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1ub2RlLWZnLWNvbG9yKTsiPjwvcG9seWdvbj4KPHRleHQgZm9udC1mYW1pbHk9IkxleGVuZCIgZm9udC1zaXplPSIxMi4wMCIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWNvZGUtZmctY29sb3IpOy0tbWQtZ3JhcGh2aXotaG92ZXItY29sb3I6IHZhcigtLW1kLWdyYXBodml6LWEtaG92ZXItY29sb3IpOyIgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iNjYiIHk9Ii0xNTguMiI+UmVsYXRpb25zaGlwPC90ZXh0Pgo8dGl0bGU+c3lzaWRlLlJlbGF0aW9uc2hpcDwvdGl0bGU+PC9hPgo8L2c+CjwvZz4KPGcgY2xhc3M9ImVkZ2UiIGlkPSJlZGdlMiI+Cjx0aXRsZT5SZWxhdGlvbnNoaXAtJmd0O01lbWJlcnNoaXA8L3RpdGxlPgo8cGF0aCBkPSJNNjYsLTE0My43QzY2LC0xMzUuOTggNjYsLTEyNi43MSA2NiwtMTE4LjExIiBmaWxsPSJub25lIiBzdHlsZT0ic3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1lZGdlLWNvbG9yKTsiIC8+Cjxwb2x5Z29uIHBvaW50cz0iNjkuNSwtMTE4LjEgNjYsLTEwOC4xIDYyLjUsLTExOC4xIDY5LjUsLTExOC4xIiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtZ3JhcGh2aXotZWRnZS1jb2xvcik7c3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1lZGdlLWNvbG9yKTsiPjwvcG9seWdvbj4KPC9nPgo8ZyBjbGFzcz0ibm9kZSIgaWQ9Im5vZGU0Ij4KPHRpdGxlPkVsZW1lbnQ8L3RpdGxlPgo8ZyBpZD0iYV9ub2RlNCI+PGEgaHJlZj0iL3B5dGhvbi92MC44LjQvc3lzaWRlL0VsZW1lbnQubWQiPgo8cG9seWdvbiBwb2ludHM9Ijk3LC0yNTIgMzUsLTI1MiAzNSwtMjE2IDk3LC0yMTYgOTcsLTI1MiIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtYmctY29sb3IpO3N0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1mZy1jb2xvcik7Ij48L3BvbHlnb24+Cjx0ZXh0IGZvbnQtZmFtaWx5PSJMZXhlbmQiIGZvbnQtc2l6ZT0iMTIuMDAiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1jb2RlLWZnLWNvbG9yKTstLW1kLWdyYXBodml6LWhvdmVyLWNvbG9yOiB2YXIoLS1tZC1ncmFwaHZpei1hLWhvdmVyLWNvbG9yKTsiIHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjY2IiB5PSItMjMwLjIiPkVsZW1lbnQ8L3RleHQ+Cjx0aXRsZT5zeXNpZGUuRWxlbWVudDwvdGl0bGU+PC9hPgo8L2c+CjwvZz4KPGcgY2xhc3M9ImVkZ2UiIGlkPSJlZGdlMyI+Cjx0aXRsZT5FbGVtZW50LSZndDtSZWxhdGlvbnNoaXA8L3RpdGxlPgo8cGF0aCBkPSJNNjYsLTIxNS43QzY2LC0yMDcuOTggNjYsLTE5OC43MSA2NiwtMTkwLjExIiBmaWxsPSJub25lIiBzdHlsZT0ic3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1lZGdlLWNvbG9yKTsiIC8+Cjxwb2x5Z29uIHBvaW50cz0iNjkuNSwtMTkwLjEgNjYsLTE4MC4xIDYyLjUsLTE5MC4xIDY5LjUsLTE5MC4xIiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtZ3JhcGh2aXotZWRnZS1jb2xvcik7c3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1lZGdlLWNvbG9yKTsiPjwvcG9seWdvbj4KPC9nPgo8ZyBjbGFzcz0ibm9kZSIgaWQ9Im5vZGU1Ij4KPHRpdGxlPkFzdE5vZGU8L3RpdGxlPgo8ZyBpZD0iYV9ub2RlNSI+PGEgaHJlZj0iL3B5dGhvbi92MC44LjQvc3lzaWRlL0FzdE5vZGUubWQiPgo8cG9seWdvbiBwb2ludHM9Ijk5LC0zMjQgMzMsLTMyNCAzMywtMjg4IDk5LC0yODggOTksLTMyNCIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtYmctY29sb3IpO3N0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1mZy1jb2xvcik7Ij48L3BvbHlnb24+Cjx0ZXh0IGZvbnQtZmFtaWx5PSJMZXhlbmQiIGZvbnQtc2l6ZT0iMTIuMDAiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1jb2RlLWZnLWNvbG9yKTstLW1kLWdyYXBodml6LWhvdmVyLWNvbG9yOiB2YXIoLS1tZC1ncmFwaHZpei1hLWhvdmVyLWNvbG9yKTsiIHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjY2IiB5PSItMzAyLjIiPkFzdE5vZGU8L3RleHQ+Cjx0aXRsZT5zeXNpZGUuQXN0Tm9kZTwvdGl0bGU+PC9hPgo8L2c+CjwvZz4KPGcgY2xhc3M9ImVkZ2UiIGlkPSJlZGdlNCI+Cjx0aXRsZT5Bc3ROb2RlLSZndDtFbGVtZW50PC90aXRsZT4KPHBhdGggZD0iTTY2LC0yODcuN0M2NiwtMjc5Ljk4IDY2LC0yNzAuNzEgNjYsLTI2Mi4xMSIgZmlsbD0ibm9uZSIgc3R5bGU9InN0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotZWRnZS1jb2xvcik7IiAvPgo8cG9seWdvbiBwb2ludHM9IjY5LjUsLTI2Mi4xIDY2LC0yNTIuMSA2Mi41LC0yNjIuMSA2OS41LC0yNjIuMSIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWdyYXBodml6LWVkZ2UtY29sb3IpO3N0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotZWRnZS1jb2xvcik7Ij48L3BvbHlnb24+CjwvZz4KPC9nPgo8L3N2Zz4=" class="graphviz" />

</div>

<span class="sd-summary-text"><span class="nerd-font"></span> Children</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/ElementFilterMembership.md" class="reference internal" title="syside.ElementFilterMembership"><span class="pre"><code class="sourceCode python">ElementFilterMembership</code></span></a>

- <a href="/python/v0.8.4/syside/FeatureMembership.md" class="reference internal" title="syside.FeatureMembership"><span class="pre"><code class="sourceCode python">FeatureMembership</code></span></a>

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

- <a href="/python/v0.8.4/syside/FeatureValue.md" class="reference internal" title="syside.FeatureValue"><span class="pre"><code class="sourceCode python">FeatureValue</code></span></a>

- <a href="/python/v0.8.4/syside/VariantMembership.md" class="reference internal" title="syside.VariantMembership"><span class="pre"><code class="sourceCode python">VariantMembership</code></span></a>

</div>

<span class="sd-summary-text">Members defined in <a href="#syside.OwningMembership" class="reference internal" title="syside.OwningMembership"><span class="pre"><code class="sourceCode python">OwningMembership</code></span></a> (5 members)</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |  |
|----|----|----|----|
| <span class="nerd-font"></span> | <a href="#syside.OwningMembership.STD" class="reference internal" title="syside.OwningMembership.STD"><span class="pre"><code class="sourceCode python">STD</code></span></a> | <span class="pre">`R`</span> |  |
| <span class="nerd-font"></span> | <a href="#syside.OwningMembership.owned_member_element" class="reference internal" title="syside.OwningMembership.owned_member_element"><span class="pre"><code class="sourceCode python">owned_member_element</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_member_element`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.OwningMembership.owned_member_element_id" class="reference internal" title="syside.OwningMembership.owned_member_element_id"><span class="pre"><code class="sourceCode python">owned_member_element_id</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_member_element_id`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.OwningMembership.owned_member_name" class="reference internal" title="syside.OwningMembership.owned_member_name"><span class="pre"><code class="sourceCode python">owned_member_name</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_member_name`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.OwningMembership.owned_member_short_name" class="reference internal" title="syside.OwningMembership.owned_member_short_name"><span class="pre"><code class="sourceCode python">owned_member_short_name</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_member_short_name`</span> defined in the KerML specification. |

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

<span class="sig-name descname"><span class="pre">STD</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><span class="pre">type</span><span class="p"><span class="pre">\[</span></span><a href="#syside.OwningMembership" class="reference internal" title="syside.OwningMembership"><span class="pre">syside.OwningMembership</span></a><span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="p"><span class="pre">...</span></span><span class="p"><span class="pre">\]</span></span><span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">()</span>*<a href="#syside.OwningMembership.STD" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned_member_element</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element"><span class="pre">syside.Element</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span>*<a href="#syside.OwningMembership.owned_member_element" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owned_member_element`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The <span class="pre">`Element`</span> that becomes an <span class="pre">`owned_member`</span> of the <span class="pre">`membership_owning_namespace`</span> due to this <span class="pre">`OwningMembership`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=161" class="reference external" target="_blank">8.3.2.4.8</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned_member_element_id</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">uuid.UUID</span>*<a href="#syside.OwningMembership.owned_member_element_id" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owned_member_element_id`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The <span class="pre">`element_id`</span> of the <span class="pre">`owned_member_element`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=162" class="reference external" target="_blank">8.3.2.4.8</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned_member_name</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span>*<a href="#syside.OwningMembership.owned_member_name" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owned_member_name`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The <span class="pre">`name`</span> of the <span class="pre">`owned_member_element`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=162" class="reference external" target="_blank">8.3.2.4.8</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned_member_short_name</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span>*<a href="#syside.OwningMembership.owned_member_short_name" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owned_member_short_name`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The <span class="pre">`short_name`</span> of the <span class="pre">`owned_member_element`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=162" class="reference external" target="_blank">8.3.2.4.8</a> of the KerML specification for more details.

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/ChainedMemberAccessor.md" class="reference internal" title="syside.ChainedMemberAccessor"><span class="pre"><code class="sourceCode python">syside.ChainedMemberAccessor</code></span></a>

  - <a href="/python/v0.8.4/syside/ChainedMemberAccessor.md" class="reference internal" title="syside.ChainedMemberAccessor.set_member_element_chain"><span class="pre"><code class="sourceCode python">set_member_element_chain</code></span></a>

- <a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element"><span class="pre"><code class="sourceCode python">syside.Element</code></span></a>

  - <a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element.owning_membership"><span class="pre"><code class="sourceCode python">owning_membership</code></span></a>

- <a href="/python/v0.8.4/syside/OwnedExpressionAccessor.md" class="reference internal" title="syside.OwnedExpressionAccessor"><span class="pre"><code class="sourceCode python">syside.OwnedExpressionAccessor</code></span></a>

  - <a href="/python/v0.8.4/syside/OwnedExpressionAccessor.md" class="reference internal" title="syside.OwnedExpressionAccessor.set_member_element"><span class="pre"><code class="sourceCode python">set_member_element</code></span></a>

- <a href="/python/v0.8.4/syside/OwnedFeatureAccessor.md" class="reference internal" title="syside.OwnedFeatureAccessor"><span class="pre"><code class="sourceCode python">syside.OwnedFeatureAccessor</code></span></a>

  - <a href="/python/v0.8.4/syside/OwnedFeatureAccessor.md" class="reference internal" title="syside.OwnedFeatureAccessor.set_member_element"><span class="pre"><code class="sourceCode python">set_member_element</code></span></a>

- <a href="/python/v0.8.4/syside/OwnedMultiplicityAccessor.md" class="reference internal" title="syside.OwnedMultiplicityAccessor"><span class="pre"><code class="sourceCode python">syside.OwnedMultiplicityAccessor</code></span></a>

  - <a href="/python/v0.8.4/syside/OwnedMultiplicityAccessor.md" class="reference internal" title="syside.OwnedMultiplicityAccessor.set_member_element"><span class="pre"><code class="sourceCode python">set_member_element</code></span></a>

- <a href="/python/v0.8.4/syside/OwnedSuccessionAccessor.md" class="reference internal" title="syside.OwnedSuccessionAccessor"><span class="pre"><code class="sourceCode python">syside.OwnedSuccessionAccessor</code></span></a>

  - <a href="/python/v0.8.4/syside/OwnedSuccessionAccessor.md" class="reference internal" title="syside.OwnedSuccessionAccessor.set_member_element"><span class="pre"><code class="sourceCode python">set_member_element</code></span></a>

- <a href="#syside.OwningMembership" class="reference internal" title="syside.OwningMembership"><span class="pre"><code class="sourceCode python">syside.OwningMembership</code></span></a>

  - <a href="#syside.OwningMembership.STD" class="reference internal" title="syside.OwningMembership.STD"><span class="pre"><code class="sourceCode python">STD</code></span></a>

- <a href="/python/v0.8.4/syside/SatisfactionSubjectAccessor.md" class="reference internal" title="syside.SatisfactionSubjectAccessor"><span class="pre"><code class="sourceCode python">syside.SatisfactionSubjectAccessor</code></span></a>

  - <a href="/python/v0.8.4/syside/SatisfactionSubjectAccessor.md" class="reference internal" title="syside.SatisfactionSubjectAccessor.set_target_chain"><span class="pre"><code class="sourceCode python">set_target_chain</code></span></a>

</div>

</div>
