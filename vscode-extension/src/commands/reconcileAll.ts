/**
 * Command to reconcile all comment threads across the entire project.
 *
 * Calls the Python CLI `comment reconcile --all --json` and parses the output
 * to show aggregate reconciliation statistics to the user.
 */

import * as vscode from 'vscode';
import { execSync } from 'child_process';
import * as path from 'path';

/**
 * Reconcile all comment threads in the project.
 *
 * Workflow:
 * 1. Validate project root exists
 * 2. Show confirmation dialog (operation may take time)
 * 3. Execute CLI with progress notification
 * 4. Parse JSON output for statistics
 * 5. Show summary notification
 * 6. Reload comments for all open editors
 *
 * @param projectRoot Absolute path to project root (containing .git)
 * @param commentProvider CommentProvider instance for reloading comments
 * @returns true if reconciliation succeeded, false otherwise
 */
export async function reconcileAllCommand(
    projectRoot: string,
    commentProvider: any // Type: CommentProvider, but avoid circular dependency
): Promise<boolean> {
    // Confirm with user before starting potentially long operation
    const confirmation = await vscode.window.showInformationMessage(
        'Reconcile all comment threads in project? This may take a moment for large projects.',
        { modal: true },
        'Reconcile All',
        'Cancel'
    );

    if (confirmation !== 'Reconcile All') {
        return false; // User cancelled
    }

    // Execute reconciliation with progress notification
    try {
        const result = await vscode.window.withProgress(
            {
                location: vscode.ProgressLocation.Notification,
                title: 'Reconciling all comment threads...',
                cancellable: false
            },
            async (progress) => {
                progress.report({ increment: 0 });

                // Build CLI command
                const cliCommand = `comment reconcile --all --json`;
                console.log(`[reconcileAll] Running CLI command: ${cliCommand}`);

                try {
                    // Execute CLI command synchronously (blocking)
                    const output = execSync(cliCommand, {
                        cwd: projectRoot,
                        encoding: 'utf-8',
                        maxBuffer: 10 * 1024 * 1024 // 10MB buffer for large outputs
                    });

                    console.log(`[reconcileAll] CLI output: ${output}`);

                    // Parse JSON output
                    let jsonData: any;
                    try {
                        jsonData = JSON.parse(output);
                    } catch (parseError: any) {
                        console.error('[reconcileAll] Failed to parse CLI output as JSON:', parseError.message);
                        console.error('[reconcileAll] Raw output:', output);
                        throw new Error(`Failed to parse reconciliation output: ${parseError.message}`);
                    }

                    progress.report({ increment: 100 });
                    return { success: true, data: jsonData };
                } catch (error: any) {
                    if (error.status === 1) {
                        // User error (exit code 1)
                        const stderr = error.stderr ? error.stderr.toString().trim() : 'Unknown error';
                        console.error('[reconcileAll] CLI user error:', stderr);
                        throw new Error(`Reconciliation failed: ${stderr}`);
                    } else if (error.status === 2) {
                        // System error (exit code 2)
                        const stderr = error.stderr ? error.stderr.toString().trim() : 'Unknown error';
                        console.error('[reconcileAll] CLI system error:', stderr);
                        throw new Error(`System error during reconciliation: ${stderr}`);
                    } else {
                        // Unknown error
                        console.error('[reconcileAll] CLI unknown error:', error.message);
                        throw new Error(`Failed to run reconciliation: ${error.message}`);
                    }
                }
            }
        );

        if (!result.success) {
            return false;
        }

        // Extract statistics from JSON output
        const stats = result.data;
        const totalFiles = stats.total_files || 0;
        const totalThreads = stats.total_threads || 0;
        const anchored = stats.anchored || 0;
        const drifted = stats.drifted || 0;
        const orphaned = stats.orphaned || 0;

        console.log(`[reconcileAll] Reconciliation complete:`, {
            totalFiles,
            totalThreads,
            anchored,
            drifted,
            orphaned
        });

        // Show summary notification
        let message: string;
        if (totalThreads === 0) {
            message = `No comment threads found in project.`;
        } else {
            message = `Reconciled ${totalThreads} threads across ${totalFiles} files: ${anchored} anchored, ${drifted} drifted, ${orphaned} orphaned`;
        }

        // Choose notification type based on results
        if (orphaned > 0 || drifted > 0) {
            vscode.window.showWarningMessage(message);
        } else {
            vscode.window.showInformationMessage(message);
        }

        // Reload comments for all open editors
        console.log('[reconcileAll] Reloading comments for all open editors');
        for (const editor of vscode.window.visibleTextEditors) {
            const document = editor.document;
            if (document.uri.scheme === 'file' && isWithinProject(document.uri.fsPath, projectRoot)) {
                await commentProvider.loadCommentsForDocument(document);
            }
        }

        return true;
    } catch (error: any) {
        console.error('[reconcileAll] Error:', error);
        vscode.window.showErrorMessage(error.message || 'Failed to reconcile comment threads');
        return false;
    }
}

/**
 * Check if a file path is within the project root.
 *
 * @param filePath Absolute file path
 * @param projectRoot Absolute project root path
 * @returns true if filePath is within projectRoot
 */
function isWithinProject(filePath: string, projectRoot: string): boolean {
    const relativePath = path.relative(projectRoot, filePath);
    return !relativePath.startsWith('..') && !path.isAbsolute(relativePath);
}

/**
 * Register the "Reconcile All" command with VSCode.
 *
 * @param context Extension context for subscriptions
 * @param projectRoot Absolute path to project root
 * @param commentProvider CommentProvider instance
 */
export function registerReconcileAllCommand(
    context: vscode.ExtensionContext,
    projectRoot: string,
    commentProvider: any // Type: CommentProvider
): void {
    const command = vscode.commands.registerCommand(
        'file-native-comments.reconcileAll',
        async () => {
            await reconcileAllCommand(projectRoot, commentProvider);
        }
    );
    context.subscriptions.push(command);
    console.log('[reconcileAll] Command registered: file-native-comments.reconcileAll');
}
