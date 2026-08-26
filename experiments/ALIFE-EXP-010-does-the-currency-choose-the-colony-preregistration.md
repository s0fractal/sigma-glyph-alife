# ALIFE-EXP-010 — does the currency choose the colony? Matter-priced against energy-priced duplication

**Preregistration. No measurement has been taken.** Non-normative.

**Written to be implemented by somebody who has not seen a harness for it**, and
by an author who will not write that harness. This document is the whole
specification; if it is not enough, that is a defect in it rather than a
question for its author. Missing choices are recorded in `DECISIONS.md` before
the measurement runs, per the ALIFE-EXP-005 arrangement.

## Why this experiment exists

Combinatory Chemistry (Kruszewski & Mikolov, arXiv:2103.08245v3, read at full
text pp. 1–10 — see [`reviews/claude-fable-2026-08-26.md`](../reviews/claude-fable-2026-08-26.md))
prices duplication in **matter**: an S-reduction fires only if a physical copy
of the duplicated argument already exists in the multiset as a reactant, and
that copy is consumed. Book I prices duplication in **energy**: `R-S` charges
ATP and conjures the copy. Same act, two currencies — and no experiment in
either literature has held everything else fixed and varied only the currency.

The bridge is cleaner here than it could be anywhere else: in a
content-addressed population, "a copy of `z` exists" is a census question about
one hash. K&M's matter condition becomes an address-count condition.

`H-CURRENCY`: the choice of currency is visible in what the colony becomes —
the two pricings select different attractors, different survivorship, and
different reaction economies, at matched total resources.

## The two arms

- **Arm E (energy)** — the ALIFE-EXP-007 chemistry **verbatim**: its reaction
  rules, its parameters as recorded in its receipt, its founders. Nothing
  changes. This arm must reproduce EXP-007's frozen numbers on matching seeds
  (control C3), which is what makes it an arm rather than a new experiment.

- **Arm M (matter)** — identical in every respect except the pricing of
  duplication:
  - An `R-S` whose duplicated argument has hash `h` is **affordable only if
    the population census holds at least one other living molecule whose
    current materialization hash equals `h`** — a different individual, not
    the substrate itself. That individual is **consumed**: removed from the
    census with death-cause `consumed`, distinct from every existing
    death-cause.
  - The ATP charge for that `R-S` is the action floor, `1`.
  - The consumed individual's remaining ATP **transfers in full to the
    duplicating agent**. Totals are conserved; this is exactly the
    redistribution covered by `transfer_preserves_bound`
    (`proofs/Population.lean`), which is why this design and not dissipation:
    the memory-bound theorem holds without new proof work.
  - **Genesis atoms are freely available.** Duplicating `I`, `K`, or `S`
    requires no consumption and costs the floor. Book I resolves genesis
    without a store; K&M keep elementary combinators in the food set. The two
    conventions agree, so this is inherited, not invented.
  - An `R-S` blocked for want of a copy is **not a death**: the agent enters
    the waiting state ALIFE-EXP-009 established for unresolved delivery, spends
    nothing while waiting, and resumes if a copy later appears — priced wait,
    zero ATP, per `resumption_bound`. EXP-009 measured that machinery; this
    arm is its first load-bearing use outside delivery.

Matched between arms: founders (EXP-001's corpus, fingerprint
`53cc6da80f66d220`), total ATP, tick and slice schedule, reaction rules,
seeds. Different between arms: the pricing of `R-S`, and nothing else.

**Seeds, pinned now:** `20260825`, `20260826`, `20260827`.

## What is already decided, and will not be claimed as a finding

- **That the arms differ.** Of course a machine with a different affordability
  rule behaves differently. Which attractors, which survivorship, which
  economy — those are open; "M ≠ E" is not.
- **That the bound holds in Arm M.** Consumption plus full transfer is
  conservation-preserving redistribution; `transfer_preserves_bound` already
  covers it. A violation is a bookkeeping bug, not a discovery.
- **That waiting is free.** EXP-009 measured 0 ATP while waiting and 100%
  answer stability. Re-deriving that here is not a result.

## Hypotheses — attributed to Claude Fable 5, filed before any harness

- **H1 (the currencies pick different colonies).** The Jaccard overlap between
  the sets of surviving molecule hashes in Arm E and Arm M at the final tick is
  **< 0.5 in at least 2 of 3 seeds**. *Falsifier:* overlap ≥ 0.5 in at least
  2 of 3 — the currency is an implementation detail and the attractors are the
  chemistry's alone.
- **H2 (matter-pricing cannibalizes).** Arm M ends with a strictly smaller
  living census than Arm E in **3 of 3 seeds**, and strictly fewer distinct
  hashes in **at least 2 of 3** — because every duplication of a non-genesis
  term eats a colony member, and EXP-001 showed the population's sharing (the
  supply of consumable copies) is spent by evaluation over the run.
  *Falsifier:* census or diversity in M matches or exceeds E at those
  thresholds.
- **H3 (the self-pricing-out curve bends).** D72 measured reaction success
  falling 54% → 16% at fixed per-reaction budget as products accumulate
  structure. In Arm M the ATP not spent on duplication remains available for
  other work, so the fall is slower: final-window success rate in M exceeds E
  by **≥ 10 percentage points in at least 2 of 3 seeds**. *Falsifier:* within
  ±10 points, or lower — the currency does not reach the affordability
  frontier.

A slot for other voices stays open until the harness first runs on any seed;
later filings score nothing.

## Nulls — preregistered here, per the D50 lesson

Any organization-flavored claim made from either arm is reported against
**both** nulls of ALIFE-EXP-008, computed by the same code path for both arms:

1. the full-shuffle null;
2. the locality-preserving null — the one that killed EXP-008's H1.

H1–H3 above are census and economy claims and do not themselves need the
nulls; the nulls are preregistered so that any *post-hoc* organization
observation (a D72-style attractor found in either arm) can be scored
immediately instead of after the fact, which was D50's defect.

## Controls, each of which must pass before a number is recorded

1. **C1 — the ledger balances in both arms**, every tick, including the
   consumed-transfer: the consumed individual's ATP appears in the duplicator's
   balance the same tick, and total ATP is constant up to the chemistry's
   already-accounted flows.
2. **C2 — consumption actually fires.** At least 50 `consumed` deaths per seed
   in Arm M. Fail-closed: EXP-002's memo fired once on a corpus that never
   asked, and adjudicated nothing; a currency experiment where the currency is
   never exercised is not one.
3. **C3 — Arm E reproduces ALIFE-EXP-007's frozen numbers** exactly on the
   seeds the two share. Otherwise Arm E is a new chemistry and the comparison
   is invalid.
4. **C4 — determinism.** Each arm, each seed, run twice: identical receipts.
5. **C5 — the corpus is EXP-001's**, by fingerprint `53cc6da80f66d220`.
6. **C6 — waiting spends nothing.** Every blocked-duplication wait in Arm M
   records 0 ATP while waiting, and every resumed agent's answer hash matches
   an uninterrupted evaluation of the same term — the EXP-009 property,
   re-asserted where it is now load-bearing.
7. **C7 — census accounting is total.** Every individual ever alive is
   accounted as settled, starved, waiting, culled, or `consumed`, and the
   counts reconcile per tick. A consumed body that also appears alive is a
   disqualifying defect.
8. **C8 — saturation is reported.** Any cap hit (waits outstanding at final
   tick, transfer overflow guards) appears in the receipt with a count.

## What would make this experiment worthless

- Reporting "M differs from E" as the finding. That is the null of the design.
- Letting Arm M's blocked duplications die instead of wait, which would
  conflate currency with mortality and measure neither.
- Adjudicating H1 on hash sets that include genesis atoms — the EXP-004
  lesson: genesis is the alphabet, not the structure. H1's hash sets exclude
  genesis atoms.
- Any organization claim not scored against both preregistered nulls.
- Concluding anything about Combinatory Chemistry itself. Arm M is
  K&M-*inspired* pricing inside this substrate; their reactor, rates, and
  Gillespie dynamics are not simulated, and nothing here validates or
  invalidates their results.

## Provenance — the arrangement, stated at its real strength

Preregistration by Claude Fable 5, who will not write the harness. The harness
author works from this committed document, the repository, and its
dependencies only, records missing choices in `DECISIONS.md` before running,
and writes the RESULT judged against this document. This is the ALIFE-EXP-005
arrangement: a real separation of roles between different models, not an
independent registry, external review, or statistical replication — and the
RESULT's provenance section must say so in those words.
