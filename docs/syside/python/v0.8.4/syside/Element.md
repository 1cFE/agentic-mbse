<div id="element-sysml" class="section">

# Element <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span><a href="#element-sysml" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">Element</span></span><a href="#syside.Element" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`Element`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> An <span class="pre">`Element`</span> is a constituent of a model that is uniquely identified relative to all other <span class="pre">`Elements`</span>. It can have <span class="pre">`Relationships`</span> with other <span class="pre">`Elements`</span>. Some of these <span class="pre">`Relationships`</span> might imply ownership of other <span class="pre">`Elements`</span>, which means that if an <span class="pre">`Element`</span> is deleted from a model, then so are all the <span class="pre">`Elements`</span> that it owns.
>
> </div>

For language description, see section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=41" class="reference external" target="_blank">7.2.2</a> of the KerML specification. For more details on the model, see section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=138" class="reference external" target="_blank">8.3.2.1.2</a> of the KerML specification.

<div class="align-center" align="center">

<img src="data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iZ3JhcGh2aXoiIHN0eWxlPSJ3aWR0aDogNC42MjVyZW07aGVpZ2h0OiA3LjI1cmVtOyIgdmlld2JveD0iMC4wMCAwLjAwIDc0LjAwIDExNi4wMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGcgY2xhc3M9ImdyYXBoIiBpZD0iZ3JhcGgwIiB0cmFuc2Zvcm09InNjYWxlKDEgMSkgcm90YXRlKDApIHRyYW5zbGF0ZSg0IDExMikiPgo8dGl0bGU+JTM8L3RpdGxlPgo8ZyBjbGFzcz0ibm9kZSIgaWQ9Im5vZGUxIj4KPHRpdGxlPkVsZW1lbnQ8L3RpdGxlPgo8ZyBpZD0iYV9ub2RlMSI+PGEgaHJlZj0iI3N5c2lkZS5FbGVtZW50Ij4KPHBvbHlnb24gcG9pbnRzPSI2NCwtMzYgMiwtMzYgMiwwIDY0LDAgNjQsLTM2IiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1iZy1jb2xvcik7c3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1ub2RlLWZnLWNvbG9yKTsiPjwvcG9seWdvbj4KPHRleHQgZm9udC1mYW1pbHk9IkxleGVuZCIgZm9udC1zaXplPSIxMi4wMCIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWNvZGUtZmctY29sb3IpOy0tbWQtZ3JhcGh2aXotaG92ZXItY29sb3I6IHZhcigtLW1kLWdyYXBodml6LWEtaG92ZXItY29sb3IpOyIgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iMzMiIHk9Ii0xNC4yIj5FbGVtZW50PC90ZXh0Pgo8dGl0bGU+c3lzaWRlLkVsZW1lbnQ8L3RpdGxlPjwvYT4KPC9nPgo8L2c+CjxnIGNsYXNzPSJub2RlIiBpZD0ibm9kZTIiPgo8dGl0bGU+QXN0Tm9kZTwvdGl0bGU+CjxnIGlkPSJhX25vZGUyIj48YSBocmVmPSIvcHl0aG9uL3YwLjguNC9zeXNpZGUvQXN0Tm9kZS5tZCI+Cjxwb2x5Z29uIHBvaW50cz0iNjYsLTEwOCAwLC0xMDggMCwtNzIgNjYsLTcyIDY2LC0xMDgiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1ncmFwaHZpei1ub2RlLWJnLWNvbG9yKTtzdHJva2U6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtZmctY29sb3IpOyI+PC9wb2x5Z29uPgo8dGV4dCBmb250LWZhbWlseT0iTGV4ZW5kIiBmb250LXNpemU9IjEyLjAwIiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtY29kZS1mZy1jb2xvcik7LS1tZC1ncmFwaHZpei1ob3Zlci1jb2xvcjogdmFyKC0tbWQtZ3JhcGh2aXotYS1ob3Zlci1jb2xvcik7IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSIzMyIgeT0iLTg2LjIiPkFzdE5vZGU8L3RleHQ+Cjx0aXRsZT5zeXNpZGUuQXN0Tm9kZTwvdGl0bGU+PC9hPgo8L2c+CjwvZz4KPGcgY2xhc3M9ImVkZ2UiIGlkPSJlZGdlMSI+Cjx0aXRsZT5Bc3ROb2RlLSZndDtFbGVtZW50PC90aXRsZT4KPHBhdGggZD0iTTMzLC03MS43QzMzLC02My45OCAzMywtNTQuNzEgMzMsLTQ2LjExIiBmaWxsPSJub25lIiBzdHlsZT0ic3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1lZGdlLWNvbG9yKTsiIC8+Cjxwb2x5Z29uIHBvaW50cz0iMzYuNSwtNDYuMSAzMywtMzYuMSAyOS41LC00Ni4xIDM2LjUsLTQ2LjEiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1ncmFwaHZpei1lZGdlLWNvbG9yKTtzdHJva2U6IHZhcigtLW1kLWdyYXBodml6LWVkZ2UtY29sb3IpOyI+PC9wb2x5Z29uPgo8L2c+CjwvZz4KPC9zdmc+" class="graphviz" />

</div>

<span class="sd-summary-text"><span class="nerd-font"></span> Children</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/AnnotatingElement.md" class="reference internal" title="syside.AnnotatingElement"><span class="pre"><code class="sourceCode python">AnnotatingElement</code></span></a>

  - <a href="/python/v0.8.4/syside/Comment.md" class="reference internal" title="syside.Comment"><span class="pre"><code class="sourceCode python">Comment</code></span></a>

    - <a href="/python/v0.8.4/syside/Documentation.md" class="reference internal" title="syside.Documentation"><span class="pre"><code class="sourceCode python">Documentation</code></span></a>

  - <a href="/python/v0.8.4/syside/TextualRepresentation.md" class="reference internal" title="syside.TextualRepresentation"><span class="pre"><code class="sourceCode python">TextualRepresentation</code></span></a>

- <a href="/python/v0.8.4/syside/Namespace.md" class="reference internal" title="syside.Namespace"><span class="pre"><code class="sourceCode python">Namespace</code></span></a>

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

- <a href="/python/v0.8.4/syside/Relationship.md" class="reference internal" title="syside.Relationship"><span class="pre"><code class="sourceCode python">Relationship</code></span></a>

  - <a href="/python/v0.8.4/syside/Annotation.md" class="reference internal" title="syside.Annotation"><span class="pre"><code class="sourceCode python">Annotation</code></span></a>

  - <a href="/python/v0.8.4/syside/Conjugation.md" class="reference internal" title="syside.Conjugation"><span class="pre"><code class="sourceCode python">Conjugation</code></span></a>

    - <a href="/python/v0.8.4/syside/PortConjugation.md" class="reference internal" title="syside.PortConjugation"><span class="pre"><code class="sourceCode python">PortConjugation</code></span></a>

  - <a href="/python/v0.8.4/syside/Dependency.md" class="reference internal" title="syside.Dependency"><span class="pre"><code class="sourceCode python">Dependency</code></span></a>

  - <a href="/python/v0.8.4/syside/Differencing.md" class="reference internal" title="syside.Differencing"><span class="pre"><code class="sourceCode python">Differencing</code></span></a>

  - <a href="/python/v0.8.4/syside/Disjoining.md" class="reference internal" title="syside.Disjoining"><span class="pre"><code class="sourceCode python">Disjoining</code></span></a>

  - <a href="/python/v0.8.4/syside/FeatureChaining.md" class="reference internal" title="syside.FeatureChaining"><span class="pre"><code class="sourceCode python">FeatureChaining</code></span></a>

  - <a href="/python/v0.8.4/syside/FeatureInverting.md" class="reference internal" title="syside.FeatureInverting"><span class="pre"><code class="sourceCode python">FeatureInverting</code></span></a>

  - <a href="/python/v0.8.4/syside/Import.md" class="reference internal" title="syside.Import"><span class="pre"><code class="sourceCode python">Import</code></span></a>

    - <a href="/python/v0.8.4/syside/Expose.md" class="reference internal" title="syside.Expose"><span class="pre"><code class="sourceCode python">Expose</code></span></a>

    - <a href="/python/v0.8.4/syside/MembershipImport.md" class="reference internal" title="syside.MembershipImport"><span class="pre"><code class="sourceCode python">MembershipImport</code></span></a>

      - <a href="/python/v0.8.4/syside/MembershipExpose.md" class="reference internal" title="syside.MembershipExpose"><span class="pre"><code class="sourceCode python">MembershipExpose</code></span></a>

    - <a href="/python/v0.8.4/syside/NamespaceImport.md" class="reference internal" title="syside.NamespaceImport"><span class="pre"><code class="sourceCode python">NamespaceImport</code></span></a>

      - <a href="/python/v0.8.4/syside/NamespaceExpose.md" class="reference internal" title="syside.NamespaceExpose"><span class="pre"><code class="sourceCode python">NamespaceExpose</code></span></a>

  - <a href="/python/v0.8.4/syside/Intersecting.md" class="reference internal" title="syside.Intersecting"><span class="pre"><code class="sourceCode python">Intersecting</code></span></a>

  - <a href="/python/v0.8.4/syside/Membership.md" class="reference internal" title="syside.Membership"><span class="pre"><code class="sourceCode python">Membership</code></span></a>

    - <a href="/python/v0.8.4/syside/OwningMembership.md" class="reference internal" title="syside.OwningMembership"><span class="pre"><code class="sourceCode python">OwningMembership</code></span></a>

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

  - <a href="/python/v0.8.4/syside/Specialization.md" class="reference internal" title="syside.Specialization"><span class="pre"><code class="sourceCode python">Specialization</code></span></a>

    - <a href="/python/v0.8.4/syside/FeatureTyping.md" class="reference internal" title="syside.FeatureTyping"><span class="pre"><code class="sourceCode python">FeatureTyping</code></span></a>

      - <a href="/python/v0.8.4/syside/ConjugatedPortTyping.md" class="reference internal" title="syside.ConjugatedPortTyping"><span class="pre"><code class="sourceCode python">ConjugatedPortTyping</code></span></a>

    - <a href="/python/v0.8.4/syside/Subclassification.md" class="reference internal" title="syside.Subclassification"><span class="pre"><code class="sourceCode python">Subclassification</code></span></a>

    - <a href="/python/v0.8.4/syside/Subsetting.md" class="reference internal" title="syside.Subsetting"><span class="pre"><code class="sourceCode python">Subsetting</code></span></a>

      - <a href="/python/v0.8.4/syside/CrossSubsetting.md" class="reference internal" title="syside.CrossSubsetting"><span class="pre"><code class="sourceCode python">CrossSubsetting</code></span></a>

      - <a href="/python/v0.8.4/syside/Redefinition.md" class="reference internal" title="syside.Redefinition"><span class="pre"><code class="sourceCode python">Redefinition</code></span></a>

      - <a href="/python/v0.8.4/syside/ReferenceSubsetting.md" class="reference internal" title="syside.ReferenceSubsetting"><span class="pre"><code class="sourceCode python">ReferenceSubsetting</code></span></a>

  - <a href="/python/v0.8.4/syside/TypeFeaturing.md" class="reference internal" title="syside.TypeFeaturing"><span class="pre"><code class="sourceCode python">TypeFeaturing</code></span></a>

  - <a href="/python/v0.8.4/syside/Unioning.md" class="reference internal" title="syside.Unioning"><span class="pre"><code class="sourceCode python">Unioning</code></span></a>

</div>

<span class="sd-summary-text">Members defined in <a href="#syside.Element" class="reference internal" title="syside.Element"><span class="pre"><code class="sourceCode python">Element</code></span></a> (26 members)</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |  |
|----|----|----|----|
| <span class="nerd-font"></span> | <a href="#syside.Element.STD" class="reference internal" title="syside.Element.STD"><span class="pre"><code class="sourceCode python">STD</code></span></a> | <span class="pre">`R`</span> |  |
| <span class="nerd-font"></span> | <a href="#syside.Element.alias_ids" class="reference internal" title="syside.Element.alias_ids"><span class="pre"><code class="sourceCode python">alias_ids</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`alias_ids`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Element.comments" class="reference internal" title="syside.Element.comments"><span class="pre"><code class="sourceCode python">comments</code></span></a> | <span class="pre">`R`</span> | The owned <span class="pre">`Comments`</span> related by <span class="pre">`owned_relationships`</span>. |
| <span class="nerd-font"></span> | <a href="#syside.Element.declared_name" class="reference internal" title="syside.Element.declared_name"><span class="pre"><code class="sourceCode python">declared_name</code></span></a> | <span class="pre">`RW`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`declared_name`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Element.declared_short_name" class="reference internal" title="syside.Element.declared_short_name"><span class="pre"><code class="sourceCode python">declared_short_name</code></span></a> | <span class="pre">`RW`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`declared_short_name`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Element.documentation" class="reference internal" title="syside.Element.documentation"><span class="pre"><code class="sourceCode python">documentation</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`documentation`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Element.element_id" class="reference internal" title="syside.Element.element_id"><span class="pre"><code class="sourceCode python">element_id</code></span></a> | <span class="pre">`RW`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`element_id`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Element.is_implied_included" class="reference internal" title="syside.Element.is_implied_included"><span class="pre"><code class="sourceCode python">is_implied_included</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`is_implied_included`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Element.is_library_element" class="reference internal" title="syside.Element.is_library_element"><span class="pre"><code class="sourceCode python">is_library_element</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`is_library_element`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Element.metadata" class="reference internal" title="syside.Element.metadata"><span class="pre"><code class="sourceCode python">metadata</code></span></a> | <span class="pre">`R`</span> | The owned metadata related by <span class="pre">`owned_relationships`</span>. |
| <span class="nerd-font"></span> | <a href="#syside.Element.name" class="reference internal" title="syside.Element.name"><span class="pre"><code class="sourceCode python">name</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`name`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Element.owned_annotations" class="reference internal" title="syside.Element.owned_annotations"><span class="pre"><code class="sourceCode python">owned_annotations</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_annotation`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Element.owned_elements" class="reference internal" title="syside.Element.owned_elements"><span class="pre"><code class="sourceCode python">owned_elements</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_element`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Element.owned_relationships" class="reference internal" title="syside.Element.owned_relationships"><span class="pre"><code class="sourceCode python">owned_relationships</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_relationship`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Element.owner" class="reference internal" title="syside.Element.owner"><span class="pre"><code class="sourceCode python">owner</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owner`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Element.owning_membership" class="reference internal" title="syside.Element.owning_membership"><span class="pre"><code class="sourceCode python">owning_membership</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owning_membership`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Element.owning_namespace" class="reference internal" title="syside.Element.owning_namespace"><span class="pre"><code class="sourceCode python">owning_namespace</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owning_namespace`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Element.owning_relationship" class="reference internal" title="syside.Element.owning_relationship"><span class="pre"><code class="sourceCode python">owning_relationship</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owning_relationship`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Element.path" class="reference internal" title="syside.Element.path"><span class="pre"><code class="sourceCode python">path</code></span></a> | <span class="pre">`R`</span> | Return a unique description of the location of this <span class="pre">`Element`</span> in the containment structure rooted in a root <span class="pre">`Namespace`</span>. In most cases the segments will be identical to <span class="pre">`QualifiedName`</span>. |
| <span class="nerd-font"></span> | <a href="#syside.Element.qualified_name" class="reference internal" title="syside.Element.qualified_name"><span class="pre"><code class="sourceCode python">qualified_name</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`qualified_name`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Element.scoped_owner" class="reference internal" title="syside.Element.scoped_owner"><span class="pre"><code class="sourceCode python">scoped_owner</code></span></a> | <span class="pre">`R`</span> | The owner of this <span class="pre">`Element`</span> as the parent of <span class="pre">`owning_membership`</span> or <span class="pre">`owning_relationship`</span> otherwise. |
| <span class="nerd-font"></span> | <a href="#syside.Element.sema_state" class="reference internal" title="syside.Element.sema_state"><span class="pre"><code class="sourceCode python">sema_state</code></span></a> | <span class="pre">`RW`</span> | The state of semantic resolution for this <span class="pre">`Element`</span>. Based on this, sema may skip elements to avoid duplicate work, e.g. when resolving elements in a group of related documents. |
| <span class="nerd-font"></span> | <a href="#syside.Element.short_name" class="reference internal" title="syside.Element.short_name"><span class="pre"><code class="sourceCode python">short_name</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`short_name`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Element.textual_representations" class="reference internal" title="syside.Element.textual_representations"><span class="pre"><code class="sourceCode python">textual_representations</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`textual_representation`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Element.__str__" class="reference internal" title="syside.Element.__str__"><span class="pre"><code class="sourceCode python"><span class="fu">__str__</span></code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.Element.matches_qualified_name" class="reference internal" title="syside.Element.matches_qualified_name"><span class="pre"><code class="sourceCode python">matches_qualified_name</code></span></a> |  | Check if the qualified name of this <span class="pre">`Element`</span> matches the provided segments of a qualified name. |

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

<span class="sig-name descname"><span class="pre">STD</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><span class="pre">type</span><span class="p"><span class="pre">\[</span></span><a href="#syside.Element" class="reference internal" title="syside.Element"><span class="pre">syside.Element</span></a><span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="p"><span class="pre">...</span></span><span class="p"><span class="pre">\]</span></span><span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">()</span>*<a href="#syside.Element.STD" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">alias_ids</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">list</span><span class="p"><span class="pre">\[</span></span><span class="pre">str</span><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Element.alias_ids" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`alias_ids`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> Various alternative identifiers for this Element. Generally, these will be set by tools.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=138" class="reference external" target="_blank">8.3.2.1.2</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">comments</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Comment.md" class="reference internal" title="syside.Comment"><span class="pre">syside.Comment</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Element.comments" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
The owned <span class="pre">`Comments`</span> related by <span class="pre">`owned_relationships`</span>.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">declared_name</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span>*<a href="#syside.Element.declared_name" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`declared_name`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The declared name of this <span class="pre">`Element`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=139" class="reference external" target="_blank">8.3.2.1.2</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">declared_short_name</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span>*<a href="#syside.Element.declared_short_name" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`declared_short_name`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> An optional alternative name for the <span class="pre">`Element`</span> that is intended to be shorter or in some way more succinct than its primary <span class="pre">`name`</span>. It may act as a modeler-specified identifier for the <span class="pre">`Element`</span>, though it is then the responsibility of the modeler to maintain the uniqueness of this identifier within a model or relative to some other context.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=139" class="reference external" target="_blank">8.3.2.1.2</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">documentation</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Documentation.md" class="reference internal" title="syside.Documentation"><span class="pre">syside.Documentation</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Element.documentation" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`documentation`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The Documentation owned by this Element.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=139" class="reference external" target="_blank">8.3.2.1.2</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">element_id</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">uuid.UUID</span>*<a href="#syside.Element.element_id" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`element_id`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The globally unique identifier for this Element. This is intended to be set by tooling, and it must not change during the lifetime of the Element.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=139" class="reference external" target="_blank">8.3.2.1.2</a> of the KerML specification for more details.

Note that <span class="pre">`element_id`</span> may be deprecated in a future release to improve performance as it has no use outside of serialization. In such cases, we may instead create and store <span class="pre">`element_ids`</span> only during serialization. Otherwise <span class="pre">`__hash__`</span> is guaranteed to remain stable while the <span class="pre">`Element`</span> is alive, however it may be reused on <span class="pre">`Document`</span> rebuilds.

Note that <span class="pre">`element_id`</span> is currently only stable for elements with <span class="pre">`qualified_name`</span>, and their owning memberships, using similar derivation strategy to the standard elements. <span class="pre">`path`</span> based element ids will be implemented in a future release when bulk-complexity can be guaranteed <span class="pre">`O(n)`</span>. While <span class="pre">`qualified_name`</span> element id has complexity of <span class="pre">`O(d)`</span>, <span class="pre">`path`</span> based has worst-case complexity of <span class="pre">`O(d^2)`</span> for elements without <span class="pre">`qualified_names`</span> because it needs to scan children linearly.

We reserve the option to change non-standard element id generation in future versions.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">is_implied_included</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*<a href="#syside.Element.is_implied_included" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`is_implied_included`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> Whether all necessary implied Relationships have been included in the <span class="pre">`owned_relationships`</span> of this Element. This property may be true, even if there are not actually any <span class="pre">`owned_relationships`</span> with <span class="pre">`is_implied`</span>` `<span class="pre">`=`</span>` `<span class="pre">`true`</span>, meaning that no such Relationships are actually implied for this Element. However, if it is false, then <span class="pre">`owned_relationships`</span> may *not* contain any implied Relationships. That is, either *all* required implied Relationships must be included, or none of them.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=139" class="reference external" target="_blank">8.3.2.1.2</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">is_library_element</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*<a href="#syside.Element.is_library_element" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`is_library_element`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> Whether this Element is contained in the ownership tree of a library model.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=139" class="reference external" target="_blank">8.3.2.1.2</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">metadata</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/MetadataFeature.md" class="reference internal" title="syside.MetadataFeature"><span class="pre">syside.MetadataFeature</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/MetadataUsage.md" class="reference internal" title="syside.MetadataUsage"><span class="pre">syside.MetadataUsage</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Element.metadata" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
The owned metadata related by <span class="pre">`owned_relationships`</span>.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">name</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span>*<a href="#syside.Element.name" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`name`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The name to be used for this <span class="pre">`Element`</span> during name resolution within its <span class="pre">`owning_namespace`</span>. This is derived using the <span class="pre">`effective_name()`</span> operation. By default, it is the same as the <span class="pre">`declared_name`</span>, but this is overridden for certain kinds of <span class="pre">`Elements`</span> to compute a <span class="pre">`name`</span> even when the <span class="pre">`declared_name`</span> is null.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=139" class="reference external" target="_blank">8.3.2.1.2</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned_annotations</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Annotation.md" class="reference internal" title="syside.Annotation"><span class="pre">syside.Annotation</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Element.owned_annotations" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owned_annotation`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The <span class="pre">`owned_relationships`</span> of this <span class="pre">`Element`</span> that are <span class="pre">`Annotations`</span>, for which this <span class="pre">`Element`</span> is the <span class="pre">`annotated_element`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=139" class="reference external" target="_blank">8.3.2.1.2</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned_elements</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="#syside.Element" class="reference internal" title="syside.Element"><span class="pre">syside.Element</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Element.owned_elements" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owned_element`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The Elements owned by this Element, derived as the owned_related_elements of the owned_relationships of this Element.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=139" class="reference external" target="_blank">8.3.2.1.2</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned_relationships</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Relationship.md" class="reference internal" title="syside.Relationship"><span class="pre">syside.Relationship</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Element.owned_relationships" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owned_relationship`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The Relationships for which this Element is the owning_related_element.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=139" class="reference external" target="_blank">8.3.2.1.2</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owner</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="#syside.Element" class="reference internal" title="syside.Element"><span class="pre">syside.Element</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span>*<a href="#syside.Element.owner" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owner`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The owner of this Element, derived as the <span class="pre">`owning_related_element`</span> of the <span class="pre">`owning_relationship`</span> of this Element, if any.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=139" class="reference external" target="_blank">8.3.2.1.2</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owning_membership</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/OwningMembership.md" class="reference internal" title="syside.OwningMembership"><span class="pre">syside.OwningMembership</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span>*<a href="#syside.Element.owning_membership" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owning_membership`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The <span class="pre">`owning_relationship`</span> of this <span class="pre">`Element`</span>, if that <span class="pre">`Relationship`</span> is a <span class="pre">`Membership`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=140" class="reference external" target="_blank">8.3.2.1.2</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owning_namespace</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/Namespace.md" class="reference internal" title="syside.Namespace"><span class="pre">syside.Namespace</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span>*<a href="#syside.Element.owning_namespace" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owning_namespace`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The <span class="pre">`Namespace`</span> that owns this <span class="pre">`Element`</span>, which is the <span class="pre">`membership_owning_namespace`</span> of the <span class="pre">`owning_membership`</span> of this <span class="pre">`Element`</span>, if any.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=140" class="reference external" target="_blank">8.3.2.1.2</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owning_relationship</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/Relationship.md" class="reference internal" title="syside.Relationship"><span class="pre">syside.Relationship</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span>*<a href="#syside.Element.owning_relationship" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owning_relationship`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The Relationship for which this Element is an owned_related_element, if any.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=140" class="reference external" target="_blank">8.3.2.1.2</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">path</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/Path.md" class="reference internal" title="syside.Path"><span class="pre">syside.Path</span></a>*<a href="#syside.Element.path" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Return a unique description of the location of this <span class="pre">`Element`</span> in the containment structure rooted in a root <span class="pre">`Namespace`</span>. In most cases the segments will be identical to <span class="pre">`QualifiedName`</span>.

For example, an <span class="pre">`OwningMembership`</span> will return its <span class="pre">`owned_member_element`</span> path with <span class="pre">`to_owning_membership`</span>` `<span class="pre">`==`</span>` `<span class="pre">`True`</span>.

*NOTE* that for now, this is only partially implemented, resolution of positions is not yet performed and an empty <span class="pre">`Path`</span> is returned instead.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">qualified_name</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/QualifiedName.md" class="reference internal" title="syside.QualifiedName"><span class="pre">syside.QualifiedName</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span>*<a href="#syside.Element.qualified_name" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`qualified_name`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The full ownership-qualified name of this <span class="pre">`Element`</span>, represented in a form that is valid according to the KerML textual concrete syntax for qualified names (including use of unrestricted name notation and escaped characters, as necessary). The <span class="pre">`qualified_name`</span> is null if this <span class="pre">`Element`</span> has no <span class="pre">`owning_namespace`</span> or if there is not a complete ownership chain of named <span class="pre">`Namespaces`</span> from a root <span class="pre">`Namespace`</span> to this <span class="pre">`Element`</span>. If the <span class="pre">`owning_namespace`</span> has other <span class="pre">`Elements`</span> with the same name as this one, then the <span class="pre">`qualified_name`</span> is null for all such <span class="pre">`Elements`</span> other than the first.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=140" class="reference external" target="_blank">8.3.2.1.2</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">scoped_owner</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="#syside.Element" class="reference internal" title="syside.Element"><span class="pre">syside.Element</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span>*<a href="#syside.Element.scoped_owner" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
The owner of this <span class="pre">`Element`</span> as the parent of <span class="pre">`owning_membership`</span> or <span class="pre">`owning_relationship`</span> otherwise.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">sema_state</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside.SemaState"><span class="pre">syside.SemaState</span></a>*<a href="#syside.Element.sema_state" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
The state of semantic resolution for this <span class="pre">`Element`</span>. Based on this, sema may skip elements to avoid duplicate work, e.g. when resolving elements in a group of related documents.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">short_name</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span>*<a href="#syside.Element.short_name" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`short_name`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The short name to be used for this <span class="pre">`Element`</span> during name resolution within its <span class="pre">`owning_namespace`</span>. This is derived using the <span class="pre">`effective_short_name()`</span> operation. By default, it is the same as the <span class="pre">`declared_short_name`</span>, but this is overridden for certain kinds of <span class="pre">`Elements`</span> to compute a <span class="pre">`short_name`</span> even when the <span class="pre">`declared_name`</span> is null.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=140" class="reference external" target="_blank">8.3.2.1.2</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">textual_representations</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/TextualRepresentation.md" class="reference internal" title="syside.TextualRepresentation"><span class="pre">syside.TextualRepresentation</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Element.textual_representations" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`textual_representation`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The <span class="pre">`TextualRepresentations`</span> that annotate this <span class="pre">`Element`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=140" class="reference external" target="_blank">8.3.2.1.2</a> of the KerML specification for more details.

<span class="nerd-font"></span> **Methods**

<span class="sig-name descname"><span class="pre">\_\_str\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">str</span></span></span><a href="#syside.Element.__str__" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">matches_qualified_name</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">Sequence</span><span class="p"><span class="pre">\[</span></span><span class="pre">str</span><span class="p"><span class="pre">\]</span></span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">bool</span></span></span><a href="#syside.Element.matches_qualified_name" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Check if the qualified name of this <span class="pre">`Element`</span> matches the provided segments of a qualified name.

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside"><span class="pre"><code class="sourceCode python">syside</code></span></a>

  - <a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside.Value"><span class="pre"><code class="sourceCode python">Value</code></span></a>

  - <a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside.deserialize"><span class="pre"><code class="sourceCode python">deserialize</code></span></a>

  - <a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside.pprint"><span class="pre"><code class="sourceCode python">pprint</code></span></a>

  - <a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside.sema_reset"><span class="pre"><code class="sourceCode python">sema_reset</code></span></a>

  - <a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside.serialize"><span class="pre"><code class="sourceCode python">serialize</code></span></a>

  - <a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside.sexp"><span class="pre"><code class="sourceCode python">sexp</code></span></a>

- <a href="/python/v0.8.4/syside/AnnotatingElement.md" class="reference internal" title="syside.AnnotatingElement"><span class="pre"><code class="sourceCode python">syside.AnnotatingElement</code></span></a>

  - <a href="/python/v0.8.4/syside/AnnotatingElement.md" class="reference internal" title="syside.AnnotatingElement.annotated_elements"><span class="pre"><code class="sourceCode python">annotated_elements</code></span></a>

- <a href="/python/v0.8.4/syside/Annotation.md" class="reference internal" title="syside.Annotation"><span class="pre"><code class="sourceCode python">syside.Annotation</code></span></a>

  - <a href="/python/v0.8.4/syside/Annotation.md" class="reference internal" title="syside.Annotation.annotated_element"><span class="pre"><code class="sourceCode python">annotated_element</code></span></a>

  - <a href="/python/v0.8.4/syside/Annotation.md" class="reference internal" title="syside.Annotation.owning_annotated_element"><span class="pre"><code class="sourceCode python">owning_annotated_element</code></span></a>

  - <a href="/python/v0.8.4/syside/Annotation.md" class="reference internal" title="syside.Annotation.owning_related_element"><span class="pre"><code class="sourceCode python">owning_related_element</code></span></a>

  - <a href="/python/v0.8.4/syside/Annotation.md" class="reference internal" title="syside.Annotation.sources"><span class="pre"><code class="sourceCode python">sources</code></span></a>

  - <a href="/python/v0.8.4/syside/Annotation.md" class="reference internal" title="syside.Annotation.targets"><span class="pre"><code class="sourceCode python">targets</code></span></a>

- <a href="/python/v0.8.4/syside/AstNode.md" class="reference internal" title="syside.AstNode"><span class="pre"><code class="sourceCode python">syside.AstNode</code></span></a>

  - <a href="/python/v0.8.4/syside/AstNode.md" class="reference internal" title="syside.AstNode.owned_elements"><span class="pre"><code class="sourceCode python">owned_elements</code></span></a>

  - <a href="/python/v0.8.4/syside/AstNode.md" class="reference internal" title="syside.AstNode.parent"><span class="pre"><code class="sourceCode python">parent</code></span></a>

- <a href="/python/v0.8.4/syside/BoundMetaclass.md" class="reference internal" title="syside.BoundMetaclass"><span class="pre"><code class="sourceCode python">syside.BoundMetaclass</code></span></a>

  - <a href="/python/v0.8.4/syside/BoundMetaclass.md" class="reference internal" title="syside.BoundMetaclass.element"><span class="pre"><code class="sourceCode python">element</code></span></a>

- <a href="/python/v0.8.4/syside/Dependency.md" class="reference internal" title="syside.Dependency"><span class="pre"><code class="sourceCode python">syside.Dependency</code></span></a>

  - <a href="/python/v0.8.4/syside/Dependency.md" class="reference internal" title="syside.Dependency.owning_related_element"><span class="pre"><code class="sourceCode python">owning_related_element</code></span></a>

  - <a href="/python/v0.8.4/syside/Dependency.md" class="reference internal" title="syside.Dependency.sources"><span class="pre"><code class="sourceCode python">sources</code></span></a>

  - <a href="/python/v0.8.4/syside/Dependency.md" class="reference internal" title="syside.Dependency.targets"><span class="pre"><code class="sourceCode python">targets</code></span></a>

- <a href="/python/v0.8.4/syside/DependencyEnds.md" class="reference internal" title="syside.DependencyEnds"><span class="pre"><code class="sourceCode python">syside.DependencyEnds</code></span></a>

  - <a href="/python/v0.8.4/syside/DependencyEnds.md" class="reference internal" title="syside.DependencyEnds.append"><span class="pre"><code class="sourceCode python">append</code></span></a>

  - <a href="/python/v0.8.4/syside/DependencyEnds.md" class="reference internal" title="syside.DependencyEnds.pop"><span class="pre"><code class="sourceCode python">pop</code></span></a>

  - <a href="/python/v0.8.4/syside/DependencyEnds.md" class="reference internal" title="syside.DependencyEnds.remove"><span class="pre"><code class="sourceCode python">remove</code></span></a>

  - <a href="/python/v0.8.4/syside/DependencyEnds.md" class="reference internal" title="syside.DependencyEnds.replace_at"><span class="pre"><code class="sourceCode python">replace_at</code></span></a>

- <a href="/python/v0.8.4/syside/DeserializedModel.md" class="reference internal" title="syside.DeserializedModel"><span class="pre"><code class="sourceCode python">syside.DeserializedModel</code></span></a>

  - <a href="/python/v0.8.4/syside/DeserializedModel.md" class="reference internal" title="syside.DeserializedModel.link"><span class="pre"><code class="sourceCode python">link</code></span></a>

  - <a href="/python/v0.8.4/syside/DeserializedModel.md" class="reference internal" title="syside.DeserializedModel.root"><span class="pre"><code class="sourceCode python">root</code></span></a>

- <a href="/python/v0.8.4/syside/Deserializer.md" class="reference internal" title="syside.Deserializer"><span class="pre"><code class="sourceCode python">syside.Deserializer</code></span></a>

  - <a href="/python/v0.8.4/syside/Deserializer.md" class="reference internal" title="syside.Deserializer.accept"><span class="pre"><code class="sourceCode python">accept</code></span></a>

- <a href="/python/v0.8.4/syside/Documentation.md" class="reference internal" title="syside.Documentation"><span class="pre"><code class="sourceCode python">syside.Documentation</code></span></a>

  - <a href="/python/v0.8.4/syside/Documentation.md" class="reference internal" title="syside.Documentation.documented_element"><span class="pre"><code class="sourceCode python">documented_element</code></span></a>

- <a href="#syside.Element" class="reference internal" title="syside.Element"><span class="pre"><code class="sourceCode python">syside.Element</code></span></a>

  - <a href="#syside.Element.STD" class="reference internal" title="syside.Element.STD"><span class="pre"><code class="sourceCode python">STD</code></span></a>

  - <a href="#syside.Element.owned_elements" class="reference internal" title="syside.Element.owned_elements"><span class="pre"><code class="sourceCode python">owned_elements</code></span></a>

  - <a href="#syside.Element.owner" class="reference internal" title="syside.Element.owner"><span class="pre"><code class="sourceCode python">owner</code></span></a>

  - <a href="#syside.Element.scoped_owner" class="reference internal" title="syside.Element.scoped_owner"><span class="pre"><code class="sourceCode python">scoped_owner</code></span></a>

- <a href="/python/v0.8.4/syside/IdMap.md" class="reference internal" title="syside.IdMap"><span class="pre"><code class="sourceCode python">syside.IdMap</code></span></a>

  - <a href="/python/v0.8.4/syside/IdMap.md" class="reference internal" title="syside.IdMap.__call__"><span class="pre"><code class="sourceCode python"><span class="fu">__call__</span></code></span></a>

  - <a href="/python/v0.8.4/syside/IdMap.md" class="reference internal" title="syside.IdMap.find"><span class="pre"><code class="sourceCode python">find</code></span></a>

  - <a href="/python/v0.8.4/syside/IdMap.md" class="reference internal" title="syside.IdMap.search"><span class="pre"><code class="sourceCode python">search</code></span></a>

- <a href="/python/v0.8.4/syside/Import.md" class="reference internal" title="syside.Import"><span class="pre"><code class="sourceCode python">syside.Import</code></span></a>

  - <a href="/python/v0.8.4/syside/Import.md" class="reference internal" title="syside.Import.imported_element"><span class="pre"><code class="sourceCode python">imported_element</code></span></a>

  - <a href="/python/v0.8.4/syside/Import.md" class="reference internal" title="syside.Import.owning_related_element"><span class="pre"><code class="sourceCode python">owning_related_element</code></span></a>

  - <a href="/python/v0.8.4/syside/Import.md" class="reference internal" title="syside.Import.sources"><span class="pre"><code class="sourceCode python">sources</code></span></a>

  - <a href="/python/v0.8.4/syside/Import.md" class="reference internal" title="syside.Import.targets"><span class="pre"><code class="sourceCode python">targets</code></span></a>

- <a href="/python/v0.8.4/syside/IndexedSymbol.md" class="reference internal" title="syside.IndexedSymbol"><span class="pre"><code class="sourceCode python">syside.IndexedSymbol</code></span></a>

  - <a href="/python/v0.8.4/syside/IndexedSymbol.md" class="reference internal" title="syside.IndexedSymbol.node"><span class="pre"><code class="sourceCode python">node</code></span></a>

- <a href="/python/v0.8.4/syside/Membership.md" class="reference internal" title="syside.Membership"><span class="pre"><code class="sourceCode python">syside.Membership</code></span></a>

  - <a href="/python/v0.8.4/syside/Membership.md" class="reference internal" title="syside.Membership.member_element"><span class="pre"><code class="sourceCode python">member_element</code></span></a>

  - <a href="/python/v0.8.4/syside/Membership.md" class="reference internal" title="syside.Membership.owning_related_element"><span class="pre"><code class="sourceCode python">owning_related_element</code></span></a>

  - <a href="/python/v0.8.4/syside/Membership.md" class="reference internal" title="syside.Membership.sources"><span class="pre"><code class="sourceCode python">sources</code></span></a>

  - <a href="/python/v0.8.4/syside/Membership.md" class="reference internal" title="syside.Membership.targets"><span class="pre"><code class="sourceCode python">targets</code></span></a>

- <a href="/python/v0.8.4/syside/MetadataAccessExpression.md" class="reference internal" title="syside.MetadataAccessExpression"><span class="pre"><code class="sourceCode python">syside.MetadataAccessExpression</code></span></a>

  - <a href="/python/v0.8.4/syside/MetadataAccessExpression.md" class="reference internal" title="syside.MetadataAccessExpression.referenced_element"><span class="pre"><code class="sourceCode python">referenced_element</code></span></a>

- <a href="/python/v0.8.4/syside/MetadataFeature.md" class="reference internal" title="syside.MetadataFeature"><span class="pre"><code class="sourceCode python">syside.MetadataFeature</code></span></a>

  - <a href="/python/v0.8.4/syside/MetadataFeature.md" class="reference internal" title="syside.MetadataFeature.annotated_elements"><span class="pre"><code class="sourceCode python">annotated_elements</code></span></a>

- <a href="/python/v0.8.4/syside/MetadataUsage.md" class="reference internal" title="syside.MetadataUsage"><span class="pre"><code class="sourceCode python">syside.MetadataUsage</code></span></a>

  - <a href="/python/v0.8.4/syside/MetadataUsage.md" class="reference internal" title="syside.MetadataUsage.annotated_elements"><span class="pre"><code class="sourceCode python">annotated_elements</code></span></a>

- <a href="/python/v0.8.4/syside/Namespace.md" class="reference internal" title="syside.Namespace"><span class="pre"><code class="sourceCode python">syside.Namespace</code></span></a>

  - <a href="/python/v0.8.4/syside/Namespace.md" class="reference internal" title="syside.Namespace.__getitem__"><span class="pre"><code class="sourceCode python"><span class="fu">__getitem__</span></code></span></a>

  - <a href="/python/v0.8.4/syside/Namespace.md" class="reference internal" title="syside.Namespace.get_member"><span class="pre"><code class="sourceCode python">get_member</code></span></a>

  - <a href="/python/v0.8.4/syside/Namespace.md" class="reference internal" title="syside.Namespace.members"><span class="pre"><code class="sourceCode python">members</code></span></a>

  - <a href="/python/v0.8.4/syside/Namespace.md" class="reference internal" title="syside.Namespace.owned_members"><span class="pre"><code class="sourceCode python">owned_members</code></span></a>

- <a href="/python/v0.8.4/syside/OwningMembership.md" class="reference internal" title="syside.OwningMembership"><span class="pre"><code class="sourceCode python">syside.OwningMembership</code></span></a>

  - <a href="/python/v0.8.4/syside/OwningMembership.md" class="reference internal" title="syside.OwningMembership.owned_member_element"><span class="pre"><code class="sourceCode python">owned_member_element</code></span></a>

- <a href="/python/v0.8.4/syside/PendingReference.md" class="reference internal" title="syside.PendingReference"><span class="pre"><code class="sourceCode python">syside.PendingReference</code></span></a>

  - <a href="/python/v0.8.4/syside/PendingReference.md" class="reference internal" title="syside.PendingReference.referent"><span class="pre"><code class="sourceCode python">referent</code></span></a>

- <a href="/python/v0.8.4/syside/ReferenceAccessor.md" class="reference internal" title="syside.ReferenceAccessor"><span class="pre"><code class="sourceCode python">syside.ReferenceAccessor</code></span></a>

  - <a href="/python/v0.8.4/syside/ReferenceAccessor.md" class="reference internal" title="syside.ReferenceAccessor.element"><span class="pre"><code class="sourceCode python">element</code></span></a>

- <a href="/python/v0.8.4/syside/ReferencePrinter.md" class="reference internal" title="syside.ReferencePrinter"><span class="pre"><code class="sourceCode python">syside.ReferencePrinter</code></span></a>

  - <a href="/python/v0.8.4/syside/ReferencePrinter.md" class="reference internal" title="syside.ReferencePrinter.__init__"><span class="pre"><code class="sourceCode python"><span class="fu">__init__</span></code></span></a>

- <a href="/python/v0.8.4/syside/Relationship.md" class="reference internal" title="syside.Relationship"><span class="pre"><code class="sourceCode python">syside.Relationship</code></span></a>

  - <a href="/python/v0.8.4/syside/Relationship.md" class="reference internal" title="syside.Relationship.first_source"><span class="pre"><code class="sourceCode python">first_source</code></span></a>

  - <a href="/python/v0.8.4/syside/Relationship.md" class="reference internal" title="syside.Relationship.first_target"><span class="pre"><code class="sourceCode python">first_target</code></span></a>

  - <a href="/python/v0.8.4/syside/Relationship.md" class="reference internal" title="syside.Relationship.owned_related_elements"><span class="pre"><code class="sourceCode python">owned_related_elements</code></span></a>

  - <a href="/python/v0.8.4/syside/Relationship.md" class="reference internal" title="syside.Relationship.owning_related_element"><span class="pre"><code class="sourceCode python">owning_related_element</code></span></a>

  - <a href="/python/v0.8.4/syside/Relationship.md" class="reference internal" title="syside.Relationship.related_elements"><span class="pre"><code class="sourceCode python">related_elements</code></span></a>

  - <a href="/python/v0.8.4/syside/Relationship.md" class="reference internal" title="syside.Relationship.sources"><span class="pre"><code class="sourceCode python">sources</code></span></a>

  - <a href="/python/v0.8.4/syside/Relationship.md" class="reference internal" title="syside.Relationship.targets"><span class="pre"><code class="sourceCode python">targets</code></span></a>

- <a href="/python/v0.8.4/syside/RelationshipBody.md" class="reference internal" title="syside.RelationshipBody"><span class="pre"><code class="sourceCode python">syside.RelationshipBody</code></span></a>

  - <a href="/python/v0.8.4/syside/RelationshipBody.md" class="reference internal" title="syside.RelationshipBody.extract"><span class="pre"><code class="sourceCode python">extract</code></span></a>

  - <a href="/python/v0.8.4/syside/RelationshipBody.md" class="reference internal" title="syside.RelationshipBody.pop"><span class="pre"><code class="sourceCode python">pop</code></span></a>

  - <a href="/python/v0.8.4/syside/RelationshipBody.md" class="reference internal" title="syside.RelationshipBody.remove_element"><span class="pre"><code class="sourceCode python">remove_element</code></span></a>

- <a href="/python/v0.8.4/syside/Serializer.md" class="reference internal" title="syside.Serializer"><span class="pre"><code class="sourceCode python">syside.Serializer</code></span></a>

  - <a href="/python/v0.8.4/syside/Serializer.md" class="reference internal" title="syside.Serializer.accept"><span class="pre"><code class="sourceCode python">accept</code></span></a>

- <a href="/python/v0.8.4/syside/Stdlib.md" class="reference internal" title="syside.Stdlib"><span class="pre"><code class="sourceCode python">syside.Stdlib</code></span></a>

  - <a href="/python/v0.8.4/syside/Stdlib.md" class="reference internal" title="syside.Stdlib.implicit_supertype_for"><span class="pre"><code class="sourceCode python">implicit_supertype_for</code></span></a>

  - <a href="/python/v0.8.4/syside/Stdlib.md" class="reference internal" title="syside.Stdlib.metaclass_for"><span class="pre"><code class="sourceCode python">metaclass_for</code></span></a>

- <a href="/python/v0.8.4/syside/TextualRepresentation.md" class="reference internal" title="syside.TextualRepresentation"><span class="pre"><code class="sourceCode python">syside.TextualRepresentation</code></span></a>

  - <a href="/python/v0.8.4/syside/TextualRepresentation.md" class="reference internal" title="syside.TextualRepresentation.represented_element"><span class="pre"><code class="sourceCode python">represented_element</code></span></a>

- <a href="/python/v0.8.4/syside/UnexpectedDifferentReference.md" class="reference internal" title="syside.UnexpectedDifferentReference"><span class="pre"><code class="sourceCode python">syside.UnexpectedDifferentReference</code></span></a>

  - <a href="/python/v0.8.4/syside/UnexpectedDifferentReference.md" class="reference internal" title="syside.UnexpectedDifferentReference.expected"><span class="pre"><code class="sourceCode python">expected</code></span></a>

  - <a href="/python/v0.8.4/syside/UnexpectedDifferentReference.md" class="reference internal" title="syside.UnexpectedDifferentReference.reference"><span class="pre"><code class="sourceCode python">reference</code></span></a>

- <a href="/python/v0.8.4/syside/ViewUsage.md" class="reference internal" title="syside.ViewUsage"><span class="pre"><code class="sourceCode python">syside.ViewUsage</code></span></a>

  - <a href="/python/v0.8.4/syside/ViewUsage.md" class="reference internal" title="syside.ViewUsage.exposed_elements"><span class="pre"><code class="sourceCode python">exposed_elements</code></span></a>

- <a href="/python/v0.8.4/syside/json//README.md" class="reference internal" title="syside.json"><span class="pre"><code class="sourceCode python">syside.json</code></span></a>

  - <a href="/python/v0.8.4/syside/json//README.md" class="reference internal" title="syside.json.DeserializationReport"><span class="pre"><code class="sourceCode python">DeserializationReport</code></span></a>

  - <a href="/python/v0.8.4/syside/json//README.md" class="reference internal" title="syside.json.dumps"><span class="pre"><code class="sourceCode python">dumps</code></span></a>

  - <a href="/python/v0.8.4/syside/json//README.md" class="reference internal" title="syside.json.loads"><span class="pre"><code class="sourceCode python">loads</code></span></a>

- <a href="/python/v0.8.4/syside/json/SerializationError.md" class="reference internal" title="syside.json.SerializationError"><span class="pre"><code class="sourceCode python">syside.json.SerializationError</code></span></a>

  - <a href="/python/v0.8.4/syside/json/SerializationError.md" class="reference internal" title="syside.json.SerializationError.report"><span class="pre"><code class="sourceCode python">report</code></span></a>

- <a href="/python/v0.8.4/syside/preview/LockedModel.md" class="reference internal" title="syside.preview.LockedModel"><span class="pre"><code class="sourceCode python">syside.preview.LockedModel</code></span></a>

  - <a href="/python/v0.8.4/syside/preview/LockedModel.md" class="reference internal" title="syside.preview.LockedModel.lookup"><span class="pre"><code class="sourceCode python">lookup</code></span></a>

  - <a href="/python/v0.8.4/syside/preview/LockedModel.md" class="reference internal" title="syside.preview.LockedModel.top_elements"><span class="pre"><code class="sourceCode python">top_elements</code></span></a>

  - <a href="/python/v0.8.4/syside/preview/LockedModel.md" class="reference internal" title="syside.preview.LockedModel.top_elements_from"><span class="pre"><code class="sourceCode python">top_elements_from</code></span></a>

  - <a href="/python/v0.8.4/syside/preview/LockedModel.md" class="reference internal" title="syside.preview.LockedModel.top_named_elements"><span class="pre"><code class="sourceCode python">top_named_elements</code></span></a>

</div>

</div>
