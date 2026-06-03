---
id: DP-051
name: monkeypatch-getattr-shadowing-via-hasattr-detection
category: anti-pattern
status: proposed
constitution-rules: []
youtube-difficulty: intermediate
youtube-episode-length: short
introduced: 2026-06
---

# monkeypatch-getattr-shadowing-via-hasattr-detection

## What it is

A class of test-isolation failure where `pytest`'s `monkeypatch.setattr` permanently corrupts the attribute resolution chain on objects that implement `__getattr__`. When `monkeypatch` probes for an attribute's existence using `hasattr`, a `__getattr__`-backed proxy satisfies the check and returns a dynamically generated value. `monkeypatch` treats that value as the canonical original, stores it, and restores it via `setattr` after the test. The result is a real instance attribute that shadows `__getattr__` for every subsequent test in the same process.

## Rationale

### The problem

`monkeypatch.setattr` follows a save-then-restore contract. Before patching, it calls `hasattr(target, name)`. If `True`, it retrieves the current value with `getattr` and schedules a `setattr(target, name, original)` undo. If `False`, it schedules a `delattr` undo instead.

Objects backed by `__getattr__` present a false positive to this probe. `__getattr__` is only invoked when normal attribute lookup fails, meaning it is the dynamic fallback layer. Yet `hasattr` cannot distinguish between an attribute that genuinely exists in `__dict__` or the class hierarchy and one synthesised on the fly by `__getattr__`. Both cases return `True`. The saved "original" is therefore an artifact of the proxy's runtime state at the moment the test began, not a stable stored value. After teardown, `monkeypatch` writes that artifact back with `setattr`, permanently populating `instance.__dict__` with a key that was never there before.

### The insight

The corruption is silent and cumulative. The first test that patches a `__getattr__`-forwarded attribute leaves a real dictionary entry. Every subsequent test encounters normal attribute lookup that resolves through `__dict__` before `__getattr__` is ever consulted. Behaviour changes across the test suite depending purely on execution order, which is the hallmark of test-isolation failure rather than product failure.

The root confusion is that `hasattr` is not a proxy-aware existence predicate. It is an exception-suppression wrapper around `getattr`. A `__getattr__` implementation that never raises `AttributeError` makes the target appear to own every possible attribute name.

### Evidence

The failure manifests in two observable ways:

1. **Order-dependent test failures.** A test that passes in isolation fails when preceded by a test that patches the same proxy attribute, because the post-teardown `setattr` leaves stale state.
2. **Incorrect mock invocation counts.** A subsequent test that expects calls to be routed through `__getattr__` finds them silently handled by the injected instance attribute instead, causing assertion mismatches on call counts or argument captures.

Both symptoms disappear when tests are run in reverse order or in isolation, confirming the stateful corruption source.

## Why we use it

Documenting this as an anti-pattern serves three purposes:

- Prevents engineers from writing `monkeypatch.setattr(proxy_instance, ...)` against `__getattr__`-backed objects without understanding the teardown risk.
- Provides a named reference when code review encounters this pattern, avoiding the need to re-derive the failure from first principles each time.
- Anchors the approved mitigation strategies so they are applied consistently rather than improvised per incident.

## How it works

The failure sequence for a `_SubprocessProxy` instance with a `__getattr__` that forwards attribute access to a subprocess handle:

1. Test A calls `monkeypatch.setattr(proxy, 'run', mock_fn)`.
2. `monkeypatch` evaluates `hasattr(proxy, 'run')`, which triggers `proxy.__getattr__('run')`. The proxy returns a bound callable. `hasattr` returns `True`.
3. `monkeypatch` calls `getattr(proxy, 'run')` to save the original. The proxy's `__getattr__` returns a freshly created callable object. This object is stored as `saved`.
4. `monkeypatch` calls `setattr(proxy, 'run', mock_fn)`. This writes `'run'` into `proxy.__dict__`.
5. Test A completes. `monkeypatch` teardown calls `setattr(proxy, 'run', saved)`. This writes the stale callable into `proxy.__dict__`, where it remains.
6. Test B runs. `proxy.run` resolves via `proxy.__dict__` and returns the stale callable. `__getattr__` is never invoked. All behaviour that depends on dynamic forwarding is broken.

The mechanism that prevents correct teardown is the absence of a sentinel distinguishing "attribute was in `__dict__` before patching" from "attribute was synthesised by `__getattr__`." `monkeypatch` has no such sentinel.

## Example

**Problematic usage:**

```python
# _SubprocessProxy delegates all attribute access to a live subprocess handle.
class _SubprocessProxy:
    def __init__(self, handle):
        object.__setattr__(self, '_handle', handle)

    def __getattr__(self, name):
        return getattr(object.__getattribute__(self, '_handle'), name)


def test_run_is_called(monkeypatch):
    proxy = _SubprocessProxy(real_handle)
    mock_fn = MagicMock()
    # Dangerous: monkeypatch will save a stale 'run' and restore it via setattr.
    monkeypatch.setattr(proxy, 'run', mock_fn)
    proxy.run('echo hello')
    mock_fn.assert_called_once_with('echo hello')
    # After teardown, proxy.__dict__['run'] = <stale callable>. __getattr__ shadowed.
```

**Correct approach — patch the handle, not the proxy:**

```python
def test_run_is_called(monkeypatch):
    proxy = _SubprocessProxy(real_handle)
    mock_fn = MagicMock()
    # Patch the underlying object where the attribute genuinely lives.
    monkeypatch.setattr(real_handle, 'run', mock_fn)
    proxy.run('echo hello')
    mock_fn.assert_called_once_with('echo hello')
    # Teardown correctly restores real_handle.__dict__ with no side effects on proxy.
```

**Alternative — bypass monkeypatch entirely for instance attributes:**

```python
def test_run_is_called():
    proxy = _SubprocessProxy(real_handle)
    mock_fn = MagicMock()
    # Write directly and clean up explicitly, or use a fresh proxy per test.
    try:
        object.__setattr__(proxy, 'run', mock_fn)
        proxy.run('echo hello')
        mock_fn.assert_called_once_with('echo hello')
    finally:
        # Explicitly remove rather than restore, matching the true pre-test state.
        try:
            object.__getattribute__(proxy, '__dict__').pop('run', None)
        except AttributeError:
            pass
```

The governing principle in both alternatives is to patch the object that owns the attribute in its own `__dict__` or class namespace, never the proxy that only forwards.

## Related patterns

- **DP-012 — proxy-transparent-test-doubles**: Covers the broader discipline of targeting the authoritative object when constructing test doubles for delegation hierarchies.
- **DP-034 — fresh-instance-per-test-fixture**: Eliminates shared mutable state between tests by constructing a new proxy instance in each test's fixture scope, making teardown residue irrelevant.
- **DP-047 — setattr-sentinel-guard**: Describes adding a `__setattr__` guard to proxy classes that raises on attempts to write attributes the proxy does not own, surfacing this failure immediately rather than silently.

## Known failure modes

**Mitigation not applied to all callsites.** Engineers unfamiliar with this anti-pattern introduce new `monkeypatch.setattr(proxy_instance, ...)` calls