---
id: DP-010
name: Parallel agent dispatch
category: execution
status: active
constitution-rules: []
youtube-difficulty: intermediate
youtube-episode-length: medium
introduced: 2026-04
---

## What it is

The agents protocol (`~/.claude/agents-protocol.md`) defines triggers that
spawn multiple agents in parallel when their work is independent. Example:
"pre-push" triggers `security-auditor` and `perf-optimizer` simultaneously
because neither depends on the other's output.

## Rationale — Why We Adopted This Pattern

*The story of how this pattern came to exist and why it was chosen over alternatives.*

### The problem we kept hitting
Sequential subagent calls (run agent A, wait, run agent B, wait, run
agent C) burned 3× the wall-clock time when the three agents had no
dependencies on each other. A pre-push audit that ran security + perf +
test-writer serially took 12 minutes; in parallel, ~4.

### What we tried first (and why it didn't work)
- **One mega-agent that does everything** — degraded for the same reason
  inline execution does (context bloat).
- **Manual parallelization with `&` in shell** — no result aggregation,
  hard to surface failures.

### The insight that unlocked the solution
**The Task tool accepts multiple subagent invocations in one assistant
turn and runs them concurrently.** As long as the agents have no
inter-dependencies, batch them.

### Why this approach, not the obvious one
*Why not always run agents serially for simplicity?* Because the cost is
linear in the number of agents, and the fleet has 24 specialists. A
pre-push that runs 4 agents in parallel saves ~9 min per push × dozens
of pushes per week = hours weekly.

### Evidence that it works
- Pre-push (`/pre-push` skill) runs 4 audits in parallel; users report
  the difference between "I'll wait for it" (serial) vs. "barely
  noticeable" (parallel).

## Why we use it

Sequential checks waste wall-clock time. If three independent audits each
take 2 minutes, running them in parallel finishes in 2 minutes instead
of 6. The orchestrator gets all results before the next decision point.

## How it works

**Trigger → mode map** (from agents-protocol.md):

| Trigger | Agent | Mode |
|---------|-------|------|
| Pre-push / PR creation | `security-auditor` + `perf-optimizer` | Parallel |
| Multi-step deterministic pipeline | `blueprint-runner` | Foreground |
| Edited 3+ Python files | `security-auditor` | Background |
| Completed a feature (5+ edits) | `test-writer` | Background |

**Dispatch rule:** All tool calls with no dependency between them must be
made in the same message (parallel). Tool calls that depend on prior
results are sequential.

**Example from `~/.claude/agents-protocol.md`:**
> "AGENT_DISPATCH: hook messages are MANDATORY — spawn immediately,
> continue working."

## Example

Pre-push for SagaMail:

```
# In a single message, three Task calls:
Task(subagent_type="security-auditor", prompt="audit SagaMail for OAuth bugs")
Task(subagent_type="perf-optimizer",   prompt="profile SagaMail message render path")
Task(subagent_type="test-writer",      prompt="cover new IMAP retry logic with tests")

# Wall-clock: max(t1, t2, t3) instead of sum
```

## Related patterns

- [DP-009] Subagent-driven (the prerequisite for parallel)
- [DP-012] Specialist agent matching
- [DP-038] Triple Review Protocol (parallel verifications)

## YouTube episode angle

- **Tech-savvy** (10-min): Live demo: pre-push event spawns 3 agents in
  parallel; show the timeline. Discuss when parallel doesn't apply
  (when output of A feeds B).
- **Lay audience** (5-min): "Three specialists in parallel beats one
  generalist sequential." Use the analogy of a pit stop crew — tire,
  fuel, windshield, all at once.

## Known failure modes / lessons learned

- `playwright-one-at-a-time.sh` hook exists because parallel Playwright
  agents collide on the headless browser instance — not all agents are
  safely parallel.
- Agents that write to overlapping files must be sequential; conflict
  resolution is not automatic.
