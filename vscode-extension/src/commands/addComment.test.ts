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

describe('addCommentCommand', () => {
    let mockEditor: any;
    let mockDocument: any;
    let mockSelection: any;
    let projectRoot: string;

    // Mock functions
    let mockShowErrorMessage: jest.Mock;
    let mockShowInformationMessage: jest.Mock;
    let mockShowInputBox: jest.Mock;
    let mockExecSync: jest.Mock;

    beforeEach(() => {
        // Reset all mocks
        jest.clearAllMocks();

        projectRoot = '/test/project';

        // Mock VSCode window methods
        mockShowErrorMessage = jest.fn();
        mockShowInformationMessage = jest.fn();
        mockShowInputBox = jest.fn();

        (vscode.window as any) = {
            activeTextEditor: undefined,
            showErrorMessage: mockShowErrorMessage,
            showInformationMessage: mockShowInformationMessage,
            showInputBox: mockShowInputBox
        };

        // Mock VSCode env
        (vscode.env as any) = {
            username: 'test-user'
        };

        // Mock execSync
        mockExecSync = child_process.execSync as jest.Mock;
    });

    describe('validation', () => {
        test('shows error when no active editor', async () => {
            // No active editor
            (vscode.window as any).activeTextEditor = undefined;

            await addCommentCommand(projectRoot);

            expect(mockShowErrorMessage).toHaveBeenCalledWith('No active editor found');
            expect(mockShowInputBox).not.toHaveBeenCalled();
        });

        test('shows error when selection is empty', async () => {
            // Create mock editor with empty selection
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
            // Create mock editor with valid selection but file outside project
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
            // Setup: VSCode selection on lines 0-2 (0-indexed)
            // Expected: CLI command with lines 1-3 (1-indexed)
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

            // Mock input box (user enters comment)
            mockShowInputBox.mockResolvedValue('Test comment');

            // Mock successful CLI execution
            mockExecSync.mockReturnValue('');

            await addCommentCommand(projectRoot);

            // Verify CLI command contains 1-indexed lines (1:3, not 0:2)
            expect(mockExecSync).toHaveBeenCalledWith(
                expect.stringContaining('-L 1:3'),
                expect.any(Object)
            );
        });

        test('handles single-line selection (start === end)', async () => {
            // VSCode line 10 (0-indexed) → sidecar line 11 (1-indexed)
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
            mockExecSync.mockReturnValue('');

            await addCommentCommand(projectRoot);

            expect(mockExecSync).toHaveBeenCalledWith(
                expect.stringContaining('-L 11:11'),
                expect.any(Object)
            );
        });
    });

    describe('CLI command generation', () => {
        beforeEach(() => {
            // Standard mock setup for CLI tests
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
            mockExecSync.mockReturnValue('');
        });

        test('generates correct CLI command with all parameters', async () => {
            mockShowInputBox.mockResolvedValue('Fix this function');

            await addCommentCommand(projectRoot);

            expect(mockExecSync).toHaveBeenCalledWith(
                'comment add "src/main.py" -L 11:16 --author="test-user" "Fix this function"',
                expect.objectContaining({
                    cwd: projectRoot,
                    encoding: 'utf-8',
                    stdio: 'pipe'
                })
            );
        });

        test('escapes double quotes in comment text', async () => {
            mockShowInputBox.mockResolvedValue('This is a "quoted" string');

            await addCommentCommand(projectRoot);

            expect(mockExecSync).toHaveBeenCalledWith(
                expect.stringContaining('This is a \\"quoted\\" string'),
                expect.any(Object)
            );
        });

        test('escapes backslashes in comment text', async () => {
            mockShowInputBox.mockResolvedValue('Path: C:\\Users\\test');

            await addCommentCommand(projectRoot);

            expect(mockExecSync).toHaveBeenCalledWith(
                expect.stringContaining('Path: C:\\\\Users\\\\test'),
                expect.any(Object)
            );
        });

        test('uses relative file path from project root', async () => {
            mockDocument = {
                uri: { fsPath: '/test/project/subdir/nested/file.txt' }
            };
            mockEditor.document = mockDocument;

            mockShowInputBox.mockResolvedValue('Comment');

            await addCommentCommand(projectRoot);

            expect(mockExecSync).toHaveBeenCalledWith(
                expect.stringContaining('comment add "subdir/nested/file.txt"'),
                expect.any(Object)
            );
        });

        test('uses fallback author when vscode.env.username is undefined', async () => {
            (vscode.env as any).username = undefined;

            mockShowInputBox.mockResolvedValue('Test');

            await addCommentCommand(projectRoot);

            expect(mockExecSync).toHaveBeenCalledWith(
                expect.stringContaining('--author="vscode-user"'),
                expect.any(Object)
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
            mockExecSync.mockReturnValue('');

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

            expect(mockExecSync).not.toHaveBeenCalled();
            expect(mockShowErrorMessage).not.toHaveBeenCalled();
            expect(mockShowInformationMessage).not.toHaveBeenCalled();
        });

        test('validates that comment text is not empty', async () => {
            mockShowInputBox.mockResolvedValue('Valid comment');
            mockExecSync.mockReturnValue('');

            await addCommentCommand(projectRoot);

            // Extract the validateInput function
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
            mockExecSync.mockReturnValue('');

            await addCommentCommand(projectRoot);

            expect(mockShowInformationMessage).toHaveBeenCalledWith(
                'Comment added to test.py:1-6'
            );
            expect(mockShowErrorMessage).not.toHaveBeenCalled();
        });

        test('shows error message when CLI fails with stderr', async () => {
            const error: any = new Error('Command failed');
            error.stderr = Buffer.from('Error: Invalid line range');
            mockExecSync.mockImplementation(() => {
                throw error;
            });

            await addCommentCommand(projectRoot);

            expect(mockShowErrorMessage).toHaveBeenCalledWith(
                'Failed to add comment: Error: Invalid line range'
            );
            expect(mockShowInformationMessage).not.toHaveBeenCalled();
        });

        test('shows error message when CLI fails without stderr', async () => {
            const error = new Error('Command not found');
            mockExecSync.mockImplementation(() => {
                throw error;
            });

            await addCommentCommand(projectRoot);

            expect(mockShowErrorMessage).toHaveBeenCalledWith(
                'Failed to add comment: Command not found'
            );
        });

        test('handles unknown error gracefully', async () => {
            mockExecSync.mockImplementation(() => {
                throw { unknown: 'error' };
            });

            await addCommentCommand(projectRoot);

            expect(mockShowErrorMessage).toHaveBeenCalledWith(
                expect.stringContaining('Failed to add comment')
            );
        });
    });
});
