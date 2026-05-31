---
id: DP-018
name: Spec-driven development (spec.md before code)
category: quality
status: active
constitution-rules: []
youtube-difficulty: beginner
youtube-episode-length: short
introduced: 2026-04
---

## What it is

Any non-trivial feature, refactor, or migration gets a `spec.md` written
BEFORE code. Project-wide work → `{project}/spec.md`. Feature-level →
`{project}/specs/{feature-slug}.md`. The `/spec` skill scaffolds the
template.

## Rationale — Why We Adopted This Pattern

*The story of how this pattern came to exist and why it was chosen over alternatives.*

### The problem we kept hitting
Diving into code without a plan led to 3 rewrites, missed edge cases,
and 23 hours of debugging where 60 min of planning would have caught
the problem on paper.

### What we tried first (and why it didn't work)
- **Just start coding** — works for trivial changes, catastrophic for
  anything else.
- **Plan in chat** — plan disappeared when the session ended.
- **TODO.md only** — captured tasks, not the *design*.

### The insight that unlocked the solution
**spec.md is the contract.** Problem / Goals / Non-goals / Design / Test
plan / Rollback. Written before code, frozen as documentation when
shipped. Single artifact for plan + verify.

### Why this approach, not the obvious one
*Why not use a heavyweight ADR for every change?* Because ADRs are for
*architectural* decisions; spec.md is for *features*. They co-exist: ADR
captures "we chose Approach A over B"; spec.md captures "this is what
Approach A actually does for this feature."

### Evidence that it works
- Anthropic's own analysis: 60 min planning saves 23+ hrs debugging.
- Specs from 2026-04 still readable and accurate; chat plans from same
  date irretrievable.

## Why we use it

CLAUDE.md rule from the workspace:
> "60 min planning saves 23+ hrs debugging."

A spec forces the author to commit to: what problem, what success looks
like, what NOT to do (non-goals), how to roll back. Mid-build pivots
become explicit (update the spec) instead of silent drift.

## How it works

**Standard spec sections:**
1. **Problem** — what is broken / missing today
2. **Goals** — measurable outcomes
3. **Non-goals** — explicitly out of scope (prevents scope creep)
4. **Design** — architecture, data flow, key decisions
5. **Test plan** — what proves it works
6. **Rollback** — how to undo if shipping breaks something

**Lifecycle:**
- Pre-code: write spec, get sign-off (self or pair-reviewer).
- During build: spec is the contract; deviations require spec updates.
- Post-ship: spec freezes as documentation; future readers see intent.

**Skill**: `/spec` generates the template and walks the workflow.

**Hooks**: `spec-reread-at-stop.sh` reminds the author to verify the
shipped code matches the spec.

## Example

Building Constitution required a spec because it touches every project:

```markdown
# spec: Constitution as Rule Registry SSoT

## Problem
Rules duplicate across CLAUDE.md files; drift undetected.

## Goals
- Single SQLite ledger for all rules
- CLI to query/promote/deprecate
- Drift detector vs actual hook artifacts

## Non-goals
- Auto-promoting proposed rules (humans only)
- Replacing per-project CLAUDE.md (Constitution complements them)

## Design
- ledger.db schema: rules, instructions, artifacts, events
- CLI: constitution.py with init/check/audit/promote/deprecate
- Drift: walk artifacts → compare to rules → emit MISSING/ORPHAN/DRIFT

## Test plan
- Bootstrap ledger from fleet → 555 rules captured
- Promote 70 proposed → all wire to hooks → 0 MISSING
- Drift detector catches a deleted hook

## Rollback
- ledger.db is append-only; restore from backup
- CLI rollback command reverts last promotion
```

## Related patterns

- [DP-020] Definition of Done
- [DP-034] Boring tech bias (specs catch novelty cost)
- [DP-039] Two-persona split (spec is the PM persona's deliverable)

## YouTube episode angle

- **Tech-savvy** (5-min): "Why I write the spec twice." Show a real
  spec, walk through each section. Discuss the cost/benefit: 60 min
  spec → saves debugging time.
- **Lay audience** (3-min): "Blueprint before construction." Like
  architecture drawings before pouring foundation.

## Known failure modes / lessons learned

- A spec without Rollback is incomplete. The [Your Company] rules.md adds
  Rollback as a hard requirement.
- Specs get stale if not updated during the build. Stop hook reminds
  to verify.
