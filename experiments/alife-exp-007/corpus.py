#!/usr/bin/env python3
"""The soup and its economy for ALIFE-EXP-007.

Founders are ALIFE-EXP-001's corpus, pinned, for the sixth time. What changes
here is the only interaction this substrate has that is native to it: one agent
applied to another **by root hash**.

THE ONE TUNED NUMBER, chosen blind before the hypotheses were written, by
measuring nothing but the reaction success rate and the surviving diversity. No
closure, no organization and no core was computed while choosing it:

    ATP/reaction   successful   distinct hashes
              50      179/400 45%           54
             200      261/400 65%           46
             800      348/400 87%           56
            3000      375/400 94%           61
           12000      398/400 100%          60

200 is the primary: a price at which a third of reactions are unaffordable, so
the budget is selective, and diversity is nowhere near collapsing.
"""
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "impl"))

import sigma_alife as al  # noqa: E402


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


EXP1 = _load("alife_exp_001_corpus", HERE.parent / "alife-exp-001" / "corpus.py")
sg = al.sg

INHERITED_FINGERPRINT = "53cc6da80f66d220"

SEED = 20260825
SEEDS = (20260825, 20260826, 20260827)
CAPACITY = 64               # AlChemy's rule: hold the population size fixed by
                            # discarding a uniformly random member
REACTIONS = 1000
ATP_PER_REACTION = 200      # blind-chosen; 65% of reactions succeed
BUDGET_SWEEP = (50, 200, 800, 3000)
SLICE_ATP = 32

# Power, stated here rather than left to the harness (DECISIONS.md D42, D45).
MIN_SUCCESS_RATE = 0.20
MIN_DISTINCT = 8


def build():
    entries = EXP1.build()
    got = EXP1.fingerprint(entries)
    if got != INHERITED_FINGERPRINT:
        raise SystemExit(f"ALIFE-EXP-007 inherits the EXP-001 corpus, which has "
                         f"moved: expected {INHERITED_FINGERPRINT}, got {got}.")
    return entries


def fingerprint(entries=None):
    return EXP1.fingerprint(entries or build())


if __name__ == "__main__":
    c = build()
    print(f"founders: {len(c)} terms from ALIFE-EXP-001 at {fingerprint(c)}")
    print(f"capacity {CAPACITY}, {REACTIONS} reactions, primary budget "
          f"{ATP_PER_REACTION} ATP/reaction, sweep {BUDGET_SWEEP}, seeds {SEEDS}")
    print(f"power: >= {int(100*MIN_SUCCESS_RATE)}% reactions succeed and "
          f">= {MIN_DISTINCT} distinct hashes, else UNADJUDICATED")
