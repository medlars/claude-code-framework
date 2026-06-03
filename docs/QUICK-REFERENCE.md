# Quick Reference — Claude Code Engineering Framework

One row per pattern. Use this as a cheat sheet during code review, planning, or onboarding.

Reports: `python3 generate-report.py --pattern DP-NNN` pulls a single pattern in full.

| Pattern | What it does | How to adopt |
|---------|--------------|--------------|
| DP-001 | CEO/PM/CIS 3-tier governance — per-project PM owns build/test/deploy; CEO supervises across projects | Create `scripts/{project}-pm.py` from `shared-libs/pm-base/pm_base.py` |
| DP-002 | Constitution — centralized rule registry, enforcement layer, audit trail | Bootstrap `Constitution/` repo; wire rules to hooks |
| DP-003 | Project registry — single source of truth for the project list | Maintain `~/Projects/shared/pm-registry.json` + `project-registry.md` |
| DP-004 | Skill-driven workflow — every project gets a `/skill` invocation | Create `~/.claude/skills/{project}/SKILL.md` with YAML frontmatter |
| DP-005 | WatchTools detector-gap — automated detectors for fleet-wide drift | Add a scope to GapWatch/CodeWatch/TestWatch/CapabilityWatch |
| DP-006 | 9-dimension audit — cold-read methodology a fresh reviewer would catch | Run `/deep-audit` + project's `/audit` skill in parallel |
| DP-007 | Central Issue Store — single store for all findings fleet-wide | Use `CentralIssueStore.add()`, never raw `INSERT INTO issues` |
| DP-008 | CEO dashboard — cross-project health JSON | `python3.14 ~/Projects/scripts/ceo.py --report` |
| DP-009 | Subagent-driven execution — parallel agents for security/perf/tests/docs | Trigger via `agents-protocol.md` map; never duplicate agents |
| DP-010 | Specialist agent fleet — one agent per domain | Create `~/.claude/agents/{name}.md` with YAML frontmatter + system prompt |
| DP-011 | Auto-agent deployment — agents spawn proactively, not on request | Trigger map in `~/.claude/agents-protocol.md` |
| DP-012 | Background agent reporting — quality checks that don't block | Set `mode: background`; agent stays quiet on clean results |
| DP-013 | Hook-as-judiciary — memory advisory, hooks enforce | Write `~/.claude/hooks/*.sh`; wire in `~/.claude/settings.json` |
| DP-014 | PreToolUse vs PostToolUse — distinct enforcement semantics | PreToolUse blocks writes (exit 2); PostToolUse reports findings |
| DP-015 | Hook output contract — Stop hooks use `systemMessage`, not `hookSpecificOutput` | Return JSON: `{"decision":"block","reason":"…"}` |
| DP-016 | Immaculate code protocol — DoD: ruff + pyright + tests + PM grade held | Add 4-step DoD to project CLAUDE.md; gate at Stop hook |
| DP-017 | PM grade snapshot + regression block | `immaculate-code-protocol-gate.sh` snapshots at usersubmit, blocks at Stop |
| DP-018 | Spec-driven development — write `spec.md` before coding | Use `/spec` skill; sections: Problem, Goals, Design, Test plan, Rollout |
| DP-019 | Test-alongside discipline — tests in same session as code | `last20-and-test-alongside.sh` hook enforces |
| DP-020 | Last-20% completeness — rate-limit + structured logs + input validation | Required on every new endpoint/handler/CF; hook enforces |
| DP-021 | TDD red→green cycle in fix mode | `cis-tdd-cycle-gate.sh` + `cis-tdd-cycle-verify.sh` track sentinels |
| DP-022 | ADR (Architecture Decision Record) — `YYYY-NNN-title.md` per non-trivial choice | Use `/adr` skill; store in `{project}/.decisions/` |
| DP-023 | Contract tests — JSON schemas in `{project}/contracts/` for API changes | Use `/contract-test` skill on every shape change |
| DP-024 | Threat model — before first deploy of PHI/financial/OAuth projects | Use `/threat-model` skill; annual review |
| DP-025 | Dependency SLA — CVE Critical 48h, High 7d, Medium 30d | Quarterly audit via `/dep-policy` skill |
| DP-026 | SLOs — at least one in `{project}/docs/slo.md` before release | Use `/slo` skill; wire to `stage_runtime` |
| DP-027 | Feature flags — risky features get runtime toggle | Remove within 2 sprints of GA; stack-specific storage |
| DP-028 | Dogfood log — daily friction → `~/Projects/shared/dogfood-log.md` | Use `/dogfood` skill; Monday triage to TODO.md |
| DP-029 | Chaos drills — quarterly for FinanceFlow/MoeMoney/EpicVDI/CorpBooks | Use `/chaos` skill; post-incident within 48h |
| DP-030 | Policy-change ledger — never silently lower a floor/baseline | Log to `{project}/logs/policy-changes.md` with rationale |
| DP-031 | Boring technology bias — pick stable over cutting-edge | Plain SQL over ORMs; model training data is deepest on boring tech |
| DP-032 | Triple Review Protocol — Functionality + Contradiction + User's reality | Required for all infra/service/capability claims |
| DP-033 | Add-then-remove migrations — never remove working infra first | Add new → verify serves traffic → remove old |
| DP-034 | Playwright-first — automate browser tasks, don't ask user | Use Playwright MCP or Browserbase; only ask for biometric/2FA |
| DP-035 | Codex delegation for substantive work — 3+ files, 200+ lines | `codex exec "<task>" </dev/null` or `/codex:rescue` skill |
| DP-036 | Familiarity-based delegation — write first draft yourself in familiar domains | AI tools 19% slower on familiar codebases (METR, Jul 2025) |
| DP-037 | Context Rot prevention — proactively prune at ~40 tool calls | Summarize completed work in 2 sentences; drop intermediate outputs |
| DP-038 | WISC context management — Write checkpoint, Isolate files, Select lines, Compress completed work | Apply on long sessions (50+ tool calls) |
| DP-039 | Two-instance pair workflow — Writer + Reviewer, sync via `pair-notes.md` | Use `/pair` skill for refactors >5 files or security-sensitive work |
| DP-040 | Credentials SSoT — `.env.shared` + `sync-credentials.sh --all` | Never edit API keys directly in project `.env`; always sync from SSoT |

---

## Pattern groupings (for quick navigation)

- **Governance (DP-001 → DP-008)** — project structure, registry, CEO/PM, CIS, audits
- **Agents (DP-009 → DP-012)** — subagent fleet, deployment, reporting modes
- **Hooks (DP-013 → DP-015)** — enforcement layer, semantics, output contracts
- **Code quality (DP-016 → DP-021)** — DoD, last-20%, TDD, test-alongside
- **Engineering hygiene (DP-022 → DP-030)** — ADR, contracts, threat model, SLOs, chaos
- **Behavioral (DP-031 → DP-040)** — boring tech, triple review, Playwright-first, Codex delegation, context management, credentials SSoT

## Tiered adoption path

- **Tier 1 (start here)**: DP-013, DP-016, DP-018, DP-019
- **Tier 2 (1-2 days setup)**: DP-001, DP-002, DP-006
- **Tier 3 (fleet management)**: DP-005, DP-007, DP-009

See `GETTING-STARTED.md` for full adoption guidance.
