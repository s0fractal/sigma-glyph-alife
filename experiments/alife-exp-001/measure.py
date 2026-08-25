#!/usr/bin/env python3
"""Run the pinned population and record what differs.

Check-only by default. `--record` rewrites `results.json`, and only after every
control in the preregistration has passed: a receipt written beside a failure is
worse than none, since it looks exactly like a receipt written beside a success.

Judged against `../ALIFE-EXP-001-anastomosis-preregistration.md`, which was
committed before this file existed. The corpus was committed before that.
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


def make_population(entries, store, seed, rebate_rate=0.0, transfers=False):
    econ = al.Economy(C.ATP_PER_AGENT * len(entries))
    agents = []
    for e in entries:
        root = al.put_term(e["term"], store)
        a = al.Agent(e["name"], root, 0)
        econ.endow(a, C.ATP_PER_AGENT)
        agents.append(a)
    return al.Population(store, agents, econ, random.Random(seed),
                         slice_atp=C.SLICE_ATP, rebate_rate=rebate_rate,
                         transfers=transfers, probe=True)


def run_population(entries, seed, ticks=C.TICKS):
    """Ticks until nothing is runnable, culling OFF: an archived agent stops
    contributing to the census, and a sharing number that rises because bodies
    were removed from the count is the confound this experiment is about."""
    store = fresh_store()
    pop = make_population(entries, store, seed)
    birth = pop.metrics()
    trace = [birth]
    for _ in range(ticks):
        if not any(a.status in al.RUNNABLE and a.atp > 0 for a in pop.agents):
            break
        trace.append(pop.step(cull=False))
    return pop, trace


def size_matched_null(total_nodes, seed):
    """A fresh population from the same generator, truncated to `total_nodes`
    node occurrences. Answers the only question that matters for H2: do terms of
    this size share this much anyway?"""
    rng = random.Random(seed)
    agents, nodes = [], 0
    store = fresh_store()
    i = 0
    while nodes < total_nodes:
        family = sorted(C.BUILDERS)[i % len(C.BUILDERS)]
        term = C.BUILDERS[family](rng)
        root = al.put_term(term, store)
        a = al.Agent(f"null-{i:03d}", root, 0)
        a.term = term                      # measured at birth: no ATP is spent here
        agents.append(a)
        nodes += sg.size(term)
        i += 1
    factor, total, unique = al.sharing_factor(agents)
    return {"agents": len(agents), "nodes_total": total, "nodes_unique": unique,
            "sharing_factor": factor}


def null_matched_agents(entries, seed):
    """POST HOC — NOT PREREGISTERED. The preregistered null fixes total node
    count, which lets the null population differ in agent COUNT: unreduced terms
    are larger, so matching nodes means drawing fewer, bigger agents, and a
    bigger tree repeats the three genesis atoms inside itself more often. This
    null fixes the agent count instead. It was written after the preregistered
    null returned an answer, and it is reported as what it is."""
    rng = random.Random(seed)
    store = fresh_store()
    agents = []
    for i, e in enumerate(entries):
        term = C.BUILDERS[e["family"]](rng)
        al.put_term(term, store)
        a = al.Agent(f"nullA-{i:03d}", sg.term_hash(term), 0)
        a.term = term
        agents.append(a)
    factor, total, unique = al.sharing_factor(agents)
    return {"agents": len(agents), "nodes_total": total, "nodes_unique": unique,
            "sharing_factor": factor}


def null_same_terms(entries):
    """POST HOC — NOT PREREGISTERED. The corpus itself, materialized but not
    reduced: what did THESE agents share before they ran? Neither size-matched
    nor agent-matched to the settled population — it is the same population at
    t=0 with its terms unfolded, which is the most direct form of the question
    and the least controlled."""
    store = fresh_store()
    agents = []
    for e in entries:
        al.put_term(e["term"], store)
        a = al.Agent(e["name"], sg.term_hash(e["term"]), 0)
        a.term = e["term"]
        agents.append(a)
    factor, total, unique = al.sharing_factor(agents)
    return {"agents": len(agents), "nodes_total": total, "nodes_unique": unique,
            "sharing_factor": factor}


def controls(entries):
    """Every control from the preregistration. Returns (ok, [(name, passed)])."""
    out = []

    # C1 — N copies of one term have sharing factor exactly N.
    store = fresh_store()
    root = al.put_term(entries[0]["term"], store)
    twins = [al.Agent(f"c1-{i}", root, 200) for i in range(8)]
    f0, _, _ = al.sharing_factor(twins)
    for t in twins:
        al.reduce_slice(t, store, 200)
    f1, _, _ = al.sharing_factor(twins)
    out.append(("C1 identical agents share everything, before and after",
                f0 == 8.0 and f1 == 8.0))

    # C2 — pairwise distinct literals share nothing.
    distinct = []
    for i in range(8):
        t = ("lit", sg.sha(b"distinct-%d" % i))
        al.put_term(t, store)
        a = al.Agent(f"c2-{i}", sg.term_hash(t), 0)
        a.term = t
        distinct.append(a)
    f2, _, _ = al.sharing_factor(distinct)
    out.append(("C2 distinct atoms share nothing", f2 == 1.0))

    # C3 — the driver is the oracle, on this corpus at this budget.
    store = fresh_store()
    agree = True
    for e in entries:
        root = al.put_term(e["term"], store)
        a = al.Agent(e["name"], root, C.ATP_PER_AGENT)
        al.reduce_slice(a, store, C.ATP_PER_AGENT, probe=True)
        r, spent = sg.eval_hash(root, C.ATP_PER_AGENT, store)
        if al.outcome_hash(a) != sg.term_hash(r) or a.spent != spent:
            agree = False
            print(f"  C3 divergence on {e['name']}")
    out.append(("C3 driver == eval_hash on every corpus term", agree))

    # C4 — conservation and the bound, at every tick of a mixed run.
    pop, trace = run_population(entries, seed=C.SEED, ticks=6)
    out.append(("C4 ledger balances and the bound holds at every tick",
                pop.economy.check(pop.agents) and pop.population_bound_holds()))

    # C5 — the corpus is the one that was pinned.
    out.append((f"C5 corpus fingerprint is {C.fingerprint()}",
                C.fingerprint() == PINNED_FINGERPRINT))
    return all(ok for _, ok in out), out


PINNED_FINGERPRINT = "53cc6da80f66d220"


def measure():
    entries = C.build()
    by_family = {}
    for e in entries:
        by_family.setdefault(e["family"], []).append(e)

    result = {"families": {}, "mixed": None, "null": None}

    for family in sorted(by_family):
        pop, trace = run_population(by_family[family], seed=C.SEED)
        result["families"][family] = {
            "birth": trace[0],
            "settled": trace[-1],
            "ticks": len(trace) - 1,
            "trace": trace,
        }

    pop, trace = run_population(entries, seed=C.SEED)
    result["mixed"] = {"birth": trace[0], "settled": trace[-1],
                       "ticks": len(trace) - 1, "trace": trace}
    result["null"] = size_matched_null(trace[-1]["nodes_total"], seed=C.SEED + 1)
    result["null_matched_agents"] = null_matched_agents(entries, seed=C.SEED + 2)
    result["null_same_terms"] = null_same_terms(entries)
    return result


def summarize(result):
    print(f"{'run':10s} {'birth':>8s} {'settled':>8s} {'Δ':>7s} "
          f"{'nodes':>7s} {'unique':>7s} {'spent':>8s} {'normal':>7s}")
    for name, r in list(result["families"].items()) + [("MIXED", result["mixed"])]:
        b, s = r["birth"], r["settled"]
        print(f"{name:10s} {b['sharing_factor']:8.3f} {s['sharing_factor']:8.3f} "
              f"{s['sharing_factor'] - b['sharing_factor']:+7.3f} "
              f"{s['nodes_total']:7d} {s['nodes_unique']:7d} "
              f"{s['atp_spent']:8d} {s['normal']:4d}/{s['agents']:<3d}")
    for label, key in (("NULL/size", "null"),
                       ("NULL/count*", "null_matched_agents"),
                       ("NULL/same*", "null_same_terms")):
        n = result[key]
        print(f"{label:10s} {'':8s} {n['sharing_factor']:8.3f} {'':7s} "
              f"{n['nodes_total']:7d} {n['nodes_unique']:7d} {'':8s} "
              f"{'':4s} {n['agents']:<3d}")
    print("* post hoc, not preregistered")
    n = result["null"]
    m = result["mixed"]["settled"]
    print()
    print(f"H1 (settled > birth, mixed): "
          f"{m['sharing_factor']:.3f} vs {result['mixed']['birth']['sharing_factor']:.3f} "
          f"-> {'holds' if m['sharing_factor'] > result['mixed']['birth']['sharing_factor'] else 'FAILS'}")
    print(f"H2 (settled > size-matched null): "
          f"{m['sharing_factor']:.3f} vs {n['sharing_factor']:.3f} "
          f"-> {'holds' if m['sharing_factor'] > n['sharing_factor'] else 'FAILS'}")
    for label, key in (("agent-count-matched", "null_matched_agents"),
                       ("same terms unreduced", "null_same_terms")):
        nn = result[key]
        print(f"   post hoc, {label}: {m['sharing_factor']:.3f} vs "
              f"{nn['sharing_factor']:.3f} -> "
              f"{'above' if m['sharing_factor'] > nn['sharing_factor'] else 'below'}")
    bound = result["mixed"]["settled"]["agents"] + result["mixed"]["settled"]["atp_spent"]
    print(f"H3 (bound vs what is stored): proved ceiling Σsize ≤ N + spent = "
          f"{bound}, actual Σsize = {m['nodes_total']}, distinct addresses = "
          f"{m['nodes_unique']} "
          f"({100.0 * m['nodes_unique'] / bound:.2f}% of the ceiling)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--record", action="store_true")
    args = ap.parse_args()

    ok, results = controls(C.build())
    for name, passed in results:
        print(("OK  " if passed else "FAIL"), name)
    if not ok:
        print("\nALIFE-EXP-001: CONTROLS FAILED — nothing measured, nothing recorded")
        return 1

    result = measure()
    print()
    summarize(result)

    # What goes in the receipt is what a REPLAY on another machine must be able
    # to reproduce byte for byte, so the oracle is identified by its digest and
    # never by its path, and the interpreter by MAJOR.MINOR — a patch release
    # that changes nothing about the arithmetic must not turn a replay red. The
    # full path and version are printed instead; they are context, not the claim.
    prov = al.provenance()
    receipt = {
        "experiment": "ALIFE-EXP-001",
        "corpus_fingerprint": C.fingerprint(),
        "corpus": {"per_family": C.PER_FAMILY, "families": sorted(C.BUILDERS),
                   "atp_per_agent": C.ATP_PER_AGENT, "slice_atp": C.SLICE_ATP,
                   "ticks": C.TICKS, "seed": C.SEED},
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
    print(f"python: {prov['python']} {platform.python_implementation()}")
    if args.record:
        (HERE / "results.json").write_text(
            json.dumps(receipt, indent=2, sort_keys=True) + "\n")
        print(f"\nrecorded {HERE / 'results.json'}")
    else:
        print("\n(check-only; pass --record to write results.json)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
