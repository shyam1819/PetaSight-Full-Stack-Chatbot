# DECISIONS

Judgment calls and the reasoning behind them. Kept current as work happens (see
[DEFINITION_OF_DONE.md](DEFINITION_OF_DONE.md)). The headline call the brief grades — the
multi-rule color collision — is **D2** below.

## D1 — Color-rule detection precision

The brief states the three rules loosely; we pinned down the exact behavior so the build is
unambiguous:

- **Case 1 needs both a city and a temperature.** A bare number that looks like a temperature
  is *not* case 1 — it falls through to case 2. This matters for the collision in D2.
- **Case 1 is a clamped 3-stop ramp.** Deep blue at ≤0°C, light purple at the ~15°C midpoint,
  bright red at ≥35°C. Values outside 0–35 clamp to the endpoints. It is not a 2-color blend —
  the purple midpoint is a real anchor.
- **Case 2 uses only the first two fractional digits.** The integer part is ignored
  (`42.37` → `.37`), mapped `.00` lightest → `.99` darkest on a grayscale ramp.
- **Cases 1 and 2 are deterministic and parsed locally; only case 3 calls the LLM.** Keeping the
  LLM out of the deterministic paths makes them testable and cheap, and reserves the model for
  the genuinely fuzzy signal (panic).

## D2 — The multi-rule collision (the part they read for)

> **Status: decided in principle, to be finalized when the matcher is built.**

A message can satisfy more than one rule at once. The brief's example —
*"Austin 21.5 we need to leave right now"* — is simultaneously a city+temp (case 1), a
standalone decimal (case 2), and panicked (case 3). The brief gives "first match wins" but
explicitly asks whether order alone is right, or whether one signal should *win for a reason*.

What's already settled by D1's precision:
- `42.37` alone → **case 2** (no city, so case 1 never matches).
- `"Austin 21.5"` → **case 1** (city + temperature present), even though `.21`/`.5` is also a
  valid decimal — case 1's match consumes it.

**The open question** is the genuine three-way overlap (city + temp + audible panic). The
candidate answer to write up and build: **let the panic/safety signal win when the message
reads as urgent**, on the reasoning that a panicked "we need to leave right now" is the user's
actual intent and the temperature is incidental context — color should communicate the thing
that matters most to a human reading the thread, not the first pattern a regex happens to hit.
This will be finalized (with the exact override condition) when the matcher is implemented, and
the chosen case will be named here with a walk-through.

## D3 — Readability: text color is computed per bubble, never fixed

Because the background is dynamic across three ramps, **text color is derived from each
bubble's background luminance** (compute relative luminance, pick the higher-contrast of
black/white) rather than hardcoded. Rationale and evidence:

- No single text color clears WCAG 4.5:1 across all three ramps. Light purple (~15°C), pale
  yellow (calm), and the `.00` end of the decimal ramp need **dark** text; deep blue, violet,
  and the dark decimal end need **light** text.
- We verified the swatch-by-swatch contrast across all three ramps before committing to this
  approach — danger zones flip to dark text exactly as expected.
- Consequence for the **background** ramps: keep endpoints/midtones out of muddy mid-gray,
  where neither black nor white passes 4.5:1. If a swatch can't pass with either text color,
  the fix is to adjust the background, not the text.

See acceptance criteria in [ASK.md](ASK.md) §3.1 and §4.1.
