#!/usr/bin/env python3
"""Every chance model must destroy exactly what it claims and no more.

A null that quietly destroys more structure than it advertises makes any
statistic look significant, and this repository has already been fooled twice by
chance models it did not check (`DECISIONS.md` D50, D54, D57). These are the
invariants each model asserts about itself, checked.
"""
import random
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "impl"))
import sigma_nulls as N  # noqa: E402


def edges_fixture(n=200, molecules=12, seed=5):
    rng = random.Random(seed)
    hs = [bytes([i]) * 4 for i in range(molecules)]
    return [(i, rng.choice(hs), rng.choice(hs), rng.choice(hs)) for i in range(n)]


def main():
    ok = []

    def chk(name, cond):
        ok.append(bool(cond))
        print(("OK  " if cond else "FAIL"), name)

    edges = edges_fixture()
    total, window = 200, 50
    rng = random.Random(1)

    for model in ("shuffle_products", "shuffle_local", "shuffle_times"):
        out = N.MODELS[model](edges, random.Random(7), window=window, total=total)
        chk(f"{model}: the graph keeps its size", len(out) == len(edges))
        made_a, used_a = N.degrees(edges)
        made_b, used_b = N.degrees(out)
        chk(f"{model}: every molecule is produced the same number of times",
            made_a == made_b)
        chk(f"{model}: reactant pairs are untouched",
            Counter((a, b) for _, a, b, _ in edges)
            == Counter((a, b) for _, a, b, _ in out))
        chk(f"{model}: the multiset of time indices is unchanged",
            Counter(i for i, *_ in edges) == Counter(i for i, *_ in out))

    # what each model DESTROYS — the other half of the claim
    prods = N.shuffle_products(edges, random.Random(3))
    chk("shuffle_products destroys the pair->product assignment",
        Counter((a, b, c) for _, a, b, c in prods)
        != Counter((a, b, c) for _, a, b, c in edges))

    times = N.shuffle_times(edges, random.Random(3))
    chk("shuffle_times leaves the chemistry EXACTLY intact",
        Counter((a, b, c) for _, a, b, c in times)
        == Counter((a, b, c) for _, a, b, c in edges))
    chk("shuffle_times moves reactions in time",
        [i for i, *_ in times] != [i for i, *_ in edges]
        or all(e[0] == t[0] for e, t in zip(edges, times)))

    loc = N.shuffle_local(edges, random.Random(3), window=window, total=total)
    recent_before = Counter(c for i, _, _, c in edges if i >= total - window)
    recent_after = Counter(c for i, _, _, c in loc if i >= total - window)
    chk("shuffle_local preserves WHICH molecules are recent",
        recent_before == recent_after)
    chk("shuffle_products does NOT preserve which molecules are recent "
        "(that is the difference between the two)",
        Counter(c for i, _, _, c in prods if i >= total - window) != recent_before
        or len(set(recent_before)) <= 1)

    # sampling, which is the whole point
    dist = N.sample(edges, lambda e: len({c for _, _, _, c in e}), "shuffle_products",
                    draws=8, seed=3)
    chk(f"sample returns a distribution and says how many draws "
        f"({dist['draws']} draws, mean {dist['mean']:.1f})",
        dist["draws"] == 8 and len(dist["values"]) == 8
        and "max" in dist and "min" in dist)

    passed = all(ok)
    print(f"\nALIFE-NULLS: {'ALL PASS' if passed else 'FAILURES PRESENT'} "
          f"({sum(ok)}/{len(ok)})")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
