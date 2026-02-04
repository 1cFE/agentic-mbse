import * as vscode from "vscode";
import * as path from "path";
import { runCliCommand } from "../utils";

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
 * @param projectRoot - Absolute path to project root (containing .git)
 */
export async function reconcileFileCommand(projectRoot: string): Promise<void> {
  const editor = vscode.window.activeTextEditor;
  if (!editor) {
    vscode.window.showWarningMessage("No active file to reconcile");
    return;
  }

  const filePath = editor.document.uri.fsPath;

  if (!filePath.startsWith(projectRoot)) {
    vscode.window.showErrorMessage(
      "Cannot reconcile file outside project root"
    );
    return;
  }

  const relativeFilePath = path.relative(projectRoot, filePath);

  try {
    console.log(`[reconcileFile] Running: comment reconcile ${filePath} --json`);
    console.log(`[reconcileFile] Working directory: ${projectRoot}`);

    const output = await runCliCommand(
      ["comment", "reconcile", filePath, "--json"],
      projectRoot
    );

    console.log(`[reconcileFile] CLI output: ${output}`);

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

    const renameNote = report.renamed ? " (file renamed)" : "";
    const message = `Reconciled ${relativeFilePath}${renameNote}: ${report.anchored} anchored, ${report.drifted} drifted, ${report.orphaned} orphaned`;

    if (report.drifted > 0 || report.orphaned > 0) {
      vscode.window.showWarningMessage(message);
    } else {
      vscode.window.showInformationMessage(message);
    }
  } catch (error: any) {
    console.error(`[reconcileFile] Error:`, error);

    if (error.status === 1) {
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
      const errorMessage = error.stderr?.toString() || error.message || "";
      vscode.window.showErrorMessage(
        `Reconciliation failed (system error): ${errorMessage.trim()}`
      );
    } else {
      const errorMessage = error.stderr?.toString() || error.message || "";
      vscode.window.showErrorMessage(
        `Reconciliation failed: ${errorMessage.trim() || "Unknown error"}`
      );
    }
  }
}

/**
 * Registers the reconcile file command with VSCode.
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
