"""A failure at any commit rung leaves the registry byte-identical, or absent where it was absent.

Failures are injected into the real rung functions, so the code that runs is
the production ladder; only the failing rung's own body is replaced.
"""

import importlib
from dataclasses import replace

import pytest

from agentic_mbse.research import (
    LocalPdfSource,
    RegistrationError,
    SourceMetadata,
    UrlSource,
    register,
)
from tests.test_research.conftest import registry_state

# The package attribute `register` is the function, so the module comes from importlib.
register_module = importlib.import_module("agentic_mbse.research.register")

METADATA = SourceMetadata(
    title="Widget Coil Note",
    use_for="Synthetic winding-pack geometry; exercises the rollback ladder.",
    validation="Compare against the fixture page itself.",
    caveat="A test fixture.",
)

#: Each commit rung, by the name the ladder calls it through in `register.py`.
RUNGS = {
    "before_rename": "_rename_into_sources",
    "after_rename": "append_manifest_row",
    "after_manifest_append": "insert_block",
}


def _fail_at(rung: str, monkeypatch) -> None:
    def boom(*args, **kwargs):
        raise OSError(f"injected failure at {rung}")

    monkeypatch.setattr(register_module, RUNGS[rung], boom)


@pytest.mark.parametrize("rung", sorted(RUNGS))
def test_failure_at_each_rung_leaves_nothing(rung, knowledge_tree, local_site, monkeypatch):
    before = registry_state(knowledge_tree)
    _fail_at(rung, monkeypatch)

    with pytest.raises(RegistrationError, match=rung):
        register(UrlSource(url=local_site.url("utf8.html")), METADATA, paths=knowledge_tree.paths)

    assert registry_state(knowledge_tree) == before
    assert not list(knowledge_tree.paths.staging.iterdir())


def test_a_failed_commit_on_a_fresh_target_leaves_no_manifest(
    knowledge_tree, local_site, monkeypatch
):
    assert not knowledge_tree.manifest.exists()  # a fresh target has none
    before = knowledge_tree.index.read_bytes()
    _fail_at("after_manifest_append", monkeypatch)

    with pytest.raises(RegistrationError):
        register(UrlSource(url=local_site.url("utf8.html")), METADATA, paths=knowledge_tree.paths)

    assert not knowledge_tree.manifest.exists()
    assert knowledge_tree.index.read_bytes() == before


@pytest.mark.parametrize("rung", sorted(RUNGS))
def test_rollback_preserves_an_earlier_registration(rung, knowledge_tree, local_site, monkeypatch):
    """The ladder undoes its own rungs and nothing else."""
    kept = register(
        UrlSource(url=local_site.url("utf8.html")), METADATA, paths=knowledge_tree.paths
    )
    assert kept.outcome == "registered"
    before = registry_state(knowledge_tree)
    _fail_at(rung, monkeypatch)

    with pytest.raises(RegistrationError):
        register(
            UrlSource(url=local_site.url("latin1.html")),
            replace(METADATA, title="Cable Note"),
            paths=knowledge_tree.paths,
        )

    assert registry_state(knowledge_tree) == before
    assert (kept.path / "output.md").is_file()


@pytest.mark.slow
def test_a_failed_local_pdf_commit_removes_its_raw_copy(knowledge_tree, generated_pdf, monkeypatch):
    before = registry_state(knowledge_tree)
    _fail_at("after_manifest_append", monkeypatch)

    with pytest.raises(RegistrationError):
        register(LocalPdfSource(path=generated_pdf), METADATA, paths=knowledge_tree.paths)

    assert registry_state(knowledge_tree) == before
    assert not (knowledge_tree.raw / generated_pdf.name).exists()
    assert generated_pdf.is_file()  # the caller's original is never moved
