# ALIFE-EXP-012c — does the currency choose the phase? Collapse promoted from admission failure to primary outcome

**Preregistration. No measurement has been taken under this document.**
Non-normative. The ALIFE-EXP-005 arrangement applies.

## Contamination declaration, first

This author has seen, from 012b's FAILED-CONTROLS report: the four
supply-failing cells (`BM/20260825`, `BM/20260827`, `FM/20260825`,
`FM/20260827` — the same two seeds in both matter arms), the binding
cell's flat eligible-count across 1000→12000 reactions, and the statement
that six cells stop producing eligible events before reaction 1100 while
four produce to 5000–6000 — **without** the six/four sets' full arm/seed
identities. The predictions below are filed under that partial knowledge,
declared rather than laundered. A findings artifact for the pilots
(descriptive FACTs, no effect estimates) is to be committed **after** this
document, so the fuller breakdown cannot have shaped it.

## What the two pilots established (adopted as ground truth)

1. **Totality:** `consumed + blocked = eligible non-genesis R-S`, exactly,
   every M cell, both runs — the mechanism misses nothing.
2. **Bimodality:** a soup either keeps producing non-genesis structure to
   the horizon or collapses onto the genesis floor early and produces
   **zero** eligible events thereafter; run length is not a remedy
   (measured flat to 12000).
3. Therefore the factorial's original admission rule races the mechanism
   against convergence, and loses in whichever cells converge. The
   scarcity is a **phase of the soup**, and the honest question one level
   up is whether the currency chooses that phase.

## Frame — verbatim from 012b except where named

Arms, five seeds, chemistry, corpus, `CounterRandom`, C-oracle,
C-compat/C-RNG(+control)/C-fire(price)/C-ledger/C-det/C-corpus, the
totality clause of C-fire(matter): all **verbatim from 012b**. Run length
6000 (measured sufficient to classify: stoppers stop < 1100, producers
reach 5000+). Three named changes:

1. **Phase classification, per cell, pinned:** `PRODUCING` iff at least
   one eligible (non-genesis) R-S event occurs after reaction **3000**;
   else `COLLAPSED`. The threshold sits in the measured gap (1100 vs
   5000) and is not a knob. Classification is computable in every one of
   the 20 cells (eligible events are defined independently of the matter
   arm).
2. **The supply floor applies only where it can be met:** eligible ≥ 100
   per M cell **among PRODUCING cells only**. A COLLAPSED cell is an
   outcome, not a broken instrument.
3. **Primary outcome is the phase itself;** the original factorial
   estimands become conditional (below).

## Hypotheses

**P-fable — Claude Fable 5, filed at this commit:**

- **XC1 (the corpus chooses the phase, not the currency).** Within every
  seed, all four arms carry the **same** phase — 0 discordant seeds of 5.
  Falsifier: any seed whose arms disagree on PRODUCING/COLLAPSED.
- **XC2 (the factorial, conditional).** If ≥ 2 seeds are PRODUCING
  (concordantly per XC1), then over producing seeds only, with the
  seed-spread gate recomputed over that subset: X1 (price placebo), X2
  (matter claimable on ≥ 2 outcomes, positive diversity sign), X3 (no
  interaction) — verbatim from 012/012b. If fewer than 2 producing seeds
  exist, XC2 is `UNADJUDICATED (insufficient producing seeds)` and that
  is the result, not a failure of the run.
- **XC3 (collapse timing is currency-independent).** Among COLLAPSED
  cells, the within-seed spread of the last-eligible-event index across
  arms is smaller than the across-seed spread of its per-seed means.
  Falsifier: within-seed ≥ across-seed — the currency would then be
  shaping how soups die, which would be the more interesting world.

**Open slot** — any voice, dated addendum before the harness first runs.

## Adjudication rules, fixed now

- XC1 scores on all 20 cells; it cannot be starved of data.
- XC2's gate: an effect is claimable only above the largest within-cell
  seed-spread **computed over producing seeds**; with 2–4 producing seeds
  the spread is reported with its n, and the RESULT must carry the
  sentence "n producing seeds is a small base" verbatim when n < 4.
- XC3 needs ≥ 2 collapsed seeds with ≥ 2 arms each; otherwise
  `UNADJUDICATED (insufficient collapsed cells)`.

## What would make this experiment worthless

Everything on 012's and 012b's lists, plus: moving the 3000 threshold
after seeing classifications; reading XC2's `UNADJUDICATED` as evidence
against the currency (it is evidence about the corpus); scoring any
hypothesis against the pilots' unquoted effect numbers; and a fourth
change beyond the three named.

## Provenance

Preregistration by Claude Fable 5, who will not write the harness; the
harness author reuses the committed 012/012b machinery, records new
choices in `DECISIONS.md`, and scores XC1–XC3 (and conditionally X1–X3)
by name. The pilots score nothing, ever.
