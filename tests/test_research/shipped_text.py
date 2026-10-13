"""Reading the shipped research text: its sections, its fenced blocks and the CLI calls it shows."""

import argparse
import re
import shlex

from agentic_mbse.cli.research_cli import register_research_subcommands

#: An `agentic-mbse research` call inside a shell line, up to a pipe or a closing `$(…)`.
_RESEARCH_CALL = re.compile(r"agentic-mbse research ([^|)\n]*)")


def section(text: str, heading: str) -> str:
    """The Markdown section opened by the line `heading`, up to the next heading of its level or higher."""
    lines = text.splitlines()
    start = lines.index(heading)
    level = len(heading) - len(heading.lstrip("#"))
    end = next(
        (
            i
            for i in range(start + 1, len(lines))
            if re.match(rf"#{{1,{level}}} ", lines[i]) and not _inside_fence(lines, i)
        ),
        len(lines),
    )
    return "\n".join(lines[start:end])


def _inside_fence(lines: list[str], index: int) -> bool:
    return sum(1 for line in lines[:index] if line.startswith("```")) % 2 == 1


def fenced_blocks(text: str, language: str) -> list[str]:
    """The bodies of the fenced code blocks tagged `language`, in order."""
    return re.findall(rf"^```{language}\n(.*?)^```", text, flags=re.MULTILINE | re.DOTALL)


def research_invocations(text: str) -> list[list[str]]:
    """The argument lists of every `agentic-mbse research` call in the text's bash blocks."""
    calls = []
    for block in fenced_blocks(text, "bash"):
        joined = block.replace("\\\n", " ")
        for line in joined.splitlines():
            if line.lstrip().startswith("#"):
                continue
            calls += [shlex.split(match) for match in _RESEARCH_CALL.findall(line)]
    return calls


def research_parser() -> argparse.ArgumentParser:
    """A parser holding only the `research` subcommands, as the CLI registers them."""
    parser = argparse.ArgumentParser(prog="agentic-mbse")
    register_research_subcommands(parser.add_subparsers(dest="command"))
    return parser
