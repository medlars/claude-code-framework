---
id: DP-022
name: pm-registry.json as project identity SSoT
category: data-management
status: active
constitution-rules: []
youtube-difficulty: intermediate
youtube-episode-length: short
introduced: 2026-05
---

## What it is

`~/Projects/shared/pm-registry.json` is the single source of truth for
every project's identity. Two arrays: `projects` (PM-bearing) and
`non_pm` (websites, hub, config). Each entry carries `canonical`
(lowercase-hyphenated name), `aliases`, `root`, `pm_script`, `type`,
`audit_skill`, `surfaces`. Powers `check.py <name>` (universal test
entrypoint) and `shared-libs/project_resolver.py` (folds any spelling
to canonical).

## Rationale — Why We Adopted This Pattern

*The story of how this pattern came to exist and why it was chosen over alternatives.*

### The problem we kept hitting
Project names were a mess. CIS stored "FinanceFlow", "financeflow",
"finance-flow", and "ff" as different projects — same code, four
different issue buckets. Cross-project queries broke. Aliases were
ad-hoc per script.

### What we tried first (and why it didn't work)
- **Free-form project names in each script** — drifted instantly.
- **A list in CLAUDE.md** — readable but not machine-queryable.

### The insight that unlocked the solution
**One JSON file is the SSoT for project identity.** Every project has a
canonical name (lowercase-hyphenated), aliases, root path, PM script
path, audit skill, and metadata. Every script that handles project names
resolves through `project_resolver.py`.

### Why this approach, not the obvious one
*Why not use directory names directly?* Because directories use TitleCase
(`FinanceFlow/`), CIS uses lowercase (`financeflow`), and audit skills
use slugs (`financeflow-audit`). One file maps all three.

### Evidence that it works
- `check.py <name>` accepts any spelling and resolves to canonical.
- CIS dedup by canonical name eliminated 4-way splits.

## Why we use it

Project names are referenced in: PM scripts, CEO config, CIS issues,
hook matchers, skill `When This Skill Is Invoked` blocks, documentation,
audit skill names. Without a canonical resolver, "FinanceFlow" vs
"financeflow" vs "FF" vs "finance-flow" creates silent gaps — CIS
issues filed under one name aren't visible to the PM querying under
another.

## How it works

**Schema:**
```json
{
  "projects": [
    {
      "canonical": "verscout",
      "aliases": ["Verscout", "Verscout Desktop", "verscout-desktop"],
      "root": "Verscout/desktop",
      "pm_script": "scripts/verscout-pm.py",
      "type": "python",
      "github": "owner/Verscout",
      "audit_skill": "/verscout-audit",
      "surfaces": ["desktop", "marketing", "web"],
      "floor_exempt": false
    },
    ...
  ],
  "non_pm": [...]
}
```

**Resolver** (`shared-libs/project_resolver.py`):
- Accepts any alias / canonical / dir basename
- Returns canonical name + root path + PM script
- Used by `check.py`, CIS writes, hook matchers, CEO dispatch

**Choke-point rule:** CIS writes call resolver in `CentralIssueStore.add()`
so every issue lands under the canonical name. Hooks that filter by
project use the resolver too.

## Example

Universal test entrypoint:
```bash
python3.14 ~/Projects/scripts/check.py "Verscout Desktop" --quick
# → resolved to canonical 'verscout' → runs Verscout/desktop/scripts/verscout-pm.py --quick
```

CIS write:
```python
client.add(rule_id="X", severity="P0", project="FF",  # any spelling
           file_path="...", line_no=..., message="...")
# → canonicalized to 'financeflow' before insert
```

## Related patterns

- [DP-001] CEO/PM/CIS hierarchy (registry is its address book)
- [DP-021] Credentials SSoT (sibling SSoT pattern)
- [DP-025] Project floor

## YouTube episode angle

- **Tech-savvy** (5-min): "One name to rule them all." Show how a typo
  used to silently misroute issues; show the resolver folding 4 spellings
  to one. Discuss the `check.py` universal entrypoint.
- **Lay audience** (3-min): "Every project has a legal name." Like a
  business registration: many nicknames, one official identifier.

## Known failure modes / lessons learned

- LESSONS 064: CIS issue-store project names are canonical at write
  time. Never write raw `INSERT INTO issues` — always go through
  resolver.
- `no-duplicate-project-registry.sh` hook prevents duplicate entries.
- New projects must register in BOTH the markdown table
  (`project-registry.md`) AND the JSON (`pm-registry.json`). The
  `project-forge` skill does this automatically.
