---
id: DP-015
name: TDD cycle gate (fail→edit→pass ordering enforced)
category: enforcement
status: active
constitution-rules: []
youtube-difficulty: advanced
youtube-episode-length: medium
introduced: 2026-05
---

## What it is

Two paired hooks (`cis-tdd-cycle-gate.sh` UserPromptSubmit and
`cis-tdd-cycle-verify.sh` Stop) that enforce a real red→green TDD cycle
when fixing a bug:
1. **First** a failing test must be observed.
2. **Then** the production code is edited.
3. **Finally** the test passes.

The hooks track evidence (`track-edit-and-evidence.sh` PostToolUse) of
each phase. Without all three in order, Stop is blocked.

## Rationale — Why We Adopted This Pattern

*The story of how this pattern came to exist and why it was chosen over alternatives.*

### The problem we kept hitting
"TDD" in name only. Engineers (human or AI) would write the fix first,
then write a test that happened to pass. The test demonstrated nothing
about the bug — it only demonstrated the fix's current behavior. Six
weeks later a refactor broke the fix and the test still passed because
it was tightly coupled to the implementation.

### What we tried first (and why it didn't work)
- **Honor-system TDD** — never works at scale.
- **Pre-commit hook requiring a new test** — caught new tests but not the
  ordering (test was written *after* fix).

### The insight that unlocked the solution
**Enforce the cycle ordering, not just the artifacts.** The TDD cycle
gate records each test execution: was there a failing test for this
function before the edit? Was there a passing test for the same function
after the edit? If yes → yes, the cycle held. If no → no.

### Why this approach, not the obvious one
*Why not just inspect git history?* Because git captures commits, not
test runs. The same commit can hide a "wrote test, then fix, then
re-wrote test to match" sequence.

### Evidence that it works
- LESSONS 073/074: TDD cycle gate false-positives debugged twice; the
  fact that it had to be debugged proves it was firing on real cases.

## Why we use it

Without TDD enforcement, fixes ship with no proof they address the bug.
"Tests pass" is meaningless if the test was written after the fix and
trivially asserts the new behavior. The cycle gate makes the failing
test the contract — the fix is judged against a pre-stated criterion.

## How it works

**Phase tracking** (`track-edit-and-evidence.sh`):
- After any test run, parse output for `FAILED|PASSED` and write to
  `/tmp/.claude_tdd_evidence_$SESSION_ID`.
- After any code edit, record the file + timestamp.

**Verification** (`cis-tdd-cycle-verify.sh` on Stop):
1. Was a TEST_FAILED event recorded?
2. Was a code edit recorded AFTER the failure?
3. Was a TEST_PASSED event recorded AFTER the edit?
4. If any answer is no → block Stop, prompt for the missing phase.

**Bypass mechanism**: `/tmp/.claude_tdd_bypass_SESSION` (rare; for
sessions doing pure refactor with no behavioral change).

## Example

Session goal: fix `parse_date` returning None for ISO strings.

Bad flow (blocked):
```
edit parse_date.py   # add isinstance check
run pytest           # passes
attempt Stop         # BLOCKED: no TEST_FAILED evidence recorded
```

Good flow:
```
run pytest tests/test_parse_date.py  # 0 tests for ISO case
write test_parse_iso_string          # NEW test
run pytest                            # FAILED — recorded
edit parse_date.py                    # add isinstance(str) check
run pytest                            # PASSED — recorded
Stop OK
```

## Related patterns

- [DP-013] Hook-as-judiciary
- [DP-014] Hypothesis gate (also blocks Stop)
- [DP-019] Test-alongside discipline (related but broader)
- [DP-016] Immaculate code protocol

## YouTube episode angle

- **Tech-savvy** (10-min): "TDD enforced by the shell." Show the hooks
  blocking Stop, the bypass mechanism, and the evidence file. Discuss
  why "I'll add tests after" never happens without enforcement.
- **Lay audience** (5-min): "Prove the test sees the bug first." Use the
  analogy of a medical lab: you draw blood BEFORE administering treatment
  so you can prove it worked.

## Known failure modes / lessons learned

- LESSONS 025: TDD cycle gate matched only pytest pass/fail patterns;
  PM grade output containing `Grade [BCDF]` triggered false TEST_FAILED.
  Fixed by tightening the regex.
- LESSONS 040/055: TDD cycle gate wrote TEST_FAILED sentinel from PM
  output, not actual pytest — caused false starts.
- LESSONS 041/056: Bypass file is per-session, not global — a stale
  bypass from a previous session shouldn't apply.
- LESSONS 073/074: "Grade [BCDF]" pattern in TEST_FAILED_SENTINEL is a
  Part-2 false positive; need explicit failure marker like `FAILED `
  with trailing space.
