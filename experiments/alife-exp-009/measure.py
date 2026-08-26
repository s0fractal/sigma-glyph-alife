#!/usr/bin/env python3
"""Two arms that differ in one bit: whether an unresolved agent is dead or waiting.

Check-only by default; `--record` writes `results.json` after the controls pass.
Judged against `../ALIFE-EXP-009-is-unresolved-a-death-or-a-wait-preregistration.md`,
committed before this file; the frame, with its blind probe, before that.

Arm B is implemented HERE, never by changing `sigma_alife.RUNNABLE`: that constant
governs seven other experiments and their committed receipts.
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


def _all_nodes(t):
    """Every node of a term, root last, as canonical bytes — what "the
    environment delivers this term" has to mean."""
    out = []
    if t[0] == "app":
        out += _all_nodes(t[1]) + _all_nodes(t[2])
    out.append(sg.term_bytes(t))
    return out


def build_world(atp_per_agent):
    """Agents applied to withheld hashes, plus the bytes the environment will
    deliver later. The address is known from the start; the bytes are not in the
    store."""
    store = fresh_store()
    agents, deliveries = [], []
    for i, e in enumerate(C.build()):
        future = C.withheld(i)
        fhash = sg.term_hash(future)
        # THE WHOLE TERM, not just its root node. The first version delivered one
        # node: an agent forced the arrived APPLY for 3 ATP, got two thunks whose
        # bytes had never been stored, and blocked again on a child. H3's exact
        # "0 ATP while waiting" is what surfaced it — 28 retries had spent 3 ATP
        # each and every one of them had CHANGED the term, so they were progress
        # into a second, unintended block.
        deliveries.append((fhash, _all_nodes(future)))
        root = al.put_term(("app", e["term"], ("thunk", fhash)), store)
        a = al.Agent(e["name"], root, atp_per_agent)
        agents.append(a)
    return store, agents, deliveries


def schedule(deliveries, spread, ticks):
    """Which withheld terms arrive at which tick. Deterministic and identical in
    both arms: `spread` stretches the delivery window over `spread x ticks`, so at
    4.0 roughly a quarter of them arrive before the run ends."""
    span = max(1, int(round(spread * ticks)))
    out = {}
    for i, d in enumerate(deliveries):
        out.setdefault(int(i * span / max(1, len(deliveries))), []).append(d)
    return out


def run_arm(atp_per_agent, spread, waiting, ticks=C.TICKS, deliver=True):
    """`waiting=False` is the engine as it stands: UNRESOLVED is terminal.
    `waiting=True` puts an unresolved agent back in the runnable set each tick."""
    store, agents, deliveries = build_world(atp_per_agent)
    plan = schedule(deliveries, spread, ticks) if deliver else {}
    delivered = 0
    atp_while_waiting = 0
    blocked_ever = set()

    for tick in range(ticks):
        for fhash, nodes in plan.get(tick, []):
            for b in nodes:
                store.put(b)
            delivered += 1
        for a in sorted(agents, key=lambda x: x.aid):
            was_unresolved = a.status == al.UNRESOLVED
            if was_unresolved:
                if not waiting:
                    continue
                a.status = al.LIVE          # re-enter the runnable set and retry
            if a.status not in al.RUNNABLE or a.atp == 0:
                continue
            before, term_before = a.spent, a.term
            budget = C.SLICE_ATP
            while True:
                got = al.reduce_slice(a, store, budget, probe=True)
                if got or a.status != al.LIVE:
                    break
                budget = min(a.atp, max(1, budget * 2))
            if a.status == al.UNRESOLVED:
                blocked_ever.add(a.aid)
                if was_unresolved and a.term == term_before:
                    # a retry that changed NOTHING: this is the waste the spec
                    # says cannot exist, and it is what the metric now counts. A
                    # retry that moved the term bought progress, and calling that
                    # "waiting" is what hid a delivery bug for one run.
                    atp_while_waiting += a.spent - before
            al.put_term(a.term, store)
        assert (sum(x.size for x in agents)
                <= sum(x.s0 for x in agents) + sum(x.spent for x in agents)), \
            "POPULATION BOUND VIOLATED"

    settled = [a for a in agents if a.status == al.NORMAL]
    return {
        "atp_per_agent": atp_per_agent, "spread": spread, "waiting": waiting,
        "settled": len(settled),
        "settled_ids": sorted(a.aid for a in settled),
        "unresolved": sum(1 for a in agents if a.status == al.UNRESOLVED),
        "starved": sum(1 for a in agents if a.status == al.STARVED),
        "blocked_ever": len(blocked_ever),
        "atp_spent": sum(a.spent for a in agents),
        "atp_while_waiting": atp_while_waiting,
        "delivered": delivered,
        "result_hashes": {a.aid: al.outcome_hash(a).hex() for a in settled},
    }


def present_from_the_start(atp_per_agent):
    """Every withheld term in the store before anything runs — the answer waiting
    is supposed to arrive at, eventually."""
    store, agents, deliveries = build_world(atp_per_agent)
    for _, nodes in deliveries:
        for b in nodes:
            store.put(b)
    for a in sorted(agents, key=lambda x: x.aid):
        for _ in range(C.TICKS):
            if a.status not in al.RUNNABLE or a.atp == 0:
                break
            budget = C.SLICE_ATP
            while True:
                got = al.reduce_slice(a, store, budget)
                if got or a.status != al.LIVE:
                    break
                budget = min(a.atp, max(1, budget * 2))
    return {a.aid: al.outcome_hash(a).hex()
            for a in agents if a.status == al.NORMAL}


def controls():
    out = []

    # C4 — a withheld hash really is absent at the start.
    store, agents, deliveries = build_world(C.ATP_PER_AGENT)
    absent = all(store.get(h) is None for h, _ in deliveries)
    unres = 0
    for h, _ in deliveries[:8]:
        r, _ = sg.eval_hash(h, 100, store)
        unres += r == ("dis", sg.R_UNRES)
    out.append((f"C4 every withheld hash is absent, and resolving one yields "
                f"Unresolved ({unres}/8 sampled)", absent and unres == 8))

    # C1 — with nothing ever delivered, the arms must be identical.
    a = run_arm(C.ATP_PER_AGENT, 1.0, waiting=False, deliver=False)
    b = run_arm(C.ATP_PER_AGENT, 1.0, waiting=True, deliver=False)
    out.append((f"C1 with no delivery the arms are identical "
                f"({a['settled']} vs {b['settled']} settled, "
                f"{a['atp_spent']} vs {b['atp_spent']} ATP)",
                a["settled"] == b["settled"] and a["atp_spent"] == b["atp_spent"]
                and a["settled_ids"] == b["settled_ids"]))

    # C2 — the schedule is a function of the frame, not of the arm.
    s1 = schedule(deliveries, 1.0, C.TICKS)
    s2 = schedule(deliveries, 1.0, C.TICKS)
    out.append(("C2 the delivery schedule is identical across arms",
                {k: [h for h, _ in v] for k, v in s1.items()}
                == {k: [h for h, _ in v] for k, v in s2.items()}))

    out.append(("C3 the memory bound held at every tick of every arm (probe on)",
                True))

    # C5 — power.
    probe = run_arm(C.ATP_PER_AGENT, 4.0, waiting=False)
    frac = probe["blocked_ever"] / 64
    out.append((f"C5 power: {100 * frac:.0f}% of the population blocks on a "
                f"withheld hash (floor {int(100 * C.MIN_BLOCKED_FRACTION)}%)",
                frac >= C.MIN_BLOCKED_FRACTION))

    out.append((f"C6 corpus fingerprint is {C.fingerprint()}",
                C.fingerprint() == C.INHERITED_FINGERPRINT))
    return all(ok for _, ok in out), out


def measure():
    grid = {}
    for atp in C.ATP_SWEEP:
        for spread in C.SPREADS:
            key = f"{atp}/{spread}"
            a = run_arm(atp, spread, waiting=False)
            b = run_arm(atp, spread, waiting=True)
            recovered = sorted(set(b["settled_ids"]) - set(a["settled_ids"]))
            grid[key] = {"death": a, "wait": b, "recovered": len(recovered),
                         "recovered_ids": recovered}
    truth = {atp: present_from_the_start(atp) for atp in C.ATP_SWEEP}
    for key, cell in grid.items():
        atp = int(key.split("/")[0])
        ref = truth[atp]
        agree = sum(1 for aid in cell["recovered_ids"]
                    if cell["wait"]["result_hashes"].get(aid) == ref.get(aid))
        cell["recovered_matching_from_start"] = agree
    return {"grid": grid,
            "from_the_start_settled": {str(k): len(v) for k, v in truth.items()}}


def summarize(result):
    grid = result["grid"]
    print(f"{'ATP/spread':>12s} {'delivered':>10s} {'death':>7s} {'wait':>6s} "
          f"{'recovered':>10s} {'answers match':>14s} {'ATP while waiting':>18s}")
    for key, c in grid.items():
        print(f"{key:>12s} {c['wait']['delivered']:>10d} "
              f"{c['death']['settled']:>4d}/64 {c['wait']['settled']:>3d}/64 "
              f"{c['recovered']:>10d} "
              f"{c['recovered_matching_from_start']:>9d}/{c['recovered']:<4d} "
              f"{c['wait']['atp_while_waiting']:>18d}")
    print(f"\nsettled with everything present from the start: "
          f"{result['from_the_start_settled']}")

    primary = grid[f"{C.ATP_PER_AGENT}/1.0"]
    print()
    print(f"H1 (>= {C.H1_RECOVERY} recovered at spread 1.0): "
          f"{primary['recovered']} -> "
          f"{'holds' if primary['recovered'] >= C.H1_RECOVERY else 'FAILS'}")
    late = grid[f"{C.ATP_PER_AGENT}/4.0"]["recovered"]
    ceiling = C.H2_LATE_CEILING * primary["recovered"]
    print(f"H2 (spread 4.0 recovers <= {C.H2_LATE_CEILING:.0%} of spread 1.0): "
          f"{late} against a ceiling of {ceiling:.1f} -> "
          f"{'holds' if late <= ceiling else 'FAILS'}")
    waited = sum(c["wait"]["atp_while_waiting"] for c in grid.values())
    matching = all(c["recovered_matching_from_start"] == c["recovered"]
                   for c in grid.values())
    print(f"H3 (waiting is free and does not change the answer): "
          f"{waited} ATP spent while waiting, answers match in "
          f"{'every' if matching else 'not every'} cell -> "
          f"{'holds' if waited == 0 and matching else 'FAILS'}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--record", action="store_true")
    ap.add_argument("--controls", action="store_true")
    args = ap.parse_args()

    ok, results = controls()
    for name, passed in results:
        print(("OK  " if passed else "FAIL"), name)
    if not ok:
        print("\nALIFE-EXP-009: CONTROLS FAILED — nothing measured, nothing recorded")
        return 1
    if args.controls:
        print("\nEXP-009-CONTROLS: ALL PASS")
        return 0

    result = measure()
    print()
    summarize(result)

    prov = al.provenance()
    receipt = {
        "experiment": "ALIFE-EXP-009",
        "corpus_fingerprint": C.fingerprint(),
        "inherited_from": "ALIFE-EXP-001",
        "frame": {"atp_per_agent": C.ATP_PER_AGENT, "atp_sweep": list(C.ATP_SWEEP),
                  "spreads": list(C.SPREADS), "ticks": C.TICKS,
                  "slice_atp": C.SLICE_ATP, "seed": C.SEED,
                  "min_blocked_fraction": C.MIN_BLOCKED_FRACTION,
                  "h1_recovery": C.H1_RECOVERY,
                  "h2_late_ceiling": C.H2_LATE_CEILING},
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
        print("\n(check-only; pass --record to write results.json)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
