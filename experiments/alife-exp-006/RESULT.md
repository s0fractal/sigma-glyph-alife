# ALIFE-EXP-006 — result

Judged against [`ALIFE-EXP-006-partial-progress-is-capital-preregistration.md`](../ALIFE-EXP-006-partial-progress-is-capital-preregistration.md),
committed before this harness; the frame, with its blind-chosen total, before
that. Corpus is EXP-001's, pinned at `53cc6da80f66d220`.

**Provenance.** Preregistration and harness by the same model in the same session
— the weaker arrangement. ALIFE-EXP-005 had two models and was better for it.
Every threshold here was numeric in the document beforehand, which is the only
compensation available.

## Why this experiment had to exist

This repository proved interruption is free, built its driver on it, advertised
"sporulation with a receipt" — and in five experiments never used it. `DECISIONS.md`
D40. This is the first measurement that needs the theorem.

## Scorecard

| | claim (with its preregistered number) | verdict |
|---|---|---|
| **H1** | an observable-state policy beats an even split by ≥ 8 agents | **FAILS** — best gap **+2** |
| **H2** | resumption is worth ≥ 8 agents against the best restarting arm | **HOLDS** — **+13 to +31** |
| **H3** | the premium grows with pulse granularity, doubling from 2 to 32 | **FAILS** — 13, 29, 27, 31, 31: rises then plateaus |

## H2 — what the theorem is worth, in agents

Same corpus, same 2000 ATP, same pulse schedule. The only difference is whether an
agent that runs out of budget keeps its body.

| pulses | best resuming | best restarting | premium |
|---:|---:|---:|---:|
| 2 | 38/64 | 25/64 | **+13** |
| 4 | 41/64 | 21/64 | **+29** |
| 8 | 47/64 | 20/64 | **+27** |
| 16 | 47/64 | 16/64 | **+31** |
| 32 | 47/64 | 16/64 | **+31** |

> **Resumption is worth about half the population.** At 16 pulses a resuming
> colony settles 47 of 64 agents on the same ATP that lets a restarting one settle
> 16. The restarting arms burn their reservoirs on attempts that end in
> `DISSONANCE(ATP Exhausted)` and start again from the root; `restart-eager`
> strands 1994 of the 2000 ATP it spends.

`restart-patient` — attempt only when the reservoir has doubled since the last
failure — is far better than the eager strawman (16 against 3 at fine pulses) and
is what H2 is scored against, as preregistered.

## H3 fails, and the reason is a ceiling rather than a mechanism

The premium is 13, 29, 27, 31, 31. It rises steeply from 2 to 4 pulses and then
stops. Not monotone (a dip at 8) and nowhere near doubling after 4.

The resuming arm is against its budget ceiling: 47 of 64 is what 2000 ATP can
settle at all in this corpus, and it reaches that from 8 pulses onward. The
restarting arm keeps degrading — 25, 21, 20, 16, 16 — monotonically, which is the
half of H3 that behaves as the hypothesis expected. The premium plateaus because
one side saturates, not because granularity stops mattering. **That observation is
post hoc**; the preregistered statement was about the gap and the gap does not
grow.

## H1 fails, and it fails interestingly

| pulses | equal | invested | smallest | random |
|---:|---:|---:|---:|---:|
| 2 | 36 | 38 | 38 | 38 |
| 4 | 39 | 41 | 40 | 41 |
| 8 | 47 | 46 | 45 | 45 |
| 16 | 47 | 40 | 39 | 44 |
| 32 | 47 | 47 | 45 | 44 |

Nothing the colony can *see* beats an even split by more than 2 agents, and
`random` — the control that isolates concentration from any cleverness — matches
the "smart" policies everywhere. So the advantage such policies do have is
concentration itself, not the proxies, and concentration is worth about two
agents.

The mechanism is the finding, and it is not what the preregistration assumed:

| pulses = 2 | settled | ATP spent | **stranded** |
|---|---:|---:|---:|
| `equal` | 36/64 | 1628 | **1003** |
| `invested` | 38/64 | 1999 | **44** |

Concentration recovers **96% of the stranded capital** — 1003 ATP down to 44 — and
converts it into **two** additional settled agents.

> **Stranded capital is not recoverable capital.** The ATP an even split leaves in
> unfinished agents is mostly sitting in agents that were nowhere near finishing.
> Recovering nearly all of it barely moves the outcome, because the binding
> constraint is the *distribution of remaining costs*, not the wastage.

That is why `invested` and `smallest` fail: both proxy "close to done" from
observable state, and neither predicts remaining cost. An agent's spend so far and
its current term size say almost nothing about what it still owes — which, on a
machine where a single `R-S` can cost `1 + size(z)`, is unsurprising in hindsight
and was not obvious in advance.

## Controls

All seven passed before the receipt was written, including:

- **C5 — resumption is actually exercised**: 44 agents starved, were refed, and
  went on to settle. The experiment tested the thing it exists to test.
- **C7 — power, from the preregistration**: the equal arm settles 73%, inside the
  25–75% band. Close to its edge, and it is the band that was fixed in advance.
- **C4** — a failed attempt in the restarting arms yields `DISSONANCE(ATP
  Exhausted)` and keeps no term, which is what makes them a model of *not having*
  this repository's extension.

## Corrections

One, and it invalidated the first run entirely.

1. **Integer division ate the fine-pulse arms.** The allocator wrote
   `budget // n`, which at 32 pulses is `62 // 64 = 0`: every agent received
   nothing, the equal arm settled 0 of 64, and the concentration policies handed
   the whole pulse to one agent and never passed the leftover on. The first grid
   would have been read as a dramatic finding about granularity. It was a division.
   `even_split` now distributes the remainder, and leftover passes down the order
   after an agent settles, as the preregistration says.

One harness decision the preregistration did not make: **a settled agent returns
its unspent ATP to the pool at the end of a pulse**, identically in every arm.
Without it, a policy that settles agents early is penalised by the ATP frozen
inside them.

## Limitations

1. One corpus, one seed, one total. The premium is measured at 2000 ATP; whether
   it is worth half a population elsewhere is untested.
2. `restart-patient`'s doubling rule is one strategy among many. A restarting
   machine with a better waiting rule would narrow H2's gap, and no search was
   made for one.
3. Only two observable proxies were tried. H1's failure says these two do not
   predict remaining cost; it does not say none can.
4. Pulses are equal and deterministic. Real drought is neither.
