"""Enumerate the candidate refusal sites in agentic-mbse, and reconcile the account.

    uv run python scripts/subset_profile/scan_sites.py --agentic-rev REV
        [--out CSV] [--reconcile ACCOUNT_CSV]

Hardened from the prototype `.project/concepts/convince-me-exec-subset/evidence/02-inventory.py`
(design D10). `scan_sites/1` scanned sysml-codegen too; that half moved to sysml-codegen's
`tests/helpers/subset_profile/site_scan.py` (EXEC-SUBSET-CONTRACT Item 2a D7), and this script
scans agentic-mbse only (`scan_sites/2`). It runs as follows:

- The tree is read from a `git archive` export of the named revision into a temp directory,
  never from a working checkout. The export's embedded commit id is checked.
- The output CSV starts with `#` header lines naming the scanner revision, the tree revision
  and every recognized form, read from `tests/fixtures/subset_profile/inventory/scanner.toml`.
  The script refuses to run if that file's forms differ from the ones coded here.
- The five computed `executable_profile` reason sites are mapped to the reasons each can emit
  (`scanner.toml` `[[computed_site]]`), and every mapped reason must be a member of
  `REASON_CODES` read from the exported `executable_profile.py`. An unmapped computed site in
  agentic-mbse is an error.
- `--reconcile` compares the scan with the site account and exits 1 on any scanned site with no
  account row (unaccounted) or account row with no scanned site (orphan).

`scan_sites/1` found executable_profile's `_diagnostic` factory only because a sysml-codegen
function has the same name, so its factory search ran over both trees. `scan_sites/2` declares
`_diagnostic` as a form instead; the 61 site IDs are unchanged.

A site is where a refusal originates. Its ID is (path, enclosing qualname, channel, code,
ordinal within that function), which survives line moves. Channels:

  coded-relay      the code is `<expr>.code`: forwarding an already-coded refusal
  coded-returned   the code is a local bound from a helper whose every return is a code literal
  coded-mapped     the code is `TABLE.get(k, default)` over a module-level literal table
  plumbing         the code is a parameter of the enclosing function (a factory)
  coded-DYNAMIC    the code is computed some other way
  shared-evidence  SemanticEvidenceError(...) (or a factory of it) with a literal code
  shared-profile   executable_profile `_diagnostic(...)` with a literal reason
"""

from __future__ import annotations

import argparse
import ast
import csv
import sys
import tempfile
from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

import tomllib

sys.path.insert(0, str(Path(__file__).resolve().parent))

from isolated_tree import export_tree, git, resolve_rev  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
SCANNER_TOML = REPO_ROOT / "tests" / "fixtures" / "subset_profile" / "inventory" / "scanner.toml"
FIELDS = ("file", "line", "function", "channel", "code", "via", "ordinal", "site_id", "resolved")

# ---- recognized forms (scanner.toml must list exactly these) -----------------------------------

CODE_ENUMS = frozenset({"SemanticEvidenceCode"})
# Classes whose constructor takes a code (first positional or code=).
CODE_TAKING = frozenset({"SemanticEvidenceError"})
SHARED_EVIDENCE_CLASS = "SemanticEvidenceError"
# executable_profile's reason factory: `_diagnostic(reason, ...)`.
SHARED_PROFILE_FACTORY = "_diagnostic"
COMPUTED_PROFILE_FILE = "agentic_mbse/sysml/executable_profile.py"


class ScanError(RuntimeError):
    """The scan cannot vouch for its output."""


def callee(node: ast.Call) -> str | None:
    f = node.func
    if isinstance(f, ast.Name):
        return f.id
    if isinstance(f, ast.Attribute):
        return f.attr
    return None


def literal_codes(expr: ast.expr | None) -> list[str] | None:
    """Codes named by a literal enum attribute, or both arms of a literal conditional."""
    if (
        isinstance(expr, ast.Attribute)
        and isinstance(expr.value, ast.Name)
        and expr.value.id in CODE_ENUMS
    ):
        return [expr.attr]
    if isinstance(expr, ast.Constant) and isinstance(expr.value, str) and expr.value.isidentifier():
        return [expr.value]  # executable_profile's string reason vocabulary
    if isinstance(expr, ast.IfExp):
        a, b = literal_codes(expr.body), literal_codes(expr.orelse)
        if a is not None and b is not None:
            return a + b
    return None


def code_returners(tree: ast.AST) -> dict[str, list[str]]:
    """Functions whose every return is a code literal or None."""
    out: dict[str, list[str]] = {}
    for fn in ast.walk(tree):
        if isinstance(fn, ast.FunctionDef):
            rets = [n for n in ast.walk(fn) if isinstance(n, ast.Return)]
            codes: list[str] = []
            ok = bool(rets)
            for r in rets:
                if r.value is None or (isinstance(r.value, ast.Constant) and r.value.value is None):
                    continue
                c = literal_codes(r.value)
                if c is None:
                    ok = False
                    break
                codes += c
            if ok and codes:
                out[fn.name] = codes
    return out


def code_tables(tree: ast.Module) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for st in tree.body:
        if isinstance(st, ast.AnnAssign):
            target: ast.expr | None = st.target
            value = st.value
        elif isinstance(st, ast.Assign):
            target, value = st.targets[0], st.value
        else:
            target, value = None, None
        if isinstance(target, ast.Name) and isinstance(value, ast.Dict):
            vals = [literal_codes(v) for v in value.values]
            codes = [c for v in vals if v is not None for c in v]
            if vals and all(v is not None for v in vals):
                out[target.id] = codes
    return out


def _code_expr(node: ast.Call, factory_pos: dict[str, int]) -> ast.expr | None:
    for kw in node.keywords:
        if kw.arg == "code":
            return kw.value
    pos = factory_pos.get(callee(node) or "", 0)
    return node.args[pos] if len(node.args) > pos else None


def factories(trees: Iterable[ast.Module]) -> dict[str, int]:
    """The declared profile factory, plus every function that takes a code parameter and passes
    it to a code-taking constructor (fixpoint)."""
    trees = list(trees)
    found: dict[str, int] = {SHARED_PROFILE_FACTORY: 0}
    while True:
        before = dict(found)
        for tree in trees:
            for fn in ast.walk(tree):
                if not isinstance(fn, ast.FunctionDef):
                    continue
                names = [a.arg for a in fn.args.args if a.arg not in ("self", "cls")]
                for call in ast.walk(fn):
                    if isinstance(call, ast.Call) and callee(call) in CODE_TAKING | set(found):
                        e = _code_expr(call, before)
                        if isinstance(e, ast.Name) and e.id in names:
                            found[fn.name] = names.index(e.id)
        if found == before:
            return found


@dataclass
class _FunctionScope:
    params: set[str] = field(default_factory=set)
    locals: dict[str, str | None] = field(default_factory=dict)


class _Visitor(ast.NodeVisitor):
    """Collect the sites in one module."""

    def __init__(self, rel: str, tree: ast.Module, factory_pos: dict[str, int]) -> None:
        self.rel, self.factory_pos = rel, factory_pos
        self.returners, self.tables = code_returners(tree), code_tables(tree)
        self.scope = _FunctionScope()
        self.stack: list[str] = []
        self.rows: list[dict[str, str]] = []
        self.ordinals: Counter[tuple[str, str, str]] = Counter()

    def classify_code(self, expr: ast.expr | None) -> tuple[str, str]:
        codes = literal_codes(expr)
        if codes is not None:
            return "coded", "|".join(codes)
        if isinstance(expr, ast.Attribute) and expr.attr == "code":
            return "coded-relay", ast.unparse(expr)
        if isinstance(expr, ast.Name):
            if expr.id in self.scope.params:
                return "plumbing", expr.id
            fn = self.scope.locals.get(expr.id)
            if fn is not None and fn in self.returners:
                return "coded-returned", "|".join(self.returners[fn])
        if (
            isinstance(expr, ast.Call)
            and isinstance(expr.func, ast.Attribute)
            and expr.func.attr == "get"
            and isinstance(expr.func.value, ast.Name)
            and expr.func.value.id in self.tables
        ):
            default = literal_codes(expr.args[1]) if len(expr.args) > 1 else []
            if default is not None:
                table = self.tables[expr.func.value.id]
                return "coded-mapped", "|".join(sorted(set(table + default)))
        return "coded-DYNAMIC", ast.unparse(expr) if expr is not None else "<none>"

    def _scope(self, node: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef) -> None:
        self.stack.append(node.name)
        saved = self.scope
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            self.scope = _FunctionScope(
                params={a.arg for a in node.args.args + node.args.kwonlyargs}
            )
            for st in ast.walk(node):
                if (
                    isinstance(st, ast.Assign)
                    and len(st.targets) == 1
                    and isinstance(st.targets[0], ast.Name)
                    and isinstance(st.value, ast.Call)
                ):
                    self.scope.locals[st.targets[0].id] = callee(st.value)
        self.generic_visit(node)
        self.scope = saved
        self.stack.pop()

    visit_FunctionDef = visit_AsyncFunctionDef = visit_ClassDef = _scope  # noqa: N815

    def add(self, node: ast.expr | ast.stmt, channel: str, code: str, via: str) -> None:
        func = ".".join(self.stack) or "<module>"
        key = (func, channel, code)
        self.ordinals[key] += 1
        self.rows.append(
            {
                "file": self.rel,
                "line": str(node.lineno),
                "function": func,
                "channel": channel,
                "code": code,
                "via": via,
                "ordinal": str(self.ordinals[key]),
                "site_id": f"{self.rel}::{func}::{channel}::{code}::{self.ordinals[key]}",
                "resolved": "",
            }
        )

    def visit_Call(self, node: ast.Call) -> None:
        name = callee(node)
        if name in {SHARED_EVIDENCE_CLASS} | set(self.factory_pos):
            channel, code = self.classify_code(_code_expr(node, self.factory_pos))
            if channel == "coded":
                channel = "shared-evidence" if code.isupper() else "shared-profile"
            self.add(node, channel, code, name or "?")
        self.generic_visit(node)


def _sources(root: Path) -> list[tuple[str, ast.Module]]:
    return [
        (str(path.relative_to(root)), ast.parse(path.read_text(encoding="utf-8")))
        for path in sorted((root / "agentic_mbse").rglob("*.py"))
    ]


def scan_sources(agentic_src: Path) -> list[dict[str, str]]:
    """Every recognized site in agentic-mbse's `src/` root, in file then source order."""
    sources = _sources(agentic_src)
    factory_pos = factories(tree for _, tree in sources)
    rows: list[dict[str, str]] = []
    for rel, tree in sources:
        visitor = _Visitor(rel, tree, factory_pos)
        visitor.visit(tree)
        rows += visitor.rows
    return rows


# ---- scanner.toml: forms, blind spots, computed sites ----------------------------------------


@dataclass(frozen=True)
class ScannerSpec:
    revision: str
    forms: dict[str, list[str]]
    blind_spots: tuple[str, ...]
    computed: dict[str, tuple[str, ...]]


def load_scanner_spec(path: Path = SCANNER_TOML) -> ScannerSpec:
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    forms = data["forms"]
    coded = {
        "code_enums": sorted(CODE_ENUMS),
        "code_taking": sorted(CODE_TAKING),
        "shared_evidence_class": [SHARED_EVIDENCE_CLASS],
        "shared_profile_factory": [SHARED_PROFILE_FACTORY],
    }
    listed = {k: sorted(v) for k, v in forms.items() if k != "channels"}
    if listed != coded:
        raise ScanError(
            f"{path}: [forms] differ from the scanner's coded forms: {listed} != {coded}"
        )
    computed = {c["site_id"]: tuple(c["reasons"]) for c in data["computed_site"]}
    return ScannerSpec(
        revision=data["scanner_revision"],
        forms=forms,
        blind_spots=tuple(b["id"] for b in data["blind_spot"]),
        computed=computed,
    )


def reason_codes(agentic_src: Path) -> frozenset[str]:
    """`REASON_CODES` as literally written in the exported `executable_profile.py`."""
    tree = ast.parse((agentic_src / COMPUTED_PROFILE_FILE).read_text(encoding="utf-8"))
    for st in tree.body:
        if (
            isinstance(st, ast.Assign)
            and isinstance(st.targets[0], ast.Name)
            and st.targets[0].id == "REASON_CODES"
            and isinstance(st.value, ast.Call)
            and isinstance(st.value.args[0], ast.Set)
        ):
            return frozenset(ast.literal_eval(st.value.args[0]))
    raise ScanError("REASON_CODES is not a literal frozenset({...}) in executable_profile.py")


def resolve_computed(rows: list[dict[str, str]], spec: ScannerSpec, codes: frozenset[str]) -> None:
    """Fill `resolved` for each mapped computed site; any unmapped one is an error."""
    seen = set()
    for row in rows:
        if row["channel"] != "coded-DYNAMIC":
            continue
        reasons = spec.computed.get(row["site_id"])
        if reasons is None:
            raise ScanError(
                f"computed reason site {row['site_id']} has no [[computed_site]] mapping"
            )
        outside = set(reasons) - codes
        if outside:
            raise ScanError(
                f"{row['site_id']} maps to reasons outside REASON_CODES: {sorted(outside)}"
            )
        row["resolved"] = "|".join(reasons)
        seen.add(row["site_id"])
    stale = set(spec.computed) - seen
    if stale:
        raise ScanError(f"[[computed_site]] names sites the scan did not find: {sorted(stale)}")


# ---- run ---------------------------------------------------------------------------------------


def _scanner_identity() -> str:
    script = str(Path(__file__).resolve().relative_to(REPO_ROOT))
    dirty = git(
        REPO_ROOT, "status", "--porcelain", "--", script, str(SCANNER_TOML.relative_to(REPO_ROOT))
    )
    head = git(REPO_ROOT, "rev-parse", "HEAD")
    return f"{script} at agentic-mbse {head}" + (" (uncommitted changes)" if dirty else "")


def write_scan(path: Path, rows: list[dict[str, str]], header: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        for line in header:
            fh.write(f"# {line}\n")
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def read_account_ids(path: Path) -> list[str]:
    with path.open(newline="", encoding="utf-8") as fh:
        return [
            row["site_id"]
            for row in csv.DictReader(line for line in fh if not line.startswith("#"))
        ]


def reconcile(rows: list[dict[str, str]], account: Path) -> tuple[list[str], list[str]]:
    """(unaccounted scanned sites, orphan account rows)."""
    ids = read_account_ids(account)
    duplicates = sorted({i for i in ids if ids.count(i) > 1})
    if duplicates:
        raise ScanError(f"{account} repeats site ids: {duplicates}")
    scanned = {r["site_id"] for r in rows}
    return sorted(scanned - set(ids)), sorted(set(ids) - scanned)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--agentic-rev", required=True)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--reconcile", type=Path, metavar="ACCOUNT_CSV")
    args = parser.parse_args()

    spec = load_scanner_spec()
    agentic_rev = resolve_rev(REPO_ROOT, args.agentic_rev)
    with tempfile.TemporaryDirectory(prefix="subset-scan-") as tmp:
        export_tree(REPO_ROOT, agentic_rev, Path(tmp) / "agentic-mbse")
        agentic_src = Path(tmp) / "agentic-mbse" / "src"
        rows = scan_sources(agentic_src)
        resolve_computed(rows, spec, reason_codes(agentic_src))

    header = [
        f"scanner: {spec.revision}; {_scanner_identity()}",
        f"agentic-mbse: {agentic_rev} (git archive, src/)",
        "recognized forms: "
        + "; ".join(f"{k}={','.join(v)}" for k, v in sorted(spec.forms.items())),
        f"blind spots: {', '.join(spec.blind_spots)} (scanner.toml)",
        f"sites: {len(rows)} (agentic-mbse)",
    ]
    for line in header:
        print(line)
    for channel, n in Counter(r["channel"] for r in rows).most_common():
        print(f"  {n:5d}  {channel}")
    if args.out:
        write_scan(args.out, rows, header)
        print(f"wrote {args.out}")
    if args.reconcile:
        unaccounted, orphans = reconcile(rows, args.reconcile)
        print(
            f"reconcile against {args.reconcile}: {len(unaccounted)} unaccounted, {len(orphans)} orphan"
        )
        for site in unaccounted:
            print(f"  UNACCOUNTED {site}")
        for site in orphans:
            print(f"  ORPHAN      {site}")
        return 1 if unaccounted or orphans else 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
