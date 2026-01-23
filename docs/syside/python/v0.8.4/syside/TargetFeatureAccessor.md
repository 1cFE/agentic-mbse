<div id="targetfeatureaccessor" class="section">

# TargetFeatureAccessor<a href="#targetfeatureaccessor" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">TargetFeatureAccessor</span></span><a href="#syside.TargetFeatureAccessor" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
<div class="align-center" align="center">

<img src="data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iZ3JhcGh2aXoiIHN0eWxlPSJ3aWR0aDogMTAuNzVyZW07aGVpZ2h0OiAxMS43NXJlbTsiIHZpZXdib3g9IjAuMDAgMC4wMCAxNzIuMDAgMTg4LjAwIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPgo8ZyBjbGFzcz0iZ3JhcGgiIGlkPSJncmFwaDAiIHRyYW5zZm9ybT0ic2NhbGUoMSAxKSByb3RhdGUoMCkgdHJhbnNsYXRlKDQgMTg0KSI+Cjx0aXRsZT4lMzwvdGl0bGU+CjxnIGNsYXNzPSJub2RlIiBpZD0ibm9kZTEiPgo8dGl0bGU+VGFyZ2V0RmVhdHVyZUFjY2Vzc29yPC90aXRsZT4KPGcgaWQ9ImFfbm9kZTEiPjxhIGhyZWY9IiNzeXNpZGUuVGFyZ2V0RmVhdHVyZUFjY2Vzc29yIj4KPHBvbHlnb24gcG9pbnRzPSIxNTguNSwtMzYgNS41LC0zNiA1LjUsMCAxNTguNSwwIDE1OC41LC0zNiIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtYmctY29sb3IpO3N0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1mZy1jb2xvcik7Ij48L3BvbHlnb24+Cjx0ZXh0IGZvbnQtZmFtaWx5PSJMZXhlbmQiIGZvbnQtc2l6ZT0iMTIuMDAiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1jb2RlLWZnLWNvbG9yKTstLW1kLWdyYXBodml6LWhvdmVyLWNvbG9yOiB2YXIoLS1tZC1ncmFwaHZpei1hLWhvdmVyLWNvbG9yKTsiIHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjgyIiB5PSItMTQuMiI+VGFyZ2V0RmVhdHVyZUFjY2Vzc29yPC90ZXh0Pgo8dGl0bGU+c3lzaWRlLlRhcmdldEZlYXR1cmVBY2Nlc3NvcjwvdGl0bGU+PC9hPgo8L2c+CjwvZz4KPGcgY2xhc3M9Im5vZGUiIGlkPSJub2RlMiI+Cjx0aXRsZT5DaGFpbmVkTWVtYmVyQWNjZXNzb3I8L3RpdGxlPgo8ZyBpZD0iYV9ub2RlMiI+PGEgaHJlZj0iL3B5dGhvbi92MC44LjQvc3lzaWRlL0NoYWluZWRNZW1iZXJBY2Nlc3Nvci5tZCI+Cjxwb2x5Z29uIHBvaW50cz0iMTY0LC0xMDggMCwtMTA4IDAsLTcyIDE2NCwtNzIgMTY0LC0xMDgiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1ncmFwaHZpei1ub2RlLWJnLWNvbG9yKTtzdHJva2U6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtZmctY29sb3IpOyI+PC9wb2x5Z29uPgo8dGV4dCBmb250LWZhbWlseT0iTGV4ZW5kIiBmb250LXNpemU9IjEyLjAwIiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtY29kZS1mZy1jb2xvcik7LS1tZC1ncmFwaHZpei1ob3Zlci1jb2xvcjogdmFyKC0tbWQtZ3JhcGh2aXotYS1ob3Zlci1jb2xvcik7IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSI4MiIgeT0iLTg2LjIiPkNoYWluZWRNZW1iZXJBY2Nlc3NvcjwvdGV4dD4KPHRpdGxlPnN5c2lkZS5DaGFpbmVkTWVtYmVyQWNjZXNzb3I8L3RpdGxlPjwvYT4KPC9nPgo8L2c+CjxnIGNsYXNzPSJlZGdlIiBpZD0iZWRnZTEiPgo8dGl0bGU+Q2hhaW5lZE1lbWJlckFjY2Vzc29yLSZndDtUYXJnZXRGZWF0dXJlQWNjZXNzb3I8L3RpdGxlPgo8cGF0aCBkPSJNODIsLTcxLjdDODIsLTYzLjk4IDgyLC01NC43MSA4MiwtNDYuMTEiIGZpbGw9Im5vbmUiIHN0eWxlPSJzdHJva2U6IHZhcigtLW1kLWdyYXBodml6LWVkZ2UtY29sb3IpOyIgLz4KPHBvbHlnb24gcG9pbnRzPSI4NS41LC00Ni4xIDgyLC0zNi4xIDc4LjUsLTQ2LjEgODUuNSwtNDYuMSIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWdyYXBodml6LWVkZ2UtY29sb3IpO3N0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotZWRnZS1jb2xvcik7Ij48L3BvbHlnb24+CjwvZz4KPGcgY2xhc3M9Im5vZGUiIGlkPSJub2RlMyI+Cjx0aXRsZT5NZW1iZXJBY2Nlc3NvcjwvdGl0bGU+CjxnIGlkPSJhX25vZGUzIj48YSBocmVmPSIvcHl0aG9uL3YwLjguNC9zeXNpZGUvTWVtYmVyQWNjZXNzb3IubWQiPgo8cG9seWdvbiBwb2ludHM9IjEzOS41LC0xODAgMjQuNSwtMTgwIDI0LjUsLTE0NCAxMzkuNSwtMTQ0IDEzOS41LC0xODAiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1ncmFwaHZpei1ub2RlLWJnLWNvbG9yKTtzdHJva2U6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtZmctY29sb3IpOyI+PC9wb2x5Z29uPgo8dGV4dCBmb250LWZhbWlseT0iTGV4ZW5kIiBmb250LXNpemU9IjEyLjAwIiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtY29kZS1mZy1jb2xvcik7LS1tZC1ncmFwaHZpei1ob3Zlci1jb2xvcjogdmFyKC0tbWQtZ3JhcGh2aXotYS1ob3Zlci1jb2xvcik7IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSI4MiIgeT0iLTE1OC4yIj5NZW1iZXJBY2Nlc3NvcjwvdGV4dD4KPHRpdGxlPnN5c2lkZS5NZW1iZXJBY2Nlc3NvcjwvdGl0bGU+PC9hPgo8L2c+CjwvZz4KPGcgY2xhc3M9ImVkZ2UiIGlkPSJlZGdlMiI+Cjx0aXRsZT5NZW1iZXJBY2Nlc3Nvci0mZ3Q7Q2hhaW5lZE1lbWJlckFjY2Vzc29yPC90aXRsZT4KPHBhdGggZD0iTTgyLC0xNDMuN0M4MiwtMTM1Ljk4IDgyLC0xMjYuNzEgODIsLTExOC4xMSIgZmlsbD0ibm9uZSIgc3R5bGU9InN0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotZWRnZS1jb2xvcik7IiAvPgo8cG9seWdvbiBwb2ludHM9Ijg1LjUsLTExOC4xIDgyLC0xMDguMSA3OC41LC0xMTguMSA4NS41LC0xMTguMSIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWdyYXBodml6LWVkZ2UtY29sb3IpO3N0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotZWRnZS1jb2xvcik7Ij48L3BvbHlnb24+CjwvZz4KPC9nPgo8L3N2Zz4=" class="graphviz" />

</div>

<span class="sd-summary-text">Members defined in <a href="#syside.TargetFeatureAccessor" class="reference internal" title="syside.TargetFeatureAccessor"><span class="pre"><code class="sourceCode python">TargetFeatureAccessor</code></span></a> (1 member)</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |  |
|----|----|----|----|
| <span class="nerd-font"></span> | <a href="#syside.TargetFeatureAccessor.set_member_element" class="reference internal" title="syside.TargetFeatureAccessor.set_member_element"><span class="pre"><code class="sourceCode python">set_member_element</code></span></a> |  | Set a new <span class="pre">`member_element`</span>. <span class="pre">`element`</span> will only be referenced if the <span class="pre">`membership`</span> is <span class="pre">`Membership`</span>, otherwise ownership constraints apply. Replaces the previous <span class="pre">`member_element`</span>, which may be reused by the model if it was owned. |

</div>

</div>

<span class="sd-summary-text">Members inherited from <a href="/python/v0.8.4/syside/ChainedMemberAccessor.md" class="reference internal" title="syside.ChainedMemberAccessor"><span class="pre"><code class="sourceCode python">ChainedMemberAccessor</code></span></a> (1 member)</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |  |
|----|----|----|----|
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/ChainedMemberAccessor.md" class="reference internal" title="syside.ChainedMemberAccessor.set_member_element_chain"><span class="pre"><code class="sourceCode python">set_member_element_chain</code></span></a> |  | Set the reference to a chain of <span class="pre">`Features`</span>. Replaces the previous <span class="pre">`member_element`</span>. |

</div>

</div>

<span class="sd-summary-text">Members inherited from <a href="/python/v0.8.4/syside/MemberAccessor.md" class="reference internal" title="syside.MemberAccessor"><span class="pre"><code class="sourceCode python">MemberAccessor</code></span></a> (5 members)</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |  |
|----|----|----|----|
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/MemberAccessor.md" class="reference internal" title="syside.MemberAccessor.member_element"><span class="pre"><code class="sourceCode python">member_element</code></span></a> | <span class="pre">`R`</span> | The <span class="pre">`member_element`</span> of this <span class="pre">`member`</span> if it is not empty. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/MemberAccessor.md" class="reference internal" title="syside.MemberAccessor.membership"><span class="pre"><code class="sourceCode python">membership</code></span></a> | <span class="pre">`R`</span> | The <span class="pre">`membership`</span> of this <span class="pre">`member`</span> if it is not empty. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/MemberAccessor.md" class="reference internal" title="syside.MemberAccessor.__bool__"><span class="pre"><code class="sourceCode python"><span class="fu">__bool__</span></code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/MemberAccessor.md" class="reference internal" title="syside.MemberAccessor.extract_member_element"><span class="pre"><code class="sourceCode python">extract_member_element</code></span></a> |  | Extract the <span class="pre">`member_element`</span> leaving this <span class="pre">`member`</span> empty. Note that not all empty <span class="pre">`members`</span> are valid textual syntax. This does not check that the model is left in a valid state. |
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/MemberAccessor.md" class="reference internal" title="syside.MemberAccessor.remove_member_element"><span class="pre"><code class="sourceCode python">remove_member_element</code></span></a> |  | Remove the <span class="pre">`member_element`</span> leaving this <span class="pre">`member`</span> empty. Note that not all empty <span class="pre">`members`</span> are valid textual syntax. This does not check that the model is left in a valid state. |

</div>

</div>

<span class="nerd-font"></span> **Methods**

<span class="sig-name descname"><span class="pre">set_member_element</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">element</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">syside.TargetFeatureAccessor.set_member_element.M</span></span>*, *<span class="n"><span class="pre">name</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside.NameID"><span class="pre">syside.NameID</span></a></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">...</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Membership.md" class="reference internal" title="syside.Membership"><span class="pre">syside.Membership</span></a><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">syside.TargetFeatureAccessor.set_member_element.M</span><span class="p"><span class="pre">\]</span></span></span></span><a href="#syside.TargetFeatureAccessor.set_member_element" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Set a new <span class="pre">`member_element`</span>. <span class="pre">`element`</span> will only be referenced if the <span class="pre">`membership`</span> is <span class="pre">`Membership`</span>, otherwise ownership constraints apply. Replaces the previous <span class="pre">`member_element`</span>, which may be reused by the model if it was owned.

Returns a pair of (<span class="pre">`membership`</span>, <span class="pre">`member_element`</span>) where <span class="pre">`member_element`</span> is <span class="pre">`element`</span>.

<span class="sig-name descname"><span class="pre">set_member_element</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">element</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">syside.TargetFeatureAccessor.set_member_element.M</span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span></span>*, *<span class="n"><span class="pre">name</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside.NameID"><span class="pre">syside.NameID</span></a></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">...</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Membership.md" class="reference internal" title="syside.Membership"><span class="pre">syside.Membership</span></a><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">syside.TargetFeatureAccessor.set_member_element.M</span><span class="p"><span class="pre">\]</span></span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span></span></span>  
<span class="pre">`set_member_element`</span> overload that will remove the member element if <span class="pre">`element`</span> is <span class="pre">`None`</span>, otherwise the behaviour is the same.

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/FeatureChainExpression.md" class="reference internal" title="syside.FeatureChainExpression"><span class="pre"><code class="sourceCode python">syside.FeatureChainExpression</code></span></a>

  - <a href="/python/v0.8.4/syside/FeatureChainExpression.md" class="reference internal" title="syside.FeatureChainExpression.target_feature_member"><span class="pre"><code class="sourceCode python">target_feature_member</code></span></a>

</div>

</div>
