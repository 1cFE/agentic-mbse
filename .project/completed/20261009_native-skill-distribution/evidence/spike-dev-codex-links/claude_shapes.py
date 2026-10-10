"""Spike: which .claude/skills link shapes does Claude Code list? Uses the probe's initialize control request."""
import json, os, selectors, shutil, subprocess, sys, tempfile, time
from pathlib import Path

def skill(d: Path, n: str):
    d.mkdir(parents=True, exist_ok=True)
    (d / "SKILL.md").write_text(f"---\nname: {n}\ndescription: spike skill {n}\n---\n\nBody of {n}.\n")

def build(base: Path):
    if base.exists(): shutil.rmtree(base)
    co, proj = base / "checkout" / "skills", base / "project"
    proj.mkdir(parents=True); subprocess.run(["git", "init", "-q", str(proj)], check=True)
    A, C = proj / ".agents" / "skills", proj / ".claude" / "skills"
    A.mkdir(parents=True); C.mkdir(parents=True)
    rel = lambda frm, to: os.path.relpath(to, frm.parent)
    cases = {}
    # today's --dev: .claude alias -> real .agents dir whose SKILL.md is an absolute file link out
    n = "ca-today-dev"; cases[n] = "alias -> .agents/skills/n (real dir, SKILL.md file link out)"
    skill(co / n, n); (A / n).mkdir(); (A / n / "SKILL.md").symlink_to(co / n / "SKILL.md"); (C / n).symlink_to(rel(C / n, A / n))
    # proposed --dev: .claude alias -> .agents/skills/n, which is an absolute folder link out
    n = "cb-alias-to-dirlink"; cases[n] = "alias -> .agents/skills/n, which is an absolute folder link out (proposed --dev)"
    skill(co / n, n); (A / n).symlink_to(co / n); (C / n).symlink_to(rel(C / n, A / n))
    # direct absolute folder link out (old main --dev shape)
    n = "cc-dir-abs-out"; cases[n] = ".claude/skills/n absolute folder link out"
    skill(co / n, n); (C / n).symlink_to(co / n)
    # control
    n = "cd-real"; cases[n] = "real dir"; skill(C / n, n)
    return proj, cases

def claude_commands(project: Path):
    env = dict(os.environ); cfg = Path(tempfile.mkdtemp(prefix="claude-cfg-"))
    env["CLAUDE_CONFIG_DIR"] = str(cfg); env.pop("CLAUDECODE", None)
    proc = subprocess.Popen(["claude", "-p", "--input-format", "stream-json", "--output-format", "stream-json",
                             "--verbose", "--setting-sources", "project"], cwd=project, env=env,
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    sel = selectors.DefaultSelector(); sel.register(proc.stdout, selectors.EVENT_READ)
    try:
        proc.stdin.write(json.dumps({"type": "control_request", "request_id": "init", "request": {"subtype": "initialize"}}) + "\n"); proc.stdin.flush()
        end = time.monotonic() + 40
        while time.monotonic() < end:
            if sel.select(1):
                line = proc.stdout.readline()
                if not line: break
                try: m = json.loads(line)
                except ValueError: continue
                if m.get("type") == "control_response":
                    return m["response"].get("response", {}).get("commands", [])
        raise RuntimeError("timeout")
    finally:
        proc.terminate(); proc.wait(timeout=5); shutil.rmtree(cfg, ignore_errors=True)

base = Path(sys.argv[1]); proj, cases = build(base)
names = {c["name"] for c in claude_commands(proj)}
out = {"claude": subprocess.check_output(["claude", "--version"], text=True).strip(),
       "cases": {n: {"shape": d, "listed": n in names} for n, d in cases.items()}}
print(json.dumps(out, indent=2)); (base / "result.json").write_text(json.dumps(out, indent=2) + "\n")
