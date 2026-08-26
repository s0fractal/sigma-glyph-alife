#!/usr/bin/env python3
"""The frame for ALIFE-EXP-010 — everything matched between the two arms.

Nothing here is chosen. The preregistration pins the founders (EXP-001's corpus
at `53cc6da80f66d220`), the seeds, and "the ALIFE-EXP-007 chemistry verbatim: its
reaction rules, its parameters as recorded in its receipt", so every frame
constant below is *read from* ALIFE-EXP-007's own frame rather than restated —
a restated constant is a constant that can drift, and Arm E has to reproduce a
frozen receipt.

The only numbers this file adds are the ones the preregistration names and does
not size: H3's final window (`DECISIONS.md` D79) and the control thresholds the
prereg states in prose (C2's 50 consumptions, H1's 0.5, H2's 3-of-3 and 2-of-3,
H3's 10 points).
"""
import importlib.util
import json
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
EXP7_RECEIPT = HERE.parent / "alife-exp-007" / "results.json"
sg = al.sg

# --- matched between the arms, inherited, not chosen -----------------------
INHERITED_FINGERPRINT = EXP7.INHERITED_FINGERPRINT
CAPACITY = EXP7.CAPACITY                 # 64
REACTIONS = EXP7.REACTIONS               # 1000
ATP_PER_REACTION = EXP7.ATP_PER_REACTION  # 200, blind-chosen in EXP-007
SLICE_ATP = EXP7.SLICE_ATP               # 32

# --- pinned by the preregistration -----------------------------------------
SEEDS = (20260825, 20260826, 20260827)
ARMS = ("E", "M")

# --- the two prices of one rule --------------------------------------------
# Arm E charges Book I's price for R-S, which is `1 + size(z)` and is not a
# constant. Arm M charges the action floor. There is no third choice to make:
# the prereg fixes both.
MATTER_PRICE = 1

# --- thresholds the prereg states in prose ---------------------------------
H1_OVERLAP_MAX = 0.5          # Jaccard(E survivors, M survivors) must be BELOW
H1_MIN_SEEDS = 2              # ... in at least 2 of 3
H2_CENSUS_SEEDS = 3           # M's living census strictly smaller in 3 of 3
H2_DISTINCT_SEEDS = 2         # ... and strictly fewer distinct hashes in >= 2
H3_MARGIN = 0.10              # M's final-window success rate exceeds E's by >= 10 pts
H3_MIN_SEEDS = 2
C2_MIN_CONSUMED = 50          # consumption must actually fire, per seed, in Arm M

# --- the one thing the prereg leaves unsized (D79) --------------------------
FINAL_WINDOW = 100            # EXP-007's own trace granularity
SENSITIVITY_WINDOWS = (100, 200, 400)   # reported beside it; score nothing

# --- nulls (D85) ------------------------------------------------------------
NULL_DRAWS = 20               # one permutation is not a null: D54
NULL_LOCAL_WINDOW = 200       # EXP-008's locality-preserving model needs a window


def build():
    entries = EXP7.build()
    got = EXP7.fingerprint(entries)
    if got != INHERITED_FINGERPRINT:
        raise SystemExit(f"ALIFE-EXP-010 inherits the EXP-001 corpus through "
                         f"EXP-007, which has moved: expected "
                         f"{INHERITED_FINGERPRINT}, got {got}.")
    return entries


def fingerprint(entries=None):
    return EXP7.fingerprint(entries or build())


def exp007_frozen():
    """ALIFE-EXP-007's committed receipt. Arm E is scored against this and not
    against a re-run of EXP-007's code: a re-run would check that two copies of
    one program agree, which is not what C3 asks."""
    return json.loads(EXP7_RECEIPT.read_text())


if __name__ == "__main__":
    c = build()
    print(f"founders: {len(c)} terms from ALIFE-EXP-001 at {fingerprint(c)}")
    print(f"arms {ARMS}; capacity {CAPACITY}, {REACTIONS} reactions, "
          f"{ATP_PER_REACTION} ATP/reaction, slice {SLICE_ATP}, seeds {SEEDS}")
    print(f"R-S price: Arm E = 1 + size(z) (Book I), Arm M = {MATTER_PRICE} "
          f"(the action floor) plus one consumed body")
    frozen = exp007_frozen()["result"]["primary"]
    print("EXP-007 frozen primary (what Arm E must reproduce):")
    for s in SEEDS:
        r = frozen[str(s)]
        print(f"  {s}  ok={r['ok']:4d} closure={r['closure']:.6f} "
              f"distinct={r['distinct']:3d} core={r['core_size']:3d} "
              f"pool_left={r['pool_left']}")
