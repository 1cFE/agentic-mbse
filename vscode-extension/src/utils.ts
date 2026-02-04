/**
 * Shared utilities for the File-Native Comment System extension.
 *
 * Centralizes common patterns used across command files:
 * - Thread metadata extraction via WeakMap
 * - Author resolution
 * - Async CLI command execution (no shell)
 */

import * as vscode from 'vscode';
import { execFile } from 'child_process';
import { promisify } from 'util';

const execFileAsync = promisify(execFile);

/**
 * Metadata stored for each VS Code CommentThread via WeakMap.
 */
export interface ThreadMetadata {
    threadId: string;
    sourceHash: string;
    health: string;
    driftDistance: number;
    status: string;
    hasDecision: boolean;
}

/**
 * WeakMap storing thread metadata keyed by VS Code CommentThread instances.
 *
 * This replaces the previous pattern of storing JSON in contextValue.
 * contextValue is now a simple string ("open" or "resolved") for menu when-clause matching.
 */
export const threadMetadataMap = new WeakMap<vscode.CommentThread, ThreadMetadata>();

/**
 * Extracts the thread ID from a CommentThread.
 *
 * Reads from the WeakMap first (new approach), then falls back to
 * parsing JSON contextValue (backward compatibility).
 *
 * @param thread The VS Code CommentThread
 * @returns The thread ID string, or null if not found
 */
export function extractThreadId(thread: vscode.CommentThread): string | null {
    const metadata = threadMetadataMap.get(thread);
    if (metadata) {
        return metadata.threadId;
    }

    // Fallback: parse JSON contextValue (backward compatibility)
    try {
        if (!thread.contextValue) {
            return null;
        }
        const context = JSON.parse(thread.contextValue);
        return context.thread_id || null;
    } catch {
        return null;
    }
}

/**
 * Extracts the source hash from a CommentThread.
 *
 * Reads from the WeakMap first, then falls back to parsing JSON contextValue.
 *
 * @param thread The VS Code CommentThread
 * @returns The source hash string, or null if not found
 */
export function extractSourceHash(thread: vscode.CommentThread): string | null {
    const metadata = threadMetadataMap.get(thread);
    if (metadata) {
        return metadata.sourceHash;
    }

    // Fallback: parse JSON contextValue
    try {
        if (!thread.contextValue) {
            return null;
        }
        const context = JSON.parse(thread.contextValue);
        return context.source_hash || null;
    } catch {
        return null;
    }
}

/**
 * Gets the current user's author name for comments.
 *
 * @returns Username from VS Code environment, or 'vscode-user' fallback
 */
export function getAuthor(): string {
    return (vscode.env as any).username || 'vscode-user';
}

/**
 * Runs a CLI command asynchronously using execFile (no shell).
 *
 * Uses execFile with an args array, which avoids shell injection entirely.
 * No escaping of special characters is needed.
 *
 * @param args Array of command arguments (first element is the command)
 * @param projectRoot Working directory for the command
 * @param opts Optional settings
 * @returns Promise resolving to stdout string
 * @throws Error with stderr/message on failure
 */
export async function runCliCommand(
    args: string[],
    projectRoot: string,
    opts?: { maxBuffer?: number }
): Promise<string> {
    const [command, ...rest] = args;
    const { stdout } = await execFileAsync(command, rest, {
        cwd: projectRoot,
        encoding: 'utf-8',
        maxBuffer: opts?.maxBuffer ?? 10 * 1024 * 1024
    });
    return stdout;
}
