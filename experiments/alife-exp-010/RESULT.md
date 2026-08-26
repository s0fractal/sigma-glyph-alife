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
price intervention is worth 0.77%, 0.40% and 1.39% of the colony's total ATP —
a lever of about one part in a hundred.**

> **Corrected 2026-08-26**, after an adversarial review found the first version
> of this sentence had the wrong denominator and the wrong estimand. It said
> "between 0.8% and 7.0%". Both numbers are withdrawn; see the
> [erratum](#erratum--2026-08-26) for what they were, what they are, and why
> the corrected ones make the same qualitative point at a third of the size.

| | |
| --- | --- |
| substrate | `impl/sigma_alife.py` 0.1.0 on Σ-GLYPH Book I, oracle sha256 `413d1f9805cdbdf42f13d967a17be26eb959c692eeb067e7146203ed9cebe64d` |
| arms | E = ALIFE-EXP-007's chemistry unchanged; M = R-S priced at the action floor plus one consumed body |
| frame | 64 founders, capacity 64, 1000 reactions, 200 ATP/reaction, slice 32 |
| seeds | `20260825`, `20260826`, `20260827`, pinned in the preregistration |
| controls | twelve (C1–C8 preregistered, C0/C0b/C0c/C9 added), all passing |
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

The direction is the interesting part, and the explanation this section gave for
it on 2026-08-26 was **wrong and is withdrawn**. It said matter-pricing widens
the colony "because eating a duplicate is a way of spending redundancy rather
than population". The harness never recorded how many living bodies carried the
demanded hash before a consumption, so it could not tell redundancy-spending
from eating the last copy. It records it now (`DECISIONS.md` D90):

| seed | consumptions | ate the **last** living copy | share | multiplicity histogram |
|---|---:|---:|---:|---|
| 20260825 | 194 | 145 | **74.7%** | 1×145, 2×27, 3×12, 4×6, 5×3, 6×1 |
| 20260826 | 101 | 78 | **77.2%** | 1×78, 2×16, 3×5, 6×1, 7×1 |
| 20260827 | 62 | 56 | **90.3%** | 1×56, 2×3, 3×2, 4×1 |

> Three consumptions in four — nine in ten on one seed — remove the **only**
> living body carrying that hash. The proposed mechanism is not merely
> unmeasured; its own event-level statistic contradicts it. Consumption in this
> arm is overwhelmingly the destruction of a singleton, not the spending of a
> surplus.

What *does* produce Arm M's higher distinctness is therefore unidentified here.
The candidates the review names — fewer culls (Arm M culls 394/281/498 against
Arm E's 629/493/430, because a consumed body leaves a slot the capacity rule
then does not have to clear), the blocked reactions, and the diverged
trajectory — are not separated by this design and cannot be, for the reason the
preregistration author owns in the erratum to
[`reviews/claude-fable-2026-08-26-exp010-response.md`](../../reviews/claude-fable-2026-08-26-exp010-response.md):
Arm M is a compound intervention.

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

**H3's statistic is right-censored, and only one arm has anything to censor**
(`DECISIONS.md` D88, added 2026-08-26). A reaction still parked at reaction 1000
counts against M's rate; Arm E has no parked state at all, and inside Arm M a
reaction born late has had less time to be woken. The window is therefore
reported as an interval — the preregistered statistic is its lower end, and its
upper end is the rate that would obtain if *every* outstanding wait were
eventually answered:

| seed | last-100 window, M: settled / waiting / failed | M rate interval | E rate |
|---|---|---:|---:|
| 20260825 | 29 / 10 / 61 | [29.0%, 39.0%] | 52.0% |
| 20260826 | 9 / 6 / 85 | [9.0%, 15.0%] | 13.0% |
| 20260827 | 49 / 0 / 51 | [49.0%, 49.0%] | 25.0% |

> Censoring does not rescue H3. On 20260825 even the upper end is 13 points
> below Arm E; on 20260827 there is nothing censored in the window at all; only
> 20260826, whose Δ is −4 points, becomes indeterminate. **The verdict is not
> re-adjudicated and does not move: 1 of 3.**

## Why H3 could not have worked, and it is the finding

*Every number in this section was recomputed on 2026-08-26; the table it
replaces is in the [erratum](#erratum--2026-08-26).*

H3's mechanism is "the ATP not spent on duplication remains available for other
work". How much ATP is that? Two different questions, which the first version of
this section ran together:

**(a) What each arm charges for duplication, over everything the colony spends.**
The denominator is `spent_total` — the spend of every individual ever born,
settled, failed and parked alike — and the ledger identity
`pool + held at the horizon + spent = endowment` closes in all six runs (control
**C9**).

| arm | seed | R-S fired | ATP on R-S | total spend | **R-S share** | mean `size(z)` | max `size(z)` |
|---|---:|---:|---:|---:|---:|---:|---:|
| E | 20260825 | 612 | 1 628 | 132 098 | **1.23%** | 1.66 | 15 |
| E | 20260826 | 331 | 928 | 148 795 | **0.62%** | 1.80 | 21 |
| E | 20260827 | 1 042 | 3 274 | 160 395 | **2.04%** | 2.14 | 43 |
| M | 20260825 | 764 | 764 | 103 950 | 0.73% | 1.21 | 5 |
| M | 20260826 | 604 | 604 | 140 365 | 0.43% | 1.26 | 3 |
| M | 20260827 | 490 | 490 | 136 625 | 0.36% | 1.10 | 9 |

**(b) The price intervention itself**, which is neither column above. It is the
counterfactual `Book I price − floor price` evaluated on *one arm's own trace*:
what that arm's duplications would have cost under the other rule, with the
trajectory held fixed. It cannot be recovered by subtracting the two arms'
totals, because the arms do not take the same trajectory.

| arm | seed | Book I − floor, on this trace | **as a share of total spend** |
|---|---:|---:|---:|
| E | 20260825 | 1 016 | **0.77%** |
| E | 20260826 | 597 | **0.40%** |
| E | 20260827 | 2 232 | **1.39%** |
| M | 20260825 | 924 | 0.89% |
| M | 20260826 | 762 | 0.54% |
| M | 20260827 | 538 | 0.39% |

> **Book I evaluates leftmost-outermost with lazy spine resolution, so when
> `R-S` fires, `z` is nearly always still a THUNK — an address of size 1.** Book
> I's energy price for a duplication, `1 + size(z)`, is therefore usually **2**,
> not "one plus a tree". Mean `size(z)` over every duplication in the energy arm
> is 1.66, 1.80 and 2.14. So switching to the floor saves one ATP per
> duplication in the common case, and the whole price intervention is worth
> **0.4% to 1.4%** of what the colony spends. `rs_zsize_hist` in the receipt
> carries the per-event counterfactual pair in full: both prices are functions
> of `size(z)`.

The two pricings are not two economies. They are the same economy with a rounding
difference of about one part in a hundred, plus a hard constraint — the copy must
exist as a body — that has nothing to do with ATP at all. Whatever separates the
arms (and H1 shows they are completely separated) is that constraint, the
blocking it causes, and the RNG divergence that follows, not the money. This
experiment cannot apportion the separation among those, because Arm M changes
them together; that is the compound-intervention defect the preregistration
author owns. ALIFE-EXP-005 found that "Book I's lazy, address-based pricing is
capability, not accounting — inside a band"; this is the same sentence arriving
from the other side, and matter-pricing lands *outside* that band.

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

Twelve, all passing before any number was recorded. Four were not in the
preregistration and are named as additions rather than folded in. C9 was added
on 2026-08-26 in response to the review. It would not by itself have caught a
mistake made in prose — but the first receipt had no total-spend figure in it at
all, which is why this document reached for a proxy, and C9 is what makes the
right denominator exist and asserts that it closes:

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
| **C9** | *(added 2026-08-26, D89)* the ledger identity is emitted and closes | `pool + held at the horizon + spent = endowment` in 6/6 runs; spend splits into settled/failed/parked exactly |

**C8, saturation.** Waits outstanding at the final tick: Arm M **152, 130, 73**
of 1000 reactions — between 7% and 15% of the colony is **unresolved at the
observation horizon**, holding 26 720, 23 175 and 12 733 ATP it may still spend.
Arm E: 0, by construction. Transfer overflow guards: 0, and that number is empty
for the reason in D77. Faults: 0. Unresolved-reference outcomes: 0. `DISSONANCE`
never entered either soup.

> *Corrected 2026-08-26.* This paragraph said those reactions were waiting "for
> a copy that never arrived". Nothing here ran the environment past reaction
> 1000, so non-arrival was never observed — only non-arrival **within the
> horizon**. "Never" is a reachability claim and this experiment does not make
> one. The same correction applies wherever this receipt said "permanent".

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

   > *Qualified 2026-08-26.* Both halves are weaker than the phrase "matter
   > conservation" suggests, and the review is right about why. The per-event
   > check is largely **structural**: an exact-hash victim represents the same
   > term as `z`, so its size matching is close to true by construction rather
   > than by policy — the check earns its place as a guard against the harness
   > consuming the wrong body, not as evidence of a physical law. The per-tick
   > inequality sums `s0` over every individual *ever born*, dead and culled
   > included, so its right-hand side only grows and can become arbitrarily
   > loose. And "freed matter" is a **census** metaphor: the content-addressed
   > store keeps every consumed term, and nothing here deallocates. A real
   > stock-flow ledger — production, consumption, culling, retained storage,
   > collection, named separately — is a successor's job and is not what this
   > receipt has.

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
  survives in both arms, and Arm M leaves 7–15% of its reactions unresolved at
  the observation horizon. It says the *price intervention* between them is
  0.4–1.4% of colony spend and that H3, which was about the ATP, was never
  going to find it. It does **not** say which of the several things Arm M
  changes at once produced the separation: it cannot.
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
   uncontrolled difference between the arms after the price itself. They are
   right-censored: the run stops at reaction 1000 without a settlement phase, so
   what is measured is unresolved-at-horizon and nothing here shows a copy could
   not arrive later.
4. `mean size(z)` is a property of leftmost-outermost lazy evaluation. A strict
   or a normalizing strategy would make duplication expensive and the currency
   question large again — which is the successor experiment, and it is about the
   evaluation order, not about the money.
5. **Arm M is a compound intervention.** It changes the price, affordability, the
   requirement for a living exact-hash body, the removal of that body, and — by
   consuming different positions in the RNG stream — the whole downstream
   trajectory. H1 establishes that two compound transition kernels produce
   different finite-horizon populations. H2's and H3's signs cannot be
   attributed to price, to matter conservation, or to victim availability
   separately. The preregistration said "the pricing of `R-S`, and nothing
   else"; its author owns that sentence as false-as-designed in the erratum to
   the response, and names the 2×2 factorial successor.
6. **"Attractor" is not operationalised here.** Three 1000-reaction trajectories
   with no burn-in, no stationarity or recurrence criterion and no convergence
   across horizons measure **finite-horizon population states**. Where this
   receipt or its preregistration says attractor, read that.

---

## Erratum — 2026-08-26

An adversarial review by Codex ([`reviews/codex-2026-08-26.md`](../../reviews/codex-2026-08-26.md),
verdict CHANGES REQUESTED) found one quantitative misstatement, two
identification failures and a release-gate hole in this receipt as first
committed (`eeb6466`). Two of its findings were reproduced independently before
it was committed. The house pattern for this is sigma-glyph's EXP-004 — re-run
at equal work, say what moved — so the measurement was re-run and this section
says what moved rather than the diff saying it.

**No verdict moves. H1 HOLDS, H2 FAILS, H3 FAILS — 1 of 3, exactly as scored on
2026-08-26 before the review.** Every preregistered criterion is unchanged and
was rescored on the re-run: H1 3/3 seeds below 0.5, H2 census 2/3 and distinct
1/3, H3 1/3. What changed is descriptive numbers and their names.

### 1. The ATP share had the wrong denominator and was the wrong estimand

Withdrawn: **"the entire currency question is worth between 0.8% and 7.0% of the
colony's ATP"**, and this table:

| arm | seed | withdrawn "ATP spent" | withdrawn share |
|---|---:|---:|---:|
| E | 20260825 | 58 296 | 2.79% |
| E | 20260826 | 47 903 | 1.94% |
| E | 20260827 | 46 973 | 6.97% |
| M | 20260825 | 47 688 | 1.60% |
| M | 20260826 | 40 138 | 1.50% |
| M | 20260827 | 61 688 | 0.79% |

The denominator was `ok × mean_cost` — the spend of the reactions that
*settled*. The numerator counted R-S actions in every reaction, including those
that later starved or parked. Two different populations. The corrected R-S
shares of actual total spend are **1.23% / 0.62% / 2.04%** in Arm E and
**0.73% / 0.43% / 0.36%** in Arm M.

Worse than the arithmetic: R-S expenditure is not the price intervention at all.
The intervention is the counterfactual `Book I price − floor price` on a fixed
trace, and on Arm E's own traces it is **0.77% / 0.40% / 1.39%** of total spend.
The receipt now emits `spent_total`, `spend_settled`, `spend_failed`,
`spend_parked`, `held_terminal`, `rs_book_i_atp`, `rs_floor_atp` and
`rs_zsize_hist` (which carries every event's counterfactual pair, both prices
being functions of `size(z)`), and control **C9** asserts the ledger identity
the review had to reconstruct by hand. `DECISIONS.md` D89.

The qualitative conclusion survives at roughly a third of the stated size: lazy
address-based pricing makes the currency a **one-part-in-a-hundred** lever, not
a seven-part one. The argument for the successor regime — enforced copy pricing,
where duplication is genuinely expensive — is *stronger* under the corrected
numbers, and that is motivation rather than a measurement.

### 2. "Eating a duplicate spends redundancy" was an explanation with nothing under it

H2's discussion explained Arm M's higher distinctness by a mechanism the harness
had never measured. It measures it now: **74.7%, 77.2% and 90.3% of consumptions
removed the only living body carrying that hash.** The mechanism is contradicted
by its own event-level statistic and is withdrawn; the cause of Arm M's higher
distinctness is left unidentified, with candidates named. `DECISIONS.md` D90.

### 3. "Permanent" waiting, and H3's arm-specific censoring

This receipt said 152/130/73 reactions were waiting "for a copy that never
arrived" and called them permanently waiting. The run stops at reaction 1000
without a settlement phase, so what was observed is **unresolved at the
observation horizon**; "never" is a reachability claim this experiment does not
make. Every such phrase is corrected above. `waiting` is now a third terminal
outcome in the receipt rather than folded into `fail`, and H3's window is
reported as an interval whose lower end is the preregistered statistic. The
interval does not change the verdict — one seed becomes indeterminate, one is
uncensored, and one is 13 points short even at its upper end. `DECISIONS.md` D88.

### 4. This experiment was absent from the advertised test matrix

Neither `tools/test-all.sh` nor CI replayed ALIFE-EXP-010: the matrix was green
while the headline could rot. It now replays in **both** profiles of
`test-all.sh` — it costs half a minute, and the ten-minute soups are the only
replays that get to be optional — and has a path-triggered CI job of its own.
Three guards gained the negative controls they lacked: `receipt_guard.py`'s
locality rule was not enforcing locality (Codex's reproducer returned `[]`; it
now returns the offender, and all fourteen committed receipts still pass),
`tests/receipt_identity_guard.py` is new and proves that a flipped verdict is
invisible to a shape guard and caught by the replay diff, and
`tests/exit_status_guard.py` could not resolve its own oracle path from a
temporary tree, which is why the canonical command was not terminal. That
command is now documented at the top of `test-all.sh`. `DECISIONS.md` D91.

### What the review changed that this receipt does not fix

The compound-intervention and attractor findings are design defects of the
preregistration, owned by its author in the erratum to
[`reviews/claude-fable-2026-08-26-exp010-response.md`](../../reviews/claude-fable-2026-08-26-exp010-response.md),
and named in Limitations 5 and 6 above. The narrower statement the review says
is currently publishable is the one this receipt now makes:

> In this bounded implementation, two compound reactor policies produce
> seed-sensitive finite-horizon populations; the preregistered survivor-overlap
> statistic is non-discriminating, and outstanding matter waits are substantial
> at the observation horizon. The marginal ATP price effect has not yet been
> identified.
