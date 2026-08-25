#!/usr/bin/env python3
"""Run both arms and record what differs.

Check-only by default. `--record` rewrites `results.json`, and only after every
control in the preregistration has passed.

Judged against `../ALIFE-EXP-002-does-sharing-pay-preregistration.md`, committed
before this file existed; the corpus was committed before that and is EXP-001's,
pinned by fingerprint.

ONE DESIGN DETAIL THE PREREGISTRATION DID NOT FIX, and it decides whether Part B
can show anything at all: which of a parent's hashes a child inherits. A child
grafted with the parent's CURRENT TERM inherits a phenotype no memo has an entry
for; a child grafted with the parent's ROOT inherits an unevaluated genome, which
is the only graft a memo can ever reach. Part B uses the root in BOTH arms, so it
biases neither, and it is named here rather than left in the code.
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


# ---------------- Part A: energy ----------------
def drive(agent, store, memo, ticks=C.TICKS):
    """One agent, the same slice policy `Population.phase_reduce` uses: a slice
    that buys nothing is doubled up to the reservoir. Used by the `private` arm,
    where agents are independent by construction, so running them one at a time
    and interleaving them give the same result."""
    for _ in range(ticks):
        if agent.status not in al.RUNNABLE or agent.atp == 0:
            break
        budget = C.SLICE_ATP
        while True:
            got = al.reduce_slice(agent, store, budget, probe=True, memo=memo)
            if got or agent.status != al.LIVE:
                break
            budget = min(agent.atp, max(1, budget * 2))
        if memo is not None and agent.status == al.NORMAL:
            memo.learn(agent.root, agent.term, agent.spent)
        al.put_term(agent.term, store)


def metrics_of(agents, econ, memo_stats):
    factor, total, unique = al.sharing_factor(agents)
    spent = sum(a.spent for a in agents)
    m = {
        "agents": len(agents),
        "normal": sum(1 for a in agents if a.status == al.NORMAL),
        "starved": sum(1 for a in agents if a.status == al.STARVED),
        "sharing_factor": factor,
        "nodes_total": total,
        "nodes_unique": unique,
        "atp_spent": spent,
        "atp_held": sum(a.atp for a in agents),
        "atp_pool": econ.pool,
        "diversity_bits": al.structural_diversity(agents),
        "peak_sum": sum(a.peak for a in agents),
    }
    m.update(memo_stats)
    m["ceiling"] = m["agents"] + m["atp_spent"]
    m["ceiling_occupancy"] = m["nodes_unique"] / m["ceiling"] if m["ceiling"] else 0.0
    return m


def run_arm(entries, arm, seed=C.SEED):
    """arm: 'off' | 'private' | 'shared'.

    'private' gives every agent its own memo, so only repetition INSIDE one agent
    can pay. 'shared' gives the population one. The difference between them is the
    inter-agent saving — anastomosis, priced — and it is the only number in Part A
    that is about sharing rather than about repetition.
    """
    store = fresh_store()
    econ = al.Economy(C.ATP_PER_AGENT * len(entries))
    agents = []
    for e in entries:
        root = al.put_term(e["term"], store)
        a = al.Agent(e["name"], root, 0)
        econ.endow(a, C.ATP_PER_AGENT)
        agents.append(a)

    if arm == "private":
        hits = misses = avoided = 0
        for a in sorted(agents, key=lambda x: x.aid):
            memo = al.Memo()
            drive(a, store, memo)
            hits, misses = hits + memo.hits, misses + memo.misses
            avoided += memo.avoided
        stats = {"memo_hits": hits, "memo_misses": misses, "memo_avoided": avoided}
    else:
        memo = al.Memo() if arm == "shared" else None
        pop = al.Population(store, agents, econ, random.Random(seed),
                            slice_atp=C.SLICE_ATP, probe=True, memo=memo)
        for _ in range(C.TICKS):
            if not any(x.status in al.RUNNABLE and x.atp > 0 for x in agents):
                break
            pop.step(cull=False)
        stats = {"memo_hits": memo.hits if memo else 0,
                 "memo_misses": memo.misses if memo else 0,
                 "memo_avoided": memo.avoided if memo else 0}

    assert econ.check(agents), f"ATP CONSERVATION VIOLATED in arm {arm}"
    return metrics_of(agents, econ, stats)


def composites(entries, store):
    """POST HOC — NOT PREREGISTERED. A population in which agents DEMAND each
    other's addresses: each composite is `corpus_i applied to corpus_j`, so
    reducing it forces two corpus roots by hash.

    It exists because Part A on the preregistered corpus measured almost nothing,
    and the reason is worth separating from the hypothesis: a memo is keyed by
    what an agent ASKS FOR, not by what it contains. Sixty-four agents can hold a
    great deal of structure in common and still never utter each other's
    addresses, in which case there is nothing for a shared memo to answer. This
    arm supplies the missing demand path and changes nothing else."""
    out = []
    n = len(entries)
    for i, e in enumerate(entries):
        j = (i * 7 + 3) % n
        root_i = al.put_term(entries[i]["term"], store)
        root_j = al.put_term(entries[j]["term"], store)
        term = ("app", ("thunk", root_i), ("thunk", root_j))
        out.append({"family": "composite", "name": f"composite-{i:02d}",
                    "term": term})
    return out


def run_composite_arm(entries, arm):
    """The corpus agents AND the composites that demand them, in one store."""
    store = fresh_store()
    all_entries = list(entries) + composites(entries, store)
    return run_arm(all_entries, arm)


def part_a(entries):
    by_family = {}
    for e in entries:
        by_family.setdefault(e["family"], []).append(e)
    out = {}
    for name, group in list(sorted(by_family.items())) + [("mixed", entries)]:
        out[name] = {arm: run_arm(group, arm) for arm in ("off", "private", "shared")}
    out["composite*"] = {arm: run_composite_arm(entries, arm)
                         for arm in ("off", "private", "shared")}
    return out


# ---------------- Part B: selection ----------------
def part_b_arm(entries, seed, memo_on):
    """One generational run. The two arms differ in exactly one bit: whether a
    demanded hash whose normal form is known can be bought at `size(nf)` instead
    of being re-derived. Same founders, same RNG stream, same everything else."""
    rng = random.Random(seed)
    store = fresh_store()
    founders = entries[:C.CARRYING_CAPACITY]
    econ = al.Economy(C.ATP_PER_AGENT * len(founders) * 4)
    memo = al.Memo() if memo_on else None

    ledger, live = [], []
    for i, e in enumerate(founders):
        root = al.put_term(e["term"], store)
        a = al.Agent(f"g0-{i:03d}", root, 0)
        econ.endow(a, C.GENERATION_ENDOWMENT)
        ledger.append(a)
        live.append(a)

    born = 0
    trace = []
    for gen in range(C.GENERATIONS):
        # --- run
        pop = al.Population(store, live, econ, rng, slice_atp=C.SLICE_ATP, memo=memo)
        for _ in range(C.TICKS):
            if not any(a.status in al.RUNNABLE and a.atp > 0 for a in live):
                break
            pop.phase_reduce()

        factor, total, unique = al.sharing_factor(live)
        trace.append({
            "generation": gen,
            "alive": len(live),
            "sharing_factor": factor,
            "nodes_total": total,
            "nodes_unique": unique,
            "mean_size": total / len(live) if live else 0.0,
            "atp_spent": sum(a.spent for a in ledger),
            "atp_held": sum(a.atp for a in live),
            "diversity_bits": al.structural_diversity(live),
            "normal": sum(1 for a in live if a.status == al.NORMAL),
            "memo_hits": memo.hits if memo else 0,
            "memo_entries": len(memo.nf) if memo else 0,
        })

        # --- drought: a flat tax, then death for anyone who cannot pay it
        for a in sorted(live, key=lambda x: x.aid):
            econ.collect(a, C.DROUGHT_TAX)
        dead = [a for a in live if a.atp == 0]
        for a in dead:
            a.status = al.ARCHIVED
        live = [a for a in live if a.atp > 0]

        # --- reproduction: the richest pay to spawn, up to capacity
        live.sort(key=lambda a: (-a.atp, a.aid))
        i = attempts = 0
        while len(live) < C.CARRYING_CAPACITY and live:
            attempts += 1
            if attempts > 4 * C.CARRYING_CAPACITY:
                break            # nobody in this generation can afford a child
            parent = live[i % len(live)]
            if parent.atp <= C.BIRTH_COST:
                break
            mate = live[(i + 1) % len(live)]
            child_root = al.crossover(parent, mate, store, rng, graft="root")
            if child_root is None:
                # A parent whose term is a single leaf has no node to graft into
                # — and a settled SKI agent very often IS one leaf. It still
                # reproduces, by APPLICATION: the child is the parent applied to
                # the mate's genome. Without this the reproduction loop spins
                # forever on a population of settled leaves, which is how the
                # first parameter probe hung.
                al.put_term(parent.term, store)
                child_root = al.put_term(
                    ("app", parent.term, ("thunk", mate.root)), store)
            i += 1
            born += 1
            child = al.Agent(f"g{gen + 1}-{born:03d}", child_root, 0,
                             lineage=(parent.aid, mate.aid), born=gen + 1)
            parent.atp -= C.BIRTH_COST
            child.atp += C.BIRTH_COST
            ledger.append(child)
            live.append(child)

        # --- cull back to capacity, poorest first
        live.sort(key=lambda a: (-a.atp, a.aid))
        for a in live[C.CARRYING_CAPACITY:]:
            econ.collect(a, a.atp)
            a.status = al.ARCHIVED
        live = live[:C.CARRYING_CAPACITY]

        # --- endowment, AFTER reproduction so a newborn is not taxed before it
        # has ever been fed. With the endowment first, every child arrived with
        # its birth cost alone and the next drought took all of it: the loop bred
        # a generation solely in order to kill it.
        for a in sorted(live, key=lambda x: x.aid):
            econ.grant(a, C.GENERATION_ENDOWMENT)

        assert econ.check(ledger), f"ATP CONSERVATION VIOLATED at generation {gen}"
        assert (sum(a.size for a in ledger)
                <= sum(a.s0 for a in ledger) + sum(a.spent for a in ledger)), \
            f"POPULATION BOUND VIOLATED at generation {gen}"
        if not live:
            break

    return {"trace": trace, "final": trace[-1] if trace else None,
            "founding": trace[0] if trace else None, "born": born,
            "ledger": len(ledger),
            # WHO survived, not just how many. The sharing factor is a function of
            # this set: if the two arms end with the same agents, the arms cannot
            # differ on H3 and the run has no power to adjudicate it, whatever the
            # ATP saving was. Control C7 reads this.
            "survivors": sorted(a.aid for a in live)}


def part_b(entries):
    out = {}
    for seed in C.SEEDS:
        out[str(seed)] = {
            "memo": part_b_arm(entries, seed, True),
            "no-memo": part_b_arm(entries, seed, False),
        }
    return out


# ---------------- controls ----------------
def controls(entries):
    out = []
    store = fresh_store()

    # C1 — the memo never moves an answer, and never costs more.
    memo = al.Memo()
    same, cheaper = True, True
    for e in entries:
        root = al.put_term(e["term"], store)
        for _ in range(2):
            a = al.Agent(e["name"], root, C.ATP_PER_AGENT)
            al.reduce_slice(a, store, C.ATP_PER_AGENT, probe=True, memo=memo)
            if a.status == al.NORMAL:
                memo.learn(root, a.term, a.spent)
            ref, spent = sg.eval_hash(root, C.ATP_PER_AGENT, store)
            same &= al.outcome_hash(a) == sg.term_hash(ref)
            cheaper &= a.spent <= spent
    out.append(("C1 the memo reaches the oracle's answer and never spends more",
                same and cheaper))

    # C2 — the mirror is a mirror (the full check lives in tests/alife_memo.py).
    mirror_ok = True
    for e in entries[:16]:
        t, spent, stats = ("thunk", al.put_term(e["term"], store)), 0, {"fetches": 0}
        for _ in range(500):
            act = al._next_action(t)
            try:
                r = sg.step5(t, 4000 - spent, store, stats, sg.DEFAULT_LIMITS)
            except (sg.BudgetExhausted, sg.Unresolved):
                break
            if r is None:
                break
            t2, cost = r
            if act is not None and act[0] == "force":
                node = t2
                for p in act[2]:
                    node = node[p]
                mirror_ok &= node[0] != "thunk" and cost == sg.size(node)
            t, spent = t2, spent + cost
    out.append(("C2 every predicted force is a real force", mirror_ok))

    # C3 — the derived price is load-bearing: a flat price must BREAK the bound.
    cheap = al.Memo(price=lambda nf: 1)
    for e in entries:
        root = al.put_term(e["term"], store)
        a = al.Agent("c", root, C.ATP_PER_AGENT)
        al.reduce_slice(a, store, C.ATP_PER_AGENT, memo=cheap)
        if a.status == al.NORMAL:
            cheap.learn(root, a.term, a.spent)
    broke = 0
    for e in entries:
        a = al.Agent("c2", al.put_term(e["term"], store), C.ATP_PER_AGENT)
        al.reduce_slice(a, store, C.ATP_PER_AGENT, memo=cheap)
        broke += (a.size > a.s0 + a.spent)
    out.append((f"C3 a flat price of 1 breaks the bound ({broke}/{len(entries)})",
                broke > 0))

    # C4 — conservation and the bound hold in the generational loop (the asserts
    # inside part_b_arm are the check; reaching here means they held).
    probe = part_b_arm(entries, C.SEED, True)
    out.append(("C4 conservation and the bound survive 12 generations",
                probe["final"] is not None))

    # C5 — with an EMPTY memo the two arms are the same run.
    a_off = run_arm(entries[:8], "off")
    a_on = run_arm(entries[:8], "shared")
    same_shape = (a_off["agents"] == a_on["agents"]
                  and a_off["nodes_total"] == a_on["nodes_total"]
                  and a_off["normal"] == a_on["normal"])
    out.append(("C5 the arms reach the same terms; only the price differs",
                same_shape))

    # C6 — the inherited corpus is EXP-001's.
    out.append((f"C6 corpus fingerprint is {C.fingerprint()}",
                C.fingerprint() == C.INHERITED_FINGERPRINT))

    # C7 — POWER. H3 compares the sharing factor of two surviving populations, so
    # it says nothing at all unless the two arms can end with different survivors.
    # A frame in which they cannot is not evidence against H3; it is a measurement
    # of the frame. This is checked per seed and reported per seed.
    powered = {}
    for seed in C.SEEDS:
        m = part_b_arm(entries, seed, True)
        n = part_b_arm(entries, seed, False)
        sa, sb = set(m["survivors"]), set(n["survivors"])
        overlap = len(sa & sb) / len(sa | sb) if (sa | sb) else 1.0
        powered[seed] = {
            "alive_both": bool(sa) and bool(sb),
            "memo_fired": m["final"]["memo_hits"] > 0,
            "survivors_differ": overlap < 1.0,
            "survivor_overlap": overlap,
            "atp_saving": (n["final"]["atp_spent"] - m["final"]["atp_spent"])
            / max(1, n["final"]["atp_spent"]),
        }
    out.append(("C7 the arms are distinguishable in principle "
                f"(overlap {', '.join(f'{100 * p["survivor_overlap"]:.0f}%' for p in powered.values())})",
                all(p["alive_both"] and p["memo_fired"] and p["survivors_differ"]
                    for p in powered.values())))
    return all(ok for _, ok in out), out


def summarize(result):
    print("PART A — energy (ATP for the same population, same terms)\n")
    print(f"{'run':8s} {'off':>8s} {'private':>8s} {'shared':>8s} "
          f"{'inter':>8s} {'share@birth':>12s} {'hits':>6s} {'ceil%':>7s}")
    for name, arms in result["part_a"].items():
        off, priv, sh = arms["off"], arms["private"], arms["shared"]
        inter = priv["atp_spent"] - sh["atp_spent"]
        print(f"{name:8s} {off['atp_spent']:8d} {priv['atp_spent']:8d} "
              f"{sh['atp_spent']:8d} {inter:8d} {sh['sharing_factor']:12.3f} "
              f"{sh['memo_hits']:6d} {100 * sh['ceiling_occupancy']:6.2f}%")
    print("\n  * composite is POST HOC — not preregistered; see measure.py")
    print("  off      no memo at all")
    print("  private  one memo per agent — only repetition INSIDE an agent pays")
    print("  shared   one memo for the population — anastomosis, priced")
    print("  inter    private − shared: the part of the saving that is sharing")

    print("\n\nPART B — selection (carrying capacity "
          f"{C.CARRYING_CAPACITY}, {C.GENERATIONS} generations)\n")
    print(f"{'seed':>10s} {'arm':>8s} {'share g0':>9s} {'share gN':>9s} "
          f"{'Δ':>7s} {'alive':>6s} {'mean size':>10s} {'spent':>9s} {'hits':>6s}")
    verdicts = []
    for seed, arms in result["part_b"].items():
        for arm in ("no-memo", "memo"):
            r = arms[arm]
            f0, fn = r["founding"], r["final"]
            print(f"{seed:>10s} {arm:>8s} {f0['sharing_factor']:9.3f} "
                  f"{fn['sharing_factor']:9.3f} "
                  f"{fn['sharing_factor'] - f0['sharing_factor']:+7.3f} "
                  f"{fn['alive']:6d} {fn['mean_size']:10.2f} "
                  f"{fn['atp_spent']:9d} {fn['memo_hits']:6d}")
        d = (arms["memo"]["final"]["sharing_factor"]
             - arms["no-memo"]["final"]["sharing_factor"])
        verdicts.append(d)
        print(f"{'':>10s} {'Δ arms':>8s} {d:+9.3f}"
              f"   {'memo shares more' if d > 0 else 'memo shares no more'}")
    print()
    won = sum(1 for d in verdicts if d > 0)
    print(f"H3 (memo arm > no-memo arm at equal capacity): {won}/{len(verdicts)} "
          f"seeds -> {'holds' if won == len(verdicts) else 'FAILS'}")
    a = result["part_a"]["mixed"]
    inter = a["private"]["atp_spent"] - a["shared"]["atp_spent"]
    frac = 100.0 * inter / max(1, a["off"]["atp_spent"])
    intra = a["off"]["atp_spent"] - a["private"]["atp_spent"]
    # H1 asked whether memoization turns sharing into ATP. A saving of a fraction
    # of a percent is not a small effect, it is no effect: the verdict is scored
    # against the run's own noise floor — one memo hit — and not against zero.
    print(f"H1 (memoization turns sharing into ATP): inter-agent saving {inter} "
          f"ATP ({frac:.2f}%), intra-agent {intra} ATP, "
          f"{a['shared']['memo_hits']} hits -> "
          f"{'holds' if a['shared']['memo_hits'] > len(result['part_a']) else 'FAILS'}")
    c = result["part_a"]["composite*"]
    c_inter = c["private"]["atp_spent"] - c["shared"]["atp_spent"]
    print(f"   post hoc, with a demand path: inter-agent saving {c_inter} ATP "
          f"({100.0 * c_inter / max(1, c['off']['atp_spent']):.1f}%), "
          f"{c['shared']['memo_hits']} hits")
    # H2 is a claim about what memoization does to the proved ceiling. On an arm
    # where the memo fired once it is not a claim about anything, so it is left
    # UNADJUDICATED rather than scored on noise.
    fired = a["shared"]["memo_hits"] > len(result["part_a"])
    verdict = ("holds" if a["shared"]["ceiling_occupancy"] > a["off"]["ceiling_occupancy"]
               else "FAILS") if fired else (
        "NOT ADJUDICATED (the memo fired once; there is no memoized run to compare)")
    print(f"H2 (the ceiling gets tighter): occupancy "
          f"{100 * a['off']['ceiling_occupancy']:.2f}% off vs "
          f"{100 * a['shared']['ceiling_occupancy']:.2f}% shared -> {verdict}")
    print(f"   post hoc, with a demand path: {100 * c['off']['ceiling_occupancy']:.2f}% "
          f"off vs {100 * c['shared']['ceiling_occupancy']:.2f}% shared -> "
          f"{'tighter' if c['shared']['ceiling_occupancy'] > c['off']['ceiling_occupancy'] else 'no tighter'}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--record", action="store_true")
    args = ap.parse_args()

    entries = C.build()
    ok, results = controls(entries)
    for name, passed in results:
        print(("OK  " if passed else "FAIL"), name)
    if not ok:
        print("\nALIFE-EXP-002: CONTROLS FAILED — nothing measured, nothing recorded")
        return 1

    result = {"part_a": part_a(entries), "part_b": part_b(entries)}
    print()
    summarize(result)

    prov = al.provenance()
    receipt = {
        "experiment": "ALIFE-EXP-002",
        "corpus_fingerprint": C.fingerprint(),
        "inherited_from": "ALIFE-EXP-001",
        "corpus": {"atp_per_agent": C.ATP_PER_AGENT, "slice_atp": C.SLICE_ATP,
                   "ticks": C.TICKS, "seeds": list(C.SEEDS),
                   "carrying_capacity": C.CARRYING_CAPACITY,
                   "generations": C.GENERATIONS, "drought_tax": C.DROUGHT_TAX,
                   "birth_cost": C.BIRTH_COST,
                   "generation_endowment": C.GENERATION_ENDOWMENT,
                   "graft": "root"},
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
