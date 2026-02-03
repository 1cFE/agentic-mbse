/**
 * Reopen Comment Thread
 *
 * Handles reopening resolved comment threads.
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
 * Handles reopening a resolved comment thread.
 *
 * Workflow:
 * 1. Extract thread_id from thread.contextValue
 * 2. Call Python CLI: `comment reopen <thread_id>`
 * 3. Show success/error notification
 * 4. Update thread state (file watcher will reload with actual data)
 *
 * @param thread - The VSCode CommentThread to reopen
 * @param projectRoot - Absolute path to project root
 * @returns Promise<void>
 */
export async function reopenThread(
    thread: vscode.CommentThread,
    projectRoot: string
): Promise<void> {
    try {
        // Extract thread_id from contextValue
        const threadId = extractThreadId(thread);
        if (!threadId) {
            vscode.window.showErrorMessage('Failed to identify thread for reopening');
            return;
        }

        // Build CLI command
        const cliCommand = `comment reopen ${threadId}`;

        console.log(`Executing: ${cliCommand}`);

        // Execute CLI command synchronously
        execSync(cliCommand, {
            cwd: projectRoot,
            encoding: 'utf-8',
            stdio: 'pipe' // Capture stdout/stderr
        });

        // Success notification
        vscode.window.showInformationMessage(`Thread ${threadId} reopened`);

        // Mark thread as unresolved immediately (file watcher will reload with actual data)
        thread.state = vscode.CommentThreadState.Unresolved;

    } catch (error: any) {
        // Show error notification with details
        const errorMessage = error.stderr?.toString() || error.message || 'Unknown error';
        vscode.window.showErrorMessage(`Failed to reopen thread: ${errorMessage}`);
        console.error('Reopen command failed:', error);
    }
}

/**
 * Registers the reopen command with VSCode.
 *
 * This function should be called during extension activation to register
 * the command that handles thread reopening.
 *
 * @param context - The VSCode extension context
 * @param projectRoot - Absolute path to project root
 */
export function registerReopenCommand(
    context: vscode.ExtensionContext,
    projectRoot: string
): void {
    // Register the reopen command
    const reopenCommand = vscode.commands.registerCommand(
        'file-native-comments.reopenThread',
        (thread: vscode.CommentThread) => {
            return reopenThread(thread, projectRoot);
        }
    );

    context.subscriptions.push(reopenCommand);

    console.log('Reopen command registered: file-native-comments.reopenThread');
}
