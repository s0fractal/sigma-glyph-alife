# ALIFE-EXP-005 — result

Judged against
[`ALIFE-EXP-005-what-book-i-already-pays-preregistration.md`](../ALIFE-EXP-005-what-book-i-already-pays-preregistration.md),
committed as `8585e31` before this harness. The inherited corpus was committed as
`e19fc42` before the preregistration and reproduces EXP-001's fingerprint
`53cc6da80f66d220`.

**Provenance, stated at its real strength.** The preregistration and harness were
written by different models. The harness author worked from the committed
document and engine API, did not contact its author, and recorded the missing
choices in [`DECISIONS.md`](DECISIONS.md) before running the measurement. This is
a real separation of roles, but not an independent registry, external review,
or statistical replication.

| | |
| --- | --- |
| substrate | `impl/sigma_alife.py` 0.1.0 on the Book-I oracle `413d1f98…` |
| corpus | 64 terms, 4 families of 16, fingerprint `53cc6da80f66d220` |
| budget | 3000 ATP per agent; slice 32; at most 24 ticks; culling off |
| Arm A | Book-I trajectory, with copy pricing accumulated only in shadow |
| Arm B | same driver, but copy price enforced for `R-S` affordability and spend |
| cap | `10^9`; zero saturated firings and zero saturated pricing attempts |
| controls | seven, all passing before `results.json` was written |

## The preregistration was underdefined

That is the first result, and it was obtained before the numbers. The document
did not determine:

1. whether a `REF` expands its target under `deep_size`;
2. whether equality with the cap is saturation, and whether capped cost is
   charged or only observed;
3. whether failed/retried prices count as saturation events;
4. how “top decile” rounds and how to evaluate “fewer than 10%” exactly;
5. what numeric threshold “wide margin” means;
6. what numeric threshold “materially fewer” means;
7. which family statistic “discount” names, how ties score, and what a zero
   `drop` denominator means.

`DECISIONS.md` fixes those choices as D1–D7. The hypothesis thresholds are:
`2×` for H1's wide margin, at least 7 fewer settlers for H2, and total Arm-A
excess with unique extrema for H3. These are harness-author decisions, not facts
discovered in the output.

## Arm A — the discount exists, is small in total, and is concentrated

| family | Book-I ATP | shadow-copy ATP | excess | ratio | `R-S` firings | max excess | median | top-decile share |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `church` | 1512 | 1512 | 0 | 1.000 | 148 | 0 | 0 | undefined (zero excess) |
| `drop` | 216 | 216 | 0 | 1.000 | 0 | — | — | — |
| `dup` | 611 | 727 | 116 | 1.190 | 23 | 18 | 2 | 36.21% (top 3) |
| `random` | 437 | 472 | 35 | 1.080 | 4 | 12 | 9.5 | 34.29% (top 1) |
| **population** | **2776** | **2927** | **151** | **1.054** | **175** | **18** | **0** | **99.34% (top 18)** |

The total discount is only **151 ATP**, or 5.44% of Book-I spend. It therefore
fails the pre-decided `2×` meaning of “wide margin.”

The concentration half of H1 does hold: the six largest firings contribute
strictly more than half the excess, and six of 175 is **3.43%**. The population
top-decile share of 99.34% needs interpretation, however: 148 `church` firings
have exactly zero excess. The distribution is concentrated partly because most
`R-S` firings duplicate only a genesis-sized argument, not because the tail is
enormous. The largest observed per-firing saving is 18 ATP.

## Arm B — the discount is not binding at this budget

| family | enforced copy ATP | Book-equivalent ATP on that trajectory | settled Arm A | settled Arm B |
|---|---:|---:|---:|---:|
| `church` | 1512 | 1512 | 16/16 | 16/16 |
| `drop` | 216 | 216 | 16/16 | 16/16 |
| `dup` | 727 | 611 | 16/16 | 16/16 |
| `random` | 472 | 437 | 16/16 | 16/16 |
| **population** | **2927** | **2776** | **64/64** | **64/64** |

Arm B fires the same 175 `R-S` reductions and reaches the same successful
trajectory. All 64 agents settle in both arms, with identical settled-agent IDs.
The higher charge changes neither an answer nor an outcome under 3000 ATP per
agent. This is H2's strong falsifier: at this budget the discount is accounting,
not capability.

## Scorecard

| | preregistered claim | verdict |
|---|---|---|
| **H1** | discount is large **and** fewer than 10% of firings contribute over half | **FAILS** — concentration holds (3.43%), wide margin does not (1.054×) |
| **H2** | enforced copy pricing materially reduces settled agents | **FAILS** — 64/64 versus 64/64; same IDs |
| **H3** | `dup` largest, `drop` uniquely smallest, gap at least 2× | **FAILS** — `dup` is uniquely largest, but `drop` ties `church` at zero |

> **Review note (author of the preregistration, 2026-08-25).** H2's verdict is
> corrected to **UNDERPOWERED** by the addendum at the end of this document. The
> defect is in the preregistration, not in this harness: it fixed a budget chosen
> so that every agent settles and then asked whether fewer would. The scorecard
> row above is left as delivered.

H3's zero denominator is reported rather than converted to infinity. D6 says a
positive `dup` over zero `drop` satisfies the ratio component, but the tied
minimum still fails the fixed unique-family separation.

## Controls

All seven passed before the receipt was written:

1. copy price never undercharged any of 175 Arm-A firings; the preregistered
   13-node thunk regression reproduced Book `2` versus copy `14`;
2. deterministic I/K-only terms fired no `R-S` and had exactly equal prices;
3. shadow off/on preserved every result hash, status, and Book-I ATP count;
4. every one of Arm B's 64 settlers matched `sigma_glyph.eval_hash`;
5. ATP conservation and the population memory bound held in both arms;
6. the corpus fingerprint was `53cc6da80f66d220`;
7. a synthetic exponential DAG saturated, and every receipt aggregate exposed
   both attempt and firing saturation counts.

The real corpus reached the cap zero times. No capped value entered these
totals. `tools/test-all.sh` also completed with `TEST-ALL: ALL GREEN`, including
the Lean premise guard, need-packet validation, and byte-generating experiment
replays.

## Limitations

1. One corpus, one seed, and a deliberately generous budget. H2 says nothing
   about the scarcity regime where the extra 151 ATP could become binding.
2. Most `R-S` firings have zero excess. A top-decile statistic over all firings
   makes the concentration look stronger than a statistic conditioned on
   positive excess; only the preregistered all-firing distribution is scored.
3. `deep_size(REF(h)) = 1 + deep(h)` and capped charging are harness decisions.
   Another defensible reading would produce a different counterfactual and must
   not reuse this receipt.
4. The cap control was synthetic; the corpus never approached it. This result
   does not characterize the truly exponential tail the cap exists to bound.
5. Copy pricing is a counterfactual used to size one Book-I discount. No claim is
   made about Warrant, conformance, receipts, or what another implementation
   owes.

## Reproduction recipe

This recipe was added only after all seven controls and the complete repository
gate passed:

```sh
cd /Users/s0fractal/Projects/sigma-glyph-alife
python3 experiments/alife-exp-005/measure.py
python3 experiments/alife-exp-005/measure.py --record
git diff --exit-code experiments/alife-exp-005/results.json
DECISION_ARCHAEOLOGY=../decision-archaeology tools/test-all.sh
```

The first command is check-only. The second rewrites `results.json` only after
all controls pass. Once the receipt is tracked, the third command proves the
replay is byte-identical to it; the final command is the repository-wide gate.


---

# Addendum — where the discount binds

**Post hoc. Not preregistered. Written by the author of the preregistration, not
by the author of the harness**, which it reuses unchanged
(`addendum_scarcity.py` calls `measure.run_arm` at other budgets rather than
reimplementing the arms).

## The preregistration contradicted itself

```
corpus.py     ATP_PER_AGENT = 3000   # "as EXP-001: enough that everyone settles"
the document  H2: "materially fewer agents reach a normal form at the same budget"
```

A budget chosen so that everybody settles cannot host a hypothesis that fewer
will. Enforced copy pricing costs **151 ATP more across all 64 agents** — 2.4
each, against a reservoir of 3000, or 0.08%. H2 could not have been true.

This repository enforces exactly that rule elsewhere and did not apply it to its
own document: ALIFE-EXP-002 wasted two frames learning it (`DECISIONS.md` D20),
and ALIFE-EXP-003 carries control C7, which refuses to adjudicate a hypothesis on
a run where the arms cannot differ. **H2's verdict is UNDERPOWERED, not FAILS**,
and the harness author's report of it followed the document faithfully.

## The measurement H2 wanted

Same two arms, same corpus, same driver; only the per-agent budget varies.

| ATP/agent | settled, Book I | settled, copy-priced | Δ | book ATP | copy ATP |
|---:|---:|---:|---:|---:|---:|
| 9 | 9/64 | 9/64 | 0 | 517 | 517 |
| 14 | 12/64 | 12/64 | 0 | 795 | 752 |
| 18 | 21/64 | 21/64 | 0 | 971 | 913 |
| 25 | 30/64 | 29/64 | **−1** | 1264 | 1257 |
| 31 | 33/64 | 32/64 | **−1** | 1467 | 1483 |
| 43 | 39/64 | 38/64 | **−1** | 1790 | 1792 |
| 62 | 53/64 | 48/64 | **−5** | 2127 | 2183 |
| 3000 *(preregistered)* | 64/64 | 64/64 | 0 | 2776 | 2927 |

> **Book I's lazy, address-based pricing is capability, not accounting — inside a
> band.** At 62 ATP per agent, charging for the tree instead of the address costs
> five agents their normal form. Below the band nobody can afford to settle
> anyway; above it, everybody can. The preregistered budget sat above the band by
> a factor of roughly fifty.

That is the same shape ALIFE-EXP-003 found for its library: a mechanism that pays
only where a colony is poor enough to need it and rich enough to use it. Two
independent mechanisms, two bands, one substrate.

## What this addendum does not do

It does not rescue H1 or H3, whose verdicts stand as the harness author recorded
them. It does not re-run the scoring thresholds of `DECISIONS.md` D6. And it is
post hoc: the budgets were chosen after seeing that the preregistered one could
not bind, which is a weaker thing than choosing them in advance, and is why the
statement above is about a band rather than about a number.
