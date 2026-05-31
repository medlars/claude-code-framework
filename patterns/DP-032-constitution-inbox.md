---
id: DP-032
name: Constitution inbox capture pipeline
category: workflow
status: active
constitution-rules: []
youtube-difficulty: intermediate
youtube-episode-length: medium
introduced: 2026-05
---

## What it is

When the user says "always do X" or "from now on, never Y", a hook
(`capture-instruction.sh` UserPromptSubmit) captures the directive as a
JSON file in `~/Projects/Constitution/inbox/`. The Constitution CLI
later promotes valid captures to active rules via human triage.

## Rationale — Why We Adopted This Pattern

*The story of how this pattern came to exist and why it was chosen over alternatives.*

### The problem we kept hitting
A new rule appeared mid-session ("always do X"). Editing CLAUDE.md
mid-session destroys the cache. Adding to memory makes it advisory only.
Adding to Constitution requires a multi-step CLI call. Friction = the
rule never gets recorded.

### What we tried first (and why it didn't work)
- **Edit CLAUDE.md** — cache destruction, lost context.
- **Memory only** — advisory.
- **Direct constitution add-rule** — too many keystrokes mid-task.

### The insight that unlocked the solution
**One-shot inbox capture.** A JSON file dropped in
`Constitution/inbox/*.json` is picked up by a poller and becomes a
*proposed* Constitution rule. No cache disruption, no manual CLI. Human
triages later via `constitution promote`.

### Why this approach, not the obvious one
*Why not auto-promote?* Because some "rules" surfaced mid-session are
context-specific and shouldn't apply fleet-wide. Human review is the
firewall.

### Evidence that it works
- Inbox queue typically has 5-20 pending rules; promotion rate ~60%
  (the other 40% are situational).

## Why we use it

Spoken rules drift. The user says "always lowercase project names" once,
the model forgets by next session, the user repeats it, the cycle
continues. The inbox captures the rule the first time and surfaces it
for promotion so it survives across sessions.

## How it works

**Capture trigger** (`capture-instruction.sh` UserPromptSubmit):
- Pattern matches: "always X", "never Y", "from now on", "going forward",
  "rule:", "convention:", etc.
- Writes `inbox/2026-MM-DD-HHMMSS-{slug}.json`:
  ```json
  {
    "ts": "2026-05-31T16:00:00Z",
    "session_id": "...",
    "raw_prompt": "Always lowercase canonical project names in CIS",
    "extracted_directive": "lowercase canonical project names in CIS"
  }
  ```

**Triage flow:**
1. `constitution inbox-clean` archives stale items.
2. `constitution add-instruction --from-inbox <file>` promotes to a
   proposed instruction in the ledger.
3. `constitution promote <id>` activates it (human required).
4. Active rule is wired to a hook or check pattern.

**Stop-time reminder** (`save-session-reminder.sh`): at session end,
prompts the user to triage inbox if anything was captured.

## Example

Mid-session, user says:
> "From now on, never edit CLAUDE.md mid-session — destroys cache."

Hook captures:
```json
{
  "ts": "2026-05-31T16:00:00Z",
  "extracted_directive": "Never edit CLAUDE.md mid-session — destroys cache"
}
```

Later triage:
```bash
constitution add-instruction --from-inbox 2026-05-31-160000-no-mid-session-claude-md.json \
  --type "behavioral_rule" --category "caching"
constitution promote CON-200
# Auto-wires: PostToolUse hook on Edit/Write of CLAUDE.md → warn
```

Now persistent and enforced.

## Related patterns

- [DP-002] Constitution as SSoT
- [DP-013] Hook-as-judiciary (capture is itself a hook)
- [DP-031] Session save (related lifecycle moment)

## YouTube episode angle

- **Tech-savvy** (10-min): "Every spoken rule becomes a tracked rule."
  Show the inbox file, the triage CLI, the hook auto-wiring. Discuss
  why spoken-only rules die.
- **Lay audience** (5-min): "Suggestion box for the AI." Every "by
  the way, do this from now on" gets dropped in the box and reviewed
  weekly.

## Known failure modes / lessons learned

- LESSONS 066: Inbox captures contain user's verbatim text — secret
  scanners flag 'CHANGEME' in user prompts. Detectors must exclude
  inbox paths.
- LESSONS 031: Inbox capture P0 false positive — same exclusion needed
  fleet-wide for any scanner that walks the repo.
