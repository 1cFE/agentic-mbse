#!/bin/bash
# usage: run.sh NAME   (expects NAME/models/... already written)
P=/tmp/claude-1000/-home-reid-src-agentic-mbse/9366fe1c-453c-484d-b30e-782bbdd1390c/scratchpad/probes
N=$1
cd /home/reid/src/agentic-mbse
uv run --env-file .env agentic-mbse validate --complete --execution-target=generated --json-report=$P/$N/report.json $P/$N/models > $P/$N/validate.txt 2>&1
python3 -c "
import json,sys
d=json.load(open('$P/$N/report.json'))
for l in d['levels']:
    for i in l['issues']:
        if i['severity']=='error': print('VALIDATE ERROR', l['level'], i['code'], i.get('message','')[:200])
print('validate levels:', [(l['level'], l['status']) for l in d['levels']])
"
/home/reid/src/sysml-codegen/.venv/bin/sysml-codegen check --models $P/$N/models > $P/$N/check.txt 2>&1
echo "check exit: $?"
grep -E "SI_|block_|manual stub|nothing to generate|Error|error|OK|ready|module" $P/$N/check.txt | head -20
