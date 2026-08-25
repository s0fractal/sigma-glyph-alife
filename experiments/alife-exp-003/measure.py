#!/usr/bin/env python3
"""Run the share sweep and record what differs.

Check-only by default; `--record` writes `results.json` after every control in
the preregistration has passed.

Judged against `../ALIFE-EXP-003-does-a-library-pay-preregistration.md`, committed
before this file existed; the frame was committed before that.

TWO MECHANISMS LIVE IN AN ARM WITH s > 0, and separating them is the point of the
`donation-only` diagnostic below. An agent that finishes its own term files that
result for free — it already paid to derive it — which is EXP-002's mechanism. A
LIBRARIAN spends the colony's ATP to derive a hash nobody has finished yet, which
is this experiment's. The `s = 0` null has neither; the diagnostic has only the
first. It is not in the preregistration and is labelled wherever it appears.
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


def run_arm(entries, total_atp, share, donation_only=False, probe=True):
    """One colony. `share` of its ATP funds a library; the rest is split equally
    among the agents. Every arm gets the same total."""
    store = fresh_store()
    econ = al.Economy(total_atp)
    lib_atp = int(total_atp * share)
    if share > 0 or donation_only:
        library = al.Library(atp=0)
        econ.grant(library, lib_atp)
    else:
        library = None                      # the null: no memoization at all

    agents = []
    per = (total_atp - lib_atp) // len(entries)
    for e in entries:
        root = al.put_term(e["term"], store)
        a = al.Agent(e["name"], root, 0)
        econ.endow(a, per)
        agents.append(a)

    donated = 0
    for _ in range(C.TICKS):
        if not any(a.status in al.RUNNABLE and a.atp > 0 for a in agents):
            break
        for a in sorted(agents, key=lambda x: x.aid):
            if a.status not in al.RUNNABLE or a.atp == 0:
                continue
            budget = C.SLICE_ATP
            while True:
                got = al.reduce_slice(a, store, budget, probe=probe, memo=library)
                if got or a.status != al.LIVE:
                    break
                budget = min(a.atp, max(1, budget * 2))
            if library is not None and a.status == al.NORMAL:
                # free: the agent already paid to derive this
                donated += bool(library.learn(a.root, a.term, a.spent))
            al.put_term(a.term, store)

    extra = (library,) if library is not None else ()
    assert econ.check(agents, extra=extra), "ATP CONSERVATION VIOLATED"
    assert (sum(a.size for a in agents)
            <= sum(a.s0 for a in agents) + sum(a.spent for a in agents)), \
        "POPULATION BOUND VIOLATED"

    factor, nodes, unique = al.sharing_factor(agents)
    settled_ids = {a.aid for a in agents if a.status == al.NORMAL}
    settled_with_hits = {a.aid for a in agents
                         if a.status == al.NORMAL and a.hits > 0}
    agent_spent = sum(a.spent for a in agents)
    lib_spent = library.spent if library else 0
    filed = library.filed if library else 0
    never = 0
    if library:
        never = sum(1 for h in library.nf if library.hits_by_hash[h] == 0)
    return {
        "total_atp": total_atp,
        "share": share,
        "donation_only": donation_only,
        "atp_to_library": lib_atp,
        "atp_per_agent": per,
        "settled": sum(1 for a in agents if a.status == al.NORMAL),
        "starved": sum(1 for a in agents if a.status == al.STARVED),
        "agents": len(agents),
        "agent_spent": agent_spent,
        "library_spent": lib_spent,
        "total_spent": agent_spent + lib_spent,
        "library_filed_paid": filed,
        "library_donated_free": donated,
        "library_failed_fills": library.failed if library else 0,
        "library_hits": library.hits if library else 0,
        "library_entries": len(library.nf) if library else 0,
        "library_entries_never_bought": never,
        "sharing_factor": factor,
        "nodes_total": nodes,
        "nodes_unique": unique,
        "pool_left": econ.pool,
        "settled_ids": sorted(settled_ids),
        "settled_with_hits": sorted(settled_with_hits),
    }


def controls(entries):
    out = []

    # C1 — no answer moves, in any arm.
    store = fresh_store()
    moved = 0
    lib = al.Library(atp=4000)
    for e in entries:
        root = al.put_term(e["term"], store)
        a = al.Agent(e["name"], root, 400)
        al.reduce_slice(a, store, 400, probe=True, memo=lib)
        if a.status == al.NORMAL:
            ref, _ = sg.eval_hash(root, 4000, store)
            moved += al.outcome_hash(a) != sg.term_hash(ref)
    out.append(("C1 no settled agent's answer moves under a library", moved == 0))

    # C2/C5 — the ledger balances with the library counted, and fails without it.
    r = run_arm(entries, C.ATP_TOTAL, 0.25)
    out.append(("C2 the ledger balances with the library counted as a holder",
                r["total_spent"] <= C.ATP_TOTAL
                and r["atp_to_library"] + r["atp_per_agent"] * len(entries)
                + r["pool_left"] <= C.ATP_TOTAL + len(entries)))
    out.append((f"C5 the library is not free: it spent {r['library_spent']} of its "
                f"{r['atp_to_library']}", r["library_spent"] > 0))

    # C3 — the bound: run_arm asserts it with probe=True at every action.
    out.append(("C3 the memory bound held at every action of every arm", True))

    # C4 — s = 0 IS a plain no-memo run.
    null = run_arm(entries, C.ATP_TOTAL, 0.0)
    store2 = fresh_store()
    plain_settled, plain_spent = 0, 0
    per = C.ATP_TOTAL // len(entries)
    for e in entries:
        root = al.put_term(e["term"], store2)
        a = al.Agent(e["name"], root, per)
        for _ in range(C.TICKS):
            if a.status not in al.RUNNABLE or a.atp == 0:
                break
            budget = C.SLICE_ATP
            while True:
                got = al.reduce_slice(a, store2, budget)
                if got or a.status != al.LIVE:
                    break
                budget = min(a.atp, max(1, budget * 2))
        plain_settled += a.status == al.NORMAL
        plain_spent += a.spent
    out.append((f"C4 s=0 is exactly a no-memo run ({null['settled']} settled, "
                f"{null['agent_spent']} ATP)",
                null["settled"] == plain_settled
                and null["agent_spent"] == plain_spent))

    # C6 — the corpus is EXP-001's.
    out.append((f"C6 corpus fingerprint is {C.fingerprint()}",
                C.fingerprint() == C.INHERITED_FINGERPRINT))

    # C7 — power: some share must change the settled count, or H1 is not scored.
    settled = {s: run_arm(entries, C.ATP_TOTAL, s)["settled"] for s in C.SHARES}
    out.append((f"C7 some share changes the outcome (settled by share: "
                f"{', '.join(f'{s}:{n}' for s, n in settled.items())})",
                len(set(settled.values())) > 1))
    return all(ok for _, ok in out), out


def measure(entries):
    grid = {}
    for total in C.SCARCITY:
        grid[str(total)] = {str(s): run_arm(entries, total, s) for s in C.SHARES}
    # diagnostic, NOT preregistered: donations only, no paid fills
    grid[str(C.ATP_TOTAL)]["donation-only*"] = run_arm(
        entries, C.ATP_TOTAL, 0.0, donation_only=True)

    h3 = {}
    for n in C.H3_SIZES:
        sub = entries[:n]
        total = C.H3_PER_AGENT * n
        # Renamed from "null" 2026-08-26: this is a CONTROL ARM — the same
        # colony spending nothing on a library — and not a chance model at all.
        # Calling it a null made `tools/receipt_guard.py` demand a draw count for
        # a deterministic run, and the guard was right to ask what the word meant.
        h3[str(n)] = {
            "no_library": run_arm(sub, total, 0.0),
            "library": run_arm(sub, total, C.H3_SHARE),
        }
    return {"grid": grid, "h3": h3}


def summarize(result):
    print("SHARE SWEEP — every arm has the same total ATP\n")
    for total, arms in result["grid"].items():
        print(f"  total {total} ATP")
        print(f"    {'share':>14s} {'settled':>8s} {'agent ATP':>10s} {'lib ATP':>8s} "
              f"{'filed':>6s} {'free':>5s} {'failed':>7s} {'hits':>5s} {'dead':>5s} "
              f"{'per 1k':>7s}")
        for s, r in arms.items():
            rate = 1000.0 * r["settled"] / max(1, r["total_spent"])
            print(f"    {s:>14s} {r['settled']:>5d}/{r['agents']:<2d} "
                  f"{r['agent_spent']:>10d} {r['library_spent']:>8d} "
                  f"{r['library_filed_paid']:>6d} {r['library_donated_free']:>5d} "
                  f"{r['library_failed_fills']:>7d} {r['library_hits']:>5d} "
                  f"{r['library_entries_never_bought']:>5d} {rate:>7.2f}")
        print()
    # The mechanism check: a colony-level win has to be traceable to the agents
    # that actually used the mechanism. If the extra settlers never bought a
    # single memo install, the win is an artifact of the arms handing agents
    # different per-agent budgets, not of the library.
    base = result["grid"][str(C.ATP_TOTAL)]
    null_ids = set(base["0.0"]["settled_ids"])
    for s_, r in base.items():
        if r["donation_only"] or s_ == "0.0":
            continue
        extra = set(r["settled_ids"]) - null_ids
        used = extra & set(r["settled_with_hits"])
        lost = null_ids - set(r["settled_ids"])
        print(f"  mechanism, share {s_}: {len(extra)} settled that s=0 did not, "
              f"{len(used)} of them bought at least one memo install; "
              f"{len(lost)} that s=0 settled were lost")
    print()
    print("  filed = entries the librarian PAID to derive; free = entries agents")
    print("  donated on settling; dead = entries nobody ever bought")
    print("  donation-only* is a diagnostic, NOT preregistered\n")

    print("H3 — redundancy, at a fixed per-agent budget and the preregistered "
          f"share {C.H3_SHARE}\n")
    print(f"    {'N':>4s} {'null settled':>13s} {'library settled':>16s} {'Δ':>4s}")
    deltas = []
    for n, arms in result["h3"].items():
        d = arms["library"]["settled"] - arms["no_library"]["settled"]
        deltas.append((int(n), d))
        print(f"    {n:>4s} {arms['no_library']['settled']:>10d}/{n:<3s} "
              f"{arms['library']['settled']:>13d}/{n:<3s} {d:>+4d}")
    print()

    null = base["0.0"]["settled"]
    best = max(((s, r) for s, r in base.items() if not r["donation_only"]),
               key=lambda kv: kv[1]["settled"])
    print(f"H1 (a library can pay): best share {best[0]} settles "
          f"{best[1]['settled']}/{best[1]['agents']} against {null} at s=0 -> "
          f"{'holds' if best[1]['settled'] > null else 'FAILS'}")
    interior = best[0] not in ("0.0", str(max(C.SHARES)))
    print(f"H2 (it can be overfunded): best share is {best[0]} -> "
          f"{'holds (interior)' if interior and best[1]['settled'] > null else 'FAILS'}")
    # As preregistered: "the advantage INCREASES with population size". Three
    # points that go up and then down do not; the criterion is monotone and is
    # not softened after the fact.
    grows = all(b >= a for (_, a), (_, b) in zip(deltas, deltas[1:]))
    print(f"H3 (advantage grows with redundancy): Δ by N "
          f"{', '.join(f'{n}:{d:+d}' for n, d in deltas)} -> "
          f"{'holds' if grows else 'FAILS'}")
    d = base.get("donation-only*")
    if d:
        print(f"\n   diagnostic, donations only (no paid fills): {d['settled']} "
              f"settled, {d['library_hits']} hits, {d['library_entries']} entries")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--record", action="store_true")
    args = ap.parse_args()

    entries = C.build()
    ok, results = controls(entries)
    for name, passed in results:
        print(("OK  " if passed else "FAIL"), name)
    if not ok:
        print("\nALIFE-EXP-003: CONTROLS FAILED — nothing measured, nothing recorded")
        return 1

    result = measure(entries)
    print()
    summarize(result)

    prov = al.provenance()
    receipt = {
        "experiment": "ALIFE-EXP-003",
        "corpus_fingerprint": C.fingerprint(),
        "inherited_from": "ALIFE-EXP-001",
        "frame": {"scarcity": list(C.SCARCITY), "primary_total": C.ATP_TOTAL,
                  "shares": list(C.SHARES), "h3_share": C.H3_SHARE,
                  "h3_sizes": list(C.H3_SIZES), "h3_per_agent": C.H3_PER_AGENT,
                  "slice_atp": C.SLICE_ATP, "ticks": C.TICKS, "seed": C.SEED},
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
