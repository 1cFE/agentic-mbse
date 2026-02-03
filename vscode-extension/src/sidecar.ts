/**
 * Sidecar file reader for comment threads.
 *
 * Reads and parses .comments/*.json files containing comment thread data.
 */

import * as fs from 'fs';
import * as path from 'path';

/**
 * Thread lifecycle status.
 */
export enum ThreadStatus {
    OPEN = "open",
    RESOLVED = "resolved",
    WONTFIX = "wontfix"
}

/**
 * Type of comment author.
 */
export enum AuthorType {
    HUMAN = "human",
    AGENT = "agent"
}

/**
 * Health status of an anchor.
 */
export enum AnchorHealth {
    ANCHORED = "anchored",  // Content matches exactly at line position
    DRIFTED = "drifted",    // Content found nearby (within search window)
    ORPHANED = "orphaned"   // Content not found in file
}

/**
 * Immutable record of a thread resolution decision.
 */
export interface Decision {
    summary: string;          // 1-10,000 characters
    decider: string;          // 1-200 characters
    timestamp: string;        // ISO 8601 UTC timestamp (e.g., "2026-02-01T10:00:00Z")
}

/**
 * A single comment within a thread.
 */
export interface Comment {
    id: string;               // ULID (26 characters)
    author: string;           // 1-200 characters
    author_type: AuthorType;
    body: string;             // 1-10,000 characters
    timestamp: string;        // ISO 8601 UTC timestamp
}

/**
 * Location anchor using multi-signal reconciliation.
 */
export interface Anchor {
    content_hash: string;         // "sha256:[64 hex chars]"
    context_hash_before: string;  // "sha256:[64 hex chars]"
    context_hash_after: string;   // "sha256:[64 hex chars]"
    line_start: number;           // 1-indexed line number (>= 1)
    line_end: number;             // 1-indexed line number (>= line_start)
    content_snippet: string;      // 1-500 characters
    health: AnchorHealth;
    drift_distance: number;       // Lines moved from original position (0 = anchored)
}

/**
 * A discussion thread anchored to a location in a source file.
 */
export interface Thread {
    id: string;                   // ULID (26 characters)
    status: ThreadStatus;
    created_at: string;           // ISO 8601 UTC timestamp
    resolved_at: string | null;   // ISO 8601 UTC timestamp or null
    comments: Comment[];
    anchor: Anchor;
    decision: Decision | null;
}

/**
 * Root structure for a sidecar JSON file.
 */
export interface SidecarFile {
    source_file: string;          // Relative path to source file (POSIX separators)
    source_hash: string;          // "sha256:[64 hex chars]"
    schema_version: string;       // Currently "1.0"
    threads: Thread[];
}

/**
 * Converts a source file path to its corresponding sidecar path.
 *
 * @param sourcePath Absolute path to the source file
 * @param projectRoot Absolute path to the project root
 * @returns Absolute path to the sidecar file (.comments/<relative_path>.json)
 */
function getSidecarPath(sourcePath: string, projectRoot: string): string {
    // Convert source path to relative path from project root
    const relativePath = path.relative(projectRoot, sourcePath);

    // Convert to POSIX-style path (forward slashes)
    const posixPath = relativePath.split(path.sep).join('/');

    // Construct sidecar path: <projectRoot>/.comments/<posixPath>.json
    return path.join(projectRoot, '.comments', `${posixPath}.json`);
}

/**
 * Reads and parses a sidecar file for a given source file.
 *
 * @param sourcePath Absolute path to the source file
 * @param projectRoot Absolute path to the project root
 * @returns Parsed SidecarFile object, or null if the sidecar doesn't exist
 * @throws Error if the JSON is malformed or doesn't match the schema
 */
export function readSidecar(sourcePath: string, projectRoot: string): SidecarFile | null {
    const sidecarPath = getSidecarPath(sourcePath, projectRoot);

    // Return null if sidecar doesn't exist
    if (!fs.existsSync(sidecarPath)) {
        return null;
    }

    // Read and parse JSON
    const jsonContent = fs.readFileSync(sidecarPath, 'utf-8');
    const data = JSON.parse(jsonContent);

    // Basic validation
    validateSidecarFile(data);

    return data as SidecarFile;
}

/**
 * Validates that a parsed JSON object matches the SidecarFile schema.
 *
 * @param data Parsed JSON object
 * @throws Error if validation fails
 */
function validateSidecarFile(data: any): void {
    // Check required top-level fields
    if (typeof data.source_file !== 'string') {
        throw new Error('Missing or invalid field: source_file');
    }
    if (typeof data.source_hash !== 'string' || !data.source_hash.match(/^sha256:[a-fA-F0-9]{64}$/)) {
        throw new Error('Missing or invalid field: source_hash (expected "sha256:[64 hex chars]")');
    }
    if (typeof data.schema_version !== 'string') {
        throw new Error('Missing or invalid field: schema_version');
    }
    if (!Array.isArray(data.threads)) {
        throw new Error('Missing or invalid field: threads (expected array)');
    }

    // Validate each thread
    for (let i = 0; i < data.threads.length; i++) {
        const thread = data.threads[i];
        validateThread(thread, i);
    }
}

/**
 * Validates a thread object.
 *
 * @param thread Thread object to validate
 * @param index Index of the thread in the threads array (for error messages)
 * @throws Error if validation fails
 */
function validateThread(thread: any, index: number): void {
    const prefix = `threads[${index}]`;

    // Check required fields
    if (typeof thread.id !== 'string' || thread.id.length !== 26) {
        throw new Error(`${prefix}.id: Expected ULID (26 characters), got: ${thread.id}`);
    }
    if (!Object.values(ThreadStatus).includes(thread.status)) {
        throw new Error(`${prefix}.status: Invalid value "${thread.status}", expected one of: ${Object.values(ThreadStatus).join(', ')}`);
    }
    if (typeof thread.created_at !== 'string') {
        throw new Error(`${prefix}.created_at: Expected ISO 8601 timestamp string`);
    }
    if (thread.resolved_at !== null && typeof thread.resolved_at !== 'string') {
        throw new Error(`${prefix}.resolved_at: Expected ISO 8601 timestamp string or null`);
    }
    if (!Array.isArray(thread.comments)) {
        throw new Error(`${prefix}.comments: Expected array`);
    }
    if (typeof thread.anchor !== 'object' || thread.anchor === null) {
        throw new Error(`${prefix}.anchor: Expected object`);
    }
    if (thread.decision !== null && typeof thread.decision !== 'object') {
        throw new Error(`${prefix}.decision: Expected object or null`);
    }

    // Validate anchor
    validateAnchor(thread.anchor, `${prefix}.anchor`);

    // Validate comments
    for (let j = 0; j < thread.comments.length; j++) {
        validateComment(thread.comments[j], `${prefix}.comments[${j}]`);
    }

    // Validate decision if present
    if (thread.decision !== null) {
        validateDecision(thread.decision, `${prefix}.decision`);
    }
}

/**
 * Validates an anchor object.
 *
 * @param anchor Anchor object to validate
 * @param prefix Path prefix for error messages
 * @throws Error if validation fails
 */
function validateAnchor(anchor: any, prefix: string): void {
    const hashPattern = /^sha256:[a-fA-F0-9]{64}$/;

    if (typeof anchor.content_hash !== 'string' || !anchor.content_hash.match(hashPattern)) {
        throw new Error(`${prefix}.content_hash: Expected "sha256:[64 hex chars]"`);
    }
    if (typeof anchor.context_hash_before !== 'string' || !anchor.context_hash_before.match(hashPattern)) {
        throw new Error(`${prefix}.context_hash_before: Expected "sha256:[64 hex chars]"`);
    }
    if (typeof anchor.context_hash_after !== 'string' || !anchor.context_hash_after.match(hashPattern)) {
        throw new Error(`${prefix}.context_hash_after: Expected "sha256:[64 hex chars]"`);
    }
    if (typeof anchor.line_start !== 'number' || anchor.line_start < 1) {
        throw new Error(`${prefix}.line_start: Expected integer >= 1`);
    }
    if (typeof anchor.line_end !== 'number' || anchor.line_end < anchor.line_start) {
        throw new Error(`${prefix}.line_end: Expected integer >= line_start`);
    }
    if (typeof anchor.content_snippet !== 'string' || anchor.content_snippet.length < 1 || anchor.content_snippet.length > 500) {
        throw new Error(`${prefix}.content_snippet: Expected string with 1-500 characters`);
    }
    if (!Object.values(AnchorHealth).includes(anchor.health)) {
        throw new Error(`${prefix}.health: Invalid value "${anchor.health}", expected one of: ${Object.values(AnchorHealth).join(', ')}`);
    }
    if (typeof anchor.drift_distance !== 'number' || anchor.drift_distance < 0) {
        throw new Error(`${prefix}.drift_distance: Expected integer >= 0`);
    }
}

/**
 * Validates a comment object.
 *
 * @param comment Comment object to validate
 * @param prefix Path prefix for error messages
 * @throws Error if validation fails
 */
function validateComment(comment: any, prefix: string): void {
    if (typeof comment.id !== 'string' || comment.id.length !== 26) {
        throw new Error(`${prefix}.id: Expected ULID (26 characters)`);
    }
    if (typeof comment.author !== 'string' || comment.author.length < 1 || comment.author.length > 200) {
        throw new Error(`${prefix}.author: Expected string with 1-200 characters`);
    }
    if (!Object.values(AuthorType).includes(comment.author_type)) {
        throw new Error(`${prefix}.author_type: Invalid value "${comment.author_type}", expected one of: ${Object.values(AuthorType).join(', ')}`);
    }
    if (typeof comment.body !== 'string' || comment.body.length < 1 || comment.body.length > 10000) {
        throw new Error(`${prefix}.body: Expected string with 1-10,000 characters`);
    }
    if (typeof comment.timestamp !== 'string') {
        throw new Error(`${prefix}.timestamp: Expected ISO 8601 timestamp string`);
    }
}

/**
 * Validates a decision object.
 *
 * @param decision Decision object to validate
 * @param prefix Path prefix for error messages
 * @throws Error if validation fails
 */
function validateDecision(decision: any, prefix: string): void {
    if (typeof decision.summary !== 'string' || decision.summary.length < 1 || decision.summary.length > 10000) {
        throw new Error(`${prefix}.summary: Expected string with 1-10,000 characters`);
    }
    if (typeof decision.decider !== 'string' || decision.decider.length < 1 || decision.decider.length > 200) {
        throw new Error(`${prefix}.decider: Expected string with 1-200 characters`);
    }
    if (typeof decision.timestamp !== 'string') {
        throw new Error(`${prefix}.timestamp: Expected ISO 8601 timestamp string`);
    }
}
