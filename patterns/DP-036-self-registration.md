---
id: DP-036
name: Design patterns registry self-registration
category: meta
status: active
constitution-rules: [SPEC-181]
youtube-difficulty: beginner
youtube-episode-length: short
introduced: 2026-05
---

## What it is

This registry is itself a design pattern: a single source of truth for
all engineering patterns, structured for both human and machine
consumption, designed so future Claude Code sessions can add new
patterns in a self-consistent way.

The registry registers itself in Constitution as SPEC-181, making the
"how to add a pattern" workflow discoverable from the rule registry.

## Rationale — Why We Adopted This Pattern

*The story of how this pattern came to exist and why it was chosen over alternatives.*

### The problem we kept hitting
New patterns kept being invented (in sessions, audits, retrospectives)
but never registered. The pattern existed in one engineer's head — when
the session ended, so did the institutional knowledge.

### What we tried first (and why it didn't work)
- **Hope someone remembers** — they didn't.
- **Per-project mistakes.md** — siloed.

### The insight that unlocked the solution
**This very registry self-registers as a pattern (DP-036).** Meta-rule:
every new mechanism, workflow, or discipline that survives 2+ uses gets a
DP-NNN file. Registered in Constitution as SPEC-181. The protocol for
adding a pattern is itself a pattern.

### Why this approach, not the obvious one
*Why not just write blog posts?* Because blog posts are linear and don't
have IDs, cross-references, or YouTube angles. The registry is a
queryable, machine-readable database with prose for humans.

### Evidence that it works
- 40 patterns registered to date; the registration protocol has been
  followed for every recent addition.

## Why we use it

Patterns without a home become folk knowledge. Folk knowledge is
re-discovered, re-invented, and contradicted across sessions. A
canonical registry with a registration protocol stops the loss.

## How it works

**Three artifacts:**
1. `README.md` — human-readable overview + protocol
2. `INDEX.md` — machine-readable YAML-ish catalog
3. `patterns/DP-NNN-*.md` — one file per pattern

**Registration protocol** (see README.md):
1. Next free ID
2. Copy template
3. Fill frontmatter (id, name, category, status, constitution-rules,
   youtube-difficulty, youtube-episode-length, introduced)
4. Write 6 mandatory sections (What/Why/How/Example/Related/YouTube)
5. Add to INDEX.md and README.md table
6. If enforcement-bearing, register in Constitution
7. If anti-pattern, append to anti-patterns.md
8. If hook-enforceable, write the hook

**Self-reference:** this pattern (DP-036) is a worked example of itself.

## Example

Adding a 41st pattern:

```bash
# 1. Find next ID
ls ~/Projects/shared/design-patterns/patterns/ | tail -1
# → DP-040-lessons-injection.md
# Next is DP-041

# 2. Copy template
cp ~/Projects/shared/design-patterns/patterns/DP-001-ceo-pm-cis-hierarchy.md \
   ~/Projects/shared/design-patterns/patterns/DP-041-my-new-pattern.md

# 3. Fill frontmatter + 6 sections
# 4. Update INDEX.md
# 5. Update README.md table
# 6. (If enforced) register in Constitution
```

## Related patterns

- [DP-002] Constitution as SSoT
- [DP-037] YouTube episode derivation

## YouTube episode angle

- **Tech-savvy** (5-min): "How I made my pattern library a pattern."
  Recursive registration; show INDEX.md schema. Discuss machine-vs-human
  consumption.
- **Lay audience** (3-min): "A library catalog of how I work." Like a
  recipe book where every recipe also includes the recipe-format rules.

## Known failure modes / lessons learned

- Without machine-readable INDEX.md, automation (audits, dashboards)
  can't enumerate patterns programmatically.
- Pattern files that skip the YouTube section lose their video-seed
  value.
