import * as vscode from 'vscode';
import * as path from 'path';

/**
 * FileWatcher monitors .comments sidecar files for external changes
 * and notifies subscribers with a 2-second debounce to avoid UI flicker.
 *
 * Implements REQ-5 from vscode-extension.md (File watching with debounce)
 * Implements REQ-4 from concurrency.md (VSCode external change handling)
 */
export class FileWatcher {
    private watcher: vscode.FileSystemWatcher | undefined;
    private debounceTimers: Map<string, NodeJS.Timeout> = new Map();
    private readonly debounceMs: number = 500;
    private callbacks: Array<(sourceFilePath: string) => void> = [];
    private projectRoot: string;

    /**
     * @param projectRoot Absolute path to project root (used to resolve source file paths)
     */
    constructor(projectRoot: string) {
        this.projectRoot = projectRoot;
    }

    /**
     * Starts watching .comments sidecar files for changes.
     * Creates a FileSystemWatcher and sets up debounced change handlers.
     */
    start(): void {
        if (this.watcher) {
            return; // Already started
        }

        // Watch pattern: **/.comments/**/*.json (all sidecar files recursively)
        const pattern = new vscode.RelativePattern(this.projectRoot, '.comments/**/*.json');
        this.watcher = vscode.workspace.createFileSystemWatcher(pattern);

        // Handle all file events (create, change, delete)
        this.watcher.onDidCreate((uri) => this.handleChange(uri));
        this.watcher.onDidChange((uri) => this.handleChange(uri));
        this.watcher.onDidDelete((uri) => this.handleChange(uri));
    }

    /**
     * Stops watching and disposes of the FileSystemWatcher.
     * Clears all pending debounce timers to prevent memory leaks.
     */
    stop(): void {
        if (this.watcher) {
            this.watcher.dispose();
            this.watcher = undefined;
        }

        // Clear all pending timers
        for (const timer of this.debounceTimers.values()) {
            clearTimeout(timer);
        }
        this.debounceTimers.clear();
    }

    /**
     * Registers a callback to be invoked when a sidecar file changes.
     * The callback receives the absolute path to the source file (not the sidecar).
     *
     * @param callback Function to call with source file path after debounce
     */
    onSidecarChanged(callback: (sourceFilePath: string) => void): void {
        this.callbacks.push(callback);
    }

    /**
     * Handles a file change event with debounce logic.
     * Extracts the source file path from the sidecar path and schedules a callback invocation.
     *
     * @param uri URI of the changed sidecar file
     */
    private handleChange(uri: vscode.Uri): void {
        const sidecarPath = uri.fsPath;
        const sourceFilePath = this.extractSourceFilePath(sidecarPath);

        if (!sourceFilePath) {
            return; // Invalid sidecar path, ignore
        }

        // Clear existing timer for this file
        const existingTimer = this.debounceTimers.get(sourceFilePath);
        if (existingTimer) {
            clearTimeout(existingTimer);
        }

        // Set new timer (2-second debounce)
        const timer = setTimeout(() => {
            this.debounceTimers.delete(sourceFilePath);
            this.notifyCallbacks(sourceFilePath);
        }, this.debounceMs);

        this.debounceTimers.set(sourceFilePath, timer);
    }

    /**
     * Notifies all registered callbacks with the source file path.
     *
     * @param sourceFilePath Absolute path to the source file
     */
    private notifyCallbacks(sourceFilePath: string): void {
        for (const callback of this.callbacks) {
            try {
                callback(sourceFilePath);
            } catch (error) {
                console.error('FileWatcher callback error:', error);
            }
        }
    }

    /**
     * Extracts the source file path from a sidecar file path.
     *
     * Example:
     *   /project/.comments/src/example.py.json -> /project/src/example.py
     *
     * @param sidecarPath Absolute path to sidecar file
     * @returns Absolute path to source file, or null if invalid
     */
    private extractSourceFilePath(sidecarPath: string): string | null {
        // Normalize path separators
        const normalizedPath = sidecarPath.replace(/\\/g, '/');

        // Find .comments directory
        const commentsIndex = normalizedPath.indexOf('/.comments/');
        if (commentsIndex === -1) {
            return null;
        }

        // Extract relative path after .comments/
        const afterComments = normalizedPath.substring(commentsIndex + '/.comments/'.length);

        // Remove .json extension
        if (!afterComments.endsWith('.json')) {
            return null;
        }
        const relativeSourcePath = afterComments.substring(0, afterComments.length - '.json'.length);

        // Construct absolute source file path
        const sourceFilePath = path.join(this.projectRoot, relativeSourcePath);

        // Convert back to platform-specific separators
        return sourceFilePath.replace(/\//g, path.sep);
    }
}
