"""C3 step 3b: prototype guidance-contract harness (pytest).

Every authored SysML fence in shipped assets must have exactly one manifest entry,
keyed by path + heading anchor + content hash. Each category carries its own check:

  fragment     reason required; content pinned by the hash in its id
  definition   loads with zero SysIDE errors; makes no execution claim
  executable   `sysml-codegen generate` succeeds; must_emit names appear in the output,
               omits names do not (a silent omission is an expected, visible outcome)
  native-only  generation refuses with exactly expect_codes (or expect_message)
  negative     same as native-only, for examples the prose marks as wrong

    C3_ROOT=<tree> C3_MANIFEST=<yaml> uv run pytest -q -p no:cacheprovider \
        .project/concepts/convince-me-exec-subset/evidence/03-harness-test.py
"""

from __future__ import annotations

import importlib.util
import os
import re
import subprocess
import tempfile
from pathlib import Path

import pytest
import syside
import yaml

HERE = Path(__file__).resolve().parent
ROOT = Path(os.environ.get("C3_ROOT", HERE.parents[3]))
MANIFEST = Path(os.environ.get("C3_MANIFEST", HERE / "03-manifest.yaml"))
CONTEXTS = Path(os.environ.get("C3_CONTEXTS", HERE / "03-contexts"))
CODEGEN = Path("/home/reid/src/sysml-codegen/.venv/bin/sysml-codegen")
ENV_FILE = HERE.parents[3] / ".env"

_spec = importlib.util.spec_from_file_location("fences", HERE / "03-fences.py")
fences = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fences)
fences.REPO = ROOT

INVENTORY = {f["id"]: f for f in fences.collect(fences.SHIPPED_GLOBS)}
ENTRIES = {e["id"]: e for e in yaml.safe_load(MANIFEST.read_text())["fences"]}
CODE = re.compile(r"\b(SI_[A-Z_]+|SYSML_NAMESPACE_NOT_DISTINGUISHABLE|OVERRIDE_TARGET_MISSING|EXTRACTION_DIAGNOSTIC_BLOCKING)\b")


def _env() -> dict[str, str]:
    env = dict(os.environ)
    for line in ENV_FILE.read_text().splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            k, v = line.split("=", 1)
            env.setdefault(k.strip(), v.strip().strip('"'))
    return env


def _model_text(entry: dict, body: str) -> str:
    if not entry.get("wrapped"):
        return body
    parts = {p.split(".")[1]: (CONTEXTS / p).read_text() for p in entry.get("context", [])}
    return fences.WRAP_HEAD + parts.get("prelude", "") + body + parts.get("harness", "") + "}\n"


def _generate(text: str) -> tuple[int, str, str]:
    with tempfile.TemporaryDirectory() as tmp:
        models = Path(tmp) / "models"
        models.mkdir()
        (models / "example.sysml").write_text(text)
        out = Path(tmp) / "generated"
        proc = subprocess.run(
            [str(CODEGEN), "generate", "--models", str(models), "--output", str(out), "--overwrite"],
            cwd=CODEGEN.parents[2], env=_env(), capture_output=True, text=True, timeout=300,
        )
        emitted = "\n".join(p.read_text() for p in out.rglob("*.py")) if out.exists() else ""
        return proc.returncode, proc.stdout + proc.stderr, emitted


def test_every_fence_has_exactly_one_entry() -> None:
    unlisted = sorted(set(INVENTORY) - set(ENTRIES))
    stale = sorted(set(ENTRIES) - set(INVENTORY))
    assert not unlisted and not stale, (
        f"{len(unlisted)} fence(s) with no manifest entry (new or edited content):\n  "
        + "\n  ".join(unlisted)
        + f"\n{len(stale)} manifest entr(y/ies) whose fence no longer exists:\n  "
        + "\n  ".join(stale)
    )


@pytest.mark.parametrize("fid", sorted(ENTRIES), ids=lambda i: i.split("@")[0][-60:] + "@" + i[-12:])
def test_entry_holds(fid: str) -> None:
    entry = ENTRIES[fid]
    if fid not in INVENTORY:
        pytest.fail("fence missing from tree (see inventory test)")
    body = INVENTORY[fid]["body"]
    cat = entry["category"]
    if cat == "fragment":
        assert entry.get("reason"), "fragment exemption needs a reason"
        return
    text = _model_text(entry, body)
    if cat == "definition":
        with tempfile.NamedTemporaryFile("w", suffix=".sysml", delete=False) as fh:
            fh.write(text)
        _, diags = syside.try_load_model([fh.name])
        errors = [d.message for d in [*diags.parser, *diags.sema, *diags.validation] if d.severity == syside.DiagnosticSeverity.Error]
        assert not errors, errors
        return
    rc, out, emitted = _generate(text)
    if cat == "executable":
        assert rc == 0, f"marked executable but the generator refused: {sorted(set(CODE.findall(out)))} {out.strip().splitlines()[-1][:300]}"
        for name in entry.get("must_emit", []):
            assert name in emitted, f"{name} missing from generated code"
        for name in entry.get("omits", []):
            assert name not in emitted, f"{name} now emitted; update the expected omission"
        return
    assert cat in ("native-only", "negative"), f"unknown category {cat}"
    assert rc != 0, f"marked {cat} but now generates; reclassify it"
    if entry.get("expect_message"):
        assert entry["expect_message"] in out
    assert sorted(set(CODE.findall(out))) == entry["expect_codes"]
