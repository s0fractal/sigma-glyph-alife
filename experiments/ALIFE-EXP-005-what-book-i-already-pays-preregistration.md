# ALIFE-EXP-005 — what does Book I already pay for address-sharing?

**Preregistration. No measurement has been taken.** Non-normative.

**Written to be implemented by somebody who has not seen a harness for it**, and
by an author who will not write that harness. See *Provenance* at the end: this
document is the whole specification, and if it is not enough, that is a defect in
it rather than a question for its author.

## Why this experiment exists

This repository published, in ALIFE-EXP-002 and in `ALIFE-ADR-002`, that **"in
Book I, sharing buys nothing"**. An external review (Claude Fable 5, 2026-08-25)
showed the claim is too broad, and the counterexample is in Book I's own pricing:

`R-S` (`S x y z → x z (y z)`) costs `1 + size(z)`, where `size` is the **hash-leaf
size of the current materialization** — an unforced thunk counts 1, whatever tree
stands behind that hash. Measured: duplicating a 13-node argument that is still a
thunk costs **2 ATP**, not 14.

So Book I already discounts duplication, by exactly the amount that laziness plus
content addressing lets it avoid writing out. That discount has never been
measured. The corrected claim — *reusing another agent's completed work* buys
nothing — stands; what this experiment asks is what the sharing that **does** pay
is worth.

## The counterfactual

Define **copy pricing**: `R-S` costs `1 + deep_size(z)`, where `deep_size` is the
number of nodes in the fully expanded tree behind `z` — thunks resolved through
the store, **each occurrence counted separately**, because a machine that copies
rather than references pays for every copy it writes. Genesis atoms resolve
without a store, as Book I says. An unresolvable hash counts 1, as it does today.

`deep_size` is exponential in depth over a DAG and must be capped
(`corpus.py: DEEP_SIZE_CAP`); saturation is reported, never silently clamped into
an average. It is linear to compute if memoized by hash — `deep(h) = 1 + deep(l) +
deep(r)` — and the harness should do that or it will not finish.

Everything else about the machine is unchanged: same corpus, same budgets, same
schedule, same driver.

## What is already decided, and will not be claimed as a finding

- **That the discount exists.** `2` against `14` on one term is measured above.
  The size of it, its distribution and its consequences are what is open.
- **That copy pricing is worse.** Of course a machine that pays for copies pays
  more. "Book I is cheaper than a strawman" is not a finding; the number, its
  shape, and whether it changes *outcomes* are.

## Hypotheses

**H1 — the discount is large, and it is concentrated.** Total ATP under copy
pricing exceeds Book I's by a wide margin on the same trajectories, and the excess
is **fat-tailed**: fewer than 10% of `R-S` firings account for more than half of
it. *Falsifier:* the excess is spread evenly across firings, which would make the
discount a constant factor rather than a property of a few large duplications.

**H2 — the discount decides outcomes, not just totals.** Under *enforced* copy
pricing — where the higher price is actually charged and agents therefore run out
of budget earlier — materially fewer agents reach a normal form at the same
budget. *Falsifier:* the same agents settle either way, which would mean the
discount is real but never binding at these budgets, and Book I's laziness is an
accounting convenience rather than a capability.

**H3 — the discount is a family property.** The `dup` family (S over a shared
argument) shows the largest discount and `drop` the smallest, with a gap of at
least 2× between them. *Falsifier:* the families do not separate, which would mean
the discount is about term size rather than about duplication.

## Design — two arms, and they are not the same measurement

- **Arm A, shadow.** Run exactly as Book I runs. Alongside, accumulate what each
  `R-S` firing *would* have cost under copy pricing. This prices **one
  trajectory** two ways. It cannot say what a copy-priced machine would do,
  because that machine would exhaust budgets at different points and take
  different paths — and saying otherwise is the mistake this arm exists to avoid.
- **Arm B, enforced.** Charge the copy price for real: the agent pays
  `1 + deep_size(z)` for an `R-S`, runs out earlier, and settles or does not.
  This answers H2 and produces a genuinely different trajectory.

Report per family and for the population: total ATP under each pricing, the ratio,
the number of `R-S` firings, the distribution of per-firing excess (at minimum:
max, median, and the share of total excess contributed by the top decile), the
settled count in each arm, and how often the cap was reached.

## Controls, each of which must pass before a number is recorded

1. **C1 — the shadow never undercharges.** For every firing, copy price ≥ Book I
   price. A single violation means `deep_size` is wrong.
2. **C2 — no R-S, no difference.** On terms whose evaluation fires no `R-S`, the
   two prices are *equal*, exactly. If they differ, something other than
   duplication is being charged.
3. **C3 — Arm A does not perturb the run.** With the shadow counter switched off
   and on, the run's result hashes and Book I ATP are identical, term for term.
   A measurement that changes what it measures is not one.
4. **C4 — Arm B is still Book I everywhere else.** Every agent that settles in
   Arm B reaches the hash `sigma_glyph.eval_hash` reaches. Prices changed; answers
   did not.
5. **C5 — conservation and the memory bound** hold in both arms. Note that Arm B
   *overcharges* relative to Book I, so the bound is preserved a fortiori; a
   violation there would indicate a bookkeeping error, not a discovery.
6. **C6 — the corpus is EXP-001's**, by fingerprint `53cc6da80f66d220`.
7. **C7 — saturation is reported.** If any `deep_size` hits the cap, the count
   appears in the receipt and in the summary. A capped value must never enter a
   mean without its count beside it.

## What would make this experiment worthless

- Reporting Arm A's ratio as "what copy pricing would cost". It is what *this*
  trajectory would have cost.
- Averaging over capped values without saying how many were capped.
- Concluding anything about `warrant`, receipts or conformance. This measures a
  discount inside one machine; it says nothing about what any other implementation
  owes.
- Re-deriving that "Book I never reuses another agent's work". That is
  ALIFE-EXP-002 and is not in question here.

## Provenance — the point of this document's format

Every preregistration in this repository so far was written by the same agent who
then wrote its harness, in the same session. That is the weakest claim in every
`RESULT.md` here, and it is stated in each of them.

This one is an attempt to fix it: the preregistration is written by one model, and
the harness is to be written by a **different** one, working from this document
and the repository's engine API, without access to its author. The separation is
not an independent registry and does not pretend to be. It buys exactly one thing
— the harness author can find this document underspecified, and that finding is
worth having *before* the numbers exist rather than after.

If the harness author needs a decision this document does not make, the right move
is to make it, record it in `DECISIONS.md`, and say so in the result. The wrong
move is to ask the author of this file.
