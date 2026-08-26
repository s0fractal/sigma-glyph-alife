#!/usr/bin/env python3
"""Where the proved ceiling's slack lives — a DESCRIPTIVE analysis, not an experiment.

No hypotheses, no preregistration, no nulls: it re-reads receipts already
committed and factors a number this repository has published seven times.

ALIFE-EXP-001 reported that a settled population occupies 6.41% of the ceiling
`proofs/Population.lean` proves (`Σ size ≤ N + spent`). That is a product of two
independent things, and only the product has ever been tracked:

    occupancy = (Σ size / ceiling)      x   (distinct addresses / Σ size)
                 ^ metabolic slack           ^ morphological slack
                 budget the run did not      structure the population holds
                 convert into structure      more than once

Raised independently by two external reviews (Claude Fable 5 and Grok, 2026-08).
The inputs are `experiments/alife-exp-001/results.json` and
`experiments/alife-exp-004/results.json`; nothing is re-run and no measurement is
taken here.

Usage:  python3 experiments/analysis-001-where-the-slack-lives/analyse.py [--record]
"""
import argparse
import json
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def factors(agents, nodes_total, nodes_unique, atp_spent):
    ceiling = agents + atp_spent
    if not ceiling or not nodes_total:
        return None
    metabolic = nodes_total / ceiling
    morphological = nodes_unique / nodes_total
    return {"ceiling": ceiling, "nodes_total": nodes_total,
            "nodes_unique": nodes_unique, "atp_spent": atp_spent,
            "metabolic": metabolic, "morphological": morphological,
            "occupancy": nodes_unique / ceiling}


def exp001():
    d = json.loads((ROOT / "experiments/alife-exp-001/results.json").read_text())
    r = d["result"]
    out = {"per_tick": [], "per_family": {}}
    for t in r["mixed"]["trace"]:
        f = factors(t["agents"], t["nodes_total"], t["nodes_unique"], t["atp_spent"])
        if f:
            out["per_tick"].append(dict(f, tick=t["tick"]))
    for name, cell in r["families"].items():
        s = cell["settled"]
        f = factors(s["agents"], s["nodes_total"], s["nodes_unique"], s["atp_spent"])
        if f:
            out["per_family"][name] = f
    s = r["mixed"]["settled"]
    out["mixed_settled"] = factors(s["agents"], s["nodes_total"], s["nodes_unique"],
                                   s["atp_spent"])
    return out


def exp004():
    d = json.loads((ROOT / "experiments/alife-exp-004/results.json").read_text())
    cells = d["result"]["cells"]
    out = {}
    for g, seeds in cells.items():
        rows = []
        for seed, cell in seeds.items():
            s = cell["settled"]
            f = factors(64, s["nodes_total"], s["nodes_unique"], s["atp_spent"])
            if f:
                rows.append(dict(f, seed=seed))
        out[g] = {
            "cells": rows,
            "metabolic_mean": statistics.mean(r["metabolic"] for r in rows),
            "morphological_mean": statistics.mean(r["morphological"] for r in rows),
            "occupancy_mean": statistics.mean(r["occupancy"] for r in rows),
        }
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--record", action="store_true")
    args = ap.parse_args()

    a1, a4 = exp001(), exp004()

    print("ALIFE-EXP-001, the mixed run, per tick\n")
    print(f"{'tick':>5s} {'Σ size':>7s} {'distinct':>9s} {'ceiling':>8s} "
          f"{'metabolic':>10s} {'morphological':>14s} {'occupancy':>10s}")
    for t in a1["per_tick"]:
        print(f"{t['tick']:>5d} {t['nodes_total']:>7d} {t['nodes_unique']:>9d} "
              f"{t['ceiling']:>8d} {100 * t['metabolic']:>9.1f}% "
              f"{100 * t['morphological']:>13.1f}% {100 * t['occupancy']:>9.2f}%")

    print("\nper family, settled\n")
    print(f"{'family':>10s} {'metabolic':>10s} {'morphological':>14s} {'occupancy':>10s}")
    for name, f in a1["per_family"].items():
        print(f"{name:>10s} {100 * f['metabolic']:>9.1f}% "
              f"{100 * f['morphological']:>13.1f}% {100 * f['occupancy']:>9.2f}%")
    m = a1["mixed_settled"]
    print(f"{'mixed':>10s} {100 * m['metabolic']:>9.1f}% "
          f"{100 * m['morphological']:>13.1f}% {100 * m['occupancy']:>9.2f}%")

    print("\nALIFE-EXP-004, ten seeds per alphabet fraction, settled\n")
    print(f"{'genesis':>8s} {'metabolic':>10s} {'morphological':>14s} {'occupancy':>10s}")
    for g in sorted(a4, key=float):
        c = a4[g]
        print(f"{g:>8s} {100 * c['metabolic_mean']:>9.1f}% "
              f"{100 * c['morphological_mean']:>13.1f}% "
              f"{100 * c['occupancy_mean']:>9.2f}%")

    met = [a4[g]["metabolic_mean"] for g in sorted(a4, key=float)]
    mor = [a4[g]["morphological_mean"] for g in sorted(a4, key=float)]
    print(f"\nacross the alphabet sweep: metabolic moves "
          f"{100 * min(met):.1f}%..{100 * max(met):.1f}% "
          f"({100 * (max(met) - min(met)):.1f} points), morphological moves "
          f"{100 * min(mor):.1f}%..{100 * max(mor):.1f}% "
          f"({100 * (max(mor) - min(mor)):.1f} points)")
    print(f"the ceiling is dominated by the {'metabolic' if min(met) < min(mor) else 'morphological'} "
          f"factor: a run converts {100 * statistics.mean(met):.0f}% of its proved "
          f"budget into materialised nodes, and de-duplicates "
          f"{100 * (1 - statistics.mean(mor)):.0f}% of those away")

    receipt = {"analysis": "where the ceiling's slack lives",
               "kind": "descriptive — no hypotheses, no measurement taken",
               "sources": ["experiments/alife-exp-001/results.json",
                           "experiments/alife-exp-004/results.json"],
               "exp001": a1, "exp004": a4}
    if args.record:
        (HERE / "analysis.json").write_text(
            json.dumps(receipt, indent=2, sort_keys=True) + "\n")
        print(f"\nrecorded {HERE / 'analysis.json'}")
    else:
        print("\n(check-only; pass --record to write analysis.json)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
