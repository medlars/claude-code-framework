---
id: DP-034
name: Boring technology bias (stable over cutting-edge)
category: workflow
status: active
constitution-rules: []
youtube-difficulty: beginner
youtube-episode-length: short
introduced: 2026-05
---

## What it is

A standing preference from `~/.claude/CLAUDE.md`:
> "When choosing a new dependency, framework, or approach, prefer
> boring, stable, well-documented choices over cutting-edge ones. Plain
> SQL over ORMs. Established frameworks over novel ones. The model's
> training data is deepest on boring technology — clever tech choices
> multiply hallucinated API calls."

(Source: Armin Ronacher, Jun 2025.)

## Rationale — Why We Adopted This Pattern

*The story of how this pattern came to exist and why it was chosen over alternatives.*

### The problem we kept hitting
Picking a novel framework (the latest ORM, the trendiest meta-framework)
multiplied hallucinated API calls. The model's training data wasn't deep
on the new tool, so it guessed — and guessed wrong, eating hours of
debugging.

### What we tried first (and why it didn't work)
- **Cutting-edge stack** — looked sophisticated, broke constantly.
- **Pinning recent SDK versions** — the SDK changed faster than docs.

### The insight that unlocked the solution
**Prefer boring, stable, well-documented technology.** Plain SQL over
ORMs. Established frameworks over novel ones. Python 3.14, Astro 6,
Swift 6.3, Postgres, Redis — the model has seen these millions of
times and gets them right on first shot. (Source: Armin Ronacher,
Jun 2025.)

### Why this approach, not the obvious one
*Why not stay current with the newest tools for performance?* Because the
correctness tax of novelty (debugging hallucinated APIs) far exceeds the
performance benefit at our scale.

### Evidence that it works
- Code written in boring tech stacks ships first-shot at much higher
  rates than code in trendy stacks.
- No "library refactor because v2 changed everything" debt.

## Why we use it

LLMs hallucinate API calls more often on libraries they've seen less of.
A cutting-edge framework with 3,000 stars and minimal training data is
a code-generation minefield. A boring framework with 50,000 stars and
years of training data generates working code on the first shot.

The deeper truth: novelty has a tax in correctness, and the owner pays
the tax in debug time.

## How it works

**Decision rule:**
- New dep needed → check: how old is it? Last commit date? Stars?
  Training data depth?
- Prefer: Postgres, Redis, Flask, Next.js stable, plain SQL, requests,
  pytest
- Avoid (without strong reason): bleeding-edge ORMs, new web
  frameworks, novel async libraries

**Fleet-standard stacks** (`~/Projects/shared/rules.md`):
- Python 3.14 + ruff + pyright + pytest
- Astro 6 + Tailwind 4 for sites
- Swift 6.3 + AppKit (not SwiftUI) for native apps
- BigQuery + Cloud Functions + Apps Script for the FF/CB/MM stack

**Hook**: `new-dependency-cve-gate.sh` runs CVE check and last-commit
check on any new dep added to `pyproject.toml`.

## Example

Need a queue? Choices:
- **Boring**: Redis BLPOP, ~30 lines of code. Done.
- **Novel**: try `arq` or `procrastinate` or some 2024 async lib.

For Vohux infrastructure: Redis. The boring choice. The model knows it
inside-out, the docs are mature, the failure modes are well-known.

## Related patterns

- [DP-018] Spec-driven dev (boring-tech bias is a design constraint)
- [DP-039] Two-persona split (PM persona evaluates the bias)

## YouTube episode angle

- **Tech-savvy** (5-min): "Why I use boring tech." Cite Armin Ronacher.
  Show a hallucinated API call on a novel lib vs clean code on a boring
  one. Discuss the correctness tax of novelty.
- **Lay audience** (3-min): "Use the tool everyone knows." Analogy: a
  plumber doesn't bring an experimental wrench to a leak; they bring
  the one they've used for 20 years.

## Known failure modes / lessons learned

- The bias has exceptions: SagaMail uses Swift 6.3 strict concurrency
  (novel) because the alternative (Objective-C) is older but worse.
  Novelty is sometimes correct — the bias is a default, not a law.
- LESSONS 062: Fleet had no coding standard until ruff+pyright+mypy
  fleet-wide; the boring stack won.
