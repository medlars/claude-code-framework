---
id: DP-045
name: Missing Input Source in Multi-Path Pipeline
category: workflow
status: proposed
constitution-rules: []
youtube-difficulty: intermediate
youtube-episode-length: short
introduced: 2026-05
---

## What it is

A design discipline requiring that every pipeline accepting inputs from multiple distinct sources be explicitly enumerated, documented, and tested at each entry point — so that a new input source discovered after initial construction is formally added to the wiring before the pipeline is considered complete.

## Rationale

### The problem

Multi-path pipelines are built incrementally. The first version wires the sources that are obvious at construction time. Additional sources get discovered later — through use, through code review, or through adjacent work — but because the pipeline already "works," the new source is noted and then quietly forgotten. No entry point gets added. Data from that source never flows downstream.

In the concrete case that prompted this pattern, a detector-gap pipeline accepted bugs from three paths: runtime Bash errors, user-reported errors in prompts, and a Stop-hook queue. When an engineer found a bug by reading code cold — static analysis, no execution — there was nowhere to send it. The pipeline had no static-analysis entry point. The bug either had to be shoehorned into an ill-fitting existing path or logged informally and lost.

### The insight

The absence of a wired input source is structurally invisible. A pipeline with three working paths looks complete. Logs show activity. Metrics show throughput. Nothing signals that a fourth class of events is falling on the floor. The gap only becomes visible when someone asks "where would I put a bug found this way?" and the honest answer is "nowhere."

Preventing this requires treating the set of input sources as an explicit, versioned artifact — not an implementation detail — and requiring that any newly identified source go through a deliberate wiring step before the pipeline is used in production.

### Evidence

The detector-gap pipeline operated correctly for its three wired paths for weeks. The missing static-analysis path was only surfaced during a retrospective discussion about why certain known bugs were never appearing in the gap tracker. Tracing backward revealed that every example of a statically discovered bug had been either manually entered by an engineer who remembered to do so, or had simply been forgotten. The pipeline's throughput metrics showed nothing wrong.

## Why we use it

- Prevents silent data loss that is undetectable from inside the pipeline
- Forces enumeration of all expected event classes before a pipeline is declared production-ready
- Creates a forcing function for updating wiring when new discovery methods or input channels are introduced
- Makes the pipeline's scope a first-class design decision rather than an emergent property of whatever got implemented first

## How it works

1. **Source inventory first.** Before implementing any routing logic, produce an exhaustive list of every mechanism by which input events can originate. Treat this list as a required design artifact, not documentation added after the fact.

2. **One explicit entry point per source.** Each source in the inventory gets its own named, documented entry point in the pipeline. Entry points are not shared across structurally different sources, because sharing obscures whether all sources are actually wired.

3. **Gap check on every new source.** Whenever a new input source is identified — at any point in the pipeline's lifecycle — a gap check is run: is this source in the inventory? Is its entry point implemented? Is it tested? All three must be true before the source is considered wired.

4. **Source completeness assertion.** The pipeline includes a lightweight assertion or audit step, run on a schedule or at deploy time, that compares the current source inventory against implemented entry points and fails loudly if any source is unwired.

5. **New source = new version.** Adding a source increments the pipeline's minor version and requires a changelog entry describing what the source is, what events it produces, and how it was previously handled (or mishandled).

## Example

**Before (broken wiring):**

The detector-gap pipeline has three entry points:

- `ingest_runtime_bash_error(event)`
- `ingest_user_reported_error(prompt_context)`
- `ingest_stop_hook_queue_item(queue_entry)`

An engineer finds a bug by reading code. There is no `ingest_static_analysis_finding()`. The engineer files a note in a personal document. The bug never reaches the gap tracker.

**After (gap check applied):**

During a pipeline review, the source inventory is audited:

| Source | Inventory | Entry Point | Test |
|---|---|---|---|
| Runtime Bash error | ✓ | ✓ | ✓ |
| User-reported prompt error | ✓ | ✓ | ✓ |
| Stop-hook queue | ✓ | ✓ | ✓ |
| Static cold-read analysis | ✓ | ✗ | ✗ |

The missing row fails the completeness assertion. A fourth entry point is implemented:

- `ingest_static_analysis_finding(file_ref, line_range, description)`

The pipeline is re-deployed at v1.1.0. Statically discovered bugs now flow through the same gap tracking, prioritization, and resolution stages as all other bug classes.

## Related patterns

- **DP-017 — Explicit Sink Enumeration:** the output-side analogue; applies the same discipline to pipeline destinations rather than sources
- **DP-029 — Dead Path Detection:** identifies pipeline branches that exist in code but receive zero events in production, which can surface sources that were wired but disconnected
- **DP-051 — Changelog as Contract** *(not yet created):* governs the versioning behavior required in step 5 of this pattern's implementation

## Known failure modes

**Inventory drift.** The source inventory is created at build time and then not maintained. New sources get implemented directly as entry points without updating the inventory, so the completeness assertion passes even though undocumented sources exist and documented gaps are masked.

**Catch-all entry points.** An engineer adds a generic `ingest_other(raw_event)` path to handle any source not explicitly wired. This satisfies the completeness assertion formally while defeating it in practice — all ungrouped sources collapse into one opaque path with no structure, no type safety, and no auditability.

**Source conflation.** Two structurally distinct sources are mapped to a single entry point because their event shapes look similar. Static analysis findings and linter warnings are both "code observations," so they share an entry point. Downstream logic cannot distinguish them, and one source's events are systematically misclassified.

**Inventory treated as optional.** Teams skip the source inventory step under time pressure, building entry points directly from known sources. The inventory is never created, so there is no artifact against which to run a completeness assertion. The pattern's core mechanism never activates.

**Late-lifecycle blindness.** The completeness assertion is run only at initial deploy. Sources added through operational evolution — new tooling, new team workflows, new automated scanners — are never checked against it because the assertion is not re-run on a schedule or on configuration change.
