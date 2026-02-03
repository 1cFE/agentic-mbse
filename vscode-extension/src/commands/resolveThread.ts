/**
 * Resolve Comment Thread
 *
 * Handles resolving comment threads, optionally capturing a decision.
 * Invoked from the context menu on a CommentThread or via command palette.
 */

import * as vscode from 'vscode';
import { execSync } from 'child_process';

/**
 * Extracts the thread_id from a CommentThread's contextValue.
 *
 * The contextValue contains JSON with metadata like:
 * {
 *   "thread_id": "01HXYZ...",
 *   "health": "anchored",
 *   "status": "open",
 *   ...
 * }
 *
 * @param thread - The VSCode CommentThread
 * @returns The thread ID string, or null if not found
 */
export function extractThreadId(thread: vscode.CommentThread): string | null {
    try {
        if (!thread.contextValue) {
            return null;
        }

        const context = JSON.parse(thread.contextValue);
        return context.thread_id || null;
    } catch (error) {
        console.error('Failed to parse thread contextValue:', error);
        return null;
    }
}

/**
 * Handles resolving a comment thread.
 *
 * Workflow:
 * 1. Extract thread_id from thread.contextValue
 * 2. Optionally prompt for decision text
 * 3. Call Python CLI: `comment resolve <thread_id> [--decision "<text>"]`
 * 4. Show success/error notification
 * 5. Update thread state (file watcher will reload with actual data)
 *
 * @param thread - The VSCode CommentThread to resolve
 * @param projectRoot - Absolute path to project root
 * @returns Promise<void>
 */
export async function resolveThread(
    thread: vscode.CommentThread,
    projectRoot: string
): Promise<void> {
    try {
        // Extract thread_id from contextValue
        const threadId = extractThreadId(thread);
        if (!threadId) {
            vscode.window.showErrorMessage('Failed to identify thread for resolution');
            return;
        }

        // Prompt for decision text (required by CLI unless using --wontfix)
        const decision = await vscode.window.showInputBox({
            prompt: 'Enter resolution decision (required)',
            placeHolder: 'Describe why this was resolved, what was decided, etc.',
            validateInput: (value) => {
                // Decision is required by the CLI (unless using --wontfix, which we don't support in VSCode yet)
                if (!value || value.trim().length === 0) {
                    return 'Decision is required. Describe why this was resolved.';
                }
                return null;
            }
        });

        // If user cancelled the input box, abort
        if (decision === undefined) {
            return;
        }

        // Trim the decision text
        const trimmedDecision = decision.trim();

        // Build CLI command (decision is now guaranteed to be non-empty)
        const cliCommand = buildResolveCliCommand(threadId, trimmedDecision);

        console.log(`Executing: ${cliCommand}`);

        // Execute CLI command synchronously
        execSync(cliCommand, {
            cwd: projectRoot,
            encoding: 'utf-8',
            stdio: 'pipe' // Capture stdout/stderr
        });

        // Success notification
        vscode.window.showInformationMessage(`Thread ${threadId} resolved`);

        // Mark thread as resolved immediately (file watcher will reload with actual data)
        thread.state = vscode.CommentThreadState.Resolved;

    } catch (error: any) {
        // Show error notification with details
        const errorMessage = error.stderr?.toString() || error.message || 'Unknown error';
        vscode.window.showErrorMessage(`Failed to resolve thread: ${errorMessage}`);
        console.error('Resolve command failed:', error);
    }
}

/**
 * Builds the CLI command for resolving a thread.
 *
 * @param threadId - The ULID of the thread
 * @param decision - Decision text (required by CLI)
 * @returns The complete CLI command string
 */
export function buildResolveCliCommand(
    threadId: string,
    decision: string
): string {
    // Escape special characters in decision text
    // Order matters: escape backslashes first, then quotes, then newlines
    const escapedDecision = decision
        .replace(/\\/g, '\\\\')  // Escape backslashes
        .replace(/"/g, '\\"')    // Escape double quotes
        .replace(/\n/g, '\\n')   // Escape newlines
        .replace(/\r/g, '\\r')   // Escape carriage returns
        .replace(/\t/g, '\\t');  // Escape tabs

    return `comment resolve ${threadId} --decision "${escapedDecision}"`;
}

/**
 * Registers the resolve command with VSCode.
 *
 * This function should be called during extension activation to register
 * the command that handles thread resolution.
 *
 * @param context - The VSCode extension context
 * @param projectRoot - Absolute path to project root
 */
export function registerResolveCommand(
    context: vscode.ExtensionContext,
    projectRoot: string
): void {
    // Register the resolve command
    const resolveCommand = vscode.commands.registerCommand(
        'file-native-comments.resolveThread',
        (thread: vscode.CommentThread) => {
            return resolveThread(thread, projectRoot);
        }
    );

    context.subscriptions.push(resolveCommand);

    console.log('Resolve command registered: file-native-comments.resolveThread');
}
