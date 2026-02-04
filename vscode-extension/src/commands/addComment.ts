/**
 * Add Comment Command
 *
 * Handles the "Add Comment" command triggered via context menu or keyboard shortcut.
 * Captures the selected text range, prompts for comment text, and creates a comment
 * thread via the Python CLI.
 */

import * as vscode from 'vscode';
import * as path from 'path';
import { getAuthor, runCliCommand } from '../utils';

/**
 * Executes the "Add Comment" command.
 *
 * @param projectRoot - Absolute path to project root (directory containing .git)
 */
export async function addCommentCommand(projectRoot: string): Promise<void> {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showErrorMessage('No active editor found');
        return;
    }

    const selection = editor.selection;
    if (selection.isEmpty) {
        vscode.window.showErrorMessage('Please select text to comment on');
        return;
    }

    // Convert VSCode selection (0-indexed) to sidecar format (1-indexed)
    const lineStart = selection.start.line + 1;
    const lineEnd = selection.end.line + 1;

    const absoluteFilePath = editor.document.uri.fsPath;
    const relativeFilePath = path.relative(projectRoot, absoluteFilePath);

    if (relativeFilePath.startsWith('..')) {
        vscode.window.showErrorMessage(
            'File is outside project root and cannot be commented on'
        );
        return;
    }

    const commentText = await vscode.window.showInputBox({
        prompt: `Add comment to ${relativeFilePath} (lines ${lineStart}-${lineEnd})`,
        placeHolder: 'Enter your comment here...',
        ignoreFocusOut: true,
        validateInput: (value) => {
            if (!value || value.trim().length === 0) {
                return 'Comment text cannot be empty';
            }
            return null;
        }
    });

    if (commentText === undefined) {
        return;
    }

    const author = getAuthor();

    try {
        console.log(`Executing: comment add "${relativeFilePath}" -L ${lineStart}:${lineEnd}`);

        await runCliCommand(
            ['comment', 'add', relativeFilePath, '-L', `${lineStart}:${lineEnd}`, `--author=${author}`, commentText],
            projectRoot
        );

        vscode.window.showInformationMessage(
            `Comment added to ${relativeFilePath}:${lineStart}-${lineEnd}`
        );

        console.log(`Comment added successfully to ${relativeFilePath}:${lineStart}-${lineEnd}`);

    } catch (error: any) {
        const errorMessage = error.stderr?.toString() || error.message || 'Unknown error';
        console.error(`Failed to add comment: ${errorMessage}`);

        vscode.window.showErrorMessage(
            `Failed to add comment: ${errorMessage}`
        );
    }
}

/**
 * Registers the "Add Comment" command with VSCode.
 */
export function registerAddCommentCommand(
    context: vscode.ExtensionContext,
    projectRoot: string
): void {
    const disposable = vscode.commands.registerCommand(
        'file-native-comments.addComment',
        () => addCommentCommand(projectRoot)
    );

    context.subscriptions.push(disposable);
    console.log('Add Comment command registered');
}
