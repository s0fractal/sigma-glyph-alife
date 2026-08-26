# ALIFE-EXP-009 — is an unresolved reference a death or a wait?

**Preregistration. No measurement has been taken** except the blind blocking
probe recorded in `alife-exp-009/corpus.py`, which counts one thing.
Non-normative.

## Why this experiment exists

Book I §3.5 defines `DISSONANCE(Unresolved Reference)` as what happens when
*"`h` is not in the store and is not an intrinsic axiom"* — an outcome **relative
to a store**. §3.4 adds that a failed resolve **is not charged**. Verified at the
pinned revision: the same hash, at the same budget, returns
`DISSONANCE(Unresolved)` for 4 ATP against one store and a settled term for 7
against a store that has since grown.

`impl/sigma_alife.py` has `RUNNABLE = (LIVE, STARVED)`. An agent that reaches a
hash the store does not hold **is dead here**, and is merely *waiting* in the
specification it consumes. Seven experiments were run on that engine without
anybody noticing.

So this experiment is half research and half a bug with a measurement attached,
and it is written that way.

## What is already decided, and will not be claimed as a finding

- **The direction.** A failed resolve costs nothing and `resumption_bound` says an
  interrupted agent keeps its work for free, so letting an unresolved agent wait
  cannot cost anything and cannot settle fewer agents. **Arm B ≥ Arm A is
  analytic.** Reporting it as a discovery would be dressing arithmetic as a
  result, which is the failure sigma-glyph's own EXP-004 preregistration warns
  against.
- **That waiting is legitimate.** Book I's determinism is relative to a store;
  resuming against a grown store is a different input, not a violated contract.

What is open is the **magnitude**, what it depends on, and whether waiting is
genuinely free in a running population rather than in a one-line argument.

## No chance model, and why

Both arms are deterministic and differ in exactly one bit — whether an
`UNRESOLVED` agent re-enters the runnable set. There is no statistic here that
chance could produce, so `DECISIONS.md` D50 does not apply and no null is
preregistered. What replaces it is the power condition below, which is the thing
that can actually make this measurement empty.

## Hypotheses, each with its number

**H1 — the magnitude is large.** At the primary budget and a delivery spread of
1.0, Arm B settles at least **30 more** agents than Arm A, out of the 51 that the
blind probe says block.
*Falsifier:* fewer than 30 — most blocked agents would then fail for some other
reason even once their hash arrives, and the engine's treatment of UNRESOLVED
would be costing far less than it looks.

**H2 — lateness is the limit.** At a spread of 4.0, where roughly a quarter of the
withheld terms arrive before the run ends, the recovery is at most **half** of the
recovery at spread 1.0.
*Falsifier:* recovery is flat in the spread, which would mean arrival time is not
what gates it and something else is.

**H3 — waiting is free, and it does not change the answer.** Two exact numbers:
ATP spent by agents while in the waiting state is **exactly 0**, and **100%** of
recovered agents reach the same result hash they reach when the withheld term is
present from the start.
*Falsifier:* either is not exact. A waiting agent that costs ATP is a different
mechanism from the one Book I describes, and a recovered agent that answers
differently would mean waiting has changed the computation rather than delayed it.

## Design

- 64 agents, EXP-001's corpus, pinned at `53cc6da80f66d220`, each applied to one
  withheld hash. Leftmost-outermost forces the agent's own work first and the
  withheld hash only when the function part is normal, so an agent does its work
  and *then* blocks.
- **Arm A** — `UNRESOLVED` is terminal, exactly as the engine behaves today.
- **Arm B** — an `UNRESOLVED` agent re-enters the runnable set each tick and
  retries. Implemented in the harness, not by changing `RUNNABLE`: altering that
  constant would change the behaviour of every other experiment in this
  repository and silently move seven committed receipts.
- Identical corpus, identical total ATP, identical delivery schedule in both arms.
- Budgets `100, 300`; delivery spreads `0.5, 1.0, 2.0, 4.0` as multiples of the
  run's length.
- Reported: settled and blocked counts per arm, ATP spent, ATP spent while
  waiting, recovered agents, and how many recovered agents match the
  present-from-the-start answer.

## Controls

1. **C1 — the arms are identical apart from the one bit.** With no withheld term
   ever released, Arm B must equal Arm A exactly: same settled count, same ATP,
   same statuses.
2. **C2 — the schedule is identical across arms**, and each withheld term enters
   the store at the same tick in both.
3. **C3 — conservation and the memory bound**, every tick, both arms.
4. **C4 — a withheld hash really is absent** at the start: every one of them must
   produce `DISSONANCE(Unresolved Reference)` from the initial store.
5. **C5 — power, from this document.** At least **25%** of the population must
   block on a withheld hash at the primary budget, or the run is
   **UNADJUDICATED**. The blind probe says 80%; the condition is here so that a
   corpus change cannot quietly empty the experiment.
6. **C6 — the corpus** is EXP-001's, by fingerprint.
7. **C7 — the receipt reproduces** byte for byte.

## What would make this experiment worthless

- Reporting `B ≥ A` as a finding. It is arithmetic, stated above as decided.
- Changing `RUNNABLE` in the engine to get Arm B, which would rewrite the past.
- Claiming Book I permits or forbids anything here. §3.5 already says what an
  unresolved reference is; what this measures is what *this substrate* threw away
  by reading it as death.

## Provenance

Preregistration and harness by the same model in the same session. Thresholds are
numeric in this document per D46, the power condition is in it per D45, and the
absence of a chance model is argued rather than assumed per D50.
