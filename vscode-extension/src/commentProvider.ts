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
import { DecorationManager } from './decorations';
import { threadMetadataMap, ThreadMetadata } from './utils';

/**
 * Provides comment threads for documents by reading from sidecar files.
 *
 * This class:
 * - Reads .comments/*.json sidecar files
 * - Converts Thread objects to vscode.CommentThread
 * - Maps thread status to VSCode resolved/unresolved states
 * - Stores metadata in WeakMap for commands to access
 * - Updates threads in-place to avoid UI flashing
 */
export class CommentProvider implements vscode.CommentingRangeProvider {
    private projectRoot: string;
    private commentController: vscode.CommentController;
    private commentThreads: Map<string, vscode.CommentThread[]> = new Map();
    private threadById: Map<string, vscode.CommentThread> = new Map();
    private decorationManager: DecorationManager;

    constructor(projectRoot: string, commentController: vscode.CommentController) {
        this.projectRoot = projectRoot;
        this.commentController = commentController;
        this.decorationManager = new DecorationManager();
    }

    provideCommentingRanges(
        document: vscode.TextDocument,
        token: vscode.CancellationToken
    ): vscode.ProviderResult<vscode.Range[]> {
        const lineCount = document.lineCount;
        if (lineCount === 0) {
            return [];
        }
        return [new vscode.Range(0, 0, lineCount - 1, 0)];
    }

    /**
     * Loads and displays comment threads for a given document.
     *
     * Uses in-place updates to avoid disposing and recreating threads,
     * which prevents UI flashing when switching tabs or when the file watcher fires.
     */
    loadCommentsForDocument(document: vscode.TextDocument): void {
        const sidecarData = readSidecar(document.uri.fsPath, this.projectRoot);
        const documentKey = document.uri.toString();

        if (sidecarData === null) {
            // No sidecar: dispose all existing threads for this document
            const existingThreads = this.commentThreads.get(documentKey);
            if (existingThreads) {
                existingThreads.forEach(thread => {
                    this.threadById.delete(this.getThreadIdFromMap(thread) || '');
                    thread.dispose();
                });
            }
            this.commentThreads.delete(documentKey);

            // Clear decorations
            const editor = vscode.window.visibleTextEditors.find(
                e => e.document.uri.toString() === documentKey
            );
            if (editor) {
                this.decorationManager.updateGutterDecorations(editor, []);
            }
            return;
        }

        // Build a map of new thread data by ID
        const newThreadDataById = new Map<string, Thread>();
        for (const thread of sidecarData.threads) {
            newThreadDataById.set(thread.id, thread);
        }

        // Build set of existing thread IDs for this document
        const existingThreads = this.commentThreads.get(documentKey) || [];
        const existingById = new Map<string, vscode.CommentThread>();
        for (const vsThread of existingThreads) {
            const id = this.getThreadIdFromMap(vsThread);
            if (id) {
                existingById.set(id, vsThread);
            }
        }

        const resultThreads: vscode.CommentThread[] = [];
        const resultThreadMap = new Map<string, vscode.CommentThread>();

        // Update existing threads in-place or dispose removed ones
        for (const [id, vsThread] of existingById) {
            const newData = newThreadDataById.get(id);
            if (newData) {
                // Update in-place
                this.updateThreadInPlace(vsThread, newData, document, sidecarData.source_hash);
                resultThreads.push(vsThread);
                resultThreadMap.set(id, vsThread);
            } else {
                // Thread removed from sidecar — dispose
                this.threadById.delete(id);
                vsThread.dispose();
            }
        }

        // Create new threads that don't exist yet
        for (const [id, threadData] of newThreadDataById) {
            if (!existingById.has(id)) {
                try {
                    const vsThread = this.convertThreadToVSCodeThread(threadData, document, sidecarData.source_hash);
                    resultThreads.push(vsThread);
                    resultThreadMap.set(id, vsThread);
                    this.threadById.set(id, vsThread);
                } catch (error) {
                    console.error(`Failed to convert thread ${id}:`, error);
                }
            }
        }

        // Store threads for this document
        if (resultThreads.length > 0) {
            this.commentThreads.set(documentKey, resultThreads);
        } else {
            this.commentThreads.delete(documentKey);
        }

        // Update gutter decorations
        const editor = vscode.window.visibleTextEditors.find(
            e => e.document.uri.toString() === documentKey
        );
        if (editor) {
            this.decorationManager.updateGutterDecorations(editor, sidecarData.threads, resultThreadMap);
        }
    }

    /**
     * Updates an existing VS Code CommentThread in-place with new sidecar data.
     * This avoids dispose-and-recreate, preventing UI flashing.
     */
    private updateThreadInPlace(
        vsThread: vscode.CommentThread,
        thread: Thread,
        document: vscode.TextDocument,
        sourceHash: string
    ): void {
        // Update range
        const startLine = Math.max(0, thread.anchor.line_start - 1);
        const endLine = Math.max(0, thread.anchor.line_end - 1);
        const documentLineCount = document.lineCount;
        const safeStartLine = Math.min(startLine, documentLineCount - 1);
        const safeEndLine = Math.min(endLine, documentLineCount - 1);

        vsThread.range = new vscode.Range(
            safeStartLine,
            0,
            safeEndLine,
            document.lineAt(safeEndLine).text.length
        );

        // Update state
        vsThread.state = (thread.status === ThreadStatus.OPEN)
            ? vscode.CommentThreadState.Unresolved
            : vscode.CommentThreadState.Resolved;

        // Update label
        if (thread.comments.length > 0) {
            const firstLine = thread.comments[0].body.split('\n')[0];
            vsThread.label = firstLine.substring(0, 100);
        }

        // Update comments
        vsThread.comments = thread.comments.map(comment =>
            this.convertCommentToVSCodeComment(comment)
        );

        // Update contextValue (simple string for when-clause matching)
        vsThread.contextValue = thread.status === ThreadStatus.OPEN ? 'open' : 'resolved';

        // Update WeakMap metadata
        threadMetadataMap.set(vsThread, {
            threadId: thread.id,
            sourceHash: sourceHash,
            health: thread.anchor.health,
            driftDistance: thread.anchor.drift_distance,
            status: thread.status,
            hasDecision: thread.decision !== null
        });
    }

    /**
     * Converts a sidecar Thread to a new VSCode CommentThread.
     */
    private convertThreadToVSCodeThread(
        thread: Thread,
        document: vscode.TextDocument,
        sourceHash: string
    ): vscode.CommentThread {
        const startLine = Math.max(0, thread.anchor.line_start - 1);
        const endLine = Math.max(0, thread.anchor.line_end - 1);
        const documentLineCount = document.lineCount;
        const safeStartLine = Math.min(startLine, documentLineCount - 1);
        const safeEndLine = Math.min(endLine, documentLineCount - 1);

        const range = new vscode.Range(
            safeStartLine,
            0,
            safeEndLine,
            document.lineAt(safeEndLine).text.length
        );

        const vsThread = this.commentController.createCommentThread(
            document.uri,
            range,
            []
        );

        vsThread.canReply = true;

        vsThread.state = (thread.status === ThreadStatus.OPEN)
            ? vscode.CommentThreadState.Unresolved
            : vscode.CommentThreadState.Resolved;

        if (thread.comments.length > 0) {
            const firstLine = thread.comments[0].body.split('\n')[0];
            vsThread.label = firstLine.substring(0, 100);
        }

        vsThread.comments = thread.comments.map(comment =>
            this.convertCommentToVSCodeComment(comment)
        );

        // Simple string contextValue for when-clause matching
        vsThread.contextValue = thread.status === ThreadStatus.OPEN ? 'open' : 'resolved';

        // Store metadata in WeakMap
        threadMetadataMap.set(vsThread, {
            threadId: thread.id,
            sourceHash: sourceHash,
            health: thread.anchor.health,
            driftDistance: thread.anchor.drift_distance,
            status: thread.status,
            hasDecision: thread.decision !== null
        });

        vsThread.collapsibleState = vscode.CommentThreadCollapsibleState.Collapsed;

        return vsThread;
    }

    private convertCommentToVSCodeComment(comment: SidecarComment): vscode.Comment {
        const body = new vscode.MarkdownString(comment.body);
        body.isTrusted = true;

        let timestamp: Date | undefined;
        try {
            timestamp = new Date(comment.timestamp);
        } catch (error) {
            console.warn(`Invalid timestamp for comment ${comment.id}: ${comment.timestamp}`);
        }

        const vsComment: vscode.Comment = {
            body: body,
            mode: vscode.CommentMode.Preview,
            author: {
                name: comment.author,
                iconPath: comment.author_type === 'agent'
                    ? vscode.Uri.parse('https://example.com/agent-icon.png')
                    : undefined
            },
            timestamp: timestamp
        };

        return vsComment;
    }

    /**
     * Gets a thread ID from the WeakMap for an existing VS Code thread.
     */
    private getThreadIdFromMap(vsThread: vscode.CommentThread): string | null {
        const metadata = threadMetadataMap.get(vsThread);
        return metadata?.threadId ?? null;
    }

    static findProjectRoot(startPath: string): string | null {
        let currentPath = startPath;
        const root = path.parse(currentPath).root;

        while (currentPath !== root) {
            const gitPath = path.join(currentPath, '.git');
            if (fs.existsSync(gitPath)) {
                return currentPath;
            }

            const parentPath = path.dirname(currentPath);
            if (parentPath === currentPath) {
                break;
            }
            currentPath = parentPath;
        }

        return null;
    }

    focusThread(threadId: string): boolean {
        return this.decorationManager.focusThread(threadId);
    }

    dispose(): void {
        for (const threads of this.commentThreads.values()) {
            threads.forEach(thread => thread.dispose());
        }
        this.commentThreads.clear();
        this.threadById.clear();
        this.decorationManager.dispose();
    }
}
