---
id: DP-058
name: Edit-region-scoped advisory detectors (signal over file-wide noise)
category: skills-agents-hooks
status: active
constitution-rules: [CON-105]
youtube-difficulty: intermediate
youtube-episode-length: medium
introduced: 2026-06
---

## What it is

A PostToolUse advisory detector (bare-except, SQL-injection, async-misuse, etc.)
that re-reads the whole edited file reports **every** pre-existing violation in that
file on **every** edit — including violations the current change never touched. A
one-line edit to a 600-line file produces a wall of warnings about debt the author
did not introduce and is not addressing right now.

The pattern: compute the line range the edit actually changed (from the tool call's
`new_string`/`edits` payload), and filter findings to that range plus a few lines of
context. Findings outside the changed region are suppressed. When the range cannot be
determined (a full-file `Write`, or an `Edit` whose `new_string` cannot be located),
the detector **fails open** and scans the whole file — it never suppresses silently.

Shared helper: `~/.claude/hooks/lib/changed_region.py` (stdin JSON → `"START END"`
1-based inclusive, or empty for scan-all). Each detector passes the region as argv to
its embedded analysis script and drops findings whose `line N:` falls outside it.

## Rationale — Why We Adopted This Pattern

### The problem we kept hitting
A fleet of 220 hooks fired on every edit. Removing a single unused `import` from a
PM script triggered five `except Exception` warnings on lines the edit never touched,
plus dead-code, complexity, and test-alongside notices for the whole file. The
operator (human and model alike) learned to ignore hook output entirely — the
"boy who cried wolf" effect. Correct individual checks summed to useless noise, and
the enforcement layer *felt* futile despite each hook working as designed.

### What we tried first (and why it didn't work)
- **Raising severity thresholds** — hid real findings along with the noise.
- **Capping output to N findings** — still surfaced N *irrelevant* findings first.
- **Disabling the noisy detectors** — threw away genuine signal; not allowed when
  hooks are the only enforcement lever.

### The insight that unlocked the solution
The detectors were answering the wrong question. "What is wrong with this file?" is a
project-wide audit question (PM/WatchTools own it). The PostToolUse question is "what
did *this edit* introduce?" Scoping findings to the changed region realigns the
detector with the event that triggered it.

### Why this approach, not the obvious one
*Why not just track which lines changed across the whole session?* Because the hook
runs per-edit in a fresh process with no session memory; the tool-call payload it
already receives is sufficient to localize the edit. *Why fail open instead of closed?*
Because a localizer bug must never hide a real security finding — an over-report is
recoverable noise, a silent miss is a shipped vulnerability.

## How to apply

Two shared helpers live in `~/.claude/hooks/lib/` (each with a test file in
`lib/tests/`): `changed_region.py` (stdin JSON → `"START END"` or empty) and
`filter_to_region.py` (post-filters a detector's emitted JSON to the region).

**Approach A — post-filter wrapper (preferred; one-line change).** Pipe the detector's
final JSON emit through the filter. No change to the detector's internals:

    HD="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    python3.14 "$TMPPY" "$FILE_PATH" 2>/dev/null | python3.14 "$HD/lib/filter_to_region.py" "$INPUT"

**Approach B — inline filter (when the detector needs the region internally).** Compute
`REGION` after `INPUT=$(cat)`, pass it as argv, and filter findings by their `line N:`
prefix inside the analysis. Used where output shape varies (e.g. `bare-except-detector`,
`sql-injection-detector`, `async-misuse-check`).

Rules for both:
- Keep the detector advisory (`exit 0`); scoping changes *what* is reported, never
  *whether* it can block.
- Fail open: unknown region (full-file `Write`, un-locatable `new_string`) → scan all.
- Skip detectors that are already diff-aware (compare `git show HEAD:` old-vs-new, e.g.
  `arity-drift-check`, `docstring-rot-detector`) — they are change-scoped by construction.

As of 2026-06, ~17 full-scanning advisory detectors are scoped this way; the 3 already
change-aware are deliberately left alone.

## Scope and limits

- Applies to **advisory** PostToolUse detectors only. Hard blockers (secrets,
  destructive commands) scan the literal `new_string`/`command` and need no region.
- Full-file `Write` cannot be narrowed — scan-all is the correct, deliberate behavior.
- Security detectors still scope to the region: a pre-existing injection far from the
  edit is the PM/audit's backlog, not this edit's regression. The author sees it when
  they touch that code.

## Related

- [[DP-013-hook-as-judiciary]] — hooks are law; this keeps the law's signal credible.
- [[DP-008-silent-failure-watch]] — the detectors this scopes are silent-failure hunters.
- [[DP-055-hook-fixture-harness]] — region-scoping must ship with a fixture test
  (`lib/tests/test_changed_region.py`) per the hook-testing pattern.
- [[DP-054-safety-critical-hook-classification]] — only non-safety-critical advisory
  hooks are scoped; safety blockers are exempt.
