<div id="type-sysml" class="section">

# Type <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span><a href="#type-sysml" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">Type</span></span><a href="#syside.Type" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`Type`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> A <span class="pre">`Type`</span> is a <span class="pre">`Namespace`</span> that is the most general kind of <span class="pre">`Element`</span> supporting the semantics of classification. A <span class="pre">`Type`</span> may be a <span class="pre">`Classifier`</span> or a <span class="pre">`Feature`</span>, defining conditions on what is classified by the <span class="pre">`Type`</span> (see also the description of <span class="pre">`is_sufficient`</span>).
>
> </div>

For language description, see section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=52" class="reference external" target="_blank">7.3.2</a> of the KerML specification. For more details on the model, see section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=171" class="reference external" target="_blank">8.3.3.1.10</a> of the KerML specification.

<div class="align-center" align="center">

<img src="data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iZ3JhcGh2aXoiIHN0eWxlPSJ3aWR0aDogNS43NXJlbTtoZWlnaHQ6IDE2LjI1cmVtOyIgdmlld2JveD0iMC4wMCAwLjAwIDkyLjAwIDI2MC4wMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGcgY2xhc3M9ImdyYXBoIiBpZD0iZ3JhcGgwIiB0cmFuc2Zvcm09InNjYWxlKDEgMSkgcm90YXRlKDApIHRyYW5zbGF0ZSg0IDI1NikiPgo8dGl0bGU+JTM8L3RpdGxlPgo8ZyBjbGFzcz0ibm9kZSIgaWQ9Im5vZGUxIj4KPHRpdGxlPlR5cGU8L3RpdGxlPgo8ZyBpZD0iYV9ub2RlMSI+PGEgaHJlZj0iI3N5c2lkZS5UeXBlIj4KPHBvbHlnb24gcG9pbnRzPSI2OSwtMzYgMTUsLTM2IDE1LDAgNjksMCA2OSwtMzYiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1ncmFwaHZpei1ub2RlLWJnLWNvbG9yKTtzdHJva2U6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtZmctY29sb3IpOyI+PC9wb2x5Z29uPgo8dGV4dCBmb250LWZhbWlseT0iTGV4ZW5kIiBmb250LXNpemU9IjEyLjAwIiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtY29kZS1mZy1jb2xvcik7LS1tZC1ncmFwaHZpei1ob3Zlci1jb2xvcjogdmFyKC0tbWQtZ3JhcGh2aXotYS1ob3Zlci1jb2xvcik7IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSI0MiIgeT0iLTE0LjIiPlR5cGU8L3RleHQ+Cjx0aXRsZT5zeXNpZGUuVHlwZTwvdGl0bGU+PC9hPgo8L2c+CjwvZz4KPGcgY2xhc3M9Im5vZGUiIGlkPSJub2RlMiI+Cjx0aXRsZT5OYW1lc3BhY2U8L3RpdGxlPgo8ZyBpZD0iYV9ub2RlMiI+PGEgaHJlZj0iL3B5dGhvbi92MC44LjQvc3lzaWRlL05hbWVzcGFjZS5tZCI+Cjxwb2x5Z29uIHBvaW50cz0iODQsLTEwOCAwLC0xMDggMCwtNzIgODQsLTcyIDg0LC0xMDgiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1ncmFwaHZpei1ub2RlLWJnLWNvbG9yKTtzdHJva2U6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtZmctY29sb3IpOyI+PC9wb2x5Z29uPgo8dGV4dCBmb250LWZhbWlseT0iTGV4ZW5kIiBmb250LXNpemU9IjEyLjAwIiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtY29kZS1mZy1jb2xvcik7LS1tZC1ncmFwaHZpei1ob3Zlci1jb2xvcjogdmFyKC0tbWQtZ3JhcGh2aXotYS1ob3Zlci1jb2xvcik7IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSI0MiIgeT0iLTg2LjIiPk5hbWVzcGFjZTwvdGV4dD4KPHRpdGxlPnN5c2lkZS5OYW1lc3BhY2U8L3RpdGxlPjwvYT4KPC9nPgo8L2c+CjxnIGNsYXNzPSJlZGdlIiBpZD0iZWRnZTEiPgo8dGl0bGU+TmFtZXNwYWNlLSZndDtUeXBlPC90aXRsZT4KPHBhdGggZD0iTTQyLC03MS43QzQyLC02My45OCA0MiwtNTQuNzEgNDIsLTQ2LjExIiBmaWxsPSJub25lIiBzdHlsZT0ic3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1lZGdlLWNvbG9yKTsiIC8+Cjxwb2x5Z29uIHBvaW50cz0iNDUuNSwtNDYuMSA0MiwtMzYuMSAzOC41LC00Ni4xIDQ1LjUsLTQ2LjEiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1ncmFwaHZpei1lZGdlLWNvbG9yKTtzdHJva2U6IHZhcigtLW1kLWdyYXBodml6LWVkZ2UtY29sb3IpOyI+PC9wb2x5Z29uPgo8L2c+CjxnIGNsYXNzPSJub2RlIiBpZD0ibm9kZTMiPgo8dGl0bGU+RWxlbWVudDwvdGl0bGU+CjxnIGlkPSJhX25vZGUzIj48YSBocmVmPSIvcHl0aG9uL3YwLjguNC9zeXNpZGUvRWxlbWVudC5tZCI+Cjxwb2x5Z29uIHBvaW50cz0iNzMsLTE4MCAxMSwtMTgwIDExLC0xNDQgNzMsLTE0NCA3MywtMTgwIiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1iZy1jb2xvcik7c3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1ub2RlLWZnLWNvbG9yKTsiPjwvcG9seWdvbj4KPHRleHQgZm9udC1mYW1pbHk9IkxleGVuZCIgZm9udC1zaXplPSIxMi4wMCIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWNvZGUtZmctY29sb3IpOy0tbWQtZ3JhcGh2aXotaG92ZXItY29sb3I6IHZhcigtLW1kLWdyYXBodml6LWEtaG92ZXItY29sb3IpOyIgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iNDIiIHk9Ii0xNTguMiI+RWxlbWVudDwvdGV4dD4KPHRpdGxlPnN5c2lkZS5FbGVtZW50PC90aXRsZT48L2E+CjwvZz4KPC9nPgo8ZyBjbGFzcz0iZWRnZSIgaWQ9ImVkZ2UyIj4KPHRpdGxlPkVsZW1lbnQtJmd0O05hbWVzcGFjZTwvdGl0bGU+CjxwYXRoIGQ9Ik00MiwtMTQzLjdDNDIsLTEzNS45OCA0MiwtMTI2LjcxIDQyLC0xMTguMTEiIGZpbGw9Im5vbmUiIHN0eWxlPSJzdHJva2U6IHZhcigtLW1kLWdyYXBodml6LWVkZ2UtY29sb3IpOyIgLz4KPHBvbHlnb24gcG9pbnRzPSI0NS41LC0xMTguMSA0MiwtMTA4LjEgMzguNSwtMTE4LjEgNDUuNSwtMTE4LjEiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1ncmFwaHZpei1lZGdlLWNvbG9yKTtzdHJva2U6IHZhcigtLW1kLWdyYXBodml6LWVkZ2UtY29sb3IpOyI+PC9wb2x5Z29uPgo8L2c+CjxnIGNsYXNzPSJub2RlIiBpZD0ibm9kZTQiPgo8dGl0bGU+QXN0Tm9kZTwvdGl0bGU+CjxnIGlkPSJhX25vZGU0Ij48YSBocmVmPSIvcHl0aG9uL3YwLjguNC9zeXNpZGUvQXN0Tm9kZS5tZCI+Cjxwb2x5Z29uIHBvaW50cz0iNzUsLTI1MiA5LC0yNTIgOSwtMjE2IDc1LC0yMTYgNzUsLTI1MiIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtYmctY29sb3IpO3N0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1mZy1jb2xvcik7Ij48L3BvbHlnb24+Cjx0ZXh0IGZvbnQtZmFtaWx5PSJMZXhlbmQiIGZvbnQtc2l6ZT0iMTIuMDAiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1jb2RlLWZnLWNvbG9yKTstLW1kLWdyYXBodml6LWhvdmVyLWNvbG9yOiB2YXIoLS1tZC1ncmFwaHZpei1hLWhvdmVyLWNvbG9yKTsiIHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjQyIiB5PSItMjMwLjIiPkFzdE5vZGU8L3RleHQ+Cjx0aXRsZT5zeXNpZGUuQXN0Tm9kZTwvdGl0bGU+PC9hPgo8L2c+CjwvZz4KPGcgY2xhc3M9ImVkZ2UiIGlkPSJlZGdlMyI+Cjx0aXRsZT5Bc3ROb2RlLSZndDtFbGVtZW50PC90aXRsZT4KPHBhdGggZD0iTTQyLC0yMTUuN0M0MiwtMjA3Ljk4IDQyLC0xOTguNzEgNDIsLTE5MC4xMSIgZmlsbD0ibm9uZSIgc3R5bGU9InN0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotZWRnZS1jb2xvcik7IiAvPgo8cG9seWdvbiBwb2ludHM9IjQ1LjUsLTE5MC4xIDQyLC0xODAuMSAzOC41LC0xOTAuMSA0NS41LC0xOTAuMSIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWdyYXBodml6LWVkZ2UtY29sb3IpO3N0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotZWRnZS1jb2xvcik7Ij48L3BvbHlnb24+CjwvZz4KPC9nPgo8L3N2Zz4=" class="graphviz" />

</div>

<span class="sd-summary-text"><span class="nerd-font"></span> Children</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/Classifier.md" class="reference internal" title="syside.Classifier"><span class="pre"><code class="sourceCode python">Classifier</code></span></a>

  - <a href="/python/v0.8.4/syside/Association.md" class="reference internal" title="syside.Association"><span class="pre"><code class="sourceCode python">Association</code></span></a>

    - <a href="/python/v0.8.4/syside/AssociationStructure.md" class="reference internal" title="syside.AssociationStructure"><span class="pre"><code class="sourceCode python">AssociationStructure</code></span></a>

    - <a href="/python/v0.8.4/syside/Interaction.md" class="reference internal" title="syside.Interaction"><span class="pre"><code class="sourceCode python">Interaction</code></span></a>

  - <a href="/python/v0.8.4/syside/Class.md" class="reference internal" title="syside.Class"><span class="pre"><code class="sourceCode python">Class</code></span></a>

    - <a href="/python/v0.8.4/syside/Behavior.md" class="reference internal" title="syside.Behavior"><span class="pre"><code class="sourceCode python">Behavior</code></span></a>

      - <a href="/python/v0.8.4/syside/Function.md" class="reference internal" title="syside.Function"><span class="pre"><code class="sourceCode python">Function</code></span></a>

        - <a href="/python/v0.8.4/syside/Predicate.md" class="reference internal" title="syside.Predicate"><span class="pre"><code class="sourceCode python">Predicate</code></span></a>

    - <a href="/python/v0.8.4/syside/Structure.md" class="reference internal" title="syside.Structure"><span class="pre"><code class="sourceCode python">Structure</code></span></a>

      - <a href="/python/v0.8.4/syside/Metaclass.md" class="reference internal" title="syside.Metaclass"><span class="pre"><code class="sourceCode python">Metaclass</code></span></a>

  - <a href="/python/v0.8.4/syside/DataType.md" class="reference internal" title="syside.DataType"><span class="pre"><code class="sourceCode python">DataType</code></span></a>

  - <a href="/python/v0.8.4/syside/Definition.md" class="reference internal" title="syside.Definition"><span class="pre"><code class="sourceCode python">Definition</code></span></a>

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

- <a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature"><span class="pre"><code class="sourceCode python">Feature</code></span></a>

  - <a href="/python/v0.8.4/syside/Connector.md" class="reference internal" title="syside.Connector"><span class="pre"><code class="sourceCode python">Connector</code></span></a>

    - <a href="/python/v0.8.4/syside/BindingConnector.md" class="reference internal" title="syside.BindingConnector"><span class="pre"><code class="sourceCode python">BindingConnector</code></span></a>

    - <a href="/python/v0.8.4/syside/Flow.md" class="reference internal" title="syside.Flow"><span class="pre"><code class="sourceCode python">Flow</code></span></a>

      - <a href="/python/v0.8.4/syside/SuccessionFlow.md" class="reference internal" title="syside.SuccessionFlow"><span class="pre"><code class="sourceCode python">SuccessionFlow</code></span></a>

    - <a href="/python/v0.8.4/syside/Succession.md" class="reference internal" title="syside.Succession"><span class="pre"><code class="sourceCode python">Succession</code></span></a>

  - <a href="/python/v0.8.4/syside/FlowEnd.md" class="reference internal" title="syside.FlowEnd"><span class="pre"><code class="sourceCode python">FlowEnd</code></span></a>

  - <a href="/python/v0.8.4/syside/MetadataFeature.md" class="reference internal" title="syside.MetadataFeature"><span class="pre"><code class="sourceCode python">MetadataFeature</code></span></a>

  - <a href="/python/v0.8.4/syside/Multiplicity.md" class="reference internal" title="syside.Multiplicity"><span class="pre"><code class="sourceCode python">Multiplicity</code></span></a>

    - <a href="/python/v0.8.4/syside/MultiplicityRange.md" class="reference internal" title="syside.MultiplicityRange"><span class="pre"><code class="sourceCode python">MultiplicityRange</code></span></a>

  - <a href="/python/v0.8.4/syside/PayloadFeature.md" class="reference internal" title="syside.PayloadFeature"><span class="pre"><code class="sourceCode python">PayloadFeature</code></span></a>

  - <a href="/python/v0.8.4/syside/Step.md" class="reference internal" title="syside.Step"><span class="pre"><code class="sourceCode python">Step</code></span></a>

    - <a href="/python/v0.8.4/syside/Expression.md" class="reference internal" title="syside.Expression"><span class="pre"><code class="sourceCode python">Expression</code></span></a>

      - <a href="/python/v0.8.4/syside/BooleanExpression.md" class="reference internal" title="syside.BooleanExpression"><span class="pre"><code class="sourceCode python">BooleanExpression</code></span></a>

        - <a href="/python/v0.8.4/syside/Invariant.md" class="reference internal" title="syside.Invariant"><span class="pre"><code class="sourceCode python">Invariant</code></span></a>

      - <a href="/python/v0.8.4/syside/FeatureReferenceExpression.md" class="reference internal" title="syside.FeatureReferenceExpression"><span class="pre"><code class="sourceCode python">FeatureReferenceExpression</code></span></a>

      - <a href="/python/v0.8.4/syside/InstantiationExpression.md" class="reference internal" title="syside.InstantiationExpression"><span class="pre"><code class="sourceCode python">InstantiationExpression</code></span></a>

        - <a href="/python/v0.8.4/syside/ConstructorExpression.md" class="reference internal" title="syside.ConstructorExpression"><span class="pre"><code class="sourceCode python">ConstructorExpression</code></span></a>

        - <a href="/python/v0.8.4/syside/InvocationExpression.md" class="reference internal" title="syside.InvocationExpression"><span class="pre"><code class="sourceCode python">InvocationExpression</code></span></a>

          - <a href="/python/v0.8.4/syside/OperatorExpression.md" class="reference internal" title="syside.OperatorExpression"><span class="pre"><code class="sourceCode python">OperatorExpression</code></span></a>

            - <a href="/python/v0.8.4/syside/CollectExpression.md" class="reference internal" title="syside.CollectExpression"><span class="pre"><code class="sourceCode python">CollectExpression</code></span></a>

            - <a href="/python/v0.8.4/syside/FeatureChainExpression.md" class="reference internal" title="syside.FeatureChainExpression"><span class="pre"><code class="sourceCode python">FeatureChainExpression</code></span></a>

            - <a href="/python/v0.8.4/syside/IndexExpression.md" class="reference internal" title="syside.IndexExpression"><span class="pre"><code class="sourceCode python">IndexExpression</code></span></a>

            - <a href="/python/v0.8.4/syside/SelectExpression.md" class="reference internal" title="syside.SelectExpression"><span class="pre"><code class="sourceCode python">SelectExpression</code></span></a>

          - <a href="/python/v0.8.4/syside/TriggerInvocationExpression.md" class="reference internal" title="syside.TriggerInvocationExpression"><span class="pre"><code class="sourceCode python">TriggerInvocationExpression</code></span></a>

      - <a href="/python/v0.8.4/syside/LiteralExpression.md" class="reference internal" title="syside.LiteralExpression"><span class="pre"><code class="sourceCode python">LiteralExpression</code></span></a>

        - <a href="/python/v0.8.4/syside/LiteralBoolean.md" class="reference internal" title="syside.LiteralBoolean"><span class="pre"><code class="sourceCode python">LiteralBoolean</code></span></a>

        - <a href="/python/v0.8.4/syside/LiteralInfinity.md" class="reference internal" title="syside.LiteralInfinity"><span class="pre"><code class="sourceCode python">LiteralInfinity</code></span></a>

        - <a href="/python/v0.8.4/syside/LiteralInteger.md" class="reference internal" title="syside.LiteralInteger"><span class="pre"><code class="sourceCode python">LiteralInteger</code></span></a>

        - <a href="/python/v0.8.4/syside/LiteralRational.md" class="reference internal" title="syside.LiteralRational"><span class="pre"><code class="sourceCode python">LiteralRational</code></span></a>

        - <a href="/python/v0.8.4/syside/LiteralString.md" class="reference internal" title="syside.LiteralString"><span class="pre"><code class="sourceCode python">LiteralString</code></span></a>

      - <a href="/python/v0.8.4/syside/MetadataAccessExpression.md" class="reference internal" title="syside.MetadataAccessExpression"><span class="pre"><code class="sourceCode python">MetadataAccessExpression</code></span></a>

      - <a href="/python/v0.8.4/syside/NullExpression.md" class="reference internal" title="syside.NullExpression"><span class="pre"><code class="sourceCode python">NullExpression</code></span></a>

  - <a href="/python/v0.8.4/syside/Usage.md" class="reference internal" title="syside.Usage"><span class="pre"><code class="sourceCode python">Usage</code></span></a>

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

<span class="sd-summary-text">Members defined in <a href="#syside.Type" class="reference internal" title="syside.Type"><span class="pre"><code class="sourceCode python">Type</code></span></a> (38 members)</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |  |
|----|----|----|----|
| <span class="nerd-font"></span> | <a href="#syside.Type.STD" class="reference internal" title="syside.Type.STD"><span class="pre"><code class="sourceCode python">STD</code></span></a> | <span class="pre">`R`</span> |  |
| <span class="nerd-font"></span> | <a href="#syside.Type.declared_multiplicity" class="reference internal" title="syside.Type.declared_multiplicity"><span class="pre"><code class="sourceCode python">declared_multiplicity</code></span></a> | <span class="pre">`R`</span> | The owned multiplicity that is declared before the children block in the textual syntax. |
| <span class="nerd-font"></span> | <a href="#syside.Type.declared_multiplicity_member" class="reference internal" title="syside.Type.declared_multiplicity_member"><span class="pre"><code class="sourceCode python">declared_multiplicity_member</code></span></a> | <span class="pre">`R`</span> | Syside specific accessor for manipulating <span class="pre">`declared_multiplicity`</span>. |
| <span class="nerd-font"></span> | <a href="#syside.Type.differencing_types" class="reference internal" title="syside.Type.differencing_types"><span class="pre"><code class="sourceCode python">differencing_types</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`differencing_type`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Type.directed_features" class="reference internal" title="syside.Type.directed_features"><span class="pre"><code class="sourceCode python">directed_features</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`directed_feature`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Type.disjoining_types" class="reference internal" title="syside.Type.disjoining_types"><span class="pre"><code class="sourceCode python">disjoining_types</code></span></a> | <span class="pre">`R`</span> | The types that related to this <span class="pre">`Type`</span> through <span class="pre">`owned_disjoinings`</span>. |
| <span class="nerd-font"></span> | <a href="#syside.Type.end_features" class="reference internal" title="syside.Type.end_features"><span class="pre"><code class="sourceCode python">end_features</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`end_feature`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Type.feature_memberships" class="reference internal" title="syside.Type.feature_memberships"><span class="pre"><code class="sourceCode python">feature_memberships</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`feature_membership`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Type.features" class="reference internal" title="syside.Type.features"><span class="pre"><code class="sourceCode python">features</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`feature`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Type.heritage" class="reference internal" title="syside.Type.heritage"><span class="pre"><code class="sourceCode python">heritage</code></span></a> | <span class="pre">`R`</span> | The specializations and conjugations owned by this <span class="pre">`Type`</span>. |
| <span class="nerd-font"></span> | <a href="#syside.Type.inherited_features" class="reference internal" title="syside.Type.inherited_features"><span class="pre"><code class="sourceCode python">inherited_features</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`inherited_feature`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Type.inherited_memberships" class="reference internal" title="syside.Type.inherited_memberships"><span class="pre"><code class="sourceCode python">inherited_memberships</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`inherited_membership`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Type.inputs" class="reference internal" title="syside.Type.inputs"><span class="pre"><code class="sourceCode python">inputs</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`input`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Type.intersecting_types" class="reference internal" title="syside.Type.intersecting_types"><span class="pre"><code class="sourceCode python">intersecting_types</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`intersecting_type`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Type.is_abstract" class="reference internal" title="syside.Type.is_abstract"><span class="pre"><code class="sourceCode python">is_abstract</code></span></a> | <span class="pre">`RW`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`is_abstract`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Type.is_abstract_explicitly" class="reference internal" title="syside.Type.is_abstract_explicitly"><span class="pre"><code class="sourceCode python">is_abstract_explicitly</code></span></a> | <span class="pre">`R`</span> | Returns <span class="pre">`True`</span> if this <span class="pre">`Type`</span> was declared as <span class="pre">`abstract`</span> in the textual syntax. |
| <span class="nerd-font"></span> | <a href="#syside.Type.is_conjugated" class="reference internal" title="syside.Type.is_conjugated"><span class="pre"><code class="sourceCode python">is_conjugated</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`is_conjugated`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Type.is_sufficient" class="reference internal" title="syside.Type.is_sufficient"><span class="pre"><code class="sourceCode python">is_sufficient</code></span></a> | <span class="pre">`RW`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`is_sufficient`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Type.is_sufficient_explicitly" class="reference internal" title="syside.Type.is_sufficient_explicitly"><span class="pre"><code class="sourceCode python">is_sufficient_explicitly</code></span></a> | <span class="pre">`R`</span> | Returns <span class="pre">`True`</span> if this <span class="pre">`Type`</span> was declared as <span class="pre">`sufficient`</span> in the textual syntax. |
| <span class="nerd-font"></span> | <a href="#syside.Type.multiplicity" class="reference internal" title="syside.Type.multiplicity"><span class="pre"><code class="sourceCode python">multiplicity</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`multiplicity`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Type.outputs" class="reference internal" title="syside.Type.outputs"><span class="pre"><code class="sourceCode python">outputs</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`output`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Type.owned_conjugator" class="reference internal" title="syside.Type.owned_conjugator"><span class="pre"><code class="sourceCode python">owned_conjugator</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_conjugator`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Type.owned_differencings" class="reference internal" title="syside.Type.owned_differencings"><span class="pre"><code class="sourceCode python">owned_differencings</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_differencing`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Type.owned_directed_features" class="reference internal" title="syside.Type.owned_directed_features"><span class="pre"><code class="sourceCode python">owned_directed_features</code></span></a> | <span class="pre">`R`</span> | The <span class="pre">`directed_features`</span> that are owned by this <span class="pre">`Type`</span>. |
| <span class="nerd-font"></span> | <a href="#syside.Type.owned_disjoinings" class="reference internal" title="syside.Type.owned_disjoinings"><span class="pre"><code class="sourceCode python">owned_disjoinings</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_disjoining`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Type.owned_end_features" class="reference internal" title="syside.Type.owned_end_features"><span class="pre"><code class="sourceCode python">owned_end_features</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_end_feature`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Type.owned_feature_memberships" class="reference internal" title="syside.Type.owned_feature_memberships"><span class="pre"><code class="sourceCode python">owned_feature_memberships</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_feature_membership`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Type.owned_features" class="reference internal" title="syside.Type.owned_features"><span class="pre"><code class="sourceCode python">owned_features</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_feature`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Type.owned_inputs" class="reference internal" title="syside.Type.owned_inputs"><span class="pre"><code class="sourceCode python">owned_inputs</code></span></a> | <span class="pre">`R`</span> | The <span class="pre">`inputs`</span> that are owned by this <span class="pre">`Type`</span>. |
| <span class="nerd-font"></span> | <a href="#syside.Type.owned_intersectings" class="reference internal" title="syside.Type.owned_intersectings"><span class="pre"><code class="sourceCode python">owned_intersectings</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_intersecting`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Type.owned_outputs" class="reference internal" title="syside.Type.owned_outputs"><span class="pre"><code class="sourceCode python">owned_outputs</code></span></a> | <span class="pre">`R`</span> | The <span class="pre">`outputs`</span> that are owned by this <span class="pre">`Type`</span>. |
| <span class="nerd-font"></span> | <a href="#syside.Type.owned_specializations" class="reference internal" title="syside.Type.owned_specializations"><span class="pre"><code class="sourceCode python">owned_specializations</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_specialization`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Type.owned_unionings" class="reference internal" title="syside.Type.owned_unionings"><span class="pre"><code class="sourceCode python">owned_unionings</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_unioning`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Type.type_relationships" class="reference internal" title="syside.Type.type_relationships"><span class="pre"><code class="sourceCode python">type_relationships</code></span></a> | <span class="pre">`R`</span> | The other type, feature relationships and <span class="pre">`FeatureChainings`</span> owned by this <span class="pre">`Type`</span>. |
| <span class="nerd-font"></span> | <a href="#syside.Type.unioning_types" class="reference internal" title="syside.Type.unioning_types"><span class="pre"><code class="sourceCode python">unioning_types</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`unioning_type`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Type.conforms" class="reference internal" title="syside.Type.conforms"><span class="pre"><code class="sourceCode python">conforms</code></span></a> |  | Returns <span class="pre">`True`</span> if this <span class="pre">`Type`</span> directly or indirectly specializes another <span class="pre">`Type`</span> while following <span class="pre">`FeatureChainings`</span>. |
| <span class="nerd-font"></span> | <a href="#syside.Type.direction_of" class="reference internal" title="syside.Type.direction_of"><span class="pre"><code class="sourceCode python">direction_of</code></span></a> |  | Returns the direction of a <span class="pre">`Feature`</span> in this <span class="pre">`Type`</span>. |
| <span class="nerd-font"></span> | <a href="#syside.Type.specializes" class="reference internal" title="syside.Type.specializes"><span class="pre"><code class="sourceCode python">specializes</code></span></a> |  | Returns <span class="pre">`True`</span> if this <span class="pre">`Type`</span> directly or indirectly specializes another <span class="pre">`Type`</span> while ignoring <span class="pre">`FeatureChainings`</span>. |

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

<span class="sig-name descname"><span class="pre">STD</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><span class="pre">type</span><span class="p"><span class="pre">\[</span></span><a href="#syside.Type" class="reference internal" title="syside.Type"><span class="pre">syside.Type</span></a><span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="p"><span class="pre">...</span></span><span class="p"><span class="pre">\]</span></span><span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">()</span>*<a href="#syside.Type.STD" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">declared_multiplicity</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/MultiplicityRange.md" class="reference internal" title="syside.MultiplicityRange"><span class="pre">syside.MultiplicityRange</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span>*<a href="#syside.Type.declared_multiplicity" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
The owned multiplicity that is declared before the children block in the textual syntax.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">declared_multiplicity_member</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/OwnedMultiplicityAccessor.md" class="reference internal" title="syside.OwnedMultiplicityAccessor"><span class="pre">syside.OwnedMultiplicityAccessor</span></a>*<a href="#syside.Type.declared_multiplicity_member" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Syside specific accessor for manipulating <span class="pre">`declared_multiplicity`</span>.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">differencing_types</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="#syside.Type" class="reference internal" title="syside.Type"><span class="pre">syside.Type</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Type.differencing_types" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`differencing_type`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The interpretations of a <span class="pre">`Type`</span> with <span class="pre">`differencing_types`</span> are asserted to be those of the first of those <span class="pre">`Types`</span>, but not including those of the remaining <span class="pre">`Types`</span>. For example, a <span class="pre">`Classifier`</span> might be the difference of a <span class="pre">`Classifier`</span> for people and another for people of a particular nationality, leaving people who are not of that nationality. Similarly, a feature of people might be the difference between a feature for their children and a <span class="pre">`Classifier`</span> for people of a particular sex, identifying their children not of that sex (because the interpretations of the children <span class="pre">`Feature`</span> that identify those of that sex are also interpretations of the <span class="pre">`Classifier`</span> for that sex).
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=171" class="reference external" target="_blank">8.3.3.1.10</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">directed_features</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature"><span class="pre">syside.Feature</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Type.directed_features" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`directed_feature`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The <span class="pre">`features`</span> of this <span class="pre">`Type`</span> that have a non-null <span class="pre">`direction`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=171" class="reference external" target="_blank">8.3.3.1.10</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">disjoining_types</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="#syside.Type" class="reference internal" title="syside.Type"><span class="pre">syside.Type</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Type.disjoining_types" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
The types that related to this <span class="pre">`Type`</span> through <span class="pre">`owned_disjoinings`</span>.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">end_features</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature"><span class="pre">syside.Feature</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Type.end_features" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`end_feature`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> All <span class="pre">`features`</span> of this <span class="pre">`Type`</span> with <span class="pre">`is_end`</span>` `<span class="pre">`=`</span>` `<span class="pre">`true`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=171" class="reference external" target="_blank">8.3.3.1.10</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">feature_memberships</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/FeatureMembership.md" class="reference internal" title="syside.FeatureMembership"><span class="pre">syside.FeatureMembership</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Type.feature_memberships" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`feature_membership`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The <span class="pre">`FeatureMemberships`</span> for <span class="pre">`features`</span> of this <span class="pre">`Type`</span>, which include all <span class="pre">`owned_feature_memberships`</span> and those <span class="pre">`inherited_memberships`</span> that are <span class="pre">`FeatureMemberships`</span> (but does *not* include any <span class="pre">`imported_memberships`</span>).
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=172" class="reference external" target="_blank">8.3.3.1.10</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">features</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature"><span class="pre">syside.Feature</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Type.features" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`feature`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The <span class="pre">`owned_member_features`</span> of the <span class="pre">`feature_memberships`</span> of this <span class="pre">`Type`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=171" class="reference external" target="_blank">8.3.3.1.10</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">heritage</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/Heritage.md" class="reference internal" title="syside.Heritage"><span class="pre">syside.Heritage</span></a>*<a href="#syside.Type.heritage" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
The specializations and conjugations owned by this <span class="pre">`Type`</span>.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">inherited_features</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature"><span class="pre">syside.Feature</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Type.inherited_features" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`inherited_feature`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> All the <span class="pre">`member_features`</span> of the <span class="pre">`inherited_memberships`</span> of this <span class="pre">`Type`</span> that are <span class="pre">`FeatureMemberships`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=172" class="reference external" target="_blank">8.3.3.1.10</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">inherited_memberships</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Membership.md" class="reference internal" title="syside.Membership"><span class="pre">syside.Membership</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Type.inherited_memberships" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`inherited_membership`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> All <span class="pre">`Memberships`</span> inherited by this <span class="pre">`Type`</span> via <span class="pre">`Specialization`</span> or <span class="pre">`Conjugation`</span>. These are included in the derived union for the <span class="pre">`memberships`</span> of the <span class="pre">`Type`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=172" class="reference external" target="_blank">8.3.3.1.10</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">inputs</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature"><span class="pre">syside.Feature</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Type.inputs" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`input`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> All <span class="pre">`features`</span> related to this <span class="pre">`Type`</span> by <span class="pre">`FeatureMemberships`</span> that have <span class="pre">`direction`</span> <span class="pre">`in`</span> or <span class="pre">`inout`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=172" class="reference external" target="_blank">8.3.3.1.10</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">intersecting_types</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="#syside.Type" class="reference internal" title="syside.Type"><span class="pre">syside.Type</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Type.intersecting_types" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`intersecting_type`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The interpretations of a <span class="pre">`Type`</span> with <span class="pre">`intersecting_types`</span> are asserted to be those in common among the <span class="pre">`intersecting_types`</span>, which are the <span class="pre">`Types`</span> derived from the <span class="pre">`intersecting_type`</span> of the <span class="pre">`owned_intersectings`</span> of this <span class="pre">`Type`</span>. For example, a <span class="pre">`Classifier`</span> might be an intersection of <span class="pre">`Classifiers`</span> for people of a particular sex and of a particular nationality. Similarly, a feature for people’s children of a particular sex might be the intersection of a <span class="pre">`Feature`</span> for their children and a <span class="pre">`Classifier`</span> for people of that sex (because the interpretations of the children <span class="pre">`Feature`</span> that identify those of that sex are also interpretations of the Classifier for that sex).
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=172" class="reference external" target="_blank">8.3.3.1.10</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">is_abstract</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*<a href="#syside.Type.is_abstract" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`is_abstract`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> Indicates whether instances of this <span class="pre">`Type`</span> must also be instances of at least one of its specialized <span class="pre">`Types`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=172" class="reference external" target="_blank">8.3.3.1.10</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">is_abstract_explicitly</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*<a href="#syside.Type.is_abstract_explicitly" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Returns <span class="pre">`True`</span> if this <span class="pre">`Type`</span> was declared as <span class="pre">`abstract`</span> in the textual syntax.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">is_conjugated</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*<a href="#syside.Type.is_conjugated" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`is_conjugated`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> Indicates whether this <span class="pre">`Type`</span> has an <span class="pre">`owned_conjugator`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=172" class="reference external" target="_blank">8.3.3.1.10</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">is_sufficient</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*<a href="#syside.Type.is_sufficient" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`is_sufficient`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> Whether all things that meet the classification conditions of this <span class="pre">`Type`</span> must be classified by the <span class="pre">`Type`</span>.
>
> (A <span class="pre">`Type`</span> gives conditions that must be met by whatever it classifies, but when <span class="pre">`is_sufficient`</span> is false, things may meet those conditions but still not be classified by the <span class="pre">`Type`</span>. For example, a Type <span class="pre">`Car`</span> that is not sufficient could require everything it classifies to have four wheels, but not all four wheeled things would classify as cars. However, if the <span class="pre">`Type`</span> <span class="pre">`Car`</span> were sufficient, it would classify all four-wheeled things.)
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=172" class="reference external" target="_blank">8.3.3.1.10</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">is_sufficient_explicitly</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*<a href="#syside.Type.is_sufficient_explicitly" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Returns <span class="pre">`True`</span> if this <span class="pre">`Type`</span> was declared as <span class="pre">`sufficient`</span> in the textual syntax.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">multiplicity</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/Multiplicity.md" class="reference internal" title="syside.Multiplicity"><span class="pre">syside.Multiplicity</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span>*<a href="#syside.Type.multiplicity" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`multiplicity`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> An <span class="pre">`owned_member`</span> of this <span class="pre">`Type`</span> that is a <span class="pre">`Multiplicity`</span>, which constraints the cardinality of the <span class="pre">`Type`</span>. If there is no such <span class="pre">`owned_member`</span>, then the cardinality of this <span class="pre">`Type`</span> is constrained by all the <span class="pre">`Multiplicity`</span> constraints applicable to any direct supertypes.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=172" class="reference external" target="_blank">8.3.3.1.10</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">outputs</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature"><span class="pre">syside.Feature</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Type.outputs" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`output`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> All <span class="pre">`features`</span> related to this <span class="pre">`Type`</span> by <span class="pre">`FeatureMemberships`</span> that have <span class="pre">`direction`</span> <span class="pre">`out`</span> or <span class="pre">`inout`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=172" class="reference external" target="_blank">8.3.3.1.10</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned_conjugator</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/Conjugation.md" class="reference internal" title="syside.Conjugation"><span class="pre">syside.Conjugation</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span>*<a href="#syside.Type.owned_conjugator" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owned_conjugator`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> A <span class="pre">`Conjugation`</span> owned by this <span class="pre">`Type`</span> for which the <span class="pre">`Type`</span> is the <span class="pre">`original_type`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=173" class="reference external" target="_blank">8.3.3.1.10</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned_differencings</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Differencing.md" class="reference internal" title="syside.Differencing"><span class="pre">syside.Differencing</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Type.owned_differencings" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owned_differencing`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The <span class="pre">`owned_relationships`</span> of this <span class="pre">`Type`</span> that are <span class="pre">`Differencings`</span>, having this <span class="pre">`Type`</span> as their <span class="pre">`type_differenced`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=173" class="reference external" target="_blank">8.3.3.1.10</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned_directed_features</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature"><span class="pre">syside.Feature</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Type.owned_directed_features" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
The <span class="pre">`directed_features`</span> that are owned by this <span class="pre">`Type`</span>.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned_disjoinings</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Disjoining.md" class="reference internal" title="syside.Disjoining"><span class="pre">syside.Disjoining</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Type.owned_disjoinings" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owned_disjoining`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The <span class="pre">`owned_relationships`</span> of this <span class="pre">`Type`</span> that are <span class="pre">`Disjoinings`</span>, for which the <span class="pre">`Type`</span> is the <span class="pre">`type_disjoined`</span> <span class="pre">`Type`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=173" class="reference external" target="_blank">8.3.3.1.10</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned_end_features</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature"><span class="pre">syside.Feature</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Type.owned_end_features" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owned_end_feature`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> All <span class="pre">`end_features`</span> of this <span class="pre">`Type`</span> that are <span class="pre">`owned_features`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=173" class="reference external" target="_blank">8.3.3.1.10</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned_feature_memberships</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/FeatureMembership.md" class="reference internal" title="syside.FeatureMembership"><span class="pre">syside.FeatureMembership</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Type.owned_feature_memberships" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owned_feature_membership`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The <span class="pre">`owned_memberships`</span> of this <span class="pre">`Type`</span> that are <span class="pre">`FeatureMemberships`</span>, for which the <span class="pre">`Type`</span> is the <span class="pre">`owning_type`</span>. Each such <span class="pre">`FeatureMembership`</span> identifies an <span class="pre">`owned_feature`</span> of the <span class="pre">`Type`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=173" class="reference external" target="_blank">8.3.3.1.10</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned_features</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature"><span class="pre">syside.Feature</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Type.owned_features" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owned_feature`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The <span class="pre">`owned_member_features`</span> of the <span class="pre">`owned_feature_memberships`</span> of this <span class="pre">`Type`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=173" class="reference external" target="_blank">8.3.3.1.10</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned_inputs</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature"><span class="pre">syside.Feature</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Type.owned_inputs" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
The <span class="pre">`inputs`</span> that are owned by this <span class="pre">`Type`</span>.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned_intersectings</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Intersecting.md" class="reference internal" title="syside.Intersecting"><span class="pre">syside.Intersecting</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Type.owned_intersectings" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owned_intersecting`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The <span class="pre">`owned_relationships`</span> of this <span class="pre">`Type`</span> that are <span class="pre">`Intersectings`</span>, have the <span class="pre">`Type`</span> as their <span class="pre">`type_intersected`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=173" class="reference external" target="_blank">8.3.3.1.10</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned_outputs</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature"><span class="pre">syside.Feature</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Type.owned_outputs" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
The <span class="pre">`outputs`</span> that are owned by this <span class="pre">`Type`</span>.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned_specializations</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Specialization.md" class="reference internal" title="syside.Specialization"><span class="pre">syside.Specialization</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Type.owned_specializations" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owned_specialization`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The <span class="pre">`owned_relationships`</span> of this <span class="pre">`Type`</span> that are <span class="pre">`Specializations`</span>, for which the <span class="pre">`Type`</span> is the <span class="pre">`specific`</span> <span class="pre">`Type`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=173" class="reference external" target="_blank">8.3.3.1.10</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned_unionings</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Unioning.md" class="reference internal" title="syside.Unioning"><span class="pre">syside.Unioning</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Type.owned_unionings" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owned_unioning`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The <span class="pre">`owned_relationships`</span> of this <span class="pre">`Type`</span> that are <span class="pre">`Unionings`</span>, having the <span class="pre">`Type`</span> as their <span class="pre">`type_unioned`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=173" class="reference external" target="_blank">8.3.3.1.10</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">type_relationships</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/TypeRelationships.md" class="reference internal" title="syside.TypeRelationships"><span class="pre">syside.TypeRelationships</span></a>*<a href="#syside.Type.type_relationships" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
The other type, feature relationships and <span class="pre">`FeatureChainings`</span> owned by this <span class="pre">`Type`</span>.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">unioning_types</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="#syside.Type" class="reference internal" title="syside.Type"><span class="pre">syside.Type</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Type.unioning_types" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`unioning_type`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The interpretations of a <span class="pre">`Type`</span> with <span class="pre">`unioning_types`</span> are asserted to be the same as those of all the <span class="pre">`unioning_types`</span> together, which are the <span class="pre">`Types`</span> derived from the <span class="pre">`unioning_type`</span> of the <span class="pre">`owned_unionings`</span> of this <span class="pre">`Type`</span>. For example, a <span class="pre">`Classifier`</span> for people might be the union of <span class="pre">`Classifiers`</span> for all the sexes. Similarly, a feature for people’s children might be the union of features dividing them in the same ways as people in general.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=173" class="reference external" target="_blank">8.3.3.1.10</a> of the KerML specification for more details.

<span class="nerd-font"></span> **Methods**

<span class="sig-name descname"><span class="pre">conforms</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">Sequence</span><span class="p"><span class="pre">\[</span></span><span class="pre">str</span><span class="p"><span class="pre">\]</span></span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">bool</span></span></span><a href="#syside.Type.conforms" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Returns <span class="pre">`True`</span> if this <span class="pre">`Type`</span> directly or indirectly specializes another <span class="pre">`Type`</span> while following <span class="pre">`FeatureChainings`</span>.

<span class="sig-name descname"><span class="pre">conforms</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="#syside.Type" class="reference internal" title="syside.Type"><span class="pre">syside.Type</span></a></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">bool</span></span></span>  

<span class="sig-name descname"><span class="pre">direction_of</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature"><span class="pre">syside.Feature</span></a></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside.FeatureDirectionKind"><span class="pre">syside.FeatureDirectionKind</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span></span></span><a href="#syside.Type.direction_of" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Returns the direction of a <span class="pre">`Feature`</span> in this <span class="pre">`Type`</span>.

<span class="sig-name descname"><span class="pre">specializes</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">Sequence</span><span class="p"><span class="pre">\[</span></span><span class="pre">str</span><span class="p"><span class="pre">\]</span></span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">bool</span></span></span><a href="#syside.Type.specializes" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Returns <span class="pre">`True`</span> if this <span class="pre">`Type`</span> directly or indirectly specializes another <span class="pre">`Type`</span> while ignoring <span class="pre">`FeatureChainings`</span>.

<span class="sig-name descname"><span class="pre">specializes</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="#syside.Type" class="reference internal" title="syside.Type"><span class="pre">syside.Type</span></a></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">bool</span></span></span>  

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/Association.md" class="reference internal" title="syside.Association"><span class="pre"><code class="sourceCode python">syside.Association</code></span></a>

  - <a href="/python/v0.8.4/syside/Association.md" class="reference internal" title="syside.Association.related_types"><span class="pre"><code class="sourceCode python">related_types</code></span></a>

  - <a href="/python/v0.8.4/syside/Association.md" class="reference internal" title="syside.Association.source_type"><span class="pre"><code class="sourceCode python">source_type</code></span></a>

  - <a href="/python/v0.8.4/syside/Association.md" class="reference internal" title="syside.Association.target_types"><span class="pre"><code class="sourceCode python">target_types</code></span></a>

- <a href="/python/v0.8.4/syside/BoundMetaclass.md" class="reference internal" title="syside.BoundMetaclass"><span class="pre"><code class="sourceCode python">syside.BoundMetaclass</code></span></a>

  - <a href="/python/v0.8.4/syside/BoundMetaclass.md" class="reference internal" title="syside.BoundMetaclass.metaclass"><span class="pre"><code class="sourceCode python">metaclass</code></span></a>

- <a href="/python/v0.8.4/syside/Compiler.md" class="reference internal" title="syside.Compiler"><span class="pre"><code class="sourceCode python">syside.Compiler</code></span></a>

  - <a href="/python/v0.8.4/syside/Compiler.md" class="reference internal" title="syside.Compiler.evaluate"><span class="pre"><code class="sourceCode python">evaluate</code></span></a>

  - <a href="/python/v0.8.4/syside/Compiler.md" class="reference internal" title="syside.Compiler.evaluate_feature"><span class="pre"><code class="sourceCode python">evaluate_feature</code></span></a>

- <a href="/python/v0.8.4/syside/Conjugation.md" class="reference internal" title="syside.Conjugation"><span class="pre"><code class="sourceCode python">syside.Conjugation</code></span></a>

  - <a href="/python/v0.8.4/syside/Conjugation.md" class="reference internal" title="syside.Conjugation.conjugated_type"><span class="pre"><code class="sourceCode python">conjugated_type</code></span></a>

  - <a href="/python/v0.8.4/syside/Conjugation.md" class="reference internal" title="syside.Conjugation.original_type"><span class="pre"><code class="sourceCode python">original_type</code></span></a>

  - <a href="/python/v0.8.4/syside/Conjugation.md" class="reference internal" title="syside.Conjugation.owning_type"><span class="pre"><code class="sourceCode python">owning_type</code></span></a>

- <a href="/python/v0.8.4/syside/ConnectionDefinition.md" class="reference internal" title="syside.ConnectionDefinition"><span class="pre"><code class="sourceCode python">syside.ConnectionDefinition</code></span></a>

  - <a href="/python/v0.8.4/syside/ConnectionDefinition.md" class="reference internal" title="syside.ConnectionDefinition.related_types"><span class="pre"><code class="sourceCode python">related_types</code></span></a>

  - <a href="/python/v0.8.4/syside/ConnectionDefinition.md" class="reference internal" title="syside.ConnectionDefinition.source_type"><span class="pre"><code class="sourceCode python">source_type</code></span></a>

  - <a href="/python/v0.8.4/syside/ConnectionDefinition.md" class="reference internal" title="syside.ConnectionDefinition.target_types"><span class="pre"><code class="sourceCode python">target_types</code></span></a>

- <a href="/python/v0.8.4/syside/Connector.md" class="reference internal" title="syside.Connector"><span class="pre"><code class="sourceCode python">syside.Connector</code></span></a>

  - <a href="/python/v0.8.4/syside/Connector.md" class="reference internal" title="syside.Connector.default_featuring_type"><span class="pre"><code class="sourceCode python">default_featuring_type</code></span></a>

- <a href="/python/v0.8.4/syside/ConnectorAsUsage.md" class="reference internal" title="syside.ConnectorAsUsage"><span class="pre"><code class="sourceCode python">syside.ConnectorAsUsage</code></span></a>

  - <a href="/python/v0.8.4/syside/ConnectorAsUsage.md" class="reference internal" title="syside.ConnectorAsUsage.default_featuring_type"><span class="pre"><code class="sourceCode python">default_featuring_type</code></span></a>

- <a href="/python/v0.8.4/syside/Differencing.md" class="reference internal" title="syside.Differencing"><span class="pre"><code class="sourceCode python">syside.Differencing</code></span></a>

  - <a href="/python/v0.8.4/syside/Differencing.md" class="reference internal" title="syside.Differencing.differencing_type"><span class="pre"><code class="sourceCode python">differencing_type</code></span></a>

  - <a href="/python/v0.8.4/syside/Differencing.md" class="reference internal" title="syside.Differencing.type_differenced"><span class="pre"><code class="sourceCode python">type_differenced</code></span></a>

- <a href="/python/v0.8.4/syside/Disjoining.md" class="reference internal" title="syside.Disjoining"><span class="pre"><code class="sourceCode python">syside.Disjoining</code></span></a>

  - <a href="/python/v0.8.4/syside/Disjoining.md" class="reference internal" title="syside.Disjoining.disjoining_type"><span class="pre"><code class="sourceCode python">disjoining_type</code></span></a>

  - <a href="/python/v0.8.4/syside/Disjoining.md" class="reference internal" title="syside.Disjoining.owning_type"><span class="pre"><code class="sourceCode python">owning_type</code></span></a>

  - <a href="/python/v0.8.4/syside/Disjoining.md" class="reference internal" title="syside.Disjoining.type_disjoined"><span class="pre"><code class="sourceCode python">type_disjoined</code></span></a>

- <a href="/python/v0.8.4/syside/Expression.md" class="reference internal" title="syside.Expression"><span class="pre"><code class="sourceCode python">syside.Expression</code></span></a>

  - <a href="/python/v0.8.4/syside/Expression.md" class="reference internal" title="syside.Expression.cached_result_type"><span class="pre"><code class="sourceCode python">cached_result_type</code></span></a>

- <a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature"><span class="pre"><code class="sourceCode python">syside.Feature</code></span></a>

  - <a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature.end_owning_type"><span class="pre"><code class="sourceCode python">end_owning_type</code></span></a>

  - <a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature.featuring_types"><span class="pre"><code class="sourceCode python">featuring_types</code></span></a>

  - <a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature.owning_type"><span class="pre"><code class="sourceCode python">owning_type</code></span></a>

  - <a href="/python/v0.8.4/syside/Feature.md" class="reference internal" title="syside.Feature.types"><span class="pre"><code class="sourceCode python">types</code></span></a>

- <a href="/python/v0.8.4/syside/FeatureMembership.md" class="reference internal" title="syside.FeatureMembership"><span class="pre"><code class="sourceCode python">syside.FeatureMembership</code></span></a>

  - <a href="/python/v0.8.4/syside/FeatureMembership.md" class="reference internal" title="syside.FeatureMembership.owning_type"><span class="pre"><code class="sourceCode python">owning_type</code></span></a>

- <a href="/python/v0.8.4/syside/FeatureTyping.md" class="reference internal" title="syside.FeatureTyping"><span class="pre"><code class="sourceCode python">syside.FeatureTyping</code></span></a>

  - <a href="/python/v0.8.4/syside/FeatureTyping.md" class="reference internal" title="syside.FeatureTyping.type"><span class="pre"><code class="sourceCode python"><span class="bu">type</span></code></span></a>

- <a href="/python/v0.8.4/syside/FlowDefinition.md" class="reference internal" title="syside.FlowDefinition"><span class="pre"><code class="sourceCode python">syside.FlowDefinition</code></span></a>

  - <a href="/python/v0.8.4/syside/FlowDefinition.md" class="reference internal" title="syside.FlowDefinition.related_types"><span class="pre"><code class="sourceCode python">related_types</code></span></a>

  - <a href="/python/v0.8.4/syside/FlowDefinition.md" class="reference internal" title="syside.FlowDefinition.source_type"><span class="pre"><code class="sourceCode python">source_type</code></span></a>

  - <a href="/python/v0.8.4/syside/FlowDefinition.md" class="reference internal" title="syside.FlowDefinition.target_types"><span class="pre"><code class="sourceCode python">target_types</code></span></a>

- <a href="/python/v0.8.4/syside/InstantiationExpression.md" class="reference internal" title="syside.InstantiationExpression"><span class="pre"><code class="sourceCode python">syside.InstantiationExpression</code></span></a>

  - <a href="/python/v0.8.4/syside/InstantiationExpression.md" class="reference internal" title="syside.InstantiationExpression.instantiated_type"><span class="pre"><code class="sourceCode python">instantiated_type</code></span></a>

- <a href="/python/v0.8.4/syside/Intersecting.md" class="reference internal" title="syside.Intersecting"><span class="pre"><code class="sourceCode python">syside.Intersecting</code></span></a>

  - <a href="/python/v0.8.4/syside/Intersecting.md" class="reference internal" title="syside.Intersecting.intersecting_type"><span class="pre"><code class="sourceCode python">intersecting_type</code></span></a>

  - <a href="/python/v0.8.4/syside/Intersecting.md" class="reference internal" title="syside.Intersecting.type_intersected"><span class="pre"><code class="sourceCode python">type_intersected</code></span></a>

- <a href="/python/v0.8.4/syside/PortConjugation.md" class="reference internal" title="syside.PortConjugation"><span class="pre"><code class="sourceCode python">syside.PortConjugation</code></span></a>

  - <a href="/python/v0.8.4/syside/PortConjugation.md" class="reference internal" title="syside.PortConjugation.conjugated_port_definition"><span class="pre"><code class="sourceCode python">conjugated_port_definition</code></span></a>

- <a href="/python/v0.8.4/syside/Specialization.md" class="reference internal" title="syside.Specialization"><span class="pre"><code class="sourceCode python">syside.Specialization</code></span></a>

  - <a href="/python/v0.8.4/syside/Specialization.md" class="reference internal" title="syside.Specialization.general"><span class="pre"><code class="sourceCode python">general</code></span></a>

  - <a href="/python/v0.8.4/syside/Specialization.md" class="reference internal" title="syside.Specialization.owning_type"><span class="pre"><code class="sourceCode python">owning_type</code></span></a>

  - <a href="/python/v0.8.4/syside/Specialization.md" class="reference internal" title="syside.Specialization.specific"><span class="pre"><code class="sourceCode python">specific</code></span></a>

- <a href="/python/v0.8.4/syside/Stdlib.md" class="reference internal" title="syside.Stdlib"><span class="pre"><code class="sourceCode python">syside.Stdlib</code></span></a>

  - <a href="/python/v0.8.4/syside/Stdlib.md" class="reference internal" title="syside.Stdlib.anything"><span class="pre"><code class="sourceCode python">anything</code></span></a>

  - <a href="/python/v0.8.4/syside/Stdlib.md" class="reference internal" title="syside.Stdlib.array"><span class="pre"><code class="sourceCode python">array</code></span></a>

  - <a href="/python/v0.8.4/syside/Stdlib.md" class="reference internal" title="syside.Stdlib.boolean"><span class="pre"><code class="sourceCode python">boolean</code></span></a>

  - <a href="/python/v0.8.4/syside/Stdlib.md" class="reference internal" title="syside.Stdlib.complex"><span class="pre"><code class="sourceCode python"><span class="bu">complex</span></code></span></a>

  - <a href="/python/v0.8.4/syside/Stdlib.md" class="reference internal" title="syside.Stdlib.implicit_supertype_for"><span class="pre"><code class="sourceCode python">implicit_supertype_for</code></span></a>

  - <a href="/python/v0.8.4/syside/Stdlib.md" class="reference internal" title="syside.Stdlib.implicit_supertypes"><span class="pre"><code class="sourceCode python">implicit_supertypes</code></span></a>

  - <a href="/python/v0.8.4/syside/Stdlib.md" class="reference internal" title="syside.Stdlib.integer"><span class="pre"><code class="sourceCode python">integer</code></span></a>

  - <a href="/python/v0.8.4/syside/Stdlib.md" class="reference internal" title="syside.Stdlib.literal_natural"><span class="pre"><code class="sourceCode python">literal_natural</code></span></a>

  - <a href="/python/v0.8.4/syside/Stdlib.md" class="reference internal" title="syside.Stdlib.literal_positive"><span class="pre"><code class="sourceCode python">literal_positive</code></span></a>

  - <a href="/python/v0.8.4/syside/Stdlib.md" class="reference internal" title="syside.Stdlib.literal_rational"><span class="pre"><code class="sourceCode python">literal_rational</code></span></a>

  - <a href="/python/v0.8.4/syside/Stdlib.md" class="reference internal" title="syside.Stdlib.literal_string"><span class="pre"><code class="sourceCode python">literal_string</code></span></a>

  - <a href="/python/v0.8.4/syside/Stdlib.md" class="reference internal" title="syside.Stdlib.metaobject"><span class="pre"><code class="sourceCode python">metaobject</code></span></a>

  - <a href="/python/v0.8.4/syside/Stdlib.md" class="reference internal" title="syside.Stdlib.number"><span class="pre"><code class="sourceCode python">number</code></span></a>

  - <a href="/python/v0.8.4/syside/Stdlib.md" class="reference internal" title="syside.Stdlib.numerical_value"><span class="pre"><code class="sourceCode python">numerical_value</code></span></a>

  - <a href="/python/v0.8.4/syside/Stdlib.md" class="reference internal" title="syside.Stdlib.ordered_collection"><span class="pre"><code class="sourceCode python">ordered_collection</code></span></a>

  - <a href="/python/v0.8.4/syside/Stdlib.md" class="reference internal" title="syside.Stdlib.real"><span class="pre"><code class="sourceCode python">real</code></span></a>

  - <a href="/python/v0.8.4/syside/Stdlib.md" class="reference internal" title="syside.Stdlib.scalar_value"><span class="pre"><code class="sourceCode python">scalar_value</code></span></a>

  - <a href="/python/v0.8.4/syside/Stdlib.md" class="reference internal" title="syside.Stdlib.semantic_metadata"><span class="pre"><code class="sourceCode python">semantic_metadata</code></span></a>

  - <a href="/python/v0.8.4/syside/Stdlib.md" class="reference internal" title="syside.Stdlib.tensor_measurement_reference"><span class="pre"><code class="sourceCode python">tensor_measurement_reference</code></span></a>

  - <a href="/python/v0.8.4/syside/Stdlib.md" class="reference internal" title="syside.Stdlib.tensor_quantity_value"><span class="pre"><code class="sourceCode python">tensor_quantity_value</code></span></a>

  - <a href="/python/v0.8.4/syside/Stdlib.md" class="reference internal" title="syside.Stdlib.unit_conversion"><span class="pre"><code class="sourceCode python">unit_conversion</code></span></a>

  - <a href="/python/v0.8.4/syside/Stdlib.md" class="reference internal" title="syside.Stdlib.unit_prefix"><span class="pre"><code class="sourceCode python">unit_prefix</code></span></a>

- <a href="#syside.Type" class="reference internal" title="syside.Type"><span class="pre"><code class="sourceCode python">syside.Type</code></span></a>

  - <a href="#syside.Type.STD" class="reference internal" title="syside.Type.STD"><span class="pre"><code class="sourceCode python">STD</code></span></a>

  - <a href="#syside.Type.conforms" class="reference internal" title="syside.Type.conforms"><span class="pre"><code class="sourceCode python">conforms</code></span></a>

  - <a href="#syside.Type.differencing_types" class="reference internal" title="syside.Type.differencing_types"><span class="pre"><code class="sourceCode python">differencing_types</code></span></a>

  - <a href="#syside.Type.disjoining_types" class="reference internal" title="syside.Type.disjoining_types"><span class="pre"><code class="sourceCode python">disjoining_types</code></span></a>

  - <a href="#syside.Type.intersecting_types" class="reference internal" title="syside.Type.intersecting_types"><span class="pre"><code class="sourceCode python">intersecting_types</code></span></a>

  - <a href="#syside.Type.specializes" class="reference internal" title="syside.Type.specializes"><span class="pre"><code class="sourceCode python">specializes</code></span></a>

  - <a href="#syside.Type.unioning_types" class="reference internal" title="syside.Type.unioning_types"><span class="pre"><code class="sourceCode python">unioning_types</code></span></a>

- <a href="/python/v0.8.4/syside/TypeFeaturing.md" class="reference internal" title="syside.TypeFeaturing"><span class="pre"><code class="sourceCode python">syside.TypeFeaturing</code></span></a>

  - <a href="/python/v0.8.4/syside/TypeFeaturing.md" class="reference internal" title="syside.TypeFeaturing.featuring_type"><span class="pre"><code class="sourceCode python">featuring_type</code></span></a>

- <a href="/python/v0.8.4/syside/TypeGuard.md" class="reference internal" title="syside.TypeGuard"><span class="pre"><code class="sourceCode python">syside.TypeGuard</code></span></a>

  - <a href="/python/v0.8.4/syside/TypeGuard.md" class="reference internal" title="syside.TypeGuard.value"><span class="pre"><code class="sourceCode python">value</code></span></a>

- <a href="/python/v0.8.4/syside/Unioning.md" class="reference internal" title="syside.Unioning"><span class="pre"><code class="sourceCode python">syside.Unioning</code></span></a>

  - <a href="/python/v0.8.4/syside/Unioning.md" class="reference internal" title="syside.Unioning.type_unioned"><span class="pre"><code class="sourceCode python">type_unioned</code></span></a>

  - <a href="/python/v0.8.4/syside/Unioning.md" class="reference internal" title="syside.Unioning.unioning_type"><span class="pre"><code class="sourceCode python">unioning_type</code></span></a>

</div>

</div>
