"""Properties of the shipped text: each bundle's envelope, and what installed text points at."""

import re
import subprocess
from argparse import Namespace
from pathlib import Path

import pytest
import tomllib

from agentic_mbse.cli import TOOL_OWNED_TEMPLATES, cmd_init
from agentic_mbse.validation.positional_check import PINNED_DISCLAIMER
from agentic_mbse.validation.subset_presentation import PACKAGED_RULES
from tests.helpers.shipped import REPO_ROOT, SKILLS, frontmatter
from tests.test_validation.test_l6_contract import BANNED as L6_BANNED

SLASH_REFERENCE = re.compile(r"`(/[a-z0-9-]+)`")
SKILL_PATH = re.compile(r"\.agents/skills/([a-z0-9-]+)((?:/[\w.-]+)*)")


@pytest.mark.parametrize("skill", SKILLS)
def test_bundle_declares_its_name_description_and_kind(skill):
    meta, _ = frontmatter(REPO_ROOT / "skills" / skill / "SKILL.md")
    assert meta["name"] == skill
    assert meta["description"]
    assert meta["metadata"]["kind"] in ("workflow", "supporting")
    assert "skills" not in meta


def test_every_bundle_opens_with_one_shared_preface():
    first_paragraphs = {
        frontmatter(REPO_ROOT / "skills" / skill / "SKILL.md")[1].lstrip("\n").split("\n\n")[0]
        for skill in SKILLS
    }
    assert len(first_paragraphs) == 1


@pytest.fixture(scope="module")
def installed(tmp_path_factory: pytest.TempPathFactory) -> Path:
    target = tmp_path_factory.mktemp("installed")
    assert cmd_init(Namespace(path=str(target), force=False, dev=False, assistant="both")) == 0
    return target


def runtime_neutral_text(target: Path) -> dict[str, str]:
    """Installed text both runtimes read: bundles, tool-owned templates, Codex role instructions."""
    texts = {
        p.relative_to(target).as_posix(): p.read_text(encoding="utf-8")
        for p in (target / ".agents/skills").rglob("*")
        if p.is_file()
    }
    for _, destination in TOOL_OWNED_TEMPLATES:
        texts[destination] = (target / destination).read_text(encoding="utf-8")
    for role in (target / ".codex/agents").glob("*.toml"):
        texts[role.relative_to(target).as_posix()] = tomllib.loads(role.read_text())[
            "developer_instructions"
        ]
    return texts


def test_installed_references_name_installed_skills(installed):
    """The deletion guard: removing a skill that other text names fails here."""
    bundles = {p.parent.name for p in (installed / ".agents/skills").glob("*/SKILL.md")}
    texts = runtime_neutral_text(installed)
    for p in [
        *(installed / ".agentic-mbse").glob("*.md"),
        *(installed / ".claude/agents").glob("*.md"),
    ]:
        texts[p.relative_to(installed).as_posix()] = p.read_text(encoding="utf-8")
    for path, text in texts.items():
        for reference in SLASH_REFERENCE.findall(text):
            assert reference[1:] in bundles, f"{path} names `{reference}`"
        for name, inside in SKILL_PATH.findall(text):
            assert name in bundles, f"{path} names .agents/skills/{name}"
            named = installed / ".agents/skills" / name / inside.strip("/").rstrip(".")
            assert named.exists(), f"{path} names {named.relative_to(installed)}"


def test_runtime_neutral_text_names_no_claude_path(installed):
    """Claude roles carry the Claude adapter, which may name .claude/; nothing else may."""
    for path, text in runtime_neutral_text(installed).items():
        assert ".claude/" not in text, path


@pytest.mark.parametrize("runtime", ["claude", "codex"])
def test_adapter_keeps_a_continuing_author_and_a_fresh_independent_reviewer(installed, runtime):
    """SC3: stages do not force new agents; only independent criticism needs a non-author."""
    text = " ".join((installed / f".agentic-mbse/{runtime}.md").read_text(encoding="utf-8").split())
    sentences = re.split(r"(?<=[.;])\s+", text)
    assert not [s for s in sentences if "stage" in s.lower() and "new agent" in s.lower()]
    assert "Keep a continuing author across stages" in text
    assert "while its context remains useful" in text
    assert "Independent criticism requires a fresh non-author agent" in text
    assert "resume an author for its audit" in text


def test_guide_locates_pattern_docs_for_either_runtime(installed):
    """SC4: main's resolver text, with no Claude-only settings path."""
    guide = (installed / "modeling_project/MODELING_GUIDE.md").read_text(encoding="utf-8")
    assert "get_docs_dir()" in guide
    assert ".claude/settings.json" not in guide


# The semantic-hazard register (EXEC-SUBSET-CONTRACT Item 4, design Appendix C).

REGISTER = REPO_ROOT / "docs/patterns/semantic-hazards.md"
# A backticked path in this repository, cited without a revision (design D18).
OWN_PATH = re.compile(
    r"`((?:\.project|tests|src|docs|scripts|skills|agents|project_templates)/[^`\s]*)`"
)
# A path in a sibling repository, cited at a pinned revision: `repo@rev:path`.
SIBLING_PATH = re.compile(r"`(sysml-codegen|dc3|fusion-tea)@([0-9a-f]{7,40}):([^`\s]+)`")
# The line patterns sysml-codegen's guidance contract scans (design I8).
QUALIFIED_BINDING = re.compile(r"\bin\s+[\w']+\s*=\s*[^;=\n]*::")
SELF_NAMED = re.compile(r"\bin\s+([\w']+)\s*=\s*\1\s*[;}]")


def register_text() -> str:
    return REGISTER.read_text(encoding="utf-8")


def test_semantic_hazards_register_cites_the_kerml_constraint_and_existing_paths():
    text = register_text()
    assert "checkFeatureParameterRedefinition" in text
    assert '<a id="positional-input-binding"></a>\n## Positional input binding' in text
    cited = OWN_PATH.findall(text)
    assert cited
    for path in cited:
        assert (REPO_ROOT / path).exists(), path


def sibling_citations() -> list[tuple[str, str, str]]:
    return sorted(set(SIBLING_PATH.findall(register_text())))


@pytest.mark.parametrize("repo, rev, path", sibling_citations())
def test_register_sibling_citations_exist_at_their_revision(repo, rev, path):
    checkout = REPO_ROOT.parent / repo
    if not (checkout / ".git").exists():
        pytest.skip(f"no {repo} checkout beside this one at {checkout}")
    found = subprocess.run(
        ["git", "-C", str(checkout), "cat-file", "-e", f"{rev}:{path}"], capture_output=True
    )
    assert found.returncode == 0, f"{repo}@{rev}:{path}"


def test_register_says_a_pin_certifies_nothing_and_is_legacy_only():
    text = register_text()
    assert PINNED_DISCLAIMER in text  # the exact text the pinned WARNING carries (Pol-4)
    assert "not a value or route-parity check" in text
    assert "recorded_against" in text
    assert "A new mismatch is repaired, not pinned" in text
    assert "reserved to the project owner" in text


def test_register_states_its_limits_and_links_the_unfiled_upstream_draft():
    text = register_text()
    assert "placeholder target" in text  # the unresolved-reference test and its verified shapes
    assert "SysIDE 0.8.4" in text
    assert "evidence/upstream-codegen-finding.md`. **It is unfiled**" in text
    assert "## Candidates, not yet reproduced" in text


def test_register_has_no_line_codegen_counts_as_a_binding_site():
    for line in register_text().splitlines():
        assert not QUALIFIED_BINDING.search(line), line
        assert not SELF_NAMED.search(line), line


# Guidance that teaches calc-usage inputs links the register (Reg-2).

REGISTER_LINK = "semantic-hazards.md#positional-input-binding"
GUIDANCE = (
    "docs/patterns/plant-idiom.md",
    "skills/sysml-conventions/SKILL.md",
    "project_templates/MODELING_GUIDE.md.template",
    "agents/sysml-expert.md",
)


@pytest.mark.parametrize("relative", GUIDANCE)
def test_guidance_links_the_register_and_teaches_by_name_or_definition_order(relative):
    text = (REPO_ROOT / relative).read_text(encoding="utf-8")
    assert REGISTER_LINK in text
    assert "`:>>`" in text or "in :>> " in text
    assert "position" in text


@pytest.mark.parametrize("relative", GUIDANCE[:3])
def test_rename_advice_says_rename_the_definition_parameter(relative):
    text = " ".join((REPO_ROOT / relative).read_text(encoding="utf-8").split())
    assert "Renaming only the usage's input" in text or "renaming only the usage's input" in text


def test_plant_idiom_order_does_not_matter_is_qualified_by_its_context():
    lines = [
        line
        for line in (REPO_ROOT / "docs/patterns/plant-idiom.md").read_text().splitlines()
        if "order does not matter" in line.lower()
    ]
    assert lines
    for line in lines:
        assert "The order of a calculation usage's inputs does matter" in line, line


# ---- Level 6 and the generator subset (Item 3 Phase 10) ----------------------------------------

L6_DOCS = ("README.md", "skills/model-validation/SKILL.md")


@pytest.mark.parametrize("relative", L6_DOCS)
def test_doc_states_profile_version_scope_incompleteness_and_not_codegen_check(relative):
    text = " ".join((REPO_ROOT / relative).read_text(encoding="utf-8").split())
    lowered = text.lower()
    assert "subset-profile/v1" in text
    assert "eight implemented rules" in lowered  # what was assessed
    assert "incomplete" in lowered and "coverage limit" in lowered
    assert "not a generation check" in lowered
    assert "future step" in lowered and "does not exist yet" in lowered
    assert "sysml-codegen check" not in lowered  # the future boundary, with no command shown
    assert "execution-target" in text and "init --execution-target" in text
    assert [banned for banned in L6_BANNED if banned in lowered] == []


def test_doc_rule_count_matches_the_packaged_profile():
    assert len(PACKAGED_RULES.rules) == 8


def test_model_validation_table_row_uses_new_l6_title():
    text = (REPO_ROOT / "skills/model-validation/SKILL.md").read_text(encoding="utf-8")
    (row,) = [line for line in text.splitlines() if line.startswith("| 6 ")]
    assert "Architecture & Generator Subset" in row and "not a generation check" in row


def test_claude_md_level_6_line_uses_new_title():
    text = (REPO_ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    (line,) = [line for line in text.splitlines() if line.strip().startswith("- Level 6:")]
    assert "Architecture & Generator Subset" in line and "readiness" not in line


def test_research_seam_describes_shared_key_set():
    text = (REPO_ROOT / "docs/research-seam.md").read_text(encoding="utf-8")
    assert "holds only `research` and `execution-target`" in text
    assert "a key other than `research` or `execution-target` in `[tool.agentic-mbse]`" in text
    assert "holds only `research`," not in text
