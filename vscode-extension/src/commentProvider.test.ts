/**
 * Unit tests for CommentProvider.
 */

import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';
import * as vscode from 'vscode';
import { CommentProvider } from './commentProvider';
import { ThreadStatus, AuthorType, AnchorHealth } from './sidecar';

// Mock vscode module for testing
jest.mock('vscode');

describe('CommentProvider', () => {
    let tempDir: string;
    let projectRoot: string;
    let commentController: vscode.CommentController;
    let provider: CommentProvider;

    beforeEach(() => {
        // Create temporary directory for test files
        tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'comment-provider-test-'));
        projectRoot = tempDir;

        // Create .comments directory
        fs.mkdirSync(path.join(projectRoot, '.comments'));

        // Create mock comment controller
        commentController = vscode.comments.createCommentController(
            'test-controller',
            'Test Controller'
        );

        // Create provider
        provider = new CommentProvider(projectRoot, commentController);
    });

    afterEach(() => {
        // Clean up temporary directory
        fs.rmSync(tempDir, { recursive: true, force: true });
    });

    describe('loadCommentsForDocument', () => {
        test('does nothing when sidecar does not exist', () => {
            // Create a mock document
            const sourcePath = path.join(projectRoot, 'example.py');
            const mockDocument = createMockDocument(sourcePath, 'print("hello")\n');

            // Call provider (should not throw)
            expect(() => {
                provider.loadCommentsForDocument(mockDocument);
            }).not.toThrow();
        });

        test('creates VSCode CommentThread for single thread', () => {
            // Create source file and sidecar
            const sourcePath = path.join(projectRoot, 'example.py');
            const sourceContent = 'def foo():\n    pass\n';
            fs.writeFileSync(sourcePath, sourceContent);

            const sidecarPath = path.join(projectRoot, '.comments', 'example.py.json');
            const sidecarData = {
                source_file: 'example.py',
                source_hash: 'sha256:' + 'a'.repeat(64),
                schema_version: '1.0',
                threads: [
                    {
                        id: '01HN2Z3V4W5X6Y7Z8A9B0C1D2E',
                        status: ThreadStatus.OPEN,
                        created_at: '2026-02-01T10:00:00Z',
                        resolved_at: null,
                        comments: [
                            {
                                id: '01HN2Z3V4W5X6Y7Z8A9B0C1D2F',
                                author: 'alice',
                                author_type: AuthorType.HUMAN,
                                body: 'This function needs documentation',
                                timestamp: '2026-02-01T10:00:00Z'
                            }
                        ],
                        anchor: {
                            content_hash: 'sha256:' + 'b'.repeat(64),
                            context_hash_before: 'sha256:' + 'c'.repeat(64),
                            context_hash_after: 'sha256:' + 'd'.repeat(64),
                            line_start: 1,
                            line_end: 2,
                            content_snippet: 'def foo():\n    pass',
                            health: AnchorHealth.ANCHORED,
                            drift_distance: 0
                        },
                        decision: null
                    }
                ]
            };
            fs.writeFileSync(sidecarPath, JSON.stringify(sidecarData, null, 2));

            // Create mock document
            const mockDocument = createMockDocument(sourcePath, sourceContent);

            // Call provider
            provider.loadCommentsForDocument(mockDocument);

            // Verify thread was created by checking internal state
            const threads = (provider as any).commentThreads.get(mockDocument.uri.toString());
            expect(threads).toHaveLength(1);
            const thread = threads[0];

            // Check thread properties
            expect(thread.state).toBe(vscode.CommentThreadState.Unresolved);
            expect(thread.canReply).toBe(true);
            expect(thread.label).toBe('This function needs documentation');
            expect(thread.comments).toHaveLength(1);

            // Check range (1-indexed → 0-indexed conversion)
            expect(thread.range.start.line).toBe(0); // line_start: 1 → 0
            expect(thread.range.end.line).toBe(1);   // line_end: 2 → 1

            // Check context value contains metadata
            const contextValue = JSON.parse(thread.contextValue!);
            expect(contextValue.health).toBe(AnchorHealth.ANCHORED);
            expect(contextValue.drift_distance).toBe(0);
            expect(contextValue.status).toBe(ThreadStatus.OPEN);
            expect(contextValue.thread_id).toBe('01HN2Z3V4W5X6Y7Z8A9B0C1D2E');
            expect(contextValue.has_decision).toBe(false);
        });

        test('maps resolved status to resolved state', () => {
            // Create sidecar with resolved thread
            const sourcePath = path.join(projectRoot, 'example.py');
            fs.writeFileSync(sourcePath, 'print("hello")\n');

            const sidecarPath = path.join(projectRoot, '.comments', 'example.py.json');
            const sidecarData = {
                source_file: 'example.py',
                source_hash: 'sha256:' + 'a'.repeat(64),
                schema_version: '1.0',
                threads: [
                    {
                        id: '01HN2Z3V4W5X6Y7Z8A9B0C1D2E',
                        status: ThreadStatus.RESOLVED,
                        created_at: '2026-02-01T10:00:00Z',
                        resolved_at: '2026-02-01T11:00:00Z',
                        comments: [
                            {
                                id: '01HN2Z3V4W5X6Y7Z8A9B0C1D2F',
                                author: 'alice',
                                author_type: AuthorType.HUMAN,
                                body: 'Fixed',
                                timestamp: '2026-02-01T10:00:00Z'
                            }
                        ],
                        anchor: {
                            content_hash: 'sha256:' + 'b'.repeat(64),
                            context_hash_before: 'sha256:' + 'c'.repeat(64),
                            context_hash_after: 'sha256:' + 'd'.repeat(64),
                            line_start: 1,
                            line_end: 1,
                            content_snippet: 'print("hello")',
                            health: AnchorHealth.ANCHORED,
                            drift_distance: 0
                        },
                        decision: null
                    }
                ]
            };
            fs.writeFileSync(sidecarPath, JSON.stringify(sidecarData, null, 2));

            const mockDocument = createMockDocument(sourcePath, 'print("hello")\n');
            provider.loadCommentsForDocument(mockDocument);

            const threads = (provider as any).commentThreads.get(mockDocument.uri.toString());
            expect(threads[0].state).toBe(vscode.CommentThreadState.Resolved);
        });

        test('handles multiple threads', () => {
            // Create sidecar with multiple threads
            const sourcePath = path.join(projectRoot, 'example.py');
            fs.writeFileSync(sourcePath, 'def foo():\n    pass\n\ndef bar():\n    pass\n');

            const sidecarPath = path.join(projectRoot, '.comments', 'example.py.json');
            const sidecarData = {
                source_file: 'example.py',
                source_hash: 'sha256:' + 'a'.repeat(64),
                schema_version: '1.0',
                threads: [
                    {
                        id: '01HN2Z3V4W5X6Y7Z8A9B0C1D2E',
                        status: ThreadStatus.OPEN,
                        created_at: '2026-02-01T10:00:00Z',
                        resolved_at: null,
                        comments: [
                            {
                                id: '01HN2Z3V4W5X6Y7Z8A9B0C1D2F',
                                author: 'alice',
                                author_type: AuthorType.HUMAN,
                                body: 'Comment on foo',
                                timestamp: '2026-02-01T10:00:00Z'
                            }
                        ],
                        anchor: {
                            content_hash: 'sha256:' + 'b'.repeat(64),
                            context_hash_before: 'sha256:' + 'c'.repeat(64),
                            context_hash_after: 'sha256:' + 'd'.repeat(64),
                            line_start: 1,
                            line_end: 2,
                            content_snippet: 'def foo():',
                            health: AnchorHealth.ANCHORED,
                            drift_distance: 0
                        },
                        decision: null
                    },
                    {
                        id: '01HN2Z3V4W5X6Y7Z8A9B0C1D2G',
                        status: ThreadStatus.OPEN,
                        created_at: '2026-02-01T10:05:00Z',
                        resolved_at: null,
                        comments: [
                            {
                                id: '01HN2Z3V4W5X6Y7Z8A9B0C1D2H',
                                author: 'bob',
                                author_type: AuthorType.AGENT,
                                body: 'Comment on bar',
                                timestamp: '2026-02-01T10:05:00Z'
                            }
                        ],
                        anchor: {
                            content_hash: 'sha256:' + 'e'.repeat(64),
                            context_hash_before: 'sha256:' + 'f'.repeat(64),
                            context_hash_after: 'sha256:' + 'a'.repeat(64),
                            line_start: 4,
                            line_end: 5,
                            content_snippet: 'def bar():',
                            health: AnchorHealth.DRIFTED,
                            drift_distance: 2
                        },
                        decision: null
                    }
                ]
            };
            fs.writeFileSync(sidecarPath, JSON.stringify(sidecarData, null, 2));

            const mockDocument = createMockDocument(sourcePath, 'def foo():\n    pass\n\ndef bar():\n    pass\n');
            provider.loadCommentsForDocument(mockDocument);

            const threads = (provider as any).commentThreads.get(mockDocument.uri.toString());
            expect(threads).toHaveLength(2);

            // Check that thread IDs are preserved in context
            const context1 = JSON.parse(threads[0].contextValue!);
            const context2 = JSON.parse(threads[1].contextValue!);
            expect(context1.thread_id).toBe('01HN2Z3V4W5X6Y7Z8A9B0C1D2E');
            expect(context2.thread_id).toBe('01HN2Z3V4W5X6Y7Z8A9B0C1D2G');

            // Check that health metadata is preserved
            expect(context1.health).toBe(AnchorHealth.ANCHORED);
            expect(context2.health).toBe(AnchorHealth.DRIFTED);
            expect(context2.drift_distance).toBe(2);
        });

        test('handles line numbers beyond document bounds', () => {
            // Create sidecar with line numbers exceeding document length
            const sourcePath = path.join(projectRoot, 'example.py');
            fs.writeFileSync(sourcePath, 'line1\n');

            const sidecarPath = path.join(projectRoot, '.comments', 'example.py.json');
            const sidecarData = {
                source_file: 'example.py',
                source_hash: 'sha256:' + 'a'.repeat(64),
                schema_version: '1.0',
                threads: [
                    {
                        id: '01HN2Z3V4W5X6Y7Z8A9B0C1D2E',
                        status: ThreadStatus.OPEN,
                        created_at: '2026-02-01T10:00:00Z',
                        resolved_at: null,
                        comments: [
                            {
                                id: '01HN2Z3V4W5X6Y7Z8A9B0C1D2F',
                                author: 'alice',
                                author_type: AuthorType.HUMAN,
                                body: 'Comment beyond bounds',
                                timestamp: '2026-02-01T10:00:00Z'
                            }
                        ],
                        anchor: {
                            content_hash: 'sha256:' + 'b'.repeat(64),
                            context_hash_before: 'sha256:' + 'c'.repeat(64),
                            context_hash_after: 'sha256:' + 'd'.repeat(64),
                            line_start: 100,
                            line_end: 105,
                            content_snippet: 'nonexistent',
                            health: AnchorHealth.ORPHANED,
                            drift_distance: 99
                        },
                        decision: null
                    }
                ]
            };
            fs.writeFileSync(sidecarPath, JSON.stringify(sidecarData, null, 2));

            const mockDocument = createMockDocument(sourcePath, 'line1\n');
            provider.loadCommentsForDocument(mockDocument);

            const threads = (provider as any).commentThreads.get(mockDocument.uri.toString());
            // Should clamp to document bounds
            // Document has 2 lines: ["line1", ""] so lineCount = 2, max line index = 1
            expect(threads).toHaveLength(1);
            expect(threads[0].range.start.line).toBe(1); // Clamped from 99 to 1
            expect(threads[0].range.end.line).toBe(1);   // Clamped from 104 to 1
        });
    });

    describe('markdown rendering', () => {
        test('renders comment body as MarkdownString', () => {
            // Create sidecar with markdown content
            const sourcePath = path.join(projectRoot, 'example.py');
            fs.writeFileSync(sourcePath, 'print("hello")\n');

            const sidecarPath = path.join(projectRoot, '.comments', 'example.py.json');
            const sidecarData = {
                source_file: 'example.py',
                source_hash: 'sha256:' + 'a'.repeat(64),
                schema_version: '1.0',
                threads: [
                    {
                        id: '01HN2Z3V4W5X6Y7Z8A9B0C1D2E',
                        status: ThreadStatus.OPEN,
                        created_at: '2026-02-01T10:00:00Z',
                        resolved_at: null,
                        comments: [
                            {
                                id: '01HN2Z3V4W5X6Y7Z8A9B0C1D2F',
                                author: 'alice',
                                author_type: AuthorType.HUMAN,
                                body: 'This is **bold** and *italic* text',
                                timestamp: '2026-02-01T10:00:00Z'
                            }
                        ],
                        anchor: {
                            content_hash: 'sha256:' + 'b'.repeat(64),
                            context_hash_before: 'sha256:' + 'c'.repeat(64),
                            context_hash_after: 'sha256:' + 'd'.repeat(64),
                            line_start: 1,
                            line_end: 1,
                            content_snippet: 'print("hello")',
                            health: AnchorHealth.ANCHORED,
                            drift_distance: 0
                        },
                        decision: null
                    }
                ]
            };
            fs.writeFileSync(sidecarPath, JSON.stringify(sidecarData, null, 2));

            const mockDocument = createMockDocument(sourcePath, 'print("hello")\n');
            provider.loadCommentsForDocument(mockDocument);

            const threads = (provider as any).commentThreads.get(mockDocument.uri.toString());
            const comment = threads[0].comments[0];

            // Verify comment body is a MarkdownString
            expect(comment.body).toBeInstanceOf(vscode.MarkdownString);
            expect(comment.body.value).toBe('This is **bold** and *italic* text');
            expect(comment.body.isTrusted).toBe(true);
        });

        test('handles inline code in markdown', () => {
            const sourcePath = path.join(projectRoot, 'example.py');
            fs.writeFileSync(sourcePath, 'x = 42\n');

            const sidecarPath = path.join(projectRoot, '.comments', 'example.py.json');
            const sidecarData = {
                source_file: 'example.py',
                source_hash: 'sha256:' + 'a'.repeat(64),
                schema_version: '1.0',
                threads: [
                    {
                        id: '01HN2Z3V4W5X6Y7Z8A9B0C1D2E',
                        status: ThreadStatus.OPEN,
                        created_at: '2026-02-01T10:00:00Z',
                        resolved_at: null,
                        comments: [
                            {
                                id: '01HN2Z3V4W5X6Y7Z8A9B0C1D2F',
                                author: 'bob',
                                author_type: AuthorType.HUMAN,
                                body: 'Use `const` instead of `var`',
                                timestamp: '2026-02-01T10:00:00Z'
                            }
                        ],
                        anchor: {
                            content_hash: 'sha256:' + 'b'.repeat(64),
                            context_hash_before: 'sha256:' + 'c'.repeat(64),
                            context_hash_after: 'sha256:' + 'd'.repeat(64),
                            line_start: 1,
                            line_end: 1,
                            content_snippet: 'x = 42',
                            health: AnchorHealth.ANCHORED,
                            drift_distance: 0
                        },
                        decision: null
                    }
                ]
            };
            fs.writeFileSync(sidecarPath, JSON.stringify(sidecarData, null, 2));

            const mockDocument = createMockDocument(sourcePath, 'x = 42\n');
            provider.loadCommentsForDocument(mockDocument);

            const threads = (provider as any).commentThreads.get(mockDocument.uri.toString());
            const comment = threads[0].comments[0];

            expect(comment.body).toBeInstanceOf(vscode.MarkdownString);
            expect(comment.body.value).toBe('Use `const` instead of `var`');
            expect(comment.body.isTrusted).toBe(true);
        });

        test('handles code blocks in markdown', () => {
            const sourcePath = path.join(projectRoot, 'example.py');
            fs.writeFileSync(sourcePath, 'def func(): pass\n');

            const markdownWithCodeBlock = 'Try this instead:\n\n```python\ndef func():\n    return None\n```';

            const sidecarPath = path.join(projectRoot, '.comments', 'example.py.json');
            const sidecarData = {
                source_file: 'example.py',
                source_hash: 'sha256:' + 'a'.repeat(64),
                schema_version: '1.0',
                threads: [
                    {
                        id: '01HN2Z3V4W5X6Y7Z8A9B0C1D2E',
                        status: ThreadStatus.OPEN,
                        created_at: '2026-02-01T10:00:00Z',
                        resolved_at: null,
                        comments: [
                            {
                                id: '01HN2Z3V4W5X6Y7Z8A9B0C1D2F',
                                author: 'charlie',
                                author_type: AuthorType.AGENT,
                                body: markdownWithCodeBlock,
                                timestamp: '2026-02-01T10:00:00Z'
                            }
                        ],
                        anchor: {
                            content_hash: 'sha256:' + 'b'.repeat(64),
                            context_hash_before: 'sha256:' + 'c'.repeat(64),
                            context_hash_after: 'sha256:' + 'd'.repeat(64),
                            line_start: 1,
                            line_end: 1,
                            content_snippet: 'def func(): pass',
                            health: AnchorHealth.ANCHORED,
                            drift_distance: 0
                        },
                        decision: null
                    }
                ]
            };
            fs.writeFileSync(sidecarPath, JSON.stringify(sidecarData, null, 2));

            const mockDocument = createMockDocument(sourcePath, 'def func(): pass\n');
            provider.loadCommentsForDocument(mockDocument);

            const threads = (provider as any).commentThreads.get(mockDocument.uri.toString());
            const comment = threads[0].comments[0];

            expect(comment.body).toBeInstanceOf(vscode.MarkdownString);
            expect(comment.body.value).toBe(markdownWithCodeBlock);
            expect(comment.body.isTrusted).toBe(true);
        });

        test('handles links in markdown', () => {
            const sourcePath = path.join(projectRoot, 'example.py');
            fs.writeFileSync(sourcePath, '# TODO\n');

            const markdownWithLinks = 'See [documentation](https://example.com/docs) for details';

            const sidecarPath = path.join(projectRoot, '.comments', 'example.py.json');
            const sidecarData = {
                source_file: 'example.py',
                source_hash: 'sha256:' + 'a'.repeat(64),
                schema_version: '1.0',
                threads: [
                    {
                        id: '01HN2Z3V4W5X6Y7Z8A9B0C1D2E',
                        status: ThreadStatus.OPEN,
                        created_at: '2026-02-01T10:00:00Z',
                        resolved_at: null,
                        comments: [
                            {
                                id: '01HN2Z3V4W5X6Y7Z8A9B0C1D2F',
                                author: 'dave',
                                author_type: AuthorType.HUMAN,
                                body: markdownWithLinks,
                                timestamp: '2026-02-01T10:00:00Z'
                            }
                        ],
                        anchor: {
                            content_hash: 'sha256:' + 'b'.repeat(64),
                            context_hash_before: 'sha256:' + 'c'.repeat(64),
                            context_hash_after: 'sha256:' + 'd'.repeat(64),
                            line_start: 1,
                            line_end: 1,
                            content_snippet: '# TODO',
                            health: AnchorHealth.ANCHORED,
                            drift_distance: 0
                        },
                        decision: null
                    }
                ]
            };
            fs.writeFileSync(sidecarPath, JSON.stringify(sidecarData, null, 2));

            const mockDocument = createMockDocument(sourcePath, '# TODO\n');
            provider.loadCommentsForDocument(mockDocument);

            const threads = (provider as any).commentThreads.get(mockDocument.uri.toString());
            const comment = threads[0].comments[0];

            expect(comment.body).toBeInstanceOf(vscode.MarkdownString);
            expect(comment.body.value).toBe(markdownWithLinks);
            expect(comment.body.isTrusted).toBe(true);
        });

        test('handles multiline markdown with mixed formatting', () => {
            const sourcePath = path.join(projectRoot, 'example.py');
            fs.writeFileSync(sourcePath, 'class Example: pass\n');

            const complexMarkdown = '# Issues Found\n\n' +
                '1. **Critical**: Use `None` instead of null\n' +
                '2. *Minor*: Add type hints\n\n' +
                'See [PEP 484](https://peps.python.org/pep-0484/) for more info.';

            const sidecarPath = path.join(projectRoot, '.comments', 'example.py.json');
            const sidecarData = {
                source_file: 'example.py',
                source_hash: 'sha256:' + 'a'.repeat(64),
                schema_version: '1.0',
                threads: [
                    {
                        id: '01HN2Z3V4W5X6Y7Z8A9B0C1D2E',
                        status: ThreadStatus.OPEN,
                        created_at: '2026-02-01T10:00:00Z',
                        resolved_at: null,
                        comments: [
                            {
                                id: '01HN2Z3V4W5X6Y7Z8A9B0C1D2F',
                                author: 'reviewer',
                                author_type: AuthorType.AGENT,
                                body: complexMarkdown,
                                timestamp: '2026-02-01T10:00:00Z'
                            }
                        ],
                        anchor: {
                            content_hash: 'sha256:' + 'b'.repeat(64),
                            context_hash_before: 'sha256:' + 'c'.repeat(64),
                            context_hash_after: 'sha256:' + 'd'.repeat(64),
                            line_start: 1,
                            line_end: 1,
                            content_snippet: 'class Example: pass',
                            health: AnchorHealth.ANCHORED,
                            drift_distance: 0
                        },
                        decision: null
                    }
                ]
            };
            fs.writeFileSync(sidecarPath, JSON.stringify(sidecarData, null, 2));

            const mockDocument = createMockDocument(sourcePath, 'class Example: pass\n');
            provider.loadCommentsForDocument(mockDocument);

            const threads = (provider as any).commentThreads.get(mockDocument.uri.toString());
            const comment = threads[0].comments[0];

            expect(comment.body).toBeInstanceOf(vscode.MarkdownString);
            expect(comment.body.value).toBe(complexMarkdown);
            expect(comment.body.isTrusted).toBe(true);
        });

        test('isTrusted enables command URIs and HTML', () => {
            // This test verifies that isTrusted is set correctly
            // When isTrusted is true, VSCode allows:
            // - command: URIs
            // - Embedded HTML
            // - Script execution in markdown
            const sourcePath = path.join(projectRoot, 'example.py');
            fs.writeFileSync(sourcePath, 'x = 1\n');

            const sidecarPath = path.join(projectRoot, '.comments', 'example.py.json');
            const sidecarData = {
                source_file: 'example.py',
                source_hash: 'sha256:' + 'a'.repeat(64),
                schema_version: '1.0',
                threads: [
                    {
                        id: '01HN2Z3V4W5X6Y7Z8A9B0C1D2E',
                        status: ThreadStatus.OPEN,
                        created_at: '2026-02-01T10:00:00Z',
                        resolved_at: null,
                        comments: [
                            {
                                id: '01HN2Z3V4W5X6Y7Z8A9B0C1D2F',
                                author: 'system',
                                author_type: AuthorType.AGENT,
                                body: 'Plain text comment',
                                timestamp: '2026-02-01T10:00:00Z'
                            }
                        ],
                        anchor: {
                            content_hash: 'sha256:' + 'b'.repeat(64),
                            context_hash_before: 'sha256:' + 'c'.repeat(64),
                            context_hash_after: 'sha256:' + 'd'.repeat(64),
                            line_start: 1,
                            line_end: 1,
                            content_snippet: 'x = 1',
                            health: AnchorHealth.ANCHORED,
                            drift_distance: 0
                        },
                        decision: null
                    }
                ]
            };
            fs.writeFileSync(sidecarPath, JSON.stringify(sidecarData, null, 2));

            const mockDocument = createMockDocument(sourcePath, 'x = 1\n');
            provider.loadCommentsForDocument(mockDocument);

            const threads = (provider as any).commentThreads.get(mockDocument.uri.toString());
            const comment = threads[0].comments[0];

            // Verify that isTrusted is set to true, enabling all markdown features
            expect(comment.body.isTrusted).toBe(true);
        });
    });

    describe('findProjectRoot', () => {
        test('finds .git directory in current directory', () => {
            // Create .git directory
            fs.mkdirSync(path.join(projectRoot, '.git'));

            const result = CommentProvider.findProjectRoot(projectRoot);
            expect(result).toBe(projectRoot);
        });

        test('finds .git directory in parent directory', () => {
            // Create nested structure
            const subdir = path.join(projectRoot, 'src', 'module');
            fs.mkdirSync(subdir, { recursive: true });
            fs.mkdirSync(path.join(projectRoot, '.git'));

            const result = CommentProvider.findProjectRoot(subdir);
            expect(result).toBe(projectRoot);
        });

        test('returns null when no .git directory found', () => {
            const result = CommentProvider.findProjectRoot(projectRoot);
            expect(result).toBeNull();
        });
    });
});

/**
 * Creates a mock VSCode TextDocument for testing.
 */
function createMockDocument(filePath: string, content: string): vscode.TextDocument {
    const lines = content.split('\n');
    return {
        uri: vscode.Uri.file(filePath),
        fileName: filePath,
        isUntitled: false,
        languageId: 'python',
        version: 1,
        isDirty: false,
        isClosed: false,
        eol: 1,
        lineCount: lines.length,
        lineAt: (line: number) => ({
            lineNumber: line,
            text: lines[line] || '',
            range: new vscode.Range(line, 0, line, (lines[line] || '').length),
            rangeIncludingLineBreak: new vscode.Range(line, 0, line + 1, 0),
            firstNonWhitespaceCharacterIndex: 0,
            isEmptyOrWhitespace: (lines[line] || '').trim().length === 0
        }),
        getText: () => content,
        getWordRangeAtPosition: () => undefined,
        offsetAt: () => 0,
        positionAt: () => ({ line: 0, character: 0 }),
        validatePosition: (pos: any) => pos,
        validateRange: (range: any) => range,
        save: () => Promise.resolve(true)
    } as any;
}
