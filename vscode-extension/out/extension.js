"use strict";
/**
 * File-Native Comment System - VSCode Extension
 *
 * Provides inline comment threading with .comments/ sidecar storage
 * and intelligent anchor reconciliation.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
exports.deactivate = deactivate;
/**
 * Extension activation entry point.
 *
 * Called when VSCode starts up (onStartupFinished activation event).
 * Initializes the comment system and registers providers.
 */
function activate(context) {
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
function deactivate() {
    console.log('File-Native Comment System deactivated');
}
//# sourceMappingURL=extension.js.map