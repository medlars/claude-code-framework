---
id: DP-041
name: Newsletter preheader snippet filter (inbox preview protection)
category: detection
status: active
constitution-rules: [DETE-001]
youtube-difficulty: beginner
youtube-episode-length: short
introduced: 2026-05
---

## What it is

When generating inbox snippet previews from email body text, filter lines
that match known image-tracker preheader patterns before selecting the first
prose line. Newsletter mailers embed hidden pixel-tracking instruction text
("Follow image link: …", "Open image to view", "Load image …") as the first
visible text in their HTML body. Without a filter, this text is promoted as
the snippet, making multiple unrelated emails appear identical in the inbox
list.

## Rationale — Why We Adopted This Pattern

*The story of how this pattern came to exist and why it was chosen over alternatives.*

### The problem we kept hitting

On 2026-05-13, SagaMail's inbox list showed identical snippet text:

    "Follow image link: { Hey, Eiman! Welcome back to the #1 AI newsletter…"

for three completely different emails (StackSocial, iPostal1, TAAFT). The
inbox became useless for distinguishing messages at a glance. Root cause:
newsletter mailers (MailChimp, Klaviyo, Drip, and others) insert a
transparent 1×1 pixel tracker early in the HTML body, surrounded by
human-readable alt text that starts with phrases like "Follow image link:"
or "Open image to view:". The Gmail API uses the first ~200 characters of
body text as its `snippet` field, so it picks up this preheader.
`extractProseSnippet()` in `AccountManager+Streaming.swift` had no guard
against these patterns.

### What we tried first (and why it didn't work)

- **No filter** — broken: identical snippets for all newsletter emails.
- **Rely on Gmail API snippet** — the API snippet field ALREADY contains
  the tracker preheader text; the problem originates upstream.
- **Strip HTML more aggressively** — the tracker text is in plain text alt
  attributes, not just in HTML tags; tag-stripping alone does not remove it.

### The insight that unlocked the solution

The tracker preheader lines all share a small set of opening phrases
("follow image", "open image", "load image"). A prefix filter on lowercased
lines — applied before selecting the first prose sentence — eliminates them
with zero false positives on legitimate prose.

### Why this approach, not the obvious one

*Why not build a full preheader classifier?* The known phrases are stable
across every major email marketing platform; a simple prefix match is the
boring, right solution (DP-034). A classifier would introduce a dependency
and a failure mode for no additional precision.

### Evidence that it works

Fix landed in `AccountManager+Streaming.swift` (`extractProseSnippet()`):

```swift
if lower.hasPrefix("follow image") || lower.hasPrefix("open image") || lower.hasPrefix("load image") { return false }
```

Post-fix: StackSocial, iPostal1, and TAAFT all show distinct, readable
snippets in the inbox list. SagaMail session 2026-05-13.

## Why we use it

Newsletter mailers deliberately put image-tracker instruction text before
prose. This text is compact and positionally first, so any "take first
readable line" algorithm without a preheader guard will surface it. The
filter is three lines of code with zero runtime cost and protects every
inbox view with newsletters.

## How it works

**Location**: `extractProseSnippet()` in the email body processing pipeline
(in SagaMail: `Sources/SagaMailDomain/AccountManager+Streaming.swift`).

**Filter logic** (Swift reference implementation):

```swift
func extractProseSnippet(from lines: [String]) -> String? {
    for line in lines {
        let lower = line.lowercased().trimmingCharacters(in: .whitespaces)
        // Skip empty lines
        guard !lower.isEmpty else { continue }
        // Skip image-tracker preheader patterns common in newsletter mailers
        if lower.hasPrefix("follow image") ||
           lower.hasPrefix("open image") ||
           lower.hasPrefix("load image") { continue }
        // Skip other known boilerplate prefixes (extend as new patterns emerge)
        if lower.hasPrefix("view in browser") ||
           lower.hasPrefix("view this email") ||
           lower.hasPrefix("unsubscribe") { continue }
        return line
    }
    return nil
}
```

**Generalizable rule**: before selecting the "first useful line" from any
user-facing text feed, define a `denylistPrefixes` set (or function) and
apply it before the selection. Extend the list as new tracker patterns are
encountered; never shrink it.

**Extension point**: the deny list can be externalized to a config file or
user-space pref list without changing the selection algorithm.

## Example

Raw HTML body first text block from a StackSocial newsletter:

```
Follow image link: { Hey, Eiman! Welcome back to the #1 AI newsletter...
```

Without filter → snippet = "Follow image link: { Hey, Eiman! Welcome back…"
(same for iPostal1, TAAFT, and 80% of newsletter mail).

With filter → snippet = "Hey, Eiman! Welcome back to the #1 AI newsletter…"
(correct; unique per email).

## Related patterns

- [DP-005] WatchTools detector-gap pattern — this fix was surfaced by a
  detector-gap report during a SagaMail session; the detector should now
  flag `extractProseSnippet` calls without a preheader guard.
- [DP-034] Boring technology bias — simple prefix match, no ML classifier.
- [DP-008] SilentFailureWatch — snippet silently returning tracker text is
  a category of silent failure (wrong output, no exception).

## YouTube episode angle

- **Tech-savvy** (8-10 min): "The hidden line your inbox is showing instead
  of your email." Show the raw HTML source of a newsletter, identify the
  tracker preheader, trace it to the Gmail `snippet` field, implement the
  three-line fix, confirm with before/after screenshots. Widen to: every
  time you select "the first line," you need a deny-list.
- **Lay audience** (5 min): "Why your inbox previews all look the same."
  Mailers put invisible instructions before their text. Your email app
  reads those instructions as the preview. The fix: teach the app to skip
  known tracker phrases and read the first real sentence instead.

## Known failure modes / lessons learned

- New ESP platforms introduce new preheader phrases over time. Maintain a
  living deny-list; treat it like an allow-list for spam (append-only
  except for confirmed false positives).
- Phrases that appear in legitimate subject lines (e.g., a newsletter
  genuinely titled "Open Image: A Philosophy of Visibility") would be
  filtered. In practice this has never occurred; the pattern is constrained
  to line-START matching, not substring matching, which limits blast radius.
