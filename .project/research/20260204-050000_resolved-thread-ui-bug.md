---
date: 2026-02-04T05:00:00-06:00
researcher: Claude
topic: "Resolved thread UI not updating - contextValue when-clause bug"
tags: [research, vscode-extension, bug, comment-api]
status: complete
last_updated: 2026-02-04
---

# Research: Resolved Thread UI Not Updating After Resolve

**Date**: 2026-02-04
**Researcher**: Claude
**Research Type**: Codebase / API Integration

## Research Question

After resolving a comment thread, the UI still shows it identically to an unresolved thread -- the resolve (checkmark) button still appears instead of switching to the reopen button, and there's no visual differentiation. Why?

## Summary

- **Root cause identified**: The `resolveThread` command (line 73) updates `thread.state` to `Resolved` but does NOT update `thread.contextValue` from `"open"` to `"resolved"`. The when-clauses in `package.json` use `contextValue` (via `commentThread =~ /open/` and `commentThread =~ /resolved/`) to decide which buttons to show, so the buttons never switch.
- **The fix is trivial**: Add `thread.contextValue = 'resolved'` after line 73 in `resolveThread.ts`, and `thread.contextValue = 'open'` after line 56 in `reopenThread.ts`.
- **Visual differentiation**: VSCode's `CommentThreadState.Resolved` does provide some built-in visual distinction (dimmed/collapsed appearance) but the degree varies by VSCode version and theme. The `contextValue` fix alone will solve the button problem.
- **The `wontfix` status also needs handling**: The sidecar has `ThreadStatus.WONTFIX` but the when-clauses only handle `open` and `resolved`. A thread with status `wontfix` would match neither, showing no buttons at all.

## Detailed Findings

### 1. The when-clause / contextValue mismatch

**package.json menu when-clauses** (`package.json:84-99`):
```json
"comments/commentThread/title": [
  {
    "command": "file-native-comments.resolveThread",
    "when": "commentController == file-native-comments && commentThread =~ /open/"
  },
  {
    "command": "file-native-comments.reopenThread",
    "when": "commentController == file-native-comments && commentThread =~ /resolved/"
  },
  {
    "command": "file-native-comments.deleteThread",
    "when": "commentController == file-native-comments"
  }
]
```

These use `commentThread =~ /open/` and `commentThread =~ /resolved/`, which match against the thread's `contextValue` property.

**Initial creation sets contextValue correctly** (`commentProvider.ts:241`):
```typescript
vsThread.contextValue = thread.status === ThreadStatus.OPEN ? 'open' : 'resolved';
```

**In-place update also sets contextValue correctly** (`commentProvider.ts:185`):
```typescript
vsThread.contextValue = thread.status === ThreadStatus.OPEN ? 'open' : 'resolved';
```

**But the resolve command does NOT update contextValue** (`resolveThread.ts:72-73`):
```typescript
vscode.window.showInformationMessage(`Thread ${threadId} resolved`);
thread.state = vscode.CommentThreadState.Resolved;
// BUG: Missing thread.contextValue = 'resolved';
```

**And the reopen command also does NOT update contextValue** (`reopenThread.ts:54-56`):
```typescript
vscode.window.showInformationMessage(`Thread ${threadId} reopened`);
thread.state = vscode.CommentThreadState.Unresolved;
// BUG: Missing thread.contextValue = 'open';
```

### 2. How `contextValue` drives the UI

The VSCode Comment API uses `contextValue` as a **context key** named `commentThread` in when-clause evaluation. The `=~` operator performs regex matching against this string.

When `contextValue` is `"open"`:
- `commentThread =~ /open/` --> **true** --> resolve button shown
- `commentThread =~ /resolved/` --> **false** --> reopen button hidden

When `contextValue` is `"resolved"`:
- `commentThread =~ /open/` --> **false** --> resolve button hidden
- `commentThread =~ /resolved/` --> **true** --> reopen button shown

Since `resolveThread` only sets `thread.state` but not `thread.contextValue`, the thread stays with `contextValue = "open"` after resolution, so the resolve button remains visible and the reopen button stays hidden.

### 3. How `CommentThreadState` affects rendering

Setting `thread.state = CommentThreadState.Resolved`:
- May collapse the thread (depending on VSCode version)
- May add a subtle "resolved" badge or dimming in some themes
- Does NOT control which menu buttons appear (that's purely `contextValue` + when-clauses)

The `state` property and `contextValue` are independent mechanisms:
- `state` = built-in visual hint (resolved badge, dimming)
- `contextValue` = custom when-clause matching for menus

Both should be updated together for consistent behavior.

### 4. The FileWatcher would eventually fix it

The FileWatcher watches `.comments/**/*.json` sidecar files. After the CLI updates the sidecar (marking thread as resolved), the FileWatcher fires, `loadCommentsForDocument` runs, and `updateThreadInPlace` correctly sets both `state` and `contextValue`. But this has a 500ms debounce and requires the sidecar file change event to propagate -- so there's a visible lag where the UI shows stale state.

The fix should update both properties immediately in the command handler for responsive UX, and the FileWatcher will confirm/reconcile shortly after.

### 5. Known VSCode bug with contextValue reset

There's a [known VSCode issue (#120680)](https://github.com/microsoft/vscode/issues/120680) where setting `contextValue` to `undefined` doesn't properly reset the context key. This is NOT the bug here (we're setting to defined strings), but it's worth knowing: always set `contextValue` to a defined string, never `undefined`.

### 6. `wontfix` status gap

`ThreadStatus.WONTFIX` exists in the sidecar model (`sidecar.ts:16`) but:
- `commentProvider.ts:241` maps both `resolved` and `wontfix` to `contextValue = 'resolved'`
- The when-clause `commentThread =~ /resolved/` would match, showing the reopen button
- This is acceptable behavior -- wontfix threads can be reopened

## Code References

- `vscode-extension/package.json:84-99` - Menu when-clauses for thread title buttons
- `vscode-extension/src/commands/resolveThread.ts:73` - Sets state but not contextValue (BUG)
- `vscode-extension/src/commands/reopenThread.ts:56` - Sets state but not contextValue (BUG)
- `vscode-extension/src/commentProvider.ts:169-171,184-185` - updateThreadInPlace correctly sets both
- `vscode-extension/src/commentProvider.ts:227-229,241` - convertThreadToVSCodeThread correctly sets both
- `vscode-extension/src/sidecar.ts:13-17` - ThreadStatus enum (OPEN, RESOLVED, WONTFIX)
- `vscode-extension/src/fileWatcher.ts` - Eventually reconciles via sidecar reload

## Recommendations

### Fix 1: Update contextValue in resolve/reopen commands (required)

In `resolveThread.ts` after line 73, add:
```typescript
thread.contextValue = 'resolved';
```

In `reopenThread.ts` after line 56, add:
```typescript
thread.contextValue = 'open';
```

This immediately updates the when-clause state so buttons switch without waiting for FileWatcher.

### Fix 2: Consider adding visual label prefix (optional enhancement)

For additional visual distinction beyond what `CommentThreadState.Resolved` provides, update the thread label:
```typescript
// In resolveThread.ts after resolution:
if (thread.label) {
    thread.label = `[Resolved] ${thread.label}`;
}
```

This gives an immediate text-level indicator that the thread is resolved. However, the FileWatcher reload would strip this prefix (since `updateThreadInPlace` rebuilds the label from sidecar data), so this would be a transient enhancement. A better approach is to include the status prefix in `updateThreadInPlace` and `convertThreadToVSCodeThread`.

### Fix 3: No changes needed to package.json

The existing when-clauses using `=~` regex matching are correct and flexible. No changes needed there.

## Open Questions

1. Should `wontfix` threads have a distinct visual treatment (different icon or label) vs. `resolved`?
2. Should the extension automatically collapse resolved threads? (`thread.collapsibleState = CollapsibleState.Collapsed`)
