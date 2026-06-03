---
id: DP-021
name: Credentials SSoT (.env.shared + sync-credentials.sh)
category: data-management
status: active
constitution-rules: []
youtube-difficulty: beginner
youtube-episode-length: short
introduced: 2026-04
---

## What it is

All API keys and secrets live in **one file**: `~/Projects/.env.shared`.
Editing a key there + running `./sync-credentials.sh --all` propagates
to every project that needs it (FinanceFlow/.env, Verscout/.env,
MoeMoney/.env.upstash, EpicVDI/.env, Moonitor launchd plist, GCE
metadata, etc.). Never edit project `.env` files directly.

## Rationale — Why We Adopted This Pattern

*The story of how this pattern came to exist and why it was chosen over alternatives.*

### The problem we kept hitting
API key rotation was a 30-minute slog: edit 8 different `.env` files,
push to each project, redeploy LaunchAgents, paste into Apps Script
Settings menu, restart daemons. Inevitably one key got missed and a
service broke days later.

### What we tried first (and why it didn't work)
- **Per-project `.env` files** — divergence inevitable; renewals missed.
- **A password manager** — for human access, not service-to-service.
- **Cloud Secret Manager** — added latency, required network calls, didn't
  cover local-only services.

### The insight that unlocked the solution
**Single Source of Truth + propagation script.** `.env.shared` holds
every secret once. `sync-credentials.sh` propagates to 8 targets
(per-project `.env`, Apps Script properties, LaunchAgent plists, GCE
metadata, …) in seconds.

### Why this approach, not the obvious one
*Why not use environment variables in shell rc?* Because they don't
follow a launched daemon, a launchd plist, or a Cloud Function. The
SSoT + sync model meets each service where it lives.

### Evidence that it works
- 2026-04-22 Anthropic key rotation took 2 minutes instead of 30.
- No service has missed a rotation since SSoT rollout.

## Why we use it

Before SSoT: ANTHROPIC_API_KEY existed in 8 places. Rotation meant
finding all 8, editing each, restarting each daemon. Inevitable: missed
copies → silent failures for days.

With SSoT: one edit, one sync, all 8 updated. Rotation is a 30-second
operation, not a 30-minute scavenger hunt.

## How it works

**The sync script (`~/Projects/sync-credentials.sh`):**
- Reads `.env.shared`
- Writes per-target subsets (each project gets only the keys it needs)
- Reloads daemons (launchd unload+load for Moonitor)
- Writes to GCE metadata for cloud-deployed services
- Prints a manual-paste reminder for Apps Script (which can't be
  programmatically updated)

**Per-target mapping** (excerpt from sync script):

| Target | Keys |
|--------|------|
| FinanceFlow/.env | AI keys, ABBYY, Netlify |
| Verscout/.env + web/.env.local | LemonSqueezy, Supabase |
| MoeMoney/.env.upstash | Upstash Redis tokens |
| Moonitor plist | ANTHROPIC_API_KEY (triggers daemon reload) |
| Moonitor GCE | ANTHROPIC_API_KEY (with --gce) |

**Backup:** `~/Projects/backup-env-shared.sh` snapshots `.env.shared` to
a private location before sync; weekly launchd job.

**Hook:** `env-var-sync-gate.sh` (Write+Edit) detects new
`os.environ["KEY"]` calls and warns if `KEY` is missing from `.env.shared`.

## Example

Rotate ANTHROPIC_API_KEY:

```bash
# 1. Get new key from console.anthropic.com
# 2. Edit one file:
vim ~/Projects/.env.shared

# 3. Sync to all targets:
./sync-credentials.sh --all --gce

# 4. Verify:
moonitor status   # daemon reloaded
gcloud functions logs read --limit 5   # GCE metadata picked up

# 5. Revoke old key in Anthropic console
```

Total time: 2 minutes. Pre-SSoT this was 30 minutes + risk of misses.

## Related patterns

- [DP-029] Secrets never in files (Keychain only — stronger form)
- [DP-022] pm-registry.json (sibling SSoT for project identity)

## YouTube episode angle

- **Tech-savvy** (5-min): "One file rotates 8 services." Show the sync
  script, walk through targets, demonstrate a rotation. Discuss why
  `.env.shared` is gitignored and backed up separately.
- **Lay audience** (3-min): "Change the password in one place." Use the
  analogy of a master key system — change the master, all locks update.

## Known failure modes / lessons learned

- Apps Script can't be programmatically updated; sync prints manual
  paste reminder. Don't skip the manual step.
- `.env.shared` must NEVER be committed to git. `git-safety.sh` hook
  blocks adding it.
- ICANN compliance email (per `feedback_icann_compliance_post_transfer`)
  is a sibling problem: 15-day deadline = single-point-of-failure for
  domain. Treat it like a credential rotation.
