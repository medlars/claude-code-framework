# Category 11 — Skills, Agents, Hooks

How the three packaging primitives are designed and used.

**Skills** (`~/.claude/skills/`, 155 total): reusable workflows invoked
by name. Pattern: each skill has a YAML frontmatter (name, description,
triggers) + structured markdown body. See [DP-009] subagent-driven and
[DP-012] specialist-matching for how they integrate.

**Agents** (`~/.claude/agents/`, 24 total): specialist personas with
their own CONTEXT.md. Pattern: each agent has YAML frontmatter (name,
description, model, tools) + system prompt. See [DP-012].

**Hooks** (`~/.claude/hooks/`, 180 total): shell scripts wired to
events in `~/.claude/settings.json`. Pattern: stdin JSON, exit codes
0/1/2, optional `additionalContext` stdout for advisory mode. See
[DP-013].

The triad maps to the supervisor stack:
- Skills = how-to manuals
- Agents = workers with manuals pre-loaded
- Hooks = referees who enforce the rules

Registries:
- Hook registry: `~/.claude/hooks/HOOK-REGISTRY.md`
- Tool registry: `~/.claude/tool-registry.md` (600+ tools)
- Agent context: `~/.claude/agents/CONTEXT.md`
