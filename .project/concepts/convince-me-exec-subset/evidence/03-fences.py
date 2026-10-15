"""C3 step 1: inventory every authored SysML fence in shipped assets and parse each one.

Run from the agentic-mbse repo root with its venv (SysIDE 0.8.4):
    uv run python .project/concepts/convince-me-exec-subset/evidence/03-fences.py

Writes 03-inventory.csv and 03-inventory.log next to this script, plus one
.sysml file per fence under <scratch>/c3/fences/ for the elaboration step.
"""

from __future__ import annotations

import csv
import hashlib
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import syside

REPO = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
SCRATCH = Path(
    os.environ.get(
        "C3_SCRATCH",
        "/tmp/claude-1000/-home-reid-src-agentic-mbse/8cecfa0f-3dca-4be9-bcbc-86b4acc4ae95/scratchpad/c3",
    )
)
FENCE_DIR = SCRATCH / "fences"

# Shipped, authored guidance (Context B assets).
SHIPPED_GLOBS = [
    "skills/**/*.md",
    "agents/**/*.md",
    "adapters/**/*.md",
    "project_templates/**/*.template",
    "project_templates/**/*.md",
    "docs/patterns/**/*.md",
    "docs/*.md",
]
# Vendored language/reference corpus: counted, never promised as generator support.
VENDORED_GLOBS = ["docs/sysmlv2/**/*.md", "docs/syside/**/*.md"]

FENCE_OPEN = re.compile(r"^(\s*)(`{3,}|~{3,})\s*([^`\s]*)\s*$")
HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
NEGATIVE = re.compile(
    r"\b(WRONG|BAD|INCORRECT|Incorrect|Wrong|Bad|DON'?T|Don'?t|will not parse|never executes|Not a check|Anti-?pattern|Avoid)\b|❌"
)
WRAP_HEAD = (
    "package FenceWrap {\n"
    "    private import ScalarValues::*;\n"
    "    private import ISQ::*;\n"
    "    private import SI::*;\n"
    "    private import NumericalFunctions::*;\n"
)


def slug(text: str) -> str:
    text = re.sub(r"[^\w\s-]", "", text.lower()).strip()
    return re.sub(r"[\s]+", "-", text)


def scan(lines: list[str], base_line: int, heading: str, out: list[dict]) -> None:
    """CommonMark-style fence scan; recurse into non-sysml fences to find nested ones."""
    i = 0
    current = heading
    while i < len(lines):
        line = lines[i]
        h = HEADING.match(line)
        if h:
            current = slug(h.group(2))
        m = FENCE_OPEN.match(line)
        if not m:
            i += 1
            continue
        marker, info = m.group(2), m.group(3).lower()
        j = i + 1
        while j < len(lines):
            close = re.match(r"^\s*(`{3,}|~{3,})\s*$", lines[j])
            if close and close.group(1)[0] == marker[0] and len(close.group(1)) >= len(marker):
                break
            j += 1
        body = lines[i + 1 : j]
        context = "\n".join(lines[max(0, i - 4) : i])
        if info in ("sysml", "kerml"):
            out.append(
                {
                    "lang": info,
                    "line": base_line + i + 1,
                    "anchor": current,
                    "body": "\n".join(body) + "\n",
                    "context": context,
                    "nested": base_line > 0,
                }
            )
        else:
            scan(body, base_line + i + 1, current, out)
        i = j + 1


def collect(globs: list[str]) -> list[dict]:
    fences: list[dict] = []
    seen: set[Path] = set()
    for g in globs:
        for path in sorted(REPO.glob(g)):
            if path in seen or not path.is_file():
                continue
            seen.add(path)
            found: list[dict] = []
            scan(path.read_text(encoding="utf-8").splitlines(), 0, "top", found)
            rel = path.relative_to(REPO).as_posix()
            for f in found:
                digest = hashlib.sha256(f["body"].encode()).hexdigest()[:12]
                f["path"] = rel
                f["id"] = f"{rel}#{f['anchor']}@{digest}"
                f["hash"] = digest
            fences.extend(found)
    return fences


def load(path: Path) -> tuple[int, int, int]:
    _, diags = syside.try_load_model([str(path)])
    err = syside.DiagnosticSeverity.Error
    p = sum(1 for d in diags.parser if d.severity == err)
    s = sum(1 for d in diags.sema if d.severity == err)
    v = sum(1 for d in diags.validation if d.severity == err)
    return p, s, v


def classify(fence: dict, idx: int) -> dict:
    FENCE_DIR.mkdir(parents=True, exist_ok=True)
    stem = f"f{idx:03d}"
    raw = FENCE_DIR / f"{stem}.sysml"
    raw.write_text(fence["body"], encoding="utf-8")
    p, s, v = load(raw)
    wrapped = FENCE_DIR / f"{stem}.wrapped.sysml"
    wrapped.write_text(WRAP_HEAD + fence["body"] + "}\n", encoding="utf-8")
    wp, ws, wv = load(wrapped)
    if p == 0 and s == 0 and v == 0:
        status = "complete-standalone"
    elif wp == 0 and ws == 0 and wv == 0:
        status = "complete-wrapped"
    elif p == 0 or wp == 0:
        status = "parses-unresolved"  # needs context: imports/definitions it names
    else:
        status = "syntax-fragment"  # elisions, deliberately invalid, or partial text
    negative = bool(NEGATIVE.search(fence["context"]) or NEGATIVE.search(fence["body"][:200]))
    return {
        "idx": idx,
        "id": fence["id"],
        "path": fence["path"],
        "line": fence["line"],
        "lang": fence["lang"],
        "nested": fence["nested"],
        "negative_marked": negative,
        "standalone_parser_err": p,
        "standalone_sema_err": s,
        "standalone_valid_err": v,
        "wrapped_parser_err": wp,
        "wrapped_sema_err": ws,
        "wrapped_valid_err": wv,
        "status": status,
        "file": raw.name if status != "complete-wrapped" else wrapped.name,
    }


def main() -> int:
    shipped = collect(SHIPPED_GLOBS)
    vendored = collect(VENDORED_GLOBS)
    rows = [classify(f, i) for i, f in enumerate(shipped)]
    with (OUT / "03-inventory.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    by_dir: dict[str, Counter] = defaultdict(Counter)
    for r in rows:
        top = "/".join(r["path"].split("/")[:2]) if r["path"].startswith("docs/") else r["path"].split("/")[0]
        by_dir[top][r["status"]] += 1
    total = Counter(r["status"] for r in rows)
    complete = total["complete-standalone"] + total["complete-wrapped"]
    lines = [
        f"syside {syside.__version__}",
        f"shipped fences: {len(rows)} (sysml {sum(r['lang']=='sysml' for r in rows)}, kerml {sum(r['lang']=='kerml' for r in rows)}; nested inside another fence {sum(r['nested'] for r in rows)})",
        f"vendored reference fences (excluded, not a support promise): {len(vendored)}",
        f"files with shipped fences: {len({r['path'] for r in rows})}",
        "",
        "status totals:",
        *[f"  {k:22} {v}" for k, v in sorted(total.items())],
        f"  complete (loads with zero errors, alone or wrapped): {complete}/{len(rows)} = {complete/len(rows):.0%}",
        f"  negative-marked by prose heuristic: {sum(r['negative_marked'] for r in rows)}",
        "",
        "by directory:",
    ]
    for d in sorted(by_dir):
        c = by_dir[d]
        lines.append(f"  {d:34} " + ", ".join(f"{k}={v}" for k, v in sorted(c.items())))
    text = "\n".join(lines) + "\n"
    (OUT / "03-inventory.log").write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
