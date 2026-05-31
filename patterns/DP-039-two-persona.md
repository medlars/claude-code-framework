---
id: DP-039
name: Plan/Programmer two-persona split
category: workflow
status: active
constitution-rules: []
youtube-difficulty: beginner
youtube-episode-length: short
introduced: 2026-04
---

## What it is

A development methodology from `~/.claude/CLAUDE.md`:
> **PM Persona (plan)**: Deeply researched, modular plans. No gaps, no
> assumptions. Document everything before coding.
>
> **Programmer Persona (execute)**: Wisest proven approach, no trial
> and error. Best on first shot.

90% of the work is the plan; 10% is the execution.

## Rationale — Why We Adopted This Pattern

*The story of how this pattern came to exist and why it was chosen over alternatives.*

### The problem we kept hitting
One-persona mode mixed planning and execution badly. The "engineer" voice
optimized for shipping over thinking; ideas got committed to code before
they were ready. Trial-and-error coding ate hours.

### What we tried first (and why it didn't work)
- **Single-persona "be thoughtful and ship"** — neither thoughtful nor
  ready.

### The insight that unlocked the solution
**Two explicit personas: PM (plan) and Programmer (execute).** PM
produces deeply researched modular plans with no gaps or assumptions.
Programmer executes the plan with the wisest proven approach, no trial
and error. The user can switch contexts deliberately (and so can the
model, via prompt cues).

### Why this approach, not the obvious one
*Why not just plan more inside one persona?* Because mode-switching is
explicit and reduces accidental "shipping a half-formed idea". The PM
persona produces an artifact (spec.md) that the Programmer persona
executes against.

### Evidence that it works
- Plan-first sessions ship faster overall because the Programmer
  persona's first attempt is usually correct.

## Why we use it

Mixing planning and coding in the same pass produces both rushed plans
and trial-and-error code. Splitting them — explicitly choose persona,
finish, switch — keeps each clean.

## How it works

**PM persona deliverables:**
- `spec.md` (DP-018)
- ADRs in `.decisions/`
- TODO.md updates with sub-tasks
- Risk + rollback considerations
- Test plan

**Programmer persona deliverables:**
- Code edits following the spec
- Tests written alongside (DP-019)
- All NFRs met (DP-020)

**Switching signal:** explicit. Shift+Tab for plan mode (free thinking,
same cache). Switch out by writing the spec, then back into edit mode.

**Anti-pattern**: skipping PM persona because "this seems simple". The
hook `pm-plan-on-task.sh` reminds at task start.

## Example

Task: "Add SR&ED quarterly summary report."

Bad (mixed): start coding immediately, realize halfway you don't know
which SR&ED rules apply, look it up, refactor, hit edge case, refactor
again.

Good (split):
- **PM**: write spec — which expenses qualify, filing-deadline math,
  CRA disclaimer text, rollback if math wrong, test fixtures from prior
  filings.
- **Programmer**: code straight from spec; tests written alongside;
  green on first run.

## Related patterns

- [DP-018] Spec-driven development
- [DP-033] WISC context management

## YouTube episode angle

- **Tech-savvy** (5-min): "Plan like a PM, code like a programmer."
  Show side-by-side: chaotic mixed session vs split session.
- **Lay audience** (3-min): "Plan the trip before driving." Drivers
  who improvise routes get lost; same with code.

## Known failure modes / lessons learned

- The 60-min planning rule (from CLAUDE.md): "60 min planning saves
  23+ hrs debugging". Verified in multiple sessions.
- Skipping PM persona is the most common protocol drift; spec.md as a
  required artifact forces compliance.
