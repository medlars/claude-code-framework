---
id: DP-024
name: CapabilityWatch 36-capability registry
category: data-management
status: active
constitution-rules: [CAP-KEY-001]
youtube-difficulty: advanced
youtube-episode-length: medium
introduced: 2026-05
---

## What it is

A registry of 36 engineering capabilities (in
`~/Projects/WatchTools/capabilitywatch/capabilitywatch.db`) tracked
across 27 projects. Each capability is something a project should have
(e.g. "has CLAUDE.md", "has PM script", "has spec.md", "has SLO doc",
"has rollback procedure"). CapabilityWatch detects gaps and supports
**safe auto-propagation** behind a worktree+PM gate.

## Rationale — Why We Adopted This Pattern

*The story of how this pattern came to exist and why it was chosen over alternatives.*

### The problem we kept hitting
"Every project should have X" lived in tribal knowledge. New projects
forgot half the items. Existing projects drifted: some had a Makefile,
some didn't; some had a TODO.md, some used a different file.

### What we tried first (and why it didn't work)
- **A "project floor" doc** — read once, ignored.
- **project-forge scaffolds** — got new projects right, but existing
  projects drifted.

### The insight that unlocked the solution
**Codify capabilities as data, then detect their absence.** 36 named
capabilities (`pm_script`, `slo_doc`, `adr_dir`, `dogfood_log`,
`changelog`, …). CapabilityWatch walks each project and reports
green/red per capability. Auto-propagation (gated by worktree + PM) can
add a missing capability via a known recipe.

### Why this approach, not the obvious one
*Why not just `project-forge` all the things?* Because project-forge is
a write-once tool; capabilities are a continuous check. Both are
needed: forge for new, watch for drift.

### Evidence that it works
- 36 capabilities, 27 projects, green/red matrix actionable at a glance.
- Capabilities added since rollout propagated to all eligible projects
  via auto-propagation gated by tests.

## Why we use it

Project floor (DP-025) defines what every project should have, but
without measurement the floor is aspirational. CapabilityWatch turns the
floor into data — every project's row, every capability's column,
green/red cells. Drift visible. Auto-propagation makes it cheap to
backfill new capabilities fleet-wide.

## How it works

**Schema:** `capabilitywatch.db` has tables `capabilities`, `projects`,
`assessments` (per-project x per-capability score).

**Capability examples** (from the 36):
- `has_claude_md` — `CLAUDE.md` at project root
- `has_pm_script` — `scripts/{project}-pm.py` exists
- `has_slo_doc` — `docs/slo.md` with at least one SLO
- `has_threat_model` — `.decisions/threat-model.md` (PHI/financial projects)
- `has_contract_test` — `contracts/` dir with JSON schemas
- `has_test_alongside` — every src module has matching tests
- `has_rollback_procedure` — spec.md has Rollback section
- `has_dep_policy` — `pyproject.toml` pinned + cve audit log

**Scan:** `python3.14 scripts/capabilitywatch-pm.py --quick` walks each
project and writes to `assessments`.

**Auto-propagation gate** (the safety mechanism):
- New capability declared in CapabilityWatch
- Auto-fix branch created per project in a worktree
- PM `--quick` runs in the worktree
- Only if PM stays green is the auto-fix surfaced for review
- Human approves before merge

**Required-only mode** (LESSONS for capabilitywatch): in `--required`
mode, projects flagged `floor_exempt: false` in `pm-registry.json` must
have all 36 capabilities; exempt projects (websites without backends)
get a curated subset.

## Example

Add a new capability: "has dogfood log entry in last 30 days".

```python
# capabilitywatch/src/checks/has_recent_dogfood.py
def check(project_root: Path) -> Score:
    log = project_root.parent / "shared" / "dogfood-log.md"
    last_entry_ts = parse_last_entry_for_project(log, project_name)
    if last_entry_ts is None or (now() - last_entry_ts).days > 30:
        return Score(value=0.0, reason="No dogfood entry in 30 days")
    return Score(value=1.0)
```

Next CEO sweep: 24 projects assessed, 6 fail. The CIS issues land
under `CAP-DOGFOOD-001`.

## Related patterns

- [DP-004] CEO propagation rule (CapabilityWatch is propagation by data)
- [DP-022] pm-registry (CapabilityWatch consumes it)
- [DP-025] Project floor (what CapabilityWatch measures)

## YouTube episode angle

- **Tech-savvy** (10-min): Show the 36-capability matrix. Live-add a
  new capability, watch the fleet sweep flag missing projects. Discuss
  the auto-propagation gate (worktree + PM = safety).
- **Lay audience** (5-min): "A scorecard for every project." Like a
  health checkup matrix at a clinic: every patient, every required
  vaccination, green or red.

## Known failure modes / lessons learned

- LESSONS (session capabilitywatch-required-only): `stage_capabilitywatch_impl`
  must run in required-only mode to avoid flagging website/non-PM
  projects for backend-only capabilities.
- LESSONS (watchtools propagation 8-pattern sweep): `_result not defined`
  bug in capabilitywatch crash path — sys.path inserts before module
  import was the root cause; CEO scanner now detects defs not calls.
- Auto-propagation must always go through worktree + PM gate; direct
  fleet-wide writes have caused regressions.
