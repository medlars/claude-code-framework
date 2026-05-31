# Claude Code Engineering Framework

> A comprehensive system of design patterns, workflows, and governance mechanisms
> for managing large-scale software projects with Claude Code.
>
> Built and refined over 12+ months across 80+ projects. Freely available for
> anyone who wants to adopt these techniques.

## What This Is

A production-tested registry of 40 engineering design patterns covering
governance, detection, execution, enforcement, quality, security, workflow,
and anti-patterns — all built on top of Claude Code.

The patterns emerged from running 80+ software projects in parallel with a
single AI assistant. They solve the hard problem: how do you turn a chat
interface into an industrial-grade software delivery system?

## Quick Start

```bash
git clone https://github.com/[your-username]/claude-code-framework
cd claude-code-framework
python3 generate-report.py --audience tech   # Full technical guide
python3 generate-report.py --audience lay    # Plain-English overview
python3 generate-report.py --youtube         # 40 episode seeds
```

## License

MIT License — use freely, attribution appreciated.

---

> Sister files: `INDEX.md` (machine-readable), `patterns/DP-NNN-*.md` (one file per pattern),
> `TEMPLATE.md` (copy-this for new patterns), `generate-report.py` (narrative renderer).

---

## Registering New Patterns

> **Every time a new engineering design is invented — during a coding session,
> audit, or retrospective — it MUST be registered here. This is non-negotiable.**
> The registry only works if it is complete. A pattern that lives in one
> engineer's head is a pattern that will be re-invented (badly) by the next
> session.

### Trigger conditions (register when you)

- Invent a new workflow that solves a recurring problem.
- Discover an anti-pattern through a production incident or audit finding.
- Create a new hook, skill, or agent that embodies a novel approach.
- Adopt a new discipline (TDD gate, hypothesis writing, Triple Review, …).
- Make an architectural decision that other sessions should follow.
- Notice yourself doing something for the third time — that's a pattern.

### How to register a new pattern

1. **Pick the next DP-NNN number** from `INDEX.md`:

   ```bash
   tail -10 ~/Projects/shared/design-patterns/INDEX.md
   ```

2. **Copy the template:**

   ```bash
   cp ~/Projects/shared/design-patterns/TEMPLATE.md \
      ~/Projects/shared/design-patterns/patterns/DP-NNN-kebab-case-name.md
   ```

3. **Fill in every section.** Frontmatter is mandatory. The
   `Rationale — Why We Adopted This Pattern` section is mandatory.

4. **Add an INDEX.md entry** under `patterns:` matching the frontmatter:

   ```yaml
   - id: DP-NNN
     name: ...
     category: ...
     status: proposed         # promote to active once validated 2+ uses
     constitution_rules: []
     youtube_difficulty: ...
     youtube_length: ...
     introduced: 2026-MM
     file: patterns/DP-NNN-slug.md
     related: [DP-XXX, ...]
   ```

5. **Add a one-line catalog row** to the table below.

6. **Add a YouTube episode seed** to
   `categories/12-youtube-episodes/episode-seeds.md` — even a one-liner.

7. **If the pattern has an enforcement mechanism, register it in Constitution:**

   ```bash
   echo "y" | python3.14 ~/Projects/Constitution/constitution.py add-rule \
     --type specification \
     --title "DP-NNN: <pattern name>" \
     --description "<one-line>" \
     --check-pattern "NONE" \
     --enforcement "documentation" \
     --category "meta"
   ```

8. **If the pattern surfaces a NEW anti-pattern,** append `AP-NNN` to
   `~/Projects/shared/anti-patterns.md`.

9. **If a future Claude Code session might re-invent it,** write a hook in
   `~/.claude/hooks/` that surfaces this pattern when the trigger condition
   is detected.

### Categories for new patterns

| Slug | Scope |
|------|-------|
| `governance` | CEO/PM/CIS hierarchy, Constitution, project contracts |
| `detection` | WatchTools, cold-read audits, CIS, exception scanners |
| `execution` | Subagents, parallelism, Codex routing, specialist agents |
| `enforcement` | Hooks, TDD gates, hypothesis gates, immaculate code protocol |
| `quality` | Cold-read audits, spec-driven dev, test-alongside, DoD, Triple Review |
| `data-management` | SSoT files (.env.shared, pm-registry.json), manifests, registries |
| `project-structure` | Project floor, shared-libs, policy-change ledger |
| `security` | PHI boundaries, Keychain, add-then-remove migrations |
| `workflow` | /save, WISC, boring tech bias, plan/programmer personas |
| `anti-pattern` | Append-only library of cross-project failure modes |
| `meta` | The registry itself, YouTube derivation |
| `skills-agents-hooks` | Reusable Claude Code primitives |

### Pattern lifecycle

- **proposed** — Invented but not yet validated across multiple sessions.
  Live in the registry but flagged as not-yet-canonical.
- **active** — Validated by use in 2+ sessions, ideally backed by a hook,
  a Constitution rule, or a CI check.
- **deprecated** — Superseded by a better approach. Kept for historical
  record; frontmatter `status: deprecated` plus a `supersedes:` line in the
  body pointing to the replacement DP-NNN.

### Pattern template (canonical)

Copy `TEMPLATE.md` — it has the full skeleton (frontmatter + 8 required
sections + Rationale) with instructional comments for each field.

---

## Executive Summary (tech-savvy)

This codebase is governed by a layered control system, not by discipline alone.
Every project is owned by a **PM script** (`scripts/{project}-pm.py`) that
runs the build/test/lint/security/coverage/contract/SLO pipeline locally and
publishes a grade to a fleet dashboard. A **CEO script**
(`~/Projects/scripts/ceo.py`) supervises all PMs in parallel and propagates
constructive patterns across them so the fleet does not drift. A **Central
Issue Store** (CIS, SQLite at `~/Projects/.uis/issues.db`) is the durable
record of every finding from 69 automated detectors (the **WatchTools**
monorepo: AuthWatch, CodeWatch, GapWatch, PHIWatch, SilentFailureWatch, …).
A **Constitution** (`~/Projects/Constitution/`) is the rule registry: 555
rules versioned in a SQLite ledger, each backed by a hook in `~/.claude/hooks/`
(180 hooks active) so behavioral rules are enforced at the shell layer, not
inside the model's reasoning loop. **Skills** (155) and **agents** (24)
package reusable workflows and specialist personas; agent dispatch is
deterministic via trigger maps (e.g. "edited 3+ Python files" → spawn
`security-auditor` in background). **Codex** is the substantive-work backend
when Anthropic limits bind; Claude Code remains the coordinator. The result
is a fleet where the human owner never types code but can ship across nine
products in parallel with deterministic quality floors.

## Executive Summary (lay audience)

Think of this as a software factory run by one person with a robot
assistant. The owner is a physician — he never writes code. Instead, he
directs an AI assistant (Claude Code) through plain English. Over a year, he
built the equivalent of a small engineering company's process manual:
- Every project has a tireless **project manager** that runs every test, lint, and
  security check before shipping.
- A **CEO** sits on top and makes sure every project obeys the same rules.
- 69 **inspectors** watch the codebase for known mistakes (secrets in code,
  missing tests, fake placeholders, etc.) and write findings to a central
  ledger.
- 555 written **rules** are mechanically enforced by 180 shell hooks — so the
  AI literally cannot break a rule, even if it wanted to.
- 155 reusable **playbooks** and 24 specialist **personas** mean the AI
  always picks the right tool for the job.

The point is not the AI's intelligence — it is the **scaffolding around the
AI** that turns a chat tool into an industrial-grade software fleet.

---

## How to use this registry

| If you want to… | Open… |
|----------------|-------|
| Get a 1-page overview | This file (README.md) |
| Find a pattern by ID | `INDEX.md` |
| Read about one pattern in depth | `patterns/DP-NNN-*.md` |
| Browse patterns by theme | `categories/{01..12}/` |
| Generate a YouTube episode | `categories/12-youtube-episodes/episode-seeds.md` |
| Render a narrative report | `python3.14 generate-report.py --full` |
| Add a new pattern | "Registering New Patterns" section above |
| Use the blank template | `TEMPLATE.md` |

---

## Pattern catalog (quick reference)

| ID | Name | Category | Difficulty |
|----|------|----------|------------|
| DP-001 | CEO/PM/CIS three-tier supervision hierarchy | governance | intermediate |
| DP-002 | Constitution as SSoT for all rules | governance | intermediate |
| DP-003 | PM script contract (14-part structure) | governance | advanced |
| DP-004 | CEO propagation rule (cross-PM consistency) | governance | advanced |
| DP-005 | WatchTools detector-gap pattern (bug → detector → prevention) | detection | intermediate |
| DP-006 | 9-dimension cold-read audit methodology | detection | advanced |
| DP-007 | CIS (Central Issue Store) as durable finding record | detection | intermediate |
| DP-008 | SilentFailureWatch pattern (exception-swallowing detection) | detection | intermediate |
| DP-009 | Subagent-driven execution (standing preference) | execution | beginner |
| DP-010 | Parallel agent dispatch pattern | execution | intermediate |
| DP-011 | Codex routing (substantive work → Codex, coordination → Claude) | execution | beginner |
| DP-012 | Specialist agent matching (domain-aware dispatch) | execution | intermediate |
| DP-013 | Hook-as-judiciary (memory is advisory, hooks are law) | enforcement | intermediate |
| DP-014 | Hypothesis gate (root-cause record before stopping) | enforcement | advanced |
| DP-015 | TDD cycle gate (fail→edit→pass ordering enforced) | enforcement | advanced |
| DP-016 | Immaculate code protocol (ruff+pyright+pytest+PM green = done) | enforcement | intermediate |
| DP-017 | Cold-read audit (new-engineer perspective) | quality | intermediate |
| DP-018 | Spec-driven development (spec.md before code) | quality | beginner |
| DP-019 | Test-alongside discipline (SE Principle 13) | quality | beginner |
| DP-020 | Definition of Done (NFR checklist) | quality | beginner |
| DP-021 | Credentials SSoT (.env.shared + sync-credentials.sh) | data-management | beginner |
| DP-022 | pm-registry.json as project identity SSoT | data-management | intermediate |
| DP-023 | WatchTools manifest.toml per tool | data-management | advanced |
| DP-024 | CapabilityWatch 36-capability registry | data-management | advanced |
| DP-025 | Project floor (CLAUDE.md + PM + CEO + skills + contracts + SLOs) | project-structure | intermediate |
| DP-026 | Shared-libs pattern (no cross-project imports) | project-structure | beginner |
| DP-027 | Policy-change ledger (before lowering any threshold) | project-structure | intermediate |
| DP-028 | PHI boundary enforcement (PHIPA/PIPEDA) | security | advanced |
| DP-029 | Secrets never in files (Keychain only) | security | intermediate |
| DP-030 | Add-then-remove migration pattern (DNS, hosting, auth) | security | intermediate |
| DP-031 | Session save protocol (/save → Apple Notes + memory + wiki) | workflow | beginner |
| DP-032 | Constitution inbox capture pipeline | workflow | intermediate |
| DP-033 | WISC context management (Write→Isolate→Select→Compress) | workflow | beginner |
| DP-034 | Boring technology bias (stable over cutting-edge) | workflow | beginner |
| DP-035 | Anti-patterns library (AP-001…AP-014) | anti-pattern | beginner |
| DP-036 | Design patterns registry self-registration (this registry) | meta | beginner |
| DP-037 | YouTube episode derivation from design patterns | meta | beginner |
| DP-038 | Triple Review Protocol (functionality + contradiction + reality) | quality | intermediate |
| DP-039 | Plan/Programmer two-persona split | workflow | beginner |
| DP-040 | Lessons-as-injected-context (lazy load on demand) | enforcement | advanced |

---

## Generating YouTube episodes from patterns

The YouTube channel covers "how a solo engineer runs a software fleet
with Claude Code". Each pattern in this registry seeds at least one episode:

1. Open `categories/12-youtube-episodes/episode-seeds.md`.
2. Find an episode candidate (working title, pattern IDs, audience).
3. Open the source patterns (e.g. `patterns/DP-001-*.md`) and use the
   **"YouTube episode angle"** section as the speaking notes.
4. Each pattern has two angles: **tech-savvy** (10-15 min deep dive) and
   **lay audience** (5-min explainer).
5. Cross-link pattern IDs in the video description so viewers can dive
   deeper.

Or programmatically:

```bash
python3.14 generate-report.py --youtube > /tmp/episode-pitch.md
```

---

## Related artifacts (cross-references)

- **Anti-patterns library**: `~/Projects/shared/anti-patterns.md` (AP-001…AP-014)
- **Lessons learned**: `~/Projects/shared/LESSONS.md` (101 numbered lessons)
- **Lessons index** (lazy-load): `~/Projects/shared/LESSONS-INDEX.md`
- **Cross-project rules**: `~/Projects/shared/rules.md`
- **CEO protocol**: `~/.claude/ceo-protocol.md`
- **Agents protocol**: `~/.claude/agents-protocol.md`
- **Hook registry**: `~/.claude/hooks/HOOK-REGISTRY.md`
- **Constitution rules** (555): `~/Projects/Constitution/ledger.db`
- **WatchTools manifest**: `~/Projects/WatchTools/CLAUDE.md`
- **PM registry** (machine-readable): `~/Projects/shared/pm-registry.json`

---

## Stats at registry creation (2026-05-31)

- **Projects governed**: 81 (24 core + 57 WatchTools phases + 6 non-PM)
- **Constitution rules**: 555 (135 active, 70 proposed, 350 deprecated)
- **Hooks**: 180
- **Skills**: 155
- **Agents**: 24
- **WatchTools detectors**: 69 tools
- **CIS rule IDs**: 250+ across all WatchTools
- **Lessons learned**: 101
- **Anti-patterns**: 14
- **Patterns in this registry**: 40 (this revision)

---

## Public release note

A redacted, dedacted version of this registry will be released on GitHub
under the [Your Company] organization. Patterns are written assuming the reader has
never seen this codebase and wants to adopt the techniques. Replace
project-specific names (<FinanceFlow>, Verscout, etc.) with `<project>` when
porting to a different codebase.
