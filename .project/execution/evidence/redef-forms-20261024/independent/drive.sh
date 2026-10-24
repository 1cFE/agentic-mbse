#!/bin/bash
P=/tmp/claude-1000/-home-reid-src-agentic-mbse/9366fe1c-453c-484d-b30e-782bbdd1390c/scratchpad/probe2
cd /home/reid/src/dc3
mkdir -p $P/logs $P/out
for d in $P/cases/*/; do
  c=$(basename $d)
  uv run --env-file .env sysml-codegen check --models $d > $P/logs/$c.check 2>&1; ce=$?
  rm -rf $P/out/$c
  uv run --env-file .env sysml-codegen generate --models $d --output $P/out/$c/pkg --package-name $c > $P/logs/$c.gen 2>&1; ge=$?
  echo "$c check=$ce gen=$ge"
done
