---
id: DP-035
name: Anti-patterns library (AP-001…AP-014)
category: anti-pattern
status: active
constitution-rules: []
youtube-difficulty: beginner
youtube-episode-length: long
introduced: 2026-04
---

## What it is

`~/Projects/shared/anti-patterns.md` — an append-only library of named
failure modes that have hit the fleet. Each entry: AP-NNN, first seen,
symptom, root cause, fix, tags. The `/anti-patterns` skill surfaces the
library; `anti-pattern-gate.sh` PreToolUse hook checks Bash commands
against known patterns.

## Rationale — Why We Adopted This Pattern

*The story of how this pattern came to exist and why it was chosen over alternatives.*

### The problem we kept hitting
The same wrong approach kept being attempted across projects: `cp -R`
to replace a running .app, `localStorage` in WKWebView, `sfltool
resetbtm` to "fix" duplicate login items. Each one cost hours; each one
had been done before; each had no durable warning.

### What we tried first (and why it didn't work)
- **Memory entries** — advisory only; rationalized past.
- **Project-specific mistakes.md files** — siloed; another project hit
  the same wall not knowing.

### The insight that unlocked the solution
**One fleet-wide, append-only anti-pattern library indexed by symptom.**
AP-001 through AP-014 (and growing). Each entry: first seen, symptom,
root cause, fix, tags. Hooks reference AP numbers when blocking.

### Why this approach, not the obvious one
*Why not just write tests that catch each anti-pattern?* Some are not
testable in code (e.g., AP-003 `sfltool resetbtm` is a shell command, not
a code path). Anti-patterns are *prose* documentation; hooks and
detectors are their *enforcement*.

### Evidence that it works
- AP-013 (inline `stage_cis_health`) was caught and fixed in 3 projects
  in one session because the library entry made the pattern obvious.
- New AP entries flow from real incidents within 24h.

## Why we use it

Distinguishes from sibling artifacts:
- **Memory** (per-session, per-feedback)
- **ADRs** (per-architecture-decision, per-project)
- **Anti-patterns** — *cross-project failure modes*, growing over time

The library prevents fleet-wide repeats of mistakes that happened once.

## How it works

**Entry format:**
```markdown
## AP-NNN: {symptom in one phrase}

**First seen**: YYYY-MM-DD · {project} · {brief incident}
**Symptom**: What you observe
**Root cause**: Why it happens
**Fix**: How to prevent + how to recover
**Tags**: {tag1, tag2}
```

**Numbering**: sequential, never re-used. Superseded entries link the
new one (`**Supersedes**: AP-NNN`).

**Enforcement** for each AP that has a detectable pattern:
- AP-001 → `block-app-deploy-while-running.sh`
- AP-002 → `ap002-webview-guard.sh`
- AP-003 → blacklisted in destructive-action gate
- AP-005 → tests that mock the DB raise CIS warning
- AP-009 → Codex output-watcher hook
- AP-013 → SilentFailureWatch detector
- AP-014 → killall-9-python warning hook

## Current library (14 entries)

| ID | Title (summarized) |
|----|-------|
| AP-001 | macOS `cp -R` silently fails to replace running .app |
| AP-002 | WKWebView browser-JS storage evaporates on page load |
| AP-003 | `sfltool resetbtm` wipes ALL system login items |
| AP-004 | `sudo rm` on icon caches corrupts RunningBoard |
| AP-005 | Mock-database tests pass while prod migration breaks |
| AP-006 | Audio dedup at 0.85 threshold over-merges similar tracks |
| AP-007 | yt-dlp archive accumulates phantom entries |
| AP-008 | Stale CLOUDSDK_PYTHON after Python uninstall |
| AP-009 | Codex bails silently on `~/.claude/CLAUDE.md` edits |
| AP-010 | `find -maxdepth 3` misses files at depth 4 |
| AP-011 | Cloudflare DNS via browser session cookies (token stale) |
| AP-012 | Documentation.AI single-site vs multi-site topology |
| AP-013 | Inlining `stage_cis_health` instead of delegating |
| AP-014 | `killall -9 python3.14` kills the Codex worker itself |

## Example

AP-001 was added after Verscout v2.x deploy failed silently:
```bash
cp -R dist/App.app /Applications/App.app  # returns 0, but old binary still running
stat /Applications/Verscout.app/Contents/MacOS/Verscout  # OLD timestamp
```

Fix becomes a documented sequence (pkill → sleep → rm → cp → verify
stat timestamp → restart) and is encoded into `scripts/rebuild-app.sh`
per project plus the `block-app-deploy-while-running.sh` hook.

## Related patterns

- [DP-005] Detector-gap pattern (APs often become detectors)
- [DP-013] Hook-as-judiciary (APs need hook enforcement to bind)

## YouTube episode angle

- **Tech-savvy** (20-min): "14 mistakes I will never make again." Walk
  through each AP with the originating incident. Best episode for a
  "war stories" series.
- **Lay audience** (10-min): "Lessons from a year of building." Tell
  each as a 1-minute story.

## Known failure modes / lessons learned

- Library is append-only; superseded entries link forward, not delete.
- Tags enable cross-cutting search (e.g. all `macos` APs, all
  `silent-failure` APs).
- Some APs are documented but lack a hook — those are the next
  detector-gap items (DP-005).
