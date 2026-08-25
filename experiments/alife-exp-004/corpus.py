#!/usr/bin/env python3
"""Corpora for ALIFE-EXP-004, with the alphabet as a knob.

ALIFE-EXP-001's generator draws a leaf from the genesis alphabet 70% of the time.
Its central finding is stated over `sharing_factor`, which counts I, K and S like
any other address — so "reduction consumes shared structure" and "reduction
consumes the alphabet" produce the same number and cannot be told apart.

This file makes the alphabet a parameter and the seed a sweep. At
`genesis_fraction = 0.7` the generator is EXP-001's exactly, so that row is a
replication and the others are the dose-response.
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

SEEDS = tuple(20260825 + i for i in range(10))
GENESIS_FRACTIONS = (0.3, 0.5, 0.7, 0.9)   # 0.7 IS EXP-001's generator
PER_FAMILY = 16
ATP_PER_AGENT = 3000                        # as EXP-001: enough for everyone to settle
SLICE_ATP = 32
TICKS = 24
EXP1_FINGERPRINT = "53cc6da80f66d220"       # the replication anchor


def _leaf(rng, g):
    """Genesis with probability `g`; the remainder split 2:1 between a fresh
    literal and a REF to genesis, which is EXP-001's split at g = 0.7."""
    r = rng.random()
    if r < g:
        return rng.choice([IG, KG, SG])
    if r < g + (1 - g) * 2 / 3:
        return ("lit", sg.sha(b"atom-%d" % rng.randrange(1 << 16)))
    return ("ref", rng.choice([sg.I_H, sg.K_H, sg.S_H]))


def _tree(rng, depth, g):
    if depth <= 0 or rng.random() < 0.3:
        return _leaf(rng, g)
    return ("app", _tree(rng, depth - 1, g), _tree(rng, depth - 1, g))


def _dup(rng, g):
    z = _tree(rng, 3, g)
    return ("app", ("app", ("app", SG, _tree(rng, 2, g)), _tree(rng, 2, g)), z)


def _drop(rng, g):
    return ("app", ("app", KG, _tree(rng, 2, g)), _tree(rng, 3, g))


def _church(rng, g):
    n = rng.randint(1, 4)
    body = ("var", "x")
    for _ in range(n):
        body = ("lapp", ("var", "f"), body)
    num = ("lam", "f", ("lam", "x", body))
    return ("app", ("app", sg.c1(num), rng.choice([IG, KG, SG])),
            rng.choice([IG, KG, SG]))


def _random(rng, g):
    return _tree(rng, 4, g)


BUILDERS = {"dup": _dup, "drop": _drop, "church": _church, "random": _random}


def build(seed, genesis_fraction):
    out = []
    for family, make in sorted(BUILDERS.items()):
        s = int(hashlib.sha256(
            f"{seed}:{genesis_fraction}:{family}".encode()).hexdigest()[:16], 16)
        rng = random.Random(s)
        for i in range(PER_FAMILY):
            out.append({"family": family, "name": f"{family}-{i:02d}",
                        "term": make(rng, genesis_fraction)})
    return out


def fingerprint(entries):
    h = hashlib.sha256()
    for e in entries:
        h.update(e["name"].encode())
        h.update(sg.term_hash(e["term"]))
    return h.hexdigest()[:16]


if __name__ == "__main__":
    print(f"{len(SEEDS)} seeds x {len(GENESIS_FRACTIONS)} genesis fractions x "
          f"{PER_FAMILY * len(BUILDERS)} terms")
    for g in GENESIS_FRACTIONS:
        e = build(SEEDS[0], g)
        print(f"  g={g}: fingerprint {fingerprint(e)}, mean size "
              f"{sum(sg.size(x['term']) for x in e) / len(e):.1f}")
