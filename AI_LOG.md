# AI_LOG

Running log of AI tooling, the prompts that mattered, and places the AI got it wrong that I had
to correct. Kept current as work happens (see [DEFINITION_OF_DONE.md](DEFINITION_OF_DONE.md)).

## Tools

- **Claude Code** (Opus) — used to interpret the brief, structure the project docs, and pin down
  the color-rule spec and readability approach before writing app code.

## Prompts that mattered

- "Describe the ASK and document it in a proper format" → produced [ASK.md](ASK.md) from
  `public/brief.pdf`.
- "Make a mandatory prerequisite list before any commits / feature completion" → produced
  [DEFINITION_OF_DONE.md](DEFINITION_OF_DONE.md), the deliverable-update gate.
- "Understand the bubble colour and its readability" → drove a contrast check across all three
  ramps and the feature wording in [DECISIONS.md](DECISIONS.md) Phase 1.

## Places the AI got it wrong (corrected)

- **Over-broad gate.** First framing of the Definition of Done implied every commit must touch
  all four deliverables. Corrected to **per-file triggers** — update only the deliverable whose
  trigger fired, don't pad the others.
- **Loose color spec.** Initial restatement treated case 1 as a plain blue→red blend and case 2
  as a whole-number map. Corrected: case 1 is a clamped **3-stop** ramp requiring a city *and* a
  temperature; case 2 uses only the **first two fractional digits**.

> No application code has been written yet, so there are no code-level AI mistakes to report.
> This section will grow as implementation starts.
