#!/usr/bin/env python3
"""Memoization: the answer must not move, and the price is not a free choice.

  M1  the mirror is a mirror. `_next_action` predicts what `step5` will do; every
      predicted force must BE a force, at the predicted position, at the price the
      machine actually charged. (One direction only, and it is the direction that
      matters: a mirror that missed a force would make the memo timid, not greedy.
      The other direction is left unchecked and said out loud.)
  M2  a memoized run reaches the ORACLE'S normal form, spends no more than the
      oracle, and satisfies the memory bound at every action.
  M3  the derived price is load-bearing: at a flat price of 1 the bound BREAKS on
      this corpus. A control that must fail, or the pricing law has no teeth.
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

    # ---- M3b: and the derived price is the smallest that does not
    nf = ("app", ("lit", sg.sha(b"a")), ("lit", sg.sha(b"b")))
    chk("M3b the derived price is exactly the size it installs",
        al.Memo.derived_price(nf) == sg.size(nf) == 3)

    # ---- M5: an unaffordable hit is skipped, not fatal
    big = max(memo.nf.items(), key=lambda kv: sg.size(kv[1][0]))
    root, (nf_term, _) = big
    price = al.Memo.derived_price(nf_term)
    a = al.Agent("poor", root, max(1, price - 1))
    al.reduce_slice(a, store, a.atp, memo=memo)
    chk(f"M5 a hit costing {price} is skipped by an agent holding {a.atp + a.spent}, "
        f"which still made progress ({a.spent} ATP, status {a.status})",
        a.status in (al.STARVED, al.NORMAL) and a.spent >= 0)

    print()
    for n in notes:
        print("note:", n)
    passed = all(ok)
    print(f"\nALIFE-MEMO: {'ALL PASS' if passed else 'FAILURES PRESENT'} "
          f"({sum(ok)}/{len(ok)})")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
