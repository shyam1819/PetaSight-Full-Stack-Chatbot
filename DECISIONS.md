# DECISIONS

Decisions by build phase (see phases in [CLAUDE.md](CLAUDE.md)). Format: `Decision — Why`.
Kept current as work happens. Pending phases are listed but empty until we reach them.

## Phase 1 — Features

- **Case 1 needs both a city and a temperature** — a bare number isn't case 1; it falls to case 2.
- **Case 1 is a clamped 3-stop ramp** (blue ≤0°C → purple ~15°C → red ≥35°C) — the purple
  midpoint is a real anchor, not a blue→red blend.
- **Case 2 uses only the first two fractional digits** (`42.37` → `.37`) — integer part is ignored.
- **Only case 3 calls the LLM; cases 1–2 are parsed locally** — keeps the deterministic paths
  testable and cheap, reserves the model for the genuinely fuzzy signal.
- **Text color is computed per bubble from background luminance, never fixed** — no single text
  color clears WCAG 4.5:1 across all three ramps; verified contrast across every swatch.
- **Collision call (the graded one): panic wins on genuine overlap** — when a message is city+temp
  *and* reads as urgent (e.g. "Austin 21.5 we need to leave right now"), color the thing that
  matters to a human, not the first regex hit. Exact override condition finalized when the matcher
  is built. (`42.37` → case 2; `"Austin 21.5"` → case 1 — settled by the rules above.)

## Phase 2 — Architecture (frontend / backend)

_Pending._

## Phase 3 — Temporary store

_Pending._

## Phase 4 — Code development

_Pending._

## Phase 5 — Deployment

_Pending._
