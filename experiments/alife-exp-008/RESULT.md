# ALIFE-EXP-008 — result

Judged against [`ALIFE-EXP-008-does-anything-maintain-itself-preregistration.md`](../ALIFE-EXP-008-does-anything-maintain-itself-preregistration.md),
committed before this harness; the frame before that. Chemistry is EXP-007's,
verbatim; founders are EXP-001's, pinned at `53cc6da80f66d220`.

## Scorecard

| | claim | verdict |
|---|---|---|
| **H1** | a self-maintaining set ≥ 3 while the shuffled-graph null is empty | **holds against the preregistered null** (4/7 windows) — and **FAILS against a stronger one** (1/7) |
| **H2** | the history-core is ≥ 5× the persisting set | **FAILS** — 2 of 5 measurable windows |
| **H3** | sustaining reactions are ≥ 30% cheaper | **UNADJUDICATED** — no set survived the stronger null to price |

## The finding is about the null, not about the soup

EXP-007 ended by saying its organizations were counted from the dead. This
experiment required them to be **alive and being re-made out of themselves**, and
that requirement does beat a complete shuffle by a wide margin:

| window | observed | full-shuffle null (mean / max of 20) | locality-preserving null (mean / max of 20) |
|---:|---:|---:|---:|
| 100 | 0 | 0.0 / 0 | 0.1 / 2 |
| 200 | 10 | 0.8 / 6 | **11.4 / 23** |
| 400 | 14 | 1.1 / 6 | **11.2 / 23** |
| 600 | 18 | 5.3 / 16 | **17.6 / 26** |

*(primary budget, seed 20260825; the other two seeds are in the receipt and behave
the same way)*

Permute every product and self-maintenance collapses to nearly nothing — a mean
under 1.1 against an observed 10 to 25. **Permute products only within the window,
so the multiset of recent products is preserved and only *who made what* is
destroyed, and the null matches or beats the observed set.**

> Most of what looks like a self-maintaining organization here is **temporal
> locality**: recent molecules are recent, and a set assembled from recent
> molecules will find recent producers for its members whoever made them. What
> remains once that is held fixed does not clear chance at 6 of 7 windows.

Scored across the whole curve, with no window selected:

| window | clears the full shuffle | clears the locality-preserving shuffle |
|---:|---:|---:|
| 25, 50 | 0/3 seeds | 0/3 seeds |
| 100 | 1/3 | 0/3 |
| 200 | 2/3 | 0/3 |
| 400 | 2/3 | 1/3 |
| 600 | 3/3 | 1/3 |
| 1000 | 3/3 | 3/3 |

Window 1000 is the whole run, where condition 2 degenerates into EXP-007's
history-core. The preregistration says not to count it, and the curve is reported
so that the degeneration is visible rather than hidden.

## H2 fails, and its failure is informative

The persistence requirement was supposed to be strictly harder than EXP-007's
history-core. It is — for two seeds:

| window | seed 25 | seed 26 | seed 27 |
|---:|---:|---:|---:|
| 200 | 14.6× | — | 2.0× |
| 400 | 10.4× | — | 1.7× |
| 600 | 8.1× | 7.4× | 1.7× |
| 1000 | 6.6× | 5.6× | 1.7× |

Seed 20260827's persisting sets are nearly as large as its whole history-core
(1.7×), because that run's history-core is small (42) to begin with. So
persistence discriminates **when there is a large history-core to discriminate
against**, and not otherwise. A ≥ 5× rule does not describe that.

## Corrections

Four, all in the harness, all against this repository's own rules.

1. **One permutation is not a null.** *The one that mattered.* The first version
   drew a **single** shuffle per window. It returned 0 everywhere, H1 held
   comfortably, and a positive result was ready to be written. Twenty draws and a
   worst-case statistic reversed it: the full-shuffle null is not always 0, and
   the locality-preserving null is usually larger than the observed set. The soup
   is what costs ten minutes; a permutation and a peel cost milliseconds, and
   there was never an excuse for one draw.
2. **The harness chose the window on the data.** It took the window maximising the
   observed set — which the preregistration lists, in as many words, under *what
   would make this experiment worthless*. It selected window 600, where the null
   already scores 16.
3. **The replacement rule then collapsed.** "Largest window where the null is
   empty" was written when the null was a single draw and empty everywhere; under
   twenty draws it selects windows at which nothing exists at all. There is now
   **no window selection**: the whole curve is scored against both nulls, which is
   what the preregistration said in the first place.
4. **A cell with no null-clean window is not a cell with an empty set.** It prints
   as `none`, not as `0`.

## Limitations

1. The locality-preserving null is post hoc. It was written because the
   preregistered one — a complete shuffle — is the weakest chance model available,
   and any structure at all beats it. That it is stronger does not make it
   *right*; a degree-preserving rewiring would be different again, and the number
   of ways to be wrong about a null is the real lesson of this experiment and of
   EXP-007.
2. Three seeds, three budgets, 1000 reactions, capacity 64, one founder corpus.
3. At 3000 ATP per reaction no self-maintaining set appears at any window in any
   seed, and at 50 ATP two of three seeds have no null-clean window at all. That
   looks like a band and is not claimed as one: with H1 failing its stronger null,
   there is no established quantity to have a band in.
4. H3's mechanism — that expensive sets cannot keep up with the discard rate —
   remains untested. The margins measured while correction 2 was still in force
   were −9%, −3%, −42% and −19%, i.e. sustaining reactions were if anything
   *dearer*, with a size-matched control noisier than the effect. It is reported
   here rather than scored.
