# ALIFE-EXP-003 — result

Judged against [`ALIFE-EXP-003-does-a-library-pay-preregistration.md`](../ALIFE-EXP-003-does-a-library-pay-preregistration.md),
committed before this harness existed; the frame was committed before that; the
corpus is EXP-001's, pinned at `53cc6da80f66d220`.

**Provenance, at its real strength.** One agent, one session, commit-order
preregistration — as in EXP-001 and EXP-002. What is different here is that the
one tuned number was chosen *before* any arm was run, by a stated blind
procedure, rather than repaired afterwards.

| | |
| --- | --- |
| question | given a fixed amount of ATP, is a colony better off funding a shared library than its own agents? |
| arms | share `s ∈ {0, 0.1, 0.25, 0.5, 0.75}` of the colony's ATP, at three scarcity levels, **same total in every arm** |
| controls | seven, all passing, including one on power |
| receipt | `results.json`, reproduced byte for byte |

## Scorecard, preregistered criteria, no adjustment

| | claim | verdict |
|---|---|---|
| **H1** | a library can pay | **HOLDS** — 37/64 settled at `s=0.25` against 33 at `s=0`, same total ATP |
| **H2** | it can be overfunded | **HOLDS** — the best share is interior (0.25); at 0.5 the colony settles 28, *worse than not having one* |
| **H3** | the advantage grows with redundancy | **FAILS** — Δ by N is +2, +7, +4: it does not increase |

This is the repository's first positive result, after two negatives. It is
reported with the mechanism check that follows, because a positive result from a
harness that could produce one by accident is worth less than a negative.

## The measurement

Every arm below has the **same total ATP**. A share funds the library; the rest
is split equally among 64 agents, who are therefore *poorer* in every library arm.

**total 2000 ATP** (at `s=0`, 33 of 64 settle unaided — the blind-chosen level)

| share | settled | agent ATP | library ATP | filed (paid) | donated (free) | failed fills | hits | never bought | settled per 1k ATP |
|---|---|---|---|---|---|---|---|---|---|
| 0.0 | 33/64 | 1467 | 0 | 0 | 0 | 0 | 0 | 0 | 22.49 |
| 0.1 | 35/64 | 1269 | 200 | 2 | 28 | 1 | 4 | 28 | 23.83 |
| **0.25** | **37/64** | 1017 | 500 | 6 | 24 | 67 | 11 | 24 | **24.39** |
| 0.5 | 28/64 | 699 | 1000 | 9 | 11 | 19 | 14 | 11 | 16.48 |
| 0.75 | 30/64 | 304 | 1500 | 29 | 0 | 5 | 31 | 5 | 16.63 |

**total 2800 ATP** — the same shape, peak at 0.1–0.25 (45–46 against 39).
**total 1200 ATP** — **no share beats `s=0`** (21 against 18–20, and 9 at `s=0.75`).

> A library pays only where a colony is poor enough to need one and rich enough
> to use one. At 1200 ATP the agents cannot afford even `size(nf)`, and every ATP
> given to a librarian is an ATP that would have settled somebody.

## The mechanism check, which is why this result is believable

Each arm gives the agents a *different* per-agent budget (31 ATP at `s=0`, 23 at
`s=0.25`), so a change in settled count could be an artifact of budget
granularity rather than of the library. It is not. Of the agents that settled in a
library arm and did **not** settle in the null:

| share | settled that `s=0` did not | of those, bought ≥1 memo install | that `s=0` settled and this arm lost |
|---|---|---|---|
| 0.1 | 4 | **4** | 2 |
| 0.25 | 10 | **10** | 6 |
| 0.5 | 14 | **14** | 19 |
| 0.75 | 13 | **13** | 16 |

**Every single one.** The winners are exactly the library's users, and the shape
of H2 becomes legible: raising the share keeps *buying* more settlers (4 → 10 →
14 → 13) while the shrinking agent budgets *lose* more (2 → 6 → 19 → 16). The
optimum is where those two curves cross, and past it a colony is funding a
library its citizens are too poor to visit.

## What the library actually does with the money

- **Most of it fails.** At `s=0.25`/2000 the librarian made 67 fills that never
  reached a normal form, against 6 that did. It still won. Demand-filled
  memoization is mostly waste plus a few entries that matter enormously.
- **Most entries are never bought again.** 24 of 30 held entries were never
  demanded a second time. That is the arithmetic the preregistration said not to
  claim as a discovery, now with a number.
- **The free entries are worthless here.** The `donation-only` diagnostic — agents
  filing their own finished work, at no cost, which is exactly ALIFE-EXP-002's
  mechanism — produced **30 entries and 0 hits**, and settled precisely as many
  agents as no library at all. EXP-002's negative reproduces exactly, at a
  different scarcity, in a different harness.

> Everything the library is worth comes from the entries somebody **paid** to
> derive on demand. Filing what agents happen to finish is free and, on this
> corpus, worth nothing.

## H3 fails, and the reason is visible

Δ over the null is +2 at N=16, +7 at N=32, +4 at N=64 — up then down. Two things
confound it and both are named rather than argued away: at N=16 the null settles
**0** agents, so the comparison is against a floor; and the corpus is fixed, so
growing N adds *different* terms rather than more copies of the same demand. A
proper test of redundancy would hold the term multiset and vary how many agents
demand each hash. That experiment is not this one.

## Corrections

One, and it is a scoring criterion rather than a run:

1. **H3's verdict was softened by the summary code and is not.** The first version
   scored H3 as holding because the last Δ exceeded the first. The
   preregistration says the advantage *increases* with population size; +2, +7,
   +4 does not increase. The check is now monotone and H3 reads FAILS.

Two design facts that were fixed before any arm ran, recorded here because they
decide what the numbers mean: `s = 0` has **no memoization at all** (not a memo
with an empty reservoir), and the `donation-only` arm is a diagnostic that is
**not** in the preregistration.

## Limitations

1. One corpus, one seed, no stochasticity — these runs are deterministic, so
   "reproducible" here means exactly that and not "robust".
2. Three scarcity levels, and the conclusion reverses at the poorest. Whether the
   band where a library pays is wide or narrow is unmeasured.
3. The librarian's policy is the crudest possible: fill on the first miss, draw
   the whole reservoir, never recurse, never evict, never rank by expected
   demand. Every one of those is a knob nobody has turned.
4. `settled agents` is the productivity measure. A colony might reasonably value
   other things — total structure materialized, sharing preserved, time to first
   answer — and this experiment measures none of them.
5. Nothing here says Book I permits or forbids any of it. That question is
   `needs/DA-SIGMA-0002` and is not decided by an experiment.
