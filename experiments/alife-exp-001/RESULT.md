# ALIFE-EXP-001 — result

Judged against [`ALIFE-EXP-001-anastomosis-preregistration.md`](../ALIFE-EXP-001-anastomosis-preregistration.md),
written before `measure.py` existed. The corpus was committed before the
preregistration. No term was added or removed after a number was known.

**Provenance, stated at its real strength.** The corpus, the preregistration and
the harness were written in one session by one agent, and the ordering above is
the commit order, not an independent registry. That is weaker than a
preregistration a second party timestamped, and it is the strongest claim this
receipt can make. What it does establish is that the corpus digest in
`results.json` is the digest of the terms committed before the hypotheses, and
that a replay reproduces the file byte for byte.

| | |
| --- | --- |
| substrate | `impl/sigma_alife.py` 0.1.0 on Σ-GLYPH Book I, oracle `413d1f98…` |
| corpus | 64 terms, 4 families of 16, fingerprint `53cc6da80f66d220` |
| budget | 3000 ATP per agent, endowed from a commons pool, nothing minted |
| policy | rebates OFF, transfers OFF, culling OFF (see below) |
| run | ticks until nothing is runnable; every family settled fully (64/64) |
| controls | five, all passing, all able to fail |
| receipt | `results.json`, reproduced byte for byte on a second run |

## The measurement

| run | sharing at birth | sharing settled | Δ | Σ size | distinct addresses | ATP spent |
|---|---|---|---|---|---|---|
| `church` | 1.455 | 4.316 | +2.861 | 82 | 19 | 1512 |
| `drop` | 1.000 | 1.778 | +0.778 | 48 | 27 | 216 |
| `dup` | 1.000 | 2.071 | +1.071 | 176 | 85 | 611 |
| `random` | 1.000 | 2.049 | +1.049 | 166 | 81 | 437 |
| **mixed** | **1.085** | **2.593** | **+1.509** | **472** | **182** | **2776** |

| null | sharing | Σ size | distinct | agents | |
|---|---|---|---|---|---|
| size-matched (preregistered) | 4.454 | 481 | 108 | 17 | |
| agent-count-matched | 3.926 | 1543 | 393 | 64 | post hoc |
| same terms, unreduced | 3.989 | 1500 | 376 | 64 | post hoc |

## H1 holds and it means nothing on its own

Sharing factor rises from 1.085 to 2.593 over a mixed run. Every family rises.
Taken alone this is the result the proposal predicted, and the preregistration
says why it must not be reported as one: agents are born as root thunks, so a
population at birth is 64 distinct addresses of size 1 and *cannot* share.
Anything that materializes structure raises the number from there.

## H2 fails, in all three nulls, in the same direction

**A settled population shares LESS than an unreduced one.** 2.593 against 4.454
(the preregistered size-matched null), 3.926 (agent-count-matched) and 3.989 (the
same 64 terms, materialized but never run). The preregistered null draws 17
agents rather than 64 — unreduced terms are larger, so matching the node count
leaves fewer of them, and a larger tree repeats the genesis atoms inside itself
more often. That confound is real, which is why two further nulls were run; both
land in the same place, and the one that removes the confound entirely (the same
terms, unreduced) is the sharpest: **these exact agents shared 3.989 before they
ran and 2.593 after.**

So in this substrate, on this corpus, with no economic pressure:

> Reduction consumes shared structure faster than it creates it. Content
> addressing gives a population its sharing at birth — from the genesis alphabet
> and from whatever the generator repeats — and evaluation spends that sharing
> down. The anastomosis the proposal predicted is not there to be found in
> reduction alone.

The mechanism is not mysterious once the number is on the table. Sharing in a
CAS is *repetition*, and the three genesis atoms are the most repeated objects
in any SKI population. Reduction eats exactly those: `R-I`, `R-K` and the head
of `R-S` consume `I`, `K` and `S` occurrences and leave behind the idiosyncratic
residue that made each term different. `R-S` does duplicate, and duplicates by
address at no new cost — the `dup` family rises most among the non-`church`
families — but duplication of one argument does not pay for the alphabet the
whole spine burned to perform it.

`church` is the exception worth naming: +2.861, the largest rise, because a
Church numeral applied to combinators normalizes to a small term built almost
entirely from the shared alphabet. That is convergence, not symbiosis: sixteen
agents ending at nearly the same answer.

## H3 holds, and gives the bound a number

`proofs/Population.lean` proves `Σ size ≤ N + budget` for agents born as root
thunks. On the mixed run that ceiling is 2840. The population's actual Σ size is
472, and it occupies **182 distinct addresses — 6.41% of the proved ceiling**.

The bound is therefore honest and extremely loose, and the looseness has two
independent sources that this experiment can now separate: reduction rarely
spends all its budget on growth (472 of 2840), and what it does materialize
overlaps (182 of 472). An operator sizing a machine from the theorem prepays
about sixteen times the memory a run of this shape actually needs.

## What this does to the research programme

- **RQ1's hypothesis is contradicted.** "Sharing factor grows super-linearly with
  population density" is not what a Σ-GLYPH population does when it merely runs.
  The interesting question moves: sharing is an *initial endowment* that
  evaluation depletes, so the substrate question becomes what pressure, if any,
  makes a population preserve it. That is `rebate_rate` — implemented, deliberately
  switched OFF here, and the subject of ALIFE-EXP-002.
- **The metric survived.** Three nulls, one preregistered and two not, agree.
- **The bound is worth reporting as a number, not an adjective.** 6.41%.

## Limitations, named rather than left to a reader

1. One generator, 64 agents, one seed. Nothing here is a claim about λ-terms in
   general, and the families are hand-built to be interpretable, not
   representative.
2. Culling is OFF. An archived agent stops contributing to the census, so culling
   would raise the sharing factor by removing bodies from the count — the exact
   confound the experiment is about. Any future run that culls must re-derive its
   null.
3. Sharing is measured over MATERIALIZED terms. Structure that an agent never
   forced is one thunk, counted once, whatever it points at. A population that
   settles without forcing much will look like it shares little.
4. No selection, no mutation, no reproduction. The engine has the operators; this
   experiment does not use them, and no sentence here is about evolution.
5. The two post-hoc nulls were written after the preregistered one returned an
   answer. They are labelled in the receipt and in the table above, and the
   preregistered null's number is reported first and unmodified.
