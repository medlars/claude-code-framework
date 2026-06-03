---
id: DP-037
name: YouTube episode derivation from design patterns
category: meta
status: active
constitution-rules: []
youtube-difficulty: beginner
youtube-episode-length: short
introduced: 2026-05
---

## What it is

A workflow: every design pattern in this registry seeds at least one
YouTube episode for the Vohux channel. The mandatory "YouTube episode
angle" section in each pattern file gives two pitches: tech-savvy
(10-15 min) and lay audience (3-8 min). `categories/12-youtube-episodes/
episode-seeds.md` aggregates the candidates.

## Rationale — Why We Adopted This Pattern

*The story of how this pattern came to exist and why it was chosen over alternatives.*

### The problem we kept hitting
The Vohux YouTube channel needs a steady stream of content. Coming up
with episode ideas from scratch every week is exhausting. Most of the
ideas were already implicit in the engineering work — we just didn't
extract them.

### What we tried first (and why it didn't work)
- **Brainstorming sessions** — ad-hoc, output uneven.
- **"What did I work on this week"** — too granular for an episode.

### The insight that unlocked the solution
**Every design pattern is at least one YouTube episode.** Each pattern
file has a `YouTube episode angle` section with two takes (tech-savvy
deep dive + lay-audience explainer). The episode-seeds.md file
aggregates these into a production-ready list.

### Why this approach, not the obvious one
*Why not just batch-write episode ideas?* Because patterns are the
*source*; episodes are *derived*. Updating a pattern auto-improves the
episode. Single source of truth.

### Evidence that it works
- 24 episode seeds across 7 series, all derived from the 40 patterns.

## Why we use it

The Vohux channel ("how a solo physician runs a software fleet with
Claude Code") needs a content backlog. Rather than improvising topics
weekly, every engineering pattern becomes a video opportunity with the
script pre-outlined in its pattern file.

## How it works

**Per-pattern fields:**
- `youtube-difficulty` (beginner | intermediate | advanced)
- `youtube-episode-length` (short = 5min, medium = 15min, long = 30min+)
- YouTube section with two angles

**Aggregation:**
- `categories/12-youtube-episodes/episode-seeds.md` lists working titles
  and pattern IDs covered.
- Each entry includes: hook (why care), key takeaways (3 bullets),
  duration estimate, target audience.

**Production sequence:**
1. Pick a seed from `episode-seeds.md`.
2. Open referenced pattern files; use their YouTube section as outline.
3. Cross-link pattern IDs in the video description so viewers can dive
   deeper at `~/Projects/shared/design-patterns/`.
4. After recording: mark the seed as `produced: YYYY-MM-DD` + add URL.

## Example

Episode 7: "Why Memory Without a Hook Is Useless"
- Covers DP-013 (Hook-as-judiciary), DP-040 (Lessons injection)
- Target: intermediate
- Duration: 15 min
- Hook: "I told my AI 'don't do X' and it did X anyway"
- Takeaways: hooks are enforcement / memory is suggestion / 180 hooks
  in this fleet
- Production outline: pull from DP-013's tech-savvy angle.

## Related patterns

- [DP-036] Self-registration (sibling meta pattern)
- All other DP-NNN patterns (each is a seed)

## YouTube episode angle

- **Tech-savvy** (5-min): "How I never run out of YouTube topics." Show
  the registry → seeds → episode pipeline. Production efficiency talk.
- **Lay audience** (3-min): "Documentation that doubles as a script."
  How writing things down twice pays back when you also make videos.

## Known failure modes / lessons learned

- YouTube sections written as marketing fluff fail as scripts. Keep
  them concrete (specific examples, file paths, real incidents).
- Episodes that span 5+ patterns are too dense; cap at 3 patterns per
  episode.
