# ALIFE-EXP-007 — do organizations form under address-level interaction, and does price choose them?

**Preregistration. No measurement has been taken** except the blind power probe
recorded in `alife-exp-007/corpus.py`, which reports reaction success and
diversity and nothing else. Non-normative.

## Why this experiment exists

Everything measured here so far has been about resources: what sharing costs
(EXP-001, -004, -005), what a memo or a library is worth (EXP-002, -003), what
resumption buys (EXP-006). Agents have interacted only through ATP.

But this substrate has an interaction that is native to it and has never been
used: **one agent applied to another by root hash**, `app(A_root, B_root)`. That
is exactly the demand path EXP-002 discovered and EXP-003 had to pay a librarian
to supply — and it is what Fontana & Buss's AlChemy does with λ-expressions:
sample two, apply, evaluate, add the result back, keep the population bounded by
discarding at random. From that they get **L0** organizations (expressions that
compute themselves) and **L1** organizations (sets in which every member is
produced by members of the same set — an autocatalytic set).

The difference here, and the only reason to run it again: **every reaction has a
price fixed by a specification, and can fail.** AlChemy's evaluation is unbounded.
Ours costs ATP, is bounded by a proved memory law, and a reaction whose budget
runs out produces nothing. So a third question exists that AlChemy cannot ask:
does the *price* decide which organization forms?

## What is already decided, and will not be claimed as a finding

- **That organizations of some kind appear in an applicative chemistry.** Fontana
  & Buss showed it in 1994 and Kruszewski & Mikolov showed it for combinators in
  2020. Reproducing it here is a precondition, not a result.
- **That closure rises as diversity collapses.** A soup holding three distinct
  terms has near-perfect closure and no organization. Every closure figure below
  is reported with the diversity it was measured at, and H1 is conditioned on it.

## Definitions, fixed here

- **Reaction:** pick `A`, `B` uniformly at random from the soup (with
  replacement), evaluate `app(thunk(A), thunk(B))` with `ATP_PER_REACTION`. On a
  normal form, its hash is the **product** and enters the soup; if the budget runs
  out, the reaction **fails, costs its ATP, and adds nothing** — a
  `DISSONANCE(ATP Exhausted)` is not a molecule.
- **Capacity:** after a product enters, a uniformly random member is discarded if
  the soup exceeds `CAPACITY`. AlChemy's rule, copied rather than invented.
- **Closure:** the fraction of successful reactions whose product was already
  present in the soup at the moment it was produced.
- **L0:** a hash `T` with an observed reaction `(T, T) → T`.
- **L1-core:** the largest set `S` of hashes such that every member of `S` is the
  product of some observed reaction whose two reactants are both in `S`. Computed
  by peeling: repeatedly drop any member with no such producing pair, until
  nothing drops.

## Hypotheses, each with its number

**H1 — closure rises without diversity collapsing.** Final closure ≥ **0.30**
while the soup still holds ≥ **8** distinct hashes, in a majority of the three
seeds.
*Falsifier:* closure only clears 0.30 in runs whose diversity has fallen below 8.
Then this is convergence, not organization, and it is the same degenerate
attractor ALIFE-EXP-002 Part B fell into.

**H2 — a real organization forms, not just self-replicators.** An L1-core of size
≥ **3** appears in a majority of seeds.
*Falsifier:* every core is a singleton or empty. L0 alone is a self-copying term,
which is interesting and is not an autocatalytic set.

**H3 — price chooses the organization.** The L1-cores found at the cheapest and
dearest budgets in the sweep (50 and 3000 ATP per reaction) overlap by a Jaccard
index below **0.5**, at the same seed.
*Falsifier:* the cores are substantially the same set. Then price bounds *how
much* chemistry happens and not *which* chemistry, and the substrate's one claim
over an unpriced artificial chemistry is empty here.

H3 is the one that is ours. H1 and H2 exist to establish that there is anything
for a price to choose between.

## Design

- Founders: EXP-001's 64 terms, pinned at `53cc6da80f66d220`.
- 1000 reactions, capacity 64, three seeds, four budgets `50, 200, 800, 3000`.
  The primary budget is 200; the sweep exists for H3.
- ATP comes from a commons pool, one reaction at a time; the pool is sized so that
  1000 reactions at the sweep's dearest budget are affordable, and the ledger is
  asserted throughout.
- Recorded: closure over time, distinct hashes over time, successful and failed
  reaction counts, mean and median successful reaction cost, the L0 set, the
  L1-core and its size, and the reaction graph digest.

## Controls

1. **C1 — every product is the oracle's answer.** For a sample of successful
   reactions, the recorded product equals `sigma_glyph.eval_hash`'s.
2. **C2 — conservation.** The commons plus every reaction's spend equals the
   endowment, at every step.
3. **C3 — the memory bound** holds at every action of every reaction.
4. **C4 — no DISSONANCE is a molecule.** No soup member is the hash of a
   `DISSONANCE`, at any point.
5. **C5 — the core algorithm is correct**, on two hand-built cases: a closed pair
   (`(a,b)→a`, `(b,a)→b`) must yield the core `{a, b}`, and an open chain
   (`(a,b)→c` alone) must yield the empty core. A peeling that returns a core on
   the open case is not computing closure.
6. **C6 — founders** are EXP-001's, by fingerprint.
7. **C7 — power, from this document.** At the primary budget, at least **20%** of
   reactions must succeed and the soup must end with at least **8** distinct
   hashes. Otherwise the run is **UNADJUDICATED** and no hypothesis is scored.
8. **C8 — the receipt reproduces** byte for byte.

## What would make this experiment worthless

- Reporting a closure figure without the diversity beside it.
- Reporting an L1-core without C5, since a peeling bug produces cores from
  anything.
- Claiming emergence. Founders here are a hand-built corpus, not a tabula rasa;
  AlChemy and Combinatory Chemistry start from far less and that difference is
  theirs, not ours. `RELATED.md`.
- Any claim about Book I. Reactions here are ordinary applications priced exactly
  as the specification prices them.

## Provenance

Preregistration and harness by the same model in the same session, as in every
experiment here except ALIFE-EXP-005. Thresholds are numeric in this document for
the reason D46 records: with no second author to be blocked by vagueness, the
document has to block the author instead.
