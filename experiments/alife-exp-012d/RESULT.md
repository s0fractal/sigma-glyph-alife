# ALIFE-EXP-012d — result

Judged against [`ALIFE-EXP-012d-does-the-price-choose-the-phase-preregistration.md`](../ALIFE-EXP-012d-does-the-price-choose-the-phase-preregistration.md),
committed at `9b045ce` before this harness existed. The choices that document
left open are `DECISIONS.md` D122–D126, committed before the measurement ran.

**Provenance, stated at its real strength.** The preregistration was written by
Claude Fable 5 and this harness by Claude Opus 5, working only from the committed
documents, the repository and its dependencies, and this is the ALIFE-EXP-005
arrangement — a real separation of roles between different models, not an
independent registry, external review, or statistical replication.

**This is the prospective test its own author asked for.** ALIFE-EXP-012c ended
with per-arm producing counts — BF 0/5, BM 1/5, FF 3/5, FM 3/5 — that its RESULT
reported and explicitly refused to claim: no gate, no null, five seeds already
seen. The preregistration declares that its author saw all of it, files the price
axis as the driver, and pins twelve seeds nobody had run. C-fresh checks that
none of them appears in EXP-010, 011, 012, 012b or 012c.

## The verdicts

**All four hypotheses fail. The 012c pattern did not replicate — and on the
decisive arm it reversed.**

| | statistic | observed | null draws | p | verdict |
|---|---|---:|---:|---:|---|
| **XD1** | #producing(floor) − #producing(book) | **−1** (needs ≥ +8) | 1000 | 0.7722 | **FAILS** |
| **XD2** | \|#producing(free) − #producing(matter)\| | **5** (needs < 95th pct = 5.00) | 1000 | 0.1419 | **FAILS** |
| **XD3** | min(other arms) − BF | **−4** (needs > 0) | 1000 | 0.9830 | **FAILS** |
| **XD4** | signed sign-test, book earlier − floor earlier | **0**, ratio 0.50 (needs ≥ 0.75) | 1000 | 0.4875 | **FAILS** |

| | |
|---|---|
| substrate | `impl/sigma_alife.py` 0.1.0 on Σ-GLYPH Book I, oracle sha256 `413d1f9805cdbdf42f13d967a17be26eb959c692eeb067e7146203ed9cebe64d` at sigma-glyph `d3f1b512` |
| frame | 4 arms × **12 fresh seeds** `20260830`–`20260841` = 48 cells, 6000 reactions, capacity 64, 200 ATP/reaction; corpus `53cc6da80f66d220` |
| randomness | counter-based, keyed `(seed, reaction_index, event)` |
| null | permute the four arm labels **within each seed**, independently per seed; 1000 draws, seeded `sha256("EXP-012d/null/{draw}")` |
| controls | eighteen, all passing before the receipt was written |

## The phases

| seed | BF | BM | FF | FM | seed |
|---|---|---|---|---|---|
| 20260830 | COLL | COLL | COLL | COLL | COLLAPSED |
| 20260831 | COLL | **PROD** | COLL | **PROD** | DISCORDANT |
| 20260832 | COLL | COLL | COLL | COLL | COLLAPSED |
| 20260833 | **PROD** | COLL | **PROD** | COLL | DISCORDANT |
| 20260834 | COLL | COLL | COLL | COLL | COLLAPSED |
| 20260835 | COLL | COLL | COLL | COLL | COLLAPSED |
| 20260836 | **PROD** | COLL | COLL | COLL | DISCORDANT |
| 20260837 | **PROD** | COLL | COLL | **PROD** | DISCORDANT |
| 20260838 | COLL | COLL | COLL | COLL | COLLAPSED |
| 20260839 | COLL | COLL | COLL | COLL | COLLAPSED |
| 20260840 | **PROD** | COLL | **PROD** | COLL | DISCORDANT |
| 20260841 | **PROD** | COLL | **PROD** | COLL | DISCORDANT |

**11 of 48 cells produce; 6 of 12 seeds are discordant.** Discordance replicates —
012c found 4 of 5 — so *something* about the arm reaches the phase. What does not
replicate is which arm.

## XD1 — price drives production: **FAILS**, with the sign reversed

> `#producing(FF ∪ FM) − #producing(BF ∪ BM) ≥ 8` of 24 cells per price level,
> **and** permutation p < 0.05. *Falsifier:* either clause.

Floor arms produce in **5 of 24** cells; Book arms in **6 of 24**. The statistic
is **−1** against a threshold of **+8**, and its one-sided permutation p is
**0.7722** over 1000 draws (two-sided 1.0000; null mean −0.11, null maximum +9).

Both clauses fail, and the first fails in the wrong direction: the Book-priced
arms produced *more* than the floor-priced ones. The null's maximum of +9 shows
the design could have detected the predicted effect — a +8 was reachable by
chance alone in this null, so a real +8 would have been unremarkable, and nothing
near it occurred.

*p is one-sided because the forecast was directional and filed in advance
(`DECISIONS.md` D123); the two-sided value is in the receipt and is worse.*

## XD2 — matter does not drive production: **FAILS**, on a tie, and the falsifier did not fire

> `|#producing(free) − #producing(matter)|` is below the null's 95th percentile.
> *Falsifier:* a null-clearing matter effect on phase.

Free arms produce in **8** cells, matter arms in **3**; the statistic is **5**.
The null's 95th percentile is **5.00**. Five is not *below* five, so the clause as
written is not met and the verdict is **FAILS**.

**This is a tie at an integer boundary and the hypothesis's two halves disagree
about it.** The statistic counts cells, so it is integer-valued and the
percentile of its null lands on an integer too. The falsifier — "a null-clearing
matter effect on phase" — **did not fire**: the observed value's permutation p is
**0.1419**, entirely ordinary under the null. So the scoring clause says FAILS
and the falsifier says the matter axis did nothing detectable. Scored as written,
because a threshold re-read after seeing the data is not a threshold; named here
because the operationalization is defective for an integer statistic, and a
successor should say "at or below" or use the p-value directly.

What this does **not** license, per the preregistration's own list: it is not
evidence that the matter axis is inert everywhere. Nothing here was measured
outside phase, at these settings.

## XD3 — BF strictly lowest: **FAILS**, and BF is the highest

> BF has the strictly lowest producing count of the four arms. *Falsifier:* any
> arm ties or undercuts BF.

| arm | BF | BM | FF | FM |
|---|---:|---:|---:|---:|
| producing (of 12) | **5** | 1 | 3 | 2 |

The margin `min(others) − BF` is **−4**; permutation p **0.9830** over 1000
draws. BF is not the lowest producer — it is the **highest**, by four cells over
the next arm.

In ALIFE-EXP-012c, BF produced in **0 of 5** seeds and was the observation the
whole price story rested on. On twelve fresh seeds it produces in **5 of 12**.
That is the clearest single number in this receipt: the pattern that motivated
the experiment inverted under prospective test.

## XD4 — the `20260827` death-timing signature: **FAILS**, at a coin flip

> Among seeds where a Book-priced and a floor-priced arm both collapse, the
> Book-priced arm's last-eligible index is smaller in ≥ 3 of every 4 such seeds,
> sign-test permutation p < 0.05.

All **12** seeds qualify, above the minimum of 4, so this is adjudicated.

| seed | Book arms' last-eligible (mean) | floor arms' (mean) | earlier |
|---|---|---|---|
| 20260830 | 476, 1439 (958) | 349, 2544 (1446) | book |
| 20260831 | 1069 (1069) | 723 (723) | floor |
| 20260832 | 536, 875 (706) | 1190, 875 (1032) | book |
| 20260833 | 480 (480) | 480 (480) | floor |
| 20260834 | 588, 632 (610) | 484, 632 (558) | floor |
| 20260835 | 429, 510 (470) | 931, 1769 (1350) | book |
| 20260836 | 1925 (1925) | 1445, 1062 (1254) | floor |
| 20260837 | 1132 (1132) | 452 (452) | floor |
| 20260838 | 538, 1326 (932) | 800, 2136 (1468) | book |
| 20260839 | 1276, 2294 (1785) | 1860, 2294 (2077) | book |
| 20260840 | 2018 (2018) | 965 (965) | floor |
| 20260841 | 343 (343) | 2103 (2103) | book |

**Book dies earlier in 6 of 12 = 0.50**, against a required 0.75. The signed
sign-test statistic is **0** — an exact tie — with permutation p **0.4875**.

Seed `20260833` is a tie on the underlying means (480 against 480) and is counted
as "floor earlier" by the strict `<` in the rule; it changes 6/12 to at most
7/12, still short of 9/12.

ALIFE-EXP-012c's seed `20260827` — four arms dead at 706, 706, 1833, 1961, the
Book-priced pair three times earlier — has no counterpart here. It was one seed.

## The mechanism stays quarantined

The preregistration files "the Book price drains ATP the floor price does not,
and drained trajectories converge sooner" as a `HYPOTHESIS`, to become a
candidate for a mediation successor **only if XD1/XD3/XD4 hold**. They do not.
It is not promoted, not narrated, and nothing in this run measured it.

## Controls

Eighteen, all passing before the receipt was written. Sixteen are verbatim from
ALIFE-EXP-012c; C-fresh and C-null are this experiment's.

| | control | outcome |
|---|---|---|
| **C-oracle(start/end)** | the pinned oracle, both ends | `413d1f98…` at `d3f1b512`, no drift across an 1107-second run |
| **C-fresh** | no measurement seed appears in EXP-010/011/012/012b/012c | 12 seeds against 5 forbidden, **0 clashes** |
| **C-fresh(exemption)** | C-compat's EXP-007 seeds contribute no scored cell | disjoint, checked |
| **C-RNG** | counter-based draws survive a perturbed history | **755/755** before, **603/603** after |
| **C-RNG-control** | the same on a positional stream must FAIL | 80/708 |
| **C-compat** | arm BF reproduces EXP-007's frozen receipt | 3 seeds × 13 fields, **0 divergences** |
| **C-eligible** | index log matches the independent counter | 48/48 cells |
| **C-fire(matter/totality)** | `consumed + blocked == eligible R-S`, exactly | all 24 M cells, 0 violations |
| **C-fire(matter/supply)** | ≥ 100 eligible R-S in every PRODUCING M cell | 3 of 24 M cells produce; **0 below the floor** |
| **C-fire(price)** | floor in FF/FM, Book I in BF/BM | 26 925 floor events, 0 violations |
| **C-ledger** | conservation and census totality per tick | 48 cells, 5984 consumed deaths, 3707 waits, 0 failures |
| **C-factorial** | the seed-subset arithmetic is the pilot's | identical on all 12 seeds |
| **C-null** | the permutation preserves each seed's phase multiset and moves the labels | 1784 relabelled cells over 50 draws |
| **C-null(seeding)** | a draw is a function of its index alone | reproducible |
| **C-det** | every cell twice | 0 divergences |
| **C-corpus / C-core** | fingerprint; open-chain peeling | pass |

## Corrections, named rather than absorbed

**A soup can die, and until this run that was a `ValueError` from inside the
RNG** (`DECISIONS.md` D126). The first attempt crashed on `BM/20260836`:
`below() needs n >= 1`, thrown four frames down in `CounterRandom` because the
soup was empty. Diagnosed before anything was changed — the census reached zero
at reaction 1926 (517 culled, 253 consumed, 1086 starved, 134 waiting, none
alive) with the ledger, the census counts and the memory bound all still holding.
Nothing was mis-booked; a matter arm ate its own census faster than settled
reactions replaced it.

Extinction is now an outcome: the run stops there, `extinct_at` enters the
receipt, and the cell is scored on what happened. **Two cells went extinct in
this run** — `BM/20260836` at reaction 1926 and `BM/20260838` at 1327, both
Book-priced matter arms. `window()` follows the same rule, counting only
reactions that ran, because reactions that never happened are not failures.

The guard lives in the shared machinery, so ALIFE-EXP-012c's receipt was
re-recorded and compared field by field: **100 keys added, 0 values changed**.
XC1, XC2 and XC3 stand exactly as scored. This is not a third frame change to
012d; it is the harness learning to survive a state its frame already permitted,
found by running it.

## What this says, and what it does not

- It says the **price does not choose the phase**, on twelve seeds nobody had
  run, against a null that could have detected the predicted effect. Four
  preregistered forecasts, four failures, one of them sign-reversed.
- It does **not** say the arm is irrelevant to the phase. Discordance replicated:
  6 of 12 seeds here, 4 of 5 in 012c. Something about the arm reaches the phase
  and neither axis, scored as preregistered, is it.
- It does **not** rehabilitate 012c's numbers or condemn them. 012c reported that
  pattern and refused to claim it. This is what refusing to claim it was for.
- Nothing here is proved. The census identity, the ledger and the memory bound
  are **checked**, on every tick of 48 cells.

## Limitations

1. Twelve seeds, four arms, one corpus, one budget, one capacity, one phase
   threshold. 11 producing cells is a thin base for any of these statistics, and
   the null's own maximum on XD1 (+9) shows how much room chance had.
2. **The phase is a binary read off one threshold.** No cell here sits near
   reaction 3000, but that is a fact about this run.
3. **XD2's clause is defective for an integer statistic** and this run landed
   exactly on the tie. The verdict is scored as written; a successor should fix
   the wording rather than inherit it.
4. **Two cells did not reach the horizon.** `BM/20260836` and `BM/20260838` went
   extinct at 1926 and 1327. Their phases are computed on the events that
   occurred, which is correct, and they are still cells that ran a third of the
   others' length — a factorial with unequal exposure is not the factorial the
   design assumed.
5. The 012c pattern that motivated this experiment came from five seeds and did
   not survive twelve. That is the finding; it is also a warning about every
   other per-arm count in this repository that has not had the same treatment.
