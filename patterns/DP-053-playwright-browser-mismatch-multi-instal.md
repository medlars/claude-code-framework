---
id: DP-053
name: Playwright Browser Mismatch Across Package Instances
category: project-structure
status: proposed
constitution-rules: []
youtube-difficulty: intermediate
youtube-episode-length: short
introduced: 2026-06
---

## What it is

A structural convention that ensures every workspace package requiring Playwright resolves to a single, shared installation whose browsers have been explicitly provisioned — rather than allowing multiple independent `node_modules` copies of Playwright to exist across a monorepo, each demanding its own browser binaries that may never be installed.

## Rationale

### The problem

Playwright pins its browser binaries to the exact package version. When a monorepo contains more than one copy of Playwright — one at the root and one (or more) inside individual workspace packages — each copy resolves its own binary path based on its own version string. Running `playwright install` against the root package installs browsers for the root copy. Any per-project copy that ships a different version, or that simply has not had `playwright install` run in its own directory, will fail at launch with a binary-not-found error even though browsers visibly exist somewhere on the machine.

In the concrete case that produced this pattern: the global smoke-test runner (`pm-smoke.mjs`) depended on a root-level Playwright installation whose Chromium build was present and working. The `verscout` web e2e package declared its own `devDependency` on Playwright 1.58.2, which resolved into `packages/verscout-web/node_modules/@playwright`. That copy required Chromium build 1208. Because `playwright install` was never run inside `packages/verscout-web`, build 1208 did not exist, and every e2e run silently failed to launch a browser.

### The insight

Playwright's browser binaries are keyed to the package instance that resolved them, not to the binary version number alone. Two packages that both declare `@playwright/test@1.58.2` will point at the same binaries only if the package manager deduplicates them into a single physical location. When deduplication does not happen — due to mismatched peer dependencies, hoisting rules, or lockfile drift — each instance behaves as if it owns its browsers exclusively. The safe position is therefore to treat Playwright as a singleton: one declared dependency, one installation, one `playwright install` invocation.

### Evidence

- `packages/verscout-web/node_modules/@playwright/test` existed alongside `node_modules/@playwright/test` at the repo root, confirming two physical copies.
- Running `npx playwright install --with-deps` from within `packages/verscout-web` immediately resolved the launch failure, confirming the root cause was a missing binary for that instance.
- The global smoke runner continued passing throughout, confirming the root copy was healthy.

## Why we use it

- Eliminates a class of CI failures where tests appear to run but browsers never launch, producing output that can be mistaken for a test-logic problem rather than a tooling problem.
- Removes ambiguity about which `playwright install` invocation a given test file depends on.
- Reduces total disk usage by avoiding duplicate browser downloads that can exceed 300 MB per Playwright version.
- Makes browser provisioning a single, auditable step in CI rather than a per-package concern scattered across job definitions.

## How it works

1. **Declare Playwright once.** Playwright and `@playwright/test` are listed as dependencies only at the monorepo root (or a dedicated testing workspace package), never inside individual feature packages.
2. **Enforce deduplication.** The root `package.json` uses a `resolutions` or `overrides` field (depending on package manager) to pin all Playwright references to the same version, ensuring the package manager cannot create a second physical copy even if a transitive dependency requests it.
3. **Single install step.** CI and local setup scripts call `playwright install --with-deps` exactly once, from the root, immediately after `npm install` / `yarn install` / `pnpm install`.
4. **Import via root alias.** Individual test files import from `@playwright/test` without path qualification. Because the package manager resolves this to the single hoisted copy, the binary path is always the one that was provisioned.
5. **Verify in pre-flight.** A lightweight pre-flight script (runnable as `npm run preflight:e2e`) calls `playwright --version` and checks that the expected Chromium build directory exists before any test suite is allowed to start.

## Example

The failure state:

```
packages/
  verscout-web/
    package.json          # "@playwright/test": "1.58.2"  <-- second copy
    node_modules/
      @playwright/test/   # requires Chromium build 1208, never installed
node_modules/
  @playwright/test/       # requires Chromium build 1195, installed and working
```

The fixed state:

```
package.json              # "@playwright/test": "1.58.2", "overrides": { "@playwright/test": "1.58.2" }
packages/
  verscout-web/
    package.json          # no Playwright dependency declared
node_modules/
  @playwright/test/       # single copy, build 1208 installed by root-level `playwright install`
```

CI setup sequence after the fix:

```
pnpm install
pnpm exec playwright install --with-deps
pnpm run preflight:e2e
pnpm run test:e2e --filter=verscout-web
```

## Related patterns

- **DP-041 — Singleton Dev Tooling Dependency** — General rule for treating build and test tools as root-only concerns in a monorepo.
- **DP-027 — CI Pre-flight Assertions** — Pattern for encoding environment assumptions as executable checks that fail fast before test suites run.
- **DP-019 — Lockfile Integrity Gate** — Pattern for detecting lockfile drift that could cause unexpected package duplication after dependency updates.

## Known failure modes

- **pnpm strict isolation.** pnpm's default `node-linker=isolated` prevents hoisting entirely. In this mode the override approach alone is insufficient; a shared Playwright workspace package must be created and each e2e package must depend on it explicitly rather than on `@playwright/test` directly.
- **Version skew after upgrades.** Updating Playwright at the root without regenerating the lockfile can leave stale entries that cause the package manager to reintroduce a second copy. The lockfile integrity gate (DP-019) should catch this, but only if it runs before browser provisioning.
- **Workspace protocol leakage.** If a package declares `"@playwright/test": "workspace:*"` intending to reference a local package, a misconfigured workspace definition will instead pull from the registry and create a new copy. Workspace protocol usage must be audited whenever Playwright is updated.
- **Missing `--with-deps` on Linux CI.** `playwright install` without `--with-deps` omits system-level libraries required by Chromium on headless Linux runners. Browser binaries exist but launch fails with a different error, which can be mistaken for the binary-mismatch problem described here. Always use `--with-deps` in CI.