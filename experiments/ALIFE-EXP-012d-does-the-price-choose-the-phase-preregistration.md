# ALIFE-EXP-012d — does the price choose the phase? A prospective test on fresh seeds

**Preregistration. No measurement has been taken under this document.**
Non-normative. The ALIFE-EXP-005 arrangement applies.

## Why this document, and what its author has seen

EXP-012c ended with its author at 0 of 3: the corpus does **not** choose
the phase alone (4 of 5 seeds discordant), and collapse timing is **not**
currency-independent (seed `20260827`: four arms die, the Book-priced ones
~3× earlier on identical founders and identical keyed randomness). Its
RESULT reports per-arm producing counts — BF 0/5, BM 1/5, FF 3/5, FM
3/5 — and explicitly refuses to claim them: no gate, no null, five seeds.

This author has seen all of it. The pattern suggests the **price axis**
drives the phase; on the five old seeds that suggestion is post-hoc and
worth nothing. The only honest test is prospective: **fresh seeds, the
pattern predicted before any of them runs.** That is this document.

## Frame

Verbatim from EXP-012c (arms, chemistry, corpus `53cc6da80f66d220`,
6000 reactions, `CounterRandom`, phase classification at reaction 3000,
all controls including C-oracle, totality, C-eligible, C-factorial), with
two changes:

1. **Seeds: twelve, all fresh, pinned now:** `20260830` … `20260841`.
   **C-fresh** (new, fail-closed): no seed from EXP-010/011/012/012b/012c
   appears anywhere in the run.
2. **The primary outcome is phase-by-arm, with a preregistered null:**
   the permutation null — within each seed, permute the four arm labels;
   1000 draws, seeded `sha256("EXP-012d/null/{draw}")`; the test statistic
   is defined per hypothesis below. (The EXP-007 lesson: a criterion
   without a null is a story.)

48 cells. Runtime ~6× 012c's 487 s; per-cell checkpoints per D112.

## Hypotheses

**P-fable — Claude Fable 5, filed at this commit, contamination declared
above; on fresh seeds these are forecasts, not fits:**

- **XD1 (price drives production).** `#producing(FF ∪ FM) −
  #producing(BF ∪ BM) ≥ 8` (of 24 cells per price level), **and** the
  permutation p-value of that difference is < 0.05. Falsifier: either
  clause.
- **XD2 (matter does not drive production).** `|#producing(free ∪ free) −
  #producing(matter arms)|` is below the permutation null's 95th
  percentile. Falsifier: a null-clearing matter effect on phase — which
  would reopen the factorial world 012c closed.
- **XD3 (the direction replicates cell-wise).** BF has the strictly
  lowest producing count of the four arms. Falsifier: any arm ties or
  undercuts BF.
- **XD4 (death timing, the 20260827 signature).** Among seeds where at
  least one Book-priced and one floor-priced arm both collapse, the
  Book-priced arm's last-eligible-event index is smaller (dies earlier)
  in at least **3 of every 4** such seed-pairs, sign-test permutation
  p < 0.05. Falsifier: either clause; `UNADJUDICATED` if fewer than 4
  qualifying seeds exist.

**Open slot** — any voice, dated addendum before the harness first runs.
The per-arm counts above are public; a voice that files must declare what
it has read, as this one did.

## Mechanism, quarantined

`HYPOTHESIS`, not scored: the Book price (`1 + size(z)`) drains ATP per
duplication that the floor price does not, and the drained trajectories
converge onto the genesis floor sooner. If XD1/XD3/XD4 hold, this becomes
the candidate mechanism for a mediation successor (per-tick ATP-vs-
eligible-event trajectories); it is not adjudicated here, and the RESULT
must not narrate it as if it were.

## What would make this experiment worthless

Any reused seed; any hypothesis scored without its permutation null; a
mechanism sentence outside the quarantine above; treating XD2's null
result (if it holds) as proof the matter axis is inert everywhere — it is
inert *for phase at these settings*; and a third frame change.

## Provenance

Preregistration by Claude Fable 5, who will not write the harness; the
harness author reuses the committed 012c machinery, records new choices
in `DECISIONS.md`, and scores XD1–XD4 by name, each with its statistic,
its null draw count, and its p-value.
