---
id: DP-020
name: Definition of Done (NFR checklist)
category: quality
status: active
constitution-rules: []
youtube-difficulty: beginner
youtube-episode-length: short
introduced: 2026-05
---

## What it is

A feature is NOT done until all NFR (non-functional requirement) checks
pass. From `~/Projects/shared/rules.md`:

- **Accessibility**: no VoiceOver/keyboard regressions (UI changes)
- **Performance**: no measurable startup/render regression vs PM baseline
- **i18n readiness**: no new hardcoded user-visible strings
- **Security**: no new secrets in code
- **PM**: pipeline green, grade ≥ starting grade
- **Last-20%** (SE Principle 12): rate-limit/retry, structured logging,
  input validation at boundaries — required on every new handler

## Rationale — Why We Adopted This Pattern

*The story of how this pattern came to exist and why it was chosen over alternatives.*

### The problem we kept hitting
"Done" was synonymous with "tests pass" — but tests covered functionality,
not NFRs. Features shipped with no accessibility, hardcoded strings,
missing security headers, no observability. Production users surfaced
problems that should have been caught before merge.

### What we tried first (and why it didn't work)
- **Manual code review for NFRs** — solo developer, no second reviewer.
- **Adding NFRs to spec.md only** — not enforced at done-time.

### The insight that unlocked the solution
**Bake NFRs into the Definition of Done.** Last-20% rule (SE Principle
12): no new handler is done until it has rate limiting/retry, structured
logging, and input validation at the boundary. Plus the broader checklist:
a11y, perf baseline, no hardcoded strings, no new secrets, PM green.

### Why this approach, not the obvious one
*Why not just trust the engineer to handle NFRs?* Because NFRs are
boring, easy to forget, and don't surface in functional tests. A
checklist makes them mechanical.

### Evidence that it works
- Last-20% hook (`last20-and-test-alongside.sh`) catches missing logging
  and validation on new handlers regularly.

## Why we use it

"Functional tests pass" is the lower bound, not the bar. NFRs catch the
slow rot: a feature ships green, but a11y regresses, latency creeps up,
hardcoded strings block localization. Bundling NFRs into DoD makes them
non-deferrable.

## How it works

**Three layers of enforcement:**

1. **Hooks** (per-edit advisory):
   - `accessibility-gate.sh` — WCAG checks on HTML edits
   - `performance-regression-gate.sh` — perf baseline diff
   - `i18n-hardcoded-string-gate.sh` — string literal detection
   - `secrets-in-content.sh` — secret pattern detection
   - `last20-preflight.sh` — handler missing NFRs

2. **PM stages** (per-quick-pass):
   - `stage_ux` — accessibility + responsiveness
   - `stage_runtime` — perf + SLO
   - `stage_security` — secret scan

3. **CEO sign-off** (per-release):
   - `ceo.py --full` aggregates per-PM NFR results
   - Cross-PM `--propagation-check` flags missing NFR stages

## Example

Ship a new dashboard widget in Verscout:

Without DoD: tests pass → ship → 3 users report keyboard-trap on Mac
voice control next week.

With DoD: `stage_ux` runs accessibility audit → flags missing ARIA labels
on widget controls → blocks PM grade → handler missing rate-limit on
`/api/widget/state` (last-20% violation) → blocked → fix both → ship.

## Related patterns

- [DP-016] Immaculate code protocol (DoD is its conceptual frame)
- [DP-019] Test-alongside
- [DP-025] Project floor

## YouTube episode angle

- **Tech-savvy** (5-min): Walk through the NFR list. Show a feature
  blocked by each one in turn. Discuss why NFRs are easier to enforce
  at edit-time than retroactively.
- **Lay audience** (3-min): "Done means done done." Use the auto-shop
  analogy: not "the engine runs" but "the engine runs, brakes work,
  lights work, signals work, registration current".

## Known failure modes / lessons learned

- NFRs that nobody owns don't get fixed. Stage names + PM owner =
  durable responsibility.
- A11y regressions are easy to miss until users complain; the static
  scanner is the safety net, not a substitute for real testing.
