# ALIFE-EXP-010 — result

Judged against [`ALIFE-EXP-010-does-the-currency-choose-the-colony-preregistration.md`](../ALIFE-EXP-010-does-the-currency-choose-the-colony-preregistration.md),
committed at `2a3ff65` before this harness existed and written by an author who
did not write it. The choices that document left open are `DECISIONS.md`
D74–D87, committed before the measurement ran. Founders are ALIFE-EXP-001's,
pinned at `53cc6da80f66d220`.

**Provenance, stated at its real strength.** The preregistration was written by
Claude Fable 5 and this harness by Claude Opus 5, working only from the committed
document, the repository and its dependencies, and this is the ALIFE-EXP-005
arrangement — a real separation of roles between different models, not an
independent registry, external review, or statistical replication. What it does
establish is that no hypothesis here was written by anyone who had seen a number,
and that the document's defects (D77, D82, and the one in *H1's threshold*
below) were found by the party that could not fix them quietly.

**H1 holds and cannot discriminate. H2 and H3 fail. The result is the third
thing: in a lazy machine a duplication is a duplication of an ADDRESS, so the
entire currency question is worth between 0.8% and 7.0% of the colony's ATP.**

| | |
| --- | --- |
| substrate | `impl/sigma_alife.py` 0.1.0 on Σ-GLYPH Book I, oracle sha256 `413d1f9805cdbdf42f13d967a17be26eb959c692eeb067e7146203ed9cebe64d` |
| arms | E = ALIFE-EXP-007's chemistry unchanged; M = R-S priced at the action floor plus one consumed body |
| frame | 64 founders, capacity 64, 1000 reactions, 200 ATP/reaction, slice 32 |
| seeds | `20260825`, `20260826`, `20260827`, pinned in the preregistration |
| controls | eleven (C1–C8 preregistered, C0/C0b/C0c added), all passing |
| receipt | `results.json`, reproduced field for field on a second run of every arm × seed |

## The measurement

| arm | seed | success | living census | distinct | closure | L1-core | mean cost | consumed | waiting at end |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| E | 20260825 | 62.9% | 64 | 46 | 0.339 | 146 | 92.7 | — | 0 |
| E | 20260826 | 49.3% | 64 | 42 | 0.385 | 156 | 97.2 | — | 0 |
| E | 20260827 | 43.0% | 64 | 38 | 0.228 | 42 | 109.2 | — | 0 |
| M | 20260825 | 58.4% | 60 | 52 | 0.307 | 288 | 81.7 | 194 | 152 |
| M | 20260826 | 38.1% | 63 | 57 | 0.234 | 81 | 105.3 | 101 | 130 |
| M | 20260827 | 56.0% | 64 | 29 | 0.377 | 109 | 110.2 | 62 | 73 |

Arm E's row is ALIFE-EXP-007's committed receipt, field for field (C3).

## The hypotheses, scored

### H1 — the currencies pick different colonies: **HOLDS**, and the threshold is uninformative

> Jaccard overlap between the sets of surviving non-genesis molecule hashes in
> Arm E and Arm M at the final tick is **< 0.5 in at least 2 of 3 seeds**.

| seed | E survivors | M survivors | Jaccard |
|---|---:|---:|---:|
| 20260825 | 44 | 50 | **0.0000** |
| 20260826 | 40 | 56 | **0.0000** |
| 20260827 | 37 | 28 | **0.0000** |

3 of 3, against a requirement of 2 of 3. **H1 HOLDS as preregistered.** The two
arms do not share one non-genesis molecule at the final tick, on any seed.

And the number says nothing, for the reason ALIFE-EXP-007's own H3 said nothing.
Hold the currency FIXED and move only the seed:

| statistic | seed pairs |
|---|---|
| E vs M, same seed *(this is H1)* | 0.0000, 0.0000, 0.0000 |
| **E vs E**, different seeds | 0.0000, 0.0125, 0.0000 |
| **M vs M**, different seeds | 0.0000, 0.0000, 0.0000 |

> Two runs of the *same* currency overlap as little as two runs of different
> ones. A bounded high-turnover soup does not repeat its molecules, so a
> near-zero survivor overlap measures turnover and not the manipulation. The
> preregistered threshold of 0.5 was cleared by a margin of half the scale, and
> a threshold that a run clears against itself is not a test.

This is the same defect EXP-007's RESULT diagnosed in EXP-007's H3 and the same
family as `DECISIONS.md` D50. It was preregistered here anyway, which is the
point of preregistering: the verdict stands as written and the baseline is
reported beside it. This baseline is **post hoc** and scores nothing.

### H2 — matter-pricing cannibalizes: **FAILS**

> Arm M ends with a strictly smaller living census than Arm E in **3 of 3**
> seeds, and strictly fewer distinct hashes in **at least 2 of 3**.

| seed | census E | census M | smaller? | distinct E | distinct M | fewer? |
|---|---:|---:|:--|---:|---:|:--|
| 20260825 | 64 | 60 | yes | 46 | **52** | no |
| 20260826 | 64 | 63 | yes | 42 | **57** | no |
| 20260827 | 64 | **64** | no | 38 | 29 | yes |

Census 2 of 3 against a requirement of 3 of 3; distinct hashes 1 of 3 against a
requirement of 2 of 3. **H2 FAILS on both clauses**, and the falsifier the
preregistration named is exactly what happened: *diversity in M matches or
exceeds E at those thresholds*, in two seeds of three, and by 6 and 15 hashes.

The direction is the interesting part. Consumption does remove bodies — 194,
101 and 62 of them — but a consumed body is removed at the moment its hash is
*in demand*, and what replaces it is a product that was not there before.
Matter-pricing does not thin the colony; on two of three seeds it **widens**
it, because eating a duplicate is a way of spending redundancy rather than
population.

### H3 — the self-pricing-out curve bends: **FAILS**

> Final-window success rate in M exceeds E by **≥ 10 percentage points in at
> least 2 of 3 seeds**. Window = the last 100 reactions (`DECISIONS.md` D79;
> the preregistration names a final window and does not size one).

| seed | E | M | Δ |
|---|---:|---:|---:|
| 20260825 | 52.0% | 29.0% | **−23.0 pts** |
| 20260826 | 13.0% | 9.0% | **−4.0 pts** |
| 20260827 | 25.0% | 49.0% | **+24.0 pts** |

1 of 3 against a requirement of 2 of 3. **H3 FAILS**, and it fails with a
reversed sign in two seeds: the arm that spends *less* on duplication ends up
*less* able to afford its own reactions. The sensitivity windows preregistered
as scoring nothing (D79) agree and do not rescue it:

| seed | Δ at 100 | Δ at 200 | Δ at 400 |
|---|---:|---:|---:|
| 20260825 | −23.0 | −25.0 | −12.5 |
| 20260826 | −4.0 | −2.0 | −7.7 |
| 20260827 | +24.0 | +16.5 | +29.2 |

## Why H3 could not have worked, and it is the finding

H3's mechanism is "the ATP not spent on duplication remains available for other
work". The harness measured how much ATP that is:

| arm | seed | R-S fired | ATP on R-S | ATP spent | share | mean `size(z)` | max `size(z)` |
|---|---:|---:|---:|---:|---:|---:|---:|
| E | 20260825 | 612 | 1 628 | 58 296 | **2.79%** | 1.66 | 15 |
| E | 20260826 | 331 | 928 | 47 903 | **1.94%** | 1.80 | 21 |
| E | 20260827 | 1 042 | 3 274 | 46 973 | **6.97%** | 2.14 | 43 |
| M | 20260825 | 764 | 764 | 47 688 | 1.60% | 1.21 | 5 |
| M | 20260826 | 604 | 604 | 40 138 | 1.50% | 1.26 | 3 |
| M | 20260827 | 490 | 490 | 61 688 | 0.79% | 1.10 | 9 |

> **Book I evaluates leftmost-outermost with lazy spine resolution, so when
> `R-S` fires, `z` is nearly always still a THUNK — an address of size 1.** Book
> I's energy price for a duplication, `1 + size(z)`, is therefore usually **2**,
> not "one plus a tree". Mean `size(z)` over every duplication in the energy arm
> is 1.66, 1.80 and 2.14. The whole difference between the two currencies is
> between 0.8% and 7.0% of what the colony spends, and switching to the floor
> saves at most one ATP per duplication in the common case.

The two pricings are not two economies. They are the same economy with a rounding
difference, plus a hard constraint — the copy must exist as a body — that has
nothing to do with ATP at all. Whatever separates the arms (and H1 shows they are
completely separated) is that constraint and the RNG divergence that follows it,
not the money. ALIFE-EXP-005 found that "Book I's lazy, address-based pricing is
capability, not accounting — inside a band"; this is the same sentence arriving
from the other side. Matter-pricing lands *outside* that band.

## The nulls, as preregistered

Any organization-flavored observation is scored against **both** ALIFE-EXP-008
nulls, by the same code path for both arms, 20 draws, locality window 200
(`DECISIONS.md` D85). The L1-core is the only such statistic here, and it is
computed and scored whether or not anything is claimed from it:

| arm | seed | core | full-shuffle max (mean) | locality max (mean) |
|---|---:|---:|---:|---:|
| E | 20260825 | 146 | 272 (226.1) | 236 (183.1) |
| E | 20260826 | 156 | 228 (192.8) | 206 (169.6) |
| E | 20260827 | 42 | 66 (10.4) | **38** (13.1) |
| M | 20260825 | 288 | 302 (249.1) | 305 (251.5) |
| M | 20260826 | 81 | 153 (19.1) | 102 (42.2) |
| M | 20260827 | 109 | 274 (225.2) | 215 (152.9) |

**No cell clears both nulls, in either arm.** One cell — Arm E, seed 20260827 —
has a core (42) above the locality-preserving null's maximum draw (38) and well
below the full shuffle's (66). That is one cell of six, on one of two models, and
it is reported here rather than named a finding. Arm M's cores are larger than
Arm E's in two of three seeds and this changes nothing: a chance graph of the
same density scores as high or higher.

## Controls

Eleven, all passing before any number was recorded. Three were not in the
preregistration and are named as additions rather than folded in:

| | control | outcome |
|---|---|---|
| **C0** | *(added, D84)* `_next_redex` is the oracle's own dispatch | 175 R-S, 750 force, 118 R-I, 168 R-K, 28 R-R predicted and fired identically; 0 disagreements |
| **C0b** | *(added)* EXP-007's core peeling closes a closed pair and returns nothing on an open chain | 2 and 0 |
| **C0c** | *(added, D87)* the pricing hook is the identity when it prices nothing | Arm E through the hook at Book I's price is identical to Arm E without it, 3/3 seeds |
| **C1** | the ledger balances in both arms, every tick, including the consumed-transfer | balanced; 0 transfer mismatches; **0 ATP moved** — see the correction below |
| **C2** | ≥ 50 `consumed` deaths per seed in Arm M | 194, 101, 62 |
| **C3** | Arm E reproduces EXP-007's frozen numbers on the shared seeds | 13 recorded fields × 3 seeds, 0 differences |
| **C4** | determinism: each arm, each seed, twice | 0 divergences |
| **C5** | the corpus is EXP-001's | `53cc6da80f66d220` |
| **C6** | waiting spends nothing; resumed answers are unchanged | **0 ATP** spent while waiting across Arm M; 75/75 sampled products equal the oracle's own normal form |
| **C7** | census accounting is total | 1064 individuals per run partitioned every tick into alive / consumed / culled / starved / waiting; 0 reconciliation failures; 0 consumed bodies appearing alive; 0 material shortfalls |
| **C8** | saturation is reported | below |

**C8, saturation.** Waits outstanding at the final tick: Arm M **152, 130, 73**
of 1000 reactions — between 7% and 15% of the colony is still waiting for a copy
that never arrived. Arm E: 0, by construction. Transfer overflow guards: 0, and
that number is empty for the reason in D77. Faults: 0. Unresolved: 0.
`DISSONANCE` never entered either soup.

## Corrections, named rather than absorbed

1. **The preregistration's ATP-transfer clause is inoperative in this frame, and
   its citation of `transfer_preserves_bound` is therefore vacuous here**
   (`DECISIONS.md` D77). EXP-007 returns a reaction's unspent ATP to the commons
   the instant it settles, so a molecule in the soup holds nothing; "the consumed
   individual's remaining ATP transfers in full" moves **0**, every time, in all
   three seeds. Giving molecules a reservoir requires not collecting, which moves
   `pool_left` — one of the frozen EXP-007 numbers C3 requires Arm E to reproduce
   *exactly* — and doing it in Arm M alone would be a second difference between
   the arms, which the same paragraph forbids. The transfer is implemented and
   measured; it is conservation-preserving for the boring reason that nothing
   moves. Conservation in Arm M is real (C1) and is not evidence for the
   redistribution argument the document makes.

2. **The bound the preregistration says "already holds" in Arm M is not the bound
   that holds** (`DECISIONS.md` D78). Book I's per-agent `size ≤ s0 + spent`
   follows from `Δsize ≤ cost − 1`, a property of Book I's *price*; charging the
   floor for a duplication abandons that premise by construction. It was measured
   rather than assumed: **1 action in 1 858** across Arm M put an agent's
   materialized size above its own `s0 + spent` (seed 20260827), and the reason
   it is not more is slack the agent had already accumulated, not the theorem.
   What does hold, checked on every consumption and every tick in both arms, is
   the *matter* statement — the consumed body leaves the census carrying at least
   the material the copy creates (0 shortfalls in 357 consumptions), and
   `Σ size(alive) ≤ Σ s0 + Σ spent` over the whole census. Arm E ran with the
   Book I probe on, over every action, including its duplications.

3. **H1's threshold cannot discriminate**, and the baseline that shows it is post
   hoc (above). The document's own "what would make this experiment worthless"
   list warns against reporting "M differs from E" as the finding; H1 as
   preregistered is a slightly stronger version of that same statement, and the
   E-vs-E baseline is what turns the warning into a number.

4. **A harness bug, found by a preregistered control.** The first C4 compared an
   Arm E run instrumented through the pricing hook against an uninstrumented
   re-run and reported three divergences. The divergence was in the
   instrumentation fields only and the fix was to run both sides the same way —
   but C4 was right to fail, and it is recorded here because the alternative
   reading (loosen the comparison until it passes) was available and is the
   failure mode rule 6 exists for.

5. **`DECISIONS.md` D74–D87** are fourteen further places the document
   underdetermined the harness — what an "individual" is when EXP-007 has no
   census (D74), which copy a consumption eats (D75), how big H3's "final
   window" is (D79), what a Jaccard over two empty sets means (D82). Each was
   fixed before the measurement ran and none was revisited afterwards.

## What this does not say

- It does not say the two currencies are the same. They are not: no molecule
  survives in both arms, and Arm M leaves 7–15% of its reactions permanently
  waiting for a copy. It says the *ATP* difference between them is 0.8–7.0% and
  that H3, which was about the ATP, was never going to find it.
- It does not say matter-pricing is worse. On two of three seeds it ends with
  more distinct molecules than the energy arm.
- It says nothing about Combinatory Chemistry. Arm M is K&M-*inspired* pricing
  inside this substrate: their reactor, their rates and their Gillespie dynamics
  are not simulated, reactants here are not consumed by their reaction, and
  nothing here validates or invalidates their results.
- Nothing here is proved. Eleven theorems are proved in this repository and are
  listed in `proofs/README.md`; the census bound and the material inequality
  above are **checked**, on every tick of six runs, and that is a different word.

## Limitations

1. Three seeds, 1000 reactions, capacity 64, one founder corpus, one budget.
   D72 already showed this chemistry prices itself out of that budget as products
   accumulate structure; both arms are inside that regime and H3's window sits
   exactly where it bites.
2. The consumption rule reads the census by *current materialization hash*, which
   in a normal-form soup is the product hash. A partially-reduced population
   would offer a different set of consumable copies.
3. The waiting machinery is EXP-009's, used here for the first time outside
   delivery, and its outstanding waits (152/130/73) are the largest single
   uncontrolled difference between the arms after the price itself.
4. `mean size(z)` is a property of leftmost-outermost lazy evaluation. A strict
   or a normalizing strategy would make duplication expensive and the currency
   question large again — which is the successor experiment, and it is about the
   evaluation order, not about the money.
