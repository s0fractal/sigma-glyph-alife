#!/usr/bin/env python3
"""Does the currency choose the PHASE? — ALIFE-EXP-012c.

The two pilots established that a soup either keeps producing non-genesis
structure to the horizon or collapses onto the genesis floor early and produces
zero eligible events thereafter, and that run length is not a remedy. Collapse
is therefore promoted from an admission failure to the primary outcome, and the
question moves one level up: does the duplication currency choose which phase a
soup lands in?

Three changes from ALIFE-EXP-012b's harness, and nothing else:
  1. phase classification per cell (PRODUCING iff an eligible R-S occurs after
     reaction 3000, pinned in `corpus.py` before any cell ran);
  2. the supply floor applies to PRODUCING M cells only;
  3. phase is the primary outcome; the factorial becomes conditional.

Check-only by default; `--record` writes `results.json` after every control
passes. Judged against
`../ALIFE-EXP-012c-does-the-currency-choose-the-phase-preregistration.md`,
committed at `73e1ca2` — BEFORE this repository's pilot findings artifact, which
is the ordering its contamination declaration depends on.

THE PILOTS SCORE NOTHING, EVER. No number from ALIFE-EXP-012 or 012b is a prior
here; the two supply their ground truth (totality, bimodality) and no estimates.
"""
import argparse
import hashlib
import importlib.util
import json
import platform
import statistics
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


# One load chain (012c -> 012b -> 012), then both frames rebound to 012c's, in
# the open, with an assert that it took. This is D110's pattern at its second
# generation: the `Soup`, the 2x2 `Gate`, the census, the `CounterRandom`
# wiring, the factorial arithmetic and the seed-spread gate are the same objects
# the pilots ran.
B = _load("alife_exp_012b_measure",
          HERE.parent / "alife-exp-012b" / "measure.py")
P = B.PILOT
P.C = C
B.C = C
assert P.C is C and B.C is C, "frame rebinding did not take"
assert P.C.REACTIONS == 6000 and P.C.PHASE_THRESHOLD == 3000

sg = al.sg


class Soup012c(P.Soup):
    """The pilots' soup, with eligible-event indices recorded in EVERY arm.

    012b instrumented `consume_for`, which only the matter arms call, so the
    free arms had counts but no indices. The phase is defined on eligible events,
    which exist in all four arms — a duplication of a non-genesis term is
    eligible whether or not this arm makes it pay a body — so classification has
    to be computable in all twenty cells, and XC1 is precisely the question of
    whether the four arms of a seed agree.

    `note_rs_bound` is called once per R-S in every arm, before the free/consume
    branch, which makes it the one hook that sees them all. The counts it
    observes are unchanged: C-det runs every cell twice and C-eligible checks the
    indices against the independent `rs_fired - rs_genesis` counter.
    """

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.eligible_at = []

    def note_rs_bound(self, agent, z, spent, charged):
        if sg.term_hash(z) not in sg.GENESIS:
            self.eligible_at.append(self.current_reaction)
        return super().note_rs_bound(agent, z, spent, charged)

    def run(self, **kw):
        r = super().run(**kw)
        at = self.eligible_at
        r["eligible_at"] = at
        r["eligible_events"] = len(at)
        r["last_eligible_reaction"] = max(at) if at else None
        r["first_eligible_reaction"] = min(at) if at else None
        r["eligible_after_threshold"] = sum(1 for i in at
                                            if i > C.PHASE_THRESHOLD)
        r["eligible_in_first_1000"] = sum(1 for i in at if i < 1000)
        r["phase"] = (C.PRODUCING if r["eligible_after_threshold"] > 0
                      else C.COLLAPSED)
        return r


def run_cell(arm, seed, **kw):
    keep = kw.pop("keep_edges", False)
    return Soup012c(arm, seed, **kw).run(keep_edges=keep)


# ---------- checkpointing (D112, same discipline) ----------
def frame_key():
    payload = json.dumps({
        "reactions": C.REACTIONS, "capacity": C.CAPACITY,
        "atp": C.ATP_PER_REACTION, "slice": C.SLICE_ATP,
        "cells": C.CELL, "seeds": list(C.SEEDS),
        "threshold": C.PHASE_THRESHOLD,
        "fingerprint": C.fingerprint(), "oracle": B.oracle_digest(),
    }, sort_keys=True)
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


def cached_cell(arm, seed, verbose=False):
    C.CHECKPOINT_DIR.mkdir(exist_ok=True)
    path = C.CHECKPOINT_DIR / f"{frame_key()}-{arm}-{seed}.json"
    if path.exists():
        return json.loads(path.read_text()), True
    t = time.time()
    r = run_cell(arm, seed)
    path.write_text(json.dumps(r, sort_keys=True))
    if verbose:
        print(f"  ... {arm}/{seed} {r['phase']} in {time.time() - t:.0f}s",
              flush=True)
    return r, False


# ---------- the conditional factorial ----------
def factorial_over(cells, seeds):
    """ALIFE-EXP-012's `factorial`, over a SUBSET of seeds.

    The pilot's version reads `C.SEEDS`; XC2 needs the same arithmetic over the
    producing seeds with the gate recomputed on that subset. Rather than trust
    the re-expression, control C-factorial below runs it over all five seeds and
    demands it equal the committed pilot's output exactly."""
    out = {}
    for outcome in C.OUTCOMES:
        v = {arm: [cells[arm][s][outcome] for s in seeds] for arm in C.ARMS}
        m = {arm: statistics.mean(v[arm]) for arm in C.ARMS}
        sp = {arm: (max(v[arm]) - min(v[arm])) for arm in C.ARMS}
        gate = max(sp.values())
        price = (m["BF"] + m["BM"]) / 2 - (m["FF"] + m["FM"]) / 2
        matter = (m["BF"] + m["FF"]) / 2 - (m["BM"] + m["FM"]) / 2
        inter = (m["BF"] - m["BM"]) - (m["FF"] - m["FM"])
        out[outcome] = {
            "label": C.OUTCOME_LABEL[outcome],
            "per_seed": {arm: v[arm] for arm in C.ARMS},
            "cell_mean": m, "cell_spread": sp, "gate": gate, "n_seeds": len(seeds),
            "effects": {
                "price": {"value": price, "claimable": abs(price) > gate},
                "matter": {"value": matter, "claimable": abs(matter) > gate},
                "interaction": {"value": inter, "claimable": abs(inter) > gate},
            },
        }
    return out


def seed_phases(cells):
    """Per seed: the four arms' phases, and the seed's own phase — PRODUCING or
    COLLAPSED when the arms agree, DISCORDANT when they do not. XC1 is the claim
    that DISCORDANT never happens."""
    out = {}
    for s in C.SEEDS:
        arms = {arm: cells[arm][s]["phase"] for arm in C.ARMS}
        distinct = set(arms.values())
        out[s] = {"arms": arms,
                  "phase": distinct.pop() if len(distinct) == 1 else C.DISCORDANT}
    return out


# ---------- controls ----------
def controls(verbose=False):
    out = []

    ok_start, got_start, _ = B.assert_pinned_oracle("start")
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
                f"({len(P.l1_core([(a, b, a), (b, a, b)]))}) and returns "
                f"nothing on an open chain ({len(P.l1_core([(a, b, c)]))})",
                P.l1_core([(a, b, a), (b, a, b)]) == {a, b}
                and P.l1_core([(a, b, c)]) == set()))

    rng = P.control_rng()
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

    frozen = C.exp007_frozen()["result"]["primary"]
    diffs = []
    for s in C.COMPAT_SEEDS:
        r = run_cell("BF", s, rng_mode="stream", reactions=C.COMPAT_REACTIONS)
        for f in P.C3_FIELDS:
            if r[f] != frozen[str(s)][f]:
                diffs.append(f"seed {s} {f}: {r[f]!r} != {frozen[str(s)][f]!r}")
    out.append((f"C-compat arm BF reproduces ALIFE-EXP-007's frozen receipt on "
                f"all {len(C.COMPAT_SEEDS)} shared seeds across "
                f"{len(P.C3_FIELDS)} recorded fields at EXP-007's own "
                f"{C.COMPAT_REACTIONS}-reaction length ({len(diffs)} "
                f"divergences)", not diffs))
    for d in diffs[:6]:
        out.append((f"   C-compat detail: {d}", False))

    if verbose:
        print(f"  running {len(C.ARMS) * len(C.SEEDS)} cells at "
              f"{C.REACTIONS} reactions ...", flush=True)
    cells = {}
    for arm in C.ARMS:
        cells[arm] = {}
        for s in C.SEEDS:
            cells[arm][s], _ = cached_cell(arm, s, verbose)
    flat = [r for arm in cells.values() for r in arm.values()]

    # C-eligible (added): the index log and the independent counter agree in
    # every one of the twenty cells. The phase is computed from the indices, so
    # an instrumentation that dropped or double-counted an event would move the
    # primary outcome silently.
    mismatch = [f"{r['arm']}/{r['seed']}" for r in flat
                if r["eligible_events"] != r["rs_fired"] - r["rs_genesis"]]
    out.append((f"C-eligible the recorded eligible-event indices match the "
                f"independent `rs_fired - rs_genesis` counter in all "
                f"{len(flat)} cells ({len(mismatch)} mismatches)", not mismatch))

    # C-fire(matter/totality) — verbatim from 012b, all M cells regardless of phase.
    ident_bad = []
    for arm in ("BM", "FM"):
        for s in C.SEEDS:
            r = cells[arm][s]
            if (r["consumed_deaths"] + r["blocked_events"]
                    != r["rs_fired"] - r["rs_genesis"]):
                ident_bad.append(f"{arm}/{s}")
    out.append((f"C-fire(matter/totality) consumed + blocked == eligible R-S, "
                f"exactly, in all 10 M cells ({len(ident_bad)} violations)",
                not ident_bad))

    # C-fire(matter/supply) — CHANGE 2: scoped to PRODUCING M cells.
    producing_m = [(arm, s) for arm in ("BM", "FM") for s in C.SEEDS
                   if cells[arm][s]["phase"] == C.PRODUCING]
    low = [f"{arm}/{s}={cells[arm][s]['rs_fired'] - cells[arm][s]['rs_genesis']}"
           for arm, s in producing_m
           if cells[arm][s]["rs_fired"] - cells[arm][s]["rs_genesis"]
           < C.C_FIRE_SUPPLY_MIN]
    out.append((f"C-fire(matter/supply) >= {C.C_FIRE_SUPPLY_MIN} eligible "
                f"non-genesis R-S in every PRODUCING M cell "
                f"({len(producing_m)} of 10 M cells are producing; "
                f"{len(low)} below the floor"
                + (f": {', '.join(low)}" if low else "") + ")", not low))

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

    # C-factorial (added): the seed-subset arithmetic is the committed pilot's.
    mine = factorial_over(cells, list(C.SEEDS))
    theirs = P.factorial(cells)
    same = json.dumps(mine, sort_keys=True, default=str) == \
        json.dumps(theirs, sort_keys=True, default=str)
    if not same:
        # `n_seeds` is the one field the subset version adds.
        stripped = {o: {k: v for k, v in mine[o].items() if k != "n_seeds"}
                    for o in mine}
        same = json.dumps(stripped, sort_keys=True, default=str) == \
            json.dumps(theirs, sort_keys=True, default=str)
    out.append((f"C-factorial the seed-subset factorial reproduces ALIFE-EXP-012's "
                f"committed `factorial()` exactly when given all "
                f"{len(C.SEEDS)} seeds", same))

    det = []
    for arm in C.ARMS:
        for s in C.SEEDS:
            again = run_cell(arm, s)
            if again != cells[arm][s]:
                det.append(f"{arm}/{s}")
    out.append((f"C-det every cell run twice gives an identical receipt "
                f"({len(det)} divergences)", not det))

    ok_end, got_end, _ = B.assert_pinned_oracle("end")
    out.append((f"C-oracle(end) the oracle did not drift during the run "
                f"(got {got_end[:16]}...)", ok_end))

    return all(ok for _, ok in out), out, cells, rng


# ---------- scoring ----------
def score(cells):
    phases = seed_phases(cells)

    # --- XC1: the corpus chooses the phase, not the currency ---------------
    discordant = [s for s in C.SEEDS if phases[s]["phase"] == C.DISCORDANT]
    xc1 = {
        "claim": "within every seed, all four arms carry the same phase",
        "per_seed": {str(s): {"arms": phases[s]["arms"],
                              "phase": phases[s]["phase"]} for s in C.SEEDS},
        "discordant_seeds": [str(s) for s in discordant],
        "n_discordant": len(discordant),
        "cells_scored": len(C.ARMS) * len(C.SEEDS),
        "verdict": "HOLDS" if not discordant else "FAILS",
    }

    producing_seeds = [s for s in C.SEEDS if phases[s]["phase"] == C.PRODUCING]
    collapsed_seeds = [s for s in C.SEEDS if phases[s]["phase"] == C.COLLAPSED]

    # --- XC2: the factorial, conditional -----------------------------------
    if len(producing_seeds) < C.XC2_MIN_PRODUCING_SEEDS:
        xc2 = {"claim": "X1/X2/X3 over producing seeds only",
               "producing_seeds": [str(s) for s in producing_seeds],
               "n_producing": len(producing_seeds),
               "verdict": "UNADJUDICATED (insufficient producing seeds)",
               "small_base": None, "factorial": None, "X": None}
    else:
        fac = factorial_over(cells, producing_seeds)
        xs = P.score(fac)
        xc2 = {"claim": "X1/X2/X3 over producing seeds only, gate recomputed "
                        "on that subset",
               "producing_seeds": [str(s) for s in producing_seeds],
               "n_producing": len(producing_seeds),
               "small_base": len(producing_seeds) < C.XC2_SMALL_BASE_N,
               "small_base_sentence": (
                   f"{len(producing_seeds)} producing seeds is a small base"
                   if len(producing_seeds) < C.XC2_SMALL_BASE_N else None),
               "factorial": fac, "X": xs,
               "verdict": "ADJUDICATED"}

    # --- XC3: collapse timing is currency-independent ----------------------
    # XC3's base is "collapsed seeds with >= 2 arms each" — seeds carrying at
    # least two COLLAPSED CELLS, not seeds whose own phase is COLLAPSED. The
    # first implementation used the latter and reported UNADJUDICATED off one
    # concordantly-collapsed seed; the qualifier "with >= 2 arms each" is
    # redundant under that reading, and XC3's claim is stated over "COLLAPSED
    # cells" grouped by seed. Corrected before the RESULT was written and named
    # in it (DECISIONS.md D121).
    usable = [s for s in C.SEEDS
              if sum(1 for arm in C.ARMS
                     if cells[arm][s]["phase"] == C.COLLAPSED
                     and cells[arm][s]["last_eligible_reaction"] is not None)
              >= C.XC3_MIN_ARMS_PER_SEED]
    if len(usable) < C.XC3_MIN_COLLAPSED_SEEDS:
        xc3 = {"claim": "within-seed spread of the last-eligible index is "
                        "smaller than the across-seed spread of its per-seed means",
               "usable_collapsed_seeds": [str(s) for s in usable],
               "verdict": "UNADJUDICATED (insufficient collapsed cells)",
               "within_seed_spreads": None, "across_seed_spread": None}
    else:
        within, means = {}, {}
        for s in usable:
            vals = [cells[arm][s]["last_eligible_reaction"] for arm in C.ARMS
                    if cells[arm][s]["phase"] == C.COLLAPSED
                    and cells[arm][s]["last_eligible_reaction"] is not None]
            within[str(s)] = {"values": vals, "spread": max(vals) - min(vals),
                              "mean": statistics.mean(vals)}
            means[str(s)] = statistics.mean(vals)
        max_within = max(v["spread"] for v in within.values())
        across = max(means.values()) - min(means.values())
        xc3 = {"claim": "within-seed spread of the last-eligible index is "
                        "smaller than the across-seed spread of its per-seed means",
               "usable_collapsed_seeds": [str(s) for s in usable],
               "within_seed_spreads": within,
               "max_within_seed_spread": max_within,
               "across_seed_spread_of_means": across,
               "verdict": "HOLDS" if max_within < across else "FAILS"}

    return {"XC1": xc1, "XC2": xc2, "XC3": xc3,
            "seed_phases": {str(s): phases[s]["phase"] for s in C.SEEDS},
            "producing_seeds": [str(s) for s in producing_seeds],
            "collapsed_seeds": [str(s) for s in collapsed_seeds]}


def summarize(result):
    cells, sc = result["cells"], result["scores"]
    print(f"{'arm':>4s} {'seed':>10s} {'phase':>10s} {'eligible':>9s} "
          f"{'after 3000':>11s} {'last elig':>10s} {'settled':>8s} "
          f"{'census':>7s} {'distinct':>9s} {'win100':>7s}")
    for s in C.SEEDS:
        for arm in C.ARMS:
            r = cells[arm][str(s)]
            print(f"{arm:>4s} {s:>10d} {r['phase']:>10s} "
                  f"{r['eligible_events']:>9d} "
                  f"{r['eligible_after_threshold']:>11d} "
                  f"{str(r['last_eligible_reaction']):>10s} "
                  f"{r['settled']:>8d} {r['census']:>7d} "
                  f"{r['distinct_nongenesis']:>9d} {r['window_success']:>6.0%}")
        print()

    x1 = sc["XC1"]
    print(f"XC1 (all four arms of a seed carry the same phase; "
          f"{x1['cells_scored']} cells)")
    for s in C.SEEDS:
        p = x1["per_seed"][str(s)]
        print(f"   {s}: " + "  ".join(f"{a}={p['arms'][a][:4]}" for a in C.ARMS)
              + f"   -> {p['phase']}")
    print(f"   -> {x1['n_discordant']} discordant seeds of {len(C.SEEDS)} "
          f"-> {x1['verdict']}")

    x2 = sc["XC2"]
    print(f"\nXC2 (the factorial, over producing seeds only)")
    print(f"   producing seeds: {x2['producing_seeds'] or 'none'} "
          f"(n={x2['n_producing']})")
    if x2["verdict"] != "ADJUDICATED":
        print(f"   -> {x2['verdict']}")
    else:
        if x2["small_base_sentence"]:
            print(f"   {x2['small_base_sentence']}")
        for outcome in C.OUTCOMES:
            f = x2["factorial"][outcome]
            print(f"   {f['label']}  (gate {f['gate']:.2f} over n={f['n_seeds']})")
            for name in ("price", "matter", "interaction"):
                e = f["effects"][name]
                print(f"      {name:<12s} {e['value']:>+9.2f}   "
                      f"{'CLAIMABLE' if e['claimable'] else 'within the gate'}")
        for k in ("X1", "X2", "X3"):
            print(f"   {k}: {x2['X'][k]['verdict']}")

    x3 = sc["XC3"]
    print(f"\nXC3 (collapse timing is currency-independent)")
    if x3["verdict"].startswith("UNADJUDICATED"):
        print(f"   -> {x3['verdict']}")
    else:
        for s, v in x3["within_seed_spreads"].items():
            print(f"   seed {s}: last-eligible {v['values']} "
                  f"spread {v['spread']}, mean {v['mean']:.1f}")
        print(f"   max within-seed spread {x3['max_within_seed_spread']} vs "
              f"across-seed spread of means "
              f"{x3['across_seed_spread_of_means']:.1f} -> {x3['verdict']}")


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
        print("\nALIFE-EXP-012c: CONTROLS FAILED - nothing measured, "
              "nothing recorded")
        return 1
    if args.controls:
        print("\nEXP-012C-CONTROLS: ALL PASS")
        return 0

    result = {
        "cells": {arm: {str(s): {k: v for k, v in cells[arm][s].items()
                                 if k != "eligible_at"}
                        for s in C.SEEDS} for arm in C.ARMS},
        "eligible_at": {arm: {str(s): cells[arm][s]["eligible_at"]
                              for s in C.SEEDS} for arm in C.ARMS},
        "scores": score(cells),
        "rng_control": rng,
    }
    print()
    summarize(result)

    prov = al.provenance()
    receipt = {
        "experiment": "ALIFE-EXP-012c",
        "corpus_fingerprint": C.fingerprint(),
        "inherited_from": ["ALIFE-EXP-001", "ALIFE-EXP-007", "ALIFE-EXP-010",
                           "ALIFE-EXP-012 + 012b (calibration pilots, "
                           "score nothing)"],
        "frame": {"arms": list(C.ARMS), "cells": C.CELL,
                  "arm_labels": C.ARM_LABEL, "seeds": list(C.SEEDS),
                  "compat_seeds": list(C.COMPAT_SEEDS),
                  "capacity": C.CAPACITY, "reactions": C.REACTIONS,
                  "compat_reactions": C.COMPAT_REACTIONS,
                  "atp_per_reaction": C.ATP_PER_REACTION,
                  "slice_atp": C.SLICE_ATP, "floor_price": C.FLOOR_PRICE,
                  "final_window": C.FINAL_WINDOW,
                  "outcomes": list(C.OUTCOMES),
                  "phase_threshold": C.PHASE_THRESHOLD,
                  "c_fire_supply_min": C.C_FIRE_SUPPLY_MIN,
                  "xc2_min_producing_seeds": C.XC2_MIN_PRODUCING_SEEDS,
                  "xc2_small_base_n": C.XC2_SMALL_BASE_N,
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
