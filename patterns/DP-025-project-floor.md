---
id: DP-025
name: Project floor (CLAUDE.md + PM + CEO + skills + contracts + SLOs)
category: project-structure
status: active
constitution-rules: []
youtube-difficulty: intermediate
youtube-episode-length: medium
introduced: 2026-04
---

## What it is

The minimum infrastructure every project must have. Currently 36 items
(measured by CapabilityWatch DP-024). The floor is non-negotiable for
non-exempt projects (`floor_exempt: false` in pm-registry.json).

## Rationale — Why We Adopted This Pattern

*The story of how this pattern came to exist and why it was chosen over alternatives.*

### The problem we kept hitting
"What does every project need?" had no canonical answer. New projects
launched without a CLAUDE.md, then realized they needed one. Without a
PM, then needed one. Without an audit skill. Each addition was a manual
retrofit.

### What we tried first (and why it didn't work)
- **Memorize the list** — forgot half of it on each new project.
- **Copy from another project** — copied stale conventions along with
  the structure.

### The insight that unlocked the solution
**The "project floor" is a named bundle of artifacts that every project
must have.** CLAUDE.md + PM script + scripts/ dir + .decisions/ +
contracts/ + docs/slo.md + audit skill + capability set. `project-forge`
scaffolds them; CapabilityWatch checks them.

### Why this approach, not the obvious one
*Why not make these optional?* Because the cost of an absent CLAUDE.md
on a 6-month-old project is high (drift, AI confusion, lost context).
Floor = non-negotiable minimum.

### Evidence that it works
- All 27 PM-bearing projects floor-compliant; new projects compliant from
  hour 0 via `project-forge`.

## Why we use it

A project without a CLAUDE.md is invisible to Claude Code's session
start. A project without a PM script is invisible to CEO. A project
without a spec.md or SLOs slides into "ship and forget" — undocumented,
unmonitored, eventually broken. The floor codifies what "ready for work"
means.

## How it works

**The floor (excerpt of the 36 capabilities):**

| Capability | Where | Why |
|------------|-------|-----|
| `CLAUDE.md` at root | `{project}/CLAUDE.md` | Session start loads it |
| `scripts/{project}-pm.py` | per project | DP-003 contract |
| Register in `pm-registry.json` | shared | DP-022 resolver |
| Register in `ceo.py` | shared | CEO dispatches PM |
| `spec.md` | root or `specs/` | DP-018 |
| `.decisions/` (ADRs) | root | Architecture choices |
| `docs/slo.md` | root | DP-020 NFR check |
| `contracts/` | root | Contract tests (DP-016) |
| `pyproject.toml` with canonical ruff/pyright/mypy | root | DP-016 |
| `pm-baselines.json` | root | PM thresholds |
| `logs/` (gitignored) | root | PM artifacts |
| `TODO.md` | root | Backlog tracking |
| `.gitignore` covering `.env`, `.coverage` | root | Secret/test hygiene |
| Audit skill `/{project}-audit` | `~/.claude/skills/` | DP-006 |

**Bootstrap tool**: `/project-forge` skill scaffolds all of the above
with canonical templates so new projects start at floor compliance.

**Enforcement:** CapabilityWatch (DP-024) measures; CEO `--full` fails
on missing floor items for non-exempt projects.

## Example

Creating a new project:
```bash
# Via project-forge skill (preferred)
/project-forge --name MyNewApp --type python

# Scaffolds:
#   MyNewApp/CLAUDE.md           (@import shared/rules.md + project-specific)
#   MyNewApp/scripts/mynewapp-pm.py
#   MyNewApp/spec.md
#   MyNewApp/.decisions/
#   MyNewApp/docs/slo.md
#   MyNewApp/contracts/
#   MyNewApp/pyproject.toml
#   MyNewApp/pm-baselines.json
#   MyNewApp/.gitignore
#   Updates pm-registry.json (canonical name + alias + root)
#   Updates ceo.py CEO_SCRIPT_MAP
#   Creates ~/.claude/skills/mynewapp-audit/
```

Floor compliance from minute zero.

## Related patterns

- [DP-003] PM script contract
- [DP-022] pm-registry.json
- [DP-024] CapabilityWatch (measures floor)
- [DP-026] Shared-libs pattern

## YouTube episode angle

- **Tech-savvy** (10-min): "What every project must have on day zero."
  Live-create a project with `/project-forge`. Show CapabilityWatch
  immediately showing it as floor-compliant.
- **Lay audience** (5-min): "Building codes for software." Like a
  building inspector's checklist before issuing an occupancy permit.

## Known failure modes / lessons learned

- Projects added before project-forge existed have backfill debt;
  CapabilityWatch's auto-propagation gate is how that gets paid down.
- Floor exemption is allowed (e.g. static websites with no backend) but
  must be explicit data in pm-registry.json, not silent skipping.
