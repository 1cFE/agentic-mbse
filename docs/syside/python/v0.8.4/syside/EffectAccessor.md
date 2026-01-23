<div id="effectaccessor" class="section">

# EffectAccessor<a href="#effectaccessor" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">EffectAccessor</span></span><a href="#syside.EffectAccessor" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
<div class="align-center" align="center">

<img src="data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iZ3JhcGh2aXoiIHN0eWxlPSJ3aWR0aDogMTAuMzEyNXJlbTtoZWlnaHQ6IDExLjc1cmVtOyIgdmlld2JveD0iMC4wMCAwLjAwIDE2NS4wMCAxODguMDAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxnIGNsYXNzPSJncmFwaCIgaWQ9ImdyYXBoMCIgdHJhbnNmb3JtPSJzY2FsZSgxIDEpIHJvdGF0ZSgwKSB0cmFuc2xhdGUoNCAxODQpIj4KPHRpdGxlPiUzPC90aXRsZT4KPGcgY2xhc3M9Im5vZGUiIGlkPSJub2RlMSI+Cjx0aXRsZT5FZmZlY3RBY2Nlc3NvcjwvdGl0bGU+CjxnIGlkPSJhX25vZGUxIj48YSBocmVmPSIjc3lzaWRlLkVmZmVjdEFjY2Vzc29yIj4KPHBvbHlnb24gcG9pbnRzPSIxMjkuNSwtMzYgMjcuNSwtMzYgMjcuNSwwIDEyOS41LDAgMTI5LjUsLTM2IiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1iZy1jb2xvcik7c3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1ub2RlLWZnLWNvbG9yKTsiPjwvcG9seWdvbj4KPHRleHQgZm9udC1mYW1pbHk9IkxleGVuZCIgZm9udC1zaXplPSIxMi4wMCIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWNvZGUtZmctY29sb3IpOy0tbWQtZ3JhcGh2aXotaG92ZXItY29sb3I6IHZhcigtLW1kLWdyYXBodml6LWEtaG92ZXItY29sb3IpOyIgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iNzguNSIgeT0iLTE0LjIiPkVmZmVjdEFjY2Vzc29yPC90ZXh0Pgo8dGl0bGU+c3lzaWRlLkVmZmVjdEFjY2Vzc29yPC90aXRsZT48L2E+CjwvZz4KPC9nPgo8ZyBjbGFzcz0ibm9kZSIgaWQ9Im5vZGUyIj4KPHRpdGxlPk93bmVkTWVtYmVyQWNjZXNzb3I8L3RpdGxlPgo8ZyBpZD0iYV9ub2RlMiI+PGEgaHJlZj0iL3B5dGhvbi92MC44LjQvc3lzaWRlL093bmVkTWVtYmVyQWNjZXNzb3IubWQiPgo8cG9seWdvbiBwb2ludHM9IjE1NywtMTA4IDAsLTEwOCAwLC03MiAxNTcsLTcyIDE1NywtMTA4IiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1iZy1jb2xvcik7c3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1ub2RlLWZnLWNvbG9yKTsiPjwvcG9seWdvbj4KPHRleHQgZm9udC1mYW1pbHk9IkxleGVuZCIgZm9udC1zaXplPSIxMi4wMCIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWNvZGUtZmctY29sb3IpOy0tbWQtZ3JhcGh2aXotaG92ZXItY29sb3I6IHZhcigtLW1kLWdyYXBodml6LWEtaG92ZXItY29sb3IpOyIgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iNzguNSIgeT0iLTg2LjIiPk93bmVkTWVtYmVyQWNjZXNzb3I8L3RleHQ+Cjx0aXRsZT5zeXNpZGUuT3duZWRNZW1iZXJBY2Nlc3NvcjwvdGl0bGU+PC9hPgo8L2c+CjwvZz4KPGcgY2xhc3M9ImVkZ2UiIGlkPSJlZGdlMSI+Cjx0aXRsZT5Pd25lZE1lbWJlckFjY2Vzc29yLSZndDtFZmZlY3RBY2Nlc3NvcjwvdGl0bGU+CjxwYXRoIGQ9Ik03OC41LC03MS43Qzc4LjUsLTYzLjk4IDc4LjUsLTU0LjcxIDc4LjUsLTQ2LjExIiBmaWxsPSJub25lIiBzdHlsZT0ic3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1lZGdlLWNvbG9yKTsiIC8+Cjxwb2x5Z29uIHBvaW50cz0iODIsLTQ2LjEgNzguNSwtMzYuMSA3NSwtNDYuMSA4MiwtNDYuMSIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWdyYXBodml6LWVkZ2UtY29sb3IpO3N0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotZWRnZS1jb2xvcik7Ij48L3BvbHlnb24+CjwvZz4KPGcgY2xhc3M9Im5vZGUiIGlkPSJub2RlMyI+Cjx0aXRsZT5NZW1iZXJBY2Nlc3NvcjwvdGl0bGU+CjxnIGlkPSJhX25vZGUzIj48YSBocmVmPSIvcHl0aG9uL3YwLjguNC9zeXNpZGUvTWVtYmVyQWNjZXNzb3IubWQiPgo8cG9seWdvbiBwb2ludHM9IjEzNiwtMTgwIDIxLC0xODAgMjEsLTE0NCAxMzYsLTE0NCAxMzYsLTE4MCIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtYmctY29sb3IpO3N0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1mZy1jb2xvcik7Ij48L3BvbHlnb24+Cjx0ZXh0IGZvbnQtZmFtaWx5PSJMZXhlbmQiIGZvbnQtc2l6ZT0iMTIuMDAiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1jb2RlLWZnLWNvbG9yKTstLW1kLWdyYXBodml6LWhvdmVyLWNvbG9yOiB2YXIoLS1tZC1ncmFwaHZpei1hLWhvdmVyLWNvbG9yKTsiIHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9Ijc4LjUiIHk9Ii0xNTguMiI+TWVtYmVyQWNjZXNzb3I8L3RleHQ+Cjx0aXRsZT5zeXNpZGUuTWVtYmVyQWNjZXNzb3I8L3RpdGxlPjwvYT4KPC9nPgo8L2c+CjxnIGNsYXNzPSJlZGdlIiBpZD0iZWRnZTIiPgo8dGl0bGU+TWVtYmVyQWNjZXNzb3ItJmd0O093bmVkTWVtYmVyQWNjZXNzb3I8L3RpdGxlPgo8cGF0aCBkPSJNNzguNSwtMTQzLjdDNzguNSwtMTM1Ljk4IDc4LjUsLTEyNi43MSA3OC41LC0xMTguMTEiIGZpbGw9Im5vbmUiIHN0eWxlPSJzdHJva2U6IHZhcigtLW1kLWdyYXBodml6LWVkZ2UtY29sb3IpOyIgLz4KPHBvbHlnb24gcG9pbnRzPSI4MiwtMTE4LjEgNzguNSwtMTA4LjEgNzUsLTExOC4xIDgyLC0xMTguMSIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWdyYXBodml6LWVkZ2UtY29sb3IpO3N0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotZWRnZS1jb2xvcik7Ij48L3BvbHlnb24+CjwvZz4KPC9nPgo8L3N2Zz4=" class="graphviz" />

</div>

<span class="sd-summary-text">Members defined in <a href="#syside.EffectAccessor" class="reference internal" title="syside.EffectAccessor"><span class="pre"><code class="sourceCode python">EffectAccessor</code></span></a> (1 member)</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |  |
|----|----|----|----|
| <span class="nerd-font"></span> | <a href="#syside.EffectAccessor.set_member_element" class="reference internal" title="syside.EffectAccessor.set_member_element"><span class="pre"><code class="sourceCode python">set_member_element</code></span></a> |  | Set a new *owned* <span class="pre">`member_element`</span>, ownership constraints apply. Replaces the previous <span class="pre">`member_element`</span>, which may be reused by the model. <span class="pre">`name_id`</span> has no effect since the <span class="pre">`element`</span> is always taken ownership of. |

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

<span class="sig-name descname"><span class="pre">set_member_element</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">element</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">syside.EffectAccessor.set_member_element.M</span></span>*, *<span class="n"><span class="pre">name</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside.NameID"><span class="pre">syside.NameID</span></a></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">...</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/TransitionFeatureMembership.md" class="reference internal" title="syside.TransitionFeatureMembership"><span class="pre">syside.TransitionFeatureMembership</span></a><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">syside.EffectAccessor.set_member_element.M</span><span class="p"><span class="pre">\]</span></span></span></span><a href="#syside.EffectAccessor.set_member_element" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Set a new *owned* <span class="pre">`member_element`</span>, ownership constraints apply. Replaces the previous <span class="pre">`member_element`</span>, which may be reused by the model. <span class="pre">`name_id`</span> has no effect since the <span class="pre">`element`</span> is always taken ownership of.

Returns a pair of (<span class="pre">`membership`</span>, <span class="pre">`member_element`</span>) where <span class="pre">`member_element`</span> is <span class="pre">`element`</span>.

<span class="sig-name descname"><span class="pre">set_member_element</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">element</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">syside.EffectAccessor.set_member_element.M</span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span></span>*, *<span class="n"><span class="pre">name</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside.NameID"><span class="pre">syside.NameID</span></a></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">...</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/TransitionFeatureMembership.md" class="reference internal" title="syside.TransitionFeatureMembership"><span class="pre">syside.TransitionFeatureMembership</span></a><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">syside.EffectAccessor.set_member_element.M</span><span class="p"><span class="pre">\]</span></span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span></span></span>  
<span class="pre">`set_member_element`</span> overload that will remove the member element if <span class="pre">`element`</span> is <span class="pre">`None`</span>, otherwise the behaviour is the same.

<span class="sig-name descname"><span class="pre">set_member_element</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">element</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">type</span><span class="p"><span class="pre">\[</span></span><span class="pre">syside.EffectAccessor.set_member_element.M</span><span class="p"><span class="pre">\]</span></span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><a href="/python/v0.8.4/syside/TransitionFeatureMembership.md" class="reference internal" title="syside.TransitionFeatureMembership"><span class="pre">syside.TransitionFeatureMembership</span></a><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">syside.EffectAccessor.set_member_element.M</span><span class="p"><span class="pre">\]</span></span></span></span>  
Constructs a new empty <span class="pre">`member_element`</span> with the provided type. Replaces the previous <span class="pre">`member_element`</span>. Because a new element is always constructed, ownership constraints do not apply.

Returns a pair of (<span class="pre">`membership`</span>, <span class="pre">`member_element`</span>).

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/TransitionUsage.md" class="reference internal" title="syside.TransitionUsage"><span class="pre"><code class="sourceCode python">syside.TransitionUsage</code></span></a>

  - <a href="/python/v0.8.4/syside/TransitionUsage.md" class="reference internal" title="syside.TransitionUsage.effect_action_member"><span class="pre"><code class="sourceCode python">effect_action_member</code></span></a>

</div>

</div>
