/**
 * Command to reconcile all comment threads across the entire project.
 *
 * Calls the Python CLI `comment reconcile --all --json` and parses the output
 * to show aggregate reconciliation statistics to the user.
 */

import * as vscode from 'vscode';
import * as path from 'path';
import { runCliCommand } from '../utils';

/**
 * Reconcile all comment threads in the project.
 *
 * @param projectRoot Absolute path to project root (containing .git)
 * @param commentProvider CommentProvider instance for reloading comments
 * @returns true if reconciliation succeeded, false otherwise
 */
export async function reconcileAllCommand(
    projectRoot: string,
    commentProvider: any
): Promise<boolean> {
    const confirmation = await vscode.window.showInformationMessage(
        'Reconcile all comment threads in project? This may take a moment for large projects.',
        { modal: true },
        'Reconcile All',
        'Cancel'
    );

    if (confirmation !== 'Reconcile All') {
        return false;
    }

    try {
        const result = await vscode.window.withProgress(
            {
                location: vscode.ProgressLocation.Notification,
                title: 'Reconciling all comment threads...',
                cancellable: false
            },
            async (progress) => {
                progress.report({ increment: 0 });

                console.log(`[reconcileAll] Running CLI command: comment reconcile --all --json`);

                try {
                    const output = await runCliCommand(
                        ['comment', 'reconcile', '--all', '--json'],
                        projectRoot
                    );

                    console.log(`[reconcileAll] CLI output: ${output}`);

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
                        const stderr = error.stderr ? error.stderr.toString().trim() : 'Unknown error';
                        console.error('[reconcileAll] CLI user error:', stderr);
                        throw new Error(`Reconciliation failed: ${stderr}`);
                    } else if (error.status === 2) {
                        const stderr = error.stderr ? error.stderr.toString().trim() : 'Unknown error';
                        console.error('[reconcileAll] CLI system error:', stderr);
                        throw new Error(`System error during reconciliation: ${stderr}`);
                    } else {
                        console.error('[reconcileAll] CLI unknown error:', error.message);
                        throw new Error(`Failed to run reconciliation: ${error.message}`);
                    }
                }
            }
        );

        if (!result.success) {
            return false;
        }

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

        let message: string;
        if (totalThreads === 0) {
            message = `No comment threads found in project.`;
        } else {
            message = `Reconciled ${totalThreads} threads across ${totalFiles} files: ${anchored} anchored, ${drifted} drifted, ${orphaned} orphaned`;
        }

        if (orphaned > 0 || drifted > 0) {
            vscode.window.showWarningMessage(message);
        } else {
            vscode.window.showInformationMessage(message);
        }

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

function isWithinProject(filePath: string, projectRoot: string): boolean {
    const relativePath = path.relative(projectRoot, filePath);
    return !relativePath.startsWith('..') && !path.isAbsolute(relativePath);
}

/**
 * Register the "Reconcile All" command with VSCode.
 */
export function registerReconcileAllCommand(
    context: vscode.ExtensionContext,
    projectRoot: string,
    commentProvider: any
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
