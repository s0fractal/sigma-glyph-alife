# Σ-GLYPH ALife

**Digital agents that run out of food without dying, on a machine where the
memory bound is a theorem instead of a timer.**

> That tagline was conditional on a schedule nothing documented until
> [ALIFE-EXP-011](experiments/alife-exp-011/RESULT.md) measured it: under the
> default tick, a starving agent that the colony *fed* was archived in the same
> tick and its food collected back — **0 of 168** fed agents ever ran again. Fixed
> on 2026-08-27, with the measurement of the bug committed first and a regression
> suite that watches the property go red on the old policy.

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
in the exit status. A skipped surface is not a passed one — the bare command
prints `NOT COMPLETE` and exits 2 when it skipped the ten-minute soup replays or
the external need-packet validator. **The canonical command, terminal only when
every claimed experiment has actually replayed, is:**

```sh
RUN_SLOW=1 DECISION_ARCHAEOLOGY=/path/to/decision-archaeology tools/test-all.sh
```

"test-all is green" is a false sentence unless that is what was run, or its two
surfaces ran in their own workflows on the same commit. Every other experiment,
ALIFE-EXP-010 included, replays in both profiles.

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

And the bound got a number — two numbers, since ChatGPT's review of 2026-08-27
pointed out that the first one was a hindsight reading of a preflight theorem
([erratum](experiments/alife-exp-001/RESULT.md#erratum--2026-08-27)).
`Σ size ≤ N + budget` holds for any budget bounding the run's spend. Instantiated
at what the run *turned out* to spend, the ceiling is 2840 nodes and the 182
distinct addresses the population occupies are **6.41%** of it. Instantiated at
what an operator actually has in advance — the 192 000 ATP endowment — it is
**192 064**, and the same 182 addresses are **~0.095%**. So an operator sizing a
machine from the theorem overprovisions by about a **thousandfold**, not the
sixteenfold this page used to claim, and the experiment can say which part of
the retrospective looseness is unspent budget and which is sharing.

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

[ALIFE-EXP-010](experiments/alife-exp-010/RESULT.md) asked the question neither
literature has held everything else fixed for: **does the currency choose the
colony?** Combinatory Chemistry prices duplication in *matter* — a physical copy
must already exist and is consumed — and Book I prices it in *energy*. Same act,
two currencies, one chemistry, three seeds. One of three preregistered
hypotheses held, and the finding is the thing none of them asked:

> **In a lazy machine, a duplication is a duplication of an ADDRESS.** Book I
> fires `R-S` leftmost-outermost, so the duplicated argument is nearly always
> still a thunk of size 1 and the energy price `1 + size(z)` is usually **2**.
> The price intervention — what Book I charges for a duplication minus what the
> floor charges, on a fixed trace — is **0.4% to 1.4%** of what the colony
> spends. The arms do end up sharing not one surviving molecule; but two runs of
> the *same* currency at different seeds share none either, so the hypothesis
> that detected the separation cannot tell it from turnover.

An adversarial review (Codex, `reviews/codex-2026-08-26.md`) then returned
CHANGES REQUESTED on that receipt: the first version of those percentages had
the wrong denominator and named the wrong estimand, "eating a duplicate spends
redundancy" was an explanation with no measurement under it — three consumptions
in four turn out to remove the *last* living copy — and the experiment was
absent from this repository's own test matrix. The verdicts did not move; the
numbers and their names did, in a dated erratum, and EXP-010 now replays in both
profiles of `tools/test-all.sh`.

[ALIFE-EXP-011](experiments/alife-exp-011/RESULT.md) is the tagline audited.
ChatGPT's review read `phase_share` / `phase_cull` and found that
`RUNNABLE = (LIVE, STARVED)` makes a starving agent simultaneously eligible for
food and eligible for burial, in that order, inside one tick. The experiment was
preregistered and run **before** the fix, deliberately — a bug fixed before it is
measured is an anecdote:

> **Under the default schedule, the tagline held only for agents nobody tried to
> feed.** 0 of 168 sufficiently-fed starving agents ever fired another action;
> 1056 of 1056 ATP granted to starving agents was collected by the cull in the
> same tick it was granted, against a hypothesis that called 10% a leak worth
> reporting. Skip the cull for that one tick and the same agents resume at
> **100%**, and **56 of 64** reach a normal form instead of 34. The cost is not
> ATP — 1056 out of 202,048 is nothing — it is agents: 30 of 64, in tick 0,
> every run.

The fix re-tests the condition instead of trusting the status: `STARVED` means
"the next action costs more than the reservoir holds", and two phases of a
commons economy run between the claim and the cull that acts on it. The
before-measurement stays pinned to the old policy in code, so it keeps
reproducing what it measured.

The **currency factorial** took three preregistrations to become answerable, and
the two that failed are kept as [calibration pilots](experiments/alife-exp-012/PILOT-FINDINGS.md)
that score nothing, ever. ALIFE-EXP-012 crossed price (Book I vs the action
floor) with matter (copy free vs an exact-hash body consumed) on decorrelated,
counter-keyed randomness — and ended FAILED-CONTROLS, because its admission rule
demanded 50 consumptions per cell and three cells could not supply them.
ALIFE-EXP-012b tried the obvious remedy, six times the run length, and ended
FAILED-CONTROLS again with the remedy **disproved**:

> Eligible duplications do not accrue with time. On the binding cell the count is
> **45 at 1000, 2000, 4000, 6000 and 12000 reactions** — twelve times the length
> buys zero. Cells are bimodal with no middle: six stop producing before reaction
> 1100 and produce nothing for the rest of the run; four produce to 5000+. A soup
> either finds a cycle that keeps making structure or collapses onto the genesis
> floor, where duplication is free and the matter rule has nothing to bite on.

So collapse was promoted from an admission failure to the primary outcome, and
[ALIFE-EXP-012c](experiments/alife-exp-012c/RESULT.md) asked whether the currency
chooses the *phase*. Fourteen controls pass, including the same supply floor —
scoped now to the cells where it can be met, where it passes 10 of 10:

> **The corpus does not choose the phase alone.** Four of five seeds have arms
> that disagree: hold the seed fixed, change only the duplication rule, and the
> soup's fate changes. And **collapse timing is not currency-independent** — on
> the one seed where all four arms died, they died at reactions 706, 706, 1833
> and 1961, the Book-priced arms nearly three times earlier than the floor-priced
> ones, on identical founders and identical keyed randomness. The conditional
> factorial is `UNADJUDICATED`: no seed is concordantly producing, which is a
> consequence of the first finding rather than a fact about the corpus.

012c's RESULT reported per-arm producing counts (BF 0/5, BM 1/5, FF 3/5, FM 3/5)
and refused to claim them — no gate, no null, five seeds already seen. So
[ALIFE-EXP-012d](experiments/alife-exp-012d/RESULT.md) filed the price axis as a
**forecast**, on twelve seeds nobody had run, with a permutation null attached to
every hypothesis. Its author was already 0 of 3 on 012c. All four forecasts
failed:

> **The price does not choose the phase.** Floor arms produced in 5 of 24 cells,
> Book arms in 6 — the predicted difference of +8 came back as **−1**
> (p = 0.77, 1000 draws). And the observation the whole story rested on
> inverted: **BF produced in 0 of 5 seeds in 012c and 5 of 12 here**, making it
> the *highest* producer rather than the lowest. The death-timing signature came
> back an exact coin flip, 6 of 12, p = 0.49.

Discordance itself replicated — 6 of 12 seeds here, 4 of 5 in 012c — so something
about the arm does reach the phase, and neither axis, scored as preregistered, is
it. This is what refusing to claim a post-hoc pattern is for, and it is a warning
about every other per-arm count in this repository that has not had the same
treatment.

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
