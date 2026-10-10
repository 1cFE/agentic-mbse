"""Spike: which link shapes does Codex's skills/list follow? No model turns, no credentials."""
import json, os, selectors, shutil, subprocess, sys, tempfile, time
from pathlib import Path

def rpc_skills(project: Path):
    env = dict(os.environ)
    home = Path(tempfile.mkdtemp(prefix="codex-home-"))
    env["CODEX_HOME"] = str(home)
    proc = subprocess.Popen(["codex", "app-server", "--stdio"], cwd=project, env=env, stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    sel = selectors.DefaultSelector(); sel.register(proc.stdout, selectors.EVENT_READ)
    def send(m): proc.stdin.write(json.dumps(m) + "\n"); proc.stdin.flush()
    def recv(i):
        end = time.monotonic() + 25
        while time.monotonic() < end:
            if sel.select(1):
                line = proc.stdout.readline()
                if not line: break
                try: m = json.loads(line)
                except ValueError: continue
                if m.get("id") == i: return m
        raise RuntimeError("timeout")
    try:
        send({"id": 1, "method": "initialize", "params": {"clientInfo": {"name": "spike", "version": "0"}, "capabilities": {"experimentalApi": True}}})
        recv(1); send({"method": "initialized", "params": {}})
        send({"id": 2, "method": "skills/list", "params": {"cwds": [str(project)], "forceReload": True}})
        return recv(2)
    finally:
        proc.terminate(); proc.wait(timeout=5); shutil.rmtree(home, ignore_errors=True)

def skill(dirpath: Path, name: str):
    dirpath.mkdir(parents=True, exist_ok=True)
    (dirpath / "SKILL.md").write_text(f"---\nname: {name}\ndescription: spike skill {name}\n---\n\nBody of {name}.\n")

def build(base: Path):
    checkout = base / "checkout"          # stands in for the agentic-mbse source checkout (outside the project)
    proj = base / "project"
    if base.exists(): shutil.rmtree(base)
    proj.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(proj)], check=True)
    A, C = proj / ".agents" / "skills", proj / ".claude" / "skills"
    A.mkdir(parents=True); C.mkdir(parents=True)
    shapes = {}
    def case(name, desc, make):
        shapes[name] = desc; make(name)
    def rel(frm: Path, to: Path): return os.path.relpath(to, frm.parent)
    # controls
    case("a-real", "real dir, real SKILL.md", lambda n: skill(A / n, n))
    case("b-dir-rel-in", "dir link, relative, to real dir in .claude/skills (fusion-tea's own shape)",
         lambda n: (skill(C / n, n), (A / n).symlink_to(rel(A / n, C / n))))
    # file links
    def file_link(n, target, absolute):
        (A / n).mkdir(); t = target; (A / n / "SKILL.md").symlink_to(t if absolute else rel(A / n / "SKILL.md", t))
    case("c-file-abs-out", "SKILL.md file link, absolute, outside project (today's --dev)",
         lambda n: (skill(checkout / "skills" / n, n), file_link(n, checkout / "skills" / n / "SKILL.md", True)))
    case("d-file-rel-out", "SKILL.md file link, relative, outside project",
         lambda n: (skill(checkout / "skills" / n, n), file_link(n, checkout / "skills" / n / "SKILL.md", False)))
    case("e-file-abs-in", "SKILL.md file link, absolute, to real file in .claude/skills",
         lambda n: (skill(C / n, n), file_link(n, C / n / "SKILL.md", True)))
    case("f-file-rel-in", "SKILL.md file link, relative, to real file in .claude/skills",
         lambda n: (skill(C / n, n), file_link(n, C / n / "SKILL.md", False)))
    # dir links
    case("g-dir-abs-out", "dir link, absolute, outside project",
         lambda n: (skill(checkout / "skills" / n, n), (A / n).symlink_to(checkout / "skills" / n)))
    case("h-dir-rel-out", "dir link, relative, outside project",
         lambda n: (skill(checkout / "skills" / n, n), (A / n).symlink_to(rel(A / n, checkout / "skills" / n))))
    case("i-dir-abs-in", "dir link, absolute, to real dir in .claude/skills",
         lambda n: (skill(C / n, n), (A / n).symlink_to(C / n)))
    # chains through .claude/skills
    case("j-chain-dir", ".agents dir link -> ../../.claude/skills/n, which is an absolute dir link outside",
         lambda n: (skill(checkout / "skills" / n, n), (C / n).symlink_to(checkout / "skills" / n), (A / n).symlink_to(rel(A / n, C / n))))
    case("k-chain-file", ".agents dir link -> ../../.claude/skills/n (real dir) whose SKILL.md is an absolute file link outside",
         lambda n: (skill(checkout / "skills" / n, n), (C / n).mkdir(), (C / n / "SKILL.md").symlink_to(checkout / "skills" / n / "SKILL.md"), (A / n).symlink_to(rel(A / n, C / n))))
    return proj, shapes

def main():
    base = Path(sys.argv[1])
    proj, shapes = build(base)
    resp = rpc_skills(proj)
    data = resp.get("result", {}).get("data", [])
    listed = {s["name"]: s for d in data for s in d["skills"]}
    errors = [e for d in data for e in d.get("errors", [])]
    out = {"codex": subprocess.check_output(["codex", "--version"], text=True).strip(), "cases": {}, "errors": errors, "rpc_error": resp.get("error")}
    for n, desc in shapes.items():
        s = listed.get(n)
        out["cases"][n] = {"shape": desc, "listed": bool(s), "scope": s and s.get("scope"), "path": s and s.get("path")}
    print(json.dumps(out, indent=2))
    (base / "result.json").write_text(json.dumps(out, indent=2) + "\n")
    print("\nother listed:", sorted(k for k in listed if k not in shapes))

main()
