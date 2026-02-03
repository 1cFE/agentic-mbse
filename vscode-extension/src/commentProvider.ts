/**
 * Comment provider for displaying threads from sidecar files.
 *
 * Implements the VSCode DocumentCommentProvider interface to render
 * comment threads as native VSCode UI elements.
 */

import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { readSidecar, Thread, ThreadStatus, AnchorHealth, Comment as SidecarComment } from './sidecar';

/**
 * Provides comment threads for documents by reading from sidecar files.
 *
 * This class:
 * - Reads .comments/*.json sidecar files
 * - Converts Thread objects to vscode.CommentThread
 * - Maps thread status to VSCode resolved/unresolved states
 * - Stores metadata (health, author type) in thread context for future use
 */
export class CommentProvider implements vscode.CommentingRangeProvider {
    private projectRoot: string;
    private commentController: vscode.CommentController;
    private commentThreads: Map<string, vscode.CommentThread[]> = new Map();

    /**
     * Creates a new CommentProvider.
     *
     * @param projectRoot Absolute path to the project root (containing .git or .comments/)
     * @param commentController The VSCode comment controller to register threads with
     */
    constructor(projectRoot: string, commentController: vscode.CommentController) {
        this.projectRoot = projectRoot;
        this.commentController = commentController;
    }

    /**
     * Provides commenting ranges for a document.
     *
     * This method is required by CommentingRangeProvider but we return undefined
     * since we want to allow comments anywhere in the document.
     *
     * @param document The document to provide ranges for
     * @param token Cancellation token
     * @returns undefined (allow comments anywhere)
     */
    provideCommentingRanges(
        document: vscode.TextDocument,
        token: vscode.CancellationToken
    ): vscode.ProviderResult<vscode.Range[]> {
        // Return undefined to allow commenting anywhere in the document
        return undefined;
    }

    /**
     * Loads and displays comment threads for a given document.
     *
     * Called when a document is opened to populate existing comments.
     *
     * @param document The VSCode document to load comments for
     */
    loadCommentsForDocument(document: vscode.TextDocument): void {
        // Read the sidecar file for this document
        const sidecarData = readSidecar(document.uri.fsPath, this.projectRoot);

        // Clear any existing threads for this document
        const documentKey = document.uri.toString();
        const existingThreads = this.commentThreads.get(documentKey);
        if (existingThreads) {
            existingThreads.forEach(thread => thread.dispose());
        }
        this.commentThreads.delete(documentKey);

        // Return if no sidecar exists
        if (sidecarData === null) {
            return;
        }

        // Convert each thread to a VSCode CommentThread
        const threads: vscode.CommentThread[] = [];

        for (const thread of sidecarData.threads) {
            try {
                const vsThread = this.convertThreadToVSCodeThread(thread, document);
                threads.push(vsThread);
            } catch (error) {
                // Log conversion errors but don't fail the entire operation
                console.error(`Failed to convert thread ${thread.id}:`, error);
            }
        }

        // Store threads for this document
        if (threads.length > 0) {
            this.commentThreads.set(documentKey, threads);
        }
    }

    /**
     * Converts a sidecar Thread to a VSCode CommentThread.
     *
     * @param thread The sidecar thread to convert
     * @param document The VSCode document this thread belongs to
     * @returns A VSCode CommentThread object
     */
    private convertThreadToVSCodeThread(
        thread: Thread,
        document: vscode.TextDocument
    ): vscode.CommentThread {
        // Convert 1-indexed line numbers to 0-indexed VSCode ranges
        // VSCode line numbers are 0-indexed, sidecar line numbers are 1-indexed
        const startLine = Math.max(0, thread.anchor.line_start - 1);
        const endLine = Math.max(0, thread.anchor.line_end - 1);

        // Ensure the range is valid for the document
        const documentLineCount = document.lineCount;
        const safeStartLine = Math.min(startLine, documentLineCount - 1);
        const safeEndLine = Math.min(endLine, documentLineCount - 1);

        const range = new vscode.Range(
            safeStartLine,
            0,
            safeEndLine,
            document.lineAt(safeEndLine).text.length
        );

        // Create the comment thread
        const vsThread = this.commentController.createCommentThread(
            document.uri,
            range,
            []
        );

        // Set thread properties
        vsThread.canReply = true;

        // Map thread status to VSCode state
        // "resolved" and "wontfix" both map to resolved state in VSCode
        vsThread.state = (thread.status === ThreadStatus.OPEN)
            ? vscode.CommentThreadState.Unresolved
            : vscode.CommentThreadState.Resolved;

        // Set the label (shown in collapsed state) to the first comment's text
        if (thread.comments.length > 0) {
            const firstCommentBody = thread.comments[0].body;
            // Truncate to first line for label
            const firstLine = firstCommentBody.split('\n')[0];
            vsThread.label = firstLine.substring(0, 100); // Limit to 100 chars
        }

        // Convert comments to VSCode format
        vsThread.comments = thread.comments.map(comment =>
            this.convertCommentToVSCodeComment(comment)
        );

        // Store metadata in context for future use (gutter icons, decorations, etc.)
        // This is a custom property that we can access later
        vsThread.contextValue = JSON.stringify({
            health: thread.anchor.health,
            drift_distance: thread.anchor.drift_distance,
            status: thread.status,
            thread_id: thread.id,
            has_decision: thread.decision !== null
        });

        // Set collapsibility (allow collapse/expand in UI)
        vsThread.collapsibleState = vscode.CommentThreadCollapsibleState.Expanded;

        return vsThread;
    }

    /**
     * Converts a sidecar Comment to a VSCode Comment.
     *
     * @param comment The sidecar comment to convert
     * @returns A VSCode Comment object
     */
    private convertCommentToVSCodeComment(comment: SidecarComment): vscode.Comment {
        // Create a markdown string for the comment body
        const body = new vscode.MarkdownString(comment.body);
        body.isTrusted = true; // Allow markdown features

        // Parse the timestamp to create a Date object
        let timestamp: Date | undefined;
        try {
            timestamp = new Date(comment.timestamp);
        } catch (error) {
            console.warn(`Invalid timestamp for comment ${comment.id}: ${comment.timestamp}`);
        }

        // Create the VSCode comment
        const vsComment: vscode.Comment = {
            body: body,
            mode: vscode.CommentMode.Preview,
            author: {
                name: comment.author,
                // Store author type in icon path for future UI differentiation
                // (e.g., agent comments could have a different icon)
                iconPath: comment.author_type === 'agent'
                    ? vscode.Uri.parse('https://example.com/agent-icon.png')
                    : undefined
            },
            timestamp: timestamp
        };

        return vsComment;
    }

    /**
     * Finds the project root by searching for .git directory.
     *
     * Walks up the directory tree from the given path until a .git directory is found.
     *
     * @param startPath Absolute path to start searching from
     * @returns Absolute path to project root, or null if not found
     */
    static findProjectRoot(startPath: string): string | null {
        let currentPath = startPath;
        const root = path.parse(currentPath).root;

        while (currentPath !== root) {
            const gitPath = path.join(currentPath, '.git');
            if (fs.existsSync(gitPath)) {
                return currentPath;
            }

            // Move up one directory
            const parentPath = path.dirname(currentPath);
            if (parentPath === currentPath) {
                // Reached root without finding .git
                break;
            }
            currentPath = parentPath;
        }

        return null;
    }
}
