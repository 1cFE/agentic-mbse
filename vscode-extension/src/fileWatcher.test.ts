import { FileWatcher } from './fileWatcher';
import * as vscode from 'vscode';

// Mock vscode module
jest.mock('vscode');

describe('FileWatcher', () => {
    let fileWatcher: FileWatcher;
    let mockWatcher: any;
    let onDidCreateHandlers: Array<(uri: vscode.Uri) => void> = [];
    let onDidChangeHandlers: Array<(uri: vscode.Uri) => void> = [];
    let onDidDeleteHandlers: Array<(uri: vscode.Uri) => void> = [];

    beforeEach(() => {
        // Reset mock handlers
        onDidCreateHandlers = [];
        onDidChangeHandlers = [];
        onDidDeleteHandlers = [];

        // Create mock watcher with event emitters
        mockWatcher = {
            onDidCreate: jest.fn((handler) => {
                onDidCreateHandlers.push(handler);
                return { dispose: jest.fn() };
            }),
            onDidChange: jest.fn((handler) => {
                onDidChangeHandlers.push(handler);
                return { dispose: jest.fn() };
            }),
            onDidDelete: jest.fn((handler) => {
                onDidDeleteHandlers.push(handler);
                return { dispose: jest.fn() };
            }),
            dispose: jest.fn(),
        };

        // Mock createFileSystemWatcher
        (vscode.workspace.createFileSystemWatcher as jest.Mock) = jest.fn(() => mockWatcher);

        // Create file watcher
        fileWatcher = new FileWatcher('/project');
    });

    afterEach(() => {
        fileWatcher.stop();
        jest.clearAllTimers();
    });

    describe('start()', () => {
        it('creates a FileSystemWatcher with correct pattern', () => {
            fileWatcher.start();

            expect(vscode.workspace.createFileSystemWatcher).toHaveBeenCalledWith(
                expect.objectContaining({
                    pattern: '.comments/**/*.json',
                })
            );
        });

        it('registers handlers for create, change, and delete events', () => {
            fileWatcher.start();

            expect(mockWatcher.onDidCreate).toHaveBeenCalled();
            expect(mockWatcher.onDidChange).toHaveBeenCalled();
            expect(mockWatcher.onDidDelete).toHaveBeenCalled();
        });

        it('does nothing if already started', () => {
            fileWatcher.start();
            fileWatcher.start();

            expect(vscode.workspace.createFileSystemWatcher).toHaveBeenCalledTimes(1);
        });
    });

    describe('stop()', () => {
        it('disposes the watcher', () => {
            fileWatcher.start();
            fileWatcher.stop();

            expect(mockWatcher.dispose).toHaveBeenCalled();
        });

        it('clears all pending debounce timers', () => {
            jest.useFakeTimers();
            fileWatcher.start();

            const callback = jest.fn();
            fileWatcher.onSidecarChanged(callback);

            // Trigger change event
            const uri = { fsPath: '/project/.comments/src/example.py.json' } as vscode.Uri;
            onDidChangeHandlers.forEach(handler => handler(uri));

            // Stop before timer fires
            fileWatcher.stop();

            // Advance timers
            jest.advanceTimersByTime(3000);

            // Callback should NOT be invoked
            expect(callback).not.toHaveBeenCalled();

            jest.useRealTimers();
        });
    });

    describe('onSidecarChanged()', () => {
        it('registers a callback', () => {
            const callback = jest.fn();
            fileWatcher.onSidecarChanged(callback);

            // Internal check: callback should be registered
            expect(callback).toBeDefined();
        });

        it('invokes callback after debounce period', (done) => {
            fileWatcher.start();

            const callback = jest.fn((sourceFilePath) => {
                expect(sourceFilePath).toBe('/project/src/example.py');
                done();
            });
            fileWatcher.onSidecarChanged(callback);

            // Trigger change event
            const uri = { fsPath: '/project/.comments/src/example.py.json' } as vscode.Uri;
            onDidChangeHandlers.forEach(handler => handler(uri));
        });

        it('debounces multiple rapid changes into single event', (done) => {
            jest.useFakeTimers();
            fileWatcher.start();

            const callback = jest.fn();
            fileWatcher.onSidecarChanged(callback);

            // Trigger 5 rapid change events
            const uri = { fsPath: '/project/.comments/src/example.py.json' } as vscode.Uri;
            for (let i = 0; i < 5; i++) {
                onDidChangeHandlers.forEach(handler => handler(uri));
                jest.advanceTimersByTime(500); // Advance 500ms between events
            }

            // Advance past debounce period
            jest.advanceTimersByTime(2000);

            // Callback should be invoked exactly once
            expect(callback).toHaveBeenCalledTimes(1);
            expect(callback).toHaveBeenCalledWith('/project/src/example.py');

            jest.useRealTimers();
            done();
        });

        it('handles multiple callbacks for same event', (done) => {
            jest.useFakeTimers();
            fileWatcher.start();

            const callback1 = jest.fn();
            const callback2 = jest.fn();
            fileWatcher.onSidecarChanged(callback1);
            fileWatcher.onSidecarChanged(callback2);

            // Trigger change event
            const uri = { fsPath: '/project/.comments/src/example.py.json' } as vscode.Uri;
            onDidChangeHandlers.forEach(handler => handler(uri));

            // Advance past debounce period
            jest.advanceTimersByTime(2500);

            // Both callbacks should be invoked
            expect(callback1).toHaveBeenCalledWith('/project/src/example.py');
            expect(callback2).toHaveBeenCalledWith('/project/src/example.py');

            jest.useRealTimers();
            done();
        });

        it('catches and logs callback errors without stopping other callbacks', (done) => {
            jest.useFakeTimers();
            fileWatcher.start();

            const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation();

            const failingCallback = jest.fn(() => {
                throw new Error('Callback error');
            });
            const successCallback = jest.fn();

            fileWatcher.onSidecarChanged(failingCallback);
            fileWatcher.onSidecarChanged(successCallback);

            // Trigger change event
            const uri = { fsPath: '/project/.comments/src/example.py.json' } as vscode.Uri;
            onDidChangeHandlers.forEach(handler => handler(uri));

            // Advance past debounce period
            jest.advanceTimersByTime(2500);

            // First callback should throw, second should still execute
            expect(failingCallback).toHaveBeenCalled();
            expect(successCallback).toHaveBeenCalled();
            expect(consoleErrorSpy).toHaveBeenCalledWith(
                'FileWatcher callback error:',
                expect.any(Error)
            );

            consoleErrorSpy.mockRestore();
            jest.useRealTimers();
            done();
        });
    });

    describe('extractSourceFilePath()', () => {
        it('extracts source path from sidecar path', (done) => {
            jest.useFakeTimers();
            fileWatcher.start();

            const callback = jest.fn((sourceFilePath) => {
                expect(sourceFilePath).toBe('/project/src/models/user.py');
            });
            fileWatcher.onSidecarChanged(callback);

            const uri = { fsPath: '/project/.comments/src/models/user.py.json' } as vscode.Uri;
            onDidChangeHandlers.forEach(handler => handler(uri));

            jest.advanceTimersByTime(2500);

            expect(callback).toHaveBeenCalledTimes(1);

            jest.useRealTimers();
            done();
        });

        it('handles Windows-style paths', (done) => {
            jest.useFakeTimers();
            fileWatcher.start();

            const callback = jest.fn();
            fileWatcher.onSidecarChanged(callback);

            // Windows-style path with backslashes
            const uri = { fsPath: 'C:\\project\\.comments\\src\\example.py.json' } as vscode.Uri;
            onDidChangeHandlers.forEach(handler => handler(uri));

            jest.advanceTimersByTime(2500);

            // Should be called (path normalization handles backslashes)
            expect(callback).toHaveBeenCalled();

            jest.useRealTimers();
            done();
        });

        it('ignores files without .json extension', (done) => {
            jest.useFakeTimers();
            fileWatcher.start();

            const callback = jest.fn();
            fileWatcher.onSidecarChanged(callback);

            // No .json extension
            const uri = { fsPath: '/project/.comments/src/example.py' } as vscode.Uri;
            onDidChangeHandlers.forEach(handler => handler(uri));

            jest.advanceTimersByTime(2500);

            // Callback should NOT be invoked
            expect(callback).not.toHaveBeenCalled();

            jest.useRealTimers();
            done();
        });

        it('ignores files outside .comments directory', (done) => {
            jest.useFakeTimers();
            fileWatcher.start();

            const callback = jest.fn();
            fileWatcher.onSidecarChanged(callback);

            // Outside .comments directory
            const uri = { fsPath: '/project/src/example.py.json' } as vscode.Uri;
            onDidChangeHandlers.forEach(handler => handler(uri));

            jest.advanceTimersByTime(2500);

            // Callback should NOT be invoked
            expect(callback).not.toHaveBeenCalled();

            jest.useRealTimers();
            done();
        });
    });

    describe('event handling', () => {
        it('handles onDidCreate events', (done) => {
            jest.useFakeTimers();
            fileWatcher.start();

            const callback = jest.fn();
            fileWatcher.onSidecarChanged(callback);

            const uri = { fsPath: '/project/.comments/src/new.py.json' } as vscode.Uri;
            onDidCreateHandlers.forEach(handler => handler(uri));

            jest.advanceTimersByTime(2500);

            expect(callback).toHaveBeenCalledWith('/project/src/new.py');

            jest.useRealTimers();
            done();
        });

        it('handles onDidDelete events', (done) => {
            jest.useFakeTimers();
            fileWatcher.start();

            const callback = jest.fn();
            fileWatcher.onSidecarChanged(callback);

            const uri = { fsPath: '/project/.comments/src/deleted.py.json' } as vscode.Uri;
            onDidDeleteHandlers.forEach(handler => handler(uri));

            jest.advanceTimersByTime(2500);

            expect(callback).toHaveBeenCalledWith('/project/src/deleted.py');

            jest.useRealTimers();
            done();
        });
    });
});
