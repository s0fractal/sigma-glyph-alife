# Where the proved ceiling's slack lives

**Descriptive analysis, not an experiment.** No hypotheses, no preregistration, no
nulls, no measurement taken: it re-reads receipts already committed and factors a
number this repository has published seven times. Raised independently by two
external reviews — Claude Fable 5 and Grok, August 2026 — and it is the cheapest
open question on the list, because the data was already on disk.

`proofs/Population.lean` proves `Σ size ≤ N + spent`. ALIFE-EXP-001 reported that
a settled population occupies **6.41%** of that ceiling. That figure is a product:

```
occupancy  =  Σ size / ceiling      ×   distinct addresses / Σ size
              ── metabolic ──           ── morphological ──
              budget the run did        structure the population
              not turn into nodes       holds more than once
```

Only the product had ever been tracked.

## They are not two views of the same thing

| genesis fraction | metabolic | morphological | occupancy |
|---:|---:|---:|---:|
| 0.3 | 17.2% | 55.6% | 9.57% |
| 0.5 | 16.7% | 46.1% | 7.62% |
| 0.7 | 14.0% | 38.6% | 5.37% |
| 0.9 | 13.2% | 25.3% | 3.23% |

*(ALIFE-EXP-004, ten seeds per row, settled populations)*

> **The alphabet moves one factor and barely touches the other.** Across the
> sweep the morphological factor travels **30 points** (55.6% → 25.3%) while the
> metabolic factor moves **4** (17.2% → 13.2%). Sharing is what the alphabet
> buys; the budget-to-structure conversion is nearly indifferent to it.

And the ceiling is dominated by the factor the alphabet does *not* control: a run
converts about **15% of its proved budget into materialised nodes at all**, then
de-duplicates roughly 59% of those away. The theorem is loose mostly because
**reduction spends budget on reductions, not on structure** — not because the
population shares.

## The two halves have different dynamics

| tick | Σ size | distinct | ceiling | metabolic | morphological | occupancy |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 64 | 59 | 64 | 100.0% | 92.2% | 92.19% |
| 1 | 536 | 228 | 1550 | 34.6% | 42.5% | 14.71% |
| 2 | 520 | 211 | 2195 | 23.7% | 40.6% | 9.61% |
| 3 | 548 | 212 | 2492 | 22.0% | 38.7% | 8.51% |
| 4 | 504 | 202 | 2716 | 18.6% | 40.1% | 7.44% |
| 5 | 478 | 184 | 2838 | 16.8% | 38.5% | 6.48% |
| 6 | 472 | 182 | 2840 | 16.6% | 38.6% | 6.41% |

> **The morphological factor is decided at materialisation and then frozen.** It
> falls from 92% to 42.5% in the first tick — the burst that turns 64 thunks into
> 536 nodes — and then sits between 38.5% and 40.6% for the rest of the run,
> moving less than 4 points while the population reduces itself to normal form.
>
> **The metabolic factor decays monotonically with every action**, 100% → 16.6%,
> and never recovers. Every tick spends budget; only the first tick builds.

That is the same story ALIFE-EXP-001 told about sharing — *an endowment that
evaluation spends down* — now visible as the arithmetic underneath it, and
separated from a second effect it had been multiplied with.

## Per family, settled

| family | metabolic | morphological | occupancy |
|---|---:|---:|---:|
| `church` | 5.4% | 23.2% | 1.24% |
| `drop` | 20.7% | 56.2% | 11.64% |
| `dup` | 28.1% | 48.3% | 13.56% |
| `random` | 36.6% | 48.8% | 17.88% |
| mixed | 16.6% | 38.6% | 6.41% |

`church` is the extreme on both axes: 1512 ATP for 82 nodes ending at 23%
distinct — Church numerals reduce a great deal and converge on small terms built
from the shared alphabet. It is the family that makes the mixed number look
worse than any other family's, and it does so through *both* factors at once.

## What this is good for, and what it is not

**Good for:** an operator sizing a machine from the theorem prepays about 16× the
memory a run of this shape needs, and now knows which 16×. Roughly 6× of it is
budget that never became structure, and roughly 2.6× is structure held more than
once. The first is a property of the *terms*; the second is a property of the
*alphabet*. They should be estimated separately.

**Not:** a tighter bound. Nothing here proves anything, and neither factor is
bounded below by any argument given here — both are measurements on one corpus at
one budget. Whether a tighter theorem exists for populations with high sharing is
Grok's question 4 and remains open.

## Reproduction

```sh
python3 experiments/analysis-001-where-the-slack-lives/analyse.py --record
git diff --exit-code experiments/analysis-001-where-the-slack-lives/analysis.json
```

Inputs are the committed receipts of ALIFE-EXP-001 and ALIFE-EXP-004. If either
is re-recorded, this re-derives from the new numbers and the diff says so.
