<div id="low-level-api" class="section">

# Low-Level API<a href="#low-level-api" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

Syside splits models into chunks, or <a href="/python/v0.8.4/syside/Document.md" class="reference internal" title="syside.Document"><span class="pre"><code class="sourceCode python">Documents</code></span></a>, each corresponding to a single source file. While this is partly to support editor applications (LSP) that must work on a per-source-file basis, it also provides a sensible model splitting for multithreading. To support multithreading in editor applications, each <a href="/python/v0.8.4/syside/Document.md" class="reference internal" title="syside.Document"><span class="pre"><code class="sourceCode python">Document</code></span></a> and <a href="/python/v0.8.4/syside/TextDocument.md" class="reference internal" title="syside.TextDocument"><span class="pre"><code class="sourceCode python">TextDocument</code></span></a> are protected by a mutex using <a href="/python/v0.8.4/syside/SharedMutex.md" class="reference internal" title="syside.SharedMutex"><span class="pre"><code class="sourceCode python">SharedMutex</code></span></a>. Python API has context-manager wrapper with automatic acquire and release:

<div class="highlight-py notranslate">

<div class="highlight">

    with mutex.lock() as document:
        # mutex acquired here
        ...

</div>

</div>

Internally, it is a type-erased wrapper to a <a href="https://en.cppreference.com/w/cpp/thread/shared_mutex.html" class="reference external" target="_blank">shared mutex-like object</a> that provides shared accesses for read-only operations, and unique accesses for write operations. Type-erasure allows identical interfaces for both single-threaded (noop mutex), and multi-threaded (shared mutex) objects, which may prove beneficial if in the future builds for free-threaded Python were offered.

Unfortunately, Python does not have read-only semantics, thus <a href="/python/v0.8.4/syside/SharedMutex.md" class="reference internal" title="syside.SharedMutex"><span class="pre"><code class="sourceCode python">SharedMutex</code></span></a> is equivalent to a regular mutex – all accesses are unique, unless it is a noop mutex, e.g. from <a href="/python/v0.8.4/syside/Document.md" class="reference internal" title="syside.Document.parse_string_st"><span class="pre"><code class="sourceCode python">parse_string_st</code></span></a>.

Additionally, each <a href="/python/v0.8.4/syside/Document.md" class="reference internal" title="syside.Document"><span class="pre"><code class="sourceCode python">Document</code></span></a> acts as a memory resource for its owned nodes (elements) – this improves memory usage, and enables incredibly useful and efficient <a href="/python/v0.8.4/syside/Document.md" class="reference internal" title="syside.Document.nodes"><span class="pre"><code class="sourceCode python">nodes</code></span></a> and <a href="/python/v0.8.4/syside/Document.md" class="reference internal" title="syside.Document.all_nodes"><span class="pre"><code class="sourceCode python">all_nodes</code></span></a> methods. However, this does prevent moving nodes from one document to another, but that is a small price to pay for the performance benefits.

<div id="pipelines" class="section">

## Pipelines<a href="#pipelines" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

Underneath everything, <a href="/python/v0.8.4/syside/Document.md" class="reference internal" title="syside.Document"><span class="pre"><code class="sourceCode python">Documents</code></span></a> in Syside are built by a <a href="/python/v0.8.4/syside/Pipeline.md" class="reference internal" title="syside.Pipeline"><span class="pre"><code class="sourceCode python">Pipeline</code></span></a>. At a high level, this is a sequence of

<div class="align-center" align="center">

<img src="data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iZ3JhcGh2aXoiIHN0eWxlPSJ3aWR0aDogMjMuNDM3NXJlbTtoZWlnaHQ6IDIuNzVyZW07IiB2aWV3Ym94PSIwLjAwIDAuMDAgMzc1LjAwIDQ0LjAwIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPgo8ZyBjbGFzcz0iZ3JhcGgiIGlkPSJncmFwaDAiIHRyYW5zZm9ybT0ic2NhbGUoMSAxKSByb3RhdGUoMCkgdHJhbnNsYXRlKDQgNDApIj4KPHRpdGxlPiUzPC90aXRsZT4KPGcgY2xhc3M9Im5vZGUiIGlkPSJub2RlMSI+Cjx0aXRsZT5jcmVhdGUgcGlwZWxpbmUgKHJldXNhYmxlKTwvdGl0bGU+Cjxwb2x5Z29uIHBvaW50cz0iMTY2LC0zNiAwLC0zNiAwLDAgMTY2LDAgMTY2LC0zNiIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtYmctY29sb3IpO3N0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1mZy1jb2xvcik7Ij48L3BvbHlnb24+Cjx0ZXh0IGZvbnQtZmFtaWx5PSJMZXhlbmQiIGZvbnQtc2l6ZT0iMTIuMDAiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1jb2RlLWZnLWNvbG9yKTsiIHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjgzIiB5PSItMTQuMiI+Y3JlYXRlIHBpcGVsaW5lIChyZXVzYWJsZSk8L3RleHQ+CjwvZz4KPGcgY2xhc3M9Im5vZGUiIGlkPSJub2RlMiI+Cjx0aXRsZT5zY2hlZHVsZTwvdGl0bGU+Cjxwb2x5Z29uIHBvaW50cz0iMjY5LC0zNiAyMDIsLTM2IDIwMiwwIDI2OSwwIDI2OSwtMzYiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1ncmFwaHZpei1ub2RlLWJnLWNvbG9yKTtzdHJva2U6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtZmctY29sb3IpOyI+PC9wb2x5Z29uPgo8dGV4dCBmb250LWZhbWlseT0iTGV4ZW5kIiBmb250LXNpemU9IjEyLjAwIiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtY29kZS1mZy1jb2xvcik7IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSIyMzUuNSIgeT0iLTE0LjIiPnNjaGVkdWxlPC90ZXh0Pgo8L2c+CjxnIGNsYXNzPSJlZGdlIiBpZD0iZWRnZTEiPgo8dGl0bGU+Y3JlYXRlIHBpcGVsaW5lIChyZXVzYWJsZSktJmd0O3NjaGVkdWxlPC90aXRsZT4KPHBhdGggZD0iTTE2Ni4zLC0xOEMxNzUuMDgsLTE4IDE4My43MywtMTggMTkxLjc2LC0xOCIgZmlsbD0ibm9uZSIgc3R5bGU9InN0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotZWRnZS1jb2xvcik7IiAvPgo8cG9seWdvbiBwb2ludHM9IjE5MS45NCwtMjEuNSAyMDEuOTQsLTE4IDE5MS45NCwtMTQuNSAxOTEuOTQsLTIxLjUiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1ncmFwaHZpei1lZGdlLWNvbG9yKTtzdHJva2U6IHZhcigtLW1kLWdyYXBodml6LWVkZ2UtY29sb3IpOyI+PC9wb2x5Z29uPgo8L2c+CjxnIGNsYXNzPSJub2RlIiBpZD0ibm9kZTMiPgo8dGl0bGU+ZXhlY3V0ZTwvdGl0bGU+Cjxwb2x5Z29uIHBvaW50cz0iMzY3LC0zNiAzMDUsLTM2IDMwNSwwIDM2NywwIDM2NywtMzYiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1ncmFwaHZpei1ub2RlLWJnLWNvbG9yKTtzdHJva2U6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtZmctY29sb3IpOyI+PC9wb2x5Z29uPgo8dGV4dCBmb250LWZhbWlseT0iTGV4ZW5kIiBmb250LXNpemU9IjEyLjAwIiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtY29kZS1mZy1jb2xvcik7IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSIzMzYiIHk9Ii0xNC4yIj5leGVjdXRlPC90ZXh0Pgo8L2c+CjxnIGNsYXNzPSJlZGdlIiBpZD0iZWRnZTIiPgo8dGl0bGU+c2NoZWR1bGUtJmd0O2V4ZWN1dGU8L3RpdGxlPgo8cGF0aCBkPSJNMjY5LjAzLC0xOEMyNzcuMjMsLTE4IDI4Ni4xNCwtMTggMjk0LjY4LC0xOCIgZmlsbD0ibm9uZSIgc3R5bGU9InN0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotZWRnZS1jb2xvcik7IiAvPgo8cG9seWdvbiBwb2ludHM9IjI5NC44NCwtMjEuNSAzMDQuODQsLTE4IDI5NC44NCwtMTQuNSAyOTQuODQsLTIxLjUiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1ncmFwaHZpei1lZGdlLWNvbG9yKTtzdHJva2U6IHZhcigtLW1kLWdyYXBodml6LWVkZ2UtY29sb3IpOyI+PC9wb2x5Z29uPgo8L2c+CjwvZz4KPC9zdmc+" class="graphviz" />

</div>

A <a href="/python/v0.8.4/syside/Pipeline.md" class="reference internal" title="syside.Pipeline"><span class="pre"><code class="sourceCode python">Pipeline</code></span></a> is constructed with

<div class="highlight-py notranslate">

<div class="highlight">

    pipeline: syside.Pipeline = syside.make_pipeline(
        syside.PipelineOptions(lib=None, static_index=None)
    )

</div>

</div>

<div class="admonition note">

Note

Current Python API is limited, and does not allow additional validation rules in the pipeline.

</div>

Constructed <a href="/python/v0.8.4/syside/Pipeline.md" class="reference internal" title="syside.Pipeline"><span class="pre"><code class="sourceCode python">Pipelines</code></span></a> are used to create build <a href="/python/v0.8.4/syside/Schedule.md" class="reference internal" title="syside.Schedule"><span class="pre"><code class="sourceCode python">Schedules</code></span></a> that are completed on an <a href="/python/v0.8.4/syside/Executor.md" class="reference internal" title="syside.Executor"><span class="pre"><code class="sourceCode python">Executor</code></span></a> (pool of worker threads):

<div class="highlight-py notranslate">

<div class="highlight">

    schedule: syside.Schedule = pipeline.schedule(
        documents,
        options=syside.ScheduleOptions(
            validation_timing=syside.ValidationTiming.Manual
        ),
        invalidated=[],
    )
    result: syside.ExecutionResult = syside.get_default_executor().run(schedule)

</div>

</div>

<div class="admonition note">

Note

<a href="/python/v0.8.4/syside/Executor.md" class="reference internal" title="syside.Executor.run"><span class="pre"><code class="sourceCode python">Executor.run</code></span></a> consumes the passed-in <span class="pre">`schedule`</span> – attempting to access its attributes afterwards will raise a <span class="pre">`RuntimeError`</span>. Instead, a cleared <a href="/python/v0.8.4/syside/Schedule.md" class="reference internal" title="syside.Schedule"><span class="pre"><code class="sourceCode python">Schedule</code></span></a> is returned in <a href="/python/v0.8.4/syside/ExecutionResult.md" class="reference internal" title="syside.ExecutionResult.schedule"><span class="pre"><code class="sourceCode python">result.schedule</code></span></a>. This should be made reusable for scheduling with fewer allocations in a future release.

</div>

<div class="admonition note">

Note

<a href="/python/v0.8.4/syside/Executor.md" class="reference internal" title="syside.Executor"><span class="pre"><code class="sourceCode python">Executors</code></span></a> are thread-pools underneath, therefore due the runtime cost of starting new threads, they should be reused as much as possible. Syside provides a default executor with <a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside.get_default_executor"><span class="pre"><code class="sourceCode python">syside.get_default_executor()</code></span></a>.

</div>

Internally, schedules are a sequence of build stages, some of which can run in parallel. Parallelism is an implementation detail, and will use worker threads from <a href="/python/v0.8.4/syside/Executor.md" class="reference internal" title="syside.Executor"><span class="pre"><code class="sourceCode python">Executor</code></span></a>.

<div class="align-center" align="center">

<img src="data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iZ3JhcGh2aXoiIHN0eWxlPSJ3aWR0aDogMzQuODc1cmVtO2hlaWdodDogMi43NXJlbTsiIHZpZXdib3g9IjAuMDAgMC4wMCA1NTguMDAgNDQuMDAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxnIGNsYXNzPSJncmFwaCIgaWQ9ImdyYXBoMCIgdHJhbnNmb3JtPSJzY2FsZSgxIDEpIHJvdGF0ZSgwKSB0cmFuc2xhdGUoNCA0MCkiPgo8dGl0bGU+JTM8L3RpdGxlPgo8ZyBjbGFzcz0ibm9kZSIgaWQ9Im5vZGUxIj4KPHRpdGxlPlBhcnNlPC90aXRsZT4KPHBvbHlnb24gcG9pbnRzPSI1NCwtMzYgMCwtMzYgMCwwIDU0LDAgNTQsLTM2IiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1iZy1jb2xvcik7c3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1ub2RlLWZnLWNvbG9yKTsiPjwvcG9seWdvbj4KPHRleHQgZm9udC1mYW1pbHk9IkxleGVuZCIgZm9udC1zaXplPSIxMi4wMCIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWNvZGUtZmctY29sb3IpOyIgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iMjciIHk9Ii0xNC4yIj5QYXJzZTwvdGV4dD4KPC9nPgo8ZyBjbGFzcz0ibm9kZSIgaWQ9Im5vZGUyIj4KPHRpdGxlPkFTVDwvdGl0bGU+Cjxwb2x5Z29uIHBvaW50cz0iMTQ0LC0zNiA5MCwtMzYgOTAsMCAxNDQsMCAxNDQsLTM2IiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1iZy1jb2xvcik7c3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1ub2RlLWZnLWNvbG9yKTsiPjwvcG9seWdvbj4KPHRleHQgZm9udC1mYW1pbHk9IkxleGVuZCIgZm9udC1zaXplPSIxMi4wMCIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWNvZGUtZmctY29sb3IpOyIgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iMTE3IiB5PSItMTQuMiI+QVNUPC90ZXh0Pgo8L2c+CjxnIGNsYXNzPSJlZGdlIiBpZD0iZWRnZTEiPgo8dGl0bGU+UGFyc2UtJmd0O0FTVDwvdGl0bGU+CjxwYXRoIGQ9Ik01NC40LC0xOEM2Mi4zOSwtMTggNzEuMzEsLTE4IDc5LjgyLC0xOCIgZmlsbD0ibm9uZSIgc3R5bGU9InN0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotZWRnZS1jb2xvcik7IiAvPgo8cG9seWdvbiBwb2ludHM9Ijc5LjkyLC0yMS41IDg5LjkyLC0xOCA3OS45MiwtMTQuNSA3OS45MiwtMjEuNSIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWdyYXBodml6LWVkZ2UtY29sb3IpO3N0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotZWRnZS1jb2xvcik7Ij48L3BvbHlnb24+CjwvZz4KPGcgY2xhc3M9Im5vZGUiIGlkPSJub2RlMyI+Cjx0aXRsZT5JbmRleGluZzwvdGl0bGU+Cjxwb2x5Z29uIHBvaW50cz0iMjQ5LC0zNiAxODAsLTM2IDE4MCwwIDI0OSwwIDI0OSwtMzYiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1ncmFwaHZpei1ub2RlLWJnLWNvbG9yKTtzdHJva2U6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtZmctY29sb3IpOyI+PC9wb2x5Z29uPgo8dGV4dCBmb250LWZhbWlseT0iTGV4ZW5kIiBmb250LXNpemU9IjEyLjAwIiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtY29kZS1mZy1jb2xvcik7IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSIyMTQuNSIgeT0iLTE0LjIiPkluZGV4aW5nPC90ZXh0Pgo8L2c+CjxnIGNsYXNzPSJlZGdlIiBpZD0iZWRnZTIiPgo8dGl0bGU+QVNULSZndDtJbmRleGluZzwvdGl0bGU+CjxwYXRoIGQ9Ik0xNDQuMSwtMThDMTUyLjAzLC0xOCAxNjAuOTksLTE4IDE2OS43NiwtMTgiIGZpbGw9Im5vbmUiIHN0eWxlPSJzdHJva2U6IHZhcigtLW1kLWdyYXBodml6LWVkZ2UtY29sb3IpOyIgLz4KPHBvbHlnb24gcG9pbnRzPSIxNjkuOSwtMjEuNSAxNzkuOSwtMTggMTY5LjksLTE0LjUgMTY5LjksLTIxLjUiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1ncmFwaHZpei1lZGdlLWNvbG9yKTtzdHJva2U6IHZhcigtLW1kLWdyYXBodml6LWVkZ2UtY29sb3IpOyI+PC9wb2x5Z29uPgo8L2c+CjxnIGNsYXNzPSJub2RlIiBpZD0ibm9kZTQiPgo8dGl0bGU+Q2FjaGluZzwvdGl0bGU+Cjxwb2x5Z29uIHBvaW50cz0iMzQ4LC0zNiAyODUsLTM2IDI4NSwwIDM0OCwwIDM0OCwtMzYiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1ncmFwaHZpei1ub2RlLWJnLWNvbG9yKTtzdHJva2U6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtZmctY29sb3IpOyI+PC9wb2x5Z29uPgo8dGV4dCBmb250LWZhbWlseT0iTGV4ZW5kIiBmb250LXNpemU9IjEyLjAwIiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtY29kZS1mZy1jb2xvcik7IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSIzMTYuNSIgeT0iLTE0LjIiPkNhY2hpbmc8L3RleHQ+CjwvZz4KPGcgY2xhc3M9ImVkZ2UiIGlkPSJlZGdlMyI+Cjx0aXRsZT5JbmRleGluZy0mZ3Q7Q2FjaGluZzwvdGl0bGU+CjxwYXRoIGQ9Ik0yNDkuMDgsLTE4QzI1Ny4zMSwtMTggMjY2LjIsLTE4IDI3NC43MywtMTgiIGZpbGw9Im5vbmUiIHN0eWxlPSJzdHJva2U6IHZhcigtLW1kLWdyYXBodml6LWVkZ2UtY29sb3IpOyIgLz4KPHBvbHlnb24gcG9pbnRzPSIyNzQuODcsLTIxLjUgMjg0Ljg3LC0xOCAyNzQuODcsLTE0LjUgMjc0Ljg3LC0yMS41IiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtZ3JhcGh2aXotZWRnZS1jb2xvcik7c3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1lZGdlLWNvbG9yKTsiPjwvcG9seWdvbj4KPC9nPgo8ZyBjbGFzcz0ibm9kZSIgaWQ9Im5vZGU1Ij4KPHRpdGxlPlNlbWE8L3RpdGxlPgo8cG9seWdvbiBwb2ludHM9IjQzOCwtMzYgMzg0LC0zNiAzODQsMCA0MzgsMCA0MzgsLTM2IiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtZ3JhcGh2aXotbm9kZS1iZy1jb2xvcik7c3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1ub2RlLWZnLWNvbG9yKTsiPjwvcG9seWdvbj4KPHRleHQgZm9udC1mYW1pbHk9IkxleGVuZCIgZm9udC1zaXplPSIxMi4wMCIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWNvZGUtZmctY29sb3IpOyIgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iNDExIiB5PSItMTQuMiI+U2VtYTwvdGV4dD4KPC9nPgo8ZyBjbGFzcz0iZWRnZSIgaWQ9ImVkZ2U0Ij4KPHRpdGxlPkNhY2hpbmctJmd0O1NlbWE8L3RpdGxlPgo8cGF0aCBkPSJNMzQ4LjA0LC0xOEMzNTYuMjcsLTE4IDM2NS4yNiwtMTggMzczLjc3LC0xOCIgZmlsbD0ibm9uZSIgc3R5bGU9InN0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotZWRnZS1jb2xvcik7IiAvPgo8cG9seWdvbiBwb2ludHM9IjM3My44MywtMjEuNSAzODMuODMsLTE4IDM3My44MywtMTQuNSAzNzMuODMsLTIxLjUiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1ncmFwaHZpei1lZGdlLWNvbG9yKTtzdHJva2U6IHZhcigtLW1kLWdyYXBodml6LWVkZ2UtY29sb3IpOyI+PC9wb2x5Z29uPgo8L2c+CjxnIGNsYXNzPSJub2RlIiBpZD0ibm9kZTYiPgo8dGl0bGU+VmFsaWRhdGlvbjwvdGl0bGU+Cjxwb2x5Z29uIHBvaW50cz0iNTUwLC0zNiA0NzQsLTM2IDQ3NCwwIDU1MCwwIDU1MCwtMzYiIHN0eWxlPSJmaWxsOiB2YXIoLS1tZC1ncmFwaHZpei1ub2RlLWJnLWNvbG9yKTtzdHJva2U6IHZhcigtLW1kLWdyYXBodml6LW5vZGUtZmctY29sb3IpOyI+PC9wb2x5Z29uPgo8dGV4dCBmb250LWZhbWlseT0iTGV4ZW5kIiBmb250LXNpemU9IjEyLjAwIiBzdHlsZT0iZmlsbDogdmFyKC0tbWQtY29kZS1mZy1jb2xvcik7IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSI1MTIiIHk9Ii0xNC4yIj5WYWxpZGF0aW9uPC90ZXh0Pgo8L2c+CjxnIGNsYXNzPSJlZGdlIiBpZD0iZWRnZTUiPgo8dGl0bGU+U2VtYS0mZ3Q7VmFsaWRhdGlvbjwvdGl0bGU+CjxwYXRoIGQ9Ik00MzguMDEsLTE4QzQ0NS45MiwtMTggNDU0Ljg2LC0xOCA0NjMuNzIsLTE4IiBmaWxsPSJub25lIiBzdHlsZT0ic3Ryb2tlOiB2YXIoLS1tZC1ncmFwaHZpei1lZGdlLWNvbG9yKTsiIC8+Cjxwb2x5Z29uIHBvaW50cz0iNDY0LC0yMS41IDQ3NCwtMTggNDY0LC0xNC41IDQ2NCwtMjEuNSIgc3R5bGU9ImZpbGw6IHZhcigtLW1kLWdyYXBodml6LWVkZ2UtY29sb3IpO3N0cm9rZTogdmFyKC0tbWQtZ3JhcGh2aXotZWRnZS1jb2xvcik7Ij48L3BvbHlnb24+CjwvZz4KPC9nPgo8L3N2Zz4=" class="graphviz" />

</div>

Each completed stage will update <a href="/python/v0.8.4/syside/BasicDocument.md" class="reference internal" title="syside.BasicDocument.build_state"><span class="pre"><code class="sourceCode python">BasicDocument.build_state</code></span></a> to a corresponding value, and will skip documents that have already been completed previously. Note that the <a href="/python/v0.8.4/syside/Schedule.md" class="reference internal" title="syside.Schedule"><span class="pre"><code class="sourceCode python">Schedule</code></span></a> is safe to execute on multiple threads without requiring explicit synchronization of separate documents – this is achieved with build dependencies between both documents and stages.

<div id="parse-ast" class="section">

### Parse & AST<a href="#parse-ast" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

This is the very first stage in the pipeline that gets run and is responsible for parsing the source and constructing an initial AST (not including implied relationships).

<div class="highlight-py notranslate">

<div class="highlight">

    assert document.build_state == syside.BuildState.Parsed

    # complete schedule here with
    options = syside.ScheduleOptions(
        validation_timing=syside.ValidationTiming.Manual,
        cutoff=syside.BuildState.Parsed,
    )

</div>

</div>

This can also be directly achieved with

<div class="highlight-py notranslate">

<div class="highlight">

    mutex: syside.SharedMutex[syside.Document]
    diagnostics: list[syside.Diagnostic]
    # single-threaded - noop mutex
    mutex, diagnostics = syside.Document.parse_string_st(
        "package P;", syside.ModelLanguage.SysML
    )

    # multi-threaded - mutex
    mutex, diagnostics = syside.Document.parse_string_mt(
        "package P;", syside.ModelLanguage.KerML
    )

</div>

</div>

If the source has changed, e.g. through <a href="/python/v0.8.4/syside/TextDocument.md" class="reference internal" title="syside.TextDocument.update"><span class="pre"><code class="sourceCode python">TextDocument.update</code></span></a>, set <span class="pre">`document.build_state`</span>` `<span class="pre">`=`</span>` `<span class="pre">`syside.BuildState.Changed`</span> to force the pipeline to reparse the source and rebuild the AST.

</div>

<div id="indexing-caching" class="section">

### Indexing & Caching<a href="#indexing-caching" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

Indexing is executed immediately after constructing the AST. It is used to resolve cross-document references in the sema stage.

Caching is dependent on all related documents having completed indexing and thus acts as a synchronization barrier – a single cache is assumed per language. In SysML and KerML, caching populates a shared <a href="/python/v0.8.4/syside/Stdlib.md" class="reference internal" title="syside.Stdlib"><span class="pre"><code class="sourceCode python">Stdlib</code></span></a>.

<div class="highlight-py notranslate">

<div class="highlight">

    assert document.build_state == syside.BuildState.Indexed

    # complete schedule here with
    options = syside.ScheduleOptions(
        validation_timing=syside.ValidationTiming.Manual,
        cutoff=syside.BuildState.Indexed,
    )

</div>

</div>

Indexing is possible manually:

<div class="highlight-py notranslate">

<div class="highlight">

    syside.collect_exports(document)
    index.insert(document)

</div>

</div>

Caching, too:

<div class="highlight-py notranslate">

<div class="highlight">

    lib = syside.Stdlib(index)
    assert lib.all_complete

</div>

</div>

Re-index <span class="pre">`documents`</span> in the pipeline with <span class="pre">`document.build_state`</span>` `<span class="pre">`=`</span>` `<span class="pre">`syside.BuildState.Parsed`</span> or lower. This is only really needed if named members in <span class="pre">`document.root_node`</span> have changed – the reference resolution otherwise is a walk through the model graph.

</div>

<div id="sema" class="section">

### Sema<a href="#sema" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

This is the semantic resolution stage, and is responsible for resolving references and specification semantic constraints (starting with <span class="pre">`check`</span> in the specification). Sema requires caching to have completed.

<div class="highlight-py notranslate">

<div class="highlight">

    assert document.build_state == syside.BuildState.Built

    # complete schedule here with
    options = syside.ScheduleOptions(
        validation_timing=syside.ValidationTiming.Manual,
        cutoff=syside.BuildState.Built,
    )

</div>

</div>

Sema can be performed manually:

<div class="highlight-py notranslate">

<div class="highlight">

    syside.Sema().resolve([document], index, lib)

</div>

</div>

This is the most important stage in SysML pipeline, and additionally, its actions are dependent on relationships between elements. Moreover, because of abundance of cycles and unclear cause-and-effect relationships in SysML, sema automatically updates <a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element.sema_state"><span class="pre"><code class="sourceCode python">Element.sema_state</code></span></a> and ignores elements with <span class="pre">`element.sema_state`</span>` `<span class="pre">`!=`</span>` `<span class="pre">`syside.SemaState.none`</span>. If a model is expected to be modified, prefer parsing the initial AST with <a href="/python/v0.8.4/syside/Document.md" class="reference internal" title="syside.Document.parse_string_st"><span class="pre"><code class="sourceCode python">parse_string_st</code></span></a> or <a href="/python/v0.8.4/syside/Document.md" class="reference internal" title="syside.Document.parse_string_mt"><span class="pre"><code class="sourceCode python">parse_string_mt</code></span></a> to avoid having to discard sema results. Otherwise, sema can be reset with

<div class="highlight-py notranslate">

<div class="highlight">

    # for a single element
    syside.sema_reset(element)

    # or the whole document
    syside.sema_reset(document)

</div>

</div>

The latter additionally resets resolved references back to placeholder values so that sema has to do reference resolution again. Note that resetting sema on a <span class="pre">`document`</span> will additionally ensure that the resolved references in the model match the resolved references from the source before resetting them back to placeholders – any mismatches will be reported through the last <span class="pre">`reporter`</span> callable parameter, these references will not be touched.

Re-run sema in the pipeline with <span class="pre">`document.build_state`</span>` `<span class="pre">`=`</span>` `<span class="pre">`syside.BuildState.Indexed`</span> or lower. Note that doing so should also be applied to any dependent documents as well. Additionally, <span class="pre">`documents`</span> can be rebuilt from the sema stage by passing them as <span class="pre">`invalidated`</span> in <a href="/python/v0.8.4/syside/Pipeline.md" class="reference internal" title="syside.Pipeline.schedule"><span class="pre"><code class="sourceCode python">Pipeline.schedule</code></span></a>.

</div>

<div id="validation" class="section">

### Validation<a href="#validation" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

This is the last stage in the pipeline and is responsible for validating the model – checking that validation constraints (starting with <span class="pre">`validate`</span>) defined in the specification are satisfied. This stage runs after <span class="pre">`documents`</span> have been semantically resolved. Note that validation does not usually check standard <span class="pre">`check...`</span> constraints as they should be enforced by the model or semantic resolution.

<div class="admonition note">

Note

Before adding non-standard lint rules, diagnostic pragmas need to be implemented that can disable unwanted diagnostics.

</div>

<div class="highlight-py notranslate">

<div class="highlight">

    assert document.build_state == syside.BuildState.Validated

    # complete schedule here with (default, no real effect)
    options = syside.ScheduleOptions(
        validation_timing=syside.ValidationTiming.Manual,
        cutoff=syside.BuildState.Validated,
    )

</div>

</div>

Already validated documents can be revalidated in the pipeline with

<div class="highlight-py notranslate">

<div class="highlight">

    schedule = pipeline.schedule(
        [document],
        options=syside.ScheduleOptions(
            validation_timing=syside.ValidationTiming.Manual,
            force_revalidation=True,
        ),
    )

    # or
    with document.lock() as doc:
        doc.build_state = syside.BuildState.Built  # or lower

</div>

</div>

Pipeline scheduling contains additional validation options:

- <a href="/python/v0.8.4/syside/ScheduleOptions.md" class="reference internal" title="syside.ScheduleOptions.validation_tier"><span class="pre"><code class="sourceCode python">validation_tier</code></span></a> controls the level of <a href="/python/v0.8.4/syside/BasicDocument.md" class="reference internal" title="syside.BasicDocument.document_tier"><span class="pre"><code class="sourceCode python">document_tier</code></span></a> that are validated, skipping documents with lower tiers. This is primarily used in editor applications where users are not usually concerned with diagnostics from the standard and external libraries. For example, setting <span class="pre">`validation_tier`</span>` `<span class="pre">`=`</span>` `<span class="pre">`syside.DocumentTier.External`</span> will validate documents with <span class="pre">`document_tier`</span>` `<span class="pre">`in`</span>` `<span class="pre">`(syside.DocumentTier.External,`</span>` `<span class="pre">`syside.DocumentTier.Project)`</span> but not documents with <span class="pre">`document_tier`</span>` `<span class="pre">`==`</span>` `<span class="pre">`syside.DocumentTier.StandardLibrary`</span>.

- <a href="/python/v0.8.4/syside/ScheduleOptions.md" class="reference internal" title="syside.ScheduleOptions.validation_timing"><span class="pre"><code class="sourceCode python">validation_timing</code></span></a> controls the cost level of validation rules that run, e.g. <span class="pre">`validation_timing`</span>` `<span class="pre">`==`</span>` `<span class="pre">`syside.ValidationTiming.Manual`</span> will run all validation rules, while <span class="pre">`validation_timing`</span>` `<span class="pre">`==`</span>` `<span class="pre">`syside.ValidationTiming.OnType`</span> – those cheap enough to run on every key stroke. At the moment, all built-in validation rules are cheap enough to run <span class="pre">`OnType`</span> but that may change in the future. Note that <span class="pre">`validation_timing`</span>` `<span class="pre">`==`</span>` `<span class="pre">`syside.ValidationTiming.Never`</span> will effectively skip validation stage.

</div>

</div>

</div>
