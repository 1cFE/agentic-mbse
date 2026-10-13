"""Compare two pytest junit XML files by test id, outcome, skip count and failure message.

Adoption rehearsal step 8a (design Appendix H3, DD15). Run it twice:

- ``junit-diff.py B.xml C.xml`` is the switch's pass rule. No test that passed in B may fail,
  error, skip or go missing in C, and a test failing in both must fail with the same message.
  The exit status is 1 when the rule is broken.
- ``junit-diff.py A.xml B.xml`` records B against A for the consequence note (step 9). It is
  not a gate on the move, so its exit status is only informational.

The output lists every changed outcome, every message difference among tests failing in both,
the tests only one side has, and the skip counts per side. Failure messages are compared after
masking pytest's per-run temporary directory and object addresses, the only parts of a message
that differ between two runs of one unchanged test. The directory is masked in both of the
forms messages carry it: absolute (``/tmp/pytest-of-USER/pytest-N/``) and relative to the
working directory (``../../pytest-of-USER/pytest-N/``), as integrate's evidence paths are.

Self-test: ``selftest/before.xml`` against ``selftest/after-holds.xml`` holds (exit 0), and
against ``selftest/after-broken.xml`` is broken four ways (exit 1). In both, ``test_fails_relative``
fails with a message that differs only in pytest's relative temporary path, and is not reported.
"""

from __future__ import annotations

import argparse
import re
import sys
import xml.etree.ElementTree as ElementTree
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

#: Outcomes a later run may not move a passing test to.
REGRESSED = ("failed", "error", "skipped", "missing")
#: Outcomes that count as failing; a test failing in both runs must fail the same way.
FAILING = ("failed", "error")
#: The per-run parts of a failure message: pytest's base temporary directory, absolute or
#: relative, and object addresses.
RUN_TOKENS = (
    (re.compile(r"/tmp/pytest-of-[^/\s]+/pytest-\d+/"), "<pytest-tmp>/"),
    (re.compile(r"(?:\.\./)+pytest-of-[^/\s]+/pytest-\d+/"), "<pytest-tmp>/"),
    (re.compile(r"\b0x[0-9a-f]{6,}\b"), "0x<address>"),
)


@dataclass(frozen=True)
class Result:
    outcome: str  # passed | failed | error | skipped
    message: str  # the failure, error or skip message; empty for a pass


def read_junit(path: Path) -> dict[str, Result]:
    """Every test case in a junit file, keyed ``classname::name``.

    A file naming one test id twice is refused: the comparison would silently keep one of them.
    """
    results: dict[str, Result] = {}
    for case in ElementTree.parse(path).getroot().iter("testcase"):
        test_id = f"{case.get('classname', '')}::{case.get('name', '')}"
        if test_id in results:
            raise SystemExit(f"{path}: test id {test_id} appears twice")
        results[test_id] = classify(case)
    return results


def classify(case: ElementTree.Element) -> Result:
    for tag, outcome in (("failure", "failed"), ("error", "error"), ("skipped", "skipped")):
        child = case.find(tag)
        if child is not None:
            return Result(outcome, mask(child.get("message") or (child.text or "").strip()))
    return Result("passed", "")


def mask(message: str) -> str:
    for pattern, replacement in RUN_TOKENS:
        message = pattern.sub(replacement, message)
    return message


def compare(before: dict[str, Result], after: dict[str, Result]) -> tuple[list[str], list[str]]:
    """The report's lines, and the subset of them that break the pass rule."""
    lines: list[str] = []
    broken: list[str] = []
    counts = {side: Counter(r.outcome for r in results.values())
              for side, results in (("before", before), ("after", after))}
    for side, count in counts.items():
        tally = ", ".join(f"{k} {count[k]}" for k in ("passed", "failed", "error", "skipped"))
        lines.append(f"{side}: {sum(count.values())} tests; {tally}")
    for test_id in sorted(set(before) | set(after)):
        was = before.get(test_id)
        now = after.get(test_id, Result("missing", ""))
        if was is None:
            lines.append(f"only after: {test_id} ({now.outcome})")
            continue
        if was.outcome in FAILING and now.outcome in FAILING:
            if was != now:
                line = (f"failing in both, differently: {test_id}\n"
                        f"  before: {was.outcome}: {was.message}\n"
                        f"  after:  {now.outcome}: {now.message}")
                lines.append(line)
                broken.append(line)
        elif was.outcome != now.outcome:
            line = f"{was.outcome} -> {now.outcome}: {test_id}"
            if now.message:
                line += f" -- {now.message}"
            lines.append(line)
            if was.outcome == "passed" and now.outcome in REGRESSED:
                broken.append(line)
    return lines, broken


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("before", type=Path, help="the earlier run's junit XML (A, or B)")
    parser.add_argument("after", type=Path, help="the later run's junit XML (B, or C)")
    args = parser.parse_args(argv)
    lines, broken = compare(read_junit(args.before), read_junit(args.after))
    print("\n".join(lines))
    print(f"pass rule: {'BROKEN' if broken else 'holds'} "
          f"({len(broken)} test(s) passed before and did not after, or changed failure message)")
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
