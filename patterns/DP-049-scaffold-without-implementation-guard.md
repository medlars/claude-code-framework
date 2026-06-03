---
id: DP-049
name: Intentional Scaffold Without Implementation Guard
category: project-structure
status: active
constitution-rules: []
youtube-difficulty: intermediate
youtube-episode-length: short
introduced: 2026-06
---

## What it is

A structural pattern in which placeholder components — functions, classes, modules, or service stubs — are committed to the codebase with clearly signalled empty bodies before any implementation exists. The emptiness is not accidental or temporary neglect; it is the deliberate output of a scoping session. An **implementation guard** (a marker, comment convention, or lint rule) is attached to each stub so that the scaffold's intentional incompleteness is machine-readable and human-legible, preventing the stubs from being mistaken for forgotten work or silently overwritten with premature logic.

## Rationale

### The problem

When a system is designed across multiple sessions or by multiple contributors, there is a recurring collision between two legitimate activities: **architectural definition** and **feature implementation**. Without a separation mechanism, stubs created during design get filled in prematurely, filled in inconsistently, or — just as damaging — left empty with no signal distinguishing them from accidental omissions. Code review, automated checks, and the next engineer all lack the context to know whether an empty body is a bug, a task, or a contract.

In the LearnWatch Phase 1 case this pattern emerged from, four components were scaffolded in a single session — `enqueuer`, `judge`, `writer`, and `deduplicator` — with no implementation planned until the following session. Without a guard, the next session would open an ambiguous codebase: are these done? Broken? In-progress?

### The insight

Intentional incompleteness is information. A stub that announces *"I am a scaffold; my implementation is deferred by design"* carries more architectural value than a half-finished function that announces nothing. The guard converts an absence of code into a **positive assertion**: the interface contract exists, the wiring exists, and the body is the remaining work unit — no more, no less.

### Evidence

The pattern mirrors established practice in several adjacent disciplines. Formal interface definitions in typed languages (abstract base classes, trait declarations, protocol types) are respected precisely because they separate contract from implementation. Agile story decomposition does the same at the task level. What this pattern adds is an in-code, in-repository artefact that survives context switches, session boundaries, and team handoffs without requiring external tracking systems to carry the intent.

## Why we use it

- **Session-boundary safety.** Work paused at the end of a session can be resumed without archaeology. The next session opens the codebase and the guards immediately surface what remains.
- **Prevents premature implementation.** Contributors cannot accidentally fill a stub with logic that contradicts a design decision made but not yet written down.
- **Enables honest integration testing.** A guarded stub can raise a controlled `NotImplementedError` or equivalent, producing a clear failure rather than silent wrong behaviour when called before its time.
- **Keeps architecture visible.** The full shape of the system exists in the repository from the moment design is complete, making dependency graphs and call sites reviewable before any implementation risk is introduced.

## How it works

1. **Design the interface first.** Name the component, define its public signature, and document its responsibility in a docstring or inline comment. Commit this as the scaffold.
2. **Attach an implementation guard.** The guard is a standardised marker — a `# SCAFFOLD: not implemented — Phase N` comment, a `raise NotImplementedError("SCAFFOLD DP-049")` statement, or a lint annotation — that makes the stub detectable by automated tooling.
3. **Register the guard in CI (optional but recommended).** A simple grep or custom lint rule counts open guards. The count can be asserted, reported, or used to block merges to main depending on project policy.
4. **Replace the guard when implementing.** The act of removing the guard is the explicit signal that implementation is complete. Guard removal without accompanying logic is a detectable anti-pattern.
5. **Never silence the guard passively.** Guards must be resolved deliberately; they must not be deleted as cleanup, commented out, or wrapped in conditionals that hide the empty body.

## Example

LearnWatch Phase 1 defines four pipeline components at the end of a design session. Each is committed in the following form:

```
class Enqueuer:
    """Receives raw watch events and places them on the processing queue.
    SCAFFOLD: implementation deferred to Phase 1 build session. DP-049.
    """
    def enqueue(self, event: WatchEvent) -> None:
        raise NotImplementedError("SCAFFOLD DP-049 — Enqueuer.enqueue")
```

The same pattern is applied to `Judge`, `Writer`, and `Deduplicator`. A CI step reports four open DP-049 guards on the Phase 1 branch. The next session opens with a precise, zero-ambiguity task list derived directly from the repository state. When each component is implemented, its guard is removed and the CI count decrements. Phase 1 is complete when the count reaches zero.

## Related patterns

- **DP-012 — Interface-First Module Definition** — defines the broader practice of committing contracts before implementations; DP-049 is the specific application of that principle at a session-boundary granularity.
- **DP-031 — Explicit Phase Tagging** — annotates code and commits with phase identifiers; DP-049 guards frequently carry phase tags as part of their marker string.
- **DP-038 — Controlled Failure Stub** — focuses on stubs that must produce safe, observable failures at runtime; DP-049 guards often use controlled failure as their enforcement mechanism.

## Known failure modes

- **Guard drift.** If the guard comment and the `NotImplementedError` diverge — one removed, the other not — the stub becomes ambiguous again. Treat them as a single atomic unit; tooling should verify both are present or both are absent.
- **Guard inflation.** Overuse turns every function placeholder into a DP-049 artefact, drowning genuine incomplete work in noise. Reserve the pattern for cross-session or cross-contributor boundaries, not intra-session work-in-progress.
- **Premature guard removal.** A contributor removes the guard to silence a failing test before implementing the body. CI must distinguish "guard removed with implementation" from "guard removed without implementation", either by requiring tests that exercise the formerly-guarded path or by pairing guard removal with a mandatory review note.
- **Stale guards.** A guard that survives past its target phase becomes indistinguishable from forgotten work. Guards should carry a target phase or date; CI can escalate stale guards to warnings after the deadline passes.
