/**
 * Reopen Comment Thread
 *
 * Handles reopening resolved comment threads.
 * Invoked from the context menu on a CommentThread or via command palette.
 */

import * as vscode from 'vscode';
import { handleConflictCheck, ConflictResolution } from '../conflictHandler';
import { extractThreadId, extractSourceHash, runCliCommand } from '../utils';

/**
 * Handles reopening a resolved comment thread.
 *
 * @param thread - The VSCode CommentThread to reopen
 * @param projectRoot - Absolute path to project root
 */
export async function reopenThread(
    thread: vscode.CommentThread,
    projectRoot: string
): Promise<void> {
    try {
        const threadId = extractThreadId(thread);
        if (!threadId) {
            vscode.window.showErrorMessage('Failed to identify thread for reopening');
            return;
        }

        const sourceHash = extractSourceHash(thread);

        const sourcePath = thread.uri.fsPath;

        const resolution = await handleConflictCheck(sourcePath, projectRoot, sourceHash);

        if (resolution === ConflictResolution.CANCEL) {
            vscode.window.showInformationMessage('Reopen cancelled');
            return;
        }

        if (resolution === ConflictResolution.RELOAD) {
            vscode.window.showInformationMessage(
                'Comments reloaded. Please retry reopening after reviewing the updated thread.'
            );
            return;
        }

        console.log(`Executing: comment reopen ${threadId}`);

        await runCliCommand(
            ['comment', 'reopen', threadId],
            projectRoot
        );

        vscode.window.showInformationMessage(`Thread ${threadId} reopened`);

        thread.state = vscode.CommentThreadState.Unresolved;
        thread.contextValue = 'open';
        if (thread.label) {
            thread.label = thread.label.replace(/^\[Resolved\] /, '');
        }

    } catch (error: any) {
        const errorMessage = error.stderr?.toString() || error.message || 'Unknown error';
        vscode.window.showErrorMessage(`Failed to reopen thread: ${errorMessage}`);
        console.error('Reopen command failed:', error);
    }
}

/**
 * Registers the reopen command with VSCode.
 */
export function registerReopenCommand(
    context: vscode.ExtensionContext,
    projectRoot: string
): void {
    const reopenCommand = vscode.commands.registerCommand(
        'file-native-comments.reopenThread',
        (thread: vscode.CommentThread) => {
            return reopenThread(thread, projectRoot);
        }
    );

    context.subscriptions.push(reopenCommand);

    console.log('Reopen command registered: file-native-comments.reopenThread');
}
