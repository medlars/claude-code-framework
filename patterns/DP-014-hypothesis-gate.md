---
id: DP-014
name: Hypothesis gate (root-cause record before stopping)
category: enforcement
status: active
constitution-rules: []
youtube-difficulty: advanced
youtube-episode-length: medium
introduced: 2026-05
---

## What it is

A Stop-event hook (`cis-hypothesis-gate.sh`) that blocks turn end if the
session edited code claiming to fix a CIS issue but didn't record a
hypothesis explaining the root cause. The companion hook
`cis-require-root-cause.sh` enforces the same for new CIS issues.

## Rationale — Why We Adopted This Pattern

*The story of how this pattern came to exist and why it was chosen over alternatives.*

### The problem we kept hitting
"Fixed it!" with no explanation. Tests went green; nobody could explain
*why*. A week later the bug came back because the "fix" was a
coincidence — random retry happened to mask the underlying race.

### What we tried first (and why it didn't work)
- **Asking the model to explain after** — explanations were post-hoc
  rationalizations, not actual root-cause analysis.
- **Requiring commit messages to include "why"** — written too late, after
  the model had moved on.

### The insight that unlocked the solution
**Force the hypothesis to be written BEFORE Stop.** A hook intercepts the
Stop event, checks for a hypothesis record (a file or CIS event), and
blocks the turn from ending if none exists. The model writes the
hypothesis *while the context is still warm*.

### Why this approach, not the obvious one
*Why not just trust the model's good intentions?* Because the model
optimizes for "task complete", not "task understood". A Stop-level hook
makes "task understood" a hard precondition for "task complete".

### Evidence that it works
- LESSONS 012 (B-012): "Write hypothesis before fixing" is now a fleet
  protocol; bugs that previously came back twice rarely come back once
  after a hypothesis-gated fix.

## Why we use it

Symptoms get patched; root causes get missed. A fix that works "for some
reason" tends to break the same way later because nobody understood why.
Forcing a written hypothesis before turn-end makes the author commit to
a causal story; if the story is wrong, the next regression makes that
obvious.

LESSONS B-011/B-012:
> "TDD cycle for all fixes. Write hypothesis before fixing. Write
> acceptance criterion before first edit."

## How it works

**Stop hook logic:**
1. Inspect recent edits — did the session touch files referenced by an
   open CIS issue?
2. If yes, check `Constitution/inbox/*.json` and CIS `issue_events`
   table for a `hypothesis` entry matching the issue ID.
3. If absent, return `systemMessage` blocking Stop with:
   ```
   You edited code linked to CIS-XYZ but didn't record a root-cause
   hypothesis. Add via:
     python3.14 ~/Projects/shared/cis-view.py log-hypothesis CIS-XYZ "<one-line cause>"
   ```

**Companion hooks:**
- `cis-log-fix-attempt.sh` (PostToolUse) — automatically logs the fix
  attempt with the file path; the human still owes the hypothesis.
- `cis-require-regression-test.sh` (Stop) — also blocks if the fix
  lacks an accompanying test that would have caught the bug.

## Example

Open CIS issue: `CIS-25761 — GapWatch flagged 'CHANGEME' in
Constitution/inbox/*.json`.

Bad: edit `gapwatch/src/placeholder_detector.py` to skip those files,
exit. → Hypothesis gate blocks Stop:
> "You touched a file linked to CIS-25761 but no hypothesis logged."

Good:
```bash
python3.14 ~/Projects/shared/cis-view.py log-hypothesis CIS-25761 \
  "Inbox captures are by design verbatim user prompts; CHANGEME is part
   of the user's text, not real code. Detector should exclude inbox paths."
```

Now Stop is allowed. The hypothesis becomes part of the issue's audit
trail — a future regression will be diagnosed against it.

## Related patterns

- [DP-007] CIS as durable finding record
- [DP-013] Hook-as-judiciary (hypothesis gate is a Stop hook)
- [DP-015] TDD cycle gate (similar enforcement style)
- [DP-038] Triple Review Protocol

## YouTube episode angle

- **Tech-savvy** (12-min): "Why every fix needs a why." Show a session
  blocked by the hypothesis gate. Walk through what the gate inspects.
  Compare to "post-mortem after the fact" — too late, by then the
  context is lost.
- **Lay audience** (5-min): "Don't fix, diagnose." Use the medical
  analogy: a doctor doesn't just give aspirin without naming the
  condition.

## Known failure modes / lessons learned

- Hypothesis text quality matters; "fixed it" is not a hypothesis. The
  hook accepts any non-empty string but the human reviewer rejects
  vacuous ones during weekly triage.
- The gate only fires for files linked to open CIS issues; unrelated
  edits don't trigger it.
