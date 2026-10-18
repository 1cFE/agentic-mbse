"""Claim 2 evidence: enumerate every site in sysml-codegen that can emit a public refusal.

Usage:
    python 02-inventory.py <codegen_src_root> <agentic_mbse_src_root> <out_csv>

<codegen_src_root> is the directory containing the ``sysml_codegen`` package.
Writes one CSV row per site and prints totals per channel and per code.

A "site" is the place a refusal originates. Identity is
(relpath, enclosing function qualname, channel, code, ordinal-within-function),
which survives line moves, so the inventory test does not churn on unrelated edits.

Channels:
  coded            ElaborationCode/ReadinessCode literal at a construction or _diagnose call
  coded-fixed      a subclass that fixes its code in __init__ (derived, not hand-listed)
  coded-relay      the code is ``<expr>.code`` - forwarding an already-coded refusal
  coded-returned   the code is a local bound from a helper whose every return is a code literal
  coded-mapped     the code is ``TABLE.get(k, default)`` over a module-level literal table
  plumbing         the code is a parameter of the enclosing function; that function's own
                   call sites are enumerated instead (factory detection is automatic)
  coded-DYNAMIC    the code is computed some other way (the falsifier)
  free-text        raise of a codegen public exception class that carries no code
  builtin          raise of a builtin exception; the CLI catch-all turns it into SI_INTERNAL_DEFECT
  shared-evidence  SemanticEvidenceError(...) raised in agentic-mbse (shared facts layer)
  shared-profile   executable_profile._diagnostic(...) string reason in agentic-mbse (shared decisions)
"""

from __future__ import annotations

import ast
import csv
import sys
from collections import Counter
from pathlib import Path

CODE_ENUMS = {"ElaborationCode", "ReadinessCode", "SemanticEvidenceCode"}

# Classes whose constructor takes a code (first positional or code=).
CODE_TAKING = {
    "ElaborationInvariantError",
    "MultiplicityExpansionError",
    "OccurrenceResolutionError",
    "_ReferenceResolutionError",
    "Diagnostic",
    "ReadinessFinding",
    "SemanticEvidenceError",
}

# Codegen public exception classes that carry free text only.
FREE_TEXT = {
    "CodeGenerationError",
    "SysMLParsingError",
    "SourceAdmissionError",
    "PredicateCompileError",
    "CompilationError",
    "GraphValidationError",
    "ExpressionInventoryError",
    "ScopePolicyMismatchError",
    "PackageSealError",
    "ProvenanceError",
    "InstanceGraphSnapshotError",
    "SnapshotShapeError",
    "SnapshotIntegrityError",
    "SnapshotCompatibilityError",
    "SnapshotStaleSourceError",
    "SnapshotCertifiabilityError",
}

BUILTIN = {
    "ValueError",
    "RuntimeError",
    "TypeError",
    "KeyError",
    "AssertionError",
    "LookupError",
    "NotImplementedError",
    "IndexError",
}

# Generation-path packages. study/ and cli/install.py are separate tools, contracts/verify.py
# uses an unrelated seal-verification Diagnostic class.
EXCLUDE = ("study/", "cli/install.py", "contracts/verify.py")


def callee(node: ast.Call) -> str | None:
    f = node.func
    if isinstance(f, ast.Name):
        return f.id
    if isinstance(f, ast.Attribute):
        return f.attr
    return None


FACTORY_POS: dict[str, int] = {}


def code_expr(node: ast.Call) -> ast.expr | None:
    for kw in node.keywords:
        if kw.arg == "code":
            return kw.value
    pos = FACTORY_POS.get(callee(node) or "", 0)
    return node.args[pos] if len(node.args) > pos else None


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


CTX: dict = {"params": set(), "returners": {}, "tables": {}, "locals": {}}


def classify_code(expr: ast.expr | None) -> tuple[str, str]:
    codes = literal_codes(expr)
    if codes is not None:
        return "coded", "|".join(codes)
    if isinstance(expr, ast.Attribute) and expr.attr == "code":
        return "coded-relay", ast.unparse(expr)
    if isinstance(expr, ast.Name):
        if expr.id in CTX["params"]:
            return "plumbing", expr.id
        fn = CTX["locals"].get(expr.id)
        if fn in CTX["returners"]:
            return "coded-returned", "|".join(CTX["returners"][fn])
    if (
        isinstance(expr, ast.Call)
        and isinstance(expr.func, ast.Attribute)
        and expr.func.attr == "get"
        and isinstance(expr.func.value, ast.Name)
        and expr.func.value.id in CTX["tables"]
    ):
        default = literal_codes(expr.args[1]) if len(expr.args) > 1 else []
        if default is not None:
            return "coded-mapped", "|".join(sorted(set(CTX["tables"][expr.func.value.id] + default)))
    return "coded-DYNAMIC", ast.unparse(expr) if expr is not None else "<none>"


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
        target = st.target if isinstance(st, ast.AnnAssign) else (st.targets[0] if isinstance(st, ast.Assign) else None)
        if isinstance(target, ast.Name) and isinstance(st.value, ast.Dict):
            vals = [literal_codes(v) for v in st.value.values]
            if vals and all(v is not None for v in vals):
                out[target.id] = [c for v in vals for c in v]  # type: ignore[union-attr]
    return out


def factories(files: list[Path]) -> dict[str, int]:
    """Functions that take a code parameter and pass it to a code-taking constructor."""
    found: dict[str, int] = {}
    trees = [ast.parse(path.read_text()) for path in files]
    while True:  # fixpoint: a function that forwards its code param to a factory is a factory
        FACTORY_POS.clear()
        FACTORY_POS.update(found)
        before = dict(found)
        for tree in trees:
            for fn in ast.walk(tree):
                if not isinstance(fn, ast.FunctionDef):
                    continue
                names = [a.arg for a in fn.args.args if a.arg not in ("self", "cls")]
                for call in ast.walk(fn):
                    if isinstance(call, ast.Call) and callee(call) in CODE_TAKING | set(found):
                        e = code_expr(call)
                        if isinstance(e, ast.Name) and e.id in names:
                            found[fn.name] = names.index(e.id)
        if found == before:
            return found


def fixed_code_classes(files: list[Path]) -> dict[str, str]:
    """Subclasses whose __init__ calls super().__init__(ElaborationCode.X, ...)."""
    fixed: dict[str, str] = {}
    for path in files:
        tree = ast.parse(path.read_text())
        for cls in ast.walk(tree):
            if not isinstance(cls, ast.ClassDef):
                continue
            for item in cls.body:
                if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                    for call in ast.walk(item):
                        if (
                            isinstance(call, ast.Call)
                            and isinstance(call.func, ast.Attribute)
                            and call.func.attr == "__init__"
                            and call.args
                        ):
                            codes = literal_codes(call.args[0])
                            if codes is not None:
                                fixed[cls.name] = "|".join(codes)
    return fixed


class Visitor(ast.NodeVisitor):
    def __init__(self, rel: str, fixed: dict[str, str], shared: bool) -> None:
        self.rel, self.fixed, self.shared = rel, fixed, shared
        self.stack: list[str] = []
        self.rows: list[dict[str, str]] = []
        self.ordinals: Counter[tuple[str, str, str]] = Counter()

    def _scope(self, node: ast.AST) -> None:
        self.stack.append(node.name)  # type: ignore[attr-defined]
        saved = (CTX["params"], CTX["locals"])
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            CTX["params"] = {a.arg for a in node.args.args + node.args.kwonlyargs}
            CTX["locals"] = {}
            for st in ast.walk(node):
                if (
                    isinstance(st, ast.Assign)
                    and len(st.targets) == 1
                    and isinstance(st.targets[0], ast.Name)
                    and isinstance(st.value, ast.Call)
                ):
                    CTX["locals"][st.targets[0].id] = callee(st.value)
        self.generic_visit(node)
        CTX["params"], CTX["locals"] = saved
        self.stack.pop()

    visit_FunctionDef = visit_AsyncFunctionDef = visit_ClassDef = _scope

    def add(self, node: ast.AST, channel: str, code: str, via: str) -> None:
        func = ".".join(self.stack) or "<module>"
        key = (func, channel, code)
        self.ordinals[key] += 1
        self.rows.append(
            {
                "file": self.rel,
                "line": str(node.lineno),  # type: ignore[attr-defined]
                "function": func,
                "channel": channel,
                "code": code,
                "via": via,
                "ordinal": str(self.ordinals[key]),
                "site_id": f"{self.rel}::{func}::{channel}::{code}::{self.ordinals[key]}",
            }
        )

    def visit_Call(self, node: ast.Call) -> None:
        name = callee(node)
        in_super_init = bool(self.stack) and self.stack[-1] == "__init__"
        if self.shared:
            if name in {"SemanticEvidenceError"} | set(FACTORY_POS):
                channel, code = classify_code(code_expr(node))
                if channel == "coded":
                    channel = "shared-evidence" if code.isupper() else "shared-profile"
                self.add(node, channel, code, name or "?")
        elif name in FACTORY_POS or (name in CODE_TAKING and not in_super_init):
            if name == "Diagnostic" and not node.args and not any(kw.arg == "code" for kw in node.keywords):
                pass  # not an elaboration Diagnostic
            else:
                channel, code = classify_code(code_expr(node))
                self.add(node, channel, code, name or "?")
        elif name in self.fixed:
            self.add(node, "coded-fixed", self.fixed[name], name)
        self.generic_visit(node)

    def visit_Raise(self, node: ast.Raise) -> None:
        if not self.shared and node.exc is not None:
            target = node.exc.func if isinstance(node.exc, ast.Call) else node.exc
            name = (
                target.id
                if isinstance(target, ast.Name)
                else target.attr
                if isinstance(target, ast.Attribute)
                else None
            )
            if name in FREE_TEXT:
                self.add(node, "free-text", name, name)
            elif name in BUILTIN:
                self.add(node, "builtin", name, name)
        self.generic_visit(node)


def inventory(codegen_root: Path, ambse_root: Path) -> list[dict[str, str]]:
    cg_files = sorted(
        p
        for p in (codegen_root / "sysml_codegen").rglob("*.py")
        if not any(str(p.relative_to(codegen_root)).replace("sysml_codegen/", "", 1).startswith(e) for e in EXCLUDE)
    )
    am_files = sorted((ambse_root / "agentic_mbse").rglob("*.py"))
    fixed = fixed_code_classes(cg_files)
    found = factories(cg_files + am_files)
    FACTORY_POS.clear()
    FACTORY_POS.update(found)
    rows: list[dict[str, str]] = []
    for files, root, shared in ((cg_files, codegen_root, False), (am_files, ambse_root, True)):
        for path in files:
            tree = ast.parse(path.read_text())
            CTX["returners"], CTX["tables"] = code_returners(tree), code_tables(tree)
            v = Visitor(str(path.relative_to(root)), fixed, shared=shared)
            v.visit(tree)
            rows += v.rows
    return rows


def main() -> None:
    codegen_root, ambse_root, out_csv = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    rows = inventory(codegen_root, ambse_root)
    with out_csv.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"total sites: {len(rows)}")
    print("\n== per channel ==")
    for ch, n in Counter(r["channel"] for r in rows).most_common():
        print(f"{n:5d}  {ch}")
    print("\n== per code (coded, coded-fixed, shared-evidence) ==")
    for code, n in Counter(
        c for r in rows if r["channel"] in {"coded", "coded-fixed", "shared-evidence", "shared-profile", "coded-returned", "coded-mapped"} for c in r["code"].split("|")
    ).most_common():
        print(f"{n:5d}  {code}")
    print("\n== free-text sites per class ==")
    for code, n in Counter(r["code"] for r in rows if r["channel"] == "free-text").most_common():
        print(f"{n:5d}  {code}")
    members: dict[str, str] = {}
    for root in (codegen_root, ambse_root):
        for path in root.rglob("*.py"):
            for cls in ast.walk(ast.parse(path.read_text())):
                if isinstance(cls, ast.ClassDef) and cls.name in CODE_ENUMS:
                    for st in cls.body:
                        if isinstance(st, ast.Assign) and isinstance(st.targets[0], ast.Name):
                            members[st.targets[0].id] = cls.name
    origin = {
        c
        for r in rows
        if r["channel"] in {"coded", "coded-fixed", "shared-evidence", "coded-returned", "coded-mapped"}
        for c in r["code"].split("|")
    }
    missing = sorted(m for m in members if m not in origin)
    print(f"\n== enum members with NO literal origin site: {len(missing)} of {len(members)} ==")
    for m in missing:
        print(f"  {members[m]}.{m}")
    print(f"\nfactories detected (code param position): {dict(sorted(FACTORY_POS.items()))}")
    print("\n== non-literal code sites (everything that is not a literal at the site) ==")
    for r in rows:
        if r["channel"] in {"coded-relay", "coded-DYNAMIC", "coded-returned", "coded-mapped", "plumbing"}:
            print(f"  {r['channel']:14s} {r['file']}:{r['line']}  {r['function']}  code={r['code']}")


if __name__ == "__main__":
    main()
