#!/usr/bin/env python3
"""The soup for ALIFE-EXP-008 — ALIFE-EXP-007's, unchanged.

EXP-007 ended on a named limitation: its L1-core was computed over the whole
reaction history, and a shuffled graph of the same density beat it. Fontana's
organizations are sets that PERSIST in the population. This experiment changes
exactly one thing — what counts as an organization — so the chemistry is
inherited verbatim, including the blind-chosen 200 ATP per reaction.

THE WINDOW IS NOT TUNED. A set is self-maintaining over `W` reactions if every
member is alive AND was re-produced within the last `W` by a pair of members of
the set. `W` is a free parameter, so it was probed on the CHANCE MODEL alone:

    window     25    50   100   200   400   600
    shuffled    0     0     0     0     0     0

The null is empty at every window, so no choice of `W` can favour the hypothesis,
and there is nothing to tune. The whole curve is reported rather than a point.
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


EXP7 = _load("alife_exp_007_corpus", HERE.parent / "alife-exp-007" / "corpus.py")
sg = al.sg

INHERITED_FINGERPRINT = EXP7.INHERITED_FINGERPRINT
SEEDS = EXP7.SEEDS
CAPACITY = EXP7.CAPACITY
REACTIONS = EXP7.REACTIONS
SLICE_ATP = EXP7.SLICE_ATP
ATP_PER_REACTION = EXP7.ATP_PER_REACTION
BUDGET_SWEEP = (50, 200, 3000)          # three, not four: the run is ten minutes

WINDOWS = (25, 50, 100, 200, 400, 600, 1000)

# H2's discrimination factor and H3's cost margin, fixed here before the harness.
MIN_SET_SIZE = 3
DISCRIMINATION_FACTOR = 5.0             # history-core must exceed the persisting set
COST_MARGIN = 0.30                      # sustaining reactions cheaper by this much


def build():
    return EXP7.build()


def fingerprint(entries=None):
    return EXP7.fingerprint(entries)


if __name__ == "__main__":
    print(f"founders {len(build())} at {fingerprint()}, capacity {CAPACITY}, "
          f"{REACTIONS} reactions, budgets {BUDGET_SWEEP}, seeds {SEEDS}")
    print(f"windows {WINDOWS} — the whole curve, because the null is empty at all "
          f"of them and there is nothing to tune")
