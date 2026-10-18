"""Assemble index.html from template.html, embedding captured logs verbatim.

Placeholders: {{log:NAME}} embeds evidence/NAME whole; {{head:N:NAME}} embeds its first N lines.
The scratchpad path is shown as $S for readability; nothing else is changed.
"""

import html
import re
from pathlib import Path

HERE = Path(__file__).parent
EVIDENCE = HERE / "evidence"
SCRATCH = "/tmp/claude-1000/-home-reid-src-agentic-mbse/8cecfa0f-3dca-4be9-bcbc-86b4acc4ae95/scratchpad"


def _embed(text: str) -> str:
    return html.escape(text.replace(SCRATCH, "$S").rstrip("\n"))


def _sub(match: re.Match[str]) -> str:
    kind, rest = match.group(1), match.group(2)
    if kind == "log":
        return _embed((EVIDENCE / rest).read_text())
    count, name = rest.split(":", 1)
    lines = (EVIDENCE / name).read_text().splitlines()
    shown = lines[: int(count)]
    return _embed("\n".join(shown) + f"\n… ({len(lines) - len(shown)} more lines in evidence/{name})")


template = (HERE / "template.html").read_text()
(HERE / "index.html").write_text(re.sub(r"\{\{(log|head):([^}]+)\}\}", _sub, template))
print("wrote", HERE / "index.html")
