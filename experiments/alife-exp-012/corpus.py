#!/usr/bin/env python3
"""The frame for ALIFE-EXP-012 — the currency factorial.

Nothing here is chosen. The preregistration pins the arms, the five seeds and
the corpus, and says the chemistry is "EXP-007's verbatim, as EXP-010 used
them", so every frame constant is READ from ALIFE-EXP-007's own frame rather
than restated. A restated constant is a constant that can drift, and C-compat
scores arm BF against a frozen receipt.

The only numbers this file adds are the ones the preregistration names in prose:
the final window (100 reactions, stated), C-fire's floor of 50 consumptions per
seed, and the four cells of the factorial.
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

# --- inherited, not chosen --------------------------------------------------
INHERITED_FINGERPRINT = EXP7.INHERITED_FINGERPRINT   # 53cc6da80f66d220
CAPACITY = EXP7.CAPACITY                             # 64
REACTIONS = EXP7.REACTIONS                           # 1000
ATP_PER_REACTION = EXP7.ATP_PER_REACTION             # 200, blind-chosen in EXP-007
SLICE_ATP = EXP7.SLICE_ATP                           # 32

# --- the 2x2, pinned by the preregistration ---------------------------------
#   price:  "book"  = Book I's `1 + size(z)`
#           "floor" = the action floor, 1
#   matter: "free"  = the copy is conjured
#           "consume" = a living exact-hash body is required and consumed
ARMS = ("BF", "BM", "FF", "FM")
CELL = {"BF": ("book", "free"), "BM": ("book", "consume"),
        "FF": ("floor", "free"), "FM": ("floor", "consume")}
ARM_LABEL = {"BF": "Book I price, copy free (the unmodified engine)",
             "BM": "Book I price, copy consumed",
             "FF": "floor price, copy free",
             "FM": "floor price, copy consumed (EXP-010's Arm M)"}
FLOOR_PRICE = 1

# --- five seeds, because the estimands are differences ----------------------
SEEDS = (20260825, 20260826, 20260827, 20260828, 20260829)
# EXP-007's frozen receipt covers only the first three; C-compat uses those.
COMPAT_SEEDS = tuple(EXP7.SEEDS)

# --- outcomes and the window ------------------------------------------------
FINAL_WINDOW = 100          # stated in the preregistration
OUTCOMES = ("settled", "census", "distinct_nongenesis", "window_success")
OUTCOME_LABEL = {
    "settled": "settled count (reactions reaching a normal form)",
    "census": "living census at the final tick",
    "distinct_nongenesis": "distinct non-genesis hashes alive at the final tick",
    "window_success": f"success rate over the last {FINAL_WINDOW} reactions",
}

# --- controls ---------------------------------------------------------------
C_FIRE_MIN_CONSUMED = 50    # per seed, in BM and FM
RNG_EVENTS = ("reactant_a", "reactant_b")   # the per-reaction keys a
                                            # decorrelation control can compare
RNG_REFERENCE_MODULUS = 1000                # a fixed n, so a draw comparison is
                                            # about the KEY and not about a soup
                                            # length that legitimately differs
ORACLE_BUDGET = 400_000


def build():
    entries = EXP7.build()
    got = EXP7.fingerprint(entries)
    if got != INHERITED_FINGERPRINT:
        raise SystemExit(f"ALIFE-EXP-012 inherits the EXP-001 corpus through "
                         f"EXP-007, which has moved: expected "
                         f"{INHERITED_FINGERPRINT}, got {got}.")
    return entries


def fingerprint(entries=None):
    return EXP7.fingerprint(entries or build())


def exp007_frozen():
    return json.loads(EXP7_RECEIPT.read_text())


if __name__ == "__main__":
    c = build()
    print(f"founders: {len(c)} terms from ALIFE-EXP-001 at {fingerprint(c)}")
    print(f"capacity {CAPACITY}, {REACTIONS} reactions, {ATP_PER_REACTION} "
          f"ATP/reaction, slice {SLICE_ATP}")
    print(f"seeds {SEEDS} ({len(SEEDS)}); C-compat seeds {COMPAT_SEEDS}")
    for arm in ARMS:
        price, matter = CELL[arm]
        print(f"  {arm}: price={price:<6s} matter={matter:<8s}  {ARM_LABEL[arm]}")
