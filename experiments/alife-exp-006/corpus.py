#!/usr/bin/env python3
"""The population and the pulsed economy for ALIFE-EXP-006.

EXP-001's corpus for the fifth time, pinned. This experiment changes one thing —
how ATP arrives — and a new corpus would change two.

THE ONE TUNED NUMBER, chosen blind before the hypotheses were written, by running
the equal-split arm ALONE and taking a total inside a 25-75% settle band:

    total  pulses  settled          total  pulses  settled
     1200       4   21/64  33%       2000       4   38/64  59%
     1200      16   16/64  25%       2000      16   37/64  58%
     1600       4   31/64  48%       2400       4   50/64  78%
     1600      16   20/64  31%       3200      16   60/64  94%

No concentrating policy and no restart arm was computed while choosing it. At
2000 ATP roughly half the colony's spend — ~1000 ATP — sits in agents that never
finish, which is the headroom a policy could take.
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
ATP_TOTAL = 2000            # blind-chosen; equal split settles 58% of 64
PULSE_COUNTS = (2, 4, 8, 16, 32)
SLICE_ATP = 32
POWER_BAND = (0.25, 0.75)   # the equal-split arm must land inside it, or the run
                            # is reported UNADJUDICATED rather than scored

POLICIES = ("equal", "invested", "smallest", "random")
RESTART_POLICIES = ("restart-eager", "restart-patient")


def build():
    entries = EXP1.build()
    got = EXP1.fingerprint(entries)
    if got != INHERITED_FINGERPRINT:
        raise SystemExit(f"ALIFE-EXP-006 inherits the EXP-001 corpus, which has "
                         f"moved: expected {INHERITED_FINGERPRINT}, got {got}.")
    return entries


def fingerprint(entries=None):
    return EXP1.fingerprint(entries or build())


if __name__ == "__main__":
    c = build()
    print(f"corpus: {len(c)} terms, inherited from ALIFE-EXP-001 at {fingerprint(c)}")
    print(f"total {ATP_TOTAL} ATP, pulses {PULSE_COUNTS}, policies {POLICIES}, "
          f"restart arms {RESTART_POLICIES}, power band {POWER_BAND}")
