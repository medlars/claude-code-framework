---
id: DP-007
name: CIS (Central Issue Store) as durable finding record
category: detection
status: active
constitution-rules: []
youtube-difficulty: intermediate
youtube-episode-length: medium
introduced: 2026-05
---

## What it is

A single SQLite database (`~/Projects/.uis/issues.db`) that holds every
finding from every detector across the fleet. Two tables: `issues` (open +
resolved findings) and `issue_events` (audit trail). All writes go through
`CentralIssueStore.add()` in `~/Projects/shared-libs/central_issue_store/`.
Project names are canonicalized (lowercase-hyphenated) at write time so
queries always resolve.

## Rationale — Why We Adopted This Pattern

*The story of how this pattern came to exist and why it was chosen over alternatives.*

### The problem we kept hitting
Bugs found in session A got fixed in session B but had no durable record.
Detectors fired, output scrolled past, sessions ended, findings vanished.
Six weeks later the same bug came back in a different project and there
was no memory it had ever existed.

### What we tried first (and why it didn't work)
- **TODO.md per project** — drifted, never queried cross-project.
- **GitHub Issues** — one repo per issue tracker, no cross-project view.
- **Markdown reports** — read once, never again.

### The insight that unlocked the solution
**Findings are data, not prose.** Every finding gets a stable ID
(`CIS-XXXXXXX`), a severity (P0/P1/P2/P3), a project, a rule ID, a
status (open/resolved), and a timestamp. Now you can query "all open P0s
in <FinanceFlow>", "all CIS-25761 occurrences fleet-wide", "issues older
than 7 days".

### Why this approach, not the obvious one
*Why not use Linear or Jira?* Because (a) the issues come from
automated detectors running on every edit, and external trackers throttle
on volume; (b) the issues need to be queried *by other PMs and hooks*
synchronously — an external API is too slow.

### Evidence that it works
- 2624 issues durably tracked in a single sweep.
- `stage_cis_health` per project queries CIS in <50ms and blocks the
  pipeline on open P0s.
- Cross-project pattern detection (e.g., AP-013) became possible because
  every project's findings live in the same SQLite DB.

## Why we use it

Before CIS, findings lived in scattered logs that nobody read. Same bug
discovered by 3 detectors → 3 silent reports. With CIS, every finding
gets a stable ID, a severity (P0/P1/P2/P3), a status, and a project link.
Stages query CIS, not their own logs. Issues get triaged centrally.

## How it works

**Schema:**
```sql
issues (id PK, rule_id, severity, project, file_path, line_no, message,
        status [open|resolved|suppressed], created_at, resolved_at,
        deduplication_hash)
issue_events (id PK, issue_id FK, event_type, note, ts)
```

**Write API** (`CentralIssueStore.add()`):
- Canonicalizes project name via `pm-registry.json`
- Computes dedup hash (project + rule_id + file + line + message)
- Inserts or updates `last_seen`
- Logs `issue_event` for audit

**Query API**:
- `cis-view.py` — terminal listing (open P0s first)
- `stage_cis_health` (in every PM) — fails on open P0s for that project
- `IssueWatch` daemon — local-AI prioritization on top of CIS findings

**Hooks**:
- `cis-p0-gate.sh` blocks Stop if any open P0 exists for current project
- `cis-hypothesis-gate.sh` requires a hypothesis before claiming a fix

## Example

A WatchTool detects a bare except in `Verscout/desktop/src/foo.py:42`:

```python
from cis_client import client
client.add(
    rule_id="CQ-EXC-001",
    severity="P1",
    project="verscout",  # canonicalized at write
    file_path="desktop/src/foo.py",
    line_no=42,
    message="bare except: swallows all exceptions",
)
```

Next Stop attempt:
```
$ python3.14 scripts/verscout-pm.py --touched
stage_cis_health: FAIL — 1 open P1 (CQ-EXC-001 at desktop/src/foo.py:42)
```

After fix:
```python
client.resolve(issue_id, note="replaced with except ValueError")
```

## Related patterns

- [DP-001] CEO/PM/CIS hierarchy
- [DP-005] Detector-gap pattern (CIS is the output channel)
- [DP-014] Hypothesis gate (gates use CIS state)
- [DP-040] Lessons-as-injected-context (CIS issues graduate to LESSONS.md)

## YouTube episode angle

- **Tech-savvy** (12-min): Show the SQLite schema. Run a live detector,
  watch the row appear in CIS. Show the stage gate failing. Fix the
  issue, watch it resolve.
- **Lay audience** (5-min): "Every bug has a paper trail." Use the
  analogy of a hospital incident report system — every finding gets a
  number, a severity, a fix log.

## Known failure modes / lessons learned

- LESSONS 064: CIS issue-store project names are CANONICAL (lowercase,
  via pm-registry.json) — never write raw `INSERT` with display names.
- LESSONS 071: Test fixtures must create BOTH `issues` and `issue_events`
  tables; missing `issue_events` causes shared impl to raise.
- AP-013: Inlining `stage_cis_health` instead of delegating to
  `stage_cis_health_impl()` makes the broad `except` turn all bugs into
  silent skips.
