/**
 * Tests for reopenThread.ts - Thread reopening functionality
 */

import * as vscode from 'vscode';
import { execSync } from 'child_process';
import { reopenThread, extractThreadId, registerReopenCommand } from './reopenThread';
import { handleConflictCheck, ConflictResolution } from '../conflictHandler';

// Mock child_process
jest.mock('child_process');
const mockExecSync = execSync as jest.MockedFunction<typeof execSync>;

// Mock vscode module
jest.mock('vscode');

// Mock conflictHandler
jest.mock('../conflictHandler');
const mockHandleConflictCheck = handleConflictCheck as jest.MockedFunction<typeof handleConflictCheck>;

describe('reopenThread', () => {
    let mockThread: vscode.CommentThread;
    const projectRoot = '/test/project';

    beforeEach(() => {
        // Reset mocks
        jest.clearAllMocks();

        // Default: no conflict detected (proceed with write)
        mockHandleConflictCheck.mockResolvedValue(ConflictResolution.OVERWRITE);

        // Create mock thread with contextValue
        mockThread = {
            contextValue: JSON.stringify({
                thread_id: '01HXYZ123456',
                health: 'anchored',
                status: 'resolved',
                has_decision: true,
                source_hash: 'sha256:abc123'
            }),
            state: vscode.CommentThreadState.Resolved,
            comments: [],
            range: new vscode.Range(0, 0, 0, 0),
            uri: vscode.Uri.file('/test/project/file.py'),
            canReply: true,
            collapsibleState: vscode.CommentThreadCollapsibleState.Expanded,
            label: 'Thread',
            dispose: jest.fn()
        };

        // Mock vscode.window.showInformationMessage
        (vscode.window.showInformationMessage as jest.Mock).mockResolvedValue(undefined);

        // Mock vscode.window.showErrorMessage
        (vscode.window.showErrorMessage as jest.Mock).mockResolvedValue(undefined);

        // Mock execSync to succeed by default
        mockExecSync.mockReturnValue(Buffer.from(''));
    });

    describe('extractThreadId', () => {
        it('should extract thread_id from contextValue', () => {
            const threadId = extractThreadId(mockThread);
            expect(threadId).toBe('01HXYZ123456');
        });

        it('should return null if contextValue is missing', () => {
            mockThread.contextValue = undefined;
            const threadId = extractThreadId(mockThread);
            expect(threadId).toBeNull();
        });

        it('should return null if contextValue is invalid JSON', () => {
            mockThread.contextValue = 'not-json';
            const threadId = extractThreadId(mockThread);
            expect(threadId).toBeNull();
        });

        it('should return null if thread_id field is missing', () => {
            mockThread.contextValue = JSON.stringify({ health: 'anchored' });
            const threadId = extractThreadId(mockThread);
            expect(threadId).toBeNull();
        });
    });

    describe('reopenThread', () => {
        it('should successfully reopen thread', async () => {
            await reopenThread(mockThread, projectRoot);

            // Should call CLI with correct command
            expect(mockExecSync).toHaveBeenCalledWith(
                'comment reopen 01HXYZ123456',
                expect.objectContaining({
                    cwd: projectRoot,
                    encoding: 'utf-8',
                    stdio: 'pipe'
                })
            );

            // Should show success notification
            expect(vscode.window.showInformationMessage).toHaveBeenCalledWith(
                'Thread 01HXYZ123456 reopened'
            );

            // Should update thread state
            expect(mockThread.state).toBe(vscode.CommentThreadState.Unresolved);
        });

        it('should show error if thread_id cannot be extracted', async () => {
            mockThread.contextValue = undefined;

            await reopenThread(mockThread, projectRoot);

            expect(vscode.window.showErrorMessage).toHaveBeenCalledWith(
                'Failed to identify thread for reopening'
            );

            // Should NOT call CLI
            expect(mockExecSync).not.toHaveBeenCalled();
        });

        it('should show error if CLI command fails', async () => {
            const cliError = new Error('CLI error') as any;
            cliError.stderr = Buffer.from('Thread not found');
            mockExecSync.mockImplementation(() => {
                throw cliError;
            });

            await reopenThread(mockThread, projectRoot);

            expect(vscode.window.showErrorMessage).toHaveBeenCalledWith(
                'Failed to reopen thread: Thread not found'
            );
        });

        it('should show error with generic message if no stderr', async () => {
            const cliError = new Error('Unknown error');
            mockExecSync.mockImplementation(() => {
                throw cliError;
            });

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
            mockExecSync.mockImplementation(() => {
                throw cliError;
            });

            await reopenThread(mockThread, projectRoot);

            expect(consoleSpy).toHaveBeenCalledWith('Reopen command failed:', cliError);

            consoleSpy.mockRestore();
        });

        it('should handle thread with missing contextValue fields gracefully', async () => {
            // Thread with minimal contextValue (only thread_id)
            mockThread.contextValue = JSON.stringify({ thread_id: '01ABC' });

            await reopenThread(mockThread, projectRoot);

            expect(mockExecSync).toHaveBeenCalledWith(
                'comment reopen 01ABC',
                expect.anything()
            );

            expect(vscode.window.showInformationMessage).toHaveBeenCalled();
        });

        it('should execute CLI in correct working directory', async () => {
            const customRoot = '/custom/project/path';

            await reopenThread(mockThread, customRoot);

            expect(mockExecSync).toHaveBeenCalledWith(
                expect.any(String),
                expect.objectContaining({
                    cwd: customRoot
                })
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

        it('should pass projectRoot to command handler', async () => {
            const mockContext = {
                subscriptions: []
            } as any as vscode.ExtensionContext;

            let registeredHandler: Function | undefined;

            (vscode.commands.registerCommand as jest.Mock).mockImplementation(
                (commandId, handler) => {
                    registeredHandler = handler;
                    return { dispose: jest.fn() };
                }
            );

            const customRoot = '/my/custom/root';
            registerReopenCommand(mockContext, customRoot);

            // Verify handler was registered
            expect(registeredHandler).toBeDefined();

            // Call the handler with a mock thread (and await since it's async)
            await registeredHandler!(mockThread);

            // Verify execSync was called with correct cwd
            expect(mockExecSync).toHaveBeenCalledWith(
                expect.any(String),
                expect.objectContaining({
                    cwd: customRoot
                })
            );
        });
    });
});
