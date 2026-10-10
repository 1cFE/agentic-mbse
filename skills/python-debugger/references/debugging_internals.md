# Python Debugging Internals

## How sys.settrace Works

Python's debugger infrastructure is built on `sys.settrace()`, which registers a trace function called by the interpreter on these events:

- `'call'` - Function called
- `'line'` - New line about to execute  
- `'return'` - Function about to return
- `'exception'` - Exception raised

```python
def trace_func(frame, event, arg):
    # frame: current stack frame
    # event: 'call', 'line', 'return', 'exception'
    # arg: depends on event (return value, exception info, etc.)
    return trace_func  # Return self to keep tracing
```

## Frame Object Properties

When a breakpoint hits, `frame` provides:

```python
frame.f_locals      # Dict of local variables
frame.f_globals     # Dict of global variables  
frame.f_code        # Code object
frame.f_code.co_filename  # Source file
frame.f_code.co_name      # Function name
frame.f_lineno      # Current line number
frame.f_back        # Calling frame (for stack trace)
```

## bdb.Bdb Architecture

The `claude_debugger.py` script extends `bdb.Bdb`:

```python
class ClaudeDebugger(bdb.Bdb):
    def user_line(self, frame):
        # Called when breakpoint hit
        self.capture_state(frame)
        self.set_continue()  # Resume execution
```

Key `bdb.Bdb` methods:
- `set_break(filename, lineno)` - Set breakpoint
- `set_continue()` - Continue to next breakpoint
- `set_step()` - Step to next line
- `set_quit()` - Stop execution

## Extending the Debugger

### Conditional Breakpoints

```python
def user_line(self, frame):
    # Only break if condition met
    if frame.f_locals.get('x', 0) > 100:
        self.captures.append(self._capture_frame(frame))
    self.set_continue()
```

### Watch Expressions

```python
def user_line(self, frame):
    watched = ['x', 'y', 'result']
    capture = {name: frame.f_locals.get(name) for name in watched}
    self.captures.append(capture)
    self.set_continue()
```

### Step-Through Simulation

```python
# Capture every line (expensive!)
def trace_all(self, frame, event, arg):
    if event == 'line':
        self.captures.append({
            'line': frame.f_lineno,
            'locals': dict(frame.f_locals)
        })
    return self.trace_all

sys.settrace(trace_all)
```

## Performance Considerations

`sys.settrace` adds overhead to every line. For long-running scripts:
- Use `--max-hits` to limit captures
- Prefer `--trace-exceptions` for crash debugging
- Set breakpoints only where needed

Python 3.12+ offers `sys.monitoring` as a more efficient alternative (used by default in newer pdb).

## Alternative: Code Injection

For maximum performance, inject capture code directly:

```python
# Before target line
__debug_state = {k: repr(v) for k, v in locals().items()}
import json; open('/tmp/state.json', 'w').write(json.dumps(__debug_state))
```

This has zero tracing overhead but requires modifying source.