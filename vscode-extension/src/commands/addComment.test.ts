/**
 * Unit tests for addComment command.
 */

import * as vscode from 'vscode';
import { addCommentCommand } from './addComment';
import * as child_process from 'child_process';

// Mock vscode module
jest.mock('vscode');

// Mock child_process module
jest.mock('child_process');

const mockExecFile = child_process.execFile as unknown as jest.Mock;

describe('addCommentCommand', () => {
    let mockEditor: any;
    let mockDocument: any;
    let mockSelection: any;
    let projectRoot: string;

    let mockShowErrorMessage: jest.Mock;
    let mockShowInformationMessage: jest.Mock;
    let mockShowInputBox: jest.Mock;

    beforeEach(() => {
        jest.clearAllMocks();

        projectRoot = '/test/project';

        mockShowErrorMessage = jest.fn();
        mockShowInformationMessage = jest.fn();
        mockShowInputBox = jest.fn();

        (vscode.window as any) = {
            activeTextEditor: undefined,
            showErrorMessage: mockShowErrorMessage,
            showInformationMessage: mockShowInformationMessage,
            showInputBox: mockShowInputBox
        };

        (vscode.env as any) = {
            username: 'test-user'
        };

        mockExecFile.mockImplementation(
            (cmd: string, args: string[], opts: any, cb: Function) => {
                cb(null, { stdout: '', stderr: '' });
            }
        );
    });

    describe('validation', () => {
        test('shows error when no active editor', async () => {
            (vscode.window as any).activeTextEditor = undefined;

            await addCommentCommand(projectRoot);

            expect(mockShowErrorMessage).toHaveBeenCalledWith('No active editor found');
            expect(mockShowInputBox).not.toHaveBeenCalled();
        });

        test('shows error when selection is empty', async () => {
            mockSelection = {
                isEmpty: true,
                start: { line: 5, character: 0 },
                end: { line: 5, character: 0 }
            };

            mockDocument = {
                uri: { fsPath: '/test/project/src/main.py' }
            };

            mockEditor = {
                selection: mockSelection,
                document: mockDocument
            };

            (vscode.window as any).activeTextEditor = mockEditor;

            await addCommentCommand(projectRoot);

            expect(mockShowErrorMessage).toHaveBeenCalledWith('Please select text to comment on');
            expect(mockShowInputBox).not.toHaveBeenCalled();
        });

        test('shows error when file is outside project root', async () => {
            mockSelection = {
                isEmpty: false,
                start: { line: 10, character: 0 },
                end: { line: 15, character: 20 }
            };

            mockDocument = {
                uri: { fsPath: '/other/directory/file.py' }
            };

            mockEditor = {
                selection: mockSelection,
                document: mockDocument
            };

            (vscode.window as any).activeTextEditor = mockEditor;

            await addCommentCommand(projectRoot);

            expect(mockShowErrorMessage).toHaveBeenCalledWith(
                'File is outside project root and cannot be commented on'
            );
            expect(mockShowInputBox).not.toHaveBeenCalled();
        });
    });

    describe('line number conversion', () => {
        test('converts 0-indexed VSCode lines to 1-indexed sidecar format', async () => {
            mockSelection = {
                isEmpty: false,
                start: { line: 0, character: 0 },
                end: { line: 2, character: 10 }
            };

            mockDocument = {
                uri: { fsPath: '/test/project/src/main.py' }
            };

            mockEditor = {
                selection: mockSelection,
                document: mockDocument
            };

            (vscode.window as any).activeTextEditor = mockEditor;
            mockShowInputBox.mockResolvedValue('Test comment');

            await addCommentCommand(projectRoot);

            expect(mockExecFile).toHaveBeenCalledWith(
                'comment',
                expect.arrayContaining(['-L', '1:3']),
                expect.any(Object),
                expect.any(Function)
            );
        });

        test('handles single-line selection (start === end)', async () => {
            mockSelection = {
                isEmpty: false,
                start: { line: 10, character: 5 },
                end: { line: 10, character: 20 }
            };

            mockDocument = {
                uri: { fsPath: '/test/project/README.md' }
            };

            mockEditor = {
                selection: mockSelection,
                document: mockDocument
            };

            (vscode.window as any).activeTextEditor = mockEditor;
            mockShowInputBox.mockResolvedValue('Comment on line 11');

            await addCommentCommand(projectRoot);

            expect(mockExecFile).toHaveBeenCalledWith(
                'comment',
                expect.arrayContaining(['-L', '11:11']),
                expect.any(Object),
                expect.any(Function)
            );
        });
    });

    describe('CLI command generation', () => {
        beforeEach(() => {
            mockSelection = {
                isEmpty: false,
                start: { line: 10, character: 0 },
                end: { line: 15, character: 20 }
            };

            mockDocument = {
                uri: { fsPath: '/test/project/src/main.py' }
            };

            mockEditor = {
                selection: mockSelection,
                document: mockDocument
            };

            (vscode.window as any).activeTextEditor = mockEditor;
        });

        test('generates correct CLI command with all parameters', async () => {
            mockShowInputBox.mockResolvedValue('Fix this function');

            await addCommentCommand(projectRoot);

            expect(mockExecFile).toHaveBeenCalledWith(
                'comment',
                ['add', 'src/main.py', '-L', '11:16', '--author=test-user', 'Fix this function'],
                expect.objectContaining({
                    cwd: projectRoot,
                    encoding: 'utf-8'
                }),
                expect.any(Function)
            );
        });

        test('passes text with special characters directly (no escaping needed)', async () => {
            mockShowInputBox.mockResolvedValue('This is a "quoted" string');

            await addCommentCommand(projectRoot);

            expect(mockExecFile).toHaveBeenCalledWith(
                'comment',
                expect.arrayContaining(['This is a "quoted" string']),
                expect.any(Object),
                expect.any(Function)
            );
        });

        test('uses relative file path from project root', async () => {
            mockDocument = {
                uri: { fsPath: '/test/project/subdir/nested/file.txt' }
            };
            mockEditor.document = mockDocument;

            mockShowInputBox.mockResolvedValue('Comment');

            await addCommentCommand(projectRoot);

            expect(mockExecFile).toHaveBeenCalledWith(
                'comment',
                expect.arrayContaining(['add', 'subdir/nested/file.txt']),
                expect.any(Object),
                expect.any(Function)
            );
        });

        test('uses fallback author when vscode.env.username is undefined', async () => {
            (vscode.env as any).username = undefined;

            mockShowInputBox.mockResolvedValue('Test');

            await addCommentCommand(projectRoot);

            expect(mockExecFile).toHaveBeenCalledWith(
                'comment',
                expect.arrayContaining(['--author=vscode-user']),
                expect.any(Object),
                expect.any(Function)
            );
        });
    });

    describe('user interaction', () => {
        beforeEach(() => {
            mockSelection = {
                isEmpty: false,
                start: { line: 5, character: 0 },
                end: { line: 10, character: 0 }
            };

            mockDocument = {
                uri: { fsPath: '/test/project/file.py' }
            };

            mockEditor = {
                selection: mockSelection,
                document: mockDocument
            };

            (vscode.window as any).activeTextEditor = mockEditor;
        });

        test('prompts user with correct file and line info', async () => {
            mockShowInputBox.mockResolvedValue('Test comment');

            await addCommentCommand(projectRoot);

            expect(mockShowInputBox).toHaveBeenCalledWith(
                expect.objectContaining({
                    prompt: 'Add comment to file.py (lines 6-11)',
                    placeHolder: 'Enter your comment here...',
                    ignoreFocusOut: true,
                    validateInput: expect.any(Function)
                })
            );
        });

        test('does nothing when user cancels input box', async () => {
            mockShowInputBox.mockResolvedValue(undefined);

            await addCommentCommand(projectRoot);

            expect(mockExecFile).not.toHaveBeenCalled();
            expect(mockShowErrorMessage).not.toHaveBeenCalled();
            expect(mockShowInformationMessage).not.toHaveBeenCalled();
        });

        test('validates that comment text is not empty', async () => {
            mockShowInputBox.mockResolvedValue('Valid comment');

            await addCommentCommand(projectRoot);

            const validateInput = mockShowInputBox.mock.calls[0][0].validateInput;

            expect(validateInput('')).toBe('Comment text cannot be empty');
            expect(validateInput('   ')).toBe('Comment text cannot be empty');
            expect(validateInput('Valid text')).toBeNull();
        });
    });

    describe('success and error handling', () => {
        beforeEach(() => {
            mockSelection = {
                isEmpty: false,
                start: { line: 0, character: 0 },
                end: { line: 5, character: 0 }
            };

            mockDocument = {
                uri: { fsPath: '/test/project/test.py' }
            };

            mockEditor = {
                selection: mockSelection,
                document: mockDocument
            };

            (vscode.window as any).activeTextEditor = mockEditor;
            mockShowInputBox.mockResolvedValue('Test comment');
        });

        test('shows success message when CLI succeeds', async () => {
            await addCommentCommand(projectRoot);

            expect(mockShowInformationMessage).toHaveBeenCalledWith(
                'Comment added to test.py:1-6'
            );
            expect(mockShowErrorMessage).not.toHaveBeenCalled();
        });

        test('shows error message when CLI fails with stderr', async () => {
            const error: any = new Error('Command failed');
            error.stderr = 'Error: Invalid line range';
            mockExecFile.mockImplementation(
                (cmd: string, args: string[], opts: any, cb: Function) => {
                    cb(error);
                }
            );

            await addCommentCommand(projectRoot);

            expect(mockShowErrorMessage).toHaveBeenCalledWith(
                'Failed to add comment: Error: Invalid line range'
            );
            expect(mockShowInformationMessage).not.toHaveBeenCalled();
        });

        test('shows error message when CLI fails without stderr', async () => {
            const error = new Error('Command not found');
            mockExecFile.mockImplementation(
                (cmd: string, args: string[], opts: any, cb: Function) => {
                    cb(error);
                }
            );

            await addCommentCommand(projectRoot);

            expect(mockShowErrorMessage).toHaveBeenCalledWith(
                'Failed to add comment: Command not found'
            );
        });
    });
});
