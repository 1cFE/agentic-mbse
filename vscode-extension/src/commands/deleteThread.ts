/**
 * Delete Comment Thread
 *
 * Handles deleting comment threads permanently.
 * Invoked from the title bar of a CommentThread.
 */

import * as vscode from 'vscode';
import { extractThreadId, runCliCommand } from '../utils';

/**
 * Handles deleting a comment thread.
 *
 * @param thread - The VSCode CommentThread to delete
 * @param projectRoot - Absolute path to project root
 */
export async function deleteThread(
    thread: vscode.CommentThread,
    projectRoot: string
): Promise<void> {
    try {
        const threadId = extractThreadId(thread);
        if (!threadId) {
            vscode.window.showErrorMessage('Failed to identify thread for deletion');
            return;
        }

        // Confirm with user
        const confirmation = await vscode.window.showWarningMessage(
            `Delete this comment thread? This cannot be undone.`,
            { modal: true },
            'Delete',
            'Cancel'
        );

        if (confirmation !== 'Delete') {
            return;
        }

        console.log(`Executing: comment delete ${threadId} --force`);

        await runCliCommand(
            ['comment', 'delete', threadId, '--force'],
            projectRoot
        );

        vscode.window.showInformationMessage(`Thread deleted`);

        // Dispose the thread from the UI
        thread.dispose();

    } catch (error: any) {
        const errorMessage = error.stderr?.toString() || error.message || 'Unknown error';
        vscode.window.showErrorMessage(`Failed to delete thread: ${errorMessage}`);
        console.error('Delete command failed:', error);
    }
}

/**
 * Registers the delete command with VSCode.
 */
export function registerDeleteCommand(
    context: vscode.ExtensionContext,
    projectRoot: string
): void {
    const deleteCommand = vscode.commands.registerCommand(
        'file-native-comments.deleteThread',
        (thread: vscode.CommentThread) => {
            return deleteThread(thread, projectRoot);
        }
    );

    context.subscriptions.push(deleteCommand);

    console.log('Delete command registered: file-native-comments.deleteThread');
}
