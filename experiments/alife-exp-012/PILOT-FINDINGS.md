# ALIFE-EXP-012 / 012b — pilot findings

**Descriptive artifact. FACTs only. These pilots score nothing, ever.**

Both runs ended `FAILED-CONTROLS` and neither wrote a receipt. Under
ALIFE-EXP-012b's successor rule they are reclassified as **calibration pilots**:
they establish measured facts about the instrument and supply no estimates.

This file therefore contains **no factorial effect estimates and no X-scoring**.
Both preregistrations' worthlessness lists forbid quoting effects that have not
cleared their admission rule, and ALIFE-EXP-012c's forbids scoring anything
against these pilots' numbers. What is below is what the two runs *measured*
about the chemistry, the mechanism and the environment.

| | |
|---|---|
| pilot 1 | ALIFE-EXP-012, commit `b8bf698`, 1000 reactions per cell |
| pilot 2 | ALIFE-EXP-012b, commit `5a80d6f`, 6000 reactions per cell |
| frame | 4 arms (BF/BM/FF/FM) × 5 seeds (`20260825`–`20260829`), EXP-007's chemistry, capacity 64, 200 ATP/reaction |
| corpus | ALIFE-EXP-001's, fingerprint `53cc6da80f66d220` |
| oracle | `413d1f9805cdbdf42f13d967a17be26eb959c692eeb067e7146203ed9cebe64d` at sigma-glyph `d3f1b512` |
| randomness | counter-based, keyed `(seed, reaction_index, event)` — `DECISIONS.md` D101–D102 |
| ordering | committed **after** ALIFE-EXP-012c's preregistration (`73e1ca2`), so the breakdown below cannot have shaped it |

## FACT 1 — totality: the mechanism misses nothing eligible

In **every** M cell of **both** runs, exactly:

```text
consumed + blocked  ==  R-S fired − R-S on genesis
```

Ten cells at 1000 reactions and ten at 6000, zero violations. Every duplication
of a non-genesis term is accounted as either a consumption or a wait; none is
dropped, double-counted, or silently priced some other way. This identity was
first a diagnostic in ALIFE-EXP-012's failure report and became a preregistered
control in 012b, where it passed.

Its consequence is the load-bearing one: when a consumption count is low, the
mechanism is not misfiring. The **eligible events themselves** are what is
scarce.

## FACT 2 — the eligible-event trajectories, per cell

Eligible = non-genesis R-S. Genesis duplication is free by the preregistered
rule, so only non-genesis duplication can engage the matter mechanism.

| cell | eligible @1000 | eligible @6000 | consumed @6000 | blocked @6000 | of them before reaction 1000 | **last eligible at** |
|---|---:|---:|---:|---:|---:|---:|
| FM/20260825 | 45 | **45** | 22 | 23 | 45 | **435** |
| BM/20260825 | 76 | **76** | 52 | 24 | 76 | **625** |
| BM/20260827 | 98 | **98** | 46 | 52 | 98 | **706** |
| FM/20260827 | 98 | **98** | 46 | 52 | 98 | **706** |
| BM/20260826 | 112 | **112** | 58 | 54 | 112 | **723** |
| BM/20260828 | 136 | 137 | 61 | 76 | 136 | **1040** |
| FM/20260826 | 200 | 347 | 236 | 111 | 200 | 5997 |
| FM/20260828 | 233 | 662 | 499 | 163 | 233 | 5927 |
| BM/20260829 | 258 | 1018 | 944 | 74 | 258 | 5985 |
| FM/20260829 | 258 | 1206 | 1132 | 74 | 258 | 5001 |

**The six / four split, with complete identities.**

*Six cells stop* — their last eligible event falls before reaction 1100, and the
remaining 82–93% of the 6000-reaction run produces **zero**:

> `FM/20260825` (last 435) · `BM/20260825` (625) · `BM/20260827` (706) ·
> `FM/20260827` (706) · `BM/20260826` (723) · `BM/20260828` (1040)

*Four cells produce to the horizon* — last eligible event between reaction 5001
and 5997:

> `FM/20260829` (5001) · `FM/20260828` (5927) · `BM/20260829` (5985) ·
> `FM/20260826` (5997)

There is **no middle**. The gap between the largest stopper (1040) and the
smallest producer (5001) is empty.

Note the arm/seed structure, stated as an observation and not as an effect:
seeds `20260825` and `20260827` stop in **both** matter arms; seed `20260829`
produces in both; seeds `20260826` and `20260828` stop in BM and produce in FM.

The free arms were counted but not indexed — the pilots instrumented only the
consumption path, so BF and FF have eligible totals at 6000
(BF: 113, 98, 221, 232, 98; FF: 473, 99, 262, 868, 686 across the five seeds)
and no last-event indices. Recording indices in all four arms is a change
belonging to a later harness, not a fact of these pilots.

## FACT 3 — run length is not a remedy: the flat curve

On the binding cell `FM/20260825`, holding everything else fixed:

| reactions | 1000 | 2000 | 4000 | 6000 | **12000** |
|---|---:|---:|---:|---:|---:|
| eligible non-genesis R-S | 45 | 45 | 45 | 45 | **45** |
| consumed | 22 | 22 | 22 | 22 | **22** |
| distinct non-genesis survivors | 27 | — | 19 | 21 | 18 |
| settled reactions | 762 | 1133 | 1345 | 1431 | 1457 |

**Twelve times the run length yields zero additional eligible events.** The run
keeps settling reactions — 762 → 1457 — so the soup is alive and reacting; what
it has stopped doing is producing non-genesis structure to duplicate. Five of
the ten M cells are similarly flat between 1000 and 6000 (76→76, 112→112,
98→98, 136→137, 45→45, 98→98).

Across the stopped cells the distinct non-genesis survivor count at 6000 falls
to between **4 and 32**, from a capacity of 64.

## FACT 4 — passing dead cells

Two of the six stopped cells clear 012b's supply floor of 100 anyway, purely by
where they happened to stop:

> `BM/20260826` — 112 eligible, **all before reaction 1000**, last at 723
> `BM/20260828` — 137 eligible, 136 before reaction 1000, last at 1040

Both are admitted by a count-over-the-whole-run criterion and both produced
nothing for the final 82–88% of the run. An admission rule stated as a total
over a fixed horizon cannot distinguish a cell that is producing from a cell
that produced early and died. This is recorded as a property of that *rule*; it
did not change either pilot's verdict.

## FACT 5 — the oracle drifted mid-session, and the digest caught it

During the first pilot the sibling `sigma-glyph` checkout advanced past
`d7eab26`, changing `impl/sigma_glyph.py` from `413d1f98…` to `a4200cb6…`.
`tools/test-all.sh` went red on ALIFE-EXP-001's replay with a one-line diff of
the recorded oracle digest. Nothing in this repository had changed.

The repository's own pin (`SIGMA_GLYPH_PIN = d3f1b512`) still yields
`413d1f98…`. Every number in this file was produced against that pinned oracle,
extracted with `git archive` so the sibling repository's working tree was never
touched. Re-running both pilots' control suites on the pinned oracle reproduced
their outcomes identically, which is how the drift was shown not to be the cause
of either failure.

ALIFE-EXP-012b added `C-oracle` in response: the digest is asserted at the start
**and** the end of a run, so a drift mid-run invalidates the run rather than the
pin. It passed at both ends of a 485-second run. `DECISIONS.md` D109.

## What these pilots do not contain

- **No factorial effect estimates.** Both runs computed cell means, seed spreads
  and the price/matter/interaction terms; none of it cleared its preregistered
  admission rule, and none of it is quoted here or anywhere else.
- **No X1/X2/X3 verdicts.** They were never adjudicated in either pilot and are
  re-filed unchanged in the successors.
- **No claim about which regime a cell lands in.** FACT 2 reports which cells
  stopped and which did not. Whether the *currency* has anything to do with that
  is the question ALIFE-EXP-012c preregisters, and this artifact was committed
  after that document precisely so it could not shape it.
