"""Print a compact summary of s1-results.json.  python3 s1_summarize.py [s1-results.json]"""
import json
import sys

d = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "s1-results.json"))
print({k: v for k, v in d.items() if k != "trees"})
for t in d["trees"]:
    print("=====", t["label"], t["export"]["commit"], "files", t["files"], "sibling_unchanged", t["sibling_unchanged"])
    print("skipped absolute links (outside models/):", len(t["export"]["skipped_absolute_links"]))
    print("settings", json.dumps(t["settings"]))
    for s in ("load", "extract", "evaluate", "string_id_run", "advisory_run"):
        print(s, {k: v for k, v in t.get(s, {}).items() if k != "traceback"})
    c = t.get("contract")
    if c:
        print({k: v for k, v in c.items() if k != "unverified_entries"})
        for u in c["unverified_entries"][:4]:
            print("  unverified:", u["rule"], u["context"], u["cause"], u["detail"][:160], "|", u["subject"])
    s = t.get("string_id_match")
    if s:
        keys = ("attrs_checked", "legacy_unextractable_issues", "legacy_flagged_with_id", "string_findings", "legacy_ids_in_string_ids", "legacy_not_string")
        print("strings", {k: s[k] for k in keys}, "string_not_legacy", len(s["string_not_legacy"]))
    a = t["advisories"]
    print("advisories: sites", a["sites"], "sum_sites", a["sum_sites"], "opaque", len(a["opaque_firings"]), a["opaque_firings"][:5])
    print("  wrappers", len(a["wrapper_firings"]), a["wrapper_firings"][:5])
    print("  walker failures", a["walker_failures"], a["walker_failure_examples"])
