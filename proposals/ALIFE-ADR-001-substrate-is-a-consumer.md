# ALIFE-ADR-001 — the substrate is a consumer, and says so in every file

**Status:** accepted for `0.1.0` (DRAFT). Non-normative.
**Supersedes nothing. Changes nothing in sigma-glyph.**
**Context:** [`ALIFE-000-substrate-proposal.md`](ALIFE-000-substrate-proposal.md)

The proposal asked one decision of its reader — new repository or in-repo
extension — and answered several others in passing that turned out to be wrong
once the code existed. This records both kinds: what was decided, and what the
proposal said that the implementation could not keep.

## 1. New repository (proposal §6, accepted as written)

`sigma-glyph-alife`, depending on `sigma-glyph>=0.6.7,<0.7.0`. The reasons in the
proposal hold: Σ-GLYPH's core is under 2-of-3 threshold-warrant governance and
49 conformance vectors, ALife runs are long and stochastic, and an ALife
researcher should not have to read SKI reduction rules to run a population.

One reason the proposal did not give, and which turned out to matter more than
the others: **this repository is allowed to be wrong in public.** Its first
experiment contradicts its own founding hypothesis. That is a normal week in a
research repository and an incident in a spec repository.

## 2. Identifiers carry an `ALIFE-` prefix (new)

The proposal names its experiments `exp-005`, `exp-006`, `exp-007`, continuing
sigma-glyph's numbering from a different repository. sigma-glyph has `exp-001`
through `exp-004` and will have an `exp-005` of its own; `MAP.md` there exists
precisely so that a cited identifier resolves to one ref holding one document.
Two repositories minting into one namespace breaks that.

So: `ALIFE-ADR-nnn` for decisions, `ALIFE-EXP-nnn` for experiments, numbered from
001 in this repository's own namespace. Directory *shapes* mirror sigma-glyph
exactly — `impl/`, `proofs/`, `tests/`, `tools/`, `experiments/`, `proposals/`,
with the uppercase preregistration beside the lowercase working directory — so a
reader who knows one repository can find anything in the other.

## 3. `impl/sigma_alife.py`, not `src/population.py` (proposal §6)

The proposal's tree has `src/population.py`, `src/morphogenesis.py`,
`proofs_lean/`. sigma-glyph keeps a flat `impl/` holding one module per Book and
installs them as top-level modules. This repository does the same with one
module, `impl/sigma_alife.py`, for the same reason sigma-glyph gives: the file
you read is the file that runs, and `python3 impl/sigma_alife.py` is its own
self-test. `proofs/` is `proofs/`.

The morphogenesis analysis the proposal wanted in a second module is four
functions (`node_census`, `population_census`, `sharing_factor`,
`structural_diversity`) and lives beside the population it measures.

## 4. The proposal's interface does not exist (proposal §6)

It writes:

```python
from sigma_glyph import eval_hash, serialize, validate
```

`eval_hash` exists. `serialize` and `validate` do not: Book I's oracle spells
them `ser` / `deser` (deserialization *is* the validation — it returns `None`
and the caller maps that to the Canonical Invalid Object). Recorded because an
interface contract that names three functions and gets one right is the shape of
a design that was never run, and because the same paragraph is what a reviewer
would otherwise cite as the API.

## 5. The population loop does NOT call `eval_hash` (new, and the load-bearing one)

Book I's `eval_hash` is total over canonical outcomes: when the budget runs out
it returns `DISSONANCE(ATP Exhausted)` **and the partial configuration is gone**.
That is the right contract for a check engine and it makes the proposal's RQ3
unimplementable as written — "agents in settled configurations retain structural
integrity and can resume" cannot be built on an API that hands back a tombstone.

So `reduce_slice` drives `sigma_glyph.step5`, the same priced action, in its own
loop, and keeps the term where the budget stopped it. The deviation is exactly
one outcome wide and it is fenced by `tests/alife_differential.py`: run whole,
the driver must agree with `eval_hash` on result hash *and* on ATP spent, over
every generated term at every budget, including the budgets either side of the
exact spend. Sliced, it must return the whole run's answer. Starved and refed, it
must return the unstarved answer.

Two lesser differences are documented at the function and not hidden:
`max_store_fetches` counts over an agent's lifetime rather than per call, and a
slice boundary is not an outcome.

## 6. Theorem 1 needed a hypothesis the proposal omitted

The proposal states:

```lean
theorem population_peak_size (agents : List Agent) (total_atp : Nat) :
  sum (map peak_size agents) ≤ total_atp + length agents
```

`+ length agents` is only right when every agent was born as a **root thunk** of
size 1. A resumed agent starts from a materialized term of size s₀ > 1, and an
agent spawned by crossover starts from whatever it was spliced into. The proved
statement is therefore

    totalSize as ≤ totalBirth as + totalSpent as

with the proposal's form recovered as `population_peak_size_thunks` under the
explicit hypothesis `∀ a ∈ as, a.birth = 1`. Proving the general form first is
what made the sliced driver in §5 legitimate: `resumption_bound` says an
interrupted run obeys exactly the inequality an uninterrupted one would have.

## 7. Theorem 3 is not worth proving; conservation is

The proposal wants "Conservative Transfer Safety": a donor keeping `size + 1`
cannot break the memory bound. The population bound mentions **no per-agent
reservoir at all** — only the total — so *any* transfer that conserves ATP
preserves it, including one that strips a donor to zero. `transfer_preserves_bound`
is therefore a three-line corollary of conservation, and the honest reading is
that the donor reserve buys **per-agent predictability, not safety**. It is
implemented as a policy heuristic and labelled as one.

The theorem that does need enforcing is the one the proposal did not state:
**ATP must not be minted.** Its §4.3 "agents receive ATP rebates" would create
ATP from a sharing measurement, and every bound stated against a total dies
quietly the moment that happens. Rebates here move ATP out of an explicit commons
pool (`Economy`), the ledger is asserted every tick, and
`tests/alife_conservation.py` C1 is a control that watches minted ATP get caught.

## 8. Preregistration is kept; the strength of the claim is not overstated

sigma-glyph's `exp-004` precedent is followed: hypotheses, corpus and controls
committed before the harness, receipts written only after every control passes,
and a `RESULT.md` that names its own corrections. What cannot be honestly copied
is independence — corpus, preregistration and harness were authored in one
session by one agent, so the ordering is commit order and the result says so in
its second paragraph rather than in a footnote.

## 9. What was NOT adopted from the proposal

- **The 16-week schedule and the venue table** (§7, §8). They describe a research
  programme, not a repository state, and a plan committed as a promise is a
  claim nothing can check. The programme lives in `ALIFE-000` as filed; what
  exists is in `README.md`, and what is next is one experiment at a time.
- **"Book IV — Substrate"** (proposal §6 alternative). Not proposed, not
  requested, and nothing here has earned a place in a normative Book.
