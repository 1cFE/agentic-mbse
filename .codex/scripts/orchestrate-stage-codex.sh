#!/usr/bin/env bash
# orchestrate-stage-codex.sh - run or resume ONE pipeline stage through `codex exec`.
#
# Mechanism only. It composes the prompt, invokes Codex, and prints compact JSON
# for the orchestrator. It does not interpret stage results.
#
# Usage:
#   orchestrate-stage-codex.sh run <stage> [opts]          # stage args read from stdin
#   orchestrate-stage-codex.sh resume <session_id> [opts]  # message read from stdin
#   orchestrate-stage-codex.sh --parse-only <jsonl> <last-message>
#
# Options:
#   --model <m>       stage model, passed through to codex exec
#   --timeout <sec>   wall-clock timeout (default: 600)
#   --sandbox <mode>  sandbox for fresh run only (default: stage-aware)
#   --cd <dir>        working directory for fresh run (default: current directory)
#   --log-dir <dir>   raw JSONL/stderr/final-message log dir (default: ./.orchestrate-logs)
#   --preamble <file> preamble to inject (default: orchestrate-preamble-codex.md beside this script)
#   --dry-run         print composed prompt + codex argv, do not call codex
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

die() { echo "orchestrate-stage-codex: $*" >&2; exit 1; }
usage() { sed -n '2,24p' "${BASH_SOURCE[0]}" >&2; exit 2; }

json_quote() {
  python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))'
}

stage_skill_name() {
  local stage="$1"
  stage="${stage#/_my_}"
  stage="${stage#_my_}"
  stage="${stage#my-}"
  stage="${stage//_/-}"
  printf 'my-%s' "$stage"
}

default_sandbox_for_stage() {
  case "$1" in
    pipeline|status|project_find|project-find|concept_design_review|concept-design-review|spec_review|spec-review|design_review|design-review)
      printf 'read-only'
      ;;
    *)
      printf 'workspace-write'
      ;;
  esac
}

parse_codex_result() {
  local raw="$1"
  local last_message="$2"
  local stderr_path="${3:-}"

  python3 - "$raw" "$last_message" "$stderr_path" <<'PY'
import json
import pathlib
import sys

raw_path = pathlib.Path(sys.argv[1])
last_path = pathlib.Path(sys.argv[2])
stderr_path = sys.argv[3]

if not raw_path.is_file():
    raise SystemExit(f"raw JSONL file not found: {raw_path}")
if not last_path.is_file():
    raise SystemExit(f"final message file not found: {last_path}")

session_id = None
is_error = False
error_events = []

with raw_path.open(encoding="utf-8") as handle:
    for line_number, line in enumerate(handle, 1):
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"invalid JSONL at {raw_path}:{line_number}: {exc}") from exc

        event_type = event.get("type")
        if event_type == "thread.started" and session_id is None:
            session_id = event.get("thread_id")
        if event_type in {"turn.failed", "error"}:
            is_error = True
            error_events.append(event)

result = last_path.read_text(encoding="utf-8")
if session_id is None:
    raise SystemExit(f"no thread.started.thread_id parsed from {raw_path}")
if result == "":
    raise SystemExit(f"final message file is empty: {last_path}")

payload = {
    "session_id": session_id,
    "result": result,
    "raw": str(raw_path),
    "stderr": stderr_path,
    "is_error": is_error,
}
if error_events:
    payload["errors"] = error_events

print(json.dumps(payload, separators=(",", ":")))
raise SystemExit(3 if is_error else 0)
PY
}

if [ "${1:-}" = "--parse-only" ]; then
  [ $# -eq 3 ] || usage
  parse_codex_result "$2" "$3" ""
  exit $?
fi

[ $# -ge 1 ] || usage
MODE="$1"; shift

MODEL="${ORCH_MODEL:-}"
TIMEOUT=600
SANDBOX=""
SANDBOX_SET=0
WORKDIR="$(pwd)"
LOGDIR="./.orchestrate-logs"
PREAMBLE="$SCRIPT_DIR/orchestrate-preamble-codex.md"
DRYRUN=0

case "$MODE" in
  run)    [ $# -ge 1 ] || die "run requires <stage>"; STAGE="$1"; shift ;;
  resume) [ $# -ge 1 ] || die "resume requires <session_id>"; SID="$1"; shift ;;
  -h|--help) usage ;;
  *) die "unknown mode '$MODE' (expected run|resume)" ;;
esac

while [ $# -gt 0 ]; do
  case "$1" in
    --model)    [ $# -ge 2 ] || die "--model requires a value"; MODEL="$2"; shift 2 ;;
    --timeout)  [ $# -ge 2 ] || die "--timeout requires a value"; TIMEOUT="$2"; shift 2 ;;
    --sandbox)  [ $# -ge 2 ] || die "--sandbox requires a value"; SANDBOX="$2"; SANDBOX_SET=1; shift 2 ;;
    --cd)       [ $# -ge 2 ] || die "--cd requires a value"; WORKDIR="$2"; shift 2 ;;
    --log-dir)  [ $# -ge 2 ] || die "--log-dir requires a value"; LOGDIR="$2"; shift 2 ;;
    --preamble) [ $# -ge 2 ] || die "--preamble requires a value"; PREAMBLE="$2"; shift 2 ;;
    --dry-run)  DRYRUN=1; shift ;;
    *) die "unknown option '$1'" ;;
  esac
done

if [ "$MODE" = "resume" ] && [ "$SANDBOX_SET" = "1" ]; then
  die "--sandbox is not supported for resume by the current Codex CLI"
fi

BODY="$(cat)"

if [ "$MODE" = "run" ]; then
  [ -f "$PREAMBLE" ] || die "preamble file not found: $PREAMBLE"
  SKILL_NAME="$(stage_skill_name "$STAGE")"
  [ "$SANDBOX_SET" = "1" ] || SANDBOX="$(default_sandbox_for_stage "$STAGE")"
  PROMPT="$(printf 'Use $%s for this pipeline stage.\n\nStage input:\n%s\n\n%s\n' "$SKILL_NAME" "$BODY" "$(cat "$PREAMBLE")")"
  LABEL="run-${SKILL_NAME#my-}"
else
  PROMPT="$BODY"
  LABEL="resume-${SID:0:8}"
fi

if [ "$DRYRUN" = "1" ]; then
  if [ "$MODE" = "run" ]; then
    echo "# codex exec --json --output-last-message <last-message> --sandbox $SANDBOX --cd $WORKDIR${MODEL:+ --model $MODEL} -"
  else
    echo "# codex exec resume --json --output-last-message <last-message>${MODEL:+ --model $MODEL} $SID -"
  fi
  echo "# --- composed prompt (piped on stdin) ---"
  printf '%s\n' "$PROMPT"
  exit 0
fi

mkdir -p "$LOGDIR" || die "could not create log dir: $LOGDIR"
STAMP="$(date +%Y%m%d-%H%M%S)-$$"
RAW="$LOGDIR/$LABEL-$STAMP.jsonl"
ERR="$LOGDIR/$LABEL-$STAMP.stderr"
LAST="$LOGDIR/$LABEL-$STAMP.final.md"

RUNNER_PID=""
CLEANUP_GRACE=5

cancel_runner() {
  local signal="$1"
  local signal_status="$2"
  local runner_pid="$RUNNER_PID"
  local escalation_pid=""

  trap - HUP INT TERM
  printf 'orchestrate-stage-codex: %s received %s; cancelling stage (raw: %s, stderr: %s, final: %s)\n' \
    "$LABEL" "$signal" "$RAW" "$ERR" "$LAST" >&2

  if [ -n "$runner_pid" ] && kill -0 "$runner_pid" 2>/dev/null; then
    kill "-$signal" "$runner_pid" 2>/dev/null || true
    (
      sleep "$CLEANUP_GRACE"
      if kill -0 "$runner_pid" 2>/dev/null; then
        printf 'orchestrate-stage-codex: %s cleanup grace expired; killing owned process group %s\n' \
          "$LABEL" "$runner_pid" >&2
        kill -KILL -- "-$runner_pid" 2>/dev/null || true
      fi
    ) &
    escalation_pid=$!

    wait "$runner_pid" 2>/dev/null || true
    RUNNER_PID=""
    kill "$escalation_pid" 2>/dev/null || true
    wait "$escalation_pid" 2>/dev/null || true
  fi

  exit "$signal_status"
}

trap 'cancel_runner HUP 129' HUP
trap 'cancel_runner INT 130' INT
trap 'cancel_runner TERM 143' TERM

if [ "$MODE" = "run" ]; then
  CODEX_ARGS=(exec --json --output-last-message "$LAST" --sandbox "$SANDBOX" --cd "$WORKDIR" -)
else
  CODEX_ARGS=(exec resume --json --output-last-message "$LAST" "$SID" -)
fi
[ -z "$MODEL" ] || CODEX_ARGS+=(--model "$MODEL")

printf '%s' "$PROMPT" | timeout "$TIMEOUT" codex "${CODEX_ARGS[@]}" > "$RAW" 2> "$ERR" &
RUNNER_PID=$!
wait "$RUNNER_PID"
RC=$?
RUNNER_PID=""
trap - HUP INT TERM
[ "$RC" -eq 124 ] && die "stage timed out after ${TIMEOUT}s (raw: $RAW, stderr: $ERR)"
[ "$RC" -ne 0 ] && die "codex exited $RC (raw: $RAW, stderr: $ERR)"

parse_codex_result "$RAW" "$LAST" "$ERR"
exit $?
