# Design Patterns Index (machine-readable)

# This file is the canonical, parseable index. Human-readable views live in
# README.md and per-category directories.

version: "1.0"
generated: 2026-05-31
total_patterns: 40
schema: |
  patterns[]:
    id: DP-NNN
    name: short descriptive name
    category: one of (governance, detection, execution, enforcement, quality,
              data-management, project-structure, security, workflow,
              anti-pattern, meta)
    status: active | deprecated
    constitution_rules: [RULE-XXX, ...]
    youtube_difficulty: beginner | intermediate | advanced
    youtube_length: short | medium | long
    introduced: YYYY-MM
    file: patterns/DP-NNN-slug.md
    related: [DP-XXX, ...]

patterns:
  - id: DP-001
    name: CEO/PM/CIS three-tier supervision hierarchy
    category: governance
    status: active
    constitution_rules: []
    youtube_difficulty: intermediate
    youtube_length: long
    introduced: 2026-04
    file: patterns/DP-001-ceo-pm-cis-hierarchy.md
    related: [DP-002, DP-003, DP-004, DP-007]

  - id: DP-002
    name: Constitution as SSoT for all rules
    category: governance
    status: active
    constitution_rules: [SPEC-181]
    youtube_difficulty: intermediate
    youtube_length: long
    introduced: 2026-05
    file: patterns/DP-002-constitution-rule-registry.md
    related: [DP-001, DP-013]

  - id: DP-003
    name: PM script contract (14-part structure)
    category: governance
    status: active
    constitution_rules: []
    youtube_difficulty: advanced
    youtube_length: long
    introduced: 2026-04
    file: patterns/DP-003-pm-script-contract.md
    related: [DP-001, DP-016, DP-019]

  - id: DP-004
    name: CEO propagation rule (cross-PM consistency)
    category: governance
    status: active
    constitution_rules: []
    youtube_difficulty: advanced
    youtube_length: medium
    introduced: 2026-04
    file: patterns/DP-004-ceo-propagation.md
    related: [DP-001, DP-003]

  - id: DP-005
    name: WatchTools detector-gap pattern (bug → detector → prevention)
    category: detection
    status: active
    constitution_rules: []
    youtube_difficulty: intermediate
    youtube_length: medium
    introduced: 2026-05
    file: patterns/DP-005-watchtools-detector-gap.md
    related: [DP-007, DP-008, DP-013, DP-035]

  - id: DP-006
    name: 9-dimension cold-read audit methodology
    category: detection
    status: active
    constitution_rules: []
    youtube_difficulty: advanced
    youtube_length: long
    introduced: 2026-05
    file: patterns/DP-006-9dim-cold-read.md
    related: [DP-005, DP-017]

  - id: DP-007
    name: CIS (Central Issue Store) as durable finding record
    category: detection
    status: active
    constitution_rules: []
    youtube_difficulty: intermediate
    youtube_length: medium
    introduced: 2026-05
    file: patterns/DP-007-central-issue-store.md
    related: [DP-001, DP-005, DP-014]

  - id: DP-008
    name: SilentFailureWatch (exception-swallowing detector)
    category: detection
    status: active
    constitution_rules: [SFW-001, SFW-002, SFW-003]
    youtube_difficulty: intermediate
    youtube_length: short
    introduced: 2026-05
    file: patterns/DP-008-silent-failure-watch.md
    related: [DP-005, DP-007]

  - id: DP-009
    name: Subagent-driven execution (standing preference)
    category: execution
    status: active
    constitution_rules: []
    youtube_difficulty: beginner
    youtube_length: short
    introduced: 2026-05
    file: patterns/DP-009-subagent-driven.md
    related: [DP-010, DP-012]

  - id: DP-010
    name: Parallel agent dispatch
    category: execution
    status: active
    constitution_rules: []
    youtube_difficulty: intermediate
    youtube_length: medium
    introduced: 2026-04
    file: patterns/DP-010-parallel-agent-dispatch.md
    related: [DP-009, DP-012]

  - id: DP-011
    name: Codex routing (substantive vs coordination)
    category: execution
    status: active
    constitution_rules: []
    youtube_difficulty: beginner
    youtube_length: short
    introduced: 2026-04
    file: patterns/DP-011-codex-routing.md
    related: [DP-009]

  - id: DP-012
    name: Specialist agent matching (domain-aware dispatch)
    category: execution
    status: active
    constitution_rules: []
    youtube_difficulty: intermediate
    youtube_length: medium
    introduced: 2026-04
    file: patterns/DP-012-specialist-agent-matching.md
    related: [DP-009, DP-010]

  - id: DP-013
    name: Hook-as-judiciary (memory is advisory, hooks are law)
    category: enforcement
    status: active
    constitution_rules: []
    youtube_difficulty: intermediate
    youtube_length: long
    introduced: 2026-05
    file: patterns/DP-013-hook-as-judiciary.md
    related: [DP-002, DP-014, DP-015, DP-040]

  - id: DP-014
    name: Hypothesis gate (root-cause record before stopping)
    category: enforcement
    status: active
    constitution_rules: []
    youtube_difficulty: advanced
    youtube_length: medium
    introduced: 2026-05
    file: patterns/DP-014-hypothesis-gate.md
    related: [DP-007, DP-013, DP-015]

  - id: DP-015
    name: TDD cycle gate (fail→edit→pass ordering enforced)
    category: enforcement
    status: active
    constitution_rules: []
    youtube_difficulty: advanced
    youtube_length: medium
    introduced: 2026-05
    file: patterns/DP-015-tdd-cycle-gate.md
    related: [DP-013, DP-019]

  - id: DP-016
    name: Immaculate code protocol (DoD = ruff+pyright+pytest+PM green)
    category: enforcement
    status: active
    constitution_rules: []
    youtube_difficulty: intermediate
    youtube_length: medium
    introduced: 2026-05
    file: patterns/DP-016-immaculate-code-protocol.md
    related: [DP-003, DP-019, DP-020]

  - id: DP-017
    name: Cold-read audit (new-engineer perspective)
    category: quality
    status: active
    constitution_rules: []
    youtube_difficulty: intermediate
    youtube_length: medium
    introduced: 2026-05
    file: patterns/DP-017-cold-read-audit.md
    related: [DP-006, DP-018]

  - id: DP-018
    name: Spec-driven development (spec.md before code)
    category: quality
    status: active
    constitution_rules: []
    youtube_difficulty: beginner
    youtube_length: short
    introduced: 2026-04
    file: patterns/DP-018-spec-driven-dev.md
    related: [DP-020, DP-039]

  - id: DP-019
    name: Test-alongside discipline (SE Principle 13)
    category: quality
    status: active
    constitution_rules: []
    youtube_difficulty: beginner
    youtube_length: short
    introduced: 2026-05
    file: patterns/DP-019-test-alongside.md
    related: [DP-015, DP-016, DP-020]

  - id: DP-020
    name: Definition of Done (NFR checklist)
    category: quality
    status: active
    constitution_rules: []
    youtube_difficulty: beginner
    youtube_length: short
    introduced: 2026-05
    file: patterns/DP-020-definition-of-done.md
    related: [DP-016, DP-019]

  - id: DP-021
    name: Credentials SSoT (.env.shared + sync script)
    category: data-management
    status: active
    constitution_rules: []
    youtube_difficulty: beginner
    youtube_length: short
    introduced: 2026-04
    file: patterns/DP-021-credentials-ssot.md
    related: [DP-029]

  - id: DP-022
    name: pm-registry.json as project identity SSoT
    category: data-management
    status: active
    constitution_rules: []
    youtube_difficulty: intermediate
    youtube_length: short
    introduced: 2026-05
    file: patterns/DP-022-pm-registry-ssot.md
    related: [DP-001, DP-025]

  - id: DP-023
    name: WatchTools manifest.toml per tool
    category: data-management
    status: active
    constitution_rules: []
    youtube_difficulty: advanced
    youtube_length: medium
    introduced: 2026-05
    file: patterns/DP-023-watchtools-manifest.md
    related: [DP-005]

  - id: DP-024
    name: CapabilityWatch 36-capability registry
    category: data-management
    status: active
    constitution_rules: [CAP-KEY-001]
    youtube_difficulty: advanced
    youtube_length: medium
    introduced: 2026-05
    file: patterns/DP-024-capability-registry.md
    related: [DP-004, DP-023]

  - id: DP-025
    name: Project floor (CLAUDE.md + PM + CEO + skills + contracts + SLOs)
    category: project-structure
    status: active
    constitution_rules: []
    youtube_difficulty: intermediate
    youtube_length: medium
    introduced: 2026-04
    file: patterns/DP-025-project-floor.md
    related: [DP-003, DP-020, DP-022]

  - id: DP-026
    name: Shared-libs pattern (no cross-project imports)
    category: project-structure
    status: active
    constitution_rules: []
    youtube_difficulty: beginner
    youtube_length: short
    introduced: 2026-04
    file: patterns/DP-026-shared-libs-boundary.md
    related: [DP-025]

  - id: DP-027
    name: Policy-change ledger (before lowering thresholds)
    category: project-structure
    status: active
    constitution_rules: []
    youtube_difficulty: intermediate
    youtube_length: short
    introduced: 2026-05
    file: patterns/DP-027-policy-change-ledger.md
    related: [DP-002, DP-013]

  - id: DP-028
    name: PHI boundary enforcement (PHIPA/PIPEDA)
    category: security
    status: active
    constitution_rules: [PHI-BND-001, PHI-LOG-001, PHI-EXT-API-001]
    youtube_difficulty: advanced
    youtube_length: long
    introduced: 2026-04
    file: patterns/DP-028-phi-boundary.md
    related: [DP-029, DP-030]

  - id: DP-029
    name: Secrets never in files (Keychain only)
    category: security
    status: active
    constitution_rules: [AUTH-STR-001, AUTH-STR-READ-001]
    youtube_difficulty: intermediate
    youtube_length: short
    introduced: 2026-04
    file: patterns/DP-029-secrets-keychain.md
    related: [DP-021, DP-028]

  - id: DP-030
    name: Add-then-remove migration (DNS, hosting, auth)
    category: security
    status: active
    constitution_rules: []
    youtube_difficulty: intermediate
    youtube_length: medium
    introduced: 2026-04
    file: patterns/DP-030-add-then-remove.md
    related: [DP-028, DP-038]

  - id: DP-031
    name: Session save protocol (/save → Notes + memory + wiki)
    category: workflow
    status: active
    constitution_rules: []
    youtube_difficulty: beginner
    youtube_length: short
    introduced: 2026-04
    file: patterns/DP-031-session-save.md
    related: [DP-033]

  - id: DP-032
    name: Constitution inbox capture pipeline
    category: workflow
    status: active
    constitution_rules: []
    youtube_difficulty: intermediate
    youtube_length: medium
    introduced: 2026-05
    file: patterns/DP-032-constitution-inbox.md
    related: [DP-002, DP-031]

  - id: DP-033
    name: WISC context management (Write→Isolate→Select→Compress)
    category: workflow
    status: active
    constitution_rules: []
    youtube_difficulty: beginner
    youtube_length: short
    introduced: 2026-05
    file: patterns/DP-033-wisc-context-mgmt.md
    related: [DP-031]

  - id: DP-034
    name: Boring technology bias (stable over cutting-edge)
    category: workflow
    status: active
    constitution_rules: []
    youtube_difficulty: beginner
    youtube_length: short
    introduced: 2026-05
    file: patterns/DP-034-boring-tech-bias.md
    related: [DP-018]

  - id: DP-035
    name: Anti-patterns library (AP-001…AP-014)
    category: anti-pattern
    status: active
    constitution_rules: []
    youtube_difficulty: beginner
    youtube_length: long
    introduced: 2026-04
    file: patterns/DP-035-anti-patterns-library.md
    related: [DP-005, DP-013]

  - id: DP-036
    name: Design patterns registry self-registration
    category: meta
    status: active
    constitution_rules: [SPEC-181]
    youtube_difficulty: beginner
    youtube_length: short
    introduced: 2026-05
    file: patterns/DP-036-self-registration.md
    related: [DP-002, DP-037]

  - id: DP-037
    name: YouTube episode derivation from design patterns
    category: meta
    status: active
    constitution_rules: []
    youtube_difficulty: beginner
    youtube_length: short
    introduced: 2026-05
    file: patterns/DP-037-youtube-derivation.md
    related: [DP-036]

  - id: DP-038
    name: Triple Review Protocol (functionality + contradiction + reality)
    category: quality
    status: active
    constitution_rules: []
    youtube_difficulty: intermediate
    youtube_length: medium
    introduced: 2026-04
    file: patterns/DP-038-triple-review.md
    related: [DP-017, DP-030]

  - id: DP-039
    name: Plan/Programmer two-persona split
    category: workflow
    status: active
    constitution_rules: []
    youtube_difficulty: beginner
    youtube_length: short
    introduced: 2026-04
    file: patterns/DP-039-two-persona.md
    related: [DP-018]

  - id: DP-040
    name: Lessons-as-injected-context (lazy load on demand)
    category: enforcement
    status: active
    constitution_rules: []
    youtube_difficulty: advanced
    youtube_length: medium
    introduced: 2026-05
    file: patterns/DP-040-lessons-injection.md
    related: [DP-013, DP-033]
