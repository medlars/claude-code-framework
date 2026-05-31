---
id: DP-027
name: Policy-change ledger (before lowering thresholds)
category: project-structure
status: active
constitution-rules: []
youtube-difficulty: intermediate
youtube-episode-length: short
introduced: 2026-05
---

## What it is

SE Principle 11 (from `~/.claude/CLAUDE.md`):
> "Never silently change a PM baseline, coverage floor, or quality
> threshold. Before editing any `pm-baselines.json`, floor value, or
> `COVERAGE_FLOOR`/`GRADE_FLOOR`/`MIN_*` constant: log the reason in
> `{project}/logs/policy-changes.md` with date and rationale. If you
> can't write one sentence justifying it, don't change it."

Enforced by `policy-change-ledger.sh` (Write+Edit PreToolUse hook).

## Rationale — Why We Adopted This Pattern

*The story of how this pattern came to exist and why it was chosen over alternatives.*

### The problem we kept hitting
Coverage floors and grade thresholds drifted *downward* silently.
Engineer hits a flaky test, lowers the floor to "ship the fix", forgets
to raise it again, and the quality bar erodes by 5% per quarter.

### What we tried first (and why it didn't work)
- **Honor system** — failed.
- **Code review** — solo developer.

### The insight that unlocked the solution
**Require a written justification BEFORE any threshold change.** A hook
intercepts edits to `pm-baselines.json`, `COVERAGE_FLOOR`, `MIN_*`
constants, etc., and blocks the edit unless `policy-changes.md` was
modified in the same session with a date + reason + re-raise plan.

### Why this approach, not the obvious one
*Why not just track threshold history in git?* Because git tells you
*what* changed, not *why*. The policy-changes ledger captures intent.

### Evidence that it works
- LESSONS 021: "Log policy changes before lowering PM thresholds" — now
  CON-002 enforced.
- No silent drift detected since rollout.

## Why we use it

Thresholds drift downward silently. Coverage was 90%, then 85%, then
80%, then nobody remembers what it should be. Each tiny lowering felt
reasonable in isolation. The ledger makes the cumulative slope visible.

LESSONS 021:
> "Log policy changes before lowering PM thresholds. Write to
> policy-changes.md with reason. CON-002 blocks silent baseline changes."

## How it works

**The ledger** (per-project): `{project}/logs/policy-changes.md`. Each
entry:
```markdown
## 2026-05-25 — Lowered COVERAGE_FLOOR from 85 → 80

**Project**: <FinanceFlow>
**File**: scripts/financeflow-pm.py
**Change**: `COVERAGE_FLOOR = 85` → `COVERAGE_FLOOR = 80`
**Reason**: New e2e test suite added 4k lines of fixtures that aren't
testable directly; pure unit-test coverage of business logic remains
>90%. Will re-raise to 85 once fixtures factored out.
**Re-raise date**: 2026-08-25 (3 months)
```

**Hook trigger:**
- PreToolUse on Write/Edit
- Inspects diff for: changes to `*-baselines.json`, constants matching
  `FLOOR|MIN_|THRESHOLD|MAX_ALLOWED`, lowering only.
- Requires an updated `policy-changes.md` in the same session, or block.

**Quarterly review:** policy-changes.md entries with `Re-raise date` in
the past get flagged in the weekly triage.

## Example

Bad (silent):
```diff
- COVERAGE_FLOOR = 85
+ COVERAGE_FLOOR = 80
```
→ Hook blocks Write: "No policy-changes.md entry for this lowering."

Good:
```bash
# 1. Edit policy-changes.md with rationale + re-raise date
# 2. Then edit the constant
```
→ Hook permits.

## Related patterns

- [DP-002] Constitution as SSoT
- [DP-013] Hook-as-judiciary
- [DP-020] Definition of Done

## YouTube episode angle

- **Tech-savvy** (5-min): "Why I require a paper trail for every
  loosened constraint." Show the slope over time without a ledger,
  then with one. Discuss the re-raise mechanic.
- **Lay audience** (3-min): "Don't lower the bar without saying why."
  Like a school accreditation board: lowering pass marks requires a
  documented justification and a re-evaluation date.

## Known failure modes / lessons learned

- LESSONS 021 (origin): without the ledger, thresholds slid undetected
  for weeks.
- The hook only catches lowering, not raising — raising is always
  permitted.
