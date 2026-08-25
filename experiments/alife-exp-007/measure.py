#!/usr/bin/env python3
"""An applicative chemistry with prices: A applied to B, by hash.

Check-only by default; `--record` writes `results.json` after the controls pass.
Judged against `../ALIFE-EXP-007-do-organizations-form-preregistration.md`,
committed before this file; the frame, with its blind-chosen budget, before that.
"""
import argparse
import json
import platform
import random
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "impl"))

import corpus as C  # noqa: E402
import sigma_alife as al  # noqa: E402
import sigma_nulls as N  # noqa: E402

sg = al.sg
DIS_HASHES = None


def fresh_store():
    st = sg.Store()
    for b in (sg.I_BYTES, sg.K_BYTES, sg.S_BYTES):
        st.put(b)
    return st


def dis_hashes():
    global DIS_HASHES
    if DIS_HASHES is None:
        DIS_HASHES = {sg.term_hash(("dis", r))
                      for r in (sg.R_ATP, sg.R_UNRES, sg.R_INVALID)}
    return DIS_HASHES


def l1_core(reactions):
    """The largest set S in which every member is the product of a reaction whose
    two reactants are both in S. Peeling: drop anything with no producing pair
    inside the current set, until nothing drops."""
    products = {}
    for a, b, c in reactions:
        products.setdefault(c, set()).add((a, b))
    core = set(products)
    changed = True
    while changed:
        changed = False
        for c in list(core):
            if not any(a in core and b in core for a, b in products[c]):
                core.discard(c)
                changed = True
    return core


def run_soup(budget, seed, reactions=C.REACTIONS, capacity=C.CAPACITY,
             probe=False, sample_check=0, keep_edges=False):
    store = fresh_store()
    rng = random.Random(seed)
    econ = al.Economy(budget * reactions + 1)
    soup = [al.put_term(e["term"], store) for e in C.build()][:capacity]
    observed, trace = [], []
    ok = fail = 0
    closed = 0
    costs = []
    checked = 0
    mismatches = 0
    poisoned = 0
    for i in range(reactions):
        a, b = rng.choice(soup), rng.choice(soup)
        root = al.put_term(("app", ("thunk", a), ("thunk", b)), store)
        agent = al.Agent(f"r{i}", root, 0)
        econ.endow(agent, budget)
        slice_atp = C.SLICE_ATP
        while agent.status in al.RUNNABLE and agent.atp > 0:
            got = al.reduce_slice(agent, store, slice_atp, probe=probe)
            if agent.status != al.LIVE:
                break
            if not got:
                slice_atp = min(agent.atp, max(1, slice_atp * 2))
        econ.collect(agent, agent.atp)          # unspent returns to the commons
        if agent.status == al.NORMAL:
            ok += 1
            costs.append(agent.spent)
            product = al.put_term(agent.term, store)
            if sample_check and checked < sample_check:
                ref, _ = sg.eval_hash(root, budget, store)
                mismatches += sg.term_hash(ref) != product
                checked += 1
            if product in soup:
                closed += 1
            observed.append((a, b, product))
            soup.append(product)
            if len(soup) > capacity:
                soup.pop(rng.randrange(len(soup)))
        else:
            fail += 1
        poisoned += sum(1 for h in soup if h in dis_hashes())
        if (i + 1) % 100 == 0:
            trace.append({"reaction": i + 1, "distinct": len(set(soup)),
                          "closure": closed / max(1, ok), "ok": ok, "fail": fail})
    core = l1_core(observed)
    edges = observed if keep_edges else None
    l0 = sorted({c.hex() for a, b, c in observed if a == b == c})
    return {
        "budget": budget, "seed": seed,
        "reactions": reactions, "ok": ok, "fail": fail,
        "success_rate": ok / reactions,
        "closure": closed / max(1, ok),
        "distinct": len(set(soup)),
        "mean_cost": statistics.mean(costs) if costs else 0,
        "median_cost": statistics.median(costs) if costs else 0,
        "l0": l0,
        "core_size": len(core),
        "core": sorted(h.hex() for h in core),
        "trace": trace,
        "checked": checked, "mismatches": mismatches, "poisoned": poisoned,
        "edges": edges,
        "ledger_ok": True,
        "pool_left": econ.pool,
        "endowment": econ.endowment,
    }


def controls(entries):
    out = []

    # C5 first: a peeling that finds cores in an open chain invalidates everything.
    a, b, c = b"a", b"b", b"c"
    closed_case = [(a, b, a), (b, a, b)]
    open_case = [(a, b, c)]
    out.append((f"C5 the core algorithm closes a closed pair "
                f"({len(l1_core(closed_case))}) and returns nothing on an open "
                f"chain ({len(l1_core(open_case))})",
                l1_core(closed_case) == {a, b} and l1_core(open_case) == set()))

    r = run_soup(C.ATP_PER_REACTION, C.SEED, reactions=200, probe=True,
                 sample_check=25)
    out.append((f"C1 {r['checked']} sampled products match the oracle "
                f"({r['mismatches']} mismatches)", r["mismatches"] == 0))
    out.append((f"C2 the commons balances: {r['pool_left']} left of "
                f"{r['endowment']}", 0 <= r["pool_left"] <= r["endowment"]))
    out.append(("C3 the memory bound held at every action (probe on)", True))
    out.append((f"C4 no DISSONANCE ever entered the soup ({r['poisoned']})",
                r["poisoned"] == 0))
    out.append((f"C6 founders fingerprint is {C.fingerprint()}",
                C.fingerprint() == C.INHERITED_FINGERPRINT))

    full = run_soup(C.ATP_PER_REACTION, C.SEED)
    powered = (full["success_rate"] >= C.MIN_SUCCESS_RATE
               and full["distinct"] >= C.MIN_DISTINCT)
    out.append((f"C7 power: {100 * full['success_rate']:.0f}% of reactions "
                f"succeed, {full['distinct']} distinct hashes survive", powered))
    return all(ok for _, ok in out), out


NULL_DRAWS = 20             # one permutation is not a null: D54
NULL_REACTIONS = 400        # the nulls run shorter than the measurement; they are
                            # about whether a STATISTIC is informative, not about
                            # the run, and a 7-minute null per cell buys nothing


def shuffled_core(edges, seed):
    """NULL for the core: same reactant pairs, same product multiset, products
    permuted among reactions. If a chance graph of the same density yields a core
    as large, then core size is a property of the graph and not of any
    organization in it."""
    rng = random.Random(seed + 9973)
    products = [c for _, _, c in edges]
    rng.shuffle(products)
    return l1_core([(a, b, p) for (a, b, _), p in zip(edges, products)])


def replay_closure(products, seed, capacity=C.CAPACITY):
    """Closure of a product sequence replayed into a bounded soup, used as the
    statistic the chance models are sampled against."""
    soup, closed = [], 0
    drop = random.Random(seed + 104729)
    for p in products:
        if p in soup:
            closed += 1
        soup.append(p)
        if len(soup) > capacity:
            soup.pop(drop.randrange(len(soup)))
    return closed / max(1, len(products))


def shuffled_closure(edges, seed, capacity=C.CAPACITY):
    """NULL for closure: replay the same product multiset in a random order into
    the same bounded soup. What survives this is the part of closure that is not
    simply the product distribution meeting a small soup."""
    rng = random.Random(seed + 7919)
    products = [c for _, _, c in edges]
    rng.shuffle(products)
    soup, closed = [], 0
    drop = random.Random(seed + 104729)
    for p in products:
        if p in soup:
            closed += 1
        soup.append(p)
        if len(soup) > capacity:
            soup.pop(drop.randrange(len(soup)))
    return closed / max(1, len(products))


def jaccard(x, y):
    x, y = set(x), set(y)
    return len(x & y) / len(x | y) if (x | y) else 1.0


def nulls():
    """POST HOC — not preregistered. Every one of this experiment's three criteria
    is met by the data; each of these asks whether a chance process meets it too.

    CORRECTED 2026-08-26: these were single draws. One permutation is not a null
    — ALIFE-EXP-008 had a finished positive result reversed by going from one draw
    to twenty (`DECISIONS.md` D54) — and the same defect was here, in a published
    result, unnoticed because its verdicts happened to survive. They are sampled
    now, through `impl/sigma_nulls.py`, and the receipt carries the draw count.
    The verdicts did not move; that they did not is a fact and was not a given."""
    out = {}
    for budget in (C.BUDGET_SWEEP[0], C.ATP_PER_REACTION):
        cell = {}
        for seed in C.SEEDS[:2]:
            r = run_soup(budget, seed, reactions=NULL_REACTIONS, keep_edges=True)
            edges = [(i, a, b, c) for i, (a, b, c) in enumerate(r["edges"])]
            core_dist = N.sample(edges, lambda e: len(l1_core(
                [(a, b, c) for _, a, b, c in e])), "shuffle_products",
                draws=NULL_DRAWS, seed=seed)
            closure_dist = N.sample(edges, lambda e: replay_closure(
                [c for _, _, _, c in e], seed), "shuffle_products",
                draws=NULL_DRAWS, seed=seed + 1)
            cell[str(seed)] = {
                "core_observed": len(l1_core(r["edges"])),
                "core_shuffled": core_dist["max"],
                "core_shuffled_mean": core_dist["mean"],
                "closure_observed": r["closure"],
                "closure_shuffled": closure_dist["max"],
                "closure_shuffled_mean": closure_dist["mean"],
                "null_draws": NULL_DRAWS,
            }
        out[str(budget)] = cell
    lo = run_soup(C.BUDGET_SWEEP[0], C.SEEDS[0], reactions=NULL_REACTIONS,
                  keep_edges=True)
    hi = run_soup(C.BUDGET_SWEEP[-1], C.SEEDS[0], reactions=NULL_REACTIONS,
                  keep_edges=True)
    out["overlap"] = {
        "core": jaccard(l1_core(lo["edges"]), l1_core(hi["edges"])),
        "products": jaccard({c for _, _, c in lo["edges"]},
                            {c for _, _, c in hi["edges"]}),
        "null_draws": NULL_DRAWS,
    }
    return out


def measure():
    primary = {str(s): run_soup(C.ATP_PER_REACTION, s) for s in C.SEEDS}
    sweep = {str(b): {str(s): run_soup(b, s) for s in C.SEEDS}
             for b in C.BUDGET_SWEEP}
    return {"primary": primary, "sweep": sweep, "nulls": nulls()}


def summarize(result):
    print(f"{'seed':>10s} {'success':>8s} {'closure':>8s} {'distinct':>9s} "
          f"{'core':>5s} {'L0':>4s} {'mean cost':>10s}")
    for seed, r in result["primary"].items():
        print(f"{seed:>10s} {100 * r['success_rate']:>7.0f}% {r['closure']:>8.3f} "
              f"{r['distinct']:>9d} {r['core_size']:>5d} {len(r['l0']):>4d} "
              f"{r['mean_cost']:>10.1f}")
    print(f"\n{'budget':>8s} {'success':>8s} {'closure':>8s} {'distinct':>9s} "
          f"{'core':>5s} {'mean cost':>10s}   (seed {C.SEEDS[0]})")
    for b, cells in result["sweep"].items():
        r = cells[str(C.SEEDS[0])]
        print(f"{b:>8s} {100 * r['success_rate']:>7.0f}% {r['closure']:>8.3f} "
              f"{r['distinct']:>9d} {r['core_size']:>5d} {r['mean_cost']:>10.1f}")

    print()
    h1 = sum(1 for r in result["primary"].values()
             if r["closure"] >= 0.30 and r["distinct"] >= C.MIN_DISTINCT)
    print(f"H1 (closure >= 0.30 with >= {C.MIN_DISTINCT} distinct): {h1}/3 seeds "
          f"-> {'holds' if h1 >= 2 else 'FAILS'}")
    h2 = sum(1 for r in result["primary"].values() if r["core_size"] >= 3)
    print(f"H2 (L1-core of size >= 3): {h2}/3 seeds -> "
          f"{'holds' if h2 >= 2 else 'FAILS'}")
    js = []
    for s in C.SEEDS:
        lo = result["sweep"][str(C.BUDGET_SWEEP[0])][str(s)]["core"]
        hi = result["sweep"][str(C.BUDGET_SWEEP[-1])][str(s)]["core"]
        js.append(jaccard(lo, hi))
    print(f"H3 (cores at {C.BUDGET_SWEEP[0]} and {C.BUDGET_SWEEP[-1]} ATP overlap "
          f"< 0.5): Jaccard {', '.join(f'{j:.3f}' for j in js)} -> "
          f"{'holds' if sum(1 for j in js if j < 0.5) >= 2 else 'FAILS'}")

    n = result["nulls"]
    print("\nNULLS (post hoc, not preregistered) — every criterion above, "
          "against chance\n")
    print(f"{'budget':>7s} {'seed':>10s} {'core':>6s} {'core/null max':>14s} "
          f"{'closure':>8s} {'closure/null max':>17s}   (nulls sampled)")
    for budget, cells in n.items():
        if budget == "overlap":
            continue
        for seed, c in cells.items():
            print(f"{budget:>7s} {seed:>10s} {c['core_observed']:>6d} "
                  f"{c['core_shuffled']:>14d} {c['closure_observed']:>8.3f} "
                  f"{c['closure_shuffled']:>17.3f}")
    o = n["overlap"]
    print(f"\n  core overlap across budgets {o['core']:.3f} against product "
          f"overlap {o['products']:.3f}")
    beaten = all(c["core_shuffled"] >= c["core_observed"]
                 for b, cells in n.items() if b != "overlap"
                 for c in cells.values())
    print(f"\n  H2 after its null: {'REFUTED — a chance graph of the same density '
          'yields a core as large' if beaten else 'survives'}")
    print(f"  H3 after its null: {'UNINFORMATIVE — the soups overlap no more than '
          'the cores' if o['products'] <= o['core'] * 2 else 'survives'}")
    print("  H1 after its null: closure exceeds the shuffled order by "
          f"{min(c['closure_observed'] - c['closure_shuffled'] for b, cells in n.items() if b != 'overlap' for c in cells.values()):+.3f} "
          f"to {max(c['closure_observed'] - c['closure_shuffled'] for b, cells in n.items() if b != 'overlap' for c in cells.values()):+.3f} "
          "— a small residual, and no criterion was preregistered for it")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--record", action="store_true")
    ap.add_argument("--controls", action="store_true",
                    help="run the controls and stop. The full grid is a "
                         "ten-minute job; the controls are the half that can "
                         "run on every push.")
    args = ap.parse_args()

    entries = C.build()
    ok, results = controls(entries)
    for name, passed in results:
        print(("OK  " if passed else "FAIL"), name)
    if not ok:
        print("\nALIFE-EXP-007: CONTROLS FAILED — nothing measured, nothing recorded")
        return 1
    if args.controls:
        print("\nEXP-007-CONTROLS: ALL PASS")
        return 0

    result = measure()
    print()
    summarize(result)

    prov = al.provenance()
    receipt = {
        "experiment": "ALIFE-EXP-007",
        "corpus_fingerprint": C.fingerprint(),
        "inherited_from": "ALIFE-EXP-001",
        "frame": {"capacity": C.CAPACITY, "reactions": C.REACTIONS,
                  "atp_per_reaction": C.ATP_PER_REACTION,
                  "budget_sweep": list(C.BUDGET_SWEEP), "seeds": list(C.SEEDS),
                  "slice_atp": C.SLICE_ATP,
                  "min_success_rate": C.MIN_SUCCESS_RATE,
                  "min_distinct": C.MIN_DISTINCT},
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
