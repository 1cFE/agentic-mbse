---
name: python-debugger
description: Programmatic Python debugging with breakpoints, state inspection, and stack traces. Use when debugging Python code that requires inspecting variable values at specific lines, understanding program state at runtime, capturing exception context, or when print-debugging is insufficient. Triggers on requests to "set a breakpoint", "inspect variables at line X", "debug this Python script", "capture the state when this crashes", or "trace execution".
---

# Python Debugger Skill

This skill enables programmatic debugging of Python scripts by setting breakpoints, capturing variable state, and inspecting stack traces—all without interactive terminal sessions.

## Core Capability

Run `scripts/claude_debugger.py` to debug Python code non-interactively:

```bash
# Set breakpoints at specific lines
python scripts/claude_debugger.py target.py --breakpoints 10,25,42

# Capture state only when exceptions occur (fastest)
python scripts/claude_debugger.py target.py --trace-exceptions

# Output to file for complex analysis
python scripts/claude_debugger.py target.py -b 10,25 -o debug_state.json
```

## Quick Reference

### Line Breakpoints
```bash
python scripts/claude_debugger.py script.py --breakpoints 15,30,45
```
Captures at each specified line: locals (with types/values), full stack trace.

### Exception Capture (Post-Mortem)
```bash
python scripts/claude_debugger.py script.py --trace-exceptions
```
Runs script normally. On exception: captures all frame locals, full traceback.

### Limit Captures
```bash
python scripts/claude_debugger.py script.py -b 10 --max-hits 3
```
Stops after 3 breakpoint hits (prevents runaway loops).

### Pass Script Arguments
```bash
python scripts/claude_debugger.py script.py -b 10 -- --input data.txt
```

## Output Format

JSON output contains:
```json
{
  "status": "completed",
  "total_hits": 3,
  "captures": [
    {
      "event": "line_breakpoint",
      "file": "/path/to/script.py",
      "line": 15,
      "function": "process_data",
      "locals": {
        "x": {"repr": "42", "type": "int", "value": 42},
        "items": {"repr": "[1, 2, 3]", "type": "list", "length": 3}
      },
      "stack_trace": [
        {"file": "script.py", "line": 15, "function": "process_data"},
        {"file": "script.py", "line": 50, "function": "main"}
      ]
    }
  ]
}
```

## Debugging Workflow

1. **Identify suspect lines** from error messages or logic analysis
2. **Set breakpoints** at those lines plus function entry points
3. **Run debugger** and examine captured state
4. **Analyze locals** to find unexpected values
5. **Trace stack** to understand call path
6. **Iterate** with adjusted breakpoints as needed

## When to Use Each Mode

| Scenario | Command |
|----------|---------|
| Know the problematic line | `--breakpoints 42` |
| Script crashes with exception | `--trace-exceptions` |
| Loop behaving unexpectedly | `-b 15 --max-hits 10` |
| Need full execution trace | `-b 1,5,10,15,20` (multiple lines) |

## Alternative Approaches

For simple cases, inline debugging may be faster:

```python
# Quick inline state dump (no external tool needed)
import json
def debug_dump(label="DEBUG"):
    import sys
    frame = sys._getframe(1)
    print(f"=== {label} at {frame.f_code.co_filename}:{frame.f_lineno} ===")
    print(json.dumps({k: repr(v) for k, v in frame.f_locals.items()}, indent=2))

# Usage: Add debug_dump("before loop") anywhere in code
```

## How It Works

The debugger uses Python's `bdb.Bdb` (debugger base class) which wraps `sys.settrace()`. When execution hits a breakpoint line, the trace function captures `frame.f_locals` and the call stack, then continues execution. No interactive terminal required.

See `references/debugging_internals.md` for advanced customization.
