/**
 * Tests for Conflict Detection and Resolution
 *
 * Verifies that optimistic concurrency control works correctly per specs/concurrency.md REQ-4.
 */

import * as fs from 'fs';
import * as path from 'path';
import * as vscode from 'vscode';
import { checkForConflict, promptUserForConflictResolution, handleConflictCheck, ConflictResolution } from './conflictHandler';
import { readSidecar } from './sidecar';

// Mock dependencies
jest.mock('./sidecar');
jest.mock('vscode');

const mockedReadSidecar = readSidecar as jest.MockedFunction<typeof readSidecar>;
const mockedShowWarningMessage = vscode.window.showWarningMessage as jest.MockedFunction<typeof vscode.window.showWarningMessage>;

describe('conflictHandler', () => {
    const projectRoot = '/home/user/project';
    const sourcePath = '/home/user/project/src/model.py';
    const relativePath = 'src/model.py';

    beforeEach(() => {
        jest.clearAllMocks();
    });

    describe('checkForConflict', () => {
        it('returns no conflict when sidecar does not exist', () => {
            mockedReadSidecar.mockReturnValue(null);

            const result = checkForConflict(sourcePath, projectRoot, 'sha256:abc123');

            expect(result.hasConflict).toBe(false);
            expect(result.onDiskSidecar).toBeNull();
            expect(result.error).toBeNull();
        });

        it('returns no conflict when expected hash is null', () => {
            const sidecar = {
                source_file: relativePath,
                source_hash: 'sha256:abc123',
                schema_version: '1.0',
                threads: []
            };
            mockedReadSidecar.mockReturnValue(sidecar);

            const result = checkForConflict(sourcePath, projectRoot, null);

            expect(result.hasConflict).toBe(false);
            expect(result.onDiskSidecar).toEqual(sidecar);
            expect(result.error).toBeNull();
        });

        it('returns no conflict when hashes match', () => {
            const sidecar = {
                source_file: relativePath,
                source_hash: 'sha256:abc123',
                schema_version: '1.0',
                threads: []
            };
            mockedReadSidecar.mockReturnValue(sidecar);

            const result = checkForConflict(sourcePath, projectRoot, 'sha256:abc123');

            expect(result.hasConflict).toBe(false);
            expect(result.onDiskSidecar).toEqual(sidecar);
            expect(result.error).toBeNull();
        });

        it('returns conflict when hashes differ', () => {
            const sidecar = {
                source_file: relativePath,
                source_hash: 'sha256:def456',
                schema_version: '1.0',
                threads: []
            };
            mockedReadSidecar.mockReturnValue(sidecar);

            const result = checkForConflict(sourcePath, projectRoot, 'sha256:abc123');

            expect(result.hasConflict).toBe(true);
            expect(result.onDiskSidecar).toEqual(sidecar);
            expect(result.error).toBeNull();
        });

        it('handles read errors gracefully', () => {
            mockedReadSidecar.mockImplementation(() => {
                throw new Error('File read error');
            });

            const result = checkForConflict(sourcePath, projectRoot, 'sha256:abc123');

            expect(result.hasConflict).toBe(false);
            expect(result.onDiskSidecar).toBeNull();
            expect(result.error).toBe('File read error');
        });

        it('handles non-Error exceptions', () => {
            mockedReadSidecar.mockImplementation(() => {
                throw 'string error';
            });

            const result = checkForConflict(sourcePath, projectRoot, 'sha256:abc123');

            expect(result.hasConflict).toBe(false);
            expect(result.onDiskSidecar).toBeNull();
            expect(result.error).toBe('Unknown error');
        });
    });

    describe('promptUserForConflictResolution', () => {
        it('returns RELOAD when user clicks Reload', async () => {
            mockedShowWarningMessage.mockResolvedValue('Reload' as any);

            const resolution = await promptUserForConflictResolution(relativePath);

            expect(resolution).toBe(ConflictResolution.RELOAD);
            expect(mockedShowWarningMessage).toHaveBeenCalledWith(
                `The comment file for "src/model.py" was modified externally. What would you like to do?`,
                { modal: true },
                'Reload',
                'Overwrite',
                'Cancel'
            );
        });

        it('returns OVERWRITE when user clicks Overwrite', async () => {
            mockedShowWarningMessage.mockResolvedValue('Overwrite' as any);

            const resolution = await promptUserForConflictResolution(relativePath);

            expect(resolution).toBe(ConflictResolution.OVERWRITE);
        });

        it('returns CANCEL when user clicks Cancel', async () => {
            mockedShowWarningMessage.mockResolvedValue('Cancel' as any);

            const resolution = await promptUserForConflictResolution(relativePath);

            expect(resolution).toBe(ConflictResolution.CANCEL);
        });

        it('returns CANCEL when user dismisses dialog', async () => {
            mockedShowWarningMessage.mockResolvedValue(undefined as any);

            const resolution = await promptUserForConflictResolution(relativePath);

            expect(resolution).toBe(ConflictResolution.CANCEL);
        });

        it('logs warning when user chooses Overwrite', async () => {
            const consoleWarnSpy = jest.spyOn(console, 'warn').mockImplementation();
            mockedShowWarningMessage.mockResolvedValue('Overwrite' as any);

            await promptUserForConflictResolution(relativePath);

            expect(consoleWarnSpy).toHaveBeenCalledWith(
                'User chose to overwrite external changes for src/model.py'
            );
            consoleWarnSpy.mockRestore();
        });
    });

    describe('handleConflictCheck', () => {
        it('returns OVERWRITE when no conflict detected', async () => {
            mockedReadSidecar.mockReturnValue({
                source_file: relativePath,
                source_hash: 'sha256:abc123',
                schema_version: '1.0',
                threads: []
            });

            const resolution = await handleConflictCheck(sourcePath, projectRoot, 'sha256:abc123');

            expect(resolution).toBe(ConflictResolution.OVERWRITE);
            expect(mockedShowWarningMessage).not.toHaveBeenCalled();
        });

        it('returns OVERWRITE when sidecar does not exist', async () => {
            mockedReadSidecar.mockReturnValue(null);

            const resolution = await handleConflictCheck(sourcePath, projectRoot, 'sha256:abc123');

            expect(resolution).toBe(ConflictResolution.OVERWRITE);
            expect(mockedShowWarningMessage).not.toHaveBeenCalled();
        });

        it('returns OVERWRITE when expected hash is null', async () => {
            mockedReadSidecar.mockReturnValue({
                source_file: relativePath,
                source_hash: 'sha256:abc123',
                schema_version: '1.0',
                threads: []
            });

            const resolution = await handleConflictCheck(sourcePath, projectRoot, null);

            expect(resolution).toBe(ConflictResolution.OVERWRITE);
            expect(mockedShowWarningMessage).not.toHaveBeenCalled();
        });

        it('prompts user when conflict detected', async () => {
            mockedReadSidecar.mockReturnValue({
                source_file: relativePath,
                source_hash: 'sha256:def456',
                schema_version: '1.0',
                threads: []
            });
            mockedShowWarningMessage.mockResolvedValue('Reload' as any);

            const resolution = await handleConflictCheck(sourcePath, projectRoot, 'sha256:abc123');

            expect(resolution).toBe(ConflictResolution.RELOAD);
            expect(mockedShowWarningMessage).toHaveBeenCalled();
        });

        it('returns user choice when conflict detected', async () => {
            mockedReadSidecar.mockReturnValue({
                source_file: relativePath,
                source_hash: 'sha256:def456',
                schema_version: '1.0',
                threads: []
            });
            mockedShowWarningMessage.mockResolvedValue('Overwrite' as any);

            const resolution = await handleConflictCheck(sourcePath, projectRoot, 'sha256:abc123');

            expect(resolution).toBe(ConflictResolution.OVERWRITE);
        });

        it('logs conflict detection', async () => {
            const consoleLogSpy = jest.spyOn(console, 'log').mockImplementation();
            mockedReadSidecar.mockReturnValue({
                source_file: relativePath,
                source_hash: 'sha256:def456',
                schema_version: '1.0',
                threads: []
            });
            mockedShowWarningMessage.mockResolvedValue('Cancel' as any);

            await handleConflictCheck(sourcePath, projectRoot, 'sha256:abc123');

            expect(consoleLogSpy).toHaveBeenCalledWith(
                expect.stringContaining('Conflict detected')
            );
            consoleLogSpy.mockRestore();
        });

        it('extracts relative path for display', async () => {
            mockedReadSidecar.mockReturnValue({
                source_file: relativePath,
                source_hash: 'sha256:def456',
                schema_version: '1.0',
                threads: []
            });
            mockedShowWarningMessage.mockResolvedValue('Cancel' as any);

            await handleConflictCheck(sourcePath, projectRoot, 'sha256:abc123');

            expect(mockedShowWarningMessage).toHaveBeenCalledWith(
                expect.stringContaining('src/model.py'),
                expect.any(Object),
                'Reload',
                'Overwrite',
                'Cancel'
            );
        });

        it('handles absolute paths outside project gracefully', async () => {
            const outsidePath = '/other/project/file.py';
            mockedReadSidecar.mockReturnValue({
                source_file: outsidePath,
                source_hash: 'sha256:def456',
                schema_version: '1.0',
                threads: []
            });
            mockedShowWarningMessage.mockResolvedValue('Cancel' as any);

            await handleConflictCheck(outsidePath, projectRoot, 'sha256:abc123');

            expect(mockedShowWarningMessage).toHaveBeenCalledWith(
                expect.stringContaining(outsidePath),
                expect.any(Object),
                'Reload',
                'Overwrite',
                'Cancel'
            );
        });

        it('treats read errors as no conflict', async () => {
            const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation();
            mockedReadSidecar.mockImplementation(() => {
                throw new Error('File read error');
            });

            const resolution = await handleConflictCheck(sourcePath, projectRoot, 'sha256:abc123');

            expect(resolution).toBe(ConflictResolution.OVERWRITE);
            expect(consoleErrorSpy).toHaveBeenCalledWith(
                expect.stringContaining('Conflict check error')
            );
            consoleErrorSpy.mockRestore();
        });
    });
});
