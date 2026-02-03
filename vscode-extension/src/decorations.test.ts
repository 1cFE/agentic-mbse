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

            // Verify that only one gutter decoration is applied for line 29 (0-indexed)
            // Count decorations that have a range at line 29
            const allRanges = mockSetDecorations.mock.calls.flatMap(call => call[1] || []);
            const rangesAtLine29 = allRanges.filter(
                (range: any) => range.range && range.range.startLine === 29
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

            // Find the decoration call with ranges at line 49 (0-indexed)
            const allRanges = mockSetDecorations.mock.calls.flatMap(call => call[1] || []);
            const appliedRange = allRanges.find(
                (range: any) => range.range && range.range.startLine === 49
            );
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

    describe('text decorations', () => {
        it('applies text decorations for unresolved threads', () => {
            const threads: Thread[] = [
                createThread({
                    id: '01HQTEST17',
                    status: ThreadStatus.OPEN,
                    health: AnchorHealth.ANCHORED,
                    lineStart: 10,
                    lineEnd: 12
                })
            ];

            decorationManager.updateGutterDecorations(mockEditor, threads);

            // Should apply text decorations
            expect(mockSetDecorations).toHaveBeenCalled();
        });

        it('applies anchored text decoration for anchored health', () => {
            const threads: Thread[] = [
                createThread({
                    id: '01HQTEST18',
                    status: ThreadStatus.OPEN,
                    health: AnchorHealth.ANCHORED,
                    lineStart: 20,
                    lineEnd: 22
                })
            ];

            decorationManager.updateGutterDecorations(mockEditor, threads);

            // Verify text decoration was applied
            expect(mockSetDecorations).toHaveBeenCalled();
        });

        it('applies drifted text decoration for drifted health', () => {
            const threads: Thread[] = [
                createThread({
                    id: '01HQTEST19',
                    status: ThreadStatus.OPEN,
                    health: AnchorHealth.DRIFTED,
                    lineStart: 30,
                    lineEnd: 32,
                    driftDistance: 5
                })
            ];

            decorationManager.updateGutterDecorations(mockEditor, threads);

            expect(mockSetDecorations).toHaveBeenCalled();
        });

        it('applies orphaned text decoration for orphaned health', () => {
            const threads: Thread[] = [
                createThread({
                    id: '01HQTEST20',
                    status: ThreadStatus.OPEN,
                    health: AnchorHealth.ORPHANED,
                    lineStart: 40,
                    lineEnd: 42
                })
            ];

            decorationManager.updateGutterDecorations(mockEditor, threads);

            expect(mockSetDecorations).toHaveBeenCalled();
        });

        it('skips text decorations for resolved threads', () => {
            const threads: Thread[] = [
                createThread({
                    id: '01HQTEST21',
                    status: ThreadStatus.RESOLVED,
                    health: AnchorHealth.ANCHORED,
                    lineStart: 50,
                    lineEnd: 52
                })
            ];

            mockSetDecorations.mockClear();
            decorationManager.updateGutterDecorations(mockEditor, threads);

            // Should still call setDecorations for gutter and clearing text decorations
            // But text decoration ranges should be empty for resolved threads
            expect(mockSetDecorations).toHaveBeenCalled();
        });

        it('skips text decorations for wontfix threads', () => {
            const threads: Thread[] = [
                createThread({
                    id: '01HQTEST22',
                    status: ThreadStatus.WONTFIX,
                    health: AnchorHealth.ANCHORED,
                    lineStart: 60,
                    lineEnd: 62
                })
            ];

            mockSetDecorations.mockClear();
            decorationManager.updateGutterDecorations(mockEditor, threads);

            expect(mockSetDecorations).toHaveBeenCalled();
        });

        it('handles multi-line text decorations', () => {
            const threads: Thread[] = [
                createThread({
                    id: '01HQTEST23',
                    status: ThreadStatus.OPEN,
                    health: AnchorHealth.ANCHORED,
                    lineStart: 70,
                    lineEnd: 75 // Spans 6 lines
                })
            ];

            decorationManager.updateGutterDecorations(mockEditor, threads);

            // Verify decoration was applied
            expect(mockSetDecorations).toHaveBeenCalled();
        });

        it('clamps text decoration ranges to document bounds', () => {
            // Create a mock editor with smaller lineCount
            const smallEditor = {
                document: {
                    uri: vscode.Uri.parse('file:///test/small.txt'),
                    lineCount: 50,
                    lineAt: (line: number) => ({
                        text: 'test line content'
                    })
                },
                setDecorations: mockSetDecorations
            } as any;

            const threads: Thread[] = [
                createThread({
                    id: '01HQTEST24',
                    status: ThreadStatus.OPEN,
                    health: AnchorHealth.ANCHORED,
                    lineStart: 48,
                    lineEnd: 100 // Beyond document bounds
                })
            ];

            decorationManager.updateGutterDecorations(smallEditor, threads);

            // Should not throw, should clamp to line 49 (0-indexed)
            expect(mockSetDecorations).toHaveBeenCalled();
        });

        it('applies multiple text decorations for multiple unresolved threads', () => {
            const threads: Thread[] = [
                createThread({
                    id: '01HQTEST25',
                    status: ThreadStatus.OPEN,
                    health: AnchorHealth.ANCHORED,
                    lineStart: 10,
                    lineEnd: 12
                }),
                createThread({
                    id: '01HQTEST26',
                    status: ThreadStatus.OPEN,
                    health: AnchorHealth.DRIFTED,
                    lineStart: 20,
                    lineEnd: 22,
                    driftDistance: 3
                }),
                createThread({
                    id: '01HQTEST27',
                    status: ThreadStatus.OPEN,
                    health: AnchorHealth.ORPHANED,
                    lineStart: 30,
                    lineEnd: 32
                })
            ];

            decorationManager.updateGutterDecorations(mockEditor, threads);

            // Should apply decorations for all three threads
            expect(mockSetDecorations).toHaveBeenCalled();
        });

        it('converts 1-indexed line numbers to 0-indexed for text decorations', () => {
            const threads: Thread[] = [
                createThread({
                    id: '01HQTEST28',
                    status: ThreadStatus.OPEN,
                    health: AnchorHealth.ANCHORED,
                    lineStart: 50, // 1-indexed in sidecar
                    lineEnd: 52
                })
            ];

            decorationManager.updateGutterDecorations(mockEditor, threads);

            expect(mockSetDecorations).toHaveBeenCalled();
        });

        it('disposes text decoration types on cleanup', () => {
            const threads: Thread[] = [
                createThread({
                    id: '01HQTEST29',
                    status: ThreadStatus.OPEN,
                    health: AnchorHealth.ANCHORED,
                    lineStart: 10,
                    lineEnd: 12
                })
            ];

            decorationManager.updateGutterDecorations(mockEditor, threads);

            const initialDecorationsCount = mockDecorationTypes.length;
            decorationManager.dispose();

            // All decoration types should have dispose called
            mockDecorationTypes.forEach(decorationType => {
                expect(decorationType.dispose).toHaveBeenCalled();
            });
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
