/**
 * Tests for deleteThread.ts - Thread deletion functionality
 */

import * as vscode from 'vscode';
import * as child_process from 'child_process';
import { deleteThread, registerDeleteCommand } from './deleteThread';
import { threadMetadataMap } from '../utils';

// Mock child_process
jest.mock('child_process');
const mockExecFile = child_process.execFile as unknown as jest.Mock;

// Mock vscode module
jest.mock('vscode');

describe('deleteThread', () => {
    let mockThread: vscode.CommentThread;
    const projectRoot = '/test/project';

    beforeEach(() => {
        jest.clearAllMocks();

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

        (vscode.window.showWarningMessage as jest.Mock).mockResolvedValue('Delete');
        (vscode.window.showInformationMessage as jest.Mock).mockResolvedValue(undefined);
        (vscode.window.showErrorMessage as jest.Mock).mockResolvedValue(undefined);

        mockExecFile.mockImplementation(
            (cmd: string, args: string[], opts: any, cb: Function) => {
                cb(null, { stdout: 'Thread 01HXYZ123456 deleted', stderr: '' });
            }
        );
    });

    it('should successfully delete a thread', async () => {
        await deleteThread(mockThread, projectRoot);

        expect(mockExecFile).toHaveBeenCalledWith(
            'comment',
            ['delete', '01HXYZ123456', '--force'],
            expect.objectContaining({
                cwd: projectRoot,
                encoding: 'utf-8'
            }),
            expect.any(Function)
        );

        expect(vscode.window.showInformationMessage).toHaveBeenCalledWith(
            'Thread deleted'
        );

        expect(mockThread.dispose).toHaveBeenCalled();
    });

    it('should confirm with user before deleting', async () => {
        await deleteThread(mockThread, projectRoot);

        expect(vscode.window.showWarningMessage).toHaveBeenCalledWith(
            'Delete this comment thread? This cannot be undone.',
            { modal: true },
            'Delete',
            'Cancel'
        );
    });

    it('should abort if user cancels confirmation', async () => {
        (vscode.window.showWarningMessage as jest.Mock).mockResolvedValue('Cancel');

        await deleteThread(mockThread, projectRoot);

        expect(mockExecFile).not.toHaveBeenCalled();
        expect(mockThread.dispose).not.toHaveBeenCalled();
    });

    it('should abort if user dismisses dialog', async () => {
        (vscode.window.showWarningMessage as jest.Mock).mockResolvedValue(undefined);

        await deleteThread(mockThread, projectRoot);

        expect(mockExecFile).not.toHaveBeenCalled();
        expect(mockThread.dispose).not.toHaveBeenCalled();
    });

    it('should show error if thread_id cannot be extracted', async () => {
        const bareThread = {
            contextValue: undefined,
            uri: vscode.Uri.file('/test/file.py'),
            dispose: jest.fn()
        } as any;

        await deleteThread(bareThread, projectRoot);

        expect(vscode.window.showErrorMessage).toHaveBeenCalledWith(
            'Failed to identify thread for deletion'
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

        await deleteThread(mockThread, projectRoot);

        expect(vscode.window.showErrorMessage).toHaveBeenCalledWith(
            'Failed to delete thread: Thread not found'
        );
        expect(mockThread.dispose).not.toHaveBeenCalled();
    });

    it('should show error with generic message if no stderr', async () => {
        const cliError = new Error('Unknown error');
        mockExecFile.mockImplementation(
            (cmd: string, args: string[], opts: any, cb: Function) => {
                cb(cliError);
            }
        );

        await deleteThread(mockThread, projectRoot);

        expect(vscode.window.showErrorMessage).toHaveBeenCalledWith(
            'Failed to delete thread: Unknown error'
        );
    });

    it('should log command execution', async () => {
        const consoleSpy = jest.spyOn(console, 'log').mockImplementation();

        await deleteThread(mockThread, projectRoot);

        expect(consoleSpy).toHaveBeenCalledWith(
            'Executing: comment delete 01HXYZ123456 --force'
        );

        consoleSpy.mockRestore();
    });
});

describe('registerDeleteCommand', () => {
    it('should register command with correct ID', () => {
        const mockContext = {
            subscriptions: []
        } as any as vscode.ExtensionContext;

        const mockDisposable = { dispose: jest.fn() };
        (vscode.commands.registerCommand as jest.Mock).mockReturnValue(mockDisposable);

        registerDeleteCommand(mockContext, '/test/project');

        expect(vscode.commands.registerCommand).toHaveBeenCalledWith(
            'file-native-comments.deleteThread',
            expect.any(Function)
        );

        expect(mockContext.subscriptions).toContain(mockDisposable);
    });

    it('should log registration', () => {
        const consoleSpy = jest.spyOn(console, 'log').mockImplementation();
        const mockContext = {
            subscriptions: []
        } as any as vscode.ExtensionContext;

        registerDeleteCommand(mockContext, '/test/project');

        expect(consoleSpy).toHaveBeenCalledWith(
            'Delete command registered: file-native-comments.deleteThread'
        );

        consoleSpy.mockRestore();
    });
});
