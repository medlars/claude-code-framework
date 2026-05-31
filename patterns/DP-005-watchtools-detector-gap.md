---
id: DP-005
name: WatchTools detector-gap pattern (bug → detector → prevention)
category: detection
status: active
constitution-rules: []
youtube-difficulty: intermediate
youtube-episode-length: medium
introduced: 2026-05
---

## What it is

Every time a bug ships to production (or worse, ships silently), the
question is asked: **"What detector would have caught this?"** If no
detector exists, one is built and added to the **WatchTools** monorepo
(`~/Projects/WatchTools/`). 69 tools, 250+ CIS rule IDs. The bug is the
test case; the detector is the prevention; the CIS rule ID is the durable
record.

## Rationale — Why We Adopted This Pattern

*The story of how this pattern came to exist and why it was chosen over alternatives.*

### The problem we kept hitting
The same bug class kept resurfacing in different projects: bare
`except: pass`, hardcoded `~/` paths, missing test files,
secrets in `.env`. Each one took 10-30 minutes to debug *every time*. By
the third occurrence in a different project, it was no longer a bug — it
was a process failure.

### What we tried first (and why it didn't work)
- **Code review** — solo developer, no second pair of eyes.
- **ESLint/ruff rules** — covered language syntax, missed semantic patterns
  ("you forgot a test alongside this new function" isn't a syntax rule).
- **Pre-commit hooks alone** — too narrow; ran only on commit, not on
  every edit.

### The insight that unlocked the solution
**Every bug found twice should become a detector.** The first instance is
a bug; the second is a class; once you write a detector, it becomes
prevention for the whole fleet, forever. This is the WatchTools
philosophy in one sentence.

### Why this approach, not the obvious one
*Why not just rely on tests?* Because tests catch bugs in the project
they're written for. A detector catches a bug class across all 81 projects
*automatically* — including projects that haven't been written yet,
because new projects pick up WatchTools via `project-forge`.

### Evidence that it works
- 69 WatchTools today, 250+ CIS rule IDs, ~80,000 lines of Python
  protecting the fleet.
- 80+ P0 fixes in a single 2026-05-30 fleet sweep, every one of them a
  bug a detector found that previously would have shipped.
- SilentFailureWatch (DP-008) alone has caught 12 distinct
  exception-swallowing bugs across 7 projects.

## Why we use it

A bug fixed once teaches one project. A bug encoded as a detector teaches
the fleet, forever. The [Your Company] fleet has 81 projects; a fix at the project
level is N=1, but a fix at the detector level is N=81.

The pattern's principle: **the cost of building a detector pays back the
first time a sibling project would have hit the same bug.**

## How it works

**Lifecycle of a detector-gap:**
1. Bug discovered → CIS issue logged with `[CIS:XXX]` ID.
2. Lesson appended to `LESSONS.md` with detector-gap note.
3. New scope added to existing WatchTool, OR new WatchTool created.
4. WatchTool runs at three tiers:
   - **PostToolUse hook** (advisory, on every edit, <5s)
   - **PM stage_watchtools** (quick tier, ≤3 min per project)
   - **CEO full sweep** (full tier, ≤45 min)
5. Findings flow to CIS via `shared/cis_client.py`.
6. Fix applied → CIS issue resolved → detector remains as regression test.

**WatchTool anatomy:**
- `src/` — detector logic, idempotent, no side effects on code
- `tests/` — fixtures simulating the bug
- `scripts/{tool}-pm.py` — registers in `ceo.py`
- `manifest.toml` — declared rule IDs, severity, applicable file types
- `docs/` — what it catches + why
- `logs/`, `TODO.md`, `pm-baselines.json` — standard PM artifacts

**Critical rule:** Tools never fix code. They detect and report. PMs own
fixing. AdvisorWatch is read-only. IssueWatch daemon owns mutation.

## Example

Bug: a test file used `sys.modules.setdefault('google', MagicMock())` at
module scope, poisoning later CF tests session-wide (LESSONS 014).

Response:
1. Lesson logged.
2. New detector added to `TestQualityWatch`: pattern matches
   `sys.modules.setdefault` at module scope outside a fixture.
3. New CIS rule ID: `TQ-FLK-002`.
4. PostToolUse hook flags it on next write.
5. PM `stage_watchtools` fails on existing instances; CIS issues filed.
6. Each project fixes its instances, never reintroduces the pattern.

## Related patterns

- [DP-007] CIS as durable finding record
- [DP-008] SilentFailureWatch (specific WatchTool)
- [DP-013] Hook-as-judiciary (detectors fire as hooks)
- [DP-035] Anti-patterns library (codified bugs)

## YouTube episode angle

- **Tech-savvy** (12-min): Walk through one bug becoming one detector.
  Show the CIS rule ID, the manifest.toml entry, the PostToolUse hook, the
  PM stage call site. Highlight: 69 detectors = 69 bugs we will never
  reintroduce.
- **Lay audience** (5-min): "Every mistake teaches the whole factory."
  Use the analogy of a safety inspector who, after one workplace injury,
  installs a guard on every machine in every facility — not just where
  the injury happened.

## Known failure modes / lessons learned

- LESSONS 022: GapWatch's `hardcoded_detector.py` was scoped to numeric
  literals only; missed string-based SSoT drift (phone numbers, GCP
  project IDs). When extending a detector, enumerate ALL gap categories.
- LESSONS 030: GapWatch `_scan_single_file()` (the hook path) didn't
  honor `_SKIP_PROJECTS`. Lesson: both the bulk and per-file paths must
  share filters.
- LESSONS 068: Secret scanners must exclude binary files (.db, .pyc,
  compiled assets) or they flood with false positives.
- LESSONS 069: Secret scanners must honor `pragma: allowlist secret`
  inline comments.
