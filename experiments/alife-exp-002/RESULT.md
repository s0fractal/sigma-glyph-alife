# ALIFE-EXP-002 — result

Judged against [`ALIFE-EXP-002-does-sharing-pay-preregistration.md`](../ALIFE-EXP-002-does-sharing-pay-preregistration.md),
committed before this harness existed. The corpus is EXP-001's, unchanged, pinned
by fingerprint `53cc6da80f66d220`.

**Provenance, at its real strength.** As with EXP-001: corpus, preregistration
and harness were authored in one session by one agent, so the ordering is commit
order, not an independent registry. Three parameters of the generational frame
were changed *after* the first runs, and both changes are named in
[Corrections](#corrections) rather than absorbed.

| | |
| --- | --- |
| substrate | `impl/sigma_alife.py` 0.1.0 on Σ-GLYPH Book I, oracle `413d1f98…` |
| arms | memo off / one memo per agent / one memo for the population |
| Part B | carrying capacity 32, 12 generations, 3 seeds, both arms per seed |
| controls | seven, all passing, including one that must fail and one on power |
| receipt | `results.json`, reproduced byte for byte on a second run |

## Scorecard, preregistered criteria, no adjustment

| | preregistered claim | verdict |
|---|---|---|
| **H1** | memoization turns sharing into ATP | **FAILS** — 6 ATP of 2776 (0.22%), one hit |
| **H2** | the proved ceiling gets tighter | **NOT ADJUDICATED** — nothing fired to compare |
| **H3** | when sharing pays, selection preserves it | **FAILS as stated** — 2 of 3 seeds, criterion was all three |

And the pricing law, filed in advance as already decided and reproduced here as
control C3, not as a finding: at a flat price of 1, **50 of 64** corpus terms
violate `size ≤ spent + 1`. At `size(nf)`, none do.

## What actually happened, which is more interesting than the scorecard

### Sharing structure is not enough. Sharing has to be *demanded*.

Part A gave one memo hit across 64 agents holding a great deal of structure in
common (sharing factor 2.593 settled, 3.989 unreduced). The reason is not that
memoization is weak; it is that **a memo is keyed by what an agent asks for, not
by what it contains.** Sixty-four agents can share three quarters of their nodes
and never once utter each other's addresses: each reduces its own tree top-down,
demanding its own subterm hashes, which no other agent's normal form is filed
under.

Two post-hoc arms supply the missing demand path and change nothing else:

| population | ATP off | ATP shared memo | saving | hits |
|---|---|---|---|---|
| the preregistered corpus | 2776 | 2770 | 0.2% | 1 |
| **+ composites** (`corpus_i · corpus_j`, so agents force each other's roots) | 9009 | 8273 | **8.2%** | 41 |
| **Part B**, where children inherit their parents' root hashes | 1163 | 964 | **17.1%** | 26 |

> Anastomosis in a content-addressed population is not a property of what agents
> have in common. It is a property of who **asks** whom. Structure shared without
> a demand path is metabolically invisible — which is the same negative
> ALIFE-EXP-001 found, one level deeper: EXP-001 showed sharing is an endowment
> that reduction spends; EXP-002 shows that even the sharing that survives buys
> nothing until something demands it by address.

Lineage is the demand path that exists for free: a child grafted with its
parent's **root** inherits an unevaluated hash whose normal form the colony
already knows. That is the mechanism, and it is why Part B is where the memo
fires at all.

### H3 is directionally supported and not established

| seed | no-memo Δ sharing | memo Δ sharing | arms differ by |
|---|---|---|---|
| 20260825 | +3.065 | +4.032 | **+0.967** |
| 20260826 | +2.626 | +4.493 | **+1.867** |
| 20260827 | +2.922 | +2.846 | −0.076 |

Two seeds in the predicted direction with a large margin, one an effective tie
against it. The preregistered criterion was all three seeds, so **H3 fails as
written**, and three seeds could not have established it in any case. What can be
said: sharing rises steeply in *both* arms — the preregistered warning that ATP
selection may simply favour small terms is visible in the data (mean term size
falls to 2.8–3.4 nodes in every arm), and the arms' survivor sets overlap by only
23%, so the two populations really are different populations, not the same one
measured twice.

The next version of this experiment needs more seeds and a mechanism that
separates "shares because small" from "shares because inherited". Not more
adjectives.

## Corrections

Four, three of them changes to what had already been committed.

1. **The committed drought killed everything.** Tax 400 against a founder holding
   ~257 of a 300 endowment is not a drought, it is extinction in generation 0,
   with no selection in it. Every seed produced one generation and an unchanged
   population, which is exactly what a null looks like from the outside.
2. **The first repair had no power.** Tax 200 / endowment 300 runs for all twelve
   generations and lets the memo save ~170 ATP against a flow of ~115,000 — 0.15%,
   and both arms end with the *identical* surviving population. A null from a
   design that could not have shown an effect is not a null; it is a measurement
   of the design. The frame was re-chosen looking **only** at turnover, saving
   fraction and how much the arms' survivor sets differ — never at the sharing
   comparison H3 is about. This is now enforced: **control C7** refuses to
   adjudicate H3 on any run where the arms end with identical survivors.
3. **Reproduction span forever on settled leaves.** A settled SKI agent is very
   often a single leaf, which `crossover` cannot graft into, so the loop retried
   the same impossible birth until the process was killed. A leaf now reproduces
   by application — the child is the parent applied to the mate's genome — and
   the attempt count is bounded.
4. **The composite arm is post hoc**, written after Part A measured nothing, and
   labelled as such in the table, in the receipt and in `measure.py`.

One design choice the preregistration did not fix and which decides whether Part B
can show anything at all: **which of a parent's hashes a child inherits.** A child
grafted with the parent's current *term* inherits a phenotype no memo has an entry
for; grafted with the parent's *root* it inherits an unevaluated genome, which is
the only graft a memo can reach. Part B uses the root **in both arms**, so it
biases neither — but it is the difference between an experiment and a formality,
and it was chosen by the author, after the fact.

## What this says to Book I

Nothing, normatively — and one thing, as a question. A memoizing evaluator returns
a different `atp_spent` for the same `(hash, budget)` than the reference oracle,
so it fails Book I's pinned conformance vectors. Book I never discusses
memoization; it forbids it by side effect of pinning spend exactly. Whether that
is intended, and if not what a memo action should cost, is filed as a case-derived
need in [`needs/`](../../needs/) — with the price already derived from Book I's own
§3.4 premise, and a reproducer that breaks the bound at anything cheaper.

## Limitations

1. Three seeds. No aggregate is offered and none should be inferred.
2. One corpus, one generator, one economy, one reproduction operator. The
   generational frame was chosen for power, and a frame chosen for power is a
   frame chosen.
3. The memo learns **whole-agent normal forms only**. Sub-term memoization — the
   version where anastomosis would not need lineage — is not implemented, because
   the machine never announces that a subterm has reached a normal form; learning
   one requires either speculative evaluation nobody has priced or reimplementing
   the evaluator. That is the road not taken, and it is where a successor should
   start.
4. Culling is ON in Part B and OFF in Part A, for the reason EXP-001 gives.
   Part B's two arms cull identically, which is what makes its comparison
   legitimate and would not have made Part A's.
