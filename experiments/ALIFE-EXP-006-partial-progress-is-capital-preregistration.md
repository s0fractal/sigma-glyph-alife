# ALIFE-EXP-006 — what is resumption worth, and can a colony spend it well?

**Preregistration. No measurement has been taken** except the blind power probe
recorded in `alife-exp-006/corpus.py`, which reports one arm. Non-normative.

## Why this experiment exists

This repository proved that interruption is free — `resumption_bound`: two
consecutive slices obey exactly the inequality one uninterrupted run would have —
built its entire driver around it, and put "sporulation with a receipt" in the
README. **And then never used it.** Five experiments in, `DECISIONS.md` D40
records that no measurement here has exercised the one capability the substrate
proved: ALIFE-EXP-003's reservoirs were smaller than its slice floor, so every
agent got its whole budget in one slice, and nothing else even tried.

A theorem nobody's experiment needs is a theorem about nothing. This experiment
needs it.

## The regime where it matters

Deliver a colony's ATP in **K pulses** instead of one endowment. Now an agent
that stops mid-reduction is holding **capital**: work already paid for, which
persists only because the substrate can resume. Two things follow that could not
be asked on a machine without resumption:

1. **Stranded capital is measurable.** ATP spent by agents that never settle is
   pure loss, and the blind probe says it is about **half the colony's spend** at
   the chosen level. That is what an allocation policy attacks.
2. **The allocation problem exists at all.** Splitting a pulse evenly funds
   everyone a little; concentrating it finishes a few. Without resumption there is
   nothing to concentrate *on*, because there is no partial state to complete.

## What is already decided, and will not be claimed as a finding

- **That resumption preserves the answer and the bound.** Proved
  (`resumption_bound`) and checked (`tests/alife_differential.py` D2/D4). Not
  measured here.
- **That an agent given `B` in one piece and in slices totalling `B` reaches the
  same place.** Same theorem. The experiment is about *who gets how much*, not
  about whether slicing works.
- **That a restarting machine wastes work.** Obviously it does. The number — how
  much, and how it scales with pulse granularity — is not obvious and is H2/H3.

## Hypotheses, each with its number

**H1 — a policy using only observable state beats an even split by ≥ 8 agents.**
At the same total ATP and the same pulse count, the best of `invested` (most-spent
first) and `smallest` (smallest current term first) settles at least **8 more** of
64 agents than `equal`. Eight is 12.5% of the population and roughly twice the
spread the `random` control is expected to produce.
*Falsifier:* no observable-state policy clears +8. The proxies for "how close is
this agent to finishing" are then too weak to spend capital on, and an even split
is as good as anything a colony can see.

**H2 — resumption is worth ≥ 8 agents against the best restarting arm.** At the
same total and pulse count, the best resuming policy settles at least **8 more**
agents than the better of `restart-eager` and `restart-patient`.
*Falsifier:* fewer than 8. Resumption would then be a convenience whose value at
these budgets is smaller than the noise between allocation policies.

**H3 — the premium grows as pulses get finer.** H2's gap is monotone
non-decreasing across pulse counts 2 → 4 → 8 → 16 → 32, and at least **doubles**
between 2 pulses and 32.
*Falsifier:* the gap is flat or non-monotone, which would mean resumption's value
is about total scarcity rather than about the granularity of arrival — a different
and weaker claim than the one the theorem invites.

## Design

- 64 agents, EXP-001's corpus, pinned at `53cc6da80f66d220`.
- **Every arm receives exactly `ATP_TOTAL` (2000), in `K` equal pulses.** An arm
  that receives a different total is not comparable and the harness must refuse
  to score it.
- Resuming policies, each allocating one pulse:
  - `equal` — the pulse divided evenly among unsettled agents.
  - `invested` — the whole pulse to the unsettled agent with the largest `spent`,
    ties by agent id; leftover after it settles passes down the same order.
  - `smallest` — the same, ordered by smallest current term size.
  - `random` — the same, ordered by a seeded shuffle. This is the control that
    says how much of any policy's advantage is just concentration.
- Restarting arms, which model a machine without resumption. An agent accumulates
  its allocation and, when it acts, calls `eval_hash(root, reservoir)`; on
  exhaustion the reservoir is **spent and the agent is back at its root**.
  - `restart-eager` — attempts on every pulse. A strawman, and named as one.
  - `restart-patient` — attempts only when its reservoir is at least twice what it
    held at its last failure. This is the strongest restarting strategy available
    without knowing a term's cost, and H2 is scored against the better of the two.
- Reported per arm: settled agents, ATP spent, **stranded ATP** (spent by agents
  that never settle), settled per 1000 ATP spent, and the settled agent ids.

## Controls

1. **C1 — no answer moves.** Every settled agent, in every arm, reaches the hash
   `sigma_glyph.eval_hash` reaches.
2. **C2 — parity.** Every arm is granted exactly the same total; the ledger
   balances at every pulse.
3. **C3 — the bound** holds at every action of every agent (`probe=True`).
4. **C4 — the restart arms really restart.** After a failed attempt, the agent's
   term is its root thunk again and its reservoir is zero. If a restart arm ever
   carries progress, it is not modelling what it claims.
5. **C5 — resumption is actually exercised.** At least one agent in the resuming
   arms must be resumed after starvation and go on to settle. If none is, this
   experiment did not test the thing it exists to test and must say so.
6. **C6 — the corpus** is EXP-001's, by fingerprint.
7. **C7 — power, stated here rather than left to the harness.** The `equal` arm
   must settle between **25% and 75%** of the population. Outside that band the
   run is reported **UNADJUDICATED** and no hypothesis is scored. This condition
   is in the preregistration because `DECISIONS.md` D42 records the last time it
   was not: ALIFE-EXP-005 preregistered a budget at which its own H2 could not be
   true.
8. **C8 — the receipt reproduces** byte for byte.

## What would make this experiment worthless

- Scoring H1 against `random` instead of `equal`; `random` is the control for
  concentration, not the baseline.
- Reporting the restart arms without naming `restart-eager` as a strawman.
- Any claim that a restarting machine is what Book I is. Book I's `eval_hash` is
  total over canonical outcomes *by design*, for a check engine that must not
  hand back half an answer. The restart arms model the absence of this
  repository's own extension, not a defect in the specification it consumes.

## Provenance

Preregistration and harness by the same model, in the same session — the weaker
arrangement. ALIFE-EXP-005 used two models and found seven underdefinitions in
its document before any number existed; this one has no second author available,
so every threshold above is numeric in the document precisely because nobody else
will be forced to invent them.
