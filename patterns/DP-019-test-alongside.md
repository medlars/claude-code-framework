---
id: DP-019
name: Test-alongside discipline (SE Principle 13)
category: quality
status: active
constitution-rules: []
youtube-difficulty: beginner
youtube-episode-length: short
introduced: 2026-05
---

## What it is

SE Principle 13 (from `~/.claude/CLAUDE.md`):
> "Any new function or module requires a corresponding test file touch
> in the same session. If no test file exists, create one. Claiming
> 'done' without a test file being created or updated is a protocol
> violation. Writing the test after the feature is too late."

Enforced by `last20-and-test-alongside.sh` PostToolUse hook.

## Rationale — Why We Adopted This Pattern

*The story of how this pattern came to exist and why it was chosen over alternatives.*

### The problem we kept hitting
"I'll add tests later" never happens. Features shipped without tests,
edge cases forgotten by the next session, deferred indefinitely. The
test-coverage debt compounded across 81 projects.

### What we tried first (and why it didn't work)
- **End-of-session "add tests" reminder** — model already context-rotted;
  test quality poor.
- **Coverage floor in PM** — caught absence of tests but not absence of
  *meaningful* tests; could be gamed with empty assertions.

### The insight that unlocked the solution
**Force the test file to be touched in the same session as the feature.**
While the implementation details are fresh, the test cost is amortized.
SE Principle 13. Enforced by `last20-and-test-alongside.sh` PostToolUse
hook.

### Why this approach, not the obvious one
*Why not just require coverage targets?* Coverage targets game easily
(stub tests, useless assertions). Test-alongside is harder to game
because the hook checks that the test *file* was modified during the
session, and TestQualityWatch checks the tests have meaningful
assertions.

### Evidence that it works
- Without the hook, test-alongside happened ~60% of the time. With the
  hook, ~95%.
- TestWatch fleet-wide gap reports shrink monotonically since hook
  rollout.

## Why we use it

"I'll add tests later" never happens. By forcing the test file touch in
the same session as the feature, the testing cost is amortized while the
implementation details are fresh. Later, the cost compounds: forgotten
edge cases, lost context, deferred indefinitely.

## How it works

**Hook trigger** (`last20-and-test-alongside.sh` PostToolUse on Write/Edit):
1. Inspect the edit: is it a new function / handler / endpoint / Cloud
   Function?
2. Was a corresponding test file (`tests/test_<module>.py` or sibling
   `*_test.py`) touched in the same session?
3. If no → emit advisory: "test-alongside missing for <function>".

**Stop-level enforcement**: `last20-preflight.sh` (Write PreToolUse)
blocks Write if a handler is missing all 3 NFRs (test, validation,
logging — the "last 20%" of any feature).

**PM stages**: `TestWatch` runs continuous gap analysis, reports
fleet-wide test deficits.

## Example

Add a new endpoint `/api/invoice/process`:

```python
# src/invoice.py
def process_invoice(invoice_id: str) -> dict:
    ...
```

Without test-alongside: ship, "I'll add tests later" → never added.

With test-alongside: same session, write:
```python
# tests/test_invoice.py
def test_process_invoice_happy_path():
    result = process_invoice("INV-001")
    assert result["status"] == "processed"

def test_process_invoice_missing_invoice():
    with pytest.raises(InvoiceNotFound):
        process_invoice("DOESNOTEXIST")
```

Hook sees both files touched in session → quiet. If only `src/invoice.py`
touched → advisory printed.

## Related patterns

- [DP-015] TDD cycle gate (stronger form)
- [DP-016] Immaculate code protocol (pytest is in the DoD)
- [DP-020] Definition of Done

## YouTube episode angle

- **Tech-savvy** (5-min): "Tests in the same session or never." Show
  the hook firing on a session that touched source without test. Show
  the TestWatch report listing fleet-wide test gaps.
- **Lay audience** (3-min): "Build the elevator and the inspection
  certificate in one trip." Otherwise the inspection never happens.

## Known failure modes / lessons learned

- LESSONS 067: TestWatch assigns P0 to PM script boilerplate (`log`,
  `stage_*`) that doesn't need direct tests. Exclusion lists needed.
- LESSONS 070-072: TestQualityWatch TQ-ASS-001 flags try/except:pass
  tests as no-assertion; must exclude `.archive/` and
  `test_zz_*_direct_call.py` patterns.
- LESSONS 013 (test-alongside protocol violation tracking): Without the
  hook, the rule was honored ~60% of the time. With the hook, ~95%.
