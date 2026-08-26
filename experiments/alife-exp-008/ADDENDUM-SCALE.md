# Addendum to ALIFE-EXP-008 — ten times the reactions, four times the seeds

**Post hoc. Not preregistered.** Written to re-check the one verdict in this
repository where more machine could buy something: H3 ("what persists is cheap")
was reported **UNADJUDICATED** because no self-maintaining set survived the
locality-preserving null, so there was nothing to price.

**First, a correction to why it was unadjudicated.** It was never a hardware
limit. Peak resident memory of the heaviest run here is **25 MB** and the grid
runs in seconds; "power" in these results means whether the *design* could show
an effect, not whether the machine could finish. What more machine buys is
**scale** — and 1000 reactions may simply be too short a run for a population to
organise in. That is the question this addendum asks.

| | |
| --- | --- |
| scale | 10,000 reactions × 12 seeds, against EXP-008's 1000 × 3 |
| everything else | EXP-008's, unchanged: same chemistry, same definition, same two chance models at 20 draws |
| machine | Apple M4 Pro, 12 workers — 242 s of CPU in 23 s of wall clock |

## H3 stays unadjudicated, and the negative is much stronger

**0 of 84 cells** clear the locality-preserving null. The observed self-maintaining
set is not merely below chance — across twelve seeds and seven windows it is
**zero everywhere but one cell**, which found six.

"We did not see it in 1000 reactions across three seeds" is now "we did not see it
in 10,000 across twelve". There is still nothing to price, and H3 remains
unadjudicated rather than refuted: a hypothesis about the cost of sustaining a set
cannot be tested where no set sustains itself.

## Why: the chemistry prices itself out of its own budget

| seed | 1000 | 2000 | 4000 | 10,000 |
|---:|---|---|---|---|
| 20260825 | 46 / 62.9% | 21 / 53.2% | 7 / 32.8% | **3 / 13.7%** |
| 20260830 | 45 / 52.2% | 16 / 36.2% | 5 / 23.3% | **2 / 10.4%** |
| 20260833 | 37 / 54.2% | 14 / 42.9% | 3 / 29.4% | **2 / 13.2%** |
| 20260831 | 61 / 37.3% | 62 / 20.3% | 55 / 11.2% | 46 / 5.0% |
| 20260836 | 44 / 57.8% | 46 / 36.3% | 50 / 20.2% | 44 / 8.8% |
| 20260829 | 36 / 86.2% | 29 / 74.7% | 5 / 84.2% | **6 / 93.7%** |

*(distinct hashes alive / reaction success rate; six of twelve seeds shown)*

> **Success falls from 54% to 16% on average while the reaction budget never
> changes.** Products accumulate structure, the next reaction has to reduce a
> bigger term, and a fixed 200 ATP stops affording it. The soup does not run out
> of molecules; it runs out of *money for them*.

Diversity splits into two regimes rather than simply collapsing. Five of twelve
seeds fall below the eight-hash floor EXP-007 preregistered as its own power
condition — two of them to **two** surviving hashes — while seven hold between 20
and 46. And seed `20260829` is the interesting one: diversity falls to six and
success **rises to 93.7%**, a small cycle of cheap reactions that has found an
attractor it can afford.

That last one is what an organisation would look like if this substrate produced
one, and the self-maintenance metric scores it **zero** — because those six
molecules are not producing each other; they are being produced *cheaply from
whatever is around*.

## What this changes

- **EXP-008's H3 verdict stands**, with a stronger negative behind it.
- **EXP-007's power condition was doing more work than it looked.** It required
  ≥ 8 distinct hashes; at 10,000 reactions five of twelve seeds would fail it, so
  that condition is not a formality at longer horizons.
- **A new open question, sharper than the one it replaces:** the chemistry has an
  affordability horizon. A fixed per-reaction budget buys a shrinking fraction of
  a growing soup, so any long-run organisation would have to be made of reactions
  that stay *cheap* — which is what H3 guessed at and could not test. The way to
  test it is a budget that scales with the soup, not more seeds.

## Reproduction

```sh
python3 experiments/alife-exp-008/addendum_scale.py --record
git diff --exit-code experiments/alife-exp-008/addendum_scale.json
```

Twelve workers, about 25 seconds. The receipt records every seed's trajectory and
both null distributions with their draw counts.
