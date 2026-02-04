/**
 * Resolve Comment Thread
 *
 * Handles resolving comment threads, optionally capturing a decision.
 * Invoked from the context menu on a CommentThread or via command palette.
 */

import * as vscode from 'vscode';
import { handleConflictCheck, ConflictResolution } from '../conflictHandler';
import { extractThreadId, extractSourceHash, runCliCommand } from '../utils';

/**
 * Handles resolving a comment thread.
 *
 * @param thread - The VSCode CommentThread to resolve
 * @param projectRoot - Absolute path to project root
 */
export async function resolveThread(
    thread: vscode.CommentThread,
    projectRoot: string
): Promise<void> {
    try {
        const threadId = extractThreadId(thread);
        if (!threadId) {
            vscode.window.showErrorMessage('Failed to identify thread for resolution');
            return;
        }

        const sourceHash = extractSourceHash(thread);

        const decision = await vscode.window.showInputBox({
            prompt: 'Enter resolution decision (required)',
            placeHolder: 'Describe why this was resolved, what was decided, etc.',
            validateInput: (value) => {
                if (!value || value.trim().length === 0) {
                    return 'Decision is required. Describe why this was resolved.';
                }
                return null;
            }
        });

        if (decision === undefined) {
            return;
        }

        const trimmedDecision = decision.trim();

        const sourcePath = thread.uri.fsPath;

        const resolution = await handleConflictCheck(sourcePath, projectRoot, sourceHash);

        if (resolution === ConflictResolution.CANCEL) {
            vscode.window.showInformationMessage('Resolution cancelled');
            return;
        }

        if (resolution === ConflictResolution.RELOAD) {
            vscode.window.showInformationMessage(
                'Comments reloaded. Please retry resolution after reviewing the updated thread.'
            );
            return;
        }

        console.log(`Executing: comment resolve ${threadId}`);

        await runCliCommand(
            ['comment', 'resolve', threadId, '--decision', trimmedDecision],
            projectRoot
        );

        vscode.window.showInformationMessage(`Thread ${threadId} resolved`);

        thread.state = vscode.CommentThreadState.Resolved;

    } catch (error: any) {
        const errorMessage = error.stderr?.toString() || error.message || 'Unknown error';
        vscode.window.showErrorMessage(`Failed to resolve thread: ${errorMessage}`);
        console.error('Resolve command failed:', error);
    }
}

/**
 * Registers the resolve command with VSCode.
 */
export function registerResolveCommand(
    context: vscode.ExtensionContext,
    projectRoot: string
): void {
    const resolveCommand = vscode.commands.registerCommand(
        'file-native-comments.resolveThread',
        (thread: vscode.CommentThread) => {
            return resolveThread(thread, projectRoot);
        }
    );

    context.subscriptions.push(resolveCommand);

    console.log('Resolve command registered: file-native-comments.resolveThread');
}
