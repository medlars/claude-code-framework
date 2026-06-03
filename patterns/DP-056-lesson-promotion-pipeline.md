---
id: DP-056
name: Lesson Promotion Pipeline
category: enforcement
status: active
constitution-rules: []
youtube-difficulty: intermediate
youtube-episode-length: medium
introduced: 2026-06
---

## Problem

LESSONS.md was an append-only prose file. When a mistake recurred, a new entry was added rather than the existing entry being escalated into enforcement. By 2026-06-03 the file had 162 entries, at least 7 duplicate clusters (e.g. the backtick-in-python3-c pattern documented in entries 008, 034, 049, and 161), and 14 lessons with no enforcement hook. The lesson existed but could not prevent recurrence because text has no enforcement power.

The symptom: the same lesson recorded four times while the same mistake happened four times.

## Solution

Replace append-only prose with structured YAML records and a promotion lifecycle.

### Record schema

```yaml
id: "008"
date: "2026-05-14"
status: "active"           # active | duplicate-of-NNN | superseded
root_invariant: "Shell scripts must not contain raw backticks inside python3 -c double-quoted strings."
affected_patterns:
  - "*.sh files invoking python3 -c \"...\" with raw backticks"
incident:
  description: "playwright-first-gate.sh: backtick Python regex parsed as command substitution"
  blast_radius: hook-fp
enforcement:
  hook: ~/.claude/hooks/hook-backtick-in-python-c-gate.sh
  regression_test: ~/.claude/hooks/tests/hook-backtick-in-python-c-gate/
recurrences: [034, 049, 161]
verified: 2026-06-03
```

### Lifecycle

```
incident → LESSONS.md entry (prose, status=active)
         → duplicate check: if same invariant exists, status=duplicate-of-NNN
         → enforcement promotion: hook added, record updated with enforcement.hook
         → recurrence tracking: new incident adds to recurrences[] of canonical entry
```

### Files

```
~/Projects/shared/lessons/
  NNN.yaml         # one file per lesson (001.yaml … 162.yaml + AP-*.yaml + B-*.yaml)
  DUPLICATES.md    # clusters of substantively identical entries
  ORPHANS.md       # lessons with hook-enforceable patterns but no hook yet
  INDEX.md         # one-line per active lesson, under 200 lines for @import

~/Projects/shared/
  LESSONS.md                       # generated compatibility shim → @imports lessons/INDEX.md
  LESSONS.md.archive-2026-06-03    # original prose preserved
  LESSONS-INDEX.md                 # 7-line shim → @imports lessons/INDEX.md (CLAUDE.md target)
```

### Dedup result (2026-06-03)

145 total records, 7+ duplicate clusters identified, 14 orphan lessons with no enforcement hook.
The 008/034/049/161 cluster: canonical=008, others status=`duplicate-of-008`.

## Invariant rule

**A duplicate lesson entry is a failure of the enforcement pipeline, not a memory problem.**

When a lesson recurs:
1. Do NOT add a new LESSONS.md entry.
2. Add to `recurrences[]` of the canonical YAML record.
3. If no enforcement hook exists: create one.
4. If a hook exists but the mistake happened anyway: the hook has a coverage gap — fix the hook.

## Related artifacts

- `~/Projects/shared/lessons/` — 145 YAML records
- `~/Projects/shared/lessons/DUPLICATES.md`
- `~/Projects/shared/lessons/ORPHANS.md`
- `~/Projects/shared/build-lessons-index.py` — regenerates INDEX.md and LESSONS-INDEX.md shim
- LESSONS.md 161 — root incident that triggered this overhaul

## Rationale — Why We Adopted This Pattern

Text-only lessons depend on the model retrieving the right rule at the right moment. That is unreliable. Structured records with mandatory `enforcement.hook` fields make the gap between "lesson recorded" and "lesson enforced" visible and actionable. ORPHANS.md is the work queue: every entry there is a known gap waiting for a hook. The lifecycle also eliminates the psychological escape valve of "recording a new lesson" as a substitute for fixing the root cause.

## YouTube episode angle

**Tech-savvy**: Why append-only lessons files don't work — and how structured YAML records with enforcement linkage close the gap between knowing and preventing.

**Lay audience**: The difference between writing down a mistake and actually preventing it from happening again.
