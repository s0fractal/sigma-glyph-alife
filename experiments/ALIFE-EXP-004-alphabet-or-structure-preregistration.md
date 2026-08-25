# ALIFE-EXP-004 — is ALIFE-EXP-001's finding about structure, or about the alphabet?

**Preregistration. No measurement has been taken.** Non-normative.

## Why this experiment exists

ALIFE-EXP-001's central sentence is:

> *Reduction consumes shared structure faster than it creates it. Content
> addressing gives a population its sharing at birth; evaluation spends it down.*

It is measured with `sharing_factor` — total node occurrences over distinct CAS
addresses — and in an SKI population the three genesis atoms are by far the most
repeated objects there are. An external review (Claude Fable 5, 2026-08-25) put
the objection precisely: that number cannot tell *"reduction consumes shared
structure"* apart from *"reduction consumes the alphabet"*, and EXP-001's own
mechanism paragraph says reduction eats exactly `I`, `K` and `S`.

The objection is demonstrable in three lines. Three agents that have all reduced
to the single leaf `I` score `sharing_factor = 3.0` — a perfect score, from a
population that has no shared structure at all, only a shared letter.

This experiment is adversarial to this repository's own published result. It is
designed so that a pass buries the claim rather than qualifies it.

## What is already decided, and will not be claimed as a finding

- **`sharing_factor` counts alphabet.** Shown above; not a discovery.
- **Convergence is not symbiosis.** EXP-001 already says this of the `church`
  family. What is open is how much of the *population-level* number it accounts
  for.

## The metrics that separate the two

- **`structural_sharing`** — the same occurrences-over-addresses ratio, counting
  only `APPLY` nodes and excluding genesis: structure an agent *built*, never
  alphabet it inherited.
- **`pairwise_jaccard`** — mean `|A ∩ B| / |A ∪ B|` over agent pairs on those
  filtered address sets. Converged agents have empty structural sets, so their
  Jaccard is *undefined*, not high; pairs where both sets are empty are counted
  and reported separately rather than averaged in as 0 or 1, either of which
  would be a lie.

## Hypotheses

**H1 — the original result replicates.** Under `sharing_factor`, at the
generator's original genesis fraction of 0.7, a settled population shares less
than the same terms materialized and unreduced, in a clear majority of 10 seeds.
*Falsifier:* it does not replicate, and EXP-001 was a single-seed artifact — which
would be a worse finding than the one this experiment is looking for.

**H2 — and it does not survive the separation.** Under `structural_sharing` the
drop **vanishes or reverses**. *Falsifier:* structural sharing falls under
reduction as well, in which case EXP-001's sentence is about structure after all
and survives an attack designed to kill it.

**H3 — dose-response.** The size of the drop under `sharing_factor` scales with
the genesis fraction: a corpus built from few genesis atoms shows little or no
drop. *Falsifier:* the drop is flat in the alphabet fraction, which would mean
something other than the alphabet is producing it.

H2 is the one that matters. H1 and H3 are what make its answer interpretable.

## Design

- Four genesis fractions `0.3, 0.5, 0.7, 0.9` × ten seeds × 64 agents. At
  `g = 0.7` the generator is EXP-001's exactly, so that row is a replication.
- Each population is measured twice on identical terms: **materialized and
  unreduced**, then **settled** (3000 ATP each, as EXP-001).
- Reported per cell: `sharing_factor`, `structural_sharing`, `pairwise_jaccard`
  with its empty-pair count, mean term size, settled count.
- **Every seed reported.** Ten seeds support a direction and a spread, not a
  p-value, and none will be offered.

## Controls

1. **C1 — the metrics disagree where they must.** A population of agents all
   equal to one leaf scores 3.0 on `sharing_factor` and 0.0 on
   `structural_sharing`; a population sharing one large subterm scores above zero
   on both. If both metrics agree on both cases, one of them is not measuring
   what it claims.
2. **C2 — the anchor.** At `g = 0.7` the generator reproduces EXP-001's leaf
   distribution; the corpus at EXP-001's own seed reproduces its fingerprint
   `53cc6da80f66d220`.
3. **C3 — conservation and the bound**, every run.
4. **C4 — the receipt is reproducible.**

## What would make this experiment worthless

- Reporting the structural metric only where it is favourable.
- Treating "the drop vanishes structurally" as *no* result: if H2 holds,
  EXP-001's headline is wrong and this repository's README has to say so in the
  same place it said the other thing.
