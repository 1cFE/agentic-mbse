/**
 * Unit tests for sidecar file reader.
 */

import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';
import { readSidecar, ThreadStatus, AuthorType, AnchorHealth } from './sidecar';

describe('readSidecar', () => {
    let tempDir: string;
    let projectRoot: string;

    beforeEach(() => {
        // Create temporary directory for test files
        tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'sidecar-test-'));
        projectRoot = tempDir;

        // Create .comments directory
        fs.mkdirSync(path.join(projectRoot, '.comments'));
    });

    afterEach(() => {
        // Clean up temporary directory
        fs.rmSync(tempDir, { recursive: true, force: true });
    });

    test('returns null when sidecar does not exist', () => {
        const sourcePath = path.join(projectRoot, 'example.py');
        const result = readSidecar(sourcePath, projectRoot);
        expect(result).toBeNull();
    });

    test('reads valid sidecar file successfully', () => {
        const sourcePath = path.join(projectRoot, 'example.py');
        const sidecarPath = path.join(projectRoot, '.comments', 'example.py.json');

        const validSidecar = {
            source_file: 'example.py',
            source_hash: 'sha256:' + 'a'.repeat(64),
            schema_version: '1.0',
            threads: [
                {
                    id: '01HN2Z3V4W5X6Y7Z8A9B0C1D2E',
                    status: 'open',
                    created_at: '2026-02-01T10:00:00Z',
                    resolved_at: null,
                    comments: [
                        {
                            id: '01HN2Z3V4W5X6Y7Z8A9B0C1D2F',
                            author: 'alice',
                            author_type: 'human',
                            body: 'This needs refactoring',
                            timestamp: '2026-02-01T10:00:00Z'
                        }
                    ],
                    anchor: {
                        content_hash: 'sha256:' + 'b'.repeat(64),
                        context_hash_before: 'sha256:' + 'c'.repeat(64),
                        context_hash_after: 'sha256:' + 'd'.repeat(64),
                        line_start: 10,
                        line_end: 15,
                        content_snippet: 'def example():',
                        health: 'anchored',
                        drift_distance: 0
                    },
                    decision: null
                }
            ]
        };

        fs.writeFileSync(sidecarPath, JSON.stringify(validSidecar, null, 2));

        const result = readSidecar(sourcePath, projectRoot);
        expect(result).not.toBeNull();
        expect(result!.source_file).toBe('example.py');
        expect(result!.source_hash).toBe('sha256:' + 'a'.repeat(64));
        expect(result!.schema_version).toBe('1.0');
        expect(result!.threads).toHaveLength(1);
        expect(result!.threads[0].id).toBe('01HN2Z3V4W5X6Y7Z8A9B0C1D2E');
        expect(result!.threads[0].status).toBe(ThreadStatus.OPEN);
        expect(result!.threads[0].comments).toHaveLength(1);
        expect(result!.threads[0].comments[0].author).toBe('alice');
        expect(result!.threads[0].comments[0].author_type).toBe(AuthorType.HUMAN);
        expect(result!.threads[0].anchor.health).toBe(AnchorHealth.ANCHORED);
    });

    test('reads sidecar with resolved thread and decision', () => {
        const sourcePath = path.join(projectRoot, 'example.py');
        const sidecarPath = path.join(projectRoot, '.comments', 'example.py.json');

        const validSidecar = {
            source_file: 'example.py',
            source_hash: 'sha256:' + 'a'.repeat(64),
            schema_version: '1.0',
            threads: [
                {
                    id: '01HN2Z3V4W5X6Y7Z8A9B0C1D2E',
                    status: 'resolved',
                    created_at: '2026-02-01T10:00:00Z',
                    resolved_at: '2026-02-01T11:00:00Z',
                    comments: [],
                    anchor: {
                        content_hash: 'sha256:' + 'b'.repeat(64),
                        context_hash_before: 'sha256:' + 'c'.repeat(64),
                        context_hash_after: 'sha256:' + 'd'.repeat(64),
                        line_start: 10,
                        line_end: 10,
                        content_snippet: 'x = 1',
                        health: 'drifted',
                        drift_distance: 5
                    },
                    decision: {
                        summary: 'Fixed in PR #123',
                        decider: 'bob',
                        timestamp: '2026-02-01T11:00:00Z'
                    }
                }
            ]
        };

        fs.writeFileSync(sidecarPath, JSON.stringify(validSidecar, null, 2));

        const result = readSidecar(sourcePath, projectRoot);
        expect(result!.threads[0].status).toBe(ThreadStatus.RESOLVED);
        expect(result!.threads[0].resolved_at).toBe('2026-02-01T11:00:00Z');
        expect(result!.threads[0].decision).not.toBeNull();
        expect(result!.threads[0].decision!.summary).toBe('Fixed in PR #123');
        expect(result!.threads[0].decision!.decider).toBe('bob');
        expect(result!.threads[0].anchor.health).toBe(AnchorHealth.DRIFTED);
        expect(result!.threads[0].anchor.drift_distance).toBe(5);
    });

    test('handles nested directory structure', () => {
        const sourcePath = path.join(projectRoot, 'src', 'utils', 'helper.ts');
        const sidecarPath = path.join(projectRoot, '.comments', 'src/utils/helper.ts.json');

        // Create nested directory structure
        fs.mkdirSync(path.join(projectRoot, '.comments', 'src', 'utils'), { recursive: true });

        const validSidecar = {
            source_file: 'src/utils/helper.ts',
            source_hash: 'sha256:' + 'a'.repeat(64),
            schema_version: '1.0',
            threads: []
        };

        fs.writeFileSync(sidecarPath, JSON.stringify(validSidecar, null, 2));

        const result = readSidecar(sourcePath, projectRoot);
        expect(result).not.toBeNull();
        expect(result!.source_file).toBe('src/utils/helper.ts');
    });

    test('throws error on invalid JSON', () => {
        const sourcePath = path.join(projectRoot, 'example.py');
        const sidecarPath = path.join(projectRoot, '.comments', 'example.py.json');

        fs.writeFileSync(sidecarPath, 'not valid json {{{');

        expect(() => {
            readSidecar(sourcePath, projectRoot);
        }).toThrow();
    });

    test('throws error when source_file is missing', () => {
        const sourcePath = path.join(projectRoot, 'example.py');
        const sidecarPath = path.join(projectRoot, '.comments', 'example.py.json');

        const invalidSidecar = {
            source_hash: 'sha256:' + 'a'.repeat(64),
            schema_version: '1.0',
            threads: []
        };

        fs.writeFileSync(sidecarPath, JSON.stringify(invalidSidecar));

        expect(() => {
            readSidecar(sourcePath, projectRoot);
        }).toThrow('Missing or invalid field: source_file');
    });

    test('throws error when source_hash has invalid format', () => {
        const sourcePath = path.join(projectRoot, 'example.py');
        const sidecarPath = path.join(projectRoot, '.comments', 'example.py.json');

        const invalidSidecar = {
            source_file: 'example.py',
            source_hash: 'invalid-hash',
            schema_version: '1.0',
            threads: []
        };

        fs.writeFileSync(sidecarPath, JSON.stringify(invalidSidecar));

        expect(() => {
            readSidecar(sourcePath, projectRoot);
        }).toThrow('Missing or invalid field: source_hash');
    });

    test('throws error when threads is not an array', () => {
        const sourcePath = path.join(projectRoot, 'example.py');
        const sidecarPath = path.join(projectRoot, '.comments', 'example.py.json');

        const invalidSidecar = {
            source_file: 'example.py',
            source_hash: 'sha256:' + 'a'.repeat(64),
            schema_version: '1.0',
            threads: 'not an array'
        };

        fs.writeFileSync(sidecarPath, JSON.stringify(invalidSidecar));

        expect(() => {
            readSidecar(sourcePath, projectRoot);
        }).toThrow('Missing or invalid field: threads');
    });

    test('throws error when thread id is not a valid ULID', () => {
        const sourcePath = path.join(projectRoot, 'example.py');
        const sidecarPath = path.join(projectRoot, '.comments', 'example.py.json');

        const invalidSidecar = {
            source_file: 'example.py',
            source_hash: 'sha256:' + 'a'.repeat(64),
            schema_version: '1.0',
            threads: [
                {
                    id: 'short',
                    status: 'open',
                    created_at: '2026-02-01T10:00:00Z',
                    resolved_at: null,
                    comments: [],
                    anchor: {
                        content_hash: 'sha256:' + 'b'.repeat(64),
                        context_hash_before: 'sha256:' + 'c'.repeat(64),
                        context_hash_after: 'sha256:' + 'd'.repeat(64),
                        line_start: 1,
                        line_end: 1,
                        content_snippet: 'x',
                        health: 'anchored',
                        drift_distance: 0
                    },
                    decision: null
                }
            ]
        };

        fs.writeFileSync(sidecarPath, JSON.stringify(invalidSidecar));

        expect(() => {
            readSidecar(sourcePath, projectRoot);
        }).toThrow(/threads\[0\]\.id.*ULID/);
    });

    test('throws error when anchor line_end < line_start', () => {
        const sourcePath = path.join(projectRoot, 'example.py');
        const sidecarPath = path.join(projectRoot, '.comments', 'example.py.json');

        const invalidSidecar = {
            source_file: 'example.py',
            source_hash: 'sha256:' + 'a'.repeat(64),
            schema_version: '1.0',
            threads: [
                {
                    id: '01HN2Z3V4W5X6Y7Z8A9B0C1D2E',
                    status: 'open',
                    created_at: '2026-02-01T10:00:00Z',
                    resolved_at: null,
                    comments: [],
                    anchor: {
                        content_hash: 'sha256:' + 'b'.repeat(64),
                        context_hash_before: 'sha256:' + 'c'.repeat(64),
                        context_hash_after: 'sha256:' + 'd'.repeat(64),
                        line_start: 10,
                        line_end: 5,
                        content_snippet: 'x',
                        health: 'anchored',
                        drift_distance: 0
                    },
                    decision: null
                }
            ]
        };

        fs.writeFileSync(sidecarPath, JSON.stringify(invalidSidecar));

        expect(() => {
            readSidecar(sourcePath, projectRoot);
        }).toThrow(/line_end.*line_start/);
    });

    test('throws error when comment body exceeds 10000 characters', () => {
        const sourcePath = path.join(projectRoot, 'example.py');
        const sidecarPath = path.join(projectRoot, '.comments', 'example.py.json');

        const invalidSidecar = {
            source_file: 'example.py',
            source_hash: 'sha256:' + 'a'.repeat(64),
            schema_version: '1.0',
            threads: [
                {
                    id: '01HN2Z3V4W5X6Y7Z8A9B0C1D2E',
                    status: 'open',
                    created_at: '2026-02-01T10:00:00Z',
                    resolved_at: null,
                    comments: [
                        {
                            id: '01HN2Z3V4W5X6Y7Z8A9B0C1D2F',
                            author: 'alice',
                            author_type: 'human',
                            body: 'x'.repeat(10001),
                            timestamp: '2026-02-01T10:00:00Z'
                        }
                    ],
                    anchor: {
                        content_hash: 'sha256:' + 'b'.repeat(64),
                        context_hash_before: 'sha256:' + 'c'.repeat(64),
                        context_hash_after: 'sha256:' + 'd'.repeat(64),
                        line_start: 1,
                        line_end: 1,
                        content_snippet: 'x',
                        health: 'anchored',
                        drift_distance: 0
                    },
                    decision: null
                }
            ]
        };

        fs.writeFileSync(sidecarPath, JSON.stringify(invalidSidecar));

        expect(() => {
            readSidecar(sourcePath, projectRoot);
        }).toThrow(/comments\[0\]\.body.*10,000 characters/);
    });

    test('reads multiple threads with different statuses', () => {
        const sourcePath = path.join(projectRoot, 'example.py');
        const sidecarPath = path.join(projectRoot, '.comments', 'example.py.json');

        const validSidecar = {
            source_file: 'example.py',
            source_hash: 'sha256:' + 'a'.repeat(64),
            schema_version: '1.0',
            threads: [
                {
                    id: '01HN2Z3V4W5X6Y7Z8A9B0C1D2E',
                    status: 'open',
                    created_at: '2026-02-01T10:00:00Z',
                    resolved_at: null,
                    comments: [],
                    anchor: {
                        content_hash: 'sha256:' + 'b'.repeat(64),
                        context_hash_before: 'sha256:' + 'c'.repeat(64),
                        context_hash_after: 'sha256:' + 'd'.repeat(64),
                        line_start: 1,
                        line_end: 1,
                        content_snippet: 'x',
                        health: 'anchored',
                        drift_distance: 0
                    },
                    decision: null
                },
                {
                    id: '01HN2Z3V4W5X6Y7Z8A9B0C1D2F',
                    status: 'wontfix',
                    created_at: '2026-02-01T10:00:00Z',
                    resolved_at: '2026-02-01T11:00:00Z',
                    comments: [],
                    anchor: {
                        content_hash: 'sha256:' + 'e'.repeat(64),
                        context_hash_before: 'sha256:' + 'f'.repeat(64),
                        context_hash_after: 'sha256:' + 'a'.repeat(64),
                        line_start: 10,
                        line_end: 10,
                        content_snippet: 'y',
                        health: 'orphaned',
                        drift_distance: 100
                    },
                    decision: {
                        summary: 'Out of scope',
                        decider: 'alice',
                        timestamp: '2026-02-01T11:00:00Z'
                    }
                }
            ]
        };

        fs.writeFileSync(sidecarPath, JSON.stringify(validSidecar, null, 2));

        const result = readSidecar(sourcePath, projectRoot);
        expect(result!.threads).toHaveLength(2);
        expect(result!.threads[0].status).toBe(ThreadStatus.OPEN);
        expect(result!.threads[1].status).toBe(ThreadStatus.WONTFIX);
        expect(result!.threads[1].anchor.health).toBe(AnchorHealth.ORPHANED);
    });
});
