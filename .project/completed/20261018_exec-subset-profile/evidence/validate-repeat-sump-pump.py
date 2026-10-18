import sys, subprocess, hashlib
from pathlib import Path
sys.path.insert(0, 'scripts/subset_profile')
from probe import child_env, export_tree, read_license_key, resolve_rev, REPO_ROOT
env = child_env(read_license_key())
for v in ("VIRTUAL_ENV","PYTHONPATH","PYTHONHOME","UV_PROJECT_ENVIRONMENT","CONDA_PREFIX"): env.pop(v, None)
work = Path('/tmp/p10/vd'); work.mkdir(exist_ok=True)
clis = {}
for label, rev in (('base','a718efec'),('final','9b123cf3')):
    dest = work/label
    if not dest.exists():
        export_tree(REPO_ROOT, resolve_rev(REPO_ROOT, rev), dest)
        subprocess.run(['uv','sync','--frozen'], cwd=dest, env=env, check=True, capture_output=True)
    clis[label] = dest/'.venv'/'bin'/'agentic-mbse'
target = work/'base'/'tests'/'fixtures'/'sump_pump'
for i in range(int(sys.argv[1]) if len(sys.argv) > 1 else 4):
    for label, cli in clis.items():
        r = subprocess.run([str(cli),'validate','--complete','--verbose',str(target)], cwd=target.parent, env=env, capture_output=True, text=True)
        out = r.stdout.replace(str(work/'base'),'<t>')
        l2 = [l for l in out.splitlines() if 'Unused definitions' in l or 'Malformed numerical:' in l]
        print(i, label, hashlib.sha1(out.encode()).hexdigest()[:8], l2)
