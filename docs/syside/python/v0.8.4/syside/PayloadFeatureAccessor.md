<div id="payloadfeatureaccessor" class="section">

# PayloadFeatureAccessor<a href="#payloadfeatureaccessor" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">PayloadFeatureAccessor</span></span><a href="#syside.PayloadFeatureAccessor" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
<div class="align-center" align="center">

<img src="data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iZ3JhcGh2aXoiIHN0eWxlPSJ3aWR0aDogMTAuNTYyNXJlbTtoZWlnaHQ6IDExLjc1cmVtOyIgdmlld2JveD0iMC4wMCAwLjAwIDE2OS4wMCAxODguMDAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxnIGNsYXNzPSJncmFwaCIgaWQ9ImdyYXBoMCIgdHJhbnNmb3JtPSJzY2FsZSgxIDEpIHJvdGF0ZSgwKSB0cmFuc2xhdGUoNCAxODQpIj4KPHRpdGxlPiUzPC90aXRsZT4KPGcgY2xhc3M9Im5vZGUiIGlkPSJub2RlMSI+Cjx0aXRsZT5QYXlsb2FkRmVhdHVyZUFjY2Vzc29yPC90aXRsZT4KPGcgaWQ9ImFfbm9kZTEiPjxhIGhyZWY9IiNzeXNpZGUuUGF5bG9hZEZlYXR1cmVBY2Nlc3NvciI+Cjxwb2x5Z29uIHBvaW50cz0iMTYxLC0zNiAwLC0zNiAwLDAgMTYxLDAgMTYxLC0zNiIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtYmctY29sb3IpO3N0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1mZy1jb2xvcik7Ij48L3BvbHlnb24+Cjx0ZXh0IGZvbnQtZmFtaWx5PSJMZXhlbmQiIGZvbnQtc2l6ZT0iMTIuMDAiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1jb2RlLWZnLWNvbG9yKTstLW1kLWdyYXBodml6LWhvdmVyLWNvbG9yOiB2YXIoLS1tZC1ncmFwaHZpei1hLWhvdmVyLWNvbG9yKTsiIHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjgwLjUiIHk9Ii0xNC4yIj5QYXlsb2FkRmVhdHVyZUFjY2Vzc29yPC90ZXh0Pgo8dGl0bGU+c3lzaWRlLlBheWxvYWRGZWF0dXJlQWNjZXNzb3I8L3RpdGxlPjwvYT4KPC9nPgo8L2c+CjxnIGNsYXNzPSJub2RlIiBpZD0ibm9kZTIiPgo8dGl0bGU+T3duZWRNZW1iZXJBY2Nlc3NvcjwvdGl0bGU+CjxnIGlkPSJhX25vZGUyIj48YSBocmVmPSIvcHl0aG9uL3YwLjguNC9zeXNpZGUvT3duZWRNZW1iZXJBY2Nlc3Nvci5tZCI+Cjxwb2x5Z29uIHBvaW50cz0iMTU5LC0xMDggMiwtMTA4IDIsLTcyIDE1OSwtNzIgMTU5LC0xMDgiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1ncmFwaHZpei1ub2RlLWJnLWNvbG9yKTtzdHJva2U6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtZmctY29sb3IpOyI+PC9wb2x5Z29uPgo8dGV4dCBmb250LWZhbWlseT0iTGV4ZW5kIiBmb250LXNpemU9IjEyLjAwIiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtY29kZS1mZy1jb2xvcik7LS1tZC1ncmFwaHZpei1ob3Zlci1jb2xvcjogdmFyKC0tbWQtZ3JhcGh2aXotYS1ob3Zlci1jb2xvcik7IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSI4MC41IiB5PSItODYuMiI+T3duZWRNZW1iZXJBY2Nlc3NvcjwvdGV4dD4KPHRpdGxlPnN5c2lkZS5Pd25lZE1lbWJlckFjY2Vzc29yPC90aXRsZT48L2E+CjwvZz4KPC9nPgo8ZyBjbGFzcz0iZWRnZSIgaWQ9ImVkZ2UxIj4KPHRpdGxlPk93bmVkTWVtYmVyQWNjZXNzb3ItJmd0O1BheWxvYWRGZWF0dXJlQWNjZXNzb3I8L3RpdGxlPgo8cGF0aCBkPSJNODAuNSwtNzEuN0M4MC41LC02My45OCA4MC41LC01NC43MSA4MC41LC00Ni4xMSIgZmlsbD0ibm9uZSIgc3R5bGU9InN0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotZWRnZS1jb2xvcik7IiAvPgo8cG9seWdvbiBwb2ludHM9Ijg0LC00Ni4xIDgwLjUsLTM2LjEgNzcsLTQ2LjEgODQsLTQ2LjEiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1ncmFwaHZpei1lZGdlLWNvbG9yKTtzdHJva2U6IHZhcigtLW1kLWdyYXBodml6LWVkZ2UtY29sb3IpOyI+PC9wb2x5Z29uPgo8L2c+CjxnIGNsYXNzPSJub2RlIiBpZD0ibm9kZTMiPgo8dGl0bGU+TWVtYmVyQWNjZXNzb3I8L3RpdGxlPgo8ZyBpZD0iYV9ub2RlMyI+PGEgaHJlZj0iL3B5dGhvbi92MC44LjQvc3lzaWRlL01lbWJlckFjY2Vzc29yLm1kIj4KPHBvbHlnb24gcG9pbnRzPSIxMzgsLTE4MCAyMywtMTgwIDIzLC0xNDQgMTM4LC0xNDQgMTM4LC0xODAiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1ncmFwaHZpei1ub2RlLWJnLWNvbG9yKTtzdHJva2U6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtZmctY29sb3IpOyI+PC9wb2x5Z29uPgo8dGV4dCBmb250LWZhbWlseT0iTGV4ZW5kIiBmb250LXNpemU9IjEyLjAwIiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtY29kZS1mZy1jb2xvcik7LS1tZC1ncmFwaHZpei1ob3Zlci1jb2xvcjogdmFyKC0tbWQtZ3JhcGh2aXotYS1ob3Zlci1jb2xvcik7IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSI4MC41IiB5PSItMTU4LjIiPk1lbWJlckFjY2Vzc29yPC90ZXh0Pgo8dGl0bGU+c3lzaWRlLk1lbWJlckFjY2Vzc29yPC90aXRsZT48L2E+CjwvZz4KPC9nPgo8ZyBjbGFzcz0iZWRnZSIgaWQ9ImVkZ2UyIj4KPHRpdGxlPk1lbWJlckFjY2Vzc29yLSZndDtPd25lZE1lbWJlckFjY2Vzc29yPC90aXRsZT4KPHBhdGggZD0iTTgwLjUsLTE0My43QzgwLjUsLTEzNS45OCA4MC41LC0xMjYuNzEgODAuNSwtMTE4LjExIiBmaWxsPSJub25lIiBzdHlsZT0ic3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1lZGdlLWNvbG9yKTsiIC8+Cjxwb2x5Z29uIHBvaW50cz0iODQsLTExOC4xIDgwLjUsLTEwOC4xIDc3LC0xMTguMSA4NCwtMTE4LjEiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1ncmFwaHZpei1lZGdlLWNvbG9yKTtzdHJva2U6IHZhcigtLW1kLWdyYXBodml6LWVkZ2UtY29sb3IpOyI+PC9wb2x5Z29uPgo8L2c+CjwvZz4KPC9zdmc+" class="graphviz" />

</div>

<span class="sd-summary-text">Members defined in <a href="#syside.PayloadFeatureAccessor" class="reference internal" title="syside.PayloadFeatureAccessor"><span class="pre"><code class="sourceCode python">PayloadFeatureAccessor</code></span></a> (1 member)</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |  |
|----|----|----|----|
| <span class="nerd-font"></span> | <a href="#syside.PayloadFeatureAccessor.set_member_element" class="reference internal" title="syside.PayloadFeatureAccessor.set_member_element"><span class="pre"><code class="sourceCode python">set_member_element</code></span></a> |  | Set a new *owned* <span class="pre">`member_element`</span>, ownership constraints apply. Replaces the previous <span class="pre">`member_element`</span>, which may be reused by the model. <span class="pre">`name_id`</span> has no effect since the <span class="pre">`element`</span> is always taken ownership of. |

</div>

</div>

<span class="sd-summary-text">Members inherited from <a href="/python/v0.8.4/syside/OwnedMemberAccessor.md" class="reference internal" title="syside.OwnedMemberAccessor"><span class="pre"><code class="sourceCode python">OwnedMemberAccessor</code></span></a> (1 member)</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |  |
|----|----|----|----|
| <span class="nerd-font"></span> | <a href="/python/v0.8.4/syside/OwnedMemberAccessor.md" class="reference internal" title="syside.OwnedMemberAccessor.add_member_element"><span class="pre"><code class="sourceCode python">add_member_element</code></span></a> |  | Constructs a new <span class="pre">`member_element`</span> with the default type if this <span class="pre">`member`</span> is empty, otherwise does nothing. |

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

<span class="sig-name descname"><span class="pre">set_member_element</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">element</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">syside.PayloadFeatureAccessor.set_member_element.M</span></span>*, *<span class="n"><span class="pre">name</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside.NameID"><span class="pre">syside.NameID</span></a></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">...</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/FeatureMembership.md" class="reference internal" title="syside.FeatureMembership"><span class="pre">syside.FeatureMembership</span></a><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">syside.PayloadFeatureAccessor.set_member_element.M</span><span class="p"><span class="pre">\]</span></span></span></span><a href="#syside.PayloadFeatureAccessor.set_member_element" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Set a new *owned* <span class="pre">`member_element`</span>, ownership constraints apply. Replaces the previous <span class="pre">`member_element`</span>, which may be reused by the model. <span class="pre">`name_id`</span> has no effect since the <span class="pre">`element`</span> is always taken ownership of.

Returns a pair of (<span class="pre">`membership`</span>, <span class="pre">`member_element`</span>) where <span class="pre">`member_element`</span> is <span class="pre">`element`</span>.

<span class="sig-name descname"><span class="pre">set_member_element</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">element</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">syside.PayloadFeatureAccessor.set_member_element.M</span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span></span>*, *<span class="n"><span class="pre">name</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside.NameID"><span class="pre">syside.NameID</span></a></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">...</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/FeatureMembership.md" class="reference internal" title="syside.FeatureMembership"><span class="pre">syside.FeatureMembership</span></a><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">syside.PayloadFeatureAccessor.set_member_element.M</span><span class="p"><span class="pre">\]</span></span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span></span></span>  
<span class="pre">`set_member_element`</span> overload that will remove the member element if <span class="pre">`element`</span> is <span class="pre">`None`</span>, otherwise the behaviour is the same.

<span class="sig-name descname"><span class="pre">set_member_element</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">element</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">type</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.PayloadFeatureAccessor.set_member_element.M</span><span class="p"><span class="pre">\]</span></span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/FeatureMembership.md" class="reference internal" title="syside.FeatureMembership"><span class="pre">syside.FeatureMembership</span></a><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">syside.PayloadFeatureAccessor.set_member_element.M</span><span class="p"><span class="pre">\]</span></span></span></span>  
Constructs a new empty <span class="pre">`member_element`</span> with the provided type. Replaces the previous <span class="pre">`member_element`</span>. Because a new element is always constructed, ownership constraints do not apply.

Returns a pair of (<span class="pre">`membership`</span>, <span class="pre">`member_element`</span>).

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/Flow.md" class="reference internal" title="syside.Flow"><span class="pre"><code class="sourceCode python">syside.Flow</code></span></a>

  - <a href="/python/v0.8.4/syside/Flow.md" class="reference internal" title="syside.Flow.payload_feature_member"><span class="pre"><code class="sourceCode python">payload_feature_member</code></span></a>

- <a href="/python/v0.8.4/syside/FlowUsage.md" class="reference internal" title="syside.FlowUsage"><span class="pre"><code class="sourceCode python">syside.FlowUsage</code></span></a>

  - <a href="/python/v0.8.4/syside/FlowUsage.md" class="reference internal" title="syside.FlowUsage.payload_feature_member"><span class="pre"><code class="sourceCode python">payload_feature_member</code></span></a>

</div>

</div>
