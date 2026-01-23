<div id="url" class="section">

# Url<a href="#url" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">Url</span></span><a href="#syside.Url" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  
<span class="pre">`URL`</span> as described using the <a href="https://datatracker.ietf.org/doc/html/rfc3986" class="reference external" target="_blank">Uniform Resource Identifier (URI)</a> specification (RFC3986).

Raises <span class="pre">`RuntimeError`</span> on invalid URLs, including those with unicode characters. Unicode characters must be percent escaped by encoding them as hex with <span class="pre">`%`</span> escape.

See <a href="https://github.com/boostorg/url" class="reference external" target="_blank">Boost.URL</a> for more details.

<div class="align-center" align="center">

<img src="data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iZ3JhcGh2aXoiIHN0eWxlPSJ3aWR0aDogMy44NzVyZW07aGVpZ2h0OiAyLjc1cmVtOyIgdmlld2JveD0iMC4wMCAwLjAwIDYyLjAwIDQ0LjAwIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPgo8ZyBjbGFzcz0iZ3JhcGgiIGlkPSJncmFwaDAiIHRyYW5zZm9ybT0ic2NhbGUoMSAxKSByb3RhdGUoMCkgdHJhbnNsYXRlKDQgNDApIj4KPHRpdGxlPiUzPC90aXRsZT4KPGcgY2xhc3M9Im5vZGUiIGlkPSJub2RlMSI+Cjx0aXRsZT5Vcmw8L3RpdGxlPgo8ZyBpZD0iYV9ub2RlMSI+PGEgaHJlZj0iI3N5c2lkZS5VcmwiPgo8cG9seWdvbiBwb2ludHM9IjU0LC0zNiAwLC0zNiAwLDAgNTQsMCA1NCwtMzYiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1ncmFwaHZpei1ub2RlLWJnLWNvbG9yKTtzdHJva2U6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtZmctY29sb3IpOyI+PC9wb2x5Z29uPgo8dGV4dCBmb250LWZhbWlseT0iTGV4ZW5kIiBmb250LXNpemU9IjEyLjAwIiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtY29kZS1mZy1jb2xvcik7LS1tZC1ncmFwaHZpei1ob3Zlci1jb2xvcjogdmFyKC0tbWQtZ3JhcGh2aXotYS1ob3Zlci1jb2xvcik7IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSIyNyIgeT0iLTE0LjIiPlVybDwvdGV4dD4KPHRpdGxlPnN5c2lkZS5Vcmw8L3RpdGxlPjwvYT4KPC9nPgo8L2c+CjwvZz4KPC9zdmc+" class="graphviz" />

</div>

<span class="sd-summary-text">Members defined in <a href="#syside.Url" class="reference internal" title="syside.Url"><span class="pre"><code class="sourceCode python">Url</code></span></a> (94 members)</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="pst-scrollable-table-container">

|  |  |  |  |
|----|----|----|----|
| <span class="nerd-font"></span> | <a href="#syside.Url.authority" class="reference internal" title="syside.Url.authority"><span class="pre"><code class="sourceCode python">authority</code></span></a> | <span class="pre">`R`</span> |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.encoded_authority" class="reference internal" title="syside.Url.encoded_authority"><span class="pre"><code class="sourceCode python">encoded_authority</code></span></a> | <span class="pre">`R`</span> |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.encoded_fragment" class="reference internal" title="syside.Url.encoded_fragment"><span class="pre"><code class="sourceCode python">encoded_fragment</code></span></a> | <span class="pre">`R`</span> |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.encoded_host" class="reference internal" title="syside.Url.encoded_host"><span class="pre"><code class="sourceCode python">encoded_host</code></span></a> | <span class="pre">`R`</span> |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.encoded_host_address" class="reference internal" title="syside.Url.encoded_host_address"><span class="pre"><code class="sourceCode python">encoded_host_address</code></span></a> | <span class="pre">`R`</span> |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.encoded_host_and_port" class="reference internal" title="syside.Url.encoded_host_and_port"><span class="pre"><code class="sourceCode python">encoded_host_and_port</code></span></a> | <span class="pre">`R`</span> |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.encoded_host_name" class="reference internal" title="syside.Url.encoded_host_name"><span class="pre"><code class="sourceCode python">encoded_host_name</code></span></a> | <span class="pre">`R`</span> |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.encoded_origin" class="reference internal" title="syside.Url.encoded_origin"><span class="pre"><code class="sourceCode python">encoded_origin</code></span></a> | <span class="pre">`R`</span> |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.encoded_params" class="reference internal" title="syside.Url.encoded_params"><span class="pre"><code class="sourceCode python">encoded_params</code></span></a> | <span class="pre">`R`</span> |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.encoded_password" class="reference internal" title="syside.Url.encoded_password"><span class="pre"><code class="sourceCode python">encoded_password</code></span></a> | <span class="pre">`R`</span> |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.encoded_path" class="reference internal" title="syside.Url.encoded_path"><span class="pre"><code class="sourceCode python">encoded_path</code></span></a> | <span class="pre">`R`</span> |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.encoded_query" class="reference internal" title="syside.Url.encoded_query"><span class="pre"><code class="sourceCode python">encoded_query</code></span></a> | <span class="pre">`R`</span> |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.encoded_resource" class="reference internal" title="syside.Url.encoded_resource"><span class="pre"><code class="sourceCode python">encoded_resource</code></span></a> | <span class="pre">`R`</span> |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.encoded_target" class="reference internal" title="syside.Url.encoded_target"><span class="pre"><code class="sourceCode python">encoded_target</code></span></a> | <span class="pre">`R`</span> |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.encoded_user" class="reference internal" title="syside.Url.encoded_user"><span class="pre"><code class="sourceCode python">encoded_user</code></span></a> | <span class="pre">`R`</span> |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.encoded_userinfo" class="reference internal" title="syside.Url.encoded_userinfo"><span class="pre"><code class="sourceCode python">encoded_userinfo</code></span></a> | <span class="pre">`R`</span> |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.encoded_zone_id" class="reference internal" title="syside.Url.encoded_zone_id"><span class="pre"><code class="sourceCode python">encoded_zone_id</code></span></a> | <span class="pre">`R`</span> |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.fragment" class="reference internal" title="syside.Url.fragment"><span class="pre"><code class="sourceCode python">fragment</code></span></a> | <span class="pre">`R`</span> |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.has_authority" class="reference internal" title="syside.Url.has_authority"><span class="pre"><code class="sourceCode python">has_authority</code></span></a> | <span class="pre">`R`</span> |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.has_fragment" class="reference internal" title="syside.Url.has_fragment"><span class="pre"><code class="sourceCode python">has_fragment</code></span></a> | <span class="pre">`R`</span> |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.has_password" class="reference internal" title="syside.Url.has_password"><span class="pre"><code class="sourceCode python">has_password</code></span></a> | <span class="pre">`R`</span> |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.has_port" class="reference internal" title="syside.Url.has_port"><span class="pre"><code class="sourceCode python">has_port</code></span></a> | <span class="pre">`R`</span> |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.has_query" class="reference internal" title="syside.Url.has_query"><span class="pre"><code class="sourceCode python">has_query</code></span></a> | <span class="pre">`R`</span> |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.has_scheme" class="reference internal" title="syside.Url.has_scheme"><span class="pre"><code class="sourceCode python">has_scheme</code></span></a> | <span class="pre">`R`</span> |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.has_userinfo" class="reference internal" title="syside.Url.has_userinfo"><span class="pre"><code class="sourceCode python">has_userinfo</code></span></a> | <span class="pre">`R`</span> |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.host" class="reference internal" title="syside.Url.host"><span class="pre"><code class="sourceCode python">host</code></span></a> | <span class="pre">`R`</span> |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.host_address" class="reference internal" title="syside.Url.host_address"><span class="pre"><code class="sourceCode python">host_address</code></span></a> | <span class="pre">`R`</span> |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.host_ipv4_address" class="reference internal" title="syside.Url.host_ipv4_address"><span class="pre"><code class="sourceCode python">host_ipv4_address</code></span></a> | <span class="pre">`R`</span> |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.host_ipv6_address" class="reference internal" title="syside.Url.host_ipv6_address"><span class="pre"><code class="sourceCode python">host_ipv6_address</code></span></a> | <span class="pre">`R`</span> |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.host_ipvfuture" class="reference internal" title="syside.Url.host_ipvfuture"><span class="pre"><code class="sourceCode python">host_ipvfuture</code></span></a> | <span class="pre">`R`</span> |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.host_name" class="reference internal" title="syside.Url.host_name"><span class="pre"><code class="sourceCode python">host_name</code></span></a> | <span class="pre">`R`</span> |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.host_type" class="reference internal" title="syside.Url.host_type"><span class="pre"><code class="sourceCode python">host_type</code></span></a> | <span class="pre">`R`</span> |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.is_path_absolute" class="reference internal" title="syside.Url.is_path_absolute"><span class="pre"><code class="sourceCode python">is_path_absolute</code></span></a> | <span class="pre">`R`</span> |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.password" class="reference internal" title="syside.Url.password"><span class="pre"><code class="sourceCode python">password</code></span></a> | <span class="pre">`R`</span> |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.path" class="reference internal" title="syside.Url.path"><span class="pre"><code class="sourceCode python">path</code></span></a> | <span class="pre">`R`</span> |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.port" class="reference internal" title="syside.Url.port"><span class="pre"><code class="sourceCode python">port</code></span></a> | <span class="pre">`R`</span> |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.port_number" class="reference internal" title="syside.Url.port_number"><span class="pre"><code class="sourceCode python">port_number</code></span></a> | <span class="pre">`R`</span> |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.query" class="reference internal" title="syside.Url.query"><span class="pre"><code class="sourceCode python">query</code></span></a> | <span class="pre">`R`</span> |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.scheme" class="reference internal" title="syside.Url.scheme"><span class="pre"><code class="sourceCode python">scheme</code></span></a> | <span class="pre">`R`</span> |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.scheme_id" class="reference internal" title="syside.Url.scheme_id"><span class="pre"><code class="sourceCode python">scheme_id</code></span></a> | <span class="pre">`R`</span> |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.user" class="reference internal" title="syside.Url.user"><span class="pre"><code class="sourceCode python">user</code></span></a> | <span class="pre">`R`</span> |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.userinfo" class="reference internal" title="syside.Url.userinfo"><span class="pre"><code class="sourceCode python">userinfo</code></span></a> | <span class="pre">`R`</span> |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.zone_id" class="reference internal" title="syside.Url.zone_id"><span class="pre"><code class="sourceCode python">zone_id</code></span></a> | <span class="pre">`R`</span> |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.__bool__" class="reference internal" title="syside.Url.__bool__"><span class="pre"><code class="sourceCode python"><span class="fu">__bool__</span></code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.__copy__" class="reference internal" title="syside.Url.__copy__"><span class="pre"><code class="sourceCode python">__copy__</code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.__deepcopy__" class="reference internal" title="syside.Url.__deepcopy__"><span class="pre"><code class="sourceCode python">__deepcopy__</code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.__hash__" class="reference internal" title="syside.Url.__hash__"><span class="pre"><code class="sourceCode python"><span class="fu">__hash__</span></code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.__init__" class="reference internal" title="syside.Url.__init__"><span class="pre"><code class="sourceCode python"><span class="fu">__init__</span></code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.__len__" class="reference internal" title="syside.Url.__len__"><span class="pre"><code class="sourceCode python"><span class="fu">__len__</span></code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.__repr__" class="reference internal" title="syside.Url.__repr__"><span class="pre"><code class="sourceCode python"><span class="fu">__repr__</span></code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.__str__" class="reference internal" title="syside.Url.__str__"><span class="pre"><code class="sourceCode python"><span class="fu">__str__</span></code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.clear" class="reference internal" title="syside.Url.clear"><span class="pre"><code class="sourceCode python">clear</code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.normalize" class="reference internal" title="syside.Url.normalize"><span class="pre"><code class="sourceCode python">normalize</code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.normalize_authority" class="reference internal" title="syside.Url.normalize_authority"><span class="pre"><code class="sourceCode python">normalize_authority</code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.normalize_fragment" class="reference internal" title="syside.Url.normalize_fragment"><span class="pre"><code class="sourceCode python">normalize_fragment</code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.normalize_path" class="reference internal" title="syside.Url.normalize_path"><span class="pre"><code class="sourceCode python">normalize_path</code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.normalize_query" class="reference internal" title="syside.Url.normalize_query"><span class="pre"><code class="sourceCode python">normalize_query</code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.normalize_scheme" class="reference internal" title="syside.Url.normalize_scheme"><span class="pre"><code class="sourceCode python">normalize_scheme</code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.params" class="reference internal" title="syside.Url.params"><span class="pre"><code class="sourceCode python">params</code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.remove_authority" class="reference internal" title="syside.Url.remove_authority"><span class="pre"><code class="sourceCode python">remove_authority</code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.remove_fragment" class="reference internal" title="syside.Url.remove_fragment"><span class="pre"><code class="sourceCode python">remove_fragment</code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.remove_origin" class="reference internal" title="syside.Url.remove_origin"><span class="pre"><code class="sourceCode python">remove_origin</code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.remove_password" class="reference internal" title="syside.Url.remove_password"><span class="pre"><code class="sourceCode python">remove_password</code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.remove_port" class="reference internal" title="syside.Url.remove_port"><span class="pre"><code class="sourceCode python">remove_port</code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.remove_query" class="reference internal" title="syside.Url.remove_query"><span class="pre"><code class="sourceCode python">remove_query</code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.remove_scheme" class="reference internal" title="syside.Url.remove_scheme"><span class="pre"><code class="sourceCode python">remove_scheme</code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.remove_userinfo" class="reference internal" title="syside.Url.remove_userinfo"><span class="pre"><code class="sourceCode python">remove_userinfo</code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.reserve" class="reference internal" title="syside.Url.reserve"><span class="pre"><code class="sourceCode python">reserve</code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.set_encoded_authority" class="reference internal" title="syside.Url.set_encoded_authority"><span class="pre"><code class="sourceCode python">set_encoded_authority</code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.set_encoded_fragment" class="reference internal" title="syside.Url.set_encoded_fragment"><span class="pre"><code class="sourceCode python">set_encoded_fragment</code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.set_encoded_host" class="reference internal" title="syside.Url.set_encoded_host"><span class="pre"><code class="sourceCode python">set_encoded_host</code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.set_encoded_host_address" class="reference internal" title="syside.Url.set_encoded_host_address"><span class="pre"><code class="sourceCode python">set_encoded_host_address</code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.set_encoded_host_name" class="reference internal" title="syside.Url.set_encoded_host_name"><span class="pre"><code class="sourceCode python">set_encoded_host_name</code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.set_encoded_password" class="reference internal" title="syside.Url.set_encoded_password"><span class="pre"><code class="sourceCode python">set_encoded_password</code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.set_encoded_path" class="reference internal" title="syside.Url.set_encoded_path"><span class="pre"><code class="sourceCode python">set_encoded_path</code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.set_encoded_query" class="reference internal" title="syside.Url.set_encoded_query"><span class="pre"><code class="sourceCode python">set_encoded_query</code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.set_encoded_user" class="reference internal" title="syside.Url.set_encoded_user"><span class="pre"><code class="sourceCode python">set_encoded_user</code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.set_encoded_userinfo" class="reference internal" title="syside.Url.set_encoded_userinfo"><span class="pre"><code class="sourceCode python">set_encoded_userinfo</code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.set_fragment" class="reference internal" title="syside.Url.set_fragment"><span class="pre"><code class="sourceCode python">set_fragment</code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.set_host" class="reference internal" title="syside.Url.set_host"><span class="pre"><code class="sourceCode python">set_host</code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.set_host_address" class="reference internal" title="syside.Url.set_host_address"><span class="pre"><code class="sourceCode python">set_host_address</code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.set_host_ipv4" class="reference internal" title="syside.Url.set_host_ipv4"><span class="pre"><code class="sourceCode python">set_host_ipv4</code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.set_host_ipv6" class="reference internal" title="syside.Url.set_host_ipv6"><span class="pre"><code class="sourceCode python">set_host_ipv6</code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.set_host_ipvfuture" class="reference internal" title="syside.Url.set_host_ipvfuture"><span class="pre"><code class="sourceCode python">set_host_ipvfuture</code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.set_host_name" class="reference internal" title="syside.Url.set_host_name"><span class="pre"><code class="sourceCode python">set_host_name</code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.set_password" class="reference internal" title="syside.Url.set_password"><span class="pre"><code class="sourceCode python">set_password</code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.set_path" class="reference internal" title="syside.Url.set_path"><span class="pre"><code class="sourceCode python">set_path</code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.set_port" class="reference internal" title="syside.Url.set_port"><span class="pre"><code class="sourceCode python">set_port</code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.set_port_number" class="reference internal" title="syside.Url.set_port_number"><span class="pre"><code class="sourceCode python">set_port_number</code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.set_query" class="reference internal" title="syside.Url.set_query"><span class="pre"><code class="sourceCode python">set_query</code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.set_scheme" class="reference internal" title="syside.Url.set_scheme"><span class="pre"><code class="sourceCode python">set_scheme</code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.set_scheme_id" class="reference internal" title="syside.Url.set_scheme_id"><span class="pre"><code class="sourceCode python">set_scheme_id</code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.set_user" class="reference internal" title="syside.Url.set_user"><span class="pre"><code class="sourceCode python">set_user</code></span></a> |  |  |
| <span class="nerd-font"></span> | <a href="#syside.Url.set_userinfo" class="reference internal" title="syside.Url.set_userinfo"><span class="pre"><code class="sourceCode python">set_userinfo</code></span></a> |  |  |

</div>

</div>

<span class="nerd-font"></span> **Attributes**

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">authority</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span>*<a href="#syside.Url.authority" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">encoded_authority</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span>*<a href="#syside.Url.encoded_authority" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">encoded_fragment</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span>*<a href="#syside.Url.encoded_fragment" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">encoded_host</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span>*<a href="#syside.Url.encoded_host" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">encoded_host_address</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span>*<a href="#syside.Url.encoded_host_address" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">encoded_host_and_port</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span>*<a href="#syside.Url.encoded_host_and_port" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">encoded_host_name</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span>*<a href="#syside.Url.encoded_host_name" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">encoded_origin</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span>*<a href="#syside.Url.encoded_origin" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">encoded_params</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">list</span><span class="p"><span class="pre">\[</span></span><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><span class="pre">str</span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span><span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">\]</span></span>*<a href="#syside.Url.encoded_params" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">encoded_password</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span>*<a href="#syside.Url.encoded_password" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">encoded_path</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span>*<a href="#syside.Url.encoded_path" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">encoded_query</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span>*<a href="#syside.Url.encoded_query" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">encoded_resource</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span>*<a href="#syside.Url.encoded_resource" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">encoded_target</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span>*<a href="#syside.Url.encoded_target" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">encoded_user</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span>*<a href="#syside.Url.encoded_user" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">encoded_userinfo</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span>*<a href="#syside.Url.encoded_userinfo" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">encoded_zone_id</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span>*<a href="#syside.Url.encoded_zone_id" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">fragment</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span>*<a href="#syside.Url.fragment" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">has_authority</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*<a href="#syside.Url.has_authority" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">has_fragment</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*<a href="#syside.Url.has_fragment" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">has_password</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*<a href="#syside.Url.has_password" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">has_port</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*<a href="#syside.Url.has_port" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">has_query</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*<a href="#syside.Url.has_query" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">has_scheme</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*<a href="#syside.Url.has_scheme" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">has_userinfo</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*<a href="#syside.Url.has_userinfo" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">host</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span>*<a href="#syside.Url.host" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">host_address</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span>*<a href="#syside.Url.host_address" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">host_ipv4_address</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/IPv4Address.md" class="reference internal" title="syside.IPv4Address"><span class="pre">syside.IPv4Address</span></a>*<a href="#syside.Url.host_ipv4_address" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">host_ipv6_address</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside/IPv6Address.md" class="reference internal" title="syside.IPv6Address"><span class="pre">syside.IPv6Address</span></a>*<a href="#syside.Url.host_ipv6_address" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">host_ipvfuture</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span>*<a href="#syside.Url.host_ipvfuture" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">host_name</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span>*<a href="#syside.Url.host_name" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">host_type</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside.HostType"><span class="pre">syside.HostType</span></a>*<a href="#syside.Url.host_type" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">is_path_absolute</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*<a href="#syside.Url.is_path_absolute" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">password</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span>*<a href="#syside.Url.password" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">path</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span>*<a href="#syside.Url.path" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">port</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span>*<a href="#syside.Url.port" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">port_number</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">int</span>*<a href="#syside.Url.port_number" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">query</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span>*<a href="#syside.Url.query" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">scheme</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span>*<a href="#syside.Url.scheme" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">scheme_id</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside.Scheme"><span class="pre">syside.Scheme</span></a>*<a href="#syside.Url.scheme_id" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">user</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span>*<a href="#syside.Url.user" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">userinfo</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span>*<a href="#syside.Url.userinfo" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

*<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">zone_id</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span>*<a href="#syside.Url.zone_id" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="nerd-font"></span> **Methods**

<span class="sig-name descname"><span class="pre">\_\_bool\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">bool</span></span></span><a href="#syside.Url.__bool__" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">\_\_copy\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="#syside.Url" class="reference internal" title="syside.Url"><span class="pre">syside.Url</span></a></span></span><a href="#syside.Url.__copy__" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">\_\_deepcopy\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="#syside.Url" class="reference internal" title="syside.Url"><span class="pre">syside.Url</span></a></span></span><a href="#syside.Url.__deepcopy__" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">\_\_hash\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">int</span></span></span><a href="#syside.Url.__hash__" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">\_\_init\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span><a href="#syside.Url.__init__" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">\_\_init\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span>  

<span class="sig-name descname"><span class="pre">\_\_len\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">int</span></span></span><a href="#syside.Url.__len__" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">\_\_repr\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">str</span></span></span><a href="#syside.Url.__repr__" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">\_\_str\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">str</span></span></span><a href="#syside.Url.__str__" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">clear</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span><a href="#syside.Url.clear" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">normalize</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="#syside.Url" class="reference internal" title="syside.Url"><span class="pre">syside.Url</span></a></span></span><a href="#syside.Url.normalize" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">normalize_authority</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="#syside.Url" class="reference internal" title="syside.Url"><span class="pre">syside.Url</span></a></span></span><a href="#syside.Url.normalize_authority" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">normalize_fragment</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="#syside.Url" class="reference internal" title="syside.Url"><span class="pre">syside.Url</span></a></span></span><a href="#syside.Url.normalize_fragment" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">normalize_path</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="#syside.Url" class="reference internal" title="syside.Url"><span class="pre">syside.Url</span></a></span></span><a href="#syside.Url.normalize_path" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">normalize_query</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="#syside.Url" class="reference internal" title="syside.Url"><span class="pre">syside.Url</span></a></span></span><a href="#syside.Url.normalize_query" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">normalize_scheme</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="#syside.Url" class="reference internal" title="syside.Url"><span class="pre">syside.Url</span></a></span></span><a href="#syside.Url.normalize_scheme" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">params</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">options</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/EncodingOpts.md" class="reference internal" title="syside.EncodingOpts"><span class="pre">syside.EncodingOpts</span></a></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">...</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">list</span><span class="p"><span class="pre">\[</span></span><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><span class="pre">str</span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><span class="pre">None</span><span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">\]</span></span></span></span><a href="#syside.Url.params" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">remove_authority</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="#syside.Url" class="reference internal" title="syside.Url"><span class="pre">syside.Url</span></a></span></span><a href="#syside.Url.remove_authority" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">remove_fragment</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="#syside.Url" class="reference internal" title="syside.Url"><span class="pre">syside.Url</span></a></span></span><a href="#syside.Url.remove_fragment" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">remove_origin</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="#syside.Url" class="reference internal" title="syside.Url"><span class="pre">syside.Url</span></a></span></span><a href="#syside.Url.remove_origin" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">remove_password</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="#syside.Url" class="reference internal" title="syside.Url"><span class="pre">syside.Url</span></a></span></span><a href="#syside.Url.remove_password" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">remove_port</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="#syside.Url" class="reference internal" title="syside.Url"><span class="pre">syside.Url</span></a></span></span><a href="#syside.Url.remove_port" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">remove_query</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="#syside.Url" class="reference internal" title="syside.Url"><span class="pre">syside.Url</span></a></span></span><a href="#syside.Url.remove_query" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">remove_scheme</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="#syside.Url" class="reference internal" title="syside.Url"><span class="pre">syside.Url</span></a></span></span><a href="#syside.Url.remove_scheme" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">remove_userinfo</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="#syside.Url" class="reference internal" title="syside.Url"><span class="pre">syside.Url</span></a></span></span><a href="#syside.Url.remove_userinfo" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">reserve</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">int</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">None</span></span></span><a href="#syside.Url.reserve" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">set_encoded_authority</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="#syside.Url" class="reference internal" title="syside.Url"><span class="pre">syside.Url</span></a></span></span><a href="#syside.Url.set_encoded_authority" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">set_encoded_fragment</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="#syside.Url" class="reference internal" title="syside.Url"><span class="pre">syside.Url</span></a></span></span><a href="#syside.Url.set_encoded_fragment" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">set_encoded_host</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="#syside.Url" class="reference internal" title="syside.Url"><span class="pre">syside.Url</span></a></span></span><a href="#syside.Url.set_encoded_host" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">set_encoded_host_address</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="#syside.Url" class="reference internal" title="syside.Url"><span class="pre">syside.Url</span></a></span></span><a href="#syside.Url.set_encoded_host_address" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">set_encoded_host_name</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="#syside.Url" class="reference internal" title="syside.Url"><span class="pre">syside.Url</span></a></span></span><a href="#syside.Url.set_encoded_host_name" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">set_encoded_password</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="#syside.Url" class="reference internal" title="syside.Url"><span class="pre">syside.Url</span></a></span></span><a href="#syside.Url.set_encoded_password" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">set_encoded_path</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="#syside.Url" class="reference internal" title="syside.Url"><span class="pre">syside.Url</span></a></span></span><a href="#syside.Url.set_encoded_path" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">set_encoded_query</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="#syside.Url" class="reference internal" title="syside.Url"><span class="pre">syside.Url</span></a></span></span><a href="#syside.Url.set_encoded_query" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">set_encoded_user</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="#syside.Url" class="reference internal" title="syside.Url"><span class="pre">syside.Url</span></a></span></span><a href="#syside.Url.set_encoded_user" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">set_encoded_userinfo</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="#syside.Url" class="reference internal" title="syside.Url"><span class="pre">syside.Url</span></a></span></span><a href="#syside.Url.set_encoded_userinfo" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">set_fragment</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="#syside.Url" class="reference internal" title="syside.Url"><span class="pre">syside.Url</span></a></span></span><a href="#syside.Url.set_fragment" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">set_host</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="#syside.Url" class="reference internal" title="syside.Url"><span class="pre">syside.Url</span></a></span></span><a href="#syside.Url.set_host" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">set_host_address</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="#syside.Url" class="reference internal" title="syside.Url"><span class="pre">syside.Url</span></a></span></span><a href="#syside.Url.set_host_address" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">set_host_ipv4</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/IPv4Address.md" class="reference internal" title="syside.IPv4Address"><span class="pre">syside.IPv4Address</span></a></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="#syside.Url" class="reference internal" title="syside.Url"><span class="pre">syside.Url</span></a></span></span><a href="#syside.Url.set_host_ipv4" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">set_host_ipv6</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside/IPv6Address.md" class="reference internal" title="syside.IPv6Address"><span class="pre">syside.IPv6Address</span></a></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="#syside.Url" class="reference internal" title="syside.Url"><span class="pre">syside.Url</span></a></span></span><a href="#syside.Url.set_host_ipv6" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">set_host_ipvfuture</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="#syside.Url" class="reference internal" title="syside.Url"><span class="pre">syside.Url</span></a></span></span><a href="#syside.Url.set_host_ipvfuture" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">set_host_name</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="#syside.Url" class="reference internal" title="syside.Url"><span class="pre">syside.Url</span></a></span></span><a href="#syside.Url.set_host_name" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">set_password</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="#syside.Url" class="reference internal" title="syside.Url"><span class="pre">syside.Url</span></a></span></span><a href="#syside.Url.set_password" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">set_path</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="#syside.Url" class="reference internal" title="syside.Url"><span class="pre">syside.Url</span></a></span></span><a href="#syside.Url.set_path" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">set_port</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="#syside.Url" class="reference internal" title="syside.Url"><span class="pre">syside.Url</span></a></span></span><a href="#syside.Url.set_port" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">set_port_number</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">int</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="#syside.Url" class="reference internal" title="syside.Url"><span class="pre">syside.Url</span></a></span></span><a href="#syside.Url.set_port_number" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">set_query</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="#syside.Url" class="reference internal" title="syside.Url"><span class="pre">syside.Url</span></a></span></span><a href="#syside.Url.set_query" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">set_scheme</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="#syside.Url" class="reference internal" title="syside.Url"><span class="pre">syside.Url</span></a></span></span><a href="#syside.Url.set_scheme" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">set_scheme_id</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside.Scheme"><span class="pre">syside.Scheme</span></a></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="#syside.Url" class="reference internal" title="syside.Url"><span class="pre">syside.Url</span></a></span></span><a href="#syside.Url.set_scheme_id" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">set_user</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="#syside.Url" class="reference internal" title="syside.Url"><span class="pre">syside.Url</span></a></span></span><a href="#syside.Url.set_user" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sig-name descname"><span class="pre">set_userinfo</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="o"><span class="pre">/</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="#syside.Url" class="reference internal" title="syside.Url"><span class="pre">syside.Url</span></a></span></span><a href="#syside.Url.set_userinfo" class="headerlink" title="Link to this definition"><span class="nerd-font"></span></a>  

<span class="sd-summary-text"><span class="nerd-font"></span> Used in</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- <a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside"><span class="pre"><code class="sourceCode python">syside</code></span></a>

  - <a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside.decode_path"><span class="pre"><code class="sourceCode python">decode_path</code></span></a>

  - <a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside.make_file_url"><span class="pre"><code class="sourceCode python">make_file_url</code></span></a>

- <a href="/python/v0.8.4/syside/BasicDocument.md" class="reference internal" title="syside.BasicDocument"><span class="pre"><code class="sourceCode python">syside.BasicDocument</code></span></a>

  - <a href="/python/v0.8.4/syside/BasicDocument.md" class="reference internal" title="syside.BasicDocument.url"><span class="pre"><code class="sourceCode python">url</code></span></a>

- <a href="/python/v0.8.4/syside/DiagnosticContext.md" class="reference internal" title="syside.DiagnosticContext"><span class="pre"><code class="sourceCode python">syside.DiagnosticContext</code></span></a>

  - <a href="/python/v0.8.4/syside/DiagnosticContext.md" class="reference internal" title="syside.DiagnosticContext.__init__"><span class="pre"><code class="sourceCode python"><span class="fu">__init__</span></code></span></a>

  - <a href="/python/v0.8.4/syside/DiagnosticContext.md" class="reference internal" title="syside.DiagnosticContext.related_sources"><span class="pre"><code class="sourceCode python">related_sources</code></span></a>

- <a href="/python/v0.8.4/syside/DiagnosticRelatedInformation.md" class="reference internal" title="syside.DiagnosticRelatedInformation"><span class="pre"><code class="sourceCode python">syside.DiagnosticRelatedInformation</code></span></a>

  - <a href="/python/v0.8.4/syside/DiagnosticRelatedInformation.md" class="reference internal" title="syside.DiagnosticRelatedInformation.__init__"><span class="pre"><code class="sourceCode python"><span class="fu">__init__</span></code></span></a>

  - <a href="/python/v0.8.4/syside/DiagnosticRelatedInformation.md" class="reference internal" title="syside.DiagnosticRelatedInformation.uri"><span class="pre"><code class="sourceCode python">uri</code></span></a>

- <a href="/python/v0.8.4/syside/Document.md" class="reference internal" title="syside.Document"><span class="pre"><code class="sourceCode python">syside.Document</code></span></a>

  - <a href="/python/v0.8.4/syside/Document.md" class="reference internal" title="syside.Document.create_mt"><span class="pre"><code class="sourceCode python">create_mt</code></span></a>

  - <a href="/python/v0.8.4/syside/Document.md" class="reference internal" title="syside.Document.create_st"><span class="pre"><code class="sourceCode python">create_st</code></span></a>

- <a href="/python/v0.8.4/syside/DocumentOptions.md" class="reference internal" title="syside.DocumentOptions"><span class="pre"><code class="sourceCode python">syside.DocumentOptions</code></span></a>

  - <a href="/python/v0.8.4/syside/DocumentOptions.md" class="reference internal" title="syside.DocumentOptions.__init__"><span class="pre"><code class="sourceCode python"><span class="fu">__init__</span></code></span></a>

  - <a href="/python/v0.8.4/syside/DocumentOptions.md" class="reference internal" title="syside.DocumentOptions.url"><span class="pre"><code class="sourceCode python">url</code></span></a>

- <a href="/python/v0.8.4/syside/IOSchedule.md" class="reference internal" title="syside.IOSchedule"><span class="pre"><code class="sourceCode python">syside.IOSchedule</code></span></a>

  - <a href="/python/v0.8.4/syside/IOSchedule.md" class="reference internal" title="syside.IOSchedule.add_source"><span class="pre"><code class="sourceCode python">add_source</code></span></a>

- <a href="/python/v0.8.4/syside/TextDocument.md" class="reference internal" title="syside.TextDocument"><span class="pre"><code class="sourceCode python">syside.TextDocument</code></span></a>

  - <a href="/python/v0.8.4/syside/TextDocument.md" class="reference internal" title="syside.TextDocument.create_mt"><span class="pre"><code class="sourceCode python">create_mt</code></span></a>

  - <a href="/python/v0.8.4/syside/TextDocument.md" class="reference internal" title="syside.TextDocument.create_st"><span class="pre"><code class="sourceCode python">create_st</code></span></a>

  - <a href="/python/v0.8.4/syside/TextDocument.md" class="reference internal" title="syside.TextDocument.url"><span class="pre"><code class="sourceCode python">url</code></span></a>

- <a href="/python/v0.8.4/syside/TextDocumentData.md" class="reference internal" title="syside.TextDocumentData"><span class="pre"><code class="sourceCode python">syside.TextDocumentData</code></span></a>

  - <a href="/python/v0.8.4/syside/TextDocumentData.md" class="reference internal" title="syside.TextDocumentData.__init__"><span class="pre"><code class="sourceCode python"><span class="fu">__init__</span></code></span></a>

  - <a href="/python/v0.8.4/syside/TextDocumentData.md" class="reference internal" title="syside.TextDocumentData.url"><span class="pre"><code class="sourceCode python">url</code></span></a>

- <a href="/python/v0.8.4/syside/TextDocuments.md" class="reference internal" title="syside.TextDocuments"><span class="pre"><code class="sourceCode python">syside.TextDocuments</code></span></a>

  - <a href="/python/v0.8.4/syside/TextDocuments.md" class="reference internal" title="syside.TextDocuments.__getitem__"><span class="pre"><code class="sourceCode python"><span class="fu">__getitem__</span></code></span></a>

  - <a href="/python/v0.8.4/syside/TextDocuments.md" class="reference internal" title="syside.TextDocuments.change_content"><span class="pre"><code class="sourceCode python">change_content</code></span></a>

  - <a href="/python/v0.8.4/syside/TextDocuments.md" class="reference internal" title="syside.TextDocuments.close"><span class="pre"><code class="sourceCode python">close</code></span></a>

  - <a href="/python/v0.8.4/syside/TextDocuments.md" class="reference internal" title="syside.TextDocuments.find_or_open"><span class="pre"><code class="sourceCode python">find_or_open</code></span></a>

  - <a href="/python/v0.8.4/syside/TextDocuments.md" class="reference internal" title="syside.TextDocuments.move"><span class="pre"><code class="sourceCode python">move</code></span></a>

  - <a href="/python/v0.8.4/syside/TextDocuments.md" class="reference internal" title="syside.TextDocuments.open"><span class="pre"><code class="sourceCode python"><span class="bu">open</span></code></span></a>

  - <a href="/python/v0.8.4/syside/TextDocuments.md" class="reference internal" title="syside.TextDocuments.save"><span class="pre"><code class="sourceCode python">save</code></span></a>

  - <a href="/python/v0.8.4/syside/TextDocuments.md" class="reference internal" title="syside.TextDocuments.visit"><span class="pre"><code class="sourceCode python">visit</code></span></a>

  - <a href="/python/v0.8.4/syside/TextDocuments.md" class="reference internal" title="syside.TextDocuments.visit_urls"><span class="pre"><code class="sourceCode python">visit_urls</code></span></a>

  - <a href="/python/v0.8.4/syside/TextDocuments.md" class="reference internal" title="syside.TextDocuments.will_save"><span class="pre"><code class="sourceCode python">will_save</code></span></a>

  - <a href="/python/v0.8.4/syside/TextDocuments.md" class="reference internal" title="syside.TextDocuments.will_save_wait_until"><span class="pre"><code class="sourceCode python">will_save_wait_until</code></span></a>

- <a href="#syside.Url" class="reference internal" title="syside.Url"><span class="pre"><code class="sourceCode python">syside.Url</code></span></a>

  - <a href="#syside.Url.__copy__" class="reference internal" title="syside.Url.__copy__"><span class="pre"><code class="sourceCode python">__copy__</code></span></a>

  - <a href="#syside.Url.__deepcopy__" class="reference internal" title="syside.Url.__deepcopy__"><span class="pre"><code class="sourceCode python">__deepcopy__</code></span></a>

  - <a href="#syside.Url.normalize" class="reference internal" title="syside.Url.normalize"><span class="pre"><code class="sourceCode python">normalize</code></span></a>

  - <a href="#syside.Url.normalize_authority" class="reference internal" title="syside.Url.normalize_authority"><span class="pre"><code class="sourceCode python">normalize_authority</code></span></a>

  - <a href="#syside.Url.normalize_fragment" class="reference internal" title="syside.Url.normalize_fragment"><span class="pre"><code class="sourceCode python">normalize_fragment</code></span></a>

  - <a href="#syside.Url.normalize_path" class="reference internal" title="syside.Url.normalize_path"><span class="pre"><code class="sourceCode python">normalize_path</code></span></a>

  - <a href="#syside.Url.normalize_query" class="reference internal" title="syside.Url.normalize_query"><span class="pre"><code class="sourceCode python">normalize_query</code></span></a>

  - <a href="#syside.Url.normalize_scheme" class="reference internal" title="syside.Url.normalize_scheme"><span class="pre"><code class="sourceCode python">normalize_scheme</code></span></a>

  - <a href="#syside.Url.remove_authority" class="reference internal" title="syside.Url.remove_authority"><span class="pre"><code class="sourceCode python">remove_authority</code></span></a>

  - <a href="#syside.Url.remove_fragment" class="reference internal" title="syside.Url.remove_fragment"><span class="pre"><code class="sourceCode python">remove_fragment</code></span></a>

  - <a href="#syside.Url.remove_origin" class="reference internal" title="syside.Url.remove_origin"><span class="pre"><code class="sourceCode python">remove_origin</code></span></a>

  - <a href="#syside.Url.remove_password" class="reference internal" title="syside.Url.remove_password"><span class="pre"><code class="sourceCode python">remove_password</code></span></a>

  - <a href="#syside.Url.remove_port" class="reference internal" title="syside.Url.remove_port"><span class="pre"><code class="sourceCode python">remove_port</code></span></a>

  - <a href="#syside.Url.remove_query" class="reference internal" title="syside.Url.remove_query"><span class="pre"><code class="sourceCode python">remove_query</code></span></a>

  - <a href="#syside.Url.remove_scheme" class="reference internal" title="syside.Url.remove_scheme"><span class="pre"><code class="sourceCode python">remove_scheme</code></span></a>

  - <a href="#syside.Url.remove_userinfo" class="reference internal" title="syside.Url.remove_userinfo"><span class="pre"><code class="sourceCode python">remove_userinfo</code></span></a>

  - <a href="#syside.Url.set_encoded_authority" class="reference internal" title="syside.Url.set_encoded_authority"><span class="pre"><code class="sourceCode python">set_encoded_authority</code></span></a>

  - <a href="#syside.Url.set_encoded_fragment" class="reference internal" title="syside.Url.set_encoded_fragment"><span class="pre"><code class="sourceCode python">set_encoded_fragment</code></span></a>

  - <a href="#syside.Url.set_encoded_host" class="reference internal" title="syside.Url.set_encoded_host"><span class="pre"><code class="sourceCode python">set_encoded_host</code></span></a>

  - <a href="#syside.Url.set_encoded_host_address" class="reference internal" title="syside.Url.set_encoded_host_address"><span class="pre"><code class="sourceCode python">set_encoded_host_address</code></span></a>

  - <a href="#syside.Url.set_encoded_host_name" class="reference internal" title="syside.Url.set_encoded_host_name"><span class="pre"><code class="sourceCode python">set_encoded_host_name</code></span></a>

  - <a href="#syside.Url.set_encoded_password" class="reference internal" title="syside.Url.set_encoded_password"><span class="pre"><code class="sourceCode python">set_encoded_password</code></span></a>

  - <a href="#syside.Url.set_encoded_path" class="reference internal" title="syside.Url.set_encoded_path"><span class="pre"><code class="sourceCode python">set_encoded_path</code></span></a>

  - <a href="#syside.Url.set_encoded_query" class="reference internal" title="syside.Url.set_encoded_query"><span class="pre"><code class="sourceCode python">set_encoded_query</code></span></a>

  - <a href="#syside.Url.set_encoded_user" class="reference internal" title="syside.Url.set_encoded_user"><span class="pre"><code class="sourceCode python">set_encoded_user</code></span></a>

  - <a href="#syside.Url.set_encoded_userinfo" class="reference internal" title="syside.Url.set_encoded_userinfo"><span class="pre"><code class="sourceCode python">set_encoded_userinfo</code></span></a>

  - <a href="#syside.Url.set_fragment" class="reference internal" title="syside.Url.set_fragment"><span class="pre"><code class="sourceCode python">set_fragment</code></span></a>

  - <a href="#syside.Url.set_host" class="reference internal" title="syside.Url.set_host"><span class="pre"><code class="sourceCode python">set_host</code></span></a>

  - <a href="#syside.Url.set_host_address" class="reference internal" title="syside.Url.set_host_address"><span class="pre"><code class="sourceCode python">set_host_address</code></span></a>

  - <a href="#syside.Url.set_host_ipv4" class="reference internal" title="syside.Url.set_host_ipv4"><span class="pre"><code class="sourceCode python">set_host_ipv4</code></span></a>

  - <a href="#syside.Url.set_host_ipv6" class="reference internal" title="syside.Url.set_host_ipv6"><span class="pre"><code class="sourceCode python">set_host_ipv6</code></span></a>

  - <a href="#syside.Url.set_host_ipvfuture" class="reference internal" title="syside.Url.set_host_ipvfuture"><span class="pre"><code class="sourceCode python">set_host_ipvfuture</code></span></a>

  - <a href="#syside.Url.set_host_name" class="reference internal" title="syside.Url.set_host_name"><span class="pre"><code class="sourceCode python">set_host_name</code></span></a>

  - <a href="#syside.Url.set_password" class="reference internal" title="syside.Url.set_password"><span class="pre"><code class="sourceCode python">set_password</code></span></a>

  - <a href="#syside.Url.set_path" class="reference internal" title="syside.Url.set_path"><span class="pre"><code class="sourceCode python">set_path</code></span></a>

  - <a href="#syside.Url.set_port" class="reference internal" title="syside.Url.set_port"><span class="pre"><code class="sourceCode python">set_port</code></span></a>

  - <a href="#syside.Url.set_port_number" class="reference internal" title="syside.Url.set_port_number"><span class="pre"><code class="sourceCode python">set_port_number</code></span></a>

  - <a href="#syside.Url.set_query" class="reference internal" title="syside.Url.set_query"><span class="pre"><code class="sourceCode python">set_query</code></span></a>

  - <a href="#syside.Url.set_scheme" class="reference internal" title="syside.Url.set_scheme"><span class="pre"><code class="sourceCode python">set_scheme</code></span></a>

  - <a href="#syside.Url.set_scheme_id" class="reference internal" title="syside.Url.set_scheme_id"><span class="pre"><code class="sourceCode python">set_scheme_id</code></span></a>

  - <a href="#syside.Url.set_user" class="reference internal" title="syside.Url.set_user"><span class="pre"><code class="sourceCode python">set_user</code></span></a>

  - <a href="#syside.Url.set_userinfo" class="reference internal" title="syside.Url.set_userinfo"><span class="pre"><code class="sourceCode python">set_userinfo</code></span></a>

- <a href="/python/v0.8.4/syside/json//README.md" class="reference internal" title="syside.json"><span class="pre"><code class="sourceCode python">syside.json</code></span></a>

  - <a href="/python/v0.8.4/syside/json//README.md" class="reference internal" title="syside.json.JsonSourceNew"><span class="pre"><code class="sourceCode python">JsonSourceNew</code></span></a>

  - <a href="/python/v0.8.4/syside/json//README.md" class="reference internal" title="syside.json.loads"><span class="pre"><code class="sourceCode python">loads</code></span></a>

</div>

</div>
