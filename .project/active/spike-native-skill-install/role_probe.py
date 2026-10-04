"""Check native custom agent registration without starting a model turn."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import yaml
from probe import BASE, REPO, discover

results = {}
with tempfile.TemporaryDirectory(prefix='roles-', dir=BASE) as scratch:
    root = Path(scratch)
    project = root / 'project'
    project.mkdir()
    subprocess.run(['git', 'init', '-q', str(project)], check=True)
    for platform in ['.claude', '.codex']:
        (project / platform / 'agents').mkdir(parents=True)
    expected = []
    for source in (REPO / 'claude/agents').glob('*.md'):
        _, header, body = source.read_text().split('---', 2)
        meta = yaml.safe_load(header)
        expected.append(meta['name'])
        body = body.replace('{SYSML_DOCS_PATH}', str(REPO / 'docs/sysmlv2')).replace('{SYSIDE_DOCS_PATH}', str(REPO / 'docs/syside'))
        (project / '.claude/agents' / source.name).write_text('---' + header + '---' + body)
        # Research sketch: preserve role text; read-only sandbox approximates expert write restriction.
        role = {'name': meta['name'], 'description': meta['description'], 'developer_instructions': body}
        if 'Bash' not in meta['tools']:
            role['sandbox_mode'] = 'read-only'
        (project / '.codex/agents' / (source.stem + '.toml')).write_text('\n'.join(k + ' = ' + json.dumps(v) for k, v in role.items()) + '\n')
    results['claude'] = discover(project, root / 'config', 'claude')
    codex_home = root / 'config/codex'
    codex_home.mkdir(parents=True, exist_ok=True)
    (codex_home / 'config.toml').write_text('[projects.' + json.dumps(str(project)) + ']\ntrust_level = "trusted"\n')
    env = dict(os.environ, CODEX_HOME=str(codex_home))
    result = subprocess.run(['codex', 'debug', 'prompt-input', 'Report no work.'], cwd=project, env=env, text=True, capture_output=True, timeout=30)
    results['codex'] = {'verdict': 'inconclusive: prompt-input does not expose a role catalog', 'returncode': result.returncode, 'role_names_in_prompt': {name: name in result.stdout for name in expected}, 'stderr': result.stderr[-2000:]}
    # Only named roles and registration results are retained, not unrelated user context.
    results['claude'] = {'registered_roles': [name for name in results['claude']['agents'] if name in expected]}
(BASE / 'role-results.json').write_text(json.dumps(results, indent=2) + '\n')
print(json.dumps(results, indent=2))
