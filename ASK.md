# ASK — PetaSight Full-Stack Engineer Take-Home

> Source: [`public/brief.pdf`](public/brief.pdf). This document restates the brief as a
> structured ASK so requirements, deliverables, and acceptance criteria are unambiguous.
> Where the brief is deliberately vague, that is called out — it is not an omission to fix here.

## 1. One-line summary

Build and deploy a **chatbot backed by a real LLM** where **each reply bubble's background
color is decided by what the user typed**, gated behind **@petasight.com sign-in enforced at
the API**, and explain the **judgment calls** in a set of writeups.

## 2. Context & intent

- Budget ~60 minutes. AI is expected to write most of the code; **that is not what is being
  evaluated**.
- What *is* evaluated: judgment on top of the AI — catching it when it's wrong, handling a
  fuzzy spec, and checking your own work.
- Finishing everything is **not** expected. A focused, well-reasoned partial submission beats
  a rushed full attempt. **Prioritize and go deep on something.**
- The submission is read on its own with no call — the **writeups carry the weight**.

## 3. What to build

A chatbot with a **live URL** (Vercel or anywhere) and a **public repo**.

### 3.1 Reply-bubble color rules (first match wins, checked in order)

| # | Trigger | Color mapping |
|---|---------|---------------|
| 1 | A **city + a temperature in °C** | Deep blue → bright red by temperature: deep blue at **≤0°C**, light purple at **~15°C**, bright red at **≥35°C** |
| 2 | Otherwise, a **standalone decimal number** | Grayscale or sepia ramp from the **first two decimal digits**: `.00` lightest → `.99` darkest |
| 3 | Otherwise, **ask the LLM** how urgent/panicked it sounds | Violet (high panic) → magenta → pale yellow (completely calm) |

> ⚠️ **The deliberately underspecified part (the part they actually read for):** a single
> message can satisfy more than one rule at once — e.g. *"Austin 21.5 we need to leave right
> now"* is a city+temp, a standalone decimal, **and** panicked. "First match wins" is given,
> but the ask is to **decide whether order alone is right, or whether one signal should win
> for a reason** — pick an answer, build it, and justify it in `DECISIONS.md`. Do **not** ask
> for clarification.

## 4. Hard requirements (must-have)

- [ ] **Real LLM on the backend** — no canned replies. (May be shut off a week after sending.)
- [ ] **Keyboard-accessible & readable** — works via keyboard; text stays readable as the
      background color shifts. **They will open the app and check this themselves.**
- [ ] **Focus management** — when a new reply appends to the thread, a keyboard user must
      **not lose their place or get yanked around**.
- [ ] **Sign-in restricted to `@petasight.com`** — and the rule is **enforced at the backend
      endpoint**, not just on the login page.

## 5. Stretch (optional — fine not to reach)

- [ ] **Per-user chat history isolation.** Messages stored per user. A signed-in user must not
      read or modify another user's messages **through the API**, even with their own valid
      `@petasight.com` session.
- [ ] Identity must be **established server-side**, never taken from the client.
- [ ] This is the **deepest part of the test**. If only partway done, state where you got to
      and how you'd close the gap in `THREATS.md`.

## 6. Bonus (only if enjoying it)

- [ ] Bot replies in a **right-to-left language**, in the voice of a **historical philosopher/
      scientist from that culture** — original script first, then an English translation.

## 7. Required deliverables (writeups)

| File | Purpose |
|------|---------|
| `AI_LOG.md` | Tools used, the few prompts that mattered, and **a couple of places the AI got it wrong** that you had to fix. |
| `DECISIONS.md` | The multi-rule collision call: **name the case you chose** and walk through the reasoning. |
| `THREATS.md` | How one signed-in user could reach another's messages via the API, the defense (built or proposed), and **why you're convinced it holds**. Write it even if isolation was only partially built. |
| `REVIEW.md` | The `review/` folder ships a small module + test with **a few bugs**. State what's broken, why, and how you'd fix it. |

> Note: the `review/` folder is referenced by the brief but **not yet present** in this repo.

## 8. How it will be evaluated

Judgment over completion. Specifically:
- How the **ambiguous (multi-rule) case** is handled.
- Reasoning about **who can touch whose data**.
- How you **read someone else's code** (the `review/` module).
- Whether you **tested your own work**.
- **Not** how many features were packed in.

## 9. Acceptance checklist (condensed)

- [ ] Live URL + public repo
- [ ] Color rule 1 (city + °C) correct across the 0 / 15 / 35 anchors
- [ ] Color rule 2 (standalone decimal) ramp by first two decimals
- [ ] Color rule 3 (LLM panic/calm) violet → magenta → pale yellow
- [ ] Multi-rule collision resolved + justified in `DECISIONS.md`
- [ ] Real LLM backend
- [ ] Keyboard operation + readable contrast at every color
- [ ] No focus disruption on new bubbles
- [ ] `@petasight.com` enforced at the API
- [ ] (Stretch) server-established identity + per-user API isolation
- [ ] `AI_LOG.md`, `DECISIONS.md`, `THREATS.md`, `REVIEW.md` written
