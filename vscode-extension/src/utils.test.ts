/**
 * Tests for shared utilities.
 */

import * as vscode from 'vscode';
import { extractThreadId, extractSourceHash, getAuthor, runCliCommand, threadMetadataMap } from './utils';
import * as child_process from 'child_process';
import { promisify } from 'util';

jest.mock('vscode');
jest.mock('child_process');

const mockExecFile = child_process.execFile as unknown as jest.Mock;

describe('extractThreadId', () => {
    it('reads from WeakMap when metadata is present', () => {
        const thread = { contextValue: 'open' } as any as vscode.CommentThread;
        threadMetadataMap.set(thread, {
            threadId: '01HXYZ123456789ABCDEF',
            sourceHash: 'sha256:abc',
            health: 'anchored',
            driftDistance: 0,
            status: 'open',
            hasDecision: false
        });

        expect(extractThreadId(thread)).toBe('01HXYZ123456789ABCDEF');
    });

    it('falls back to JSON contextValue when no WeakMap entry', () => {
        const thread = {
            contextValue: JSON.stringify({ thread_id: '01HFALLBACK' })
        } as any as vscode.CommentThread;

        expect(extractThreadId(thread)).toBe('01HFALLBACK');
    });

    it('returns null when contextValue is undefined and no WeakMap entry', () => {
        const thread = { contextValue: undefined } as any as vscode.CommentThread;
        expect(extractThreadId(thread)).toBeNull();
    });

    it('returns null when contextValue is invalid JSON and no WeakMap entry', () => {
        const thread = { contextValue: 'open' } as any as vscode.CommentThread;
        expect(extractThreadId(thread)).toBeNull();
    });
});

describe('extractSourceHash', () => {
    it('reads from WeakMap when metadata is present', () => {
        const thread = { contextValue: 'open' } as any as vscode.CommentThread;
        threadMetadataMap.set(thread, {
            threadId: '01HXYZ',
            sourceHash: 'sha256:deadbeef',
            health: 'anchored',
            driftDistance: 0,
            status: 'open',
            hasDecision: false
        });

        expect(extractSourceHash(thread)).toBe('sha256:deadbeef');
    });

    it('falls back to JSON contextValue when no WeakMap entry', () => {
        const thread = {
            contextValue: JSON.stringify({ source_hash: 'sha256:fallback' })
        } as any as vscode.CommentThread;

        expect(extractSourceHash(thread)).toBe('sha256:fallback');
    });

    it('returns null when no metadata available', () => {
        const thread = { contextValue: undefined } as any as vscode.CommentThread;
        expect(extractSourceHash(thread)).toBeNull();
    });
});

describe('getAuthor', () => {
    it('returns vscode.env.username when available', () => {
        (vscode.env as any) = { username: 'alice' };
        expect(getAuthor()).toBe('alice');
    });

    it('returns fallback when username is undefined', () => {
        (vscode.env as any) = {};
        expect(getAuthor()).toBe('vscode-user');
    });
});

describe('runCliCommand', () => {
    beforeEach(() => {
        jest.clearAllMocks();
    });

    it('calls execFile with correct args and returns stdout', async () => {
        mockExecFile.mockImplementation(
            (cmd: string, args: string[], opts: any, cb: Function) => {
                cb(null, { stdout: 'success output', stderr: '' });
            }
        );

        const result = await runCliCommand(['comment', 'reply', '01HXYZ', 'hello'], '/project');

        expect(mockExecFile).toHaveBeenCalledWith(
            'comment',
            ['reply', '01HXYZ', 'hello'],
            expect.objectContaining({
                cwd: '/project',
                encoding: 'utf-8'
            }),
            expect.any(Function)
        );
        expect(result).toBe('success output');
    });

    it('rejects on CLI error', async () => {
        const error = new Error('Command failed');
        (error as any).stderr = 'Thread not found';
        mockExecFile.mockImplementation(
            (cmd: string, args: string[], opts: any, cb: Function) => {
                cb(error);
            }
        );

        await expect(runCliCommand(['comment', 'reply', '01HXYZ', 'hello'], '/project'))
            .rejects.toThrow('Command failed');
    });

    it('passes custom maxBuffer option', async () => {
        mockExecFile.mockImplementation(
            (cmd: string, args: string[], opts: any, cb: Function) => {
                cb(null, { stdout: '', stderr: '' });
            }
        );

        await runCliCommand(['comment', 'list'], '/project', { maxBuffer: 1024 });

        expect(mockExecFile).toHaveBeenCalledWith(
            'comment',
            ['list'],
            expect.objectContaining({ maxBuffer: 1024 }),
            expect.any(Function)
        );
    });
});
