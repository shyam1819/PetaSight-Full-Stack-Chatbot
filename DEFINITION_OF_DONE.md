# Definition of Done — Mandatory Pre-Commit / Pre-Feature Gate

> **This gate is mandatory.** No commit is made and no feature is called "done" until this
> list has been walked. The deliverable writeups (`AI_LOG.md`, `DECISIONS.md`, `THREATS.md`,
> `REVIEW.md`) must be kept current **as work happens**, not reconstructed at the end — the
> brief grades the writeups on their own, so a stale writeup is a real defect.

## 0. The rule, in one line

Before **every** commit and before declaring **any** feature complete: walk the table below,
and **update every deliverable whose trigger fired** in the work you're about to commit.

## 1. Deliverable update triggers

Update the file **whenever its trigger applies** to the change being committed.

| Deliverable | Update it when… | What to add |
|-------------|-----------------|-------------|
| `AI_LOG.md` | You used AI to produce or change code/docs in this commit | The prompt(s) that mattered, and **any place the AI got it wrong** that you caught and fixed |
| `DECISIONS.md` | You made a non-obvious judgment call — especially the multi-rule color collision, but also any spec ambiguity you resolved | Name the case, the option chosen, and the reasoning |
| `THREATS.md` | You touched auth, sign-in, the API surface, identity, or per-user data isolation | The attack considered, the defense (shipped or proposed), and why you believe it holds |
| `REVIEW.md` | You worked through the `review/` module's bugs | What's broken, why, and the fix |

If a trigger did **not** fire, that file legitimately stays unchanged for this commit — that is
expected, not a violation.

## 2. Pre-commit checklist (run every time)

- [ ] **Deliverables current** — every file whose trigger fired above is updated in this commit.
- [ ] **No deferred writeup debt** — there is no judgment call or AI miss from this session that
      still needs to be written down "later."
- [ ] **Self-checked** — the change was actually run/tested, not just assumed to work
      (the brief explicitly grades whether you checked your own work).
- [ ] **Keyboard + focus** — if UI changed, it was tested with the keyboard only and focus is
      not stolen on new bubbles (see [ASK.md](ASK.md) §4.1).
- [ ] **Scope-clean** — only intended files are staged (e.g. no `.DS_Store`).
- [ ] **Message honest** — the commit message states what actually changed, including which
      deliverables were updated.

## 3. Definition of Done for a feature

A feature is done only when **all** of the following hold:

- [ ] It works end-to-end and was verified by actually exercising it.
- [ ] Accessibility/focus criteria in [ASK.md](ASK.md) §4.1 pass (if UI).
- [ ] Backend rules are enforced server-side, not just client-side (if applicable).
- [ ] Every deliverable trigger the feature fired has been satisfied (§1).
- [ ] The acceptance items it covers in [ASK.md](ASK.md) §9 are checked off.

## 4. Why this exists

The take-home is read with no call; the writeups carry the weight. Updating them continuously
keeps them accurate and prevents the end-of-session scramble where the reasoning behind a
decision — or the AI mistake you caught three commits ago — has already been forgotten.
