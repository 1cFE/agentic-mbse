/**
 * Tests for resolveThread.ts - Thread resolution functionality
 */

import * as vscode from 'vscode';
import * as child_process from 'child_process';
import { resolveThread, registerResolveCommand } from './resolveThread';
import { handleConflictCheck, ConflictResolution } from '../conflictHandler';
import { extractThreadId } from '../utils';
import { threadMetadataMap } from '../utils';

// Mock child_process
jest.mock('child_process');
const mockExecFile = child_process.execFile as unknown as jest.Mock;

// Mock vscode module
jest.mock('vscode');

// Mock conflictHandler
jest.mock('../conflictHandler');
const mockHandleConflictCheck = handleConflictCheck as jest.MockedFunction<typeof handleConflictCheck>;

describe('resolveThread', () => {
    let mockThread: vscode.CommentThread;
    const projectRoot = '/test/project';

    beforeEach(() => {
        jest.clearAllMocks();

        mockHandleConflictCheck.mockResolvedValue(ConflictResolution.OVERWRITE);

        mockThread = {
            contextValue: 'open',
            state: vscode.CommentThreadState.Unresolved,
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
            status: 'open',
            hasDecision: false
        });

        (vscode.window.showInputBox as jest.Mock).mockResolvedValue('Fixed by refactoring');
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

        it('should return null if no metadata exists', () => {
            const bareThread = { contextValue: undefined } as any;
            const threadId = extractThreadId(bareThread);
            expect(threadId).toBeNull();
        });
    });

    describe('resolveThread', () => {
        it('should successfully resolve thread with decision', async () => {
            (vscode.window.showInputBox as jest.Mock).mockResolvedValue('Fixed the bug');

            await resolveThread(mockThread, projectRoot);

            expect(mockExecFile).toHaveBeenCalledWith(
                'comment',
                ['resolve', '01HXYZ123456', '--decision', 'Fixed the bug'],
                expect.objectContaining({
                    cwd: projectRoot,
                    encoding: 'utf-8'
                }),
                expect.any(Function)
            );

            expect(vscode.window.showInformationMessage).toHaveBeenCalledWith(
                'Thread 01HXYZ123456 resolved'
            );

            expect(mockThread.state).toBe(vscode.CommentThreadState.Resolved);
        });

        it('should abort if user cancels input box', async () => {
            (vscode.window.showInputBox as jest.Mock).mockResolvedValue(undefined);

            await resolveThread(mockThread, projectRoot);

            expect(mockExecFile).not.toHaveBeenCalled();
            expect(vscode.window.showInformationMessage).not.toHaveBeenCalled();
        });

        it('should show error if thread_id cannot be extracted', async () => {
            const bareThread = { contextValue: undefined, uri: vscode.Uri.file('/test/file.py') } as any;

            await resolveThread(bareThread, projectRoot);

            expect(vscode.window.showErrorMessage).toHaveBeenCalledWith(
                'Failed to identify thread for resolution'
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

            (vscode.window.showInputBox as jest.Mock).mockResolvedValue('Fixed');

            await resolveThread(mockThread, projectRoot);

            expect(vscode.window.showErrorMessage).toHaveBeenCalledWith(
                'Failed to resolve thread: Thread not found'
            );
        });

        it('should validate input box to reject empty or whitespace-only decision', async () => {
            let validationFunction: ((value: string) => string | null) | undefined;

            (vscode.window.showInputBox as jest.Mock).mockImplementation((options) => {
                validationFunction = options.validateInput;
                return Promise.resolve('Valid decision');
            });

            await resolveThread(mockThread, projectRoot);

            expect(validationFunction).toBeDefined();
            expect(validationFunction!('')).toBe('Decision is required. Describe why this was resolved.');
            expect(validationFunction!('   ')).toBe('Decision is required. Describe why this was resolved.');
            expect(validationFunction!('Valid text')).toBeNull();
        });

        it('should log command execution', async () => {
            const consoleSpy = jest.spyOn(console, 'log').mockImplementation();

            (vscode.window.showInputBox as jest.Mock).mockResolvedValue('Fixed');

            await resolveThread(mockThread, projectRoot);

            expect(consoleSpy).toHaveBeenCalledWith(
                'Executing: comment resolve 01HXYZ123456'
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

            (vscode.window.showInputBox as jest.Mock).mockResolvedValue('Fixed');

            await resolveThread(mockThread, projectRoot);

            expect(consoleSpy).toHaveBeenCalledWith('Resolve command failed:', cliError);

            consoleSpy.mockRestore();
        });
    });

    describe('registerResolveCommand', () => {
        it('should register command with correct ID', () => {
            const mockContext = {
                subscriptions: []
            } as any as vscode.ExtensionContext;

            const mockDisposable = { dispose: jest.fn() };
            (vscode.commands.registerCommand as jest.Mock).mockReturnValue(mockDisposable);

            registerResolveCommand(mockContext, projectRoot);

            expect(vscode.commands.registerCommand).toHaveBeenCalledWith(
                'file-native-comments.resolveThread',
                expect.any(Function)
            );

            expect(mockContext.subscriptions).toContain(mockDisposable);
        });

        it('should log registration', () => {
            const consoleSpy = jest.spyOn(console, 'log').mockImplementation();
            const mockContext = {
                subscriptions: []
            } as any as vscode.ExtensionContext;

            registerResolveCommand(mockContext, projectRoot);

            expect(consoleSpy).toHaveBeenCalledWith(
                'Resolve command registered: file-native-comments.resolveThread'
            );

            consoleSpy.mockRestore();
        });
    });
});
