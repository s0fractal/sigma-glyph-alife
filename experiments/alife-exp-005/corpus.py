#!/usr/bin/env python3
"""The population for ALIFE-EXP-005 — ALIFE-EXP-001's, for the fourth time.

EXP-005 changes one thing about the machine: what a duplication is charged. A new
corpus would change two things at once. The terms are imported unchanged and
pinned; if that file moves, this one refuses to run.
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
ATP_PER_AGENT = 3000        # as EXP-001: enough that everyone settles under Book I
SLICE_ATP = 32
TICKS = 24

# The counterfactual's only free parameter. A copy price is the size of the tree
# a duplication WOULD have to write out, and over a DAG that is exponential in
# depth, so it is capped and the cap is reported. A cap that is hit is not a
# measurement failure — it is the finding, in its loudest form.
DEEP_SIZE_CAP = 10 ** 9


def build():
    entries = EXP1.build()
    got = EXP1.fingerprint(entries)
    if got != INHERITED_FINGERPRINT:
        raise SystemExit(
            f"ALIFE-EXP-005 inherits the EXP-001 corpus, which has moved: "
            f"expected {INHERITED_FINGERPRINT}, got {got}.")
    return entries


def fingerprint(entries=None):
    return EXP1.fingerprint(entries or build())


if __name__ == "__main__":
    c = build()
    print(f"corpus: {len(c)} terms, inherited from ALIFE-EXP-001 at {fingerprint(c)}")
    print(f"budget {ATP_PER_AGENT}/agent, slice {SLICE_ATP}, ticks {TICKS}, "
          f"deep-size cap {DEEP_SIZE_CAP}")
