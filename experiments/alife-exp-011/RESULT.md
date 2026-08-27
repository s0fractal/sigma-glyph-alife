# ALIFE-EXP-011 — result

Judged against [`ALIFE-EXP-011-does-food-help-preregistration.md`](../ALIFE-EXP-011-does-food-help-preregistration.md),
committed at `a1ef892` before this harness existed and written by an author who
did not write it. The choices that document left open are `DECISIONS.md`
D92–D97, committed before the receipt. Founders are ALIFE-EXP-001's, pinned at
`53cc6da80f66d220`. **Measured on the engine as it stands** — no fix had landed
when these numbers were taken, which is the whole design.

**Provenance, stated at its real strength.** The preregistration was written by
Claude Fable 5 and this harness by Claude Opus 5, working only from the committed
document, the repository and its dependencies, and this is the ALIFE-EXP-005
arrangement — a real separation of roles between different models, not an
independent registry, external review, or statistical replication. One
prediction stood above the harness by construction and is attributed to the
review that made it: **ChatGPT**, in
[`reviews/chatgpt-2026-08-27.md`](../../reviews/chatgpt-2026-08-27.md),
predicted H1 false. It is false, at exactly the rate predicted.

## The abstract

**Under the default `step(cull=True)` schedule, the tagline held only for agents
nobody tried to feed.** An agent that starves in `phase_reduce` and is given
enough ATP for its next action in `phase_share` of the same tick is archived by
`phase_cull` in that same tick, and the ATP is collected back into the commons —
**0 of 168** sufficiently-fed agents ever fired another action, and **1056 of
1056** ATP granted to starving agents was buried with them. Skip the cull for
the tick in which the feeding happens and the same agents resume at a rate of
**100%**, 22 more of the 64 reach a normal form, and every one of them lands on
the answer the oracle gives for an uninterrupted run.

| | |
| --- | --- |
| substrate | `impl/sigma_alife.py` 0.1.0 on Σ-GLYPH Book I, oracle sha256 `413d1f9805cdbdf42f13d967a17be26eb959c692eeb067e7146203ed9cebe64d` |
| corpus | ALIFE-EXP-001's 64 terms, fingerprint `53cc6da80f66d220` |
| **budget** | **32 ATP per agent**, from a dry run reading starvation counts only (below) |
| arms | (a) default schedule, natural sharing; (b) default schedule, forced grants; (c) forced grants, cull-free window |
| seeds | `20260825`, `20260826`, `20260827` — pinned, and inert here (see Limitations 1) |
| schedule | 24 ticks, slice 32, `step(cull=True)` in every arm; arm (c) skips the cull on a tick where feeding happened |
| controls | five, all passing before any number was recorded |
| receipt | `results.json`, identical on a second run of every arm × seed |

### The budget, fixed before the hypotheses were measured

The preregistration delegates the budget and permits the dry run to observe
**starvation counts only**. The sweep and the selection rule were fixed in
`corpus.py` first (D92): take the budget whose ever-starved fraction is closest
to 0.50, ties toward the smaller. `measure.py --dry-run` prints starvation counts
and nothing else:

| ATP/agent | 8 | 12 | 16 | 24 | **32** | 48 | 64 | 96 | 128 | 256 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ever starved | 85.9% | 85.9% | 75.0% | 56.2% | **46.9%** | 26.6% | 15.6% | 12.5% | 6.2% | 0.0% |

## The measurement

| arm | seed | fed | sufficiently | fired again | survival | ATP granted to starving | fed-then-buried | leak | archived | settled |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| a | 20260825 | 28 | 26 | **0** | **0.0%** | 243 | 243 | **100%** | 30 | 34 |
| a | 20260826 | 28 | 26 | **0** | **0.0%** | 243 | 243 | **100%** | 30 | 34 |
| a | 20260827 | 28 | 26 | **0** | **0.0%** | 243 | 243 | **100%** | 30 | 34 |
| b | 20260825 | 30 | 30 | **0** | **0.0%** | 109 | 109 | **100%** | 30 | 34 |
| b | 20260826 | 30 | 30 | **0** | **0.0%** | 109 | 109 | **100%** | 30 | 34 |
| b | 20260827 | 30 | 30 | **0** | **0.0%** | 109 | 109 | **100%** | 30 | 34 |
| c | 20260825 | 30 | 30 | **30** | **100%** | 1136 | 0 | 0% | **0** | **56** |
| c | 20260826 | 30 | 30 | **30** | **100%** | 1136 | 0 | 0% | **0** | **56** |
| c | 20260827 | 30 | 30 | **30** | **100%** | 1136 | 0 | 0% | **0** | **56** |

## The hypotheses, scored

### H1 — a fed starving agent fires a further action: **FALSE**, at exactly 0%

> An agent that starves during `phase_reduce` of tick T and receives ATP
> sufficient for its next action during `phase_share` or `phase_interact` of the
> same tick T, under the default `step(cull=True)`, **fires at least one further
> priced action in any later tick.** *Preregistered expectation: H1 is FALSE
> with survival rate exactly 0%.*

**0 of 168** sufficiently-fed agents across arms (a) and (b), all three seeds.
Survival rate **0.0%**, which is the preregistered expectation to the digit.
The falsifier — *any* such agent surviving to fire an action — did not occur
once.

| arm | fed | fed **sufficiently** | fired again | rate |
|---|---:|---:|---:|---:|
| (a) natural sharing | 84 | 78 | 0 | 0.0% |
| (b) forced grants | 90 | 90 | 0 | 0.0% |

**Arm (a)'s sufficiency check, which the preregistration requires before this
number may be reported.** Of arm (a)'s 84 natural rebate events, **78 left the
agent's ATP strictly above its next-action price and 6 did not**. The rate above
is over the 78. Reporting arm (a)'s 0% without that split would have been
scoring the engine's generosity, not its schedule — the preregistration lists
exactly that as something that would make this experiment worthless.

**Attribution.** H1-is-false was predicted by ChatGPT's review before any harness
existed, from a code reading of `phase_share` / `phase_cull`, and verified by
the preregistration's author before the preregistration was committed. This
receipt is the number, not the discovery.

**The mechanism, from the worked example** (arm (b), seed `20260825`, the full
60-event log is in the receipt). Everything happens in **tick 0**:

| tick | phase | event |
|---|---|---|
| 0 | reduce | 30 agents exhaust their reservoir → `STARVED` |
| 0 | share | each is granted its next-action price + 1 — e.g. `church-00`: price 3, granted 4, ATP after 5 |
| 0 | cull | `STARVED` is still `STARVED`: `Economy.collect` takes the 5 back and the agent becomes `ARCHIVED` |

Neither `Economy.grant` nor `conservative_transfer` changes a status, and
`STARVED` is in `RUNNABLE`, so the agent is simultaneously *eligible for food*
and *eligible for burial*, in that order, inside one tick. The status bucket
counts say it without commentary: of the fed agents, **28/28 in arm (a) and
30/30 in arm (b) are `archived-same-tick`**; `survivor-fired`,
`archived-later-without-firing`, `settled` and `waiting` are all zero.

### H2 — the cost: **HOLDS**, and the threshold was three decimal places too generous

> Fed-then-buried ATP exceeds **10%** of all ATP ever granted to starving agents.
> *Falsifier:* ≤ 10% — the leak exists but is marginal at these settings.

**1056 of 1056 ATP = 100.0%.** Not a tenth. All of it.

| arm | granted to starving | buried the same tick | share |
|---|---:|---:|---:|
| (a) natural sharing | 729 | 729 | 100% |
| (b) forced grants | 327 | 327 | 100% |

The threshold was written to let a marginal leak fail the hypothesis. There is
no margin: at this budget every ATP that reaches a starving agent reaches it in
a tick that also buries it, because the agents that starve here starve in tick 0
and are fed and culled before they ever run again. The `atp_collected` figures in
the receipt are larger than the granted ones (the cull also takes the residual
dust the agent was starved with), so 100% is the conservative reading of the
leak, not the flattering one.

### H3 — the escape hatch is real: **HOLDS**, at 100%

> The same feeding, applied in a tick where cull is skipped, yields survival rate
> **100%**: the agent resumes and, per `resumption_bound`, lands on the whole-run
> answer.

**90 of 90 fed agents fired again — 100.0%.** And **66 of 66** of those that
settled reached the hash `sigma_glyph.eval_hash` returns for an uninterrupted
evaluation of the same root.

The contrast is the number worth carrying: with the cull-free window, **56 of 64
agents reach a normal form against 34** under the default schedule, and **0 are
archived against 30**. Twenty-two agents' worth of finished work is the difference
between feeding them and feeding them where the schedule can hear it.

**This does not validate the economy**, and the preregistration says so in
advance. It validates `resumption_bound`'s machinery, which ALIFE-EXP-006 already
measured. Here it is a control by contrast: it establishes that the failure in
H1 is the phase order and not something deeper, because the identical grants to
the identical agents work perfectly the moment the cull is not standing behind
them.

## Controls

Five, all passing before the receipt was written.

| | control | outcome |
|---|---|---|
| **C1** | conservation and the population bound, every tick, every arm | 0 failures across 9 runs; the engine's own asserts were on as well |
| **C2** | the feeding is real — fail-closed | all **1050** forced grants left the agent's ATP strictly above its next-action price; 0 insufficient, 0 truncated by the commons |
| **C3** | determinism | every arm × seed run twice, 0 divergences |
| **C4** | the corpus is EXP-001's | `53cc6da80f66d220` |
| **C5** | status accounting is total | every fed agent in exactly one bucket; 0 unclassified, 0 reconciliation failures |

C2 is the one that earned its place, for the reason the preregistration gives:
ALIFE-EXP-002's memo fired once on a corpus that never asked for it and
adjudicated nothing. An experiment about food where the food was never enough
would have produced the same 0% and meant nothing at all. It was enough 1050
times out of 1050.

## What this says, and what it does not

- It does **not** say the tagline is false. `STARVED` really does preserve a
  body, and ALIFE-EXP-006 and ALIFE-EXP-009 really did resume starved agents.
  It says the resumption story is **conditional on a schedule nothing
  documented**: under `step(cull=True)`, the body survives exactly as long as
  nobody feeds it, because feeding it is what puts ATP in the reservoir the cull
  then collects. Every prior experiment in this repository that measured
  resumption ran with `cull=False`, including ALIFE-EXP-001, which is why seven
  receipts sit on top of this path without touching it.
- It does **not** say the leak is expensive in absolute terms. 1056 ATP out of a
  202 048-ATP economy is nothing. What it costs is **agents**: 30 of 64, in
  tick 0, every run.
- It says nothing about which fix is right. The preregistration leaves that to
  the fixer and this receipt is deliberately the *before* measurement; the
  regression suite that lands with the fix is the *after*, and neither is edited
  to meet the other.
- Nothing here is proved. `resumption_bound` and `population_peak_size` are
  proved (`proofs/README.md`); that a fed agent survives a cull is a property of
  a **policy**, and this receipt is the first thing in the repository to check
  it.

## Limitations

1. **The three seeds cannot differ, and reporting them as three samples would be
   a lie** (D96). `Population` draws on its RNG in exactly two places:
   `phase_interact`'s pairing and `crossover`. Transfers are off and nothing
   reproduces, so all three seeds return byte-identical numbers in every arm.
   They are pinned by the preregistration, run, and reported — as one sample
   printed three times.
2. One budget, one corpus, 24 ticks, 64 agents. At 32 ATP/agent the starvation
   is concentrated in tick 0; a budget where agents starve late would spread the
   same leak over a run and might not produce a 100% same-tick burial.
3. Arm (a)'s rebate rate of 1.0 is chosen to be generous (D94), so arm (a)
   measures what the schedule does to a well-funded rebate, not what the rebate
   would do at a rate somebody had tuned.
4. `transfers` is off in every arm, so `phase_interact` — the second feeding
   path the review names — is not exercised here at all. The regression suite
   that lands with the fix must cover it, and the preregistration says so.
5. Arm (c) skips the cull on **every** tick, because feeding happens on every
   tick (24 of 24). It is a cull-free arm in practice, not a one-tick window
   applied once, and the 56-of-64 settlement figure should be read as "what this
   colony does when nothing culls it", not as a proposed fix.
