---
id: DP-042
name: Progressive image-unblock UX (all-folders Load + guarded Trust)
category: security
status: active
constitution-rules: [SEC-001]
youtube-difficulty: beginner
youtube-episode-length: short
introduced: 2026-05
---

## What it is

Email security banners that block remote images must provide a "Load Images"
button in ALL folders — including high-risk ones like Spam and Trash. The
distinction between folder types governs what PERSISTENT trust actions are
offered, not whether the one-time override is available.

| Folder type | "Load Images" shown | "Always Trust Sender" shown |
|-------------|--------------------|-----------------------------|
| Standard (Inbox, Sent, Archive, …) | Yes | Yes |
| High-risk (Spam, Trash, Quarantine) | Yes | No |

This is the progressive image-unblock pattern: every user always has an
escape hatch; permanent whitelist expansion is limited to contexts where
it is safe.

## Rationale — Why We Adopted This Pattern

*The story of how this pattern came to exist and why it was chosen over alternatives.*

### The problem we kept hitting

SagaMail showed a red shield banner in Spam and Trash:

    "Remote images are always blocked in this folder to protect your privacy."

The banner was correct — but there was NO "Load Images" button. The
`!inUnsafeFolder` guard in `MessageDetailView.swift` prevented the button
from appearing in high-risk folders. A user opening a legitimate email
that had been incorrectly filtered to Spam had no way to see its images
without moving the message first. The UI was a dead-end.

### What we tried first (and why it didn't work)

- **No button in unsafe folders** — original implementation. Correctly
  blocked persistent trust expansion but created a usability dead-end:
  users couldn't see images in any Spam/Trash message even when they
  chose to.
- **Allow both buttons in all folders** — rejected. "Always Trust Sender"
  on a spam message would permanently whitelist a malicious address.
  Security regression, not acceptable.

### The insight that unlocked the solution

The security concern is about PERSISTENT state changes (adding a sender
to a trust whitelist), not about one-time rendering. Loading an image
once to read a message is always the user's choice; permanently trusting
the sender is the dangerous action. These are two different verbs — split
them accordingly.

### Why this approach, not the obvious one

*Why not just block all image loading in unsafe folders?* Because the user
already decided to open the message. They navigated to Spam deliberately.
Denying them a one-time override is paternalistic and creates friction for
legitimate false-positives. Security UX that has no escape hatch trains
users to route around it (move to Inbox first, then read) which is worse.

### Evidence that it works

Fix in `MessageDetailView.swift`:

```swift
// Load Images — shown in ALL folders
Button("Load Images") { loadImages() }

// Always Trust Sender — shown ONLY in non-unsafe folders
if !inUnsafeFolder {
    Button("Always Trust Sender") { trustSender() }
}
```

SagaMail session 2026-05-13. No security regression; usability blocker
resolved.

## Why we use it

Security controls must have an escape hatch for the user. Without one,
users work around the control (moving messages before reading, disabling
the feature entirely). The pattern separates ONE-TIME overrides (always
available) from PERSISTENT trust expansion (context-gated). This is the
minimum viable security UX for image blocking.

## How it works

**Inputs required**:
1. `inUnsafeFolder: Bool` — derived from the message's folder path or
   labels. Typical unsafe folders: Spam, Junk, Trash, Quarantine.
2. `imagesLoaded: Bool` — current rendering state for this message view.
3. A `loadImages()` action — sets `imagesLoaded = true` for this session.
4. A `trustSender()` action — adds sender to persistent whitelist.

**Decision tree**:

```
showBanner = remoteImagesBlocked && !imagesLoaded
  showLoadButton = showBanner                    // always
  showTrustButton = showBanner && !inUnsafeFolder // guarded
```

**UI layout** (SagaMail reference, SwiftUI):

```swift
if showBanner {
    HStack {
        Image(systemName: "shield.fill").foregroundColor(.red)
        Text(bannerText)
        Spacer()
        Button("Load Images") { loadImages() }
        if !inUnsafeFolder {
            Button("Always Trust Sender") { trustSender() }
        }
    }
    .padding()
    .background(Color.red.opacity(0.1))
}
```

**Folder classification** — classify as unsafe if any of:
- Folder path contains "spam", "junk", "trash" (case-insensitive)
- IMAP folder flags include `\Junk` or `\Trash`
- Gmail label set includes "SPAM" or "TRASH"

## Example

**Before fix** (dead-end in Spam):
```
[🛡 Remote images are always blocked in this folder to protect your privacy.]
```
No buttons. User cannot view images. Must move message to Inbox first.

**After fix** (escape hatch available everywhere):

In Spam/Trash:
```
[🛡 Remote images are blocked in this folder.   [Load Images]            ]
```

In Inbox (no prior trust):
```
[🛡 Remote images blocked.   [Load Images]   [Always Trust Sender]       ]
```

## Related patterns

- [DP-028] PHI boundary enforcement — same "one-time vs persistent" split
  applies to data access gates.
- [DP-030] Add-then-remove migration — both patterns share the principle
  that a reversible operation (one-time load) should never be blocked by
  rules designed for irreversible operations (persistent trust).
- [DP-034] Boring technology bias — the fix is a simple conditional; no
  new framework or abstraction required.

## YouTube episode angle

- **Tech-savvy** (8 min): "The security UX mistake that makes people
  disable protection entirely." Show the dead-end UI → show the fix →
  discuss one-time vs persistent trust as a design primitive. Applicable
  to any permission system (camera, location, notifications).
- **Lay audience** (5 min): "Your spam folder had a locked door with no
  handle." You peeked inside deliberately. The app shouldn't refuse to
  let you look — it should just not put you on the VIP list automatically.

## Known failure modes / lessons learned

- **Trust button in wrong context**: if `inUnsafeFolder` is computed
  per-render instead of per-account/folder the button can flicker.
  Derive it once when the message view loads.
- **Load Images persists across navigation**: if `imagesLoaded` is stored
  in view state and the view is not rebuilt on message change, images
  from message A appear loaded when navigating to message B. Scope
  `imagesLoaded` to the message ID, not the view instance.
- **Banner text mismatch**: after adding "Load Images" to the unsafe-folder
  banner, update the banner text to match. A banner saying "images are
  always blocked" next to a "Load Images" button is confusing.
