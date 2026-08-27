# ALIFE-EXP-012b — the currency factorial, with an admission rule that measures the right thing

**Preregistration. No measurement has been taken.** Non-normative. The
ALIFE-EXP-005 arrangement applies; the author of this document will not
write the harness.

## Why a successor, and whose defect it is

EXP-012's first harness run ended **FAILED-CONTROLS** (commit `b8bf698`):
C-fire(matter)'s floor of ≥ 50 consumptions per M cell failed in 3 of 10
cells. The floor was this author's defect: it was calibrated against
EXP-010's counts, which came from a **correlated** RNG stream — and
removing that correlation was the entire point of the factorial. The
harness's diagnostic is adopted as the ground truth of this document:
`consumed + blocked = R-S fired − R-S on genesis`, **exactly**, in every M
cell — the mechanism fires on every eligible event; what is scarce is the
eligible events themselves (65–91% of duplications hit genesis atoms,
free by the preregistered rule).

Per rule 3, EXP-012's run is reclassified as the **calibration pilot**: it
scores nothing, ever, and its measured eligible-event rates (22–190 per
1000 reactions per M cell) are the calibration inputs below. X1–X3 were
never adjudicated there and are re-filed here unchanged.

## Changes from EXP-012 — exactly two; everything else is incorporated verbatim by reference

1. **Run length: 6000 reactions per cell** (was EXP-007's 1000). Derived
   from the pilot: the worst M cell produced 22 eligible events per 1000
   reactions; 6000 puts its expectation at ~132, above the floor below
   with margin. The number is pinned now and is not a knob.
2. **C-fire(matter), corrected — two clauses, both fail-closed:**
   - **totality:** `consumed + blocked = R-S fired − R-S on genesis`,
     exactly, per M cell (the pilot's identity — the mechanism misses
     nothing eligible);
   - **supply:** eligible (non-genesis) R-S events ≥ **100** per M cell —
     a statistical-power floor on the *event base*, which is what the old
     floor was mistakenly pointed at the mechanism about.

Arms, seeds (`20260825`–`20260829`), chemistry, corpus
(`53cc6da80f66d220`), counter-based RNG design (D101–D102's
`CounterRandom`, already committed), estimands, the seed-spread gate, all
other controls (C-compat, C-RNG with its negative control, C-fire(price),
C-ledger, C-det, C-corpus), and the worthlessness list: **verbatim from
[`ALIFE-EXP-012-the-currency-factorial-preregistration.md`](ALIFE-EXP-012-the-currency-factorial-preregistration.md)**,
with every per-1000-reactions expectation scaled by 6.

## Predictions — re-filed unchanged

**P-fable — Claude Fable 5, identical to EXP-012's X1–X3:**

- **X1** — the price main effect on settled count is within the
  seed-spread gate (price is a placebo at lazy prices).
- **X2** — the matter main effect is claimable on ≥ 2 of 4 outcomes, with
  a positive diversity sign for M.
- **X3** — the interaction is within the gate on every outcome.

Falsifiers as in EXP-012. **Open slot** for other voices until the
harness first runs on any cell.

## One added control

**C-oracle.** The pilot found the sibling oracle drifting mid-session
(D109). Every 012b receipt must be produced against the repository's
pinned oracle digest (`413d1f98…` at pin `d3f1b512`), asserted at start
and end of the run; a drift mid-run invalidates the run, not the pin.

## What would make this experiment worthless

Everything on EXP-012's list, plus: treating the pilot's unquoted
factorial numbers as priors anywhere in the RESULT — they were produced
under a failed admission rule and are not evidence; and any third change
beyond the two named above.
