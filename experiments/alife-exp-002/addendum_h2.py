#!/usr/bin/env python3
"""ADDENDUM to ALIFE-EXP-002 — adjudicating H2 on the arm where the memo fired.

POST HOC, not preregistered. No measurement is taken: this reads the committed
receipt and scores a hypothesis that the preregistered arm could not test.

H2 asked whether a memoized run makes the proved ceiling `N + spent` a tighter
description of what a machine stores. It was reported NOT ADJUDICATED because on
the preregistered corpus the memo fired ONCE — there was no memoized run to
compare. The reason was the experiment's own headline finding: a memo is keyed by
what an agent asks for, and 64 agents holding three quarters of their nodes in
common never utter each other's addresses.

The `composite` arm, added post hoc in the same experiment, supplies the demand
path and fires 41 times. H2 is adjudicable there, and only there.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    record = "--record" in sys.argv
    d = json.loads((HERE / "results.json").read_text())["result"]["part_a"]
    rows = []
    print(f"{'population':>18s} {'hits':>5s} {'Σ size':>7s} {'distinct':>9s} "
          f"{'ceiling':>8s} {'occupancy':>10s}")
    for name in ("mixed", "composite*"):
        for arm in ("off", "shared"):
            r = d[name][arm]
            rows.append({"population": name, "arm": arm,
                         "memo_hits": r["memo_hits"],
                         "nodes_total": r["nodes_total"],
                         "nodes_unique": r["nodes_unique"],
                         "ceiling": r["ceiling"],
                         "occupancy": r["ceiling_occupancy"]})
            print(f"{name + '/' + arm:>18s} {r['memo_hits']:>5d} "
                  f"{r['nodes_total']:>7d} {r['nodes_unique']:>9d} "
                  f"{r['ceiling']:>8d} {100 * r['ceiling_occupancy']:>9.2f}%")

    c = d["composite*"]
    off, sh = c["off"], c["shared"]
    tighter = sh["ceiling_occupancy"] > off["ceiling_occupancy"]
    rel = sh["ceiling_occupancy"] / off["ceiling_occupancy"]
    print(f"\n  preregistered corpus: {d['mixed']['shared']['memo_hits']} memo hit — "
          f"nothing to compare, which is why H2 was NOT ADJUDICATED")
    print(f"  composite arm (post hoc): {sh['memo_hits']} hits, occupancy "
          f"{100 * off['ceiling_occupancy']:.2f}% -> "
          f"{100 * sh['ceiling_occupancy']:.2f}% "
          f"({'tighter' if tighter else 'no tighter'}, {rel:.2f}x relative)")
    print(f"  mechanism, as H2 predicted it: the ceiling falls "
          f"{off['ceiling']} -> {sh['ceiling']} because the memo spends less; "
          f"distinct addresses move {off['nodes_unique']} -> {sh['nodes_unique']}")
    print(f"\nH2 on the composite arm: {'holds' if tighter else 'FAILS'} — "
          f"post hoc, one arm, one seed, deterministic")

    if record:
        (HERE / "addendum_h2.json").write_text(json.dumps(
            {"addendum": "ALIFE-EXP-002 H2, adjudicated on the composite arm",
             "kind": "post hoc, not preregistered; no measurement taken",
             "source": "experiments/alife-exp-002/results.json",
             "rows": rows,
             "verdict": {"holds": tighter, "relative": rel,
                         "hits": sh["memo_hits"]}},
            indent=2, sort_keys=True) + "\n")
        print(f"\nrecorded {HERE / 'addendum_h2.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
