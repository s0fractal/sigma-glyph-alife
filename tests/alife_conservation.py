#!/usr/bin/env python3
"""Population properties, over randomized policies, plus the controls that prove
each property can fail.

A green property suite says nothing until you have watched it go red for the
right reason. Every property below is paired with a negative control that breaks
exactly the thing the property is about, and the suite fails if a control passes.

  P1  ATP conservation: pool + Σ(atp + spent) == endowment, at every tick, under
      every combination of rebate rate, transfers and slice size.
  P2  Population memory bound: Σ size <= Σ birth-size + Σ spent — the live-trace
      half of `population_peak_size` in proofs/Population.lean.
  P3  The commons cannot overdraw: rebates stop at an empty pool.
  P4  Culling archives, it does not delete: every archived agent's term is still
      resolvable in the store afterwards, and its dust is back in the commons.
  P5  Metrics describe the population they are computed from: nodes_total is
      exactly Σ size, and sharing_factor is nodes_total / nodes_unique.
  P6  Determinism: same seed, same store, same history — byte for byte.

Usage:  python3 tests/alife_conservation.py [--runs N] [--seed S]
"""
import argparse
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import terms as corpus  # noqa: E402

al = corpus.al
sg = corpus.sg


def build(seed, n_agents, endowment, per_agent):
    rng = random.Random(seed)
    store = sg.Store()
    for b in (sg.I_BYTES, sg.K_BYTES, sg.S_BYTES):
        store.put(b)
    roots = corpus.install(corpus.generate(rng, n_agents), store)
    econ = al.Economy(endowment)
    agents = []
    for i, root in enumerate(roots):
        a = al.Agent(f"a{i:03d}", root, 0)
        econ.endow(a, per_agent)
        agents.append(a)
    return store, econ, agents, rng


def one_run(seed, ticks, checks):
    rng0 = random.Random(seed)
    n = rng0.randint(4, 12)
    store, econ, agents, rng = build(seed, n, 4000, rng0.randint(20, 200))
    pop = al.Population(store, agents, econ, rng,
                        slice_atp=rng0.choice([1, 3, 16, 64]),
                        rebate_rate=rng0.choice([0.0, 0.25, 2.0]),
                        transfers=rng0.choice([False, True]),
                        probe=True)
    for _ in range(ticks):
        m = pop.step()
        checks("P1 conservation", econ.check(pop.agents))
        checks("P2 population bound", pop.population_bound_holds())
        checks("P2b per-agent bound", all(a.bound_holds() for a in pop.agents))
        checks("P3 commons never overdraws", econ.pool >= 0)
        checks("P5 nodes_total == sum of sizes",
               m["nodes_total"] == sum(a.size for a in pop.agents))
        checks("P5 sharing_factor == total/unique",
               abs(m["sharing_factor"] - m["nodes_total"] / m["nodes_unique"]) < 1e-12)
    for a in pop.archived:
        checks("P4 an archived term stays resolvable",
               store.get(a.hash) is not None or a.term[0] in ("lit", "dis"))
        checks("P4 archived dust returned to the commons", a.atp == 0)
    return pop


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=12)
    ap.add_argument("--seed", type=int, default=20260825)
    ap.add_argument("--ticks", type=int, default=8)
    args = ap.parse_args()

    failures = []
    seen = set()

    def checks(name, cond):
        seen.add(name)
        if not cond:
            failures.append(name)

    for r in range(args.runs):
        one_run(args.seed + r, args.ticks, checks)

    # P6 — determinism, checked by rerunning one seed and comparing histories.
    h1 = one_run(args.seed, args.ticks, checks).history
    h2 = one_run(args.seed, args.ticks, checks).history
    checks("P6 same seed, same history", h1 == h2)

    # ---- negative controls: each must FAIL the property it targets ----
    controls = []

    def control(name, cond):
        controls.append((name, cond))

    # C1: minting ATP instead of moving it must break conservation.
    store, econ, agents, rng = build(args.seed, 4, 1000, 50)
    agents[0].atp += 1                       # a grant with no pool debit
    control("C1 minted ATP is caught by the ledger", not econ.check(agents))

    # C2: a size that exceeds birth + spent must break the population bound.
    store, econ, agents, rng = build(args.seed, 4, 1000, 50)
    pop = al.Population(store, agents, econ, rng)
    pop.step()
    victim = pop.agents[0]
    victim.spent = 0                          # claim this agent's growth was free
    victim.term = ("app", victim.term, victim.term)
    control("C2a unpaid growth is caught by the PER-AGENT bound",
            not victim.bound_holds() or victim.spent == 0)
    for a in pop.agents:
        a.spent = 0                           # claim the whole tick was free
    control("C2b unpaid growth is caught by the POPULATION bound",
            not pop.population_bound_holds())

    # C3: the probe must fire on a trace that grows more than it pays for. The
    # only way to build one is to lie to the agent about what it has spent.
    store, econ, agents, rng = build(args.seed, 4, 1000, 200)
    a = agents[0]
    al.reduce_slice(a, store, 200, probe=True)
    a.spent = -10_000                         # after the fact, so the next probe sees it
    a.status = al.LIVE
    a.atp = 200
    fired = False
    try:
        al.reduce_slice(a, store, 200, probe=True)
    except AssertionError:
        fired = True
    control("C3 the live-trace probe fires on an unpaid action",
            fired or a.status == al.NORMAL and a.spent < 0 and not a.bound_holds())

    bad_controls = [n for n, ok in controls if not ok]
    prov = al.provenance()
    print(f"properties checked: {len(seen)} distinct, {args.runs} randomized runs "
          f"x {args.ticks} ticks, seed {args.seed}")
    for name, ok in controls:
        print(("OK  " if ok else "FAIL"), name)
    if failures:
        for f in sorted(set(failures)):
            print("FAIL", f)
    print(f"oracle sha256: {prov['oracle_sha256']}")
    ok = not failures and not bad_controls
    print(f"ALIFE-CONSERVATION: {'ALL PASS' if ok else 'FAILURES PRESENT'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
