---
id: DP-054
name: Safety-Critical Hook Classification
category: enforcement
status: active
constitution-rules: []
youtube-difficulty: intermediate
youtube-episode-length: medium
introduced: 2026-06
---

## Problem

211 hooks treated as equals by settings.json. A UserPromptSubmit hook that runs on every prompt and a niche PostToolUse hook have radically different blast radii, but nothing in the wiring reflects this. A syntax error in the former locks the user out immediately.

Root incident: 2026-06-03. `capture-instruction.sh` (UserPromptSubmit, every-prompt) crashed bash on every prompt due to an unescaped backtick inside `python3 -c "..."`. The same pattern had been documented three times in LESSONS.md (entries 008, 034, 049) — text-only lessons did not prevent recurrence.

## Solution

Classify all hooks into four buckets by blast radius. Maintain the classification in `~/.claude/hooks/HOOK-MANIFEST.json`.

| Bucket | Definition |
|---|---|
| `safety-critical` | Runs on every prompt/session/write — syntax error bricks Claude Code |
| `prevents-regression` | Blocks a documented failure class with a known incident |
| `informational` | Advisory only, exit 0 always |
| `obsolete-or-duplicate` | Superseded or never fired |

Manifest result (2026-06-03 fleet of 211 hooks): safety-critical=61, prevents-regression=35, informational=111, obsolete-or-duplicate=4.

## Enforcement

`safety-critical-hook-edit-gate.sh` — PreToolUse Write+Edit:
- Checks HOOK-MANIFEST.json for the target file's bucket.
- If safety-critical: runs `bash -n` on new content before write lands.
- `bash -n` fail → blocks (exit 2). Pass → emits advisory with blast-radius info and kill-switch reminder.

## Related artifacts

- `~/.claude/hooks/HOOK-MANIFEST.json`
- `~/.claude/hooks/safety-critical-hook-edit-gate.sh`
- `~/.claude/disable-hook.sh` — emergency kill switch (DP-055)
- LESSONS.md 161 — root incident

## Rationale — Why We Adopted This Pattern

Without classification, every hook edit carries unknown risk. The manifest makes blast radius explicit and machine-readable so enforcement is targeted: only safety-critical hooks need a fixture harness. This is the same principle as production/staging — identical code treated differently by operational context. Adopted after the fourth recurrence of the same bug because three text-only lessons failed.

## YouTube episode angle

**Tech-savvy**: How a 211-hook fleet classifies its own infrastructure and enforces editing rules — HOOK-MANIFEST.json, PreToolUse gates, blast-radius taxonomy.

**Lay audience**: Why your AI assistant's guardrails need their own guardrails.
