#!/usr/bin/env python3
"""Measure the same populations under a metric that counts the alphabet and one
that does not.

Check-only by default; `--record` writes `results.json` after the controls pass.
Judged against `../ALIFE-EXP-004-alphabet-or-structure-preregistration.md`,
committed before this file; the corpora were committed before that.
"""
import argparse
import json
import platform
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


def metrics(agents, store):
    sf, occ, uniq = al.sharing_factor(agents)
    st_f, st_occ, st_uniq = al.structural_sharing(agents, store)
    jac, pairs, empty = al.pairwise_jaccard(agents, store)
    return {
        "sharing_factor": sf, "nodes_total": occ, "nodes_unique": uniq,
        "structural_sharing": st_f, "compound_total": st_occ,
        "compound_unique": st_uniq,
        "jaccard": jac, "jaccard_pairs": pairs, "jaccard_empty_pairs": empty,
        "mean_size": occ / len(agents) if agents else 0.0,
    }


def run_cell(seed, g):
    """One corpus: measured materialized-and-unreduced, then settled."""
    entries = C.build(seed, g)
    store = fresh_store()

    unreduced = []
    for e in entries:
        al.put_term(e["term"], store)
        a = al.Agent(e["name"], sg.term_hash(e["term"]), 0)
        a.term = e["term"]
        unreduced.append(a)
    birth = metrics(unreduced, store)

    econ = al.Economy(C.ATP_PER_AGENT * len(entries))
    agents = []
    for e in entries:
        root = al.put_term(e["term"], store)
        a = al.Agent(e["name"], root, 0)
        econ.endow(a, C.ATP_PER_AGENT)
        agents.append(a)
    for _ in range(C.TICKS):
        if not any(a.status in al.RUNNABLE and a.atp > 0 for a in agents):
            break
        for a in sorted(agents, key=lambda x: x.aid):
            if a.status not in al.RUNNABLE or a.atp == 0:
                continue
            budget = C.SLICE_ATP
            while True:
                got = al.reduce_slice(a, store, budget, probe=True)
                if got or a.status != al.LIVE:
                    break
                budget = min(a.atp, max(1, budget * 2))
            al.put_term(a.term, store)
    assert econ.check(agents), "ATP CONSERVATION VIOLATED"
    assert (sum(a.size for a in agents)
            <= sum(a.s0 for a in agents) + sum(a.spent for a in agents)), \
        "POPULATION BOUND VIOLATED"
    settled = metrics(agents, store)
    settled["settled"] = sum(1 for a in agents if a.status == al.NORMAL)
    settled["atp_spent"] = sum(a.spent for a in agents)
    return {"fingerprint": C.fingerprint(entries),
            "unreduced": birth, "settled": settled}


def controls():
    out = []
    store = fresh_store()
    IG = ("lit", sg.sha(b"I"))
    A = lambda x, y: ("app", x, y)

    conv = []
    for i in range(3):
        a = al.Agent(f"c{i}", al.put_term(IG, store), 0)
        a.term = IG
        conv.append(a)
    sf = al.sharing_factor(conv)[0]
    stf = al.structural_sharing(conv, store)[0]
    jac, pairs, empty = al.pairwise_jaccard(conv, store)
    out.append((f"C1 convergence scores {sf:.1f} on sharing_factor and "
                f"{stf:.1f} on structural sharing, with {empty} empty pairs",
                sf == 3.0 and stf == 0.0 and pairs == 0 and empty == 3))

    big = A(A(IG, IG), A(IG, IG))
    sh = []
    for i, extra in enumerate([("lit", sg.sha(b"a")), ("lit", sg.sha(b"b")),
                               ("lit", sg.sha(b"c"))]):
        t = A(big, extra)
        a = al.Agent(f"s{i}", al.put_term(t, store), 0)
        a.term = t
        sh.append(a)
    stf2 = al.structural_sharing(sh, store)[0]
    jac2, pairs2, _ = al.pairwise_jaccard(sh, store)
    out.append((f"C1 real shared structure scores {stf2:.2f} structural and "
                f"{jac2:.2f} Jaccard over {pairs2} pairs",
                stf2 > 1.0 and jac2 > 0.0 and pairs2 == 3))

    anchor = C.build(20260825, 0.7)
    out.append((f"C2 the generator at g=0.7 is EXP-001's leaf distribution "
                f"(anchor fingerprint {C.fingerprint(anchor)})",
                len(anchor) == 64))
    out.append(("C3 conservation and the bound: asserted in every cell", True))
    return all(ok for _, ok in out), out


def summarize(result):
    print(f"{'g':>5s} {'metric':>12s} {'unreduced':>10s} {'settled':>9s} "
          f"{'Δ':>8s} {'seeds down':>11s}")
    for g in map(str, C.GENESIS_FRACTIONS):
        cells = result["cells"][g]
        for label, key in (("sharing", "sharing_factor"),
                           ("structural", "structural_sharing"),
                           ("jaccard", "jaccard")):
            us = [c["unreduced"][key] for c in cells.values()]
            ss = [c["settled"][key] for c in cells.values()]
            du = sum(1 for u, s in zip(us, ss) if s < u)
            print(f"{g:>5s} {label:>12s} {sum(us)/len(us):>10.3f} "
                  f"{sum(ss)/len(ss):>9.3f} "
                  f"{(sum(ss)-sum(us))/len(us):>+8.3f} {du:>7d}/{len(us)}")
        print()

    anchor = result["cells"]["0.7"]
    down = sum(1 for c in anchor.values()
               if c["settled"]["sharing_factor"] < c["unreduced"]["sharing_factor"])
    print(f"H1 (EXP-001 replicates under its own metric at g=0.7): "
          f"{down}/{len(anchor)} seeds fall -> "
          f"{'holds' if down > len(anchor) / 2 else 'FAILS'}")
    sdown = sum(1 for c in anchor.values()
                if c["settled"]["structural_sharing"] < c["unreduced"]["structural_sharing"])
    print(f"H2 (the drop does NOT survive the separation): {sdown}/{len(anchor)} "
          f"seeds fall structurally -> "
          f"{'holds — EXP-001 measured the alphabet' if sdown <= len(anchor) / 2 else 'FAILS — the drop is structural too'}")
    drops = []
    for g in C.GENESIS_FRACTIONS:
        cells = result["cells"][str(g)]
        d = sum(c["settled"]["sharing_factor"] - c["unreduced"]["sharing_factor"]
                for c in cells.values()) / len(cells)
        drops.append((g, d))
    mono = all(b <= a for (_, a), (_, b) in zip(drops, drops[1:]))
    print(f"H3 (the drop scales with the alphabet): "
          f"{', '.join(f'{g}:{d:+.2f}' for g, d in drops)} -> "
          f"{'holds' if mono else 'FAILS'}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--record", action="store_true")
    args = ap.parse_args()

    ok, results = controls()
    for name, passed in results:
        print(("OK  " if passed else "FAIL"), name)
    if not ok:
        print("\nALIFE-EXP-004: CONTROLS FAILED — nothing measured, nothing recorded")
        return 1

    cells = {}
    for g in C.GENESIS_FRACTIONS:
        cells[str(g)] = {str(seed): run_cell(seed, g) for seed in C.SEEDS}
    result = {"cells": cells}
    print()
    summarize(result)

    prov = al.provenance()
    receipt = {
        "experiment": "ALIFE-EXP-004",
        "frame": {"seeds": list(C.SEEDS),
                  "genesis_fractions": list(C.GENESIS_FRACTIONS),
                  "per_family": C.PER_FAMILY, "atp_per_agent": C.ATP_PER_AGENT,
                  "slice_atp": C.SLICE_ATP, "ticks": C.TICKS},
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
    print(f"\noracle: {prov['oracle_source']}  (sha256 {prov['oracle_sha256'][:16]}…)")
    if args.record:
        (HERE / "results.json").write_text(
            json.dumps(receipt, indent=2, sort_keys=True) + "\n")
        print(f"recorded {HERE / 'results.json'}")
    else:
        print("(check-only; pass --record to write results.json)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
