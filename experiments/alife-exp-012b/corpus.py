#!/usr/bin/env python3
"""The frame for ALIFE-EXP-012b — the currency factorial, re-admitted.

EXP-012's frame verbatim, with **exactly the two changes** its successor
preregistration names, and one added control constant. Everything else is read
from ALIFE-EXP-012's own frame module rather than restated, so "incorporated
verbatim by reference" is true of the code and not only of the prose: a
constant that is restated is a constant that can drift.
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


PILOT = _load("alife_exp_012_corpus",
              HERE.parent / "alife-exp-012" / "corpus.py")
sg = al.sg

# --- verbatim from ALIFE-EXP-012, by reference ------------------------------
INHERITED_FINGERPRINT = PILOT.INHERITED_FINGERPRINT
CAPACITY = PILOT.CAPACITY
ATP_PER_REACTION = PILOT.ATP_PER_REACTION
SLICE_ATP = PILOT.SLICE_ATP
ARMS = PILOT.ARMS
CELL = PILOT.CELL
ARM_LABEL = PILOT.ARM_LABEL
FLOOR_PRICE = PILOT.FLOOR_PRICE
SEEDS = PILOT.SEEDS
COMPAT_SEEDS = PILOT.COMPAT_SEEDS
FINAL_WINDOW = PILOT.FINAL_WINDOW          # 100; not one of the two changes
OUTCOMES = PILOT.OUTCOMES
OUTCOME_LABEL = PILOT.OUTCOME_LABEL
RNG_EVENTS = PILOT.RNG_EVENTS
RNG_REFERENCE_MODULUS = PILOT.RNG_REFERENCE_MODULUS
ORACLE_BUDGET = PILOT.ORACLE_BUDGET
build = PILOT.build
fingerprint = PILOT.fingerprint
exp007_frozen = PILOT.exp007_frozen

# --- CHANGE 1 of 2: run length ----------------------------------------------
REACTIONS = 6000
# C-compat scores arm BF against ALIFE-EXP-007's committed receipt, which is a
# 1000-reaction measurement. The control therefore runs at EXP-007's length —
# that is what "reproduces EXP-007's frozen receipt" can possibly mean — while
# the measurement runs at 6000. See DECISIONS.md D111.
COMPAT_REACTIONS = PILOT.REACTIONS         # 1000, EXP-007's

# --- CHANGE 2 of 2: the admission rule, split in two ------------------------
# totality: `consumed + blocked == R-S fired - R-S on genesis`, exactly, per M
#   cell. The pilot's own diagnostic, promoted to a control: the mechanism must
#   miss nothing eligible.
# supply:   eligible (non-genesis) R-S events >= 100 per M cell. A power floor
#   on the EVENT BASE, which is what the pilot's floor was mistakenly pointed at
#   the mechanism about.
C_FIRE_SUPPLY_MIN = 100

# --- the added control ------------------------------------------------------
# D109: the sibling oracle drifted mid-session during the pilot. Every 012b
# number must be produced against the repository's pinned oracle, asserted at
# the start AND the end of the run — a drift mid-run invalidates the run, not
# the pin.
PINNED_ORACLE_SHA256 = \
    "413d1f9805cdbdf42f13d967a17be26eb959c692eeb067e7146203ed9cebe64d"
PINNED_ORACLE_COMMIT = "d3f1b512a967b9c50111684efa512a48fce9ef8d"

# --- checkpointing (D112) ---------------------------------------------------
CHECKPOINT_DIR = HERE / "checkpoints"


if __name__ == "__main__":
    c = build()
    print(f"founders: {len(c)} terms from ALIFE-EXP-001 at {fingerprint(c)}")
    print(f"CHANGE 1: {REACTIONS} reactions per cell (pilot: {PILOT.REACTIONS})")
    print(f"CHANGE 2: C-fire(matter) = totality (identity, per M cell) + "
          f"supply (>= {C_FIRE_SUPPLY_MIN} eligible R-S per M cell)")
    print(f"ADDED   : C-oracle, pinned digest {PINNED_ORACLE_SHA256[:16]}... "
          f"at commit {PINNED_ORACLE_COMMIT[:12]}")
    print(f"verbatim: arms {ARMS}, seeds {SEEDS}, capacity {CAPACITY}, "
          f"{ATP_PER_REACTION} ATP/reaction, window {FINAL_WINDOW}")
    print(f"C-compat runs at {COMPAT_REACTIONS} reactions (EXP-007's length)")
