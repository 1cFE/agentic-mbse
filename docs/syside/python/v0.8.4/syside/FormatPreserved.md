<div id="formatpreserved" class="section">

# FormatPreserved<a href="#formatpreserved" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">FormatPreserved</span></span><span class="sig-paren">\[</span>*<span class="n"><span class="pre">T</span></span>*<span class="sig-paren">\]</span><a href="#syside.FormatPreserved" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
<div class="align-center" align="center">

<img src="data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iZ3JhcGh2aXoiIHN0eWxlPSJ3aWR0aDogNy43NXJlbTtoZWlnaHQ6IDIuNzVyZW07IiB2aWV3Ym94PSIwLjAwIDAuMDAgMTI0LjAwIDQ0LjAwIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPgo8ZyBjbGFzcz0iZ3JhcGgiIGlkPSJncmFwaDAiIHRyYW5zZm9ybT0ic2NhbGUoMSAxKSByb3RhdGUoMCkgdHJhbnNsYXRlKDQgNDApIj4KPHRpdGxlPiUzPC90aXRsZT4KPGcgY2xhc3M9Im5vZGUiIGlkPSJub2RlMSI+Cjx0aXRsZT5Gb3JtYXRQcmVzZXJ2ZWQ8L3RpdGxlPgo8ZyBpZD0iYV9ub2RlMSI+PGEgaHJlZj0iI3N5c2lkZS5Gb3JtYXRQcmVzZXJ2ZWQiPgo8cG9seWdvbiBwb2ludHM9IjExNiwtMzYgMCwtMzYgMCwwIDExNiwwIDExNiwtMzYiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1ncmFwaHZpei1ub2RlLWJnLWNvbG9yKTtzdHJva2U6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtZmctY29sb3IpOyI+PC9wb2x5Z29uPgo8dGV4dCBmb250LWZhbWlseT0iTGV4ZW5kIiBmb250LXNpemU9IjEyLjAwIiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtY29kZS1mZy1jb2xvcik7LS1tZC1ncmFwaHZpei1ob3Zlci1jb2xvcjogdmFyKC0tbWQtZ3JhcGh2aXotYS1ob3Zlci1jb2xvcik7IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSI1OCIgeT0iLTE0LjIiPkZvcm1hdFByZXNlcnZlZDwvdGV4dD4KPHRpdGxlPnN5c2lkZS5Gb3JtYXRQcmVzZXJ2ZWQ8L3RpdGxlPjwvYT4KPC9nPgo8L2c+CjwvZz4KPC9zdmc+" class="graphviz" />

</div>

<span class="sd-summary-text">Members defined in <a href="#syside.FormatPreserved" class="reference internal" title="syside.FormatPreserved"><span class="pre"><code class="sourceCode python">FormatPreserved</code></span></a> (2 members)</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |  |
|----|----|----|----|
| <span class="nerd-font"></span> | <a href="#syside.FormatPreserved.fallback" class="reference internal" title="syside.FormatPreserved.fallback"><span class="pre"><code class="sourceCode python">fallback</code></span></a> | <span class="pre">`RW`</span> | Controls <span class="pre">`preserve`</span> formatting for cases when there is no associated source text or <span class="pre">`preserve`</span> is false. |
| <span class="nerd-font"></span> | <a href="#syside.FormatPreserved.preserve" class="reference internal" title="syside.FormatPreserved.preserve"><span class="pre"><code class="sourceCode python">preserve</code></span></a> | <span class="pre">`RW`</span> | Controls formatting in majority of cases. Set to true to preserve tokens and keywords as they appear in the source code. |

</div>

</div>

<span class="nerd-font"></span> **Attributes**

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">fallback</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">syside.T</span>*<a href="#syside.FormatPreserved.fallback" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Controls <span class="pre">`preserve`</span> formatting for cases when there is no associated source text or <span class="pre">`preserve`</span> is false.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">preserve</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*<a href="#syside.FormatPreserved.preserve" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Controls formatting in majority of cases. Set to true to preserve tokens and keywords as they appear in the source code.

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions"><span class="pre"><code class="sourceCode python">syside.FormatOptions</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.action_node_keyword"><span class="pre"><code class="sourceCode python">action_node_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.allocation_usage_keyword"><span class="pre"><code class="sourceCode python">allocation_usage_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.assert_constraint_usage_keyword"><span class="pre"><code class="sourceCode python">assert_constraint_usage_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.attribute_usage_reference_keyword"><span class="pre"><code class="sourceCode python">attribute_usage_reference_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.binary_allocation_usages"><span class="pre"><code class="sourceCode python">binary_allocation_usages</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.binary_binding_connector_of_keyword"><span class="pre"><code class="sourceCode python">binary_binding_connector_of_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.binary_binding_connectors"><span class="pre"><code class="sourceCode python">binary_binding_connectors</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.binary_connection_usages"><span class="pre"><code class="sourceCode python">binary_connection_usages</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.binary_connectors"><span class="pre"><code class="sourceCode python">binary_connectors</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.binary_connectors_from_keyword"><span class="pre"><code class="sourceCode python">binary_connectors_from_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.binary_interface_usages"><span class="pre"><code class="sourceCode python">binary_interface_usages</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.binary_succession_first_keyword"><span class="pre"><code class="sourceCode python">binary_succession_first_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.binary_successions"><span class="pre"><code class="sourceCode python">binary_successions</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.binding_connector_as_usage_keyword"><span class="pre"><code class="sourceCode python">binding_connector_as_usage_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.comment_keyword"><span class="pre"><code class="sourceCode python">comment_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.conjugation_keyword"><span class="pre"><code class="sourceCode python">conjugation_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.connection_usage_keyword"><span class="pre"><code class="sourceCode python">connection_usage_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.connection_usage_reference_keyword"><span class="pre"><code class="sourceCode python">connection_usage_reference_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.connector_as_usage_reference_keyword"><span class="pre"><code class="sourceCode python">connector_as_usage_reference_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.declaration_conjugated_port_typing"><span class="pre"><code class="sourceCode python">declaration_conjugated_port_typing</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.declaration_conjugation"><span class="pre"><code class="sourceCode python">declaration_conjugation</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.declaration_cross_subsetting"><span class="pre"><code class="sourceCode python">declaration_cross_subsetting</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.declaration_feature_typing"><span class="pre"><code class="sourceCode python">declaration_feature_typing</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.declaration_redefinition"><span class="pre"><code class="sourceCode python">declaration_redefinition</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.declaration_reference_subsetting"><span class="pre"><code class="sourceCode python">declaration_reference_subsetting</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.declaration_specialization"><span class="pre"><code class="sourceCode python">declaration_specialization</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.declaration_subclassification"><span class="pre"><code class="sourceCode python">declaration_subclassification</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.declaration_subsetting"><span class="pre"><code class="sourceCode python">declaration_subsetting</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.dependency_from_keyword"><span class="pre"><code class="sourceCode python">dependency_from_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.disjoining_keyword"><span class="pre"><code class="sourceCode python">disjoining_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.empty_namespace_brackets"><span class="pre"><code class="sourceCode python">empty_namespace_brackets</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.enum_member_keyword"><span class="pre"><code class="sourceCode python">enum_member_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.event_occurrence_keyword"><span class="pre"><code class="sourceCode python">event_occurrence_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.event_occurrence_reference_keyword"><span class="pre"><code class="sourceCode python">event_occurrence_reference_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.exhibit_state_reference_keyword"><span class="pre"><code class="sourceCode python">exhibit_state_reference_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.exhibit_state_usage_keyword"><span class="pre"><code class="sourceCode python">exhibit_state_usage_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.feature_keyword"><span class="pre"><code class="sourceCode python">feature_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.feature_value_equals"><span class="pre"><code class="sourceCode python">feature_value_equals</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.featuring_of_keyword"><span class="pre"><code class="sourceCode python">featuring_of_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.flow_from_keyword"><span class="pre"><code class="sourceCode python">flow_from_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.flow_usage_from_keyword"><span class="pre"><code class="sourceCode python">flow_usage_from_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.framed_concern_keyword"><span class="pre"><code class="sourceCode python">framed_concern_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.include_use_case_reference_keyword"><span class="pre"><code class="sourceCode python">include_use_case_reference_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.include_use_case_usage_keyword"><span class="pre"><code class="sourceCode python">include_use_case_usage_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.interface_port_keyword"><span class="pre"><code class="sourceCode python">interface_port_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.interface_usage_connect_keyword"><span class="pre"><code class="sourceCode python">interface_usage_connect_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.invariant_true_keyword"><span class="pre"><code class="sourceCode python">invariant_true_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.inverting_keyword"><span class="pre"><code class="sourceCode python">inverting_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.metadata_body_feature_keyword"><span class="pre"><code class="sourceCode python">metadata_body_feature_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.metadata_body_feature_redefines"><span class="pre"><code class="sourceCode python">metadata_body_feature_redefines</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.metadata_feature_keyword"><span class="pre"><code class="sourceCode python">metadata_feature_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.null_expression"><span class="pre"><code class="sourceCode python">null_expression</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.occurrence_keyword"><span class="pre"><code class="sourceCode python">occurrence_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.ordered_nonunique_priority"><span class="pre"><code class="sourceCode python">ordered_nonunique_priority</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.perform_action_reference_keyword"><span class="pre"><code class="sourceCode python">perform_action_reference_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.perform_action_usage_keyword"><span class="pre"><code class="sourceCode python">perform_action_usage_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.port_usage_reference_keyword"><span class="pre"><code class="sourceCode python">port_usage_reference_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.public_keyword"><span class="pre"><code class="sourceCode python">public_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.reference_usage_keyword"><span class="pre"><code class="sourceCode python">reference_usage_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.satisfy_requirement_assert_keyword"><span class="pre"><code class="sourceCode python">satisfy_requirement_assert_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.satisfy_requirement_keyword"><span class="pre"><code class="sourceCode python">satisfy_requirement_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.specialization_keyword_feature_typing"><span class="pre"><code class="sourceCode python">specialization_keyword_feature_typing</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.specialization_keyword_redefinition"><span class="pre"><code class="sourceCode python">specialization_keyword_redefinition</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.specialization_keyword_specialization"><span class="pre"><code class="sourceCode python">specialization_keyword_specialization</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.specialization_keyword_subclassification"><span class="pre"><code class="sourceCode python">specialization_keyword_subclassification</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.specialization_keyword_subsetting"><span class="pre"><code class="sourceCode python">specialization_keyword_subsetting</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.succession_as_usage_keyword"><span class="pre"><code class="sourceCode python">succession_as_usage_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.succession_flow_from_keyword"><span class="pre"><code class="sourceCode python">succession_flow_from_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.succession_flow_usage_from_keyword"><span class="pre"><code class="sourceCode python">succession_flow_usage_from_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.textual_representation_keyword"><span class="pre"><code class="sourceCode python">textual_representation_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.transition_usage_first_keyword"><span class="pre"><code class="sourceCode python">transition_usage_first_keyword</code></span></a>

  - <a href="/python/v0.8.4/syside/FormatOptions.md" class="reference internal" title="syside.FormatOptions.transition_usage_keyword"><span class="pre"><code class="sourceCode python">transition_usage_keyword</code></span></a>

</div>

</div>
