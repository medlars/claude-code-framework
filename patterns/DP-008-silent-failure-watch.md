---
id: DP-008
name: SilentFailureWatch (exception-swallowing detector)
category: detection
status: active
constitution-rules: [SFW-001, SFW-002, SFW-003]
youtube-difficulty: intermediate
youtube-episode-length: short
introduced: 2026-05
---

## What it is

A specialized WatchTool that detects the most insidious anti-pattern in
the fleet: **a stage that swallows its exception and reports success**.
After the AP-013 incident (Verscout's `stage_cis_health` silently
skipping because of a missing import), this detector was generalized
fleet-wide.

## Rationale — Why We Adopted This Pattern

*The story of how this pattern came to exist and why it was chosen over alternatives.*

### The problem we kept hitting
The most expensive bugs in the fleet were silent failures: a `try / except
Exception: pass` that swallowed a real error, a stage that "passed"
because its broad exception handler returned True on KeyError. The
pipeline was green; production was on fire.

### What we tried first (and why it didn't work)
- **Linters that flag bare `except:`** — caught the *bare* form, missed
  `except Exception: pass` and `except Exception as e: logger.debug(e)`.
- **Code review** — silent failures look fine in a diff.
- **Pyright** — type-correct silence is still silence.

### The insight that unlocked the solution
**Exception-swallowing is a pattern, not a symptom.** Three rule IDs
(SFW-001 bare except, SFW-002 swallowed Exception, SFW-003 logger.debug
on a caught Exception) catch ~95% of the silent-failure surface.

### Why this approach, not the obvious one
*Why not just require specific exception types?* Because legitimate
catch-all blocks exist (top-level main loops, defensive cleanup). The
detector exempts those via a comment marker (`# pragma: silent-ok`) so
intentional silence is documented but unintentional silence is loud.

### Evidence that it works
- AP-013 surfaced because SilentFailureWatch flagged the inline
  `stage_cis_health` `except Exception` that hid a `NameError`.
- 12 distinct silent-failure bugs across 7 projects caught in the first
  month after rollout.

## Why we use it

Bare `except Exception: pass` makes tests green when they should be red.
A broken stage that reports "passed" is worse than one that crashes —
it actively hides the problem. SilentFailureWatch makes the pattern a
P0 CIS issue.

## How it works

**SFW-001** — A function with `try:` followed by `except:` or
`except Exception:` with no re-raise, no specific exception type, and no
log/warn/escalate call. Pattern match:

```python
try:
    ...
except Exception:        # ← flagged
    pass                  # or `return None`, or `return True`
```

**SFW-002** — A `stage_*` function returning a truthy result inside an
`except` block (the success path being the failure path).

**SFW-003** — A subprocess call without `check=True`, no return-code
inspection, and a default-True assumption.

**How it's enforced:**
- CodeWatch + GapWatch run the detector on every Python file
- `bare-except-detector.sh` PostToolUse hook fires on every edit
- PM `stage_codewatch` and `stage_watchtools` surface findings via CIS

## Example

The bug that birthed this detector (Verscout 2026-05-29):

```python
def stage_cis_health(self) -> StageResult:
    try:
        conn = sqlite3.connect(CIS_DB)  # NameError: sqlite3 not imported
        open_p0 = conn.execute("SELECT COUNT(*) FROM issues WHERE ...").fetchone()
        return StageResult(passed=open_p0 == 0)
    except Exception:                    # ← swallowed NameError
        return StageResult(passed=True)  # ← always-pass on error
```

The stage reported PASS for weeks while never actually checking CIS. Fix:

```python
def stage_cis_health(self) -> StageResult:
    from pm_base_pm_stages import stage_cis_health_impl
    return stage_cis_health_impl(project_name=self.PROJECT_NAME)
```

## Related patterns

- [DP-003] PM script contract (stages with broad except poison the contract)
- [DP-005] Detector-gap pattern (AP-013 → SilentFailureWatch)
- [DP-007] CIS (where findings land)
- [DP-013] Hook-as-judiciary (per-edit detection)

## YouTube episode angle

- **Tech-savvy** (8-min): "The bug that always says it passed." Show the
  Verscout incident. Demonstrate the detector flagging similar patterns
  fleet-wide. Discuss why `except Exception: pass` is rarely the right
  call.
- **Lay audience** (4-min): "Why your tests lie to you." Use the analogy
  of a fire alarm that beeps "all clear" when its battery dies. The
  worst kind of error is the one that pretends to succeed.

## Known failure modes / lessons learned

- AP-013 (the origin incident)
- Pattern is per-stage, but the principle applies to any boundary —
  network calls, file reads, IPC. CodeQualityWatch CQ-EXC-001/002
  generalize beyond stages.
