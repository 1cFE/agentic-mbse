/**
 * Tests for reopenThread.ts - Thread reopening functionality
 */

import * as vscode from 'vscode';
import * as child_process from 'child_process';
import { reopenThread, registerReopenCommand } from './reopenThread';
import { handleConflictCheck, ConflictResolution } from '../conflictHandler';
import { extractThreadId, threadMetadataMap } from '../utils';

// Mock child_process
jest.mock('child_process');
const mockExecFile = child_process.execFile as unknown as jest.Mock;

// Mock vscode module
jest.mock('vscode');

// Mock conflictHandler
jest.mock('../conflictHandler');
const mockHandleConflictCheck = handleConflictCheck as jest.MockedFunction<typeof handleConflictCheck>;

describe('reopenThread', () => {
    let mockThread: vscode.CommentThread;
    const projectRoot = '/test/project';

    beforeEach(() => {
        jest.clearAllMocks();

        mockHandleConflictCheck.mockResolvedValue(ConflictResolution.OVERWRITE);

        mockThread = {
            contextValue: 'resolved',
            state: vscode.CommentThreadState.Resolved,
            comments: [],
            range: new vscode.Range(0, 0, 0, 0),
            uri: vscode.Uri.file('/test/project/file.py'),
            canReply: true,
            collapsibleState: vscode.CommentThreadCollapsibleState.Expanded,
            label: 'Thread',
            dispose: jest.fn()
        };

        threadMetadataMap.set(mockThread, {
            threadId: '01HXYZ123456',
            sourceHash: 'sha256:abc123',
            health: 'anchored',
            driftDistance: 0,
            status: 'resolved',
            hasDecision: true
        });

        (vscode.window.showInformationMessage as jest.Mock).mockResolvedValue(undefined);
        (vscode.window.showErrorMessage as jest.Mock).mockResolvedValue(undefined);

        mockExecFile.mockImplementation(
            (cmd: string, args: string[], opts: any, cb: Function) => {
                cb(null, { stdout: '', stderr: '' });
            }
        );
    });

    describe('extractThreadId', () => {
        it('should extract thread_id from WeakMap', () => {
            const threadId = extractThreadId(mockThread);
            expect(threadId).toBe('01HXYZ123456');
        });

        it('should return null if no metadata', () => {
            const bareThread = { contextValue: undefined } as any;
            const threadId = extractThreadId(bareThread);
            expect(threadId).toBeNull();
        });
    });

    describe('reopenThread', () => {
        it('should successfully reopen thread', async () => {
            await reopenThread(mockThread, projectRoot);

            expect(mockExecFile).toHaveBeenCalledWith(
                'comment',
                ['reopen', '01HXYZ123456'],
                expect.objectContaining({
                    cwd: projectRoot,
                    encoding: 'utf-8'
                }),
                expect.any(Function)
            );

            expect(vscode.window.showInformationMessage).toHaveBeenCalledWith(
                'Thread 01HXYZ123456 reopened'
            );

            expect(mockThread.state).toBe(vscode.CommentThreadState.Unresolved);
        });

        it('should show error if thread_id cannot be extracted', async () => {
            const bareThread = { contextValue: undefined, uri: vscode.Uri.file('/test/file.py') } as any;

            await reopenThread(bareThread, projectRoot);

            expect(vscode.window.showErrorMessage).toHaveBeenCalledWith(
                'Failed to identify thread for reopening'
            );
            expect(mockExecFile).not.toHaveBeenCalled();
        });

        it('should show error if CLI command fails', async () => {
            const cliError = new Error('CLI error') as any;
            cliError.stderr = 'Thread not found';
            mockExecFile.mockImplementation(
                (cmd: string, args: string[], opts: any, cb: Function) => {
                    cb(cliError);
                }
            );

            await reopenThread(mockThread, projectRoot);

            expect(vscode.window.showErrorMessage).toHaveBeenCalledWith(
                'Failed to reopen thread: Thread not found'
            );
        });

        it('should show error with generic message if no stderr', async () => {
            const cliError = new Error('Unknown error');
            mockExecFile.mockImplementation(
                (cmd: string, args: string[], opts: any, cb: Function) => {
                    cb(cliError);
                }
            );

            await reopenThread(mockThread, projectRoot);

            expect(vscode.window.showErrorMessage).toHaveBeenCalledWith(
                'Failed to reopen thread: Unknown error'
            );
        });

        it('should log command execution', async () => {
            const consoleSpy = jest.spyOn(console, 'log').mockImplementation();

            await reopenThread(mockThread, projectRoot);

            expect(consoleSpy).toHaveBeenCalledWith(
                'Executing: comment reopen 01HXYZ123456'
            );

            consoleSpy.mockRestore();
        });

        it('should log errors', async () => {
            const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
            const cliError = new Error('Test error');
            mockExecFile.mockImplementation(
                (cmd: string, args: string[], opts: any, cb: Function) => {
                    cb(cliError);
                }
            );

            await reopenThread(mockThread, projectRoot);

            expect(consoleSpy).toHaveBeenCalledWith('Reopen command failed:', cliError);

            consoleSpy.mockRestore();
        });

        it('should handle thread with minimal metadata gracefully', async () => {
            const minimalThread = {
                contextValue: 'resolved',
                uri: vscode.Uri.file('/test/project/file.py'),
                state: vscode.CommentThreadState.Resolved,
                comments: [],
                range: new vscode.Range(0, 0, 0, 0),
                canReply: true,
                collapsibleState: vscode.CommentThreadCollapsibleState.Expanded,
                dispose: jest.fn()
            } as any;

            threadMetadataMap.set(minimalThread, {
                threadId: '01ABC',
                sourceHash: '',
                health: 'anchored',
                driftDistance: 0,
                status: 'resolved',
                hasDecision: false
            });

            await reopenThread(minimalThread, projectRoot);

            expect(mockExecFile).toHaveBeenCalledWith(
                'comment',
                ['reopen', '01ABC'],
                expect.anything(),
                expect.any(Function)
            );

            expect(vscode.window.showInformationMessage).toHaveBeenCalled();
        });

        it('should execute CLI in correct working directory', async () => {
            const customRoot = '/custom/project/path';

            await reopenThread(mockThread, customRoot);

            expect(mockExecFile).toHaveBeenCalledWith(
                expect.any(String),
                expect.any(Array),
                expect.objectContaining({
                    cwd: customRoot
                }),
                expect.any(Function)
            );
        });
    });

    describe('registerReopenCommand', () => {
        it('should register command with correct ID', () => {
            const mockContext = {
                subscriptions: []
            } as any as vscode.ExtensionContext;

            const mockDisposable = { dispose: jest.fn() };
            (vscode.commands.registerCommand as jest.Mock).mockReturnValue(mockDisposable);

            registerReopenCommand(mockContext, projectRoot);

            expect(vscode.commands.registerCommand).toHaveBeenCalledWith(
                'file-native-comments.reopenThread',
                expect.any(Function)
            );

            expect(mockContext.subscriptions).toContain(mockDisposable);
        });

        it('should log registration', () => {
            const consoleSpy = jest.spyOn(console, 'log').mockImplementation();
            const mockContext = {
                subscriptions: []
            } as any as vscode.ExtensionContext;

            registerReopenCommand(mockContext, projectRoot);

            expect(consoleSpy).toHaveBeenCalledWith(
                'Reopen command registered: file-native-comments.reopenThread'
            );

            consoleSpy.mockRestore();
        });
    });
});
