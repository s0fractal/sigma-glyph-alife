# ALIFE-EXP-002 — does sharing pay, and does paying select for it?

**Preregistration. No measurement has been taken** beyond the probe reported in
§"already decided" below, which is stated there precisely so it cannot be
re-sold as a finding. Non-normative: nothing here changes Book I, Book II,
Book III or any released Σ-GLYPH contract.

## Why this experiment and not the one that was announced

`README.md` and ALIFE-ADR-001 both pointed at a rebate economy as the next step:
if reduction spends sharing down (ALIFE-EXP-001), pay agents for sharing and see
whether they keep it. That experiment was dropped, and the reason is recorded in
`DECISIONS.md` and ALIFE-ADR-002 rather than left as a change of subject.

The short form: a rebate is a pressure hand-designed to reward the quantity being
measured, so its result is knowable in advance — selection selects for what the
designer paid for. Underneath it sits a substrate fact that EXP-001 could not
see and that makes the rebate look like what it is:

> **In Book I, sharing buys nothing.** Two agents holding the same subterm each
> pay to materialize it. Measured: the same hash, evaluated twice, costs
> `10/10`, `106/106`, `3981/3981` ATP. Sharing is a *memory* phenomenon in this
> machine and never an *energy* one, so no population living on it can have a
> gradient toward sharing to begin with. The rebate was an attempt to paint one on.

The question worth asking is therefore not "what pressure can we invent" but
"can the substrate make sharing pay on its own terms" — and content addressing
already says how: one hash has exactly one normal form, so a normal form written
back into the store is a **function**, not a cache heuristic.

> **Correction, 2026-08-25.** The paragraph below states that any price under
> `size(nf)` breaks the memory bound. That is off by one and was measured rather
> than derived. The bound needs only `Δsize ≤ Δcost`, so the true floor is
> `size(nf) − 1`; `size(nf)` is what preserves the stronger per-row discipline
> every Book I action satisfies (`Δsize ≤ cost − 1`), tightly. Both are now
> machine-checked — `memo_discipline` and `memo_below_floor_breaks` in
> `proofs/Population.lean` — and the correction is recorded in `DECISIONS.md` D33
> and in the amendment to `ALIFE-ADR-002`. This preregistration is left as it was
> filed; a preregistration that gets edited is not one.

## What is already decided, and will not be claimed as a finding

**The price of a memo hit is forced, not chosen.** Book I §3.4 rests on one
per-action premise: an action grows the term by at most `cost − 1`. Installing a
normal form of size `k` where a thunk of size 1 stood grows the term by `k − 1`,
so any price below `k` breaks the premise and with it `size ≤ spent + 1`. A price
of exactly `k` makes the inequality **tight**, which no other action of the
machine does.

That is arithmetic, and a probe has already watched it happen (26/60 corpus terms
violate the bound at a flat price of 1, worst excess +27; zero violations at
`size(nf)`). It is reproduced here as **control C3**, not reported as a result.
The one-line consequence, which the result may quote and the experiment does not
have to prove:

> In a size-priced machine, memoization can refund time and never space.

## What is genuinely open

### Part A — energy

**H1 — memoization turns sharing into ATP.** Over the EXP-001 corpus, total
population ATP with the memo on is materially below the memo-off run, and the
saving is a function of how much structure the population had in common. The
falsifier is a saving that does not track sharing: if the memo arm saves the same
fraction on a population that shares nothing as on one that shares heavily, the
saving is about repetition inside single agents and this experiment has found
nothing about anastomosis.

**H2 — the bound gets no looser and the ceiling gets closer.** EXP-001 measured
the population occupying 6.41% of the proved ceiling `N + budget`. A memoized run
buys the same structure for less ATP, so the ceiling — which is `N + spent` —
drops. Predicted: the *ratio* of materialized nodes to ceiling RISES, i.e. the
theorem becomes a tighter description of a memoizing machine than of Book I's.
The falsifier is the ratio falling or not moving.

### Part B — selection

**H3 — when sharing pays, selection preserves it.** With a fixed carrying
capacity, a drought tax and reproduction paid for out of what an agent has left,
the memo arm's surviving population has a **higher sharing factor** than the
no-memo arm's, at the same generation, from the same seed and the same founders.

This is the hypothesis the experiment exists for, and the two arms differ in
**exactly one bit** — the price of a demanded hash whose normal form is known.
Everything else, including the RNG stream, is identical.

**Stated in advance, because it is the likeliest way to be fooled:** ATP
selection may simply favour SMALL terms, and small SKI terms are built from the
three genesis atoms, which share trivially. Both arms would then rise and the
rise would be about size, not sharing. That is why the discriminator is
memo-arm-against-no-memo-arm at equal carrying capacity, and never the rise
itself. If both arms rise together, H3 is refuted and the honest report is that
metabolic sharing is not what the selection is seeing.

## Design

- **Corpus:** the ALIFE-EXP-001 corpus, unchanged, pinned by its fingerprint
  `53cc6da80f66d220`. A different corpus would answer two questions at once with
  no way to tell which half of a difference came from the price.
- **Part A:** one population per family plus one mixed, each run twice — memo
  off, memo on at the derived price — with everything else identical.
- **Part B:** carrying capacity 32, 12 generations, three seeds, both arms per
  seed. Each generation: run to settling or starvation; the commons releases
  `GENERATION_ENDOWMENT` per agent; a `DROUGHT_TAX` is collected from everyone;
  the richest survivors pay `BIRTH_COST` to spawn children by crossover at a
  shared CAS node; the population is culled back to capacity, poorest first.
- **Every seed reported individually.** Three seeds cannot support an aggregate
  and will not be given one.
- **Culling is ON in Part B and OFF in Part A**, for the reason EXP-001 gives:
  an archived agent leaves the census, so culling moves the sharing factor by
  itself. Part B compares two arms that cull identically, which is what makes the
  comparison legitimate there and would not make it legitimate in Part A.

## Controls, each of which must pass before a number is recorded

1. **C1 — the memo never moves an answer.** Every corpus term, memo on, must
   reach the hash `sigma_glyph.eval_hash` reaches, and spend no more than it.
2. **C2 — the mirror is a mirror.** Every force `_next_action` predicts is a real
   force at the predicted position and price (`tests/alife_memo.py` M1). A memo
   that fires where the machine did not demand a hash would buy structure the run
   never asked for, and the ATP figures would stop meaning what they say.
3. **C3 — the derived price is load-bearing.** At a flat price of 1 the bound
   must BREAK on this corpus. A control that must fail, or the pricing law has no
   teeth.
4. **C4 — conservation and the bound**, at every tick of every arm, including
   the generational loop where ATP moves between commons, agents and children.
5. **C5 — the arms differ in one bit.** With the memo emptied, the memo-on arm
   must reproduce the memo-off arm exactly: same statuses, same ATP, same terms.
6. **C6 — the receipt is reproducible** and the inherited corpus fingerprint is
   the one EXP-001 recorded.

## What would make this experiment worthless

- Reporting Part A's saving without showing it tracks sharing (H1's falsifier).
- Reporting a rise in Part B without the no-memo arm beside it.
- Any claim that memoization is permitted, intended or forbidden by Book I. It is
  none of those things here: it is a *conformance collision* (a memoizing
  implementation returns a different `atp_spent` for the same term and fails
  Book I's pinned vectors), and it is filed as a case-derived need under
  `needs/`, not decided in an experiment.
