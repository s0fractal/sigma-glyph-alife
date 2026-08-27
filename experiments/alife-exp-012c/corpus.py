#!/usr/bin/env python3
"""The frame for ALIFE-EXP-012c — does the currency choose the phase?

ALIFE-EXP-012b's frame verbatim, read from that module rather than restated,
plus the three changes its successor preregistration names and nothing else.
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


B = _load("alife_exp_012b_corpus",
          HERE.parent / "alife-exp-012b" / "corpus.py")
sg = al.sg

# --- verbatim from ALIFE-EXP-012b, by reference -----------------------------
INHERITED_FINGERPRINT = B.INHERITED_FINGERPRINT
CAPACITY = B.CAPACITY
ATP_PER_REACTION = B.ATP_PER_REACTION
SLICE_ATP = B.SLICE_ATP
ARMS = B.ARMS
CELL = B.CELL
ARM_LABEL = B.ARM_LABEL
FLOOR_PRICE = B.FLOOR_PRICE
SEEDS = B.SEEDS
COMPAT_SEEDS = B.COMPAT_SEEDS
COMPAT_REACTIONS = B.COMPAT_REACTIONS
FINAL_WINDOW = B.FINAL_WINDOW
OUTCOMES = B.OUTCOMES
OUTCOME_LABEL = B.OUTCOME_LABEL
RNG_EVENTS = B.RNG_EVENTS
RNG_REFERENCE_MODULUS = B.RNG_REFERENCE_MODULUS
ORACLE_BUDGET = B.ORACLE_BUDGET
REACTIONS = B.REACTIONS                      # 6000, measured sufficient to classify
C_FIRE_SUPPLY_MIN = B.C_FIRE_SUPPLY_MIN      # 100
PINNED_ORACLE_SHA256 = B.PINNED_ORACLE_SHA256
PINNED_ORACLE_COMMIT = B.PINNED_ORACLE_COMMIT
build = B.build
fingerprint = B.fingerprint
exp007_frozen = B.exp007_frozen

# --- CHANGE 1 of 3: phase classification, pinned ----------------------------
# PRODUCING iff at least one eligible (non-genesis) R-S event occurs AFTER
# reaction 3000; else COLLAPSED. The threshold sits in the gap the pilots
# measured — stoppers stop below 1100, producers reach 5000+ — and is fixed
# here, before any 012c cell has run. Moving it after seeing classifications is
# on the worthlessness list.
PHASE_THRESHOLD = 3000
PRODUCING = "PRODUCING"
COLLAPSED = "COLLAPSED"
DISCORDANT = "DISCORDANT"

# --- CHANGE 2 of 3: the supply floor is scoped ------------------------------
# `eligible >= C_FIRE_SUPPLY_MIN` per M cell, among PRODUCING cells only. A
# COLLAPSED cell is an outcome, not a broken instrument.

# --- CHANGE 3 of 3: phase is the primary outcome ----------------------------
# The 012/012b factorial estimands become conditional; see XC2.
XC2_MIN_PRODUCING_SEEDS = 2
XC2_SMALL_BASE_N = 4          # below this, the RESULT carries the verbatim
                              # "n producing seeds is a small base" sentence
XC3_MIN_COLLAPSED_SEEDS = 2
XC3_MIN_ARMS_PER_SEED = 2

CHECKPOINT_DIR = HERE / "checkpoints"


if __name__ == "__main__":
    c = build()
    print(f"founders: {len(c)} terms from ALIFE-EXP-001 at {fingerprint(c)}")
    print(f"verbatim from 012b: arms {ARMS}, seeds {SEEDS}, "
          f"{REACTIONS} reactions, supply floor {C_FIRE_SUPPLY_MIN}, "
          f"window {FINAL_WINDOW}")
    print(f"CHANGE 1: phase = PRODUCING iff an eligible R-S occurs after "
          f"reaction {PHASE_THRESHOLD}")
    print(f"CHANGE 2: the supply floor applies to PRODUCING M cells only")
    print(f"CHANGE 3: phase is the primary outcome; the factorial is "
          f"conditional on >= {XC2_MIN_PRODUCING_SEEDS} producing seeds")
