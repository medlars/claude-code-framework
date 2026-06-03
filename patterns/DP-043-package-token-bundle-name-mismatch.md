---
id: DP-043
name: Assumption of Name Equivalence Between Package Manager Token
category: detection
status: active
constitution-rules: []
youtube-difficulty: intermediate
youtube-episode-length: short
introduced: 2026-05
---

## What it is

A detection pattern that identifies code paths which silently assume a package manager token (e.g., a Homebrew cask name) maps 1-to-1 onto the real artifact name on disk (e.g., a `.app` bundle name), and code paths that treat a cached installation-state snapshot as perpetually valid after a mutation event such as an upgrade.

## Rationale

### The problem

Package manager tokens are slugs chosen for registry uniqueness and URL safety. They bear no contractual relationship to the name the installed artifact presents to the host OS. When code constructs a filesystem path or a shell invocation by concatenating a token directly—`open -a <cask-token>`—it fails silently or with a misleading error whenever the vendor chose a different bundle name. The same class of mistake appears in version caches: after `brew upgrade` runs, the cached installed-version record is stale, so the next scan compares the live app against an old cache entry and raises a false-positive outdated alert.

Both failures share a root: the code treats a symbolic identifier as a ground-truth artifact descriptor without revalidating it against the real artifact.

### The insight

A package manager token is an opaque registry key, not a filesystem name. Any code that uses a token as though it were a name is making an undeclared assumption. That assumption must be made explicit—by a lookup table, a metadata query, or a post-mutation cache-invalidation step—before the token is used in a context that requires the real name.

### Evidence

- `microsoft-teams` (cask token) installs as `Microsoft Teams.app`, not `microsoft-teams.app`. An `open -a microsoft-teams` call fails with "Application not found."
- `google-chrome` installs as `Google Chrome.app`; the capitalization and space alone break naive path construction.
- Post-upgrade rescans that read a warm version cache re-flag freshly updated applications as outdated until the cache TTL expires or is manually cleared.

## Why we use it

- Eliminates a class of false-positive outdated-app alerts that erode user trust in scan results.
- Prevents silent failures in automation that launches applications by cask token.
- Makes the implicit token-to-name contract explicit and auditable, reducing the surface area for future regressions when vendors rename bundles.
- The fix is low-cost once the pattern is recognized: a single metadata lookup or a cache-invalidation hook prevents the entire failure class.

## How it works

1. **Token resolution step.** Whenever a cask token must be used in a filesystem or shell context, resolve it to its canonical artifact name first. Use `brew info --json=v2 <token>` or the equivalent metadata API; extract the `artifacts` array to find the actual `.app` bundle name. Cache this resolved name alongside the token, not instead of it.

2. **Mutation-aware cache invalidation.** Treat the installed-version cache as invalidated for any package that was touched by an install, upgrade, or uninstall operation during the current session. Invalidation must occur before the next scan cycle reads from the cache, not after.

3. **Assertion at the call site.** At every site that passes a name to an OS-level API (`open -a`, `mdfind`, `osascript`, path construction), assert that the value was produced by the resolution step, not by direct token forwarding. A type alias or wrapper function can enforce this structurally.

4. **Test coverage.** Include at least one test fixture where the cask token and the bundle name differ. This prevents regression—the microsoft-teams case is a permanent good fixture because the divergence is intentional and stable.

## Example

**Before — assumes equivalence:**

A scan loop builds the launch command as `open -a microsoft-teams`. The post-upgrade version cache still holds `21.x` after the system is updated to `24.x`. The app fails to open; the next scan reports the app as outdated.

**After — explicit resolution:**

The scan loop calls the metadata API for `microsoft-teams`, receives `Microsoft Teams` as the bundle name, and stores the pair `{token: "microsoft-teams", bundle_name: "Microsoft Teams"}`. The launch command becomes `open -a "Microsoft Teams"`. When the upgrade event fires, the cache entry keyed on `microsoft-teams` is explicitly deleted before the next scan reads it. The scan then queries the live app bundle for its version string and compares it against the registry—no false positive.

## Related patterns

- **DP-011 — Stale Cache After Mutation** — covers the general case of cache invalidation following write operations; DP-043 is a specific instance scoped to package manager state.
- **DP-027 — Implicit Identity Assumption** — addresses the broader problem of using one identifier class in a context that requires a different identity class.
- **DP-038 — Silent Failure on Missing Artifact** — describes how `open -a` and similar APIs fail without raising exceptions, making the name-equivalence assumption particularly hard to detect in production.

## Known failure modes

- **Metadata API unavailability.** If `brew info` is unavailable (offline, corrupted install), the resolution step fails. The code must decide whether to fall back to the token (accepting possible failure) or to abort the operation and surface an explicit error. Silently falling back to the token defeats the purpose of the pattern.
- **Multi-artifact casks.** Some casks install more than one `.app` bundle. The resolution step must handle a list, not a scalar, and the call site must specify which artifact it intends to reference.
- **Vendor renames.** A vendor can rename the `.app` bundle in a new version. The resolved bundle name must be re-fetched after an upgrade, not read from a pre-upgrade cache entry. This is an intersection with the mutation-aware invalidation step; both must be applied together.
- **Token reuse across package managers.** A Homebrew cask token and an npm package name can be identical strings with no relationship. Code that operates across multiple package managers must namespace its resolution cache by package manager to avoid cross-contamination.