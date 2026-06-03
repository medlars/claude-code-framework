---
id: DP-026
name: Shared-libs pattern (no cross-project imports)
category: project-structure
status: active
constitution-rules: []
youtube-difficulty: beginner
youtube-episode-length: short
introduced: 2026-04
---

## What it is

A hard rule from `~/Projects/shared/rules.md`:
> "No cross-project imports — projects are independent. Shared code
> lives in `shared-libs/`."

Cross-project shared code goes in `~/Projects/shared-libs/`. Examples:
`pm-base/` (PM script base classes), `central_issue_store/` (CIS
client), `iMessage/` (notification helper), `pm_base_pm_stages/` (shared
stage implementations).

## Rationale — Why We Adopted This Pattern

*The story of how this pattern came to exist and why it was chosen over alternatives.*

### The problem we kept hitting
Project A imported from Project B's `utils/`. Project B refactored.
Project A broke silently because nobody traced the import. By the time
the bug surfaced, two more projects had grown the same cross-coupling.

### What we tried first (and why it didn't work)
- **"Just be careful"** — wasn't.
- **Documented "don't do this"** — done anyway.

### The insight that unlocked the solution
**Cross-project imports are banned; shared code lives only in
`shared-libs/`.** Every project imports from `shared-libs/` (which has
its own PM + tests + versioning). BoundaryWatch BW001 detects
cross-project imports at scan time and files a P0.

### Why this approach, not the obvious one
*Why not allow imports between related projects?* Because "related"
drifts. Today FinanceFlow ↔ CorpBooks are related; tomorrow CorpBooks
spins out. The boundary keeps projects independently releasable.

### Evidence that it works
- BoundaryWatch BW001 fires on the rare attempted cross-project import
  and forces the engineer to either inline the code or move it to
  shared-libs.

## Why we use it

Cross-project imports create invisible coupling. FinanceFlow importing
from CorpBooks means changing CorpBooks can silently break FinanceFlow.
Boundaries enforce that shared code is *intentional* and *versioned*.

## How it works

**Boundary check** (hook: `boundarywatch-post-edit.sh`):
- Edits to `Project_A/src/*.py` that import from `Project_B/...` raise BW001.
- Edits importing from `shared-libs/` are fine.
- Edits importing from `~/Projects/scripts/` (CEO scripts) are fine for
  PM scripts only.

**Layering:**
```
shared-libs/        ← shared code (versioned, breaking changes coordinated)
  pm-base/
  central_issue_store/
  iMessage/
  ...

Project_A/          ← independent
  src/
  tests/

Project_B/          ← independent
  src/
  tests/

scripts/ceo.py      ← orchestrator (knows all projects, but projects don't know each other)
```

**Coordination of breaking changes**: when `shared-libs/pm-base` changes
breakingly, fleet-wide CEO sweep verifies every PM still works. Three
projects depend most heavily: FinanceFlow, CorpBooks, MoeMoney.

## Example

Bad (cross-project):
```python
# In CorpBooks/src/tax.py
from FinanceFlow.src.categorizer import categorize_expense  # ← BW001
```

Good (via shared-libs):
```python
# Move shared logic to shared-libs/tax_categorizer/categorizer.py
# Both projects import from shared-libs:
from tax_categorizer import categorize_expense
```

## Related patterns

- [DP-025] Project floor
- [DP-001] CEO/PM/CIS hierarchy
- [DP-022] pm-registry SSoT

## YouTube episode angle

- **Tech-savvy** (5-min): "Independence via shared-libs." Show the
  boundarywatch hook firing. Walk through pm-base inheritance. Discuss
  why "just import it from the other project" rots fast.
- **Lay audience** (3-min): "Separate tenants, common utilities."
  Apartment building analogy: each unit independent, but shared plumbing
  managed centrally.

## Known failure modes / lessons learned

- Shared-libs version bumps that aren't fleet-tested have caused PM
  regressions (LESSONS for shared-libs changes affecting FF/CB/MM —
  test all three).
- "Just one quick import" rationalizations bypass the hook; per-edit
  detection catches them.
