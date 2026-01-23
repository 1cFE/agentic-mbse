<div id="namespace-sysml" class="section">

# Namespace <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span><a href="#namespace-sysml" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">Namespace</span></span><a href="#syside.Namespace" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`Namespace`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> A <span class="pre">`Namespace`</span> is an <span class="pre">`Element`</span> that contains other <span class="pre">`Elements`</span>, known as its <span class="pre">`members`</span>, via <span class="pre">`Membership`</span> <span class="pre">`Relationships`</span> with those <span class="pre">`Elements`</span>. The <span class="pre">`members`</span> of a <span class="pre">`Namespace`</span> may be owned by the <span class="pre">`Namespace`</span>, aliased in the <span class="pre">`Namespace`</span>, or imported into the <span class="pre">`Namespace`</span> via <span class="pre">`Import`</span> <span class="pre">`Relationships`</span>.
>
> A <span class="pre">`Namespace`</span> can provide names for its <span class="pre">`members`</span> via the <span class="pre">`member_names`</span> and <span class="pre">`member_short_names`</span> specified by the <span class="pre">`Memberships`</span> in the <span class="pre">`Namespace`</span>. If a <span class="pre">`Membership`</span> specifies a <span class="pre">`member_name`</span> and/or <span class="pre">`member_short_name`</span>, then those are names of the corresponding <span class="pre">`member_element`</span> relative to the <span class="pre">`Namespace`</span>. For an <span class="pre">`OwningMembership`</span>, the <span class="pre">`owned_member_name`</span> and <span class="pre">`owned_member_short_name`</span> are given by the <span class="pre">`Element`</span> <span class="pre">`name`</span> and <span class="pre">`short_name`</span>. Note that the same <span class="pre">`Element`</span> may be the <span class="pre">`member_element`</span> of multiple <span class="pre">`Memberships`</span> in a <span class="pre">`Namespace`</span> (though it may be owned at most once), each of which may define a separate alias for the <span class="pre">`Element`</span> relative to the <span class="pre">`Namespace`</span>.
>
> </div>

For language description, see section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=46" class="reference external" target="_blank">7.2.5</a> of the KerML specification. For more details on the model, see section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=156" class="reference external" target="_blank">8.3.2.4.5</a> of the KerML specification.

<div class="align-center" align="center">

<img src="data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iZ3JhcGh2aXoiIHN0eWxlPSJ3aWR0aDogNS43NXJlbTtoZWlnaHQ6IDExLjc1cmVtOyIgdmlld2JveD0iMC4wMCAwLjAwIDkyLjAwIDE4OC4wMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGcgY2xhc3M9ImdyYXBoIiBpZD0iZ3JhcGgwIiB0cmFuc2Zvcm09InNjYWxlKDEgMSkgcm90YXRlKDApIHRyYW5zbGF0ZSg0IDE4NCkiPgo8dGl0bGU+JTM8L3RpdGxlPgo8ZyBjbGFzcz0ibm9kZSIgaWQ9Im5vZGUxIj4KPHRpdGxlPk5hbWVzcGFjZTwvdGl0bGU+CjxnIGlkPSJhX25vZGUxIj48YSBocmVmPSIjc3lzaWRlLk5hbWVzcGFjZSI+Cjxwb2x5Z29uIHBvaW50cz0iODQsLTM2IDAsLTM2IDAsMCA4NCwwIDg0LC0zNiIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtYmctY29sb3IpO3N0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1mZy1jb2xvcik7Ij48L3BvbHlnb24+Cjx0ZXh0IGZvbnQtZmFtaWx5PSJMZXhlbmQiIGZvbnQtc2l6ZT0iMTIuMDAiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1jb2RlLWZnLWNvbG9yKTstLW1kLWdyYXBodml6LWhvdmVyLWNvbG9yOiB2YXIoLS1tZC1ncmFwaHZpei1hLWhvdmVyLWNvbG9yKTsiIHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjQyIiB5PSItMTQuMiI+TmFtZXNwYWNlPC90ZXh0Pgo8dGl0bGU+c3lzaWRlLk5hbWVzcGFjZTwvdGl0bGU+PC9hPgo8L2c+CjwvZz4KPGcgY2xhc3M9Im5vZGUiIGlkPSJub2RlMiI+Cjx0aXRsZT5FbGVtZW50PC90aXRsZT4KPGcgaWQ9ImFfbm9kZTIiPjxhIGhyZWY9Ii9weXRob24vdjAuOC40L3N5c2lkZS9FbGVtZW50Lm1kIj4KPHBvbHlnb24gcG9pbnRzPSI3MywtMTA4IDExLC0xMDggMTEsLTcyIDczLC03MiA3MywtMTA4IiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1iZy1jb2xvcik7c3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1ub2RlLWZnLWNvbG9yKTsiPjwvcG9seWdvbj4KPHRleHQgZm9udC1mYW1pbHk9IkxleGVuZCIgZm9udC1zaXplPSIxMi4wMCIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWNvZGUtZmctY29sb3IpOy0tbWQtZ3JhcGh2aXotaG92ZXItY29sb3I6IHZhcigtLW1kLWdyYXBodml6LWEtaG92ZXItY29sb3IpOyIgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iNDIiIHk9Ii04Ni4yIj5FbGVtZW50PC90ZXh0Pgo8dGl0bGU+c3lzaWRlLkVsZW1lbnQ8L3RpdGxlPjwvYT4KPC9nPgo8L2c+CjxnIGNsYXNzPSJlZGdlIiBpZD0iZWRnZTEiPgo8dGl0bGU+RWxlbWVudC0mZ3Q7TmFtZXNwYWNlPC90aXRsZT4KPHBhdGggZD0iTTQyLC03MS43QzQyLC02My45OCA0MiwtNTQuNzEgNDIsLTQ2LjExIiBmaWxsPSJub25lIiBzdHlsZT0ic3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1lZGdlLWNvbG9yKTsiIC8+Cjxwb2x5Z29uIHBvaW50cz0iNDUuNSwtNDYuMSA0MiwtMzYuMSAzOC41LC00Ni4xIDQ1LjUsLTQ2LjEiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1ncmFwaHZpei1lZGdlLWNvbG9yKTtzdHJva2U6IHZhcigtLW1kLWdyYXBodml6LWVkZ2UtY29sb3IpOyI+PC9wb2x5Z29uPgo8L2c+CjxnIGNsYXNzPSJub2RlIiBpZD0ibm9kZTMiPgo8dGl0bGU+QXN0Tm9kZTwvdGl0bGU+CjxnIGlkPSJhX25vZGUzIj48YSBocmVmPSIvcHl0aG9uL3YwLjguNC9zeXNpZGUvQXN0Tm9kZS5tZCI+Cjxwb2x5Z29uIHBvaW50cz0iNzUsLTE4MCA5LC0xODAgOSwtMTQ0IDc1LC0xNDQgNzUsLTE4MCIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtYmctY29sb3IpO3N0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1mZy1jb2xvcik7Ij48L3BvbHlnb24+Cjx0ZXh0IGZvbnQtZmFtaWx5PSJMZXhlbmQiIGZvbnQtc2l6ZT0iMTIuMDAiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1jb2RlLWZnLWNvbG9yKTstLW1kLWdyYXBodml6LWhvdmVyLWNvbG9yOiB2YXIoLS1tZC1ncmFwaHZpei1hLWhvdmVyLWNvbG9yKTsiIHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjQyIiB5PSItMTU4LjIiPkFzdE5vZGU8L3RleHQ+Cjx0aXRsZT5zeXNpZGUuQXN0Tm9kZTwvdGl0bGU+PC9hPgo8L2c+CjwvZz4KPGcgY2xhc3M9ImVkZ2UiIGlkPSJlZGdlMiI+Cjx0aXRsZT5Bc3ROb2RlLSZndDtFbGVtZW50PC90aXRsZT4KPHBhdGggZD0iTTQyLC0xNDMuN0M0MiwtMTM1Ljk4IDQyLC0xMjYuNzEgNDIsLTExOC4xMSIgZmlsbD0ibm9uZSIgc3R5bGU9InN0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotZWRnZS1jb2xvcik7IiAvPgo8cG9seWdvbiBwb2ludHM9IjQ1LjUsLTExOC4xIDQyLC0xMDguMSAzOC41LC0xMTguMSA0NS41LC0xMTguMSIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWdyYXBodml6LWVkZ2UtY29sb3IpO3N0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotZWRnZS1jb2xvcik7Ij48L3BvbHlnb24+CjwvZz4KPC9nPgo8L3N2Zz4=" class="graphviz" />

</div>

<span class="sd-summary-text"><span class="nerd-font"></span> Children</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/Package.md" class="reference internal" title="syside.Package"><span class="pre"><code class="sourceCode python">Package</code></span></a>

  - <a href="/python/v0.8.4/syside/LibraryPackage.md" class="reference internal" title="syside.LibraryPackage"><span class="pre"><code class="sourceCode python">LibraryPackage</code></span></a>

- <a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type"><span class="pre"><code class="sourceCode python">Type</code></span></a>

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

<span class="sd-summary-text">Members defined in <a href="#syside.Namespace" class="reference internal" title="syside.Namespace"><span class="pre"><code class="sourceCode python">Namespace</code></span></a> (12 members)</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |  |
|----|----|----|----|
| <span class="nerd-font"></span> | <a href="#syside.Namespace.STD" class="reference internal" title="syside.Namespace.STD"><span class="pre"><code class="sourceCode python">STD</code></span></a> | <span class="pre">`R`</span> |  |
| <span class="nerd-font"></span> | <a href="#syside.Namespace.children" class="reference internal" title="syside.Namespace.children"><span class="pre"><code class="sourceCode python">children</code></span></a> | <span class="pre">`R`</span> | The elements enclosed by curly brackets in textual syntax. |
| <span class="nerd-font"></span> | <a href="#syside.Namespace.imported_memberships" class="reference internal" title="syside.Namespace.imported_memberships"><span class="pre"><code class="sourceCode python">imported_memberships</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`imported_membership`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Namespace.members" class="reference internal" title="syside.Namespace.members"><span class="pre"><code class="sourceCode python">members</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`member`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Namespace.memberships" class="reference internal" title="syside.Namespace.memberships"><span class="pre"><code class="sourceCode python">memberships</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`membership`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Namespace.owned_imports" class="reference internal" title="syside.Namespace.owned_imports"><span class="pre"><code class="sourceCode python">owned_imports</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_import`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Namespace.owned_members" class="reference internal" title="syside.Namespace.owned_members"><span class="pre"><code class="sourceCode python">owned_members</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_member`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Namespace.owned_memberships" class="reference internal" title="syside.Namespace.owned_memberships"><span class="pre"><code class="sourceCode python">owned_memberships</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_membership`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Namespace.prefixes" class="reference internal" title="syside.Namespace.prefixes"><span class="pre"><code class="sourceCode python">prefixes</code></span></a> | <span class="pre">`R`</span> | Metadata prefixes, prefixed with <span class="pre">`#`</span> in textual syntax. |
| <span class="nerd-font"></span> | <a href="#syside.Namespace.__getitem__" class="reference internal" title="syside.Namespace.__getitem__"><span class="pre"><code class="sourceCode python"><span class="fu">__getitem__</span></code></span></a> |  | Access owned named members by name. Throws <span class="pre">`KeyError`</span> if a member with such name does not exist. |
| <span class="nerd-font"></span> | <a href="#syside.Namespace.get_member" class="reference internal" title="syside.Namespace.get_member"><span class="pre"><code class="sourceCode python">get_member</code></span></a> |  | Non-throwing variant of <span class="pre">`__getitem__`</span>. Returns None if a named member was not found. |
| <span class="nerd-font"></span> | <a href="#syside.Namespace.get_membership" class="reference internal" title="syside.Namespace.get_membership"><span class="pre"><code class="sourceCode python">get_membership</code></span></a> |  | Access owned memberships by name. Returns None if an owned member or membership with such name does not exist. |

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

<span class="sig-name descname"><span class="pre">STD</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><span class="pre">type</span><span class="p"><span class="pre">\[</span></span><a href="#syside.Namespace" class="reference internal" title="syside.Namespace"><span class="pre">syside.Namespace</span></a><span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="p"><span class="pre">...</span></span><span class="p"><span class="pre">\]</span></span><span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">()</span>*<a href="#syside.Namespace.STD" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">children</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/NamespaceBody.md" class="reference internal" title="syside.NamespaceBody"><span class="pre">syside.NamespaceBody</span></a>*<a href="#syside.Namespace.children" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
The elements enclosed by curly brackets in textual syntax.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">imported_memberships</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Membership.md" class="reference internal" title="syside.Membership"><span class="pre">syside.Membership</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Namespace.imported_memberships" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`imported_membership`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The <span class="pre">`Memberships`</span> in this <span class="pre">`Namespace`</span> that result from the <span class="pre">`owned_imports`</span> of this <span class="pre">`Namespace`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=156" class="reference external" target="_blank">8.3.2.4.5</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">members</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element"><span class="pre">syside.Element</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Namespace.members" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`member`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The set of all member <span class="pre">`Elements`</span> of this <span class="pre">`Namespace`</span>, which are the <span class="pre">`member_elements`</span> of all <span class="pre">`memberships`</span> of the <span class="pre">`Namespace`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=156" class="reference external" target="_blank">8.3.2.4.5</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">memberships</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Membership.md" class="reference internal" title="syside.Membership"><span class="pre">syside.Membership</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Namespace.memberships" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`membership`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> All <span class="pre">`Memberships`</span> in this <span class="pre">`Namespace`</span>, including (at least) the union of <span class="pre">`owned_memberships`</span> and <span class="pre">`imported_memberships`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=157" class="reference external" target="_blank">8.3.2.4.5</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned_imports</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Import.md" class="reference internal" title="syside.Import"><span class="pre">syside.Import</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Namespace.owned_imports" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owned_import`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The <span class="pre">`owned_relationships`</span> of this <span class="pre">`Namespace`</span> that are <span class="pre">`Imports`</span>, for which the <span class="pre">`Namespace`</span> is the <span class="pre">`import_owning_namespace`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=157" class="reference external" target="_blank">8.3.2.4.5</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned_members</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element"><span class="pre">syside.Element</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Namespace.owned_members" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owned_member`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The owned <span class="pre">`members`</span> of this <span class="pre">`Namespace`</span>, which are the <span class="pre">`owned_member_elements`</span> of the <span class="pre">`owned_memberships`</span> of the <span class="pre">`Namespace`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=157" class="reference external" target="_blank">8.3.2.4.5</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned_memberships</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Membership.md" class="reference internal" title="syside.Membership"><span class="pre">syside.Membership</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Namespace.owned_memberships" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owned_membership`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The <span class="pre">`owned_relationships`</span> of this <span class="pre">`Namespace`</span> that are <span class="pre">`Memberships`</span>, for which the <span class="pre">`Namespace`</span> is the <span class="pre">`membership_owning_namespace`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=157" class="reference external" target="_blank">8.3.2.4.5</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">prefixes</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/NamespacePrefixes.md" class="reference internal" title="syside.NamespacePrefixes"><span class="pre">syside.NamespacePrefixes</span></a>*<a href="#syside.Namespace.prefixes" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Metadata prefixes, prefixed with <span class="pre">`#`</span> in textual syntax.

<span class="nerd-font"></span> **Methods**

<span class="sig-name descname"><span class="pre">\_\_getitem\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element"><span class="pre">syside.Element</span></a></span></span><a href="#syside.Namespace.__getitem__" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Access owned named members by name. Throws <span class="pre">`KeyError`</span> if a member with such name does not exist.

<span class="sig-name descname"><span class="pre">get_member</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element"><span class="pre">syside.Element</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span></span></span><a href="#syside.Namespace.get_member" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Non-throwing variant of <span class="pre">`__getitem__`</span>. Returns None if a named member was not found.

<span class="sig-name descname"><span class="pre">get_member</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg0</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="n"><span class="pre">arg1</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element"><span class="pre">syside.Element</span></a></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element"><span class="pre">syside.Element</span></a></span></span>  
Overload for <span class="pre">`get_member`</span> that returns the last argument if a member was not found.

<span class="sig-name descname"><span class="pre">get_membership</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="/python/v0.8.4/syside/Membership.md" class="reference internal" title="syside.Membership"><span class="pre">syside.Membership</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span></span></span><a href="#syside.Namespace.get_membership" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Access owned memberships by name. Returns None if an owned member or membership with such name does not exist.

<span class="sig-name descname"><span class="pre">get_membership</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg0</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="n"><span class="pre">arg1</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/Membership.md" class="reference internal" title="syside.Membership"><span class="pre">syside.Membership</span></a></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="/python/v0.8.4/syside/Membership.md" class="reference internal" title="syside.Membership"><span class="pre">syside.Membership</span></a></span></span>  
Overload for <span class="pre">`get_membership`</span> that returns the last argument if a member was not found.

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/Document.md" class="reference internal" title="syside.Document"><span class="pre"><code class="sourceCode python">syside.Document</code></span></a>

  - <a href="/python/v0.8.4/syside/Document.md" class="reference internal" title="syside.Document.root_node"><span class="pre"><code class="sourceCode python">root_node</code></span></a>

- <a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element"><span class="pre"><code class="sourceCode python">syside.Element</code></span></a>

  - <a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element.owning_namespace"><span class="pre"><code class="sourceCode python">owning_namespace</code></span></a>

- <a href="/python/v0.8.4/syside/Import.md" class="reference internal" title="syside.Import"><span class="pre"><code class="sourceCode python">syside.Import</code></span></a>

  - <a href="/python/v0.8.4/syside/Import.md" class="reference internal" title="syside.Import.import_owning_namespace"><span class="pre"><code class="sourceCode python">import_owning_namespace</code></span></a>

  - <a href="/python/v0.8.4/syside/Import.md" class="reference internal" title="syside.Import.import_target"><span class="pre"><code class="sourceCode python">import_target</code></span></a>

- <a href="/python/v0.8.4/syside/Membership.md" class="reference internal" title="syside.Membership"><span class="pre"><code class="sourceCode python">syside.Membership</code></span></a>

  - <a href="/python/v0.8.4/syside/Membership.md" class="reference internal" title="syside.Membership.membership_owning_namespace"><span class="pre"><code class="sourceCode python">membership_owning_namespace</code></span></a>

- <a href="#syside.Namespace" class="reference internal" title="syside.Namespace"><span class="pre"><code class="sourceCode python">syside.Namespace</code></span></a>

  - <a href="#syside.Namespace.STD" class="reference internal" title="syside.Namespace.STD"><span class="pre"><code class="sourceCode python">STD</code></span></a>

- <a href="/python/v0.8.4/syside/NamespaceImport.md" class="reference internal" title="syside.NamespaceImport"><span class="pre"><code class="sourceCode python">syside.NamespaceImport</code></span></a>

  - <a href="/python/v0.8.4/syside/NamespaceImport.md" class="reference internal" title="syside.NamespaceImport.imported_namespace"><span class="pre"><code class="sourceCode python">imported_namespace</code></span></a>

- <a href="/python/v0.8.4/syside/experimental/viz//README.md" class="reference internal" title="syside.experimental.viz"><span class="pre"><code class="sourceCode python">syside.experimental.viz</code></span></a>

  - <a href="/python/v0.8.4/syside/experimental/viz//README.md" class="reference internal" title="syside.experimental.viz.transform_to"><span class="pre"><code class="sourceCode python">transform_to</code></span></a>

</div>

</div>
