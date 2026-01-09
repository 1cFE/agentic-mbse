#!/usr/bin/env python3
"""
claude_debugger.py - A non-interactive debugger for Claude Code

This script allows Claude Code to set breakpoints and inspect program state
without requiring an interactive terminal session.

Usage:
    python claude_debugger.py script.py --breakpoints 10,25,42
    python claude_debugger.py script.py --breakpoints 10,25 --output state.json
    python claude_debugger.py script.py --functions main,process_data
    python claude_debugger.py script.py --breakpoints 10 --max-hits 5
    python claude_debugger.py script.py --trace-exceptions

The output is JSON containing captured state at each breakpoint hit.
"""

import argparse
import bdb
import json
import os
import sys
import traceback


class ClaudeDebugger(bdb.Bdb):
    """A programmatic debugger that captures state at breakpoints."""

    def __init__(self, max_hits: int = 50, capture_globals: bool = False):
        super().__init__()
        self.max_hits = max_hits
        self.capture_globals = capture_globals
        self.captures = []
        self.hit_count = 0
        self.function_breakpoints = set()

    def user_line(self, frame):
        """Called when execution stops at a line (breakpoint hit)."""
        if self.hit_count >= self.max_hits:
            self.set_quit()
            return

        self.hit_count += 1
        capture = self._capture_frame(frame, "line_breakpoint")
        self.captures.append(capture)
        self.set_continue()

    def user_call(self, frame, argument_list):
        """Called when a function is called (if we're tracing it)."""
        func_name = frame.f_code.co_name
        if func_name in self.function_breakpoints:
            if self.hit_count >= self.max_hits:
                self.set_quit()
                return

            self.hit_count += 1
            capture = self._capture_frame(frame, "function_entry")
            capture["arguments"] = self._safe_repr(argument_list)
            self.captures.append(capture)
        self.set_continue()

    def user_return(self, frame, return_value):
        """Called when a function returns (if we're tracing it)."""
        func_name = frame.f_code.co_name
        if func_name in self.function_breakpoints:
            if self.hit_count >= self.max_hits:
                self.set_quit()
                return

            self.hit_count += 1
            capture = self._capture_frame(frame, "function_return")
            capture["return_value"] = self._safe_repr(return_value)
            self.captures.append(capture)
        self.set_continue()

    def user_exception(self, frame, exc_info):
        """Called when an exception occurs."""
        if self.hit_count >= self.max_hits:
            self.set_quit()
            return

        self.hit_count += 1
        exc_type, exc_value, exc_tb = exc_info
        capture = self._capture_frame(frame, "exception")
        capture["exception"] = {
            "type": exc_type.__name__ if exc_type else None,
            "message": str(exc_value) if exc_value else None,
            "traceback": traceback.format_exception(exc_type, exc_value, exc_tb),
        }
        self.captures.append(capture)
        self.set_continue()

    def _capture_frame(self, frame, event_type: str) -> dict:
        """Capture the full state of a frame."""
        capture = {
            "event": event_type,
            "hit_number": self.hit_count,
            "file": frame.f_code.co_filename,
            "line": frame.f_lineno,
            "function": frame.f_code.co_name,
            "locals": {},
            "stack_trace": [],
        }

        # Capture local variables
        for name, value in frame.f_locals.items():
            capture["locals"][name] = {
                "repr": self._safe_repr(value),
                "type": type(value).__name__,
            }
            # Add extra info for common types
            if isinstance(value, (list, tuple, dict, set, frozenset)):
                capture["locals"][name]["length"] = len(value)
            if isinstance(value, (int, float)):
                capture["locals"][name]["value"] = value

        # Capture stack trace
        current = frame
        while current:
            capture["stack_trace"].append(
                {
                    "file": current.f_code.co_filename,
                    "line": current.f_lineno,
                    "function": current.f_code.co_name,
                }
            )
            current = current.f_back

        # Optionally capture globals
        if self.capture_globals:
            capture["globals"] = {
                k: self._safe_repr(v)
                for k, v in frame.f_globals.items()
                if not k.startswith("__")
            }

        return capture

    def _safe_repr(self, obj, max_length: int = 500) -> str:
        """Safely get repr of an object, truncating if too long."""
        try:
            r = repr(obj)
            if len(r) > max_length:
                return r[:max_length] + "... [truncated]"
            return r
        except Exception as e:
            return f"<repr failed: {e}>"

    def add_function_breakpoint(self, func_name: str):
        """Add a breakpoint on function entry/exit."""
        self.function_breakpoints.add(func_name)

    def run_script(self, script_path: str, script_args: list = None):
        """Run a script with debugging enabled."""
        script_path = os.path.abspath(script_path)

        # Set up sys.argv for the script
        old_argv = sys.argv
        sys.argv = [script_path] + (script_args or [])

        # Add script directory to path
        script_dir = os.path.dirname(script_path)
        if script_dir not in sys.path:
            sys.path.insert(0, script_dir)

        try:
            with open(script_path) as f:
                code = compile(f.read(), script_path, "exec")

            globals_dict = {
                "__name__": "__main__",
                "__file__": script_path,
                "__builtins__": __builtins__,
            }

            self.run(code, globals_dict)

        finally:
            sys.argv = old_argv

        return self.captures


def run_with_exception_capture(script_path: str, script_args: list = None) -> dict:
    """Run a script and capture full state if an exception occurs."""
    script_path = os.path.abspath(script_path)

    old_argv = sys.argv
    sys.argv = [script_path] + (script_args or [])

    script_dir = os.path.dirname(script_path)
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)

    result = {
        "status": "success",
        "exception": None,
        "frames": [],
    }

    try:
        with open(script_path) as f:
            code = compile(f.read(), script_path, "exec")

        exec(code, {"__name__": "__main__", "__file__": script_path})

    except Exception as e:
        exc_type, exc_value, exc_tb = sys.exc_info()

        result["status"] = "exception"
        result["exception"] = {
            "type": exc_type.__name__,
            "message": str(exc_value),
            "traceback": traceback.format_exc(),
        }

        # Capture all frames in the traceback
        tb = exc_tb
        while tb:
            frame = tb.tb_frame
            result["frames"].append(
                {
                    "file": frame.f_code.co_filename,
                    "line": tb.tb_lineno,
                    "function": frame.f_code.co_name,
                    "locals": {k: repr(v)[:200] for k, v in frame.f_locals.items()},
                }
            )
            tb = tb.tb_next

    finally:
        sys.argv = old_argv

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Non-interactive debugger for Claude Code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Set breakpoints at specific lines
  python claude_debugger.py script.py --breakpoints 10,25,42
  
  # Break on function entry/exit
  python claude_debugger.py script.py --functions main,process
  
  # Capture only on exceptions (post-mortem style)
  python claude_debugger.py script.py --trace-exceptions
  
  # Limit captures and specify output file
  python claude_debugger.py script.py -b 10,20 --max-hits 3 -o debug.json
  
  # Pass arguments to the script
  python claude_debugger.py script.py -b 10 -- --input data.txt
        """,
    )

    parser.add_argument("script", help="Python script to debug")
    parser.add_argument(
        "-b", "--breakpoints", help="Comma-separated list of line numbers"
    )
    parser.add_argument(
        "-f", "--functions", help="Comma-separated list of function names to trace"
    )
    parser.add_argument(
        "-o", "--output", help="Output file for JSON results (default: stdout)"
    )
    parser.add_argument(
        "--max-hits",
        type=int,
        default=50,
        help="Maximum number of breakpoint hits to capture",
    )
    parser.add_argument(
        "--trace-exceptions",
        action="store_true",
        help="Only capture state on exceptions (faster)",
    )
    parser.add_argument(
        "--capture-globals", action="store_true", help="Also capture global variables"
    )
    parser.add_argument(
        "script_args", nargs="*", help="Arguments to pass to the script"
    )

    args = parser.parse_args()

    # Validate script exists
    if not os.path.exists(args.script):
        print(f"Error: Script not found: {args.script}", file=sys.stderr)
        sys.exit(1)

    script_path = os.path.abspath(args.script)

    # Exception-only mode
    if args.trace_exceptions:
        result = run_with_exception_capture(script_path, args.script_args)
        output = json.dumps(result, indent=2)

        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
            print(f"Results written to {args.output}")
        else:
            print(output)
        return

    # Full debugging mode
    debugger = ClaudeDebugger(
        max_hits=args.max_hits, capture_globals=args.capture_globals
    )

    # Set line breakpoints
    if args.breakpoints:
        for line in args.breakpoints.split(","):
            line = int(line.strip())
            debugger.set_break(script_path, line)

    # Set function breakpoints
    if args.functions:
        for func in args.functions.split(","):
            debugger.add_function_breakpoint(func.strip())

    # Require at least one breakpoint type
    if not args.breakpoints and not args.functions:
        print("Error: Specify --breakpoints or --functions", file=sys.stderr)
        sys.exit(1)

    # Run with debugging
    try:
        captures = debugger.run_script(script_path, args.script_args)

        result = {
            "status": "completed",
            "script": script_path,
            "total_hits": len(captures),
            "captures": captures,
        }

    except bdb.BdbQuit:
        result = {
            "status": "max_hits_reached",
            "script": script_path,
            "total_hits": len(debugger.captures),
            "captures": debugger.captures,
        }

    except Exception as e:
        result = {
            "status": "error",
            "script": script_path,
            "error": str(e),
            "traceback": traceback.format_exc(),
            "captures_before_error": debugger.captures,
        }

    # Output results
    output = json.dumps(result, indent=2)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Results written to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
