/-
Σ-GLYPH ALife — mechanized bounds for a SLICED, RESUMABLE, MANY-AGENT run.

  THEOREM (resumption):   a run stopped and resumed obeys the same bound as the
                          run that was never stopped.
  THEOREM (population):   Σ size ≤ Σ birth-size + total ATP spent, and with every
                          agent born as a root thunk, Σ size ≤ N + budget.
  COROLLARY (transfer):   any redistribution of ATP that conserves the total
                          preserves the population bound — including one that
                          strips a donor to zero.

SCOPE — what this file proves and what it does not.

`Acc` and `Step` below are a VERBATIM copy of the accounting model in
`proofs/SizeBound.lean` of s0fractal/sigma-glyph (the seven priced actions of
Book I §3.4 and their exact effect on (size, spent)). The copy is not a
convenience: `proofs/premise_guard.py` fails if it drifts from the original by
so much as a token, because everything below is only as true as that model is,
and a substrate that quietly re-specifies its dependency's premise is proving
something about a machine nobody runs.

What sigma-glyph proves from that model is `Reach`, a run from the fixed initial
state ⟨1,0⟩ — one `eval_hash` call, from a root thunk, to an outcome. That is
the wrong starting point for a population: an ALife agent stops when its ATP
runs out and resumes from wherever it stopped, with a materialized term of size
s₀ > 1 and a spend counter already above zero. So this file generalizes `Reach`
to `ReachFrom a b` — a run between two arbitrary accounting states — and proves
the bound in the difference form that survives resumption. `Reach`'s bound is
recovered as the special case a = ⟨1,0⟩ (`memory_bound_from_thunk`), which is
what makes this a generalization rather than a different claim.

NOT PROVED HERE, and not claimed anywhere else either:
  * that `impl/sigma_alife.py`'s driver takes exactly these actions. That is
    checked, not proved: `tests/alife_differential.py` holds the driver to
    `eval_hash` on result and spend, and `reduce_slice(..., probe=True)` asserts
    the invariant against live traces at every action. Same two-layer split as
    sigma-glyph's own (checked algebra + checked premise on live traces).
  * anything about the ECONOMY policies — rebates, the donor reserve, culling.
    `transfer_preserves_bound` says the bound does not depend on them, which is
    the opposite of proving they are good.
  * termination, liveness, or that any agent reaches a normal form.

Verified with Lean 4 core only (no mathlib):  lean proofs/Population.lean
-/

namespace SigmaGlyphALife

/-- Machine state, abstracted to the accounting pair. -/
structure Acc where
  size  : Nat
  spent : Nat

/-- One priced action of the Book I §3.4 machine, by its exact accounting
    effect. Rules that shrink carry their shrink as a hypothesis (R-I drops
    an APPLY node and the ⟨I⟩ leaf: at least 2; R-K additionally drops the
    discarded argument, whose size is at least 1, and the ⟨K⟩ leaf: at
    least 4). R-S is parametrized by the size `z ≥ 1` of the duplicated
    argument in its current materialization (hash-leaf model: thunks
    count 1 and are not forced). -/
inductive Step : Acc → Acc → Prop where
  | forceAtom  {s p : Nat} :
      Step ⟨s, p⟩ ⟨s, p + 1⟩
  | forceRef   {s p : Nat} :
      Step ⟨s, p⟩ ⟨s + 1, p + 2⟩
  | forceApply {s p : Nat} :
      Step ⟨s, p⟩ ⟨s + 2, p + 3⟩
  | rr {s p : Nat} (h : 2 ≤ s) :
      Step ⟨s, p⟩ ⟨s - 1, p + 1⟩
  | ri {s p s' : Nat} (h : s' + 2 ≤ s) :
      Step ⟨s, p⟩ ⟨s', p + 1⟩
  | rk {s p s' : Nat} (h : s' + 4 ≤ s) :
      Step ⟨s, p⟩ ⟨s', p + 1⟩
  | rs {s p z : Nat} (h : 1 ≤ z) :
      Step ⟨s, p⟩ ⟨s + z - 1, p + 1 + z⟩

/-- The per-action premise in difference form: an action never grows the term
    by more than it charges. Book I states it as `Δsize ≤ cost − 1`; over ℕ,
    with no subtraction, that is exactly this. -/
theorem step_delta {a b : Acc} (st : Step a b) :
    b.size + a.spent ≤ a.size + b.spent := by
  cases st <;> simp_all <;> omega

/-- Spending is monotone: no action refunds. -/
theorem step_spent {a b : Acc} (st : Step a b) : a.spent ≤ b.spent := by
  cases st <;> simp_all <;> omega

/-- A run between two arbitrary accounting states. `Reach` in sigma-glyph fixes
    the start at ⟨1,0⟩; a resumed agent starts wherever the budget stopped it,
    so the start has to be a parameter or the population loop is outside the
    proof. `refl` is what makes an interrupted slice a run of length zero. -/
inductive ReachFrom : Acc → Acc → Prop where
  | refl {a : Acc} : ReachFrom a a
  | step {a b c : Acc} : ReachFrom a b → Step b c → ReachFrom a c

/-- THE BOUND, in the form that survives resumption:
    growth is bounded by spend, measured from wherever the run started. -/
theorem bound_from {a b : Acc} (r : ReachFrom a b) :
    b.size + a.spent ≤ a.size + b.spent := by
  induction r with
  | refl => omega
  | step r' st ih =>
      have hd := step_delta st
      have hs := step_spent st
      omega

theorem spent_mono {a b : Acc} (r : ReachFrom a b) : a.spent ≤ b.spent := by
  induction r with
  | refl => omega
  | step _ st ih => have := step_spent st; omega

/-- Runs compose. This is the whole content of "slicing is free": stopping a
    run at a slice boundary and starting another from that exact state is the
    same run, so it is bounded by the same inequality. -/
theorem ReachFrom.trans {a b c : Acc} (r₁ : ReachFrom a b) (r₂ : ReachFrom b c) :
    ReachFrom a c := by
  induction r₂ with
  | refl => exact r₁
  | step _ st ih => exact ReachFrom.step ih st

/-- SLICING DOES NOT WEAKEN THE BOUND. Two consecutive slices obey exactly the
    inequality one uninterrupted run would have obeyed — the resumed agent gets
    no allowance for having been interrupted, and pays no penalty for it. -/
theorem resumption_bound {a b c : Acc}
    (r₁ : ReachFrom a b) (r₂ : ReachFrom b c) :
    c.size + a.spent ≤ a.size + c.spent :=
  bound_from (r₁.trans r₂)

/-- Book I's own statement, recovered as the special case: an agent born as a
    root thunk (size 1, spent 0) satisfies `size ≤ spent + 1` however many times
    it was stopped and resumed on the way. -/
theorem memory_bound_from_thunk {b : Acc} (r : ReachFrom ⟨1, 0⟩ b) :
    b.size ≤ b.spent + 1 := by
  have := bound_from r; simp at this; omega

/-- An agent: born at some materialized size with nothing spent, currently at
    `state`, and the run that connects them. The proof field is the point —
    a list of these is a population whose every member is a real run. -/
structure Agent where
  birth : Nat
  state : Acc
  run   : ReachFrom ⟨birth, 0⟩ state

def totalSize : List Agent → Nat
  | []      => 0
  | a :: as => a.state.size + totalSize as

def totalSpent : List Agent → Nat
  | []      => 0
  | a :: as => a.state.spent + totalSpent as

def totalBirth : List Agent → Nat
  | []      => 0
  | a :: as => a.birth + totalBirth as

/-- POPULATION MEMORY BOUND. The materialized size of a whole population is
    bounded by what it was born with plus what it has burned — with no
    independence assumption, no per-agent budget, and no appeal to sharing.
    (Sharing can only make the CAS footprint SMALLER than this sum: two agents
    holding the same subterm hold one address. The bound is therefore loose by
    exactly the amount the anastomosis experiments measure.) -/
theorem population_peak_size (as : List Agent) :
    totalSize as ≤ totalBirth as + totalSpent as := by
  induction as with
  | nil => simp [totalSize, totalBirth, totalSpent]
  | cons a as ih =>
      have h := bound_from a.run
      simp at h
      simp [totalSize, totalBirth, totalSpent]
      omega

/-- Every agent born as a root thunk contributes exactly 1 to the birth sum. -/
theorem totalBirth_ones : ∀ (as : List Agent), (∀ a ∈ as, a.birth = 1) →
    totalBirth as = as.length
  | [], _ => by simp [totalBirth]
  | a :: as, h => by
      have ha : a.birth = 1 := h a (by simp)
      have ih := totalBirth_ones as (fun x hx => h x (by simp [hx]))
      simp [totalBirth, ha, ih]
      omega

/-- The preflight form, as an operator would use it: a population of N agents,
    each born as a root thunk, that has been given `budget` ATP in total can
    never have materialized more than `N + budget` nodes — whatever the agents
    are, whatever they do, and however the budget was divided among them. -/
theorem population_peak_size_thunks (as : List Agent) (budget : Nat)
    (hb : ∀ a ∈ as, a.birth = 1) (hs : totalSpent as ≤ budget) :
    totalSize as ≤ as.length + budget := by
  have hbirth := totalBirth_ones as hb
  have := population_peak_size as
  omega

/-- CONSERVATIVE TRANSFER, stated honestly.

    The original proposal asked for a theorem saying a donor that keeps
    `size + 1` cannot break the memory bound. That theorem is not worth having,
    because the weaker hypothesis already suffices: the population bound above
    mentions no per-agent reservoir at all. Any policy that MOVES ATP between
    agents — conservative, osmotic, or a donor stripped to zero — leaves both
    sides of `population_peak_size_thunks` untouched, because only the total
    appears in it.

    What a donor reserve buys is per-agent predictability, not safety. Naming
    that difference is the point of stating this as a corollary of conservation
    rather than as a theorem about the rule. -/
theorem transfer_preserves_bound (as : List Agent) (before after : Nat)
    (hcons : before = after) (hs : totalSpent as ≤ before)
    (hb : ∀ a ∈ as, a.birth = 1) :
    totalSize as ≤ as.length + after := by
  subst hcons
  exact population_peak_size_thunks as before hb hs

end SigmaGlyphALife
