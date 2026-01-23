<div id="chainedfeaturememberaccessor" class="section">

# ChainedFeatureMemberAccessor<a href="#chainedfeaturememberaccessor" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">ChainedFeatureMemberAccessor</span></span><a href="#syside.ChainedFeatureMemberAccessor" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
<div class="align-center" align="center">

<img src="data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iZ3JhcGh2aXoiIHN0eWxlPSJ3aWR0aDogMTMuNjI1cmVtO2hlaWdodDogMTEuNzVyZW07IiB2aWV3Ym94PSIwLjAwIDAuMDAgMjE4LjAwIDE4OC4wMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGcgY2xhc3M9ImdyYXBoIiBpZD0iZ3JhcGgwIiB0cmFuc2Zvcm09InNjYWxlKDEgMSkgcm90YXRlKDApIHRyYW5zbGF0ZSg0IDE4NCkiPgo8dGl0bGU+JTM8L3RpdGxlPgo8ZyBjbGFzcz0ibm9kZSIgaWQ9Im5vZGUxIj4KPHRpdGxlPkNoYWluZWRGZWF0dXJlTWVtYmVyQWNjZXNzb3I8L3RpdGxlPgo8ZyBpZD0iYV9ub2RlMSI+PGEgaHJlZj0iI3N5c2lkZS5DaGFpbmVkRmVhdHVyZU1lbWJlckFjY2Vzc29yIj4KPHBvbHlnb24gcG9pbnRzPSIyMTAsLTM2IDAsLTM2IDAsMCAyMTAsMCAyMTAsLTM2IiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1iZy1jb2xvcik7c3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1ub2RlLWZnLWNvbG9yKTsiPjwvcG9seWdvbj4KPHRleHQgZm9udC1mYW1pbHk9IkxleGVuZCIgZm9udC1zaXplPSIxMi4wMCIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWNvZGUtZmctY29sb3IpOy0tbWQtZ3JhcGh2aXotaG92ZXItY29sb3I6IHZhcigtLW1kLWdyYXBodml6LWEtaG92ZXItY29sb3IpOyIgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iMTA1IiB5PSItMTQuMiI+Q2hhaW5lZEZlYXR1cmVNZW1iZXJBY2Nlc3NvcjwvdGV4dD4KPHRpdGxlPnN5c2lkZS5DaGFpbmVkRmVhdHVyZU1lbWJlckFjY2Vzc29yPC90aXRsZT48L2E+CjwvZz4KPC9nPgo8ZyBjbGFzcz0ibm9kZSIgaWQ9Im5vZGUyIj4KPHRpdGxlPkNoYWluZWRNZW1iZXJBY2Nlc3NvcjwvdGl0bGU+CjxnIGlkPSJhX25vZGUyIj48YSBocmVmPSIvcHl0aG9uL3YwLjguNC9zeXNpZGUvQ2hhaW5lZE1lbWJlckFjY2Vzc29yLm1kIj4KPHBvbHlnb24gcG9pbnRzPSIxODcsLTEwOCAyMywtMTA4IDIzLC03MiAxODcsLTcyIDE4NywtMTA4IiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1iZy1jb2xvcik7c3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1ub2RlLWZnLWNvbG9yKTsiPjwvcG9seWdvbj4KPHRleHQgZm9udC1mYW1pbHk9IkxleGVuZCIgZm9udC1zaXplPSIxMi4wMCIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWNvZGUtZmctY29sb3IpOy0tbWQtZ3JhcGh2aXotaG92ZXItY29sb3I6IHZhcigtLW1kLWdyYXBodml6LWEtaG92ZXItY29sb3IpOyIgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iMTA1IiB5PSItODYuMiI+Q2hhaW5lZE1lbWJlckFjY2Vzc29yPC90ZXh0Pgo8dGl0bGU+c3lzaWRlLkNoYWluZWRNZW1iZXJBY2Nlc3NvcjwvdGl0bGU+PC9hPgo8L2c+CjwvZz4KPGcgY2xhc3M9ImVkZ2UiIGlkPSJlZGdlMSI+Cjx0aXRsZT5DaGFpbmVkTWVtYmVyQWNjZXNzb3ItJmd0O0NoYWluZWRGZWF0dXJlTWVtYmVyQWNjZXNzb3I8L3RpdGxlPgo8cGF0aCBkPSJNMTA1LC03MS43QzEwNSwtNjMuOTggMTA1LC01NC43MSAxMDUsLTQ2LjExIiBmaWxsPSJub25lIiBzdHlsZT0ic3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1lZGdlLWNvbG9yKTsiIC8+Cjxwb2x5Z29uIHBvaW50cz0iMTA4LjUsLTQ2LjEgMTA1LC0zNi4xIDEwMS41LC00Ni4xIDEwOC41LC00Ni4xIiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtZ3JhcGh2aXotZWRnZS1jb2xvcik7c3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1lZGdlLWNvbG9yKTsiPjwvcG9seWdvbj4KPC9nPgo8ZyBjbGFzcz0ibm9kZSIgaWQ9Im5vZGUzIj4KPHRpdGxlPk1lbWJlckFjY2Vzc29yPC90aXRsZT4KPGcgaWQ9ImFfbm9kZTMiPjxhIGhyZWY9Ii9weXRob24vdjAuOC40L3N5c2lkZS9NZW1iZXJBY2Nlc3Nvci5tZCI+Cjxwb2x5Z29uIHBvaW50cz0iMTYyLjUsLTE4MCA0Ny41LC0xODAgNDcuNSwtMTQ0IDE2Mi41LC0xNDQgMTYyLjUsLTE4MCIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtYmctY29sb3IpO3N0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1mZy1jb2xvcik7Ij48L3BvbHlnb24+Cjx0ZXh0IGZvbnQtZmFtaWx5PSJMZXhlbmQiIGZvbnQtc2l6ZT0iMTIuMDAiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1jb2RlLWZnLWNvbG9yKTstLW1kLWdyYXBodml6LWhvdmVyLWNvbG9yOiB2YXIoLS1tZC1ncmFwaHZpei1hLWhvdmVyLWNvbG9yKTsiIHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjEwNSIgeT0iLTE1OC4yIj5NZW1iZXJBY2Nlc3NvcjwvdGV4dD4KPHRpdGxlPnN5c2lkZS5NZW1iZXJBY2Nlc3NvcjwvdGl0bGU+PC9hPgo8L2c+CjwvZz4KPGcgY2xhc3M9ImVkZ2UiIGlkPSJlZGdlMiI+Cjx0aXRsZT5NZW1iZXJBY2Nlc3Nvci0mZ3Q7Q2hhaW5lZE1lbWJlckFjY2Vzc29yPC90aXRsZT4KPHBhdGggZD0iTTEwNSwtMTQzLjdDMTA1LC0xMzUuOTggMTA1LC0xMjYuNzEgMTA1LC0xMTguMTEiIGZpbGw9Im5vbmUiIHN0eWxlPSJzdHJva2U6IHZhcigtLW1kLWdyYXBodml6LWVkZ2UtY29sb3IpOyIgLz4KPHBvbHlnb24gcG9pbnRzPSIxMDguNSwtMTE4LjEgMTA1LC0xMDguMSAxMDEuNSwtMTE4LjEgMTA4LjUsLTExOC4xIiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtZ3JhcGh2aXotZWRnZS1jb2xvcik7c3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1lZGdlLWNvbG9yKTsiPjwvcG9seWdvbj4KPC9nPgo8L2c+Cjwvc3ZnPg==" class="graphviz" />

</div>

<span class="sd-summary-text">Members defined in <a href="#syside.ChainedFeatureMemberAccessor" class="reference internal" title="syside.ChainedFeatureMemberAccessor"><span class="pre"><code class="sourceCode python">ChainedFeatureMemberAccessor</code></span></a> (1 member)</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |  |
|----|----|----|----|
| <span class="nerd-font"></span> | <a href="#syside.ChainedFeatureMemberAccessor.set_member_element" class="reference internal" title="syside.ChainedFeatureMemberAccessor.set_member_element"><span class="pre"><code class="sourceCode python">set_member_element</code></span></a> |  | Set a new <span class="pre">`member_element`</span>. <span class="pre">`element`</span> will only be referenced if the <span class="pre">`membership`</span> is <span class="pre">`Membership`</span>, otherwise ownership constraints apply. Replaces the previous <span class="pre">`member_element`</span>, which may be reused by the model if it was owned. |

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

<span class="sig-name descname"><span class="pre">set_member_element</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">element</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">syside.ChainedFeatureMemberAccessor.set_member_element.M</span></span>*, *<span class="n"><span class="pre">name</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside.NameID"><span class="pre">syside.NameID</span></a></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">...</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Membership.md" class="reference internal" title="syside.Membership"><span class="pre">syside.Membership</span></a><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">syside.ChainedFeatureMemberAccessor.set_member_element.M</span><span class="p"><span class="pre">\]</span></span></span></span><a href="#syside.ChainedFeatureMemberAccessor.set_member_element" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Set a new <span class="pre">`member_element`</span>. <span class="pre">`element`</span> will only be referenced if the <span class="pre">`membership`</span> is <span class="pre">`Membership`</span>, otherwise ownership constraints apply. Replaces the previous <span class="pre">`member_element`</span>, which may be reused by the model if it was owned.

Returns a pair of (<span class="pre">`membership`</span>, <span class="pre">`member_element`</span>) where <span class="pre">`member_element`</span> is <span class="pre">`element`</span>.

<span class="sig-name descname"><span class="pre">set_member_element</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">element</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">syside.ChainedFeatureMemberAccessor.set_member_element.M</span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span></span>*, *<span class="n"><span class="pre">name</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside.NameID"><span class="pre">syside.NameID</span></a></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">...</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/Membership.md" class="reference internal" title="syside.Membership"><span class="pre">syside.Membership</span></a><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">syside.ChainedFeatureMemberAccessor.set_member_element.M</span><span class="p"><span class="pre">\]</span></span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span></span></span>  
<span class="pre">`set_member_element`</span> overload that will remove the member element if <span class="pre">`element`</span> is <span class="pre">`None`</span>, otherwise the behaviour is the same.

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/AssignmentActionUsage.md" class="reference internal" title="syside.AssignmentActionUsage"><span class="pre"><code class="sourceCode python">syside.AssignmentActionUsage</code></span></a>

  - <a href="/python/v0.8.4/syside/AssignmentActionUsage.md" class="reference internal" title="syside.AssignmentActionUsage.referent_member"><span class="pre"><code class="sourceCode python">referent_member</code></span></a>

</div>

</div>
