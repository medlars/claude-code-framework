---
id: DP-031
name: Session save protocol (/save → Apple Notes + memory + wiki)
category: workflow
status: active
constitution-rules: []
youtube-difficulty: beginner
youtube-episode-length: short
introduced: 2026-04
---

## What it is

The `/save` skill captures the current session into three places:
1. Apple Notes — summary + detail notes (with `(TAG)` suffix)
2. Memory — session entry in `~/.claude/projects/.../memory/MEMORY.md`
3. Wiki (when applicable) — distilled lesson at `~/wiki/`

Plus an enforced rename step: `require-rename-before-save.sh` hook
blocks save until the user runs `/rename` to confirm a session name —
no invented names.

## Rationale — Why We Adopted This Pattern

*The story of how this pattern came to exist and why it was chosen over alternatives.*

### The problem we kept hitting
A long session full of decisions, fixes, and context disappeared at
`/clear`. Six weeks later, "did I already try X?" had no answer.
Important findings were lost.

### What we tried first (and why it didn't work)
- **TodoWrite only** — captured tactics, not the session narrative.
- **Manual note-taking** — inconsistent, often skipped.

### The insight that unlocked the solution
**`/save` is mechanical: prompts for a name, writes to Apple Notes
(summary + detail), updates memory, optionally updates the wiki.** The
rename gate prevents invented names; the operator must approve the name
via `/rename`.

### Why this approach, not the obvious one
*Why not use a session-journal CLI?* It exists (and is used) — but
Apple Notes is searchable from any device including the owner's iPhone
during clinic hours.

### Evidence that it works
- 200+ saved sessions in Apple Notes, all queryable.
- MEMORY.md auto-index acts as a TOC; never lost a session since the
  protocol was set.

## Why we use it

Sessions are dense. Without explicit save, the work disappears at
`/compact` or `/clear`. With it, every long session contributes a memory
entry visible to the next session, two Apple Notes for human review, and
optionally a wiki page for distilled knowledge.

## How it works

**Hard rename gate** (`require-rename-before-save.sh`):
- Save attempted without `set-session-name.sh` having recorded a name
- Hook blocks; user must `/rename <name>` first
- Prevents "session_2026_05_31" auto-names that nobody can find later

**The save sequence:**
1. User: `/save`
2. Skill computes the session summary (recent edits, decisions, files).
3. Writes Apple Notes (capped at 2500 chars per body — `apple-notes-size-gate.sh`):
   - `(SUM)` summary note
   - `(DET)` detail note (multi-part if needed: pt.1/pt.2)
4. Appends memory entry to MEMORY.md (one-line index entry under ~200
   chars, detail in topic file).
5. If session generated a reusable lesson → graduate to `LESSONS.md` via
   `graduate-to-lessons.py`.
6. If session covered a new entity/concept → wiki page.

**Lifecycle:** memory entries auto-load at session start (via @import in
CLAUDE.md), so the next session has prior context.

## Example

End of a long FinanceFlow session:

```bash
/rename ff-pre-insert-pipeline-fix-2026-05-30
/save
```

Outputs:
- Apple Note `(SUM)` "ff-pre-insert-pipeline-fix-2026-05-30" — 1-page summary
- Apple Note `(DET)` — file changes, decisions, follow-ups
- MEMORY.md gets: `[FF pre-insert pipeline fix 2026-05-30](session_ff_pre_insert_pipeline_2026_05_30.md) — Description in one line under 200 chars`
- LESSONS.md gets new entry if pattern is reusable

## Related patterns

- [DP-002] Constitution as SSoT (lessons inform new rules)
- [DP-033] WISC context management
- [DP-040] Lessons-as-injected-context

## YouTube episode angle

- **Tech-savvy** (5-min): "How I make a long session into a permanent
  record." Walk through /save outputs; show MEMORY.md auto-injection
  next session. Discuss the rename gate.
- **Lay audience** (3-min): "Don't let the day disappear." Like a
  doctor's daily note: every shift documented for the next shift to
  pick up.

## Known failure modes / lessons learned

- Memory entries exceed 200 chars → auto-truncation breaks links.
  Format discipline matters.
- Apple Notes >2500 chars hang the MCP. The size gate enforces
  pt.1/pt.2 splits at natural section boundaries.
- LESSONS B-005: `Path.home()` not `/Users/eiman/` — applies to wiki
  paths too.
- Without rename: session names like "session_2026_05_31" make memory
  unsearchable.
