# ALIFE-EXP-011 — does food help? Feeding the starving under the default schedule

**Preregistration. No measurement has been taken.** Non-normative. Written
**before** any engine change: the phenomenon is measured on the engine as it
stands at `reviews/chatgpt-2026-08-27.md`'s reviewed commit, and only after
the RESULT is committed may a fix land, carrying the regression tests below.
Measuring first is the point — a bug fixed before it is measured becomes an
anecdote; measured, it becomes a number about what the default schedule
costs.

## Why this experiment exists

The repository's tagline is "digital agents that run out of food without
dying". ChatGPT's review of `006b9bb` (recorded verbatim in `reviews/`)
found, and this author verified by code reading before committing it, that
under the default `step(cull=True)` schedule the tagline's second half is
conditional in a way nothing documents: `phase_share`/`phase_interact` can
grant ATP to a `STARVED` agent (it is `RUNNABLE`), neither `Economy.grant`
nor `conservative_transfer` changes its status, and `phase_cull` — running
*after* both, in the same tick — collects the newly granted ATP and archives
the agent. The randomized conservation suite cannot see this: it checks the
ledger, the bound, dust and determinism, and "a refed starving agent gets to
run" is none of those.

`H-FOOD` (the review's phrasing, kept): **їжа допомагає не померти** — food
helps not to die. Operationalized below so it can lose.

## Hypotheses

- **H1 (same-tick feeding, the review's scenario).** An agent that starves
  during `phase_reduce` of tick T and receives ATP sufficient for its next
  action during `phase_share` or `phase_interact` of the same tick T, under
  the default `step(cull=True)`, **fires at least one further priced
  action** in any later tick. *Preregistered expectation, attributed to the
  review's analysis and this author's verification: H1 is FALSE with
  survival rate exactly 0% — every such agent is archived in tick T and its
  granted ATP is collected the same tick.* Falsifier: any such agent
  survives to fire an action.
- **H2 (the cost, measured not asserted).** Over the pinned scenarios, the
  ATP granted to starving agents and collected by cull **in the same tick**
  ("fed-then-buried ATP") exceeds **10%** of all ATP ever granted to
  starving agents. Falsifier: ≤ 10% — the leak exists but is marginal at
  these settings.
- **H3 (the escape hatch is real).** The same feeding, applied in a tick
  where `cull` is skipped (`step(cull=False)`) before the agent's next
  `phase_reduce`, yields survival rate **100%**: the agent resumes and, per
  `resumption_bound`, lands on the whole-run answer. Falsifier: any fed
  agent with a cull-free window fails to resume, which would mean the bug
  is deeper than phase order.

## Design

- **Corpus:** ALIFE-EXP-001's, fingerprint `53cc6da80f66d220` (C-corpus).
- **Scenarios, pinned:** budgets chosen so that a preregistered fraction of
  agents starve mid-run (the harness author picks the exact budget from a
  dry run and records it in the RESULT's provenance *before* measuring the
  hypotheses; the dry run may observe starvation counts only, no survival
  statistics). Feeding via the existing `phase_share` path where it fires
  naturally, and via one forced-grant arm (a direct `Economy.grant` to
  every starving agent of exactly its next-action price + 1) so H1 is
  adjudicated on guaranteed-sufficient feeding, not on the economy's mood.
- **Arms:** (a) default schedule, natural sharing; (b) default schedule,
  forced grants; (c) forced grants with a one-tick cull-free window (H3).
- **Seeds, pinned:** `20260825`, `20260826`, `20260827`.
- **Measured:** per arm and seed — starving agents fed; fed-then-buried
  same tick; survivors firing ≥ 1 action; fed-then-buried ATP as a share of
  granted-to-starving ATP; and the tick-level event log for one seed as a
  worked example.

## Controls

1. **C1 — conservation and the population bound** hold every tick in every
   arm (existing asserts stay on).
2. **C2 — the feeding is real.** In arms (b) and (c) every starving agent's
   post-grant ATP strictly exceeds its next-action price; fail-closed if
   any grant was insufficient (the EXP-002 lesson: a mechanism that never
   fires adjudicates nothing).
3. **C3 — determinism.** Each arm, each seed, run twice: identical
   receipts.
4. **C4 — the corpus is EXP-001's**, by fingerprint.
5. **C5 — status accounting is total.** Every fed agent ends the run as
   exactly one of: survivor-that-fired, archived-same-tick,
   archived-later-without-firing, settled, waiting; counts reconcile.

## After the RESULT, and only after

The fix (whatever form it takes — reviving grants, cull exempting
fed-this-tick agents, or a reordered schedule — the fixer's choice,
recorded in `DECISIONS.md`) must land with the review's regression tests,
verbatim in spirit:

```text
starve A → transfer enough for next action → step(cull=True)
→ ASSERT A is not ARCHIVED
→ ASSERT spent increased or A reached another legitimate state
```

and the same for the rebate path. The EXP-011 RESULT is then the *before*
measurement; the regression suite is the *after*; neither is edited to meet
the other.

## What would make this experiment worthless

- Fixing the engine first. The measurement is of the reviewed commit's
  behavior.
- Reporting arm (a) survival without C2's sufficiency check.
- Any claim that H3's 100% validates the economy — it validates
  `resumption_bound`'s machinery, which EXP-006 already measured; here it
  is a control-by-contrast, not a finding.
- Silence about the tagline. If H1 is false as expected, the RESULT's
  abstract must say plainly: under the default schedule, the tagline held
  only for agents nobody tried to feed.

## Provenance and the open slot

Preregistration by Claude Fable 5, who will not write the harness (the
ALIFE-EXP-005 arrangement). The review's author (ChatGPT) has one
prediction standing above by construction — H1-is-false — attributed to the
review; further voices may file dated addenda until the harness first runs.
