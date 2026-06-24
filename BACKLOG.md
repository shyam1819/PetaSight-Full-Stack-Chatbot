# Backlog — Epics & Stories

Agile breakdown for transparency. Epics map to the ASK features plus the enabling
infrastructure and the graded deliverables. Stories are the shippable units under each epic.

Status legend: ✅ done · 🔄 in progress · ⬜ todo

## Epics

| ID | Epic | Maps to | Status |
|----|------|---------|--------|
| EP-1 | Deployment & Infrastructure | Enabling (live URL, CI/CD, DB) | ✅ done |
| EP-2 | Authentication & Access Control | Feature 4 (@petasight.com, stateless identity) | ✅ done |
| EP-3 | Bubble Color Engine | Feature 1 (3 rules, collision, readability) | ⬜ todo |
| EP-4 | LLM Backend Integration | Feature 2 (real LLM, panic classification) | ⬜ todo |
| EP-5 | Conversations, History & User Isolation | Messaging + stretch (per-user data) | ⬜ todo |
| EP-6 | Frontend Experience & Accessibility | Feature 3 (login + chat UI, keyboard, focus) | ⬜ todo |
| EP-7 | Security Threat Model & Code Review | Deliverables (THREATS.md, REVIEW.md) | ⬜ todo |

## Epic goals

- **EP-1 — Deployment & Infrastructure.** A public live URL with a gated CI/CD pipeline and a
  provisioned database, so every later change ships and is verifiable. *(Tasks 1–2 complete:
  Vercel + GitHub Actions, Neon Postgres wired, schema applied.)*
- **EP-2 — Authentication & Access Control.** Only `@petasight.com` users get in, enforced at the
  backend with a stateless, server-established session; no signup/reset beyond trust-on-first-use.
- **EP-3 — Bubble Color Engine.** Decide each reply bubble's color from the user's message via the
  first-match-wins rule chain, with the collision call resolved and text contrast guaranteed.
- **EP-4 — LLM Backend Integration.** A real LLM behind a swappable interface, used for the
  panic/calm classification and the chat replies.
- **EP-5 — Conversations, History & User Isolation.** Persist messages per user; list
  conversations, fetch history, send messages — with no cross-user access through the API.
- **EP-6 — Frontend Experience & Accessibility.** Login and chat screens that are keyboard-
  operable, keep focus stable as replies arrive, and stay readable across every bubble color.
- **EP-7 — Security Threat Model & Code Review.** Write the threat model for per-user isolation
  and the review of the provided `review/` module.

## Stories

Each story tagged by layer: **[BE]** backend · **[UI]** frontend · **[Infra]** · **[Docs]**.

### EP-1 — Deployment & Infrastructure ✅
- ✅ 1.1 [Infra] CI/CD: Vercel + GitHub Actions (dev→Preview, main→Prod), gated on build + py-compile
- ✅ 1.2 [BE] Health endpoint + minimal login slice proving frontend↔`/api` same-origin
- ✅ 1.3 [Infra] Provision Neon Postgres; wire pooled (runtime) + unpooled (DDL) creds via Vercel env
- ✅ 1.4 [BE] Schema (users/conversations/messages) + `db_health` connectivity check
- ✅ 1.5 [BE] Lock shared-module import convention (`api/_core`, `from api._core...`)

### EP-2 — Authentication & Access Control 🔄
Backend
- ✅ 2.1 [BE] PBKDF2-HMAC-SHA256 password hashing module (per-user salt, high iterations)
- ✅ 2.2 [BE] HMAC signed-session token (sign/verify) + HttpOnly/Secure/SameSite cookie helpers; `SESSION_SECRET`
- ✅ 2.3 [BE] User repository (find / create by email)
- ✅ 2.4 [BE] Auth service: `@petasight.com` gate + trust-on-first-use + wrong-password rejection
- ✅ 2.5 [BE] Endpoints: `POST /api/login`, `POST /api/logout`, `GET /api/me`
- ✅ 2.6 [BE] Require-auth guard: server-established `user_id` for protected routes

UI
- ✅ 2.7 [UI] Accessible login form wired to `/api/login` (loading + error states)
- ✅ 2.8 [UI] Session-aware gating (authed→chat, logout control, 401 handling)

### EP-3 — Bubble Color Engine 🔄
Backend
- ✅ 3.1 [BE] Color primitives (RGB, clamp, lerp) — reuse the corrected `review/` logic
- ✅ 3.2 [BE] TemperatureRule: city+temp detection, clamped blue→purple→red
- ✅ 3.3 [BE] DecimalRule: standalone decimal, first two fractional digits → grayscale/sepia
- ✅ 3.4 [BE] PanicRule: calm/neutral/panicked → pale yellow/magenta/violet
- ✅ 3.5 [BE] Resolver (first-match-wins chain) + collision decision (strict first-match-wins; temp needs a unit)
- ✅ 3.6 [BE] Attach computed color to the reply (ChatService) + persist `bubble_color`/`color_rule` (message repo)

UI
- ⬜ 3.7 [UI] Apply the returned background color to reply bubbles

### EP-4 — LLM Backend Integration 🔄
Decision: Groq + `openai/gpt-oss-120b` via LangChain `ChatGroq`, behind the `LLMClient` interface.
One structured "analyze" call returns reply + all 3 signals (LLM classifies; code validates the
decimal and owns the resolver).
Backend
- ✅ 4.1 [BE] `LLMClient` interface (stdlib) + `GroqLLMClient` (LangChain `ChatGroq`); deps + `GROQ_API_KEY` env
- ✅ 4.2 [BE] "analyze" agent — LangGraph fan-out: parallel reply + classify (signals: city, temperature_c, decimal, panic); live-verified
- ✅ 4.3 [BE] Rate limiting on the Groq client via LangChain `InMemoryRateLimiter` (20/min, check 0.1s, burst 20; module-level shared across both ChatGroq; per-instance in serverless — global would need a shared store)
- ⬜ 4.4 [BE] (Bonus) RTL philosopher persona reply: original script + English translation

### EP-5 — Conversations, History & User Isolation 🔄
Backend
- ✅ 5.1 [BE] Conversation repository (create, list by `user_id`)
- ✅ 5.2 [BE] Message repository (insert, fetch history) — every query filtered by `user_id`
- ✅ 5.3 [BE] Chat service: send → verify ownership → persist user msg → color → LLM reply → persist
- ✅ 5.4 [BE] Endpoints: list/create conversations, get history, send message (auth-guarded)
- ⬜ 5.5 [BE] Per-user isolation enforcement: ownership checks, identity from session not client (stretch)

UI
- ⬜ 5.6 [UI] Conversations list (view, select, create new)
- ⬜ 5.7 [UI] Message thread (load history, render user/assistant bubbles)
- ⬜ 5.8 [UI] Send-message flow integrated with the backend

### EP-6 — Frontend Experience & Accessibility ⬜
UI
- ⬜ 6.1 [UI] App shell + login↔chat navigation (auth-aware)
- ⬜ 6.2 [UI] Chat layout (thread + composer)
- ⬜ 6.3 [UI] Keyboard operability (tab order, visible focus rings, Enter-to-send)
- ⬜ 6.4 [UI] Focus management: focus stays in input on new reply (no yank)
- ⬜ 6.5 [UI] `aria-live="polite"` thread announcements
- ⬜ 6.6 [UI] Per-bubble readable text contrast (luminance-based; account for opacity composite)
- ⬜ 6.7 [UI] Aesthetics: chat background + bubble opacity (the deferred styling)

### EP-7 — Security Threat Model & Code Review ⬜
- ⬜ 7.1 [Docs] THREATS.md — isolation attack/defense and why it holds
- ⬜ 7.2 [Docs] REVIEW.md — review the provided `review/` module (bugs + fixes)
- ⬜ 7.3 [BE] Harden/lock any isolation or exposed-endpoint gaps found
