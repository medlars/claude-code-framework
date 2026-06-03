---
id: DP-011
name: Codex routing (substantive work → Codex, coordination → Claude)
category: execution
status: active
constitution-rules: []
youtube-difficulty: beginner
youtube-episode-length: short
introduced: 2026-04
---

## What it is

A standing directive (effective 2026-04-26, until lifted): when a task
involves 3+ files, 200+ lines, long pipelines, or audits, **delegate to
Codex** via the `codex:codex-rescue` agent or the CLI
`codex exec "<task>" </dev/null`. Claude Code stays as the coordinator;
Codex does the heavy lifting.

## Rationale — Why We Adopted This Pattern

*The story of how this pattern came to exist and why it was chosen over alternatives.*

### The problem we kept hitting
By April 2026 we were burning through the Anthropic rate limit by 4 PM
every day. Many tasks (large refactors, audits, long pipelines) didn't
*need* Claude's reasoning — they needed deterministic execution. Using
Claude for both was wasteful.

### What we tried first (and why it didn't work)
- **Buying more Anthropic tokens** — expensive, not a structural fix.
- **Aggressive `/compact`** — bought a few more turns, lost context.
- **Local LLMs (Ollama)** — at 6B-30B scale, tool use was unreliable,
  context windows too small for pipeline tasks.

### The insight that unlocked the solution
**Codex is cheaper, deterministic, and has a 1M context window — perfect
for substantive work.** Claude stays as the coordinator: planning,
reading, quoting files, making the architectural calls. The active
directive (2026-04-26): "Default to Codex for any change touching 3+
files or 200+ lines."

### Why this approach, not the obvious one
*Why not just use Codex for everything?* Because Codex is weaker at
nuanced reasoning (architecture choices, "should we even do this?",
debugging that requires understanding why a design exists). Claude's
strength is judgement; Codex's strength is throughput.

### Evidence that it works
- 2026-05-30 fleet sweep: 80+ P0 fixes done by Codex from Claude-
  authored briefs; Claude touched <500 lines of code itself.
- Anthropic rate limit usage dropped ~70% while output went up.

## Why we use it

Anthropic usage limits became a constraint. Codex (OpenAI) runs on a
separate quota with similar capability for substantive code work. Keep
Claude for: planning, reading/quoting files, coordinating subagents,
anything faster to do once than to brief Codex on.

The directive is in `~/.claude/CLAUDE.md` "ACTIVE DIRECTIVE" section.

## How it works

**Decision rule:**
- 3+ files, 200+ lines, audit, refactor, long pipeline → **Codex**
- Single-file tweak, quick fix, file reading, planning → **Claude**

**Two delegation modes:**
1. Skill: `/codex:rescue` — natural language hand-off, structured
2. CLI: `codex exec "<task>" </dev/null` — one-shot, redirects stdin

**Caching note:** Codex has a different model + cache than Claude. The
first prompt to Codex should set up its own context (load CLAUDE.md, read
relevant files) so its subsequent turns can reuse the cache.

**Guardrails:**
- AP-009: Codex bails silently on `~/.claude/CLAUDE.md` edits because of
  the destructive-action hook. Edit those in Claude directly.
- AP-014: Never use `killall -9 python3.14` from inside a Codex task —
  it kills the Codex task-worker itself.

## Example

Bad (Claude inline, hits usage limit):
```
"Refactor all 22 FinanceFlow .gs files to use SpreadsheetRouter."
→ Claude edits 22 files, 2000 lines, consumes 80K tokens
```

Good (Codex):
```
Task(subagent_type="codex:codex-rescue",
     prompt="Refactor all 22 FinanceFlow .gs files to use SpreadsheetRouter
             instead of getActiveSpreadsheet(). Run tests. Report a summary.")
→ Claude consumes ~500 tokens for the task call + summary
```

## Related patterns

- [DP-009] Subagent-driven execution
- [DP-010] Parallel agent dispatch
- [DP-033] WISC context management

## YouTube episode angle

- **Tech-savvy** (5-min): "Why I use two AIs." Show the cost split and
  when each is right. Demonstrate a Codex task running in the background
  while Claude plans the next step.
- **Lay audience** (3-min): "Different tools for different jobs." Use
  the analogy of a contractor who hires specialists for the heavy work
  but coordinates the schedule themselves.

## Known failure modes / lessons learned

- AP-009: Codex bails silently on `~/.claude/CLAUDE.md` edits.
- AP-014: `killall -9 python3.14` kills Codex's task-worker.
- LESSONS B-003: Analysis findings → explicit agent brief; Codex
  re-derives requirements from generic prompts and often misses scope.
