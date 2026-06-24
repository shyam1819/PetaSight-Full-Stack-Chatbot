# DECISIONS

Decisions by build phase (see phases in [CLAUDE.md](CLAUDE.md)). Format: `Decision — Why`.
Kept current as work happens. Pending phases are listed but empty until we reach them.

## Phase 1 — Features

The 4 concrete asks, as specified in [ASK.md](ASK.md). What the ASK requires only — our
solution approach is recorded later, in the phase where we decide it.

### Feature 1 — Reply-bubble color
- Background color of each reply bubble depends on the user's message; **first match wins**,
  rules checked in order.
- Rule 1 — city + temperature (°C): deep blue ≤0 → light purple ~15 → bright red ≥35.
- Rule 2 — standalone decimal: grayscale/sepia from the first two decimal digits, `.00`
  lightest → `.99` darkest.
- Rule 3 — ask the LLM how urgent/panicked it sounds: violet → magenta → pale yellow.
- A message can match more than one rule. The ASK **requires a documented decision** on which
  signal wins (not order alone). _Decision pending — to be made when the matcher is built._
- Assumption: "bubble" = the **AI reply message div** (WhatsApp-style); the user's message sets
  the color of the assistant's reply bubble.
- Aesthetics not in the ASK — chat background color, bubble opacity/transparency — are deferred
  to Phase 4 (code development), constrained by the readability requirement in Feature 3.

### Feature 2 — Real LLM backend
- Replies come from a real LLM on the backend, not canned responses.
- LLM access is **temporary**: a basic API key/access is provisioned for evaluation and will be
  revoked ~1 week / 10 days after submission (the ASK allows shutting the project off then).
  Implication: the key lives in backend env/secrets only, never in the client, and the app may
  stop replying once it's pulled — that is expected.

### Feature 3 — Keyboard, readability, focus
- Works with a keyboard; text stays readable as the background color shifts.
- When a reply appends, a keyboard user must not lose their place or get yanked around.

### Feature 4 — Sign-in restricted to @petasight.com
- Only `@petasight.com` emails get in, **enforced at the backend endpoint**, not just the login page.

## Phase 2 — Architecture (frontend / backend)

_Pending._

## Phase 3 — Temporary store

_Pending._

## Phase 4 — Code development

_Pending._

## Phase 5 — Deployment

_Pending._
