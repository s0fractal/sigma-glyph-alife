# ALIFE-EXP-009 — result

Judged against [`ALIFE-EXP-009-is-unresolved-a-death-or-a-wait-preregistration.md`](../ALIFE-EXP-009-is-unresolved-a-death-or-a-wait-preregistration.md),
committed before this harness; the frame, with its blind probe, before that.
Corpus is EXP-001's, pinned at `53cc6da80f66d220`.

## Scorecard

| | claim (with its preregistered number) | verdict |
|---|---|---|
| **H1** | ≥ 30 agents recovered at delivery spread 1.0 | **HOLDS** — 45 |
| **H2** | spread 4.0 recovers ≤ 50% of spread 1.0 | **HOLDS** — 7 against a ceiling of 22.5 |
| **H3** | 0 ATP spent while waiting, 100% of answers unchanged | **HOLDS** — exactly 0, and 100% in every cell |

The **direction** was filed in advance as decided, not discovered: a failed
resolve is not charged and `resumption_bound` makes interruption free, so waiting
cannot cost anything. What was open was the size of it.

## What the engine was throwing away

| ATP / spread | delivered | dead-on-unresolved | waiting | recovered | answers match | ATP while waiting |
|---|---:|---:|---:|---:|---:|---:|
| 300 / 0.5 | 64 | 20/64 | **64/64** | 44 | 44/44 | 0 |
| 300 / 1.0 | 64 | 19/64 | **64/64** | 45 | 45/45 | 0 |
| 300 / 2.0 | 32 | 16/64 | 38/64 | 22 | 22/22 | 0 |
| 300 / 4.0 | 16 | 15/64 | 22/64 | 7 | 7/7 | 0 |
| 100 / 1.0 | 64 | 11/64 | 56/64 | 45 | 45/45 | 0 |

*(with every withheld term present from the start, 64 settle at 300 ATP and 56 at 100)*

> **Treating an unresolved reference as death discarded 45 of 64 agents that Book
> I says were merely waiting.** At 300 ATP with delivery inside the run, letting
> them wait settles the **entire population** — the same number that settles when
> nothing was ever withheld. Waiting recovers *everything recoverable*, not merely
> more.

And it is nearly free. Same reservoirs, same deliveries, same ticks:

```
arm A: 19/64 settled, 2955 ATP
arm B: 64/64 settled, 3292 ATP        337 extra ATP bought 45 agents
```

Seven-and-a-half ATP per recovered agent, because every one of them had already
done its work and was sitting one force away from finishing. Arm A's settlers are
a strict subset of arm B's.

## H2: lateness is the only thing that gates it

Recovery falls 45 → 22 → 7 as the delivery window stretches from one run-length to
four, tracking the number of terms that arrive at all (64 → 32 → 16). Nothing else
limits it: no agent in any cell spent ATP while waiting, and no recovered agent
answered differently from the run where the term was never withheld.

## The bug this experiment was written to measure, and the one it found

The first was known: `impl/sigma_alife.py` has `RUNNABLE = (LIVE, STARVED)`, and
seven experiments ran on it.

The second was not. **H3's exact "0 ATP while waiting" caught a defect in this
harness before the result was written.** The first run reported 432 ATP spent
waiting, which the specification says cannot happen. It was real: the environment
was delivering **one node** — the withheld term's root — and not the term. An
agent forced the arrived `APPLY` for 3 ATP, received two thunks whose bytes had
never been stored, and blocked again on a child. Every one of the 28 charged
retries had *changed the term*, so they were progress into a second, unintended
block, and the metric was counting progress as waiting.

Fixed by delivering every node of the term, and by counting as waste only a retry
that changed nothing. An exact-value hypothesis earned its keep: a threshold like
"waiting is cheap" would have passed and hidden it.

## Corrections

1. **The environment delivered a node, not a term** (above). Before the fix the
   grid read 17 recovered at the primary cell instead of 45, and H1 and H3 both
   failed.
2. **H1's threshold was very nearly unreachable, and for the wrong reason.** It
   was set at 30 from the blind probe's "51 agents block", without asking how many
   of those could settle *even with the hash present*. Before the delivery fix
   that ceiling was 17 — so H1 could not have held at any magnitude of the effect.
   It holds now because the fix raised the ceiling to 45, not because the
   threshold was well chosen. See `DECISIONS.md` D68: preregister the **ceiling**
   of a statistic, not only a threshold on it.

## Limitations

1. One corpus, one withheld term per agent, deterministic arrivals. Real
   environments deliver on nobody's schedule.
2. The withheld terms are small by construction — the experiment is about *when*
   a hash arrives, not what it costs once it does.
3. Both arms are deterministic; there is no chance model here and the
   preregistration argues why rather than skipping one.
4. **Nothing here changes the engine's default.** `RUNNABLE` still excludes
   `UNRESOLVED`, so every previously committed receipt still replays. The
   capability is now available as an opt-in
   (`Population(..., wait_on_unresolved=True)`), and the default is left alone
   deliberately: changing it would silently move seven receipts and rewrite what
   this repository has already published.
