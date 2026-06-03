---
id: DP-003
name: PM script contract (14-part structure)
category: governance
status: active
constitution-rules: []
youtube-difficulty: advanced
youtube-episode-length: long
introduced: 2026-04
---

## What it is

Every project has a PM script at `{project}/scripts/{project}-pm.py`
(FinanceFlow's lives at `automation/comprehensive_pm_monitor.py`) that
follows a 14-part contract. The script is the project's contract with the
rest of the fleet: it speaks a common grammar so the CEO can compose all
PMs into one dashboard.

## Rationale — Why We Adopted This Pattern

*The story of how this pattern came to exist and why it was chosen over alternatives.*

### The problem we kept hitting
When the fleet had 8 projects, each PM was hand-rolled. Some had
`--quick`, some had `--all`, some had no modes at all. Adding a new stage
(say, `stage_codewatch`) meant editing 8 files differently. Stages were
named differently in each project, so the CEO couldn't aggregate them.

### What we tried first (and why it didn't work)
- **Free-form PMs** — no contract; CEO aggregation was impossible.
- **A base class with inheritance** — Python's MRO complications killed
  composability when stages needed to be conditionally enabled per project.
- **A YAML config + generic runner** — couldn't express the rich
  project-specific stage logic (Apps Script timeouts, GAS quotas).

### The insight that unlocked the solution
**Define the contract, not the implementation.** Every PM exposes the same
3 invocation modes (`--touched | --quick | --full`), the same stage names
(`stage_build`, `stage_test`, `stage_lint`, …), the same output schema
(`logs/pm-last-status.json`), and the same publish call
(`publish_and_persist()`). What happens *inside* a stage is project-specific.

### Why this approach, not the obvious one
*Why not a fully-shared framework like pytest plugins?* Because PMs run
heterogeneous workloads (Python pytest, Swift `xcodebuild test`, GAS
`clasp push`, Astro builds, Cloud Function deploys). A pytest plugin
can't run `clasp`. The contract gives uniformity *across* stacks without
forcing one stack on everyone.

### Evidence that it works
- 27 PM scripts across 27 projects, all answer the same 5 questions
  (build / test / lint / security / grade).
- CEO can run all 81 PMs in parallel because every output is the same
  shape.
- New projects bootstrap with `project-forge`, which generates a
  contract-compliant PM in seconds.

## Why we use it

A fleet of 81 projects with 81 different test runners is unmanageable. The
PM contract turns every project into a black box with the same five inputs
and the same five outputs. New projects bootstrap from a template; new
patterns added to one PM propagate to all via `PROPAGATION_PATTERNS`.

## How it works

**The 14 parts:**
1. **Constants block**: `PROJECT_NAME`, `ROOT`, `PYTHON`, `PM_LOG`.
2. **Stage functions**: each prefixed `stage_` — build / test / lint /
   security / codewatch / cis_health / watchtools / runtime / contract_test
   / mutation / chaos / ux / propagation. Returns `StageResult`.
3. **Touched mode**: `--touched` runs only stages affected by recent edits.
4. **Quick mode**: `--quick` runs the standard pipeline (~4–7 min).
5. **Full mode**: `--full` runs everything including slow stages (~7–15 min).
6. **Query mode**: `query risk --file X`, `query coverage --file X`,
   `query why-failed --stage Y` — synchronous answers without running stages.
7. **TODO management**: reads/writes `{project}/TODO.md` with SLA tracking.
8. **Baselines**: `pm-baselines.json` for performance/coverage thresholds.
9. **Diagnostics**: writes `logs/pm-diagnostics.json` after every run.
10. **Status persistence**: writes `logs/pm-last-status.json` (machine state).
11. **Audit log**: appends to `logs/pm.log`.
12. **Session journal**: writes to `logs/pm-session.jsonl`.
13. **Dashboard publish**: calls `publish_and_persist()` →
    `~/Projects/ceo-dashboard.json`.
14. **Grade computation**: A/B/C/D/F based on stage results, written to
    status JSON.

**Inheritance:** all PMs inherit from `shared-libs/pm-base/pm_base.py`. Per-
project PM only overrides the stages it actually runs. Shared impls
(`stage_cis_health_impl`, `stage_codewatch_impl`, etc.) live in
`shared-libs/pm-base/pm_base_pm_stages.py` so a bug fix is fleet-wide.

## Example

A minimal stage looks like:

```python
def stage_test(self) -> StageResult:
    result = self._run_subprocess(
        [self.PYTHON, "-m", "pytest", "tests/", "-q"],
        timeout=300,
    )
    return StageResult(
        name="test",
        passed=result.returncode == 0,
        score=1.0 if result.returncode == 0 else 0.0,
        details=result.stdout[-2000:],
    )
```

Then `--touched` knows: edited `*.py` under `src/` → run `stage_test` +
`stage_lint`. Edited `cloud-functions/*.py` → also run `stage_security`.

## Related patterns

- [DP-001] CEO/PM/CIS hierarchy
- [DP-004] CEO propagation rule
- [DP-016] Immaculate code protocol (DoD checks)
- [DP-019] Test-alongside discipline
- [DP-026] Shared-libs pattern (where stage impls live)

## YouTube episode angle

- **Tech-savvy** (15-min): Code-walk a real PM script. Highlight the
  StageResult dataclass, the shared-libs delegation, the touched-mode
  filter. Compare to Jenkinsfile / GitHub Actions YAML — same shape, but
  runs locally on every edit.
- **Lay audience** (8-min): "Every project has a robot tester." Show the
  PM running tests in 5 seconds after an edit. Show the dashboard turning
  red when one stage fails.

## Known failure modes / lessons learned

- AP-013: Inlining `stage_cis_health` instead of delegating diverges from
  canonical impl and hides bugs.
- LESSONS 022: A `except Exception` in a stage that swallows the bug
  reports "passed" while actually skipping the check — SilentFailureWatch
  (DP-008) was built to detect this.
- LESSONS 071: Test fixtures for stages must mirror the production schema
  (issues + issue_events tables) or shared impls raise during tests.
