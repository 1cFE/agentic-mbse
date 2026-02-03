/**
 * Add Comment Command
 *
 * Handles the "Add Comment" command triggered via context menu or keyboard shortcut.
 * Captures the selected text range, prompts for comment text, and creates a comment
 * thread via the Python CLI.
 */

import * as vscode from 'vscode';
import { execSync } from 'child_process';
import * as path from 'path';

/**
 * Executes the "Add Comment" command.
 *
 * Workflow:
 * 1. Validate active editor and selection
 * 2. Convert VSCode selection (0-indexed) to sidecar format (1-indexed)
 * 3. Prompt user for comment text
 * 4. Call Python CLI: `comment add <file> -L <start>:<end> "<text>"`
 * 5. Show success/error notification
 *
 * @param projectRoot - Absolute path to project root (directory containing .git)
 */
export async function addCommentCommand(projectRoot: string): Promise<void> {
    // Get active text editor
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showErrorMessage('No active editor found');
        return;
    }

    // Get selection
    const selection = editor.selection;
    if (selection.isEmpty) {
        vscode.window.showErrorMessage('Please select text to comment on');
        return;
    }

    // Convert VSCode selection (0-indexed) to sidecar format (1-indexed)
    const lineStart = selection.start.line + 1;
    const lineEnd = selection.end.line + 1;

    // Get file path relative to project root
    const absoluteFilePath = editor.document.uri.fsPath;
    const relativeFilePath = path.relative(projectRoot, absoluteFilePath);

    // Validate file is within project root
    if (relativeFilePath.startsWith('..')) {
        vscode.window.showErrorMessage(
            'File is outside project root and cannot be commented on'
        );
        return;
    }

    // Prompt for comment text
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

    // User cancelled
    if (commentText === undefined) {
        return;
    }

    // Get author from VSCode environment (fallback to 'vscode-user')
    // Note: vscode.env.username is available in VSCode 1.55+
    const author = (vscode.env as any).username || 'vscode-user';

    try {
        // Build CLI command
        // Format: comment add <file> -L <start>:<end> --author=<author> "<text>"
        const cliCommand = buildCliCommand(
            relativeFilePath,
            lineStart,
            lineEnd,
            author,
            commentText
        );

        console.log(`Executing: ${cliCommand}`);

        // Execute CLI command synchronously
        execSync(cliCommand, {
            cwd: projectRoot,
            encoding: 'utf-8',
            stdio: 'pipe' // Capture stdout/stderr
        });

        // Success notification
        vscode.window.showInformationMessage(
            `Comment added to ${relativeFilePath}:${lineStart}-${lineEnd}`
        );

        console.log(`Comment added successfully to ${relativeFilePath}:${lineStart}-${lineEnd}`);

    } catch (error: any) {
        // CLI command failed
        const errorMessage = error.stderr?.toString() || error.message || 'Unknown error';
        console.error(`Failed to add comment: ${errorMessage}`);

        vscode.window.showErrorMessage(
            `Failed to add comment: ${errorMessage}`
        );
    }
}

/**
 * Builds the CLI command string for adding a comment.
 *
 * Escapes special characters in comment text to prevent shell injection.
 *
 * @param filePath - Relative file path from project root
 * @param lineStart - Starting line number (1-indexed)
 * @param lineEnd - Ending line number (1-indexed)
 * @param author - Author username
 * @param commentText - Comment body text
 * @returns CLI command string
 */
function buildCliCommand(
    filePath: string,
    lineStart: number,
    lineEnd: number,
    author: string,
    commentText: string
): string {
    // Escape double quotes and backslashes in comment text
    const escapedText = commentText
        .replace(/\\/g, '\\\\')  // Escape backslashes first
        .replace(/"/g, '\\"');   // Escape double quotes

    // Build command with proper quoting
    // Note: Using 'comment' directly assumes it's in PATH (e.g., via uv tool install)
    return `comment add "${filePath}" -L ${lineStart}:${lineEnd} --author="${author}" "${escapedText}"`;
}

/**
 * Registers the "Add Comment" command with VSCode.
 *
 * @param context - Extension context for subscriptions
 * @param projectRoot - Absolute path to project root
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
