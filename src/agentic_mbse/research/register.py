"""`register`: the one door a source takes into a target's `knowledge/`.

The ladder refuses everything it can before a byte is fetched, captures into a
staging directory of its own, checks what it captured, and only then commits
four artifacts together under the registry lock: the source directory, the raw
copy, one manifest row and one index block. A failed commit rung undoes the
rungs before it, so the registry is left as it was.

Given a run directory, every returned outcome leaves one receipt there. The
seam's `close` reads those receipts, never this module.
"""

from __future__ import annotations

import shutil
import uuid
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Literal

from agentic_mbse.research.capture import (
    CAPTURE_TIMEOUT_S,
    STAGED_INPUT_DIR,
    Captured,
    CaptureFailure,
    capture,
    sha256_of,
    web_capture_available,
)
from agentic_mbse.research.holdout import (
    HoldoutGuard,
    HoldoutGuardError,
    HoldoutHit,
    first_file_hit,
    first_term_hit,
    input_path_hit,
    load_holdout_guard,
)
from agentic_mbse.research.index import (
    SOURCES_PREFIX,
    insert_block,
    render_batch_block,
    render_seam_block,
)
from agentic_mbse.research.manifest import (
    ManifestMark,
    Row,
    append_manifest_row,
    first_matching_row,
    mark_manifest,
    roll_back_manifest,
)
from agentic_mbse.research.paths import (
    RegistryPaths,
    default_paths,
    registry_lock,
    sweep_stale_staging,
)
from agentic_mbse.research.runs import Triage, read_receipts, run_limits, write_receipt
from agentic_mbse.research.sources import (
    KeyedFileSource,
    Source,
    SourceMetadata,
    UrlSource,
    normalize_url,
    slugify,
)

Outcome = Literal[
    "registered",
    "duplicate",
    "holdout_hit",
    "capture_failed",
    "precondition_failed",
    "limit_reached",
]

DEFAULT_BUDGET = 0.0

# Capture is bounded by its timeout and commit is a few filesystem calls under
# the lock, so no live attempt's staging directory ever gets this old.
STALE_STAGING_AGE_S = 4 * CAPTURE_TIMEOUT_S

# Outcomes reached only after the extractor ran.
_POST_CAPTURE_OUTCOMES = frozenset({"registered", "capture_failed"})


class RegistrationError(RuntimeError):
    """A commit rung failed. Everything the attempt wrote has already been undone."""


@dataclass(frozen=True)
class RegistrationResult:
    """What one registration attempt came to.

    `registered` carries where the source landed and its hashes, `duplicate` the
    entry it duplicates, and `holdout_hit` the rule that fired and where. Every
    refusal carries a one-line reason.
    """

    outcome: Outcome
    reason: str = ""
    slug: str | None = None
    path: Path | None = None
    location: str | None = None
    source_id: str | None = None
    raw_sha256: str | None = None
    raw_artifact_sha256: str | None = None
    extract_sha256: str | None = None
    rule_id: str | None = None
    offsets: tuple[int, ...] = ()
    existing_slug: str | None = None
    existing_path: str | None = None


def register(
    source: Source,
    metadata: SourceMetadata,
    *,
    paths: RegistryPaths | None = None,
    guard: HoldoutGuard | None = None,
    budget: float = DEFAULT_BUDGET,
    run_dir: Path | None = None,
    triage: Triage = "keeper",
) -> RegistrationResult:
    """Capture, hold-out check and register one source.

    Returns a result for every refusal: blank metadata, a missing input file or
    index, a hold-out hit, a guard that cannot answer, a duplicate, a spent
    capture limit, a missing web extra, a failed capture. Raises
    `RegistrationError` when a commit rung failed, with the registry left as it
    was, and `subprocess.TimeoutExpired` when capture overran.

    `paths` defaults to the project in the current directory, and `guard` to the
    one that project's `pyproject.toml` names (`load_holdout_guard`). Given
    `run_dir`, the attempt counts against the run's `max_captures`, and every
    returned outcome writes one receipt there; a raised error writes none.
    """
    paths = paths if paths is not None else default_paths()
    guard = guard if guard is not None else load_holdout_guard(paths.project_root)
    result = _attempt(source, metadata, paths=paths, guard=guard, budget=budget, run_dir=run_dir)
    if run_dir is not None:
        write_receipt(
            run_dir,
            outcome=result.outcome,
            candidate=source.identity,
            slug=result.slug,
            path=result.location,
            source_id=result.source_id,
            triage=triage,
            reason=result.reason,
            rule_id=result.rule_id,
            captured=_spent_a_capture(result),
            at=datetime.now(timezone.utc),
        )
    return result


def manifest_row(
    source: Source,
    *,
    title: str,
    slug: str,
    source_id: str,
    raw_artifact_sha256: str,
    extract_sha256: str,
    extracted: date,
) -> Row:
    """The manifest row for a registered source, its fields in the order the registry writes them.

    The raw SHA-256 is the source id: a source's identity is the digest of its
    raw bytes as fetched.
    """
    return {
        "source_id": source_id,
        "source_kind": source.kind,
        "slug": slug,
        "title": title,
        **source.row_extras,
        "raw_sha256": source_id,
        "raw_artifact_sha256": raw_artifact_sha256,
        "extract_sha256": extract_sha256,
        "date_extracted": extracted.isoformat(),
    }


def _attempt(
    source: Source,
    metadata: SourceMetadata,
    *,
    paths: RegistryPaths,
    guard: HoldoutGuard,
    budget: float,
    run_dir: Path | None,
) -> RegistrationResult:
    """The ladder, without the receipt written around it."""
    sweep_stale_staging(paths, older_than_s=STALE_STAGING_AGE_S)

    refusal = _pre_capture_refusal(source, metadata, paths=paths, guard=guard, run_dir=run_dir)
    if refusal is not None:
        return refusal

    staging = paths.staging / uuid.uuid4().hex
    staging.mkdir(parents=True)
    try:
        captured = capture(source, staging, budget=budget)
        if isinstance(captured, CaptureFailure):
            return RegistrationResult(outcome="capture_failed", reason=captured.reason)

        refusal = _post_capture_refusal(captured, paths=paths, guard=guard)
        if refusal is not None:
            return refusal

        return _commit(source, metadata, captured, paths=paths)
    finally:
        shutil.rmtree(staging, ignore_errors=True)


# --- before capture --------------------------------------------------------------


def _pre_capture_refusal(
    source: Source,
    metadata: SourceMetadata,
    *,
    paths: RegistryPaths,
    guard: HoldoutGuard,
    run_dir: Path | None,
) -> RegistrationResult | None:
    """The first refusal that applies before anything is fetched, or None to go on to capture.

    Cheapest first, so nothing is fetched that a later check would throw away.
    """
    blank = _blank_required_fields(source, metadata)
    if blank:
        return _precondition_failed(f"caller must supply non-empty {', '.join(blank)}")
    staged = source.staged_input
    if staged is not None and not staged.is_file():
        return _precondition_failed(f"input file not found: {staged}")
    if not paths.index.is_file():
        return _precondition_failed(f"source index missing: {paths.index}")

    try:
        hit = _input_identity_holdout_hit(source, metadata, guard)
    except HoldoutGuardError as fault:
        return _precondition_failed(str(fault))
    if hit is not None:
        return _holdout_refusal(hit)

    existing = _row_matching_input_identity(source, paths)
    if existing is not None:
        return _duplicate_of(existing, reason=f"already registered as {existing['slug']}")

    limit = _limit_refusal(run_dir)
    if limit is not None:
        return limit

    if isinstance(source, UrlSource) and not web_capture_available():
        return _precondition_failed("URL capture needs the web extra: install agentic-mbse[web]")
    return None


def _blank_required_fields(source: Source, metadata: SourceMetadata) -> list[str]:
    """The metadata fields this source's index block needs that the caller left blank.

    A seam block needs all four; a batch caller supplies only the title.
    """
    fields = {"title": metadata.title}
    if source.index_profile == "seam":
        fields |= {
            "use_for": metadata.use_for,
            "validation": metadata.validation,
            "caveat": metadata.caveat,
        }
    return [name for name, value in fields.items() if not value.strip()]


def _input_identity_holdout_hit(
    source: Source, metadata: SourceMetadata, guard: HoldoutGuard
) -> HoldoutHit | None:
    """Check what the caller handed in: the input path, the URL or key, and the title.

    The destination slug is newly minted and could never match, so it is not checked.
    """
    staged = source.staged_input
    if staged is not None:
        hit = input_path_hit(guard, staged)
        if hit is not None:
            return hit
    for text in (source.identity, metadata.title):
        hit = first_term_hit(guard, text)
        if hit is not None:
            return hit
    return None


def _row_matching_input_identity(source: Source, paths: RegistryPaths) -> Row | None:
    """The first row the input already duplicates, judged before any fetch.

    A keyed source matches its key field exactly, whatever the row's kind. A URL
    matches exactly, or with scheme and host lowercased and the fragment dropped.
    A local PDF carries neither, so only its source id can catch it, after capture.
    """
    if isinstance(source, KeyedFileSource):
        return first_matching_row(paths, lambda row: row.get(source.key_field) == source.key)
    if isinstance(source, UrlSource):
        normalized = normalize_url(source.url)
        return first_matching_row(
            paths,
            lambda row: bool(row.get("source_url"))
            and (row["source_url"] == source.url or normalize_url(row["source_url"]) == normalized),
        )
    return None


def _limit_refusal(run_dir: Path | None) -> RegistrationResult | None:
    """Refuse when the run has spent its `max_captures`. No run, or no limit, never refuses."""
    if run_dir is None:
        return None
    limit = run_limits(run_dir).get("max_captures")
    if limit is None:
        return None
    spent = sum(1 for receipt in read_receipts(run_dir) if receipt.get("captured"))
    if spent < limit:
        return None
    return RegistrationResult(
        outcome="limit_reached", reason=f"run has spent its max_captures limit of {limit}"
    )


# --- after capture ---------------------------------------------------------------


def _post_capture_refusal(
    captured: Captured, *, paths: RegistryPaths, guard: HoldoutGuard
) -> RegistrationResult | None:
    """The hold-out scan of what was captured, then dedupe on the bytes as fetched."""
    try:
        hit = _captured_holdout_hit(captured, guard)
    except HoldoutGuardError as fault:
        # The capture is spent, so the refusal carries its source id and counts against
        # the run's max_captures.
        return RegistrationResult(
            outcome="precondition_failed", reason=str(fault), source_id=captured.source_id
        )
    if hit is not None:
        return _holdout_refusal(hit)

    existing = first_matching_row(paths, lambda row: row.get("source_id") == captured.source_id)
    if existing is not None:
        return _duplicate_of(
            existing, reason=f"same bytes already registered (source_id {captured.source_id})"
        )
    return None


def _captured_holdout_hit(captured: Captured, guard: HoldoutGuard) -> HoldoutHit | None:
    """The first barred term in the extract, then in the raw artifact."""
    for artifact in (captured.extract, captured.raw_artifact):
        hit = first_file_hit(guard, artifact)
        if hit is not None:
            return hit
    return None


# --- refusals --------------------------------------------------------------------


def _precondition_failed(reason: str) -> RegistrationResult:
    return RegistrationResult(outcome="precondition_failed", reason=reason)


def _holdout_refusal(hit: HoldoutHit) -> RegistrationResult:
    """Record the rule that fired and where, never the content that fired it."""
    return RegistrationResult(
        outcome="holdout_hit",
        reason=f"{hit.rule_id} matched {hit.count}x",
        rule_id=hit.rule_id,
        offsets=hit.offsets,
    )


def _duplicate_of(row: Row, *, reason: str) -> RegistrationResult:
    return RegistrationResult(
        outcome="duplicate",
        reason=reason,
        source_id=row.get("source_id"),
        existing_slug=row["slug"],
        existing_path=f"{SOURCES_PREFIX}{row['slug']}/",
    )


# --- commit, and the rollback that undoes it -------------------------------------
#
# Each rung is a module-level name, so a test can make any one of them fail.


def _commit(
    source: Source,
    metadata: SourceMetadata,
    captured: Captured,
    *,
    paths: RegistryPaths,
) -> RegistrationResult:
    """Move the four artifacts into place under the registry lock, or undo every rung that ran.

    The index read-modify-write goes last because it is the riskiest, so its
    failure only has to undo cheap, exactly known things.
    """
    with registry_lock(paths):
        slug = _resolve_slug(slugify(metadata.title), paths.sources, source.slug_suffix)
        source_dir = paths.sources / slug
        staged = source.staged_input
        raw_copy = paths.raw / staged.name if staged is not None else None
        manifest_mark = mark_manifest(paths)
        added = date.today()

        try:
            _rename_into_sources(captured.staging, source_dir)
            moved_raw = _move_raw_copy(source_dir, raw_copy)
            # Digested once and handed to both writers, so the row and the block cannot disagree.
            raw_artifact_sha256 = (
                sha256_of(moved_raw) if moved_raw is not None else captured.raw_artifact_sha256
            )
            append_manifest_row(
                paths,
                manifest_row(
                    source,
                    title=metadata.title,
                    slug=slug,
                    source_id=captured.source_id,
                    raw_artifact_sha256=raw_artifact_sha256,
                    extract_sha256=captured.extract_sha256,
                    extracted=added,
                ),
            )
            insert_block(
                paths.index,
                _index_block(
                    source,
                    metadata,
                    slug=slug,
                    source_id=captured.source_id,
                    raw_artifact_sha256=raw_artifact_sha256,
                    extract_sha256=captured.extract_sha256,
                    added=added,
                ),
            )
        except Exception as error:
            _roll_back(source_dir, raw_copy, manifest_mark, paths)
            raise RegistrationError(f"commit failed for {source.identity}: {error}") from error

    return RegistrationResult(
        outcome="registered",
        slug=slug,
        path=source_dir,
        location=f"{SOURCES_PREFIX}{slug}/",
        source_id=captured.source_id,
        raw_sha256=captured.source_id,
        raw_artifact_sha256=raw_artifact_sha256,
        extract_sha256=captured.extract_sha256,
    )


def _resolve_slug(slug: str, sources_dir: Path, suffix: str | None) -> str:
    """`slug`, or a free variant of it: with the source's own suffix if it has one, else `_2`, `_3`, …"""
    if not (sources_dir / slug).exists():
        return slug
    if suffix is not None:
        return f"{slug}_{suffix}"
    n = 2
    while (sources_dir / f"{slug}_{n}").exists():
        n += 1
    return f"{slug}_{n}"


def _rename_into_sources(staging: Path, source_dir: Path) -> None:
    """Rung one: staging becomes the source directory in one atomic rename on the same filesystem."""
    source_dir.parent.mkdir(parents=True, exist_ok=True)
    staging.rename(source_dir)


def _move_raw_copy(source_dir: Path, raw_copy: Path | None) -> Path | None:
    """Rung two: move the staged local input out of the source directory to `raw_copy`."""
    if raw_copy is None:
        return None
    staged = source_dir / STAGED_INPUT_DIR / raw_copy.name
    raw_copy.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(staged, raw_copy)
    shutil.rmtree(source_dir / STAGED_INPUT_DIR, ignore_errors=True)
    return raw_copy


def _index_block(
    source: Source,
    metadata: SourceMetadata,
    *,
    slug: str,
    source_id: str,
    raw_artifact_sha256: str,
    extract_sha256: str,
    added: date,
) -> str:
    """The index block for the source: a batch block for a keyed source, a seam block otherwise."""
    if isinstance(source, KeyedFileSource):
        return render_batch_block(
            title=metadata.title,
            slug=slug,
            key_label=source.key_label,
            key_display=source.key_display,
            source_id=source_id,
            extract_sha256=extract_sha256,
            added=added,
        )
    return render_seam_block(
        title=metadata.title,
        slug=slug,
        source_kind=source.kind,
        origin=source.url if isinstance(source, UrlSource) else str(source.path),
        use_for=metadata.use_for,
        validation=metadata.validation,
        caveat=metadata.caveat,
        source_id=source_id,
        raw_artifact_sha256=raw_artifact_sha256,
        extract_sha256=extract_sha256,
        added=added,
    )


def _roll_back(
    source_dir: Path, raw_copy: Path | None, manifest_mark: ManifestMark, paths: RegistryPaths
) -> None:
    """Undo the commit rungs in reverse. A rung that never ran makes its step a no-op.

    The slug was resolved under the lock to a directory that did not exist, so
    removing `source_dir` removes only what this attempt created.
    """
    roll_back_manifest(paths, manifest_mark)
    if raw_copy is not None:
        raw_copy.unlink(missing_ok=True)
    shutil.rmtree(source_dir, ignore_errors=True)


# --- receipts --------------------------------------------------------------------


def _spent_a_capture(result: RegistrationResult) -> bool:
    """True when the extractor ran for this attempt, which is what `max_captures` counts."""
    if result.outcome in _POST_CAPTURE_OUTCOMES:
        return True
    # A duplicate found after capture carries the captured source id, and so does a
    # guard fault after capture. A duplicate found before the fetch carries one too
    # when the row it matched has one; the count has always included those, so a
    # run's limit means what it meant before. A hold-out hit after capture carries
    # none, and has never counted.
    return (
        result.outcome in {"duplicate", "holdout_hit", "precondition_failed"}
        and result.source_id is not None
    )
