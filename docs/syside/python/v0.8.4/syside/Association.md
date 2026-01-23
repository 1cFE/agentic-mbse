<div id="association-sysml" class="section">

# Association <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span><a href="#association-sysml" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">Association</span></span><a href="#syside.Association" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`Association`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> An <span class="pre">`Association`</span> is a <span class="pre">`Relationship`</span> and a <span class="pre">`Classifier`</span> to enable classification of links between things (in the universe). The co-domains (<span class="pre">`types`</span>) of the <span class="pre">`association_end`</span> <span class="pre">`Features`</span> are the <span class="pre">`related_types`</span>, as co-domain and participants (linked things) of an <span class="pre">`Association`</span> identify each other.
>
> </div>

For language description, see section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=69" class="reference external" target="_blank">7.4.5</a> of the KerML specification. For more details on the model, see section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=211" class="reference external" target="_blank">8.3.4.4.2</a> of the KerML specification.

<div class="align-center" align="center">

<img src="data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iZ3JhcGh2aXoiIHN0eWxlPSJ3aWR0aDogNS43NXJlbTtoZWlnaHQ6IDI1LjI1cmVtOyIgdmlld2JveD0iMC4wMCAwLjAwIDkyLjAwIDQwNC4wMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGcgY2xhc3M9ImdyYXBoIiBpZD0iZ3JhcGgwIiB0cmFuc2Zvcm09InNjYWxlKDEgMSkgcm90YXRlKDApIHRyYW5zbGF0ZSg0IDQwMCkiPgo8dGl0bGU+JTM8L3RpdGxlPgo8ZyBjbGFzcz0ibm9kZSIgaWQ9Im5vZGUxIj4KPHRpdGxlPkFzc29jaWF0aW9uPC90aXRsZT4KPGcgaWQ9ImFfbm9kZTEiPjxhIGhyZWY9IiNzeXNpZGUuQXNzb2NpYXRpb24iPgo8cG9seWdvbiBwb2ludHM9IjgzLjUsLTM2IDAuNSwtMzYgMC41LDAgODMuNSwwIDgzLjUsLTM2IiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1iZy1jb2xvcik7c3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1ub2RlLWZnLWNvbG9yKTsiPjwvcG9seWdvbj4KPHRleHQgZm9udC1mYW1pbHk9IkxleGVuZCIgZm9udC1zaXplPSIxMi4wMCIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWNvZGUtZmctY29sb3IpOy0tbWQtZ3JhcGh2aXotaG92ZXItY29sb3I6IHZhcigtLW1kLWdyYXBodml6LWEtaG92ZXItY29sb3IpOyIgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iNDIiIHk9Ii0xNC4yIj5Bc3NvY2lhdGlvbjwvdGV4dD4KPHRpdGxlPnN5c2lkZS5Bc3NvY2lhdGlvbjwvdGl0bGU+PC9hPgo8L2c+CjwvZz4KPGcgY2xhc3M9Im5vZGUiIGlkPSJub2RlMiI+Cjx0aXRsZT5DbGFzc2lmaWVyPC90aXRsZT4KPGcgaWQ9ImFfbm9kZTIiPjxhIGhyZWY9Ii9weXRob24vdjAuOC40L3N5c2lkZS9DbGFzc2lmaWVyLm1kIj4KPHBvbHlnb24gcG9pbnRzPSI3Ni41LC0xMDggNy41LC0xMDggNy41LC03MiA3Ni41LC03MiA3Ni41LC0xMDgiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1ncmFwaHZpei1ub2RlLWJnLWNvbG9yKTtzdHJva2U6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtZmctY29sb3IpOyI+PC9wb2x5Z29uPgo8dGV4dCBmb250LWZhbWlseT0iTGV4ZW5kIiBmb250LXNpemU9IjEyLjAwIiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtY29kZS1mZy1jb2xvcik7LS1tZC1ncmFwaHZpei1ob3Zlci1jb2xvcjogdmFyKC0tbWQtZ3JhcGh2aXotYS1ob3Zlci1jb2xvcik7IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSI0MiIgeT0iLTg2LjIiPkNsYXNzaWZpZXI8L3RleHQ+Cjx0aXRsZT5zeXNpZGUuQ2xhc3NpZmllcjwvdGl0bGU+PC9hPgo8L2c+CjwvZz4KPGcgY2xhc3M9ImVkZ2UiIGlkPSJlZGdlMSI+Cjx0aXRsZT5DbGFzc2lmaWVyLSZndDtBc3NvY2lhdGlvbjwvdGl0bGU+CjxwYXRoIGQ9Ik00MiwtNzEuN0M0MiwtNjMuOTggNDIsLTU0LjcxIDQyLC00Ni4xMSIgZmlsbD0ibm9uZSIgc3R5bGU9InN0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotZWRnZS1jb2xvcik7IiAvPgo8cG9seWdvbiBwb2ludHM9IjQ1LjUsLTQ2LjEgNDIsLTM2LjEgMzguNSwtNDYuMSA0NS41LC00Ni4xIiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtZ3JhcGh2aXotZWRnZS1jb2xvcik7c3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1lZGdlLWNvbG9yKTsiPjwvcG9seWdvbj4KPC9nPgo8ZyBjbGFzcz0ibm9kZSIgaWQ9Im5vZGUzIj4KPHRpdGxlPlR5cGU8L3RpdGxlPgo8ZyBpZD0iYV9ub2RlMyI+PGEgaHJlZj0iL3B5dGhvbi92MC44LjQvc3lzaWRlL1R5cGUubWQiPgo8cG9seWdvbiBwb2ludHM9IjY5LC0xODAgMTUsLTE4MCAxNSwtMTQ0IDY5LC0xNDQgNjksLTE4MCIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtYmctY29sb3IpO3N0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1mZy1jb2xvcik7Ij48L3BvbHlnb24+Cjx0ZXh0IGZvbnQtZmFtaWx5PSJMZXhlbmQiIGZvbnQtc2l6ZT0iMTIuMDAiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1jb2RlLWZnLWNvbG9yKTstLW1kLWdyYXBodml6LWhvdmVyLWNvbG9yOiB2YXIoLS1tZC1ncmFwaHZpei1hLWhvdmVyLWNvbG9yKTsiIHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjQyIiB5PSItMTU4LjIiPlR5cGU8L3RleHQ+Cjx0aXRsZT5zeXNpZGUuVHlwZTwvdGl0bGU+PC9hPgo8L2c+CjwvZz4KPGcgY2xhc3M9ImVkZ2UiIGlkPSJlZGdlMiI+Cjx0aXRsZT5UeXBlLSZndDtDbGFzc2lmaWVyPC90aXRsZT4KPHBhdGggZD0iTTQyLC0xNDMuN0M0MiwtMTM1Ljk4IDQyLC0xMjYuNzEgNDIsLTExOC4xMSIgZmlsbD0ibm9uZSIgc3R5bGU9InN0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotZWRnZS1jb2xvcik7IiAvPgo8cG9seWdvbiBwb2ludHM9IjQ1LjUsLTExOC4xIDQyLC0xMDguMSAzOC41LC0xMTguMSA0NS41LC0xMTguMSIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWdyYXBodml6LWVkZ2UtY29sb3IpO3N0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotZWRnZS1jb2xvcik7Ij48L3BvbHlnb24+CjwvZz4KPGcgY2xhc3M9Im5vZGUiIGlkPSJub2RlNCI+Cjx0aXRsZT5OYW1lc3BhY2U8L3RpdGxlPgo8ZyBpZD0iYV9ub2RlNCI+PGEgaHJlZj0iL3B5dGhvbi92MC44LjQvc3lzaWRlL05hbWVzcGFjZS5tZCI+Cjxwb2x5Z29uIHBvaW50cz0iODQsLTI1MiAwLC0yNTIgMCwtMjE2IDg0LC0yMTYgODQsLTI1MiIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtYmctY29sb3IpO3N0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1mZy1jb2xvcik7Ij48L3BvbHlnb24+Cjx0ZXh0IGZvbnQtZmFtaWx5PSJMZXhlbmQiIGZvbnQtc2l6ZT0iMTIuMDAiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1jb2RlLWZnLWNvbG9yKTstLW1kLWdyYXBodml6LWhvdmVyLWNvbG9yOiB2YXIoLS1tZC1ncmFwaHZpei1hLWhvdmVyLWNvbG9yKTsiIHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjQyIiB5PSItMjMwLjIiPk5hbWVzcGFjZTwvdGV4dD4KPHRpdGxlPnN5c2lkZS5OYW1lc3BhY2U8L3RpdGxlPjwvYT4KPC9nPgo8L2c+CjxnIGNsYXNzPSJlZGdlIiBpZD0iZWRnZTMiPgo8dGl0bGU+TmFtZXNwYWNlLSZndDtUeXBlPC90aXRsZT4KPHBhdGggZD0iTTQyLC0yMTUuN0M0MiwtMjA3Ljk4IDQyLC0xOTguNzEgNDIsLTE5MC4xMSIgZmlsbD0ibm9uZSIgc3R5bGU9InN0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotZWRnZS1jb2xvcik7IiAvPgo8cG9seWdvbiBwb2ludHM9IjQ1LjUsLTE5MC4xIDQyLC0xODAuMSAzOC41LC0xOTAuMSA0NS41LC0xOTAuMSIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWdyYXBodml6LWVkZ2UtY29sb3IpO3N0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotZWRnZS1jb2xvcik7Ij48L3BvbHlnb24+CjwvZz4KPGcgY2xhc3M9Im5vZGUiIGlkPSJub2RlNSI+Cjx0aXRsZT5FbGVtZW50PC90aXRsZT4KPGcgaWQ9ImFfbm9kZTUiPjxhIGhyZWY9Ii9weXRob24vdjAuOC40L3N5c2lkZS9FbGVtZW50Lm1kIj4KPHBvbHlnb24gcG9pbnRzPSI3MywtMzI0IDExLC0zMjQgMTEsLTI4OCA3MywtMjg4IDczLC0zMjQiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1ncmFwaHZpei1ub2RlLWJnLWNvbG9yKTtzdHJva2U6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtZmctY29sb3IpOyI+PC9wb2x5Z29uPgo8dGV4dCBmb250LWZhbWlseT0iTGV4ZW5kIiBmb250LXNpemU9IjEyLjAwIiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtY29kZS1mZy1jb2xvcik7LS1tZC1ncmFwaHZpei1ob3Zlci1jb2xvcjogdmFyKC0tbWQtZ3JhcGh2aXotYS1ob3Zlci1jb2xvcik7IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSI0MiIgeT0iLTMwMi4yIj5FbGVtZW50PC90ZXh0Pgo8dGl0bGU+c3lzaWRlLkVsZW1lbnQ8L3RpdGxlPjwvYT4KPC9nPgo8L2c+CjxnIGNsYXNzPSJlZGdlIiBpZD0iZWRnZTQiPgo8dGl0bGU+RWxlbWVudC0mZ3Q7TmFtZXNwYWNlPC90aXRsZT4KPHBhdGggZD0iTTQyLC0yODcuN0M0MiwtMjc5Ljk4IDQyLC0yNzAuNzEgNDIsLTI2Mi4xMSIgZmlsbD0ibm9uZSIgc3R5bGU9InN0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotZWRnZS1jb2xvcik7IiAvPgo8cG9seWdvbiBwb2ludHM9IjQ1LjUsLTI2Mi4xIDQyLC0yNTIuMSAzOC41LC0yNjIuMSA0NS41LC0yNjIuMSIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWdyYXBodml6LWVkZ2UtY29sb3IpO3N0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotZWRnZS1jb2xvcik7Ij48L3BvbHlnb24+CjwvZz4KPGcgY2xhc3M9Im5vZGUiIGlkPSJub2RlNiI+Cjx0aXRsZT5Bc3ROb2RlPC90aXRsZT4KPGcgaWQ9ImFfbm9kZTYiPjxhIGhyZWY9Ii9weXRob24vdjAuOC40L3N5c2lkZS9Bc3ROb2RlLm1kIj4KPHBvbHlnb24gcG9pbnRzPSI3NSwtMzk2IDksLTM5NiA5LC0zNjAgNzUsLTM2MCA3NSwtMzk2IiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1iZy1jb2xvcik7c3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1ub2RlLWZnLWNvbG9yKTsiPjwvcG9seWdvbj4KPHRleHQgZm9udC1mYW1pbHk9IkxleGVuZCIgZm9udC1zaXplPSIxMi4wMCIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWNvZGUtZmctY29sb3IpOy0tbWQtZ3JhcGh2aXotaG92ZXItY29sb3I6IHZhcigtLW1kLWdyYXBodml6LWEtaG92ZXItY29sb3IpOyIgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iNDIiIHk9Ii0zNzQuMiI+QXN0Tm9kZTwvdGV4dD4KPHRpdGxlPnN5c2lkZS5Bc3ROb2RlPC90aXRsZT48L2E+CjwvZz4KPC9nPgo8ZyBjbGFzcz0iZWRnZSIgaWQ9ImVkZ2U1Ij4KPHRpdGxlPkFzdE5vZGUtJmd0O0VsZW1lbnQ8L3RpdGxlPgo8cGF0aCBkPSJNNDIsLTM1OS43QzQyLC0zNTEuOTggNDIsLTM0Mi43MSA0MiwtMzM0LjExIiBmaWxsPSJub25lIiBzdHlsZT0ic3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1lZGdlLWNvbG9yKTsiIC8+Cjxwb2x5Z29uIHBvaW50cz0iNDUuNSwtMzM0LjEgNDIsLTMyNC4xIDM4LjUsLTMzNC4xIDQ1LjUsLTMzNC4xIiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtZ3JhcGh2aXotZWRnZS1jb2xvcik7c3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1lZGdlLWNvbG9yKTsiPjwvcG9seWdvbj4KPC9nPgo8L2c+Cjwvc3ZnPg==" class="graphviz" />

</div>

<span class="sd-summary-text"><span class="nerd-font"></span> Children</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/AssociationStructure.md" class="reference internal" title="syside.AssociationStructure"><span class="pre"><code class="sourceCode python">AssociationStructure</code></span></a>

- <a href="/python/v0.8.4/syside/Interaction.md" class="reference internal" title="syside.Interaction"><span class="pre"><code class="sourceCode python">Interaction</code></span></a>

</div>

<span class="sd-summary-text">Members defined in <a href="#syside.Association" class="reference internal" title="syside.Association"><span class="pre"><code class="sourceCode python">Association</code></span></a> (12 members)</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |  |
|----|----|----|----|
| <span class="nerd-font"></span> | <a href="#syside.Association.STD" class="reference internal" title="syside.Association.STD"><span class="pre"><code class="sourceCode python">STD</code></span></a> | <span class="pre">`R`</span> |  |
| <span class="nerd-font"></span> | <a href="#syside.Association.association_ends" class="reference internal" title="syside.Association.association_ends"><span class="pre"><code class="sourceCode python">association_ends</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`association_end`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Association.is_implied" class="reference internal" title="syside.Association.is_implied"><span class="pre"><code class="sourceCode python">is_implied</code></span></a> | <span class="pre">`RW`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`is_implied`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Association.owned_related_elements" class="reference internal" title="syside.Association.owned_related_elements"><span class="pre"><code class="sourceCode python">owned_related_elements</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_related_element`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Association.owning_related_element" class="reference internal" title="syside.Association.owning_related_element"><span class="pre"><code class="sourceCode python">owning_related_element</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owning_related_element`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Association.related_elements" class="reference internal" title="syside.Association.related_elements"><span class="pre"><code class="sourceCode python">related_elements</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`related_element`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Association.related_types" class="reference internal" title="syside.Association.related_types"><span class="pre"><code class="sourceCode python">related_types</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`related_type`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Association.source" class="reference internal" title="syside.Association.source"><span class="pre"><code class="sourceCode python">source</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`source`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Association.source_type" class="reference internal" title="syside.Association.source_type"><span class="pre"><code class="sourceCode python">source_type</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`source_type`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Association.sources" class="reference internal" title="syside.Association.sources"><span class="pre"><code class="sourceCode python">sources</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`source`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Association.target_types" class="reference internal" title="syside.Association.target_types"><span class="pre"><code class="sourceCode python">target_types</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`target_type`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Association.targets" class="reference internal" title="syside.Association.targets"><span class="pre"><code class="sourceCode python">targets</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`target`</span> defined in the KerML specification. |

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

<span class="sig-name descname"><span class="pre">STD</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><span class="pre">Union</span><span class="p"><span class="pre">\[</span></span><span class="pre">type</span><span class="p"><span class="pre">\[</span></span><a href="#syside.Association" class="reference internal" title="syside.Association"><span class="pre">syside.Association</span></a><span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">type</span><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/ConnectionDefinition.md" class="reference internal" title="syside.ConnectionDefinition"><span class="pre">ConnectionDefinition</span></a><span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">type</span><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/FlowDefinition.md" class="reference internal" title="syside.FlowDefinition"><span class="pre">FlowDefinition</span></a><span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="p"><span class="pre">...</span></span><span class="p"><span class="pre">\]</span></span><span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">()</span>*<a href="#syside.Association.STD" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">association_ends</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature"><span class="pre">syside.Feature</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Association.association_ends" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`association_end`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The <span class="pre">`features`</span> of the <span class="pre">`Association`</span> that identify the things that can be related by it. A concrete <span class="pre">`Association`</span> must have at least two <span class="pre">`association_ends`</span>. When it has exactly two, the <span class="pre">`Association`</span> is called a *binary* <span class="pre">`Association`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=211" class="reference external" target="_blank">8.3.4.4.2</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">is_implied</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*<a href="#syside.Association.is_implied" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`is_implied`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> Whether this Relationship was generated by tooling to meet semantic rules, rather than being directly created by a modeler.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=143" class="reference external" target="_blank">8.3.2.1.3</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned_related_elements</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature"><span class="pre">syside.Feature</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Association.owned_related_elements" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owned_related_element`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The related_elements of this Relationship that are owned by the Relationship.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=143" class="reference external" target="_blank">8.3.2.1.3</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owning_related_element</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">None</span>*<a href="#syside.Association.owning_related_element" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owning_related_element`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The related_element of this Relationship that owns the Relationship, if any.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=143" class="reference external" target="_blank">8.3.2.1.3</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">related_elements</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature"><span class="pre">syside.Feature</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Association.related_elements" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`related_element`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The Elements that are related by this Relationship, derived as the union of the <span class="pre">`source`</span> and <span class="pre">`target`</span> Elements of the Relationship.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=143" class="reference external" target="_blank">8.3.2.1.3</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">related_types</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type"><span class="pre">syside.Type</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Association.related_types" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`related_type`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The <span class="pre">`types`</span> of the <span class="pre">`association_ends`</span> of the <span class="pre">`Association`</span>, which are the <span class="pre">`related_elements`</span> of the <span class="pre">`Association`</span> considered as a <span class="pre">`Relationship`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=211" class="reference external" target="_blank">8.3.4.4.2</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">source</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature"><span class="pre">syside.Feature</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span>*<a href="#syside.Association.source" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`source`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The <span class="pre">`related_elements`</span>` `<span class="pre">`from`</span>` `<span class="pre">`which`</span>` `<span class="pre">`this`</span>` `<span class="pre">`Relationship`</span>` `<span class="pre">`is`</span>` `<span class="pre">`considered`</span>` `<span class="pre">`to`</span>` `<span class="pre">`be`</span>` `<span class="pre">`directed.`</span>
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=143" class="reference external" target="_blank">8.3.2.1.3</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">source_type</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type"><span class="pre">syside.Type</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span>*<a href="#syside.Association.source_type" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`source_type`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The source <span class="pre">`related_type`</span> for this <span class="pre">`Association`</span>. It is the first <span class="pre">`related_type`</span> of the <span class="pre">`Association`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=211" class="reference external" target="_blank">8.3.4.4.2</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">sources</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">list</span><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature"><span class="pre">syside.Feature</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Association.sources" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`source`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The <span class="pre">`related_elements`</span>` `<span class="pre">`from`</span>` `<span class="pre">`which`</span>` `<span class="pre">`this`</span>` `<span class="pre">`Relationship`</span>` `<span class="pre">`is`</span>` `<span class="pre">`considered`</span>` `<span class="pre">`to`</span>` `<span class="pre">`be`</span>` `<span class="pre">`directed.`</span>
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=143" class="reference external" target="_blank">8.3.2.1.3</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">target_types</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type"><span class="pre">syside.Type</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Association.target_types" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`target_type`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The target <span class="pre">`related_types`</span> for this <span class="pre">`Association`</span>. This includes all the <span class="pre">`related_types`</span> other than the <span class="pre">`source_type`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=212" class="reference external" target="_blank">8.3.4.4.2</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">targets</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature"><span class="pre">syside.Feature</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Association.targets" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`target`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The <span class="pre">`related_elements`</span> to which this Relationship is considered to be directed.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=143" class="reference external" target="_blank">8.3.2.1.3</a> of the KerML specification for more details.

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="#syside.Association" class="reference internal" title="syside.Association"><span class="pre"><code class="sourceCode python">syside.Association</code></span></a>

  - <a href="#syside.Association.STD" class="reference internal" title="syside.Association.STD"><span class="pre"><code class="sourceCode python">STD</code></span></a>

- <a href="/python/v0.8.4/syside/Connector.md" class="reference internal" title="syside.Connector"><span class="pre"><code class="sourceCode python">syside.Connector</code></span></a>

  - <a href="/python/v0.8.4/syside/Connector.md" class="reference internal" title="syside.Connector.associations"><span class="pre"><code class="sourceCode python">associations</code></span></a>

- <a href="/python/v0.8.4/syside/ConnectorAsUsage.md" class="reference internal" title="syside.ConnectorAsUsage"><span class="pre"><code class="sourceCode python">syside.ConnectorAsUsage</code></span></a>

  - <a href="/python/v0.8.4/syside/ConnectorAsUsage.md" class="reference internal" title="syside.ConnectorAsUsage.associations"><span class="pre"><code class="sourceCode python">associations</code></span></a>

- <a href="/python/v0.8.4/syside/Relationship.md" class="reference internal" title="syside.Relationship"><span class="pre"><code class="sourceCode python">syside.Relationship</code></span></a>

  - <a href="/python/v0.8.4/syside/Relationship.md" class="reference internal" title="syside.Relationship.STD"><span class="pre"><code class="sourceCode python">STD</code></span></a>

</div>

</div>
