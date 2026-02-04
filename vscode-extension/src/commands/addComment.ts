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
import { log } from '../extension';

/**
 * Executes the "Add Comment" command.
 *
 * @param projectRoot - Absolute path to project root (directory containing .git)
 */
export async function addCommentCommand(projectRoot: string): Promise<void> {
    log('addComment command invoked');
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        log('addComment: No active editor');
        vscode.window.showErrorMessage('No active editor found');
        return;
    }

    const selection = editor.selection;
    log(`addComment: selection empty=${selection.isEmpty}, start=${selection.start.line}, end=${selection.end.line}`);
    if (selection.isEmpty) {
        vscode.window.showErrorMessage('Please select text to comment on');
        return;
    }

    // Convert VSCode selection (0-indexed) to sidecar format (1-indexed)
    const lineStart = selection.start.line + 1;
    const lineEnd = selection.end.line + 1;

    const absoluteFilePath = editor.document.uri.fsPath;
    const relativeFilePath = path.relative(projectRoot, absoluteFilePath);
    log(`addComment: file=${relativeFilePath}, lines=${lineStart}-${lineEnd}`);

    if (relativeFilePath.startsWith('..')) {
        log(`addComment: file outside project root`);
        vscode.window.showErrorMessage(
            'File is outside project root and cannot be commented on'
        );
        return;
    }

    log('addComment: showing input box...');
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
        log('addComment: user cancelled input');
        return;
    }

    const author = getAuthor();
    log(`addComment: author=${author}, text="${commentText.substring(0, 50)}"`);

    try {
        const args = ['comment', 'add', relativeFilePath, '-L', `${lineStart}:${lineEnd}`, `--author=${author}`, commentText];
        log(`addComment: executing CLI: ${args.join(' ')}`);

        const result = await runCliCommand(args, projectRoot);
        log(`addComment: CLI result: ${result.substring(0, 200)}`);

        vscode.window.showInformationMessage(
            `Comment added to ${relativeFilePath}:${lineStart}-${lineEnd}`
        );

    } catch (error: any) {
        const errorMessage = error.stderr?.toString() || error.message || 'Unknown error';
        log(`addComment: FAILED: ${errorMessage}`);
        if (error.stack) {
            log(`addComment: stack: ${error.stack}`);
        }

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
