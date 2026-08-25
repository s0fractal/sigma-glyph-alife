#!/usr/bin/env python3
"""Chance models for reaction graphs, sampled rather than consulted once.

Two experiments in a row here produced a positive result that a null destroyed,
and in both the null arrived after the fact (`DECISIONS.md` D50, D54, D57). The
worst of it was ALIFE-EXP-008, which drew a SINGLE permutation, found it empty,
and had a finished positive result before twenty draws reversed it.

So the chance models live here, beside the substrate, with three properties the
ad-hoc versions did not have:

  * **they are sampled.** Every function returns a distribution over `draws`
    permutations, never one graph.
  * **they say what they preserve**, and `tests/alife_nulls.py` checks that they
    do — a null that quietly destroys more than it claims makes any statistic
    look significant.
  * **they are three, not one.** A complete shuffle is the weakest chance model
    available and nearly anything beats it. Each model below destroys ONE thing
    and holds the rest fixed, so the three together say *which* structure a
    statistic is detecting.

A reaction graph is a list of `(index, a, b, c)`: at time `index`, reactants `a`
and `b` produced `c`.

    model              destroys                      preserves
    ─────────────────  ────────────────────────────  ──────────────────────────
    shuffle_products   which pair produced which      production counts, reactant
                       molecule, everywhere           pairs, all times
    shuffle_local      the same, but only WITHIN      additionally: which
                       a window                       molecules are recent
    shuffle_times      when each reaction happened    the chemistry exactly:
                                                      every (a,b)->c edge intact
"""
import random
import statistics
from collections import Counter

__all__ = ["shuffle_products", "shuffle_local", "shuffle_times", "sample",
           "degrees", "MODELS"]


def degrees(edges):
    """(production count per molecule, use count per molecule as a reactant).
    What a null claims to preserve has to be measurable, or the claim is decor."""
    made = Counter(c for _, _, _, c in edges)
    used = Counter()
    for _, a, b, _ in edges:
        used[a] += 1
        used[b] += 1
    return made, used


def shuffle_products(edges, rng, window=None, total=None):
    """Permute products across every reaction. Destroys which pair made what;
    keeps every reactant pair, every time index, and each molecule's total
    production count."""
    products = [c for _, _, _, c in edges]
    rng.shuffle(products)
    return [(i, a, b, p) for (i, a, b, _), p in zip(edges, products)]


def shuffle_local(edges, rng, window=None, total=None):
    """Permute products only within the last `window` reactions, and separately
    within everything before it. Additionally preserves WHICH molecules are
    recent — the structure a windowed statistic is most likely to be reading by
    accident."""
    if window is None or total is None:
        return shuffle_products(edges, rng)
    out = list(edges)
    inside = [k for k, e in enumerate(edges) if e[0] >= total - window]
    outside = [k for k, e in enumerate(edges) if e[0] < total - window]
    for block in (inside, outside):
        products = [edges[k][3] for k in block]
        rng.shuffle(products)
        for k, p in zip(block, products):
            i, a, b, _ = edges[k]
            out[k] = (i, a, b, p)
    return out


def shuffle_times(edges, rng, window=None, total=None):
    """Permute the time indices, leaving every `(a, b) -> c` edge exactly as it
    was. The chemistry is untouched; only WHEN each reaction happened moves. A
    statistic that survives this is reading the reactions; one that does not is
    reading the schedule."""
    times = [i for i, _, _, _ in edges]
    rng.shuffle(times)
    return [(t, a, b, c) for (_, a, b, c), t in zip(edges, times)]


MODELS = {"shuffle_products": shuffle_products,
          "shuffle_local": shuffle_local,
          "shuffle_times": shuffle_times}


def sample(edges, statistic, model, draws=20, seed=0, window=None, total=None):
    """Apply `statistic` to `draws` permutations under `model` and return the
    distribution. `draws` is in the return value because a receipt that reports a
    null without saying how many times it was drawn is reporting a coin flip."""
    fn = MODELS[model] if isinstance(model, str) else model
    values = []
    for d in range(draws):
        rng = random.Random(seed * 1_000_003 + d)
        values.append(statistic(fn(edges, rng, window=window, total=total)))
    return {"model": model if isinstance(model, str) else fn.__name__,
            "draws": draws,
            "mean": statistics.mean(values),
            "max": max(values),
            "min": min(values),
            "values": values}
