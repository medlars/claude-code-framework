---
id: DP-006
name: 9-dimension cold-read audit methodology
category: detection
status: active
constitution-rules: []
youtube-difficulty: advanced
youtube-episode-length: long
introduced: 2026-05
---

## What it is

A structured audit applied to every project where the auditor reads the
codebase with no prior context and scores it on 9 dimensions. The 2026-05-30
fleet sweep using this methodology identified 2,624 issues across 81
projects, leading to 80+ P0 fixes within 24 hours.

## Rationale — Why We Adopted This Pattern

*The story of how this pattern came to exist and why it was chosen over alternatives.*

### The problem we kept hitting
Auditing a project from the inside (running its own tests, reading its own
docs) misses entire classes of bugs because the author is too close. The
project passes its own checks but a stranger reading the repo finds 30
broken assumptions in 10 minutes.

### What we tried first (and why it didn't work)
- **`pytest --cov`** — measures only what tests measure.
- **External code review** — solo developer, no team.
- **Random LLM "review this code" prompts** — vague output, missed the
  systematic patterns.

### The insight that unlocked the solution
**Auditing needs a checklist with dimensions.** Nine dimensions cover
80% of fleet-relevant bug classes: build, tests, types, data, errors,
security, ops, observability, doc drift. Run each dimension as a
cold-read pass with a fresh-eyes prompt and the model finds bugs the
author rationalized past.

### Why this approach, not the obvious one
*Why not just trust the existing detectors?* Because detectors catch
*known* bug classes. A 9-dim audit catches *unknown* bugs by reading the
code as a stranger would, then a new detector is born for any pattern
worth catching forever.

### Evidence that it works
- 81-project cold-read in 24 hours surfaced 2,624 issues (most P2/P3,
  80+ P0).
- Every audit pass typically births 1-3 new WatchTools detectors.
- 9-dim audit found bugs in WatchTools itself (the auditors needed
  auditing).

## Why we use it

A familiar codebase hides its bugs. The author's mental model fills in
gaps that aren't actually in the code. The cold-read forces the auditor
to assume nothing: every variable, every assumption, every implicit
invariant gets questioned.

## How it works

**The 9 dimensions** (applied in order):
1. **Build integrity** — Does it actually build? Pinned deps? Repro?
2. **Test integrity** — Do tests actually exercise prod code paths? Mocks
   that pass without testing? Schema drift between fixtures and prod?
3. **Type safety** — pyright clean? Any `Any` hiding errors?
4. **Data correctness** — Decimal vs float for money? Timezones? Schema
   migrations?
5. **Error handling** — Bare except? Swallowed exceptions? Sentinel
   returns mixed with raises?
6. **Security** — Secrets in code? SQL injection? Auth bypass?
7. **Operational** — Logging level appropriate? Retries? Rate limits?
   Idempotency?
8. **Observability** — Can you tell from logs alone what happened? PM
   dashboard visible?
9. **Documentation reality gap** — Does the README match the code? Are
   there stub functions claiming completeness?

Each dimension produces a list of findings → CIS issues → fix backlog.

## Example

Cold-read of Moonitor surfaced 6 bugs the author missed:
- `prune_old_items` defined but never wired (dimension 7: operational)
- Apple ns timestamps multiplied by 1e9 unnecessarily (dimension 4: data)
- Two threads writing to SQLite without WAL (dimension 5/6: concurrency)
- Stage swallowed exception via bare `except` (dimension 5)
- README claimed an MCP tool not actually implemented (dimension 9)
- 1806 tests passed but `state.db` schema in tests differed from prod
  (dimension 2: test-prod schema drift)

All 6 became CIS issues, fixed within the session, regressors registered
as TestQualityWatch + SilentFailureWatch detectors so the pattern can't
return.

## Related patterns

- [DP-005] Detector-gap pattern (audit findings often become detectors)
- [DP-007] CIS as durable record (audit output)
- [DP-017] Cold-read audit (general principle)
- [DP-038] Triple Review Protocol (smaller analog)

## YouTube episode angle

- **Tech-savvy** (20-min): Pick one project, audit it live on camera with
  the 9-dim checklist. Annotate each finding with severity. Show the CIS
  output. Compare to traditional code review (line-by-line, single
  perspective) — 9-dim forces multi-perspective sweep.
- **Lay audience** (10-min): "How I find bugs in my own code." Use the
  analogy of a chef who runs through 9 health-inspection questions before
  closing the restaurant: storage temps, hand-wash logs, etc.

## Known failure modes / lessons learned

- Without dimension 2 (test-prod schema drift) the fleet had passing
  tests + broken prod for months (AP-005 Mock-database tests).
- Dimension 5 (error handling) discoveries were the seed for
  SilentFailureWatch (DP-008).
- Dimension 9 (doc reality gap) discoveries seeded GapWatch's
  `placeholder_detector` and `docstring_rot_detector` hooks.
