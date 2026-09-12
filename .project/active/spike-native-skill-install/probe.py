"""Throwaway native-client discovery probe; no model turns or credentials required."""
import json
import os
from pathlib import Path
import selectors
import shutil
import subprocess
import tempfile
import time

BASE = Path(__file__).resolve().parent
REPO = BASE.parents[2]


def summarize(response, client):
    if client == 'codex':
        return {'skills': [s for d in response.get('result', {}).get('data', [])
                           for s in d['skills'] if s.get('scope') == 'repo'],
                'errors': [e for d in response.get('result', {}).get('data', [])
                           for e in d.get('errors', [])], 'error': response.get('error')}
    data = response.get('response', {}).get('response', {})
    return {'commands': [s for s in data.get('commands', [])
                         if '(project)' in s.get('description', '')],
            'agents': [a['name'] for a in data.get('agents', [])],
            'error': response.get('response', {}).get('error')}


def receive(proc, predicate, timeout=25):
    selector = selectors.DefaultSelector()
    selector.register(proc.stdout, selectors.EVENT_READ)
    deadline = time.monotonic() + timeout
    seen = []
    while time.monotonic() < deadline:
        if selector.select(min(1, deadline - time.monotonic())):
            line = proc.stdout.readline()
            if not line:
                break
            try:
                message = json.loads(line)
            except ValueError:
                continue
            seen.append(message)
            if predicate(message):
                return message
    raise RuntimeError(f'No matching response; received {seen!r}')


def send(proc, message):
    proc.stdin.write(json.dumps(message) + '\n')
    proc.stdin.flush()


def discover(project, config, client):
    env = dict(os.environ)
    env['CODEX_HOME'] = str(config / 'codex')
    env['CLAUDE_CONFIG_DIR'] = str(config / 'claude')
    env.pop('CLAUDECODE', None)
    for folder in ['codex', 'claude']:
        (config / folder).mkdir(parents=True, exist_ok=True)
    args = ['codex', 'app-server', '--stdio'] if client == 'codex' else [
        'claude', '-p', '--input-format', 'stream-json', '--output-format',
        'stream-json', '--verbose', '--setting-sources', 'project']
    with tempfile.TemporaryFile(mode='w+') as err:
        proc = subprocess.Popen(args, cwd=project, env=env, stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=err, text=True)
        try:
            if client == 'codex':
                send(proc, {'id': 1, 'method': 'initialize', 'params': {
                    'clientInfo': {'name': 'mbse-spike', 'version': '0.1'},
                    'capabilities': {'experimentalApi': True}}})
                receive(proc, lambda m: m.get('id') == 1)
                send(proc, {'method': 'initialized', 'params': {}})
                send(proc, {'id': 2, 'method': 'skills/list', 'params': {
                    'cwds': [str(project)], 'forceReload': True}})
                return summarize(receive(proc, lambda m: m.get('id') == 2), client)
            send(proc, {'type': 'control_request', 'request_id': 'init',
                        'request': {'subtype': 'initialize'}})
            return summarize(receive(proc, lambda m: m.get('type') == 'control_response'), client)
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()


def main():
    results = {'versions': {c: subprocess.check_output([c, '--version'], text=True).strip()
                            for c in ['codex', 'claude']}, 'cases': {}}
    with tempfile.TemporaryDirectory(prefix='fixture-', dir=BASE) as scratch:
        root = Path(scratch)
        project = root / 'project'
        project.mkdir()
        subprocess.run(['git', 'init', '-q', str(project)], check=True)
        shared = project / '.agents/skills/mbse-probe'
        shared.mkdir(parents=True)
        (shared / 'SKILL.md').write_text('---\nname: mbse-probe\ndescription: MBSE shared skill discovery sentinel\nallowed-tools: [Read, Grep]\nuser-invocable: true\nskills: [missing-probe-dependency]\n---\nRead references/sentinel.txt.\n')
        (shared / 'references').mkdir()
        (shared / 'references/sentinel.txt').write_text('MBSE_REFERENCE_SENTINEL\n')
        claude_skills = project / '.claude/skills'
        claude_skills.mkdir(parents=True)
        (claude_skills / 'mbse-probe').symlink_to('../../.agents/skills/mbse-probe', target_is_directory=True)
        for case in ['shared-relative', 'relocated', 'both-symlinked', 'legacy-duplicate', 'full-catalog', 'copy-fallback']:
            if case == 'relocated':
                moved = root / 'relocated-project'
                project.rename(moved)
                project = moved
            if case == 'both-symlinked':
                neutral = project / 'shared/mbse-probe'
                neutral.parent.mkdir()
                (project / '.agents/skills/mbse-probe').rename(neutral)
                (project / '.agents/skills/mbse-probe').symlink_to('../../shared/mbse-probe', target_is_directory=True)
            if case == 'legacy-duplicate':
                legacy = project / '.claude/commands'
                legacy.mkdir()
                (legacy / 'mbse-probe.md').write_text('---\nname: mbse-probe\ndescription: LEGACY_SENTINEL\n---\nLegacy command.\n')
            if case == 'full-catalog':
                for command in (REPO / 'claude/commands').glob('*.md'):
                    dest = project / '.agents/skills' / command.stem
                    dest.mkdir()
                    (dest / 'SKILL.md').write_text(command.read_text())
                for source in (REPO / 'claude/skills').iterdir():
                    if source.is_dir():
                        shutil.copytree(source, project / '.agents/skills' / source.name)
                for source in (project / '.agents/skills').iterdir():
                    alias = project / '.claude/skills' / source.name
                    if not alias.exists():
                        alias.symlink_to('../../.agents/skills/' + source.name, target_is_directory=True)
            if case == 'copy-fallback':
                for alias in (project / '.claude/skills').iterdir():
                    resolved = alias.resolve()
                    alias.unlink()
                    shutil.copytree(resolved, alias)
            results['cases'][case] = {}
            for client in ['codex', 'claude']:
                try:
                    results['cases'][case][client] = discover(project, root / 'config', client)
                except Exception as exc:
                    results['cases'][case][client] = {'probe_error': str(exc)}
            results['cases'][case]['reference_read'] = (project / '.claude/skills/mbse-probe/references/sentinel.txt').read_text().strip()
    (BASE / 'results.json').write_text(json.dumps(results, indent=2) + '\n')
    for name, case in results['cases'].items():
        print(name, {client: len(case[client].get('skills' if client == 'codex' else 'commands', [])) for client in ['codex', 'claude']})


if __name__ == '__main__':
    main()
