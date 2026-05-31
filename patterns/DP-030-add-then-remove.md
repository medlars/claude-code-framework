---
id: DP-030
name: Add-then-remove migration (DNS, hosting, auth)
category: security
status: active
constitution-rules: []
youtube-difficulty: intermediate
youtube-episode-length: medium
introduced: 2026-04
---

## What it is

A rule from `~/.claude/CLAUDE.md`:
> "Migrations (DNS, hosting, auth) — add new → verify serves traffic →
> remove old. Never remove working infra first."

For DNS cutovers, hosting migrations, OAuth provider changes, and
similar irreversible operations: deploy the new path alongside the old,
verify the new path actually serves real traffic, then remove the old.

## Rationale — Why We Adopted This Pattern

*The story of how this pattern came to exist and why it was chosen over alternatives.*

### The problem we kept hitting
Migrations went wrong in catastrophic ways. The 2026-04-25 DNS migration
nuked [your-domain.com] mail because the old MX was removed before the new one
was verified. The ICANN compliance email arrived during the cutover and
was missed, auto-suspending the domain for 4 days.

### What we tried first (and why it didn't work)
- **"Move fast"** — moved fast straight off the cliff.
- **Manual checklists** — skipped under time pressure.

### The insight that unlocked the solution
**Always add the new infrastructure first, verify it serves traffic for
24-48 hours, THEN remove the old.** Never remove working infrastructure
first. Treat ICANN compliance emails like a credential rotation:
respond immediately.

### Why this approach, not the obvious one
*Why not just do atomic cutovers?* Because DNS, OAuth, and hosting
changes are not atomic in practice (TTL propagation, cache, intermediary
network issues). Overlap is the only safe path.

### Evidence that it works
- Every DNS, OAuth, and hosting migration since 2026-04-25 followed
  add-then-remove; zero outages.

## Why we use it

Removing first → flapping outage during the brief gap before the new
path is wired correctly. With domains, the gap can be hours (DNS TTL).
With OAuth, the gap can be permanent (revoked refresh tokens). The
add-then-remove pattern always has a working path.

## How it works

**DNS cutover example:**
1. Add new A/CNAME record (e.g. `app.example.com` → new host).
2. Lower TTL on old record.
3. Wait for TTL expiration + propagation (15 min to hours).
4. Curl new host directly via Host header; verify it serves the right
   content.
5. Update DNS to point only to new.
6. Wait an observation window (24-48h).
7. Decommission old host.

**OAuth migration example:**
1. Add second OAuth client to provider.
2. Issue new tokens against new client.
3. Run both old and new in parallel; new path observed in logs.
4. After all clients refreshed, revoke old client.

**Hosting migration example** (FF Cloud Functions → Cloud Run):
1. Deploy new service alongside old.
2. Mirror 5% of traffic via load balancer.
3. Gradually increase to 100%.
4. Decommission old after 7-day observation.

**Triple Review Protocol** (DP-038) is the prerequisite for high-stakes
migrations — read the existing setup before adding anything.

## Example

DNS cutover for `docs.[your-domain.com]` to a new Cloudflare Pages site:

```bash
# Bad
delete-existing-cname docs.[your-domain.com]   # ← outage starts here
add-cname docs.[your-domain.com] → new-target  # ← finish line, but TTL still propagating

# Good
add-cname docs.[your-domain.com].staging → new-target  # parallel
curl -H "Host: docs.[your-domain.com]" https://new-target  # verify
update-cname docs.[your-domain.com] → new-target
# (wait 24h)
remove staging entry
```

## Related patterns

- [DP-028] PHI boundary (cutovers must keep audit unbroken)
- [DP-038] Triple Review Protocol

## YouTube episode angle

- **Tech-savvy** (10-min): "Never remove the working bridge first."
  Walk through DNS, OAuth, and hosting examples. Discuss TTL realities
  and observation windows.
- **Lay audience** (5-min): "Build the new bridge before tearing down
  the old." Use the bridge-replacement analogy literally — close one
  lane, open new, then close old.

## Known failure modes / lessons learned

- Memory entry `feedback_icann_compliance_post_transfer`: 15-day
  ICANN compliance deadline after domain transfer → if missed, domain
  suspends. Treat like a credential rotation; auto-confirm immediately.
- Memory entry `feedback_use_playwright_first`: for migrations
  requiring browser actions, Playwright/Browserbase first; ask user
  only for 2FA.
