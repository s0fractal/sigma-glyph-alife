#!/usr/bin/env python3
"""The population to be measured — deliberately the SAME one as ALIFE-EXP-001.

EXP-002 asks what changes when sharing starts to cost something. A different
corpus would answer that question and one other at the same time, and there would
be no way to tell which half of any difference came from the price. So the terms
are imported unchanged from `../alife-exp-001/corpus.py` and pinned by the
fingerprint that experiment recorded: if that file ever moves, this one refuses to
run rather than silently comparing against a different population.

What is new here is only the generational frame Part B needs — a carrying
capacity, a drought tax, and a reproduction budget — and those are stated here,
before the harness, like everything else.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "impl"))
sys.path.insert(0, str(HERE.parent / "alife-exp-001"))

import corpus as EXP1  # noqa: E402
import sigma_alife as al  # noqa: E402

sg = al.sg

# The fingerprint ALIFE-EXP-001 recorded. Not a copy of the terms — a refusal to
# proceed if they are not the same terms.
INHERITED_FINGERPRINT = "53cc6da80f66d220"

SEED = 20260825
SEEDS = (20260825, 20260826, 20260827)   # Part B is stochastic; every seed reported
ATP_PER_AGENT = 3000                     # identical to EXP-001, so Part A compares
SLICE_ATP = 32
TICKS = 24

# --- Part B: the generational frame -------------------------------------------
CARRYING_CAPACITY = 32   # constant in BOTH arms. Without it the memo arm simply
                         # keeps more agents alive and a sharing comparison would
                         # be measuring population size.
GENERATIONS = 12
DROUGHT_TAX = 400        # ATP collected from every agent, every generation
BIRTH_COST = 200         # what a parent pays into a child's reservoir
GENERATION_ENDOWMENT = 300   # ATP the commons releases per agent per generation


def build():
    entries = EXP1.build()
    got = EXP1.fingerprint(entries)
    if got != INHERITED_FINGERPRINT:
        raise SystemExit(
            f"ALIFE-EXP-002 inherits the EXP-001 corpus, which has moved: "
            f"expected {INHERITED_FINGERPRINT}, got {got}. A comparison against "
            f"EXP-001's numbers would no longer be a comparison.")
    return entries


def fingerprint(entries=None):
    return EXP1.fingerprint(entries or build())


if __name__ == "__main__":
    c = build()
    print(f"corpus: {len(c)} terms, inherited from ALIFE-EXP-001 at "
          f"{fingerprint(c)}")
    print(f"part B: capacity {CARRYING_CAPACITY}, {GENERATIONS} generations, "
          f"tax {DROUGHT_TAX}, birth {BIRTH_COST}, endowment "
          f"{GENERATION_ENDOWMENT}/agent/generation, seeds {SEEDS}")
