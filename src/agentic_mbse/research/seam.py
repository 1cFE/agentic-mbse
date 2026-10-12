"""The seam's bookkeeper: one research run, from its request to its return.

`open_run` checks a request, refuses one that a recorded negative already
answers, and creates the run directory. The `log_*` functions record what the
agent did. `close` computes the run's class from the receipts `register` wrote
and from the run log, never from what the agent reports, and writes
`return.json`. A run that found nothing usable also writes a negative, keyed on
the request, which the next `open_run` of the same request honours.

This module reads a run's receipts and log only through `runs.py`, and never
imports the registry.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal, TypedDict

from agentic_mbse.research.runs import (
    RUN_META,
    Receipt,
    Triage,
    append_run_log,
    is_run_dir,
    read_receipts,
    read_run_log,
    read_run_meta,
    start_run,
    write_return,
)

REQUIRED_REQUEST_FIELDS = (
    "request_id",
    "question",
    "consumer",
    "gap_type",
    "priority",
    "where_to_look",
)

#: Receipt outcomes that leave a named candidate for a person to resolve.
QUEUEING_OUTCOMES = frozenset({"holdout_hit", "capture_failed", "precondition_failed"})

FailureDisposition = Literal["queued", "closed"]
FAILURE_DISPOSITIONS: tuple[FailureDisposition, ...] = ("queued", "closed")

SeamClass = Literal["REGISTERED", "OPERATOR_QUEUE", "BLOCKER", "BOUNDED_NEGATIVE"]
Adequacy = Literal["exhausted", "limit_reached"]
LimitName = Literal["max_captures", "max_searches"]
OpenOutcome = Literal["opened", "invalid_request", "answered_by_negative"]

_DEFAULT_REASONS: dict[SeamClass, str] = {
    "REGISTERED": "at least one source is registered and citable",
    "OPERATOR_QUEUE": "a named candidate is blocked on something a human must resolve",
    "BOUNDED_NEGATIVE": "the search ran and found no usable source",
    "BLOCKER": "the seam could not proceed",
}


class SeamError(RuntimeError):
    """The bookkeeper was asked to work on something that is not a run, or to record an unknown disposition."""


@dataclass(frozen=True)
class SeamHome:
    """Where a project's request files, negatives and runs live."""

    root: Path

    @property
    def negatives(self) -> Path:
        return self.root / "negatives"

    @property
    def runs(self) -> Path:
        return self.root / "runs"


def default_home() -> SeamHome:
    """The seam home of the project in the current directory, with relative paths."""
    return SeamHome(root=Path("knowledge/research/requests"))


@dataclass(frozen=True)
class OpenResult:
    """What `open_run` came to. Only `opened` created a run directory, and carries it."""

    outcome: OpenOutcome
    message: str
    run_dir: Path | None = None


class RegisteredEntry(TypedDict):
    """A source the return names a citable path for. `pre_existing` when this run did not write it."""

    slug: str | None
    path: str | None
    source_id: str | None
    pre_existing: bool


class QueuedEntry(TypedDict):
    """A named candidate a person has to resolve, and why."""

    candidate: str
    reason: str


# The return a run's `return.json` holds, in the order it is written. "class" is
# a keyword, so the functional form is the only way to spell this shape.
SeamReturn = TypedDict(
    "SeamReturn",
    {
        "request_id": str,
        "run": str,
        "class": SeamClass,
        "registered": list[RegisteredEntry],
        "queued": list[QueuedEntry],
        "negative": str | None,
        "limit_reached": LimitName | None,
        "reason": str,
    },
)


def request_key(request: Mapping[str, Any]) -> str:
    """A stable hash of what the request asks, whatever the order of its `where_to_look` list.

    Priority and limits say how hard to look, not what to look for, so they stay
    out of the key: raising a limit does not make a new request. Negatives are
    filed under this key, so a changed formula would silently reopen every one.
    """
    identity = {
        "question": request["question"],
        "consumer": request["consumer"],
        "gap_type": request["gap_type"],
        "where_to_look": sorted(request.get("where_to_look") or []),
    }
    canonical = json.dumps(identity, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


def open_run(
    request_path: Path,
    *,
    home: SeamHome | None = None,
    override_reason: str | None = None,
) -> OpenResult:
    """Check the request, honour any recorded negative, and create the run directory.

    This is the only producer of a run directory, and every other function
    refuses anything else, so no run reaches a return without passing the
    negative check. `invalid_request` when the file is not readable JSON or a
    required field is empty. `answered_by_negative` when a negative is filed
    under the request's key and `override_reason` is blank. A non-blank
    override is appended to that negative's `reopened` history, never erasing
    it. `home` defaults to the project in the current directory.
    """
    home = home if home is not None else default_home()
    try:
        request = json.loads(request_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return OpenResult("invalid_request", f"request is unreadable: {error}")

    missing = [field for field in REQUIRED_REQUEST_FIELDS if not request.get(field)]
    if missing:
        return OpenResult(
            "invalid_request", f"request is missing required field(s): {', '.join(missing)}"
        )

    key = request_key(request)
    negative_path = home.negatives / f"{key}.json"
    reason = (override_reason or "").strip()
    if negative_path.exists() and not reason:
        return OpenResult(
            "answered_by_negative",
            f"a bounded negative already answers this request (key {key}): {negative_path}. "
            "Read it. To search again, supply --override-reason.",
        )

    run_dir = home.runs / request["request_id"] / _now().strftime("%Y%m%dT%H%M%S%f")
    start_run(
        run_dir,
        {
            "request_id": request["request_id"],
            "request_key": key,
            "request_path": str(request_path),
            "home_root": str(home.root),
            "limits": request.get("limits", {}),
            "opened_at": _now().isoformat(),
            "override_reason": reason or None,
        },
        f"# Research run {request['request_id']}\n\n"
        f"**Question:** {request['question']}\n\n"
        f"**Consumer:** {request['consumer']}  ·  **Request key:** `{key}`\n\n",
    )
    if reason:
        _record_reopen(negative_path, run_dir, reason)
    return OpenResult("opened", f"run opened at {run_dir}", run_dir)


def log_search(run_dir: Path, query: str) -> None:
    """Record a query the agent ran. `close` counts these against `max_searches`."""
    _append(run_dir, {"kind": "search", "query": query}, f"- searched: `{query}`")


def log_candidate(run_dir: Path, ref: str, triage: Triage, note: str = "") -> None:
    """Record a candidate and what triage decided about it."""
    _append(
        run_dir,
        {"kind": "candidate", "ref": ref, "triage": triage, "note": note},
        f"- candidate {ref} — **{triage}** {note}".rstrip(),
    )


def log_failure(
    run_dir: Path, ref: str, reason: str, disposition: FailureDisposition = "queued"
) -> None:
    """Record a candidate that could not be brought in, and why.

    `queued` (the default) hands it to a person: a paywall, a login wall or a
    repeated fetch failure is something somebody could still get past, and
    defaulting the other way would file a negative over it. `closed` is for a
    candidate nobody should chase, such as a dead link; it is recorded in the
    negative instead.
    """
    if disposition not in FAILURE_DISPOSITIONS:
        raise SeamError(f"disposition must be one of {FAILURE_DISPOSITIONS}: {disposition!r}")
    _append(
        run_dir,
        {"kind": "failure", "ref": ref, "reason": reason, "disposition": disposition},
        f"- failed {ref} — {reason} ({disposition})",
    )


def log_fault(run_dir: Path, reason: str) -> None:
    """Record a run-scoped fault: the seam itself could not proceed."""
    _append(run_dir, {"kind": "fault", "reason": reason}, f"- **run fault**: {reason}")


def close(run_dir: Path, *, adequacy: Adequacy = "exhausted") -> SeamReturn:
    """Compute the run's class, write `return.json`, and return what it holds.

    Each of two records is authoritative over what only it can know. The
    receipts say what reached the registry, and nothing the agent logs adds to
    or removes from `registered`. The run log says which candidates were blocked
    before there was anything to register, which only the agent saw, and that
    is where the triage half of `queued` comes from. A `BOUNDED_NEGATIVE` run
    also files its negative, with `adequacy` `limit_reached` whenever a declared
    limit stopped the search.
    """
    _require_run(run_dir)
    meta = read_run_meta(run_dir)
    receipts = read_receipts(run_dir)
    entries = read_run_log(run_dir)

    registered = _registered_entries(receipts)
    queued = _queued_entries(receipts, entries)
    faults = [entry["reason"] for entry in entries if entry["kind"] == "fault"]
    limit = _limit_reached(meta, receipts, entries)
    seam_class = _seam_class(registered=registered, queued=queued, faults=faults, receipts=receipts)

    negative_path = None
    if seam_class == "BOUNDED_NEGATIVE":
        negative_path = _write_negative(
            SeamHome(root=Path(meta["home_root"])),
            meta,
            entries,
            receipts,
            adequacy="limit_reached" if limit else adequacy,
        )

    payload: SeamReturn = {
        "request_id": meta["request_id"],
        "run": str(run_dir),
        "class": seam_class,
        "registered": registered,
        "queued": queued,
        "negative": str(negative_path) if negative_path else None,
        "limit_reached": limit,
        "reason": "; ".join(faults) if faults else _DEFAULT_REASONS[seam_class],
    }
    write_return(run_dir, payload)
    return payload


# --- the class -------------------------------------------------------------------


def _seam_class(
    *,
    registered: Sequence[RegisteredEntry],
    queued: Sequence[QueuedEntry],
    faults: Sequence[str],
    receipts: Sequence[Receipt],
) -> SeamClass:
    """One class per run; the first that applies wins.

    A run-scoped fault makes the run a `BLOCKER` only when it never got as far
    as a receipt. Once a candidate reached `register`, the search established
    something, so a later fault leaves the class to what the receipts say and
    only supplies the return's reason.
    """
    if registered:
        return "REGISTERED"
    if queued:
        return "OPERATOR_QUEUE"
    if faults and not receipts:
        return "BLOCKER"
    return "BOUNDED_NEGATIVE"


def _registered_entries(receipts: Sequence[Receipt]) -> list[RegisteredEntry]:
    """Sources the return can name a citable path for.

    A duplicate whose candidate triage kept answers the request as well as a new
    registration does; `pre_existing` records that this run did not write it.
    """
    entries: list[RegisteredEntry] = []
    for receipt in receipts:
        if receipt["outcome"] == "registered":
            pre_existing = False
        elif receipt["outcome"] == "duplicate" and receipt.get("triage") == "keeper":
            pre_existing = True
        else:
            continue
        entries.append(
            {
                "slug": receipt["slug"],
                "path": receipt["path"],
                "source_id": receipt["source_id"],
                "pre_existing": pre_existing,
            }
        )
    return entries


def _queued_entries(
    receipts: Sequence[Receipt], entries: Sequence[Mapping[str, Any]]
) -> list[QueuedEntry]:
    """Candidates a person has to resolve, from both places one can be found.

    A refused registration leaves a receipt. A candidate blocked at triage
    (paywalled, behind a login wall, unreachable) never reaches `register`, so
    it exists only in the run log; a failure logged without a disposition is
    queued.
    """
    queued: list[QueuedEntry] = [
        {"candidate": receipt["candidate"], "reason": receipt.get("reason") or receipt["outcome"]}
        for receipt in receipts
        if receipt["outcome"] in QUEUEING_OUTCOMES
    ]
    queued += [
        {"candidate": entry["ref"], "reason": entry["reason"]}
        for entry in entries
        if entry["kind"] == "failure" and entry.get("disposition", "queued") == "queued"
    ]
    return queued


def _limit_reached(
    meta: Mapping[str, Any], receipts: Sequence[Receipt], entries: Sequence[Mapping[str, Any]]
) -> LimitName | None:
    """The declared limit that stopped the search, if one did."""
    if any(receipt["outcome"] == "limit_reached" for receipt in receipts):
        return "max_captures"
    max_searches = meta.get("limits", {}).get("max_searches")
    if max_searches is not None:
        searched = sum(1 for entry in entries if entry["kind"] == "search")
        if searched >= max_searches:
            return "max_searches"
    return None


# --- negatives ---------------------------------------------------------------------


def _write_negative(
    home: SeamHome,
    meta: Mapping[str, Any],
    entries: Sequence[Mapping[str, Any]],
    receipts: Sequence[Receipt],
    *,
    adequacy: Adequacy,
) -> Path:
    """File the run's negative under its request key, keeping any earlier reopen history."""
    home.negatives.mkdir(parents=True, exist_ok=True)
    path = home.negatives / f"{meta['request_key']}.json"
    reopened = json.loads(path.read_text(encoding="utf-8"))["reopened"] if path.exists() else []

    candidates = [
        {"ref": entry["ref"], "triage": entry["triage"], "note": entry["note"]}
        for entry in entries
        if entry["kind"] == "candidate"
    ]
    failures = [
        {"ref": entry["ref"], "reason": entry["reason"]}
        for entry in entries
        if entry["kind"] == "failure"
    ]
    failures += [
        {"ref": receipt["candidate"], "reason": receipt.get("reason") or receipt["outcome"]}
        for receipt in receipts
        if receipt["outcome"] not in {"registered", "duplicate"}
    ]
    negative = {
        "request_key": meta["request_key"],
        "request_id": meta["request_id"],
        "queries": [entry["query"] for entry in entries if entry["kind"] == "search"],
        "candidates": candidates,
        "failures": failures,
        "adequacy": adequacy,
        "reopened": reopened,
        "recorded_at": _now().isoformat(),
    }
    path.write_text(json.dumps(negative, indent=2) + "\n", encoding="utf-8")
    return path


def _record_reopen(negative_path: Path, run_dir: Path, reason: str) -> None:
    """Append one reopening to the negative's history."""
    negative = json.loads(negative_path.read_text(encoding="utf-8"))
    negative.setdefault("reopened", []).append(
        {"reason": reason, "run": str(run_dir), "at": _now().isoformat()}
    )
    negative_path.write_text(json.dumps(negative, indent=2) + "\n", encoding="utf-8")


# --- the run log -------------------------------------------------------------------


def _append(run_dir: Path, entry: dict[str, Any], prose: str) -> None:
    """Append one timestamped step to an existing run's log."""
    _require_run(run_dir)
    append_run_log(run_dir, {**entry, "at": _now().isoformat()}, prose)


def _require_run(run_dir: Path) -> None:
    if not is_run_dir(run_dir):
        raise SeamError(f"{run_dir} is not a run directory — no {RUN_META}")


def _now() -> datetime:
    return datetime.now(timezone.utc)
