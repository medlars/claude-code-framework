---
id: DP-052
name: Custom URL Scheme Isolation in WebView
category: execution
status: proposed
constitution-rules: []
youtube-difficulty: intermediate
youtube-episode-length: short
introduced: 2026-06
---

## What it is

Custom URL Scheme Isolation in WebView is a routing pattern that intercepts non-HTTP URL schemes inside a WebView and delegates them to the host process for OS-level dispatch, rather than expecting the WebView to handle them natively.

## Rationale

### The problem

WKWebView imposes a strict navigation policy on custom URL schemes such as `macappstore://`, `tel://`, `mailto://`, and similar deep-link protocols. When JavaScript calls `window.open()` with one of these schemes, WKWebView silently swallows the navigation event. No error is raised, no delegate callback fires with a useful signal, and the user sees nothing happen. The button appears broken even though the URL itself is valid.

### The insight

WKWebView is designed to handle HTTP and HTTPS traffic. Everything else is considered out of scope for the renderer. The OS, however, knows exactly what to do with `macappstore://` — it is LSOpenURL that must receive the call, not the web rendering engine. The fix is therefore architectural: the WebView should never attempt to open these schemes itself. Instead it should signal the host process, which calls into the OS directly.

### Evidence

Routing the scheme through a Flask subprocess call — where the backend invokes the platform open command — caused the App Store to launch correctly on the first attempt. The identical URL passed to `window.open()` had produced no observable effect for every prior invocation.

## Why we use it

- Eliminates silent failures where a WebView swallows a navigation event with no error surface
- Keeps OS-level dispatch in the one layer that has the correct permissions and registered URL handler knowledge
- Makes the behaviour explicit and testable: the host process call can be logged, retried, or mocked in tests
- Applies uniformly to any custom scheme, so the same pattern handles `mailto://`, `tel://`, `spotify://`, and others without case-by-case workarounds

## How it works

1. The WebView intercepts the navigation request before it proceeds, typically in a `decidePolicyForNavigationAction` delegate or an equivalent message handler.
2. The interceptor inspects the URL scheme. If the scheme is not `http` or `https`, it cancels the WebView navigation and instead posts the URL to the host process.
3. The host process — a native app layer, a local Flask server, or any IPC-capable backend — receives the URL and calls the OS open API (`NSWorkspace.shared.open`, `subprocess.run(["open", url])`, `ShellExecute`, etc.).
4. The OS resolves the registered handler for the scheme and launches the appropriate application.
5. The WebView remains on its current page, unaffected.

The interception point is critical. In WKWebView specifically, the delegate method must call the `decisionHandler` with `.cancel` before any attempt to let the WebView proceed, because there is no recovery path once the silent drop occurs.

## Example

A macOS desktop app embeds WKWebView to display a software catalogue. Each product card has a button labelled "View in App Store" that constructs a `macappstore://` URL and calls `window.open()`.

**Before the pattern:** The click event fires, `window.open()` is called, WKWebView receives the navigation, finds no handler, drops it. The App Store never opens.

**After the pattern:**

- A JavaScript message handler is registered under the name `openExternalURL`.
- The button onclick calls `window.webkit.messageHandlers.openExternalURL.postMessage(url)` instead of `window.open()`.
- The WKScriptMessageHandler delegate receives the message and calls `NSWorkspace.shared.open(URL(string: url)!)`.
- The App Store opens at the correct product page.

In a Flask-backed variant, the message handler posts the URL to a local endpoint, and the Flask route executes `subprocess.run(["open", url])`. The outcome is identical; the indirection through Flask is useful when the WebView host is a non-native runtime such as Python or Electron.

## Related patterns

- **DP-031 – Host Bridge Messaging** — establishes the general pattern of JavaScript-to-host communication; Custom URL Scheme Isolation is a specific application of that bridge for navigation events.
- **DP-044 – Subprocess Side Effect Isolation** — governs when a Flask or subprocess call is the correct place to invoke a side effect with OS scope.
- **DP-019 – Navigation Policy Guard** — covers the broader practice of auditing all navigation decisions in a WebView before allowing them to proceed.

## Known failure modes

- **Missing cancellation of the default action.** If the delegate calls `decisionHandler(.allow)` and also dispatches to the host, some runtimes will attempt both paths. The WebView path will silently fail and may log a confusing error that masks the successful OS dispatch.
- **Scheme allow-list drift.** If a new custom scheme is introduced in content but not added to the interceptor's scheme check, it falls through to the WebView and is swallowed silently again. The allow-list of safe HTTP schemes should be an explicit set, not an ad-hoc condition.
- **Sandboxing restrictions on the host process.** In a fully sandboxed Mac App Store build, `NSWorkspace.shared.open` for certain schemes requires an entitlement. The pattern itself is correct, but the host process must have the necessary capability declared or the OS call will also fail silently.
- **Flask subprocess not running.** In the Flask-backed variant, if the local server has crashed or not yet started, the HTTP post from the WebView will fail. The pattern should include a readiness check or a retry with user-visible feedback rather than failing silently in a different layer.