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
- **Collision decision (the graded one): strict first-match-wins**, in the brief's order
  (temperature → decimal → panic). We honour the explicit spec ("Check these in order, first match
  wins") rather than overriding by signal. Rationale: the order runs most-objective →
  most-subjective — a present city+temperature or a decimal is a concrete fact in the text, whereas
  panic is a fuzzy LLM judgment; so when a concrete signal is present it gives a more predictable,
  explainable, deterministic colour than letting panic override.
- **Temperature requires a unit or explicit description.** A number is a temperature only when given
  with a unit (°C, C, "degrees", "Celsius") or described as a temperature; a **bare** number next to
  a city (plain "Austin 21.5") is NOT a temperature → it falls through to the decimal rule. This is
  stricter than — and **deliberately diverges from** — the brief's collision example (which reads
  "Austin 21.5" as a temperature): we judge a bare number too ambiguous to be "a temperature in
  Celsius". Enforced in the classify prompt; verified live ("Austin 21.5"→decimal, "Austin 21.5C" /
  "21.5 degrees in Austin"→temperature, "the score is 21.5"→decimal). **Consequence:** the brief's
  example "Austin 21.5 we need to leave right now" colours as a **decimal** (gray), not temperature
  or panic.
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
- **Connection vars** — the Neon/Vercel integration injects with a `petasight_postgres_` prefix.
  Runtime functions use the **pooled** URL (`petasight_postgres_DATABASE_URL`, PgBouncer — right
  for many short serverless connections); **migrations/DDL** use the **unpooled** URL
  (`..._DATABASE_URL_UNPOOLED`, direct). DB creds live in Vercel only, never in GitHub.
- **Schema** (`db/schema.sql`, idempotent): `users`, `conversations`, `messages`. Every
  conversation and message carries `user_id` for per-user isolation. Applied to Neon.

## Phase 4 — Code development

Implementation decisions organized by **epic / story** (mirrors [BACKLOG.md](BACKLOG.md)).
Cross-cutting feature/architecture/store/deploy decisions stay in Phases 1–3 and 5. New story
decisions get appended under their epic as we complete them.

### EP-1 — Deployment & Infrastructure
- **1.5 Shared-module import convention** — backend shared code lives under `api/_<pkg>/` and is
  imported package-style: `from api._core.<module> import <name>`. Verified on Vercel: the whole
  `api/` tree is bundled and cwd `/var/task` is on `sys.path` so `api.` resolves; a bare
  `from _core...` does **not** work at top level. Underscore-prefixed dirs (`_core`, `_services`,
  …) aren't treated as routes. Enables handler → service → repository layering without per-handler
  `sys.path` hacks.

### EP-2 — Authentication & Access Control
- **2.1 Password hashing** — PBKDF2-HMAC-SHA256 (stdlib), per-password salt, ~210k iterations,
  self-describing stored format (`pbkdf2_sha256$iterations$salt$hash`), constant-time verify.
  Chosen over bcrypt/argon2 to avoid a native dependency on the serverless build.
- **2.2 Stateless sessions** — HMAC-signed cookie token `{sub, email, iat, exp, jti}`; verify
  signature (constant-time) **then** expiry; no server-side session store. Flags
  `HttpOnly; Secure; SameSite=Lax`; 1h TTL; random `jti` per token. `SameSite=Lax` over `None`
  (same-origin, no cross-site need) and over `Strict` (preserves top-level-nav UX) — blocks CSRF.
  `SESSION_SECRET` injected, **fails closed** if missing. Replay tradeoffs →
  [THREATS.md](THREATS.md) T1/T2.
- **2.3 User repository** — Repository pattern: `UserRepository` Protocol + concrete
  `PostgresUserRepository`, a frozen `User` dataclass, and a shared `db.connect()` reading the
  pooled DSN. The repo owns **all** user SQL so the auth service depends on the interface
  (testable with a fake). `create()` raises on duplicate email; the service handles
  trust-on-first-use. Repo verified by an integration check against live Neon (model mapping
  unit-tested separately).
- **2.4 Auth service** — pure `AuthService` over the `UserRepository` interface; returns an
  `AuthResult` with an `AuthOutcome` enum (`CREATED` / `AUTHENTICATED` / `INVALID_CREDENTIALS` /
  `DOMAIN_NOT_ALLOWED` / `MISSING_FIELDS`) that 2.5 maps to HTTP codes. Enforces `@petasight.com`
  server-side, trust-on-first-use, wrong-password **rejection without overwrite**, and email
  normalization (strip+lower). Session secret injectable. Interfaces extracted to
  `repositories.py` (DIP) so the service imports **no psycopg** — verified, and unit-tested with a
  fake repo (6 tests).
- **2.5 Auth endpoints** — thin handlers over the service/session primitives: `POST /api/login`
  (outcome→status 201/200/401/403/400, sets the HttpOnly cookie), `POST /api/logout` (clears the
  cookie, idempotent), `GET /api/me` (identity from the verified cookie, else 401). Shared
  `http_helpers` for body/JSON; **503 fail-closed** if `SESSION_SECRET` is missing. Replaced the
  Task-1 login stub. Verified live end-to-end on the Preview deploy (8-step round-trip).
- **2.6 Require-auth guard** — one seam (`auth_guard.py`) turns the session cookie into a
  server-established identity: `authenticate()` (pure decision) + `require_user()` (handler glue →
  401 unauth / 503 misconfig). Protected handlers get `user_id` **only** from the verified
  signature, never from client input — consistent enforcement and the single seam EP-5 isolation
  relies on. `/api/me` refactored onto it. 5 unit tests; imports no psycopg. Completes the EP-2
  backend.
- **Session refresh — deliberately omitted.** No `/api/session/refresh`; the 1h TTL is **absolute**,
  not sliding. Rationale: (1) preserves the tight replay bound from THREATS T1/T2 — sliding refresh
  would let an actively-replayed stolen cookie be renewed too; (2) a reviewer's session is short, so
  1h is ample; (3) expiry is handled cleanly by the UI's 401 handling (drop to login), so no abrupt
  failure. If long active sessions later prove annoying, add sliding refresh **with an absolute
  max-age cap** (preserve original `iat`) and document the replay tradeoff here + in THREATS.
- **2.7 Login UI** — accessible `LoginForm` wired to `/api/login` via a typed client
  (`src/api/auth.ts`, same-origin so the cookie is set automatically). A11y by construction:
  `label[for]` associations, autofocus the email field, visible focus rings, `disabled`/`aria-busy`
  while loading, errors announced via `role="status" aria-live="polite"` (no focus steal),
  `aria-invalid` on failure. Maps backend messages (403 domain / 401 creds / 400 missing / 503 /
  network). Strictly to ASK — no remember-me/social; one helper line for trust-on-first-use. App
  shows a temporary success placeholder pending 2.8 gating. The on-screen disclosure of the
  `@petasight.com` requirement and trust-on-first-use is **intentional for the assignment** (makes
  the behavior obvious to reviewers); a production app would avoid advertising the allowed domain /
  auto-create behavior to limit user enumeration.
- **Password policy — none enforced (scope).** No strength/complexity/min-length rules;
  trust-on-first-use accepts any non-empty password (empty is rejected). Deliberate simplification
  for the assignment — a production app would enforce a policy (length/complexity, breach check)
  and rate-limit attempts. Hashing (PBKDF2) still protects stored credentials regardless.
- **2.8 Session gating** — `App` checks `/api/me` once on load (phases: loading / anon / authed),
  so a signed-in user persists across refresh and an expired/invalid session (401) falls back to
  login. Signed-in shell shows the email + a **Log out** control (`POST /api/logout`, clears client
  state). Loading announced via `role="status" aria-live`. Completes the EP-2 frontend; the chat
  screen itself is deferred to EP-3/EP-5/EP-6.

### EP-3 — Bubble Colour Engine
- **Colour decided + stored in the backend; contrast computed in the frontend.** The bubble
  background colour is a *domain decision* (LLM signals → rules → colour) persisted as the source of
  truth (stable, cheap on read, survives `GROQ_API_KEY` revocation) — so it's computed server-side.
  The readable *text* colour depends on the actual painted background (incl. opacity compositing),
  which only the browser knows, so it's computed in the frontend (EP-6).
- **3.1 Colour primitives** — `colors.py`: a frozen `Color(r,g,b)` with `.to_hex()` (the stored
  form), plus pure `clamp`, `lerp`, `lerp_color` (interpolation factor clamped), and a multi-stop
  `ramp(stops, t)` that backs the 3-stop temperature and panic ramps. A corrected take on the
  `review/` module's `_lerp`. Pure/stdlib, 5 unit tests.
- **3.2 TemperatureRule** — `temperature_color(°C)` = `ramp` over stops `[(0, deep blue),
  (15, light purple), (35, bright red)]` (keyed directly on °C, so clamping + the two-segment
  interpolation are free); anchors reused from the `review/` module. `temperature_rule` applies
  only when **both** `city` and `temperature_c` are present (LLM-detected). Uniform rule signature
  `(message, analysis) -> Color | None` for the resolver chain. 4 unit tests.
- **3.3 DecimalRule** — **code-authoritative**: regex `(?<![\w.])\d+\.\d+(?![\w.])` extracts the
  first standalone decimal from the message (excludes version strings / IPs; integers don't match),
  ignoring the LLM's `decimal_value`. First two fractional digits (right-padded, so `0.5`→`50`,
  `3.0`→`00`) map to a grayscale ramp: `.00` `#ECEAE3` lightest → `.99` `#1C1C1C` darkest. 4 unit
  tests including the code-authoritative case (text without a decimal → None even if the LLM
  reported one).
- **3.4 PanicRule** — the 3-level enum maps straight to the brief's named colours (no
  interpolation): `calm` → pale yellow `#F4EDA6`, `neutral` → magenta `#D6219B`, `panicked` →
  violet `#7A1FA2`. `panic_rule` is the **fallback** (always matches); defensive default neutral. 2
  unit tests.
- **3.5 Resolver** — `resolve_bubble_color(message, analysis)` chains the rules strict
  first-match-wins (temperature → decimal → panic) and returns `BubbleColor(color, rule)` — `rule`
  is stored as provenance. Collision + temperature-unit interpretation per Feature 1; the classify
  prompt was tightened so `temperature_c` is set only with a unit/description. 4 resolver tests (14
  total); verified live end to end.
- **3.6 ChatService (compute/attach).** `ChatService.build_reply(message)` composes `analyze()` →
  `resolve_bubble_color()` into `AssistantReply(reply, bubble_color hex, rule, analysis)`. Depends
  on the `LLMClient` interface (DI), imports no psycopg/langchain → unit-tested with a fake LLM (3
  tests). The DB **persistence** of `bubble_color` + provenance lands in EP-5 (message repo + chat
  endpoint), where the conversation/user context exists.

### EP-4 — LLM Backend Integration
- **Provider/framework** — Groq + `openai/gpt-oss-120b` via **LangChain `ChatGroq`** behind the
  stdlib `LLMClient` interface. LangChain chosen (over a raw API call) for `with_structured_output`
  ergonomics, accepting the heavier cold start; it's isolated in `groq_client.py` so the rest of
  the app and tests depend only on the interface + a stdlib `MessageAnalysis` dataclass.
  `GROQ_API_KEY` lives in Vercel env (temporary eval key, Feature 2).
- **Call architecture — two parallel calls via LangGraph fan-out.** `analyze()` runs a focused chat
  `reply` node and a structured `classify` node concurrently (both branch from `START` in one
  super-step, then join) and waits for both — so reply + signals are produced simultaneously. Chosen
  over a single unified call for separation of concerns / per-node **prompts** (REPLY vs CLASSIFY),
  accepting **2× LLM calls** and the `langgraph` dependency weight. The `LLMClient` interface is
  unchanged, so the rest of the app is unaffected.
- **Single model instance + process-wide singleton.** One `ChatGroq` backs **both** graph nodes
  (reply invokes it directly; classify wraps it via `with_structured_output`) — schema-constrained
  classification makes per-node temperatures unnecessary, so a single shared model is simpler.
  `get_groq_client()` is a **lazy module-level singleton**: the model + compiled graph are built
  **once per warm instance** and reused across requests, all paced by the one shared rate limiter
  (so rate limiting is global *within* the instance). DI preserved — services depend on the
  `LLMClient` interface, the composition root supplies the singleton, tests inject a fake.
- **LLM classifies, code decides.** The `classify` node returns signals for all three conditions
  (`city`, `temperature_c`, `decimal_value`, `panic`); the LLM classifies (city/temp/panic need
  understanding; it also reports the decimal), but **code stays authoritative** — it re-validates
  the decimal with a regex (regex wins on disagreement) and owns the rule precedence + collision
  (EP-3). Colour rules stay pure functions fed by signals. Rationale: rule 1 (city) needs world
  knowledge, but rule 2 (decimal) is exact form where regex is strictly safer.
- **4.3 Rate limiting — LangChain `InMemoryRateLimiter` (per-instance, not global).** Attach an
  `InMemoryRateLimiter` to `ChatGroq` to pace LLM calls — stay under Groq's limits and bound
  cost/abuse. Config: **20 req/min** (`requests_per_second=20/60`), `check_every_n_seconds=0.1`,
  `max_bucket_size=20` (burst); **one module-level limiter shared by both `ChatGroq` instances**, so
  20/min is a combined cap that persists across requests on a warm instance.
  **Acknowledged limitation: this is NOT global rate limiting.** The limiter lives in
  process memory, so in serverless it throttles only **per warm instance**; multiple concurrent
  Vercel instances can collectively exceed the intended rate. True global throttling would need a
  **shared store** (e.g. Redis/Upstash), which we deliberately excluded (no Redis). Accepted for
  this scope as a known limitation; a production deployment would move to a shared-store limiter.
- **Persist the colour decision; never recompute on read.** When a message is sent, the computed
  `bubble_color` (plus provenance: matched rule + the signals) is stored on the assistant message
  row. History loads read the stored colour — **no recomputation, no LLM replay**. Three reasons:
  (1) cost/latency — recomputing every historical message per load is absurd; (2) the `GROQ_API_KEY`
  is revoked after ~1 week (Feature 2), so recomputation would *fail* on old messages — stored
  colours keep history rendering; (3) the LLM is non-deterministic, so recomputing could change an
  old bubble's colour — stored = stable. (Implemented in EP-5's chat flow.)
- **Panic representation — 3-level ordinal category, not a float.** The LLM returns
  `panic ∈ {calm, neutral, panicked}` (a constrained enum in the structured schema); code maps it
  to the violet→magenta→yellow ramp: calm → pale yellow, neutral → magenta, panicked → violet.
  Rationale: panic is the model's *subjective* judgment, so a 0–1 float is false precision and less
  reproducible; an ordinal classification is reliable, testable, and aligns 1:1 with the brief's
  three named colours. (Temperature stays continuous — it's a real number the user supplies.)

## Phase 5 — Deployment

- **CI/CD via GitHub Actions** (`.github/workflows/deploy.yml`), not Vercel's native Git
  integration — keeps deploys gated behind our own checks (frontend build + Python compile)
  before shipping, matching the Definition-of-Done "test before deploy" rule.
- **Branch strategy:** push to `dev` → Vercel **Preview** deploy (shareable test URL); push to
  `main` → **Production**. Work happens on `dev`; `main` stays releasable.
- Deploy uses the Vercel CLI with `VERCEL_TOKEN` / `VERCEL_ORG_ID` / `VERCEL_PROJECT_ID` stored as
  GitHub Actions secrets (set once by the repo owner).
- **Stable dev URL via alias** — CLI deploys (vs Vercel's native Git integration) produce a new
  immutable URL per push and **no** `-git-dev-` branch alias, so the host-only session cookie
  appeared "lost" when testing across deploys. Fix: the workflow re-points a stable alias
  (`petasight-chat-dev.vercel.app`) at each dev deployment, so login persists across refresh and
  redeploys. (Production gets its stable domain from `--prod` on main.)
- **Build happens in Vercel's cloud, not prebuilt in CI** — the Python builder uses `uv`, which
  isn't on the CI runner (or a local machine), so `vercel build`/`--prebuilt` fails with
  `spawn uv ENOENT`. Using plain `vercel deploy` lets Vercel build server-side where `uv` exists;
  our CI gate (npm build + `py_compile`) still runs first. Local `vercel dev` needs `uv` installed
  (`brew install uv`).
