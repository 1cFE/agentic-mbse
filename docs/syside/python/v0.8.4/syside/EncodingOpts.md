<div id="encodingopts" class="section">

# EncodingOpts<a href="#encodingopts" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">EncodingOpts</span></span><a href="#syside.EncodingOpts" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
Percent-encoding options

These options are used to customize the behavior of algorithms which use percent escapes, such as encoding or decoding.

<div class="align-center" align="center">

<img src="data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iZ3JhcGh2aXoiIHN0eWxlPSJ3aWR0aDogNi41NjI1cmVtO2hlaWdodDogMi43NXJlbTsiIHZpZXdib3g9IjAuMDAgMC4wMCAxMDUuMDAgNDQuMDAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxnIGNsYXNzPSJncmFwaCIgaWQ9ImdyYXBoMCIgdHJhbnNmb3JtPSJzY2FsZSgxIDEpIHJvdGF0ZSgwKSB0cmFuc2xhdGUoNCA0MCkiPgo8dGl0bGU+JTM8L3RpdGxlPgo8ZyBjbGFzcz0ibm9kZSIgaWQ9Im5vZGUxIj4KPHRpdGxlPkVuY29kaW5nT3B0czwvdGl0bGU+CjxnIGlkPSJhX25vZGUxIj48YSBocmVmPSIjc3lzaWRlLkVuY29kaW5nT3B0cyI+Cjxwb2x5Z29uIHBvaW50cz0iOTcsLTM2IDAsLTM2IDAsMCA5NywwIDk3LC0zNiIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtYmctY29sb3IpO3N0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1mZy1jb2xvcik7Ij48L3BvbHlnb24+Cjx0ZXh0IGZvbnQtZmFtaWx5PSJMZXhlbmQiIGZvbnQtc2l6ZT0iMTIuMDAiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1jb2RlLWZnLWNvbG9yKTstLW1kLWdyYXBodml6LWhvdmVyLWNvbG9yOiB2YXIoLS1tZC1ncmFwaHZpei1hLWhvdmVyLWNvbG9yKTsiIHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjQ4LjUiIHk9Ii0xNC4yIj5FbmNvZGluZ09wdHM8L3RleHQ+Cjx0aXRsZT5zeXNpZGUuRW5jb2RpbmdPcHRzPC90aXRsZT48L2E+CjwvZz4KPC9nPgo8L2c+Cjwvc3ZnPg==" class="graphviz" />

</div>

<span class="sd-summary-text">Members defined in <a href="#syside.EncodingOpts" class="reference internal" title="syside.EncodingOpts"><span class="pre"><code class="sourceCode python">EncodingOpts</code></span></a> (4 members)</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |  |
|----|----|----|----|
| <span class="nerd-font"></span> | <a href="#syside.EncodingOpts.disallow_null" class="reference internal" title="syside.EncodingOpts.disallow_null"><span class="pre"><code class="sourceCode python">disallow_null</code></span></a> | <span class="pre">`RW`</span> | True if nulls are not allowed |
| <span class="nerd-font"></span> | <a href="#syside.EncodingOpts.lower_case" class="reference internal" title="syside.EncodingOpts.lower_case"><span class="pre"><code class="sourceCode python">lower_case</code></span></a> | <span class="pre">`RW`</span> | True if hexadecimal digits are emitted as lower case |
| <span class="nerd-font"></span> | <a href="#syside.EncodingOpts.space_as_plus" class="reference internal" title="syside.EncodingOpts.space_as_plus"><span class="pre"><code class="sourceCode python">space_as_plus</code></span></a> | <span class="pre">`RW`</span> | True if spaces encode to and from plus signs |
| <span class="nerd-font"></span> | <a href="#syside.EncodingOpts.__init__" class="reference internal" title="syside.EncodingOpts.__init__"><span class="pre"><code class="sourceCode python"><span class="fu">__init__</span></code></span></a> |  |  |

</div>

</div>

<span class="nerd-font"></span> **Attributes**

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">disallow_null</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*<a href="#syside.EncodingOpts.disallow_null" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
True if nulls are not allowed

Normally all possible character values (from 0 to 255) are allowed, with reserved characters being replaced with escapes upon encoding. When this option is true, attempting to decode a null will result in an error.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">lower_case</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*<a href="#syside.EncodingOpts.lower_case" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
True if hexadecimal digits are emitted as lower case

By default, percent-encoding algorithms emit hexadecimal digits A through F as uppercase letters. When this option is <span class="pre">`true`</span>, lowercase letters are used.

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">space_as_plus</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*<a href="#syside.EncodingOpts.space_as_plus" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
True if spaces encode to and from plus signs

This option controls whether or not the PLUS character (“+”) is used to represent the SP character (” “) when encoding or decoding. Although not prescribed by the RFC, plus signs are commonly treated as spaces upon decoding when used in the query of URLs using well known schemes such as HTTP.

<span class="nerd-font"></span> **Methods**

<span class="sig-name descname"><span class="pre">\_\_init\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">space_as_plus</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">False</span></span>*, *<span class="n"><span class="pre">lower_case</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">False</span></span>*, *<span class="n"><span class="pre">disallow_null</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">False</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span><a href="#syside.EncodingOpts.__init__" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside"><span class="pre"><code class="sourceCode python">syside</code></span></a>

  - <a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside.decode_path"><span class="pre"><code class="sourceCode python">decode_path</code></span></a>

  - <a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside.make_file_url"><span class="pre"><code class="sourceCode python">make_file_url</code></span></a>

- <a href="/python/v0.8.4/syside/Url.md" class="reference internal" title="syside.Url"><span class="pre"><code class="sourceCode python">syside.Url</code></span></a>

  - <a href="/python/v0.8.4/syside/Url.md" class="reference internal" title="syside.Url.params"><span class="pre"><code class="sourceCode python">params</code></span></a>

</div>

</div>
