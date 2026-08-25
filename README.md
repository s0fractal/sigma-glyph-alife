# Σ-GLYPH ALife

**Digital agents that run out of food without dying, on a machine where the
memory bound is a theorem instead of a timer.**

An artificial-life substrate built on [Σ-GLYPH](https://github.com/s0fractal/sigma-glyph)
Book I: a content-addressed combinator machine whose evaluation is deterministic,
whose sharing is structural, and whose peak memory is priced by the same integer
that prices its work (`size ≤ spent + 1`, machine-checked). Agents are terms,
food is ATP, and the store they live in is one shared CAS — two agents holding
equal structure hold **one** address, because there is nothing else they could
hold.

    ┌─────────────────────────────────────────────┐
    │  impl/sigma_alife.py                        │
    │  Agent · Population · Economy · metrics      │
    ├─────────────────────────────────────────────┤
    │  sigma-glyph >=0.6.7,<0.7.0   (Book I)      │
    │  content-addressed DAG · priced step · ATP  │
    ├─────────────────────────────────────────────┤
    │  proofs/Population.lean   (Lean 4 core)     │
    │  resumption · population bound · transfers  │
    └─────────────────────────────────────────────┘

**Status: DRAFT / EXPERIMENTAL, `0.1.0`.** Non-normative. Nothing here changes
Book I, Book II, Book III or any released Σ-GLYPH contract.

## Three commands to trust nothing

```sh
export SIGMA_GLYPH=../sigma-glyph/impl        # or pip install "sigma-glyph>=0.6.7,<0.7.0"
python3 impl/sigma_alife.py                   # ALIFE: ALL PASS (29/29)
python3 tests/alife_differential.py           # ALIFE-DIFFERENTIAL: ALL AGREE
tools/test-all.sh                             # everything, and it names its skips
```

`tools/test-all.sh` counts and names every surface it could not check and says so
in the exit status. A skipped surface is not a passed one.

## The one interesting engineering decision

Book I's `eval_hash` is **total over canonical outcomes**: when the budget runs
out it returns `DISSONANCE(ATP Exhausted)` and the partial term is gone. Right
for a check engine — a run either produced an answer or it did not — and fatal
for a population, where *starving* has to leave a body that can be fed later.

So the population loop drives `step5`, Book I's own priced action, in its own
loop, and keeps the term where the budget stopped it. The freedom is exactly one
outcome wide, and two things keep it there:

- **A proof.** `resumption_bound` (Lean, core only, no mathlib): two consecutive
  slices obey exactly the inequality one uninterrupted run would have. A resumed
  agent gets no allowance for having been interrupted and pays no penalty for it.
- **A differential.** `tests/alife_differential.py`: run whole, the driver must
  agree with `eval_hash` on result hash **and** ATP spent, over every generated
  term at every budget, including the budgets either side of the exact spend;
  sliced, it must return the whole run's answer; starved and refed, the
  unstarved answer. It fails closed if no case ever starved.

That is sporulation with a receipt: an agent stops mid-reduction, waits, is fed,
and lands on the answer it would have reached had nothing interrupted it.

## What is proved, what is checked, what is neither

| | |
|---|---|
| **Proved** (Lean 4 core, 11 theorems, no `sorry`, statements pinned) | slicing does not weaken the memory bound; `Σ size ≤ Σ birth + Σ spent` for a whole population; `N + budget` for agents born as root thunks; any ATP redistribution that conserves the total preserves that bound |
| **Checked** (live traces, differentials, negative controls) | the driver *is* the oracle; the bound holds at every action; the ledger balances every tick; every gate puts its verdict in its exit status; every property has a control that makes it go red |
| **Neither** (policy, and labelled as policy in the code) | sharing rebates, the donor reserve, culling, crossover. One defensible choice each. None of them is claimed to have any biological or economic property |

`proofs/premise_guard.py` is the reason the first row means anything: `lean` exits
0 on a file whose proofs are `sorry`ed, and on `theorem t : True := trivial`
forever. It pins every guarded statement, denies the escape hatches, requires
every declared theorem to be on the list — and compares the accounting model
this repository copied from sigma-glyph token by token against the original, so a
change over there cannot leave the theorems here quietly describing a machine
nobody runs.

## The first result contradicts the proposal that started the repository

[ALIFE-EXP-001](experiments/alife-exp-001/RESULT.md) asked whether reduction
increases structural sharing — the "anastomosis" the founding proposal predicted.
Preregistered, with the null model fixed in advance, because sharing rises
trivially when terms shrink toward an alphabet of three genesis atoms.

> Sharing does rise over a run (1.085 → 2.593). It also **fails every null**. The
> same 64 agents, materialized but never run, share 3.989. A settled population
> shares *less* than an unreduced one: reduction consumes shared structure faster
> than it creates it. Content addressing gives a population its sharing at birth;
> evaluation spends it down.

And the bound got a number: the proved ceiling for that run is 2840 nodes, the
population actually materialized 472, occupying **182 distinct addresses — 6.41%
of the ceiling**. The theorem is honest and very loose, and the experiment can
now say which half of the looseness comes from unspent budget and which from
sharing.

[ALIFE-EXP-002](experiments/alife-exp-002/RESULT.md) went one level down and its
preregistered hypotheses failed too. What it found instead:

> **In Book I, sharing buys nothing** — the same hash evaluated twice by two
> agents costs the same both times. And once a memo makes sharing payable, it
> still does nothing for a population of distinct roots: one hit across 64 agents
> holding three quarters of their nodes in common. A memo is keyed by what an
> agent *asks for*, not by what it contains. Supply a demand path — composites
> that force each other's roots, or children that inherit their parents' — and
> the same memo cuts population ATP by 8–17%. **Sharing pays only where something
> demands it by address, and lineage is the demand path that exists for free.**

That is what the separate repository is for. `sigma-glyph` is a specification
under threshold-warrant governance; this is a place where a founding hypothesis
can be wrong in public on the first measurement, and its replacement wrong on the
second.

## Layout

Directory shapes mirror sigma-glyph exactly, so a reader who knows one can find
anything in the other.

| path | what |
|---|---|
| `impl/sigma_alife.py` | the whole substrate: `Agent`, `Population`, `Economy`, the driver, the metrics, and its own self-test |
| `proofs/Population.lean` | 11 theorems, Lean 4 core only |
| `proofs/premise_guard.py` | pins them, and pins the premise copied from sigma-glyph |
| `tests/` | the differential, the property suite with its negative controls, the exit-status guard |
| `experiments/ALIFE-EXP-nnn-*-preregistration.md` | hypotheses, corpus and controls, committed before the harness |
| `experiments/alife-exp-nnn/` | corpus, `measure.py`, `results.json`, `RESULT.md` |
| `proposals/ALIFE-000-substrate-proposal.md` | the founding proposal, filed verbatim, wrong parts included |
| `proposals/ALIFE-ADR-001-*.md` | what was decided differently, and why |
| `needs/` | demand on another repository, as a packet with a reproducer |
| `DECISIONS.md` | the log of every judgment call, corrections included |
| `tools/test-all.sh` | the complete matrix, one command |

Identifiers carry an `ALIFE-` prefix: sigma-glyph has its own `ADR-nnn` and
`EXP-nnn` and a `MAP.md` that resolves a cited identifier to one ref holding one
document. Two repositories minting into one namespace break exactly that.

## Relationship to Σ-GLYPH

A consumer, and only a consumer. It reads `impl/sigma_glyph.py` (the Book I
oracle) and copies one model out of `proofs/SizeBound.lean`. It changes nothing
there, proposes nothing there, and has no standing in its governance.

Every receipt records the **SHA-256 of the oracle file that produced it**.
"sigma-glyph 0.6.7" names a release; the digest names what ran. CI carries one
visible pin of the dependency, and what would justify moving it is written above
the pin.

## Where to look next

- `experiments/ALIFE-EXP-001-anastomosis-preregistration.md` — how an experiment
  here is expected to be set up, including the paragraph on what would make it
  worthless.
- `proposals/ALIFE-ADR-001-substrate-is-a-consumer.md` — the founding proposal's
  API did not exist, its Theorem 1 was missing a hypothesis, and its Theorem 3
  was not the theorem that mattered. All three are recorded rather than quietly
  patched.
- `DECISIONS.md` — every judgment call in this repository, with what was rejected
  and what would overturn it, including the corrections. The rebate economy this
  README used to announce as EXP-002 is in there, with the reason it was dropped.
- `needs/DA-SIGMA-0002-memo-pricing/` — the one question this work sends back to
  Book I: may a conforming implementation reuse a result it has already paid for,
  and at what price? Filed as a `decision-archaeology.need@v0` packet with a
  reproducer, not as a proposal. Prepared, not yet filed upstream.

---

MIT. Built on Σ-GLYPH by s0fractal; the research programme in
`proposals/ALIFE-000` was written by Kimi (Moonshot AI).
