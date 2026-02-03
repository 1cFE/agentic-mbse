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

    // Text decoration types for inline highlights (created once, reused)
    private textDecorations: Map<string, vscode.TextEditorDecorationType> = new Map();

    // Active editors with decorations (for cleanup)
    private decoratedEditors: Set<vscode.TextEditor> = new Set();

    constructor() {
        this.initializeGutterDecorations();
        this.initializeTextDecorations();
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
     * Creates text decoration types for inline highlights based on health status.
     *
     * Called once during construction to pre-create all decoration types.
     */
    private initializeTextDecorations(): void {
        // Anchored - Subtle yellow background
        this.textDecorations.set('text-anchored', vscode.window.createTextEditorDecorationType({
            backgroundColor: 'rgba(240, 219, 79, 0.1)', // Yellow with 10% opacity
            borderRadius: '2px'
        }));

        // Drifted - Dashed yellow underline
        this.textDecorations.set('text-drifted', vscode.window.createTextEditorDecorationType({
            textDecoration: 'underline dashed rgba(255, 152, 0, 0.8)', // Orange dashed underline
            borderRadius: '2px'
        }));

        // Orphaned - Strikethrough with dimmed color
        this.textDecorations.set('text-orphaned', vscode.window.createTextEditorDecorationType({
            textDecoration: 'line-through',
            opacity: '0.5'
        }));
    }

    /**
     * Updates gutter decorations and text highlights for an editor based on threads.
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
        const gutterRanges = new Map<string, vscode.DecorationOptions[]>();
        for (const decorationType of this.gutterDecorations.keys()) {
            gutterRanges.set(decorationType, []);
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

            gutterRanges.get(decorationKey)?.push(decorationOptions);
        }

        // Apply all gutter decorations
        for (const [decorationKey, ranges] of gutterRanges) {
            const decorationType = this.gutterDecorations.get(decorationKey);
            if (decorationType && ranges.length > 0) {
                editor.setDecorations(decorationType, ranges);
            }
        }

        // Update text highlights
        this.updateTextDecorations(editor, threads);

        // Track this editor for cleanup
        this.decoratedEditors.add(editor);
    }

    /**
     * Updates text decorations (inline highlights) for an editor based on threads.
     *
     * Applies health-based styling to anchored text ranges.
     * Skips decorations for resolved threads (REQ-3).
     *
     * @param editor The VSCode text editor to update
     * @param threads Array of comment threads to visualize
     */
    private updateTextDecorations(editor: vscode.TextEditor, threads: Thread[]): void {
        // Prepare decoration ranges for each health status
        const textRanges = new Map<string, vscode.Range[]>();
        for (const decorationType of this.textDecorations.keys()) {
            textRanges.set(decorationType, []);
        }

        // Process each thread
        for (const thread of threads) {
            // Skip resolved threads (REQ-3: clear highlights when resolved)
            if (thread.status === ThreadStatus.RESOLVED || thread.status === ThreadStatus.WONTFIX) {
                continue;
            }

            // Determine text decoration key based on health
            const textDecorationKey = this.getTextDecorationKey(thread);
            if (!textDecorationKey) {
                continue; // No decoration for this health status
            }

            // Create range for the entire anchor (line_start to line_end)
            // Convert from 1-indexed (sidecar) to 0-indexed (VSCode)
            const startLine = thread.anchor.line_start - 1;
            const endLine = thread.anchor.line_end - 1;

            // Clamp to document bounds
            const maxLine = Math.max(0, editor.document.lineCount - 1);
            const clampedStartLine = Math.min(startLine, maxLine);
            const clampedEndLine = Math.min(endLine, maxLine);

            // For multi-line anchors, create a range spanning entire lines
            const startChar = 0;
            const endChar = editor.document.lineAt(clampedEndLine).text.length;

            const range = new vscode.Range(clampedStartLine, startChar, clampedEndLine, endChar);
            textRanges.get(textDecorationKey)?.push(range);
        }

        // Apply all text decorations
        for (const [decorationKey, ranges] of textRanges) {
            const decorationType = this.textDecorations.get(decorationKey);
            if (decorationType) {
                editor.setDecorations(decorationType, ranges);
            }
        }
    }

    /**
     * Determines the text decoration key for a thread based on health status.
     *
     * @param thread The thread to get decoration for
     * @returns Text decoration key (e.g., "text-anchored") or null if no decoration
     */
    private getTextDecorationKey(thread: Thread): string | null {
        switch (thread.anchor.health) {
            case AnchorHealth.ANCHORED:
                return 'text-anchored';
            case AnchorHealth.DRIFTED:
                return 'text-drifted';
            case AnchorHealth.ORPHANED:
                return 'text-orphaned';
            default:
                return null;
        }
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
     * Clears all decorations (gutter and text) for an editor.
     *
     * @param editor The editor to clear decorations from
     */
    private clearDecorationsForEditor(editor: vscode.TextEditor): void {
        // Clear gutter decorations
        for (const decorationType of this.gutterDecorations.values()) {
            editor.setDecorations(decorationType, []);
        }

        // Clear text decorations
        for (const decorationType of this.textDecorations.values()) {
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

        // Dispose all gutter decoration types
        for (const decorationType of this.gutterDecorations.values()) {
            decorationType.dispose();
        }
        this.gutterDecorations.clear();

        // Dispose all text decoration types
        for (const decorationType of this.textDecorations.values()) {
            decorationType.dispose();
        }
        this.textDecorations.clear();
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
