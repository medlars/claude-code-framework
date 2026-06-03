---
id: DP-048
name: Incomplete Scaffold Handoff Without Implementation Tracking
category: project-structure
status: proposed
constitution-rules: []
youtube-difficulty: intermediate
youtube-episode-length: short
introduced: 2026-06
---

## What it is

A pattern that recognizes when a codebase contains intentional structural stubs — files, modules, or interfaces created to define shape but not behavior — and ensures those stubs are explicitly tracked as unimplemented work rather than silently carried forward as if complete. The pattern distinguishes between a scaffold that *is the deliverable* and a scaffold that *precedes the deliverable*, then creates an unambiguous handoff record so the next session, engineer, or agent cannot mistake presence for completeness.

## Rationale

### The problem

Scaffolding looks like progress. When a session ends with files created, directories structured, and function signatures in place, the surface appearance of a working system can cause the next person — or the same person returning later — to begin work on top of an assumed foundation that does not yet exist. In the LearnWatch Phase 1 case, four components (enqueuer, judge, writer, deduplicator) were stubbed with correct interfaces but no logic. Without explicit tracking, the next session could wire them together, write tests against them, or mark Phase 1 complete — all while the actual implementation work had never been done.

The cost of this mistake is not just wasted time. It is wasted confidence. Systems built on unimplemented stubs fail in ways that look like integration problems, timing problems, or environmental problems — not like the obvious absence of a function body.

### The insight

The act of scaffolding and the act of implementing are two distinct deliverables that occupy different sessions for good reason. Scaffolding resolves design uncertainty. Implementation resolves behavioral uncertainty. When a session boundary falls between them, the scaffold is complete and correct — but it must be labeled with the same rigor applied to any incomplete work item. The insight is that *intentional incompleteness is not a defect to be hidden; it is a state to be declared*.

A stub file with no tracking artifact is a liability. The same stub file with an explicit `TODO: Phase 1 implementation — next session` marker, a registry entry, or a handoff note is a contract. The difference is not in the code; it is in the metadata surrounding the code.

### Evidence

LearnWatch Phase 1 scaffolded four core pipeline components across a single session. The stubs were correct in structure and naming. No implementation existed. The session ended without a formal record that distinguished "scaffold created" from "component implemented." Had DP-048 been applied, the handoff would have produced an explicit list of the four unimplemented modules with their expected behaviors, preventing any downstream session from treating Phase 1 as shippable.

## Why we use it

- Prevents false-positive progress signals at session boundaries
- Eliminates ambiguity for agents, collaborators, or future-self about what "exists" versus what "works"
- Keeps scaffold work — which has real value — from being conflated with implementation work, which preserves accurate velocity tracking
- Creates a recoverable handoff state: even if context is lost, the tracking artifact restores intent

## How it works

1. **At scaffold creation**, annotate each stub with a structured marker that names the expected behavior, not just the fact of incompleteness. A comment reading `// TODO: implement` is insufficient. A comment reading `// TODO: Phase 1 — enqueue validated watch event to Redis stream, return enqueue ID` is a contract.

2. **At session close**, produce a handoff note that enumerates every unimplemented stub by module name, expected behavior, and the phase or session that owns implementation. This note lives adjacent to the code — in a `HANDOFF.md`, a session log entry, or a registry record — not only in the engineer's memory.

3. **At session open**, the first act before writing any new code is to locate and read the handoff note. Stubs without implementation are not touched for integration or testing until their implementation task has been explicitly closed.

4. **On implementation completion**, the stub marker is replaced with a completion marker or removed, and the handoff record is updated. Presence of a stub marker in a merged branch signals work that has not been done.

## Example

LearnWatch Phase 1 scaffolded the following pipeline components with no implementation:

| Module | Stub Location | Expected Behavior |
|---|---|---|
| `enqueuer` | `src/pipeline/enqueuer.ts` | Accept validated watch event, push to Redis stream, return stream entry ID |
| `judge` | `src/pipeline/judge.ts` | Evaluate watch event against user learning profile, return relevance score |
| `writer` | `src/pipeline/writer.ts` | Persist scored event to database with metadata |
| `deduplicator` | `src/pipeline/deduplicator.ts` | Check event fingerprint against recent window, return duplicate/novel status |

The correct handoff artifact at end of scaffold session:

```
HANDOFF — LearnWatch Phase 1 Scaffold Complete
Date: 2026-06
Status: Scaffold only. Zero implementation exists.
Next session must implement all four modules before any integration work begins.
Do not write pipeline wiring, tests, or Phase 2 work until this list is cleared.
```

Each stub file opens with a structured marker:

```
// UNIMPLEMENTED — Phase 1 / Session: LearnWatch-002
// Expected: [behavior description]
// Owner: next session
```

## Related patterns

- **DP-012 Session Boundary Artifact** — defines the general practice of producing recoverable state at every session close; DP-048 is a specialization for scaffold-specific state
- **DP-031 Interface-First Component Design** — the upstream pattern that produces intentional stubs; DP-048 governs what happens after stubs exist
- **DP-019 Phase Gate Checklist** — ensures phase transitions are not made until gate criteria are met; DP-048 feeds the implementation criteria that Phase Gates check

## Known failure modes

**Silent stub aging.** A stub that is never implemented but also never causes a test failure can persist across many sessions without being noticed. Mitigation: stub markers must appear in a location that is checked during routine build or lint passes, not only in comments that require file-level inspection.

**Over-annotation leading to noise desensitization.** If every file in a project carries `UNIMPLEMENTED` markers for minor gaps, engineers begin ignoring them. Mitigation: reserve structured stub markers strictly for session-boundary handoffs, not for routine in-flight development TODOs.

**Handoff note decay.** A handoff note written at session close is accurate at that moment. If partial implementation occurs without updating the note, it becomes misleading. Mitigation: the handoff note is a living document updated on every touch, not an archive artifact written once.

**Mistaking scaffold quality for implementation readiness.** A well-designed stub can appear so complete — correct types, good names, sensible signatures — that reviewers assume the body is trivially absent rather than genuinely missing. Mitigation: stub markers should state expected behavior in behavioral terms, making the gap concrete rather than cosmetic.
