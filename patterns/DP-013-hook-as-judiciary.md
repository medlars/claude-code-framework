---
id: DP-013
name: Hook-as-judiciary (memory is advisory, hooks are law)
category: enforcement
status: active
constitution-rules: []
youtube-difficulty: intermediate
youtube-episode-length: long
introduced: 2026-05
---

## What it is

Behavioral rules expressed only as memory or CLAUDE.md instructions are
**advisory** — the model can rationalize past them. The same rule
expressed as a shell hook in `~/.claude/hooks/` is **law** — it runs in a
separate shell process, sees the proposed action, and can block (exit 2)
or augment (additionalContext). 180 hooks currently active. The fleet
treats hooks as the judiciary: rules become enforceable when wired.

## Rationale — Why We Adopted This Pattern

*The story of how this pattern came to exist and why it was chosen over alternatives.*

### The problem we kept hitting
Behavioral rules in CLAUDE.md were ignored ~40% of the time. The model
would read them at session start, then rationalize past them mid-session
("this case is different"). Memory entries had the same fate.

### What we tried first (and why it didn't work)
- **Stronger language in CLAUDE.md** ("NEVER", "MUST", "CRITICAL") —
  marginal improvement.
- **Repeating critical rules at end of long prompts** — helped a bit.
- **Reminding the model mid-session** — required human intervention.

### The insight that unlocked the solution
**Shell-level enforcement is outside the model's reasoning loop.** A hook
that returns exit 2 *cannot* be rationalized away. LESSONS 002:
"Memory without a hook is advisory only."

### Why this approach, not the obvious one
*Why not just trust the model to follow rules?* Because the model is
stochastic. Even 95% compliance means 1 in 20 critical actions slips
through. For high-blast-radius operations (DNS edits, force pushes,
`rm -rf`) that's unacceptable.

### Evidence that it works
- 180 hooks active fleet-wide.
- The TDD cycle gate (DP-015) is hook-enforced; before the hook,
  test-after happened ~60% of the time; after, ~95%.
- AP-014 (Codex `killall -9 python3.14`) became a hook block within 24
  hours of the incident.

## Why we use it

The owner's hard-won insight (LESSONS 002):
> "Memory without a hook is advisory only. Every behavioral memory must
> be paired with a hook in `~/.claude/hooks/`. Shell-level enforcement is
> outside Claude's reasoning loop — it cannot be rationalized away."

A model can talk itself into ignoring a CLAUDE.md rule. It cannot talk
itself past a hook that returns exit 2.

## How it works

**Hook events** (matched in `~/.claude/settings.json`):
- `UserPromptSubmit` — runs before model sees prompt; can inject context
- `PreToolUse:<tool>` — runs before a tool call; exit 2 blocks
- `PostToolUse:<tool>` — runs after a tool call; advisory only (cannot
  block, but can inject context for next turn)
- `Stop` — runs when model attempts to end turn; can prevent end
- `PreCompact` — runs before context compaction

**Hook contract:**
```bash
#!/bin/bash
# Read JSON from stdin
INPUT=$(cat)
# Inspect (jq), decide, exit 0/1/2 or print JSON to stdout
```

**Three enforcement tiers:**
1. **Hard block** (PreToolUse, exit 2): tool call refused
2. **Advisory** (PostToolUse, JSON `additionalContext`): next turn sees the warning
3. **Async** (PostToolUse with `async: true`): fire-and-forget, never blocks

**Hook registry**: `~/.claude/hooks/HOOK-REGISTRY.md` — every hook with
matcher, purpose, status, known gaps.

**Memory-paired-with-hook rule**: when a behavioral memory is saved, the
`memory-requires-hook.sh` PostToolUse hook reminds the author to wire a
hook.

## Example

Rule: "Never use `getActiveSpreadsheet()` in <FinanceFlow> (use
SpreadsheetRouter)."

Without a hook: rule lives in <FinanceFlow>/CLAUDE.md, agent occasionally
forgets, ships bug.

With a hook: `financeflow-gate.sh` (PreToolUse:Write+Edit) matches
`*.gs|*.html` under `<FinanceFlow>/`, greps for `getActiveSpreadsheet()`,
returns exit 2 + a message. Bug cannot ship.

## Related patterns

- [DP-002] Constitution as SSoT (rules → hooks pipeline)
- [DP-014] Hypothesis gate (specific hook)
- [DP-015] TDD cycle gate (specific hook)
- [DP-040] Lessons-as-injected-context (hook that injects)

## YouTube episode angle

- **Tech-savvy** (15-min): "Why I don't trust AI to follow rules." Show
  three examples of rules the AI rationalized past, then the hooks that
  enforce them. Walk through hook anatomy (stdin JSON, exit codes,
  additionalContext).
- **Lay audience** (8-min): "Trust, but install a fence." Use the
  analogy of a railway crossing: the warning sign is advisory; the
  barrier arm is law. Both exist for a reason.

## Known failure modes / lessons learned

- LESSONS 065: A hook that prints to STDERR and exits 0 is INVISIBLE
  to the model — the message never surfaces. Use JSON to stdout for
  advisory output.
- LESSONS 024: `set -uo pipefail` + grep can kill a hook before it
  emits its block JSON. Use `while read` loops.
- LESSONS 025: Hook pipe-test output containing error-like strings
  causes false-positive matches in downstream hooks. Avoid logging hook
  test runs through the same scanners.
- LESSONS 073/074: Stop hooks use top-level `systemMessage` not
  `hookSpecificOutput` (schema gate added).
- AP-010: `find -maxdepth 2` misses files at depth 3+; hooks doing
  fleet scans must use `-maxdepth 4` or more.
