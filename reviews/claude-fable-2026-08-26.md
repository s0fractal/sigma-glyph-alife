# External review — the RELATED.md caveat, partly discharged

**Target:** `master` at the state containing EXP-001…009, analysis-001, and
DECISIONS.md through D73.

| field | value |
|---|---|
| attributed model | Claude Fable 5 (`claude-fable-5`) |
| date | 2026-08-26 |
| platform | Claude Code CLI, local session with the repository owner |
| what was executed | `impl/sigma_alife.py` against `SIGMA_GLYPH=../sigma-glyph/impl`: **ALIFE: ALL PASS (29/29)**, oracle sha256 `413d1f98…` — and nothing else. No experiment was re-run; no receipt was re-verified |
| primary sources read this session | Kruszewski & Mikolov, arXiv:2103.08245v3, **pp. 1–10 of the full text** (model definition, temporal evolution, detection §5.1–5.2); Mathis, Patel, Weimer & Forrest, arXiv:2408.12137v2, **pp. 1–8 of the full text** (model recount, L0/L1/L2, methods, L0/L1 results) |
| what remains unread | K&M experimental sections beyond p. 10 (emergent-structure results, consumption-above-chance metric details); Return-to-AlChemy beyond p. 8 (L2, random-generator study, CRN construction) |

Per `AGENTS.md`: this is not a roster review and grants nothing. It records
what one reviewer read, ran, and now predicts.

---

## 1. RELATED.md against the primary texts

`RELATED.md` was written from abstracts and says so. The pages read this
session discharge part of that caveat. Verdicts, per claim:

**Claim 1 — "molecules are content-addressed here, copies there" — CONFIRMED
against full text.** K&M §4: "we postulate the existence of a multiset of CL
expressions P"; concentrations are per-expression counts; nothing in the model
shares structure between instances. No sharing or deduplication is measured
anywhere in pp. 1–10. The differentiation stands, now on a real reading.

**Claim 2 — "resource law is a theorem, not a bookkeeping rule" — CONFIRMED,
and sharpenable into something better.** K&M enforce conservation by *reaction
design*: reduction rules emit by-products carrying the removed combinators, and
— the important part — the S-reaction requires a **physical copy of the
duplicated argument to already exist in the multiset as a reactant**, which is
consumed. So the deep contrast is not "bookkeeping vs proof"; it is:

> **Combinatory Chemistry prices duplication in matter** (a copy must pre-exist
> and is consumed); **Book I prices duplication in energy** (`C_dup` charges
> ATP). Same act, two currencies.

That sentence is stronger positioning than what RELATED.md has, and it opens a
real experiment (V1, §3).

**Claim 3 needs a correction before any paper repeats it.** Resumability *per
se* is not new. K&M: "each reduce reaction corresponds to a single reduction
step that can always be computed … distributing their (potentially infinite)
computation steps over time as individual reactions" — their expressions are
never discarded for failing to normalize, because a step is atomic and
recursion is just more reactions. AlChemy, by contrast, uses *pragmatic
reduction*: a 500-step cap, and a reaction that hits it is "elastic" — the
original expressions are returned and **the partial work is discarded**. The
honest three-way table, which I recommend RELATED.md adopt verbatim:

| system | interrupted evaluation |
|---|---|
| AlChemy (Fontana & Buss; Mathis et al. 2024) | partial work discarded ("elastic" reaction) |
| Combinatory Chemistry (K&M) | no partials exist — steps are atomic, recursion is distributed over reactions |
| this repository | partial work kept, **with a machine-checked receipt** (`resumption_bound`: two slices obey exactly the whole-run inequality) |

What is new here is the receipt and the pricing, not the survival.

**A differentiator RELATED.md does not name and should.** K&M sample reactions
via Gillespie and pick redexes at random ("more natural for a chemical
system"); AlChemy picks colliding pairs at random. This repository's runs are
**deterministic** on a pinned corpus under Book I's normative strategy. That
determinism is not a detail — it is the *enabling condition* for the
preregistration-with-exact-numbers discipline this repository runs on. Neither
ancestor could have preregistered "H2 ≥ 8 agents" and meant it.

**One line worth adding.** K&M cite Fontana & Buss's 1996 follow-up **MC2**
(a chemistry based on Linear Logic, addressing conservation of mass) as having
no empirical work they know of. Linear logic is resource-sensitive duplication
— the closest *theoretical* ancestor of priced duplication — and the fact that
its empirical slot has been open since 1996 is exactly the slot this
repository occupies.

## 2. The null battery is ahead of the flagship literature, and can now say so

Verified against Return-to-AlChemy pp. 5–8: the reappraisal detects and
characterizes organizations via **perturbation robustness** (replace p% of
expressions with the identity and see whether the organization survives),
Jaccard similarity, population entropy, and expression length. **No shuffled or
randomized null baseline appears in the pages read.** Their surprise finding —
complex, stable organizations in unfiltered L0 simulations, robust to 90%
replacement — is reported without any null of the kind EXP-007 was killed by.

Meanwhile EXP-007's own record is: all three preregistered criteria met, and
**none survives its null**; EXP-008's H1 beats the full shuffle and dies
against the locality-preserving null. If the same locality-preserving null were
run against organization detection in the wider literature, some published
organizations might not survive it either. That is a claimable methodological
contribution — arguably the strongest one this repository has — and it is
currently buried in two RESULT files and D50. It deserves to be the explicit
second thesis of any paper: *the field's detection criteria pass things its
own nulls would kill, and here is the null battery.*

## 3. Vectors, with attributed predictions filed before any harness

Per rule 7, these are hypotheses offered for preregistration, not
preregistrations. Predictions are mine, to be scored by name if adopted.

**V1 — matter-pricing vs energy-pricing (the K&M bridge).** Implement K&M-style
conservation inside this substrate: an `S`-duplication is affordable only if a
copy of the duplicated subterm exists in the population, and consumes it.
Matched total resources, same founders, same chemistry otherwise. Question:
do the two currencies select the same organizations?
*Prediction (fable):* they do not — matter-pricing favors decomposition loops
(K&M's metabolic cycles need a supply of consumable parts), energy-pricing
favors cheap self-contained cycles like the 93.7%-success attractor D72 found.
*Falsifier:* same attractor sets under both currencies at matched totals.

**V2 — determinism as an instrument.** Run the EXP-007 chemistry under
Gillespie-style stochastic reaction sampling at matched reaction counts, same
founders, and score the same criteria against the same nulls.
*Prediction (fable):* criteria-passing is roughly insensitive, but the
locality-preserving null becomes **harder** to beat under stochastic sampling —
i.e. part of what the stochastic literature reads as organization is sampling
structure. This is the riskiest prediction in this file and the one I would
most like to see scored.

**V3 — lineage-priced memoization (blocked, and the block is named).** EXP-002
found the memo pays only down a demand path and lineage is the free one. The
evolutionary question — does selection favor memo-heavy lineages, and is there
a threshold in memo price where it stops — is well-posed but **blocked on
DA-SIGMA-0002** (`k` vs `k−1`), already filed under `needs/`. Nothing to do
here but keep the dependency visible in whatever roadmap exists.

**V4 — endorse D72's successor as stated.** A budget that scales with the soup
is the right next experiment and needs no input from me; the self-pricing-out
finding (success 54% → 16% at fixed per-reaction budget) is itself worth a
paragraph in any paper, because neither ancestor *could* observe it — neither
has a per-action budget at all.

## 4. Paper shape, updated for what §§1–2 established

The thesis I would now write on the title page: **evaluation spends sharing,
affordability is the selection pressure, and the null battery is the method.**
Three legs:

1. *Substrate* (vs K&M, now with page-level positioning): energy-priced
   duplication with a machine-checked bound, deterministic runs, resumption
   with a receipt — against matter-priced, stochastic, atomic-step chemistry.
2. *Results:* EXP-001/004 (sharing is spent, survives the adversarial re-test
   10/10), EXP-003/005 (the library band; the 25–62 ATP binding range),
   EXP-006 (resumption worth +13…+31 agents, first use of the theorem),
   D72 (self-pricing-out).
3. *Method:* the null battery, positioned against a flagship reappraisal that
   uses perturbation robustness and no nulls (§2).

What still blocks it: the unread halves of both primary sources (the K&M
consumption-metric details matter for leg 1's fairness; Return-to-AlChemy's
L2/random-generator sections matter for leg 3's claim), and V4's run, which
would turn D72 from an anecdote into a measured curve. Population scale (64)
is a reviewer objection leg 2 cannot dodge; D72's twelve-worker scale run is
the template for answering it.

## 5. What this review did not do

It did not verify any receipt, re-run any experiment, audit the Lean proofs
beyond noting `premise_guard`'s existence, or read either primary source to the
end. §1's verdicts hold for the pages named in the provenance table and no
further.
