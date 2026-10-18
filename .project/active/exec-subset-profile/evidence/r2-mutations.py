"""Run R2 mutations in a scratch copy of agentic-mbse; print which tests catch each.

Usage: python mutate.py <scratch-dir>. The scratch dir is a git repo whose HEAD is the clean
baseline; every mutation is reverted with `git checkout -- . && git clean -fdq` afterwards.
"""
import json, re, subprocess, sys
from pathlib import Path

S = Path(sys.argv[1])
RULES = S / "src/agentic_mbse/sysml/subset_profile_rules.toml"
PROFILE = S / "src/agentic_mbse/sysml/subset_profile.py"
PROBES = S / "tests/fixtures/subset_profile/probes"
TESTS = ["tests/test_subset_probe_evidence.py", "tests/test_subset_matrix.py", "tests/test_sysml/"]

def sub(path, old, new, count=1):
    text = path.read_text()
    assert text.count(old) >= 1, (path, old)
    path.write_text(text.replace(old, new, count))

def obs_edit(probe, fn):
    p = PROBES / probe / "observation.json"
    data = json.loads(p.read_text()); fn(data); p.write_text(json.dumps(data, indent=2) + "\n")

BIND_INST = 'context = "owner_instantiated"\noutcome = "refused"\nevidence = [\n    "probe:binding-source__expression_source__owner_instantiated",'
REFUSED_PROBE = "indexed-reference__indexed_reference__attribute_value"

def m1(): sub(RULES, BIND_INST, BIND_INST.replace('owner_instantiated",', 'owner_package",'))
def m2(): sub(RULES, '[[rule.shape.admission]]\ncontext = "attribute_value"\noutcome = "refused"\nevidence = ["probe:indexed-reference__indexed_reference__attribute_value"]',
              '[[rule.shape.admission]]\ncontext = "calc_result_expression"\noutcome = "refused"\nevidence = []\n\n[[rule.shape.admission]]\ncontext = "attribute_value"\noutcome = "refused"\nevidence = ["probe:indexed-reference__indexed_reference__attribute_value"]')
def m3(): sub(RULES, BIND_INST, BIND_INST + '\n    "probe:binding-source__expression_source__owner_instantiated__nonexistent",')
def m4():  # (a') an admitted pair flipped to refused, keeping its own probe
    sub(RULES, 'context = "owner_uninstantiated"\noutcome = "admitted"\nevidence = [\n    "probe:binding-source__expression_source__owner_uninstantiated"',
        'context = "owner_uninstantiated"\noutcome = "refused"\nevidence = [\n    "probe:binding-source__expression_source__owner_uninstantiated"')
def m4b():  # S1: the omitted partner flipped to refused
    sub(RULES, 'context = "other_expression_site"\noutcome = "omitted"\nevidence = ["probe:indexed-reference__indexed_reference__other_expression_site"]',
        'context = "other_expression_site"\noutcome = "refused"\nevidence = ["probe:indexed-reference__indexed_reference__other_expression_site"]')
def m5():
    def f(d):
        d["run"]["error_lines"] = [l.replace("SI_INDEXED_SOURCE_UNSUPPORTED", "SI_EXPRESSION_SOURCE_UNSUPPORTED") for l in d["run"]["error_lines"]]
    obs_edit(REFUSED_PROBE, f)
def m6a(): (PROBES / REFUSED_PROBE / "observation.json").unlink()
def m6b(): obs_edit(REFUSED_PROBE, lambda d: d.__setitem__("certifies", False))
def m7():
    def f(d):
        d["run"]["error_lines"] = [re.sub(r"model\.sysml:(\d+)", "model.sysml:99", l) for l in d["run"]["error_lines"]]
    obs_edit(REFUSED_PROBE, f)
def m8(): sub(PROFILE, "return _Placement(ContextId.OWNER_UNINSTANTIATED, 0, ())", "return _Placement(ContextId.OWNER_INSTANTIATED, 0, ())")
def m9(): sub(PROFILE, "            return self.constraint_placement(consumer.element_id)\n        return _Placement(ContextId.OWNER_OTHER, None, ())",
              "            return self.constraint_placement(consumer.element_id)\n        return _Placement(ContextId.OWNER_INSTANTIATED, None, ())")
def m10():  # S1 omission check: the dropped literal shows up in the output
    obs_edit("invocation-callable__unsupported_callable__other_expression_site",
             lambda d: d["run"]["mentions"].__setitem__("4271.5", ["modules/fx/twice.py"]))
def m11(): sub(PROFILE, "    if refused and not not_refused_by_probe and no_admitted is None:", "    if False:")
def m12(): sub(PROFILE, "        if Outcome.REFUSED in outcomes:\n            return Verdict.REFUSED_INCOMPLETE\n", "")

MUTATIONS = [
    ("m1", "Refused admission citing an unrelated probe", m1),
    ("m2", "New refused admission with no evidence", m2),
    ("m3", "Refused admission citing a nonexistent probe whose id has the right prefix", m3),
    ("m4", "(a') An admitted pair flipped to refused, keeping its own probe", m4),
    ("m4b", "S1: the omitted partner flipped to refused (shape left with no non-refused probe)", m4b),
    ("m5", "Observed code changed in a refused probe's observation", m5),
    ("m6a", "A cited observation deleted", m6a),
    ("m6b", "A cited observation's certifies flipped to false", m6b),
    ("m7", "Error line moved outside the construct", m7),
    ("m8", "Unreached owner placed as instantiated (_unreached)", m8),
    ("m9", "consumer_placement fallback changed to OWNER_INSTANTIATED (audit A2)", m9),
    ("m10", "S1 omission: the dropped literal is mentioned in a generated file", m10),
    ("m11", "Loader gate for a non-refused partner removed", m11),
    ("m12", "S3: INCOMPLETE outranks REFUSED again", m12),
]

def run():
    r = subprocess.run(["uv", "run", "--frozen", "pytest", *TESTS, "-q", "-p", "no:cacheprovider", "-rfE", "--no-header"],
                       cwd=S, capture_output=True, text=True)
    out = r.stdout + r.stderr
    caught = sorted({m.group(1) for m in re.finditer(r"^(?:FAILED|ERROR) (\S+)", out, re.M)})
    summary = [l for l in out.splitlines() if re.search(r"\d+ (passed|failed|error)", l)]
    return r.returncode, caught, (summary[-1] if summary else out[-500:])

only = sys.argv[2:] or None
code, caught, summary = run()
print(f"baseline: exit {code}; {summary}")
if code != 0:
    print("\n".join(caught)); sys.exit("baseline not green")
for key, label, fn in MUTATIONS:
    if only and key not in only: continue
    fn()
    code, caught, summary = run()
    subprocess.run("git checkout -q -- . && git clean -fdq", shell=True, cwd=S, check=True)
    print(f"\n## {key}: {label}\nexit {code}; {summary}\ncaught by {len(caught)}:")
    for c in caught[:12]: print("  " + c)
    if len(caught) > 12: print(f"  ... and {len(caught) - 12} more")
