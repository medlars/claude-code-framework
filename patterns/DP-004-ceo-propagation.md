---
id: DP-004
name: CEO propagation rule (cross-PM consistency)
category: governance
status: active
constitution-rules: []
youtube-difficulty: advanced
youtube-episode-length: medium
introduced: 2026-04
---

## What it is

A discipline enforced by `ceo.py --propagation-check`: when a
constructive rule, stage, or empowerment lands in one PM and is
applicable to others, the CEO flags every PM that lacks it. A
`PROPAGATION_PATTERNS` list in `ceo.py` records each pattern as
`(stage_name, applies_to_dict)`.

## Rationale — Why We Adopted This Pattern

*The story of how this pattern came to exist and why it was chosen over alternatives.*

### The problem we kept hitting
A fix landed in FinanceFlow that should have been applied to MoeMoney
and CorpBooks (all three use the same shared-libs PM base). Nobody
remembered to propagate. Six weeks later the same bug bit MoeMoney in
production.

### What we tried first (and why it didn't work)
- **Manual TODO entries** — got lost in per-project TODO.md drift.
- **Slack reminders** — the owner is a physician, not always at a keyboard.
- **"Just refactor into shared-libs"** — only works when the change is
  pure logic, not when it's a per-project stage configuration tweak.

### The insight that unlocked the solution
**Drift is detectable.** A constructive change to one PM (new stage,
stricter threshold, additional check) is a *pattern* that other PMs may
or may not have. The CEO can enumerate `PROPAGATION_PATTERNS` and walk
the fleet looking for missing siblings — and surface them as a propagation
report, not a free-form "you should consider…".

### Why this approach, not the obvious one
*Why not require all PMs to use a shared base class?* Because some stages
are intentionally not universal (GAS projects don't have `stage_mutation`
because there's no Python to mutate). Propagation must be *advisory*,
not mandatory — the human signs off on each propagation.

### Evidence that it works
- WatchTools 8-pattern fleet sweep (2026-05-30): CEO surfaced 8 different
  patterns missing across various PMs; after fixing, drift = 0 across
  the whole fleet.
- AP-013 (inline `stage_cis_health`) was propagation-detected in 3
  projects within 2 minutes.

## Why we use it

Without this rule, FinanceFlow gets a new `stage_chaos` and the other 8
PMs stagnate. Six months later, only one project has chaos coverage and
the fleet drifts into 81 personal styles. Propagation enforces the
invariant: **anything useful in one PM is owed to every applicable PM.**

## How it works

`PROPAGATION_PATTERNS` (in `ceo.py`):

```python
PROPAGATION_PATTERNS = [
    ("stage_contract_test", {"FinanceFlow": True, "CorpBooks": True, "MoeMoney": True, ...}),
    ("stage_chaos",         {"FinanceFlow": True, "CorpBooks": True, "MoeMoney": True, "EpicVDI": True}),
    ("stage_ux",            {<all visual products>: True}),
    ("stage_runtime",       {<all daemon products>: True}),
    ...
]
```

`ceo.py --propagation-check` walks every PM module, introspects for stages,
and prints:

```
DRIFT: stage_chaos missing in MoeMoney (applies_to=True)
DRIFT: stage_chaos missing in EpicVDI (applies_to=True)
OK:    stage_contract_test present in FinanceFlow, CorpBooks, MoeMoney
```

When `applies_to` is False (e.g. Constitution has no UI → `stage_ux=False`),
it's exempted. Exemptions are explicit data, not silent skips.

## Example

A new `stage_silent_failure_check` lands in FinanceFlow's PM. The owner
adds one line to `ceo.py`:

```python
("stage_silent_failure_check", {p: True for p in ALL_PRODUCT_PMS}),
```

Next `ceo.py --propagation-check` flags 23 PMs missing the stage. Each is
fixed by adding `from pm_base_pm_stages import stage_silent_failure_check_impl`
and a one-line wrapper. The pattern is now fleet-wide.

## Related patterns

- [DP-001] CEO/PM/CIS hierarchy (CEO sits above PMs)
- [DP-003] PM script contract (the surface CEO inspects)
- [DP-023] WatchTools manifest (cross-tool propagation analog)

## YouTube episode angle

- **Tech-savvy** (12-min): Live-demo `--propagation-check`, add a stage
  to one PM, watch it light up across the fleet. Compare to monorepo CI
  matrices (every change runs on every project) vs. polyrepo drift.
- **Lay audience** (5-min): "How I keep 24 projects from drifting." Show
  the dashboard: 24 rows, 14 columns of green/red squares. Explain that
  when one row gets a new column, the others must too.

## Known failure modes / lessons learned

- Stages added without updating `PROPAGATION_PATTERNS` slip silently;
  CEO hooks (`global-ceo-session-start.sh`) print propagation health on
  session start as a forcing function.
- `applies_to: False` exemptions must be explicit; an unlisted project
  defaults to True, surfacing the drift loudly.
