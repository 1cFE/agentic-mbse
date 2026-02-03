import * as vscode from "vscode";
import {
  showDecisionsCommand,
  registerShowDecisionsCommand,
} from "./showDecisions";
import * as fs from "fs";
import * as path from "path";

// Mock fs module
jest.mock("fs");
const mockExistsSync = fs.existsSync as jest.MockedFunction<
  typeof fs.existsSync
>;

// Mock vscode.workspace
const mockOpenTextDocument = jest.fn();
(vscode.workspace as any).openTextDocument = mockOpenTextDocument;

// Mock vscode.window
const mockShowTextDocument = jest.fn();
(vscode.window as any).showTextDocument = mockShowTextDocument;

describe("showDecisionsCommand", () => {
  const projectRoot = "/home/user/project";
  const decisionsPath = path.join(projectRoot, "DECISIONS.md");

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("should open DECISIONS.md when file exists", async () => {
    // Mock file exists
    mockExistsSync.mockReturnValue(true);

    // Mock document
    const mockDocument = {
      uri: { fsPath: decisionsPath },
      getText: () => "# Decisions\n\nSome decisions here...",
    };
    mockOpenTextDocument.mockResolvedValue(mockDocument);
    mockShowTextDocument.mockResolvedValue(undefined);

    await showDecisionsCommand(projectRoot);

    // Verify file existence check
    expect(mockExistsSync).toHaveBeenCalledWith(decisionsPath);

    // Verify document opened
    expect(mockOpenTextDocument).toHaveBeenCalledWith(decisionsPath);

    // Verify document shown in editor
    expect(mockShowTextDocument).toHaveBeenCalledWith(mockDocument, {
      preview: false,
      viewColumn: vscode.ViewColumn.Active,
    });

    // Should not show any error notifications
    expect(vscode.window.showErrorMessage).not.toHaveBeenCalled();
    expect(vscode.window.showInformationMessage).not.toHaveBeenCalled();
  });

  it("should show info notification when DECISIONS.md does not exist", async () => {
    // Mock file does not exist
    mockExistsSync.mockReturnValue(false);

    await showDecisionsCommand(projectRoot);

    // Verify file existence check
    expect(mockExistsSync).toHaveBeenCalledWith(decisionsPath);

    // Should show informative message
    expect(vscode.window.showInformationMessage).toHaveBeenCalledWith(
      "No DECISIONS.md found. Run 'comment decisions' from the CLI to generate it."
    );

    // Should not attempt to open file
    expect(mockOpenTextDocument).not.toHaveBeenCalled();
    expect(mockShowTextDocument).not.toHaveBeenCalled();
  });

  it("should show error notification when file cannot be opened", async () => {
    // Mock file exists
    mockExistsSync.mockReturnValue(true);

    // Mock error when opening document
    const error = new Error("Permission denied");
    mockOpenTextDocument.mockRejectedValue(error);

    await showDecisionsCommand(projectRoot);

    // Verify file existence check
    expect(mockExistsSync).toHaveBeenCalledWith(decisionsPath);

    // Verify attempt to open document
    expect(mockOpenTextDocument).toHaveBeenCalledWith(decisionsPath);

    // Should show error notification
    expect(vscode.window.showErrorMessage).toHaveBeenCalledWith(
      "Failed to open DECISIONS.md: Permission denied"
    );

    // Should not show document
    expect(mockShowTextDocument).not.toHaveBeenCalled();
  });

  it("should show error notification when showTextDocument fails", async () => {
    // Mock file exists
    mockExistsSync.mockReturnValue(true);

    // Mock successful document opening
    const mockDocument = {
      uri: { fsPath: decisionsPath },
      getText: () => "# Decisions",
    };
    mockOpenTextDocument.mockResolvedValue(mockDocument);

    // Mock error when showing document
    const error = new Error("Editor error");
    mockShowTextDocument.mockRejectedValue(error);

    await showDecisionsCommand(projectRoot);

    // Verify file existence check
    expect(mockExistsSync).toHaveBeenCalledWith(decisionsPath);

    // Verify attempt to open and show document
    expect(mockOpenTextDocument).toHaveBeenCalledWith(decisionsPath);
    expect(mockShowTextDocument).toHaveBeenCalledWith(mockDocument, {
      preview: false,
      viewColumn: vscode.ViewColumn.Active,
    });

    // Should show error notification
    expect(vscode.window.showErrorMessage).toHaveBeenCalledWith(
      "Failed to open DECISIONS.md: Editor error"
    );
  });

  it("should handle error without message", async () => {
    // Mock file exists
    mockExistsSync.mockReturnValue(true);

    // Mock error without message
    const error = {};
    mockOpenTextDocument.mockRejectedValue(error);

    await showDecisionsCommand(projectRoot);

    // Should show error notification with generic message
    expect(vscode.window.showErrorMessage).toHaveBeenCalledWith(
      "Failed to open DECISIONS.md: Unknown error"
    );
  });

  it("should construct correct path for DECISIONS.md", async () => {
    // Mock file exists
    mockExistsSync.mockReturnValue(true);

    const mockDocument = { uri: { fsPath: decisionsPath } };
    mockOpenTextDocument.mockResolvedValue(mockDocument);
    mockShowTextDocument.mockResolvedValue(undefined);

    await showDecisionsCommand(projectRoot);

    // Verify path construction
    const expectedPath = path.join(projectRoot, "DECISIONS.md");
    expect(mockExistsSync).toHaveBeenCalledWith(expectedPath);
    expect(mockOpenTextDocument).toHaveBeenCalledWith(expectedPath);
  });

  it("should work with different project roots", async () => {
    const differentRoot = "/opt/projects/my-project";
    const differentDecisionsPath = path.join(differentRoot, "DECISIONS.md");

    // Mock file exists
    mockExistsSync.mockReturnValue(true);

    const mockDocument = { uri: { fsPath: differentDecisionsPath } };
    mockOpenTextDocument.mockResolvedValue(mockDocument);
    mockShowTextDocument.mockResolvedValue(undefined);

    await showDecisionsCommand(differentRoot);

    // Verify correct path used
    expect(mockExistsSync).toHaveBeenCalledWith(differentDecisionsPath);
    expect(mockOpenTextDocument).toHaveBeenCalledWith(differentDecisionsPath);
  });

  it("should log file path to console", async () => {
    const consoleLogSpy = jest.spyOn(console, "log").mockImplementation();

    // Mock file exists
    mockExistsSync.mockReturnValue(true);

    const mockDocument = { uri: { fsPath: decisionsPath } };
    mockOpenTextDocument.mockResolvedValue(mockDocument);
    mockShowTextDocument.mockResolvedValue(undefined);

    await showDecisionsCommand(projectRoot);

    expect(consoleLogSpy).toHaveBeenCalledWith(
      expect.stringContaining("[showDecisions] Looking for:")
    );
    expect(consoleLogSpy).toHaveBeenCalledWith(
      expect.stringContaining("[showDecisions] Successfully opened DECISIONS.md")
    );

    consoleLogSpy.mockRestore();
  });

  it("should log when file not found", async () => {
    const consoleLogSpy = jest.spyOn(console, "log").mockImplementation();

    // Mock file does not exist
    mockExistsSync.mockReturnValue(false);

    await showDecisionsCommand(projectRoot);

    expect(consoleLogSpy).toHaveBeenCalledWith(
      expect.stringContaining("[showDecisions] DECISIONS.md not found")
    );

    consoleLogSpy.mockRestore();
  });

  it("should log errors to console", async () => {
    const consoleErrorSpy = jest.spyOn(console, "error").mockImplementation();

    // Mock file exists
    mockExistsSync.mockReturnValue(true);

    // Mock error
    const error = new Error("Test error");
    mockOpenTextDocument.mockRejectedValue(error);

    await showDecisionsCommand(projectRoot);

    expect(consoleErrorSpy).toHaveBeenCalledWith(
      expect.stringContaining("[showDecisions] Error:"),
      error
    );

    consoleErrorSpy.mockRestore();
  });
});

describe("registerShowDecisionsCommand", () => {
  it("should register command with correct ID", () => {
    const mockContext = {
      subscriptions: [] as vscode.Disposable[],
    } as vscode.ExtensionContext;

    const projectRoot = "/home/user/project";

    registerShowDecisionsCommand(mockContext, projectRoot);

    expect(vscode.commands.registerCommand).toHaveBeenCalledWith(
      "file-native-comments.showDecisions",
      expect.any(Function)
    );

    expect(mockContext.subscriptions.length).toBe(1);
  });

  it("should log registration to console", () => {
    const consoleLogSpy = jest.spyOn(console, "log").mockImplementation();
    const mockContext = {
      subscriptions: [] as vscode.Disposable[],
    } as vscode.ExtensionContext;

    registerShowDecisionsCommand(mockContext, "/home/user/project");

    expect(consoleLogSpy).toHaveBeenCalledWith(
      expect.stringContaining("[showDecisions] Registered command:")
    );

    consoleLogSpy.mockRestore();
  });
});
