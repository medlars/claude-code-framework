---
id: DP-044
name: Missing Input Pathway in Multi-Source Detection Pipeline
category: workflow
status: active
constitution-rules: []
youtube-difficulty: intermediate
youtube-episode-length: short
introduced: 2026-05
---

## What it is

A structural design rule requiring that every legitimate source of bug discovery in a system is explicitly wired as a named, tested input pathway into the central defect pipeline. No detection source may exist as an informal side-channel or implicit assumption. Each pathway must have a defined trigger mechanism, a normalization contract, and a verified integration test.

## Rationale

### The problem

Multi-source detection pipelines accumulate input pathways incrementally. The first pathway is built carefully; subsequent pathways are added reactively as new detection sources emerge. This incremental approach almost always produces gaps: sources that generate valid signals but have no formal trigger connecting them to the pipeline. The pipeline appears complete because the existing pathways work correctly, but entire classes of findings silently evaporate before they can be acted on.

In the motivating case, the detector-gap pipeline accepted bugs from three sources: runtime Bash errors captured by an execution harness, user-reported errors embedded in prompt text, and entries queued by a Stop-hook processor. Static cold-read analysis — a developer reading source code and identifying a defect without executing it — was a real and frequent discovery activity, but it had no pathway. Bugs found this way either had to be manually inserted into the queue by remembering a separate procedure, or they were lost entirely. The pipeline did not fail loudly. It simply never received those signals.

### The insight

A pipeline that handles only the sources its authors thought of during construction is not a complete pipeline — it is a partial pipeline with an invisible boundary. The boundary is invisible because the missing pathways produce no errors; they produce nothing at all. Completeness cannot be inferred from the absence of failures. It must be established by positive enumeration: list every source, verify every source has a pathway, and make the list a first-class artifact that is reviewed whenever a new detection activity is introduced.

### Evidence

The static cold-read gap went unnoticed because code review, exploratory reading, and documentation audits are cognitively distinct from tool-mediated execution. They do not naturally produce machine-readable output. When developers found bugs this way, the path of least resistance was to fix the bug immediately or add a comment, neither of which fed the pipeline. The pipeline's metrics consequently undercounted statically discovered defects, producing skewed data about defect origin distribution and suppressing improvements targeted at static analysis workflows.

## Why we use it

- Prevents silent signal loss from detection sources that lack formal integration
- Makes pipeline coverage auditable by maintaining an explicit source registry
- Forces new detection activities to define their integration contract before they are adopted, rather than after gaps are noticed
- Decouples the act of discovery from the act of pipeline entry, allowing asynchronous or human-mediated sources to participate alongside automated ones
- Produces accurate defect-origin telemetry, which is a prerequisite for allocating detection investment correctly

## How it works

1. **Enumerate all detection sources.** Maintain a source registry — a simple table listing every activity or tool that can legitimately discover a defect. Examples: runtime execution harness, user prompt parsing, Stop-hook processor, static cold-read review, linter output, dependency audit, test failure, external security report.

2. **Define a pathway for each source.** Each source maps to exactly one intake pathway. The pathway specifies: the trigger mechanism (automatic, semi-automatic, or manual with a defined UI), the normalization schema the finding must conform to, and the queue or handler that receives it.

3. **Classify the trigger type explicitly.** Not all pathways can be fully automated. Static cold-read findings require a human-initiated action. That action must be defined, documented, and made low-friction — for example, a single CLI command or form that accepts a finding description and injects a normalized record into the queue. The classification (automatic / semi-automatic / manual) is recorded in the source registry.

4. **Write an integration test for each pathway.** Each pathway must have at least one test that proves a finding originating from that source reaches the pipeline in a normalized form. Tests for manual pathways simulate the human action programmatically.

5. **Gate source registry completeness at intake.** When a new detection activity is proposed or observed, the first question asked is: does this source have a registered pathway? If not, creating the pathway is a prerequisite for adopting the activity, not a follow-up task.

6. **Review the registry on a defined cadence.** At each pipeline retrospective, the source registry is walked in full. Sources with low signal volume are investigated — low volume may indicate a healthy source, an underused detection activity, or a broken pathway that is silently dropping findings.

## Example

Before the pattern was applied, the detector-gap pipeline had this effective source table (implicit, never written down):

| Source | Pathway |
|---|---|
| Runtime Bash error | Execution harness → normalize → queue |
| User-reported error in prompt | Prompt parser → normalize → queue |
| Stop-hook queue entry | Stop-hook processor → queue |

Static cold-read analysis existed as a detection activity but had no row. After applying the pattern, the registry became explicit and gained the missing entry:

| Source | Trigger type | Pathway |
|---|---|---|
| Runtime Bash error | Automatic | Execution harness → normalize → queue |
| User-reported error in prompt | Automatic | Prompt parser → normalize → queue |
| Stop-hook queue entry | Automatic | Stop-hook processor → queue |
| Static cold-read analysis | Manual | `vohux report-finding --source cold-read --description "…"` → normalize → queue |

The manual trigger was implemented as a single CLI command. An integration test verified that invoking the command with a valid description produced a normalized record in the queue indistinguishable in schema from automatically generated records. The source registry was committed to the repository alongside the pipeline code.

## Related patterns

- **DP-017 · Explicit Queue Contract** — defines the normalization schema that all pathways must produce; DP-044 ensures every source has a pathway, DP-017 ensures every pathway produces conformant output
- **DP-029 · Dead Signal Audit** — periodic review process for detecting pathways that are registered but producing unexpectedly low or zero signal
- **DP-051 · Manual Trigger Affordance** *(not yet created)* — design rules for low-friction human-initiated pipeline entry points, directly applicable to the manual trigger class defined in step 3 of this pattern
- **DP-008 · Pipeline Source Registry** — the artifact format used to maintain the enumerated source list; DP-044 specifies the workflow discipline, DP-008 specifies the schema

## Known failure modes

**Registry drift.** The source registry is created accurately but not updated when new detection activities are introduced informally. Mitigated by making the registry a required review item in onboarding for new detection tools and in pipeline retrospectives.

**Manual trigger abandonment.** A manual pathway is defined and tested but is too cumbersome to use in practice, so developers stop using it. Findings from that source silently drop again despite the pathway existing on paper. Mitigated by instrumenting pathway usage and alerting when a manual pathway has had zero submissions for longer than a defined interval.

**Schema partial compliance.** A pathway produces records that pass validation but omit optional fields that downstream consumers depend on for routing or prioritization. The finding enters the pipeline but is mishandled. Mitigated by distinguishing required from recommended fields in the normalization schema and adding downstream routing tests that exercise optional field handling.

**Source conflation.** Two distinct detection activities are mapped to a single pathway entry because they seem similar. One activity's nuances are lost in normalization. Mitigated by requiring that each source registry entry correspond to a single, independently describable discovery activity, and reviewing entries where signal characteristics diverge from expectation.

**Completeness illusion from test coverage.** All registered pathways have passing integration tests, creating confidence that the pipeline is complete. But an unregistered source still has no pathway and no test. This failure mode is inherent — tests can only cover what is enumerated. Mitigated by making the enumeration process itself an auditable activity with sign-off, not a one-time setup task.
