#!/usr/bin/env python3
"""Self-maintaining sets: alive, and being re-made out of themselves.

Check-only by default; `--record` writes `results.json` after the controls pass.
Judged against `../ALIFE-EXP-008-does-anything-maintain-itself-preregistration.md`,
committed before this file; the frame before that.

The soup runner duplicates ALIFE-EXP-007's rather than importing it, deliberately:
this one has to return the reaction INDEX and the final soup, and editing a
committed experiment's harness to serve a later one would change its receipt.
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

sg = al.sg


def fresh_store():
    st = sg.Store()
    for b in (sg.I_BYTES, sg.K_BYTES, sg.S_BYTES):
        st.put(b)
    return st


def dis_hashes():
    return {sg.term_hash(("dis", r)) for r in (sg.R_ATP, sg.R_UNRES, sg.R_INVALID)}


def history_core(edges):
    """ALIFE-EXP-007's metric, recomputed here for H2's comparison."""
    producers = {}
    for _, a, b, c in edges:
        producers.setdefault(c, set()).add((a, b))
    core = set(producers)
    changed = True
    while changed:
        changed = False
        for c in list(core):
            if not any(a in core and b in core for a, b in producers[c]):
                core.discard(c)
                changed = True
    return core


def self_maintaining(edges, alive, window, total):
    """Alive, and re-produced inside the last `window` reactions by a pair of
    members of the set. Peeled to a fixed point."""
    producers = {}
    for i, a, b, c in edges:
        if i >= total - window:
            producers.setdefault(c, set()).add((a, b))
    core = set(producers) & set(alive)
    changed = True
    while changed:
        changed = False
        for c in list(core):
            if not any(a in core and b in core for a, b in producers[c]):
                core.discard(c)
                changed = True
    return core


def sustaining_costs(edges, core, window, total, costs):
    """Costs of the reactions inside the window that sustain the set."""
    out = []
    for (i, a, b, c), cost in zip(edges, costs):
        if i >= total - window and c in core and a in core and b in core:
            out.append(cost)
    return out


def run_soup(budget, seed, reactions=C.REACTIONS, probe=False):
    store = fresh_store()
    rng = random.Random(seed)
    econ = al.Economy(budget * reactions + 1)
    soup = [al.put_term(e["term"], store) for e in C.build()][:C.CAPACITY]
    edges, costs = [], []
    ok = fail = poisoned = 0
    bad = dis_hashes()
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
        econ.collect(agent, agent.atp)
        if agent.status == al.NORMAL:
            ok += 1
            product = al.put_term(agent.term, store)
            edges.append((i, a, b, product))
            costs.append(agent.spent)
            soup.append(product)
            if len(soup) > C.CAPACITY:
                soup.pop(rng.randrange(len(soup)))
        else:
            fail += 1
        poisoned += sum(1 for h in soup if h in bad)
    return {"edges": edges, "costs": costs, "alive": set(soup), "ok": ok,
            "fail": fail, "poisoned": poisoned, "pool_left": econ.pool,
            "endowment": econ.endowment, "reactions": reactions}


def shuffle_edges_local(run, seed, window, total):
    """A STRONGER null than a full shuffle. Permuting every product destroys
    temporal locality too, so any set that self-maintains beats it — the chance
    model is too weak to be evidence on its own. This one permutes products only
    WITHIN the window and only within the earlier block, so the multiset of recent
    products is exactly preserved and the only thing destroyed is WHICH pair made
    which molecule. A set that survives this maintains itself because of who
    produces whom."""
    rng = random.Random(seed + 8191)
    edges = run["edges"]
    inside = [k for k, (i, *_ ) in enumerate(edges) if i >= total - window]
    outside = [k for k, (i, *_ ) in enumerate(edges) if i < total - window]
    out = list(edges)
    for block in (inside, outside):
        prods = [edges[k][3] for k in block]
        rng.shuffle(prods)
        for k, p in zip(block, prods):
            i, a, b, _ = edges[k]
            out[k] = (i, a, b, p)
    return out


def shuffle_edges(run, seed):
    rng = random.Random(seed + 4093)
    products = [c for _, _, _, c in run["edges"]]
    rng.shuffle(products)
    return [(i, a, b, p) for (i, a, b, _), p in zip(run["edges"], products)]


NULL_DRAWS = 20     # ONE shuffle is not a null. The first version drew a single
                    # permutation per window, and the locality-preserving draw at
                    # window 200 came back LARGER than the observed set — which
                    # says nothing either way, because a single draw of a noisy
                    # statistic is a coin, not a distribution. The soup is what
                    # costs ten minutes; a permutation and a peel cost
                    # milliseconds, so there is no excuse for one.


def analyse(run, seed):
    total = run["reactions"]
    alive = run["alive"]
    curve = {}
    for w in C.WINDOWS:
        obs = self_maintaining(run["edges"], alive, w, total)
        full, local = [], []
        for d in range(NULL_DRAWS):
            full.append(len(self_maintaining(
                shuffle_edges(run, seed + 1000 * d), alive, w, total)))
            local.append(len(self_maintaining(
                shuffle_edges_local(run, seed + 1000 * d, w, total),
                alive, w, total)))
        curve[str(w)] = {"observed": len(obs),
                         "null": max(full), "null_mean": statistics.mean(full),
                         "null_local": max(local),
                         "null_local_mean": statistics.mean(local),
                         "null_draws": NULL_DRAWS,
                         "members": sorted(h.hex()[:12] for h in obs)}
    # THE WINDOW IS CHOSEN BY THE NULL, NEVER BY THE DATA. The first version of
    # this function took the window that maximised the OBSERVED set — which is
    # precisely what the preregistration lists under "what would make this
    # experiment worthless", and it selected window 600, where the null already
    # scores 16. The rule is now: the largest window at which the shuffled graph
    # still yields nothing. Beyond it the metric degenerates into EXP-007's
    # history-core, which chance beats, and the curve is reported so that
    # degeneration is visible.
    # "Clean" now means the null's WORST of 20 draws is still empty, not that one
    # lucky draw was.
    clean = [w for w in C.WINDOWS if curve[str(w)]["null"] == 0]
    best_w = max(clean) if clean else 0
    best = self_maintaining(run["edges"], alive, best_w, total) if best_w else set()
    sustain = sustaining_costs(run["edges"], best, best_w, total, run["costs"])
    rng = random.Random(seed + 61)
    matched = set(rng.sample(sorted(alive), min(len(best), len(alive)))) if best else set()
    matched_costs = sustaining_costs(run["edges"], matched, best_w, total, run["costs"])
    return {
        "curve": curve,
        "best_window": best_w,
        "best_size": len(best),
        "null_local_at_best": curve[str(best_w)]["null_local"] if best_w else 0,
        "history_core": len(history_core(run["edges"])),
        "alive": len(alive),
        "ok": run["ok"], "fail": run["fail"],
        "mean_cost_all": statistics.mean(run["costs"]) if run["costs"] else 0.0,
        "mean_cost_sustaining": statistics.mean(sustain) if sustain else 0.0,
        "mean_cost_matched": statistics.mean(matched_costs) if matched_costs else 0.0,
        "sustaining_reactions": len(sustain),
    }


def controls():
    out = []
    a, b, c = b"a", b"b", b"c"
    total = 10
    alive = {a, b}
    inside = [(8, a, b, a), (9, b, a, b)]
    outside = [(0, a, b, a), (9, b, a, b)]
    out.append(("C1 a self-maintaining pair inside the window is found",
                self_maintaining(inside, alive, 5, total) == {a, b}))
    out.append(("C1 a production outside the window does not count",
                self_maintaining(outside, alive, 5, total) == set()))
    out.append(("C1 a dead member kills the set",
                self_maintaining(inside, {a}, 5, total) == set()))

    r = run_soup(C.ATP_PER_REACTION, C.SEEDS[0], reactions=200, probe=True)
    out.append((f"C3 conservation: {r['pool_left']} left of {r['endowment']}; "
                f"the bound held at every action",
                0 <= r["pool_left"] <= r["endowment"]))
    out.append((f"C4 no DISSONANCE entered the soup ({r['poisoned']})",
                r["poisoned"] == 0))
    out.append((f"C5 founders fingerprint is {C.fingerprint()}",
                C.fingerprint() == C.INHERITED_FINGERPRINT))
    return all(ok for _, ok in out), out


def measure():
    cells = {}
    for budget in C.BUDGET_SWEEP:
        for seed in C.SEEDS:
            run = run_soup(budget, seed)
            cells[f"{budget}/{seed}"] = analyse(run, seed)
    return {"cells": cells}


def summarize(result):
    cells = result["cells"]
    print(f"{'budget/seed':>16s} {'alive':>6s} {'history core':>13s} "
          f"{'null-clean window':>18s} {'self-maintaining':>17s} {'null':>5s}")
    for key, r in cells.items():
        # A cell with NO null-clean window is not a zero: it is a cell where the
        # metric cannot be told from chance at any window, and it prints as such
        # rather than as a set of size 0.
        w = r["best_window"]
        window = str(w) if w else "none"
        nul = str(r["curve"][str(w)]["null"]) if w else "-"
        size = str(r["best_size"]) if w else "-"
        print(f"{key:>16s} {r['alive']:>6d} {r['history_core']:>13d} "
              f"{window:>18s} {size:>17s} {nul:>5s}")

    print(f"\nwindow curve at {C.ATP_PER_REACTION} ATP, seed {C.SEEDS[0]} "
          f"(observed / full-shuffle null / locality-preserving null)")
    r = cells[f"{C.ATP_PER_REACTION}/{C.SEEDS[0]}"]
    print("  " + "  ".join(f"{w}: {r['curve'][str(w)]['observed']}/"
                           f"{r['curve'][str(w)]['null']}/"
                           f"{r['curve'][str(w)]['null_local']}" for w in C.WINDOWS))
    print(f"  (nulls are the MAX over {NULL_DRAWS} permutations, not one draw)")

    print()
    # NO WINDOW IS SELECTED. The rule that picked "the largest window at which the
    # null is empty" was written when the null was a single draw and empty
    # everywhere; with twenty draws it collapses to windows where nothing exists
    # at all. The preregistration says the whole curve is reported, so the whole
    # curve is scored, against both chance models, at every window.
    primary = [(s_, cells[f"{C.ATP_PER_REACTION}/{s_}"]) for s_ in C.SEEDS]
    print(f"H1 scored across the curve — observed > the null's MAX of "
          f"{NULL_DRAWS} draws, at the same window\n")
    print(f"{'window':>7s} {'clears full shuffle':>20s} {'clears locality-preserving':>27s}")
    full_wins = local_wins = 0
    for w in C.WINDOWS:
        f_ = sum(1 for _, r in primary
                 if r["curve"][str(w)]["observed"] >= C.MIN_SET_SIZE
                 and r["curve"][str(w)]["observed"] > r["curve"][str(w)]["null"])
        l_ = sum(1 for _, r in primary
                 if r["curve"][str(w)]["observed"] >= C.MIN_SET_SIZE
                 and r["curve"][str(w)]["observed"] > r["curve"][str(w)]["null_local"])
        full_wins += f_ >= 2
        local_wins += l_ >= 2
        print(f"{w:>7d} {f'{f_}/3 seeds':>20s} {f'{l_}/3 seeds':>27s}")
    print(f"\nH1 against the PREREGISTERED null (full shuffle): clears at "
          f"{full_wins}/{len(C.WINDOWS)} windows -> "
          f"{'holds' if full_wins >= 3 else 'FAILS'}")
    print(f"H1 against the STRONGER null (locality-preserving, post hoc): clears "
          f"at {local_wins}/{len(C.WINDOWS)} windows -> "
          f"{'holds' if local_wins >= 3 else 'FAILS'}")
    h1 = full_wins

    # H2 across the curve as well, for the same reason: no window is selected.
    print(f"\nH2 — does persistence discriminate? history-core against the "
          f"self-maintaining set, per window, at {C.ATP_PER_REACTION} ATP\n")
    print(f"{'window':>7s} " + " ".join(f"{str(s_):>10s}" for s_, _ in primary))
    ratios_by_window = {}
    for w in C.WINDOWS:
        row, ratios = [], []
        for s_, r in primary:
            obs = r["curve"][str(w)]["observed"]
            if obs:
                x = r["history_core"] / obs
                ratios.append(x)
                row.append(f"{x:>10.1f}")
            else:
                row.append(f"{'-':>10s}")
        ratios_by_window[w] = ratios
        print(f"{w:>7d} " + " ".join(row))
    clears = sum(1 for w, rs in ratios_by_window.items()
                 if rs and sum(1 for x in rs if x >= C.DISCRIMINATION_FACTOR) >= 2)
    measurable = sum(1 for rs in ratios_by_window.values() if rs)
    print(f"\nH2 (history core >= {C.DISCRIMINATION_FACTOR}x the persisting set): "
          f"clears at {clears}/{measurable} windows where a set exists -> "
          f"{'holds' if measurable and clears > measurable / 2 else 'FAILS'}")
    print("H3: UNADJUDICATED — see RESULT.md. The cost margins measured while an "
          "earlier window rule was in force were -9%, -3%, -42% and -19%, i.e. "
          "sustaining reactions were if anything DEARER, and the size-matched "
          "control was noisier than the effect. No stable set survived the "
          "stronger null to price properly.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--record", action="store_true")
    ap.add_argument("--controls", action="store_true")
    args = ap.parse_args()

    ok, results = controls()
    for name, passed in results:
        print(("OK  " if passed else "FAIL"), name)
    if not ok:
        print("\nALIFE-EXP-008: CONTROLS FAILED — nothing measured, nothing recorded")
        return 1
    if args.controls:
        print("\nEXP-008-CONTROLS: ALL PASS")
        return 0

    result = measure()
    print()
    summarize(result)

    prov = al.provenance()
    receipt = {
        "experiment": "ALIFE-EXP-008",
        "corpus_fingerprint": C.fingerprint(),
        "inherited_from": "ALIFE-EXP-007",
        "frame": {"capacity": C.CAPACITY, "reactions": C.REACTIONS,
                  "budget_sweep": list(C.BUDGET_SWEEP), "seeds": list(C.SEEDS),
                  "windows": list(C.WINDOWS), "min_set_size": C.MIN_SET_SIZE,
                  "discrimination_factor": C.DISCRIMINATION_FACTOR,
                  "cost_margin": C.COST_MARGIN},
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
