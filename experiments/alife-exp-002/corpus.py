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
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "impl"))

import sigma_alife as al  # noqa: E402


def _load(name, path):
    """Load EXP-001's corpus under its OWN module name. Both experiments call the
    file `corpus.py`, so a plain import from a sys.path entry resolves to
    whichever one is already in sys.modules — which, when this file is the one
    being imported, is this file, importing itself until Python gives up."""
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


EXP1 = _load("alife_exp_001_corpus", HERE.parent / "alife-exp-001" / "corpus.py")

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
# CORRECTED TWICE after the first runs, and both corrections are recorded because
# the frame was committed before the harness and changing it afterwards is a
# researcher's degree of freedom, not a bug fix.
#
# 1. tax 400 / birth 200 / endowment 300 kills the entire population in
#    generation 0: a founder spends a median of 31 ATP and a mean of 43, so it
#    holds ~257 of its 300 endowment when a tax of 400 arrives. A tax nobody can
#    pay is not a drought, it is an extinction event with no selection in it.
# 2. tax 200 / birth 150 / endowment 300 runs, and has NO POWER: the memo saves
#    ~170 ATP against a flow of ~115,000, i.e. 0.15%, and the two arms end with
#    the identical population. A null from a design that could not have shown an
#    effect is not a null; it is a measurement of the design.
#
# The frame below was chosen on POWER ALONE, looking only at turnover, at the
# saving fraction, and at how much the two arms' survivor sets differ — never at
# the sharing comparison H3 is about. It gives 26 births over 12 generations, a
# 17.1% ATP saving, and survivor sets that overlap by 23%. Control C7 in
# measure.py enforces that condition on every recorded run: if the arms cannot
# differ, H3 is reported as UNDERPOWERED and is not scored either way.
#
# Set the numbers back to 400/200/300 or 200/150/300 to reproduce either failure.
DROUGHT_TAX = 30         # ATP collected from every agent, every generation
BIRTH_COST = 40          # what a parent pays into a child's reservoir
GENERATION_ENDOWMENT = 40    # ATP the commons releases per agent per generation


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
