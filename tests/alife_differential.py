#!/usr/bin/env python3
"""The substrate's driver must BE the Book I oracle, everywhere it claims to be.

`impl/sigma_alife.py` does not call `eval_hash`; it drives `step5` itself so a
starved agent keeps its body instead of collapsing to DISSONANCE(ATP Exhausted).
That freedom is exactly one outcome wide, and this is the gate that keeps it
there. For every generated term at every budget:

  D1  run whole (one slice, the full reservoir), map the outcome the way
      `outcome_hash` documents, and demand the SAME result hash and the SAME
      atp_spent as `eval_hash` — a driver that agreed on the answer but not on
      the price would put every ATP number in this repository in doubt;
  D2  run the same term SLICED, escalating the slice only when it buys nothing,
      and demand the whole run's result and spend back — this is the live-trace
      half of `resumption_bound` in `proofs/Population.lean`;
  D3  assert the memory bound after every single action of the sliced run
      (`probe=True`);
  D4  starve deliberately, then feed, and demand the unstarved answer — the
      sporulation claim, checked instead of asserted.

Usage:  python3 tests/alife_differential.py [--terms N] [--seed S]
Exit nonzero on any divergence; the failing case prints its seed and index.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import terms as corpus  # noqa: E402

al = corpus.al
sg = corpus.sg


def budgets_for(root, store):
    """Budgets that bracket the interesting boundary: nothing, everything, and
    the exact spend of a full run ±1 — the point where the oracle flips between
    an answer and ATP Exhausted, and where a driver that is off by one shows."""
    _, full = sg.eval_hash(root, 4000, store)
    return sorted({0, 1, 2, max(0, full - 1), full, full + 1, 4000})


def run(term_count, seed):
    import random
    rng = random.Random(seed)
    store = sg.Store()
    for b in (sg.I_BYTES, sg.K_BYTES, sg.S_BYTES):
        store.put(b)
    roots = corpus.install(corpus.generate(rng, term_count), store)

    cases = 0
    exercised = {"whole": 0, "sliced": 0, "starved-then-fed": 0, "stalls": 0}
    for i, root in enumerate(roots):
        for atp in budgets_for(root, store):
            cases += 1
            where = f"seed {seed} term {i} atp {atp}"

            expect_term, expect_spent = sg.eval_hash(root, atp, store)
            expect = sg.term_hash(expect_term)

            # D1 — whole
            whole = al.Agent(f"w{i}", root, atp)
            al.reduce_slice(whole, store, atp)
            exercised["whole"] += 1
            if al.outcome_hash(whole) != expect or whole.spent != expect_spent:
                print(f"FAIL D1 {where}: driver "
                      f"({al.outcome_hash(whole).hex()[:12]}, {whole.spent}) != oracle "
                      f"({expect.hex()[:12]}, {expect_spent})")
                return False, (cases, exercised)

            # D2 + D3 — sliced, with the bound probed at every action
            sliced = al.Agent(f"s{i}", root, atp)
            step = 1
            guard = 0
            while sliced.status == al.LIVE:
                guard += 1
                if guard > 10_000:
                    print(f"FAIL D2 {where}: sliced run did not settle")
                    return False, (cases, exercised)
                got = al.reduce_slice(sliced, store, step, probe=True)
                if got == 0 and sliced.status == al.LIVE:
                    exercised["stalls"] += 1
                    step = min(max(1, sliced.atp), step * 2)
            exercised["sliced"] += 1
            if al.outcome_hash(sliced) != expect or sliced.spent != expect_spent:
                print(f"FAIL D2 {where}: sliced "
                      f"({al.outcome_hash(sliced).hex()[:12]}, {sliced.spent}) != oracle "
                      f"({expect.hex()[:12]}, {expect_spent})")
                return False, (cases, exercised)
            if not sliced.bound_holds():
                print(f"FAIL D3 {where}: size {sliced.size} > s0 + spent {sliced.spent}")
                return False, (cases, exercised)

            # D4 — starve on a third of the budget, then feed the rest
            if atp >= 3:  # below that there is nothing to divide into a third
                spore = al.Agent(f"z{i}", root, atp // 3)
                al.reduce_slice(spore, store, spore.atp)
                if spore.status == al.STARVED:
                    if spore.term[0] == "dis" and spore.term[1] == sg.R_ATP:
                        print(f"FAIL D4 {where}: starvation collapsed the term")
                        return False, (cases, exercised)
                    spore.atp = atp - spore.spent
                    spore.status = al.LIVE
                    exercised["starved-then-fed"] += 1
                    al.reduce_slice(spore, store, atp)
                    if al.outcome_hash(spore) != expect or spore.spent != expect_spent:
                        print(f"FAIL D4 {where}: refed "
                              f"({al.outcome_hash(spore).hex()[:12]}, {spore.spent}) != "
                              f"oracle ({expect.hex()[:12]}, {expect_spent})")
                        return False, (cases, exercised)
    return True, (cases, exercised)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--terms", type=int, default=80)
    ap.add_argument("--seed", type=int, default=20260825)
    args = ap.parse_args()
    ok, (cases, exercised) = run(args.terms, args.seed)
    prov = al.provenance()
    print(f"oracle: {prov['oracle_source']}")
    print(f"oracle sha256: {prov['oracle_sha256']}")
    # A count of what actually ran, because "ALL AGREE" over a checklist nothing
    # reached is the exact shape of a green gate that checks nothing: the
    # starve-then-feed arm only fires on terms that CAN starve at that budget.
    print("exercised: " + ", ".join(f"{k}={v}" for k, v in exercised.items()))
    if ok and exercised["starved-then-fed"] == 0:
        print("ALIFE-DIFFERENTIAL: VACUOUS — no case ever starved, so D4 checked "
              "nothing. Raise --terms or widen the corpus.")
        return 1
    print(f"ALIFE-DIFFERENTIAL: {'ALL AGREE' if ok else 'DIVERGENCE'} "
          f"({cases} cases, {args.terms} terms, seed {args.seed}, "
          f"driver+sliced+refed vs python-oracle)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
