# ALIFE-EXP-004 — result

Judged against [`ALIFE-EXP-004-alphabet-or-structure-preregistration.md`](../ALIFE-EXP-004-alphabet-or-structure-preregistration.md),
committed before this harness; the corpora were committed before that.

This experiment was designed to **destroy** this repository's most-quoted
sentence. It did not.

| | |
| --- | --- |
| prompted by | an external review (Claude Fable 5, 2026-08-25) |
| design | 4 genesis fractions × 10 seeds × 64 agents, each measured unreduced and settled |
| anchor | at `g = 0.7` the generator is ALIFE-EXP-001's exactly |
| controls | four, including one that proves the two metrics disagree where they must |

## The objection was right, and the finding survives it

`sharing_factor` counts the three genesis atoms like any other address. Three
agents that have all reduced to the single leaf `I` score **3.0** — a perfect
score from a population with no shared structure whatsoever. That is control C1,
and it means EXP-001's number genuinely could not distinguish *"reduction
consumes shared structure"* from *"reduction consumes the alphabet"*.

So both were measured, on the same populations, with a metric that counts only
`APPLY` nodes and excludes genesis entirely.

| g | metric | unreduced | settled | Δ | seeds falling |
|---|---|---|---|---|---|
| 0.3 | sharing (EXP-001's) | 3.047 | 1.816 | −1.231 | 10/10 |
| 0.3 | **structural** | 2.024 | 1.337 | **−0.687** | **10/10** |
| 0.3 | pairwise Jaccard | 0.043 | 0.005 | −0.038 | 10/10 |
| 0.5 | sharing | 3.432 | 2.193 | −1.239 | 10/10 |
| 0.5 | **structural** | 2.158 | 1.500 | **−0.658** | **10/10** |
| 0.7 | sharing | 4.153 | 2.609 | −1.544 | 10/10 |
| 0.7 | **structural** | 2.435 | 1.579 | **−0.856** | **10/10** |
| 0.7 | pairwise Jaccard | 0.060 | 0.015 | −0.045 | 10/10 |
| 0.9 | sharing | 5.430 | 4.042 | −1.388 | 9/10 |
| 0.9 | **structural** | 2.876 | 2.259 | **−0.617** | 9/10 |

## Scorecard

| | claim | verdict |
|---|---|---|
| **H1** | EXP-001 replicates under its own metric | **HOLDS** — 10/10 seeds |
| **H2** | the drop does *not* survive the separation | **FAILS** — it survives in 10/10 seeds |
| **H3** | the drop scales with the alphabet | **FAILS** — flat: −1.23, −1.24, −1.54, −1.39 |

H2 was the hypothesis that mattered and it was written so that this repository
would lose. It lost the hypothesis and kept the finding:

> **Reduction consumes shared structure, and not merely the alphabet.** Excluding
> genesis and counting only `APPLY` nodes, a settled population's structural
> sharing falls in every seed at every alphabet fraction tested. Pairwise
> structural overlap falls with it — 0.060 to 0.015 at the anchor — so this is not
> an aggregate artifact either. Compound occurrences fall 722 → 133 and distinct
> compound addresses 285 → 97: the population loses structure wholesale, and what
> is left repeats less than what it replaced.

H3's failure says the same thing from the other side: if the alphabet were
producing the effect, a corpus built from few genesis atoms would show little of
it. The drop is essentially flat across `g ∈ {0.3 … 0.9}`.

## What the objection did change

Three things, none of them the headline:

1. **EXP-001 was one seed.** It is now ten, at four alphabet fractions, with the
   original as an anchor. "Byte-for-byte reproducible" was never robustness, and
   this is the first result here that has any.
2. **The metric was ambiguous and is no longer the only one reported.**
   `structural_sharing` and `pairwise_jaccard` are engine metrics now, with C1 as
   the standing control that they disagree with `sharing_factor` exactly where
   they must.
3. **The convergence caveat has a number.** 210 of 2016 settled pairs at the
   anchor have no compound structure on either side — agents that reduced to a
   bare leaf. Those pairs are *excluded* from the Jaccard rather than scored 0 or
   1, since either would be a lie, and the count is reported beside the mean.

## Limitations

1. Ten seeds, one generator family, one budget. This is a direction and a spread;
   no p-value is offered and none should be inferred.
2. `structural_sharing` treats an unresolvable thunk as a leaf — conservative,
   since it can only *understate* structure, but it means a population that never
   forces anything looks structureless.
3. Reduction here runs to settling with a generous budget. Whether the same holds
   under scarcity, where agents stop mid-term, is untested — and EXP-003's arms
   live exactly there.
4. Nothing here revisits *why*. EXP-001's mechanism paragraph blames `R-I`, `R-K`
   and the head of `R-S` eating the alphabet; this result says the alphabet is not
   the whole story, and does not say what the rest of it is.
