---
id: DP-001
name: CEO/PM/CIS three-tier supervision hierarchy
category: governance
status: active
constitution-rules: []
youtube-difficulty: intermediate
youtube-episode-length: long
introduced: 2026-04
---

## What it is

A three-tier control structure that governs every project in the fleet.
Claude Code is the engineer; each project has a **PM script** that owns its
quality pipeline; a single **CEO script** aggregates all PMs and enforces
cross-project consistency; and the **Central Issue Store (CIS)** is the
shared durable record of every finding from every detector.

| Tier | Owns | File |
|------|------|------|
| Claude Code | edits, commits, calls subagents | (the model) |
| **PM** | one project's pipeline (build/test/lint/security/SLO) | `{project}/scripts/{project}-pm.py` |
| **CEO** | cross-project consistency, propagation, dashboard | `~/Projects/scripts/ceo.py` |
| **CIS** | durable findings ledger | `~/Projects/.uis/issues.db` |

## Rationale — Why We Adopted This Pattern

*The story of how this pattern came to exist and why it was chosen over alternatives.*

### The problem we kept hitting
By April 2026 the fleet had grown to 24 active projects plus 57 WatchTools
phases. Each project had its own test-running convention, its own concept of
"done", and its own ad-hoc PM script. There was no single place to ask
"is the fleet green right now?" — answering it took 20 minutes of `cd` and
`pytest`. Worse, a fix made in FinanceFlow never propagated to MoeMoney
or CorpBooks even when the bug class was identical (e.g. the inline
`stage_cis_health` divergence in AP-013 hit three projects in succession).

### What we tried first (and why it didn't work)
- **GitHub Actions only** — runs post-push, slow feedback (5-10 min per
  commit), no local awareness, no cross-project visibility.
- **A single mega-PM script** — got to ~3,000 lines before becoming
  unmaintainable; project-specific edge cases drowned out the common pipeline.
- **Per-project README "how to test" sections** — drifted within a month.

### The insight that unlocked the solution
**Quality is a property of the pipeline, not of the engineer.** If the
pipeline lives in version control, the engineer is interchangeable. The
model layer (Claude Code) is stochastic; the script layer (PM + CEO + CIS)
is deterministic and survives across sessions. By moving state and policy
into scripts, we made the model a worker following a foreman's
instructions, not a co-author of policy.

### Why this approach, not the obvious one
*Why not just use a CI server like Buildkite or Jenkins?* Because the
feedback loop must run in < 60s after every edit — a CI server is too far
away. The PM script runs locally on the dev machine, surfaces findings in
the same shell, and only the **summary** (grade + counts) goes to the
fleet dashboard. Best of both worlds: local speed, fleet visibility.

### Evidence that it works
- 2026-05-30 fleet sweep: CEO ran all 81 PMs in parallel, surfaced 2,624
  issues in one pass.
- AP-013 (inline `stage_cis_health`) was detected and fixed across all
  three projects in a single session because the CEO propagation check
  flagged the divergence.
- Cross-session continuity: a Stop-hook regression in TestWatch was
  caught by `--touched` 14 seconds after the offending edit, before the
  next file was opened.

## Why we use it

Without this hierarchy a fleet of 81 projects becomes 81 personal styles.
Symptoms before the hierarchy existed: each project had its own
test-running convention, its own concept of "done", its own lint config, no
way to know which projects were green at any moment, no way to apply a fix
fleet-wide. With the hierarchy: every project answers the same five
questions (build pass? tests pass? lint clean? security clean? grade ≥
baseline?) and the CEO turns 81 yes/no answers into a single dashboard.

The model layer (Claude Code) is fast but stochastic; the script layer (PM
and CEO) is deterministic and survives across sessions. By putting state
and policy in scripts, the model becomes interchangeable — it is just
another worker following the foreman's instructions.

## How it works

**PM script contract (per project):**
- Lives at `{project}/scripts/{project}-pm.py`.
- Exposes 3 invocation modes: `--touched` (10–60s after each edit),
  `--quick` (4–7 min after a phase), `--full` (7–15 min before release).
- Owns stages: `stage_build`, `stage_test`, `stage_lint`, `stage_security`,
  `stage_codewatch`, `stage_cis_health`, `stage_watchtools`, `stage_runtime`,
  `stage_contract_test`, `stage_mutation`, `stage_chaos`, `stage_ux`,
  `stage_propagation`.
- Writes `logs/pm-last-status.json` (machine-readable state) and
  `logs/pm.log` (audit trail).
- Publishes to `~/Projects/ceo-dashboard.json` via `publish_and_persist()`.

**CEO script:**
- Runs all PMs in parallel.
- Aggregates `pm-last-status.json` from each → `ceo-dashboard.json`.
- Enforces `PROPAGATION_PATTERNS`: when a stage exists in one PM and is
  applicable elsewhere, flags missing PMs.
- Commands: `ceo.py --quick`, `--full`, `--report`, `--propagation-check`,
  `--auto` (autonomous fix loop).

**CIS:**
- Single SQLite DB at `~/Projects/.uis/issues.db`.
- Schema: `issues` (open/resolved findings) + `issue_events` (audit trail).
- All WatchTools write via `shared/cis_client.py` → `CentralIssueStore.add()`.
- Stage `stage_cis_health` queries it per-project and fails on open P0s.
- Canonical project names enforced at write time (lowercase, hyphenated).

## Example

A typical edit cycle in FinanceFlow:

```bash
# 1. Engineer edits a .gs file
vim FinanceFlow/src/SpreadsheetRouter.gs

# 2. PostToolUse hook fires PM --touched (auto)
ceo-supervisor-hook.sh → python3.14 scripts/financeflow-pm.py --touched

# 3. PM writes pm-last-status.json + publishes to ceo-dashboard.json
# 4. CIS gets any new findings (e.g. CodeWatch detected a missing import)

# 5. Engineer queries before next edit
python3.14 scripts/financeflow-pm.py query risk --file SpreadsheetRouter.gs

# 6. Before release: full pass
python3.14 scripts/financeflow-pm.py --full
python3.14 ~/Projects/scripts/ceo.py --full
```

## Related patterns

- [DP-002] Constitution as SSoT for all rules
- [DP-003] PM script contract (14-part structure)
- [DP-004] CEO propagation rule
- [DP-007] CIS as durable finding record
- [DP-022] pm-registry.json as project identity SSoT

## YouTube episode angle

- **Tech-savvy** (15-min): Walk through a real edit cycle. Show
  `pm-last-status.json` before/after a change. Open `ceo-dashboard.json`
  live. Demonstrate `--propagation-check` flagging a missing stage. Compare
  to GitHub Actions (centralized, post-push) vs. local PM (decentralized,
  per-edit).
- **Lay audience** (8-min): "I built a robot factory foreman." Use the
  analogy of a 1,000-room hotel with a manager for each floor and a
  hotel-wide GM. Show the dashboard turning red when one room is dirty.
  Emphasize: the human (owner) only looks at one screen.

## Known failure modes / lessons learned

- AP-013: Inlining `stage_cis_health` instead of delegating to shared-libs
  diverges the canonical implementation and hides bugs.
- LESSONS 002: A behavioral memory without a hook is advisory only — the PM
  is the enforcement vehicle for policy, not memory.
- LESSONS 064: CIS project names must be canonical at write time; renames
  break cross-project lookups.
