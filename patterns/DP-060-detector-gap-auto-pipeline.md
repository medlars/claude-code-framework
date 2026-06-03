---
id: DP-060
name: Detector-gap auto-pipeline (error → spec → detector → prevention)
category: detection
status: active
constitution-rules: []
youtube-difficulty: intermediate
youtube-episode-length: medium
introduced: 2026-06
---

## What it is

Every time a new error or bug class is observed at runtime, the **detector-gap
auto-pipeline** automatically classifies it, routes it to the most appropriate
WatchTool, generates an Opus-authored spec and Sonnet-authored implementation
for a new detector, smoke-tests it, wires it into `find_findings()`, and
graduates the lesson to `LESSONS.md` — all without human intervention. The
pipeline runs as a background daemon triggered by PostToolUse and Stop hooks.

This pattern is the *automated counterpart* to DP-005 (WatchTools
detector-gap). DP-005 describes the philosophy ("every bug becomes a
detector"); DP-060 describes the autonomous machinery that executes that
philosophy without requiring the developer to manually write a detector each
time.

## Rationale — Why We Adopted This Pattern

### The problem we kept hitting

DP-005 established the right philosophy — every new bug class should produce
a detector. But in practice, the human (and Claude Code as coordinator) would
fix the immediate bug, move on, and the "add a detector for this" step would
either be deferred, forgotten, or require a separate session to execute.
The LESSONS.md was growing with entries marked `[DETECTOR-GAP]` that were
never acted on.

### What we tried first (and why it didn't work)

- **Manual detector authoring per session** — slow, context-dependent, required
  the developer to remember DP-005 at the right moment.
- **TODO.md entries for detector work** — silently aged; TODO items for
  WatchTool additions competed with feature work and lost every time.
- **Lessons injection hooks** — surfaced the gap to Claude Code, but Claude
  Code had to decide to act; a busy session would skip it.

### The insight that unlocked the solution

**The moment of error capture is also the moment of maximum signal.** When a
PostToolUse hook fires on a non-zero exit, Python traceback, or PM stage
FAIL, all the context needed to classify the error and spec a detector is
already present in the hook payload. The window to capture and queue the
error is <5 seconds. If queued immediately, the pipeline can process it
asynchronously at session end (Stop hook), when Claude Code is not in the
critical path.

### Why this approach, not the obvious one

*Why not just run the detector generator synchronously?* Generating a
spec with Opus + implementing with Sonnet takes 30–90 seconds. A synchronous
hook would block every Bash tool call on any error signal. Queueing to a
JSONL file and flushing at Stop keeps the PostToolUse hook under 5s while
guaranteeing nothing leaks.

### Evidence that it works

- Built and validated 2026-06-03 in a single session: hooks written, queue
  flushed correctly, routing TOML wired, Opus spec + Sonnet code path
  confirmed.
- The pipeline handles the 5 most common error signal types automatically:
  non-zero exit, Python traceback, `pytest FAILED`, PM stage `FAIL`, and
  hypothesis-prompted gaps.
- Previously, detector gaps accumulated in `LESSONS.md` for days or weeks.
  With this pipeline, they are processed within the same session they are
  observed.

## Why we use it

A bug fixed once teaches one project. A bug encoded as a detector teaches
the fleet, forever (DP-005). This pipeline makes DP-005 *happen automatically*:
the observation of an error at the hook layer triggers the full
detector-authoring and wiring pipeline without any manual intervention.
The developer's only job is to review the generated detector before it ships.

## How it works

**Pipeline stages:**

| Stage | Trigger | File | Timing |
|-------|---------|------|--------|
| 1. Capture | PostToolUse on Bash non-zero exit / traceback / PM FAIL | `detector-gap-post-tool.sh` | <5s, async |
| 2. Queue | Append JSONL entry with error excerpt + project + tool | `logs/detector-gaps.jsonl` | instant |
| 3. Hypothesis gate | UserPromptSubmit — Claude diagnoses a bug → queue entry | `detector-gap-from-hypothesis.sh` | on hypothesis write |
| 4. Flush | Stop hook — process all unprocessed entries | `detector-gap-stop.sh` | session end |
| 5. Classify + route | Opus reads error excerpt → selects target WatchTool or "new" | `scripts/detector-gap.py --process-all` | background |
| 6. Spec | Opus writes structured detector spec in `docs/detector-specs/` | `detector-gap.py` | async |
| 7. Implement | Sonnet generates Python detector from spec | `detector-gap.py` | async |
| 8. Smoke test | Compile check + fixture run | `detector-gap.py` | async |
| 9. Wire | Append call to target WatchTool's `find_findings()` | `detector-gap.py` | async |
| 10. Graduate | Append lesson to `LESSONS.md` with detector context | `detector-gap.py` | async |

**Key files:**

```
~/Projects/WatchTools/
  scripts/
    detector-gap.py          # Main pipeline orchestrator
    detector_gap_helpers.py  # Shared helpers (slug, commit, routing, etc.)
  logs/
    detector-gaps.jsonl      # JSONL queue (append-only; processed flag updated in place)
    detector-gap.log         # Execution log
  docs/
    detector-specs/          # Opus-authored specs (one .md per queued entry)
  detector-routing.toml      # Maps error patterns to target WatchTool

~/.claude/hooks/
  detector-gap-post-tool.sh       # PostToolUse capture hook
  detector-gap-stop.sh            # Stop flush hook
  detector-gap-from-hypothesis.sh # UserPromptSubmit hypothesis capture
  detector-gap-user-prompt.sh     # UserPromptSubmit user-described error capture
  detector-gap-response.sh        # PostToolUse on Claude response (assistant turn)
```

**Queue entry schema:**

```json
{
  "id": "<uuid>",
  "ts": "2026-06-03T...",
  "source": "post_tool_bash_nonzero",
  "tool": "CodeWatch",
  "error_excerpt": "<first 500 chars of error>",
  "project": "verscout",
  "processed": false
}
```

**Routing logic:** `detector-routing.toml` maps error signal categories
(import errors, type errors, test failures, PM stage failures, secret
leaks, etc.) to target WatchTools. When no existing tool matches, the
pipeline creates a new WatchTool scaffold via `project-forge` patterns.

**Model assignment:**
- **Opus 4.7** — spec authoring (requires deep reasoning about error
  patterns and detection strategy)
- **Sonnet 4.6** — code implementation from spec (fast, reliable tool use)

## Example

A PM stage run produces:

```
[FAIL] stage_lint: ruff found E501 line-too-long in 3 files
```

1. `detector-gap-post-tool.sh` fires → captures excerpt → appends to `detector-gaps.jsonl`.
2. Session ends → `detector-gap-stop.sh` calls `detector-gap.py --process-all`.
3. Opus classifies: "lint rule non-compliance" → routes to `CodeWatch`.
4. Opus writes spec: "detect files where lines exceed 120 chars without a `# noqa` exemption".
5. Sonnet implements the scope as a new `CodeWatch` scope: `CW-LINT-003`.
6. Smoke test passes.
7. `find_findings()` in CodeWatch updated with new scope call.
8. Lesson appended: "E501 line length is now auto-detected fleet-wide via CW-LINT-003."

## Related patterns

- [DP-005] WatchTools detector-gap philosophy (the principle this pipeline automates)
- [DP-007] CIS as durable finding record (where wired detectors write findings)
- [DP-013] Hook-as-judiciary (capture and flush happen at hook layer)
- [DP-040] Lessons-as-injected-context (graduate step appends to LESSONS.md)
- [DP-056] Lesson promotion pipeline (graduated lessons become hooks/rules)

## YouTube episode angle

- **Tech-savvy** (15-min): Walk the pipeline live — trigger an error in a
  demo project, watch the PostToolUse hook queue it, watch the Stop hook
  flush it, show the Opus spec file, the Sonnet implementation, and the
  wired `find_findings()` call. Highlight: no human wrote a single line of
  the detector.
- **Lay audience** (6-min): "A factory that inspects itself." Analogy: a
  car factory where every defect that reaches the end of the line
  automatically installs a new quality-control camera at the point where
  the defect occurred. The camera is running before the next shift starts.

## Known failure modes / lessons learned

- PostToolUse hooks must complete in <5s; Opus calls cannot run synchronously.
  Always queue → flush at Stop. (Lesson: async is not optional for LLM-backed hooks.)
- The JSONL queue is append-only; mark `processed: true` by appending a new
  record with the same `id` and `processed: true` rather than editing lines
  in place. JSONL is a write-once format.
- `detector-routing.toml` must be kept current as new WatchTools are added;
  otherwise Opus will route to "new tool" when an existing tool could handle it.
- Smoke tests must use real fixture files, not mocks (AP-005). A detector
  that passes a mocked smoke test may fail on real code.
