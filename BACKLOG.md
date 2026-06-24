# Backlog — Epics & Stories

Agile breakdown for transparency. Epics map to the ASK features plus the enabling
infrastructure and the graded deliverables. Stories are the shippable units under each epic.

Status legend: ✅ done · 🔄 in progress · ⬜ todo

## Epics

| ID | Epic | Maps to | Status |
|----|------|---------|--------|
| EP-1 | Deployment & Infrastructure | Enabling (live URL, CI/CD, DB) | ✅ done |
| EP-2 | Authentication & Access Control | Feature 4 (@petasight.com, stateless identity) | 🔄 in progress |
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

_To be defined per epic (next step)._
