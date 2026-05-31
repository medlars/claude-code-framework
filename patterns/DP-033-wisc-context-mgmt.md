---
id: DP-033
name: WISC context management (Write→Isolate→Select→Compress)
category: workflow
status: active
constitution-rules: []
youtube-difficulty: beginner
youtube-episode-length: short
introduced: 2026-05
---

## What it is

A four-step protocol from `~/.claude/CLAUDE.md` for long sessions:
- **W**rite checkpoint (snapshot progress to a file)
- **I**solate active files (drop everything else from working memory)
- **S**elect only needed lines (don't reread whole files)
- **C**ompress completed work to 1–2 sentences

Applied at ~40+ tool calls or when context-rot signals appear
(referencing stale file content, forgetting earlier decisions,
re-solving solved problems).

## Rationale — Why We Adopted This Pattern

*The story of how this pattern came to exist and why it was chosen over alternatives.*

### The problem we kept hitting
Long sessions (50+ tool calls) degraded in quality even within the
context window limit. The model started referencing stale file content,
forgetting earlier decisions, re-solving solved problems, contradicting
earlier analysis.

### What we tried first (and why it didn't work)
- **`/compact`** — destroyed cache, lost context, replaced one failure
  mode with another.
- **`/clear` then resume** — lost too much.

### The insight that unlocked the solution
**Prune working memory before quality degrades.** WISC: **W**rite a
checkpoint (current state in one sentence) → **I**solate active files →
**S**elect only the lines needed → **C**ompress completed work to 1-2
sentences. Done by the model itself, no `/compact` required.

### Why this approach, not the obvious one
*Why not just rely on Claude's own context management?* Because the
context window has a hard limit AND a soft quality limit far below it.
WISC operates above both.

### Evidence that it works
- Sessions that apply WISC at the 40-tool-call mark maintain output
  quality; sessions that don't visibly degrade.

## Why we use it

Long contexts degrade output quality even within the context window
limit ("context rot"). Without WISC, the orchestrator accumulates
50KB+ of stale tool output, slowing reasoning and increasing
hallucination. WISC trims to the live working set.

## How it works

**W — Write checkpoint** (`inject-compact-checkpoint.sh`):
- Snapshot to `progress.txt` or pair-notes file
- JSON for structured status, git for code state
- The checkpoint is the recovery point

**I — Isolate**:
- Mentally drop files no longer being edited
- Only the files in the active code change stay in working memory
- Past tool outputs become historical noise

**S — Select**:
- Read only the lines you need with Read offset+limit
- Avoid `cat full_file.py` when 20 lines will do
- Use Grep with -n to locate precisely

**C — Compress**:
- Summarize completed phases as 1-2 sentences
- "Phase 1 complete: fixed bare-except in 4 files, tests green"
- Drop the per-file detail

**Hook**: `inject-compact-checkpoint.sh` reminds at threshold.

## Example

After 40 tool calls in a refactor:

Without WISC: orchestrator still references the first edit's output;
context is 80KB of mixed signal/noise; next decision is fuzzy.

With WISC:
- W: `echo "Phase 1: refactored SpreadsheetRouter (4 files). Phase 2 next." > progress.txt`
- I: only `ColumnMapper.gs` is being edited now
- S: Read offset=120 limit=60 instead of full file
- C: drop the 6 earlier Read outputs from active reasoning

## Related patterns

- [DP-009] Subagent-driven (subagents are W in WISC)
- [DP-031] Session save (formal W at session end)
- [DP-040] Lessons-as-injected-context (lazy-load is select+compress)

## YouTube episode angle

- **Tech-savvy** (5-min): "Why long contexts get dumber." Show context
  rot with metrics. Walk through WISC steps live.
- **Lay audience** (3-min): "Clean your desk before the next case."
  Analogy: surgeon's instrument tray reset between procedures.

## Known failure modes / lessons learned

- /compact mid-task destroys cache; WISC is the alternative — keep
  cache warm by trimming working memory manually.
- LESSONS B-013: Write acceptance criterion before first edit — pairs
  with C (the criterion is the compressed goal).
