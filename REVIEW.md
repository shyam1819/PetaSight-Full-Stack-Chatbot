# REVIEW

Review of the provided module [`public/review/bubble_service.py`](public/review/bubble_service.py)
and its test [`public/review/test_bubble_service.py`](public/review/test_bubble_service.py).

**Summary.** At a glance it looks fine and the test suite is green — which is itself the problem:
the tests pass *despite* a security bypass and a caching bug that returns wrong colours. The pure
colour maths (`temp_to_rgb`) is actually correct (the boundary cases at 0/15/35 are handled). The
issues are in everything wrapped around it. Findings below, most important first.

---

## R1 — `is_petasight_user` trusts a client-supplied header (security bypass) — **high**

```python
email = request.headers.get("X-User-Email", "")
return email.strip().lower().endswith("@petasight.com")
```

**Broken:** identity is taken from the `X-User-Email` **request header**, which the *client*
controls. Anyone can send `X-User-Email: anyone@petasight.com` and pass the gate — the `@petasight.com`
restriction is trivially bypassed. This is the exact "identity is something the client hands you"
mistake the brief warns against; the gate enforces nothing.

**Fix:** establish identity **server-side** and never read it from a request header. Verify a
signed session the server issued at login (HMAC-signed cookie / verified JWT) and read the email
from that verified payload, then check the domain. (This is what our app's `require_user()` /
signed-cookie session does — see THREATS T3.) Secondary nit: prefer an exact domain check
(`email.rsplit("@", 1)[-1] == "petasight.com"`) over `endswith`, which also matches odd inputs like
`a@b@petasight.com`.

## R2 — the cache returns the wrong colour for different fractional temps — **correctness**

```python
def cached_color(celsius):
    """... Keyed on the temperature so that 21.4 and 21.6 are two different entries."""
    key = int(celsius)
    ...
```

**Broken:** the docstring claims `21.4` and `21.6` are different entries, but `int(21.4) == int(21.6)
== 21` — they collapse to the **same** key. `temp_to_rgb` uses the full-precision `celsius`, so the
cache loses the fraction it actually maps on: `cached_color(21.9)` stores `21.9`'s colour under key
`21`, and a later `cached_color(21.1)` returns **`21.9`'s colour** instead of `21.1`'s. The cache
silently serves incorrect colours, and the code does the *opposite* of what its docstring says.

**Fix:** remove the cache (R3). If a cache were genuinely needed, key on the actual value used for
the mapping (e.g. round to the precision you care about) and correct the docstring.

## R3 — why cache at all? Delete it — **design**

**Broken/unnecessary:** `temp_to_rgb` is pure, deterministic, and cheap (a few `lerp`s, no I/O).
Memoising it buys nothing and introduces R2, R4, and an **unbounded map** — entries are only
TTL-checked on read and never evicted, so the process-wide dict grows and holds stale data. In a
serverless deployment it's also pointless: instances are short-lived and not shared, so it mostly
misses.

**Fix:** drop the cache and call the function directly:

```python
def cached_color(celsius):
    return temp_to_rgb(celsius)   # pure + cheap; no cache, no bugs
```

(or remove `cached_color` entirely and call `temp_to_rgb` at the call site).

## R4 — the "thread-safe" claim is false — **concurrency / misleading docs**

```python
# Thread-safe: two requests for the same temperature share one computed colour ...
_CACHE = {}
```

**Broken:** there is **no lock**. `cached_color` does an unsynchronised check-then-write on the
shared dict, so concurrent requests race (redundant computes, last-writer-wins). CPython's GIL makes
each individual dict op atomic, so it won't corrupt or crash — but the comment advertises a
guarantee the code doesn't implement, which is misleading and fragile (it leans on a CPython
implementation detail, not real synchronisation).

**Fix:** if a shared cache were truly required, guard the critical section with a `threading.Lock`;
otherwise remove the claim. Best resolved by R3 (no cache → nothing to synchronise).

## R5 — the tests pass but don't test the risky behaviour — **tests**

- `test_cache_runs_twice` calls `cached_color(22)` twice then `assert True` — it asserts **nothing**;
  it always passes regardless of the cache working.
- The suite is green **despite R1 and R2**: nothing checks that a spoofed `X-User-Email` is rejected,
  and nothing checks that two fractional temps with the same integer part get different colours.
  Green tests give false confidence here.
- `test_cached_color_returns_a_tuple` only checks the *type*, not the value.

**Fix:**
- Catch R2: `assert cached_color(21.1) != cached_color(21.9)` (fails today). Once R3 lands, test
  `temp_to_rgb` directly instead.
- Catch R1: test the auth path with a *server-established* identity, and assert that a request whose
  only "identity" is a client header is **not** trusted; add a negative test for a non-`@petasight.com`
  user being rejected.

---

## What's correct (verified, not flagged)

`temp_to_rgb` itself is right: `<=0` → deep blue, `>=35` → bright red, and the two interpolation
segments (0→15 blue→purple, 15→35 purple→red) are continuous, with the `15` boundary handled.
