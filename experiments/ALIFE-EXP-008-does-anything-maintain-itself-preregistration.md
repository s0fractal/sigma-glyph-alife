# ALIFE-EXP-008 — does anything in the soup maintain itself?

**Preregistration. No measurement has been taken** except the window probe in
`alife-exp-008/corpus.py`, which reports the chance model and nothing else.
Non-normative.

## Why this experiment exists

ALIFE-EXP-007 measured organization the way an outsider would and every criterion
it met was met by chance. Its own limitation section names the gap: **its
L1-core was computed over the whole reaction history**, so it counted molecules
that died hundreds of reactions ago, and a shuffled graph of the same density
produced a larger one.

Fontana & Buss's organizations are not history. They are sets that **persist in
the population** — that keep existing while the discard rule keeps deleting.
This experiment asks for that, and only that.

## The definition, fixed here

A set `S` of hashes is **self-maintaining over a window `W`** when every member
of `S`

1. is **alive** — present in the soup at the end of the run; and
2. was **re-produced within the last `W` reactions** by a reaction whose two
   reactants are both members of `S`.

Computed by peeling: drop any member that fails either condition, until nothing
drops. Condition 2 is what EXP-007's core lacked, and it is the whole of the
difference: a member must be *being made*, now, out of the set itself.

**The window is not tuned.** It is a free parameter, so it was probed against the
chance model alone. A shuffled reaction graph yields an **empty** self-maintaining
set at every window from 25 to 600. No choice of `W` can favour the hypothesis, so
the full curve is reported rather than a point.

## What is already decided, and will not be claimed as a finding

- **That a history-core is met by chance.** ALIFE-EXP-007 measured it; this
  experiment exists because of it.
- **That the shuffled null is empty here.** Probed above. What is open is whether
  the *observed* data is empty too — in which case this metric is vacuous in the
  other direction and the honest report is that nothing in this soup maintains
  itself.

## Hypotheses, each with its number and its chance model

**H1 — something maintains itself.** A self-maintaining set of size ≥ **3** exists
at some window, in a majority of the three seeds, **while the shuffled-graph null
is empty at that same window**. The null is inside the hypothesis, per
`DECISIONS.md` D50, because that is the rule EXP-007 was written without.
*Falsifier:* every observed set is empty or smaller than 3. Then nothing in this
chemistry maintains itself at this scale, and EXP-007's organizations were
entirely an artifact of counting the dead.

**H2 — persistence discriminates.** On the same runs, EXP-007's history-core is at
least **5×** larger than the self-maintaining set.
*Falsifier:* they are the same size, which would mean the persistence requirement
adds nothing and the two metrics are one metric.

**H3 — what persists is cheap.** The reactions that sustain a self-maintaining set
cost at least **30% less** than the mean successful reaction in the same run,
compared against the same statistic over a size-matched random subset of alive
hashes.
*Mechanism, stated so it can be wrong:* the discard rule deletes members at a
fixed rate, so a set whose members are expensive to re-make cannot replace them
fast enough. Price would then decide not *which* molecules exist but *which*
organizations can hold together — the substrate's own question, which EXP-007
could not answer with a statistic that did not discriminate.
*Falsifier:* no cost difference, or the random subset shows the same one.

## Design

- The chemistry is EXP-007's, verbatim: same founders, same capacity 64, same 1000
  reactions, same random discard, same reaction rule, same blind-chosen 200 ATP.
- Budgets `50, 200, 3000` × three seeds. Three budgets, not four: the run is a
  ten-minute job and the fourth bought nothing in EXP-007.
- Windows `25, 50, 100, 200, 400, 600, 1000`, the whole curve, for the observed
  data **and** the shuffled null, side by side in every table.
- Reported: self-maintaining set size per window, the null's size per window,
  EXP-007's history-core on the same run, the sustaining reactions' mean cost, the
  size-matched random subset's mean cost, and the set's membership.

## Controls

1. **C1 — the peeling is correct.** On a hand-built self-maintaining pair, both
   alive and both re-produced inside the window, the set is `{a, b}`; move either
   production outside the window and the set is empty; kill either member and the
   set is empty. Three cases, because condition 2 is new and untested.
2. **C2 — the null is computed on the same run**, not on a fresh one: same
   reactant pairs, same product multiset, products permuted.
3. **C3 — conservation and the memory bound**, throughout.
4. **C4 — no DISSONANCE is a molecule.**
5. **C5 — founders** are EXP-001's, by fingerprint.
6. **C6 — vacuity is reported, not hidden.** If every observed set at every window
   in every arm is empty, the run is **UNADJUDICATED** for H2 and H3 — there is
   nothing to compare — and H1 is reported as **refuted**, which is a real answer
   and not a failure of the harness.
7. **C7 — the receipt reproduces** byte for byte.

## What would make this experiment worthless

- Reporting a self-maintaining set without the null column beside it, at the same
  window, on the same run.
- Choosing the window after seeing the observed curve.
- Calling a set that exists at window 1000 — the whole run — self-maintaining. At
  that window condition 2 degenerates into EXP-007's history-core, and the curve
  is reported precisely so that degeneration is visible rather than hidden.
- Claiming emergence, again. Founders are a hand-built corpus. `RELATED.md`.

## Provenance

Preregistration and harness by the same model in the same session. Thresholds and
chance models are in this document because, per D46 and D50, nobody else is here
to be blocked by their absence.
