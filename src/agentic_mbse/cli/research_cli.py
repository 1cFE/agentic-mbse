"""CLI handlers for the `agentic-mbse research` subcommands.

Every subcommand runs from the project root, the directory holding
`knowledge/`, so the paths it prints and records stay relative to it. Each
handler parses its flags, calls one `agentic_mbse.research` function, prints the
result, and maps the outcome to an exit code. An error the package raises
prints as one line on stderr.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any, get_args

from agentic_mbse.research import (
    LocalPdfSource,
    RegistrationError,
    RegistrationResult,
    SourceMetadata,
    UrlSource,
    default_paths,
    register,
)
from agentic_mbse.research.index import (
    HAND_CURATED_TYPES,
    EntryResult,
    HandCuratedEntry,
    add_entry,
    list_entries,
    remove_entry,
    replace_entry,
)
from agentic_mbse.research.register import DEFAULT_BUDGET
from agentic_mbse.research.retire import RetirementError, RetirementResult, retire
from agentic_mbse.research.runs import RUN_META, Triage, is_run_dir
from agentic_mbse.research.seam import (
    FAILURE_DISPOSITIONS,
    Adequacy,
    OpenOutcome,
    SeamError,
    close,
    log_candidate,
    log_failure,
    log_fault,
    log_search,
    open_run,
)
from agentic_mbse.research.verify import format_finding, verify
from agentic_mbse.validation import EXIT_FAILURE, EXIT_SUCCESS

EXIT_USAGE = 2

#: `open` exits 2 on a request it cannot use and 3 on one a recorded negative answers.
OPEN_EXIT_CODES: dict[OpenOutcome, int] = {
    "opened": EXIT_SUCCESS,
    "invalid_request": EXIT_USAGE,
    "answered_by_negative": 3,
}

#: The hand-curated outcomes that wrote something.
ENTRY_WRITES = frozenset({"added", "replaced", "removed"})

#: The registration fields `register` prints, in order, when set.
REGISTRATION_FIELDS = (
    "reason",
    "slug",
    "location",
    "source_id",
    "raw_sha256",
    "raw_artifact_sha256",
    "extract_sha256",
    "rule_id",
    "existing_slug",
    "existing_path",
)


def cmd_research(args: argparse.Namespace) -> int:
    """Run the research subcommand `args` names, from the project root only."""
    if args.research_handler is None:
        print(
            "Error: No operation specified. Run 'agentic-mbse research --help' for available "
            "operations.",
            file=sys.stderr,
        )
        return EXIT_USAGE
    if not Path("knowledge").is_dir():
        print(
            "Error: run 'agentic-mbse research' from the project root; "
            f"there is no knowledge/ directory in {Path.cwd()}",
            file=sys.stderr,
        )
        return EXIT_FAILURE
    handler: Callable[[argparse.Namespace], int] = args.research_handler
    return handler(args)


# --- the run -------------------------------------------------------------------------


def _open(args: argparse.Namespace) -> int:
    result = open_run(args.request, override_reason=args.override_reason)
    print(result.message)
    if result.run_dir is not None:
        print(result.run_dir)
    return OPEN_EXIT_CODES[result.outcome]


def _log(args: argparse.Namespace) -> int:
    if args.candidate is not None and args.triage is None:
        _print_error("--candidate requires --triage")
        return EXIT_USAGE
    if args.failure is not None and not args.reason:
        _print_error("--failure requires --reason")
        return EXIT_USAGE
    try:
        _log_step(args)
    except SeamError as error:
        _print_error(error)
        return EXIT_FAILURE
    return EXIT_SUCCESS


def _log_step(args: argparse.Namespace) -> None:
    """Record the one step the mutually exclusive flags name."""
    if args.search is not None:
        log_search(args.run_dir, args.search)
    elif args.candidate is not None:
        log_candidate(args.run_dir, args.candidate, args.triage, args.note)
    elif args.failure is not None:
        log_failure(args.run_dir, args.failure, args.reason, args.disposition)
    else:
        log_fault(args.run_dir, args.fault)


def _close(args: argparse.Namespace) -> int:
    try:
        returned = close(args.run_dir, adequacy=args.adequacy)
    except SeamError as error:
        _print_error(error)
        return EXIT_FAILURE
    print(json.dumps(returned, indent=2))
    return EXIT_SUCCESS


# --- the registry ----------------------------------------------------------------------


def _register(args: argparse.Namespace) -> int:
    # A receipt must land in a run `open` created, never in a directory it would make up.
    if args.run_dir is not None and not is_run_dir(args.run_dir):
        _print_error(f"{args.run_dir} is not a run directory — no {RUN_META}")
        return EXIT_FAILURE
    source = (
        UrlSource(url=args.url) if args.url is not None else LocalPdfSource(path=args.local_pdf)
    )
    metadata = SourceMetadata(
        title=args.title, use_for=args.use_for, validation=args.validation, caveat=args.caveat
    )
    try:
        result = register(
            source, metadata, budget=args.budget, run_dir=args.run_dir, triage=args.triage
        )
    except RegistrationError as error:
        _print_error(error)
        return EXIT_FAILURE
    except subprocess.TimeoutExpired as error:
        _print_error(f"capture timed out, nothing registered: {error}")
        return EXIT_FAILURE
    print(json.dumps(_registration_payload(result), indent=2))
    return EXIT_SUCCESS if result.outcome == "registered" else EXIT_FAILURE


def _registration_payload(result: RegistrationResult) -> dict[str, Any]:
    """The outcome, then every set field in `REGISTRATION_FIELDS` order, then any offsets."""
    payload: dict[str, Any] = {"outcome": result.outcome}
    for field in REGISTRATION_FIELDS:
        value = getattr(result, field)
        if value:
            payload[field] = value
    if result.offsets:
        payload["offsets"] = list(result.offsets)
    return payload


def _retire(args: argparse.Namespace) -> int:
    try:
        result = retire(args.slug, args.reason)
    except RetirementError as error:
        _print_error(error)
        return EXIT_FAILURE
    if result.outcome != "retired":
        print(json.dumps(_retirement_refusal_payload(result), indent=2))
        return EXIT_FAILURE
    _print_retirement(result)
    return EXIT_SUCCESS


def _retirement_refusal_payload(result: RetirementResult) -> dict[str, Any]:
    payload: dict[str, Any] = {"outcome": result.outcome, "reason": result.reason}
    if result.rule_id:
        payload["rule_id"] = result.rule_id
        payload["offsets"] = list(result.offsets)
    if result.references:
        payload["references"] = list(result.references)
    return payload


def _print_retirement(result: RetirementResult) -> None:
    """Print what the retirement removed and the `RETIRED.jsonl` line it recorded."""
    removed, line = result.removed, result.retired_line
    assert removed is not None and line is not None  # a `retired` result carries both
    print(f"retired {result.slug}")
    print(f"  removed manifest row:   {json.dumps(removed['manifest_row'])}")
    print(f"  removed source dir:     {removed['source_dir']}")
    print(
        f"  removed raw copy:       {removed['raw_copy'] or '(none stored outside the source dir)'}"
    )
    print("  removed index block:")
    for block_line in removed["index_block"].splitlines():
        print(f"    {block_line}")
    print("  RETIRED.jsonl line:")
    print(f"    {json.dumps(line)}")


def _verify(args: argparse.Namespace) -> int:
    report = verify(default_paths())
    for finding in report.findings:
        print(format_finding(finding))
    faults = sum(1 for finding in report.findings if finding.klass == "fault")
    legacy = sum(1 for finding in report.findings if finding.klass == "legacy")
    print(f"\n{faults} fault(s), {legacy} legacy entry(ies)")
    return EXIT_FAILURE if report.has_faults else EXIT_SUCCESS


# --- hand-curated entries ----------------------------------------------------------------


def _sources(args: argparse.Namespace) -> int:
    paths = default_paths()
    if not paths.index.is_file():
        _print_error(f"source index missing: {paths.index}")
        return EXIT_FAILURE
    for entry in list_entries(paths):
        print(
            f"{entry.label} {entry.type or '(no type)'} {entry.title} — "
            f"{entry.location or '(no location)'}"
        )
    return EXIT_SUCCESS


def _add_entry(args: argparse.Namespace) -> int:
    entry = HandCuratedEntry(
        title=args.title,
        type=args.type,
        location=args.location,
        use_for=args.use_for,
        validation=args.validation,
    )
    write = replace_entry if args.replace else add_entry
    return _report_entry(write(entry))


def _remove_entry(args: argparse.Namespace) -> int:
    return _report_entry(remove_entry(args.title))


def _report_entry(result: EntryResult) -> int:
    """Print the outcome and reason, plus the rule and offsets of a hold-out hit."""
    payload: dict[str, Any] = {"outcome": result.outcome, "reason": result.reason}
    if result.rule_id:
        payload["rule_id"] = result.rule_id
        payload["offsets"] = list(result.offsets)
    print(json.dumps(payload, indent=2))
    return EXIT_SUCCESS if result.outcome in ENTRY_WRITES else EXIT_FAILURE


def _print_error(message: object) -> None:
    print(f"Error: {message}", file=sys.stderr)


# --- registration ------------------------------------------------------------------------


def register_research_subcommands(subparsers: argparse._SubParsersAction) -> None:
    """Register the `research` subcommand group: the seam's run, the registry, and the index's hand-curated entries."""
    research = subparsers.add_parser(
        "research",
        help="Acquire sources into knowledge/ and maintain the source registry",
        description=(
            "Run from the project root (the directory holding knowledge/). open, log and close "
            "keep a research run's record and compute its class. register and retire are the "
            "only way a source enters or leaves knowledge/sources/, and verify reports where the "
            "registry disagrees with itself. sources, add-entry and remove-entry list the source "
            "index and manage its hand-curated entries."
        ),
    )
    research.set_defaults(func=cmd_research, research_handler=None)
    subs = research.add_subparsers(dest="operation")

    p = subs.add_parser("open", help="Validate a request file and open a run directory")
    p.add_argument(
        "request", type=Path, help="The request file, e.g. knowledge/research/requests/REQ-001.json"
    )
    p.add_argument(
        "--override-reason",
        help="Why this request is searched again despite a recorded bounded negative; "
        "recorded on the negative",
    )
    p.set_defaults(research_handler=_open)

    p = subs.add_parser("log", help="Record one step of a run")
    p.add_argument("run_dir", type=Path, help="The run directory `open` printed")
    step = p.add_mutually_exclusive_group(required=True)
    step.add_argument("--search", help="A query that was run")
    step.add_argument("--candidate", help="A candidate reference that was triaged")
    step.add_argument("--failure", help="A candidate reference that could not be brought in")
    step.add_argument("--fault", help="A run-scoped fault: the seam could not proceed")
    p.add_argument("--triage", choices=get_args(Triage), help="Required with --candidate")
    p.add_argument("--note", default="", help="Free text for --candidate")
    p.add_argument("--reason", default="", help="Required with --failure")
    p.add_argument(
        "--disposition",
        choices=FAILURE_DISPOSITIONS,
        default="queued",
        help="With --failure: 'queued' hands the candidate to a person (default; a paywall, a "
        "login wall, a repeated fetch failure); 'closed' records it in the bounded negative "
        "instead",
    )
    p.set_defaults(research_handler=_log)

    p = subs.add_parser("close", help="Compute the run's class and write its return.json")
    p.add_argument("run_dir", type=Path, help="The run directory `open` printed")
    p.add_argument(
        "--adequacy",
        choices=get_args(Adequacy),
        default="exhausted",
        help="Why the search is considered adequate (default: exhausted)",
    )
    p.set_defaults(research_handler=_close)

    p = subs.add_parser("register", help="Capture and register one URL or local PDF")
    origin = p.add_mutually_exclusive_group(required=True)
    origin.add_argument("--url", help="URL to fetch and register")
    origin.add_argument("--local-pdf", type=Path, help="Local PDF to register")
    p.add_argument("--title", required=True, help="Title for the index entry and the slug")
    p.add_argument(
        "--use-for",
        required=True,
        help="What this source establishes, and which question it serves",
    )
    p.add_argument("--validation", required=True, help="How a reader checks its numbers")
    p.add_argument("--caveat", required=True, help="What limits its authority")
    p.add_argument(
        "--budget",
        type=float,
        default=DEFAULT_BUDGET,
        help=f"Claude budget in USD for extraction (default {DEFAULT_BUDGET})",
    )
    p.add_argument(
        "--run",
        dest="run_dir",
        type=Path,
        help="The run directory; the attempt leaves a receipt there and counts against the "
        "run's max_captures",
    )
    p.add_argument(
        "--triage",
        choices=get_args(Triage),
        default="keeper",
        help="The triage decision recorded on the receipt (default: keeper)",
    )
    p.set_defaults(research_handler=_register)

    p = subs.add_parser(
        "retire",
        help="Retire one registered source: remove its manifest row, index entry, source "
        "directory and raw copy together, and record the removal in knowledge/RETIRED.jsonl",
    )
    p.add_argument("--slug", required=True, help="The registry slug to retire")
    p.add_argument(
        "--reason", required=True, help="Why it is retired; recorded verbatim in RETIRED.jsonl"
    )
    p.set_defaults(research_handler=_retire)

    p = subs.add_parser("verify", help="Report registry drift. Never repairs, never writes.")
    p.set_defaults(research_handler=_verify)

    p = subs.add_parser(
        "sources",
        help="List every source index entry, labelled registered, hand-curated or unregistered",
    )
    p.set_defaults(research_handler=_sources)

    p = subs.add_parser(
        "add-entry",
        help="Add a hand-curated entry for a source the registry cannot capture, or rewrite "
        "one with --replace",
    )
    p.add_argument("--title", required=True, help="The entry's heading")
    p.add_argument("--type", required=True, help=f"One of: {', '.join(HAND_CURATED_TYPES)}")
    p.add_argument("--location", required=True, help="Path or URL; never under knowledge/sources/")
    p.add_argument("--use-for", required=True, help="What the source is used for")
    p.add_argument("--validation", required=True, help="How its content is checked")
    p.add_argument(
        "--replace",
        action="store_true",
        help="Rewrite the one hand-curated entry with this title instead of adding one",
    )
    p.set_defaults(research_handler=_add_entry)

    p = subs.add_parser("remove-entry", help="Remove a hand-curated entry by its title")
    p.add_argument("--title", required=True, help="The entry's heading")
    p.set_defaults(research_handler=_remove_entry)
