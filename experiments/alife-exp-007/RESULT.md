# ALIFE-EXP-007 — result

Judged against [`ALIFE-EXP-007-do-organizations-form-preregistration.md`](../ALIFE-EXP-007-do-organizations-form-preregistration.md),
committed before this harness; the frame, with its blind-chosen budget, before
that. Founders are EXP-001's, pinned at `53cc6da80f66d220`.

**All three preregistered criteria were met. None of them survives its null.**

That sentence is the result. The nulls were **not** preregistered — a defect in
the document, recorded in `DECISIONS.md` D50 — and they were written after the
criteria came back green, which is the worst possible time to be asking whether a
statistic means anything and still better than not asking.

## What the criteria said

| | preregistered criterion | as measured |
|---|---|---|
| **H1** | closure ≥ 0.30 with ≥ 8 distinct hashes, majority of seeds | met, 2/3 |
| **H2** | an L1-core of size ≥ 3, majority of seeds | met, 3/3 — cores of **146, 156, 42** |
| **H3** | cores at 50 and 3000 ATP overlap by Jaccard < 0.5 | met, 3/3 — **0.020, 0.026, 0.000** |

| seed | success | closure | distinct | core | L0 | mean cost |
|---|---:|---:|---:|---:|---:|---:|
| 20260825 | 63% | 0.339 | 46 | 146 | 0 | 92.7 |
| 20260826 | 49% | 0.385 | 42 | 156 | 1 | 97.2 |
| 20260827 | 43% | 0.228 | 38 | 42 | 1 | 109.2 |

## What the nulls said

**H2 — refuted.** Shuffle the reaction graph: keep every reactant pair, keep the
product multiset, permute which product came from which pair. A chance graph of
the same density yields a core **as large or larger**, every time.

| budget | seed | core observed | core, shuffled graph |
|---:|---:|---:|---:|
| 50 | 20260825 | 24 | **84** |
| 50 | 20260826 | 30 | **62** |
| 200 | 20260825 | 0 | 0 |
| 200 | 20260826 | 77 | **111** |

> An L1-core in a bounded soup with high turnover is not evidence of an
> organization. Almost every molecule is produced from molecules that were
> themselves products, so "every member is produced by members of the set" is
> nearly free. The core is not a distinguished subset: at the primary budget it
> contains **43 of the 46** hashes still alive at the end — and is three times
> larger than the soup, so 70% of it is molecules that died long ago.

**H3 — uninformative.** The cores at 50 and 3000 ATP overlap by 0.055. So do the
molecules: **product overlap 0.032**. The cores are, if anything, marginally
*more* similar than the chemistries that produced them. A near-zero core overlap
across budgets measures molecular turnover, not organizational selection. The
preregistered threshold of 0.5 was met by a margin that says nothing.

**H1 — mostly explained.** Replay the same product multiset into the same bounded
soup in a random order and closure barely moves:

| budget | seed | closure | closure, shuffled order |
|---:|---:|---:|---:|
| 50 | 20260825 | 0.434 | 0.421 |
| 50 | 20260826 | 0.429 | 0.363 |
| 200 | 20260825 | 0.263 | 0.203 |
| 200 | 20260826 | 0.348 | 0.295 |

Between 85% and 97% of the closure is reproduced by shuffling. A residual
remains, and its size moved when the nulls were corrected:

> **Correction, 2026-08-26.** These nulls were **single draws**. ALIFE-EXP-008
> then had a finished positive result reversed by going from one draw to twenty
> (`DECISIONS.md` D54), and `tools/receipt_guard.py` found the same defect sitting
> in this receipt. Sampled twenty times through `impl/sigma_nulls.py`, the two
> verdicts above do not move — a chance graph still yields a core as large, the
> soups still overlap no more than the cores — but the closure residual falls from
> **+0.012 … +0.065** to **−0.008 … +0.044**, i.e. one cell is now *below* its
> null. The residual was already reported as unscored; it is now also reported as
> not consistently positive.

## The scorecard that matters

| | after its null |
|---|---|
| **H1** | **not established** — the criterion was met; 85–97% of it is chance |
| **H2** | **artifact** — chance graphs of the same density score higher |
| **H3** | **uninformative** — measures turnover; the soups overlap even less |

## What this says, and what it does not

It does **not** say that AlChemy's organizations are an artifact. Fontana & Buss
run from a near-tabula-rasa state, over far longer horizons, and their
organizations are sets that *persist and reproduce themselves in the population* —
not, as here, sets extracted from a whole reaction history. The founders here are
a hand-built 64-term corpus, and 1000 reactions is a short run. `RELATED.md`.

What it does say is narrower and useful:

> **A closure statistic and an L1-core, computed over the reaction history of a
> bounded high-turnover soup, are met by chance.** Anyone measuring organization
> this way — including this repository, an hour ago — needs the shuffled-graph
> null beside the number, or the number is graph density with a biological name.

And the substrate's own question, H3, remains open rather than answered. Price
plainly changes *what gets made*: mean reaction cost runs 25.5 → 92.7 → 384.7 →
1003 across the budget sweep, and the resulting molecules barely overlap. Whether
price selects an *organization* cannot be told with a statistic that does not
discriminate.

## Controls

All seven passed before the receipt was written. The one that earned its place is
**C5**: the core algorithm must return the empty core on an open chain
(`(a,b)→c` alone), because a peeling bug produces cores from anything. It passed —
which is what makes the null's verdict interesting rather than a bug report.

Also of note: **C4**, no `DISSONANCE` ever entered the soup. A failed reaction
costs its ATP and adds nothing, which is what makes this a chemistry with a
price rather than one with a poison.

## Limitations

1. **The core is computed over history, not over a persisting set.** That is the
   single biggest gap between this measurement and Fontana's definition, and the
   obvious next design: require a core's members to be present in the soup and
   self-maintaining under the discard rule.
2. Three seeds, 1000 reactions, capacity 64, one founder corpus. AlChemy ran far
   longer from far less.
3. The nulls are post hoc. They are in the receipt and replayable, and they were
   written after the criteria came back green.
4. `L0` — self-computing terms, `(T,T) → T` — appeared at most once per run. Not
   enough to say anything about.
5. Nothing here is about Book I. Reactions are ordinary applications priced
   exactly as the specification prices them.
