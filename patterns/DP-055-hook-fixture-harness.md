---
id: DP-055
name: Hook Fixture Harness with Post-Write Validation
category: enforcement
status: active
constitution-rules: []
youtube-difficulty: intermediate
youtube-episode-length: medium
introduced: 2026-06
---

## Problem

Hooks are production infrastructure that runs on every prompt, but they are edited like throwaway scripts — no tests, no staging, no validation until the broken version is already live. The 2026-06-03 lockout happened because `capture-instruction.sh` was edited and immediately active with no validation step between "write" and "run on next prompt."

A `bash -n` syntax check (DP-054's PreToolUse gate) catches parse errors but not behavioral regressions — a hook that parses fine but silently exits 1 instead of 0 on every prompt is equally damaging and harder to detect.

## Solution

Build a fixture harness for every safety-critical hook and run it automatically after any hook file is written.

### Structure

```
~/.claude/hooks/tests/
  run-tests.sh                        # main runner — 83 tests, ~30s
  <hook-name>/
    valid-input.json                  # payload that should exit 0, no advisory
    trigger-input.json                # payload that exercises the hook's purpose
    expected-valid.json               # {"exit_code": 0}
    expected-trigger.json             # {"exit_code": 0, "stdout_contains": "KEYWORD"}
  _stubs/                             # lightweight env stubs (PM scripts, pyproject.toml, etc.)
~/.claude/hooks/safety-critical-hook-edit-gate-fixtures/
  valid-write.json, sc-hook-valid.json, sc-hook-broken.json, expected-*.json
```

### Trigger

`hook-test-on-hook-write.sh` — PostToolUse Write+Edit:
1. Reads the tool payload to extract `file_path`.
2. If the file is not a `.sh` inside `~/.claude/hooks/` → exits instantly (zero overhead on all other writes).
3. If it is a hook file → runs `run-tests.sh` against the live fleet.
4. Silent on green. Emits `additionalContext` with summary and FAIL lines on any failure.

### Coverage (2026-06-03)

- 27 every-prompt safety-critical hooks covered (UserPromptSubmit + Stop + SessionStart).
- `cis-p0-gate.sh` excluded — has its own pre-existing test suite.
- 83 total assertions: 27 bash-n checks + 26×2 behavioral + 4 gate-hook fixtures.

## Key design decisions

**Silent on pass** — green runs produce no output. Noise from always-passing suites trains the engineer to ignore them.

**Advisory on fail, never block** — the PostToolUse hook cannot undo a write. Emitting a clear failure message is more useful than a silent block that still leaves the broken file on disk.

**Targeted wrapper, not global runner** — running 83 tests on every Python/Swift/JS write would add 60s overhead to every edit. The wrapper checks `file_path` first and exits in milliseconds for non-hook files.

**Sandbox HOME in test runner** — tests set `HOME` to a sandbox path to prevent Constitution inbox contamination and side effects. `PHASE2_REAL_HOME` is captured at runner start before any sandbox override.

## Related artifacts

- `~/.claude/hooks/tests/run-tests.sh`
- `~/.claude/hooks/hook-test-on-hook-write.sh` — the PostToolUse trigger
- `~/.claude/hooks/safety-critical-hook-edit-gate.sh` — complementary PreToolUse syntax gate (DP-054)
- `~/.claude/disable-hook.sh` — emergency kill switch if the harness itself breaks

## Rationale — Why We Adopted This Pattern

The 2026-06-03 lockout was caused by a hook that passed `bash -n` (the grammar is valid) but crashed at runtime due to bash interpreting backticks as command substitution inside a double-quoted python3 -c block. A behavioral fixture that pipes a real payload through the hook would have caught this immediately. The pattern closes the gap between "syntactically valid" and "behaviorally correct."

## YouTube episode angle

**Tech-savvy**: Building a fixture harness for shell hooks — payload-driven tests, sandbox HOME, targeted PostToolUse triggering, silent-on-green discipline.

**Lay audience**: How do you test the code that checks your code? And how do you make sure testing it doesn't slow everything down?
