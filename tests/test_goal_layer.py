"""The goal layer agentic-mbse ships: `run-goal`, `narrate-goal`, the goal runbook and templates.

The files are ported from the project that first ran the layer. The port keeps the runbook's
sections and limits (design Invariant 2), and the shipped text points at nothing in that
project (spec SC2). Provenance citations in the decision record carry `@2b1e9f9d5` and are
exempt: they cite the source project as provenance, not as authority.
"""

import re

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
