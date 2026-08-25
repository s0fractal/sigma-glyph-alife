# Proofs

One file, `Population.lean`, Lean 4 core only, no mathlib, no `lake`:

    lean proofs/Population.lean          # checks it
    python3 proofs/premise_guard.py      # checks that checking it means something

## What is proved

| theorem | says |
|---|---|
| `step_delta` | an action never grows the term by more than it charges (Book I §3.4 in ℕ, no subtraction) |
| `bound_from` | growth is bounded by spend, measured **from wherever the run started** |
| `ReachFrom.trans` | runs compose |
| `resumption_bound` | **slicing does not weaken the bound**: two consecutive slices obey exactly the inequality one uninterrupted run would have |
| `memory_bound_from_thunk` | Book I's own `size ≤ spent + 1`, recovered as the special case of an agent born as a root thunk |
| `population_peak_size` | `Σ size ≤ Σ birth-size + Σ spent`, with no independence assumption and no appeal to sharing |
| `population_peak_size_thunks` | the operator's form: N agents born as thunks with `budget` between them never materialize more than `N + budget` nodes |
| `transfer_preserves_bound` | any ATP redistribution that conserves the total preserves that bound — **including one that strips a donor to zero** |

`resumption_bound` is the one that earns its keep. `impl/sigma_alife.py` does not
call `eval_hash`, because Book I's exhaustion outcome discards the partial term
and a population needs a body to resume (ALIFE-ADR-001 §5). Driving the priced
step directly is only legitimate if an interrupted run is bounded like an
uninterrupted one, and that is what this file establishes.

`transfer_preserves_bound` is the one that deletes work. The founding proposal
asked for a "Conservative Transfer Safety" theorem about donors keeping
`size + 1`. The population bound mentions no per-agent reservoir at all, so the
conservative rule is not what makes transfers safe — conservation is. The rule
survives in the code as a *heuristic for per-agent predictability*, labelled as
one.

## What is NOT proved, and is not claimed anywhere else either

- **That the Python driver takes these actions.** That is checked, not proved:
  `tests/alife_differential.py` holds `reduce_slice` to `eval_hash` on result
  hash and ATP spent, whole and sliced and starved-then-refed, and
  `reduce_slice(..., probe=True)` asserts the invariant against live traces at
  every action. Two layers, the same split sigma-glyph uses: checked algebra
  plus checked premise on live traces.
- **Anything about the economy policies.** Rebates, the donor reserve, culling
  and crossover are policy. The only theorem that touches them says the bound
  does not depend on them.
- **Termination or liveness.** Nothing here says an agent reaches a normal form.

## The copied premise

`Acc` and `Step` are a **verbatim copy** of sigma-glyph's
`proofs/SizeBound.lean` — the seven priced actions of Book I §3.4 and their exact
effect on `(size, spent)`. Everything above is only as true as that copy is
faithful, so `premise_guard.py` compares it token by token against the original
and fails hard on any difference. The fix for a failure is to re-copy and
re-check every theorem, never to edit the copy.

Set `SIGMA_GLYPH_PROOFS` to the `proofs/` directory of a sigma-glyph checkout;
when the two repositories sit side by side it is found automatically.

## Scope of the guard, stated so it is not mistaken for its neighbour

`premise_guard.py` is **weaker** than sigma-glyph's `proofs/proof_guard.py`. That
one loads the compiled `.olean` as data and pins each theorem's *elaborated type*
against the kernel environment; this one pins *source text*, denies the
metaprogramming and axiom routes, requires every declared theorem to be on the
guarded list, and refuses to parse a file it cannot honestly lex. A determined
notation or delaborator trick could still dress up a statement. That is what a
repository with one core-only Lean file and no `lake` build can enforce today; a
second proof front is the point at which the real guard should be ported rather
than this one extended.
