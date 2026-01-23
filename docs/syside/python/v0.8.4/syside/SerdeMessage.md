<div id="serdemessage" class="section">

# SerdeMessage<a href="#serdemessage" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">SerdeMessage</span></span><span class="sig-paren">\[</span>*<span class="n"><span class="pre">T</span></span>*<span class="sig-paren">\]</span><a href="#syside.SerdeMessage" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Message emitted during (de)serialization

<div class="align-center" align="center">

<img src="data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iZ3JhcGh2aXoiIHN0eWxlPSJ3aWR0aDogNi44MTI1cmVtO2hlaWdodDogMi43NXJlbTsiIHZpZXdib3g9IjAuMDAgMC4wMCAxMDkuMDAgNDQuMDAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxnIGNsYXNzPSJncmFwaCIgaWQ9ImdyYXBoMCIgdHJhbnNmb3JtPSJzY2FsZSgxIDEpIHJvdGF0ZSgwKSB0cmFuc2xhdGUoNCA0MCkiPgo8dGl0bGU+JTM8L3RpdGxlPgo8ZyBjbGFzcz0ibm9kZSIgaWQ9Im5vZGUxIj4KPHRpdGxlPlNlcmRlTWVzc2FnZTwvdGl0bGU+CjxnIGlkPSJhX25vZGUxIj48YSBocmVmPSIjc3lzaWRlLlNlcmRlTWVzc2FnZSI+Cjxwb2x5Z29uIHBvaW50cz0iMTAxLC0zNiAwLC0zNiAwLDAgMTAxLDAgMTAxLC0zNiIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtYmctY29sb3IpO3N0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1mZy1jb2xvcik7Ij48L3BvbHlnb24+Cjx0ZXh0IGZvbnQtZmFtaWx5PSJMZXhlbmQiIGZvbnQtc2l6ZT0iMTIuMDAiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1jb2RlLWZnLWNvbG9yKTstLW1kLWdyYXBodml6LWhvdmVyLWNvbG9yOiB2YXIoLS1tZC1ncmFwaHZpei1hLWhvdmVyLWNvbG9yKTsiIHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjUwLjUiIHk9Ii0xNC4yIj5TZXJkZU1lc3NhZ2U8L3RleHQ+Cjx0aXRsZT5zeXNpZGUuU2VyZGVNZXNzYWdlPC90aXRsZT48L2E+CjwvZz4KPC9nPgo8L2c+Cjwvc3ZnPg==" class="graphviz" />

</div>

<span class="sd-summary-text">Members defined in <a href="#syside.SerdeMessage" class="reference internal" title="syside.SerdeMessage"><span class="pre"><code class="sourceCode python">SerdeMessage</code></span></a> (4 members)</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |  |
|----|----|----|----|
| <span class="nerd-font"></span> | <a href="#syside.SerdeMessage.context" class="reference internal" title="syside.SerdeMessage.context"><span class="pre"><code class="sourceCode python">context</code></span></a> | <span class="pre">`R`</span> | The context that this message applies to. |
| <span class="nerd-font"></span> | <a href="#syside.SerdeMessage.message" class="reference internal" title="syside.SerdeMessage.message"><span class="pre"><code class="sourceCode python">message</code></span></a> | <span class="pre">`R`</span> | Message contents. |
| <span class="nerd-font"></span> | <a href="#syside.SerdeMessage.severity" class="reference internal" title="syside.SerdeMessage.severity"><span class="pre"><code class="sourceCode python">severity</code></span></a> | <span class="pre">`R`</span> | The severity of the message. |
| <span class="nerd-font"></span> | <a href="#syside.SerdeMessage.__str__" class="reference internal" title="syside.SerdeMessage.__str__"><span class="pre"><code class="sourceCode python"><span class="fu">__str__</span></code></span></a> |  |  |

</div>

</div>

<span class="nerd-font"></span> **Attributes**

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">context</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">syside.T</span>*<a href="#syside.SerdeMessage.context" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
The context that this message applies to.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">message</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span>*<a href="#syside.SerdeMessage.message" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Message contents.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">severity</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside.DiagnosticSeverity"><span class="pre">syside.DiagnosticSeverity</span></a>*<a href="#syside.SerdeMessage.severity" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
The severity of the message.

<span class="nerd-font"></span> **Methods**

<span class="sig-name descname"><span class="pre">\_\_str\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">str</span></span></span><a href="#syside.SerdeMessage.__str__" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside/SerdeReport.md" class="reference internal" title="syside.SerdeReport"><span class="pre"><code class="sourceCode python">syside.SerdeReport</code></span></a>

  - <a href="/python/v0.8.4/syside/SerdeReport.md" class="reference internal" title="syside.SerdeReport.messages"><span class="pre"><code class="sourceCode python">messages</code></span></a>

</div>

</div>
