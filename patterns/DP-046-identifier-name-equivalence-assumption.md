---
id: DP-046
name: Assumption of Identity Equivalence Between Identifier and Re
category: anti-pattern
status: proposed
constitution-rules: []
youtube-difficulty: intermediate
youtube-episode-length: short
introduced: 2026-05
---

## What it is

The Assumption of Identity Equivalence Between Identifier and Resource is an anti-pattern in which a system treats a resource's symbolic identifier—such as a package token, slug, or registry key—as if it were structurally identical to every derived name or path the resource carries at runtime. The system skips the lookup step that would resolve the identifier to the resource's actual name and instead substitutes the identifier directly wherever the real name is required.

## Rationale

### The problem

Software that manages installed applications frequently must bridge two distinct namespaces: the canonical identifier space controlled by the registry or package manager, and the filesystem or OS namespace that reflects how the resource actually materialised on disk. These namespaces are related but not equivalent. A cask token such as `microsoft-teams` is a human-readable, URL-safe handle chosen by the package maintainer; the `.app` bundle that the installer places on disk is named `Microsoft Teams.app`, a string governed by Apple's bundle conventions and the upstream vendor's own choices.

When code that opens an application calls `open -a <cask-token>` it passes the token directly to the macOS launch subsystem, which performs a case-sensitive, space-sensitive match against bundle display names. The token does not match, so the command fails silently or with a misleading error. The same class of mistake appears in cache invalidation: if a post-update routine clears or refreshes installed-version records by keying on the token rather than querying the actual installed bundle, cached stale entries survive the update. On the next scan cycle, the cache still reports the old version, causing the application to be flagged as outdated immediately after a successful update.

### The insight

An identifier is a *reference* to a resource, not a *projection* of it. Any attribute of a resource that is not guaranteed by the identifier's own specification—display name, filesystem path, version string, bundle ID—must be resolved through an authoritative lookup before use. Conflating reference and projection is safe only within a closed system where the registry controls both the identifier format and every derived attribute. In practice such closure is rare; most useful systems bridge at least two namespaces with independent naming conventions.

### Evidence

Two concrete failure modes document this pattern in production use:

1. `open -a microsoft-teams` fails because the macOS `open` command matches against `CFBundleName` or the Finder display name, neither of which is derived from the Homebrew cask token. The resolution is to query `brew info --json=v2 microsoft-teams` for the `artifacts` field, extract the `.app` bundle name, and pass that name to `open -a`.

2. A post-update version cache keyed on the cask token retains the pre-update version record when the invalidation routine compares token strings rather than querying the installed bundle's `CFBundleShortVersionString` directly from the `.app` on disk. Subsequent scans re-flag the app as outdated until the cache TTL expires or a full cache flush is triggered manually.

## Why we use it

This document catalogues the anti-pattern so that engineers can recognise the telltale structure—an identifier being used verbatim in a context that requires a resolved attribute—before writing or reviewing code that crosses namespace boundaries. Naming the pattern gives reviewers a shared vocabulary for rejection comments and gives authors a concrete checklist item: *have I resolved this identifier to the actual resource attribute this context requires?*

## How it works

The anti-pattern manifests through the following mechanism:

1. A registry or package manager assigns an identifier (`cask-token`, slug, ID) to a resource.
2. Code downstream of the registry needs an attribute of the resource that exists in a different namespace (filesystem path, display name, version string).
3. The code uses the identifier as a direct substitute for that attribute without performing a lookup.
4. The target system receives the identifier in a context where it expects the resolved attribute, and either fails, returns a wrong result, or silently operates on the wrong resource.
5. Caches or derived state that should have been invalidated after a mutating operation are keyed on the identifier, so they survive changes that alter only the resolved attribute.

The corrective structure requires an explicit resolution step between receiving an identifier and consuming a derived attribute. The resolution step must be:

- **Authoritative**: it queries the system that owns the target namespace (the OS, the filesystem, the bundle manifest).
- **Fresh**: it is performed after any operation that may have changed the resolved value, not served from a pre-mutation cache.
- **Scoped**: the resolved value is not promoted back to the identifier's role; it is used only in the context that requires it and discarded thereafter.

## Example

**Broken flow — identity equivalence assumed**

```
user requests open microsoft-teams
  → run: open -a microsoft-teams
  → macOS: no application named "microsoft-teams" found
  → error
```

```
brew upgrade microsoft-teams completes
  → cache entry: { token: "microsoft-teams", version: "1.0.0" } remains
  → next scan: installed version "1.0.0" < latest "2.0.0" → flagged outdated
  → user sees false positive
```

**Corrected flow — explicit resolution**

```
user requests open microsoft-teams
  → query: brew info --json=v2 microsoft-teams
  → extract artifact: "Microsoft Teams.app"
  → run: open -a "Microsoft Teams.app"
  → macOS: match found, application launched
```

```
brew upgrade microsoft-teams completes
  → invalidate cache entry for token "microsoft-teams"
  → next scan: read CFBundleShortVersionString from /Applications/Microsoft Teams.app
  → cache populated with resolved version "2.0.0"
  → no false positive
```

## Related patterns

- **DP-017 Leaky Abstraction at Namespace Boundary** — describes the broader failure mode of allowing one namespace's conventions to bleed into another; DP-046 is a specific instance where the leaked assumption is strict name equality.
- **DP-029 Stale Cache After Mutation** — covers cache invalidation failures generally; DP-046 names the root cause of one common class of such failures: the cache key does not change when the resolved attribute changes because the key is the identifier, not the attribute.
- **DP-061 Implicit Canonical Form Assumption** *(not yet created)* — addresses systems that assume a resource has exactly one textual representation; complements DP-046 when the identifier and the resolved name are both valid but non-interchangeable representations.

## Known failure modes

**Silent launch failure.** When `open -a` or an equivalent OS invocation receives a token instead of a display name, many operating systems return a non-zero exit code without emitting a user-visible error message. Callers that do not check exit codes will log success while the application never opens.

**Persistent false-positive outdated flags.** If cache invalidation is triggered by token comparison alone, an upgrade that changes only the installed version leaves the cache key intact. The scan loop re-reads the cached pre-upgrade version on every cycle until TTL expiry, generating repeated incorrect alerts and potentially triggering automated re-upgrade attempts.

**Cross-platform identifier collision.** On case-insensitive filesystems the token and the display name may accidentally resolve to the same entry even when they differ in case or spacing, masking the bug in development environments and exposing it only on case-sensitive volumes.

**Resolution cache poisoning.** If the resolution lookup result is cached without a post-mutation invalidation strategy, a correct resolution performed before an upgrade will be served as authoritative after the upgrade, reproducing the original stale-data failure at one remove.

**Brittle vendored name assumptions.** When developers discover the mismatch and hard-code the resolved name as a constant (e.g. `APP_NAME = "Microsoft Teams.app"`), the fix becomes a new source of breakage whenever the upstream vendor renames the bundle across a major release, unless the constant is sourced from the registry's artifact metadata rather than maintained by hand.
