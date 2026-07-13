"""S2 provisional ExpressionIR: extract / serialize / compile.

Throwaway spike code. The node algebra follows the concept's requirements
(literal, feature reference, n-ary operator, invocation, unit annotation,
explicit unsupported node); the exact field shapes are PROVISIONAL pending S1.

Three pieces:
- IRNode (pydantic): serializable tree, canonical JSON via model_dump_json.
- extract_ir(): live syside expression node -> IRNode. No evaluator calls.
- compile_predicate(): IRNode -> generated Python source implementing the
  documented three-valued (Kleene) semantics: any non-finite operand makes its
  own leaf comparison unknown (None); unknown propagates only where a
  connective needs it (Kleene and/or/not). Margin only for simple-inequality
  roots, sign fixed by structure and flipped under negated assertion polarity.
"""

from __future__ import annotations

import math
from typing import Any, Literal, Optional

from pydantic import BaseModel

from agentic_mbse.sysml.syside_adapter import SysideAdapter

# --- IR ---------------------------------------------------------------------

COMPARISON_OPS = {"<", "<=", ">", ">=", "==", "!="}
LOGICAL_OPS = {"and", "or", "not", "xor", "implies"}
ARITHMETIC_OPS = {"+", "-", "*", "/", "**", "^"}


class IRNode(BaseModel):
    """One node of the provisional ExpressionIR. Tagged union via `kind`."""

    kind: Literal[
        "literal", "feature_ref", "op", "invocation", "unit", "unsupported"
    ]
    # literal
    value: Optional[float | int | bool | str] = None
    value_type: Optional[str] = None  # "real" | "integer" | "boolean" | "string"
    # feature_ref — source name + qualified target; NOT pre-classified
    source_name: Optional[str] = None
    target_qn: Optional[list[str]] = None
    segments: Optional[list[str]] = None
    # op — n-ary preserved, operator normalized to SysML symbol text
    operator: Optional[str] = None
    operands: Optional[list["IRNode"]] = None
    # invocation
    function_qn: Optional[list[str]] = None
    arguments: Optional[list["IRNode"]] = None
    # unit annotation: operands[0] is the value subtree
    unit_text: Optional[str] = None
    # unsupported — structural diagnostic
    node_type: Optional[str] = None
    diagnostic: Optional[str] = None

    def to_json(self) -> str:
        return self.model_dump_json(exclude_none=True)

    @classmethod
    def from_json(cls, text: str) -> "IRNode":
        return cls.model_validate_json(text)


# --- syside -> IR extraction --------------------------------------------------

# syside 0.8.4 Operator enum -> SysML symbol text (filled by observation in
# probe 2; str() on the enum is checked there and this map is the fallback).
_OPERATOR_ENUM_MAP = {
    "LessEqual": "<=",
    "GreaterEqual": ">=",
    "Less": "<",
    "Greater": ">",
    "Equal": "==",
    "NotEqual": "!=",
    "Plus": "+",
    "Minus": "-",
    "Multiply": "*",
    "Divide": "/",
    "Power": "**",
    "Caret": "^",
    "And": "and",
    "Or": "or",
    "Not": "not",
    "Xor": "xor",
    "Implies": "implies",
    "Index": "[",
}


def _operator_text(raw: Any) -> str:
    s = str(raw)
    if s.startswith("Operator."):
        name = s.split(".", 1)[1]
        return _OPERATOR_ENUM_MAP.get(name, name)
    return s


def extract_ir(node: Any) -> IRNode:
    """Convert a live syside expression node to the provisional IR.

    Structural only — never invokes the evaluator. Unknown constructs become
    explicit `unsupported` nodes carrying a diagnostic, mirroring the concept's
    requirement that silence is never an outcome.
    """
    # FeatureChainExpression before OperatorExpression (FCE subtypes OE).
    if SysideAdapter.is_instance(node, "FeatureChainExpression"):
        from agentic_mbse.sysml.expression import extract_feature_chain_segments

        segments = extract_feature_chain_segments(node)
        return IRNode(
            kind="feature_ref",
            source_name=".".join(segments) if segments else None,
            segments=segments or None,
        )

    if SysideAdapter.is_instance(node, "OperatorExpression"):
        op = _operator_text(getattr(node, "operator", None))
        operands = [extract_ir(o) for o in list(getattr(node, "operands", []) or [])]
        if op == "[":
            # unit annotation: value operand + unit ref
            unit_text = None
            if len(operands) > 1 and operands[1].kind == "feature_ref":
                unit_text = operands[1].source_name
            return IRNode(kind="unit", operands=[operands[0]], unit_text=unit_text)
        return IRNode(kind="op", operator=op, operands=operands)

    if SysideAdapter.is_instance(node, "FeatureReferenceExpression"):
        referent = getattr(node, "referent", None)
        name = getattr(referent, "name", None) if referent is not None else None
        qn = getattr(referent, "qualified_name", None) if referent is not None else None
        qn_parts: list[str] | None = None
        if qn is not None:
            try:
                qn_parts = [str(p) for p in qn]
            except TypeError:
                qn_parts = [str(qn)]
        return IRNode(kind="feature_ref", source_name=name, target_qn=qn_parts)

    if SysideAdapter.is_instance(node, "LiteralRational"):
        return IRNode(kind="literal", value=float(node.value), value_type="real")
    if SysideAdapter.is_instance(node, "LiteralInteger"):
        return IRNode(kind="literal", value=int(node.value), value_type="integer")
    if SysideAdapter.is_instance(node, "LiteralBoolean"):
        return IRNode(kind="literal", value=bool(node.value), value_type="boolean")
    if SysideAdapter.is_instance(node, "LiteralString"):
        return IRNode(kind="literal", value=str(node.value), value_type="string")

    if hasattr(node, "function") and hasattr(node.function, "name"):
        args = [extract_ir(o) for o in list(getattr(node, "operands", []) or [])]
        fqn = getattr(node.function, "qualified_name", None)
        return IRNode(
            kind="invocation",
            function_qn=[str(p) for p in fqn] if fqn is not None else None,
            arguments=args,
        )

    tname = type(node).__name__
    return IRNode(
        kind="unsupported", node_type=tname, diagnostic=f"unknown node type: {tname}"
    )


# --- IR -> Python (Kleene three-valued predicate semantics) -------------------

_KLEENE_RUNTIME = '''
import math

def _fin(x):
    return isinstance(x, (int, float)) and math.isfinite(x)

def _cmp(op, a, b):
    """Leaf comparison: unknown (None) if either operand is non-finite."""
    if not _fin(a) or not _fin(b):
        return None
    if op == "<=": return a <= b
    if op == ">=": return a >= b
    if op == "<":  return a < b
    if op == ">":  return a > b
    if op == "==": return a == b
    if op == "!=": return a != b
    raise ValueError(f"not a comparison: {op}")

def _and(*vals):
    if any(v is False for v in vals): return False
    if any(v is None for v in vals): return None
    return True

def _or(*vals):
    if any(v is True for v in vals): return True
    if any(v is None for v in vals): return None
    return False

def _not(v):
    return None if v is None else (not v)
'''


class PredicateCompileError(Exception):
    pass


def _compile_numeric(n: IRNode) -> str:
    """Numeric (float-valued) subtree -> plain Python expression."""
    if n.kind == "literal":
        if n.value_type in ("real", "integer"):
            return repr(n.value)
        raise PredicateCompileError(f"non-numeric literal in numeric position: {n.value_type}")
    if n.kind == "feature_ref":
        if n.segments:
            raise PredicateCompileError("feature chain not supported in profile v1")
        return n.source_name or "_unnamed"
    if n.kind == "unit":
        return _compile_numeric(n.operands[0])
    if n.kind == "op":
        if n.operator in ARITHMETIC_OPS:
            py_op = "**" if n.operator in ("**", "^") else n.operator
            if len(n.operands) == 1:
                return f"(-{_compile_numeric(n.operands[0])})"
            parts = [_compile_numeric(o) for o in n.operands]
            # n-ary left-fold, matching today's compiler
            expr = parts[0]
            for p in parts[1:]:
                expr = f"({expr} {py_op} {p})"
            return expr
        raise PredicateCompileError(f"operator {n.operator!r} in numeric position")
    raise PredicateCompileError(f"{n.kind} in numeric position")


def _compile_boolean(n: IRNode) -> str:
    """Boolean-valued subtree -> three-valued Python expression."""
    if n.kind == "op" and n.operator in COMPARISON_OPS:
        if n.operator in ("==", "!="):
            raise PredicateCompileError(
                "equality blocked in profile v1 (type-proof pending S1)"
            )
        a = _compile_numeric(n.operands[0])
        b = _compile_numeric(n.operands[1])
        return f"_cmp({n.operator!r}, {a}, {b})"
    if n.kind == "op" and n.operator in ("and", "or"):
        fn = "_and" if n.operator == "and" else "_or"
        parts = ", ".join(_compile_boolean(o) for o in n.operands)
        return f"{fn}({parts})"
    if n.kind == "op" and n.operator == "not":
        return f"_not({_compile_boolean(n.operands[0])})"
    if n.kind == "literal" and n.value_type == "boolean":
        return repr(n.value)
    raise PredicateCompileError(f"unsupported boolean node: {n.kind}/{n.operator}")


def _leaf_ref_names(n: IRNode, acc: list[str]) -> None:
    if n.kind == "feature_ref" and n.source_name and n.source_name not in acc:
        acc.append(n.source_name)
    for child in (n.operands or []) + (n.arguments or []):
        _leaf_ref_names(child, acc)


def margin_expression(n: IRNode, negated: bool) -> str | None:
    """Signed margin for a simple-inequality root; None for compound shapes.

    Sign convention: positive margin <=> assertion satisfied. A negated
    assertion flips the sign.
    """
    if n.kind != "op" or n.operator not in ("<", "<=", ">", ">="):
        return None
    a = _compile_numeric(n.operands[0])
    b = _compile_numeric(n.operands[1])
    raw = f"({b} - {a})" if n.operator in ("<", "<=") else f"({a} - {b})"
    body = f"(-{raw})" if negated else raw
    return (
        f"({body} if (_fin({a}) and _fin({b})) else None)"
    )


def compile_predicate(
    ir: IRNode, fn_name: str, negated: bool = False
) -> tuple[str, list[str]]:
    """Generate Python source for one predicate.

    Returns (source, arg_names). The generated function returns a dict:
    {"value": raw predicate value (True/False/None),
     "status": satisfied|violated|indeterminate (polarity applied),
     "margin": signed float or None}.
    """
    args: list[str] = []
    _leaf_ref_names(ir, args)
    body = _compile_boolean(ir)
    margin = margin_expression(ir, negated) or "None"
    expected = "False" if negated else "True"
    src = f'''{_KLEENE_RUNTIME}

def {fn_name}({", ".join(args)}):
    value = {body}
    if value is None:
        status = "indeterminate"
    elif value == {expected}:
        status = "satisfied"
    else:
        status = "violated"
    return {{"value": value, "status": status, "margin": {margin}}}
'''
    return src, args


def load_predicate(src: str, fn_name: str):
    ns: dict[str, Any] = {"math": math}
    exec(src, ns)  # noqa: S102 — spike scratch code
    return ns[fn_name]
