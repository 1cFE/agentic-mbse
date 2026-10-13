"""How capture starts the extractor: with the running interpreter, and never with its Claude flags.

`--index` and `--summarize` start the `claude` CLI, which refuses to run inside
an agent session, and the class of a run must come only from receipts and the
run log, never from an extractor summary.
"""

import subprocess
import sys

import pytest

from agentic_mbse.research import LocalPdfSource, SourceMetadata, UrlSource, register

METADATA = SourceMetadata(
    title="Widget Coil Note",
    use_for="Synthetic winding-pack geometry; exercises the extractor command.",
    validation="Compare against the fixture page itself.",
    caveat="A test fixture.",
)


@pytest.fixture
def extractor_calls(monkeypatch) -> list[list[str]]:
    """Record every extractor run, and fail it, so no capture completes."""
    calls: list[list[str]] = []

    def run(command, **kwargs):
        calls.append(command)
        return subprocess.CompletedProcess(command, 2, stdout="", stderr="first\nlast line\n")

    monkeypatch.setattr(subprocess, "run", run)
    return calls


def test_a_url_capture_runs_the_extractor_on_the_url(local_site, knowledge_tree, extractor_calls):
    url = local_site.url("utf8.html")
    result = register(UrlSource(url=url), METADATA, paths=knowledge_tree.paths, budget=1.5)

    (command,) = extractor_calls
    staging = command[command.index("--output") + 1]
    assert command == [
        sys.executable,
        "-m",
        "agentic_mbse",
        "extract",
        url,
        "--save-source",
        "--output",
        staging,
        "--budget",
        "1.5",
    ]
    assert staging.startswith(str(knowledge_tree.paths.staging) + "/")
    assert result.outcome == "capture_failed"
    assert result.reason == "last line"


def test_a_local_capture_runs_the_extractor_on_a_staged_copy(
    knowledge_tree, generated_pdf, extractor_calls
):
    register(LocalPdfSource(path=generated_pdf), METADATA, paths=knowledge_tree.paths)

    (command,) = extractor_calls
    assert command[:4] == [sys.executable, "-m", "agentic_mbse", "extract"]
    staging = command[command.index("--output") + 1]
    assert command[4] == f"{staging}/.rawin/{generated_pdf.name}"


def test_the_extractor_never_gets_its_claude_flags(local_site, knowledge_tree, extractor_calls):
    register(UrlSource(url=local_site.url("utf8.html")), METADATA, paths=knowledge_tree.paths)

    (command,) = extractor_calls
    assert "--index" not in command
    assert "--summarize" not in command
