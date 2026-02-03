/**
 * Mock implementation of vscode module for testing.
 */

export class Range {
    public start: { line: number; character: number };
    public end: { line: number; character: number };

    constructor(
        startLine: number,
        startCharacter: number,
        endLine: number,
        endCharacter: number
    ) {
        this.start = { line: startLine, character: startCharacter };
        this.end = { line: endLine, character: endCharacter };
    }
}

export class RelativePattern {
    constructor(
        public base: string,
        public pattern: string
    ) {}
}

export enum CommentMode {
    Preview = 0,
    Editing = 1
}

export enum CommentThreadState {
    Unresolved = 0,
    Resolved = 1
}

export enum CommentThreadCollapsibleState {
    Collapsed = 0,
    Expanded = 1
}

export class MarkdownString {
    public isTrusted: boolean = false;
    constructor(public value: string) {}
}

export class Uri {
    constructor(public fsPath: string) {}

    static parse(uri: string): Uri {
        return { fsPath: uri, toString: () => uri } as any;
    }

    static file(path: string): Uri {
        return { fsPath: path, toString: () => path } as any;
    }

    toString(): string {
        return this.fsPath;
    }
}

export interface CommentThread {
    uri: Uri;
    range: Range;
    comments: any[];
    canReply: boolean;
    state: CommentThreadState;
    label?: string;
    contextValue?: string;
    collapsibleState: CommentThreadCollapsibleState;
    dispose(): void;
}

export interface CommentReply {
    thread: CommentThread;
    text: string;
}

export interface CommentController {
    id: string;
    label: string;
    commentingRangeProvider?: any;
    replyHandler?: (reply: CommentReply) => void | Promise<void>;
    createCommentThread(uri: Uri, range: Range, comments: any[]): CommentThread;
    dispose?(): void;
}

export const comments = {
    createCommentController: (id: string, label: string): CommentController => ({
        id,
        label,
        createCommentThread: (uri: Uri, range: Range, commentsList: any[]): CommentThread => ({
            uri,
            range,
            comments: commentsList,
            canReply: false,
            state: CommentThreadState.Unresolved,
            label: '',
            contextValue: '',
            collapsibleState: CommentThreadCollapsibleState.Expanded,
            dispose: () => {}
        })
    })
};

export const workspace = {
    workspaceFolders: undefined as any,
    textDocuments: [] as any[],
    onDidOpenTextDocument: () => ({ dispose: () => {} }),
    createFileSystemWatcher: jest.fn()
};

export interface TextEditorDecorationType {
    key: string;
    dispose(): void;
}

export const window = {
    showInformationMessage: jest.fn(),
    showErrorMessage: jest.fn(),
    showWarningMessage: jest.fn(),
    showInputBox: jest.fn(),
    activeTextEditor: undefined as any,
    visibleTextEditors: [] as any[],
    createTextEditorDecorationType: jest.fn((options: any): TextEditorDecorationType => ({
        key: 'mock-decoration',
        dispose: jest.fn()
    })),
    onDidChangeVisibleTextEditors: jest.fn(() => ({ dispose: jest.fn() }))
};

export const env = {
    username: 'testuser'
};

export const commands = {
    registerCommand: jest.fn()
};

export enum TextEditorRevealType {
    Default = 0,
    InCenter = 1,
    InCenterIfOutsideViewport = 2,
    AtTop = 3
}
