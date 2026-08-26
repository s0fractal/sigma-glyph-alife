#!/usr/bin/env python3
"""ADDENDUM to ALIFE-EXP-008 — does self-maintenance appear at ten times the scale?

POST HOC, not preregistered, and written for a specific reason: EXP-008's H3
("what persists is cheap") was reported UNADJUDICATED because no self-maintaining
set survived the locality-preserving null, so there was nothing to price. That is
the one verdict in this repository where more machine buys something real — not
because the earlier runs were resource-limited (peak RSS was 25 MB) but because
1000 reactions may simply be too short a run for a population to organise in.

So: ten times the reactions, four times the seeds, run in parallel. If a set
survives the strong null at this scale, H3 becomes adjudicable and is priced. If
none does, "we did not see it in 1000 reactions" becomes "we did not see it in
10,000 across twelve seeds", which is a different and stronger statement.

Everything else is EXP-008's, unchanged: the same chemistry, the same definition
of a self-maintaining set, the same two chance models sampled twenty times.
"""
import argparse
import json
import multiprocessing as mp
import platform
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "impl"))

import corpus as C  # noqa: E402
import measure as M  # noqa: E402  — the same runner, the same peeling
import sigma_alife as al  # noqa: E402

REACTIONS = 10_000
SEEDS = tuple(20260825 + i for i in range(12))
BUDGET = C.ATP_PER_REACTION            # the primary, blind-chosen level
WINDOWS = (250, 500, 1000, 2000, 4000, 6000, 10_000)
NULL_DRAWS = 20


HORIZONS = (1000, 2000, 4000, 10_000)


def one_cell(seed):
    # The RNG stream is deterministic, so a shorter run is exactly the prefix of a
    # longer one: running at increasing horizons gives the trajectory for free and
    # needs no instrumentation inside the runner.
    trajectory = []
    for h in HORIZONS[:-1]:
        r = M.run_soup(BUDGET, seed, reactions=h)
        trajectory.append({"reactions": h, "alive": len(r["alive"]),
                           "ok": r["ok"], "success_rate": r["ok"] / h})
    run = M.run_soup(BUDGET, seed, reactions=REACTIONS)
    trajectory.append({"reactions": REACTIONS, "alive": len(run["alive"]),
                       "ok": run["ok"], "success_rate": run["ok"] / REACTIONS})
    edges, alive, total = run["edges"], run["alive"], REACTIONS
    curve = {}
    for w in WINDOWS:
        obs = M.self_maintaining(edges, alive, w, total)
        full, local = [], []
        for d in range(NULL_DRAWS):
            full.append(len(M.self_maintaining(
                M.shuffle_edges(run, seed + 1000 * d), alive, w, total)))
            local.append(len(M.self_maintaining(
                M.shuffle_edges_local(run, seed + 1000 * d, w, total),
                alive, w, total)))
        sustain = M.sustaining_costs(edges, obs, w, total, run["costs"])
        curve[str(w)] = {
            "observed": len(obs),
            "null_full_max": max(full), "null_full_mean": statistics.mean(full),
            "null_local_max": max(local), "null_local_mean": statistics.mean(local),
            "null_draws": NULL_DRAWS,
            "sustaining_reactions": len(sustain),
            "sustaining_mean_cost": statistics.mean(sustain) if sustain else 0.0,
        }
    return {
        "seed": seed, "reactions": REACTIONS, "ok": run["ok"], "fail": run["fail"],
        "alive": len(alive), "history_core": len(M.history_core(edges)),
        "mean_cost_all": statistics.mean(run["costs"]) if run["costs"] else 0.0,
        "curve": curve, "trajectory": trajectory,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--record", action="store_true")
    ap.add_argument("--seeds", type=int, default=len(SEEDS))
    args = ap.parse_args()
    seeds = SEEDS[:args.seeds]

    workers = min(len(seeds), mp.cpu_count() - 2)
    print(f"ADDENDUM (post hoc): {REACTIONS} reactions x {len(seeds)} seeds at "
          f"{BUDGET} ATP, {workers} workers\n")
    with mp.Pool(workers) as pool:
        cells = pool.map(one_cell, seeds)

    print("diversity and success over the run — distinct hashes alive / success rate\n")
    print(f"{'seed':>10s} " + " ".join(f"{h:>12d}" for h in HORIZONS))
    for c in cells:
        cells_row = " ".join(f"{t['alive']:>4d}/{100*t['success_rate']:>5.1f}%"
                             for t in c["trajectory"])
        print(f"{c['seed']:>10d} {cells_row}")
    collapsed = sum(1 for c in cells if c["trajectory"][-1]["alive"] <= C.EXP7.MIN_DISTINCT)
    print(f"\n{collapsed} of {len(cells)} soups end below the {C.EXP7.MIN_DISTINCT}-hash "
          f"diversity floor EXP-007 preregistered as its power condition\n")

    print(f"{'seed':>10s} {'window':>7s} {'observed':>9s} {'full null':>12s} "
          f"{'local null':>12s} {'clears local':>13s}")
    clears = []
    for c in cells:
        for w in WINDOWS:
            e = c["curve"][str(w)]
            beat = e["observed"] >= C.MIN_SET_SIZE and e["observed"] > e["null_local_max"]
            if beat:
                clears.append((c["seed"], w, e))
            if w in (1000, 4000, 10_000):
                print(f"{c['seed']:>10d} {w:>7d} {e['observed']:>9d} "
                      f"{e['null_full_mean']:>6.1f}/{e['null_full_max']:<5d} "
                      f"{e['null_local_mean']:>6.1f}/{e['null_local_max']:<5d} "
                      f"{'YES' if beat else '-':>13s}")

    print(f"\ncells clearing the locality-preserving null: {len(clears)} of "
          f"{len(cells) * len(WINDOWS)}")
    verdict = {"clears": len(clears), "cells": len(cells) * len(WINDOWS)}
    if clears:
        prices = []
        for seed, w, e in clears:
            cell = next(c for c in cells if c["seed"] == seed)
            if e["sustaining_mean_cost"] and cell["mean_cost_all"]:
                prices.append((cell["mean_cost_all"] - e["sustaining_mean_cost"])
                              / cell["mean_cost_all"])
        if prices:
            held = sum(1 for x in prices if x >= C.COST_MARGIN)
            print(f"H3 is adjudicable now: sustaining reactions are cheaper by "
                  f"{', '.join(f'{100*x:+.0f}%' for x in prices[:8])} -> "
                  f"{'holds' if held > len(prices) / 2 else 'FAILS'} "
                  f"(threshold {int(100*C.COST_MARGIN)}%)")
            verdict["h3_margins"] = prices
            verdict["h3"] = "holds" if held > len(prices) / 2 else "FAILS"
        else:
            verdict["h3"] = "no sustaining reactions to price"
            print("H3: sets clear the null but have no sustaining reactions to price")
    else:
        verdict["h3"] = "UNADJUDICATED at scale"
        print("H3 stays UNADJUDICATED — and the negative is now ten times longer "
              "and four times wider than the one EXP-008 reported.")

    receipt = {"addendum": "ALIFE-EXP-008 at ten times the scale",
               "kind": "post hoc, not preregistered",
               "frame": {"reactions": REACTIONS, "seeds": list(seeds),
                         "budget": BUDGET, "windows": list(WINDOWS),
                         "null_draws": NULL_DRAWS},
               "provenance": {"oracle_sha256": al.provenance()["oracle_sha256"],
                              "python": ".".join(
                                  al.provenance()["python"].split(".")[:2]),
                              "platform": platform.python_implementation()},
               "verdict": verdict, "cells": cells}
    if args.record:
        (HERE / "addendum_scale.json").write_text(
            json.dumps(receipt, indent=2, sort_keys=True) + "\n")
        print(f"\nrecorded {HERE / 'addendum_scale.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
