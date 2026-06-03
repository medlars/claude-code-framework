---
id: DP-059
name: Untested Hook Scripts Without Automated Validation
category: anti-pattern
status: proposed
constitution-rules: [CON-106]
youtube-difficulty: intermediate
youtube-episode-length: short
introduced: 2026-06
---

## What it is

A development practice where hook scripts — shell scripts wired into an agent or tool lifecycle — are written and deployed without any automated test execution, fixture runners, or behavioral validation. Scripts are treated as write-and-forget artifacts: once authored, they are assumed correct until a visible failure occurs in production. No post-write validation step exists, no mock stdin fixtures are exercised, and no structural smoke tests confirm that field extraction, conditional branching, or output wiring behave as intended.

## Rationale

### The problem

Hook scripts occupy a deceptively fragile position in a system. They run on the edge of the primary execution environment — reading from stdin, extracting fields from structured payloads, writing to files or pipes — and a single logic error can silently corrupt state, drop data, or crash the host process entirely. Unlike application code, hooks often lack visibility: they do not surface warnings, they do not throw exceptions into observable logs, and they accumulate debt across many independent authoring sessions with no shared review cycle.

The failure mode is not gradual degradation. It is sudden, total, and opaque. A hook that fails to read stdin correctly will consume the input stream, leaving the host process starved. A hook that extracts the wrong JSON field will silently discard every event it touches. A hook that writes to a missing path will crash with an exit code the parent process may interpret as a fatal signal. Because these errors are silent during development, confidence in the hook grows over time even as the defect deepens.

### The insight

Hooks are software. They require the same validation discipline as any other software boundary in the system. The small surface area and shell-script medium create an illusion of simplicity that suppresses the instinct to test. That illusion is the anti-pattern. A 30-line shell script that reads from stdin and writes JSON fields is fully testable with a fixture file, a pipe, and an assertion on output or side effect. The absence of that test is not a time-saving shortcut — it is deferred breakage with compounding interest.

Automated validation does not require a complex framework. It requires intentionality: a decision, made at hook-creation time, that the script will be exercised against a known input before it is deployed and after every significant change.

### Evidence

On 2026-06-03, `capture-instruction.sh` — a hook wired into the Claude Code session lifecycle — contained a defect in its stdin reading logic that had accumulated silently across multiple authoring sessions. The defect was never caught because no fixture runner existed and no post-write validation was performed. When the hook executed in a safety-critical path, it bricked the entire Claude Code session, requiring full recovery. The defect was not novel or subtle; it was the class of error that a single pipe-test against a mock payload would have caught at authoring time.

## Why we use it

This anti-pattern is documented to make the failure mode explicit and named. Without a named pattern, the behavior recurs naturally: hooks feel simple, testing feels over-engineered for shell scripts, and the cost is invisible until it is total. By naming the anti-pattern, teams can identify when they are drifting into it, reference a concrete failure history, and apply the corresponding remediation pattern (see Related Patterns) before accumulating silent defects.

## How it works

The anti-pattern establishes itself through a sequence of low-resistance decisions:

1. A hook script is written quickly to solve an immediate need.
2. Manual inspection substitutes for execution against a real or mock payload.
3. No fixture file is created. No test invocation is scripted. No CI step validates the hook.
4. The hook is deployed and appears to work because the happy path is exercised incidentally.
5. A second, third, and fourth hook are written under the same assumptions, establishing the pattern as the team norm.
6. A change to payload structure, a new edge case in stdin buffering, or a missing dependency silently invalidates a hook.
7. The defect accumulates across sessions, invisible, until a critical execution path triggers it.
8. Failure is total and the root cause is opaque because no test artifact exists to isolate the defect.

The reinforcing mechanism is that hooks which do not immediately fail build false confidence. Each successful incidental execution is misread as validation. The longer the hook runs without a visible failure, the less likely a test is ever written for it.

## Example

A hook script `capture-instruction.sh` is written to read a JSON payload from stdin, extract the `instruction` field, and append it to a log file.

```sh
#!/usr/bin/env bash
input=$(cat)
instruction=$(echo "$input" | jq -r '.instruction')
echo "$instruction" >> ~/.claude/instructions.log
```

This script is visually plausible. It is deployed without a test. Three sessions later, the upstream payload structure changes: the field is now nested at `.event.instruction`. The extraction silently returns `null` for every subsequent invocation. The log fills with null entries. No alarm fires. Six sessions later, a related hook depends on the log being populated and crashes when it encounters malformed data. The crash surfaces in a completely different context, making the root cause non-obvious.

A fixture-based test written at authoring time would have looked like:

```sh
echo '{"instruction": "test payload"}' | bash capture-instruction.sh
assert_file_contains ~/.claude/instructions.log "test payload"
```

A change to the payload structure would have broken this test immediately, surfacing the defect in the authoring session rather than six sessions later in a crash.

## Related patterns

- **DP-058 Hook Script Fixture Validation** — The remediation pattern. Establishes a required fixture runner, post-write validation step, and behavioral pipe-test contract for all hook scripts at creation time.
- **DP-031 Silent Failure Accumulation** — The broader anti-pattern class of which this is a specific instance: defects that produce no observable signal during development and compound across sessions.
- **DP-044 Write-and-Forget Infrastructure** — Operational infrastructure authored without ownership, monitoring, or validation lifecycle, leading to entropy accumulation in supporting systems.

## Known failure modes

**Stdin consumption without validation.** A hook that calls `cat` or reads from stdin without asserting on the result consumes the stream. If the read logic is incorrect, the host process receives an empty or malformed buffer with no error surfaced.

**Silent null extraction.** Shell scripts using `jq` or `awk` for field extraction return empty strings or literal `null` on missing fields rather than non-zero exit codes. Scripts that do not assert on extraction results will process null values silently and indefinitely.

**Exit code misinterpretation.** Some hook host environments treat any non-zero exit from a hook as a fatal signal. A hook that exits non-zero due to a missing file or failed command can terminate the parent process in ways that appear unrelated to the hook itself.

**Cross-session confidence drift.** The longer a defective hook runs without triggering its failure condition, the lower the perceived priority of adding tests. This creates an inverse relationship between hook age and test likelihood — the oldest, most trusted hooks are often the least validated.

**Payload schema drift.** Hook scripts are typically not updated when upstream payload schemas change because no contract exists to enforce the relationship. Fixture tests with versioned payloads are the only mechanism that makes schema drift immediately visible.