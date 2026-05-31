---
id: DP-009
name: Subagent-driven execution (standing preference)
category: execution
status: active
constitution-rules: []
youtube-difficulty: beginner
youtube-episode-length: short
introduced: 2026-05
---

## What it is

A standing preference (2026-05-13): when a task can be delegated to a
subagent, **always choose subagent-driven over inline execution**. The
hook `enforce-subagent-driven.sh` enforces this — questions about
"should I do X inline or delegate?" are blocked because the answer is
always "delegate".

## Rationale — Why We Adopted This Pattern

*The story of how this pattern came to exist and why it was chosen over alternatives.*

### The problem we kept hitting
Long sessions where Claude Code did everything inline (Read, Edit, Bash,
plan, decide) degraded in quality after ~40 tool calls. Context rot.
Decisions made early in the session conflicted with edits made later. The
orchestrator got dumber the more it did.

### What we tried first (and why it didn't work)
- **Frequent `/compact`** — destroyed cache, lost context, replaced one
  failure mode with another.
- **Shorter sessions** — broke continuity, forced re-derivation.
- **TodoWrite** — helped with task tracking but didn't reduce the
  orchestrator's load.

### The insight that unlocked the solution
**The orchestrator should orchestrate, not execute.** Hand the work to a
subagent with a fresh context window, get the result back as a summary,
and the orchestrator's context stays clean. The 2026-05-13 confirmation
made this the default: "Always choose subagent-driven over inline."

### Why this approach, not the obvious one
*Why not just always run inline since it's faster?* It *feels* faster
because there's no spawn overhead. But the quality decay over a long
session costs far more than the spawn cost. METR (Jul 2025) found AI is
19% slower than manual on familiar code — but the inverse is true on
unfamiliar code, and subagents bring fresh familiarity to each domain.

### Evidence that it works
- `enforce-subagent-driven.sh` hook now intercepts inline-execution
  attempts and recommends a subagent.
- Long sessions (50+ tool calls) maintain output quality when the
  orchestrator delegates; degrade visibly when it doesn't.

## Why we use it

Inline execution pollutes the orchestrator's context, slows the model
down with tool-output noise, and prevents parallelism. Subagents run in
isolated contexts, can run in parallel, and return only their conclusion
— keeping the orchestrator's context clean and focused on coordination.

## How it works

**Decision tree:**
- Task touches 1–2 files and is local → inline OK
- Task touches 3+ files, runs a pipeline, or needs deep code search →
  spawn a subagent (Task tool with `subagent_type`)
- Task is a quality/security check that shouldn't block → background
  subagent

**Standing rule** (from `~/.claude/CLAUDE.md`):
> "Always choose subagent-driven over inline execution; confirmed
> 2026-05-13; hook `enforce-subagent-driven.sh` also enforces this."

**Hook enforcement:**
`block-subagent-driven-question.sh` blocks any user-facing question like
"Do you want me to delegate or do this inline?" — the answer is always
delegate, so don't ask.

## Example

Bad (inline, pollutes context):
```
[orchestrator reads 14 files, runs 8 greps, edits 5 files, runs tests]
→ context now contains 50KB of tool output
```

Good (subagent):
```
Task(subagent_type="codex:codex-rescue",
     prompt="Refactor financeflow ColumnMapper to use SpreadsheetRouter
             across all 22 files; ensure tests pass; report a summary")
→ context contains: one task call + one summary (≤2KB)
```

## Related patterns

- [DP-010] Parallel agent dispatch
- [DP-011] Codex routing (specific case of subagent-driven)
- [DP-012] Specialist agent matching
- [DP-033] WISC context management (subagents are the W in WISC)

## YouTube episode angle

- **Tech-savvy** (5-min): "Why I never edit code inline." Show context
  pollution side-by-side: inline (50KB output) vs subagent (2KB
  summary). Demonstrate that the orchestrator stays sharp on a long
  session by delegating heavy work.
- **Lay audience** (3-min): "Don't do the work yourself — hire a
  specialist." Use the manager analogy: a good manager doesn't write the
  code, they pick the right engineer and review the result.

## Known failure modes / lessons learned

- Owner had to be reminded multiple times until the hook was added;
  LESSONS B-004 codified "Memory requires a hook" — preference alone is
  not enforcement.
- Subagent reports must be concise: parent agent reads the text, not
  files. Subagents that write summary .md files waste tokens.
