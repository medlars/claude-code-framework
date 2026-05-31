---
id: DP-023
name: WatchTools manifest.toml per tool
category: data-management
status: active
constitution-rules: []
youtube-difficulty: advanced
youtube-episode-length: medium
introduced: 2026-05
---

## What it is

Each WatchTool ships a `manifest.toml` declaring its rule IDs, severity
levels, applicable file types, and suppression policy. The shared
infrastructure (`shared/finding.py`, `shared/cis_client.py`,
`shared/state_manager.py`) reads manifests to dispatch findings
consistently.

## Rationale — Why We Adopted This Pattern

*The story of how this pattern came to exist and why it was chosen over alternatives.*

### The problem we kept hitting
Each WatchTool had different config conventions: some used Python
constants, some used JSON files, some had no config at all (hardcoded).
Adding a new project to a detector required N file edits across N
detectors.

### What we tried first (and why it didn't work)
- **Free-form configs** — divergence; new projects opted out by accident.
- **One global config file** — bloated, no per-tool ownership.

### The insight that unlocked the solution
**Each WatchTool owns a `manifest.toml`.** It declares the tool's name,
rule IDs, applicable file globs, project allowlist/blocklist, severity
defaults, and detector entrypoint. The shared driver reads the manifest
and runs the tool uniformly.

### Why this approach, not the obvious one
*Why not YAML?* TOML is simpler for flat key-value configs and less
indentation-sensitive — fewer accidental bugs.

### Evidence that it works
- 69 WatchTools, all with the same manifest schema; new tools added
  in <30 minutes (template + manifest + detector code).

## Why we use it

A WatchTool without a manifest is opaque: callers don't know which rules
it owns, what files it applies to, or how to suppress false positives.
The manifest is the public contract.

## How it works

**Manifest schema:**
```toml
[tool]
name = "phiwatch"
description = "PHIPA compliance scanner"
version = "1.0.0"

[[rules]]
id = "PHI-BND-001"
title = "PHI must not cross trust boundary"
severity = "P0"
applies_to = ["*.py"]
suppressible = true

[[rules]]
id = "PHI-LOG-001"
title = "PHI must not appear in logs"
severity = "P0"
applies_to = ["*.py", "*.swift"]
suppressible = false  # never allowed
```

**Discoverability:**
- `WatchTools/CLAUDE.md` aggregates all manifest summaries
- `shared/cis_client.py` validates rule_id against manifest before write
- New tool authors declare manifest first, write detectors second

**Suppression policy:**
- Per-rule `suppressible: true` allows inline `# noqa: PHI-LOG-001`
  with owner + expiry
- `suppressible: false` rules cannot be suppressed (e.g. PHI logging)
- All suppressions tracked in `WatchTools/shared/suppressions.json`

## Example

Adding a new detector to PHIWatch:

```toml
# Add to phiwatch/manifest.toml
[[rules]]
id = "PHI-TMP-001"
title = "PHI must not be written to /tmp"
severity = "P0"
applies_to = ["*.py"]
suppressible = false
```

Now `shared/cis_client.add(rule_id="PHI-TMP-001", ...)` succeeds; any
other rule_id is rejected at write time, preventing typos.

## Related patterns

- [DP-005] Detector-gap pattern
- [DP-007] CIS (manifest enforces rule_id validity)
- [DP-024] CapabilityWatch registry

## YouTube episode angle

- **Tech-savvy** (10-min): "Every detector is a public API." Walk
  through PHIWatch's manifest. Show suppression policy. Demonstrate the
  type-check at CIS write rejecting invalid rule_id.
- **Lay audience** (5-min): "Inspectors with badges." Each inspector
  carries a badge listing what they're allowed to check.

## Known failure modes / lessons learned

- LESSONS 066: GapWatch placeholder_detector flagged 'CHANGEME' in
  Constitution/inbox/*.json (user prompts containing the word, not
  code). Manifest `applies_to` should exclude inbox paths.
- LESSONS 068: Secret scanners must exclude binary files; manifest
  `applies_to` patterns must be restrictive enough.
