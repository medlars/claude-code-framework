---
id: DP-029
name: Secrets never in files (Keychain only)
category: security
status: active
constitution-rules: [AUTH-STR-001, AUTH-STR-READ-001]
youtube-difficulty: intermediate
youtube-episode-length: short
introduced: 2026-04
---

## What it is

Secrets (OAuth tokens, API keys for downstream services, encryption
keys) live in macOS Keychain or platform Secret Manager — never in
files. Even `.env` files are for non-secret config and shared rotated
keys; per-user / per-account credentials go to Keychain.

## Rationale — Why We Adopted This Pattern

*The story of how this pattern came to exist and why it was chosen over alternatives.*

### The problem we kept hitting
Secrets in `.env` files end up committed by accident. Secrets in
`config.json` end up in PR diffs. Secrets in CLAUDE.md end up in the
prompt cache. The variety of "where could this secret end up" is
unbounded.

### What we tried first (and why it didn't work)
- **`.gitignore`** — caught the obvious cases, missed the indirect ones
  (e.g., a backup script that tarred the whole project).
- **Secret-scanning tools (truffleHog, gitleaks)** — post-hoc, after the
  secret was already in a commit.

### The insight that unlocked the solution
**Secrets live only in macOS Keychain, never in files.** AUTH-STR-001
(write) and AUTH-STR-READ-001 (read) hooks enforce it. The .env.shared
pattern (DP-021) is an exception for *propagation* — but `.env.shared`
itself is gitignored and never leaves the local machine.

### Why this approach, not the obvious one
*Why not use Cloud Secret Manager everywhere?* Because (a) network
dependence for local dev, (b) cost, (c) macOS Keychain provides Touch
ID-gated access for free.

### Evidence that it works
- LESSONS 013: `-T ""` keychain ACL lockout — discovered because we use
  Keychain; secrets-in-files codebases would never have hit this and
  would never have learned the lesson.

## Why we use it

A leaked `.env` is a leaked secret. A leaked file commit is a leaked
secret. Keychain provides:
- OS-level access control (per-app entitlements)
- Encryption at rest
- No "oops, committed it" failure mode

## How it works

**Storage:**
```bash
security add-generic-password \
  -a $USER \
  -s "myapp-imap-[your-username]-gmail" \
  -w "$IMAP_TOKEN"
```

**Retrieval:**
```python
import subprocess
def get_keychain_secret(service: str) -> str:
    result = subprocess.run(
        ["security", "find-generic-password", "-s", service, "-w"],
        capture_output=True, text=True, check=True,
    )
    return result.stdout.strip()
```

**Hooks:**
- `secrets-in-content.sh` (PostToolUse) — detects token-shaped strings
  in written content.
- `block-keychain-dump.sh` (PreToolUse:Bash) — blocks
  `security dump-keychain`.

**Per-account isolation:** <SagaMail>'s 40-account architecture uses one
Keychain item per account; never a single multi-account secrets file.

## Example

OAuth refresh token for Gmail account `[your-email@example.com]`:

```bash
# Store
security add-generic-password \
  -a [your-email@example.com] \
  -s "sagamail-gmail-oauth-refresh" \
  -w "$REFRESH_TOKEN"

# Retrieve
TOKEN=$(security find-generic-password \
  -a [your-email@example.com] \
  -s "sagamail-gmail-oauth-refresh" -w)
```

## Related patterns

- [DP-021] Credentials SSoT (rotated keys, not per-account secrets)
- [DP-028] PHI boundary

## YouTube episode angle

- **Tech-savvy** (5-min): "Why every token belongs in Keychain." Show
  the secrets-in-content hook blocking a write. Compare to .env-only
  approaches and their failure modes.
- **Lay audience** (3-min): "Keys go in the safe, not the kitchen
  drawer." Use the analogy of a hotel safe vs leaving keys on the
  nightstand.

## Known failure modes / lessons learned

- LESSONS 013: `-T ""` flag in `security add-generic-password` causes
  keychain ACL lock to an ephemeral ad-hoc identity → every new build
  fails. Never use `-T ""`.
- LESSONS 060: Same issue in Verscout — caused keychain reads to fail.
- macOS 26 + <EmailManager>: Apple Mail-style apps need per-account
  storage; one item per (account_id, scope) tuple.
- `security dump-keychain` is banned (would dump all secrets to text).
