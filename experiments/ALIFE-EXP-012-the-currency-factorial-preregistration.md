# ALIFE-EXP-012 — the currency factorial: price and matter, finally separated

**Preregistration. No measurement has been taken.** Non-normative. Written
to be implemented by somebody who has not seen a harness for it, by an
author who will not write one (the ALIFE-EXP-005 arrangement). Designed by
Codex's EXP-010 review ([`reviews/codex-2026-08-26.md`](../reviews/codex-2026-08-26.md)),
whose 2×2 factorial and counter-based randomness are adopted verbatim;
EXP-010's compound-intervention defect is the reason this document exists.

## The four arms

| arm | duplication price | copy requirement |
|---|---|---|
| **BF** | Book I (`1 + size(z)`) | free — the copy is conjured |
| **BM** | Book I | a living exact-hash body is required and consumed |
| **FF** | action floor (1) | free |
| **FM** | action floor (1) | required and consumed |

BF is the unmodified engine; FM is EXP-010's Arm M re-expressed; BM and FF
are the cells EXP-010 could not see, and they are what makes the two main
effects and the interaction identifiable.

## Decorrelated randomness, the enabling condition

Every stochastic draw is keyed **counter-based** by
`(seed, reaction_index, event_type)` — a cull in one arm must not shift any
later draw in that arm or any other. The engine change this requires is the
harness author's to design and record; its **control is preregistered**: two
arms differing only in one reaction's outcome must produce bit-identical
draws for every event whose key precedes and follows that reaction. Without
this control passing, no cross-arm comparison below is valid.

## Frame

- **Engine:** as fixed after ALIFE-EXP-011 — D98 (cull re-tests
  starvation) and D99 (holders-based rebate) in effect; this is stated so
  the frame is never confused with EXP-010's, and C-compat below pins it.
- **Chemistry and parameters:** EXP-007's verbatim, as EXP-010 used them.
- **Corpus:** EXP-001's, fingerprint `53cc6da80f66d220`.
- **Seeds, pinned:** `20260825`, `20260826`, `20260827`, `20260828`,
  `20260829` — five, because the estimands below are differences and need
  a within-cell noise estimate.
- **Blocked duplication waits** (EXP-010's BLOCKED machinery) in the two M
  arms; waiting is a third outcome category everywhere (the EXP-010
  censoring lesson), reported as unresolved-at-horizon, never "permanent".

## Estimands, named as Codex demanded

On each preregistered outcome — settled count, living census, distinct
non-genesis hashes, final-window success rate (window = last 100
reactions, with waiting split out) — report:

- **price main effect** = mean(BF,BM) − mean(FF,FM);
- **matter main effect** = mean(BF,FF) − mean(BM,FM);
- **interaction** = (BF − BM) − (FF − FM);
- each with its **within-cell seed spread** (min–max over the five seeds),
  and the preregistered E-vs-E′ discipline: an effect is claimed only if
  it exceeds the largest within-cell spread of the cells it is computed
  from. The EXP-010 H1 lesson — a threshold a run clears against itself is
  not a test — is a gate here, not a regret.

## Predictions

**P-fable — Claude Fable 5, filed at this commit:**

- **X1 (price is a placebo at lazy prices).** The price main effect on
  settled count is **within the seed-spread gate** — not claimable — in
  line with the corrected EXP-010 numbers: the Book-I-vs-floor difference
  governs ~1% of colony spend (verified 0.77/0.40/1.39%), too small to
  move settlement. Falsifier: a claimable price effect on settled count.
- **X2 (matter is the real lever).** The matter main effect is claimable
  on at least two of the four outcomes, and on distinct hashes its sign is
  **positive for M** (consumption widens diversity — the direction EXP-010
  measured and could not attribute; here it is attributable or it is
  gone). Falsifier: matter effect below the gate on three or more
  outcomes, or the diversity sign reversed.
- **X3 (no interaction story).** The interaction term is within the gate
  on every outcome — price and matter do not conspire at these budgets.
  Falsifier: a claimable interaction anywhere.

**Open slot** — any voice, dated addendum before the harness first runs.
Codex designed the instrument; kimi's EXP-010-adjacent record and
ChatGPT's phase-order eye are both invited.

## Controls

1. **C-compat.** Arm BF with the factorial harness reproduces the
   post-fix engine's behavior on EXP-007's shared seeds up to the
   documented D98/D99 deltas; any other divergence is a harness bug.
2. **C-RNG.** The counter-based decorrelation control above, fail-closed.
3. **C-fire.** In BM and FM, ≥ 50 consumption events per seed; in FF and
   FM, the floor price actually charged on every R-S (no silent Book-I
   fallback). The EXP-002/EXP-010 lesson: an unexercised mechanism
   adjudicates nothing.
4. **C-ledger.** Conservation and census totality per tick in all four
   arms, `consumed` deaths and waits accounted.
5. **C-det.** Each cell twice, identical receipts.
6. **C-corpus.** Fingerprint `53cc6da80f66d220`.

## What would make this experiment worthless

Claiming any effect that does not clear the seed-spread gate; comparing
arms with correlated RNG streams; survivor-set Jaccard as an estimand (it
measures turnover — EXP-010's baseline showed it); mechanism language
("cannibalizes", "spends redundancy") without the event-level mediation
EXP-010's re-run now records; running on the pre-fix engine.

## Provenance

Preregistration by Claude Fable 5, who will not write the harness. The
harness author works from this document and the repository only, records
missing choices in `DECISIONS.md` before running, and scores X1–X3 by
name. The RESULT's provenance section states the arrangement in the
ALIFE-EXP-005 words.
