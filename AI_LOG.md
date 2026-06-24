# AI_LOG

Running log of AI tooling, the prompts that mattered, and places the AI got it wrong that I had
to correct. Kept current as work happens (see [DEFINITION_OF_DONE.md](DEFINITION_OF_DONE.md)).

## Tools

- **Claude Code** (Opus) — used to interpret the brief, structure the project docs, and pin down
  the color-rule spec and readability approach before writing app code.

## Prompts that mattered

Approach: **lock the target features first, then lock the development phases** — decide *what* the
ASK requires before deciding *how* to build it, recording each in [DECISIONS.md](DECISIONS.md).

Setup
- "Describe the ASK and document it in a proper format" → produced [ASK.md](ASK.md) from
  `public/brief.pdf`.
- "Make a mandatory prerequisite list before any commits / feature completion" → produced
  [DEFINITION_OF_DONE.md](DEFINITION_OF_DONE.md), the deliverable-update gate.
- "Follow a series of steps / template … decisions per step" → set the 5 build phases in
  [CLAUDE.md](CLAUDE.md) and structured DECISIONS by phase.

Stage 1 — lock the target features (Phase 1)
- "Document by feature wise, we have 4 concrete asks" → DECISIONS Phase 1 captures the 4 asks as
  the ASK specifies, spec-only (no approach).
- "Understand the bubble colour and its readability" → contrast check across all three ramps and
  the Feature 1 wording.
- Feature scoping prompts → recorded assumptions: bubble = AI reply div, per-message (no history),
  temporary LLM key, domain-only trust-on-first-use auth, no forgot-password.

Stage 2 — lock the development phases (Phase 2–3)
- "Can Vercel deploy containers / Python serverless / what frontend?" → established Vercel is
  serverless-only; locked **Python functions in `api/`** + **Vite + React (TS)** frontend, one
  repo same-origin, **not** Next.js.
- "Lock Python serverless backend and Neon Postgres" + "no Redis, keep it simple" → locked the
  full stack and the store in DECISIONS Phase 2–3.

## Places the AI got it wrong (corrected)

- **Over-broad gate.** First framing of the Definition of Done implied every commit must touch
  all four deliverables. Corrected to **per-file triggers** — update only the deliverable whose
  trigger fired, don't pad the others.
- **Loose color spec.** Initial restatement treated case 1 as a plain blue→red blend and case 2
  as a whole-number map. Corrected: case 1 is a clamped **3-stop** ramp requiring a city *and* a
  temperature; case 2 uses only the **first two fractional digits**.
- **Documented approach too early.** First Phase 1 write-up recorded our *solution* (the collision
  call, per-bubble computed text color) in the features section. Corrected to spec-only —
  features capture what the ASK requires; our approach is recorded in the phase where we decide it.
- **Missed the provided starter code.** Claimed the `review/` folder wasn't in the repo. It is —
  `public/review/` ships Python (`bubble_service.py` + its test). Corrected; this also signals the
  expected stack leans Python, which feeds the Phase 2 backend decision.

## Where decisions live

Design/judgment decisions are logged in [DECISIONS.md](DECISIONS.md) by build phase, not here —
this file stays scoped to tooling, key prompts, and AI corrections to avoid duplicating it.

- **tsconfig composite mismatch (Task 1).** Scaffolded a referenced `tsconfig.node.json`; `npm run
  build` failed (TS6306/TS6310/TS5096) and the composite project emitted stray `vite.config.js` /
  `.tsbuildinfo` files into the repo. Simplified to a single non-composite `tsconfig.json` +
  `tsc && vite build`. Caught by running the build and inspecting git status, not trusting the
  scaffold.

## Task 1 — deploy pipeline (done)

- Scaffolded a minimal Vite + React (TS) login page + Python `api/health.py` and `api/login.py`
  (domain-gated stub, no DB) to prove the deploy + frontend↔`/api` integration.
- GitHub Actions deploy to Vercel is green (dev → Preview). Verified live on the Preview URL:
  `/api/health` → 200 `{"status":"ok"}`; `/api/login` → 200 (valid), 403 (wrong domain), 400
  (missing fields); `/` serves the frontend.
- **Deployment Protection gotcha:** Vercel Authentication was on by default and returned 401 for
  the whole deployment (frontend included), not just `/api`. Disabled it so the live URL is public.
  Backend access control is enforced in app code (auth), not by hiding the endpoint — the API is
  inherently public once the browser calls it.

## Task 2 — Neon Postgres (done)

- Neon provisioned via the Vercel Marketplace; env vars injected with a `petasight_postgres_`
  prefix. Added `psycopg[binary]`, a self-contained `api/db_health.py` connectivity check, and
  `db/schema.sql` (users/conversations/messages, idempotent).
- Applied the schema to Neon from a throwaway venv using the unpooled connection (`vercel env
  pull` → run → deleted the pulled secrets + venv).
- Verified live on the deployed function: `/api/db_health` → 200 `{"db":"ok","via":
  "petasight_postgres_DATABASE_URL","expected_tables":3}`. psycopg installs fine in the Vercel
  build; runtime connects via the pooled URL.

## Task 3 — stateless backend (in progress)

- **3.1 import de-risk (done).** Probed how Vercel resolves shared modules. Found: the whole
  `api/` tree is bundled, but bare `from _core...` fails at top level — `from api._core.<m> import
  …` works (cwd `/var/task` on sys.path). Locked that convention; removed the probe.
- **2.1 PBKDF2 hashing (done).** Stdlib PBKDF2-HMAC-SHA256, per-password salt, self-describing
  stored format, constant-time verify; 6 unit tests pass. Walked the login data-flow and the
  logout/stateless-revocation tradeoff → recorded as THREATS T1; flagged for final review in
  REVIEW.md.
- **2.2 signed-cookie sessions (done).** Stateless HMAC-signed token (`sub/email/iat/exp/jti`),
  verify signature then expiry, `HttpOnly; Secure; SameSite=Lax`, 1h TTL, injectable secret
  (fails closed); 9 unit tests pass. Discussed bearer-token replay → recorded as THREATS T2;
  chose `SameSite=Lax` and against IP-binding (false logouts for mobile).
- **2.3 user repository (done).** Repository pattern (`UserRepository` Protocol +
  `PostgresUserRepository`), frozen `User` model, shared `db.connect()`. Model mapping
  unit-tested; create/find/get/duplicate integration-tested against live Neon (pulled creds in a
  throwaway venv, row cleaned up, secrets deleted after).
- **2.4 auth service (done).** `AuthService` over the repo interface: domain gate,
  trust-on-first-use, wrong-password rejection (no overwrite), email normalization; outcome enum
  for handler mapping. Extracted `UserRepository` to `repositories.py` (DIP) so the service has
  zero psycopg dependency (verified `psycopg loaded: False`); 6 unit tests with a fake repo.
- **2.5 auth endpoints (done).** login/logout/me wired to `AuthService` + sessions via thin
  handlers + `http_helpers`. Verified live on Preview: 201 create → 200 me → 200 re-auth → 401
  wrong-pw → 403 bad-domain → 400 missing → 200 logout → 401 me. `SESSION_SECRET` set in Vercel
  (Preview/Prod).
- **2.6 auth guard (done).** `authenticate()` (pure) + `require_user()` (handler glue);
  `/api/me` refactored onto it. Verified live: me 200 with cookie, 401 without. 5 unit tests, no
  psycopg. Completes EP-2 backend (2.1–2.6); only the login UI (2.7–2.8) remains.
- **2.7 login form (done).** Accessible `LoginForm` + typed auth client; loading/error states,
  `aria-live` status, autofocus, visible focus rings, `aria-invalid`. Build passes; wired to the
  live `/api/login` (verified in 2.5). Session gating + chat come in 2.8.
- **2.8 session gating (done).** `getMe`/`logout` client; `App` gates on `/api/me`
  (loading/anon/authed), persists across refresh, 401→login, logout clears state + shows shell with
  email + Log out. Build passes. **Completes EP-2.**
- **"Refresh logs me out" — diagnosed as deploy-URL churn, not a bug.** Confirmed the cookie/headers
  are correct and the login→me round-trip works via curl; the cause was a new immutable Preview URL
  per push (CLI deploys give no branch alias) + host-only cookie. Fixed with a stable alias
  (`petasight-chat-dev.vercel.app`) re-pointed by the deploy workflow.

## EP-4 — LLM integration

- **Decisions.** User chose **LangChain** (over a raw call) and to let the **LLM classify** all 3
  signals. Settled the nuance: rule 1 (city) needs world knowledge → LLM; rule 2 (decimal) is exact
  form → regex is safer, so code re-validates the decimal and owns the resolver/collision.
- **4.1 llm client (done).** `LLMClient` interface + stdlib `MessageAnalysis` dataclass +
  `GroqLLMClient` (LangChain `ChatGroq`, `openai/gpt-oss-120b`, `with_structured_output`). LangChain
  isolated in `groq_client.py`. Unit-tested the interface with a fake (no LangChain); added
  `langchain-groq`/`pydantic`. Live `analyze` deferred to 4.2 (needs `GROQ_API_KEY`).
- **4.2 analyze agent (done).** Verified live on Vercel via a temp probe: "Austin 21.5 we need to
  leave right now" → city=Austin, temperature_c=21.5, decimal_value="21.5", panic=0.8, sensible
  reply. The model reported 21.5 as a decimal too (it's the temp) — confirms code must own the
  resolver (rule 1 first-match-wins ignores it). Probe removed.
- **Panic = 3-level ordinal enum (decision + verified).** Chose `{calm, neutral, panicked}` over a
  0–1 float (subjective judgment → false precision; ordinal is reliable/testable and maps 1:1 to
  the brief's 3 colours). Constrained `Literal` in the structured schema. Verified live across
  samples: "leave right now"→panicked, "all good here"→calm, "total came to 42.37"→neutral (decimal
  42.37 also extracted). Probe removed.
- **Two parallel calls via LangGraph (user decision).** Reworked `analyze()` into a LangGraph
  fan-out: `reply` + `classify` nodes branch from START, run concurrently, then join (interface
  unchanged). Verified live: **parallel 0.7s vs sequential 1.75s (~2.5×)**, correct signals.
  Tradeoff: 2× LLM calls + `langgraph` dep. Also decided: **persist `bubble_color` + provenance**;
  history reads stored (never recompute / replay the LLM — also survives key revocation).
- **4.3 rate limiting (done).** `InMemoryRateLimiter` — 20/min (`requests_per_second=20/60`),
  `check_every_n_seconds=0.1`, `max_bucket_size=20`. One **module-level** limiter shared across all
  calls (combined cap, persists across warm-instance requests). Verified the rate-limited client
  still constructs + `analyze()`s live.
- **Singleton + single model instance (user suggestion).** Collapsed the two `ChatGroq` objects to
  one shared by both nodes (classify wraps it via structured output), and added a lazy process-wide
  singleton `get_groq_client()` so model + graph build once per warm instance. Rate limiting is
  global within the instance; DI preserved via the `LLMClient` interface.

## EP-3 — bubble colour engine

- **Backend vs frontend split (discussed).** Bubble background colour = domain decision → computed
  + stored server-side; readable text contrast → frontend (needs the painted/opacity-composited bg).
- **3.1 colour primitives (done).** `colors.py`: `Color(r,g,b).to_hex()`, `clamp`, `lerp`,
  `lerp_color` (clamped factor), multi-stop `ramp()`. Pure/stdlib; 5 unit tests; corrected `_lerp`
  from `review/`.
- **3.2 TemperatureRule (done).** `temperature_color(°C)` via `ramp` over deep-blue/light-purple/
  bright-red stops (review/ anchors); `temperature_rule` needs both city + temp. Uniform
  `(message, analysis) -> Color | None` signature for the chain. 4 unit tests.
- **3.3 DecimalRule (done).** Code-authoritative regex extracts the standalone decimal (ignores the
  LLM's value, excludes versions/IPs); first two fractional digits (right-padded) → grayscale ramp
  `#ECEAE3`→`#1C1C1C`. 4 unit tests incl. the code-wins case.
- **3.4 PanicRule (done).** 3-level enum → named colours: calm `#F4EDA6`, neutral `#D6219B`,
  panicked `#7A1FA2`; fallback rule (always matches). 2 unit tests. All three rules now built.
- **3.5 resolver + temperature-needs-a-unit (done).** `resolve_bubble_color` strict first-match-wins
  (temp→decimal→panic) → `BubbleColor(color, rule)` provenance. **Collision = strict
  first-match-wins** (documented; diverges from the brief's example). User refinement: a bare number
  next to a city is NOT a temperature — tightened the classify prompt. Verified live: "Austin
  21.5"→decimal, "Austin 21.5C" / "21.5 degrees in Austin"→temperature, "the score is 21.5"→decimal.
  14 unit tests.
- **3.6 ChatService compute/attach (done).** `build_reply` composes analyze → resolve into
  `AssistantReply(reply, bubble_color, rule, analysis)`; LLMClient-injected, no psycopg/langchain, 3
  fake-LLM tests. DB persist deferred to EP-5 (needs conversation/message repo).

## EP-5 — conversations, history & isolation

- **5.1 conversation repo (done).** `PostgresConversationRepository` (create / list_by_user / get),
  **every method scoped by user_id**; `get()` ownership-scoped so a non-owner gets None. `Conversation`
  model + unit test. Integration-tested on live Neon incl. isolation (B can't get A's conversation).
- **5.2 message repo (done).** `PostgresMessageRepository` (add / list_for_conversation), history
  filtered by `user_id`; persists `bubble_color` + `color_rule` (added the column via idempotent
  migration to live Neon). `Message` model + unit test; integration-tested incl. message-level
  isolation (B reads nothing from A's conversation). **Closes 3.6's persist half.**
- **5.3 chat service orchestration (done).** `send_message` verifies ownership → compute-first →
  persist user + coloured assistant message; returns None for unowned conversations. DI over repo
  interfaces (no psycopg/langchain); 5 fake-based unit tests.
- **5.4 endpoints (done).** `/api/conversations` + `/api/messages`, auth-guarded, `user_id` from the
  verified cookie only; ownership → 404. Verified live incl. isolation (B→404, no-cookie→401) and
  correct colours.
- **Debugging: deployed app uses a different Neon branch.** Message endpoints 500'd while
  conversations worked. Chased it: `color_rule` existed on the DB `vercel env pull` returned, but the
  deployed app's writes weren't visible there (`conversations count 0` while IDs kept advancing).
  Root cause: Neon's Vercel integration binds Preview deployments to a **separate Neon branch**
  (`ep-orange-truth…` vs the pulled `ep-rough-pine…`) without `color_rule`. Fixed with a temporary
  in-app `/api/db_migrate` endpoint that migrates the app's own branch; confirmed the branch is
  stable across deploys, then removed the endpoint. Lesson: migrate the branch the *app* uses, not
  the one the CLI hands you.
- **5.5 isolation + THREATS (done).** Enforcement already shipped (5.1–5.4); wrote THREATS T3 — the
  per-user isolation threat model (IDOR / identity-injection / cookie-forgery → defenses → live +
  test verification → residual risk). Stretch goal met and proven.
- **5.6 conversations list UI (done).** `ConversationList` sidebar (view/select/create) wired to
  `/api/conversations`; accessible (nav, aria-current, role=status). Two-pane signed-in shell. Build
  green.
- **5.7 message thread + contrast (done; also EP-6 6.6).** `MessageThread` renders user/assistant
  bubbles; assistant gets the engine `bubble_color` with text colour derived via WCAG luminance
  (`readableTextColor`). Verified the contrast picks across all engine colours (danger zones → dark
  text). Bubbles opaque → no compositing needed.
