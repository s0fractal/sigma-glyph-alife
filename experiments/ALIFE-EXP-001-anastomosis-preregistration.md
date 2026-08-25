# ALIFE-EXP-001 — does reduction share, or does it just shrink?

**Preregistration. No measurement has been taken.** Non-normative: nothing here
changes Book I, Book II, Book III or any released Σ-GLYPH contract.

## The question, stated so it can fail

A Σ-GLYPH population lives on one content-addressed store. Two agents holding
structurally equal subterms hold **one** address, by construction — there is no
de-duplication pass, because there is nothing to de-duplicate. The proposal this
repository was built from calls the emergent version of that *anastomosis* and
predicts that sharing rises as a population reduces.

The prediction is worth measuring and the obvious way of measuring it is worth
refusing. Here is the trap: SKI reduction **shrinks** terms toward normal forms,
and the normal forms are mostly built from the three genesis atoms. A population
reduced to `I`, `K` and `S` shares almost everything — not because reduction
found structure in common, but because it destroyed everything that differed.
Sharing factor rising is therefore *compatible with reduction being purely
destructive*, and a paper that reports the rise without separating the two would
be reporting attrition and calling it symbiosis.

So the measurement is defined against a null from the start.

## What is already decided on paper, and will not be claimed as a finding

- **Unique addresses grow sublinearly in population size** for any fixed
  generator over a finite alphabet. That is Heaps' law with a hash for an index,
  not a property of Σ-GLYPH.
- **R-S duplicates by address.** `S x y z → x z (y z)` copies `z` and charges
  `1 + size(z)`; both copies are the same NodeHash. That the copy costs no new
  address is arithmetic in the size model, decided in ADR-001×003.
- **The population memory bound holds.** `Σ size ≤ Σ birth + Σ spent` is proved
  in `proofs/Population.lean`. Measuring it is a control, not a result.

## What is genuinely open, and is what gets measured

**H1 — reduction is net anastomotic.** Sharing factor at settling exceeds
sharing factor at birth, *for the population as a whole*.

**H2 — and not merely by attrition.** The rise survives the size-matched null:
a fresh population drawn from the same generator and truncated to the settled
population's total node count has a **lower** sharing factor than the settled
population does. If the null matches or beats the settled population, H1 is
confirmed as an artifact of shrinkage and the honest report is that reduction
shares nothing the generator did not already share.

**H3 — the theorem is loose by exactly the sharing.** `Σ size ≤ N + budget` is
what is proved; `unique addresses` is what a machine actually stores. The gap
between them is predicted to widen monotonically with the sharing factor over a
run, which would make the bound a *worst-case* statement about a quantity no
implementation pays.

If H1 is false, the honest statement is that a content-addressed substrate gives
sharing for free at birth and reduction does not add to it — which is still a
result about where the sharing comes from, and a less interesting substrate.

## Families, and what each is a control on

| family | shape | what it is for |
|---|---|---|
| `dup` | `S x y z`, one shared `z` | sharing can only rise. **Control on H1**: if `dup` does not rise, the harness is wrong |
| `drop` | `K x y` | structure LEAVES the population. Expected to fall, or the metric is measuring shrinkage |
| `church` | `(λf.λx.fⁿx) g h` via the C1 compiler | λ-terms as they would actually be submitted |
| `random` | random trees, fixed seeds | the question with no construction behind it; includes terms that never settle inside the budget |

## Protocol

- corpus: `corpus.py`, 16 terms per family, pinned by `fingerprint()`. Committed
  before `measure.py` was written;
- each term becomes one agent with a reservoir of `ATP_PER_AGENT`, endowed out
  of an explicit commons pool — nothing is minted;
- one run per family plus one mixed run over the whole corpus; `TICKS` ticks or
  until nothing is runnable, whichever comes first;
- rebates OFF and transfers OFF in the recorded runs. A rebate is a selection
  pressure, and switching it on while measuring what structure does on its own
  would measure the pressure instead. (The engine implements both; ALIFE-EXP-002
  is where they belong.)
- per tick, record: sharing factor, node occurrences, distinct addresses, ATP
  spent and held, status counts, structural diversity, Σ peak size;
- the size-matched null is drawn from the same generator with a **different**
  seed and truncated to the settled population's node count, so it answers "do
  terms of this size share this much anyway?".

## Controls, each of which must pass before a number is recorded

1. **C1 — identical agents.** N copies of one term have sharing factor exactly N
   at every tick. If this drifts, the census is wrong.
2. **C2 — distinct atoms.** A population of pairwise distinct literals has
   sharing factor exactly 1.0. If this rises, the census is collapsing things
   that are not equal.
3. **C3 — the driver is the oracle.** Every corpus term, run whole at the run's
   budget, agrees with `sigma_glyph.eval_hash` on result hash and ATP spent.
4. **C4 — conservation and the bound.** At every tick: the ledger balances and
   `Σ size ≤ Σ birth + Σ spent`.
5. **C5 — the receipt is reproducible.** The corpus fingerprint recomputed at
   measurement time equals the one committed, and a second run of `measure.py`
   produces a byte-identical `results.json`.

`measure.py` is check-only by default and writes `results.json` only after every
control has passed. A receipt written beside a failure is worse than none, since
it looks exactly like a receipt written beside a success.

## What would make this experiment worthless

- Reporting the population-level rise without the null (H2 is the whole point).
- Reporting `dup` rising as evidence for H1 — it is a control, and a control
  cannot be its own finding.
- Any claim about *evolution*. Nothing here mutates, selects or reproduces.
  ALIFE-EXP-003 is where reproduction belongs, and it is not written yet.

---

Preregistered against `impl/sigma_alife.py` and the corpus pinned at
`fingerprint()`, on the Book I oracle whose SHA-256 the receipt records.
