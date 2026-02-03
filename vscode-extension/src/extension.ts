/**
 * File-Native Comment System - VSCode Extension
 *
 * Provides inline comment threading with .comments/ sidecar storage
 * and intelligent anchor reconciliation.
 */

import * as vscode from 'vscode';

/**
 * Extension activation entry point.
 *
 * Called when VSCode starts up (onStartupFinished activation event).
 * Initializes the comment system and registers providers.
 */
export function activate(context: vscode.ExtensionContext): void {
    console.log('File-Native Comment System activated');

    // Future: Register CommentController here
    // Future: Initialize file watchers for .comments/ directory
    // Future: Load sidecar files and display comment threads
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
