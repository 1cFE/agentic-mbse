/**
 * Reply to Comment Thread
 *
 * Handles replies to existing comment threads. Invoked when users type in
 * the reply input box at the bottom of a CommentThread.
 *
 * Uses VSCode command pattern - the CommentReply object is passed automatically
 * when the command is triggered from the UI.
 */

import * as vscode from 'vscode';
import { execSync } from 'child_process';
import { handleConflictCheck, ConflictResolution } from '../conflictHandler';

/**
 * Handles reply to a comment thread.
 *
 * Workflow:
 * 1. Extract thread_id and source_hash from thread.contextValue
 * 2. Check for conflicts (compare source_hash with on-disk version)
 * 3. If conflict, prompt user (Reload/Overwrite/Cancel)
 * 4. Call Python CLI: `comment reply <thread_id> "<text>" --author=<author>`
 * 5. Show success/error notification
 * 6. Update thread with temporary comment (file watcher will reload with actual data)
 *
 * @param reply - The VSCode CommentReply object (contains thread and text)
 * @param projectRoot - Absolute path to project root
 * @returns Promise<void>
 */
export async function handleReply(
    reply: vscode.CommentReply,
    projectRoot: string
): Promise<void> {
    try {
        // Extract thread_id and source_hash from contextValue
        const threadId = extractThreadId(reply.thread);
        if (!threadId) {
            vscode.window.showErrorMessage('Failed to identify thread for reply');
            return;
        }

        const sourceHash = extractSourceHash(reply.thread);

        // Validate reply text
        if (!reply.text || reply.text.trim().length === 0) {
            vscode.window.showErrorMessage('Reply text cannot be empty');
            return;
        }

        // Get source file path from thread URI
        const sourcePath = reply.thread.uri.fsPath;

        // Check for conflicts before writing
        const resolution = await handleConflictCheck(sourcePath, projectRoot, sourceHash);

        if (resolution === ConflictResolution.CANCEL) {
            vscode.window.showInformationMessage('Reply cancelled');
            return;
        }

        if (resolution === ConflictResolution.RELOAD) {
            vscode.window.showInformationMessage(
                'Comments reloaded. Please retry your reply after reviewing the updated thread.'
            );
            // File watcher will trigger reload automatically
            return;
        }

        // Resolution is OVERWRITE or no conflict detected - proceed with write
        // Get author from VSCode environment (fallback to 'vscode-user')
        const author = (vscode.env as any).username || 'vscode-user';

        // Build CLI command
        // Format: comment reply <thread_id> "<text>" --author=<author>
        const cliCommand = buildReplyCliCommand(threadId, reply.text, author);

        console.log(`Executing: ${cliCommand}`);

        // Execute CLI command synchronously
        execSync(cliCommand, {
            cwd: projectRoot,
            encoding: 'utf-8',
            stdio: 'pipe' // Capture stdout/stderr
        });

        // Success notification
        vscode.window.showInformationMessage(`Reply added to thread ${threadId}`);

        // Create a temporary comment object
        // The actual comment will be loaded from the sidecar file via file watcher
        const tempComment: vscode.Comment = {
            body: new vscode.MarkdownString(reply.text),
            mode: vscode.CommentMode.Preview,
            author: {
                name: author
            },
            timestamp: new Date()
        };

        // Add the temporary comment to the thread
        // This provides immediate feedback while the file watcher reloads
        reply.thread.comments = [...reply.thread.comments, tempComment];

    } catch (error: any) {
        // Show error notification with details
        const errorMessage = error.stderr?.toString() || error.message || 'Unknown error';
        vscode.window.showErrorMessage(`Failed to add reply: ${errorMessage}`);
        console.error('Reply command failed:', error);
    }
}

/**
 * Extracts the thread_id from a CommentThread's contextValue.
 *
 * The contextValue contains JSON with metadata like:
 * {
 *   "thread_id": "01HXYZ...",
 *   "health": "anchored",
 *   "status": "open",
 *   "source_hash": "sha256:...",
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
 * Extracts the source_hash from a CommentThread's contextValue.
 *
 * The source_hash is used for conflict detection - if the on-disk sidecar
 * has a different source_hash, it means the sidecar was modified externally.
 *
 * @param thread - The VSCode CommentThread
 * @returns The source hash string, or null if not found
 */
export function extractSourceHash(thread: vscode.CommentThread): string | null {
    try {
        if (!thread.contextValue) {
            return null;
        }

        const context = JSON.parse(thread.contextValue);
        return context.source_hash || null;
    } catch (error) {
        console.error('Failed to parse thread contextValue:', error);
        return null;
    }
}

/**
 * Builds the CLI command for replying to a thread.
 *
 * @param threadId - The ULID of the thread
 * @param text - The reply text
 * @param author - The author name
 * @returns The complete CLI command string
 */
export function buildReplyCliCommand(
    threadId: string,
    text: string,
    author: string
): string {
    // Escape special characters in text
    // Order matters: escape backslashes first, then quotes, then newlines
    const escapedText = text
        .replace(/\\/g, '\\\\')  // Escape backslashes
        .replace(/"/g, '\\"')    // Escape double quotes
        .replace(/\n/g, '\\n')   // Escape newlines
        .replace(/\r/g, '\\r')   // Escape carriage returns
        .replace(/\t/g, '\\t');  // Escape tabs

    // Build command with proper quoting
    return `comment reply ${threadId} "${escapedText}" --author="${author}"`;
}

/**
 * Registers the reply command with VSCode.
 *
 * This function should be called during extension activation to register
 * the command that handles comment replies.
 *
 * @param context - The VSCode extension context
 * @param projectRoot - Absolute path to project root
 */
export function registerReplyCommand(
    context: vscode.ExtensionContext,
    projectRoot: string
): void {
    // Register the reply command
    // This command is automatically invoked when users submit text in the reply input box
    const replyCommand = vscode.commands.registerCommand(
        'file-native-comments.replyNote',
        (reply: vscode.CommentReply) => {
            return handleReply(reply, projectRoot);
        }
    );

    context.subscriptions.push(replyCommand);

    console.log('Reply command registered: file-native-comments.replyNote');
}
