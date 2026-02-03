/**
 * Tests for Reply Comment functionality
 */

import * as vscode from 'vscode';
import { handleReply, extractThreadId, buildReplyCliCommand, registerReplyCommand } from './replyComment';
import * as child_process from 'child_process';
import { handleConflictCheck, ConflictResolution } from '../conflictHandler';

// Mock child_process
jest.mock('child_process');
const mockExecSync = child_process.execSync as jest.MockedFunction<typeof child_process.execSync>;

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

        // Default: no conflict detected (proceed with write)
        mockHandleConflictCheck.mockResolvedValue(ConflictResolution.OVERWRITE);

        // Mock VSCode environment
        (vscode.env as any) = { username: 'testuser' };

        // Create mock thread with contextValue containing thread_id
        mockThread = {
            contextValue: JSON.stringify({
                thread_id: '01HXYZ123456789ABCDEF',
                health: 'anchored',
                status: 'open',
                source_hash: 'sha256:abc123'
            }),
            uri: vscode.Uri.file('/test/project/src/file.ts'),
            range: new vscode.Range(0, 0, 5, 0),
            comments: [],
            canReply: true,
            state: vscode.CommentThreadState.Unresolved,
            collapsibleState: vscode.CommentThreadCollapsibleState.Expanded,
            dispose: jest.fn()
        } as any;

        // Create mock reply object
        mockReply = {
            thread: mockThread,
            text: 'This is a reply'
        };

        // Mock showInformationMessage and showErrorMessage
        (vscode.window.showInformationMessage as jest.Mock) = jest.fn();
        (vscode.window.showErrorMessage as jest.Mock) = jest.fn();

        // Mock execSync to succeed by default
        mockExecSync.mockReturnValue(Buffer.from(''));
    });

    describe('Basic reply functionality', () => {
        it('should successfully reply to a thread', async () => {
            await handleReply(mockReply, projectRoot);

            // Should call CLI with correct command
            expect(mockExecSync).toHaveBeenCalledWith(
                'comment reply 01HXYZ123456789ABCDEF "This is a reply" --author="testuser"',
                expect.objectContaining({
                    cwd: projectRoot,
                    encoding: 'utf-8',
                    stdio: 'pipe'
                })
            );

            // Should show success notification
            expect(vscode.window.showInformationMessage).toHaveBeenCalledWith(
                'Reply added to thread 01HXYZ123456789ABCDEF'
            );

            // Should add temporary comment to thread
            expect(mockThread.comments.length).toBe(1);
            expect((mockThread.comments[0].body as vscode.MarkdownString).value).toBe('This is a reply');
            expect(mockThread.comments[0].author.name).toBe('testuser');
            expect(mockThread.comments[0].mode).toBe(vscode.CommentMode.Preview);
        });

        it('should use fallback author when username unavailable', async () => {
            // Remove username from environment
            (vscode.env as any) = {};

            await handleReply(mockReply, projectRoot);

            expect(mockExecSync).toHaveBeenCalledWith(
                expect.stringContaining('--author="vscode-user"'),
                expect.any(Object)
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
        it('should fail when thread has no contextValue', async () => {
            mockThread.contextValue = undefined;

            await handleReply(mockReply, projectRoot);

            expect(vscode.window.showErrorMessage).toHaveBeenCalledWith(
                'Failed to identify thread for reply'
            );
            expect(mockExecSync).not.toHaveBeenCalled();
            expect(mockThread.comments.length).toBe(0);
        });

        it('should fail when contextValue has invalid JSON', async () => {
            mockThread.contextValue = 'invalid json {';

            await handleReply(mockReply, projectRoot);

            expect(vscode.window.showErrorMessage).toHaveBeenCalledWith(
                'Failed to identify thread for reply'
            );
        });

        it('should fail when contextValue missing thread_id', async () => {
            mockThread.contextValue = JSON.stringify({
                health: 'anchored',
                status: 'open'
                // No thread_id
            });

            await handleReply(mockReply, projectRoot);

            expect(vscode.window.showErrorMessage).toHaveBeenCalledWith(
                'Failed to identify thread for reply'
            );
        });
    });

    describe('Input validation', () => {
        it('should reject empty reply text', async () => {
            mockReply.text = '';

            await handleReply(mockReply, projectRoot);

            expect(vscode.window.showErrorMessage).toHaveBeenCalledWith(
                'Reply text cannot be empty'
            );
            expect(mockExecSync).not.toHaveBeenCalled();
        });

        it('should reject whitespace-only reply text', async () => {
            mockReply.text = '   \n  \t  ';

            await handleReply(mockReply, projectRoot);

            expect(vscode.window.showErrorMessage).toHaveBeenCalledWith(
                'Reply text cannot be empty'
            );
        });

        it('should accept reply with leading/trailing whitespace', async () => {
            mockReply.text = '  Valid reply with spaces  ';

            await handleReply(mockReply, projectRoot);

            // Should pass the text as-is (spaces preserved)
            expect(mockExecSync).toHaveBeenCalledWith(
                expect.stringContaining('"  Valid reply with spaces  "'),
                expect.any(Object)
            );
        });
    });

    describe('Text escaping', () => {
        it('should escape double quotes in reply text', async () => {
            mockReply.text = 'Reply with "quoted" text';

            await handleReply(mockReply, projectRoot);

            expect(mockExecSync).toHaveBeenCalledWith(
                'comment reply 01HXYZ123456789ABCDEF "Reply with \\"quoted\\" text" --author="testuser"',
                expect.any(Object)
            );
        });

        it('should escape backslashes in reply text', async () => {
            mockReply.text = 'Path: C:\\Users\\test';

            await handleReply(mockReply, projectRoot);

            expect(mockExecSync).toHaveBeenCalledWith(
                'comment reply 01HXYZ123456789ABCDEF "Path: C:\\\\Users\\\\test" --author="testuser"',
                expect.any(Object)
            );
        });

        it('should escape both backslashes and quotes', async () => {
            mockReply.text = 'Code: "C:\\Program Files\\"';

            await handleReply(mockReply, projectRoot);

            expect(mockExecSync).toHaveBeenCalledWith(
                'comment reply 01HXYZ123456789ABCDEF "Code: \\"C:\\\\Program Files\\\\\\"" --author="testuser"',
                expect.any(Object)
            );
        });

        it('should handle multiline reply text', async () => {
            mockReply.text = 'Line 1\nLine 2\nLine 3';

            await handleReply(mockReply, projectRoot);

            expect(mockExecSync).toHaveBeenCalledWith(
                'comment reply 01HXYZ123456789ABCDEF "Line 1\\nLine 2\\nLine 3" --author="testuser"',
                expect.any(Object)
            );
        });
    });

    describe('Error handling', () => {
        it('should show error notification when CLI command fails', async () => {
            const cliError = new Error('CLI execution failed');
            (cliError as any).stderr = Buffer.from('Error: Thread not found');
            mockExecSync.mockImplementation(() => {
                throw cliError;
            });

            await handleReply(mockReply, projectRoot);

            expect(vscode.window.showErrorMessage).toHaveBeenCalledWith(
                'Failed to add reply: Error: Thread not found'
            );
            expect(mockThread.comments.length).toBe(0);
        });

        it('should handle CLI error without stderr', async () => {
            const cliError = new Error('Unknown CLI error');
            mockExecSync.mockImplementation(() => {
                throw cliError;
            });

            await handleReply(mockReply, projectRoot);

            expect(vscode.window.showErrorMessage).toHaveBeenCalledWith(
                'Failed to add reply: Unknown CLI error'
            );
        });

        it('should handle generic error without message', async () => {
            mockExecSync.mockImplementation(() => {
                throw { stderr: null }; // Error object without message
            });

            await handleReply(mockReply, projectRoot);

            expect(vscode.window.showErrorMessage).toHaveBeenCalledWith(
                'Failed to add reply: Unknown error'
            );
        });
    });

    describe('CLI command construction', () => {
        it('should build correct CLI command with all parameters', async () => {
            const threadId = '01HXYZ123456789ABCDEF';
            mockThread.contextValue = JSON.stringify({ thread_id: threadId });

            mockReply.text = 'My reply';

            await handleReply(mockReply, projectRoot);

            expect(mockExecSync).toHaveBeenCalledWith(
                `comment reply ${threadId} "My reply" --author="testuser"`,
                expect.objectContaining({
                    cwd: projectRoot,
                    encoding: 'utf-8',
                    stdio: 'pipe'
                })
            );
        });

        it('should execute command in correct working directory', async () => {
            const customRoot = '/custom/project/path';

            await handleReply(mockReply, customRoot);

            expect(mockExecSync).toHaveBeenCalledWith(
                expect.any(String),
                expect.objectContaining({
                    cwd: customRoot
                })
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

            // Should have both comments
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

describe('extractThreadId', () => {
    it('should extract thread_id from valid contextValue', () => {
        const mockThread: vscode.CommentThread = {
            contextValue: JSON.stringify({
                thread_id: '01HXYZ123456789ABCDEF',
                health: 'anchored'
            })
        } as any;

        const result = extractThreadId(mockThread);
        expect(result).toBe('01HXYZ123456789ABCDEF');
    });

    it('should return null when contextValue is undefined', () => {
        const mockThread: vscode.CommentThread = {
            contextValue: undefined
        } as any;

        const result = extractThreadId(mockThread);
        expect(result).toBeNull();
    });

    it('should return null when contextValue is invalid JSON', () => {
        const mockThread: vscode.CommentThread = {
            contextValue: 'invalid json'
        } as any;

        const result = extractThreadId(mockThread);
        expect(result).toBeNull();
    });

    it('should return null when thread_id is missing', () => {
        const mockThread: vscode.CommentThread = {
            contextValue: JSON.stringify({ health: 'anchored' })
        } as any;

        const result = extractThreadId(mockThread);
        expect(result).toBeNull();
    });
});

describe('buildReplyCliCommand', () => {
    it('should build command with correct format', () => {
        const result = buildReplyCliCommand('01HXYZ', 'Test reply', 'testuser');
        expect(result).toBe('comment reply 01HXYZ "Test reply" --author="testuser"');
    });

    it('should escape double quotes', () => {
        const result = buildReplyCliCommand('01HXYZ', 'Reply with "quotes"', 'testuser');
        expect(result).toBe('comment reply 01HXYZ "Reply with \\"quotes\\"" --author="testuser"');
    });

    it('should escape backslashes', () => {
        const result = buildReplyCliCommand('01HXYZ', 'Path: C:\\test', 'testuser');
        expect(result).toBe('comment reply 01HXYZ "Path: C:\\\\test" --author="testuser"');
    });
});

describe('registerReplyCommand', () => {
    let mockContext: vscode.ExtensionContext;
    const projectRoot = '/test/project';

    beforeEach(() => {
        jest.clearAllMocks();

        // Create mock extension context
        mockContext = {
            subscriptions: []
        } as any;

        // Mock VSCode commands
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
