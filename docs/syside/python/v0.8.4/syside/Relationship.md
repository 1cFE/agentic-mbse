<div id="relationship-sysml" class="section">

# Relationship <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span><a href="#relationship-sysml" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">Relationship</span></span><a href="#syside.Relationship" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`Relationship`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> A <span class="pre">`Relationship`</span> is an <span class="pre">`Element`</span> that relates other <span class="pre">`Element`</span>. Some of its <span class="pre">`related_elements`</span> may be owned, in which case those <span class="pre">`owned_related_elements`</span> will be deleted from a model if their <span class="pre">`owning_relationship`</span> is. A <span class="pre">`Relationship`</span> may also be owned by another <span class="pre">`Element`</span>, in which case the <span class="pre">`owned_related_elements`</span> of the <span class="pre">`Relationship`</span> are also considered to be transitively owned by the <span class="pre">`owning_related_element`</span> of the <span class="pre">`Relationship`</span>.
>
> The <span class="pre">`related_elements`</span> of a <span class="pre">`Relationship`</span> are divided into <span class="pre">`source`</span> and <span class="pre">`target`</span> <span class="pre">`Elements`</span>. The <span class="pre">`Relationship`</span> is considered to be directed from the <span class="pre">`source`</span> to the <span class="pre">`target`</span> <span class="pre">`Elements`</span>. An undirected <span class="pre">`Relationship`</span> may have either all <span class="pre">`source`</span> or all <span class="pre">`target`</span> <span class="pre">`Elements`</span>.
>
> A “relationship <span class="pre">`Element`</span>” in the abstract syntax is generically any <span class="pre">`Element`</span> that is an instance of either <span class="pre">`Relationship`</span> or a direct or indirect specialization of <span class="pre">`Relationship`</span>. Any other kind of <span class="pre">`Element`</span> is a “non-relationship <span class="pre">`Element`</span>”. It is a convention of that non-relationship <span class="pre">`Elements`</span> are *only* related via reified relationship <span class="pre">`Elements`</span>. Any meta-associations directly between non-relationship <span class="pre">`Elements`</span> must be derived from underlying reified <span class="pre">`Relationship`</span>.
>
> </div>

For language description, see section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=41" class="reference external" target="_blank">7.2.2</a> of the KerML specification. For more details on the model, see section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=143" class="reference external" target="_blank">8.3.2.1.3</a> of the KerML specification.

<div class="align-center" align="center">

<img src="data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iZ3JhcGh2aXoiIHN0eWxlPSJ3aWR0aDogNS45Mzc1cmVtO2hlaWdodDogMTEuNzVyZW07IiB2aWV3Ym94PSIwLjAwIDAuMDAgOTUuMDAgMTg4LjAwIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPgo8ZyBjbGFzcz0iZ3JhcGgiIGlkPSJncmFwaDAiIHRyYW5zZm9ybT0ic2NhbGUoMSAxKSByb3RhdGUoMCkgdHJhbnNsYXRlKDQgMTg0KSI+Cjx0aXRsZT4lMzwvdGl0bGU+CjxnIGNsYXNzPSJub2RlIiBpZD0ibm9kZTEiPgo8dGl0bGU+UmVsYXRpb25zaGlwPC90aXRsZT4KPGcgaWQ9ImFfbm9kZTEiPjxhIGhyZWY9IiNzeXNpZGUuUmVsYXRpb25zaGlwIj4KPHBvbHlnb24gcG9pbnRzPSI4NywtMzYgMCwtMzYgMCwwIDg3LDAgODcsLTM2IiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1iZy1jb2xvcik7c3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1ub2RlLWZnLWNvbG9yKTsiPjwvcG9seWdvbj4KPHRleHQgZm9udC1mYW1pbHk9IkxleGVuZCIgZm9udC1zaXplPSIxMi4wMCIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWNvZGUtZmctY29sb3IpOy0tbWQtZ3JhcGh2aXotaG92ZXItY29sb3I6IHZhcigtLW1kLWdyYXBodml6LWEtaG92ZXItY29sb3IpOyIgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iNDMuNSIgeT0iLTE0LjIiPlJlbGF0aW9uc2hpcDwvdGV4dD4KPHRpdGxlPnN5c2lkZS5SZWxhdGlvbnNoaXA8L3RpdGxlPjwvYT4KPC9nPgo8L2c+CjxnIGNsYXNzPSJub2RlIiBpZD0ibm9kZTIiPgo8dGl0bGU+RWxlbWVudDwvdGl0bGU+CjxnIGlkPSJhX25vZGUyIj48YSBocmVmPSIvcHl0aG9uL3YwLjguNC9zeXNpZGUvRWxlbWVudC5tZCI+Cjxwb2x5Z29uIHBvaW50cz0iNzQuNSwtMTA4IDEyLjUsLTEwOCAxMi41LC03MiA3NC41LC03MiA3NC41LC0xMDgiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1ncmFwaHZpei1ub2RlLWJnLWNvbG9yKTtzdHJva2U6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtZmctY29sb3IpOyI+PC9wb2x5Z29uPgo8dGV4dCBmb250LWZhbWlseT0iTGV4ZW5kIiBmb250LXNpemU9IjEyLjAwIiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtY29kZS1mZy1jb2xvcik7LS1tZC1ncmFwaHZpei1ob3Zlci1jb2xvcjogdmFyKC0tbWQtZ3JhcGh2aXotYS1ob3Zlci1jb2xvcik7IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSI0My41IiB5PSItODYuMiI+RWxlbWVudDwvdGV4dD4KPHRpdGxlPnN5c2lkZS5FbGVtZW50PC90aXRsZT48L2E+CjwvZz4KPC9nPgo8ZyBjbGFzcz0iZWRnZSIgaWQ9ImVkZ2UxIj4KPHRpdGxlPkVsZW1lbnQtJmd0O1JlbGF0aW9uc2hpcDwvdGl0bGU+CjxwYXRoIGQ9Ik00My41LC03MS43QzQzLjUsLTYzLjk4IDQzLjUsLTU0LjcxIDQzLjUsLTQ2LjExIiBmaWxsPSJub25lIiBzdHlsZT0ic3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1lZGdlLWNvbG9yKTsiIC8+Cjxwb2x5Z29uIHBvaW50cz0iNDcsLTQ2LjEgNDMuNSwtMzYuMSA0MCwtNDYuMSA0NywtNDYuMSIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWdyYXBodml6LWVkZ2UtY29sb3IpO3N0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotZWRnZS1jb2xvcik7Ij48L3BvbHlnb24+CjwvZz4KPGcgY2xhc3M9Im5vZGUiIGlkPSJub2RlMyI+Cjx0aXRsZT5Bc3ROb2RlPC90aXRsZT4KPGcgaWQ9ImFfbm9kZTMiPjxhIGhyZWY9Ii9weXRob24vdjAuOC40L3N5c2lkZS9Bc3ROb2RlLm1kIj4KPHBvbHlnb24gcG9pbnRzPSI3Ni41LC0xODAgMTAuNSwtMTgwIDEwLjUsLTE0NCA3Ni41LC0xNDQgNzYuNSwtMTgwIiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1iZy1jb2xvcik7c3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1ub2RlLWZnLWNvbG9yKTsiPjwvcG9seWdvbj4KPHRleHQgZm9udC1mYW1pbHk9IkxleGVuZCIgZm9udC1zaXplPSIxMi4wMCIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWNvZGUtZmctY29sb3IpOy0tbWQtZ3JhcGh2aXotaG92ZXItY29sb3I6IHZhcigtLW1kLWdyYXBodml6LWEtaG92ZXItY29sb3IpOyIgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iNDMuNSIgeT0iLTE1OC4yIj5Bc3ROb2RlPC90ZXh0Pgo8dGl0bGU+c3lzaWRlLkFzdE5vZGU8L3RpdGxlPjwvYT4KPC9nPgo8L2c+CjxnIGNsYXNzPSJlZGdlIiBpZD0iZWRnZTIiPgo8dGl0bGU+QXN0Tm9kZS0mZ3Q7RWxlbWVudDwvdGl0bGU+CjxwYXRoIGQ9Ik00My41LC0xNDMuN0M0My41LC0xMzUuOTggNDMuNSwtMTI2LjcxIDQzLjUsLTExOC4xMSIgZmlsbD0ibm9uZSIgc3R5bGU9InN0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotZWRnZS1jb2xvcik7IiAvPgo8cG9seWdvbiBwb2ludHM9IjQ3LC0xMTguMSA0My41LC0xMDguMSA0MCwtMTE4LjEgNDcsLTExOC4xIiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtZ3JhcGh2aXotZWRnZS1jb2xvcik7c3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1lZGdlLWNvbG9yKTsiPjwvcG9seWdvbj4KPC9nPgo8L2c+Cjwvc3ZnPg==" class="graphviz" />

</div>

<span class="sd-summary-text"><span class="nerd-font"></span> Children</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

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

<span class="sd-summary-text">Members defined in <a href="#syside.Relationship" class="reference internal" title="syside.Relationship"><span class="pre"><code class="sourceCode python">Relationship</code></span></a> (13 members)</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |  |
|----|----|----|----|
| <span class="nerd-font"></span> | <a href="#syside.Relationship.STD" class="reference internal" title="syside.Relationship.STD"><span class="pre"><code class="sourceCode python">STD</code></span></a> | <span class="pre">`R`</span> |  |
| <span class="nerd-font"></span> | <a href="#syside.Relationship.first_source" class="reference internal" title="syside.Relationship.first_source"><span class="pre"><code class="sourceCode python">first_source</code></span></a> | <span class="pre">`R`</span> | Convenience method for sources\[0\]. |
| <span class="nerd-font"></span> | <a href="#syside.Relationship.first_target" class="reference internal" title="syside.Relationship.first_target"><span class="pre"><code class="sourceCode python">first_target</code></span></a> | <span class="pre">`R`</span> | Convenience method for targets\[0\]. |
| <span class="nerd-font"></span> | <a href="#syside.Relationship.is_implied" class="reference internal" title="syside.Relationship.is_implied"><span class="pre"><code class="sourceCode python">is_implied</code></span></a> | <span class="pre">`RW`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`is_implied`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Relationship.is_visibility_implied" class="reference internal" title="syside.Relationship.is_visibility_implied"><span class="pre"><code class="sourceCode python">is_visibility_implied</code></span></a> | <span class="pre">`R`</span> | Returns <span class="pre">`True`</span> if this <span class="pre">`Relationship`</span> is using implicit visibility. |
| <span class="nerd-font"></span> | <a href="#syside.Relationship.owned_related_elements" class="reference internal" title="syside.Relationship.owned_related_elements"><span class="pre"><code class="sourceCode python">owned_related_elements</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owned_related_element`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Relationship.owning_related_element" class="reference internal" title="syside.Relationship.owning_related_element"><span class="pre"><code class="sourceCode python">owning_related_element</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`owning_related_element`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Relationship.related_elements" class="reference internal" title="syside.Relationship.related_elements"><span class="pre"><code class="sourceCode python">related_elements</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`related_element`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Relationship.sources" class="reference internal" title="syside.Relationship.sources"><span class="pre"><code class="sourceCode python">sources</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`source`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Relationship.targets" class="reference internal" title="syside.Relationship.targets"><span class="pre"><code class="sourceCode python">targets</code></span></a> | <span class="pre">`R`</span> <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">SysML</span> | Implementation of <span class="pre">`target`</span> defined in the KerML specification. |
| <span class="nerd-font"></span> | <a href="#syside.Relationship.visibility" class="reference internal" title="syside.Relationship.visibility"><span class="pre"><code class="sourceCode python">visibility</code></span></a> | <span class="pre">`RW`</span> | The visibility level of the related elements from this <span class="pre">`Relationship`</span> relative to the <span class="pre">`owning_related_element`</span>. |
| <span class="nerd-font"></span> | <a href="#syside.Relationship.reset_visibility" class="reference internal" title="syside.Relationship.reset_visibility"><span class="pre"><code class="sourceCode python">reset_visibility</code></span></a> |  | Reset visibility to its implicit value. |
| <span class="nerd-font"></span> | <a href="#syside.Relationship.try_set_visibility" class="reference internal" title="syside.Relationship.try_set_visibility"><span class="pre"><code class="sourceCode python">try_set_visibility</code></span></a> |  | Non-throwing alternative to <span class="pre">`visibility`</span> setter. |

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

<span class="sig-name descname"><span class="pre">STD</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><span class="pre">Union</span><span class="p"><span class="pre">\[</span></span><span class="pre">type</span><span class="p"><span class="pre">\[</span></span><a href="#syside.Relationship" class="reference internal" title="syside.Relationship"><span class="pre">syside.Relationship</span></a><span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">type</span><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Association.md" class="reference internal" title="syside.Association"><span class="pre">syside.Association</span></a><span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">type</span><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/ConnectionDefinition.md" class="reference internal" title="syside.ConnectionDefinition"><span class="pre">syside.ConnectionDefinition</span></a><span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">type</span><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Connector.md" class="reference internal" title="syside.Connector"><span class="pre">syside.Connector</span></a><span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">type</span><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/ConnectorAsUsage.md" class="reference internal" title="syside.ConnectorAsUsage"><span class="pre">syside.ConnectorAsUsage</span></a><span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">type</span><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/FlowDefinition.md" class="reference internal" title="syside.FlowDefinition"><span class="pre">syside.FlowDefinition</span></a><span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="p"><span class="pre">...</span></span><span class="p"><span class="pre">\]</span></span><span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">()</span>*<a href="#syside.Relationship.STD" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">first_source</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element"><span class="pre">syside.Element</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span>*<a href="#syside.Relationship.first_source" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Convenience method for sources\[0\].

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">first_target</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element"><span class="pre">syside.Element</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span>*<a href="#syside.Relationship.first_target" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Convenience method for targets\[0\].

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">is_implied</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*<a href="#syside.Relationship.is_implied" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`is_implied`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> Whether this Relationship was generated by tooling to meet semantic rules, rather than being directly created by a modeler.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=143" class="reference external" target="_blank">8.3.2.1.3</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">is_visibility_implied</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*<a href="#syside.Relationship.is_visibility_implied" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Returns <span class="pre">`True`</span> if this <span class="pre">`Relationship`</span> is using implicit visibility.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owned_related_elements</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element"><span class="pre">syside.Element</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Relationship.owned_related_elements" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owned_related_element`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The related_elements of this Relationship that are owned by the Relationship.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=143" class="reference external" target="_blank">8.3.2.1.3</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">owning_related_element</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element"><span class="pre">syside.Element</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span>*<a href="#syside.Relationship.owning_related_element" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`owning_related_element`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The related_element of this Relationship that owns the Relationship, if any.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=143" class="reference external" target="_blank">8.3.2.1.3</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">related_elements</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/LazyIterator.md" class="reference internal" title="syside.LazyIterator"><span class="pre">syside.LazyIterator</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element"><span class="pre">syside.Element</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Relationship.related_elements" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`related_element`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The Elements that are related by this Relationship, derived as the union of the <span class="pre">`source`</span> and <span class="pre">`target`</span> Elements of the Relationship.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=143" class="reference external" target="_blank">8.3.2.1.3</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">sources</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/ContainerView.md" class="reference internal" title="syside.ContainerView"><span class="pre">syside.ContainerView</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element"><span class="pre">syside.Element</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Relationship.sources" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`source`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The <span class="pre">`related_elements`</span>` `<span class="pre">`from`</span>` `<span class="pre">`which`</span>` `<span class="pre">`this`</span>` `<span class="pre">`Relationship`</span>` `<span class="pre">`is`</span>` `<span class="pre">`considered`</span>` `<span class="pre">`to`</span>` `<span class="pre">`be`</span>` `<span class="pre">`directed.`</span>
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=143" class="reference external" target="_blank">8.3.2.1.3</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">targets</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/ContainerView.md" class="reference internal" title="syside.ContainerView"><span class="pre">syside.ContainerView</span></a><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element"><span class="pre">syside.Element</span></a><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Relationship.targets" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Implementation of <span class="pre">`target`</span> defined in the KerML specification.

**Specification**:

> <div>
>
> The <span class="pre">`related_elements`</span> to which this Relationship is considered to be directed.
>
> </div>

See section <a href="https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/tags/2025-07/doc/1-Kernel_Modeling_Language.pdf#page=143" class="reference external" target="_blank">8.3.2.1.3</a> of the KerML specification for more details.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">visibility</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside.VisibilityKind"><span class="pre">syside.VisibilityKind</span></a>*<a href="#syside.Relationship.visibility" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
The visibility level of the related elements from this <span class="pre">`Relationship`</span> relative to the <span class="pre">`owning_related_element`</span>.

Raises <span class="pre">`TypeError`</span> if visibility is immutable, e.g. on <span class="pre">`Expose`</span> elements.

<span class="nerd-font"></span> **Methods**

<span class="sig-name descname"><span class="pre">reset_visibility</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span><a href="#syside.Relationship.reset_visibility" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Reset visibility to its implicit value.

<span class="sig-name descname"><span class="pre">try_set_visibility</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside.VisibilityKind"><span class="pre">syside.VisibilityKind</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">bool</span></span></span><a href="#syside.Relationship.try_set_visibility" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Non-throwing alternative to <span class="pre">`visibility`</span> setter.

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element"><span class="pre"><code class="sourceCode python">syside.Element</code></span></a>

  - <a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element.owned_relationships"><span class="pre"><code class="sourceCode python">owned_relationships</code></span></a>

  - <a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element.owning_relationship"><span class="pre"><code class="sourceCode python">owning_relationship</code></span></a>

- <a href="#syside.Relationship" class="reference internal" title="syside.Relationship"><span class="pre"><code class="sourceCode python">syside.Relationship</code></span></a>

  - <a href="#syside.Relationship.STD" class="reference internal" title="syside.Relationship.STD"><span class="pre"><code class="sourceCode python">STD</code></span></a>

</div>

</div>
