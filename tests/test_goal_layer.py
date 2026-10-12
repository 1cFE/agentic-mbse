"""The goal layer agentic-mbse ships: `run-goal`, `narrate-goal`, the goal runbook and templates.

The files are ported from the project that first ran the layer. The port keeps the runbook's
sections and limits (design Invariant 2), and the shipped text points at nothing in that
project (spec SC2). Provenance citations in the decision record carry `@2b1e9f9d5` and are
exempt: they cite the source project as provenance, not as authority.

`init` installs the layer into every target (spec SC1). Its narrative-link test must run from a
copy and from an `init --dev` link (design D9).
"""

import re
import subprocess
import sys
from argparse import Namespace
from pathlib import Path

import pytest

from agentic_mbse.cli import cmd_init
from tests.helpers.shipped import REPO_ROOT

GOAL_SOURCES = [
    "skills/run-goal/SKILL.md",
    "skills/narrate-goal/SKILL.md",
    "project_templates/GOAL_RUNBOOK.md.template",
    "project_templates/goal.md.template",
    "project_templates/trail.md.template",
    "project_templates/learnings.md.template",
]
SC2 = re.compile(
    r"fusion-tea|MR-[0-9]|\.codex-test|stellarator|exploration/|\.claude/|/home/|research_seam"
    r"|source_registry|integrate\.py|STUDY_POLICY|holdout|ARIES|aries-cs|demo-depth-rubric"
    r"|depth target|GSTH|WI-0[0-9]"
)
RUNBOOK_H2 = [  # the source runbook's H2s, in order (Invariant 2)
    "What this is, and what it is not",
    "The five surfaces",
    'What "fresh" means',
    "Review scope and evidence reuse",
    "Grounding a goal",
    "Opening and closing a round",
    "Running one task",
    "The pre-execution disposition checkpoint",
    "The fresh review",
    "Timing of review coverage",
    "When a cited artifact moves",
    "Resuming an interruption",
    "Limits",
    "The discovery log",
    "The native seams",
    "The decisions behind this",
]
GOAL_FILES = [
    "work/orchestration/GOAL_RUNBOOK.md",
    "work/orchestration/goal-templates/goal.md",
    "work/orchestration/goal-templates/trail.md",
    "work/orchestration/goal-templates/learnings.md",
    "tests/orchestration/test_narrative_links.py",
]


def test_goal_text_points_at_nothing_in_fusion_tea():
    for path in GOAL_SOURCES:
        for n, line in enumerate((REPO_ROOT / path).read_text(encoding="utf-8").splitlines(), 1):
            if "@2b1e9f9d5" in line:  # a provenance citation in the decision record
                continue
            assert not SC2.search(line), f"{path}:{n}"
            assert ".project/" not in line or "for example" in line, f"{path}:{n}"


def test_runbook_keeps_its_sections_and_limits():
    text = (REPO_ROOT / "project_templates/GOAL_RUNBOOK.md.template").read_text(encoding="utf-8")
    assert re.findall(r"^## (.+)$", text, re.M) == RUNBOOK_H2
    assert all(v in text for v in ("**2 retries**", "**2 revisions**", "**6 rounds**"))


def test_goal_close_heading_is_named():
    trail = (REPO_ROOT / "project_templates/trail.md.template").read_text(encoding="utf-8")
    assert "## Goal close — YYYY-MM-DD" in trail


def init(target: Path, assistant: str = "both", dev: bool = False) -> None:
    assert cmd_init(Namespace(path=str(target), force=False, dev=dev, assistant=assistant)) == 0


@pytest.mark.parametrize("assistant", ["claude", "codex", "both"])
def test_init_installs_the_goal_layer(tmp_path, assistant):
    init(tmp_path, assistant)
    for skill in ("run-goal", "narrate-goal"):
        assert (tmp_path / ".agents/skills" / skill / "SKILL.md").is_file(), skill
    for path in GOAL_FILES:
        assert (tmp_path / path).is_file(), path
    assert (tmp_path / "work/orchestration/goals").is_dir()
    assert (tmp_path / "work/narratives").is_dir()


def test_dev_links_goal_files_and_ignores_them(tmp_path):
    init(tmp_path, dev=True)
    for path in GOAL_FILES:
        assert (tmp_path / path).is_symlink(), path
    ignored = (tmp_path / ".gitignore").read_text().splitlines()
    assert {
        "work/orchestration/GOAL_RUNBOOK.md",
        "work/orchestration/goal-templates/",
        "tests/orchestration/test_narrative_links.py",
    } <= set(ignored)


def run_narrative_test(target: Path) -> subprocess.CompletedProcess[str]:
    command = [
        *(sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"),
        "tests/orchestration/test_narrative_links.py",
    ]
    return subprocess.run(command, cwd=target, capture_output=True, text=True)


@pytest.mark.parametrize("dev", [False, True])
def test_narrative_link_test_fails_then_passes_in_the_target(tmp_path, dev):
    """Under --dev the test is a link into this repo; a root resolved through it misses the target."""
    init(tmp_path, dev=dev)
    (tmp_path / "work/narratives/n.md").write_text("[e](../orchestration/goals/g/e.md)\n")
    broken = run_narrative_test(tmp_path)
    assert broken.returncode == 1, broken.stdout
    assert "unresolved link ../orchestration/goals/g/e.md" in broken.stdout
    (tmp_path / "work/orchestration/goals/g").mkdir()
    (tmp_path / "work/orchestration/goals/g/e.md").write_text("e\n")
    fixed = run_narrative_test(tmp_path)
    assert fixed.returncode == 0, fixed.stdout
