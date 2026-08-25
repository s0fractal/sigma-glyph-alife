#!/usr/bin/env python3
"""Random term generation for the substrate's test suites.

Closed λ-terms compiled through Book I's canonical C1 compiler, plus raw SKI
trees, plus the two shapes that matter for a resource model: a duplicator that
makes `size` grow (S over a shared argument) and a term that demands a hash no
store holds. Deterministic from a seed — a divergence found here has to be
reproducible from the seed alone or it is not a finding.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "impl"))
import sigma_alife as al  # noqa: E402

sg = al.sg

IG = ("lit", sg.sha(b"I"))
KG = ("lit", sg.sha(b"K"))
SG = ("lit", sg.sha(b"S"))


def ski(rng, depth):
    """A raw SKI tree, with the occasional REF and ghost REF."""
    if depth <= 0 or rng.random() < 0.3:
        r = rng.random()
        if r < 0.6:
            return rng.choice([IG, KG, SG])
        if r < 0.8:
            return ("ref", rng.choice([sg.I_H, sg.K_H, sg.S_H]))
        return ("ref", sg.sha(b"ghost-%d" % rng.randrange(1 << 30)))
    return ("app", ski(rng, depth - 1), ski(rng, depth - 1))


def lam(rng, depth, bound=()):
    """A CLOSED λ-term: a variable is only ever drawn from what is in scope, so
    `c1` never has to reject one (`_abstract` raises on an escaping variable)."""
    r = rng.random()
    if depth <= 0 or r < 0.25:
        if bound and r < 0.5:
            return ("var", rng.choice(bound))
        return rng.choice([IG, KG, SG])
    if r < 0.6:
        v = "v%d" % len(bound)
        return ("lam", v, lam(rng, depth - 1, bound + (v,)))
    return ("lapp", lam(rng, depth - 1, bound), lam(rng, depth - 1, bound))


def church(n):
    """Church numeral λf.λx. fⁿ x, as a λ-term for the C1 compiler."""
    body = ("var", "x")
    for _ in range(n):
        body = ("lapp", ("var", "f"), body)
    return ("lam", "f", ("lam", "x", body))


def duplicator(rng, depth):
    """S x y z with one shared z: the shape where `size` actually grows, since
    R-S copies z and charges `1 + size(z)` for it."""
    z = ski(rng, depth)
    x, y = ski(rng, max(0, depth - 1)), ski(rng, max(0, depth - 1))
    return ("app", ("app", ("app", SG, x), y), z)


def generate(rng, count, depth=4):
    """A mixed corpus of λ-terms as Book I sees them (already C1-compiled)."""
    out = []
    for i in range(count):
        pick = i % 4
        if pick == 0:
            out.append(ski(rng, depth))
        elif pick == 1:
            out.append(sg.c1(lam(rng, depth)))
        elif pick == 2:
            out.append(("app", sg.c1(church(rng.randint(0, 3))),
                        rng.choice([IG, KG, SG])))
        else:
            out.append(duplicator(rng, depth - 1))
    return out


def install(terms, store):
    """Write every term into the store and return the root hashes."""
    return [al.put_term(t, store) for t in terms]
