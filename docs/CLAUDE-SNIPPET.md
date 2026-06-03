## Claude Code Engineering Framework

This project follows the [Claude Code Engineering Framework](https://github.com/owner/claude-code-framework) — 40 patterns for managing software projects with Claude Code.

@import ~/claude-code-framework/patterns/DP-013-hook-as-judiciary.md (## What it is)
@import ~/claude-code-framework/patterns/DP-016-immaculate-code-protocol.md (## How it works)

### Active patterns in this project

<!-- Fill in the DP-NNN patterns you have adopted. Start with Tier 1: -->

- DP-013: Hook-as-judiciary — memory advisory, hooks enforce
- DP-016: Immaculate code protocol — tests + lint + PM green = done
- DP-018: Spec-driven development — write `spec.md` before coding
- DP-019: Test-alongside discipline — tests land same session as code

<!-- Add Tier 2 / Tier 3 patterns as you adopt them. -->

### Definition of Done

A task is complete when:

- [ ] Tests pass (`pytest` / `swift test` / `jest` — whatever applies)
- [ ] Linter clean (`ruff` / `eslint` / `swiftlint`)
- [ ] PM grade held (if a PM script exists for this project)
- [ ] No new TODOs added without a tracked issue id
- [ ] No new secrets, no hardcoded URLs, no `print()` for logging

### Enforcement

Hooks live in `~/.claude/hooks/`. They are the law (DP-013).

Memory (this file) is advisory — Claude reads it but may drift mid-session. Hooks fire deterministically.

Never bypass a hook without writing the rationale in `logs/policy-changes.md`. If you cannot write one sentence justifying the bypass, do not bypass it.

### Framework reference

- Full pattern index: `~/claude-code-framework/INDEX.md`
- Generate report: `python3 ~/claude-code-framework/generate-report.py --audience tech`
- Single pattern: `python3 ~/claude-code-framework/generate-report.py --pattern DP-NNN`
