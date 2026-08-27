#!/usr/bin/env python3
"""Does the PRICE choose the phase? A prospective test on fresh seeds.

ALIFE-EXP-012c reported per-arm producing counts (BF 0/5, BM 1/5, FF 3/5,
FM 3/5) and refused to claim them: no gate, no null, five seeds already seen.
This document's author saw all of it and filed the pattern as a forecast on
twelve seeds nobody has run. That is the only thing that makes it a test.

Two changes from 012c's harness and nothing else: twelve fresh seeds guarded by
C-fresh, and a phase-by-arm primary outcome carrying a permutation null attached
to every hypothesis.

Check-only by default; `--record` writes `results.json` after every control
passes. Judged against
`../ALIFE-EXP-012d-does-the-price-choose-the-phase-preregistration.md`.

THE MECHANISM IS QUARANTINED. The preregistration files "the Book price drains
ATP the floor price does not, and drained trajectories converge sooner" as a
HYPOTHESIS that this experiment does not adjudicate. Nothing here measures it
and the RESULT does not narrate it.
"""
import argparse
import hashlib
import importlib.util
import json
import platform
import random
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


# D110/D116's pattern at its third generation: one load chain
# (012d -> 012c -> 012b -> 012), every module's frame rebound to this one, with
# an assert that it took. `Soup012c` carries the all-arm eligible instrumentation
# D117 introduced, which is what makes a phase computable in all 48 cells.
Q = _load("alife_exp_012c_measure",
          HERE.parent / "alife-exp-012c" / "measure.py")
B = Q.B
P = Q.P
Q.C = B.C = P.C = C
assert Q.C is C and B.C is C and P.C is C, "frame rebinding did not take"
assert P.C.REACTIONS == 6000 and P.C.PHASE_THRESHOLD == 3000
assert len(C.SEEDS) == 12

sg = al.sg
run_cell = Q.run_cell                      # Soup012c, verbatim


# ---------- checkpointing (D112) ----------
def frame_key():
    payload = json.dumps({
        "reactions": C.REACTIONS, "capacity": C.CAPACITY,
        "atp": C.ATP_PER_REACTION, "slice": C.SLICE_ATP,
        "cells": C.CELL, "seeds": list(C.SEEDS),
        "threshold": C.PHASE_THRESHOLD,
        "fingerprint": C.fingerprint(), "oracle": B.oracle_digest(),
        # Bumped when the shared machinery's OUTPUT SCHEMA changes, so a
        # cached cell from an older harness cannot be compared against a fresh
        # one. D112's rule, extended from the frame to the instrument.
        "schema": 2,
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


# ---------- the permutation null ----------
def permuted(cells, draw):
    """Relabel the four arms within every seed, independently per seed.

    Holds each seed's multiset of phases and last-eligible indices fixed and
    destroys only the association between an ARM and its outcome — which is the
    association every hypothesis here is about. Seeded exactly as the
    preregistration specifies."""
    digest = hashlib.sha256(C.NULL_SEED_TEMPLATE.format(draw=draw).encode())
    rng = random.Random(int.from_bytes(digest.digest(), "big"))
    out = {arm: {} for arm in C.ARMS}
    for s in C.SEEDS:
        perm = list(C.ARMS)
        rng.shuffle(perm)
        for label, src in zip(C.ARMS, perm):
            out[label][s] = cells[src][s]
    return out


def n_producing(cells, arms):
    return sum(1 for arm in arms for s in C.SEEDS
               if cells[arm][s]["phase"] == C.PRODUCING)


def xd1_stat(cells):
    return (n_producing(cells, C.FLOOR_ARMS)
            - n_producing(cells, C.BOOK_ARMS))


def xd2_stat(cells):
    return abs(n_producing(cells, C.FREE_ARMS)
               - n_producing(cells, C.MATTER_ARMS))


def xd3_stat(cells):
    """The margin by which BF is the strictly lowest producer. Positive iff BF
    is strictly below every other arm."""
    counts = {arm: n_producing(cells, (arm,)) for arm in C.ARMS}
    others = [counts[a] for a in C.ARMS if a != "BF"]
    return min(others) - counts["BF"]


def xd4_pairs(cells):
    """Per seed: the mean last-eligible index over COLLAPSED Book arms and over
    COLLAPSED floor arms. A seed qualifies when both sides are non-empty."""
    rows = {}
    for s in C.SEEDS:
        book = [cells[a][s]["last_eligible_reaction"] for a in C.BOOK_ARMS
                if cells[a][s]["phase"] == C.COLLAPSED
                and cells[a][s]["last_eligible_reaction"] is not None]
        floor = [cells[a][s]["last_eligible_reaction"] for a in C.FLOOR_ARMS
                 if cells[a][s]["phase"] == C.COLLAPSED
                 and cells[a][s]["last_eligible_reaction"] is not None]
        if book and floor:
            rows[s] = {"book": book, "floor": floor,
                       "book_mean": statistics.mean(book),
                       "floor_mean": statistics.mean(floor),
                       "book_earlier": statistics.mean(book)
                       < statistics.mean(floor)}
    return rows


def xd4_stat(cells):
    """Signed sign-test statistic: seeds where the Book arms die earlier minus
    seeds where the floor arms do. Symmetric around zero under the null."""
    rows = xd4_pairs(cells)
    earlier = sum(1 for r in rows.values() if r["book_earlier"])
    return 2 * earlier - len(rows), len(rows)


def nulls(cells, draws=None):
    """Every statistic over every draw, from ONE pass of permutations, so all
    four hypotheses are scored against the same null realizations."""
    draws = C.NULL_DRAWS if draws is None else draws
    out = {"xd1": [], "xd2": [], "xd3": [], "xd4": [], "xd4_n": []}
    for d in range(draws):
        p = permuted(cells, d)
        out["xd1"].append(xd1_stat(p))
        out["xd2"].append(xd2_stat(p))
        out["xd3"].append(xd3_stat(p))
        stat, n = xd4_stat(p)
        out["xd4"].append(stat)
        out["xd4_n"].append(n)
    return out


def p_upper(observed, dist):
    """One-sided permutation p, with the observed value counted in the
    numerator — the conventional (r+1)/(n+1) estimator, which never returns
    zero and never claims more resolution than the draw count bought."""
    ge = sum(1 for v in dist if v >= observed)
    return (ge + 1) / (len(dist) + 1)


def percentile(dist, q):
    s = sorted(dist)
    if not s:
        return None
    k = (len(s) - 1) * q / 100.0
    lo, hi = int(k), min(int(k) + 1, len(s) - 1)
    return s[lo] + (s[hi] - s[lo]) * (k - lo)


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

    # C-fresh, fail-closed, FIRST after the oracle: a reused seed makes every
    # forecast below a fit, and no later control can undo that.
    forbidden = C.forbidden_seeds()
    all_forbidden = set()
    for seeds in forbidden.values():
        all_forbidden |= set(seeds)
    clash = sorted(set(C.SEEDS) & all_forbidden)
    out.append((f"C-fresh none of the {len(C.SEEDS)} measurement seeds "
                f"{C.SEEDS[0]}..{C.SEEDS[-1]} appears in "
                f"{'/'.join(k.replace('alife-exp-', 'EXP-') for k in forbidden)} "
                f"({len(all_forbidden)} forbidden seeds; {len(clash)} clashes)",
                not clash))
    # The single named exemption, checked rather than asserted: C-compat runs on
    # ALIFE-EXP-007's three seeds because it reproduces EXP-007's frozen
    # receipt, which exists only for those seeds. Its runs must contribute no
    # cell to any hypothesis — see DECISIONS.md D122.
    out.append((f"C-fresh(exemption) C-compat's seeds "
                f"{tuple(C.COMPAT_SEEDS)} are EXP-007's and are disjoint from "
                f"the measurement seeds, so no cell scored below comes from "
                f"them", not (set(C.COMPAT_SEEDS) & set(C.SEEDS))))
    if clash:
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

    mismatch = [f"{r['arm']}/{r['seed']}" for r in flat
                if r["eligible_events"] != r["rs_fired"] - r["rs_genesis"]]
    out.append((f"C-eligible the recorded eligible-event indices match the "
                f"independent `rs_fired - rs_genesis` counter in all "
                f"{len(flat)} cells ({len(mismatch)} mismatches)", not mismatch))

    ident_bad = []
    for arm in C.MATTER_ARMS:
        for s in C.SEEDS:
            r = cells[arm][s]
            if (r["consumed_deaths"] + r["blocked_events"]
                    != r["rs_fired"] - r["rs_genesis"]):
                ident_bad.append(f"{arm}/{s}")
    out.append((f"C-fire(matter/totality) consumed + blocked == eligible R-S, "
                f"exactly, in all {2 * len(C.SEEDS)} M cells "
                f"({len(ident_bad)} violations)", not ident_bad))

    producing_m = [(arm, s) for arm in C.MATTER_ARMS for s in C.SEEDS
                   if cells[arm][s]["phase"] == C.PRODUCING]
    low = [f"{arm}/{s}={cells[arm][s]['rs_fired'] - cells[arm][s]['rs_genesis']}"
           for arm, s in producing_m
           if cells[arm][s]["rs_fired"] - cells[arm][s]["rs_genesis"]
           < C.C_FIRE_SUPPLY_MIN]
    out.append((f"C-fire(matter/supply) >= {C.C_FIRE_SUPPLY_MIN} eligible "
                f"non-genesis R-S in every PRODUCING M cell "
                f"({len(producing_m)} of {2 * len(C.SEEDS)} M cells are "
                f"producing; {len(low)} below the floor"
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
                       for arm in C.FLOOR_ARMS for s in C.SEEDS)
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

    mine = Q.factorial_over(cells, list(C.SEEDS))
    theirs = P.factorial(cells)
    strip = {o: {k: v for k, v in mine[o].items() if k != "n_seeds"}
             for o in mine}
    same = json.dumps(strip, sort_keys=True, default=str) == \
        json.dumps(theirs, sort_keys=True, default=str)
    out.append((f"C-factorial the seed-subset factorial reproduces "
                f"ALIFE-EXP-012's committed `factorial()` exactly when given "
                f"all {len(C.SEEDS)} seeds", same))

    # C-null (added): the permutation null must preserve what it claims to and
    # destroy what it claims to. Per draw, every seed keeps its exact multiset of
    # phases; and across draws the arm labels really move.
    ok_preserve, moved = True, 0
    for d in range(50):
        p = permuted(cells, d)
        for s in C.SEEDS:
            if sorted(p[a][s]["phase"] for a in C.ARMS) != \
               sorted(cells[a][s]["phase"] for a in C.ARMS):
                ok_preserve = False
        moved += sum(1 for a in C.ARMS for s in C.SEEDS
                     if p[a][s] is not cells[a][s])
    out.append((f"C-null the arm-label permutation preserves every seed's "
                f"multiset of phases exactly and does move the labels "
                f"({moved} relabelled cells over 50 draws)",
                ok_preserve and moved > 0))
    # ... and is reproducible from its specified seeding, not from process state.
    reproducible = all(
        json.dumps({a: {str(s): permuted(cells, d)[a][s]["phase"]
                        for s in C.SEEDS} for a in C.ARMS}, sort_keys=True)
        == json.dumps({a: {str(s): permuted(cells, d)[a][s]["phase"]
                           for s in C.SEEDS} for a in C.ARMS}, sort_keys=True)
        for d in (0, 7, 999))
    out.append(("C-null(seeding) a draw is a function of its index alone, "
                "sha256(\"EXP-012d/null/{draw}\")", reproducible))

    det = []
    for arm in C.ARMS:
        for s in C.SEEDS:
            if run_cell(arm, s) != cells[arm][s]:
                det.append(f"{arm}/{s}")
    out.append((f"C-det every cell run twice gives an identical receipt "
                f"({len(det)} divergences)", not det))

    ok_end, got_end, _ = B.assert_pinned_oracle("end")
    out.append((f"C-oracle(end) the oracle did not drift during the run "
                f"(got {got_end[:16]}...)", ok_end))

    return all(ok for _, ok in out), out, cells, rng


# ---------- scoring ----------
def score(cells):
    dist = nulls(cells)
    per_arm = {arm: n_producing(cells, (arm,)) for arm in C.ARMS}

    # --- XD1 ---------------------------------------------------------------
    o1 = xd1_stat(cells)
    p1 = p_upper(o1, dist["xd1"])
    p1_two = (sum(1 for v in dist["xd1"] if abs(v) >= abs(o1)) + 1) / \
        (len(dist["xd1"]) + 1)
    xd1 = {
        "claim": "#producing(FF u FM) - #producing(BF u BM) >= 8 of 24 each, "
                 "and permutation p < 0.05",
        "statistic": "#producing(floor arms) - #producing(book arms)",
        "observed": o1, "threshold": C.XD1_MIN_DIFF,
        "producing_floor": n_producing(cells, C.FLOOR_ARMS),
        "producing_book": n_producing(cells, C.BOOK_ARMS),
        "cells_per_level": len(C.FLOOR_ARMS) * len(C.SEEDS),
        "null_draws": C.NULL_DRAWS, "p_value": p1,
        "p_value_two_sided": p1_two,
        "null_mean": statistics.mean(dist["xd1"]),
        "null_max": max(dist["xd1"]),
        "clause_threshold": o1 >= C.XD1_MIN_DIFF,
        "clause_p": p1 < C.XD1_ALPHA,
        "verdict": "HOLDS" if (o1 >= C.XD1_MIN_DIFF and p1 < C.XD1_ALPHA)
                   else "FAILS",
    }

    # --- XD2 ---------------------------------------------------------------
    o2 = xd2_stat(cells)
    cut = percentile(dist["xd2"], C.XD2_PERCENTILE)
    p2 = p_upper(o2, dist["xd2"])
    xd2 = {
        "claim": "|#producing(free arms) - #producing(matter arms)| is below "
                 "the null's 95th percentile",
        "statistic": "|#producing(BF u FF) - #producing(BM u FM)|",
        "observed": o2,
        "producing_free": n_producing(cells, C.FREE_ARMS),
        "producing_matter": n_producing(cells, C.MATTER_ARMS),
        "null_draws": C.NULL_DRAWS,
        "null_percentile_95": cut, "p_value": p2,
        "verdict": "HOLDS" if o2 < cut else "FAILS",
    }

    # --- XD3 ---------------------------------------------------------------
    o3 = xd3_stat(cells)
    p3 = p_upper(o3, dist["xd3"])
    xd3 = {
        "claim": "BF has the strictly lowest producing count of the four arms",
        "statistic": "min(other arms' producing count) - BF's",
        "observed": o3, "per_arm_producing": per_arm,
        "null_draws": C.NULL_DRAWS, "p_value": p3,
        "verdict": "HOLDS" if o3 > 0 else "FAILS",
    }

    # --- XD4 ---------------------------------------------------------------
    rows = xd4_pairs(cells)
    o4, n4 = xd4_stat(cells)
    earlier = sum(1 for r in rows.values() if r["book_earlier"])
    if n4 < C.XD4_MIN_SEEDS:
        xd4 = {"claim": "among seeds where a Book-priced and a floor-priced arm "
                        "both collapse, the Book-priced arm dies earlier in "
                        ">= 3 of every 4, sign-test p < 0.05",
               "qualifying_seeds": n4,
               "verdict": f"UNADJUDICATED (only {n4} qualifying seeds, "
                          f"{C.XD4_MIN_SEEDS} required)"}
    else:
        p4 = p_upper(o4, dist["xd4"])
        ratio = earlier / n4
        xd4 = {"claim": "among seeds where a Book-priced and a floor-priced arm "
                        "both collapse, the Book-priced arm dies earlier in "
                        ">= 3 of every 4, sign-test p < 0.05",
               "statistic": "signed sign-test count (book earlier - floor "
                            "earlier) over qualifying seeds",
               "qualifying_seeds": n4, "book_earlier": earlier,
               "ratio": ratio, "min_ratio": C.XD4_MIN_RATIO,
               "observed": o4, "null_draws": C.NULL_DRAWS, "p_value": p4,
               "per_seed": {str(s): {k: v for k, v in r.items()}
                            for s, r in rows.items()},
               "clause_ratio": ratio >= C.XD4_MIN_RATIO,
               "clause_p": p4 < C.XD4_ALPHA,
               "verdict": "HOLDS" if (ratio >= C.XD4_MIN_RATIO
                                      and p4 < C.XD4_ALPHA) else "FAILS"}

    seed_phase = {}
    for s in C.SEEDS:
        arms = {arm: cells[arm][s]["phase"] for arm in C.ARMS}
        d = set(arms.values())
        seed_phase[str(s)] = {"arms": arms,
                              "phase": d.pop() if len(d) == 1 else C.DISCORDANT}

    return {"XD1": xd1, "XD2": xd2, "XD3": xd3, "XD4": xd4,
            "per_arm_producing": per_arm,
            "producing_cells": n_producing(cells, C.ARMS),
            "total_cells": len(C.ARMS) * len(C.SEEDS),
            "seed_phases": seed_phase,
            "null_spec": {"draws": C.NULL_DRAWS,
                          "seeding": C.NULL_SEED_TEMPLATE,
                          "model": "permute the four arm labels within each "
                                   "seed, independently per seed"}}


def summarize(result):
    cells, sc = result["cells"], result["scores"]
    print(f"{'seed':>10s}  " + "  ".join(f"{a:>10s}" for a in C.ARMS))
    for s in C.SEEDS:
        row = "  ".join(f"{cells[a][str(s)]['phase'][:4]:>10s}" for a in C.ARMS)
        print(f"{s:>10d}  {row}   {sc['seed_phases'][str(s)]['phase']}")
    print(f"\nproducing per arm: " + "  ".join(
        f"{a}={sc['per_arm_producing'][a]}/{len(C.SEEDS)}" for a in C.ARMS)
        + f"   ({sc['producing_cells']}/{sc['total_cells']} cells)")
    print(f"null: {sc['null_spec']['draws']} draws, "
          f"{sc['null_spec']['model']}\n")

    x = sc["XD1"]
    print(f"XD1 (price drives production)")
    print(f"   floor {x['producing_floor']}/{x['cells_per_level']} vs book "
          f"{x['producing_book']}/{x['cells_per_level']}  ->  statistic "
          f"{x['observed']:+d} (threshold >= {x['threshold']})")
    print(f"   permutation p = {x['p_value']:.4f} over {x['null_draws']} draws "
          f"(two-sided {x['p_value_two_sided']:.4f}; null mean "
          f"{x['null_mean']:+.2f}, max {x['null_max']:+d})")
    print(f"   -> {x['verdict']}")

    x = sc["XD2"]
    print(f"\nXD2 (matter does not drive production)")
    print(f"   free {x['producing_free']} vs matter {x['producing_matter']}  "
          f"->  |difference| {x['observed']}")
    print(f"   null 95th percentile {x['null_percentile_95']:.2f}, "
          f"p = {x['p_value']:.4f} over {x['null_draws']} draws")
    print(f"   -> {x['verdict']}")

    x = sc["XD3"]
    print(f"\nXD3 (BF strictly lowest)")
    print(f"   per arm " + "  ".join(f"{a}={x['per_arm_producing'][a]}"
                                     for a in C.ARMS)
          + f"  ->  margin {x['observed']:+d}")
    print(f"   permutation p = {x['p_value']:.4f} over {x['null_draws']} draws")
    print(f"   -> {x['verdict']}")

    x = sc["XD4"]
    print(f"\nXD4 (the 20260827 death-timing signature)")
    if x["verdict"].startswith("UNADJUDICATED"):
        print(f"   -> {x['verdict']}")
    else:
        for s, r in x["per_seed"].items():
            print(f"   seed {s}: book {r['book']} (mean {r['book_mean']:.0f}) "
                  f"vs floor {r['floor']} (mean {r['floor_mean']:.0f})"
                  f"  -> {'book earlier' if r['book_earlier'] else 'floor earlier'}")
        print(f"   book earlier in {x['book_earlier']}/{x['qualifying_seeds']} "
              f"= {x['ratio']:.2f} (needs >= {x['min_ratio']}), signed "
              f"statistic {x['observed']:+d}")
        print(f"   permutation p = {x['p_value']:.4f} over {x['null_draws']} "
              f"draws")
        print(f"   -> {x['verdict']}")


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
        print("\nALIFE-EXP-012d: CONTROLS FAILED - nothing measured, "
              "nothing recorded")
        return 1
    if args.controls:
        print("\nEXP-012D-CONTROLS: ALL PASS")
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
        "experiment": "ALIFE-EXP-012d",
        "corpus_fingerprint": C.fingerprint(),
        "inherited_from": ["ALIFE-EXP-001", "ALIFE-EXP-007", "ALIFE-EXP-010",
                           "ALIFE-EXP-012c"],
        "frame": {"arms": list(C.ARMS), "cells": C.CELL,
                  "arm_labels": C.ARM_LABEL, "seeds": list(C.SEEDS),
                  "forbidden_seeds": {k: list(v) for k, v in
                                      C.forbidden_seeds().items()},
                  "compat_seeds": list(C.COMPAT_SEEDS),
                  "capacity": C.CAPACITY, "reactions": C.REACTIONS,
                  "compat_reactions": C.COMPAT_REACTIONS,
                  "atp_per_reaction": C.ATP_PER_REACTION,
                  "slice_atp": C.SLICE_ATP, "floor_price": C.FLOOR_PRICE,
                  "final_window": C.FINAL_WINDOW,
                  "phase_threshold": C.PHASE_THRESHOLD,
                  "c_fire_supply_min": C.C_FIRE_SUPPLY_MIN,
                  "null_draws": C.NULL_DRAWS,
                  "null_seeding": C.NULL_SEED_TEMPLATE,
                  "xd1_min_diff": C.XD1_MIN_DIFF,
                  "xd2_percentile": C.XD2_PERCENTILE,
                  "xd4_min_ratio": C.XD4_MIN_RATIO,
                  "xd4_min_seeds": C.XD4_MIN_SEEDS,
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
