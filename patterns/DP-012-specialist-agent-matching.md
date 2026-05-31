---
id: DP-012
name: Specialist agent matching (domain-aware dispatch)
category: execution
status: active
constitution-rules: []
youtube-difficulty: intermediate
youtube-episode-length: medium
introduced: 2026-04
---

## What it is

A trigger map (in `~/.claude/agents-protocol.md`) that routes work to the
right specialist agent based on file paths, keywords, and task domain.
24 specialist agents cover Swift, Apps Script, n8n, MCP servers, project-
specific code (financeflow-specialist, corpbooks-specialist, etc.), and
cross-cutting concerns (security-auditor, perf-optimizer).

## Rationale — Why We Adopted This Pattern

*The story of how this pattern came to exist and why it was chosen over alternatives.*

### The problem we kept hitting
A generic "code-reviewer" agent applied to a Swift codebase produced
generic feedback. The same agent on Apps Script missed GAS-specific
gotchas (6-min limit, SpreadsheetRouter pattern). One agent could not be
expert at everything.

### What we tried first (and why it didn't work)
- **One mega-agent with all the rules** — bloated, slow, low signal.
- **Per-task agent (security-auditor, perf-optimizer, etc.)** — good
  start, but missed domain (Swift vs. GAS vs. Python).

### The insight that unlocked the solution
**Match specialists to domains via trigger maps.** "Edited a Swift file
in <SagaMail>" → spawn `swift-specialist`. "Edited a GAS file in
<FinanceFlow>" → spawn `financeflow-specialist`. Trigger maps in
`agents-protocol.md` make this deterministic.

### Why this approach, not the obvious one
*Why not let Claude pick the agent dynamically?* Because Claude's
choice was inconsistent — sometimes the right agent, sometimes a
generic one. A hard-coded trigger map removes the decision and never
forgets.

### Evidence that it works
- 24 specialists, each pre-loaded with domain knowledge
  (financeflow-specialist knows SpreadsheetRouter; sagamail-specialist
  knows Swift 6.3 concurrency rules).
- Familiarity-based delegation rule (drafted 2026-05): write the first
  draft yourself in your *expert* domains, delegate everything else.

## Why we use it

A generalist agent re-derives domain context every time. A specialist
agent has the domain pre-loaded in its CONTEXT.md and SKILL.md. For
familiar codebases (Swift in <SagaMail>, Apps Script in <FinanceFlow>), the
specialist beats the generalist on first-shot accuracy. METR (Jul 2025)
found AI tools are 19% slower on familiar codebases — the specialist
agent mitigates this by pre-loading domain knowledge.

## How it works

**Trigger → agent map** (excerpt from agents-protocol.md):

| Trigger | Agent |
|---------|-------|
| Swift code / <SagaMail> / <PanoMac> / XCTest | `swift-specialist` |
| <FinanceFlow> / SpreadsheetRouter / ColumnMapper | `financeflow-specialist` |
| CIS issue / P0 escalation | `cis-analyst` |
| GAS / Apps Script / `*.gs` / clasp | `apps-script-specialist` |
| <Moonitor> channel / LaunchAgent | `moonitor-ops` |
| `git blame` / "why does this exist?" | `git-historian` |
| Verscout desktop / Sparkle / LemonSqueezy | `verscout-specialist` |
| <CorpBooks> / Canadian tax / RDTOH | `corpbooks-specialist` |
| MCP server / `mcp__*` tools | `mcp-specialist` |

**Anti-duplicate rule:** "Never duplicate — don't run an agent on code
another is already reviewing."

**Familiarity-based override:** For code in domains the human owner
knows deeply, write the first draft yourself or review line-by-line
before delegating. Reserve full agent delegation for new stacks and
one-offs. (Source: METR's 19% finding + 2026-04 owner directive.)

## Example

User asks: "Fix the OAuth token refresh in <SagaMail>."

Dispatch:
1. Match: "<SagaMail>" + "OAuth" → `swift-specialist` (<SagaMail> is Swift)
   + `security-auditor` (OAuth is security)
2. Spawn in parallel.
3. Each agent reads <SagaMail>'s CLAUDE.md + relevant sources.
4. `swift-specialist` produces the patch; `security-auditor` reviews.

## Related patterns

- [DP-009] Subagent-driven execution
- [DP-010] Parallel agent dispatch
- [DP-039] Two-persona split (specialist is the programmer persona)

## YouTube episode angle

- **Tech-savvy** (10-min): Show the trigger map. Live-demo: same task
  routed to a generalist vs specialist; compare outputs. Discuss the
  CONTEXT.md pattern (each specialist has shared owner context + own
  domain context).
- **Lay audience** (5-min): "I have 24 specialists on call." Use the
  hospital analogy: a heart attack doesn't go to a generalist — it
  goes to a cardiologist. Same with code domains.

## Known failure modes / lessons learned

- Specialist agents become stale if their domain CONTEXT.md isn't
  updated when the project changes. `agent-staleness-check.sh` hook
  flags agents whose backing project hasn't been touched in 30 days.
- LESSONS B-003: Without an explicit briefing, even the right specialist
  can re-derive scope incorrectly.
