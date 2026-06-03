---
id: DP-016
name: Immaculate code protocol (DoD = ruff+pyright+pytest+PM green)
category: enforcement
status: active
constitution-rules: []
youtube-difficulty: intermediate
youtube-episode-length: medium
introduced: 2026-05
---

## What it is

A protocol declared in `~/.claude/CLAUDE.md` that defines "done" as four
non-negotiable checks on every touched file:

```bash
ruff check <touched files> --select E,F,W   # zero lint errors
pyright <touched files>                       # zero type errors
python3.14 -m pytest tests/ -q --tb=short    # green
python3.14 scripts/{project}-pm.py --quick   # grade >= starting grade
```

Enforced by `immaculate-code-protocol-gate.sh` (UserPromptSubmit
snapshot + Stop verification).

## Rationale — Why We Adopted This Pattern

*The story of how this pattern came to exist and why it was chosen over alternatives.*

### The problem we kept hitting
"Done" meant whatever the engineer wanted it to mean. Sometimes "tests
pass". Sometimes "compiles". Sometimes "deployed". Cross-project
"done" was incomparable — FinanceFlow's "done" was MoeMoney's "barely
started".

### What we tried first (and why it didn't work)
- **Per-project DoD documents** — drifted, ignored.
- **A checklist in CLAUDE.md** — read once at session start, forgotten by
  the time the change shipped.

### The insight that unlocked the solution
**Done = four gates: ruff clean + pyright clean + pytest green + PM
grade ≥ starting grade.** Four binary checks, automatable, no judgement
required. The protocol gate hook snapshots the starting grade and blocks
Stop on regression.

### Why this approach, not the obvious one
*Why not include more gates (security scan, perf bench, coverage)?* Those
*are* included — they're inside the PM grade. The four gates are the
*minimum*. Projects add stricter gates inside PM stages.

### Evidence that it works
- `immaculate-code-protocol-gate.sh` blocks Stop on grade regression
  hundreds of times per week across the fleet.
- DoD-aligned PRs merge faster because reviewers know exactly what to
  check.

## Why we use it

"Tests pass" is too soft a definition. Lint warnings rot; type drift
hides bugs; the PM grade captures the integrated quality of all stages.
The protocol promotes the integrated grade to the bar.

## How it works

**Pre-code gate (UserPromptSubmit):**
1. Read project CLAUDE.md (SSoT for rules).
2. Snapshot PM grade from `logs/pm-last-status.json`.
3. Remind the model of DoD checklist.

**Stop gate:**
1. Re-snapshot PM grade.
2. Compare to baseline.
3. If grade regressed → block Stop, surface the regression.
4. If grade improved → record in `logs/pm-grade-history.jsonl`.

**Per-edit gates:**
- `pyright-per-edit.sh` — type errors per file
- `post-edit-verify.sh` — ruff on save
- `bare-except-detector.sh`, `float-money-detector.sh`,
  `n-plus-one-query-detector.sh`, etc. — pattern checks

**Code shape rules** (from CLAUDE.md):
- Three similar lines beats a premature abstraction
- Comments explain WHY only
- No backwards-compat hacks (no `_var` renames, no re-exports)
- Error handling only at real system boundaries

## Example

Session goal: add a Cloud Function for invoice processing.

Without protocol: tests pass, ship. Three weeks later: lint warnings
accumulate, types drift, PM grade slides B → D unnoticed.

With protocol:
```
[edit src/invoice.py]
[edit tests/test_invoice.py]
ruff check src/invoice.py tests/test_invoice.py   # 0 errors
pyright src/invoice.py tests/test_invoice.py      # 0 errors
pytest tests/test_invoice.py -q                    # 4 passed
python3.14 scripts/financeflow-pm.py --quick      # grade A (was A)
→ Stop OK
```

If pyright finds an issue: Stop is blocked until it's fixed. The PM grade
acts as the integrated quality check that catches what individual lints
miss.

## Related patterns

- [DP-003] PM script contract
- [DP-015] TDD cycle gate
- [DP-019] Test-alongside
- [DP-020] Definition of Done

## YouTube episode angle

- **Tech-savvy** (12-min): "Why 'tests pass' isn't enough." Walk through
  the four gates. Show the PM grade history file. Demonstrate Stop
  being blocked by regression.
- **Lay audience** (5-min): "Four-point inspection before shipping."
  Like a pre-flight checklist for pilots — every item every time.

## Known failure modes / lessons learned

- Snapshot is from `logs/pm-last-status.json`; if PM hasn't run recently,
  baseline is stale. UserPromptSubmit hook re-snapshots fresh.
- LESSONS 003: `sys.path.insert` files need `# noqa: E402` on every
  import below the insert, not just the first.
- LESSONS 023: pyright flags `_alias` imports as "not accessed" even
  when used; drop leading underscore on intentional aliases.
