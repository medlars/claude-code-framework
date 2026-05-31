---
id: DP-038
name: Triple Review Protocol (functionality + contradiction + reality)
category: quality
status: active
constitution-rules: []
youtube-difficulty: intermediate
youtube-episode-length: medium
introduced: 2026-04
---

## What it is

A protocol from `~/.claude/CLAUDE.md`:
> "Triple Review Protocol — required for all infra/service/capability
> answers:
> 1. Functionality: covers ALL functions? Show gaps.
> 2. Contradiction: conflicts with existing setup?
> 3. User's reality: what's already configured? Check tools, don't
>    assume."

Origin: 2026-04-14, after 5 wrong email-infrastructure claims caused
contradictory systems to be set up.

## Rationale — Why We Adopted This Pattern

*The story of how this pattern came to exist and why it was chosen over alternatives.*

### The problem we kept hitting
2026-04-14 incident: Claude made 5 wrong email-infrastructure claims in
one session, set up contradictory mail systems, and the owner had to
roll back the mess. Self-review by the same model produced the same
errors twice.

### What we tried first (and why it didn't work)
- **Asking "are you sure?"** — model said yes confidently each time.
- **Adding more detail to the prompt** — increased verbosity, not
  accuracy.

### The insight that unlocked the solution
**Three independent reviews before acting on high-stakes infra answers.**
(1) Functionality: does this cover all required functions? (2)
Contradiction: does this conflict with the existing setup? (3) Reality:
what is *actually* configured right now (check tools, don't assume).

### Why this approach, not the obvious one
*Why not just use a checklist?* The Triple Review *is* a checklist, but
each pass uses different evidence (spec, codebase, runtime state).
Three angles catch what one would miss.

### Evidence that it works
- Since rollout, no contradictory infra setup has shipped.
- High-stakes changes (DNS, billing, auth, hosting) now require Triple
  Review *and* a Codex verification agent.

## Why we use it

Single-pass answers are often plausible-but-wrong because the model
fills gaps with assumptions. Triple Review forces three different
modes: completeness check, conflict check, ground-truth check.

For high-stakes changes (email, DNS, hosting, auth): spawn a Codex
verification agent before executing. Self-review is insufficient.

## How it works

**Three passes:**

**1. Functionality check** — list every function the proposed change
needs to cover. Any uncovered? Surface gaps explicitly.

**2. Contradiction check** — read existing config / running services /
DNS / etc. Does the proposal conflict with what's already there?

**3. Reality check** — use Read/Grep/Bash to verify ground truth.
Don't assume; tools are cheap, wrong infra is expensive.

**Enforcement:**
- `infrastructure-triple-review.sh` PreToolUse:Bash hook intercepts
  DNS/email/hosting commands and requires the three-pass record.
- `infrastructure-contradiction-check.sh` PostToolUse looks for
  conflicting commands in session history.

**Codex verification agent:** for high-stakes changes, spawn:
```
Task(subagent_type="codex:codex-rescue",
     prompt="Verify this DNS plan against current Cloudflare zone:
             [plan]. Report any contradictions.")
```

## Example

User asks: "Set up DMARC for [your-domain.com]."

Without triple review: model writes a generic DMARC record, applies it,
breaks existing email forwarding because it didn't check that an SPF
include from a third-party was already there.

With triple review:
1. **Functionality**: covers DMARC alignment, reporting URI, policy
   level → yes.
2. **Contradiction**: queries existing DNS → finds existing
   `v=spf1 include:third-party.example -all` from Workspace.
3. **Reality**: existing DMARC at `_dmarc.[your-domain.com]` is `p=none` (in
   monitoring mode) → preserve the rua/ruf addresses; tighten policy
   only after observation window.

Plan accepted. No breakage.

## Related patterns

- [DP-006] 9-dim cold-read audit (larger sibling)
- [DP-017] Cold-read audit
- [DP-030] Add-then-remove migration

## YouTube episode angle

- **Tech-savvy** (10-min): "Why I review my AI's plans three times."
  Walk through the 2026-04-14 email incident. Show the hook firing.
- **Lay audience** (5-min): "Measure twice, cut once — then check the
  measuring tape." Add the third check that catches what the first
  two missed.

## Known failure modes / lessons learned

- Origin incident (2026-04-14): 5 wrong claims, contradictory email
  systems set up. Protocol was the response.
- LESSONS: For familiar territory the protocol is overkill; reserve
  for infra/auth/billing/DNS.
