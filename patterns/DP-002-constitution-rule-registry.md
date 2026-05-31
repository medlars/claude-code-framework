---
id: DP-002
name: Constitution as SSoT for all rules
category: governance
status: active
constitution-rules: [SPEC-181]
youtube-difficulty: intermediate
youtube-episode-length: long
introduced: 2026-05
---

## What it is

The Constitution is a SQLite-backed rule registry at `~/Projects/Constitution/`
that holds every rule the fleet must obey — including behavioral rules,
hook rules, CLAUDE.md fragments, anti-patterns, ADRs, and specifications.
Every rule has a status (proposed / active / deprecated), a category, an
enforcement tier (hook-enforced / other-wired / ledger-only), and a backlink
to its enforcement artifact (a hook, a stage, a check_pattern).

Current state (2026-05-31): 555 rules total — 135 active, 70 proposed, 350
deprecated. 53 are hook-enforced.

## Rationale — Why We Adopted This Pattern

*The story of how this pattern came to exist and why it was chosen over alternatives.*

### The problem we kept hitting
Rules lived in 12 different CLAUDE.md files (global, per-project, per-skill).
The same rule appeared in 4 places, two of which disagreed. New sessions
didn't know which rule applied. Deprecated rules lingered because nobody
knew what depended on them. When a CLAUDE.md was edited mid-session the
prompt cache was destroyed and the rule sometimes wasn't reloaded until
the next conversation.

### What we tried first (and why it didn't work)
- **One mega-CLAUDE.md** — hit Claude Code's context budget; rule density
  dropped reasoning quality.
- **Per-project CLAUDE.md only** — global rules duplicated, drifted within
  weeks.
- **Memory entries** — advisory only; LESSONS 002 nailed this: "memory
  without a hook is a wish".

### The insight that unlocked the solution
**Rules should be first-class data, not prose.** Once a rule is in a
SQLite ledger with an ID, a category, a status, and a backlink to its
enforcement artifact, you can query it, audit it, deprecate it, and most
importantly *detect drift*. Markdown can't do that.

### Why this approach, not the obvious one
*Why not just use a YAML file?* Because we need an audit trail (`events`
table), an inbox queue (`instructions` table), and joinable artifact
links — a database does this natively. A YAML diff doesn't tell you
"this rule went from proposed → active because of session X on date Y";
the `events` table does.

### Evidence that it works
- 555 rules tracked; 350 cleanly deprecated without leaving dangling
  enforcement.
- `constitution audit` finds MISSING/ORPHAN/DRIFT cases in seconds;
  before, drift went undetected for months.
- SPEC-181 (this very registry) is itself recorded as a Constitution rule
  with a backlink to the design-patterns directory — meta-self-consistency.

## Why we use it

Rules in markdown files drift. The same rule appears in 4 places, two of
which disagree. New sessions don't know which rule applies. Deprecated
rules linger because nobody knows what depends on them.

The Constitution solves this by making rules first-class data with a CLI
(`constitution.py`) and a ledger (`ledger.db`). Every rule has a single
authoritative record. Every artifact (hook, doc, check) traces back to its
rule. Drift detection compares "what's in the ledger" vs "what's actually
wired" and surfaces gaps.

The deeper principle: **rules should be discoverable, queryable, and
auditable — not buried in tribal knowledge.**

## How it works

**Schema:**
- `rules` (id, title, description, type, category, status, check_pattern,
  enforcement, created_at, deprecated_at, supersedes)
- `instructions` (proposed rule fragments from session inbox; promote to rules)
- `artifacts` (hook files, doc fragments, check patterns linked to rules)
- `events` (audit trail: who changed what when)

**CLI surface:**
```bash
constitution init                # crawl fleet, populate ledger as proposed
constitution audit               # detect drift/gaps/orphans
constitution add-rule --type ... --title ... --check-pattern ...
constitution promote <id>        # proposed → active (requires human)
constitution deprecate <id>      # active → deprecated
constitution stats               # 555 total, breakdown by category
constitution why <id>            # full history of a rule
constitution serve               # dashboard at localhost:7879
```

**Inbox capture:** When a CLAUDE.md edit or session reveals a new rule, it
lands in `Constitution/inbox/*.json` and becomes a `proposed` instruction.
Humans triage via `constitution add-instruction` → `promote`.

**Drift detection:** `constitution audit` walks the fleet and compares
rules against actual artifacts. Three failure modes:
- Rule active but no enforcement wired → MISSING
- Artifact present but no rule → ORPHAN
- Rule and artifact disagree → DRIFT

## Example

Adding the design-patterns registry itself as a rule:

```bash
python3.14 ~/Projects/Constitution/constitution.py add-rule \
  --type specification \
  --title "Design Patterns Registry" \
  --description "SSoT for all Claude Code engineering patterns, SPEC-181" \
  --check-pattern "NONE" \
  --enforcement "documentation" \
  --category "meta"
```

Querying who depends on a rule:

```bash
constitution why CON-039
# → CON-039: No hardcoded ~/ paths
#   Enforced by: no-hardcoded-paths.sh, hardcoded-path-in-content.sh
#   Created: 2026-05-04
#   Lessons: LESSONS 019, LESSONS 028
```

## Related patterns

- [DP-001] CEO/PM/CIS hierarchy (Constitution sits beside CIS)
- [DP-013] Hook-as-judiciary (Constitution rules need hook enforcement)
- [DP-027] Policy-change ledger (Constitution events table is the audit)
- [DP-032] Inbox capture pipeline (how proposed rules enter)
- [DP-036] Self-registration of this very registry

## YouTube episode angle

- **Tech-savvy** (15-min): "Why your markdown rules are lying to you." Show
  three competing copies of the same rule across 3 CLAUDE.md files; run
  `constitution audit` to find the drift; demonstrate the dashboard.
- **Lay audience** (8-min): "I gave my AI a law library." Use the analogy
  of a country's legal code vs. a verbal agreement. Show that 555 rules
  exist; the AI cannot break them because a shell hook enforces each one.

## Known failure modes / lessons learned

- LESSONS 005: `db.add_instruction()` requires `type_=` (not `type=`)
  because `type` is a Python builtin.
- LESSONS 006: `ledger_only` sentinel artifacts must be skipped in
  drift detection; otherwise 72 false MISSING reports.
- LESSONS 007: `stage_lint` must scope to `src/`, not root, to avoid E402
  false positives from `sys.path.insert` in `constitution.py` entrypoint.
- no.md 001: Never bulk-promote proposed rules; human review required.
