import * as vscode from "vscode";
import * as path from "path";
import * as fs from "fs";

/**
 * Opens the DECISIONS.md file in the editor if it exists.
 *
 * This command locates the DECISIONS.md file at the project root
 * and opens it in a text editor. If the file doesn't exist, it shows
 * a notification prompting the user to generate it using the CLI.
 *
 * @param projectRoot - Absolute path to project root (containing .git)
 */
export async function showDecisionsCommand(projectRoot: string): Promise<void> {
  // Construct path to DECISIONS.md (always at project root)
  const decisionsPath = path.join(projectRoot, "DECISIONS.md");

  console.log(`[showDecisions] Looking for: ${decisionsPath}`);

  try {
    // Check if file exists
    if (!fs.existsSync(decisionsPath)) {
      console.log(`[showDecisions] DECISIONS.md not found`);
      vscode.window.showInformationMessage(
        "No DECISIONS.md found. Run 'comment decisions' from the CLI to generate it."
      );
      return;
    }

    // Open file in editor
    const document = await vscode.workspace.openTextDocument(decisionsPath);
    await vscode.window.showTextDocument(document, {
      preview: false, // Open in normal editor, not preview mode
      viewColumn: vscode.ViewColumn.Active,
    });

    console.log(`[showDecisions] Successfully opened DECISIONS.md`);
  } catch (error: any) {
    console.error(`[showDecisions] Error:`, error);
    const errorMessage = error.message || "Unknown error";
    vscode.window.showErrorMessage(
      `Failed to open DECISIONS.md: ${errorMessage}`
    );
  }
}

/**
 * Registers the show decisions command with VSCode.
 *
 * This function should be called during extension activation.
 *
 * @param context - Extension context
 * @param projectRoot - Absolute path to project root
 */
export function registerShowDecisionsCommand(
  context: vscode.ExtensionContext,
  projectRoot: string
): void {
  const command = vscode.commands.registerCommand(
    "file-native-comments.showDecisions",
    () => showDecisionsCommand(projectRoot)
  );

  context.subscriptions.push(command);
  console.log(
    "[showDecisions] Registered command: file-native-comments.showDecisions"
  );
}
