#!/usr/bin/env python3
"""The currency factorial, re-admitted — ALIFE-EXP-012b.

Exactly two changes from ALIFE-EXP-012's harness (6000 reactions per cell; a
C-fire(matter) split into totality and supply) plus one added control
(C-oracle). Everything else is the pilot's, **reused rather than copied**: this
module imports `experiments/alife-exp-012/measure.py` and rebinds its frame, so
the `Soup`, the 2x2 `Gate`, the census, `CounterRandom` wiring, the factorial
arithmetic and the seed-spread gate are the same objects the pilot ran, not a
second copy that could drift from them.

Check-only by default; `--record` writes `results.json` after every control
passes. Judged against `../ALIFE-EXP-012b-the-currency-factorial-preregistration.md`.

THE PILOT SCORES NOTHING. ALIFE-EXP-012's run is the calibration pilot by its
successor's own rule; its unadjudicated factorial numbers are not priors here
and appear nowhere in this receipt.
"""
import argparse
import hashlib
import importlib.util
import json
import platform
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "impl"))

import corpus as C  # noqa: E402
import sigma_alife as al  # noqa: E402


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


PILOT = _load("alife_exp_012_measure",
              HERE.parent / "alife-exp-012" / "measure.py")
# The frame swap, in the open. Every function in PILOT reads `C` as a module
# global at call time, so rebinding it here is what makes "the pilot's machinery
# on 012b's frame" true rather than hopeful — and the assert is what makes it
# checked rather than assumed.
PILOT.C = C
assert PILOT.C.REACTIONS == C.REACTIONS == 6000, "frame rebinding did not take"
assert PILOT.C.C_FIRE_SUPPLY_MIN == 100

sg = al.sg


class Soup012b(PILOT.Soup):
    """The pilot's soup, plus one diagnostic the pilot did not need.

    `eligible_at` is the reaction index of every non-genesis (consumption-
    eligible) R-S event. The pilot could only report how MANY there were; the
    successor's run-length argument is a claim about how they are DISTRIBUTED,
    and that claim is only checkable if somebody writes the indices down.
    """

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.eligible_at = []

    def consume_for(self, agent, z, spent):
        if sg.term_hash(z) not in sg.GENESIS:
            self.eligible_at.append(self.current_reaction)
        return super().consume_for(agent, z, spent)

    def run(self, **kw):
        r = super().run(**kw)
        r["eligible_at"] = self.eligible_at
        r["eligible_events"] = len(self.eligible_at)
        r["last_eligible_reaction"] = (max(self.eligible_at)
                                       if self.eligible_at else None)
        r["eligible_in_first_1000"] = sum(1 for i in self.eligible_at if i < 1000)
        return r


def run_cell(arm, seed, **kw):
    keep = kw.pop("keep_edges", False)
    s = Soup012b(arm, seed, **kw)
    r = s.run(keep_edges=keep)
    if "eligible_events" not in r:            # the free arms never consume
        r["eligible_events"] = r["rs_fired"] - r["rs_genesis"]
    return r


# ---------- C-oracle ----------
def oracle_digest():
    src = al.ORACLE_SOURCE.replace("installed:", "")
    return hashlib.sha256(Path(src).read_bytes()).hexdigest()


def assert_pinned_oracle(where):
    got = oracle_digest()
    return got == C.PINNED_ORACLE_SHA256, got, where


# ---------- checkpointing (D112) ----------
def frame_key():
    """What a cached cell is a cell OF. Any change to the frame, the arms, the
    seeds or the oracle invalidates every checkpoint, because a checkpoint that
    survives a frame change is a stale number wearing a fresh receipt."""
    payload = json.dumps({
        "reactions": C.REACTIONS, "capacity": C.CAPACITY,
        "atp": C.ATP_PER_REACTION, "slice": C.SLICE_ATP,
        "cells": C.CELL, "seeds": list(C.SEEDS),
        "fingerprint": C.fingerprint(), "oracle": oracle_digest(),
    }, sort_keys=True)
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


def cached_cell(arm, seed, verbose=False):
    """One cell, from disk if a checkpoint for THIS frame exists.

    The full grid is twenty cells of about ten seconds each and the controls
    run it twice; a session limit in the middle should not cost the cells that
    already finished."""
    C.CHECKPOINT_DIR.mkdir(exist_ok=True)
    path = C.CHECKPOINT_DIR / f"{frame_key()}-{arm}-{seed}.json"
    if path.exists():
        return json.loads(path.read_text()), True
    t = time.time()
    r = run_cell(arm, seed)
    path.write_text(json.dumps(r, sort_keys=True))
    if verbose:
        print(f"  ... {arm}/{seed} in {time.time() - t:.0f}s", flush=True)
    return r, False


# ---------- controls ----------
def controls(verbose=False):
    out = []

    # C-oracle, at the start. A drift mid-run invalidates the run, not the pin.
    ok_start, got_start, _ = assert_pinned_oracle("start")
    out.append((f"C-oracle(start) the oracle is the repository's pin "
                f"{C.PINNED_ORACLE_SHA256[:16]}... at commit "
                f"{C.PINNED_ORACLE_COMMIT[:12]} (got {got_start[:16]}...)",
                ok_start))
    if not ok_start:
        return False, out, None, None

    out.append((f"C-corpus the corpus is ALIFE-EXP-001's, fingerprint "
                f"{C.fingerprint()}",
                C.fingerprint() == C.INHERITED_FINGERPRINT))

    a, b, c = b"a", b"b", b"c"
    out.append((f"C-core the peeling used by C-compat closes a closed pair "
                f"({len(PILOT.l1_core([(a, b, a), (b, a, b)]))}) and returns "
                f"nothing on an open chain "
                f"({len(PILOT.l1_core([(a, b, c)]))})",
                PILOT.l1_core([(a, b, a), (b, a, b)]) == {a, b}
                and PILOT.l1_core([(a, b, c)]) == set()))

    # C-RNG first: without it no cross-arm comparison is valid.
    rng = PILOT.control_rng()
    cm, sm = rng["counter"], rng["stream"]
    ok_counter = (cm["agree_before"] == cm["keys_before"]
                  and cm["agree_after"] == cm["keys_after"]
                  and cm["keys_after"] > 0 and cm["histories_diverged"])
    out.append((f"C-RNG counter-based draws survive a perturbed history: "
                f"{cm['agree_before']}/{cm['keys_before']} keyed draws before "
                f"reaction {cm['perturbed_at']} and "
                f"{cm['agree_after']}/{cm['keys_after']} after it are "
                f"bit-identical, with the two runs' histories genuinely "
                f"different", ok_counter))
    ok_stream = sm["agree_after"] < sm["keys_after"]
    out.append((f"C-RNG-control the same comparison on a positional stream "
                f"FAILS as it must: only {sm['agree_after']}/"
                f"{sm['keys_after']} draws after the perturbation agree",
                ok_stream))
    if not (ok_counter and ok_stream):
        return False, out, None, rng

    # C-compat, at EXP-007's own run length.
    frozen = C.exp007_frozen()["result"]["primary"]
    diffs = []
    for s in C.COMPAT_SEEDS:
        r = run_cell("BF", s, rng_mode="stream", reactions=C.COMPAT_REACTIONS)
        for f in PILOT.C3_FIELDS:
            if r[f] != frozen[str(s)][f]:
                diffs.append(f"seed {s} {f}: {r[f]!r} != {frozen[str(s)][f]!r}")
    out.append((f"C-compat arm BF reproduces ALIFE-EXP-007's frozen receipt on "
                f"all {len(C.COMPAT_SEEDS)} shared seeds across "
                f"{len(PILOT.C3_FIELDS)} recorded fields at EXP-007's own "
                f"{C.COMPAT_REACTIONS}-reaction length ({len(diffs)} "
                f"divergences)", not diffs))
    for d in diffs[:6]:
        out.append((f"   C-compat detail: {d}", False))

    if verbose:
        print(f"  running {len(C.ARMS) * len(C.SEEDS)} cells at "
              f"{C.REACTIONS} reactions ...", flush=True)
    cells, reused = {}, 0
    for arm in C.ARMS:
        cells[arm] = {}
        for s in C.SEEDS:
            cells[arm][s], hit = cached_cell(arm, s, verbose)
            reused += hit
    flat = [r for arm in cells.values() for r in arm.values()]

    # C-fire(matter), both clauses, both fail-closed.
    ident_bad, supply_low, detail = [], [], []
    for arm in ("BM", "FM"):
        for s in C.SEEDS:
            r = cells[arm][s]
            eligible = r["rs_fired"] - r["rs_genesis"]
            if r["consumed_deaths"] + r["blocked_events"] != eligible:
                ident_bad.append(f"{arm}/{s}")
            if eligible < C.C_FIRE_SUPPLY_MIN:
                supply_low.append(f"{arm}/{s}={eligible}")
            detail.append(
                f"{arm}/{s}: {r['rs_fired']} R-S, {r['rs_genesis']} on genesis, "
                f"{eligible} eligible = {r['consumed_deaths']} consumed + "
                f"{r['blocked_events']} blocked; "
                f"{r.get('eligible_in_first_1000', '?')} of them before "
                f"reaction 1000, last at "
                f"{r.get('last_eligible_reaction', '?')}")
    out.append((f"C-fire(matter/totality) consumed + blocked == eligible R-S, "
                f"exactly, in all 10 M cells ({len(ident_bad)} violations)",
                not ident_bad))
    out.append((f"C-fire(matter/supply) >= {C.C_FIRE_SUPPLY_MIN} eligible "
                f"non-genesis R-S per M cell: "
                f"{[cells['BM'][s]['rs_fired'] - cells['BM'][s]['rs_genesis'] for s in C.SEEDS]} in BM, "
                f"{[cells['FM'][s]['rs_fired'] - cells['FM'][s]['rs_genesis'] for s in C.SEEDS]} in FM"
                + (f" - BELOW THE FLOOR in {len(supply_low)} of 10 cells "
                   f"({', '.join(supply_low)})" if supply_low else ""),
                not supply_low))
    if supply_low:
        for d in detail:
            out.append((f"   C-fire detail: {d}", True))

    bad_price = []
    for arm in C.ARMS:
        want_floor = C.CELL[arm][0] == "floor"
        for s in C.SEEDS:
            charged = cells[arm][s]["rs_price_charged"]
            book = cells[arm][s]["rs_book_price"]
            if want_floor:
                if set(charged) != {str(C.FLOOR_PRICE)}:
                    bad_price.append(f"{arm}/{s} charged {sorted(charged)}")
            elif charged != book:
                bad_price.append(f"{arm}/{s} book price not charged")
    floor_events = sum(cells[arm][s]["rs_fired"]
                       for arm in ("FF", "FM") for s in C.SEEDS)
    out.append((f"C-fire(price) the floor is charged on every R-S in FF and FM "
                f"({floor_events} events, no silent Book-I fallback) and Book I "
                f"on every R-S in BF and BM ({len(bad_price)} violations)",
                not bad_price and floor_events > 0))

    led = [f"{r['arm']}/{r['seed']}" for r in flat
           if not r["ledger_ok"] or not r["ledger_identity_ok"]
           or not r["census_counts_ok"] or r["consumed_but_alive"]]
    out.append((f"C-ledger conservation and census totality on every tick of "
                f"all {len(flat)} cells; "
                f"{sum(r['consumed_deaths'] for r in flat)} consumed deaths and "
                f"{sum(r['waits_outstanding'] for r in flat)} waits at the "
                f"horizon accounted ({len(led)} failures)", not led))

    det = []
    for arm in C.ARMS:
        for s in C.SEEDS:
            again = run_cell(arm, s)
            if {k: v for k, v in again.items() if k != "eligible_at"} != \
               {k: v for k, v in cells[arm][s].items() if k != "eligible_at"}:
                det.append(f"{arm}/{s}")
    out.append((f"C-det every cell run twice gives an identical receipt "
                f"({len(det)} divergences)", not det))

    # C-oracle, at the end.
    ok_end, got_end, _ = assert_pinned_oracle("end")
    out.append((f"C-oracle(end) the oracle did not drift during the run "
                f"(got {got_end[:16]}...)", ok_end))

    return all(ok for _, ok in out), out, cells, rng


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--record", action="store_true")
    ap.add_argument("--controls", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    C.build()
    t0 = time.time()
    ok, results, cells, rng = controls(verbose=args.verbose)
    for name, passed in results:
        print(("OK  " if passed else "FAIL"), name)
    print(f"\n({time.time() - t0:.0f}s)")
    if not ok:
        print("\nALIFE-EXP-012b: CONTROLS FAILED - nothing measured, "
              "nothing recorded")
        return 1
    if args.controls:
        print("\nEXP-012B-CONTROLS: ALL PASS")
        return 0

    fac = PILOT.factorial(cells)
    result = {
        "cells": {arm: {str(s): {k: v for k, v in cells[arm][s].items()
                                 if k != "eligible_at"}
                        for s in C.SEEDS} for arm in C.ARMS},
        "factorial": fac,
        "scores": PILOT.score(fac),
        "rng_control": rng,
    }
    print()
    PILOT.summarize(result)

    prov = al.provenance()
    receipt = {
        "experiment": "ALIFE-EXP-012b",
        "corpus_fingerprint": C.fingerprint(),
        "inherited_from": ["ALIFE-EXP-001", "ALIFE-EXP-007", "ALIFE-EXP-010",
                           "ALIFE-EXP-012 (calibration pilot, scores nothing)"],
        "frame": {"arms": list(C.ARMS), "cells": C.CELL,
                  "arm_labels": C.ARM_LABEL, "seeds": list(C.SEEDS),
                  "compat_seeds": list(C.COMPAT_SEEDS),
                  "capacity": C.CAPACITY, "reactions": C.REACTIONS,
                  "compat_reactions": C.COMPAT_REACTIONS,
                  "atp_per_reaction": C.ATP_PER_REACTION,
                  "slice_atp": C.SLICE_ATP, "floor_price": C.FLOOR_PRICE,
                  "final_window": C.FINAL_WINDOW,
                  "outcomes": list(C.OUTCOMES),
                  "c_fire_supply_min": C.C_FIRE_SUPPLY_MIN,
                  "pinned_oracle_sha256": C.PINNED_ORACLE_SHA256,
                  "pinned_oracle_commit": C.PINNED_ORACLE_COMMIT,
                  "rng": "counter-based, keyed (seed, reaction_index, event)",
                  "engine": "post-ALIFE-EXP-011: D98, D99"},
        "provenance": {
            "sigma_alife_version": prov["sigma_alife_version"],
            "sigma_glyph_requirement": prov["sigma_glyph_requirement"],
            "oracle_sha256": prov["oracle_sha256"],
            "python": ".".join(prov["python"].split(".")[:2]),
            "platform": platform.python_implementation(),
        },
        "controls": {name: passed for name, passed in results},
        "result": result,
    }
    print(f"\noracle: {prov['oracle_source']}  "
          f"(sha256 {prov['oracle_sha256'][:16]}...)")
    if args.record:
        (HERE / "results.json").write_text(
            json.dumps(receipt, indent=2, sort_keys=True) + "\n")
        print(f"recorded {HERE / 'results.json'}")
    else:
        print("\n(check-only; pass --record to write results.json)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
