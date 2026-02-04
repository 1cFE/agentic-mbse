import * as vscode from "vscode";
import { reconcileFileCommand, registerReconcileFileCommand } from "./reconcileFile";
import * as childProcess from "child_process";

// Mock child_process
jest.mock("child_process");
const mockExecFile = childProcess.execFile as unknown as jest.Mock;

describe("reconcileFileCommand", () => {
  let mockEditor: vscode.TextEditor;
  const projectRoot = "/home/user/project";
  const filePath = "/home/user/project/src/example.py";
  const relativeFilePath = "src/example.py";

  beforeEach(() => {
    jest.clearAllMocks();

    mockEditor = {
      document: {
        uri: { fsPath: filePath },
      },
    } as any;

    (vscode.window as any).activeTextEditor = mockEditor;

    mockExecFile.mockImplementation(
      (cmd: string, args: string[], opts: any, cb: Function) => {
        cb(null, { stdout: '{}', stderr: '' });
      }
    );
  });

  it("should show warning when no active editor", async () => {
    (vscode.window as any).activeTextEditor = undefined;

    await reconcileFileCommand(projectRoot);

    expect(vscode.window.showWarningMessage).toHaveBeenCalledWith(
      "No active file to reconcile"
    );
    expect(mockExecFile).not.toHaveBeenCalled();
  });

  it("should show error when file is outside project root", async () => {
    const outsideFilePath = "/home/other/file.py";
    mockEditor = {
      document: {
        uri: { fsPath: outsideFilePath },
      },
    } as any;
    (vscode.window as any).activeTextEditor = mockEditor;

    await reconcileFileCommand(projectRoot);

    expect(vscode.window.showErrorMessage).toHaveBeenCalledWith(
      "Cannot reconcile file outside project root"
    );
    expect(mockExecFile).not.toHaveBeenCalled();
  });

  it("should execute CLI command with correct arguments", async () => {
    const mockReport = {
      file: relativeFilePath,
      renamed: false,
      total_threads: 3,
      anchored: 2,
      drifted: 1,
      orphaned: 0,
      max_drift: 5,
      source_hash_before: "abc123",
      source_hash_after: "def456",
    };

    mockExecFile.mockImplementation(
      (cmd: string, args: string[], opts: any, cb: Function) => {
        cb(null, { stdout: JSON.stringify(mockReport), stderr: '' });
      }
    );

    await reconcileFileCommand(projectRoot);

    expect(mockExecFile).toHaveBeenCalledWith(
      "comment",
      ["reconcile", filePath, "--json"],
      expect.objectContaining({
        cwd: projectRoot,
        encoding: "utf-8",
      }),
      expect.any(Function)
    );
  });

  it("should show success notification when all threads anchored", async () => {
    const mockReport = {
      file: relativeFilePath,
      renamed: false,
      total_threads: 3,
      anchored: 3,
      drifted: 0,
      orphaned: 0,
      max_drift: 0,
      source_hash_before: "abc123",
      source_hash_after: "abc123",
    };

    mockExecFile.mockImplementation(
      (cmd: string, args: string[], opts: any, cb: Function) => {
        cb(null, { stdout: JSON.stringify(mockReport), stderr: '' });
      }
    );

    await reconcileFileCommand(projectRoot);

    expect(vscode.window.showInformationMessage).toHaveBeenCalledWith(
      `Reconciled ${relativeFilePath}: 3 anchored, 0 drifted, 0 orphaned`
    );
  });

  it("should show warning notification when threads drifted", async () => {
    const mockReport = {
      file: relativeFilePath,
      renamed: false,
      total_threads: 3,
      anchored: 1,
      drifted: 2,
      orphaned: 0,
      max_drift: 10,
      source_hash_before: "abc123",
      source_hash_after: "def456",
    };

    mockExecFile.mockImplementation(
      (cmd: string, args: string[], opts: any, cb: Function) => {
        cb(null, { stdout: JSON.stringify(mockReport), stderr: '' });
      }
    );

    await reconcileFileCommand(projectRoot);

    expect(vscode.window.showWarningMessage).toHaveBeenCalledWith(
      `Reconciled ${relativeFilePath}: 1 anchored, 2 drifted, 0 orphaned`
    );
  });

  it("should include rename note in notification when file renamed", async () => {
    const mockReport = {
      file: relativeFilePath,
      renamed: true,
      total_threads: 3,
      anchored: 3,
      drifted: 0,
      orphaned: 0,
      max_drift: 0,
      source_hash_before: "abc123",
      source_hash_after: "abc123",
    };

    mockExecFile.mockImplementation(
      (cmd: string, args: string[], opts: any, cb: Function) => {
        cb(null, { stdout: JSON.stringify(mockReport), stderr: '' });
      }
    );

    await reconcileFileCommand(projectRoot);

    expect(vscode.window.showInformationMessage).toHaveBeenCalledWith(
      `Reconciled ${relativeFilePath} (file renamed): 3 anchored, 0 drifted, 0 orphaned`
    );
  });

  it("should show error notification when CLI output is not valid JSON", async () => {
    mockExecFile.mockImplementation(
      (cmd: string, args: string[], opts: any, cb: Function) => {
        cb(null, { stdout: "Not valid JSON output", stderr: '' });
      }
    );

    await reconcileFileCommand(projectRoot);

    expect(vscode.window.showErrorMessage).toHaveBeenCalledWith(
      "Reconciliation failed: Invalid CLI output (expected JSON)"
    );
  });

  it("should show info notification when no comments found (exit code 1)", async () => {
    const error: any = new Error("Command failed");
    error.status = 1;
    error.stderr = "Error: No comments found for src/example.py";

    mockExecFile.mockImplementation(
      (cmd: string, args: string[], opts: any, cb: Function) => {
        cb(error);
      }
    );

    await reconcileFileCommand(projectRoot);

    expect(vscode.window.showInformationMessage).toHaveBeenCalledWith(
      `No comments found for ${relativeFilePath}`
    );
  });

  it("should show error notification for system errors (exit code 2)", async () => {
    const error: any = new Error("Command failed");
    error.status = 2;
    error.stderr = "Error: Permission denied";

    mockExecFile.mockImplementation(
      (cmd: string, args: string[], opts: any, cb: Function) => {
        cb(error);
      }
    );

    await reconcileFileCommand(projectRoot);

    expect(vscode.window.showErrorMessage).toHaveBeenCalledWith(
      "Reconciliation failed (system error): Error: Permission denied"
    );
  });

  it("should show error notification for unknown errors", async () => {
    const error: any = new Error("Unknown error");
    error.stderr = "Something went wrong";

    mockExecFile.mockImplementation(
      (cmd: string, args: string[], opts: any, cb: Function) => {
        cb(error);
      }
    );

    await reconcileFileCommand(projectRoot);

    expect(vscode.window.showErrorMessage).toHaveBeenCalledWith(
      "Reconciliation failed: Something went wrong"
    );
  });

  it("should log CLI command and output to console", async () => {
    const consoleLogSpy = jest.spyOn(console, "log").mockImplementation();

    const mockReport = {
      file: relativeFilePath,
      renamed: false,
      total_threads: 1,
      anchored: 1,
      drifted: 0,
      orphaned: 0,
      max_drift: 0,
      source_hash_before: "abc",
      source_hash_after: "abc",
    };

    mockExecFile.mockImplementation(
      (cmd: string, args: string[], opts: any, cb: Function) => {
        cb(null, { stdout: JSON.stringify(mockReport), stderr: '' });
      }
    );

    await reconcileFileCommand(projectRoot);

    expect(consoleLogSpy).toHaveBeenCalledWith(
      expect.stringContaining("[reconcileFile] Running:")
    );
    expect(consoleLogSpy).toHaveBeenCalledWith(
      expect.stringContaining("[reconcileFile] CLI output:")
    );

    consoleLogSpy.mockRestore();
  });
});

describe("registerReconcileFileCommand", () => {
  it("should register command with correct ID", () => {
    const mockContext = {
      subscriptions: [] as vscode.Disposable[],
    } as vscode.ExtensionContext;

    const projectRoot = "/home/user/project";

    registerReconcileFileCommand(mockContext, projectRoot);

    expect(vscode.commands.registerCommand).toHaveBeenCalledWith(
      "file-native-comments.reconcileFile",
      expect.any(Function)
    );

    expect(mockContext.subscriptions.length).toBe(1);
  });

  it("should log registration to console", () => {
    const consoleLogSpy = jest.spyOn(console, "log").mockImplementation();
    const mockContext = {
      subscriptions: [] as vscode.Disposable[],
    } as vscode.ExtensionContext;

    registerReconcileFileCommand(mockContext, "/home/user/project");

    expect(consoleLogSpy).toHaveBeenCalledWith(
      expect.stringContaining("[reconcileFile] Registered command:")
    );

    consoleLogSpy.mockRestore();
  });
});
