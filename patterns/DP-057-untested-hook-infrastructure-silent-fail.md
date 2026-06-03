---
id: DP-057
name: Untested Hook Infrastructure with Silent Logic Degradation
category: quality
status: proposed
constitution-rules: []
youtube-difficulty: intermediate
youtube-episode-length: short
introduced: 2026-06
---

## What it is

A design pattern that mandates automated test execution for all hook scripts at the point of authorship, enforcing fixture runners, post-write validation, and behavioral pipe-tests so that logic bugs in hook infrastructure are caught immediately rather than allowed to accumulate silently across sessions.

## Rationale

### The problem

Hook scripts occupy an unusual position in a system: they are invoked automatically by infrastructure, often in response to side-effects, and their failure modes are frequently invisible. A hook that reads the wrong field from a JSON payload, fails to wire an output correctly, or misreads stdin will typically exit zero and produce no visible error. The system continues. The hook is simply inert — or worse, partially effective in ways that are hard to distinguish from correct behavior.

This invisibility makes hooks uniquely vulnerable to write-and-forget authorship. A developer writes a hook, observes no immediate crash, and moves on. Over multiple sessions, across multiple contributors, small logic bugs accumulate. Each one is individually undetectable. Collectively, they constitute silent degradation of the hook layer.

The failure mode eventually triggered on 2026-06-03, when `capture-instruction.sh` — a safety-critical hook responsible for session capture — contained compounded logic errors that had never been validated under real invocation conditions. When the hook fired in a live Claude Code session, it bricked the session entirely. No warning had been emitted across any prior execution. The bugs had been present, silently, for an indeterminate period.

### The insight

Hooks are code. Code requires tests. The fact that hooks are invoked by infrastructure rather than called directly by application logic does not reduce this requirement — it increases it, because the invocation path itself is harder to inspect. A hook that cannot be exercised in isolation by a fixture runner is a hook that can only be validated by triggering its production side-effect, which is exactly the condition that makes silent degradation possible.

The pattern therefore treats hook authorship as incomplete until three conditions are satisfied: the hook can be invoked by a fixture runner with controlled input, its output can be asserted against known expectations, and a behavioral pipe-test validates that the full stdin-to-effect chain produces the correct result. These are not optional quality additions. They are the definition of "written."

### Evidence

The 2026-06-03 incident provides direct evidence. `capture-instruction.sh` had accumulated at least three distinct logic errors: incorrect field extraction from the hook payload, broken stdin buffering under non-interactive invocation, and a missing output wire that caused the captured instruction to be discarded rather than written. None of these produced a visible error signal in any prior session. All three were detectable by a fixture runner exercising the hook against a synthetic payload. No fixture runner existed.

## Why we use it

Silent logic degradation in hook infrastructure is particularly damaging because the hooks that matter most — those tied to safety, capture, or session integrity — are also the hooks most likely to be invoked infrequently under normal operation, meaning their bugs have the most time to accumulate before they surface. The pattern exists to eliminate the accumulation window entirely by making validation a precondition of authorship rather than a retrospective activity.

It also addresses a secondary failure mode: hooks that were once correct but regressed silently when surrounding infrastructure changed. A fixture runner that is re-executed across sessions provides regression coverage that write-and-forget authorship cannot.

## How it works

**Fixture runner requirement.** Every hook directory contains a `tests/` subdirectory with at least one fixture file per hook. The fixture file provides a synthetic invocation payload — typically a JSON blob or stdin string — that represents a realistic production input. A runner script (`run-hook-tests.sh` or equivalent) invokes each hook with its fixture input and captures stdout, stderr, and exit code.

**Post-write validation gate.** Hook authorship is considered incomplete until the fixture runner executes cleanly against the new hook. In practice this means the runner is invoked as part of the commit hook or authorship checklist. A hook that cannot be exercised by the fixture runner is not merged.

**Behavioral pipe-tests.** Beyond fixture invocation, each hook has at least one pipe-test that validates the full stdin-to-effect chain. For a hook that reads a payload from stdin and writes a file, the pipe-test confirms that the file exists, contains the expected content, and was written to the expected path. For a hook that emits to stdout for downstream consumption, the pipe-test pipes that output into the downstream consumer and asserts on the final state.

**Field extraction assertions.** A specific class of pipe-test targets field extraction, which is the most common source of silent logic errors in hook scripts. The fixture payload contains known field values, and the test asserts that the hook extracted the correct field — not merely that it exited zero.

**Session-spanning re-execution.** Fixture runners are not one-time checks. They are re-executed at the start of each session that touches hook infrastructure, providing regression coverage across the accumulation window that silent degradation exploits.

## Example

A hook `capture-instruction.sh` reads a JSON payload from stdin, extracts the `instruction` field, and writes it to a session log. Without this pattern, the hook is written, observed to exit zero in a manual test, and committed. Bugs in `jq` field extraction or the output path are invisible.

With this pattern, a fixture file `tests/capture-instruction-fixture.json` contains:

```json
{"instruction": "summarize the current task", "session_id": "abc123"}
```

The fixture runner pipes this into the hook and asserts that `session-log.txt` contains the string `summarize the current task`. If the hook extracts the wrong field, writes to the wrong path, or fails to buffer stdin correctly, the assertion fails immediately. The hook is not committed until the assertion passes. When surrounding infrastructure changes the payload schema in a later session, re-running the fixture runner surfaces the regression before the hook fires in production.

## Related patterns

**DP-012 — Commit Gate Enforcement** establishes the broader principle of making quality checks preconditions of authorship rather than retrospective activities. DP-057 applies that principle specifically to hook infrastructure.

**DP-031 — Infrastructure Side-Effect Isolation** addresses the complementary problem of hooks that produce side-effects that are difficult to assert on in test conditions. The fixture runner approach in DP-057 depends on the side-effect isolation techniques in DP-031 to make behavioral pipe-tests tractable.

**DP-044 — Silent Failure Surface Auditing** provides the audit methodology for identifying which parts of a system are capable of silent failure. Hook infrastructure consistently appears as a high-risk surface in DP-044 audits, which is the systemic context from which DP-057 emerged.

## Known failure modes

**Fixture staleness.** Fixture files that are not updated when the hook payload schema changes become false negatives — the runner passes because the fixture exercises the old schema path, but the hook fails in production against the new schema. Mitigated by coupling fixture updates to schema change commits.

**Shallow pipe-tests.** A pipe-test that only asserts exit code rather than output content provides no protection against field extraction errors. The pattern requires content-level assertions, but this requirement is easy to satisfy superficially. Code review of pipe-tests should explicitly check that assertions target content, not just exit status.

**Runner not re-executed.** The session-spanning re-execution requirement is procedural rather than enforced by tooling in most implementations. If re-execution is skipped in a session that modifies hook infrastructure indirectly — for example, by changing a shared library the hook depends on — the regression window reopens. Full enforcement requires the runner to be triggered by any change to files in the hook dependency graph, not only changes to the hook script itself.

**Fixture environment mismatch.** Fixture runners that execute in a different environment than production invocation — different shell version, different PATH, different stdin buffering behavior — can pass while production invocations fail. The 2026-06-03 incident included a stdin buffering bug that was environment-specific. Fixture runners should be validated against the production invocation environment, not assumed to be equivalent.