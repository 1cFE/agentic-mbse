#!/usr/bin/env python3
"""Context window measurement for D2.4.

Measures token counts for skills, references, and commands to inform
loading strategy decisions (Q9, Q10, Q11).

Uses tiktoken cl100k_base as a proxy for Claude's tokenizer.
"""

import os
from pathlib import Path

import tiktoken

ROOT = Path(__file__).resolve().parents[3]  # agentic-mbse repo root
SKILLS_DIR = ROOT / "claude" / "skills"
COMMANDS_DIR = ROOT / "claude" / "commands"

enc = tiktoken.get_encoding("cl100k_base")

# Command-skill dependency table from components.md
COMMAND_SKILLS: dict[str, list[str]] = {
    "spec-model": ["project-structure", "source-traceability"],
    "design-model": ["sysml-conventions", "project-structure", "model-validation", "source-traceability"],
    "plan-model": ["model-validation"],
    "implement-model": ["sysml-conventions", "model-validation", "project-structure"],
    "audit-models": ["model-validation", "source-traceability", "requirements-tracking"],
    "research": ["source-traceability"],
    "quick-model": ["sysml-conventions", "model-validation"],
    "review-model": ["sysml-conventions", "model-validation", "project-structure", "requirements-tracking"],
    "analyze-models": ["project-structure", "model-validation"],
    "status": ["epic-decomposition", "requirements-tracking"],
    "backlog": ["epic-decomposition"],
    "onboard": ["project-structure", "source-traceability", "epic-decomposition"],
    "formalize-intent": ["project-structure"],
    "manage-sources": ["source-traceability"],
}


def count_tokens(path: Path) -> int:
    text = path.read_text()
    return len(enc.encode(text))


def count_lines(path: Path) -> int:
    return len(path.read_text().splitlines())


def measure_skills() -> dict[str, dict]:
    """Measure each skill's SKILL.md and references."""
    results = {}
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        if not skill_dir.is_dir():
            continue
        name = skill_dir.name
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue

        entry = {
            "skill_tokens": count_tokens(skill_md),
            "skill_lines": count_lines(skill_md),
            "ref_tokens": 0,
            "ref_lines": 0,
            "ref_files": [],
        }

        refs_dir = skill_dir / "references"
        if refs_dir.exists():
            for ref in sorted(refs_dir.glob("*.md")):
                t = count_tokens(ref)
                l = count_lines(ref)
                entry["ref_tokens"] += t
                entry["ref_lines"] += l
                entry["ref_files"].append((ref.name, t, l))

        results[name] = entry
    return results


def measure_commands() -> dict[str, dict]:
    """Measure each command file."""
    results = {}
    for cmd in sorted(COMMANDS_DIR.glob("*.md")):
        results[cmd.stem] = {
            "tokens": count_tokens(cmd),
            "lines": count_lines(cmd),
        }
    return results


def compute_command_loads(skills: dict) -> dict[str, dict]:
    """Compute per-command skill loading costs."""
    results = {}
    for cmd, skill_names in sorted(COMMAND_SKILLS.items()):
        skill_only = sum(skills[s]["skill_tokens"] for s in skill_names if s in skills)
        with_refs = sum(
            skills[s]["skill_tokens"] + skills[s]["ref_tokens"]
            for s in skill_names
            if s in skills
        )
        results[cmd] = {
            "skills": skill_names,
            "skill_count": len(skill_names),
            "skill_tokens": skill_only,
            "total_tokens": with_refs,
        }
    return results


def print_markdown(skills: dict, commands: dict, loads: dict):
    # Table 1: Per-skill token counts
    print("## Table 1: Per-Skill Token Counts\n")
    print("| Skill | Lines | SKILL.md Tokens | Ref Tokens | Total Tokens |")
    print("|-------|------:|----------------:|-----------:|-------------:|")
    total_skill = total_ref = 0
    for name, d in sorted(skills.items()):
        total = d["skill_tokens"] + d["ref_tokens"]
        total_skill += d["skill_tokens"]
        total_ref += d["ref_tokens"]
        ref_str = str(d["ref_tokens"]) if d["ref_tokens"] else "—"
        print(f"| {name} | {d['skill_lines']} | {d['skill_tokens']:,} | {ref_str} | {total:,} |")
    print(f"| **TOTAL** | | **{total_skill:,}** | **{total_ref:,}** | **{total_skill + total_ref:,}** |")

    # Table 1b: Reference file detail
    has_refs = any(d["ref_files"] for d in skills.values())
    if has_refs:
        print("\n### Reference File Detail\n")
        print("| Skill | Reference File | Lines | Tokens |")
        print("|-------|---------------|------:|-------:|")
        for name, d in sorted(skills.items()):
            for fname, t, l in d["ref_files"]:
                print(f"| {name} | {fname} | {l} | {t:,} |")

    # Table 2: Current command token counts (baseline)
    print("\n## Table 2: Current Command Token Counts (Baseline)\n")
    print("| Command | Lines | Tokens |")
    print("|---------|------:|-------:|")
    total_cmd = 0
    for name, d in sorted(commands.items()):
        total_cmd += d["tokens"]
        print(f"| /{name} | {d['lines']} | {d['tokens']:,} |")
    print(f"| **TOTAL** | | **{total_cmd:,}** |")

    # Table 3: Per-command skill load
    print("\n## Table 3: Per-Command Skill Load\n")
    print("| Command | # Skills | Skills (SKILL.md only) | Skills + Refs | Current Command |")
    print("|---------|:--------:|-----------------------:|--------------:|----------------:|")
    for name, d in sorted(loads.items()):
        cmd_tokens = commands.get(name, {}).get("tokens", "—")
        cmd_str = f"{cmd_tokens:,}" if isinstance(cmd_tokens, int) else cmd_tokens
        print(f"| /{name} | {d['skill_count']} | {d['skill_tokens']:,} | {d['total_tokens']:,} | {cmd_str} |")

    # Table 4: Projected total (command + skills) vs current
    print("\n## Table 4: Projected Total Context vs Current (Command + Skills)\n")
    print("| Command | Current Tokens | Projected Command (~250) | + Skills | Projected Total | Delta |")
    print("|---------|---------------:|-------------------------:|---------:|----------------:|------:|")
    projected_cmd = 250  # target ~200-300 lines ≈ ~250 token avg placeholder
    for name, d in sorted(loads.items()):
        current = commands.get(name, {}).get("tokens")
        if current is None:
            continue
        # Use a rough estimate: refactored command ≈ 30-50% of current
        # since extracted knowledge goes to skills
        projected_cmd_tokens = int(current * 0.4)  # conservative: 40% remains
        proj_total = projected_cmd_tokens + d["skill_tokens"]
        delta = proj_total - current
        pct = (delta / current * 100) if current else 0
        print(f"| /{name} | {current:,} | {projected_cmd_tokens:,} | {d['skill_tokens']:,} | {proj_total:,} | {delta:+,} ({pct:+.0f}%) |")

    # Summary stats
    print("\n## Summary Statistics\n")
    all_skill_tokens = [d["skill_tokens"] for d in skills.values()]
    all_load_tokens = [d["skill_tokens"] for d in loads.values()]
    print(f"- **Skills count**: {len(skills)}")
    print(f"- **Total SKILL.md tokens**: {total_skill:,}")
    print(f"- **Total reference tokens**: {total_ref:,}")
    print(f"- **Min skill tokens**: {min(all_skill_tokens):,}")
    print(f"- **Max skill tokens**: {max(all_skill_tokens):,}")
    print(f"- **Mean skill tokens**: {sum(all_skill_tokens) // len(all_skill_tokens):,}")
    print(f"- **Max command skill load (SKILL.md only)**: {max(all_load_tokens):,}")
    print(f"- **Max command skill load (with refs)**: {max(d['total_tokens'] for d in loads.values()):,}")
    print(f"- **Total current command tokens**: {total_cmd:,}")

    # Decision criteria check
    print("\n## Decision Criteria Check\n")
    all_under_200 = all(d["skill_lines"] <= 200 for d in skills.values())
    max_load = max(all_load_tokens)
    print(f"- All SKILL.md < 200 lines? **{'YES' if all_under_200 else 'NO'}**")
    if not all_under_200:
        over = [(n, d["skill_lines"]) for n, d in skills.items() if d["skill_lines"] > 200]
        for n, l in over:
            print(f"  - {n}: {l} lines")
    print(f"- Max command skill load: **{max_load:,} tokens**")
    print(f"- Max load < 4,000 tokens? **{'YES' if max_load < 4000 else 'NO'}**")

    if all_under_200 and max_load < 4000:
        print("\n**→ DECISION: Load skills upfront. No staging needed.**")
    elif max_load < 4000:
        print("\n**→ DECISION: Move overflow skills to references, keep upfront loading.**")
    elif max_load > 4000:
        print("\n**→ DECISION: Stage skills by phase.**")


if __name__ == "__main__":
    skills = measure_skills()
    commands = measure_commands()
    loads = compute_command_loads(skills)
    print_markdown(skills, commands, loads)
