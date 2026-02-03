/**
 * Decoration manager for gutter icons and inline text highlights.
 *
 * Provides visual feedback for comment thread locations using:
 * - Status-based gutter icons (yellow/green/red/orange)
 * - Health-based text decorations (solid/dashed/strikethrough)
 */

import * as vscode from 'vscode';
import { Thread, ThreadStatus, AnchorHealth } from './sidecar';

/**
 * Metadata stored in thread contextValue for decoration logic.
 */
interface ThreadMetadata {
    health: AnchorHealth;
    drift_distance: number;
    status: ThreadStatus;
    thread_id: string;
    has_decision: boolean;
}

/**
 * Status priority for resolving conflicts when multiple threads on same line.
 * Higher number = higher priority (shown in gutter).
 */
const STATUS_PRIORITY: Record<string, number> = {
    [AnchorHealth.ORPHANED]: 4,  // Highest priority - critical issue
    [AnchorHealth.DRIFTED]: 3,   // Medium priority - needs attention
    'open': 2,                    // Active threads (unresolved)
    [ThreadStatus.RESOLVED]: 1,  // Lowest priority - resolved
    [ThreadStatus.WONTFIX]: 1    // Same as resolved
};

/**
 * Manages gutter icons and text decorations for comment threads.
 *
 * Creates and applies VSCode decorations based on thread status and health.
 */
export class DecorationManager {
    // Gutter decoration types (created once, reused)
    private gutterDecorations: Map<string, vscode.TextEditorDecorationType> = new Map();

    // Active editors with decorations (for cleanup)
    private decoratedEditors: Set<vscode.TextEditor> = new Set();

    constructor() {
        this.initializeGutterDecorations();
    }

    /**
     * Creates decoration types for each status/health combination.
     *
     * Called once during construction to pre-create all decoration types.
     */
    private initializeGutterDecorations(): void {
        // Open (anchored) - Yellow circle
        this.gutterDecorations.set('open-anchored', vscode.window.createTextEditorDecorationType({
            gutterIconPath: this.createCircleIconDataUri('#f0db4f'), // Yellow
            gutterIconSize: 'contain'
        }));

        // Open (drifted) - Orange circle with drift indicator
        this.gutterDecorations.set('open-drifted', vscode.window.createTextEditorDecorationType({
            gutterIconPath: this.createDriftIconDataUri('#ff9800'), // Orange
            gutterIconSize: 'contain'
        }));

        // Orphaned - Red warning triangle
        this.gutterDecorations.set('orphaned', vscode.window.createTextEditorDecorationType({
            gutterIconPath: this.createWarningIconDataUri('#f44336'), // Red
            gutterIconSize: 'contain'
        }));

        // Resolved - Green checkmark
        this.gutterDecorations.set('resolved', vscode.window.createTextEditorDecorationType({
            gutterIconPath: this.createCheckmarkIconDataUri('#4caf50'), // Green
            gutterIconSize: 'contain'
        }));
    }

    /**
     * Updates gutter decorations for an editor based on threads.
     *
     * Aggregates threads by line number and applies appropriate decorations.
     *
     * @param editor The VSCode text editor to update
     * @param threads Array of comment threads to visualize
     */
    updateGutterDecorations(editor: vscode.TextEditor, threads: Thread[]): void {
        // Clear existing decorations for this editor
        this.clearDecorationsForEditor(editor);

        // Group threads by line number (use line_start for positioning)
        const threadsByLine = new Map<number, Thread[]>();
        for (const thread of threads) {
            const line = thread.anchor.line_start - 1; // Convert to 0-indexed
            if (!threadsByLine.has(line)) {
                threadsByLine.set(line, []);
            }
            threadsByLine.get(line)!.push(thread);
        }

        // Prepare decoration ranges for each type
        const decorationRanges = new Map<string, vscode.DecorationOptions[]>();
        for (const decorationType of this.gutterDecorations.keys()) {
            decorationRanges.set(decorationType, []);
        }

        // Process each line with threads
        for (const [line, lineThreads] of threadsByLine) {
            // Find highest priority thread for this line
            const priorityThread = this.selectPriorityThread(lineThreads);

            // Determine decoration type key
            const decorationKey = this.getDecorationKey(priorityThread);

            // Create decoration range with hover tooltip
            const range = new vscode.Range(line, 0, line, 0);
            const hoverMessage = this.createHoverMessage(lineThreads);

            const decorationOptions: vscode.DecorationOptions = {
                range,
                hoverMessage
            };

            decorationRanges.get(decorationKey)?.push(decorationOptions);
        }

        // Apply all decorations
        for (const [decorationKey, ranges] of decorationRanges) {
            const decorationType = this.gutterDecorations.get(decorationKey);
            if (decorationType && ranges.length > 0) {
                editor.setDecorations(decorationType, ranges);
            }
        }

        // Track this editor for cleanup
        this.decoratedEditors.add(editor);
    }

    /**
     * Selects the highest priority thread from a set of threads on the same line.
     *
     * Priority order: orphaned > drifted > open > resolved
     *
     * @param threads Threads on the same line
     * @returns The thread with highest priority
     */
    private selectPriorityThread(threads: Thread[]): Thread {
        let highestPriority = -1;
        let priorityThread = threads[0];

        for (const thread of threads) {
            const priority = this.getThreadPriority(thread);
            if (priority > highestPriority) {
                highestPriority = priority;
                priorityThread = thread;
            }
        }

        return priorityThread;
    }

    /**
     * Gets the priority value for a thread.
     *
     * @param thread The thread to evaluate
     * @returns Priority value (higher = more important)
     */
    private getThreadPriority(thread: Thread): number {
        // Orphaned and drifted take precedence over status
        if (thread.anchor.health === AnchorHealth.ORPHANED) {
            return STATUS_PRIORITY[AnchorHealth.ORPHANED];
        }
        if (thread.anchor.health === AnchorHealth.DRIFTED) {
            return STATUS_PRIORITY[AnchorHealth.DRIFTED];
        }

        // Otherwise use status priority
        if (thread.status === ThreadStatus.OPEN) {
            return STATUS_PRIORITY['open'];
        }

        return STATUS_PRIORITY[ThreadStatus.RESOLVED];
    }

    /**
     * Determines the decoration key for a thread.
     *
     * @param thread The thread to get decoration for
     * @returns Decoration key (e.g., "open-anchored", "orphaned")
     */
    private getDecorationKey(thread: Thread): string {
        // Orphaned threads always use orphaned decoration
        if (thread.anchor.health === AnchorHealth.ORPHANED) {
            return 'orphaned';
        }

        // Resolved threads always use resolved decoration
        if (thread.status === ThreadStatus.RESOLVED || thread.status === ThreadStatus.WONTFIX) {
            return 'resolved';
        }

        // Open threads use health-based decoration
        if (thread.anchor.health === AnchorHealth.DRIFTED) {
            return 'open-drifted';
        }

        return 'open-anchored';
    }

    /**
     * Creates a hover message for threads on a line.
     *
     * @param threads Threads to include in the message
     * @returns Markdown hover message
     */
    private createHoverMessage(threads: Thread[]): vscode.MarkdownString {
        const lines: string[] = [];

        if (threads.length === 1) {
            const thread = threads[0];
            lines.push(`**Thread #${thread.id.substring(0, 8)}**`);
            lines.push(`Status: ${thread.status}`);
            lines.push(`Health: ${thread.anchor.health}`);
            lines.push(`Comments: ${thread.comments.length}`);

            if (thread.anchor.health === AnchorHealth.DRIFTED) {
                lines.push(`Drift: ${thread.anchor.drift_distance} lines`);
            } else if (thread.anchor.health === AnchorHealth.ORPHANED) {
                lines.push(`⚠️ Anchor lost: \`${thread.anchor.content_snippet.substring(0, 50)}...\``);
            }
        } else {
            lines.push(`**${threads.length} comment threads**`);
            for (const thread of threads) {
                const shortId = thread.id.substring(0, 8);
                const statusIcon = this.getStatusIcon(thread);
                lines.push(`${statusIcon} ${shortId} (${thread.comments.length} comments)`);
            }
        }

        const message = new vscode.MarkdownString(lines.join('\n\n'));
        message.isTrusted = true;
        return message;
    }

    /**
     * Gets a status icon for display in hover messages.
     *
     * @param thread The thread to get icon for
     * @returns Icon string (emoji)
     */
    private getStatusIcon(thread: Thread): string {
        if (thread.anchor.health === AnchorHealth.ORPHANED) {
            return '🔴';
        }
        if (thread.anchor.health === AnchorHealth.DRIFTED) {
            return '🟠';
        }
        if (thread.status === ThreadStatus.RESOLVED || thread.status === ThreadStatus.WONTFIX) {
            return '🟢';
        }
        return '🟡';
    }

    /**
     * Clears all decorations for an editor.
     *
     * @param editor The editor to clear decorations from
     */
    private clearDecorationsForEditor(editor: vscode.TextEditor): void {
        for (const decorationType of this.gutterDecorations.values()) {
            editor.setDecorations(decorationType, []);
        }
    }

    /**
     * Disposes all decoration types and clears tracked editors.
     *
     * Called when the extension deactivates.
     */
    dispose(): void {
        // Clear decorations from all editors
        for (const editor of this.decoratedEditors) {
            this.clearDecorationsForEditor(editor);
        }
        this.decoratedEditors.clear();

        // Dispose all decoration types
        for (const decorationType of this.gutterDecorations.values()) {
            decorationType.dispose();
        }
        this.gutterDecorations.clear();
    }

    /**
     * Creates an SVG data URI for a circle icon.
     *
     * @param color The fill color (hex code)
     * @returns Data URI string
     */
    private createCircleIconDataUri(color: string): vscode.Uri {
        const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16">
            <circle cx="8" cy="8" r="6" fill="${color}" stroke="#000" stroke-width="0.5"/>
        </svg>`;
        return vscode.Uri.parse(`data:image/svg+xml;base64,${Buffer.from(svg).toString('base64')}`);
    }

    /**
     * Creates an SVG data URI for a drift indicator icon (circle with arrows).
     *
     * @param color The fill color (hex code)
     * @returns Data URI string
     */
    private createDriftIconDataUri(color: string): vscode.Uri {
        const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16">
            <circle cx="8" cy="8" r="6" fill="${color}" stroke="#000" stroke-width="0.5"/>
            <path d="M 5 8 L 7 6 M 7 10 L 5 8 M 11 8 L 9 6 M 9 10 L 11 8" stroke="#fff" stroke-width="1.5" fill="none"/>
        </svg>`;
        return vscode.Uri.parse(`data:image/svg+xml;base64,${Buffer.from(svg).toString('base64')}`);
    }

    /**
     * Creates an SVG data URI for a warning icon (triangle with exclamation).
     *
     * @param color The fill color (hex code)
     * @returns Data URI string
     */
    private createWarningIconDataUri(color: string): vscode.Uri {
        const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16">
            <path d="M 8 2 L 14 14 L 2 14 Z" fill="${color}" stroke="#000" stroke-width="0.5"/>
            <text x="8" y="12" font-size="10" font-weight="bold" text-anchor="middle" fill="#fff">!</text>
        </svg>`;
        return vscode.Uri.parse(`data:image/svg+xml;base64,${Buffer.from(svg).toString('base64')}`);
    }

    /**
     * Creates an SVG data URI for a checkmark icon.
     *
     * @param color The fill color (hex code)
     * @returns Data URI string
     */
    private createCheckmarkIconDataUri(color: string): vscode.Uri {
        const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16">
            <circle cx="8" cy="8" r="6" fill="${color}" stroke="#000" stroke-width="0.5"/>
            <path d="M 5 8 L 7 10 L 11 6" stroke="#fff" stroke-width="2" fill="none" stroke-linecap="round"/>
        </svg>`;
        return vscode.Uri.parse(`data:image/svg+xml;base64,${Buffer.from(svg).toString('base64')}`);
    }
}
