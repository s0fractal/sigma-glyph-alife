#!/usr/bin/env python3
"""The population to be measured. Fixed here, before any measurement is recorded.

Four families, chosen for what each one can show and not for what it will say:

- `dup`     S over a SHARED argument: R-S copies `z` and charges `1 + size(z)`
            for it, and the copy is the same content address as the original.
            This is where sharing can only rise. It is a CONTROL on H1: if the
            dup family does not rise, the harness is wrong, not the hypothesis.
- `drop`    K-heavy terms that discard their argument. Structure LEAVES the
            population here. A control in the other direction.
- `church`  Church numerals applied to combinators, through Book I's own C1
            compiler — λ-calculus as an ALife substrate actually gets used.
- `random`  the same question with no construction behind it, from fixed seeds,
            including terms that never settle inside the budget.

Every term is a Book I term (already C1-compiled where it started as a λ-term),
and the whole corpus is pinned by `fingerprint()` — the SHA-256 over each term's
NodeHash in order. `measure.py` refuses to record a receipt if the fingerprint
it computes is not the one committed here.
"""
import hashlib
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "impl"))
import sigma_alife as al  # noqa: E402

sg = al.sg

IG = ("lit", sg.sha(b"I"))
KG = ("lit", sg.sha(b"K"))
SG = ("lit", sg.sha(b"S"))

SEED = 20260825
PER_FAMILY = 16          # agents per family
ATP_PER_AGENT = 3000     # the whole reservoir an agent ever gets
SLICE_ATP = 32           # the floor on one tick's attempt (see Population.phase_reduce)
TICKS = 24               # ticks per run; runs stop early when nothing is runnable
CAP = 4000               # generation-time evaluation cap, for the corpus report only


def _leaf(rng):
    r = rng.random()
    if r < 0.7:
        return rng.choice([IG, KG, SG])
    if r < 0.9:
        return ("lit", sg.sha(b"atom-%d" % rng.randrange(1 << 16)))
    return ("ref", rng.choice([sg.I_H, sg.K_H, sg.S_H]))


def _tree(rng, depth):
    if depth <= 0 or rng.random() < 0.3:
        return _leaf(rng)
    return ("app", _tree(rng, depth - 1), _tree(rng, depth - 1))


def _dup(rng):
    """S x y z — one argument, two consumers, one address."""
    z = _tree(rng, 3)
    return ("app", ("app", ("app", SG, _tree(rng, 2)), _tree(rng, 2)), z)


def _drop(rng):
    """K x y — the discarded argument is where structure leaves the population."""
    return ("app", ("app", KG, _tree(rng, 2)), _tree(rng, 3))


def _church(rng):
    """(λf.λx. fⁿ x) g h, compiled by Book I's C1."""
    n = rng.randint(1, 4)
    body = ("var", "x")
    for _ in range(n):
        body = ("lapp", ("var", "f"), body)
    num = ("lam", "f", ("lam", "x", body))
    return ("app", ("app", sg.c1(num), rng.choice([IG, KG, SG])),
            rng.choice([IG, KG, SG]))


def _random(rng):
    return _tree(rng, 4)


BUILDERS = {"dup": _dup, "drop": _drop, "church": _church, "random": _random}


def build():
    """The corpus, deterministically: one RNG per family so that adding a family
    later cannot silently change the terms of the families beside it."""
    out = []
    for family, make in sorted(BUILDERS.items()):
        # Seeded from SHA-256 of (SEED, family) rather than from Python's own
        # `hash`, which is salted per process: a corpus that cannot be rebuilt
        # in a second process is not a pinned corpus.
        seed = int(hashlib.sha256(f"{SEED}:{family}".encode()).hexdigest()[:16], 16)
        rng = random.Random(seed)
        for i in range(PER_FAMILY):
            out.append({"family": family, "name": f"{family}-{i:02d}",
                        "term": make(rng)})
    return out


def fingerprint(corpus=None):
    """SHA-256 over the corpus's NodeHashes, in order. Pins the terms, not the
    file: a reordering, an added term or a changed leaf all move it."""
    corpus = corpus or build()
    h = hashlib.sha256()
    for entry in corpus:
        h.update(entry["name"].encode())
        h.update(sg.term_hash(entry["term"]))
    return h.hexdigest()[:16]


if __name__ == "__main__":
    c = build()
    print(f"corpus: {len(c)} terms, {len(BUILDERS)} families, "
          f"{PER_FAMILY} per family")
    print(f"fingerprint: {fingerprint(c)}")
    for entry in c[:4] + c[-2:]:
        print(f"  {entry['name']:12s} size={sg.size(entry['term']):3d} "
              f"hash={sg.term_hash(entry['term']).hex()[:12]}")
