"""Properties of the shipped text: each bundle's envelope, and what installed text points at."""

import re
import subprocess
from argparse import Namespace
from pathlib import Path

import pytest
import tomllib

from agentic_mbse.cli import TOOL_OWNED_TEMPLATES, cmd_init
from agentic_mbse.validation.positional_check import PINNED_DISCLAIMER
from tests.helpers.shipped import REPO_ROOT, SKILLS, frontmatter

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


def test_register_states_its_limits_and_links_the_filed_upstream_finding():
    text = register_text()
    assert "placeholder target" in text  # the unresolved-reference test and its verified shapes
    assert "SysIDE 0.8.4" in text
    assert "evidence/upstream-codegen-finding.md`. It was filed on 2026-10-22" in text
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


# ---- Level 6 and the execution target ---------------------------------------------------------

L6_DOCS = ("README.md", "skills/model-validation/SKILL.md")
#: Words that would claim L6 says a model generates.
L6_BANNED = (
    "generated-ready",
    "generation-ready",
    "ready to generate",
    "will generate",
    "generator accepts",
    "readiness",
)


@pytest.mark.parametrize("relative", L6_DOCS)
def test_doc_says_l6_is_not_the_generation_answer_and_what_the_setting_does(relative):
    text = " ".join((REPO_ROOT / relative).read_text(encoding="utf-8").split())
    lowered = text.lower()
    assert "sysml-codegen check" in text
    assert "execution-target" in text and "init --execution-target" in text
    assert "targets generated code" in lowered
    assert "one info summary" in lowered
    assert [banned for banned in L6_BANNED if banned in lowered] == []


def test_model_validation_names_the_generation_check():
    text = " ".join(
        (REPO_ROOT / "skills/model-validation/SKILL.md").read_text(encoding="utf-8").split()
    )
    assert "does not exist yet" not in text
    assert "uv run sysml-codegen check --models models/" in text
    assert "the generation answer comes from `sysml-codegen check`" in text
    assert "never as fine" in text
    assert "“Generated code” in `modeling_project/MODELING_PROCESS.md`" in text


def test_model_validation_table_row_uses_the_l6_title():
    text = (REPO_ROOT / "skills/model-validation/SKILL.md").read_text(encoding="utf-8")
    (row,) = [line for line in text.splitlines() if line.startswith("| 6 ")]
    assert "Architecture & Conventions" in row and "not a generation check" in row


@pytest.mark.parametrize(
    "relative",
    (
        "README.md",
        "CLAUDE.md",
        "skills/model-validation/SKILL.md",
        "skills/toolkit-awareness/SKILL.md",
    ),
)
def test_doc_says_every_l6_run_ends_with_the_generation_pointer(relative):
    text = " ".join((REPO_ROOT / relative).read_text(encoding="utf-8").split())
    assert re.search(
        r"every run that includes (L6|Level 6 \(Architecture & Conventions\)) ends", text, re.I
    )
    assert "Codegen Conventions" not in text


def test_claude_md_level_6_line_uses_the_l6_title():
    text = (REPO_ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    (line,) = [line for line in text.splitlines() if line.strip().startswith("- Level 6:")]
    assert "Architecture & Conventions" in line and "readiness" not in line
    assert "sysml-codegen check" in line


def test_research_seam_describes_shared_key_set():
    text = (REPO_ROOT / "docs/research-seam.md").read_text(encoding="utf-8")
    assert "holds only `research` and `execution-target`" in text
    assert "a key other than `research` or `execution-target` in `[tool.agentic-mbse]`" in text
    assert "holds only `research`," not in text


# ---- The generator's three structural limits ----------------------------------------------------

LIMITS_GUIDANCE = (
    "project_templates/MODELING_GUIDE.md.template",
    "skills/sysml-conventions/SKILL.md",
)
LIMIT_LEADS = (
    "**1. An `assert constraint` goes on a part, not inside a calculation.**",
    "**2. Part multiplicities are exact.**",
    "**3. A calculation input receives one value.**",
)


@pytest.mark.parametrize("relative", LIMITS_GUIDANCE)
def test_guidance_states_the_three_generator_limits(relative):
    text = (REPO_ROOT / relative).read_text(encoding="utf-8")
    assert "## Three Structures the Code Generator Refuses" in text
    for lead in LIMIT_LEADS:
        assert lead in text
    assert text.count("// Correct") >= 3 and text.count("// Incorrect") >= 3
    # Probe g4: the generator refuses a list-valued attribute that nothing reads.
    assert "A list-valued attribute is refused even when no calculation reads it" in text


ASSERT_STOPS_NOTHING = "A failed assert does not stop anything."


@pytest.mark.parametrize("relative", LIMITS_GUIDANCE)
def test_guidance_says_a_failed_assert_stops_nothing(relative):
    # Evidence: generated-results-guidance evidence/risk1-reruns.md, the violated-assert run.
    text = (REPO_ROOT / relative).read_text(encoding="utf-8")
    assert ASSERT_STOPS_NOTHING in text
    assert "must check the constraint verdicts before using the numbers" in text


# Each place that teaches a conditional or a library function the generator refuses
# (evidence/risk1-reruns.md: check refused both conditional forms and `min`).
CHECK_FIRST = (
    "project_templates/MODELING_GUIDE.md.template",
    "skills/sysml-conventions/SKILL.md",
    "docs/patterns/conditionals.md",
    "docs/patterns/syntax-reference.md",
    "agents/kerml-expert.md",
    "agents/sysmlv2-validator.md",
)


@pytest.mark.parametrize("relative", CHECK_FIRST)
def test_conditional_and_function_teaching_says_run_check_first(relative):
    text = (REPO_ROOT / relative).read_text(encoding="utf-8")
    assert "The code generator does not accept" in text
    assert "run `sysml-codegen check` before relying on" in text


def test_pattern_docs_state_the_limits_in_place():
    constraints = (REPO_ROOT / "docs/patterns/constraints.md").read_text(encoding="utf-8")
    assert "### Checking a Calculation's Result: Assert on the Part" in constraints
    calculations = (REPO_ROOT / "docs/patterns/adr002-calculations.md").read_text(encoding="utf-8")
    assert "## Calculation Inputs and Part Counts" in calculations


SYSML_FENCE = re.compile(r"```sysml\n(.*?)```", re.DOTALL)
CALC_OPENER = re.compile(r"\bcalc\b[^;{]*\{")


def _calc_bodies(fence: str):
    """Each `calc def` or calc usage body in a fence, by brace matching."""
    for match in CALC_OPENER.finditer(fence):
        depth, start = 1, match.end()
        for index in range(start, len(fence)):
            depth += {"{": 1, "}": -1}.get(fence[index], 0)
            if depth == 0:
                yield match.group(0), fence[start:index]
                break


def test_no_shipped_example_teaches_an_assert_inside_a_calculation_as_correct():
    shipped = [*(REPO_ROOT / "docs/patterns").glob("*.md"), *(REPO_ROOT / "skills").rglob("*.md")]
    shipped += [
        *(REPO_ROOT / "project_templates").glob("*.template"),
        *(REPO_ROOT / "agents").glob("*.md"),
    ]
    found = []
    for path in shipped:
        for fence in SYSML_FENCE.findall(path.read_text(encoding="utf-8")):
            for opener, body in _calc_bodies(fence):
                if "assert constraint" not in body:
                    continue
                preceding = fence[: fence.index(opener)].rsplit("\n", 2)[-2:]
                if not any("Incorrect" in line for line in preceding):
                    found.append(f"{path.relative_to(REPO_ROOT)}: {opener}")
    assert found == []


# ---- The workflow runs the generator's check early ----------------------------------------------

CHECK_COMMAND = "uv run sysml-codegen check --models models/"
WORKFLOW_POINTERS = (
    "skills/design-model/SKILL.md",
    "skills/plan-model/SKILL.md",
    "skills/implement-model/SKILL.md",
    "skills/model-validation/SKILL.md",
    "skills/toolkit-awareness/SKILL.md",
)


def test_modeling_process_says_when_and_how_to_run_the_generation_check():
    text = (REPO_ROOT / "project_templates/MODELING_PROCESS.md.template").read_text(
        encoding="utf-8"
    )
    (row,) = [
        line
        for line in text.splitlines()
        if 'execution-target = "generated"' in line and line.startswith("|")
    ]
    assert "first model pieces" in row and "each phase" in row and "parked" in row
    section = text.split("## Generated code\n", 1)[1].split("\n## ", 1)[0]
    assert CHECK_COMMAND in section
    for exit_line in ("**Exit 0:**", "**Exit 1:**", "**Exit 2:**"):
        assert exit_line in section
    assert "**Generation parked.**" in section and "does not block" in section
    assert "**sysml-codegen missing.**" in section and "Never report it as fine" in section


@pytest.mark.parametrize("relative", WORKFLOW_POINTERS)
def test_workflow_skill_points_at_the_generation_check(relative):
    text = (REPO_ROOT / relative).read_text(encoding="utf-8")
    assert CHECK_COMMAND in text
    assert "Generated code" in text and "MODELING_PROCESS.md" in text
