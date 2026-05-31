---
id: DP-017
name: Cold-read audit (new-engineer perspective)
category: quality
status: active
constitution-rules: []
youtube-difficulty: intermediate
youtube-episode-length: medium
introduced: 2026-05
---

## What it is

The general principle behind DP-006: when auditing your own code, read it
as if you'd never seen it before. Drop every assumption. Question every
identifier, every implicit invariant, every "obviously" call. The
specialized form is the 9-dim audit (DP-006).

## Rationale — Why We Adopted This Pattern

*The story of how this pattern came to exist and why it was chosen over alternatives.*

### The problem we kept hitting
Project owners (us included) are too close to their own code. They know
the conventions, the implicit invariants, the unwritten "we never call
this from there" rules. A new engineer joining the project would trip
over all of them in week 1. We don't have new engineers — but the cost
of unspoken assumptions is real.

### What we tried first (and why it didn't work)
- **Reading our own docs** — we wrote them, we believe them; if the docs
  are wrong, we don't notice.
- **Asking an LLM to "review the code"** — too vague.

### The insight that unlocked the solution
**Pretend you're a new engineer with no context and try to ship something
trivial.** Every assumption you have to make explicit is a doc gap;
every place you guess wrong is a comment debt.

### Why this approach, not the obvious one
*Why not just hire a new engineer?* (Solo developer; not an option.)
The next-best thing is a fresh-context LLM session with an explicit
"cold read" prompt.

### Evidence that it works
- /sagamail-audit, /financeflow-audit, etc. all use cold-read prompts and
  consistently surface 10-30 doc/assumption gaps per audit.

## Why we use it

Familiarity is a bug factory. The author knows what the code *should* do
and reads that into the code, blind to what it actually does. A cold-read
costs hours but pays back when a 10-line bug nobody saw for months
surfaces in one sweep.

## How it works

**Cold-read discipline:**
1. Pick a project you've worked on for >2 months.
2. Open a fresh session with zero project context loaded.
3. Read the entry point first. Read every imported module before reading
   the caller. Question every function name (does it actually do that?).
4. Annotate as you go: every assumption, every "I think this is the
   case", every "but X probably handles it" — these are the bug sites.
5. Run the 9-dim checklist (DP-006) against each.

**Variant: cold-read agent.** Spawn a fresh subagent with no prior
session memory; brief it with only the project's CLAUDE.md and ask it
to audit. The agent has no familiarity bias.

## Example

The <Moonitor> cold-read (2026-05-30) — author had worked on the project
for 3 months. Cold-read found:
- `prune_old_items` defined but never called from any path
- Apple ns timestamps multiplied by 1e9 (already in ns)
- README mentioned an MCP tool not actually implemented
- 1806 tests passed but state.db schema differed from prod fixtures

None of these would have surfaced in a familiar-mode review.

## Related patterns

- [DP-005] Detector-gap pattern (cold-read findings → detectors)
- [DP-006] 9-dimension cold-read audit (the specialized form)
- [DP-038] Triple Review Protocol (related discipline)

## YouTube episode angle

- **Tech-savvy** (10-min): Live cold-read of a project. Narrate every
  assumption challenged. Compare to "code review by author" (least
  effective) vs "code review by stranger" (most effective).
- **Lay audience** (5-min): "Audit your own work like a stranger."
  Analogy: a writer who reads their draft aloud in a different voice
  hears the typos their inner ear glossed over.

## Known failure modes / lessons learned

- Time-pressured cold-reads degrade into familiar reads. Schedule them
  separately from feature work.
- Subagent cold-reads need explicit "do not assume" framing in the
  briefing or they default to author-mode patterns.
