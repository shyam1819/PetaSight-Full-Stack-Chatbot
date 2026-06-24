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
- Assumption: bubble color is decided **per message in isolation** — conversation history does
  not influence it; only the single user message that triggered the reply is evaluated.
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
- Assumption 1 — no external identity provider to verify a real person: accept **any** credentials
  whose email matches the `@petasight.com` domain (domain check is the only gate on who's valid).
- Assumption 2 — no onboarding / no pre-provisioned passwords / no separate "create user" flow.
  Account is created **on first sign-in** (trust-on-first-use): the email + password entered the
  first time becomes the stored credential for that email.
- Re-access: signing in again with the **same** email + password authenticates the
  already-created user. Implication (for the auth to hold): an existing email with a **wrong**
  password must be **rejected**, never silently re-created — otherwise anyone could overwrite or
  take over another `@petasight.com` account. (Feeds [THREATS.md](THREATS.md).)
- No **forgot-password** / password-reset flow — kept out to stay simple and within the scope of
  the assignment.

## Phase 2 — Architecture (frontend / backend)

**Stack (locked):** Vercel host · Python serverless functions (`api/`) · Vite + React (TypeScript)
frontend · Neon Postgres store · one repo, same origin. No Redis/cache server.

- **Host: Vercel** — Vercel is not a container platform, so compute is serverless functions, not
  a long-running server.
- **Backend: Python serverless functions** in `api/` (bare Python handlers; framework optional) —
  serverless is the only Vercel option, and Python aligns with the provided `review/` starter.
- **Stateless backend → all state in the DB** — functions are ephemeral with no shared memory
  between invocations, so no in-memory cache/session (the starter's process-wide `_CACHE` would
  not hold). Identity and per-user data live in the store, enforced in the Python functions.
- **One repo, same origin** — static frontend served at `/`, `api/*.py` at `/api/*`; no CORS, and
  the Python functions are the enforced backend for the `@petasight.com` gate and isolation.
- **Backend reachability is enforced at the app layer, not the network** — frontend and `/api`
  share one public origin; the browser calls `/api` directly, so the endpoint is inherently
  public. "Only reachable through the frontend" = require a server-issued session on every API
  call (anon/cross-user → 401/403). Vercel Deployment Protection is **disabled** (it blocks the
  whole deployment incl. the frontend, so it's not a backend-only gate). Feeds [THREATS.md](THREATS.md).
- **Frontend: Vite + React (TypeScript)**, static SPA in the same project — scaffolded from the
  minimal official Vite starter (not a heavy third-party template, so all code is ours and
  reviewable). React chosen for deliberate **focus control** (`ref` to return focus to the input)
  and a stable **`aria-live="polite"`** thread, which is the part the brief grades; **not** Next.js
  (its Node backend is redundant against Python `/api`).
- **Assessment files stay in `public/`** — Vite's `publicDir` is pointed elsewhere so `public/`
  (brief + `review/`) is ignored by the build and never deployed to the live URL.

## Phase 3 — Temporary store

- **Neon Postgres (serverless, free tier)** — relational model fits `users` + per-user `messages`
  cleanly, per-user isolation is a simple `WHERE user_id = ...`, scales to zero, and is $0 at this
  scale. Provisioned via the Vercel Marketplace (env vars auto-injected). Required regardless,
  since serverless functions can't keep state in memory.
- **No Redis / cache server** — kept out to keep the approach simple. Neon is the only store; the
  color logic is cheap to recompute per request, so caching adds complexity without real benefit
  here (the starter's in-memory `_CACHE` wouldn't survive serverless invocations anyway).

## Phase 4 — Code development

_Pending._

## Phase 5 — Deployment

- **CI/CD via GitHub Actions** (`.github/workflows/deploy.yml`), not Vercel's native Git
  integration — keeps deploys gated behind our own checks (frontend build + Python compile)
  before shipping, matching the Definition-of-Done "test before deploy" rule.
- **Branch strategy:** push to `dev` → Vercel **Preview** deploy (shareable test URL); push to
  `main` → **Production**. Work happens on `dev`; `main` stays releasable.
- Deploy uses the Vercel CLI with `VERCEL_TOKEN` / `VERCEL_ORG_ID` / `VERCEL_PROJECT_ID` stored as
  GitHub Actions secrets (set once by the repo owner).
- **Build happens in Vercel's cloud, not prebuilt in CI** — the Python builder uses `uv`, which
  isn't on the CI runner (or a local machine), so `vercel build`/`--prebuilt` fails with
  `spawn uv ENOENT`. Using plain `vercel deploy` lets Vercel build server-side where `uv` exists;
  our CI gate (npm build + `py_compile`) still runs first. Local `vercel dev` needs `uv` installed
  (`brew install uv`).
