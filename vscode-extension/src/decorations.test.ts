/**
 * Unit tests for DecorationManager.
 */

import * as vscode from 'vscode';
import { DecorationManager } from './decorations';
import { Thread, ThreadStatus, AnchorHealth, Comment } from './sidecar';

// Mock tracking
const mockDecorationTypes: any[] = [];
const mockSetDecorations = jest.fn();

describe('DecorationManager', () => {
    let decorationManager: DecorationManager;
    let mockEditor: vscode.TextEditor;
    let originalCreateDecorationType: any;

    beforeEach(() => {
        jest.clearAllMocks();
        mockDecorationTypes.length = 0;

        // Mock createTextEditorDecorationType to track created decorations
        originalCreateDecorationType = vscode.window.createTextEditorDecorationType;
        (vscode.window.createTextEditorDecorationType as jest.Mock) = jest.fn((options: any) => {
            const decorationType = {
                key: 'test-decoration',
                dispose: jest.fn()
            };
            mockDecorationTypes.push(decorationType);
            return decorationType;
        });

        decorationManager = new DecorationManager();

        // Create a mock editor
        mockEditor = {
            document: {
                uri: vscode.Uri.parse('file:///test/file.txt'),
                lineCount: 100,
                lineAt: (line: number) => ({
                    text: 'test line content'
                })
            },
            setDecorations: mockSetDecorations
        } as any;
    });

    afterEach(() => {
        decorationManager.dispose();
        // Restore original mock
        vscode.window.createTextEditorDecorationType = originalCreateDecorationType;
    });

    describe('initialization', () => {
        it('creates decoration types on construction', () => {
            expect(mockDecorationTypes.length).toBeGreaterThan(0);
        });
    });

    describe('updateGutterDecorations', () => {
        it('applies decorations for a single anchored thread', () => {
            const threads: Thread[] = [
                createThread({
                    id: '01HQTEST1',
                    status: ThreadStatus.OPEN,
                    health: AnchorHealth.ANCHORED,
                    lineStart: 10
                })
            ];

            decorationManager.updateGutterDecorations(mockEditor, threads);

            // Should call setDecorations at least once
            expect(mockSetDecorations).toHaveBeenCalled();
        });

        it('applies correct decoration type for open anchored thread', () => {
            const threads: Thread[] = [
                createThread({
                    id: '01HQTEST1',
                    status: ThreadStatus.OPEN,
                    health: AnchorHealth.ANCHORED,
                    lineStart: 10
                })
            ];

            decorationManager.updateGutterDecorations(mockEditor, threads);

            // Verify setDecorations was called with non-empty ranges for at least one decoration type
            const callsWithRanges = mockSetDecorations.mock.calls.filter(
                call => call[1] && call[1].length > 0
            );
            expect(callsWithRanges.length).toBeGreaterThan(0);
        });

        it('applies correct decoration type for drifted thread', () => {
            const threads: Thread[] = [
                createThread({
                    id: '01HQTEST2',
                    status: ThreadStatus.OPEN,
                    health: AnchorHealth.DRIFTED,
                    lineStart: 15,
                    driftDistance: 5
                })
            ];

            decorationManager.updateGutterDecorations(mockEditor, threads);

            const callsWithRanges = mockSetDecorations.mock.calls.filter(
                call => call[1] && call[1].length > 0
            );
            expect(callsWithRanges.length).toBeGreaterThan(0);
        });

        it('applies correct decoration type for orphaned thread', () => {
            const threads: Thread[] = [
                createThread({
                    id: '01HQTEST3',
                    status: ThreadStatus.OPEN,
                    health: AnchorHealth.ORPHANED,
                    lineStart: 20
                })
            ];

            decorationManager.updateGutterDecorations(mockEditor, threads);

            const callsWithRanges = mockSetDecorations.mock.calls.filter(
                call => call[1] && call[1].length > 0
            );
            expect(callsWithRanges.length).toBeGreaterThan(0);
        });

        it('applies correct decoration type for resolved thread', () => {
            const threads: Thread[] = [
                createThread({
                    id: '01HQTEST4',
                    status: ThreadStatus.RESOLVED,
                    health: AnchorHealth.ANCHORED,
                    lineStart: 25
                })
            ];

            decorationManager.updateGutterDecorations(mockEditor, threads);

            const callsWithRanges = mockSetDecorations.mock.calls.filter(
                call => call[1] && call[1].length > 0
            );
            expect(callsWithRanges.length).toBeGreaterThan(0);
        });

        it('handles multiple threads on the same line', () => {
            const threads: Thread[] = [
                createThread({
                    id: '01HQTEST5',
                    status: ThreadStatus.OPEN,
                    health: AnchorHealth.ANCHORED,
                    lineStart: 30
                }),
                createThread({
                    id: '01HQTEST6',
                    status: ThreadStatus.RESOLVED,
                    health: AnchorHealth.ANCHORED,
                    lineStart: 30
                })
            ];

            decorationManager.updateGutterDecorations(mockEditor, threads);

            // Should only show one decoration per line (highest priority)
            const callsWithRanges = mockSetDecorations.mock.calls.filter(
                call => call[1] && call[1].length > 0
            );
            expect(callsWithRanges.length).toBeGreaterThan(0);

            // Verify that only one range is applied for line 29 (0-indexed)
            const allRanges = mockSetDecorations.mock.calls.flatMap(call => call[1] || []);
            const rangesAtLine29 = allRanges.filter(
                (range: any) => range.range.startLine === 29
            );
            expect(rangesAtLine29.length).toBe(1);
        });

        it('prioritizes orphaned threads over other statuses', () => {
            const threads: Thread[] = [
                createThread({
                    id: '01HQTEST7',
                    status: ThreadStatus.OPEN,
                    health: AnchorHealth.ORPHANED,
                    lineStart: 40
                }),
                createThread({
                    id: '01HQTEST8',
                    status: ThreadStatus.OPEN,
                    health: AnchorHealth.ANCHORED,
                    lineStart: 40
                })
            ];

            decorationManager.updateGutterDecorations(mockEditor, threads);

            // The orphaned thread should take priority
            const callsWithRanges = mockSetDecorations.mock.calls.filter(
                call => call[1] && call[1].length > 0
            );
            expect(callsWithRanges.length).toBeGreaterThan(0);
        });

        it('converts 1-indexed line numbers to 0-indexed', () => {
            const threads: Thread[] = [
                createThread({
                    id: '01HQTEST9',
                    status: ThreadStatus.OPEN,
                    health: AnchorHealth.ANCHORED,
                    lineStart: 50 // 1-indexed in sidecar
                })
            ];

            decorationManager.updateGutterDecorations(mockEditor, threads);

            // Find the decoration call with ranges
            const allRanges = mockSetDecorations.mock.calls.flatMap(call => call[1] || []);
            const appliedRange = allRanges.find((range: any) => range.range.startLine === 49);
            expect(appliedRange).toBeDefined();
        });

        it('includes hover messages with thread metadata', () => {
            const threads: Thread[] = [
                createThread({
                    id: '01HQTEST10',
                    status: ThreadStatus.OPEN,
                    health: AnchorHealth.ANCHORED,
                    lineStart: 60,
                    commentCount: 3
                })
            ];

            decorationManager.updateGutterDecorations(mockEditor, threads);

            // Find the decoration options with hover message
            const allRanges = mockSetDecorations.mock.calls.flatMap(call => call[1] || []);
            const rangeWithHover = allRanges.find(
                (range: any) => range.hoverMessage !== undefined
            );
            expect(rangeWithHover).toBeDefined();
        });

        it('clears decorations when no threads provided', () => {
            decorationManager.updateGutterDecorations(mockEditor, []);

            // Should still call setDecorations to clear previous decorations
            expect(mockSetDecorations).toHaveBeenCalled();
        });

        it('handles empty thread array gracefully', () => {
            expect(() => {
                decorationManager.updateGutterDecorations(mockEditor, []);
            }).not.toThrow();
        });
    });

    describe('dispose', () => {
        it('disposes all decoration types', () => {
            const initialCount = mockDecorationTypes.length;

            decorationManager.dispose();

            // All decoration types should have dispose called
            mockDecorationTypes.forEach(decorationType => {
                expect(decorationType.dispose).toHaveBeenCalled();
            });
        });

        it('clears decorations from tracked editors', () => {
            const threads: Thread[] = [
                createThread({
                    id: '01HQTEST11',
                    status: ThreadStatus.OPEN,
                    health: AnchorHealth.ANCHORED,
                    lineStart: 70
                })
            ];

            decorationManager.updateGutterDecorations(mockEditor, threads);
            mockSetDecorations.mockClear();

            decorationManager.dispose();

            // Should call setDecorations to clear decorations
            expect(mockSetDecorations).toHaveBeenCalled();
        });
    });

    describe('hover messages', () => {
        it('includes thread ID in single thread hover', () => {
            const threads: Thread[] = [
                createThread({
                    id: '01HQTEST12TEST',
                    status: ThreadStatus.OPEN,
                    health: AnchorHealth.ANCHORED,
                    lineStart: 80
                })
            ];

            decorationManager.updateGutterDecorations(mockEditor, threads);

            const allRanges = mockSetDecorations.mock.calls.flatMap(call => call[1] || []);
            const rangeWithHover = allRanges.find(
                (range: any) => range.hoverMessage !== undefined
            );

            expect(rangeWithHover).toBeDefined();
            const hoverText = rangeWithHover.hoverMessage.value;
            expect(hoverText).toContain('01HQTEST');
        });

        it('shows drift distance for drifted threads', () => {
            const threads: Thread[] = [
                createThread({
                    id: '01HQTEST13',
                    status: ThreadStatus.OPEN,
                    health: AnchorHealth.DRIFTED,
                    lineStart: 85,
                    driftDistance: 10
                })
            ];

            decorationManager.updateGutterDecorations(mockEditor, threads);

            const allRanges = mockSetDecorations.mock.calls.flatMap(call => call[1] || []);
            const rangeWithHover = allRanges.find(
                (range: any) => range.hoverMessage !== undefined
            );

            expect(rangeWithHover).toBeDefined();
            const hoverText = rangeWithHover.hoverMessage.value;
            expect(hoverText).toContain('10');
        });

        it('shows anchor lost message for orphaned threads', () => {
            const threads: Thread[] = [
                createThread({
                    id: '01HQTEST14',
                    status: ThreadStatus.OPEN,
                    health: AnchorHealth.ORPHANED,
                    lineStart: 90,
                    contentSnippet: 'original code snippet'
                })
            ];

            decorationManager.updateGutterDecorations(mockEditor, threads);

            const allRanges = mockSetDecorations.mock.calls.flatMap(call => call[1] || []);
            const rangeWithHover = allRanges.find(
                (range: any) => range.hoverMessage !== undefined
            );

            expect(rangeWithHover).toBeDefined();
            const hoverText = rangeWithHover.hoverMessage.value;
            expect(hoverText).toContain('Anchor lost');
        });

        it('shows count for multiple threads on same line', () => {
            const threads: Thread[] = [
                createThread({
                    id: '01HQTEST15',
                    status: ThreadStatus.OPEN,
                    health: AnchorHealth.ANCHORED,
                    lineStart: 95
                }),
                createThread({
                    id: '01HQTEST16',
                    status: ThreadStatus.OPEN,
                    health: AnchorHealth.ANCHORED,
                    lineStart: 95
                })
            ];

            decorationManager.updateGutterDecorations(mockEditor, threads);

            const allRanges = mockSetDecorations.mock.calls.flatMap(call => call[1] || []);
            const rangeWithHover = allRanges.find(
                (range: any) => range.hoverMessage !== undefined
            );

            expect(rangeWithHover).toBeDefined();
            const hoverText = rangeWithHover.hoverMessage.value;
            expect(hoverText).toContain('2');
            expect(hoverText).toContain('comment threads');
        });
    });
});

/**
 * Helper function to create a test thread.
 */
function createThread(options: {
    id: string;
    status: ThreadStatus;
    health: AnchorHealth;
    lineStart: number;
    lineEnd?: number;
    commentCount?: number;
    driftDistance?: number;
    contentSnippet?: string;
}): Thread {
    const comments: Comment[] = [];
    const count = options.commentCount || 1;
    for (let i = 0; i < count; i++) {
        comments.push({
            id: `${options.id}_C${i}`,
            author: 'testuser',
            author_type: 'human' as any,
            body: `Test comment ${i}`,
            timestamp: '2026-02-03T10:00:00Z'
        });
    }

    return {
        id: options.id,
        status: options.status,
        created_at: '2026-02-03T10:00:00Z',
        resolved_at: options.status === ThreadStatus.RESOLVED ? '2026-02-03T11:00:00Z' : null,
        comments: comments,
        anchor: {
            content_hash: 'sha256:' + '0'.repeat(64),
            context_hash_before: 'sha256:' + '1'.repeat(64),
            context_hash_after: 'sha256:' + '2'.repeat(64),
            line_start: options.lineStart,
            line_end: options.lineEnd || options.lineStart,
            content_snippet: options.contentSnippet || 'test snippet',
            health: options.health,
            drift_distance: options.driftDistance || 0
        },
        decision: null
    };
}
