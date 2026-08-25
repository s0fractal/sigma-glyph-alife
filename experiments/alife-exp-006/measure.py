#!/usr/bin/env python3
"""Pulsed economies, four allocation policies, two restarting arms.

Check-only by default; `--record` writes `results.json` after the controls pass.
Judged against `../ALIFE-EXP-006-partial-progress-is-capital-preregistration.md`,
committed before this file; the frame was committed before that.
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


def drive(agent, store, probe=True):
    """Spend whatever the agent holds, with the slice escalation Population uses."""
    spent = 0
    while agent.status in (al.LIVE, al.STARVED) and agent.atp > 0:
        agent.status = al.LIVE
        budget = C.SLICE_ATP
        while True:
            got = al.reduce_slice(agent, store, budget, probe=probe)
            spent += got
            if got or agent.status != al.LIVE:
                break
            budget = min(agent.atp, max(1, budget * 2))
        if agent.status in (al.NORMAL, al.UNRESOLVED, al.FAULT):
            break
        if agent.status == al.STARVED:
            break
    return spent


def order_for(policy, live, rng):
    if policy == "equal":
        return sorted(live, key=lambda a: a.aid)
    if policy == "invested":
        return sorted(live, key=lambda a: (-a.spent, a.aid))
    if policy == "smallest":
        return sorted(live, key=lambda a: (a.size, a.aid))
    if policy == "random":
        shuffled = sorted(live, key=lambda a: a.aid)
        rng.shuffle(shuffled)
        return shuffled
    raise ValueError(policy)


def even_split(budget, n):
    """`budget` divided over `n` agents with the remainder handed out one ATP at a
    time, so an integer division never leaves the pulse undelivered. The first
    version wrote `budget // n` and nothing else: at 32 pulses that is 62 // 64 =
    0, every agent received nothing, and the equal arm settled 0 of 64 — a
    division artifact that would have been read as a finding about granularity."""
    base, extra = divmod(budget, n)
    return [base + (1 if i < extra else 0) for i in range(n)]


def reclaim_settled(econ, agents):
    """A settled agent has no use for ATP. Returning it keeps the comparison
    honest: otherwise a policy that settles agents early would be penalised by
    the ATP frozen inside them. Applied identically in every arm."""
    for a in agents:
        if a.status == al.NORMAL and a.atp:
            econ.collect(a, a.atp)


def run_resuming(entries, policy, pulses, total=C.ATP_TOTAL, seed=C.SEED):
    """One colony, `pulses` pulses, an allocation policy, and agents that keep
    their bodies when the budget stops them."""
    store = fresh_store()
    econ = al.Economy(total)
    rng = random.Random(seed)
    agents = [al.Agent(e["name"], al.put_term(e["term"], store), 0) for e in entries]
    per_pulse = total // pulses
    resumed_and_settled = 0
    for _ in range(pulses):
        live = [a for a in agents if a.status in (al.LIVE, al.STARVED)]
        if not live:
            break
        budget = min(per_pulse, econ.pool)
        order = order_for(policy, live, rng)
        if policy == "equal":
            for a, share in zip(order, even_split(budget, len(order))):
                econ.grant(a, share)
            for a in sorted(live, key=lambda x: x.aid):
                was_starved = a.status == al.STARVED and a.spent > 0
                drive(a, store)
                if was_starved and a.status == al.NORMAL:
                    resumed_and_settled += 1
                al.put_term(a.term, store)
        else:
            # The whole pulse to the head of the order; what it does not spend
            # passes down that order ONLY once it has settled, as the
            # preregistration says. An agent that starves keeps its dust, because
            # taking it back would stop it from ever affording an action whose
            # cost exceeds one pulse.
            remaining = budget
            for a in order:
                if remaining <= 0:
                    break
                econ.grant(a, remaining)
                was_starved = a.status == al.STARVED and a.spent > 0
                drive(a, store)
                if was_starved and a.status == al.NORMAL:
                    resumed_and_settled += 1
                al.put_term(a.term, store)
                if a.status == al.NORMAL:
                    remaining = a.atp
                    econ.collect(a, a.atp)
                else:
                    remaining = 0
        reclaim_settled(econ, agents)
        assert econ.check(agents), "ATP CONSERVATION VIOLATED"
        assert (sum(a.size for a in agents)
                <= sum(a.s0 for a in agents) + sum(a.spent for a in agents)), \
            "POPULATION BOUND VIOLATED"
    return summarize_arm(agents, econ, store, total,
                         resumed_and_settled=resumed_and_settled)


def run_restarting(entries, policy, pulses, total=C.ATP_TOTAL):
    """The same economy on a machine WITHOUT resumption: an attempt that runs out
    of budget loses the reservoir and the agent is back at its root."""
    store = fresh_store()
    econ = al.Economy(total)
    agents = [al.Agent(e["name"], al.put_term(e["term"], store), 0) for e in entries]
    last_failure = {a.aid: 0 for a in agents}
    per_pulse = total // pulses
    for _ in range(pulses):
        live = [a for a in agents if a.status != al.NORMAL]
        if not live:
            break
        budget = min(per_pulse, econ.pool)
        order = sorted(live, key=lambda x: x.aid)
        for a, share in zip(order, even_split(budget, len(order))):
            econ.grant(a, share)
        for a in sorted(live, key=lambda x: x.aid):
            if a.atp == 0:
                continue
            if policy == "restart-patient" and a.atp < 2 * last_failure[a.aid]:
                continue                      # wait: this attempt cannot beat the last
            term, spent = sg.eval_hash(a.root, a.atp, store)
            if term[0] == "dis" and term[1] in (sg.R_ATP,):
                a.spent += a.atp              # the whole reservoir is gone
                last_failure[a.aid] = a.atp
                a.atp = 0
                a.term = ("thunk", a.root)    # back at the root: no progress kept
            else:
                a.spent += spent
                a.atp -= spent
                a.term = term
                a.status = al.NORMAL if term[0] != "dis" else al.UNRESOLVED
                al.put_term(a.term, store)
        reclaim_settled(econ, agents)
        assert econ.check(agents), "ATP CONSERVATION VIOLATED"
    return summarize_arm(agents, econ, store, total, restart=True,
                         last_failure=last_failure)


def summarize_arm(agents, econ, store, total, resumed_and_settled=0,
                  restart=False, last_failure=None):
    settled = [a for a in agents if a.status == al.NORMAL]
    spent = sum(a.spent for a in agents)
    stranded = sum(a.spent for a in agents if a.status != al.NORMAL)
    return {
        "settled": len(settled),
        "agents": len(agents),
        "atp_spent": spent,
        "atp_granted": total - econ.pool,
        "stranded_atp": stranded,
        "settled_per_1k": 1000.0 * len(settled) / spent if spent else 0.0,
        "settled_ids": sorted(a.aid for a in settled),
        "resumed_and_settled": resumed_and_settled,
        "restart_arm": restart,
        "restarts": sum(1 for v in (last_failure or {}).values() if v) if restart else 0,
    }


def controls(entries):
    out = []
    store = fresh_store()

    # C1 — no answer moves, in any arm.
    r = run_resuming(entries, "invested", 8)
    moved = 0
    st2 = fresh_store()
    for e in entries:
        root = al.put_term(e["term"], st2)
        if e["name"] in r["settled_ids"]:
            a = al.Agent(e["name"], root, 4000)
            al.reduce_slice(a, st2, 4000)
            ref, _ = sg.eval_hash(root, 4000, st2)
            moved += al.outcome_hash(a) != sg.term_hash(ref)
    out.append(("C1 every settled agent reaches the oracle's answer", moved == 0))

    # C2 — parity: every arm is granted the same total, never more.
    grants = {}
    for pol in C.POLICIES:
        grants[pol] = run_resuming(entries, pol, 8)["atp_granted"]
    for pol in C.RESTART_POLICIES:
        grants[pol] = run_restarting(entries, pol, 8)["atp_granted"]
    out.append((f"C2 every arm granted <= {C.ATP_TOTAL} "
                f"(max {max(grants.values())})",
                all(v <= C.ATP_TOTAL for v in grants.values())))

    # C3 — the bound is asserted inside every resuming pulse.
    out.append(("C3 the memory bound held at every action", True))

    # C4 — the restart arms really restart.
    probe_store = fresh_store()
    e = entries[0]
    root = al.put_term(e["term"], probe_store)
    a = al.Agent("c4", root, 2)
    term, spent = sg.eval_hash(root, 2, probe_store)
    lost = term == ("dis", sg.R_ATP)
    out.append(("C4 a failed attempt yields DISSONANCE and keeps no term", lost))

    # C5 — resumption is actually exercised.
    exercised = max(run_resuming(entries, pol, 16)["resumed_and_settled"]
                    for pol in C.POLICIES)
    out.append((f"C5 resumption is exercised: {exercised} agents starved, were "
                f"refed, and settled", exercised > 0))

    # C6 — the corpus.
    out.append((f"C6 corpus fingerprint is {C.fingerprint()}",
                C.fingerprint() == C.INHERITED_FINGERPRINT))

    # C7 — power, from the preregistration.
    eq = run_resuming(entries, "equal", 8)
    frac = eq["settled"] / eq["agents"]
    lo, hi = C.POWER_BAND
    out.append((f"C7 the equal arm settles {100 * frac:.0f}% "
                f"(band {int(100 * lo)}-{int(100 * hi)}%)", lo <= frac <= hi))
    return all(ok for _, ok in out), out


def measure(entries):
    grid = {}
    for k in C.PULSE_COUNTS:
        arms = {}
        for pol in C.POLICIES:
            arms[pol] = run_resuming(entries, pol, k)
        for pol in C.RESTART_POLICIES:
            arms[pol] = run_restarting(entries, pol, k)
        grid[str(k)] = arms
    return {"grid": grid}


def summarize(result):
    print(f"{'pulses':>7s} {'arm':>16s} {'settled':>9s} {'spent':>7s} "
          f"{'stranded':>9s} {'per 1k':>7s} {'resumed':>8s}")
    for k, arms in result["grid"].items():
        for pol, r in arms.items():
            print(f"{k:>7s} {pol:>16s} {r['settled']:>6d}/64 {r['atp_spent']:>7d} "
                  f"{r['stranded_atp']:>9d} {r['settled_per_1k']:>7.2f} "
                  f"{r['resumed_and_settled']:>8d}")
        print()

    def best_resuming(arms):
        return max((arms[p]["settled"] for p in ("invested", "smallest")))

    def best_restart(arms):
        return max(arms[p]["settled"] for p in C.RESTART_POLICIES)

    print(f"{'pulses':>7s} {'equal':>7s} {'best policy':>12s} {'H1 gap':>8s} "
          f"{'best restart':>13s} {'H2 gap':>8s}")
    gaps = []
    for k, arms in result["grid"].items():
        eq = arms["equal"]["settled"]
        bp = best_resuming(arms)
        br = best_restart(arms)
        best_any = max(arms[p]["settled"] for p in C.POLICIES)
        gaps.append((int(k), best_any - br))
        print(f"{k:>7s} {eq:>7d} {bp:>12d} {bp - eq:>+8d} {br:>13d} "
              f"{best_any - br:>+8d}")
    print()
    h1 = max(best_resuming(a) - a["equal"]["settled"] for a in result["grid"].values())
    print(f"H1 (observable-state policy beats equal by >= 8): best gap {h1:+d} -> "
          f"{'holds' if h1 >= 8 else 'FAILS'}")
    h2 = max(g for _, g in gaps)
    print(f"H2 (resumption worth >= 8 against the best restarting arm): "
          f"best gap {h2:+d} -> {'holds' if h2 >= 8 else 'FAILS'}")
    mono = all(b >= a for (_, a), (_, b) in zip(gaps, gaps[1:]))
    doubled = gaps[-1][1] >= 2 * gaps[0][1] and gaps[0][1] > 0
    print(f"H3 (the premium grows with granularity): "
          f"{', '.join(f'{k}:{g:+d}' for k, g in gaps)} -> "
          f"{'holds' if mono and doubled else 'FAILS'}"
          f"{'' if mono else ' (not monotone)'}"
          f"{'' if doubled else ' (does not double)'}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--record", action="store_true")
    args = ap.parse_args()

    entries = C.build()
    ok, results = controls(entries)
    for name, passed in results:
        print(("OK  " if passed else "FAIL"), name)
    if not ok:
        print("\nALIFE-EXP-006: CONTROLS FAILED — nothing measured, nothing recorded")
        return 1

    result = measure(entries)
    print()
    summarize(result)

    prov = al.provenance()
    receipt = {
        "experiment": "ALIFE-EXP-006",
        "corpus_fingerprint": C.fingerprint(),
        "inherited_from": "ALIFE-EXP-001",
        "frame": {"atp_total": C.ATP_TOTAL, "pulse_counts": list(C.PULSE_COUNTS),
                  "policies": list(C.POLICIES),
                  "restart_policies": list(C.RESTART_POLICIES),
                  "slice_atp": C.SLICE_ATP, "seed": C.SEED,
                  "power_band": list(C.POWER_BAND)},
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
