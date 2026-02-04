/**
 * Tests for Reply Comment functionality
 */

import * as vscode from 'vscode';
import { handleReply, registerReplyCommand } from './replyComment';
import * as child_process from 'child_process';
import { handleConflictCheck, ConflictResolution } from '../conflictHandler';
import { threadMetadataMap } from '../utils';

// Mock child_process
jest.mock('child_process');
const mockExecFile = child_process.execFile as unknown as jest.Mock;

// Mock VSCode API
jest.mock('vscode');

// Mock conflictHandler
jest.mock('../conflictHandler');
const mockHandleConflictCheck = handleConflictCheck as jest.MockedFunction<typeof handleConflictCheck>;

describe('handleReply', () => {
    const projectRoot = '/test/project';
    let mockThread: vscode.CommentThread;
    let mockReply: vscode.CommentReply;

    beforeEach(() => {
        jest.clearAllMocks();

        mockHandleConflictCheck.mockResolvedValue(ConflictResolution.OVERWRITE);

        (vscode.env as any) = { username: 'testuser' };

        // Create mock thread and set WeakMap metadata
        mockThread = {
            contextValue: 'open',
            uri: vscode.Uri.file('/test/project/src/file.ts'),
            range: new vscode.Range(0, 0, 5, 0),
            comments: [],
            canReply: true,
            state: vscode.CommentThreadState.Unresolved,
            collapsibleState: vscode.CommentThreadCollapsibleState.Expanded,
            dispose: jest.fn()
        } as any;

        threadMetadataMap.set(mockThread, {
            threadId: '01HXYZ123456789ABCDEF',
            sourceHash: 'sha256:abc123',
            health: 'anchored',
            driftDistance: 0,
            status: 'open',
            hasDecision: false
        });

        mockReply = {
            thread: mockThread,
            text: 'This is a reply'
        };

        (vscode.window.showInformationMessage as jest.Mock) = jest.fn();
        (vscode.window.showErrorMessage as jest.Mock) = jest.fn();

        // Mock execFile to succeed by default
        mockExecFile.mockImplementation(
            (cmd: string, args: string[], opts: any, cb: Function) => {
                cb(null, { stdout: '', stderr: '' });
            }
        );
    });

    describe('Basic reply functionality', () => {
        it('should successfully reply to a thread', async () => {
            await handleReply(mockReply, projectRoot);

            // Should call execFile with correct args
            expect(mockExecFile).toHaveBeenCalledWith(
                'comment',
                ['reply', '01HXYZ123456789ABCDEF', 'This is a reply', '--author=testuser'],
                expect.objectContaining({
                    cwd: projectRoot,
                    encoding: 'utf-8'
                }),
                expect.any(Function)
            );

            expect(vscode.window.showInformationMessage).toHaveBeenCalledWith(
                'Reply added to thread 01HXYZ123456789ABCDEF'
            );

            expect(mockThread.comments.length).toBe(1);
            expect((mockThread.comments[0].body as vscode.MarkdownString).value).toBe('This is a reply');
            expect(mockThread.comments[0].author.name).toBe('testuser');
            expect(mockThread.comments[0].mode).toBe(vscode.CommentMode.Preview);
        });

        it('should use fallback author when username unavailable', async () => {
            (vscode.env as any) = {};

            await handleReply(mockReply, projectRoot);

            expect(mockExecFile).toHaveBeenCalledWith(
                'comment',
                expect.arrayContaining(['--author=vscode-user']),
                expect.any(Object),
                expect.any(Function)
            );
        });

        it('should add comment with timestamp', async () => {
            const beforeTime = new Date();
            await handleReply(mockReply, projectRoot);
            const afterTime = new Date();

            expect(mockThread.comments[0].timestamp).toBeDefined();
            expect(mockThread.comments[0].timestamp!.getTime()).toBeGreaterThanOrEqual(beforeTime.getTime());
            expect(mockThread.comments[0].timestamp!.getTime()).toBeLessThanOrEqual(afterTime.getTime());
        });
    });

    describe('Thread ID extraction', () => {
        it('should fail when no thread metadata exists', async () => {
            // Remove from WeakMap and clear contextValue
            const bareThread = {
                contextValue: undefined,
                uri: vscode.Uri.file('/test/project/src/file.ts'),
                range: new vscode.Range(0, 0, 5, 0),
                comments: [],
                canReply: true,
                state: vscode.CommentThreadState.Unresolved,
                collapsibleState: vscode.CommentThreadCollapsibleState.Expanded,
                dispose: jest.fn()
            } as any;

            mockReply.thread = bareThread;

            await handleReply(mockReply, projectRoot);

            expect(vscode.window.showErrorMessage).toHaveBeenCalledWith(
                'Failed to identify thread for reply'
            );
            expect(mockExecFile).not.toHaveBeenCalled();
        });
    });

    describe('Input validation', () => {
        it('should reject empty reply text', async () => {
            mockReply.text = '';

            await handleReply(mockReply, projectRoot);

            expect(vscode.window.showErrorMessage).toHaveBeenCalledWith(
                'Reply text cannot be empty'
            );
            expect(mockExecFile).not.toHaveBeenCalled();
        });

        it('should reject whitespace-only reply text', async () => {
            mockReply.text = '   \n  \t  ';

            await handleReply(mockReply, projectRoot);

            expect(vscode.window.showErrorMessage).toHaveBeenCalledWith(
                'Reply text cannot be empty'
            );
        });
    });

    describe('Text handling', () => {
        it('should pass text with special characters directly (no escaping needed)', async () => {
            mockReply.text = 'Reply with "quotes" and C:\\path';

            await handleReply(mockReply, projectRoot);

            // execFile passes args as array, no shell escaping needed
            expect(mockExecFile).toHaveBeenCalledWith(
                'comment',
                ['reply', '01HXYZ123456789ABCDEF', 'Reply with "quotes" and C:\\path', '--author=testuser'],
                expect.any(Object),
                expect.any(Function)
            );
        });

        it('should handle multiline reply text', async () => {
            mockReply.text = 'Line 1\nLine 2\nLine 3';

            await handleReply(mockReply, projectRoot);

            expect(mockExecFile).toHaveBeenCalledWith(
                'comment',
                ['reply', '01HXYZ123456789ABCDEF', 'Line 1\nLine 2\nLine 3', '--author=testuser'],
                expect.any(Object),
                expect.any(Function)
            );
        });
    });

    describe('Error handling', () => {
        it('should show error notification when CLI command fails', async () => {
            const cliError = new Error('CLI execution failed');
            (cliError as any).stderr = 'Error: Thread not found';
            mockExecFile.mockImplementation(
                (cmd: string, args: string[], opts: any, cb: Function) => {
                    cb(cliError);
                }
            );

            await handleReply(mockReply, projectRoot);

            expect(vscode.window.showErrorMessage).toHaveBeenCalledWith(
                'Failed to add reply: Error: Thread not found'
            );
            expect(mockThread.comments.length).toBe(0);
        });

        it('should handle CLI error without stderr', async () => {
            const cliError = new Error('Unknown CLI error');
            mockExecFile.mockImplementation(
                (cmd: string, args: string[], opts: any, cb: Function) => {
                    cb(cliError);
                }
            );

            await handleReply(mockReply, projectRoot);

            expect(vscode.window.showErrorMessage).toHaveBeenCalledWith(
                'Failed to add reply: Unknown CLI error'
            );
        });
    });

    describe('Temporary comment creation', () => {
        it('should preserve existing comments when adding reply', async () => {
            const existingComment: vscode.Comment = {
                body: new vscode.MarkdownString('Existing comment'),
                mode: vscode.CommentMode.Preview,
                author: { name: 'otheruser' }
            };

            mockThread.comments = [existingComment];

            await handleReply(mockReply, projectRoot);

            expect(mockThread.comments.length).toBe(2);
            expect((mockThread.comments[0].body as vscode.MarkdownString).value).toBe(
                'Existing comment'
            );
            expect((mockThread.comments[1].body as vscode.MarkdownString).value).toBe(
                'This is a reply'
            );
        });
    });
});

describe('registerReplyCommand', () => {
    let mockContext: vscode.ExtensionContext;
    const projectRoot = '/test/project';

    beforeEach(() => {
        jest.clearAllMocks();

        mockContext = {
            subscriptions: []
        } as any;

        (vscode.commands.registerCommand as jest.Mock) = jest.fn((id, handler) => ({
            dispose: jest.fn()
        }));
    });

    it('should register reply command', () => {
        registerReplyCommand(mockContext, projectRoot);

        expect(vscode.commands.registerCommand).toHaveBeenCalledWith(
            'file-native-comments.replyNote',
            expect.any(Function)
        );

        expect(mockContext.subscriptions.length).toBe(1);
    });

    it('should register command with correct ID', () => {
        registerReplyCommand(mockContext, projectRoot);

        const registerCall = (vscode.commands.registerCommand as jest.Mock).mock.calls[0];
        expect(registerCall[0]).toBe('file-native-comments.replyNote');
    });
});
