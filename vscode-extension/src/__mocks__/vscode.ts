/**
 * Mock implementation of vscode module for testing.
 */

export class Range {
    constructor(
        public startLine: number,
        public startCharacter: number,
        public endLine: number,
        public endCharacter: number
    ) {}
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

export interface CommentController {
    id: string;
    label: string;
    commentingRangeProvider?: any;
    createCommentThread(uri: Uri, range: Range, comments: any[]): CommentThread;
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
