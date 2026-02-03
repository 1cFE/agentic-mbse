import * as vscode from "vscode";
import { execSync } from "child_process";
import * as path from "path";

/**
 * Interface for reconciliation report returned by CLI (--json format)
 */
interface ReconciliationReport {
  file: string;
  renamed: boolean;
  total_threads: number;
  anchored: number;
  drifted: number;
  orphaned: number;
  max_drift: number;
  source_hash_before: string;
  source_hash_after: string;
}

/**
 * Reconciles anchors for the active file by calling the Python CLI.
 *
 * This command runs `comment reconcile <file> --json` and displays
 * the reconciliation results in a notification.
 *
 * @param projectRoot - Absolute path to project root (containing .git)
 */
export async function reconcileFileCommand(projectRoot: string): Promise<void> {
  // Get active editor
  const editor = vscode.window.activeTextEditor;
  if (!editor) {
    vscode.window.showWarningMessage("No active file to reconcile");
    return;
  }

  const filePath = editor.document.uri.fsPath;

  // Validate file is within project
  if (!filePath.startsWith(projectRoot)) {
    vscode.window.showErrorMessage(
      "Cannot reconcile file outside project root"
    );
    return;
  }

  // Compute relative path for display and CLI
  const relativeFilePath = path.relative(projectRoot, filePath);

  try {
    // Build CLI command
    const escapedFilePath = escapeShellArg(filePath);
    const command = `comment reconcile ${escapedFilePath} --json`;

    console.log(`[reconcileFile] Running: ${command}`);
    console.log(`[reconcileFile] Working directory: ${projectRoot}`);

    // Execute CLI command
    const output = execSync(command, {
      cwd: projectRoot,
      encoding: "utf-8",
      maxBuffer: 10 * 1024 * 1024, // 10MB buffer
    });

    console.log(`[reconcileFile] CLI output: ${output}`);

    // Parse JSON output
    let report: ReconciliationReport;
    try {
      report = JSON.parse(output);
    } catch (parseError) {
      console.error(
        `[reconcileFile] Failed to parse CLI output:`,
        parseError
      );
      vscode.window.showErrorMessage(
        `Reconciliation failed: Invalid CLI output (expected JSON)`
      );
      return;
    }

    // Build notification message
    const renameNote = report.renamed ? " (file renamed)" : "";
    const message = `Reconciled ${relativeFilePath}${renameNote}: ${report.anchored} anchored, ${report.drifted} drifted, ${report.orphaned} orphaned`;

    if (report.drifted > 0 || report.orphaned > 0) {
      vscode.window.showWarningMessage(message);
    } else {
      vscode.window.showInformationMessage(message);
    }

    // Note: File watcher will trigger UI update automatically (2-second debounce)
    // No need to manually reload comments here
  } catch (error: any) {
    console.error(`[reconcileFile] Error:`, error);

    // Handle specific error cases
    if (error.status === 1) {
      // Exit code 1 = user error (e.g., no comments found)
      const errorMessage = error.stderr?.toString() || error.message || "";
      if (errorMessage.includes("No comments found")) {
        vscode.window.showInformationMessage(
          `No comments found for ${relativeFilePath}`
        );
      } else {
        vscode.window.showErrorMessage(
          `Reconciliation failed: ${errorMessage.trim()}`
        );
      }
    } else if (error.status === 2) {
      // Exit code 2 = system error
      const errorMessage = error.stderr?.toString() || error.message || "";
      vscode.window.showErrorMessage(
        `Reconciliation failed (system error): ${errorMessage.trim()}`
      );
    } else {
      // Unknown error
      const errorMessage = error.stderr?.toString() || error.message || "";
      vscode.window.showErrorMessage(
        `Reconciliation failed: ${errorMessage.trim() || "Unknown error"}`
      );
    }
  }
}

/**
 * Escapes a file path for use in a shell command.
 *
 * This function escapes:
 * - Backslashes (\\)
 * - Double quotes (")
 * - Single quotes (')
 * - Spaces
 * - Special shell characters ($, `, !, etc.)
 *
 * @param arg - The argument to escape
 * @returns The escaped argument wrapped in double quotes
 */
function escapeShellArg(arg: string): string {
  // Escape backslashes first, then double quotes
  let escaped = arg.replace(/\\/g, "\\\\").replace(/"/g, '\\"');

  // Wrap in double quotes
  return `"${escaped}"`;
}

/**
 * Registers the reconcile file command with VSCode.
 *
 * This function should be called during extension activation.
 *
 * @param context - Extension context
 * @param projectRoot - Absolute path to project root
 */
export function registerReconcileFileCommand(
  context: vscode.ExtensionContext,
  projectRoot: string
): void {
  const command = vscode.commands.registerCommand(
    "file-native-comments.reconcileFile",
    () => reconcileFileCommand(projectRoot)
  );

  context.subscriptions.push(command);
  console.log(
    "[reconcileFile] Registered command: file-native-comments.reconcileFile"
  );
}
