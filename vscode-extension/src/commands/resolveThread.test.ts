/**
 * Tests for resolveThread.ts - Thread resolution functionality
 */

import * as vscode from 'vscode';
import { execSync } from 'child_process';
import { resolveThread, buildResolveCliCommand, extractThreadId, registerResolveCommand } from './resolveThread';

// Mock child_process
jest.mock('child_process');
const mockExecSync = execSync as jest.MockedFunction<typeof execSync>;

// Mock vscode module
jest.mock('vscode');

describe('resolveThread', () => {
    let mockThread: vscode.CommentThread;
    const projectRoot = '/test/project';

    beforeEach(() => {
        // Reset mocks
        jest.clearAllMocks();

        // Create mock thread with contextValue
        mockThread = {
            contextValue: JSON.stringify({
                thread_id: '01HXYZ123456',
                health: 'anchored',
                status: 'open',
                has_decision: false
            }),
            state: vscode.CommentThreadState.Unresolved,
            comments: [],
            range: new vscode.Range(0, 0, 0, 0),
            uri: vscode.Uri.file('/test/project/file.py'),
            canReply: true,
            collapsibleState: vscode.CommentThreadCollapsibleState.Expanded,
            label: 'Thread',
            dispose: jest.fn()
        };

        // Mock vscode.window.showInputBox to return a decision by default
        (vscode.window.showInputBox as jest.Mock).mockResolvedValue('Fixed by refactoring');

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

    describe('buildResolveCliCommand', () => {
        it('should build command with decision text', () => {
            const cmd = buildResolveCliCommand('01HXYZ123456', 'Fixed by refactoring');
            expect(cmd).toBe('comment resolve 01HXYZ123456 --decision "Fixed by refactoring"');
        });

        it('should escape double quotes in decision', () => {
            const cmd = buildResolveCliCommand('01HXYZ123456', 'Fixed "issue" here');
            expect(cmd).toBe('comment resolve 01HXYZ123456 --decision "Fixed \\"issue\\" here"');
        });

        it('should escape backslashes in decision', () => {
            const cmd = buildResolveCliCommand('01HXYZ123456', 'Path: C:\\Users\\test');
            expect(cmd).toBe('comment resolve 01HXYZ123456 --decision "Path: C:\\\\Users\\\\test"');
        });

        it('should escape newlines in decision', () => {
            const cmd = buildResolveCliCommand('01HXYZ123456', 'Line 1\nLine 2');
            expect(cmd).toBe('comment resolve 01HXYZ123456 --decision "Line 1\\nLine 2"');
        });

        it('should escape tabs in decision', () => {
            const cmd = buildResolveCliCommand('01HXYZ123456', 'Col1\tCol2');
            expect(cmd).toBe('comment resolve 01HXYZ123456 --decision "Col1\\tCol2"');
        });

        it('should escape carriage returns in decision', () => {
            const cmd = buildResolveCliCommand('01HXYZ123456', 'Line 1\r\nLine 2');
            expect(cmd).toBe('comment resolve 01HXYZ123456 --decision "Line 1\\r\\nLine 2"');
        });


        it('should handle complex escaping (backslashes before quotes)', () => {
            const cmd = buildResolveCliCommand('01HXYZ123456', 'Path: "C:\\Users\\"');
            expect(cmd).toBe('comment resolve 01HXYZ123456 --decision "Path: \\"C:\\\\Users\\\\\\""');
        });
    });

    describe('resolveThread', () => {
        it('should successfully resolve thread with decision', async () => {
            (vscode.window.showInputBox as jest.Mock).mockResolvedValue('Fixed the bug');

            await resolveThread(mockThread, projectRoot);

            // Should call CLI with correct command
            expect(mockExecSync).toHaveBeenCalledWith(
                'comment resolve 01HXYZ123456 --decision "Fixed the bug"',
                expect.objectContaining({
                    cwd: projectRoot,
                    encoding: 'utf-8',
                    stdio: 'pipe'
                })
            );

            // Should show success notification
            expect(vscode.window.showInformationMessage).toHaveBeenCalledWith(
                'Thread 01HXYZ123456 resolved'
            );

            // Should update thread state
            expect(mockThread.state).toBe(vscode.CommentThreadState.Resolved);
        });


        it('should abort if user cancels input box', async () => {
            (vscode.window.showInputBox as jest.Mock).mockResolvedValue(undefined);

            await resolveThread(mockThread, projectRoot);

            // Should NOT call CLI
            expect(mockExecSync).not.toHaveBeenCalled();

            // Should NOT show notification
            expect(vscode.window.showInformationMessage).not.toHaveBeenCalled();
        });

        it('should show error if thread_id cannot be extracted', async () => {
            mockThread.contextValue = undefined;

            await resolveThread(mockThread, projectRoot);

            expect(vscode.window.showErrorMessage).toHaveBeenCalledWith(
                'Failed to identify thread for resolution'
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

            (vscode.window.showInputBox as jest.Mock).mockResolvedValue('Fixed');

            await resolveThread(mockThread, projectRoot);

            expect(vscode.window.showErrorMessage).toHaveBeenCalledWith(
                'Failed to resolve thread: Thread not found'
            );
        });

        it('should show error with generic message if no stderr', async () => {
            const cliError = new Error('Unknown error');
            mockExecSync.mockImplementation(() => {
                throw cliError;
            });

            (vscode.window.showInputBox as jest.Mock).mockResolvedValue('Fixed');

            await resolveThread(mockThread, projectRoot);

            expect(vscode.window.showErrorMessage).toHaveBeenCalledWith(
                'Failed to resolve thread: Unknown error'
            );
        });

        it('should validate input box to reject empty or whitespace-only decision', async () => {
            let validationFunction: ((value: string) => string | null) | undefined;

            (vscode.window.showInputBox as jest.Mock).mockImplementation((options) => {
                validationFunction = options.validateInput;
                return Promise.resolve('Valid decision');
            });

            await resolveThread(mockThread, projectRoot);

            // Test the validation function
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
                'Executing: comment resolve 01HXYZ123456 --decision "Fixed"'
            );

            consoleSpy.mockRestore();
        });

        it('should log errors', async () => {
            const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
            const cliError = new Error('Test error');
            mockExecSync.mockImplementation(() => {
                throw cliError;
            });

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
