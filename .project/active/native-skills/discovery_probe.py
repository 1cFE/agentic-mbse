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
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("project", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    results = {"project": str(args.project), "versions": {client: subprocess.check_output([client, "--version"], text=True).strip() for client in ("claude", "codex")}, "clients": {}}
    with tempfile.TemporaryDirectory(prefix="mbse-native-discovery-") as scratch:
        for client in ("claude", "codex"):
            result = discover(args.project, Path(scratch), client)
            entries = result.get("skills" if client == "codex" else "commands", [])
            results["clients"][client] = {"names": sorted(item["name"] for item in entries), "errors": result.get("errors", []), "error": result.get("error")}
            if client == "claude":
                expected = {"python-debugger", "kerml-expert", "sysml-expert", "syside-expert", "sysmlv2-validator"}
                results["clients"][client]["expert_roles"] = sorted(expected.intersection(result["agents"]))
    args.output.write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps(results, indent=2))
    assert len(results["clients"]["codex"]["names"]) == 25
    assert len(results["clients"]["claude"]["names"]) == 18
    assert len(results["clients"]["claude"]["expert_roles"]) == 5
    assert all(not data["error"] and not data["errors"] for data in results["clients"].values())


if __name__ == "__main__":
    main()
