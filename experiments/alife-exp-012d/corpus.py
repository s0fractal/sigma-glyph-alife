#!/usr/bin/env python3
"""The frame for ALIFE-EXP-012d — does the PRICE choose the phase?

ALIFE-EXP-012c's frame verbatim, read from that module rather than restated,
with the two changes its successor preregistration names: twelve fresh seeds,
and a phase-by-arm primary outcome carrying a permutation null.
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


PREV = _load("alife_exp_012c_corpus",
             HERE.parent / "alife-exp-012c" / "corpus.py")
sg = al.sg

# --- verbatim from ALIFE-EXP-012c, by reference -----------------------------
INHERITED_FINGERPRINT = PREV.INHERITED_FINGERPRINT
CAPACITY = PREV.CAPACITY
ATP_PER_REACTION = PREV.ATP_PER_REACTION
SLICE_ATP = PREV.SLICE_ATP
ARMS = PREV.ARMS
CELL = PREV.CELL
ARM_LABEL = PREV.ARM_LABEL
FLOOR_PRICE = PREV.FLOOR_PRICE
COMPAT_SEEDS = PREV.COMPAT_SEEDS          # EXP-007's; see C-fresh's exemption
COMPAT_REACTIONS = PREV.COMPAT_REACTIONS
FINAL_WINDOW = PREV.FINAL_WINDOW
OUTCOMES = PREV.OUTCOMES
OUTCOME_LABEL = PREV.OUTCOME_LABEL
ORACLE_BUDGET = PREV.ORACLE_BUDGET
REACTIONS = PREV.REACTIONS                # 6000
C_FIRE_SUPPLY_MIN = PREV.C_FIRE_SUPPLY_MIN
PHASE_THRESHOLD = PREV.PHASE_THRESHOLD    # 3000
PRODUCING = PREV.PRODUCING
COLLAPSED = PREV.COLLAPSED
DISCORDANT = PREV.DISCORDANT
PINNED_ORACLE_SHA256 = PREV.PINNED_ORACLE_SHA256
PINNED_ORACLE_COMMIT = PREV.PINNED_ORACLE_COMMIT
build = PREV.build
fingerprint = PREV.fingerprint
exp007_frozen = PREV.exp007_frozen

# --- CHANGE 1 of 2: twelve fresh seeds, pinned ------------------------------
SEEDS = tuple(range(20260830, 20260842))          # 20260830 ... 20260841
assert len(SEEDS) == 12

# The experiments whose seeds C-fresh forbids. Read from their committed frames
# rather than restated, so a seed added to one of them later cannot quietly stop
# being forbidden here.
PRIOR_EXPERIMENTS = ("alife-exp-010", "alife-exp-011", "alife-exp-012",
                     "alife-exp-012b", "alife-exp-012c")


def forbidden_seeds():
    out = {}
    for i, name in enumerate(PRIOR_EXPERIMENTS):
        mod = _load(f"_fresh_probe_{i}", HERE.parent / name / "corpus.py")
        out[name] = tuple(mod.SEEDS)
    return out


# --- CHANGE 2 of 2: the phase-by-arm null -----------------------------------
# Within each seed, permute the four arm labels. This holds each seed's multiset
# of phases and last-eligible indices fixed and destroys only the association
# between an ARM and its outcome, which is the association every hypothesis
# below is about.
NULL_DRAWS = 1000
NULL_SEED_TEMPLATE = "EXP-012d/null/{draw}"

XD1_MIN_DIFF = 8            # #producing(floor) - #producing(book), of 24 each
XD1_ALPHA = 0.05
XD2_PERCENTILE = 95         # observed must fall BELOW this percentile of the null
XD4_MIN_RATIO = 0.75        # book earlier in >= 3 of every 4 qualifying seeds
XD4_MIN_SEEDS = 4
XD4_ALPHA = 0.05

BOOK_ARMS = ("BF", "BM")
FLOOR_ARMS = ("FF", "FM")
FREE_ARMS = ("BF", "FF")
MATTER_ARMS = ("BM", "FM")

CHECKPOINT_DIR = HERE / "checkpoints"


if __name__ == "__main__":
    c = build()
    print(f"founders: {len(c)} terms from ALIFE-EXP-001 at {fingerprint(c)}")
    print(f"verbatim from 012c: arms {ARMS}, {REACTIONS} reactions, "
          f"phase threshold {PHASE_THRESHOLD}, supply floor {C_FIRE_SUPPLY_MIN}")
    print(f"CHANGE 1: {len(SEEDS)} fresh seeds {SEEDS[0]}..{SEEDS[-1]} "
          f"-> {len(ARMS) * len(SEEDS)} cells")
    for name, seeds in forbidden_seeds().items():
        print(f"          forbidden by C-fresh via {name}: {seeds}")
    print(f"CHANGE 2: phase-by-arm primary outcome; permutation null over arm "
          f"labels within a seed, {NULL_DRAWS} draws, seeded "
          f"sha256(\"{NULL_SEED_TEMPLATE}\")")
