# ALIFE-EXP-012c — result

Judged against [`ALIFE-EXP-012c-does-the-currency-choose-the-phase-preregistration.md`](../ALIFE-EXP-012c-does-the-currency-choose-the-phase-preregistration.md),
committed at `73e1ca2` before this harness existed. The choices that document
left open are `DECISIONS.md` D116–D121, committed before the measurement ran.

**Provenance, stated at its real strength.** The preregistration was written by
Claude Fable 5 and this harness by Claude Opus 5, working only from the committed
documents, the repository and its dependencies, and this is the ALIFE-EXP-005
arrangement — a real separation of roles between different models, not an
independent registry, external review, or statistical replication.

**The ordering the design depends on, verifiable in `git log`.** The
preregistration is `73e1ca2`, timestamped 2026-08-27 08:25:44 +0300. The pilots'
findings artifact — which publishes the full arm/seed identities of the six/four
split — is `3be06b8`, 08:31:00 +0300, **five minutes later**. The
preregistration's contamination declaration says its author had seen the four
supply-failing cells and the six/four counts *without* those identities; the
commit order is what makes that checkable rather than asserted.

**The pilots score nothing, ever.** No number from ALIFE-EXP-012 or 012b is used
as a prior, a threshold or evidence anywhere below. They contribute two measured
facts — totality and bimodality — and no estimates.

## The verdicts

| | | |
|---|---|---|
| **XC1** | the corpus chooses the phase, not the currency | **FAILS** — 4 discordant seeds of 5 |
| **XC2** | the factorial, conditional on producing seeds | **UNADJUDICATED (insufficient producing seeds)** — 0 concordantly producing |
| **XC3** | collapse timing is currency-independent | **FAILS** — max within-seed spread 1255 against an across-seed spread of means of 856.5 |

Two preregistered falsifiers fired. XC3's is the one its author named as the
more interesting world: *"the currency would then be shaping how soups die."*

| | |
|---|---|
| substrate | `impl/sigma_alife.py` 0.1.0 on Σ-GLYPH Book I, oracle sha256 `413d1f9805cdbdf42f13d967a17be26eb959c692eeb067e7146203ed9cebe64d` at sigma-glyph `d3f1b512` |
| arms | BF (Book price, copy free) · BM (Book, consumed) · FF (floor, free) · FM (floor, consumed) |
| frame | 5 seeds × 4 arms, 6000 reactions, capacity 64, 200 ATP/reaction; corpus `53cc6da80f66d220` |
| randomness | counter-based, keyed `(seed, reaction_index, event)` |
| phase | PRODUCING iff an eligible (non-genesis) R-S occurs after reaction **3000**, pinned before any cell ran |
| controls | fourteen, all passing before the receipt was written |
| receipt | `results.json`, every cell identical on a second run |

## XC1 — the corpus does not choose the phase alone: **FAILS**

> Within every seed, all four arms carry the same phase — 0 discordant seeds of
> 5. *Falsifier:* any seed whose arms disagree.

| seed | BF | BM | FF | FM | seed phase |
|---|---|---|---|---|---|
| 20260825 | COLLAPSED | COLLAPSED | **PRODUCING** | COLLAPSED | **DISCORDANT** |
| 20260826 | COLLAPSED | COLLAPSED | COLLAPSED | **PRODUCING** | **DISCORDANT** |
| 20260827 | COLLAPSED | COLLAPSED | COLLAPSED | COLLAPSED | COLLAPSED |
| 20260828 | COLLAPSED | COLLAPSED | **PRODUCING** | **PRODUCING** | **DISCORDANT** |
| 20260829 | COLLAPSED | **PRODUCING** | **PRODUCING** | **PRODUCING** | **DISCORDANT** |

**Four of five seeds are discordant**, scored over all 20 cells as the rule
requires. Only `20260827` agrees, and it agrees on COLLAPSED. The falsifier did
not fire marginally: on `20260829` three arms produce and one does not.

Holding the seed fixed and changing only the duplication rule changes whether the
soup keeps producing structure or collapses onto the genesis floor. Whatever
chooses the phase, it is not the corpus alone.

**What the arms did, reported and not scored.** Producing cells per arm:

| arm | price | copy | producing |
|---|---|---|---:|
| BF | Book I | free | **0 of 5** |
| BM | Book I | consumed | **1 of 5** |
| FF | floor | free | **3 of 5** |
| FM | floor | consumed | **3 of 5** |

Both floor-priced arms produce in three seeds; both Book-priced arms produce in
at most one. **No preregistered criterion scores this**, and it is not claimed:
XC1 tests concordance, not direction, and this document preregisters no gate for
a phase-by-arm effect. Twenty cells across five seeds with no null is exactly the
shape of statistic ALIFE-EXP-007 and ALIFE-EXP-008 had destroyed by their nulls.
It is stated because XC1's failure makes "the arms disagree" a finding, and a
reader is entitled to know *how* they disagree — and it is the successor's
question, not this one's answer.

## XC2 — the conditional factorial: **UNADJUDICATED (insufficient producing seeds)**

> If ≥ 2 seeds are PRODUCING (concordantly per XC1), score X1/X2/X3 over
> producing seeds with the gate recomputed on that subset. Fewer than 2 and XC2
> is UNADJUDICATED, "and that is the result, not a failure of the run."

**Zero seeds are concordantly PRODUCING.** Seven of the twenty cells produce,
but they never fill a seed: the closest is `20260829` at three of four. X1, X2 and X3
are therefore not scored here, in any form, and no factorial effect estimate
appears in this receipt.

**Why this is unadjudicated matters, and it is not the reason the
preregistration anticipated.** That document warns against "reading XC2's
UNADJUDICATED as evidence against the currency (it is evidence about the
corpus)" — written for a world where every seed collapsed. That is not this
world. Here the base is empty *because XC1 failed*: the arms of a seed disagree,
so no seed is concordantly anything except `20260827`, which is concordantly
collapsed. The emptiness is a consequence of arm-level discordance, which is
evidence that the currency reaches the phase. Reading it as evidence about the
corpus would be as wrong as the reading the preregistration guards against, in
the opposite direction. It is evidence about **XC1**.

## XC3 — collapse timing is currency-independent: **FAILS**

> Among COLLAPSED cells, the within-seed spread of the last-eligible-event index
> across arms is smaller than the across-seed spread of its per-seed means.
> *Falsifier:* within-seed ≥ across-seed.

Base: seeds carrying at least two COLLAPSED cells with a last-eligible index —
four of the five (`20260829` has only one collapsed arm).

| seed | last-eligible index, per collapsed arm | within-seed spread | mean |
|---|---|---:|---:|
| 20260825 | 899, 625, 435 | 464 | 653.0 |
| 20260826 | 306, 723, 306 | 417 | 445.0 |
| 20260827 | 1833, 706, 1961, 706 | **1255** | 1301.5 |
| 20260828 | 964, 1040 | 76 | 1002.0 |

**Largest within-seed spread 1255** (seed `20260827`) against an **across-seed
spread of the per-seed means of 856.5**. Within exceeds across, so XC3 **FAILS**.

Seed `20260827` is the whole story and it is the seed that passed XC1: all four
arms collapse, and they collapse at 706, 706, 1833 and 1961 — the two Book-priced
arms stop nearly three times earlier than the two floor-priced ones, on identical
founders and identical keyed randomness. Concordance on *whether* a soup dies did
not bring concordance on *when*.

The two arms that share a last-eligible index exactly — BM and FM at 706 on
`20260827`, and BF and FF at 306 on `20260826` — are the pairs that differ only
in price and only in matter respectively, which is the kind of structure a
factorial exists to read. There is no preregistered criterion for it here.

## Controls

Fourteen, all passing before the receipt was written. Eleven are verbatim from
ALIFE-EXP-012b; three are additions this harness needed, named as additions.

| | control | outcome |
|---|---|---|
| **C-oracle(start/end)** | the pinned oracle, asserted at both ends | `413d1f98…` at `d3f1b512`, no drift across a 487-second run |
| **C-RNG** | counter-based draws survive a perturbed history | **827/827** keyed draws before the perturbed reaction and **771/771** after are bit-identical, histories genuinely diverged |
| **C-RNG-control** | the same on a positional stream must FAIL | 4/665 |
| **C-compat** | arm BF reproduces EXP-007's frozen receipt | 3 seeds × 13 fields, **0 divergences**, at EXP-007's own 1000-reaction length |
| **C-eligible** *(added, D117)* | the index log matches the independent counter | 20/20 cells, 0 mismatches |
| **C-fire(matter/totality)** | `consumed + blocked == eligible R-S`, exactly | all 10 M cells, 0 violations |
| **C-fire(matter/supply)** | ≥ 100 eligible R-S in every **PRODUCING** M cell | 4 of 10 M cells produce; **0 below the floor** |
| **C-fire(price)** | floor charged in FF/FM, Book I in BF/BM | 8689 floor events, no silent fallback, 0 violations |
| **C-ledger** | conservation and census totality per tick | 20 cells, 3096 consumed deaths, 673 waits, 0 failures |
| **C-factorial** *(added, D118)* | the seed-subset arithmetic is the pilot's | identical to ALIFE-EXP-012's committed `factorial()` on all five seeds |
| **C-det** | every cell twice | 0 divergences |
| **C-corpus / C-core** | fingerprint; the peeling returns nothing on an open chain | pass |

**C-fire(matter/supply) is the control that this experiment exists to have
fixed.** The same floor of 100 that failed in 4 of 10 cells under 012b passes in
10 of 10 here, because it is scoped to the cells where it can be met. Nothing
about the chemistry changed; the admission rule stopped racing the mechanism
against convergence.

## Corrections, named rather than absorbed

1. **XC3's base was wrong on the first implementation** (`DECISIONS.md` D121). It
   restricted the comparison to seeds whose *own* phase is COLLAPSED and reported
   `UNADJUDICATED (insufficient collapsed cells)` off the single such seed. The
   adjudication rule says "≥ 2 collapsed seeds **with ≥ 2 arms each**", a
   qualifier that is redundant under the concordant reading, and the hypothesis
   is stated over COLLAPSED *cells*. Corrected to seeds carrying at least two
   collapsed cells: four seeds qualify and XC3 becomes adjudicable. The
   correction was made from re-reading the rule against the output, before any
   RESULT existed and before the verdict was known.

2. **The instrumentation had to move** (`DECISIONS.md` D117). 012b recorded
   eligible-event indices inside `consume_for`, which only the matter arms call.
   The phase is defined on eligible events, which exist in all four arms, and XC1
   is precisely whether the four arms agree — so it could not be asked of two of
   them. `note_rs_bound` sees every R-S in every arm. C-eligible was added to
   check that moving the instrument moved no number.

## What this says, and what it does not

- It does **not** say the currency chooses the phase. It says the corpus does
  not choose it alone: four of five seeds have arms that disagree. Which
  direction the currency pushes is visible in the per-arm counts above and is
  not scored by anything preregistered here.
- It does **not** rescue the factorial. XC2 is unadjudicated and no effect
  estimate exists in this receipt.
- It says collapse timing is **not** currency-independent, and the clearest case
  is the one seed where every arm collapsed: 706, 706, 1833, 1961.
- Nothing here is proved. The census identity and the ledger are **checked**, on
  every tick of twenty cells.

## Limitations

1. Five seeds, four arms, one corpus, one budget, one capacity. Twenty cells is a
   small factorial and the phase is a binary read off one threshold.
2. **The threshold is pinned but it is still a threshold.** 3000 sits in a gap
   the pilots measured (stoppers below 1100, producers above 5000) and was fixed
   before any 012c cell ran. Every cell in this run lands far from it — the
   largest collapsed last-eligible index is 1961 and the smallest producing one
   is 4346 — so no cell is near the boundary. That is a fact about this run and
   not a guarantee about another.
3. **The per-arm phase pattern has no null.** Seven producing cells distributed
   0 / 1 / 3 / 3 across the arms is suggestive and unscored. A successor needs a
   preregistered criterion and a permutation null over the arm labels, or it will
   be EXP-007's L1-core again: a statistic met by chance and named for biology.
4. XC3's comparison rests heavily on one seed. `20260827` supplies the largest
   within-seed spread and is the only seed with four collapsed arms; drop it and
   the verdict is not the same computation.
5. The soup census in `FM/20260828` ends at **7** rather than at capacity 64 —
   consumption removed molecules faster than settled reactions replaced them.
   Reported because it is the one cell where the matter rule visibly shrank the
   population, and it is not something any hypothesis here scores.
