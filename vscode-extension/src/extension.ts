/**
 * File-Native Comment System - VSCode Extension
 *
 * Provides inline comment threading with .comments/ sidecar storage
 * and intelligent anchor reconciliation.
 */

import * as vscode from 'vscode';
import { CommentProvider } from './commentProvider';
import { FileWatcher } from './fileWatcher';
import { registerAddCommentCommand } from './commands/addComment';
import { registerReplyCommand } from './commands/replyComment';
import { registerResolveCommand } from './commands/resolveThread';
import { registerReopenCommand } from './commands/reopenThread';
import { registerReconcileFileCommand } from './commands/reconcileFile';
import { registerReconcileAllCommand } from './commands/reconcileAll';
import { registerShowDecisionsCommand } from './commands/showDecisions';

/**
 * Extension activation entry point.
 *
 * Called when VSCode starts up (onStartupFinished activation event).
 * Initializes the comment system and registers providers.
 */
export function activate(context: vscode.ExtensionContext): void {
    console.log('File-Native Comment System activated');

    // Register the comment controller
    const commentController = vscode.comments.createCommentController(
        'file-native-comments',
        'File-Native Comments'
    );

    // Store controller in context for disposal on deactivation
    context.subscriptions.push(commentController);

    console.log('CommentController registered');

    // Find project root (directory containing .git)
    const workspaceFolders = vscode.workspace.workspaceFolders;
    if (!workspaceFolders || workspaceFolders.length === 0) {
        console.warn('No workspace folder open, comment system not initialized');
        return;
    }

    const workspaceRoot = workspaceFolders[0].uri.fsPath;
    const projectRoot = CommentProvider.findProjectRoot(workspaceRoot);

    if (!projectRoot) {
        console.warn('No .git directory found, comment system not initialized');
        return;
    }

    console.log(`Project root found: ${projectRoot}`);

    // Create and register the comment provider
    const commentProvider = new CommentProvider(projectRoot, commentController);
    commentController.commentingRangeProvider = commentProvider;

    // Dispose comment provider on deactivation
    context.subscriptions.push({
        dispose: () => commentProvider.dispose()
    });

    console.log('CommentProvider registered');

    // Load comments for all currently open documents
    vscode.workspace.textDocuments.forEach(document => {
        commentProvider.loadCommentsForDocument(document);
    });

    // Load comments when a document is opened
    context.subscriptions.push(
        vscode.workspace.onDidOpenTextDocument(document => {
            commentProvider.loadCommentsForDocument(document);
        })
    );

    // Update decorations when visible editors change (e.g., switching tabs)
    context.subscriptions.push(
        vscode.window.onDidChangeVisibleTextEditors(() => {
            // Refresh decorations for all visible editors
            vscode.window.visibleTextEditors.forEach(editor => {
                commentProvider.loadCommentsForDocument(editor.document);
            });
        })
    );

    // Initialize file watcher for real-time sync with CLI/MCP changes
    const fileWatcher = new FileWatcher(projectRoot);
    fileWatcher.start();

    // When a sidecar file changes, reload comments for the affected source file
    fileWatcher.onSidecarChanged((sourceFilePath) => {
        // Find the open document for this source file
        const document = vscode.workspace.textDocuments.find(
            doc => doc.uri.fsPath === sourceFilePath
        );

        if (document) {
            console.log(`Sidecar changed for ${sourceFilePath}, reloading comments`);
            commentProvider.loadCommentsForDocument(document);
        }
    });

    // Dispose file watcher on deactivation
    context.subscriptions.push({
        dispose: () => fileWatcher.stop()
    });

    // Register "Add Comment" command
    registerAddCommentCommand(context, projectRoot);

    // Register reply command for comment threads
    registerReplyCommand(context, projectRoot);

    // Register resolve and reopen commands for thread management
    registerResolveCommand(context, projectRoot);
    registerReopenCommand(context, projectRoot);

    // Register reconcile file command for manual anchor reconciliation
    registerReconcileFileCommand(context, projectRoot);

    // Register reconcile all command for project-wide reconciliation
    registerReconcileAllCommand(context, projectRoot, commentProvider);

    // Register show decisions command to view DECISIONS.md
    registerShowDecisionsCommand(context, projectRoot);

    // Register "Focus Thread" command (for programmatic and UI use)
    // This command can be triggered by clicking gutter icons or via command palette
    context.subscriptions.push(
        vscode.commands.registerCommand('file-native-comments.focusThread', async (threadId?: string) => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showWarningMessage('No active editor');
                return;
            }

            // If no threadId provided, show quick pick of threads in current file
            if (!threadId) {
                const { readSidecar } = require('./sidecar');
                const sidecarData = readSidecar(editor.document.uri.fsPath, projectRoot);

                if (!sidecarData || sidecarData.threads.length === 0) {
                    vscode.window.showInformationMessage('No comments in this file');
                    return;
                }

                // Create quick pick items with threadId property
                interface ThreadQuickPickItem extends vscode.QuickPickItem {
                    threadId: string;
                }

                const items: ThreadQuickPickItem[] = sidecarData.threads.map((thread: any) => ({
                    label: `Line ${thread.anchor.line_start}: ${thread.comments[0].body.split('\n')[0].substring(0, 50)}`,
                    description: `${thread.status} • ${thread.comments.length} comments`,
                    threadId: thread.id
                }));

                const selected = await vscode.window.showQuickPick(items, {
                    placeHolder: 'Select a comment thread to navigate to'
                });

                if (selected) {
                    threadId = selected.threadId;
                }
            }

            // Focus the thread
            if (threadId) {
                console.log(`Focus thread command invoked with ID: ${threadId}`);
                const success = commentProvider.focusThread(threadId);
                if (!success) {
                    vscode.window.showWarningMessage(`Could not find thread ${threadId.substring(0, 8)}`);
                }
            }
        })
    );
}

/**
 * Extension deactivation entry point.
 *
 * Called when the extension is deactivated (e.g., VSCode shutdown).
 * Cleanup resources and dispose of registered providers.
 */
export function deactivate(): void {
    console.log('File-Native Comment System deactivated');
}
