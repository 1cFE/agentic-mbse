<div id="feature-sysml" class="section">

# Feature <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span><a href="#feature-sysml" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">Feature</span></span><a href="#syside.Feature" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`Feature`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> A <span class="pre">`Feature`</span> is a <span class="pre">`Type`</span> that classifies relations between multiple things (in the universe). The domain of the relation is the intersection of the <span class="pre">`featuring_types`</span> of the <span class="pre">`Feature`</span>. (The domain of a <span class="pre">`Feature`</span> with no <span class="pre">`featuring_types`</span> is implicitly the most general <span class="pre">`Type`</span> <span class="pre">`Base::Anything`</span> from the Kernel Semantic Library.) The co-domain of the relation is the intersection of the <span class="pre">`types`</span> of the <span class="pre">`Feature`</span>.
>
> In the simplest cases, the <span class="pre">`featuring_types`</span> and <span class="pre">`types`</span> are <span class="pre">`Classifiers`</span> and the <span class="pre">`Feature`</span> relates two things, one from the domain and one from the range. Examples include cars paired with wheels, people paired with other people, and cars paired with numbers representing the car length.
>
> Since <span class="pre">`Features`</span> are <span class="pre">`Types`</span>, their <span class="pre">`featuring_types`</span> and <span class="pre">`types`</span> can be <span class="pre">`Features`</span>. In this case, the <span class="pre">`Feature`</span> effectively classifies relations between relations, which can be interpreted as the sequence of things related by the domain <span class="pre">`Feature`</span> concatenated with the sequence of things related by the co-domain <span class="pre">`Feature`</span>.
>
> The *values* of a <span class="pre">`Feature`</span> for a given instance of its domain are all the instances of its co-domain that are related to that domain instance by the <span class="pre">`Feature`</span>. The values of a <span class="pre">`Feature`</span> with <span class="pre">`chaining_features`</span> are the same as values of the last <span class="pre">`Feature`</span> in the chain, which can be found by starting with values of the first <span class="pre">`Feature`</span>, then using those values as domain instances to obtain values of the second <span class="pre">`Feature`</span>, and so on, to values of the last <span class="pre">`Feature`</span>.
>
> </div>

For language description, see section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=58" class="reference external" target="_blank">7.3.4</a> of the KerML specification. For more details on the model, see section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=187" class="reference external" target="_blank">8.3.3.3.4</a> of the KerML specification.

<div class="align-center" align="center">

<img src="data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iZ3JhcGh2aXoiIHN0eWxlPSJ3aWR0aDogNS43NXJlbTtoZWlnaHQ6IDIwLjc1cmVtOyIgdmlld2JveD0iMC4wMCAwLjAwIDkyLjAwIDMzMi4wMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGcgY2xhc3M9ImdyYXBoIiBpZD0iZ3JhcGgwIiB0cmFuc2Zvcm09InNjYWxlKDEgMSkgcm90YXRlKDApIHRyYW5zbGF0ZSg0IDMyOCkiPgo8dGl0bGU+JTM8L3RpdGxlPgo8ZyBjbGFzcz0ibm9kZSIgaWQ9Im5vZGUxIj4KPHRpdGxlPkZlYXR1cmU8L3RpdGxlPgo8ZyBpZD0iYV9ub2RlMSI+PGEgaHJlZj0iI3N5c2lkZS5GZWF0dXJlIj4KPHBvbHlnb24gcG9pbnRzPSI3MiwtMzYgMTIsLTM2IDEyLDAgNzIsMCA3MiwtMzYiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1ncmFwaHZpei1ub2RlLWJnLWNvbG9yKTtzdHJva2U6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtZmctY29sb3IpOyI+PC9wb2x5Z29uPgo8dGV4dCBmb250LWZhbWlseT0iTGV4ZW5kIiBmb250LXNpemU9IjEyLjAwIiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtY29kZS1mZy1jb2xvcik7LS1tZC1ncmFwaHZpei1ob3Zlci1jb2xvcjogdmFyKC0tbWQtZ3JhcGh2aXotYS1ob3Zlci1jb2xvcik7IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSI0MiIgeT0iLTE0LjIiPkZlYXR1cmU8L3RleHQ+Cjx0aXRsZT5zeXNpZGUuRmVhdHVyZTwvdGl0bGU+PC9hPgo8L2c+CjwvZz4KPGcgY2xhc3M9Im5vZGUiIGlkPSJub2RlMiI+Cjx0aXRsZT5UeXBlPC90aXRsZT4KPGcgaWQ9ImFfbm9kZTIiPjxhIGhyZWY9Ii9weXRob24vdjAuOC40L3N5c2lkZS9UeXBlLm1kIj4KPHBvbHlnb24gcG9pbnRzPSI2OSwtMTA4IDE1LC0xMDggMTUsLTcyIDY5LC03MiA2OSwtMTA4IiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1iZy1jb2xvcik7c3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1ub2RlLWZnLWNvbG9yKTsiPjwvcG9seWdvbj4KPHRleHQgZm9udC1mYW1pbHk9IkxleGVuZCIgZm9udC1zaXplPSIxMi4wMCIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWNvZGUtZmctY29sb3IpOy0tbWQtZ3JhcGh2aXotaG92ZXItY29sb3I6IHZhcigtLW1kLWdyYXBodml6LWEtaG92ZXItY29sb3IpOyIgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iNDIiIHk9Ii04Ni4yIj5UeXBlPC90ZXh0Pgo8dGl0bGU+c3lzaWRlLlR5cGU8L3RpdGxlPjwvYT4KPC9nPgo8L2c+CjxnIGNsYXNzPSJlZGdlIiBpZD0iZWRnZTEiPgo8dGl0bGU+VHlwZS0mZ3Q7RmVhdHVyZTwvdGl0bGU+CjxwYXRoIGQ9Ik00MiwtNzEuN0M0MiwtNjMuOTggNDIsLTU0LjcxIDQyLC00Ni4xMSIgZmlsbD0ibm9uZSIgc3R5bGU9InN0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotZWRnZS1jb2xvcik7IiAvPgo8cG9seWdvbiBwb2ludHM9IjQ1LjUsLTQ2LjEgNDIsLTM2LjEgMzguNSwtNDYuMSA0NS41LC00Ni4xIiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtZ3JhcGh2aXotZWRnZS1jb2xvcik7c3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1lZGdlLWNvbG9yKTsiPjwvcG9seWdvbj4KPC9nPgo8ZyBjbGFzcz0ibm9kZSIgaWQ9Im5vZGUzIj4KPHRpdGxlPk5hbWVzcGFjZTwvdGl0bGU+CjxnIGlkPSJhX25vZGUzIj48YSBocmVmPSIvcHl0aG9uL3YwLjguNC9zeXNpZGUvTmFtZXNwYWNlLm1kIj4KPHBvbHlnb24gcG9pbnRzPSI4NCwtMTgwIDAsLTE4MCAwLC0xNDQgODQsLTE0NCA4NCwtMTgwIiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1iZy1jb2xvcik7c3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1ub2RlLWZnLWNvbG9yKTsiPjwvcG9seWdvbj4KPHRleHQgZm9udC1mYW1pbHk9IkxleGVuZCIgZm9udC1zaXplPSIxMi4wMCIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWNvZGUtZmctY29sb3IpOy0tbWQtZ3JhcGh2aXotaG92ZXItY29sb3I6IHZhcigtLW1kLWdyYXBodml6LWEtaG92ZXItY29sb3IpOyIgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iNDIiIHk9Ii0xNTguMiI+TmFtZXNwYWNlPC90ZXh0Pgo8dGl0bGU+c3lzaWRlLk5hbWVzcGFjZTwvdGl0bGU+PC9hPgo8L2c+CjwvZz4KPGcgY2xhc3M9ImVkZ2UiIGlkPSJlZGdlMiI+Cjx0aXRsZT5OYW1lc3BhY2UtJmd0O1R5cGU8L3RpdGxlPgo8cGF0aCBkPSJNNDIsLTE0My43QzQyLC0xMzUuOTggNDIsLTEyNi43MSA0MiwtMTE4LjExIiBmaWxsPSJub25lIiBzdHlsZT0ic3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1lZGdlLWNvbG9yKTsiIC8+Cjxwb2x5Z29uIHBvaW50cz0iNDUuNSwtMTE4LjEgNDIsLTEwOC4xIDM4LjUsLTExOC4xIDQ1LjUsLTExOC4xIiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtZ3JhcGh2aXotZWRnZS1jb2xvcik7c3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1lZGdlLWNvbG9yKTsiPjwvcG9seWdvbj4KPC9nPgo8ZyBjbGFzcz0ibm9kZSIgaWQ9Im5vZGU0Ij4KPHRpdGxlPkVsZW1lbnQ8L3RpdGxlPgo8ZyBpZD0iYV9ub2RlNCI+PGEgaHJlZj0iL3B5dGhvbi92MC44LjQvc3lzaWRlL0VsZW1lbnQubWQiPgo8cG9seWdvbiBwb2ludHM9IjczLC0yNTIgMTEsLTI1MiAxMSwtMjE2IDczLC0yMTYgNzMsLTI1MiIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtYmctY29sb3IpO3N0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1mZy1jb2xvcik7Ij48L3BvbHlnb24+Cjx0ZXh0IGZvbnQtZmFtaWx5PSJMZXhlbmQiIGZvbnQtc2l6ZT0iMTIuMDAiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1jb2RlLWZnLWNvbG9yKTstLW1kLWdyYXBodml6LWhvdmVyLWNvbG9yOiB2YXIoLS1tZC1ncmFwaHZpei1hLWhvdmVyLWNvbG9yKTsiIHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjQyIiB5PSItMjMwLjIiPkVsZW1lbnQ8L3RleHQ+Cjx0aXRsZT5zeXNpZGUuRWxlbWVudDwvdGl0bGU+PC9hPgo8L2c+CjwvZz4KPGcgY2xhc3M9ImVkZ2UiIGlkPSJlZGdlMyI+Cjx0aXRsZT5FbGVtZW50LSZndDtOYW1lc3BhY2U8L3RpdGxlPgo8cGF0aCBkPSJNNDIsLTIxNS43QzQyLC0yMDcuOTggNDIsLTE5OC43MSA0MiwtMTkwLjExIiBmaWxsPSJub25lIiBzdHlsZT0ic3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1lZGdlLWNvbG9yKTsiIC8+Cjxwb2x5Z29uIHBvaW50cz0iNDUuNSwtMTkwLjEgNDIsLTE4MC4xIDM4LjUsLTE5MC4xIDQ1LjUsLTE5MC4xIiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtZ3JhcGh2aXotZWRnZS1jb2xvcik7c3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1lZGdlLWNvbG9yKTsiPjwvcG9seWdvbj4KPC9nPgo8ZyBjbGFzcz0ibm9kZSIgaWQ9Im5vZGU1Ij4KPHRpdGxlPkFzdE5vZGU8L3RpdGxlPgo8ZyBpZD0iYV9ub2RlNSI+PGEgaHJlZj0iL3B5dGhvbi92MC44LjQvc3lzaWRlL0FzdE5vZGUubWQiPgo8cG9seWdvbiBwb2ludHM9Ijc1LC0zMjQgOSwtMzI0IDksLTI4OCA3NSwtMjg4IDc1LC0zMjQiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1ncmFwaHZpei1ub2RlLWJnLWNvbG9yKTtzdHJva2U6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtZmctY29sb3IpOyI+PC9wb2x5Z29uPgo8dGV4dCBmb250LWZhbWlseT0iTGV4ZW5kIiBmb250LXNpemU9IjEyLjAwIiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtY29kZS1mZy1jb2xvcik7LS1tZC1ncmFwaHZpei1ob3Zlci1jb2xvcjogdmFyKC0tbWQtZ3JhcGh2aXotYS1ob3Zlci1jb2xvcik7IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSI0MiIgeT0iLTMwMi4yIj5Bc3ROb2RlPC90ZXh0Pgo8dGl0bGU+c3lzaWRlLkFzdE5vZGU8L3RpdGxlPjwvYT4KPC9nPgo8L2c+CjxnIGNsYXNzPSJlZGdlIiBpZD0iZWRnZTQiPgo8dGl0bGU+QXN0Tm9kZS0mZ3Q7RWxlbWVudDwvdGl0bGU+CjxwYXRoIGQ9Ik00MiwtMjg3LjdDNDIsLTI3OS45OCA0MiwtMjcwLjcxIDQyLC0yNjIuMTEiIGZpbGw9Im5vbmUiIHN0eWxlPSJzdHJva2U6IHZhcigtLW1kLWdyYXBodml6LWVkZ2UtY29sb3IpOyIgLz4KPHBvbHlnb24gcG9pbnRzPSI0NS41LC0yNjIuMSA0MiwtMjUyLjEgMzguNSwtMjYyLjEgNDUuNSwtMjYyLjEiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1ncmFwaHZpei1lZGdlLWNvbG9yKTtzdHJva2U6IHZhcigtLW1kLWdyYXBodml6LWVkZ2UtY29sb3IpOyI+PC9wb2x5Z29uPgo8L2c+CjwvZz4KPC9zdmc+" class="graphviz" />

</div>

<span class="sd-summary-text"><span class="nerd-font"></span> Children</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

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

<span class="sd-summary-text">Members defined in <a href="#syside.Feature" class="reference internal" title="syside.Feature"><span class="pre"><code class="sourceCode python">Feature</code></span></a> (45 members)</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |  |
|----|----|----|----|
| <span class="nerd-font"></span> | <a href="#syside.Feature.STD" class="reference internal" title="syside.Feature.STD"><span class="pre"><code class="sourceCode python">STD</code></span></a> | <span class="pre">`R`</span> |  |
| <span class="nerd-font"></span> | <a href="#syside.Feature.basic_feature" class="reference internal" title="syside.Feature.basic_feature"><span class="pre"><code class="sourceCode python">basic_feature</code></span></a> | <span class="pre">`R`</span> | The <span class="pre">`last_chaining_feature`</span> if one exists, otherwise this <span class="pre">`Feature`</span>. |
| <span class="nerd-font"></span> | <a href="#syside.Feature.chaining_features" class="reference internal" title="syside.Feature.chaining_features"><span class="pre"><code class="sourceCode python">chaining_features</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`chaining_feature`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Feature.cross_feature" class="reference internal" title="syside.Feature.cross_feature"><span class="pre"><code class="sourceCode python">cross_feature</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`cross_feature`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Feature.direction" class="reference internal" title="syside.Feature.direction"><span class="pre"><code class="sourceCode python">direction</code></span></a> | <span class="pre">`RW`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`direction`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Feature.end_owning_type" class="reference internal" title="syside.Feature.end_owning_type"><span class="pre"><code class="sourceCode python">end_owning_type</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`end_owning_type`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Feature.explicit_direction" class="reference internal" title="syside.Feature.explicit_direction"><span class="pre"><code class="sourceCode python">explicit_direction</code></span></a> | <span class="pre">`R`</span> | Returns the direction this <span class="pre">`Feature`</span> has been declared with in the textual syntax. |
| <span class="nerd-font"></span> | <a href="#syside.Feature.feature_target" class="reference internal" title="syside.Feature.feature_target"><span class="pre"><code class="sourceCode python">feature_target</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`feature_target`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Feature.feature_value" class="reference internal" title="syside.Feature.feature_value"><span class="pre"><code class="sourceCode python">feature_value</code></span></a> | <span class="pre">`R`</span> | The <span class="pre">`FeatureValue`</span> owned by this <span class="pre">`Feature`</span> if any. |
| <span class="nerd-font"></span> | <a href="#syside.Feature.feature_value_expression" class="reference internal" title="syside.Feature.feature_value_expression"><span class="pre"><code class="sourceCode python">feature_value_expression</code></span></a> | <span class="pre">`R`</span> | The feature value <span class="pre">`Expression`</span> of this <span class="pre">`Feature`</span> if any. |
| <span class="nerd-font"></span> | <a href="#syside.Feature.feature_value_member" class="reference internal" title="syside.Feature.feature_value_member"><span class="pre"><code class="sourceCode python">feature_value_member</code></span></a> | <span class="pre">`R`</span> | Syside specific accessor for manipulating <span class="pre">`feature_value`</span>. |
| <span class="nerd-font"></span> | <a href="#syside.Feature.featuring_types" class="reference internal" title="syside.Feature.featuring_types"><span class="pre"><code class="sourceCode python">featuring_types</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`featuring_type`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Feature.first_chaining_feature" class="reference internal" title="syside.Feature.first_chaining_feature"><span class="pre"><code class="sourceCode python">first_chaining_feature</code></span></a> | <span class="pre">`R`</span> | The related <span class="pre">`Feature`</span> related by the first <span class="pre">`owned_feature_chaining`</span> if any. |
| <span class="nerd-font"></span> | <a href="#syside.Feature.is_composite" class="reference internal" title="syside.Feature.is_composite"><span class="pre"><code class="sourceCode python">is_composite</code></span></a> | <span class="pre">`RW`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`is_composite`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Feature.is_composite_explicitly" class="reference internal" title="syside.Feature.is_composite_explicitly"><span class="pre"><code class="sourceCode python">is_composite_explicitly</code></span></a> | <span class="pre">`R`</span> | Returns <span class="pre">`True`</span> if this <span class="pre">`Feature`</span> has been declared <span class="pre">`composite`</span> in the textual syntax. |
| <span class="nerd-font"></span> | <a href="#syside.Feature.is_constant" class="reference internal" title="syside.Feature.is_constant"><span class="pre"><code class="sourceCode python">is_constant</code></span></a> | <span class="pre">`RW`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`is_constant`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Feature.is_constant_explicitly" class="reference internal" title="syside.Feature.is_constant_explicitly"><span class="pre"><code class="sourceCode python">is_constant_explicitly</code></span></a> | <span class="pre">`R`</span> | Returns <span class="pre">`True`</span> if this <span class="pre">`Feature`</span> has been declared <span class="pre">`constant`</span> in the textual syntax. |
| <span class="nerd-font"></span> | <a href="#syside.Feature.is_derived" class="reference internal" title="syside.Feature.is_derived"><span class="pre"><code class="sourceCode python">is_derived</code></span></a> | <span class="pre">`RW`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`is_derived`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Feature.is_end" class="reference internal" title="syside.Feature.is_end"><span class="pre"><code class="sourceCode python">is_end</code></span></a> | <span class="pre">`RW`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`is_end`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Feature.is_end_explicitly" class="reference internal" title="syside.Feature.is_end_explicitly"><span class="pre"><code class="sourceCode python">is_end_explicitly</code></span></a> | <span class="pre">`R`</span> | Returns <span class="pre">`True`</span> if this <span class="pre">`Feature`</span> has been declared <span class="pre">`end`</span> in the textual syntax. |
| <span class="nerd-font"></span> | <a href="#syside.Feature.is_nonunique" class="reference internal" title="syside.Feature.is_nonunique"><span class="pre"><code class="sourceCode python">is_nonunique</code></span></a> | <span class="pre">`RW`</span> |  |
| <span class="nerd-font"></span> | <a href="#syside.Feature.is_ordered" class="reference internal" title="syside.Feature.is_ordered"><span class="pre"><code class="sourceCode python">is_ordered</code></span></a> | <span class="pre">`RW`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`is_ordered`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Feature.is_portion" class="reference internal" title="syside.Feature.is_portion"><span class="pre"><code class="sourceCode python">is_portion</code></span></a> | <span class="pre">`RW`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`is_portion`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Feature.is_read_only" class="reference internal" title="syside.Feature.is_read_only"><span class="pre"><code class="sourceCode python">is_read_only</code></span></a> | <span class="pre">`RW`</span> | Alias for is_constant. |
| <span class="nerd-font"></span> | <a href="#syside.Feature.is_unique" class="reference internal" title="syside.Feature.is_unique"><span class="pre"><code class="sourceCode python">is_unique</code></span></a> | <span class="pre">`RW`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`is_unique`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Feature.is_variable" class="reference internal" title="syside.Feature.is_variable"><span class="pre"><code class="sourceCode python">is_variable</code></span></a> | <span class="pre">`RW`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`is_variable`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Feature.is_variable_explicitly" class="reference internal" title="syside.Feature.is_variable_explicitly"><span class="pre"><code class="sourceCode python">is_variable_explicitly</code></span></a> | <span class="pre">`R`</span> | Returns <span class="pre">`True`</span> if this <span class="pre">`Feature`</span> has been declared <span class="pre">`variable`</span> in the textual syntax. |
| <span class="nerd-font"></span> | <a href="#syside.Feature.last_chaining_feature" class="reference internal" title="syside.Feature.last_chaining_feature"><span class="pre"><code class="sourceCode python">last_chaining_feature</code></span></a> | <span class="pre">`R`</span> | The related <span class="pre">`Feature`</span> related by the last <span class="pre">`owned_feature_chaining`</span> if any. |
| <span class="nerd-font"></span> | <a href="#syside.Feature.owned_cross_feature" class="reference internal" title="syside.Feature.owned_cross_feature"><span class="pre"><code class="sourceCode python">owned_cross_feature</code></span></a> | <span class="pre">`R`</span> | The member <span class="pre">`Feature`</span> that is declared before any prefixes in the textual syntax. |
| <span class="nerd-font"></span> | <a href="#syside.Feature.owned_cross_feature_member" class="reference internal" title="syside.Feature.owned_cross_feature_member"><span class="pre"><code class="sourceCode python">owned_cross_feature_member</code></span></a> | <span class="pre">`R`</span> | Syside specific accessor for either owned crossing_feature or crossing_multiplicity. This is the member <span class="pre">`Feature`</span> that is declared before any prefixes in the textual syntax. |
| <span class="nerd-font"></span> | <a href="#syside.Feature.owned_cross_subsetting" class="reference internal" title="syside.Feature.owned_cross_subsetting"><span class="pre"><code class="sourceCode python">owned_cross_subsetting</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_cross_subsetting`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Feature.owned_feature_chainings" class="reference internal" title="syside.Feature.owned_feature_chainings"><span class="pre"><code class="sourceCode python">owned_feature_chainings</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_feature_chaining`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Feature.owned_feature_invertings" class="reference internal" title="syside.Feature.owned_feature_invertings"><span class="pre"><code class="sourceCode python">owned_feature_invertings</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_feature_inverting`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Feature.owned_redefinitions" class="reference internal" title="syside.Feature.owned_redefinitions"><span class="pre"><code class="sourceCode python">owned_redefinitions</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_redefinition`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Feature.owned_reference_subsetting" class="reference internal" title="syside.Feature.owned_reference_subsetting"><span class="pre"><code class="sourceCode python">owned_reference_subsetting</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_reference_subsetting`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Feature.owned_subsettings" class="reference internal" title="syside.Feature.owned_subsettings"><span class="pre"><code class="sourceCode python">owned_subsettings</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_subsetting`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Feature.owned_type_featurings" class="reference internal" title="syside.Feature.owned_type_featurings"><span class="pre"><code class="sourceCode python">owned_type_featurings</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_type_featuring`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Feature.owned_typings" class="reference internal" title="syside.Feature.owned_typings"><span class="pre"><code class="sourceCode python">owned_typings</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_typing`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Feature.owning_feature_membership" class="reference internal" title="syside.Feature.owning_feature_membership"><span class="pre"><code class="sourceCode python">owning_feature_membership</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owning_feature_membership`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Feature.owning_type" class="reference internal" title="syside.Feature.owning_type"><span class="pre"><code class="sourceCode python">owning_type</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owning_type`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Feature.referenced_feature" class="reference internal" title="syside.Feature.referenced_feature"><span class="pre"><code class="sourceCode python">referenced_feature</code></span></a> | <span class="pre">`R`</span> | Returns the <span class="pre">`Feature`</span> this <span class="pre">`Feature`</span> references through <span class="pre">`ReferenceSubsetting`</span> if any. |
| <span class="nerd-font"></span> | <a href="#syside.Feature.referenced_feature_target" class="reference internal" title="syside.Feature.referenced_feature_target"><span class="pre"><code class="sourceCode python">referenced_feature_target</code></span></a> | <span class="pre">`R`</span> | Returns the <span class="pre">`feature_target`</span> of <span class="pre">`referenced_feature`</span>, i.e. <span class="pre">`referenced_feature.feature_target`</span>. |
| <span class="nerd-font"></span> | <a href="#syside.Feature.types" class="reference internal" title="syside.Feature.types"><span class="pre"><code class="sourceCode python">types</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`type`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Feature.find_owned_cross_feature" class="reference internal" title="syside.Feature.find_owned_cross_feature"><span class="pre"><code class="sourceCode python">find_owned_cross_feature</code></span></a> |  | Find the owned cross feature by potentially checking children. This is needed for spec that defined owned cross feature as the first member feature that is not a MetadataFeature or Multiplicity of an end feature. Since SysML does not allow member features (member keyword in KerML), this is equivalent to owned_cross_feature in SysML. |
| <span class="nerd-font"></span> | <a href="#syside.Feature.try_set_is_variable" class="reference internal" title="syside.Feature.try_set_is_variable"><span class="pre"><code class="sourceCode python">try_set_is_variable</code></span></a> |  | Non-raising variant of <span class="pre">`is_variable`</span> setter that returns <span class="pre">`False`</span> on <span class="pre">`Usages`</span> without modifying <span class="pre">`is_variable`</span>. |

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

<span class="sig-name descname"><span class="pre">STD</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><span class="pre">type</span><span class="p"><span class="pre">\[</span></span><a href="#syside.Feature" class="reference internal" title="syside.Feature"><span class="pre">syside.Feature</span></a><span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="p"><span class="pre">...</span></span><span class="p"><span class="pre">\]</span></span><span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">()</span>*<a href="#syside.Feature.STD" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">basic_feature</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="#syside.Feature" class="reference internal" title="syside.Feature"><span class="pre">syside.Feature</span></a>*<a href="#syside.Feature.basic_feature" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
The <span class="pre">`last_chaining_feature`</span> if one exists, otherwise this <span class="pre">`Feature`</span>.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">chaining_features</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="#syside.Feature" class="reference internal" title="syside.Feature"><span class="pre">syside.Feature</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Feature.chaining_features" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`chaining_feature`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The <span class="pre">`Feature`</span> that are chained together to determine the values of this <span class="pre">`Feature`</span>, derived from the <span class="pre">`chaining_features`</span> of the <span class="pre">`owned_feature_chainings`</span> of this <span class="pre">`Feature`</span>, in the same order. The values of a <span class="pre">`Feature`</span> with <span class="pre">`chaining_features`</span> are the same as values of the last <span class="pre">`Feature`</span> in the chain, which can be found by starting with the values of the first <span class="pre">`Feature`</span> (for each instance of the domain of the original <span class="pre">`Feature`</span>), then using each of those as domain instances to find the values of the second <span class="pre">`Feature`</span> in chaining_features, and so on, to values of the last <span class="pre">`Feature`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=188" class="reference external" target="_blank">8.3.3.3.4</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">cross_feature</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="#syside.Feature" class="reference internal" title="syside.Feature"><span class="pre">syside.Feature</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span>*<a href="#syside.Feature.cross_feature" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`cross_feature`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The second <span class="pre">`chaining_feature`</span> of the <span class="pre">`crossed_feature`</span> of the <span class="pre">`owned_cross_subsetting`</span> of this <span class="pre">`Feature`</span>, if it has one. Semantically, the values of the <span class="pre">`cross_feature`</span> of an end <span class="pre">`Feature`</span> must include all values of the end <span class="pre">`Feature`</span> obtained when navigating from values of the other end <span class="pre">`Features`</span> of the same <span class="pre">`owning_type`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=188" class="reference external" target="_blank">8.3.3.3.4</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">direction</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside.FeatureDirectionKind"><span class="pre">syside.FeatureDirectionKind</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span>*<a href="#syside.Feature.direction" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`direction`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> Indicates how values of this <span class="pre">`Feature`</span> are determined or used (as specified for the <span class="pre">`FeatureDirectionKind`</span>).
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=188" class="reference external" target="_blank">8.3.3.3.4</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">end_owning_type</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type"><span class="pre">syside.Type</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span>*<a href="#syside.Feature.end_owning_type" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`end_owning_type`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The <span class="pre">`Type`</span> that is related to this <span class="pre">`Feature`</span> by an <span class="pre">`EndFeatureMembership`</span> in which the <span class="pre">`Feature`</span> is an <span class="pre">`owned_member_feature`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=188" class="reference external" target="_blank">8.3.3.3.4</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">explicit_direction</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside.FeatureDirectionKind"><span class="pre">syside.FeatureDirectionKind</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span>*<a href="#syside.Feature.explicit_direction" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Returns the direction this <span class="pre">`Feature`</span> has been declared with in the textual syntax.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">feature_target</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="#syside.Feature" class="reference internal" title="syside.Feature"><span class="pre">syside.Feature</span></a>*<a href="#syside.Feature.feature_target" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`feature_target`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The last of the <span class="pre">`chaining_features`</span> of this <span class="pre">`Feature`</span>, if it has any. Otherwise, this <span class="pre">`Feature`</span> itself.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=188" class="reference external" target="_blank">8.3.3.3.4</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">feature_value</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/FeatureValue.md" class="reference internal" title="syside.FeatureValue"><span class="pre">syside.FeatureValue</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span>*<a href="#syside.Feature.feature_value" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
The <span class="pre">`FeatureValue`</span> owned by this <span class="pre">`Feature`</span> if any.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">feature_value_expression</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/Expression.md" class="reference internal" title="syside.Expression"><span class="pre">syside.Expression</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span>*<a href="#syside.Feature.feature_value_expression" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
The feature value <span class="pre">`Expression`</span> of this <span class="pre">`Feature`</span> if any.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">feature_value_member</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/FeatureValueAccessor.md" class="reference internal" title="syside.FeatureValueAccessor"><span class="pre">syside.FeatureValueAccessor</span></a>*<a href="#syside.Feature.feature_value_member" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Syside specific accessor for manipulating <span class="pre">`feature_value`</span>.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">featuring_types</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type"><span class="pre">syside.Type</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Feature.featuring_types" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`featuring_type`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> <span class="pre">`Types`</span> that feature this <span class="pre">`Feature`</span>, such that any instance in the domain of the <span class="pre">`Feature`</span> must be classified by all of these <span class="pre">`Types`</span>, including at least all the <span class="pre">`featuring_types`</span> of its <span class="pre">`type_featurings`</span>. If the <span class="pre">`Feature`</span> is chained, then the <span class="pre">`featuring_types`</span> of the first <span class="pre">`Feature`</span> in the chain are also <span class="pre">`featuring_types`</span> of the chained <span class="pre">`Feature`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=188" class="reference external" target="_blank">8.3.3.3.4</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">first_chaining_feature</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="#syside.Feature" class="reference internal" title="syside.Feature"><span class="pre">syside.Feature</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span>*<a href="#syside.Feature.first_chaining_feature" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
The related <span class="pre">`Feature`</span> related by the first <span class="pre">`owned_feature_chaining`</span> if any.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">is_composite</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*<a href="#syside.Feature.is_composite" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`is_composite`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> Whether the <span class="pre">`Feature`</span> is a composite <span class="pre">`feature`</span> of its <span class="pre">`featuring_type`</span>. If so, the values of the <span class="pre">`Feature`</span> cannot exist after its featuring instance no longer does and cannot be values of another composite feature that is not on the same featuring instance.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=189" class="reference external" target="_blank">8.3.3.3.4</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">is_composite_explicitly</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*<a href="#syside.Feature.is_composite_explicitly" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Returns <span class="pre">`True`</span> if this <span class="pre">`Feature`</span> has been declared <span class="pre">`composite`</span> in the textual syntax.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">is_constant</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*<a href="#syside.Feature.is_constant" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`is_constant`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> If <span class="pre">`is_variable`</span> is true, then whether the value of this <span class="pre">`Feature`</span> nevertheless does not change over all <span class="pre">`snapshots`</span> of its <span class="pre">`owning_type`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=189" class="reference external" target="_blank">8.3.3.3.4</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">is_constant_explicitly</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*<a href="#syside.Feature.is_constant_explicitly" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Returns <span class="pre">`True`</span> if this <span class="pre">`Feature`</span> has been declared <span class="pre">`constant`</span> in the textual syntax.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">is_derived</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*<a href="#syside.Feature.is_derived" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`is_derived`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> Whether the values of this <span class="pre">`Feature`</span> can always be computed from the values of other <span class="pre">`Features`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=189" class="reference external" target="_blank">8.3.3.3.4</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">is_end</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*<a href="#syside.Feature.is_end" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`is_end`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> Whether or not this <span class="pre">`Feature`</span> is an end <span class="pre">`Feature`</span>. An end <span class="pre">`Feature`</span> always has multiplicity 1, mapping each of its domain instances to a single co-domain instance. However, it may have a <span class="pre">`cross_feature`</span>, in which case values of the <span class="pre">`cross_feature`</span> must be the same as those found by navigation across instances of the <span class="pre">`owning_type`</span> from values of other end <span class="pre">`Features`</span> to values of this Feature. If the <span class="pre">`owning_type`</span> has *n* end <span class="pre">`Features`</span>, then the multiplicity, ordering, and uniqueness declared for the <span class="pre">`cross_feature`</span> of any one of these end <span class="pre">`Features`</span> constrains the cardinality, ordering, and uniqueness of the collection of values of that <span class="pre">`Feature`</span> reached by navigation when the values of the other *n-1* end <span class="pre">`Features`</span> are held fixed.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=189" class="reference external" target="_blank">8.3.3.3.4</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">is_end_explicitly</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*<a href="#syside.Feature.is_end_explicitly" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Returns <span class="pre">`True`</span> if this <span class="pre">`Feature`</span> has been declared <span class="pre">`end`</span> in the textual syntax.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">is_nonunique</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*<a href="#syside.Feature.is_nonunique" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">is_ordered</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*<a href="#syside.Feature.is_ordered" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`is_ordered`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> Whether an order exists for the values of this <span class="pre">`Feature`</span> or not.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=189" class="reference external" target="_blank">8.3.3.3.4</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">is_portion</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*<a href="#syside.Feature.is_portion" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`is_portion`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> Whether the values of this <span class="pre">`Feature`</span> are contained in the space and time of instances of the domain of the <span class="pre">`Feature`</span> and represent the same thing as those instances.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=189" class="reference external" target="_blank">8.3.3.3.4</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">is_read_only</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*<a href="#syside.Feature.is_read_only" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Alias for is_constant.

Removed in 2025-04 specification, will be removed in a future Syside release.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">is_unique</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*<a href="#syside.Feature.is_unique" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`is_unique`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> Whether or not values for this <span class="pre">`Feature`</span> must have no duplicates or not.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=189" class="reference external" target="_blank">8.3.3.3.4</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">is_variable</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*<a href="#syside.Feature.is_variable" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`is_variable`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> Whether the value of this <span class="pre">`Feature`</span> might vary over time. That is, whether the <span class="pre">`Feature`</span> may have a different value for each <span class="pre">`snapshot`</span> of an <span class="pre">`owning_type`</span> that is an <span class="pre">`Occurrence`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=189" class="reference external" target="_blank">8.3.3.3.4</a> of the KerML specification for more details.

Note that this will raise <span class="pre">`TypeError`</span> if attempting to set <span class="pre">`is_variable`</span> on <span class="pre">`Usages`</span> because it is computed by sema, see <span class="pre">`Usage.may_time_vary`</span>. Prefer using <span class="pre">`try_set_is_variable`</span> for non-raising behaviour.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">is_variable_explicitly</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*<a href="#syside.Feature.is_variable_explicitly" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Returns <span class="pre">`True`</span> if this <span class="pre">`Feature`</span> has been declared <span class="pre">`variable`</span> in the textual syntax.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">last_chaining_feature</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="#syside.Feature" class="reference internal" title="syside.Feature"><span class="pre">syside.Feature</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span>*<a href="#syside.Feature.last_chaining_feature" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
The related <span class="pre">`Feature`</span> related by the last <span class="pre">`owned_feature_chaining`</span> if any.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned_cross_feature</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="#syside.Feature" class="reference internal" title="syside.Feature"><span class="pre">syside.Feature</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span>*<a href="#syside.Feature.owned_cross_feature" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
The member <span class="pre">`Feature`</span> that is declared before any prefixes in the textual syntax.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned_cross_feature_member</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/OwnedFeatureAccessor.md" class="reference internal" title="syside.OwnedFeatureAccessor"><span class="pre">syside.OwnedFeatureAccessor</span></a>*<a href="#syside.Feature.owned_cross_feature_member" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Syside specific accessor for either owned crossing_feature or crossing_multiplicity. This is the member <span class="pre">`Feature`</span> that is declared before any prefixes in the textual syntax.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned_cross_subsetting</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/CrossSubsetting.md" class="reference internal" title="syside.CrossSubsetting"><span class="pre">syside.CrossSubsetting</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span>*<a href="#syside.Feature.owned_cross_subsetting" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owned_cross_subsetting`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The one <span class="pre">`owned_subsetting`</span> of this <span class="pre">`Feature`</span>, if any, that is a <span class="pre">`CrossSubsetting},`</span>` `<span class="pre">`for`</span>` `<span class="pre">`which`</span>` `<span class="pre">`the`</span>` `<span class="pre">`Feature`</span>` `<span class="pre">`is`</span>` `<span class="pre">`the`</span>` `<span class="pre">`crossing_feature.`</span>
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=189" class="reference external" target="_blank">8.3.3.3.4</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned_feature_chainings</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/FeatureChaining.md" class="reference internal" title="syside.FeatureChaining"><span class="pre">syside.FeatureChaining</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Feature.owned_feature_chainings" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owned_feature_chaining`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The <span class="pre">`owned_relationships`</span> of this <span class="pre">`Feature`</span> that are <span class="pre">`FeatureChainings`</span>, for which the <span class="pre">`Feature`</span> will be the <span class="pre">`feature_chained`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=189" class="reference external" target="_blank">8.3.3.3.4</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned_feature_invertings</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/FeatureInverting.md" class="reference internal" title="syside.FeatureInverting"><span class="pre">syside.FeatureInverting</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Feature.owned_feature_invertings" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owned_feature_inverting`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The <span class="pre">`owned_relationships`</span> of this <span class="pre">`Feature`</span> that are <span class="pre">`FeatureInvertings`</span> and for which the <span class="pre">`Feature`</span> is the <span class="pre">`feature_inverted`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=190" class="reference external" target="_blank">8.3.3.3.4</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned_redefinitions</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Redefinition.md" class="reference internal" title="syside.Redefinition"><span class="pre">syside.Redefinition</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Feature.owned_redefinitions" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owned_redefinition`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The <span class="pre">`owned_subsettings`</span> of this <span class="pre">`Feature`</span> that are <span class="pre">`Redefinitions`</span>, for which the <span class="pre">`Feature`</span> is the <span class="pre">`redefining_feature`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=190" class="reference external" target="_blank">8.3.3.3.4</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned_reference_subsetting</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/ReferenceSubsetting.md" class="reference internal" title="syside.ReferenceSubsetting"><span class="pre">syside.ReferenceSubsetting</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span>*<a href="#syside.Feature.owned_reference_subsetting" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owned_reference_subsetting`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The one <span class="pre">`owned_subsetting`</span> of this <span class="pre">`Feature`</span>, if any, that is a <span class="pre">`ReferenceSubsetting`</span>, for which the <span class="pre">`Feature`</span> is the <span class="pre">`referencing_feature`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=190" class="reference external" target="_blank">8.3.3.3.4</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned_subsettings</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Subsetting.md" class="reference internal" title="syside.Subsetting"><span class="pre">syside.Subsetting</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Feature.owned_subsettings" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owned_subsetting`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The <span class="pre">`owned_specializations`</span> of this <span class="pre">`Feature`</span> that are <span class="pre">`Subsettings`</span>, for which the <span class="pre">`Feature`</span> is the <span class="pre">`subsetting_feature`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=190" class="reference external" target="_blank">8.3.3.3.4</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned_type_featurings</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/TypeFeaturing.md" class="reference internal" title="syside.TypeFeaturing"><span class="pre">syside.TypeFeaturing</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Feature.owned_type_featurings" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owned_type_featuring`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The <span class="pre">`owned_relationships`</span> of this <span class="pre">`Feature`</span> that are <span class="pre">`TypeFeaturings`</span> and for which the <span class="pre">`Feature`</span> is the <span class="pre">`feature_of_type`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=190" class="reference external" target="_blank">8.3.3.3.4</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned_typings</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/FeatureTyping.md" class="reference internal" title="syside.FeatureTyping"><span class="pre">syside.FeatureTyping</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Feature.owned_typings" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owned_typing`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The <span class="pre">`owned_specializations`</span> of this <span class="pre">`Feature`</span> that are <span class="pre">`FeatureTypings`</span>, for which the <span class="pre">`Feature`</span> is the <span class="pre">`typed_feature`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=190" class="reference external" target="_blank">8.3.3.3.4</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owning_feature_membership</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/FeatureMembership.md" class="reference internal" title="syside.FeatureMembership"><span class="pre">syside.FeatureMembership</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span>*<a href="#syside.Feature.owning_feature_membership" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owning_feature_membership`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The <span class="pre">`FeatureMembership`</span> that owns this <span class="pre">`Feature`</span> as an <span class="pre">`owned_member_feature`</span>, determining its <span class="pre">`owning_type`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=190" class="reference external" target="_blank">8.3.3.3.4</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owning_type</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type"><span class="pre">syside.Type</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span>*<a href="#syside.Feature.owning_type" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owning_type`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The <span class="pre">`Type`</span> that is the <span class="pre">`owning_type`</span> of the <span class="pre">`owning_feature_membership`</span> of this <span class="pre">`Feature`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=190" class="reference external" target="_blank">8.3.3.3.4</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">referenced_feature</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="#syside.Feature" class="reference internal" title="syside.Feature"><span class="pre">syside.Feature</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span>*<a href="#syside.Feature.referenced_feature" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Returns the <span class="pre">`Feature`</span> this <span class="pre">`Feature`</span> references through <span class="pre">`ReferenceSubsetting`</span> if any.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">referenced_feature_target</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="#syside.Feature" class="reference internal" title="syside.Feature"><span class="pre">syside.Feature</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span>*<a href="#syside.Feature.referenced_feature_target" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Returns the <span class="pre">`feature_target`</span> of <span class="pre">`referenced_feature`</span>, i.e. <span class="pre">`referenced_feature.feature_target`</span>.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">types</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type"><span class="pre">syside.Type</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Feature.types" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`type`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> <span class="pre">`Types`</span> that restrict the values of this <span class="pre">`Feature`</span>, such that the values must be instances of all the <span class="pre">`types`</span>. The types of a <span class="pre">`Feature`</span> are derived from its <span class="pre">`typings`</span> and the <span class="pre">`types`</span> of its <span class="pre">`subsettings`</span>. If the <span class="pre">`Feature`</span> is chained, then the <span class="pre">`types`</span> of the last <span class="pre">`Feature`</span> in the chain are also <span class="pre">`types`</span> of the chained <span class="pre">`Feature`</span>.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=190" class="reference external" target="_blank">8.3.3.3.4</a> of the KerML specification for more details.

<span class="nerd-font"></span> **Methods**

<span class="sig-name descname"><span class="pre">find_owned_cross_feature</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="#syside.Feature" class="reference internal" title="syside.Feature"><span class="pre">syside.Feature</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span></span></span><a href="#syside.Feature.find_owned_cross_feature" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Find the owned cross feature by potentially checking children. This is needed for spec that defined owned cross feature as the first member feature that is not a MetadataFeature or Multiplicity of an end feature. Since SysML does not allow member features (member keyword in KerML), this is equivalent to owned_cross_feature in SysML.

<span class="sig-name descname"><span class="pre">try_set_is_variable</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">bool</span></span></span><a href="#syside.Feature.try_set_is_variable" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Non-raising variant of <span class="pre">`is_variable`</span> setter that returns <span class="pre">`False`</span> on <span class="pre">`Usages`</span> without modifying <span class="pre">`is_variable`</span>.

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/ActionDefinition.md" class="reference internal" title="syside.ActionDefinition"><span class="pre"><code class="sourceCode python">syside.ActionDefinition</code></span></a>

  - <a href="/python/v0.8.4/syside/ActionDefinition.md" class="reference internal" title="syside.ActionDefinition.parameters"><span class="pre"><code class="sourceCode python">parameters</code></span></a>

- <a href="/python/v0.8.4/syside/ActionUsage.md" class="reference internal" title="syside.ActionUsage"><span class="pre"><code class="sourceCode python">syside.ActionUsage</code></span></a>

  - <a href="/python/v0.8.4/syside/ActionUsage.md" class="reference internal" title="syside.ActionUsage.owned_parameters"><span class="pre"><code class="sourceCode python">owned_parameters</code></span></a>

  - <a href="/python/v0.8.4/syside/ActionUsage.md" class="reference internal" title="syside.ActionUsage.parameters"><span class="pre"><code class="sourceCode python">parameters</code></span></a>

- <a href="/python/v0.8.4/syside/AssignmentActionUsage.md" class="reference internal" title="syside.AssignmentActionUsage"><span class="pre"><code class="sourceCode python">syside.AssignmentActionUsage</code></span></a>

  - <a href="/python/v0.8.4/syside/AssignmentActionUsage.md" class="reference internal" title="syside.AssignmentActionUsage.referent"><span class="pre"><code class="sourceCode python">referent</code></span></a>

- <a href="/python/v0.8.4/syside/Association.md" class="reference internal" title="syside.Association"><span class="pre"><code class="sourceCode python">syside.Association</code></span></a>

  - <a href="/python/v0.8.4/syside/Association.md" class="reference internal" title="syside.Association.association_ends"><span class="pre"><code class="sourceCode python">association_ends</code></span></a>

  - <a href="/python/v0.8.4/syside/Association.md" class="reference internal" title="syside.Association.owned_related_elements"><span class="pre"><code class="sourceCode python">owned_related_elements</code></span></a>

  - <a href="/python/v0.8.4/syside/Association.md" class="reference internal" title="syside.Association.related_elements"><span class="pre"><code class="sourceCode python">related_elements</code></span></a>

  - <a href="/python/v0.8.4/syside/Association.md" class="reference internal" title="syside.Association.source"><span class="pre"><code class="sourceCode python">source</code></span></a>

  - <a href="/python/v0.8.4/syside/Association.md" class="reference internal" title="syside.Association.sources"><span class="pre"><code class="sourceCode python">sources</code></span></a>

  - <a href="/python/v0.8.4/syside/Association.md" class="reference internal" title="syside.Association.targets"><span class="pre"><code class="sourceCode python">targets</code></span></a>

- <a href="/python/v0.8.4/syside/Behavior.md" class="reference internal" title="syside.Behavior"><span class="pre"><code class="sourceCode python">syside.Behavior</code></span></a>

  - <a href="/python/v0.8.4/syside/Behavior.md" class="reference internal" title="syside.Behavior.parameters"><span class="pre"><code class="sourceCode python">parameters</code></span></a>

- <a href="/python/v0.8.4/syside/CalculationDefinition.md" class="reference internal" title="syside.CalculationDefinition"><span class="pre"><code class="sourceCode python">syside.CalculationDefinition</code></span></a>

  - <a href="/python/v0.8.4/syside/CalculationDefinition.md" class="reference internal" title="syside.CalculationDefinition.any_result"><span class="pre"><code class="sourceCode python">any_result</code></span></a>

  - <a href="/python/v0.8.4/syside/CalculationDefinition.md" class="reference internal" title="syside.CalculationDefinition.result"><span class="pre"><code class="sourceCode python">result</code></span></a>

- <a href="/python/v0.8.4/syside/CalculationUsage.md" class="reference internal" title="syside.CalculationUsage"><span class="pre"><code class="sourceCode python">syside.CalculationUsage</code></span></a>

  - <a href="/python/v0.8.4/syside/CalculationUsage.md" class="reference internal" title="syside.CalculationUsage.result"><span class="pre"><code class="sourceCode python">result</code></span></a>

- <a href="/python/v0.8.4/syside/ChainedChildrenNodes.md" class="reference internal" title="syside.ChainedChildrenNodes"><span class="pre"><code class="sourceCode python">syside.ChainedChildrenNodes</code></span></a>

  - <a href="/python/v0.8.4/syside/ChainedChildrenNodes.md" class="reference internal" title="syside.ChainedChildrenNodes.append_chain"><span class="pre"><code class="sourceCode python">append_chain</code></span></a>

  - <a href="/python/v0.8.4/syside/ChainedChildrenNodes.md" class="reference internal" title="syside.ChainedChildrenNodes.insert_chain"><span class="pre"><code class="sourceCode python">insert_chain</code></span></a>

  - <a href="/python/v0.8.4/syside/ChainedChildrenNodes.md" class="reference internal" title="syside.ChainedChildrenNodes.replace_chain_at"><span class="pre"><code class="sourceCode python">replace_chain_at</code></span></a>

- <a href="/python/v0.8.4/syside/ChainedMemberAccessor.md" class="reference internal" title="syside.ChainedMemberAccessor"><span class="pre"><code class="sourceCode python">syside.ChainedMemberAccessor</code></span></a>

  - <a href="/python/v0.8.4/syside/ChainedMemberAccessor.md" class="reference internal" title="syside.ChainedMemberAccessor.set_member_element_chain"><span class="pre"><code class="sourceCode python">set_member_element_chain</code></span></a>

- <a href="/python/v0.8.4/syside/ChainedReferenceAccessor.md" class="reference internal" title="syside.ChainedReferenceAccessor"><span class="pre"><code class="sourceCode python">syside.ChainedReferenceAccessor</code></span></a>

  - <a href="/python/v0.8.4/syside/ChainedReferenceAccessor.md" class="reference internal" title="syside.ChainedReferenceAccessor.set_chain"><span class="pre"><code class="sourceCode python">set_chain</code></span></a>

  - <a href="/python/v0.8.4/syside/ChainedReferenceAccessor.md" class="reference internal" title="syside.ChainedReferenceAccessor.try_set_chain"><span class="pre"><code class="sourceCode python">try_set_chain</code></span></a>

- <a href="/python/v0.8.4/syside/Compiler.md" class="reference internal" title="syside.Compiler"><span class="pre"><code class="sourceCode python">syside.Compiler</code></span></a>

  - <a href="/python/v0.8.4/syside/Compiler.md" class="reference internal" title="syside.Compiler.evaluate_feature"><span class="pre"><code class="sourceCode python">evaluate_feature</code></span></a>

- <a href="/python/v0.8.4/syside/ConnectionDefinition.md" class="reference internal" title="syside.ConnectionDefinition"><span class="pre"><code class="sourceCode python">syside.ConnectionDefinition</code></span></a>

  - <a href="/python/v0.8.4/syside/ConnectionDefinition.md" class="reference internal" title="syside.ConnectionDefinition.association_ends"><span class="pre"><code class="sourceCode python">association_ends</code></span></a>

  - <a href="/python/v0.8.4/syside/ConnectionDefinition.md" class="reference internal" title="syside.ConnectionDefinition.owned_related_elements"><span class="pre"><code class="sourceCode python">owned_related_elements</code></span></a>

  - <a href="/python/v0.8.4/syside/ConnectionDefinition.md" class="reference internal" title="syside.ConnectionDefinition.related_elements"><span class="pre"><code class="sourceCode python">related_elements</code></span></a>

  - <a href="/python/v0.8.4/syside/ConnectionDefinition.md" class="reference internal" title="syside.ConnectionDefinition.source"><span class="pre"><code class="sourceCode python">source</code></span></a>

  - <a href="/python/v0.8.4/syside/ConnectionDefinition.md" class="reference internal" title="syside.ConnectionDefinition.sources"><span class="pre"><code class="sourceCode python">sources</code></span></a>

  - <a href="/python/v0.8.4/syside/ConnectionDefinition.md" class="reference internal" title="syside.ConnectionDefinition.targets"><span class="pre"><code class="sourceCode python">targets</code></span></a>

- <a href="/python/v0.8.4/syside/Connector.md" class="reference internal" title="syside.Connector"><span class="pre"><code class="sourceCode python">syside.Connector</code></span></a>

  - <a href="/python/v0.8.4/syside/Connector.md" class="reference internal" title="syside.Connector.connector_ends"><span class="pre"><code class="sourceCode python">connector_ends</code></span></a>

  - <a href="/python/v0.8.4/syside/Connector.md" class="reference internal" title="syside.Connector.owned_related_elements"><span class="pre"><code class="sourceCode python">owned_related_elements</code></span></a>

  - <a href="/python/v0.8.4/syside/Connector.md" class="reference internal" title="syside.Connector.related_elements"><span class="pre"><code class="sourceCode python">related_elements</code></span></a>

  - <a href="/python/v0.8.4/syside/Connector.md" class="reference internal" title="syside.Connector.related_features"><span class="pre"><code class="sourceCode python">related_features</code></span></a>

  - <a href="/python/v0.8.4/syside/Connector.md" class="reference internal" title="syside.Connector.source"><span class="pre"><code class="sourceCode python">source</code></span></a>

  - <a href="/python/v0.8.4/syside/Connector.md" class="reference internal" title="syside.Connector.source_feature"><span class="pre"><code class="sourceCode python">source_feature</code></span></a>

  - <a href="/python/v0.8.4/syside/Connector.md" class="reference internal" title="syside.Connector.sources"><span class="pre"><code class="sourceCode python">sources</code></span></a>

  - <a href="/python/v0.8.4/syside/Connector.md" class="reference internal" title="syside.Connector.target_features"><span class="pre"><code class="sourceCode python">target_features</code></span></a>

  - <a href="/python/v0.8.4/syside/Connector.md" class="reference internal" title="syside.Connector.targets"><span class="pre"><code class="sourceCode python">targets</code></span></a>

- <a href="/python/v0.8.4/syside/ConnectorAsUsage.md" class="reference internal" title="syside.ConnectorAsUsage"><span class="pre"><code class="sourceCode python">syside.ConnectorAsUsage</code></span></a>

  - <a href="/python/v0.8.4/syside/ConnectorAsUsage.md" class="reference internal" title="syside.ConnectorAsUsage.connector_ends"><span class="pre"><code class="sourceCode python">connector_ends</code></span></a>

  - <a href="/python/v0.8.4/syside/ConnectorAsUsage.md" class="reference internal" title="syside.ConnectorAsUsage.owned_related_elements"><span class="pre"><code class="sourceCode python">owned_related_elements</code></span></a>

  - <a href="/python/v0.8.4/syside/ConnectorAsUsage.md" class="reference internal" title="syside.ConnectorAsUsage.related_elements"><span class="pre"><code class="sourceCode python">related_elements</code></span></a>

  - <a href="/python/v0.8.4/syside/ConnectorAsUsage.md" class="reference internal" title="syside.ConnectorAsUsage.related_features"><span class="pre"><code class="sourceCode python">related_features</code></span></a>

  - <a href="/python/v0.8.4/syside/ConnectorAsUsage.md" class="reference internal" title="syside.ConnectorAsUsage.source"><span class="pre"><code class="sourceCode python">source</code></span></a>

  - <a href="/python/v0.8.4/syside/ConnectorAsUsage.md" class="reference internal" title="syside.ConnectorAsUsage.source_feature"><span class="pre"><code class="sourceCode python">source_feature</code></span></a>

  - <a href="/python/v0.8.4/syside/ConnectorAsUsage.md" class="reference internal" title="syside.ConnectorAsUsage.sources"><span class="pre"><code class="sourceCode python">sources</code></span></a>

  - <a href="/python/v0.8.4/syside/ConnectorAsUsage.md" class="reference internal" title="syside.ConnectorAsUsage.target_features"><span class="pre"><code class="sourceCode python">target_features</code></span></a>

  - <a href="/python/v0.8.4/syside/ConnectorAsUsage.md" class="reference internal" title="syside.ConnectorAsUsage.targets"><span class="pre"><code class="sourceCode python">targets</code></span></a>

- <a href="/python/v0.8.4/syside/ConstraintDefinition.md" class="reference internal" title="syside.ConstraintDefinition"><span class="pre"><code class="sourceCode python">syside.ConstraintDefinition</code></span></a>

  - <a href="/python/v0.8.4/syside/ConstraintDefinition.md" class="reference internal" title="syside.ConstraintDefinition.any_result"><span class="pre"><code class="sourceCode python">any_result</code></span></a>

  - <a href="/python/v0.8.4/syside/ConstraintDefinition.md" class="reference internal" title="syside.ConstraintDefinition.parameters"><span class="pre"><code class="sourceCode python">parameters</code></span></a>

  - <a href="/python/v0.8.4/syside/ConstraintDefinition.md" class="reference internal" title="syside.ConstraintDefinition.result"><span class="pre"><code class="sourceCode python">result</code></span></a>

- <a href="/python/v0.8.4/syside/ConstraintUsage.md" class="reference internal" title="syside.ConstraintUsage"><span class="pre"><code class="sourceCode python">syside.ConstraintUsage</code></span></a>

  - <a href="/python/v0.8.4/syside/ConstraintUsage.md" class="reference internal" title="syside.ConstraintUsage.owned_parameters"><span class="pre"><code class="sourceCode python">owned_parameters</code></span></a>

  - <a href="/python/v0.8.4/syside/ConstraintUsage.md" class="reference internal" title="syside.ConstraintUsage.parameters"><span class="pre"><code class="sourceCode python">parameters</code></span></a>

  - <a href="/python/v0.8.4/syside/ConstraintUsage.md" class="reference internal" title="syside.ConstraintUsage.result"><span class="pre"><code class="sourceCode python">result</code></span></a>

- <a href="/python/v0.8.4/syside/CrossSubsetting.md" class="reference internal" title="syside.CrossSubsetting"><span class="pre"><code class="sourceCode python">syside.CrossSubsetting</code></span></a>

  - <a href="/python/v0.8.4/syside/CrossSubsetting.md" class="reference internal" title="syside.CrossSubsetting.crossed_feature"><span class="pre"><code class="sourceCode python">crossed_feature</code></span></a>

  - <a href="/python/v0.8.4/syside/CrossSubsetting.md" class="reference internal" title="syside.CrossSubsetting.crossing_feature"><span class="pre"><code class="sourceCode python">crossing_feature</code></span></a>

- <a href="/python/v0.8.4/syside/Expression.md" class="reference internal" title="syside.Expression"><span class="pre"><code class="sourceCode python">syside.Expression</code></span></a>

  - <a href="/python/v0.8.4/syside/Expression.md" class="reference internal" title="syside.Expression.result"><span class="pre"><code class="sourceCode python">result</code></span></a>

- <a href="#syside.Feature" class="reference internal" title="syside.Feature"><span class="pre"><code class="sourceCode python">syside.Feature</code></span></a>

  - <a href="#syside.Feature.STD" class="reference internal" title="syside.Feature.STD"><span class="pre"><code class="sourceCode python">STD</code></span></a>

  - <a href="#syside.Feature.basic_feature" class="reference internal" title="syside.Feature.basic_feature"><span class="pre"><code class="sourceCode python">basic_feature</code></span></a>

  - <a href="#syside.Feature.chaining_features" class="reference internal" title="syside.Feature.chaining_features"><span class="pre"><code class="sourceCode python">chaining_features</code></span></a>

  - <a href="#syside.Feature.cross_feature" class="reference internal" title="syside.Feature.cross_feature"><span class="pre"><code class="sourceCode python">cross_feature</code></span></a>

  - <a href="#syside.Feature.feature_target" class="reference internal" title="syside.Feature.feature_target"><span class="pre"><code class="sourceCode python">feature_target</code></span></a>

  - <a href="#syside.Feature.find_owned_cross_feature" class="reference internal" title="syside.Feature.find_owned_cross_feature"><span class="pre"><code class="sourceCode python">find_owned_cross_feature</code></span></a>

  - <a href="#syside.Feature.first_chaining_feature" class="reference internal" title="syside.Feature.first_chaining_feature"><span class="pre"><code class="sourceCode python">first_chaining_feature</code></span></a>

  - <a href="#syside.Feature.last_chaining_feature" class="reference internal" title="syside.Feature.last_chaining_feature"><span class="pre"><code class="sourceCode python">last_chaining_feature</code></span></a>

  - <a href="#syside.Feature.owned_cross_feature" class="reference internal" title="syside.Feature.owned_cross_feature"><span class="pre"><code class="sourceCode python">owned_cross_feature</code></span></a>

  - <a href="#syside.Feature.referenced_feature" class="reference internal" title="syside.Feature.referenced_feature"><span class="pre"><code class="sourceCode python">referenced_feature</code></span></a>

  - <a href="#syside.Feature.referenced_feature_target" class="reference internal" title="syside.Feature.referenced_feature_target"><span class="pre"><code class="sourceCode python">referenced_feature_target</code></span></a>

- <a href="/python/v0.8.4/syside/FeatureChainExpression.md" class="reference internal" title="syside.FeatureChainExpression"><span class="pre"><code class="sourceCode python">syside.FeatureChainExpression</code></span></a>

  - <a href="/python/v0.8.4/syside/FeatureChainExpression.md" class="reference internal" title="syside.FeatureChainExpression.target_feature"><span class="pre"><code class="sourceCode python">target_feature</code></span></a>

- <a href="/python/v0.8.4/syside/FeatureChaining.md" class="reference internal" title="syside.FeatureChaining"><span class="pre"><code class="sourceCode python">syside.FeatureChaining</code></span></a>

  - <a href="/python/v0.8.4/syside/FeatureChaining.md" class="reference internal" title="syside.FeatureChaining.chaining_feature"><span class="pre"><code class="sourceCode python">chaining_feature</code></span></a>

  - <a href="/python/v0.8.4/syside/FeatureChaining.md" class="reference internal" title="syside.FeatureChaining.feature_chained"><span class="pre"><code class="sourceCode python">feature_chained</code></span></a>

- <a href="/python/v0.8.4/syside/FeatureInverting.md" class="reference internal" title="syside.FeatureInverting"><span class="pre"><code class="sourceCode python">syside.FeatureInverting</code></span></a>

  - <a href="/python/v0.8.4/syside/FeatureInverting.md" class="reference internal" title="syside.FeatureInverting.feature_inverted"><span class="pre"><code class="sourceCode python">feature_inverted</code></span></a>

  - <a href="/python/v0.8.4/syside/FeatureInverting.md" class="reference internal" title="syside.FeatureInverting.inverting_feature"><span class="pre"><code class="sourceCode python">inverting_feature</code></span></a>

  - <a href="/python/v0.8.4/syside/FeatureInverting.md" class="reference internal" title="syside.FeatureInverting.owning_feature"><span class="pre"><code class="sourceCode python">owning_feature</code></span></a>

- <a href="/python/v0.8.4/syside/FeatureMembership.md" class="reference internal" title="syside.FeatureMembership"><span class="pre"><code class="sourceCode python">syside.FeatureMembership</code></span></a>

  - <a href="/python/v0.8.4/syside/FeatureMembership.md" class="reference internal" title="syside.FeatureMembership.owned_member_feature"><span class="pre"><code class="sourceCode python">owned_member_feature</code></span></a>

- <a href="/python/v0.8.4/syside/FeatureReferenceExpression.md" class="reference internal" title="syside.FeatureReferenceExpression"><span class="pre"><code class="sourceCode python">syside.FeatureReferenceExpression</code></span></a>

  - <a href="/python/v0.8.4/syside/FeatureReferenceExpression.md" class="reference internal" title="syside.FeatureReferenceExpression.referent"><span class="pre"><code class="sourceCode python">referent</code></span></a>

- <a href="/python/v0.8.4/syside/FeatureTyping.md" class="reference internal" title="syside.FeatureTyping"><span class="pre"><code class="sourceCode python">syside.FeatureTyping</code></span></a>

  - <a href="/python/v0.8.4/syside/FeatureTyping.md" class="reference internal" title="syside.FeatureTyping.owning_feature"><span class="pre"><code class="sourceCode python">owning_feature</code></span></a>

  - <a href="/python/v0.8.4/syside/FeatureTyping.md" class="reference internal" title="syside.FeatureTyping.typed_feature"><span class="pre"><code class="sourceCode python">typed_feature</code></span></a>

- <a href="/python/v0.8.4/syside/FeatureValue.md" class="reference internal" title="syside.FeatureValue"><span class="pre"><code class="sourceCode python">syside.FeatureValue</code></span></a>

  - <a href="/python/v0.8.4/syside/FeatureValue.md" class="reference internal" title="syside.FeatureValue.feature_with_value"><span class="pre"><code class="sourceCode python">feature_with_value</code></span></a>

- <a href="/python/v0.8.4/syside/Flow.md" class="reference internal" title="syside.Flow"><span class="pre"><code class="sourceCode python">syside.Flow</code></span></a>

  - <a href="/python/v0.8.4/syside/Flow.md" class="reference internal" title="syside.Flow.owned_parameters"><span class="pre"><code class="sourceCode python">owned_parameters</code></span></a>

  - <a href="/python/v0.8.4/syside/Flow.md" class="reference internal" title="syside.Flow.parameters"><span class="pre"><code class="sourceCode python">parameters</code></span></a>

  - <a href="/python/v0.8.4/syside/Flow.md" class="reference internal" title="syside.Flow.source_output_feature"><span class="pre"><code class="sourceCode python">source_output_feature</code></span></a>

  - <a href="/python/v0.8.4/syside/Flow.md" class="reference internal" title="syside.Flow.target_input_feature"><span class="pre"><code class="sourceCode python">target_input_feature</code></span></a>

- <a href="/python/v0.8.4/syside/FlowDefinition.md" class="reference internal" title="syside.FlowDefinition"><span class="pre"><code class="sourceCode python">syside.FlowDefinition</code></span></a>

  - <a href="/python/v0.8.4/syside/FlowDefinition.md" class="reference internal" title="syside.FlowDefinition.association_ends"><span class="pre"><code class="sourceCode python">association_ends</code></span></a>

  - <a href="/python/v0.8.4/syside/FlowDefinition.md" class="reference internal" title="syside.FlowDefinition.owned_related_elements"><span class="pre"><code class="sourceCode python">owned_related_elements</code></span></a>

  - <a href="/python/v0.8.4/syside/FlowDefinition.md" class="reference internal" title="syside.FlowDefinition.related_elements"><span class="pre"><code class="sourceCode python">related_elements</code></span></a>

  - <a href="/python/v0.8.4/syside/FlowDefinition.md" class="reference internal" title="syside.FlowDefinition.source"><span class="pre"><code class="sourceCode python">source</code></span></a>

  - <a href="/python/v0.8.4/syside/FlowDefinition.md" class="reference internal" title="syside.FlowDefinition.sources"><span class="pre"><code class="sourceCode python">sources</code></span></a>

  - <a href="/python/v0.8.4/syside/FlowDefinition.md" class="reference internal" title="syside.FlowDefinition.targets"><span class="pre"><code class="sourceCode python">targets</code></span></a>

- <a href="/python/v0.8.4/syside/FlowUsage.md" class="reference internal" title="syside.FlowUsage"><span class="pre"><code class="sourceCode python">syside.FlowUsage</code></span></a>

  - <a href="/python/v0.8.4/syside/FlowUsage.md" class="reference internal" title="syside.FlowUsage.owned_parameters"><span class="pre"><code class="sourceCode python">owned_parameters</code></span></a>

  - <a href="/python/v0.8.4/syside/FlowUsage.md" class="reference internal" title="syside.FlowUsage.parameters"><span class="pre"><code class="sourceCode python">parameters</code></span></a>

  - <a href="/python/v0.8.4/syside/FlowUsage.md" class="reference internal" title="syside.FlowUsage.source_output_feature"><span class="pre"><code class="sourceCode python">source_output_feature</code></span></a>

  - <a href="/python/v0.8.4/syside/FlowUsage.md" class="reference internal" title="syside.FlowUsage.target_input_feature"><span class="pre"><code class="sourceCode python">target_input_feature</code></span></a>

- <a href="/python/v0.8.4/syside/Function.md" class="reference internal" title="syside.Function"><span class="pre"><code class="sourceCode python">syside.Function</code></span></a>

  - <a href="/python/v0.8.4/syside/Function.md" class="reference internal" title="syside.Function.any_result"><span class="pre"><code class="sourceCode python">any_result</code></span></a>

  - <a href="/python/v0.8.4/syside/Function.md" class="reference internal" title="syside.Function.result"><span class="pre"><code class="sourceCode python">result</code></span></a>

- <a href="/python/v0.8.4/syside/Heritage.md" class="reference internal" title="syside.Heritage"><span class="pre"><code class="sourceCode python">syside.Heritage</code></span></a>

  - <a href="/python/v0.8.4/syside/Heritage.md" class="reference internal" title="syside.Heritage.append_chain"><span class="pre"><code class="sourceCode python">append_chain</code></span></a>

  - <a href="/python/v0.8.4/syside/Heritage.md" class="reference internal" title="syside.Heritage.insert_chain"><span class="pre"><code class="sourceCode python">insert_chain</code></span></a>

  - <a href="/python/v0.8.4/syside/Heritage.md" class="reference internal" title="syside.Heritage.replace_chain_at"><span class="pre"><code class="sourceCode python">replace_chain_at</code></span></a>

- <a href="/python/v0.8.4/syside/Interaction.md" class="reference internal" title="syside.Interaction"><span class="pre"><code class="sourceCode python">syside.Interaction</code></span></a>

  - <a href="/python/v0.8.4/syside/Interaction.md" class="reference internal" title="syside.Interaction.parameters"><span class="pre"><code class="sourceCode python">parameters</code></span></a>

- <a href="/python/v0.8.4/syside/ParameterMembership.md" class="reference internal" title="syside.ParameterMembership"><span class="pre"><code class="sourceCode python">syside.ParameterMembership</code></span></a>

  - <a href="/python/v0.8.4/syside/ParameterMembership.md" class="reference internal" title="syside.ParameterMembership.owned_member_parameter"><span class="pre"><code class="sourceCode python">owned_member_parameter</code></span></a>

- <a href="/python/v0.8.4/syside/Redefinition.md" class="reference internal" title="syside.Redefinition"><span class="pre"><code class="sourceCode python">syside.Redefinition</code></span></a>

  - <a href="/python/v0.8.4/syside/Redefinition.md" class="reference internal" title="syside.Redefinition.redefined_feature"><span class="pre"><code class="sourceCode python">redefined_feature</code></span></a>

  - <a href="/python/v0.8.4/syside/Redefinition.md" class="reference internal" title="syside.Redefinition.redefining_feature"><span class="pre"><code class="sourceCode python">redefining_feature</code></span></a>

- <a href="/python/v0.8.4/syside/ReferenceSubsetting.md" class="reference internal" title="syside.ReferenceSubsetting"><span class="pre"><code class="sourceCode python">syside.ReferenceSubsetting</code></span></a>

  - <a href="/python/v0.8.4/syside/ReferenceSubsetting.md" class="reference internal" title="syside.ReferenceSubsetting.referenced_feature"><span class="pre"><code class="sourceCode python">referenced_feature</code></span></a>

  - <a href="/python/v0.8.4/syside/ReferenceSubsetting.md" class="reference internal" title="syside.ReferenceSubsetting.referencing_feature"><span class="pre"><code class="sourceCode python">referencing_feature</code></span></a>

- <a href="/python/v0.8.4/syside/SatisfactionSubjectAccessor.md" class="reference internal" title="syside.SatisfactionSubjectAccessor"><span class="pre"><code class="sourceCode python">syside.SatisfactionSubjectAccessor</code></span></a>

  - <a href="/python/v0.8.4/syside/SatisfactionSubjectAccessor.md" class="reference internal" title="syside.SatisfactionSubjectAccessor.set_target_chain"><span class="pre"><code class="sourceCode python">set_target_chain</code></span></a>

  - <a href="/python/v0.8.4/syside/SatisfactionSubjectAccessor.md" class="reference internal" title="syside.SatisfactionSubjectAccessor.target"><span class="pre"><code class="sourceCode python">target</code></span></a>

- <a href="/python/v0.8.4/syside/SatisfyRequirementUsage.md" class="reference internal" title="syside.SatisfyRequirementUsage"><span class="pre"><code class="sourceCode python">syside.SatisfyRequirementUsage</code></span></a>

  - <a href="/python/v0.8.4/syside/SatisfyRequirementUsage.md" class="reference internal" title="syside.SatisfyRequirementUsage.satisfying_feature"><span class="pre"><code class="sourceCode python">satisfying_feature</code></span></a>

- <a href="/python/v0.8.4/syside/Stdlib.md" class="reference internal" title="syside.Stdlib"><span class="pre"><code class="sourceCode python">syside.Stdlib</code></span></a>

  - <a href="/python/v0.8.4/syside/Stdlib.md" class="reference internal" title="syside.Stdlib.array_dimensions"><span class="pre"><code class="sourceCode python">array_dimensions</code></span></a>

  - <a href="/python/v0.8.4/syside/Stdlib.md" class="reference internal" title="syside.Stdlib.collection_elements"><span class="pre"><code class="sourceCode python">collection_elements</code></span></a>

  - <a href="/python/v0.8.4/syside/Stdlib.md" class="reference internal" title="syside.Stdlib.measurement_unit_conversion"><span class="pre"><code class="sourceCode python">measurement_unit_conversion</code></span></a>

  - <a href="/python/v0.8.4/syside/Stdlib.md" class="reference internal" title="syside.Stdlib.metadata_annotated_element"><span class="pre"><code class="sourceCode python">metadata_annotated_element</code></span></a>

  - <a href="/python/v0.8.4/syside/Stdlib.md" class="reference internal" title="syside.Stdlib.self_reference"><span class="pre"><code class="sourceCode python">self_reference</code></span></a>

  - <a href="/python/v0.8.4/syside/Stdlib.md" class="reference internal" title="syside.Stdlib.semantic_metadata_base_type"><span class="pre"><code class="sourceCode python">semantic_metadata_base_type</code></span></a>

  - <a href="/python/v0.8.4/syside/Stdlib.md" class="reference internal" title="syside.Stdlib.unit_conversion_factor"><span class="pre"><code class="sourceCode python">unit_conversion_factor</code></span></a>

  - <a href="/python/v0.8.4/syside/Stdlib.md" class="reference internal" title="syside.Stdlib.unit_conversion_reference"><span class="pre"><code class="sourceCode python">unit_conversion_reference</code></span></a>

  - <a href="/python/v0.8.4/syside/Stdlib.md" class="reference internal" title="syside.Stdlib.unit_prefix_factor"><span class="pre"><code class="sourceCode python">unit_prefix_factor</code></span></a>

- <a href="/python/v0.8.4/syside/Step.md" class="reference internal" title="syside.Step"><span class="pre"><code class="sourceCode python">syside.Step</code></span></a>

  - <a href="/python/v0.8.4/syside/Step.md" class="reference internal" title="syside.Step.owned_parameters"><span class="pre"><code class="sourceCode python">owned_parameters</code></span></a>

  - <a href="/python/v0.8.4/syside/Step.md" class="reference internal" title="syside.Step.parameters"><span class="pre"><code class="sourceCode python">parameters</code></span></a>

- <a href="/python/v0.8.4/syside/Subsetting.md" class="reference internal" title="syside.Subsetting"><span class="pre"><code class="sourceCode python">syside.Subsetting</code></span></a>

  - <a href="/python/v0.8.4/syside/Subsetting.md" class="reference internal" title="syside.Subsetting.owning_feature"><span class="pre"><code class="sourceCode python">owning_feature</code></span></a>

  - <a href="/python/v0.8.4/syside/Subsetting.md" class="reference internal" title="syside.Subsetting.subsetted_feature"><span class="pre"><code class="sourceCode python">subsetted_feature</code></span></a>

  - <a href="/python/v0.8.4/syside/Subsetting.md" class="reference internal" title="syside.Subsetting.subsetting_feature"><span class="pre"><code class="sourceCode python">subsetting_feature</code></span></a>

- <a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type"><span class="pre"><code class="sourceCode python">syside.Type</code></span></a>

  - <a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type.directed_features"><span class="pre"><code class="sourceCode python">directed_features</code></span></a>

  - <a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type.direction_of"><span class="pre"><code class="sourceCode python">direction_of</code></span></a>

  - <a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type.end_features"><span class="pre"><code class="sourceCode python">end_features</code></span></a>

  - <a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type.features"><span class="pre"><code class="sourceCode python">features</code></span></a>

  - <a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type.inherited_features"><span class="pre"><code class="sourceCode python">inherited_features</code></span></a>

  - <a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type.inputs"><span class="pre"><code class="sourceCode python">inputs</code></span></a>

  - <a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type.outputs"><span class="pre"><code class="sourceCode python">outputs</code></span></a>

  - <a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type.owned_directed_features"><span class="pre"><code class="sourceCode python">owned_directed_features</code></span></a>

  - <a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type.owned_end_features"><span class="pre"><code class="sourceCode python">owned_end_features</code></span></a>

  - <a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type.owned_features"><span class="pre"><code class="sourceCode python">owned_features</code></span></a>

  - <a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type.owned_inputs"><span class="pre"><code class="sourceCode python">owned_inputs</code></span></a>

  - <a href="/python/v0.8.4/syside/Type.md" class="reference internal" title="syside.Type.owned_outputs"><span class="pre"><code class="sourceCode python">owned_outputs</code></span></a>

- <a href="/python/v0.8.4/syside/TypeFeaturing.md" class="reference internal" title="syside.TypeFeaturing"><span class="pre"><code class="sourceCode python">syside.TypeFeaturing</code></span></a>

  - <a href="/python/v0.8.4/syside/TypeFeaturing.md" class="reference internal" title="syside.TypeFeaturing.feature_of_type"><span class="pre"><code class="sourceCode python">feature_of_type</code></span></a>

  - <a href="/python/v0.8.4/syside/TypeFeaturing.md" class="reference internal" title="syside.TypeFeaturing.owning_feature_of_type"><span class="pre"><code class="sourceCode python">owning_feature_of_type</code></span></a>

- <a href="/python/v0.8.4/syside/TypeRelationships.md" class="reference internal" title="syside.TypeRelationships"><span class="pre"><code class="sourceCode python">syside.TypeRelationships</code></span></a>

  - <a href="/python/v0.8.4/syside/TypeRelationships.md" class="reference internal" title="syside.TypeRelationships.append_chain"><span class="pre"><code class="sourceCode python">append_chain</code></span></a>

  - <a href="/python/v0.8.4/syside/TypeRelationships.md" class="reference internal" title="syside.TypeRelationships.insert_chain"><span class="pre"><code class="sourceCode python">insert_chain</code></span></a>

  - <a href="/python/v0.8.4/syside/TypeRelationships.md" class="reference internal" title="syside.TypeRelationships.replace_chain_at"><span class="pre"><code class="sourceCode python">replace_chain_at</code></span></a>

</div>

</div>
