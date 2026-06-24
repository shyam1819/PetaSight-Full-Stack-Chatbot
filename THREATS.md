# THREATS

Threat model for the PetaSight chatbot. Grows as features land; the deep per-user **isolation**
analysis arrives with EP-5/EP-7. Format per entry: **attack → defense → residual risk**.

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
