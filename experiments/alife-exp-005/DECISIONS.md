# ALIFE-EXP-005 — harness decisions

These decisions were made from the preregistration and engine API before the
EXP-005 measurement was run. They fill operational gaps; they do not amend the
preregistered hypotheses.

## D1 — what `deep_size` expands

`deep_size` counts the fully expanded serialization tree of an occurrence:

- `LITERAL` and `DISSONANCE` count 1;
- `APPLY(l, r)` counts `1 + deep(l) + deep(r)`;
- `REF(h)` counts `1 + deep(h)` (the REF node and the addressed tree);
- a thunk counts the tree at its hash;
- a genesis hash resolves intrinsically;
- an absent or invalid hash counts 1.

A hash cycle denotes an infinite expansion and therefore saturates. Memoization
is by hash, but repeated child occurrences add the memoized value repeatedly.
Thus memoization changes runtime, not the copy semantics.

## D2 — cap semantics and saturation counts

`DEEP_SIZE_CAP` is an inclusive returned ceiling. A value is marked saturated
only when the uncapped value is greater than the cap, or when a child already
saturated; an exactly computable value equal to the cap is not marked
saturated. Copy pricing charges `1 + DEEP_SIZE_CAP` after saturation. Therefore
any total containing a saturated price is a lower bound on uncapped copy cost.

The receipt reports both saturated **pricing attempts** and saturated successful
`R-S` firings. Retry attempts caused by slice escalation are attempts; the
per-firing distribution contains successful firings only.

## D3 — driver and Arm B implementation

Both arms use EXP-001's sorted-agent, one-slice-per-tick driver, escalation from
`SLICE_ATP`, 24-tick limit, shared store, and culling off. The local reducer is a
literal pricing hook around the same `sigma_glyph.step5` action. It changes only
the affordability test and charged cost of a detected `R-S`; the returned term
is still the oracle step's returned term. All other actions use the oracle cost.

Arm A's shadow observes successful `R-S` firings and never changes affordability
or the agent ledger. Arm B computes the copy price before an `R-S` can fire and
uses that price for both affordability and the ledger.

## D4 — what totals and ratios mean

For Arm A, `book_atp` is actual spend and `copy_atp` is the shadow price of that
same Book-I trajectory. For Arm B, `copy_atp` is actual enforced spend and
`book_atp` is the sum of Book-I costs for the actions that actually fired on the
Arm-B trajectory. No Arm-A total is presented as the cost of Arm B.

Population figures are one mixed 64-agent run per arm; family figures are
partitions of those same runs, not separate reruns.

## D5 — distribution conventions

The median is Python's ordinary median over per-firing excesses. The top decile
contains `max(1, ceil(n / 10))` largest firings (or none when `n = 0`). The
receipt also reports the smallest descending prefix whose cumulative excess is
strictly greater than half the total, because H1 says **fewer than 10%**, which
rounding a top decile cannot decide for small `n`.

## D6 — hypothesis scoring thresholds

The preregistration leaves “wide margin” and “materially fewer” numeric-free.
They are fixed here as follows:

- H1 “wide margin”: Arm-A population shadow-copy ATP is at least 2 times its
  Book-I ATP. H1 as a whole also requires that the strict-majority prefix from
  D5 contain fewer than 10% of `R-S` firings.
- H2 “materially fewer”: Arm B settles at least `ceil(10% * 64) = 7` fewer
  agents than Arm A. Settled agent identities are also recorded, so the weaker
  preregistered falsifier (“the same agents settle”) remains inspectable.
- H3 “discount”: total Arm-A shadow excess per family. `dup` must be the unique
  maximum, `drop` the unique minimum, and `dup / drop >= 2`. If `drop` is zero,
  the ratio condition holds only when `dup` is positive.

These thresholds are harness-author decisions, not findings from the data.

## D7 — seven controls and recording

C1 and C3 range over the full Arm-A corpus run. C4 ranges over every Arm-B agent
that settles. C2 uses deterministic I/K-only terms that cannot fire `R-S`. C5
checks conservation and the population memory bound in both complete runs. C6
checks the inherited fingerprint. C7 both forces a synthetic saturated DAG and
checks that every aggregate in the would-be receipt carries explicit attempt and
firing saturation fields.

`results.json` is written only after all seven controls pass. `RESULT.md`'s
reproduction recipe is written only after those controls and `tools/test-all.sh`
have passed.
