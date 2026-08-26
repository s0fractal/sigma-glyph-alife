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

That sentence was then attacked on purpose. Its metric counts the genesis atoms
`I`, `K`, `S` like any other address, so three agents that all reduced to the
single leaf `I` score a *perfect* 3.0 — and "reduction consumes structure" could
not be told apart from "reduction consumes the alphabet".
[ALIFE-EXP-004](experiments/alife-exp-004/RESULT.md) measured both, over ten
seeds and four alphabet fractions, with the hypothesis written so the repository
would lose. **It survived:** counting only `APPLY` nodes and excluding genesis
entirely, structural sharing still falls in 10 of 10 seeds at every alphabet
fraction, and pairwise structural overlap falls with it.

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

[ALIFE-EXP-003](experiments/alife-exp-003/RESULT.md) asked the economic question
underneath that — *given a fixed amount of ATP, is a colony better off funding a
shared library than its own agents?* — and got the repository's first positive
result:

> A library of normal forms, filled **on demand** out of a reservoir the agents
> did not get, settles **37 of 64 agents against 33** at the same total ATP. It
> can also be overfunded: at half the colony's ATP it settles 28, *worse than not
> having one*. And it pays only in a band — at the poorest level tested, no share
> beats no library at all. Every agent that settled under a library and not
> without one had bought at least one entry: 4 of 4, 10 of 10, 14 of 14, 13 of 13.
> Meanwhile the entries agents donate for free — EXP-002's mechanism — produced
> 30 entries and **zero** hits. Everything the library is worth comes from what
> somebody paid to derive on demand.

[ALIFE-EXP-006](experiments/alife-exp-006/RESULT.md) finally spent the theorem.
Deliver a colony's ATP in pulses instead of one endowment, and an agent stopped
mid-reduction is holding capital — work already paid for, which persists only
because the substrate can resume:

> **Resumption is worth about half the population.** On the same 2000 ATP and the
> same schedule, a resuming colony settles 47 of 64 agents where a restarting one
> settles 16. But nothing the colony can *see* spends that capital better than an
> even split: concentration recovers 96% of the stranded ATP — 1003 down to 44 —
> and converts it into **two** more settled agents. Stranded capital is not
> recoverable capital; the binding constraint is the distribution of remaining
> costs, and an agent's spend so far tells you almost nothing about what it still
> owes.

[ALIFE-EXP-007](experiments/alife-exp-007/RESULT.md) let agents interact the only
way this substrate natively can — one applied to another **by root hash**, which
is AlChemy's move with a price attached. All three preregistered criteria came
back green. Then the nulls ran:

> **Every criterion was met and none survived.** A shuffled reaction graph of the
> same density yields a larger autocatalytic core than the real one. Cores at
> different budgets barely overlap — and so do the *molecules*, even less. And 85
> to 97% of the closure is reproduced by replaying the same products in a random
> order. What is left is worth more than what was lost: **a closure statistic and
> an L1-core over a bounded, high-turnover soup are met by chance**, and anyone
> measuring organization that way needs a shuffled-graph null beside the number.

[ALIFE-EXP-008](experiments/alife-exp-008/RESULT.md) took EXP-007's own stated
limitation — organizations counted from the dead — and demanded sets that are
**alive and being re-made out of themselves**. They beat a complete shuffle by a
wide margin. Then a stronger null:

> Permute products only *within* the window, so the recent molecules stay recent
> and only *who made what* is destroyed, and the null **matches or beats** the
> observed set at 6 of 7 windows. Most of what looked like a self-maintaining
> organization is **temporal locality**. And the reason the first version of this
> experiment reported the opposite is that it drew **one** permutation: twenty
> draws and a worst-case statistic reversed the result.

[ALIFE-EXP-009](experiments/alife-exp-009/RESULT.md) turned out to be half
research and half a bug with a measurement attached. Book I §3.5 makes
`DISSONANCE(Unresolved Reference)` an outcome **relative to a store**, and §3.4
says a failed resolve is not charged — so in a population whose store grows, such
an agent is *waiting*. This engine had `RUNNABLE = (LIVE, STARVED)`, and seven
experiments ran on it:

> **Treating an unresolved reference as death discarded 45 of 64 agents.** Letting
> them wait settles the entire population — the same number that settles when
> nothing was withheld at all — for **337 extra ATP**, about seven and a half per
> recovered agent, because each had already done its work and sat one force from
> finishing. Zero ATP is spent while waiting, and every recovered agent reaches the
> answer it reaches when the term was never withheld.

That is what the separate repository is for. `sigma-glyph` is a specification
under threshold-warrant governance; this is a place where a founding hypothesis
can be wrong in public on the first measurement, and its replacement wrong on the
second, before anything is right on the third.

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
  and at which of two prices? Filed as a `decision-archaeology.need@v0` packet
  with a reproducer, not as a proposal. **Filed 2026-08-26** as
  [s0fractal/sigma-glyph#25](https://github.com/s0fractal/sigma-glyph/pull/25) —
  open, unmerged, awaiting owner-side triage. Its disposition stays `untriaged`
  until they say otherwise.
- `RELATED.md` — the two nearest ancestors (Fontana & Buss's AlChemy; Kruszewski
  & Mikolov's Combinatory Chemistry) and what is actually new here, which is the
  machine and not the metaphor.

## Open questions, in the order they became interesting

No schedule and no venue — `ALIFE-ADR-001 §9`, and standing direction since
2026-08-25. These are questions, not promises.

- ~~What does Book I already pay for address-sharing?~~ **Answered by
  [ALIFE-EXP-005](experiments/alife-exp-005/RESULT.md): 5.4% on this corpus, and
  it decides outcomes only inside a band.** The first experiment here whose
  preregistration and harness were written by *different models* — the separation
  found seven underdefinitions in the document before any number existed, and the
  document turned out to have preregistered a budget at which its own H2 could not
  be true.
- **Can a library be made to break even?** The bound gives a price *floor*, not a
  price, so a librarian may charge above it. Cost-recovery pricing, fill-on-k-th
  miss, eviction, ranking by expected demand — ALIFE-EXP-003 used the crudest
  policy on every axis and still found a band where it pays.
- **What survives a conservation law instead of a fitness function?** The one
  evolutionary arm here bred for cheapness and got the empty program, which is the
  known failure. Combinatory Chemistry's answer — conserve, and let structure be
  what survives — is the better direction, and this substrate conserves ATP by
  construction.
- **Do organizations form under address-level interaction?** The only interactions
  here are ATP and the memo. Applying one agent to another *by root hash* is the
  substrate's native interaction, and it is exactly the demand path EXP-002 found
  and EXP-003 had to fund. Whether closed sets form under it — AlChemy's L1 — is
  open.
- ~~Does the loose ceiling decompose?~~ **Answered by
  [analysis-001](experiments/analysis-001-where-the-slack-lives/ANALYSIS.md),
  from receipts already on disk.** The two halves behave nothing alike: across an
  alphabet sweep the *morphological* factor travels 30 points and the *metabolic*
  one moves 4, and the ceiling is dominated by the factor the alphabet does not
  control. A run turns ~15% of its proved budget into materialised nodes and
  de-duplicates ~59% of those away — the theorem is loose mostly because reduction
  spends budget on **reductions**, not on structure. Over a run the morphological
  factor freezes after the first tick while the metabolic one decays
  monotonically.
- **Is there a tighter bound for populations with high sharing?** The
  decomposition says where to look; nothing here proves anything about it.

---

MIT. Built on Σ-GLYPH by s0fractal; the research programme in
`proposals/ALIFE-000` was written by Kimi (Moonshot AI).
