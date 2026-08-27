#!/usr/bin/env python3
"""Price and matter, crossed — the factorial ALIFE-EXP-010 could not run.

Four arms over one chemistry, differing in exactly two bits: what a duplication
COSTS (Book I's `1 + size(z)` or the action floor) and whether the copy has to
come out of a living body. EXP-010 varied both together and could attribute
nothing; this varies them separately.

Check-only by default; `--record` writes `results.json` after every control
passes. Judged against `../ALIFE-EXP-012-the-currency-factorial-preregistration.md`,
committed before this file; the choices it left open are `DECISIONS.md`
D101-D106, committed before the measurement ran.

THE ENGINE RUNS AS FIXED. D98 (the cull re-tests starvation) and D99 (the
holders-based rebate) are in effect and are not reverted for comparability —
C-compat pins the frame instead, by scoring arm BF against ALIFE-EXP-007's
frozen receipt in stream-RNG mode. That control is what makes "the deltas are
documented" a number rather than a promise.
"""
import argparse
import hashlib
import json
import platform
import statistics
import sys
from collections import Counter, deque
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "impl"))

import corpus as C  # noqa: E402
import sigma_alife as al  # noqa: E402

sg = al.sg
DIS_HASHES = None


def fresh_store():
    st = sg.Store()
    for b in (sg.I_BYTES, sg.K_BYTES, sg.S_BYTES):
        st.put(b)
    return st


def dis_hashes():
    global DIS_HASHES
    if DIS_HASHES is None:
        DIS_HASHES = {sg.term_hash(("dis", r))
                      for r in (sg.R_ATP, sg.R_UNRES, sg.R_INVALID)}
    return DIS_HASHES


def l1_core(reactions):
    """ALIFE-EXP-007's peeling, carried verbatim and re-guarded by its own
    open-chain control below. Used only by C-compat, which has to reproduce
    EXP-007's `core_size` and `core`; it is not an estimand here."""
    products = {}
    for a, b, c in reactions:
        products.setdefault(c, set()).add((a, b))
    core = set(products)
    changed = True
    while changed:
        changed = False
        for c in list(core):
            if not any(a in core and b in core for a, b in products[c]):
                core.discard(c)
                changed = True
    return core


# ---------- the 2x2 gate ----------
class Gate:
    """One rule, two bits. `reduce_slice` consumes `.price_of` and `.afford`.

    `price` is "book" (`1 + size(z)`, Book I's own) or "floor" (the action
    floor). `matter` is "free" (the copy is conjured, Book I's own) or "consume"
    (a living exact-hash body is required and consumed, EXP-010's Arm M rule).
    BF is therefore the unmodified chemistry driven through the hook, which
    EXP-010's C0c established is the identity on it.
    """

    def __init__(self, soup, price, matter):
        self.soup = soup
        self.price = price
        self.matter = matter

    def price_of(self, z):
        return 1 + sg.size(z) if self.price == "book" else C.FLOOR_PRICE

    def afford(self, agent, z, spent):
        s = self.soup
        s.rs_fired += 1
        charged = self.price_of(z)
        s.rs_price_charged[charged] += 1
        s.rs_book_price[1 + sg.size(z)] += 1
        s.rs_atp += charged
        s.rs_zsize_sum += sg.size(z)
        if sg.term_hash(z) in sg.GENESIS:
            s.rs_genesis += 1
        # The Book I per-agent bound, measured in EVERY cell rather than only
        # where a body pays for the copy. `size <= s0 + spent` follows from
        # `dsize <= cost - 1`, a property of Book I's PRICE, so the floor arms
        # abandon the premise by construction and FF has nothing leaving the
        # census to offset the copy either. That is a result of the factorial,
        # not a control failure, and it is only a result if it is counted.
        s.note_rs_bound(agent, z, spent, charged)
        if self.matter == "free":
            return True
        return s.consume_for(agent, z, spent)


# ---------- the census ----------
STATES = ("alive", "consumed", "culled", "starved", "waiting", "faulted",
          "unresolved")


class Individual:
    """One molecule-life (ALIFE-EXP-010 D74): the 64 founders and the 1000
    reactions are one population, and every member leaves it in exactly one way."""
    __slots__ = ("iid", "born", "founder", "hash", "size", "s0", "state",
                 "agent", "waiting_on")

    def __init__(self, iid, born, founder, s0):
        self.iid = iid
        self.born = born
        self.founder = founder
        self.hash = None
        self.size = s0
        self.s0 = s0
        self.state = "alive" if founder else "running"
        self.agent = None
        self.waiting_on = None


class Soup:
    """EXP-007's bounded reactor with a census, a 2x2 duplication gate, and
    randomness that a counterfactual cannot shift.

    Every stochastic draw goes through `self.rng.below(n, index, event)` with
    `index` the REACTION index and `event` a name — never through a positional
    stream. `rng_mode="stream"` swaps in `StreamRandom`, which ignores the keys
    and reproduces EXP-007's draw order for C-compat and for C-RNG's negative
    control.
    """

    def __init__(self, arm, seed, reactions=None, capacity=None,
                 rng_mode="counter", perturb_at=None):
        self.arm = arm
        price, matter = C.CELL[arm]
        self.seed = seed
        self.reactions = C.REACTIONS if reactions is None else reactions
        self.capacity = C.CAPACITY if capacity is None else capacity
        self.rng_mode = rng_mode
        self.rng = (al.CounterRandom(seed, label=f"exp012") if rng_mode == "counter"
                    else al.StreamRandom(seed))
        # C-RNG's subject: the reaction at which this run is forced to differ.
        self.perturb_at = perturb_at
        self.budget = C.ATP_PER_REACTION
        self.store = fresh_store()
        self.econ = al.Economy(self.budget * self.reactions + 1)
        self.gate = Gate(self, price, matter)

        self.individuals = []
        self.soup = []
        for e in C.build()[:self.capacity]:
            h = al.put_term(e["term"], self.store)
            ind = Individual(len(self.individuals), 0, True, sg.size(e["term"]))
            ind.hash = h
            self.individuals.append(ind)
            self.soup.append(ind)

        self.parked = {}
        self.observed = []
        self.edge_of = {}
        self.ok = self.closed = self.poisoned = 0
        self.terminal_failed = 0
        self.costs = []
        self.settled_at_birth = set()
        self.spend_settled = self.spend_failed = 0
        self.cull_seq = 0
        self.draw_log = []          # (index, event, n, value, word) — C-RNG
        self.rs_fired = 0
        self.rs_genesis = 0
        self.rs_atp = 0
        self.rs_zsize_sum = 0
        self.rs_price_charged = Counter()
        self.rs_book_price = Counter()
        self.consumed = 0
        self.consumed_last_copy = 0
        self.consumption_multiplicity = Counter()
        self.blocked_events = 0
        self.blocked_on = None
        self.wake_events = 0
        self.atp_while_waiting = 0
        self.material_shortfalls = 0
        self.book1_violating_actions = 0
        self.book1_violations = set()
        self.running_iid = None
        self.ledger_ok = True
        self.census_bound_ok = True
        self.census_counts_ok = True
        self.consumed_but_alive = 0
        self.perturbed = False

    # -- randomness ----------------------------------------------------------
    def draw(self, n, index, event):
        v = self.rng.below(n, index, event)
        self.draw_log.append((index, event, n, v,
                              self.rng.word(index, event, 0)))
        return v

    @property
    def spent_released(self):
        return self.spend_settled + self.spend_failed

    # -- matter --------------------------------------------------------------
    def note_rs_bound(self, agent, z, spent, charged):
        """What Book I's per-agent bound will read the instant this R-S lands."""
        after = sg.size(agent.term) + max(0, sg.size(z) - 1)
        if after > agent.s0 + agent.spent + spent + charged:
            self.book1_violations.add(self.running_iid)
            self.book1_violating_actions += 1

    def consume_for(self, agent, z, spent):
        """EXP-010's Arm M rule, unchanged: a living exact-hash body, the
        earliest born, removed with death-cause `consumed`; genesis atoms free;
        no copy means a WAIT, never a death."""
        h = sg.term_hash(z)
        if h in sg.GENESIS:
            return True
        victim = None
        multiplicity = 0
        for ind in self.soup:
            if ind.hash == h:
                multiplicity += 1
                victim = ind if victim is None or ind.born < victim.born else victim
        if victim is None:
            self.blocked_events += 1
            self.blocked_on = h
            return False
        self.consumption_multiplicity[multiplicity] += 1
        if multiplicity == 1:
            self.consumed_last_copy += 1
        if victim.size < sg.size(z):
            self.material_shortfalls += 1
        self.soup.remove(victim)
        victim.state = "consumed"
        self.consumed += 1
        return True

    # -- the driver ----------------------------------------------------------
    def drive(self, ind):
        agent = ind.agent
        self.blocked_on = None
        self.running_iid = ind.iid
        spent_before = agent.spent
        term_before = agent.term
        slice_atp = C.SLICE_ATP
        while agent.status in al.RUNNABLE and agent.atp > 0:
            got = al.reduce_slice(agent, self.store, slice_atp,
                                  duplication_gate=self.gate)
            if agent.status != al.LIVE:
                break
            if not got:
                slice_atp = min(agent.atp, max(1, slice_atp * 2))
        ind.size = sg.size(agent.term)
        if agent.status == al.BLOCKED:
            if ind.state == "waiting" and agent.term == term_before:
                self.atp_while_waiting += agent.spent - spent_before
            ind.state = "waiting"
            ind.waiting_on = self.blocked_on
            self.parked.setdefault(self.blocked_on, []).append(ind)
            return None
        ind.waiting_on = None
        if agent.status == al.NORMAL:
            return self.settle(ind)
        self.econ.collect(agent, agent.atp)
        ind.state = {al.STARVED: "starved", al.FAULT: "faulted",
                     al.UNRESOLVED: "unresolved"}.get(agent.status, "starved")
        self.terminal_failed += 1
        self.spend_failed += agent.spent
        ind.agent = None
        return None

    def settle(self, ind):
        agent = ind.agent
        self.econ.collect(agent, agent.atp)
        self.ok += 1
        self.settled_at_birth.add(ind.born)
        self.costs.append(agent.spent)
        self.spend_settled += agent.spent
        product = al.put_term(agent.term, self.store)
        if any(m.hash == product for m in self.soup):
            self.closed += 1
        a, b = self.edge_of[ind.iid]
        self.observed.append((a, b, product))
        ind.hash = product
        ind.size = sg.size(agent.term)
        ind.state = "alive"
        ind.agent = None
        self.soup.append(ind)
        if len(self.soup) > self.capacity:
            event = f"cull:{self.cull_seq}"
            self.cull_seq += 1
            victim = self.soup.pop(self.draw(len(self.soup),
                                             self.current_reaction, event))
            victim.state = "culled"
        return product

    def wake(self, product):
        queue = deque(sorted(self.parked.pop(product, []),
                             key=lambda x: x.born))
        while queue:
            ind = queue.popleft()
            self.wake_events += 1
            ind.agent.status = al.LIVE
            made = self.drive(ind)
            if made is not None:
                for nxt in sorted(self.parked.pop(made, []),
                                  key=lambda x: x.born):
                    queue.append(nxt)

    # -- invariants ----------------------------------------------------------
    def check_invariants(self):
        parked = [i for i in self.individuals if i.state == "waiting"]
        held = sum(i.agent.atp for i in parked if i.agent)
        spent = self.spent_released + sum(i.agent.spent
                                          for i in self.individuals if i.agent)
        if self.econ.pool + held + spent != self.econ.endowment:
            self.ledger_ok = False
        alive = [i for i in self.individuals if i.state == "alive"]
        lhs = sum(i.size for i in alive) + sum(i.size for i in parked)
        if lhs > sum(i.s0 for i in self.individuals) + spent:
            self.census_bound_ok = False
        counts = {s: 0 for s in STATES}
        running = 0
        for i in self.individuals:
            if i.state == "running":
                running += 1
            else:
                counts[i.state] += 1
        if sum(counts.values()) + running != len(self.individuals):
            self.census_counts_ok = False
        if counts["alive"] != len(self.soup):
            self.census_counts_ok = False
        soup_ids = {i.iid for i in self.soup}
        for i in self.individuals:
            if i.state == "consumed" and i.iid in soup_ids:
                self.consumed_but_alive += 1
        return counts

    # -- the run -------------------------------------------------------------
    def run(self, keep_edges=False):
        counts = None
        for i in range(self.reactions):
            self.current_reaction = i
            self.cull_seq = 0
            a = self.soup[self.draw(len(self.soup), i, "reactant_a")].hash
            b = self.soup[self.draw(len(self.soup), i, "reactant_b")].hash
            root = al.put_term(("app", ("thunk", a), ("thunk", b)), self.store)
            ind = Individual(len(self.individuals), i, False, 1)
            self.individuals.append(ind)
            self.edge_of[ind.iid] = (a, b)
            agent = al.Agent(f"r{i}", root, 0)
            ind.agent = agent
            self.econ.endow(agent, self.budget)
            if self.perturb_at is not None and i == self.perturb_at:
                # C-RNG's perturbation: this one reaction is denied its budget,
                # so it starves where it would have settled and every LATER
                # history differs. The draws must not.
                self.econ.collect(agent, agent.atp)
                self.perturbed = True
                ind.state = "starved"
                self.terminal_failed += 1
                ind.agent = None
                product = None
            else:
                product = self.drive(ind)
            if product is not None:
                self.wake(product)
            self.poisoned += sum(1 for m in self.soup
                                 if m.hash in dis_hashes())
            counts = self.check_invariants()
        outstanding = counts["waiting"]
        parked = [i for i in self.individuals if i.state == "waiting"]
        spend_parked = sum(i.agent.spent for i in parked if i.agent)
        held_terminal = sum(i.agent.atp for i in parked if i.agent)
        spent_total = self.spent_released + spend_parked
        core = l1_core(self.observed)
        survivors = {m.hash for m in self.soup if m.hash not in sg.GENESIS}
        return {
            "arm": self.arm, "seed": self.seed, "rng_mode": self.rng_mode,
            "reactions": self.reactions,
            # --- the preregistered outcomes ---
            "settled": self.ok,
            "census": len(self.soup),
            "distinct_nongenesis": len(survivors),
            "window_success": self.window(C.FINAL_WINDOW)["rate"],
            "window": {str(w): self.window(w) for w in (100, 200, 400)},
            # --- EXP-007 comparison surface (C-compat) ---
            "ok": self.ok,
            "fail": self.terminal_failed + outstanding,
            "success_rate": self.ok / self.reactions,
            "closure": self.closed / max(1, self.ok),
            "distinct": len({m.hash for m in self.soup}),
            "mean_cost": statistics.mean(self.costs) if self.costs else 0,
            "median_cost": statistics.median(self.costs) if self.costs else 0,
            "l0": sorted({c.hex() for a, b, c in self.observed if a == b == c}),
            "core_size": len(core),
            "core": sorted(h.hex() for h in core),
            "poisoned": self.poisoned,
            "pool_left": self.econ.pool,
            "endowment": self.econ.endowment,
            # --- ledger and census (C-ledger) ---
            "terminal_settled": self.ok,
            "terminal_failed": self.terminal_failed,
            "terminal_waiting": outstanding,
            "spent_total": spent_total,
            "spend_settled": self.spend_settled,
            "spend_failed": self.spend_failed,
            "spend_parked": spend_parked,
            "held_terminal": held_terminal,
            "ledger_identity_ok": (self.econ.pool + held_terminal + spent_total
                                   == self.econ.endowment),
            "ledger_ok": self.ledger_ok,
            "census_bound_ok": self.census_bound_ok,
            "census_counts_ok": self.census_counts_ok,
            "consumed_but_alive": self.consumed_but_alive,
            "census_counts": counts,
            "born": len(self.individuals),
            # --- the two bits, exercised (C-fire) ---
            "rs_fired": self.rs_fired,
            "rs_genesis": self.rs_genesis,
            "rs_atp": self.rs_atp,
            "rs_price_charged": {str(k): v for k, v in
                                 sorted(self.rs_price_charged.items())},
            "rs_book_price": {str(k): v for k, v in
                              sorted(self.rs_book_price.items())},
            "rs_zsize_mean": (self.rs_zsize_sum / self.rs_fired
                              if self.rs_fired else 0),
            "consumed_deaths": self.consumed,
            "consumed_last_copy": self.consumed_last_copy,
            "consumption_multiplicity": {str(k): v for k, v in
                                         sorted(self.consumption_multiplicity.items())},
            "blocked_events": self.blocked_events,
            "waits_outstanding": outstanding,
            "wake_events": self.wake_events,
            "atp_while_waiting": self.atp_while_waiting,
            "material_shortfalls": self.material_shortfalls,
            "book1_violating_actions": self.book1_violating_actions,
            "book1_violations": len(self.book1_violations),
            "draws": self.rng.draws,
            "edges": self.observed if keep_edges else None,
        }

    def window(self, w):
        """The last `w` reactions by BIRTH index, split three ways. `rate` is
        settled/w — the preregistered statistic — and `waiting` is reported
        beside it rather than folded into failure (the EXP-010 censoring
        lesson): a parked reaction is unresolved AT THE HORIZON."""
        lo = self.reactions - w
        settled = sum(1 for i in self.settled_at_birth if i >= lo)
        waiting = sum(1 for i in self.individuals
                      if not i.founder and i.born >= lo and i.state == "waiting")
        return {"settled": settled, "waiting": waiting,
                "failed": w - settled - waiting,
                "rate": settled / w,
                "rate_upper": (settled + waiting) / w}


def run_cell(arm, seed, **kw):
    keep = kw.pop("keep_edges", False)
    return Soup(arm, seed, **kw).run(keep_edges=keep)


# ---------- controls ----------
def control_rng():
    """C-RNG, fail-closed and with its own negative control.

    A draw must be a function of `(seed, reaction, event)` and of nothing else.
    So: run a cell, run it again with ONE reaction forced to starve where it
    settled, and demand that every keyed draw word agree — before and after the
    perturbation — even though the soups diverge from that reaction onward.

    Then the same comparison under `StreamRandom`, where it must FAIL. A
    decorrelation control that cannot fail is a decorrelation control nobody has
    watched, and this whole experiment exists because EXP-010's arms had
    correlated streams.
    """
    seed, k = C.SEEDS[0], 300
    out = {}
    for mode in ("counter", "stream"):
        b = Soup("FM", seed, reactions=600, rng_mode=mode)
        b.run()
        p = Soup("FM", seed, reactions=600, rng_mode=mode, perturb_at=k)
        p.run()
        bw = {(i, e): w for i, e, n, v, w in b.draw_log}
        pw = {(i, e): w for i, e, n, v, w in p.draw_log}
        shared = sorted(set(bw) & set(pw))
        before = [key for key in shared if key[0] < k]
        after = [key for key in shared if key[0] > k]
        agree_before = sum(1 for key in before if bw[key] == pw[key])
        agree_after = sum(1 for key in after if bw[key] == pw[key])
        out[mode] = {"keys_before": len(before), "agree_before": agree_before,
                     "keys_after": len(after), "agree_after": agree_after,
                     "perturbed_at": k,
                     "histories_diverged": b.ok != p.ok}
    return out


C3_FIELDS = ("ok", "fail", "success_rate", "closure", "distinct", "mean_cost",
             "median_cost", "core_size", "core", "l0", "poisoned", "pool_left",
             "endowment")


def controls():
    out = []

    out.append((f"C-corpus the corpus is ALIFE-EXP-001's, fingerprint "
                f"{C.fingerprint()}",
                C.fingerprint() == C.INHERITED_FINGERPRINT))

    a, b, c = b"a", b"b", b"c"
    out.append((f"C-core the peeling used by C-compat closes a closed pair "
                f"({len(l1_core([(a, b, a), (b, a, b)]))}) and returns nothing "
                f"on an open chain ({len(l1_core([(a, b, c)]))})",
                l1_core([(a, b, a), (b, a, b)]) == {a, b}
                and l1_core([(a, b, c)]) == set()))

    # C-RNG FIRST: without it no cross-arm comparison below is valid.
    rng = control_rng()
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

    # C-compat: arm BF, stream RNG, against EXP-007's committed receipt.
    frozen = C.exp007_frozen()["result"]["primary"]
    compat = {s: run_cell("BF", s, rng_mode="stream") for s in C.COMPAT_SEEDS}
    diffs = []
    for s in C.COMPAT_SEEDS:
        ref = frozen[str(s)]
        for f in C3_FIELDS:
            if compat[s][f] != ref[f]:
                diffs.append(f"seed {s} {f}: {compat[s][f]!r} != {ref[f]!r}")
    out.append((f"C-compat arm BF on the post-D98/D99 engine reproduces "
                f"ALIFE-EXP-007's frozen receipt on all {len(C.COMPAT_SEEDS)} "
                f"shared seeds across {len(C3_FIELDS)} recorded fields "
                f"({len(diffs)} divergences) - so the documented deltas on this "
                f"chemistry are zero and any other difference is a harness bug",
                not diffs))
    for d in diffs[:6]:
        out.append((f"   C-compat detail: {d}", False))

    cells = {arm: {s: run_cell(arm, s) for s in C.SEEDS} for arm in C.ARMS}
    flat = [r for a in cells.values() for r in a.values()]

    # C-fire, both halves.
    cons = {arm: {s: cells[arm][s]["consumed_deaths"] for s in C.SEEDS}
            for arm in ("BM", "FM")}
    # STRICT reading: for each of BM and FM, for each seed, >= 50. That is the
    # reading that matches ALIFE-EXP-010's C2 ("at least 50 consumed deaths per
    # seed in Arm M"), which this control is echoing, and it is the demanding
    # one. Choosing the looser per-seed-across-both-arms reading would pass
    # every cell, which is exactly why it is not chosen. See DECISIONS.md D107.
    low = [f"{arm}/{s}={cons[arm][s]}" for arm in ("BM", "FM") for s in C.SEEDS
           if cons[arm][s] < C.C_FIRE_MIN_CONSUMED]
    fire_m = not low
    detail = []
    for arm in ("BM", "FM"):
        for s in C.SEEDS:
            r = cells[arm][s]
            detail.append(f"{arm}/{s}: {r['rs_fired']} R-S, "
                          f"{r['rs_genesis']} on genesis (free), "
                          f"{r['rs_fired'] - r['rs_genesis']} eligible = "
                          f"{r['consumed_deaths']} consumed + "
                          f"{r['blocked_events']} blocked")
    out.append((f"C-fire(matter) >= {C.C_FIRE_MIN_CONSUMED} consumption events "
                f"in every M cell: BM {[cons['BM'][s] for s in C.SEEDS]}, FM "
                f"{[cons['FM'][s] for s in C.SEEDS]}"
                + (f" - BELOW THE FLOOR in {len(low)} of 10 cells ({', '.join(low)})"
                   if low else ""), fire_m))
    if low:
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
                if set(book) == {str(C.FLOOR_PRICE)}:
                    bad_price.append(f"{arm}/{s} never duplicated anything "
                                     f"bigger than a leaf")
            elif charged != book:
                bad_price.append(f"{arm}/{s} book price not charged")
    floor_events = sum(cells[arm][s]["rs_fired"]
                       for arm in ("FF", "FM") for s in C.SEEDS)
    out.append((f"C-fire(price) the floor is charged on every R-S in FF and FM "
                f"({floor_events} events, no silent Book-I fallback) and Book I "
                f"is charged on every R-S in BF and BM ({len(bad_price)} "
                f"violations)", not bad_price and floor_events > 0))

    # C-ledger.
    led = [f"{r['arm']}/{r['seed']}" for r in flat
           if not r["ledger_ok"] or not r["ledger_identity_ok"]
           or not r["census_counts_ok"] or r["consumed_but_alive"]]
    waits = sum(r["waits_outstanding"] for r in flat)
    consumed = sum(r["consumed_deaths"] for r in flat)
    out.append((f"C-ledger conservation and census totality held on every tick "
                f"of all {len(flat)} cells; {consumed} `consumed` deaths and "
                f"{waits} waits at the horizon are accounted "
                f"({len(led)} failures)", not led))

    # C-det.
    det = []
    for arm in C.ARMS:
        for s in C.SEEDS:
            if run_cell(arm, s) != cells[arm][s]:
                det.append(f"{arm}/{s}")
    out.append((f"C-det every cell run twice gives an identical receipt "
                f"({len(det)} divergences)", not det))

    return all(ok for _, ok in out), out, cells, rng


# ---------- the factorial ----------
def spread(values):
    return max(values) - min(values)


def factorial(cells):
    """Main effects, interaction, and the gate they must clear.

    The gate is the preregistered E-vs-E' discipline: an effect is claimed only
    if it exceeds the LARGEST within-cell seed spread among the cells it is
    computed from. All three estimands here are computed from all four cells, so
    they share one gate per outcome.
    """
    out = {}
    for outcome in C.OUTCOMES:
        v = {arm: [cells[arm][s][outcome] for s in C.SEEDS] for arm in C.ARMS}
        m = {arm: statistics.mean(v[arm]) for arm in C.ARMS}
        sp = {arm: spread(v[arm]) for arm in C.ARMS}
        gate = max(sp.values())
        price = (m["BF"] + m["BM"]) / 2 - (m["FF"] + m["FM"]) / 2
        matter = (m["BF"] + m["FF"]) / 2 - (m["BM"] + m["FM"]) / 2
        inter = (m["BF"] - m["BM"]) - (m["FF"] - m["FM"])
        out[outcome] = {
            "label": C.OUTCOME_LABEL[outcome],
            "per_seed": {arm: v[arm] for arm in C.ARMS},
            "cell_mean": m, "cell_spread": sp, "gate": gate,
            "effects": {
                "price": {"value": price, "claimable": abs(price) > gate},
                "matter": {"value": matter, "claimable": abs(matter) > gate},
                "interaction": {"value": inter, "claimable": abs(inter) > gate},
            },
        }
    return out


def score(fac):
    """X1, X2, X3, by name, under the gate."""
    price_settled = fac["settled"]["effects"]["price"]
    x1 = not price_settled["claimable"]

    matter_claimable = [o for o in C.OUTCOMES
                        if fac[o]["effects"]["matter"]["claimable"]]
    diversity = fac["distinct_nongenesis"]["effects"]["matter"]
    # "positive for M" — the effect is defined free-minus-consume, so M being
    # HIGHER means the effect is negative. Named explicitly so the sign cannot
    # be read backwards.
    diversity_positive_for_m = diversity["value"] < 0
    x2 = len(matter_claimable) >= 2 and diversity_positive_for_m

    inter_claimable = [o for o in C.OUTCOMES
                       if fac[o]["effects"]["interaction"]["claimable"]]
    x3 = not inter_claimable

    return {
        "X1": {"claim": "the price main effect on settled count is WITHIN the "
                        "seed-spread gate (not claimable)",
               "price_effect_on_settled": price_settled["value"],
               "gate": fac["settled"]["gate"],
               "claimable": price_settled["claimable"],
               "verdict": "HOLDS" if x1 else "FAILS"},
        "X2": {"claim": "the matter main effect is claimable on >= 2 of 4 "
                        "outcomes, and on distinct hashes its sign favours M",
               "claimable_outcomes": matter_claimable,
               "n_claimable": len(matter_claimable),
               "diversity_effect_free_minus_consume": diversity["value"],
               "diversity_gate": fac["distinct_nongenesis"]["gate"],
               "diversity_claimable": diversity["claimable"],
               "diversity_favours_m": diversity_positive_for_m,
               "verdict": "HOLDS" if x2 else "FAILS"},
        "X3": {"claim": "the interaction term is within the gate on every "
                        "outcome",
               "claimable_outcomes": inter_claimable,
               "verdict": "HOLDS" if x3 else "FAILS"},
    }


def summarize(result):
    cells, fac, sc = result["cells"], result["factorial"], result["scores"]
    print(f"{'arm':>4s} {'seed':>10s} {'settled':>8s} {'census':>7s} "
          f"{'distinct':>9s} {'win100':>7s} {'waiting':>8s} {'consumed':>9s} "
          f"{'R-S':>6s} {'ATP on R-S':>11s} {'bookI viol':>11s}")
    for arm in C.ARMS:
        for s in C.SEEDS:
            r = cells[arm][str(s)]
            print(f"{arm:>4s} {s:>10d} {r['settled']:>8d} {r['census']:>7d} "
                  f"{r['distinct_nongenesis']:>9d} "
                  f"{r['window_success']:>6.0%} {r['waits_outstanding']:>8d} "
                  f"{r['consumed_deaths']:>9d} {r['rs_fired']:>6d} "
                  f"{r['rs_atp']:>11d} {r['book1_violating_actions']:>11d}")

    print("\nTHE FACTORIAL — every effect beside the gate it has to clear\n")
    for outcome in C.OUTCOMES:
        f = fac[outcome]
        print(f"  {f['label']}")
        print(f"    cell means   " + "  ".join(
            f"{arm} {f['cell_mean'][arm]:>8.2f}" for arm in C.ARMS))
        print(f"    seed spreads " + "  ".join(
            f"{arm} {f['cell_spread'][arm]:>8.2f}" for arm in C.ARMS)
            + f"   -> gate {f['gate']:.2f}")
        for name in ("price", "matter", "interaction"):
            e = f["effects"][name]
            mark = "CLAIMABLE" if e["claimable"] else "within the gate"
            print(f"    {name:<12s} {e['value']:>+9.2f}   {mark}")
        print()

    print("PREDICTIONS, scored by name\n")
    for k in ("X1", "X2", "X3"):
        print(f"  {k}: {sc[k]['verdict']} — {sc[k]['claim']}")
    print(f"     X1: price effect on settled {sc['X1']['price_effect_on_settled']:+.2f} "
          f"against a gate of {sc['X1']['gate']:.2f}")
    print(f"     X2: matter claimable on {sc['X2']['n_claimable']}/4 "
          f"{sc['X2']['claimable_outcomes']}; diversity effect "
          f"{sc['X2']['diversity_effect_free_minus_consume']:+.2f} "
          f"(free minus consume; negative = M is more diverse), "
          f"{'claimable' if sc['X2']['diversity_claimable'] else 'within the gate'}")
    print(f"     X3: interaction claimable on "
          f"{sc['X3']['claimable_outcomes'] or 'nothing'}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--record", action="store_true")
    ap.add_argument("--controls", action="store_true")
    args = ap.parse_args()

    C.build()
    ok, results, cells, rng = controls()
    for name, passed in results:
        print(("OK  " if passed else "FAIL"), name)
    if not ok:
        print("\nALIFE-EXP-012: CONTROLS FAILED - nothing measured, "
              "nothing recorded")
        return 1
    if args.controls:
        print("\nEXP-012-CONTROLS: ALL PASS")
        return 0

    fac = factorial(cells)
    result = {
        "cells": {arm: {str(s): cells[arm][s] for s in C.SEEDS}
                  for arm in C.ARMS},
        "factorial": fac,
        "scores": score(fac),
        "rng_control": rng,
    }
    print()
    summarize(result)

    prov = al.provenance()
    receipt = {
        "experiment": "ALIFE-EXP-012",
        "corpus_fingerprint": C.fingerprint(),
        "inherited_from": ["ALIFE-EXP-001", "ALIFE-EXP-007", "ALIFE-EXP-010"],
        "frame": {"arms": list(C.ARMS), "cells": C.CELL,
                  "arm_labels": C.ARM_LABEL, "seeds": list(C.SEEDS),
                  "compat_seeds": list(C.COMPAT_SEEDS),
                  "capacity": C.CAPACITY, "reactions": C.REACTIONS,
                  "atp_per_reaction": C.ATP_PER_REACTION,
                  "slice_atp": C.SLICE_ATP, "floor_price": C.FLOOR_PRICE,
                  "final_window": C.FINAL_WINDOW,
                  "outcomes": list(C.OUTCOMES),
                  "c_fire_min_consumed": C.C_FIRE_MIN_CONSUMED,
                  "rng": "counter-based, keyed (seed, reaction_index, event)",
                  "engine": "post-ALIFE-EXP-011: D98 cull re-tests starvation, "
                            "D99 holders-based rebate"},
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
