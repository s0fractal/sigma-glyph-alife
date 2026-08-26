#!/usr/bin/env python3
"""A population that demands hashes the environment has not delivered yet.

ALIFE-EXP-001's corpus for the seventh time, each term applied to one **withheld**
hash: the bytes exist, their address is known, and the store does not hold them
until a schedule releases them.

Book I §3.5 makes `DISSONANCE(Unresolved Reference)` an outcome *relative to a
store* — "h is not in the store and is not an intrinsic axiom" — and §3.4 says a
failed resolve is not charged. `impl/sigma_alife.py` nevertheless treats
UNRESOLVED as terminal: `RUNNABLE = (LIVE, STARVED)`. So an agent that reaches a
hash which has not arrived is dead in this substrate and merely *waiting* in the
specification.

THE BLIND PROBE. Only one number was measured before the hypotheses were written:
how many agents block at all. If almost none did, the arms could not differ.

    ATP/agent   blocked on a future hash   settled   starved
          100                      46/64        10         8
          300                      51/64        13         0
         1000                      51/64        13         0

300 is the primary: 51 of 64 block, none starve, so "blocked" and "out of budget"
do not mix. 100 is the secondary, where they do.
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
ATP_PER_AGENT = 300              # blind-chosen: 51/64 block, 0 starve
ATP_SWEEP = (100, 300)
SLICE_ATP = 32
TICKS = 24
# How late the environment delivers, as a multiple of the run's length. At 0.5
# everything has arrived by half-time; at 4 only about a quarter arrives at all.
SPREADS = (0.5, 1.0, 2.0, 4.0)

MIN_BLOCKED_FRACTION = 0.25      # power, stated here rather than in the harness
H1_RECOVERY = 30                 # arm B must settle at least this many more
H2_LATE_CEILING = 0.5            # spread 4 recovers at most half of spread 1


def withheld(i):
    """The i-th term the environment will deliver. Deterministic, and small: the
    experiment is about WHEN it arrives, not about what it costs."""
    t = ("lit", sg.sha(b"future-%d" % i))
    for _ in range(i % 3):
        t = ("app", t, ("lit", sg.sha(b"I")))
    return t


def build():
    entries = EXP1.build()
    got = EXP1.fingerprint(entries)
    if got != INHERITED_FINGERPRINT:
        raise SystemExit(f"ALIFE-EXP-009 inherits the EXP-001 corpus, which has "
                         f"moved: expected {INHERITED_FINGERPRINT}, got {got}.")
    return entries


def fingerprint(entries=None):
    return EXP1.fingerprint(entries)


if __name__ == "__main__":
    c = build()
    print(f"founders {len(c)} from ALIFE-EXP-001 at {fingerprint(c)}")
    print(f"primary {ATP_PER_AGENT} ATP/agent, sweep {ATP_SWEEP}, ticks {TICKS}, "
          f"delivery spreads {SPREADS}")
    print(f"power: at least {int(100 * MIN_BLOCKED_FRACTION)}% must block, or "
          f"UNADJUDICATED")
