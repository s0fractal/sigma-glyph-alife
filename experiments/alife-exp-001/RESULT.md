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

> **Correction, 2026-08-26.** The two nulls below that *draw* — the size-matched
> and the agent-count-matched — were single draws when this was written.
> `tools/receipt_guard.py` found that in this published receipt after
> ALIFE-EXP-008 had a positive result reversed by exactly the same defect
> (`DECISIONS.md` D54, D58). They are sampled twenty times each now. The verdict
> got **stronger**, not weaker: the settled population's 2.593 is below the
> size-matched null's *minimum* over twenty draws (3.192, mean 3.682, max 4.454),
> so H2's failure does not depend on which draw was reported. The third null is
> not a chance model at all — it is the same 64 terms materialised — and is
> renamed `unreduced_same_terms` to stop it claiming to be one.

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
thunks. On the mixed run, instantiated at the budget the run turned out to
spend, that ceiling is 2840. The population's actual Σ size is 472, and it
occupies **182 distinct addresses — 6.41% of that ceiling**.

> **Corrected 2026-08-27** — see the [erratum](#erratum--2026-08-27). The
> ceiling above is **retrospective**: `budget` is instantiated at 2776, the ATP
> the run is now known to have spent. An operator sizing a machine *before* the
> run knows only the endowment, 192 000 ATP, and the same theorem then gives
> **192 064**. Both are correct instances of one theorem; only the second is
> available in advance. 6.41% is unchanged as a retrospective figure and is not
> a preflight one.

The bound is therefore honest and extremely loose, and the looseness has two
independent sources that this experiment can now separate: reduction rarely
spends all its budget on growth (472 of 2840), and what it does materialize
overlaps (182 of 472). An operator sizing a machine from the theorem
**preflight** — the only way an operator can size a machine — prepays about a
**thousand** times the memory a run of this shape actually needs; the
sixteenfold figure this paragraph used to give is what the theorem prepays once
you already know what the run spent.

## What this does to the research programme

- **RQ1's hypothesis is contradicted.** "Sharing factor grows super-linearly with
  population density" is not what a Σ-GLYPH population does when it merely runs.
  The interesting question moves: sharing is an *initial endowment* that
  evaluation depletes, so the substrate question becomes what pressure, if any,
  makes a population preserve it. That is `rebate_rate` — implemented, deliberately
  switched OFF here, and the subject of ALIFE-EXP-002.
- **The metric survived.** Three nulls, one preregistered and two not, agree.
- **The bound is worth reporting as a number, not an adjective.** 6.41%
  retrospectively; ~0.095% preflight. Two numbers, one theorem — see the
  [erratum](#erratum--2026-08-27).

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

---

## Erratum — 2026-08-27

ChatGPT's cross-repo review of `006b9bb`
([`reviews/chatgpt-2026-08-27.md`](../../reviews/chatgpt-2026-08-27.md)) found
that this receipt's headline percentage instantiates a **preflight** theorem
with a **hindsight** budget. The finding was verified against this experiment's
committed receipt before the review was recorded. **No measurement and no
verdict changes**: H1, H2 and H3 stand exactly as scored, every number in the
tables above is unmoved, and `results.json` is untouched. What changes is the
reading of one denominator.

`proofs/Population.lean` proves

```text
totalSize ≤ N + budget          provided  totalSpent ≤ budget
```

which is true of *any* `budget` bounding what the run spends. This receipt chose
the tightest one available after the fact, and then described the result in the
voice of somebody sizing a machine in advance. Those are two different
quantities and they now get two names:

| | `budget` | ceiling `N + budget` | 182 distinct addresses are | Σ size 472 is |
|---|---:|---:|---:|---:|
| **retrospective bound** — knowable only after the run | actual spent, 2 776 | **2 840** | **6.41%** | 16.6% |
| **preflight bound** — what an operator has in advance | endowment, 192 000 | **192 064** | **~0.095%** | 0.246% |

The endowment is not an estimate: `measure.py` builds `Economy(3000 × 64)` and
endows every agent with 3000, so 192 000 ATP is what this colony was committed
and 192 064 is the number the theorem hands an operator at preflight. The run
spent 1.45% of it.

**The corrected operational sentence.** This receipt said an operator "prepays
about sixteen times the memory a run of this shape actually needs". Sixteen is
`2840 / 182`, and it is what the theorem costs an operator who already knows the
answer. Against the preflight ceiling the overprovision is `192064 / 182` ≈
**1 055×** on distinct addresses and `192064 / 472` ≈ **407×** on Σ size —
three orders of magnitude, not one. The same correction is applied to the
sentence in `README.md`.

**Why this is not a defect in the theorem.** It is a defect in this document's
reading of it. `population_peak_size_thunks` is stated exactly as an operator
needs it — over a budget fixed in advance — and ALIFE-EXP-004 already decomposed
the retrospective looseness into its two factors. What no experiment here had
separated is the *third* factor, which is the whole distance between what a
colony is endowed and what it spends: on this run, a factor of 69. The successor
question that follows is sharper than "is the bound loose" and is not asked
anywhere in this repository yet:

> Preflight, the ceiling is dominated by ATP a colony never spends. Is there a
> tighter statement over *committed* budget — or does an operator simply have to
> size for the endowment and accept a thousandfold margin?

**Attribution.** The finding is ChatGPT's, from the review linked above; the
verification and this erratum are the repository's. Nothing about this
correction was found by a gate here, and the randomized suites could not have
found it: it is a claim about which of two true instantiations a sentence meant.
