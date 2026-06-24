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
  verify signature then expiry, `HttpOnly; Secure; SameSite=Lax`, 8h TTL, injectable secret
  (fails closed); 9 unit tests pass. Discussed bearer-token replay → recorded as THREATS T2;
  chose `SameSite=Lax` and against IP-binding (false logouts for mobile).
