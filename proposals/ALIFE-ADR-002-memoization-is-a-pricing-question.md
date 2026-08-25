# ALIFE-ADR-002 — memoization is a pricing question, not a policy question

**Status:** accepted for `0.1.0` (DRAFT). Non-normative.
**Context:** [`experiments/alife-exp-001/RESULT.md`](../experiments/alife-exp-001/RESULT.md),
[`ALIFE-ADR-001`](ALIFE-ADR-001-substrate-is-a-consumer.md), and the rebate
economy this repository announced as its next step and did not run.
**Log:** `DECISIONS.md` D16–D22.

## What was announced, and why it was dropped

`README.md` and ALIFE-ADR-001 both pointed at a rebate economy: EXP-001 showed
reduction spends sharing down, so pay agents for sharing and see whether they
keep it. Two reasons not to.

The weaker one: a rebate is a pressure hand-designed to reward the quantity being
measured. Selection selects for what the designer paid for, and the result would
have said more about the design than about the substrate.

The load-bearing one is a measurement. **In Book I, sharing buys nothing.** The
same hash, evaluated twice by two agents, costs the same both times — `10/10`,
`106/106`, `3981/3981` ATP. Book I charges every agent for every materialization,
so two agents holding the same subterm pay for it twice. Sharing there is a
*memory* phenomenon and never an *energy* one.

That reframes EXP-001's negative. A population whose sharing has no metabolic
consequence has no gradient toward sharing to begin with — not because evolution
failed to find one, but because there is none to find. The rebate was a coat of
paint over that fact.

## Decision

Ask instead whether the substrate can make sharing pay **on its own terms**, and
content addressing already says how: one hash has exactly one normal form, so a
normal form written back into the store is a *function*, not a cache heuristic.
Book I's determinism is what makes the memo sound; nothing new has to be assumed.

**The price is derived, not chosen.** Book I §3.4 rests on one per-action premise:
an action grows the term by at most `cost − 1`. Installing a normal form of size
`k` where a thunk of size 1 stood grows the term by `k − 1`, so:

- any price below `k` breaks the premise, and with it `size ≤ spent + 1`
  (measured: 50 of 64 corpus terms violate the bound at a flat price of 1);
- a price of exactly `k` makes the inequality **tight**, which no other action of
  this machine does.

> In a size-priced machine, memoization can refund time and never space.

That sentence is the whole ADR. `Memo.derived_price` is `k`, the cheap price runs
as a control that must fail, and neither is a policy anybody gets to tune.

## Consequences

1. **A conformance collision, filed rather than resolved.** A memoizing evaluator
   returns a different `atp_spent` for the same `(hash, budget)` than the
   reference oracle, so it fails Book I's pinned vectors. Book I never discusses
   memoization — it forbids it as a side effect of pinning spend exactly. Whether
   that is intended is a question for Book I's owners and goes to them as a
   case-derived need under `needs/`, with the price already derived from their own
   premise and a reproducer that breaks the bound at anything cheaper. This
   repository proposes no change to Book I and has no standing to.
2. **Memo is OFF by default**, and every receipt that used one says so. A number
   produced with a memo is not comparable with a Book I number, and the receipt
   must not let anyone believe otherwise.
3. **EXP-002 found the mechanism has a precondition nobody had stated.** A memo is
   keyed by what an agent *asks for*, not by what it contains, so a population of
   distinct roots never triggers it: 1 hit across 64 agents sharing three quarters
   of their nodes. Supply a demand path — composites that force each other's
   roots, or children that inherit their parents' — and the same memo cuts
   population ATP by 8–17%. **Sharing pays only where something demands it by
   address**, and lineage is the demand path that exists for free.
4. **Sub-term memoization is the road not taken.** It is the version in which
   anastomosis would not need lineage, and it is unavailable without either
   speculative evaluation nobody has priced or a reimplementation of the
   evaluator. `DECISIONS.md` D18.

## Alternatives rejected

- **The rebate economy.** Above. It may still be worth running *after* EXP-002, as
  a control: if metabolic sharing already produces the pressure, an invented one
  is redundant, and that is a result about invented incentives.
- **Drought / sporulation (RQ3).** Already proved (`resumption_bound`) and
  differentially checked. Running it would dress a theorem as a result — the
  failure sigma-glyph's own EXP-004 preregistration warns against.
- **Evolutionary pressure on structure (RQ4).** Has no mechanism until sharing
  costs something. It belongs after this decision, not before it.
