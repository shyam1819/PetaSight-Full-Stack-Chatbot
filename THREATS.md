# THREATS

Threat model for the PetaSight chatbot. Format per entry: **attack → defense → residual risk**.
T3 is the deepest concern (per-user isolation — the brief's stretch goal), and it is **implemented
and verified live**, not just modelled.

## T1 — Session replay after logout (stateless sessions)

**Context.** Sessions are stateless: a signed, HttpOnly cookie holding an HMAC over
`{user_id, email, exp, jti}`. The server keeps no session store and validates a request by
checking the signature and expiry only.

**Attack.** An attacker who obtains a copy of a valid session cookie can replay it. Logout only
deletes the cookie in *that* browser; because there is no server-side session record, a
previously copied token stays valid until it expires — **logout cannot revoke it**.

**Defense (shipped).**
- `HttpOnly` — JavaScript can't read the cookie, so an XSS bug can't exfiltrate the session.
- `Secure` — sent only over HTTPS, so it isn't exposed on the network in transit.
- `SameSite=Lax` — limits the cookie being sent on cross-site requests (CSRF).
- **Short token TTL** bounds the replay window; a fresh, unique token (new `exp` + random `jti`)
  is issued on every login.

**Residual risk / tradeoff.** No instant server-side revocation — the price of statelessness.
Accepted for this scope, bounded by the short TTL. If instant revocation were required: a
server-side token denylist (breaks pure statelessness — a deliberate call) or rotating
`SESSION_SECRET` (invalidates everyone's sessions at once).

## T2 — Stolen session cookie replayed from another source

**Context.** The session cookie is a bearer token: the HMAC signature proves the token is
authentic and untampered, **not** that the sender is its rightful owner. Anyone holding the
cookie value is treated as that user until it expires.

**Attack.** An attacker copies a valid session cookie and replays it from a different
machine/IP/browser; the server verifies the signature, reads `user_id`, and serves the victim's
data.

**Defense (shipped).** The common *remote* theft vectors are closed: `HttpOnly` (XSS can't read
it), `Secure` + HTTPS (not sniffable in transit), `SameSite=Lax` (not sent cross-site). Short TTL
bounds the replay window. Per-user **isolation** means a stolen token only ever impersonates that
one user — it never crosses into other users' data.

**Residual risk / tradeoff.** A cookie copied from the victim's *own* browser/device is
replayable until expiry — inherent to stateless bearer sessions. We deliberately **avoid
IP-binding** (breaks mobile/roaming users with false logouts) and a **server-side revocation
store** (breaks statelessness). If tighter control were needed: shorten the TTL further, or move
to stateful sessions with revocation.

## T3 — One signed-in user reaching another user's data (per-user isolation)

The deepest concern (the brief's stretch goal): user **A**, holding a *valid* `@petasight.com`
session of their own, tries to read or modify user **B**'s conversations/messages through the API.

**Attacks considered.**
1. **IDOR** — A calls `GET /api/messages?conversation_id=<B's id>` or `POST /api/messages` with B's
   `conversation_id`. IDs are sequential `BIGSERIAL`, so A can enumerate/guess B's.
2. **Identity injection** — A supplies a `user_id` (body/query/header) to act as B.
3. **Cookie forgery** — A edits the session cookie to set `sub` = B's id.

**Defenses (shipped).**
- **Identity is server-established, never client-supplied.** Every handler takes `user_id` only
  from `require_user()` → the verified cookie's `sub`. No code path reads a user id from the
  request, so **attack 2 has no surface**. (This is exactly the `review/` module's `X-User-Email`
  mistake — trusting a client header for identity — which we avoid.)
- **Ownership-scoped queries.** Every conversation/message query filters by `user_id` in SQL:
  `WHERE id = %s AND user_id = %s` (conversations), `WHERE conversation_id = %s AND user_id = %s`
  (messages). So A passing B's `conversation_id` (**attack 1**) matches no rows → `404`;
  `send_message` returns `None` → `404`. The id is only a lookup key; ownership is always re-checked
  against the *cookie's* user.
- **Defense in depth.** Messages carry `user_id` (denormalized), so history reads scope on
  `user_id` directly — even if the conversation ownership check were ever bypassed, message reads
  return only the caller's rows.
- **Cookie integrity.** The session is HMAC-signed with `SESSION_SECRET`; tampering `sub` breaks the
  signature → `401` (**attack 3** fails). See T1/T2.

**How I convinced myself it holds.**
- **Live:** as B, `GET` history and `POST` send to A's `conversation_id` both returned **404**; no
  cookie → **401**; B's own conversation list was empty. As A, the full flow worked.
- **Integration tests** prove repo-level isolation (B can't `get` A's conversation; B reads no
  messages from A's conversation).
- **Unit test** confirms `send_message` rejects an unowned conversation.
- The only client-controlled identifier is `conversation_id`, and every query that consumes it also
  constrains `user_id` — so an id A doesn't own yields nothing.

**Residual risk / honest notes.**
- **Enumeration:** sequential ids let A *guess* B's ids, but guessing is useless — ownership
  scoping returns `404` regardless, and a non-existent id and a non-owned id both return a **uniform
  404** (no existence oracle). UUID ids would hide existence further; not needed given the uniform
  response.
- Isolation rests on session integrity — a leaked `SESSION_SECRET` would let an attacker forge any
  `sub`. Mitigated by keeping it server-side (Vercel env only) and the short token TTL (T1/T2).
