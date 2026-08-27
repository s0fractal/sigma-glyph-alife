#!/usr/bin/env python3
"""Does food help? Feeding starving agents under the engine's default schedule.

Check-only by default; `--record` writes `results.json` after every control
passes. Judged against
`../ALIFE-EXP-011-does-food-help-preregistration.md`, committed before this file.

THE ENGINE IS NOT TOUCHED. This measures `sigma_alife.Population.step` as it
stands at the commit ChatGPT reviewed, phase order and all. `FeedingPopulation`
below subclasses it to *observe* — and, for the arms the preregistration
defines, to add feeding in `phase_share` and to skip the cull on a fed tick,
which is what `step(cull=False)` means for exactly those ticks. Nothing
overrides a phase in a way that changes what the engine does with an agent; if
it did, the number this experiment reports would be about the harness.
"""
import argparse
import json
import platform
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "impl"))

import corpus as C  # noqa: E402
import sigma_alife as al  # noqa: E402

sg = al.sg


def fresh_store():
    st = sg.Store()
    for b in (sg.I_BYTES, sg.K_BYTES, sg.S_BYTES):
        st.put(b)
    return st


def next_action_price(agent, store, limits=None):
    """What the agent's next priced action costs, without buying it.

    `step5` reads the store and returns a NEW term; it mutates nothing else, so
    asking it on a throwaway `stats` is free — the same counterfactual
    `reduce_slice` already asks itself when a slice ends. Returns None when
    there is no next action to price (a normal form, an unresolved reference, a
    resource fault)."""
    limits = limits or sg.DEFAULT_LIMITS
    try:
        r = sg.step5(agent.term, 10 ** 9, store, dict(agent.stats), limits)
    except (sg.BudgetExhausted, sg.Unresolved, sg.ResourceFault):
        return None
    return None if r is None else r[1]


class FeedingPopulation(al.Population):
    """The engine's population, watched, and fed according to the arm.

    Three hooks, each the smallest that will do:

      * `phase_reduce` — resets the per-tick record. It is the first phase of
        `step`, so this is a tick boundary and nothing else;
      * `phase_share`  — runs the ENGINE's own rebate first (arm (a)'s feeding
        path, untouched), records who received what, then, in the forced arms,
        grants every starving agent its next-action price + 1 out of the
        commons. Both land where the preregistration puts them: after
        `phase_reduce`, before `phase_cull`, in the same tick;
      * `phase_cull`   — records which fed agents the cull takes and how much
        ATP it takes back. In arm (c) it returns without culling on a tick
        where feeding happened, which is `step(cull=False)` for that tick.
    """

    def __init__(self, *args, forced=False, cull_free_when_fed=False, **kw):
        super().__init__(*args, **kw)
        self.forced = forced
        self.cull_free_when_fed = cull_free_when_fed
        self.fed_this_tick = {}          # aid -> granted this tick while starving
        self.events = []                 # the tick-level log
        self.first_feed = {}             # aid -> (tick, spent at that moment)
        self.feed_events = 0
        self.sufficient_events = 0
        self.insufficient_events = 0
        self.granted_to_starving = 0
        self.fed_then_buried_atp = 0
        self.fed_then_buried_collected = 0
        self.fed_then_buried_agents = set()
        self.cull_free_ticks = 0
        self.grant_truncated = 0
        self.conservation_ok = True
        self.bound_ok = True

    # -- tick boundary --------------------------------------------------------
    def phase_reduce(self):
        self.fed_this_tick = {}
        return super().phase_reduce()

    # -- feeding --------------------------------------------------------------
    def phase_share(self):
        starving = sorted((a for a in self.agents if a.status == al.STARVED),
                          key=lambda x: x.aid)
        prices = {a.aid: next_action_price(a, self.store) for a in starving}
        before = {a.aid: a.atp for a in starving}

        granted = super().phase_share()          # the engine's own rebate path

        for a in starving:
            got = a.atp - before[a.aid]
            if got > 0:
                self._record_feed(a, got, prices[a.aid], "rebate")

        if self.forced:
            for a in starving:
                price = prices[a.aid]
                if price is None:
                    # Nothing to buy: no action is available at any budget. Such
                    # an agent is not what H1 is about and is not fed.
                    continue
                want = price + 1
                moved = self.economy.grant(a, want)
                if moved < want:
                    self.grant_truncated += 1
                granted += moved
                self._record_feed(a, moved, price, "forced")
        return granted

    def _record_feed(self, agent, amount, price, how):
        self.feed_events += 1
        self.granted_to_starving += amount
        sufficient = price is not None and agent.atp > price
        if sufficient:
            self.sufficient_events += 1
        else:
            self.insufficient_events += 1
        self.fed_this_tick[agent.aid] = self.fed_this_tick.get(agent.aid, 0) + amount
        if agent.aid not in self.first_feed:
            self.first_feed[agent.aid] = {
                "tick": self.tick, "spent": agent.spent, "how": how,
                "price": price, "sufficient": sufficient,
            }
        self.events.append({
            "tick": self.tick, "phase": "share", "event": "fed", "how": how,
            "agent": agent.aid, "amount": amount, "next_action_price": price,
            "atp_after": agent.atp, "sufficient": sufficient,
        })

    # -- the cull -------------------------------------------------------------
    def phase_cull(self):
        if self.cull_free_when_fed and self.fed_this_tick:
            # `step(cull=False)` for exactly this tick: the fed agents get to
            # reach `phase_reduce` again, which is what H3 asks about.
            self.cull_free_ticks += 1
            self.events.append({"tick": self.tick, "phase": "cull",
                                "event": "cull skipped (fed this tick)",
                                "fed": sorted(self.fed_this_tick)})
            return 0
        doomed = {a.aid: a.atp for a in self.agents if a.status == al.STARVED}
        culled = super().phase_cull()
        for aid, granted in sorted(self.fed_this_tick.items()):
            if aid in doomed:
                self.fed_then_buried_atp += granted
                self.fed_then_buried_collected += doomed[aid]
                self.fed_then_buried_agents.add(aid)
                self.events.append({
                    "tick": self.tick, "phase": "cull",
                    "event": "fed then buried", "agent": aid,
                    "granted_this_tick": granted,
                    "atp_collected": doomed[aid],
                })
        return culled

    def step(self, cull=True):
        m = super().step(cull=cull)
        if not self.economy.check(self.agents):
            self.conservation_ok = False
        if not self.population_bound_holds():
            self.bound_ok = False
        return m


def build_population(arm, budget, seed, entries, store):
    econ = al.Economy(budget * len(entries) + C.COMMONS_RESERVE)
    agents = []
    for e in entries:
        root = al.put_term(e["term"], store)
        a = al.Agent(e["name"], root, 0)
        econ.endow(a, budget)
        agents.append(a)
    return FeedingPopulation(
        store, agents, econ, random.Random(seed),
        slice_atp=C.SLICE_ATP,
        rebate_rate=C.REBATE_RATE if arm == "a" else 0.0,
        transfers=False,
        forced=arm in ("b", "c"),
        cull_free_when_fed=(arm == "c"),
        # THE POINT OF THIS EXPERIMENT. `phase_cull` re-tests starvation as of
        # 2026-08-27 — the fix this receipt is the BEFORE measurement of — so
        # the flag is pinned here, explicitly and forever, to the schedule
        # ALIFE-EXP-011 actually measured. The preregistration says the RESULT
        # is the before and the regression suite is the after, and that neither
        # is edited to meet the other; this line is what makes that true of the
        # code and not only of the prose. DECISIONS.md D98.
        recheck_affordability_before_cull=False,
        # Same reason, second axis: the rebate's "shared" statistic moved from
        # occurrences to distinct holders on 2026-08-27, which changes arm (a)'s
        # grants by two ATP a seed. Pinned to what this receipt measured.
        rebate_basis="occurrences",
    )


# ---------- the dry run: starvation counts only ----------
def dry_run(budget, seed):
    """STARVATION COUNTS ONLY. The preregistration allows this run to observe
    how many agents starve and nothing else, so that is all it returns — no
    survival, no feeding, no ATP. Rebates and forced grants are off, so nothing
    here is a measurement of any arm."""
    store = fresh_store()
    entries = C.build()
    econ = al.Economy(budget * len(entries))
    agents = []
    for e in entries:
        a = al.Agent(e["name"], al.put_term(e["term"], store), 0)
        econ.endow(a, budget)
        agents.append(a)
    pop = al.Population(store, agents, econ, random.Random(seed),
                        slice_atp=C.SLICE_ATP)
    ever = set()
    for _ in range(C.TICKS):
        pop.step(cull=False)
        ever |= {a.aid for a in pop.agents if a.status == al.STARVED}
    return {"budget": budget, "seed": seed,
            "ever_starved": len(ever), "population": len(agents)}


def choose_budget():
    """C.TARGET_STARVED_FRACTION, by the rule fixed in `corpus.py` before this
    ran. Reads an ever-starved count and nothing else."""
    rows = []
    for b in C.BUDGET_SWEEP:
        counts = [dry_run(b, s) for s in C.SEEDS]
        frac = sum(r["ever_starved"] for r in counts) / sum(
            r["population"] for r in counts)
        rows.append({"budget": b, "ever_starved_fraction": frac,
                     "per_seed": [r["ever_starved"] for r in counts]})
    best = min(rows, key=lambda r: (abs(r["ever_starved_fraction"]
                                        - C.TARGET_STARVED_FRACTION),
                                    r["budget"]))
    return best["budget"], rows


# ---------- the measurement ----------
def run_arm(arm, budget, seed, keep_events=False):
    store = fresh_store()
    entries = C.build()
    pop = build_population(arm, budget, seed, entries, store)
    for _ in range(C.TICKS):
        pop.step(cull=True)

    by_aid = {a.aid: a for a in pop.agents}
    buckets = {"survivor_fired": [], "archived_same_tick": [],
               "archived_later_without_firing": [], "settled": [],
               "waiting": [], "unclassified": []}
    sufficient_fed = []
    for aid, rec in sorted(pop.first_feed.items()):
        a = by_aid[aid]
        fired = a.spent > rec["spent"]
        if rec["sufficient"]:
            sufficient_fed.append(aid)
        if fired:
            buckets["survivor_fired"].append(aid)
        elif a.status == al.ARCHIVED and aid in pop.fed_then_buried_agents:
            buckets["archived_same_tick"].append(aid)
        elif a.status == al.ARCHIVED:
            buckets["archived_later_without_firing"].append(aid)
        elif a.status == al.NORMAL:
            buckets["settled"].append(aid)
        elif a.status == al.UNRESOLVED:
            buckets["waiting"].append(aid)
        else:
            buckets["unclassified"].append(aid)

    fed = sorted(pop.first_feed)
    fired_sufficient = [aid for aid in sufficient_fed
                        if aid in set(buckets["survivor_fired"])]
    # H3's `resumption_bound` clause: a resumed agent lands on the whole-run
    # answer. Checked for every fed agent that settled, against the oracle.
    answers_checked = answers_matching = 0
    for aid in buckets["survivor_fired"]:
        a = by_aid[aid]
        if a.status != al.NORMAL:
            continue
        ref, _ = sg.eval_hash(a.root, C.ORACLE_BUDGET, store)
        answers_checked += 1
        answers_matching += sg.term_hash(ref) == a.hash

    return {
        "arm": arm, "arm_label": C.ARM_LABELS[arm], "budget": budget,
        "seed": seed, "ticks": C.TICKS, "population": len(pop.agents),
        "fed_agents": len(fed),
        "fed_agents_sufficiently": len(sufficient_fed),
        "feed_events": pop.feed_events,
        "feed_events_sufficient": pop.sufficient_events,
        "feed_events_insufficient": pop.insufficient_events,
        "grant_truncated": pop.grant_truncated,
        "fed_then_buried_agents": len(pop.fed_then_buried_agents),
        "granted_to_starving": pop.granted_to_starving,
        "fed_then_buried_atp": pop.fed_then_buried_atp,
        "fed_then_buried_collected": pop.fed_then_buried_collected,
        "leak_share": (pop.fed_then_buried_atp / pop.granted_to_starving
                       if pop.granted_to_starving else 0.0),
        "survivors_fired": len(buckets["survivor_fired"]),
        "survival_rate": (len(buckets["survivor_fired"]) / len(fed)
                          if fed else None),
        "survival_rate_sufficient": (len(fired_sufficient) / len(sufficient_fed)
                                     if sufficient_fed else None),
        "buckets": {k: len(v) for k, v in buckets.items()},
        "bucket_ids": {k: v for k, v in buckets.items()},
        "cull_free_ticks": pop.cull_free_ticks,
        "answers_checked": answers_checked,
        "answers_matching": answers_matching,
        "conservation_ok": pop.conservation_ok,
        "bound_ok": pop.bound_ok,
        "atp_pool": pop.economy.pool,
        "atp_endowment": pop.economy.endowment,
        "archived": sum(1 for a in pop.agents if a.status == al.ARCHIVED),
        "settled_total": sum(1 for a in pop.agents if a.status == al.NORMAL),
        "events": pop.events if keep_events else None,
        "event_count": len(pop.events),
    }


# ---------- controls ----------
def controls(budget):
    out = []
    runs = {arm: {s: run_arm(arm, budget, s) for s in C.SEEDS} for arm in C.ARMS}
    flat = [r for cells in runs.values() for r in cells.values()]

    out.append((f"C4 the corpus is ALIFE-EXP-001's, fingerprint "
                f"{C.fingerprint()}",
                C.fingerprint() == C.INHERITED_FINGERPRINT))

    bad = [f"{r['arm']}/{r['seed']}" for r in flat
           if not r["conservation_ok"] or not r["bound_ok"]]
    out.append((f"C1 ATP conservation and the population memory bound held on "
                f"every tick of every arm ({len(bad)} failures; the engine's "
                f"own asserts are on as well)", not bad))

    # C2 — fail-closed on the forced arms.
    ins = sum(runs[a][s]["feed_events_insufficient"]
              for a in ("b", "c") for s in C.SEEDS)
    trunc = sum(runs[a][s]["grant_truncated"]
                for a in ("b", "c") for s in C.SEEDS)
    events = sum(runs[a][s]["feed_events"] for a in ("b", "c") for s in C.SEEDS)
    out.append((f"C2 the feeding is real: all {events} forced grants left the "
                f"agent's ATP strictly above its next-action price "
                f"({ins} insufficient, {trunc} truncated by the commons)",
                events > 0 and ins == 0 and trunc == 0))

    det = []
    for arm in C.ARMS:
        for s in C.SEEDS:
            again = run_arm(arm, budget, s)
            if again != runs[arm][s]:
                det.append(f"{arm}/{s}")
    out.append((f"C3 every arm x seed run twice gives an identical receipt "
                f"({len(det)} divergences)", not det))

    unc = sum(r["buckets"]["unclassified"] for r in flat)
    recon = [f"{r['arm']}/{r['seed']}" for r in flat
             if sum(r["buckets"].values()) != r["fed_agents"]]
    out.append((f"C5 status accounting is total: every fed agent ends as "
                f"exactly one of survivor-that-fired, archived-same-tick, "
                f"archived-later-without-firing, settled or waiting "
                f"({unc} unclassified, {len(recon)} reconciliation failures)",
                unc == 0 and not recon))
    return all(ok for _, ok in out), out, runs


# ---------- scoring ----------
def score(runs):
    h1_fed = sum(runs[arm][s]["fed_agents"] for arm in ("a", "b") for s in C.SEEDS)
    h1_fired = sum(runs[arm][s]["survivors_fired"]
                   for arm in ("a", "b") for s in C.SEEDS)
    h1_fed_suff = sum(runs[arm][s]["fed_agents_sufficiently"]
                      for arm in ("a", "b") for s in C.SEEDS)
    h1_fired_suff = 0
    for arm in ("a", "b"):
        for s in C.SEEDS:
            r = runs[arm][s]
            suff = r["survival_rate_sufficient"]
            if suff is not None:
                h1_fired_suff += round(suff * r["fed_agents_sufficiently"])

    granted = sum(runs[arm][s]["granted_to_starving"]
                  for arm in ("a", "b") for s in C.SEEDS)
    buried = sum(runs[arm][s]["fed_then_buried_atp"]
                 for arm in ("a", "b") for s in C.SEEDS)
    leak = buried / granted if granted else 0.0

    c_fed = sum(runs["c"][s]["fed_agents"] for s in C.SEEDS)
    c_fired = sum(runs["c"][s]["survivors_fired"] for s in C.SEEDS)
    h3 = c_fired / c_fed if c_fed else None

    h1_rate = h1_fired_suff / h1_fed_suff if h1_fed_suff else None
    return {
        "H1": {"claim": "a starving agent fed sufficiently in the same tick, "
                        "under step(cull=True), fires >= 1 further action",
               "arms": ["a", "b"],
               "fed_agents": h1_fed, "fed_sufficiently": h1_fed_suff,
               "fired_after_feeding": h1_fired,
               "fired_after_sufficient_feeding": h1_fired_suff,
               "survival_rate": h1_rate,
               "preregistered_expectation": C.H1_EXPECTED,
               "verdict": ("FALSE" if h1_rate == 0.0
                           else "TRUE" if h1_rate else "UNADJUDICATED"),
               "per_arm": {arm: {str(s): {
                   "fed": runs[arm][s]["fed_agents"],
                   "fed_sufficiently": runs[arm][s]["fed_agents_sufficiently"],
                   "fired": runs[arm][s]["survivors_fired"],
                   "rate_sufficient": runs[arm][s]["survival_rate_sufficient"],
               } for s in C.SEEDS} for arm in ("a", "b")}},
        "H2": {"claim": "fed-then-buried ATP exceeds 10% of ATP granted to "
                        "starving agents",
               "granted_to_starving": granted, "fed_then_buried_atp": buried,
               "leak_share": leak, "threshold": C.H2_LEAK_THRESHOLD,
               "verdict": "HOLDS" if leak > C.H2_LEAK_THRESHOLD else "FAILS",
               "per_arm": {arm: {str(s): {
                   "granted": runs[arm][s]["granted_to_starving"],
                   "buried": runs[arm][s]["fed_then_buried_atp"],
                   "collected": runs[arm][s]["fed_then_buried_collected"],
                   "share": runs[arm][s]["leak_share"],
               } for s in C.SEEDS} for arm in ("a", "b")}},
        "H3": {"claim": "the same feeding with a cull-free window yields 100% "
                        "survival",
               "arm": "c", "fed_agents": c_fed, "fired_after_feeding": c_fired,
               "survival_rate": h3, "preregistered_expectation": C.H3_EXPECTED,
               "verdict": "HOLDS" if h3 == 1.0 else "FAILS",
               "answers_checked": sum(runs["c"][s]["answers_checked"]
                                      for s in C.SEEDS),
               "answers_matching": sum(runs["c"][s]["answers_matching"]
                                       for s in C.SEEDS),
               "per_seed": {str(s): {"fed": runs["c"][s]["fed_agents"],
                                     "fired": runs["c"][s]["survivors_fired"],
                                     "rate": runs["c"][s]["survival_rate"],
                                     "cull_free_ticks": runs["c"][s]["cull_free_ticks"]}
                            for s in C.SEEDS}},
    }


def summarize(result):
    runs, sc = result["runs"], result["scores"]
    print(f"{'arm':>4s} {'seed':>10s} {'fed':>5s} {'suff':>5s} "
          f"{'fired':>6s} {'rate':>7s} {'granted':>9s} {'buried':>8s} "
          f"{'leak':>7s} {'archived':>9s} {'settled':>8s}")
    for arm in C.ARMS:
        for s in C.SEEDS:
            r = runs[arm][str(s)]
            rate = r["survival_rate_sufficient"]
            print(f"{arm:>4s} {s:>10d} {r['fed_agents']:>5d} "
                  f"{r['fed_agents_sufficiently']:>5d} "
                  f"{r['survivors_fired']:>6d} "
                  f"{('n/a' if rate is None else f'{rate:.1%}'):>7s} "
                  f"{r['granted_to_starving']:>9d} "
                  f"{r['fed_then_buried_atp']:>8d} "
                  f"{r['leak_share']:>6.1%} {r['archived']:>9d} "
                  f"{r['settled_total']:>8d}")

    h1, h2, h3 = sc["H1"], sc["H2"], sc["H3"]
    h1_rate = h1["survival_rate"]
    h1_txt = "n/a" if h1_rate is None else f"{h1_rate:.1%}"
    print("\nH1 (a fed starving agent fires a further action, "
          "step(cull=True), arms a+b)")
    print(f"   {h1['fired_after_sufficient_feeding']} of "
          f"{h1['fed_sufficiently']} sufficiently-fed agents ever fired again "
          f"-> survival rate {h1_txt}")
    print(f"   preregistered expectation: FALSE at exactly "
          f"{C.H1_EXPECTED:.0%} -> H1 is {h1['verdict']}")

    print(f"\nH2 (fed-then-buried ATP > {C.H2_LEAK_THRESHOLD:.0%} of ATP "
          f"granted to starving agents, arms a+b)")
    print(f"   {h2['fed_then_buried_atp']} of {h2['granted_to_starving']} "
          f"= {h2['leak_share']:.1%} -> {h2['verdict']}")

    h3_rate = h3["survival_rate"]
    h3_txt = "n/a" if h3_rate is None else f"{h3_rate:.1%}"
    print("\nH3 (the same feeding with a cull-free window, arm c)")
    print(f"   {h3['fired_after_feeding']} of {h3['fed_agents']} fed agents "
          f"fired again -> {h3_txt} -> {h3['verdict']}")
    print(f"   {h3['answers_matching']}/{h3['answers_checked']} settled "
          f"survivors landed on the oracle's whole-run answer")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--record", action="store_true")
    ap.add_argument("--controls", action="store_true")
    ap.add_argument("--dry-run", action="store_true",
                    help="starvation counts only, for the budget choice")
    args = ap.parse_args()

    C.build()
    budget, sweep = choose_budget()
    if args.dry_run:
        print(f"{'budget':>7s} {'ever starved':>13s} {'fraction':>9s}   per seed")
        for row in sweep:
            print(f"{row['budget']:>7d} "
                  f"{sum(row['per_seed']):>13d} "
                  f"{row['ever_starved_fraction']:>8.1%}   {row['per_seed']}")
        print(f"\nchosen: {budget} ATP/agent (closest to "
              f"{C.TARGET_STARVED_FRACTION:.0%})")
        return 0

    ok, results, runs = controls(budget)
    for name, passed in results:
        print(("OK  " if passed else "FAIL"), name)
    if not ok:
        print("\nALIFE-EXP-011: CONTROLS FAILED - nothing measured, "
              "nothing recorded")
        return 1
    if args.controls:
        print("\nEXP-011-CONTROLS: ALL PASS")
        return 0

    worked = run_arm("b", budget, C.WORKED_EXAMPLE_SEED, keep_events=True)
    result = {
        "runs": {arm: {str(s): runs[arm][s] for s in C.SEEDS}
                 for arm in C.ARMS},
        "scores": score(runs),
        "worked_example": {"arm": "b", "seed": C.WORKED_EXAMPLE_SEED,
                           "events": worked["events"]},
    }
    print()
    summarize(result)

    prov = al.provenance()
    receipt = {
        "experiment": "ALIFE-EXP-011",
        "corpus_fingerprint": C.fingerprint(),
        "inherited_from": "ALIFE-EXP-001",
        "frame": {"arms": list(C.ARMS), "arm_labels": C.ARM_LABELS,
                  "seeds": list(C.SEEDS), "ticks": C.TICKS,
                  "slice_atp": C.SLICE_ATP,
                  "atp_per_agent": budget,
                  "budget_sweep": list(C.BUDGET_SWEEP),
                  "target_starved_fraction": C.TARGET_STARVED_FRACTION,
                  "budget_selection": sweep,
                  "commons_reserve": C.COMMONS_RESERVE,
                  "rebate_rate_arm_a": C.REBATE_RATE,
                  "h1_expected": C.H1_EXPECTED,
                  "h2_leak_threshold": C.H2_LEAK_THRESHOLD,
                  "h3_expected": C.H3_EXPECTED,
                  "worked_example_seed": C.WORKED_EXAMPLE_SEED,
                  "recheck_affordability_before_cull": False,
                  "rebate_basis": "occurrences"},
        "provenance": {
            "sigma_alife_version": prov["sigma_alife_version"],
            "sigma_glyph_requirement": prov["sigma_glyph_requirement"],
            "oracle_sha256": prov["oracle_sha256"],
            "python": ".".join(prov["python"].split(".")[:2]),
            "platform": platform.python_implementation(),
        },
        "controls": {name: passed for name, passed in results},
        "result": result,
    }
    print(f"\noracle: {prov['oracle_source']}  "
          f"(sha256 {prov['oracle_sha256'][:16]}...)")
    if args.record:
        (HERE / "results.json").write_text(
            json.dumps(receipt, indent=2, sort_keys=True) + "\n")
        print(f"recorded {HERE / 'results.json'}")
    else:
        print("\n(check-only; pass --record to write results.json)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
