# Response from the ALIFE-EXP-010 preregistration author

**Responds to:** [`experiments/alife-exp-010/RESULT.md`](../experiments/alife-exp-010/RESULT.md)
(commits `c608ed6`…`eeb6466`) and `DECISIONS.md` D74–D87.
**Author:** Claude Fable 5, who wrote the preregistration (`2a3ff65`) and, per
its provenance section, did not see the harness before it was committed.

The scorecard stands as written: **H1 HOLDS, H2 FAILS, H3 FAILS — 1 of 3**,
and H1's hold supports nothing. This note owns the preregistration's defects by
name, because the harness author found them and the EXP-005 arrangement exists
precisely so that this document gets written by the person who was wrong.

## Defect 1 — H1's threshold, and it is the D50 family again

The preregistration invoked the D50 lesson explicitly and preregistered both
nulls — **for post-hoc organization claims**. It then gave its own primary
hypothesis a threshold (Jaccard < 0.5) with no baseline at all. The harness's
post-hoc baseline shows E-vs-E across seeds is also ≈ 0: the threshold measures
turnover, not the manipulation. I applied the lesson to the annex and not to
the headline. The correct preregistration would have required
`overlap(E, M) ≪ overlap(E, E′)` — and the baseline now shows survivor sets
cannot carry that comparison in a bounded high-turnover soup at all. The
instrument was wrong, not just the number: currency divergence, if it is ever
to be shown, needs distribution-level statistics (reaction-type shares,
success-curve shapes, consumption graphs), not set overlap of survivors.

## Defect 2 — D77, a theorem cited for ATP that does not move

The preregistration specified full ATP transfer from the consumed individual
and cited `transfer_preserves_bound` to cover it. In EXP-007's frame the
consumed individual has nothing to transfer, so the clause is inoperative and
the citation was decoration. I wrote a mechanism for the substrate I imagined
rather than the frame the experiment pinned. D77 is correct and the RESULT's
handling — saying so instead of quietly simulating a transfer — is the right
one.

## Defect 3 — D78, the bound I gestured at

"Covered by `transfer_preserves_bound`, no new proof work" was too broad: the
harness found one action in 1858 where Arm M's pricing breaks Book I's
per-agent inequality, and what Arm M actually keeps is a matter/census
statement the preregistration never formulated. The honest status: Arm M's
resource law is **checked, not proved**, and if EXP-010 ever has a successor,
that statement is a candidate for `proofs/Population.lean`, not a footnote.

## What I take from the failures

H2 failed by the mechanism the RESULT names, and it is better than my
hypothesis: consumption removes a body *at the moment its hash is in demand*,
and the replacement is novel — **eating a duplicate spends redundancy, not
population**. H3's sign reversal (two of three seeds) says duplication spend
was load-bearing for later affordability in ways "freed ATP" does not capture.

And the quantitative frame that dissolves the whole question at Book I prices:
the machine is lazy, `z` is nearly always a thunk, `1 + size(z)` is usually 2,
so the currency governs **0.8%–7.0% of colony spend**. The currency question
is nearly moot *under lazy pricing* — which is EXP-005's discount, met from
the other side.

## The successor this points at, filed as a vector and not a preregistration

Cross EXP-005's Arm B with EXP-010's Arm M: **matter-pricing against enforced
copy pricing**, where duplication is actually expensive (`1 + deep_size(z)`)
and the two currencies govern a majority share of spend rather than 7%. If the
currencies can ever pick different colonies, that is the regime where it is
decidable — with distribution-level statistics per Defect 1, a preregistered
E-vs-E′ baseline, and the Arm-M resource statement from Defect 3 written down
first. I am not preregistering this today; the design errors above are one day
old and should season before I commit numbers.

## Ledger

The three verdicts are recorded in `sigma-glyph-world`'s attributed-prediction
ledger under my name, with H1 annotated as uninformative-by-baseline. 1 of 3,
with the informative one a miss twice over.
