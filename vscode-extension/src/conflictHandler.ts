/**
 * Conflict Detection and Resolution
 *
 * Implements optimistic concurrency control for sidecar files per specs/concurrency.md REQ-4.
 * Detects when sidecar file was modified externally (e.g., by CLI or another process) and
 * prompts user to resolve the conflict.
 *
 * Required by: specs/concurrency.md AC-2
 */

import * as vscode from 'vscode';
import { readSidecar, SidecarFile } from './sidecar';

/**
 * Result of conflict detection check.
 */
export interface ConflictCheckResult {
    /**
     * True if source_hash differs between in-memory and on-disk versions.
     */
    hasConflict: boolean;

    /**
     * On-disk sidecar data (null if file doesn't exist or can't be read).
     */
    onDiskSidecar: SidecarFile | null;

    /**
     * Error message if read failed (null on success).
     */
    error: string | null;
}

/**
 * User's choice for resolving conflict.
 */
export enum ConflictResolution {
    /**
     * Reload from disk, discard in-memory changes, retry operation with fresh data.
     */
    RELOAD = "reload",

    /**
     * Proceed with write, overwriting on-disk changes (data loss risk).
     */
    OVERWRITE = "overwrite",

    /**
     * Cancel operation, no changes made.
     */
    CANCEL = "cancel"
}

/**
 * Checks if sidecar file has been modified externally since it was last read.
 *
 * Workflow:
 * 1. Read sidecar from disk
 * 2. Compare source_hash with in-memory version
 * 3. Return conflict status and on-disk data
 *
 * Note: This implementation uses Option B from task notes - reads sidecar on each check
 * rather than maintaining in-memory cache. Simpler and avoids state management issues.
 *
 * @param sourcePath Absolute path to source file
 * @param projectRoot Absolute path to project root
 * @param expectedHash Expected source_hash from in-memory data (may be null if unknown)
 * @returns Conflict check result with status and on-disk data
 */
export function checkForConflict(
    sourcePath: string,
    projectRoot: string,
    expectedHash: string | null
): ConflictCheckResult {
    try {
        // Read current sidecar from disk
        const onDiskSidecar = readSidecar(sourcePath, projectRoot);

        if (!onDiskSidecar) {
            // Sidecar doesn't exist - no conflict possible
            return {
                hasConflict: false,
                onDiskSidecar: null,
                error: null
            };
        }

        // If we don't have an expected hash, assume no conflict (first write)
        if (expectedHash === null) {
            return {
                hasConflict: false,
                onDiskSidecar,
                error: null
            };
        }

        // Compare hashes - conflict if they differ
        const hasConflict = onDiskSidecar.source_hash !== expectedHash;

        return {
            hasConflict,
            onDiskSidecar,
            error: null
        };
    } catch (error) {
        // Read error - treat as no conflict but log the error
        console.error('Error reading sidecar for conflict check:', error);
        return {
            hasConflict: false,
            onDiskSidecar: null,
            error: error instanceof Error ? error.message : 'Unknown error'
        };
    }
}

/**
 * Prompts user to resolve a conflict between in-memory and on-disk sidecar versions.
 *
 * Shows modal warning dialog with three options:
 * - "Reload": Discard in-memory changes, reload from disk, retry operation
 * - "Overwrite": Proceed with write (warns about data loss)
 * - "Cancel": Abort operation
 *
 * Required by: specs/concurrency.md REQ-4 and AC-2
 *
 * @param sourcePath Relative path to source file (for display in message)
 * @returns User's choice (Reload, Overwrite, or Cancel)
 */
export async function promptUserForConflictResolution(
    sourcePath: string
): Promise<ConflictResolution> {
    const message = `The comment file for "${sourcePath}" was modified externally. What would you like to do?`;

    const choice = await vscode.window.showWarningMessage(
        message,
        { modal: true },
        'Reload',
        'Overwrite',
        'Cancel'
    );

    switch (choice) {
        case 'Reload':
            return ConflictResolution.RELOAD;
        case 'Overwrite':
            console.warn(`User chose to overwrite external changes for ${sourcePath}`);
            return ConflictResolution.OVERWRITE;
        case 'Cancel':
        default:
            return ConflictResolution.CANCEL;
    }
}

/**
 * Handles conflict detection and resolution workflow for write operations.
 *
 * Integrated workflow:
 * 1. Check for conflict (compare source_hash)
 * 2. If no conflict, return success (caller proceeds with write)
 * 3. If conflict, prompt user for resolution
 * 4. Return user's choice (caller handles reload/overwrite/cancel logic)
 *
 * Usage example:
 * ```typescript
 * const resolution = await handleConflictCheck(sourcePath, projectRoot, expectedHash);
 * if (resolution === ConflictResolution.CANCEL) {
 *     vscode.window.showInformationMessage('Operation cancelled');
 *     return;
 * }
 * if (resolution === ConflictResolution.RELOAD) {
 *     // Reload sidecar and retry operation
 *     await commentProvider.loadCommentsForDocument(document);
 *     return; // Exit and let user retry manually
 * }
 * // ConflictResolution.OVERWRITE or no conflict - proceed with write
 * ```
 *
 * @param sourcePath Absolute path to source file
 * @param projectRoot Absolute path to project root
 * @param expectedHash Expected source_hash (null if unknown)
 * @returns Resolution strategy (OVERWRITE if no conflict, user choice if conflict)
 */
export async function handleConflictCheck(
    sourcePath: string,
    projectRoot: string,
    expectedHash: string | null
): Promise<ConflictResolution> {
    // Check for conflict
    const conflictCheck = checkForConflict(sourcePath, projectRoot, expectedHash);

    if (conflictCheck.error) {
        console.error(`Conflict check error: ${conflictCheck.error}`);
        // Treat read errors as "no conflict" and let write attempt proceed
        // (write will fail with appropriate error if file is actually inaccessible)
        return ConflictResolution.OVERWRITE;
    }

    if (!conflictCheck.hasConflict) {
        // No conflict - proceed with write
        return ConflictResolution.OVERWRITE;
    }

    // Conflict detected - prompt user
    console.log(`Conflict detected for ${sourcePath}: hash mismatch`);

    // Extract relative path for display
    const relativePath = sourcePath.startsWith(projectRoot)
        ? sourcePath.substring(projectRoot.length + 1)
        : sourcePath;

    return await promptUserForConflictResolution(relativePath);
}
