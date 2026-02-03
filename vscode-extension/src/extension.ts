/**
 * File-Native Comment System - VSCode Extension
 *
 * Provides inline comment threading with .comments/ sidecar storage
 * and intelligent anchor reconciliation.
 */

import * as vscode from 'vscode';
import { CommentProvider } from './commentProvider';
import { FileWatcher } from './fileWatcher';

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
