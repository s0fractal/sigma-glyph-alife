#!/usr/bin/env python3
"""The population and the frame for ALIFE-EXP-003. Fixed here, before the harness.

The terms are ALIFE-EXP-001's, unchanged and pinned, for the third time and for
the same reason: this experiment changes ONE thing about the colony — where its
ATP goes — and a new corpus would answer that question and another one at once.

What is new is the frame, and one number in it was chosen with the arm comparison
deliberately hidden. See SCARCITY below.
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
SLICE_ATP = 32
TICKS = 24

# THE SCARCITY LEVEL, and how it was chosen. A colony that can settle every agent
# without help cannot be helped: at 4000 ATP 53 of 64 agents reach a normal form
# on their own, and any library is then pure overhead. A colony too poor to settle
# anything cannot be helped either. So the level was picked by running the s=0 arm
# alone — nothing but "how many settle when the colony spends everything on
# agents" — and taking the one inside a 40–70% band. The sweep's other arms were
# not computed, looked at, or guessed at while choosing it.
#
#   600 -> 9/64    900 -> 12/64   1200 -> 21/64   1600 -> 30/64
#   2000 -> 33/64  2800 -> 39/64  4000 -> 53/64
#
ATP_TOTAL = 2000                        # 33/64 = 52% settle unaided
SCARCITY = (1200, 2000, 2800)           # secondary levels, all preregistered here,
                                        # so no conclusion rests on one economy

# The colony's whole endowment is split: a share `s` to the library, the rest
# divided equally among the agents. EVERY arm has the same total ATP — otherwise
# the experiment would measure "more ATP is better", which needs no experiment.
SHARES = (0.0, 0.1, 0.25, 0.5, 0.75)

# H3 varies population size at a FIXED per-agent budget, so redundancy is the only
# thing changing, and at a FIXED share chosen here rather than at whichever share
# turns out to win.
H3_SHARE = 0.25
H3_SIZES = (16, 32, 64)
H3_PER_AGENT = ATP_TOTAL // 64          # = 31


def build():
    entries = EXP1.build()
    got = EXP1.fingerprint(entries)
    if got != INHERITED_FINGERPRINT:
        raise SystemExit(
            f"ALIFE-EXP-003 inherits the EXP-001 corpus, which has moved: "
            f"expected {INHERITED_FINGERPRINT}, got {got}.")
    return entries


def fingerprint(entries=None):
    return EXP1.fingerprint(entries or build())


if __name__ == "__main__":
    c = build()
    print(f"corpus: {len(c)} terms, inherited from ALIFE-EXP-001 at {fingerprint(c)}")
    print(f"scarcity {SCARCITY} (primary {ATP_TOTAL}), shares {SHARES}")
    print(f"H3: sizes {H3_SIZES} at share {H3_SHARE}, {H3_PER_AGENT} ATP per agent")
