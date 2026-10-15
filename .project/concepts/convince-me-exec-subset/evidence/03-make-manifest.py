"""C3 step 3a: write 03-manifest.yaml, one honest category per inventoried fence.

The categories come from what the fence actually does today (03-inventory.csv and
03-elaboration.json), not from what its prose claims. In the end state a person
reviews each entry; here the point is only that a complete, honest manifest exists
and that the harness built on it passes.

    uv run python .project/concepts/convince-me-exec-subset/evidence/03-make-manifest.py
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent


def main() -> None:
    inv = list(csv.DictReader((HERE / "03-inventory.csv").open()))
    runs = json.loads((HERE / "03-elaboration.json").read_text())
    final = {}
    for r in runs:  # the context run, when there is one, is the one that counts
        if r["idx"] not in final or r["context"]:
            final[r["idx"]] = r
    entries = []
    for row in inv:
        idx = int(row["idx"])
        entry: dict = {"id": row["id"]}
        ctx = sorted(p.name for p in (HERE / "03-contexts").glob(f"{idx:03d}.*.sysml"))
        if ctx:
            entry["context"] = ctx
        if not row["status"].startswith("complete") and not ctx:
            entry["category"] = "fragment"
            entry["reason"] = (
                "does not parse standalone" if row["status"] == "syntax-fragment"
                else "parses, but names definitions it does not include"
            )
        else:
            r = final[idx]
            entry["wrapped"] = row["status"] == "complete-wrapped" or bool(ctx)
            outcome = r["generate_outcome"]
            if outcome == "generated":
                entry["category"] = "executable"
                if idx == 10:
                    entry["must_emit"] = ["mass"]
                    entry["omits"] = ["material"]  # String: dropped silently today
            elif outcome == "nothing-to-generate":
                entry["category"] = "definition"
            else:
                entry["category"] = "negative" if row["negative_marked"] == "True" else "native-only"
                entry["expect_codes"] = r["generate_codes"]
                if outcome == "error":
                    entry["expect_message"] = "name-safety violation"
        entries.append(entry)
    (HERE / "03-manifest.yaml").write_text(yaml.safe_dump({"fences": entries}, sort_keys=False, width=200))
    counts: dict[str, int] = {}
    for e in entries:
        counts[e["category"]] = counts.get(e["category"], 0) + 1
    print(len(entries), counts)


if __name__ == "__main__":
    main()
