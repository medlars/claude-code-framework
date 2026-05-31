# YouTube Episode Seeds — [Your Company] Channel

> Source: every pattern in `~/Projects/shared/design-patterns/patterns/`
> seeds at least one episode. 40+ episode candidates below — one or more
> per DP-NNN pattern.
> Channel theme: "How a solo physician runs a software fleet with Claude Code."
>
> Each entry: Title · Patterns covered · Audience · Duration · Hook · 3 takeaways.

---

## Series 1: Governance (the supervisor stack)

### EP-01: "I built a foreman, a CEO, and a court clerk for my code"
- **Patterns**: DP-001, DP-007
- **Audience**: intermediate
- **Duration**: 15 min
- **Hook**: Most solo developers ship code with no oversight. I built three layers of automated supervision and it changed everything.
- **Takeaways**:
  - PM script per project = local quality foreman.
  - CEO script = cross-project consistency enforcer.
  - CIS = durable bug ledger that survives sessions.

### EP-02: "555 rules. Zero of them in your head."
- **Patterns**: DP-002, DP-032
- **Audience**: intermediate
- **Duration**: 15 min
- **Hook**: Your CLAUDE.md is lying to you. Here's how I built a queryable, auditable rule registry that the AI can't drift from.
- **Takeaways**:
  - Markdown rules drift; SQLite rules don't.
  - 555 rules, 135 active, all backed by hooks.
  - Inbox capture turns "always do X" into a tracked rule.

### EP-03: "Every project speaks the same dialect (and why that matters)"
- **Patterns**: DP-003, DP-004, DP-022
- **Audience**: advanced
- **Duration**: 20 min
- **Hook**: 81 projects, one PM contract. Here's the 14-part structure every project must follow.
- **Takeaways**:
  - PM contract = uniform black box.
  - CEO propagation prevents drift.
  - Canonical names via pm-registry.json.

### EP-04: "Bug in one project? Fix it in all 81."
- **Patterns**: DP-004
- **Audience**: advanced
- **Duration**: 12 min
- **Hook**: A fix landed in <FinanceFlow>. Six weeks later the same bug bit <MoeMoney> in production. Here's the propagation system that stopped that forever.
- **Takeaways**:
  - PROPAGATION_PATTERNS in `ceo.py` enumerate cross-PM patterns.
  - `--propagation-check` surfaces missing siblings without acting.
  - Auto-propagation is gated by worktree + PM green.

---

## Series 2: Detection (the inspector fleet)

### EP-05: "69 robots inspect my code 24/7"
- **Patterns**: DP-005, DP-008, DP-023
- **Audience**: intermediate
- **Duration**: 15 min
- **Hook**: I never repeat the same bug fleet-wide because the first instance becomes a detector.
- **Takeaways**:
  - Detector-gap pattern: bug → detector → prevention.
  - 69 WatchTools, 250+ rule IDs.
  - SilentFailureWatch: the bug that always says "passed".

### EP-06: "How I find bugs in my own code"
- **Patterns**: DP-006, DP-017
- **Audience**: advanced
- **Duration**: 25 min
- **Hook**: I audited 81 projects in 24 hours and found 2,624 issues. Here's the 9-dimension checklist I used.
- **Takeaways**:
  - Cold-read = read as a stranger.
  - 9 dimensions cover build, test, types, data, errors, security, ops, observability, doc drift.
  - 80+ P0 fixes flowed from one sweep.

### EP-07: "Every bug has a paper trail"
- **Patterns**: DP-007
- **Audience**: intermediate
- **Duration**: 10 min
- **Hook**: I never lose a bug report because every finding gets a stable ID, severity, and lifecycle.
- **Takeaways**:
  - One SQLite DB for the entire fleet's findings.
  - Canonical project names prevent dead-letter bugs.
  - PM stages query CIS, fail on open P0s.

### EP-08: "The bug that always says 'passed'"
- **Patterns**: DP-008
- **Audience**: intermediate
- **Duration**: 8 min
- **Hook**: My pipeline was green. My production was on fire. Here's the detector that catches the bug class behind both.
- **Takeaways**:
  - `except Exception: pass` is the most expensive line of Python.
  - Three rule IDs cover ~95% of the surface.
  - `# pragma: silent-ok` documents intentional silence.

### EP-09: "How each detector earns its keep"
- **Patterns**: DP-023
- **Audience**: advanced
- **Duration**: 12 min
- **Hook**: Each of my 69 inspectors carries a config card. Here's why uniform tools beat one-off scripts.
- **Takeaways**:
  - `manifest.toml` per WatchTool.
  - One driver runs all 69.
  - New detector ships in <30 min.

---

## Series 3: Execution (delegation > inline)

### EP-10: "Why I never edit code inline anymore"
- **Patterns**: DP-009, DP-010, DP-011
- **Audience**: beginner
- **Duration**: 10 min
- **Hook**: My orchestrator gets dumber the more it does. So I made it stop doing anything itself.
- **Takeaways**:
  - Subagent-driven is the default, not the exception.
  - Parallel agent dispatch saves wall-clock time.
  - Codex for substantive work; Claude coordinates.

### EP-11: "24 specialists on call"
- **Patterns**: DP-012
- **Audience**: intermediate
- **Duration**: 12 min
- **Hook**: A generalist AI keeps re-deriving context. I built 24 specialists pre-loaded with domain knowledge.
- **Takeaways**:
  - Trigger maps route work deterministically.
  - Familiarity-based delegation rules.
  - METR 19%-slower-on-familiar-code finding.

### EP-12: "Four agents in parallel saved me 9 minutes per push"
- **Patterns**: DP-010
- **Audience**: intermediate
- **Duration**: 8 min
- **Hook**: Sequential subagent calls are linear cost. One Task tool block runs them all at once.
- **Takeaways**:
  - Batch agents with no inter-dependencies.
  - Pre-push audit: serial 12 min → parallel 4 min.
  - The trigger is "I have N independent checks".

### EP-13: "Why I send substantive work to Codex"
- **Patterns**: DP-011
- **Audience**: beginner
- **Duration**: 7 min
- **Hook**: I cut my Anthropic usage by 70% without shipping less. Here's the routing rule that did it.
- **Takeaways**:
  - Claude = judgement; Codex = throughput.
  - 3+ files or 200+ lines → Codex.
  - The 1M context window matters more than you think.

---

## Series 4: Enforcement (hooks are law)

### EP-14: "Memory without a hook is a wish"
- **Patterns**: DP-013, DP-040
- **Audience**: intermediate
- **Duration**: 15 min
- **Hook**: I told my AI "don't do X" and it did X anyway. Then I wrote a shell hook and it stopped.
- **Takeaways**:
  - Memory = advisory; hook = law.
  - 180 hooks in this fleet.
  - Lazy lesson injection saves tokens.

### EP-15: "Every fix needs a why"
- **Patterns**: DP-014, DP-015
- **Audience**: advanced
- **Duration**: 15 min
- **Hook**: Tests pass — but does anybody know WHY they pass? My Stop hook makes you write it down.
- **Takeaways**:
  - Hypothesis gate before Stop.
  - TDD cycle enforced: fail → edit → pass.
  - Without a hypothesis, "fixed it" is fragile.

### EP-16: "Done means all four: ruff, pyright, pytest, PM"
- **Patterns**: DP-016, DP-020
- **Audience**: intermediate
- **Duration**: 12 min
- **Hook**: "Tests pass" is the lower bound, not the bar. Here are the four gates that define "done" in my fleet.
- **Takeaways**:
  - PM grade is the integrated quality score.
  - NFRs (a11y, perf, i18n, secrets) baked into DoD.
  - Last-20% rule: retry + logging + validation.

### EP-17: "I made my AI write down the why before stopping"
- **Patterns**: DP-014
- **Audience**: advanced
- **Duration**: 10 min
- **Hook**: 'Fixed it!' with no explanation was costing me. So I built a Stop-level hook that demands a hypothesis.
- **Takeaways**:
  - Post-hoc explanations are rationalizations.
  - The hypothesis must be written while context is warm.
  - Bugs that previously came back twice rarely come back once.

### EP-18: "TDD that actually works (because a hook enforces ordering)"
- **Patterns**: DP-015
- **Audience**: advanced
- **Duration**: 10 min
- **Hook**: 'TDD' in name only is everywhere. Here's the hook that enforces the cycle ordering, not just the artifacts.
- **Takeaways**:
  - Honor-system TDD never works at scale.
  - The gate records each test execution.
  - Git can't see what came before what.

---

## Series 5: Quality (process discipline)

### EP-19: "Cold-read your own code"
- **Patterns**: DP-017
- **Audience**: intermediate
- **Duration**: 10 min
- **Hook**: I tried shipping something trivial pretending I'd never seen the project. Found 30 doc gaps in 10 minutes.
- **Takeaways**:
  - The author is too close to their own code.
  - Every assumption surfaced is a comment debt repaid.
  - Audit skills bake the cold-read prompt in.

### EP-20: "Why I write the spec twice"
- **Patterns**: DP-018, DP-039
- **Audience**: beginner
- **Duration**: 8 min
- **Hook**: 60 minutes of planning saves 23 hours of debugging. The numbers came from real sessions.
- **Takeaways**:
  - Spec sections: problem, goals, non-goals, design, tests, rollback.
  - PM persona vs Programmer persona.
  - Plan mode (Shift+Tab) is free thinking.

### EP-21: "Tests in the same session or never"
- **Patterns**: DP-019
- **Audience**: beginner
- **Duration**: 7 min
- **Hook**: "I'll add tests later" never happens. So I made my hook block Stop until I do.
- **Takeaways**:
  - SE Principle 13: test-alongside.
  - PostToolUse hook catches the violation.
  - TestWatch surfaces fleet-wide gaps.

### EP-22: "Why I review my AI's plans three times"
- **Patterns**: DP-038
- **Audience**: intermediate
- **Duration**: 12 min
- **Hook**: An infra change went wrong five times in one session. Here's the protocol I built so it can't happen again.
- **Takeaways**:
  - Functionality + Contradiction + Reality.
  - Triple Review for DNS, email, auth, hosting.
  - Codex verification agent for high-stakes changes.

### EP-23: "NFRs as gates, not nice-to-haves"
- **Patterns**: DP-020
- **Audience**: beginner
- **Duration**: 7 min
- **Hook**: 'Done' used to mean tests pass. Now it means tests + a11y + logging + validation + retry.
- **Takeaways**:
  - The last-20% checklist.
  - Last20 hook surfaces the gap.
  - DoD = the actual contract, not aspirational.

---

## Series 6: Data, structure, security

### EP-24: "One file rotates 8 services"
- **Patterns**: DP-021, DP-029
- **Audience**: beginner
- **Duration**: 8 min
- **Hook**: API key rotation used to take me 30 minutes. Now it takes 2.
- **Takeaways**:
  - Credentials SSoT pattern.
  - Keychain for per-account secrets.
  - Never commit `.env.shared`.

### EP-25: "Every project must have these 36 things"
- **Patterns**: DP-024, DP-025
- **Audience**: intermediate
- **Duration**: 15 min
- **Hook**: The project floor codified. CapabilityWatch turns "should have" into a measurable grid.
- **Takeaways**:
  - 36 capabilities, 27 projects, green/red matrix.
  - Auto-propagation behind worktree+PM gate.
  - project-forge scaffolds floor-compliant from day zero.

### EP-26: "Independence via shared-libs"
- **Patterns**: DP-026
- **Audience**: beginner
- **Duration**: 7 min
- **Hook**: Cross-project imports created hidden coupling. Now they're banned.
- **Takeaways**:
  - shared-libs/ is the only legal share path.
  - BoundaryWatch BW001 enforces.
  - Breaking changes to shared-libs trigger fleet-wide test.

### EP-27: "Project identity in one JSON file"
- **Patterns**: DP-022
- **Audience**: intermediate
- **Duration**: 6 min
- **Hook**: '<FinanceFlow>', 'financeflow', 'finance-flow', and 'ff' were four different projects in my CIS. Until I built the canonical-name SSoT.
- **Takeaways**:
  - One JSON file holds canonical, aliases, root, PM path.
  - `project_resolver.py` is the choke-point.
  - `check.py <any-spelling> --quick` just works.

### EP-28: "Patient privacy without trusting humans"
- **Patterns**: DP-028
- **Audience**: advanced
- **Duration**: 25 min
- **Hook**: I'm a doctor. PHI leaks would end my career. Here's how I made privacy a mechanical property of my code.
- **Takeaways**:
  - PHIWatch rule IDs.
  - 18-identifier de-identification pipeline.
  - Local Llama for PHI-touching LLM work — never cloud APIs.

### EP-29: "Secrets never live in files"
- **Patterns**: DP-029
- **Audience**: intermediate
- **Duration**: 8 min
- **Hook**: A leaked `.env` is one git push away. So I moved all my secrets to Keychain — and built hooks to enforce it.
- **Takeaways**:
  - macOS Keychain over `.env` everywhere possible.
  - Two hooks: write-side and read-side.
  - Touch ID-gated access is free.

### EP-30: "Never tear down the working bridge first"
- **Patterns**: DP-030
- **Audience**: intermediate
- **Duration**: 12 min
- **Hook**: I once nuked DNS during a migration. Now there's a rule: add new, verify, remove old.
- **Takeaways**:
  - Add-then-remove for DNS, OAuth, hosting.
  - 24-48h observation window before decommission.
  - Treat ICANN compliance email like a credential rotation.

---

## Series 7: Workflow, anti-patterns, and meta

### EP-31: "Don't lower the bar without saying why"
- **Patterns**: DP-027
- **Audience**: intermediate
- **Duration**: 8 min
- **Hook**: Quality thresholds drift downward silently. My hook makes you write down the why before lowering anything.
- **Takeaways**:
  - policy-changes.md ledger.
  - Hook intercepts COVERAGE_FLOOR / GRADE_FLOOR / MIN_* changes.
  - Re-raise date required.

### EP-32: "Don't let the day disappear"
- **Patterns**: DP-031, DP-033
- **Audience**: beginner
- **Duration**: 8 min
- **Hook**: A long session is dense. Here's how I capture every one into permanent record without losing context.
- **Takeaways**:
  - /save → Apple Notes + memory + wiki.
  - WISC: Write, Isolate, Select, Compress.
  - Rename gate prevents invented names.

### EP-33: "Why I use boring tech"
- **Patterns**: DP-034
- **Audience**: beginner
- **Duration**: 8 min
- **Hook**: Novel frameworks make my AI hallucinate APIs. Boring ones don't. Here's why I pick the 20-year-old tool.
- **Takeaways**:
  - LLM training data depth = correctness on first shot.
  - Fleet stack: Python 3.14, Astro 6, Swift 6.3, Postgres, Redis.
  - Novelty has a correctness tax.

### EP-34: "14 mistakes I will never make again"
- **Patterns**: DP-035
- **Audience**: beginner
- **Duration**: 25 min
- **Hook**: Every entry in my anti-patterns library is a war story. Here are all 14.
- **Takeaways**:
  - Append-only library of cross-project failure modes.
  - Each AP gets a hook to prevent recurrence.
  - Tags enable fast lookup.

### EP-35: "How I made my pattern library a pattern"
- **Patterns**: DP-036, DP-037
- **Audience**: beginner
- **Duration**: 7 min
- **Hook**: This very registry is a design pattern. Recursive registration, machine-readable, video-script ready.
- **Takeaways**:
  - Registration protocol for new patterns.
  - YouTube angles baked into every pattern file.
  - INDEX.md for machine consumption.

### EP-36: "Anatomy of a context-rotted session (and how to prevent it)"
- **Patterns**: DP-033
- **Audience**: beginner
- **Duration**: 9 min
- **Hook**: Long sessions degrade in quality long before they hit the context limit. Here's the prune-as-you-go technique that fixes it.
- **Takeaways**:
  - Signs: stale file refs, re-solved problems, contradictions.
  - WISC > /compact.
  - Do it before quality drops.

### EP-37: "/save: the one-keystroke session journal"
- **Patterns**: DP-031
- **Audience**: beginner
- **Duration**: 6 min
- **Hook**: I never lose a session because the workflow that captures one takes ten seconds.
- **Takeaways**:
  - Apple Notes for cross-device search.
  - Memory file for next-session injection.
  - Rename gate prevents invented names.

### EP-38: "Don't let the cache forget your rules"
- **Patterns**: DP-032
- **Audience**: intermediate
- **Duration**: 8 min
- **Hook**: Adding a rule to CLAUDE.md kills your prompt cache. So I built a JSON inbox that captures rules mid-session without disrupting anything.
- **Takeaways**:
  - JSON drop → proposed rule.
  - Human triage prevents cruft.
  - Cache stays warm.

### EP-39: "Lazy-load 101 lessons without paying for them upfront"
- **Patterns**: DP-040
- **Audience**: advanced
- **Duration**: 10 min
- **Hook**: My LESSONS.md is 4,000 tokens. My LESSONS-INDEX.md is 1,100. I only load the full lesson when a task needs it.
- **Takeaways**:
  - Two-tier injection: cheap index always, full lesson on demand.
  - PostToolUse hook regenerates the index.
  - Cache hit rate way up.

### EP-40: "Two personas, one keyboard"
- **Patterns**: DP-039
- **Audience**: beginner
- **Duration**: 6 min
- **Hook**: When I'm planning, I'm the PM. When I'm executing, I'm the Programmer. Same chat, different mode.
- **Takeaways**:
  - PM produces deeply researched modular plans.
  - Programmer executes with the wisest proven approach.
  - Explicit mode-switch reduces accidental ships.

---

## Production pipeline

For each episode:

1. Open the listed pattern files; the **"YouTube episode angle"** section
   is your outline (tech-savvy + lay angle).
2. Record 10-15 min for intermediate/advanced; 5-8 min for beginner.
3. Description: link `~/Projects/shared/design-patterns/patterns/DP-NNN-*.md`
   for viewers who want depth.
4. After recording: add `produced: YYYY-MM-DD` and `url: ...` to the
   episode entry above.

## Difficulty distribution

- **Beginner** (16): EP-10, EP-13, EP-20, EP-21, EP-23, EP-24, EP-26, EP-32, EP-33, EP-34, EP-35, EP-36, EP-37, EP-40
- **Intermediate** (16): EP-01, EP-02, EP-05, EP-07, EP-08, EP-11, EP-12, EP-14, EP-16, EP-19, EP-22, EP-25, EP-27, EP-29, EP-30, EP-31, EP-38
- **Advanced** (8): EP-03, EP-04, EP-06, EP-09, EP-15, EP-17, EP-18, EP-28, EP-39

## Duration distribution

- **Short** (5-10 min): EP-04 area through EP-40 mostly — high cadence
- **Medium** (12-15 min): bigger architectural deep-dives
- **Long** (20-25 min): EP-03, EP-06, EP-28, EP-34 — the canonical
  walkthroughs

## Coverage check

Every pattern DP-001 through DP-040 appears in at least one seed above
(verify with `grep -E 'DP-[0-9]{3}' episode-seeds.md | sort -u | wc -l`
should equal 40).
