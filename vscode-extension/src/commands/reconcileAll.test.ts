/**
 * Tests for reconcileAll command
 */

import * as vscode from 'vscode';
import { reconcileAllCommand, registerReconcileAllCommand } from './reconcileAll';
import * as child_process from 'child_process';

// Mock child_process
jest.mock('child_process');
const mockExecSync = child_process.execSync as jest.MockedFunction<typeof child_process.execSync>;

describe('reconcileAllCommand', () => {
    let mockProjectRoot: string;
    let mockCommentProvider: any;
    let mockShowInformationMessage: jest.Mock;
    let mockShowWarningMessage: jest.Mock;
    let mockShowErrorMessage: jest.Mock;
    let mockWithProgress: jest.Mock;
    let mockVisibleTextEditors: any[];

    beforeEach(() => {
        mockProjectRoot = '/home/user/project';
        mockCommentProvider = {
            loadCommentsForDocument: jest.fn().mockResolvedValue(undefined)
        };

        // Mock vscode.window methods
        mockShowInformationMessage = jest.fn();
        mockShowWarningMessage = jest.fn();
        mockShowErrorMessage = jest.fn();
        mockWithProgress = jest.fn();
        mockVisibleTextEditors = [];

        (vscode.window as any).showInformationMessage = mockShowInformationMessage;
        (vscode.window as any).showWarningMessage = mockShowWarningMessage;
        (vscode.window as any).showErrorMessage = mockShowErrorMessage;
        (vscode.window as any).withProgress = mockWithProgress;
        Object.defineProperty(vscode.window, 'visibleTextEditors', {
            get: () => mockVisibleTextEditors,
            configurable: true
        });

        // Clear mocks
        jest.clearAllMocks();
    });

    afterEach(() => {
        jest.restoreAllMocks();
    });

    describe('user confirmation', () => {
        it('returns false when user cancels confirmation dialog', async () => {
            mockShowInformationMessage.mockResolvedValue('Cancel');

            const result = await reconcileAllCommand(mockProjectRoot, mockCommentProvider);

            expect(result).toBe(false);
            expect(mockShowInformationMessage).toHaveBeenCalledWith(
                'Reconcile all comment threads in project? This may take a moment for large projects.',
                { modal: true },
                'Reconcile All',
                'Cancel'
            );
            expect(mockWithProgress).not.toHaveBeenCalled();
            expect(mockExecSync).not.toHaveBeenCalled();
        });

        it('returns false when user dismisses confirmation dialog', async () => {
            mockShowInformationMessage.mockResolvedValue(undefined);

            const result = await reconcileAllCommand(mockProjectRoot, mockCommentProvider);

            expect(result).toBe(false);
            expect(mockWithProgress).not.toHaveBeenCalled();
        });

        it('proceeds when user confirms', async () => {
            mockShowInformationMessage.mockResolvedValue('Reconcile All');
            mockWithProgress.mockImplementation(async (options, callback) => {
                return await callback({ report: jest.fn() });
            });
            mockExecSync.mockReturnValue(JSON.stringify({
                total_files: 1,
                total_threads: 5,
                anchored: 5,
                drifted: 0,
                orphaned: 0
            }));

            const result = await reconcileAllCommand(mockProjectRoot, mockCommentProvider);

            expect(result).toBe(true);
            expect(mockWithProgress).toHaveBeenCalled();
        });
    });

    describe('CLI execution', () => {
        beforeEach(() => {
            mockShowInformationMessage.mockResolvedValue('Reconcile All');
        });

        it('calls CLI with correct command', async () => {
            mockWithProgress.mockImplementation(async (options, callback) => {
                return await callback({ report: jest.fn() });
            });
            mockExecSync.mockReturnValue(JSON.stringify({
                total_files: 2,
                total_threads: 10,
                anchored: 8,
                drifted: 1,
                orphaned: 1
            }));

            await reconcileAllCommand(mockProjectRoot, mockCommentProvider);

            expect(mockExecSync).toHaveBeenCalledWith(
                'comment reconcile --all --json',
                expect.objectContaining({
                    cwd: mockProjectRoot,
                    encoding: 'utf-8',
                    maxBuffer: 10 * 1024 * 1024
                })
            );
        });

        it('shows progress notification during execution', async () => {
            const mockProgress = { report: jest.fn() };
            mockWithProgress.mockImplementation(async (options, callback) => {
                expect(options).toEqual({
                    location: vscode.ProgressLocation.Notification,
                    title: 'Reconciling all comment threads...',
                    cancellable: false
                });
                return await callback(mockProgress);
            });
            mockExecSync.mockReturnValue(JSON.stringify({
                total_files: 1,
                total_threads: 3,
                anchored: 3,
                drifted: 0,
                orphaned: 0
            }));

            await reconcileAllCommand(mockProjectRoot, mockCommentProvider);

            expect(mockProgress.report).toHaveBeenCalledWith({ increment: 0 });
            expect(mockProgress.report).toHaveBeenCalledWith({ increment: 100 });
        });
    });

    describe('JSON parsing', () => {
        beforeEach(() => {
            mockShowInformationMessage.mockResolvedValue('Reconcile All');
            mockWithProgress.mockImplementation(async (options, callback) => {
                return await callback({ report: jest.fn() });
            });
        });

        it('parses CLI JSON output correctly', async () => {
            const mockStats = {
                total_files: 3,
                total_threads: 15,
                anchored: 12,
                drifted: 2,
                orphaned: 1
            };
            mockExecSync.mockReturnValue(JSON.stringify(mockStats));

            const result = await reconcileAllCommand(mockProjectRoot, mockCommentProvider);

            expect(result).toBe(true);
            expect(mockShowWarningMessage).toHaveBeenCalledWith(
                'Reconciled 15 threads across 3 files: 12 anchored, 2 drifted, 1 orphaned'
            );
        });

        it('handles malformed JSON output', async () => {
            mockExecSync.mockReturnValue('not valid json');

            const result = await reconcileAllCommand(mockProjectRoot, mockCommentProvider);

            expect(result).toBe(false);
            expect(mockShowErrorMessage).toHaveBeenCalledWith(
                expect.stringContaining('Failed to parse reconciliation output')
            );
        });

        it('handles empty output', async () => {
            mockExecSync.mockReturnValue('');

            const result = await reconcileAllCommand(mockProjectRoot, mockCommentProvider);

            expect(result).toBe(false);
            expect(mockShowErrorMessage).toHaveBeenCalled();
        });
    });

    describe('notifications', () => {
        beforeEach(() => {
            mockShowInformationMessage.mockResolvedValue('Reconcile All');
            mockWithProgress.mockImplementation(async (options, callback) => {
                return await callback({ report: jest.fn() });
            });
        });

        it('shows success notification when all threads anchored', async () => {
            mockExecSync.mockReturnValue(JSON.stringify({
                total_files: 2,
                total_threads: 10,
                anchored: 10,
                drifted: 0,
                orphaned: 0
            }));

            await reconcileAllCommand(mockProjectRoot, mockCommentProvider);

            expect(mockShowInformationMessage).toHaveBeenCalledWith(
                'Reconciled 10 threads across 2 files: 10 anchored, 0 drifted, 0 orphaned'
            );
            expect(mockShowWarningMessage).not.toHaveBeenCalled();
        });

        it('shows warning notification when threads are drifted', async () => {
            mockExecSync.mockReturnValue(JSON.stringify({
                total_files: 1,
                total_threads: 5,
                anchored: 3,
                drifted: 2,
                orphaned: 0
            }));

            await reconcileAllCommand(mockProjectRoot, mockCommentProvider);

            expect(mockShowWarningMessage).toHaveBeenCalledWith(
                'Reconciled 5 threads across 1 files: 3 anchored, 2 drifted, 0 orphaned'
            );
            expect(mockShowInformationMessage).toHaveBeenCalledTimes(1); // Confirmation dialog only
        });

        it('shows warning notification when threads are orphaned', async () => {
            mockExecSync.mockReturnValue(JSON.stringify({
                total_files: 3,
                total_threads: 8,
                anchored: 6,
                drifted: 0,
                orphaned: 2
            }));

            await reconcileAllCommand(mockProjectRoot, mockCommentProvider);

            expect(mockShowWarningMessage).toHaveBeenCalledWith(
                'Reconciled 8 threads across 3 files: 6 anchored, 0 drifted, 2 orphaned'
            );
        });

        it('shows message when no threads found', async () => {
            mockExecSync.mockReturnValue(JSON.stringify({
                total_files: 0,
                total_threads: 0,
                anchored: 0,
                drifted: 0,
                orphaned: 0
            }));

            await reconcileAllCommand(mockProjectRoot, mockCommentProvider);

            expect(mockShowInformationMessage).toHaveBeenCalledWith(
                'No comment threads found in project.'
            );
        });

        it('handles missing statistics fields gracefully', async () => {
            mockExecSync.mockReturnValue(JSON.stringify({}));

            await reconcileAllCommand(mockProjectRoot, mockCommentProvider);

            expect(mockShowInformationMessage).toHaveBeenCalledWith(
                'No comment threads found in project.'
            );
        });
    });

    describe('error handling', () => {
        beforeEach(() => {
            mockShowInformationMessage.mockResolvedValue('Reconcile All');
            mockWithProgress.mockImplementation(async (options, callback) => {
                return await callback({ report: jest.fn() });
            });
        });

        it('handles user error (exit code 1)', async () => {
            const error: any = new Error('Command failed');
            error.status = 1;
            error.stderr = Buffer.from('No sidecar files found');
            mockExecSync.mockImplementation(() => { throw error; });

            const result = await reconcileAllCommand(mockProjectRoot, mockCommentProvider);

            expect(result).toBe(false);
            expect(mockShowErrorMessage).toHaveBeenCalledWith(
                'Reconciliation failed: No sidecar files found'
            );
        });

        it('handles system error (exit code 2)', async () => {
            const error: any = new Error('Command failed');
            error.status = 2;
            error.stderr = Buffer.from('File system error');
            mockExecSync.mockImplementation(() => { throw error; });

            const result = await reconcileAllCommand(mockProjectRoot, mockCommentProvider);

            expect(result).toBe(false);
            expect(mockShowErrorMessage).toHaveBeenCalledWith(
                'System error during reconciliation: File system error'
            );
        });

        it('handles unknown CLI error', async () => {
            const error = new Error('Unknown error');
            mockExecSync.mockImplementation(() => { throw error; });

            const result = await reconcileAllCommand(mockProjectRoot, mockCommentProvider);

            expect(result).toBe(false);
            expect(mockShowErrorMessage).toHaveBeenCalledWith(
                'Failed to run reconciliation: Unknown error'
            );
        });

        it('handles stderr without message', async () => {
            const error: any = new Error('Command failed');
            error.status = 1;
            error.stderr = undefined;
            mockExecSync.mockImplementation(() => { throw error; });

            const result = await reconcileAllCommand(mockProjectRoot, mockCommentProvider);

            expect(result).toBe(false);
            expect(mockShowErrorMessage).toHaveBeenCalledWith(
                'Reconciliation failed: Unknown error'
            );
        });
    });

    describe('comment reload', () => {
        beforeEach(() => {
            mockShowInformationMessage.mockResolvedValue('Reconcile All');
            mockWithProgress.mockImplementation(async (options, callback) => {
                return await callback({ report: jest.fn() });
            });
            mockExecSync.mockReturnValue(JSON.stringify({
                total_files: 1,
                total_threads: 3,
                anchored: 3,
                drifted: 0,
                orphaned: 0
            }));
        });

        it('reloads comments for all visible editors after reconciliation', async () => {
            const mockDocument1 = {
                uri: { scheme: 'file', fsPath: '/home/user/project/file1.txt' }
            };
            const mockDocument2 = {
                uri: { scheme: 'file', fsPath: '/home/user/project/subdir/file2.txt' }
            };
            const mockEditor1 = { document: mockDocument1 };
            const mockEditor2 = { document: mockDocument2 };
            mockVisibleTextEditors = [mockEditor1, mockEditor2];

            await reconcileAllCommand(mockProjectRoot, mockCommentProvider);

            expect(mockCommentProvider.loadCommentsForDocument).toHaveBeenCalledTimes(2);
            expect(mockCommentProvider.loadCommentsForDocument).toHaveBeenCalledWith(mockDocument1);
            expect(mockCommentProvider.loadCommentsForDocument).toHaveBeenCalledWith(mockDocument2);
        });

        it('skips non-file URIs when reloading comments', async () => {
            const mockDocument1 = {
                uri: { scheme: 'file', fsPath: '/home/user/project/file1.txt' }
            };
            const mockDocument2 = {
                uri: { scheme: 'untitled', fsPath: '' }
            };
            const mockEditor1 = { document: mockDocument1 };
            const mockEditor2 = { document: mockDocument2 };
            mockVisibleTextEditors = [mockEditor1, mockEditor2];

            await reconcileAllCommand(mockProjectRoot, mockCommentProvider);

            expect(mockCommentProvider.loadCommentsForDocument).toHaveBeenCalledTimes(1);
            expect(mockCommentProvider.loadCommentsForDocument).toHaveBeenCalledWith(mockDocument1);
        });

        it('skips files outside project when reloading comments', async () => {
            const mockDocument1 = {
                uri: { scheme: 'file', fsPath: '/home/user/project/file1.txt' }
            };
            const mockDocument2 = {
                uri: { scheme: 'file', fsPath: '/home/user/other-project/file2.txt' }
            };
            const mockEditor1 = { document: mockDocument1 };
            const mockEditor2 = { document: mockDocument2 };
            mockVisibleTextEditors = [mockEditor1, mockEditor2];

            await reconcileAllCommand(mockProjectRoot, mockCommentProvider);

            expect(mockCommentProvider.loadCommentsForDocument).toHaveBeenCalledTimes(1);
            expect(mockCommentProvider.loadCommentsForDocument).toHaveBeenCalledWith(mockDocument1);
        });

        it('handles no visible editors gracefully', async () => {
            mockVisibleTextEditors = [];

            await reconcileAllCommand(mockProjectRoot, mockCommentProvider);

            expect(mockCommentProvider.loadCommentsForDocument).not.toHaveBeenCalled();
        });
    });

    describe('registerReconcileAllCommand', () => {
        it('registers command with correct ID', () => {
            const mockContext = {
                subscriptions: []
            } as any;
            const mockRegisterCommand = jest.fn().mockReturnValue({} as vscode.Disposable);
            (vscode.commands as any).registerCommand = mockRegisterCommand;

            registerReconcileAllCommand(mockContext, mockProjectRoot, mockCommentProvider);

            expect(mockRegisterCommand).toHaveBeenCalledWith(
                'file-native-comments.reconcileAll',
                expect.any(Function)
            );
            expect(mockContext.subscriptions).toHaveLength(1);
        });

        it('calls reconcileAllCommand when command invoked', async () => {
            const mockContext = {
                subscriptions: []
            } as any;
            let registeredCallback: any;
            const mockRegisterCommand = jest.fn((id, callback) => {
                registeredCallback = callback;
                return {} as vscode.Disposable;
            });
            (vscode.commands as any).registerCommand = mockRegisterCommand;

            mockShowInformationMessage.mockResolvedValue('Reconcile All');
            mockWithProgress.mockImplementation(async (options, callback) => {
                return await callback({ report: jest.fn() });
            });
            mockExecSync.mockReturnValue(JSON.stringify({
                total_files: 1,
                total_threads: 2,
                anchored: 2,
                drifted: 0,
                orphaned: 0
            }));

            registerReconcileAllCommand(mockContext, mockProjectRoot, mockCommentProvider);
            await registeredCallback();

            expect(mockShowInformationMessage).toHaveBeenCalled();
            expect(mockExecSync).toHaveBeenCalled();
        });
    });
});
