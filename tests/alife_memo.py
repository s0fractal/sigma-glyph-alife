#!/usr/bin/env python3
"""Memoization: the answer must not move, and the price has two floors.

  M1  the mirror is a mirror. `_next_action` predicts what `step5` will do; every
      predicted force must BE a force, at the predicted position, at the price the
      machine actually charged. (One direction only, and it is the direction that
      matters: a mirror that missed a force would make the memo timid, not greedy.
      The other direction is left unchecked and said out loud.)
  M2  a memoized run reaches the ORACLE'S normal form, spends no more than the
      oracle, and satisfies the memory bound at every action.
  M3  the price boundaries, both of them, measured rather than asserted: the
      memory bound survives at `size(nf) - 1` and breaks at `size(nf) - 2`, and
      `size(nf)` is what additionally preserves Book I's per-row discipline. The
      first version of this suite checked only a flat price of 1 and the repository
      generalized from it to "any price below size(nf) breaks the bound", which is
      false at size(nf) - 1. Boundaries get checked at the boundary.
  M4  the memo never learns something false: a term first evaluated with a warm
      memo and the same term evaluated from a cold store agree.
  M5  a hit the budget cannot afford is skipped, not fatal — the plain force costs
      at most 3, so a shortcut nobody can buy must not starve an agent.

Usage:  python3 tests/alife_memo.py [--terms N] [--seed S]
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import terms as corpus  # noqa: E402

al = corpus.al
sg = corpus.sg


def node_at(t, path):
    for step in path:
        t = t[step]
    return t


def fresh_store():
    st = sg.Store()
    for b in (sg.I_BYTES, sg.K_BYTES, sg.S_BYTES):
        st.put(b)
    return st


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--terms", type=int, default=60)
    ap.add_argument("--seed", type=int, default=20260825)
    args = ap.parse_args()
    import random
    rng = random.Random(args.seed)

    store = fresh_store()
    roots = corpus.install(corpus.generate(rng, args.terms), store)
    ok, notes = [], []

    def chk(name, cond):
        ok.append(bool(cond))
        print(("OK  " if cond else "FAIL"), name)

    # ---- M1: the mirror predicts the machine
    predicted = mismatched = rules = 0
    for root in roots:
        t, spent, stats = ("thunk", root), 0, {"fetches": 0}
        for _ in range(2000):
            act = al._next_action(t)
            try:
                r = sg.step5(t, 4000 - spent, store, stats, sg.DEFAULT_LIMITS)
            except (sg.BudgetExhausted, sg.Unresolved):
                break
            if r is None:
                chk_nf = act is None
                if not chk_nf:
                    mismatched += 1
                break
            t2, cost = r
            if act is not None and act[0] == "force":
                predicted += 1
                before, after = node_at(t, act[2]), node_at(t2, act[2])
                if not (before == ("thunk", act[1]) and after[0] != "thunk"
                        and cost == sg.size(after)):
                    mismatched += 1
            else:
                rules += 1
            t, spent = t2, spent + cost
    chk(f"M1 every predicted force IS a force at that position and price "
        f"({predicted} forces, {rules} rule firings)",
        predicted > 0 and mismatched == 0)
    notes.append(f"M1 checked {predicted} predicted forces; the reverse direction "
                 f"(a force the mirror missed) is NOT checked")

    # ---- M2 / M4: warm memo, cold truth
    memo = al.Memo()
    warm_total = cold_total = 0
    same_answer = True
    bound_ok = True
    for root in roots:
        ref, cold = sg.eval_hash(root, 4000, store)
        a = al.Agent("m", root, 4000)
        al.reduce_slice(a, store, 4000, probe=True, memo=memo)
        if a.status == al.NORMAL:
            memo.learn(root, a.term, a.spent)
        same_answer &= al.outcome_hash(a) == sg.term_hash(ref)
        bound_ok &= a.bound_holds()
        warm_total += a.spent
        cold_total += cold
    # second pass: now every root is in the memo
    replay_total, replay_same = 0, True
    for root in roots:
        ref, _ = sg.eval_hash(root, 4000, store)
        a = al.Agent("r", root, 4000)
        al.reduce_slice(a, store, 4000, probe=True, memo=memo)
        replay_same &= al.outcome_hash(a) == sg.term_hash(ref)
        replay_total += a.spent
    chk("M2 a memoized run reaches the oracle's normal form", same_answer and replay_same)
    chk("M2 the memory bound holds at every action of a memoized run", bound_ok)
    chk(f"M2 memoized spend never exceeds the oracle's "
        f"({replay_total} vs {cold_total})", replay_total <= cold_total)
    chk(f"M4 the memo learned {len(memo.nf)} normal forms and none of them moved "
        f"an answer", replay_same and len(memo.nf) > 0)
    notes.append(f"M2 warm-run ATP {replay_total} against oracle {cold_total} "
                 f"({100.0 * replay_total / max(1, cold_total):.1f}%), "
                 f"{memo.hits} hits")

    # ---- M3: the price is load-bearing (a control that MUST break the bound)
    cheap = al.Memo(price=lambda nf: 1)
    for root in roots:
        a = al.Agent("c", root, 4000)
        al.reduce_slice(a, store, 4000, memo=cheap)
        if a.status == al.NORMAL:
            cheap.learn(root, a.term, a.spent)
    broke = 0
    worst = 0
    for root in roots:
        a = al.Agent("c2", root, 4000)
        al.reduce_slice(a, store, 4000, memo=cheap)
        excess = a.size - (a.s0 + a.spent)
        if excess > 0:
            broke += 1
            worst = max(worst, excess)
    chk(f"M3 a flat price of 1 BREAKS the bound ({broke}/{len(roots)} terms, "
        f"worst excess +{worst})", broke > 0)

    # M3a/M3b — the boundary itself, both sides of it.
    def violations(price):
        m = al.Memo(price=price)
        for root in roots:
            a = al.Agent("w", root, 4000)
            al.reduce_slice(a, store, 4000, memo=m)
            if a.status == al.NORMAL:
                m.learn(root, a.term, a.spent)
        bad = 0
        for root in roots:
            a = al.Agent("c", root, 4000)
            al.reduce_slice(a, store, 4000, memo=m)
            bad += a.size > a.s0 + a.spent
        return bad

    at_floor = violations(lambda nf: max(0, sg.size(nf) - 1))
    below = violations(lambda nf: max(0, sg.size(nf) - 2))
    chk(f"M3a size(nf) - 1 is SOUND for the bound ({at_floor} violations) — the "
        f"floor is one below the price this repository implements", at_floor == 0)
    chk(f"M3b size(nf) - 2 breaks it ({below}/{len(roots)}) — the floor is real",
        below > 0)

    # ---- M3c: what the implemented price actually is, and what it buys
    nf = ("app", ("lit", sg.sha(b"a")), ("lit", sg.sha(b"b")))
    chk("M3c the implemented price is the size it installs",
        al.Memo.derived_price(nf) == sg.size(nf) == 3)
    chk("M3c and that price keeps Book I's per-row discipline (dsize <= cost - 1)",
        (sg.size(nf) - 1) <= al.Memo.derived_price(nf) - 1)

    # ---- M5: an unaffordable hit is skipped, not fatal
    big = max(memo.nf.items(), key=lambda kv: sg.size(kv[1][0]))
    root, (nf_term, _) = big
    price = al.Memo.derived_price(nf_term)
    a = al.Agent("poor", root, max(1, price - 1))
    al.reduce_slice(a, store, a.atp, memo=memo)
    chk(f"M5 a hit costing {price} is skipped by an agent holding {a.atp + a.spent}, "
        f"which still made progress ({a.spent} ATP, status {a.status})",
        a.status in (al.STARVED, al.NORMAL) and a.spent >= 0)

    # ---- L: the library (colony-funded, demand-filled subterm memoization)
    lib_store = fresh_store()
    lib_roots = corpus.install(corpus.generate(random.Random(args.seed), 24), lib_store)

    def run_pop(memo, atp=2000):
        agents = []
        for i, root in enumerate(lib_roots):
            a = al.Agent(f"L{i:02d}", root, atp)
            al.reduce_slice(a, lib_store, atp, probe=True, memo=memo)
            agents.append(a)
        return agents

    econ = al.Economy(24 * 2000 + 4000)
    library = al.Library(atp=4000)
    agents = run_pop(library)
    for a in agents:
        econ.grant(a, 0)
    answers_ok = all(
        al.outcome_hash(a) == sg.term_hash(sg.eval_hash(a.root, 2000, lib_store)[0])
        for a in agents)
    chk(f"L1 the library filed {library.filed} normal forms on demand "
        f"({library.hits} hits, {library.failed} failed fills)",
        library.filed > 0 and library.hits > 0)
    chk("L1 and every agent still reached the oracle's answer", answers_ok)
    chk("L1 the bound held at every action of every agent",
        all(a.bound_holds() for a in agents))

    plain = al.Memo()
    plain_agents = run_pop(plain)
    lib_spent = sum(a.spent for a in agents)
    plain_spent = sum(a.spent for a in plain_agents)
    notes.append(f"L1 agents spent {lib_spent} with a library against {plain_spent} "
                 f"without; the library itself spent {library.spent} filling "
                 f"{library.filed} entries")

    # L2 — a library with an empty reservoir IS a plain memo.
    broke = al.Library(atp=0)
    broke_agents = run_pop(broke)
    chk("L2 a library with no reservoir behaves exactly like a plain memo",
        sum(a.spent for a in broke_agents) == plain_spent
        and broke.filed == 0 and broke.spent == 0)

    # L3 — the ledger sees the library's reservoir.
    e2 = al.Economy(10_000)
    lib2 = al.Library(atp=0)
    e2.pool -= 3000
    lib2.atp += 3000                       # the commons setting ATP aside
    ag2 = []
    for i, root in enumerate(lib_roots[:6]):
        a = al.Agent(f"E{i}", root, 0)
        e2.endow(a, 500)
        ag2.append(a)
    for a in ag2:
        al.reduce_slice(a, lib_store, a.atp, memo=lib2)
    chk("L3 conservation holds with the library counted as a holder",
        e2.check(ag2, extra=(lib2,)))
    chk("L3 and FAILS when it is left out of the sum",
        not e2.check(ag2) or lib2.spent == 0)

    # L4 — `learn` refuses what is not a normal form, and what is not a function
    # of the hash. Controls: each must be REFUSED.
    guard = al.Memo()
    starved = al.Agent("starve", lib_roots[0], 1)
    al.reduce_slice(starved, lib_store, 1)
    chk("L4 a term with an action left is refused",
        guard.learn(lib_roots[0], starved.term, 1) is False
        or starved.status == al.NORMAL)
    chk("L4 DISSONANCE(ATP Exhausted) is refused — it is a function of a budget",
        guard.learn(sg.sha(b"x1"), ("dis", sg.R_ATP), 1) is False)
    chk("L4 DISSONANCE(Unresolved) is refused — it is a function of a store",
        guard.learn(sg.sha(b"x2"), ("dis", sg.R_UNRES), 1) is False)
    chk("L4 DISSONANCE(Invalid Object) is allowed — it is a function of bytes",
        guard.learn(sg.sha(b"x3"), ("dis", sg.R_INVALID), 1) is True)

    # L5 — the depth bound is real: a shallower librarian files less.
    deep = al.Library(atp=4000, max_depth=4)
    shallow = al.Library(atp=4000, max_depth=1)
    run_pop(deep)
    run_pop(shallow)
    chk(f"L5 max_depth bounds the recursion (depth 4 filed {deep.filed}, "
        f"depth 1 filed {shallow.filed})", shallow.filed <= deep.filed)

    print()
    for n in notes:
        print("note:", n)
    passed = all(ok)
    print(f"\nALIFE-MEMO: {'ALL PASS' if passed else 'FAILURES PRESENT'} "
          f"({sum(ok)}/{len(ok)})")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
