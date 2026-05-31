---
id: DP-NNN                              # Next free number — see INDEX.md
name: Short descriptive name            # ≤ 60 chars; appears in the catalog table
category: governance                    # One of: governance, detection, execution,
                                        # enforcement, quality, data-management,
                                        # project-structure, security, workflow,
                                        # anti-pattern, meta, skills-agents-hooks
status: proposed                        # proposed | active | deprecated
constitution-rules: []                  # [SPEC-NNN, CON-NNN] — backlinks to Constitution
youtube-difficulty: beginner            # beginner | intermediate | advanced
youtube-episode-length: short           # short (5-10 min) | medium (12-15 min) | long (20-25 min)
introduced: 2026-MM                     # YYYY-MM the pattern was first validated
---

<!--
  NEW-PATTERN INSTRUCTIONS (delete this comment before committing):

  1. Pick the next DP-NNN from `INDEX.md` (tail the file, increment by 1).
  2. Save this file as `patterns/DP-NNN-kebab-case-name.md`.
  3. Fill EVERY section below. Sections marked OPTIONAL may be omitted if
     genuinely not applicable, but explain why in one line.
  4. Add a `patterns:` entry to `INDEX.md` matching the frontmatter above.
  5. Add a one-line row to `README.md`'s catalog table.
  6. Add at least one episode seed to
     `categories/12-youtube-episodes/episode-seeds.md`.
  7. If the pattern has an enforcement mechanism, register it in Constitution:

       echo "y" | python3.14 ~/Projects/Constitution/constitution.py add-rule \
         --type specification \
         --title "DP-NNN: <name>" \
         --description "<one-line>" \
         --check-pattern "NONE" \
         --enforcement "documentation" \
         --category "<category>"

  8. If the pattern surfaces a NEW anti-pattern, append `AP-NNN` to
     `~/Projects/shared/anti-patterns.md`.

  Style: short paragraphs, tables over prose for structured info,
  no emojis, no marketing language. Max line 200 chars (CI may enforce).
-->

## What it is

<!-- 1-3 paragraphs. The PATTERN itself — not why or how. -->

## Rationale — Why We Adopted This Pattern

*The story of how this pattern came to exist and why it was chosen over alternatives.*

### The problem we kept hitting

<!-- The specific friction, failure mode, or repeated mistake. Name actual
     incidents if known (e.g. "2026-04-25 DNS migration nuked [your-domain.com] mail"). -->

### What we tried first (and why it didn't work)

<!-- Alternatives considered or attempted. Why they failed or were rejected.
     Bullet form is fine. -->

### The insight that unlocked the solution

<!-- The "aha" moment. The core principle that made the current pattern the
     right answer. 1-2 sentences usually enough. -->

### Why this approach, not the obvious one

<!-- Address the most natural alternative head-on.
     "Why not just X?" answered directly. -->

### Evidence that it works

<!-- Concrete results: bugs prevented, time saved, real incidents caught.
     Reference LESSONS, AP-NNN, CIS issue IDs, session dates where possible. -->

## Why we use it

<!-- Compact statement: the value proposition in one short paragraph.
     This is the section a busy reader scans. Keep it tight. -->

## How it works

<!-- The mechanism: files involved, hook events, CLI commands, schema.
     Tables and code blocks welcome. This is the implementation reference. -->

## Example

<!-- A real or representative case showing the pattern in action.
     Code/shell preferred over prose. -->

## Related patterns

<!-- - [DP-XXX] Name (one line on relationship) -->

## YouTube episode angle

- **Tech-savvy** (10-15 min): <!-- outline; specific demos -->
- **Lay audience** (5-8 min): <!-- analogy first; concrete win second -->

## Known failure modes / lessons learned

<!-- OPTIONAL. Reference LESSONS NNN, AP-NNN, CIS:CIS-XXXX where applicable. -->
