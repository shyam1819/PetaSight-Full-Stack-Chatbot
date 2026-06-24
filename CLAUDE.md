# CLAUDE.md

Guidance for working in this repo. Read before making changes.

## What this is

PetaSight Full-Stack Engineer take-home: an LLM-backed chatbot where each reply bubble's
background color is decided by the user's message, behind `@petasight.com` API-enforced
sign-in. The full requirements live in [ASK.md](ASK.md) (derived from `public/brief.pdf`).
It is graded on **judgment and the writeups**, not feature count or AI-generated code volume.

## Mandatory gate — before every commit and every "done" feature

Walk [DEFINITION_OF_DONE.md](DEFINITION_OF_DONE.md) first. In short:

- **Update each deliverable whose trigger fired** in the work being committed:
  - `AI_LOG.md` — AI was used / an AI mistake was caught and fixed
  - `DECISIONS.md` — a judgment call was made (esp. the multi-rule color collision)
  - `THREATS.md` — auth, identity, the API surface, or per-user isolation was touched
  - `REVIEW.md` — the `review/` module bugs were worked
- If a trigger did **not** fire, that file legitimately stays unchanged — do not pad it.
- Keep these writeups current **as work happens**, never reconstructed at the end.
- Before committing: confirm deliverables are current, the change was **actually tested**,
  scope is clean (no `.DS_Store`), and the commit message is honest about what changed.

## Build phases (follow in order)

Work through the project in this sequence; don't jump ahead. Record every decision under its
phase in [DECISIONS.md](DECISIONS.md).

1. **Features** — color rules, readability, the collision call.
2. **Architecture** — frontend and backend shape, framework, auth flow.
3. **Temporary store** — where messages/identity live (the per-user isolation store).
4. **Code development** — implement against the locked decisions.
5. **Deployment** — live URL (Vercel), env/secrets.

## Documents

Keep docs simple and short — concise entries over prose. `DECISIONS.md` uses `Decision — Why`
bullets grouped by phase. Don't pad a doc to look thorough.

## Project conventions

- Commit/push only when the user asks.
- Backend rules (email allowlist, per-user isolation) must be enforced **server-side**, never
  trusted from the client.
- UI changes must pass the keyboard + focus criteria in [ASK.md](ASK.md) §4.1: keyboard-only
  operable, readable contrast at every bubble color, and focus is never stolen when a new
  reply appends (announce via `aria-live`, keep focus in the input).
