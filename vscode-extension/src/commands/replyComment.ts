/**
 * Reply to Comment Thread
 *
 * Handles replies to existing comment threads. Invoked when users type in
 * the reply input box at the bottom of a CommentThread.
 */

import * as vscode from 'vscode';
import { handleConflictCheck, ConflictResolution } from '../conflictHandler';
import { extractThreadId, extractSourceHash, getAuthor, runCliCommand } from '../utils';

/**
 * Handles reply to a comment thread.
 *
 * @param reply - The VSCode CommentReply object (contains thread and text)
 * @param projectRoot - Absolute path to project root
 */
export async function handleReply(
    reply: vscode.CommentReply,
    projectRoot: string
): Promise<void> {
    try {
        const threadId = extractThreadId(reply.thread);
        if (!threadId) {
            vscode.window.showErrorMessage('Failed to identify thread for reply');
            return;
        }

        const sourceHash = extractSourceHash(reply.thread);

        if (!reply.text || reply.text.trim().length === 0) {
            vscode.window.showErrorMessage('Reply text cannot be empty');
            return;
        }

        const sourcePath = reply.thread.uri.fsPath;

        const resolution = await handleConflictCheck(sourcePath, projectRoot, sourceHash);

        if (resolution === ConflictResolution.CANCEL) {
            vscode.window.showInformationMessage('Reply cancelled');
            return;
        }

        if (resolution === ConflictResolution.RELOAD) {
            vscode.window.showInformationMessage(
                'Comments reloaded. Please retry your reply after reviewing the updated thread.'
            );
            return;
        }

        const author = getAuthor();

        console.log(`Executing: comment reply ${threadId}`);

        await runCliCommand(
            ['comment', 'reply', threadId, reply.text, `--author=${author}`],
            projectRoot
        );

        vscode.window.showInformationMessage(`Reply added to thread ${threadId}`);

        const tempComment: vscode.Comment = {
            body: new vscode.MarkdownString(reply.text),
            mode: vscode.CommentMode.Preview,
            author: {
                name: author
            },
            timestamp: new Date()
        };

        reply.thread.comments = [...reply.thread.comments, tempComment];

    } catch (error: any) {
        const errorMessage = error.stderr?.toString() || error.message || 'Unknown error';
        vscode.window.showErrorMessage(`Failed to add reply: ${errorMessage}`);
        console.error('Reply command failed:', error);
    }
}

/**
 * Registers the reply command with VSCode.
 */
export function registerReplyCommand(
    context: vscode.ExtensionContext,
    projectRoot: string
): void {
    const replyCommand = vscode.commands.registerCommand(
        'file-native-comments.replyNote',
        (reply: vscode.CommentReply) => {
            return handleReply(reply, projectRoot);
        }
    );

    context.subscriptions.push(replyCommand);

    console.log('Reply command registered: file-native-comments.replyNote');
}
