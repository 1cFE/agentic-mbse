---
date: 2026-09-07T16:23:10-07:00
researcher: Codex
topic: "Native Claude Code and Codex support through shared skills"
tags: [research, skills, claude-code, codex, installation, portability]
status: complete
last_updated: 2026-09-07
---

# Research: Native Claude Code and Codex skills

**Research type:** Codebase / integration / architecture feasibility. **Repository baseline:** `main`, `88e2489`. **Observed clients:** Claude Code 2.1.263 and Codex CLI 0.153.4 on Linux. Platform claims below are version-sensitive.

## Research Question

[OWNER] Research what it takes for the shipped MBSE workflows to support both Claude Code and Codex natively: command-to-skill migration gotchas, every built-in feature/pattern used and its Codex equivalent, and the cleanest installation design. Use runnable spikes to confirm assumptions. [EXAMPLE] The owner's suggestion of “symlinking to multiple locations” is an installation option to investigate, not a settled design.

This concerns the product in `claude/`, installed into target modeling projects. The personal `$my-*` development skills are outside the product inventory. Existing command-refresh research concerns prompt/artifact quality; it does not settle this migration's design ([prior research](20260703-112157_command-refresh-from-agentic-project-init.md)). All recommendations below are [AGENT], not approved requirements.

## Summary

- **Native support is feasible.** All 15 shipped command files load as skills in both clients, alongside the ten existing skills. Moving files alone does not adapt tool names, native agent definitions, user questions, permissions, or hardcoded paths. See the [discovery spike](../active/spike-native-skill-install/findings.md).
- **Claude migration is mostly mechanical.** Preserve names and bodies, package supporting files, and deliberately handle visibility, duplicate legacy commands, and platform-specific metadata. Existing commands remain supported; migration is not urgent for compatibility ([Claude skills](https://code.claude.com/docs/en/skills)).
- **Codex supports the core workflow patterns:** local tools, skills, custom agents, parallel delegation, file-backed plans, web research, MCP, and hooks. Several have different interfaces or policy semantics. “Supported pattern” does not mean a Claude configuration file can be copied unchanged. The feature matrix distinguishes these cases.
- **Prefer shared authoring and shared installed skills, with small native adapters.** A project-local `.agents/skills/<name>/` tree plus per-skill `.claude/skills/<name>` relative symlinks worked in both clients and after relocation. Copies worked as a fallback.
- **Migration must fix ownership handling.** Spikes reproduced silently lost skill edits, lost protection after skipping a modified command, and forced command installation writing through symlinks. These are existing installer defects, not platform limitations ([installer findings](../active/spike-native-skill-install/installer-findings.md)).

## Evidence and Limits

Three fresh research agents inventoried shipped content, installers, and surrounding patterns. The runnable probes use isolated projects and real client discovery interfaces. They make no model/API turns. The research session itself successfully used fresh Codex subagents; this is separate from testing an installed MBSE role.

| Evidence level | Established here |
|---|---|
| Repository inspection | 15 commands, 5 expert agents, 10 skills, 1 hook, installer/package/template dependencies |
| Native-client discovery | Shared symlinks, chained symlinks, relocation, copy fallback, legacy duplicate precedence in Claude's catalog, acceptance of all 25 skill bundles |
| Executed installer behavior | Re-init edit loss and destination-symlink handling through actual CLI functions |
| Official documented capability | Codex custom TOML agents, delegation, skills, hooks, MCP and security controls; Claude migration/metadata semantics |
| Not certified here | Full modeling run, actual custom Codex role spawn, nested modeling orchestration, question UI, hook dispatch, Docling integration, external-source permissions, Windows/macOS |

The attempted Codex custom-agent probe was **inconclusive**: `debug prompt-input` returned messages without a role catalog. That does not disprove documented support. Claude registered all five rendered expert agents. See [role results](../active/spike-native-skill-install/role-results.json).

## 1. Switching Claude Commands to Skills

### File layout and migration behavior

The local spike converts each command to `<name>/SKILL.md` without changing its content. Claude lists all 15 workflows plus `pdf-analysis`, `python-debugger`, and `record-learning`. Seven reference-only skills remain hidden from the invocable command catalog. Codex lists all 25 bundles without loader errors ([probe](../active/spike-native-skill-install/probe.py), [results](../active/spike-native-skill-install/results.json)).

Claude uses the skill directory name for a project slash command. Same-name skills override legacy commands. `user-invocable: true` does not mean manual-only; `disable-model-invocation: true` controls automatic invocation. `allowed-tools` grants per-turn permissions rather than restricting the tool set. Arguments are appended when no substitution consumes them. These distinctions matter during conversion ([Claude frontmatter and invocation](https://code.claude.com/docs/en/skills#frontmatter-reference)).

[AGENT] Keep workflow names initially, remove only provably tool-owned legacy files, and make invocation policy an explicit choice. Do not add `context: fork` globally: conversational workflows need the current owner discussion, and orchestration already creates fresh stage contexts (`claude/commands/spec-model.md:57`, `onboard.md:41`, `orchestrate-modeling.md:72`).

### Metadata is not a dependency system

Every command declares `skills: [...]` in frontmatter and separately describes those skills in its body (`claude/commands/design-model.md:4`, `:19`). Claude documents `skills` as **subagent** preloading metadata, not a skill-to-skill dependency field ([subagent preloading](https://code.claude.com/docs/en/sub-agents#preload-skills-into-subagents)). The probe's deliberately missing dependency does not prevent discovery. It does not prove preloading works.

[AGENT] Retain explicit instructions to read relevant skills. Move catalog-only dependency information into standard `metadata` if it is useful to our tooling, or remove it. Avoid building a dependency resolver unless deterministic preloading is actually needed.

### Existing gotchas that conversion exposes

- **Tool naming has moved already.** Claude renamed Task to Agent; Task references in settings/agent definitions remain aliases. Refresh the literal examples during adaptation (`claude/commands/orchestrate-modeling.md:72`; [Claude tool naming](https://code.claude.com/docs/en/sub-agents#restrict-which-subagents-can-be-spawned)).
- **Nested delegation is version-sensitive.** The orchestrator creates stage agents, and several stages create experts. Current Claude supports nested subagents with a depth limit, but defaults changed across versions. Test the two-level workflow on the minimum supported version ([Claude nesting](https://code.claude.com/docs/en/sub-agents#nested-subagents), `claude/commands/design-model.md:54`).
- **Supporting files must travel with their skill.** PDF and debugger utilities, extraction notes, Python environment guidance, and SysML stencils are runtime inputs. Linking only `SKILL.md` would leave these behind (`claude/skills/pdf-analysis/SKILL.md:19`, `python-debugger/SKILL.md:13`, `sysml-conventions/SKILL.md:249`).
- **Do not assume the working directory becomes the skill directory.** Rewrite script examples to resolve from the skill's discovered location, and keep outputs in the target project. Existing debugger examples use `python scripts/...`; PDF examples use `.claude/skills/...` (`claude/skills/python-debugger/SKILL.md:17`, `pdf-analysis/SKILL.md:30`).
- **Generic names can collide with built-ins or other packages.** The shipped `status` appears in Claude's catalog, but both clients have their own status command. Actual TUI dispatch was not tested. Decide whether a targeted rename such as `model-status` is warranted; do not rename the whole catalog just for this possibility ([Claude commands](https://code.claude.com/docs/en/commands), `claude/commands/status.md:2`).
- **Broad grants deserve an intentional review.** All 15 commands currently list Bash and write tools, including analysis workflows. Keeping that field preserves authored behavior; stripping it changes approval behavior. It is not a portable security boundary (`claude/commands/analyze-models.md:5`).

## 2. Built-in Features and Patterns: Codex Compatibility

“Equivalent” means the workflow can be expressed natively. “Adapt” identifies a change needed in the shipped product. The current research environment exposes shell execution, patches, image viewing, web tools, fresh agent spawning, waiting, messaging and user-input tools; their literal names can vary by client/tool configuration.

| Feature used | Repository evidence | Codex status and required adaptation |
|---|---|---|
| Named workflow and arguments | All command headers; `backlog.md:12`, `status.md:12` | Native skills. Document `$backlog add …` rather than assuming arbitrary `/backlog` dispatch. Inputs already use prose; no argument macro conversion is needed. [Skills](https://learn.chatgpt.com/docs/build-skills) |
| Discovery / progressive loading | Ten skill descriptions; `toolkit-awareness/SKILL.md:1` | Native. Shared directories loaded in the spike. Codex uses `.agents/skills` and explicitly supports symlinked folders. [Skills](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills) |
| Explicit Skill tool reference | `claude/skills/record-learning/SKILL.md:67` | Prose instructions distinguish owner invocation from agent invocation through Claude's Skill tool. Adapt to native Codex skill selection/loading; this is not an executable API call in the source. |
| Manual vs implicit invocation | All commands `:6`; seven reference skills hide user invocation | Partial metadata parity. Codex's `agents/openai.yaml` can set `policy.allow_implicit_invocation: false`; no equivalent hiding control was established for Claude's `user-invocable: false`. The spike confirms the reference skills remain listed by Codex. [Metadata](https://learn.chatgpt.com/docs/build-skills#optional-metadata) |
| Read, Grep, Glob | All command allowlists; experts' `tools` | Equivalent file reading/search through shell and native tools. Replace tool-shaped `Read(offset=…, limit=…)` examples with intent or host-specific examples (`claude/agents/kerml-expert.md:57`). |
| Bash, Write, Edit | All command allowlists | Equivalent shell execution and file edits; use available exec/patch tools. Existing Python, `uv`, Git, pytest and PM CLI work is ordinary subprocess work, subject to the client's sandbox. |
| Parallel Explore/general-purpose agents | `research.md:37`, `design-model.md:54`, `analyze-models.md:38` | Native delegation. [AGENT] Proposed mapping: Explore → `explorer`, general-purpose → `default`, implementation → `worker` where appropriate; confirm the installed role catalog. Wait and gather results explicitly. [Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents) |
| Five named expert roles | `claude/agents/*.md:1` | Native custom agents use `.codex/agents/*.toml`, requiring `name`, `description`, `developer_instructions`. Render from common role text; Markdown agent files are not native Codex agent configs. Documented, not spawn-tested here. [Custom agents](https://learn.chatgpt.com/docs/agent-configuration/subagents#custom-agents) |
| Role tool restrictions | Expert `tools: Read, Grep, Glob`; validator `Bash, Write, Read` | Not a one-to-one mapping. A read-only Codex sandbox protects writes but does not remove shell capability. Do not describe it as the same tool allowlist. Validate any stronger restriction separately. |
| Fresh stage and audit contexts | `orchestrate-modeling.md:72`, `:85`, `:109` | Supported pattern. In this Codex host, use fresh spawning with `fork_turns: "none"`; never substitute a full-history fork or resume. Exact tool parameters belong in the Codex adapter, not shared domain prose. |
| Nested stages and experts | `orchestrate-modeling.md:72` → `research.md:37` / `design-model.md:54` | Supported by this host's collaboration interface. Native release testing must exercise this depth and configured concurrency. Queue excess work; “run four checks in parallel” need not mean four simultaneous slots. |
| Parent-mediated owner decisions | `orchestrate-modeling.md:79`, `:129` | Portable instruction policy: child returns blockers, parent decides routine execution details, reserved owner decisions remain reserved. Preserve this behavior when translating tools. |
| Interactive questions and approval | `manage-sources.md:29`, `:42`, `audit-models.md:107`, `record-learning/SKILL.md:63` | Equivalent conversational behavior, not identical widget API. Use the available Codex question tool only where supported; otherwise ask in text and wait. This session has mode-dependent synchronous input plus asynchronous input. Do not bake either UI into domain requirements. |
| Deliberate text questions | `onboard.md:41` | Already portable; preserve the request to answer naturally. Do not mechanically replace every question with a structured widget. |
| Durable task tracking / resume | `implement-model.md:33`, `:46`; `plan-model.md:93`; `orchestrate-modeling.md:43` | Portable files and checkboxes. No shipped TodoWrite or TaskCreate/Update dependency exists. Keep artifact evidence as the resume source. |
| WebSearch and WebFetch | `research.md:5`, `:53`; `design-model.md:5` | Native web research is available, with environment/network policy controlling use. Adapt to the exposed search/open tool; the current Codex CLI also documents `--search` in local help. |
| Image reading | `pdf-analysis/SKILL.md:63` | Native image-viewing equivalent is available here (`view_image`); replace “Read the image” tool identity. Rendering remains the same Python utility. |
| Docling MCP | `pdf-analysis/SKILL.md:48` | Codex supports MCP; configure the server natively and discover its exposed tool names. The product currently supplies prose tool names, not a server installation. No end-to-end Docling test was run. [MCP configuration](https://learn.chatgpt.com/docs/extend/mcp) |
| Project instructions | `onboard.md:79`, `toolkit-awareness/SKILL.md:41` | Codex loads `AGENTS.md`; `CLAUDE.md` requires an explicit fallback configuration to be discovered automatically. Prefer native entry files pointing to shared project guidance. Preserve owner content. [Instructions](https://learn.chatgpt.com/docs/agent-configuration/agents-md) |
| External documentation permissions | `manage-sources.md:52`, `cli/__init__.py:934` | Adapt separately. Claude's `Read(path)` JSON rules are not Codex sandbox settings. Determine required reads under active policy; never convert a read request into a broad writable-root grant. [Security](https://learn.chatgpt.com/docs/agent-approvals-security) |
| Formatting hook | `claude/hooks/ruff-format.sh:9`, `:22` | Codex has native PostToolUse hooks. Its apply-patch event supplies `tool_input.command`, so the existing `file_path` parser would do nothing. Translate event input or invoke formatting explicitly. [Hooks](https://learn.chatgpt.com/docs/hooks) |
| PM state / atomic CLI operations | `research.md:63`, `backlog.md:76`, `status.md:83` | Portable CLI contract. Keep registry schemas, MR/PR/DI/SV identifiers, and owner curation unchanged. New skill packaging does not require a PM engine rewrite. |

### Every workflow, including the less visible cases

Common metadata, file operations and conversational input apply to all rows. Paths in this table are under `claude/commands/`.

| Workflow | Distinct behavior to preserve or adapt |
|---|---|
| `analyze-models` | Parallel exploration, validation, timestamped analysis report (`:38`, `:49`, `:67`). |
| `audit-models` | Work-item/Epic/project scopes; numerical checks; PM updates; optional owner-held close choice (`:16`, `:37`, `:67`, `:107`). |
| `backlog` | Add/decompose/close input grammar; add-epic/add-item/close-item CLI; template fallback (`:12`, `:76`, `:94`, `:110`). |
| `design-model` | Parallel experts, source analysis, prototype validation and owner approval (`:54`, `:69`, `:81`). |
| `formalize-intent` | File/conversation input, parallel exploration, owner-curated intent passed as JSON to PM (`:29`, `:57`, `:74`). |
| `implement-model` | Checkboxes, temporary syntax probes, parallel validator/expert work, traceability mutations and regression tests (`:45`, `:49`, `:58`, `:64`, `:75`). |
| `manage-sources` | Question choices, path checks, source edits, platform permission merge (`:29`, `:42`, `:48`, `:52`). |
| `onboard` | Git safety gate, text questions, populated project context and platform instructions (`:29`, `:41`, `:57`, `:79`). |
| `orchestrate-modeling` | One alignment, immutable brief, fresh stages/audits, returned blockers, independent write surfaces, bounded repair, owner-held archive (`:46`, `:57`, `:72`, `:119`, `:144`). |
| `plan-model` | File-backed phases, approval, checklists and generated parallel-Task instructions (`:73`, `:93`, `:104`). |
| `quick-model` | Single-file scope gate, concrete edit approval, validation; no explicit subagent requirement (`:37`, `:63`, `:69`). |
| `research` | Three research modes, parallel experts, web tools, script-owned pending report and separate report/insight approval (`:35`, `:53`, `:63`, `:79`). |
| `review-model` | Four independent checks, owner accept/skip/defer, advisory review verdict (`:39`, `:51`, `:63`). |
| `spec-model` | Scope confirmation, sourced MR requirements, SV entries, authoritative spec frontmatter (`:57`, `:61`, `:69`, `:81`). |
| `status` | Dashboard/decompose/close modes, deterministic state plus interpretation, four optional post-close questions (`:25`, `:35`, `:75`, `:90`). |

### All supporting skills and agents

Reference skills: `epic-decomposition`, `model-validation`, `project-structure`, `requirements-tracking`, `source-traceability`, `sysml-conventions`, `toolkit-awareness`. Their `SKILL.md` frontmatter declares implicit triggers and `user-invocable: false`. Active utilities: `pdf-analysis`, `python-debugger`, `record-learning`. Each was loaded in the full-catalog probe. Four reference documents and two executable Python files must remain bundled with their respective directories.

Expert roles: `kerml-expert`, `sysml-expert`, and `syside-expert` are reference readers; `sysmlv2-validator` executes validation and writes probes; `python-debugger` runs the bundled debugger. Native role generation must preserve these responsibilities and resolve documentation paths (`claude/agents/kerml-expert.md:15`, `sysml-expert.md:16`, `syside-expert.md:15`, `sysmlv2-validator.md:26`, `python-debugger.md:17`). Neither utility script calls a model provider: the debugger uses `bdb`, and the PDF script uses Python extraction/rendering libraries (`claude/skills/python-debugger/scripts/claude_debugger.py:18`, `pdf-analysis/scripts/extract_page.py:28`).

No command uses argument macros, dynamic shell injection, file-expansion syntax, model-selection frontmatter, fork frontmatter, task-manager APIs, or plan-mode tools. No shipped agent declares model selection, memory, hooks, or preloaded skills. These capabilities need no migration work merely because the platforms support them.

### Hooks and provider independence are separate concerns

The formatter is an assistant PostToolUse hook, despite CLAUDE.md calling the folder “Git hooks.” Neither installer registers it: both copy the script, while generated settings contain permissions only (`src/agentic_mbse/cli/__init__.py:830`, `:959`; `scripts/replicate_setup.sh:82`, `:101`). [AGENT] Decide whether native dual support includes activating formatting. Activation would add behavior to the current install.

Codex hooks can live in `.codex/hooks.json` and require trust review. Patch events need a different payload parser; matching `Edit|Write` alone does not fix that ([Codex hooks](https://learn.chatgpt.com/docs/hooks#tool-coverage)). The hook also requires Bash, `jq`, and bare `ruff` on PATH (`claude/hooks/ruff-format.sh:1`, `:9`, `:22`).

Supporting Codex as the interactive agent does not automatically remove every Anthropic dependency from the Python package. The enhanced extraction backend still invokes `claude -p` (`src/agentic_mbse/extraction/claude_enhance.py:78`). The shipped PDF helper itself does not. [AGENT] Treat a provider-independent extraction backend as separate scope unless the owner requires “Codex-only, no Claude executable/account.”

## 3. Clean Installation Design

### Recommended layout

[AGENT] Author workflow skills once in an ordinary package source directory such as `skills/`. Install project-local canonical bundles in `.agents/skills/`. Add relative per-skill Claude aliases. Keep native agent/config outputs separate. This is the smallest tested layout with one installed skill copy:

```text
<target>/
├── .agents/skills/
│   ├── spec-model/SKILL.md
│   ├── pdf-analysis/{SKILL.md,scripts/,references/}
│   └── ...                     # 25 bundles in the current inventory
├── .claude/
│   ├── skills/spec-model -> ../../.agents/skills/spec-model
│   ├── skills/pdf-analysis -> ../../.agents/skills/pdf-analysis
│   ├── agents/*.md              # rendered Claude roles
│   └── settings.json            # Claude-specific, owner-preserving
├── .codex/
│   ├── agents/*.toml            # rendered Codex roles
│   └── config.toml              # only needed native configuration
├── AGENTS.md / CLAUDE.md        # native entries, shared guidance references
└── knowledge/, modeling_project/, work/, data/, models/
```

This diagram is an [EXAMPLE], not an approved schema. Shared skill content should state actions in plain language: read, search, edit, ask and wait, delegate to a fresh agent, gather evidence. Put the few tool-specific instructions into short Claude/Codex notes or reference files. The spike confirms tolerant loading of the existing Claude frontmatter. [AGENT] Add Codex invocation metadata through `agents/openai.yaml` where needed; that combined bundle was not tested here, and semantic equivalence must be tested field by field. Render separate entry files only when the runtime content actually diverges. Avoid a general prompt-transpilation framework.

Native agent definitions require generation because their schemas differ. Keep each expert's domain instructions once and render the small native envelopes and documentation paths. Do not raw-symlink templates containing unresolved `{SYSML_DOCS_PATH}` or `{SYSIDE_DOCS_PATH}` tokens; current `--dev` does this (`src/agentic_mbse/cli/__init__.py:776`).

### Installation options and tradeoffs

| Option | Assessment |
|---|---|
| Canonical `.agents/skills`, per-skill Claude relative links | Recommended Unix layout. Tested in both clients, including relocation. Each shared bundle has one update target. Native metadata/adapters still matter. |
| Neutral payload directory with links from both roots | Also tested. Adds another location and alias layer; use only if owning `.agents/skills` is undesirable. |
| Generated copies in both roots | Recommended fallback when symlinks are unavailable or inconvenient. Still one authoring source, but two installed copies to reconcile and hash. |
| Link discovery roots wholesale | Avoid as default. It captures unrelated owner skills and makes coexistence/collision handling harder. Per-skill links limit ownership. |
| Absolute links into checkout/site-packages | Reserve for opt-in development mode. Package uninstall, environment recreation, checkout movement and Git sharing can break targets. Current `--dev` uses absolute links (`cli/__init__.py:479`). |
| Independent Claude/Codex prompt trees | Simple first patch, persistent semantic drift afterwards. Prefer native envelopes around shared instructions. |
| Native plugins | Useful future distribution channel, but still need Python package/project initialization and native configuration. Claude plugin names introduce namespace considerations. Evaluate separately from this installer migration ([Claude plugins](https://code.claude.com/docs/en/plugins), [Codex distribution](https://learn.chatgpt.com/docs/build-skills#distribute-skills-with-plugins)). |

Codex supports explicit skill mention via `$name` and optional manual-only policy in `agents/openai.yaml`; these belong in the native usage examples. Neither client needs another symlink in `.codex/skills` for the tested layout ([Codex skills](https://learn.chatgpt.com/docs/build-skills)).

### One installer, shared state, explicit ownership

[AGENT] Extend `agentic-mbse init` with a runtime selector, for example `--assistant claude|codex|both`, and a link/copy option. Exact flag names and default selection remain design choices. Install modeling templates once. Keep backward-compatible behavior for existing CLI callers, and make `install-commands` route through the same installation primitives rather than retain a separate copying path.

The shell replication script should call the common installer or a shared Python entry point. Today it overwrites owner documents/settings on each run, unlike normal init (`scripts/replicate_setup.sh:154`, `:184`, `:190`; `src/agentic_mbse/cli/__init__.py:889`, `:934`). A second platform would amplify that divergence.

[AGENT] Record owned paths and installed hashes in a runtime-neutral manifest, including every skill resource and each alias. Import the legacy `.claude/.tool-hashes.json` before migration. Retain the original baseline hash when a user skips an update. Reconcile retired files only when provenance proves ownership; preserve or back up changed/unknown legacy commands. A same-name new skill can otherwise hide a customized old command without deleting it.

The spike establishes three concrete requirements for a safe implementation:

1. Preserve skipped modifications across third and later init runs. The current replacement manifest drops skipped entries (`src/agentic_mbse/cli/__init__.py:595`, `:752`, `:967`).
2. Handle skill contents individually or with an explicit owned-tree policy. Current re-init deletes the entire directory, including owner additions (`src/agentic_mbse/cli/__init__.py:471`, `:823`).
3. Unlink installer-owned destination symlinks before copying; never write through them accidentally. The hash-aware helper does this, while forced `install-commands` does not (`src/agentic_mbse/cli/__init__.py:431`, `:1053`).

These are [INFERRED] implementation needs from observed failure modes, not owner-originated requirements. See [executed installer evidence](../active/spike-native-skill-install/installer-findings.md).

Codex protects `.agents` and `.codex` within writable roots. Normal shell installation outside the assistant is straightforward; in-session installation/update can require the client's approval path. Symlinking is not a way to grant writes or bypass that protection ([security](https://learn.chatgpt.com/docs/agent-approvals-security#protected-paths-in-writable-roots)). Model outputs should stay in ordinary project directories, never beside installed skill scripts.

### Packaging and adjacent changes

| Change area | Current reference | Expected work |
|---|---|---|
| Package inventory/data roots | `src/agentic_mbse/cli/__init__.py:18`, `:108`; `pyproject.toml:66` | Package shared skills and native adapter inputs; update source/wheel lookup. |
| Init and command-only install | `src/agentic_mbse/cli/__init__.py:549`, `:1015` | Runtime selection, ownership, migration retirement, aliases/copies, safe updates. |
| Replication helper | `scripts/replicate_setup.sh:48` | Consolidate with common installation behavior. |
| Tool documentation | `project_templates/MODELING_PROCESS.md.template:163`, `:223`; `MODELING_GUIDE.md.template:277` | Replace literal Task/Read examples and single-platform permissions guidance. |
| Onboarding / source setup | `claude/commands/onboard.md:57`, `:79`; `manage-sources.md:52` | Native context entry files and platform-specific permission guidance. |
| Skill utilities / expert paths | `claude/skills/pdf-analysis/SKILL.md:19`; `claude/agents/python-debugger.md:17` | Resolve script paths from the bundle; render external-doc references. |
| Root discovery | `src/agentic_mbse/cli/__init__.py:169` | Keep `work/BACKLOG.md` primary; reconsider Claude-only fallback for Codex-only partial installs. |
| Help / README / examples | `project_templates/README.md.template:22`, `:81`; `cli/__init__.py:1121` | Explain both native invocation styles and selected runtime installation. |
| Tests | `tests/test_cli.py:262`, `:403`, `:815`; `tests/test_modeling_command_contracts.py:68` | Replace Task-wording assertions with shared behavioral contracts plus native adapter checks; add migration/update tests. |

## Feasibility and Recommended Sequence

The effort is concentrated in installation lifecycle and a small number of runtime adapters. The core modeling instructions and deterministic PM/validation APIs can be shared. No new workflow engine is indicated by this research.

[AGENT] First implement and test the ownership-safe shared installer and package layout. Then migrate the 15 workflows and ten skill bundles, remove hardcoded platform paths, render the five roles, and adapt onboarding/permissions and question instructions. Finally test both native clients with one simple workflow and a small orchestrator run that exercises delegation, a returned blocker, an independent audit, and an external reference. Treat hook activation and provider-independent extraction as explicit scope decisions.

Release validation should cover source and wheel installs; Claude-only, Codex-only and both; copy/link transitions; repeated init after skipped edits; modified legacy commands; owner-created skills and config; relocation; supporting-script invocation; and both catalogs. Add behavioral smoke tests for `$name`/`/name` input, manual/implicit activation, named expert spawning, two-level delegation, and reserved owner decisions. Test the lowest supported client versions, not just these local versions.

Existing prompt contradictions should be surfaced during adaptation, without silently rewriting their authority: toolkit-awareness rejects standalone `syside check`, while implement/plan prescribe it (`claude/skills/toolkit-awareness/SKILL.md:69`, `claude/commands/implement-model.md:45`, `plan-model.md:101`). Permission-path guidance is referenced but absent from toolkit-awareness (`manage-sources.md:52`). These are source inconsistencies to resolve explicitly when specifying changes.

## Open Questions

- Should workflow skills retain current implicit invocation behavior or become manual-only? The owner has not decided this. Reference skills should remain available when relevant.
- Does “native Codex support” include eliminating the enhanced extraction backend's Claude CLI dependency, or only native interactive workflows?
- Which operating systems and minimum client versions must be supported? Symlink discovery is confirmed only on the recorded Linux clients.
- Should the currently unregistered formatter become an active hook? That is additional installed behavior.
- Should generic `status` be renamed after testing actual TUI collision behavior?
- How strict must expert tool restrictions be across platforms? Read-only filesystem policy is not identical to Claude's Read/Grep/Glob-only capability set.

These questions do not block the feasibility conclusion. They affect the eventual implementation contract. The research is complete; full behavioral equivalence remains a release validation obligation rather than a result claimed by the discovery spike.
