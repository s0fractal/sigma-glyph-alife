#!/usr/bin/env python3
"""Two arms that differ in one price: what a duplication is paid for with.

Arm E is ALIFE-EXP-007's chemistry unchanged — `R-S` costs `1 + size(z)` in ATP
and the copy is conjured. Arm M charges the action floor and takes the copy out
of the census: a living molecule with the duplicated argument's hash is consumed,
and an `R-S` with no copy to eat is a WAIT, not a death.

Check-only by default; `--record` writes `results.json` after every control
passes. Judged against
`../ALIFE-EXP-010-does-the-currency-choose-the-colony-preregistration.md`,
committed before this file; the choices that document left open are in
`DECISIONS.md` D74-D86, committed before this file ran.

The two arms share ONE driver. `sigma_alife.reduce_slice` gained a
`duplication_gate` hook (D86) rather than this harness gaining a second copy of
the reduction loop, because "identical in every respect except the pricing of
duplication" is a claim about the code and not only about the intent.
"""
import argparse
import json
import platform
import random
import statistics
import sys
from collections import deque
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "impl"))

import corpus as C  # noqa: E402
import sigma_alife as al  # noqa: E402
import sigma_nulls as N  # noqa: E402

sg = al.sg
DIS_HASHES = None
ORACLE_BUDGET = 400_000        # a budget large enough that "the oracle did not
                               # finish" means divergence, not poverty


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
    """ALIFE-EXP-007's peeling, copied verbatim and re-guarded by its own C5
    below rather than imported: EXP-007's `measure.py` binds the module name
    `corpus` to its own frame on import, and two experiments cannot both own that
    name in one process."""
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


def jaccard(x, y):
    """|A n B| / |A u B|, and None — never 1.0 — when both sides are empty.
    D82: an empty union is an absent measurement, and H1 is scored on overlap
    being BELOW a threshold, so calling it 0.0 would hand H1 a free seed."""
    x, y = set(x), set(y)
    if not (x | y):
        return None
    return len(x & y) / len(x | y)


# ---------- the census (D74) ----------
class Individual:
    """One molecule-life: born, possibly reduced, possibly living in the soup,
    and leaving it in exactly one way. `state` is the C7 partition."""
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


STATES = ("alive", "consumed", "culled", "starved", "waiting", "faulted",
          "unresolved")


class MatterGate:
    """The Arm M price of `R-S`, as `reduce_slice` consumes it (D86)."""

    def __init__(self, soup):
        self.soup = soup

    def price_of(self, z):
        return C.MATTER_PRICE

    def afford(self, agent, z, spent):
        return self.soup.afford_duplication(agent, z, spent)


class EnergyGate:
    """Book I's own price for `R-S`, through the same hook, affording always.

    This gate changes NOTHING — it is the identity on the chemistry — and exists
    so that the hook itself can be falsified rather than trusted (D87). Control
    C0c runs Arm E through it and requires the receipt to be identical to Arm E
    running on the oracle's untouched dispatch; only then is Arm M's machinery
    known to be re-pricing one rule rather than perturbing the loop. It is also
    the only way to count how many duplications the ENERGY arm performs, which
    is the denominator every matter-arm statement is implicitly against.
    """

    def __init__(self, soup):
        self.soup = soup

    def price_of(self, z):
        return 1 + sg.size(z)

    def afford(self, agent, z, spent):
        self.soup.rs_fired += 1
        self.soup.note_z(z, self.price_of(z))
        if sg.term_hash(z) in sg.GENESIS:
            self.soup.rs_genesis += 1
        return True


class Soup:
    """ALIFE-EXP-007's bounded reactor, with a census bolted on that both arms
    carry. Arm E's numbers must come out of this the way they came out of
    EXP-007 — see control C3 — so every RNG draw below is the draw EXP-007 made,
    in the order it made it."""

    def __init__(self, arm, budget, seed, reactions, capacity, probe,
                 observe=False):
        self.arm = arm
        self.budget = budget
        self.seed = seed
        self.reactions = reactions
        self.capacity = capacity
        # D78: an arm that charges the floor for a duplication has given up the
        # premise `dsize <= cost - 1` that the Book I per-agent bound follows
        # from, so Arm M runs with the probe OFF and the harness checks the
        # census bound instead. Arm E keeps the probe on every action.
        self.probe = probe and arm == "E"
        self.store = fresh_store()
        self.rng = random.Random(seed)
        self.econ = al.Economy(budget * reactions + 1)
        self.observe = observe
        self.gate = (MatterGate(self) if arm == "M"
                     else EnergyGate(self) if observe else None)

        self.individuals = []
        self.soup = []                 # list of living Individuals, positional
        for e in C.build()[:capacity]:
            h = al.put_term(e["term"], self.store)
            ind = Individual(len(self.individuals), 0, True, sg.size(e["term"]))
            ind.hash = h
            self.individuals.append(ind)
            self.soup.append(ind)

        self.parked = {}               # awaited hash -> [Individual] (D81)
        self.observed = []             # (a, b, product) reaction edges
        self.ok = self.fail = self.closed = self.poisoned = 0
        self.costs = []
        self.trace = []
        self.settled_at_birth = set()
        self.checked = self.mismatches = self.oracle_unfinished = 0
        self.sample_check = 0

        # matter bookkeeping
        self.rs_fired = 0
        self.rs_genesis = 0
        self.rs_atp = 0                 # what duplication actually costs in this
        self.rs_zsize_sum = 0           # arm, and how much term is being copied:
        self.rs_zsize_max = 0           # the machine is LAZY, so `z` is usually
                                        # an address and `1 + size(z)` is usually 2
        self.consumed = 0
        self.blocked_events = 0
        self.blocked_on = None
        self.atp_transferred = 0
        self.transfer_mismatches = 0
        self.material_shortfalls = 0    # size(consumed) < size(z): must stay 0
        self.material_freed = 0
        self.material_created = 0
        self.book1_violations = set()   # individuals whose per-agent Book I
                                        # bound `size <= s0 + spent` ever failed
        self.book1_violating_actions = 0
        self.running_iid = None
        self.atp_while_waiting = 0
        self.wake_events = 0
        self.ledger_ok = True
        self.census_bound_ok = True
        self.census_counts_ok = True
        self.consumed_but_alive = 0
        self.spent_total = 0

    def note_z(self, z, price):
        n = sg.size(z)
        self.rs_atp += price
        self.rs_zsize_sum += n
        self.rs_zsize_max = max(self.rs_zsize_max, n)

    # -- the matter price -----------------------------------------------------
    def afford_duplication(self, agent, z, spent):
        """Book I's `R-S` conjures the copy and charges for it. Here the copy is
        matter: it comes out of a living body or it does not come at all."""
        h = sg.term_hash(z)
        self.rs_fired += 1
        self.note_z(z, C.MATTER_PRICE)
        # What Book I's per-agent bound will read the instant this action lands.
        # Reported, never suppressed (D78): a floor-priced duplication that grows
        # the term by more than one BREAKS `size <= s0 + spent`, deterministically
        # and by design, and a receipt that showed zero here would be hiding the
        # arm rather than measuring it.
        after = sg.size(agent.term) + max(0, sg.size(z) - 1)
        if after > agent.s0 + agent.spent + spent + C.MATTER_PRICE:
            self.book1_violations.add(self.running_iid)
            self.book1_violating_actions += 1
        if h in sg.GENESIS:
            # Genesis atoms are freely available — Book I resolves genesis without
            # a store, K&M keep the elementary combinators in the food set. A
            # genesis `z` is a size-1 leaf, so the copy adds nothing to the census
            # and the Book I discipline `dsize <= cost - 1` survives at the floor.
            self.rs_genesis += 1
            return True
        victim = None
        for ind in self.soup:
            if ind.hash == h:
                victim = ind if victim is None or ind.born < victim.born else victim
        if victim is None:
            self.blocked_events += 1
            self.blocked_on = h
            return False

        # consume: the body leaves the census, its reservoir moves in full
        before = agent.atp
        moved = getattr(victim, "atp", 0)      # D77: molecules hold none here
        agent.atp += moved
        self.atp_transferred += moved
        if agent.atp - before != moved:
            self.transfer_mismatches += 1
        self.soup.remove(victim)
        victim.state = "consumed"
        self.consumed += 1
        self.material_freed += victim.size
        self.material_created += max(0, sg.size(z) - 1)
        if victim.size < sg.size(z):
            self.material_shortfalls += 1
        return True

    # -- the driver -----------------------------------------------------------
    def drive(self, ind):
        """EXP-007's escalating-slice loop, unchanged, plus the parking that a
        re-priced R-S makes possible. Arm E never parks."""
        agent = ind.agent
        self.blocked_on = None
        self.running_iid = ind.iid
        spent_before = agent.spent
        term_before = agent.term
        slice_atp = C.SLICE_ATP
        while agent.status in al.RUNNABLE and agent.atp > 0:
            got = al.reduce_slice(agent, self.store, slice_atp, probe=self.probe,
                                  duplication_gate=self.gate)
            if agent.status != al.LIVE:
                break
            if not got:
                slice_atp = min(agent.atp, max(1, slice_atp * 2))
        ind.size = sg.size(agent.term)
        if agent.size > agent.s0 + agent.spent:
            self.book1_violations.add(ind.iid)
        if agent.status == al.BLOCKED:
            if ind.state == "waiting" and agent.term == term_before:
                # a retry that changed NOTHING is the wait EXP-009 priced at
                # zero; a retry that moved the term bought progress and calling
                # that "waiting" is what hid a delivery bug for one run there
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
        self.fail += 1
        self.release(ind)
        return None

    def release(self, ind):
        """An individual that will never run again hands its ledger line to the
        run total and drops the term. Keeping a thousand finished agents alive
        would hold a thousand terms in memory for no reason; keeping their SPEND
        is not optional, because the ledger and the census bound are both stated
        against a sum over everything ever born."""
        self.spent_total += ind.agent.spent
        ind.agent = None

    def settle(self, ind):
        """EXP-007's success path, action for action, with the individual that
        ran the reaction becoming the molecule the reaction made."""
        agent = ind.agent
        self.econ.collect(agent, agent.atp)
        self.ok += 1
        self.settled_at_birth.add(ind.born)
        self.costs.append(agent.spent)
        product = al.put_term(agent.term, self.store)
        if self.sample_check and self.checked < self.sample_check:
            oracle_atp = self.budget if self.arm == "E" else ORACLE_BUDGET
            ref, _ = sg.eval_hash(agent.root, oracle_atp, self.store)
            if ref == ("dis", sg.R_ATP):
                self.oracle_unfinished += 1
            else:
                self.mismatches += sg.term_hash(ref) != product
            self.checked += 1
        if any(m.hash == product for m in self.soup):
            self.closed += 1
        a, b = self.edge_of[ind.iid]
        self.observed.append((a, b, product))
        ind.hash = product
        ind.size = sg.size(agent.term)
        ind.state = "alive"
        self.release(ind)
        self.soup.append(ind)
        if len(self.soup) > self.capacity:
            victim = self.soup.pop(self.rng.randrange(len(self.soup)))
            victim.state = "culled"
        return product

    def wake(self, product):
        """D81: the molecule that just arrived is the only thing that can unblock
        an agent waiting for it. Birth order; no randomness drawn."""
        queue = deque()
        for ind in sorted(self.parked.pop(product, []), key=lambda x: x.born):
            queue.append(ind)
        while queue:
            ind = queue.popleft()
            self.wake_events += 1
            ind.agent.status = al.LIVE
            made = self.drive(ind)
            if made is not None:
                for nxt in sorted(self.parked.pop(made, []), key=lambda x: x.born):
                    queue.append(nxt)

    # -- invariants (C1, C7) ---------------------------------------------------
    def check_invariants(self):
        parked = [i for i in self.individuals if i.state == "waiting"]
        held = sum(i.agent.atp for i in parked if i.agent)
        spent = self.spent_total + sum(i.agent.spent
                                       for i in self.individuals if i.agent)
        if self.econ.pool + held + spent != self.econ.endowment:
            self.ledger_ok = False
        alive = [i for i in self.individuals if i.state == "alive"]
        lhs = sum(i.size for i in alive) + sum(i.size for i in parked)
        rhs = sum(i.s0 for i in self.individuals) + spent
        if lhs > rhs:
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

    # -- the run ---------------------------------------------------------------
    def run(self, sample_check=0, keep_edges=False):
        self.sample_check = sample_check
        self.edge_of = {}
        counts = None
        for i in range(self.reactions):
            a = self.rng.choice(self.soup).hash
            b = self.rng.choice(self.soup).hash
            root = al.put_term(("app", ("thunk", a), ("thunk", b)), self.store)
            ind = Individual(len(self.individuals), i, False, 1)
            self.individuals.append(ind)
            self.edge_of[ind.iid] = (a, b)
            agent = al.Agent(f"r{i}", root, 0)
            ind.agent = agent
            self.econ.endow(agent, self.budget)
            product = self.drive(ind)
            if product is not None:
                self.wake(product)
            self.poisoned += sum(1 for m in self.soup if m.hash in dis_hashes())
            counts = self.check_invariants()
            if (i + 1) % 100 == 0:
                self.trace.append({"reaction": i + 1,
                                   "distinct": len({m.hash for m in self.soup}),
                                   "closure": self.closed / max(1, self.ok),
                                   "ok": self.ok, "fail": self.fail,
                                   "census": len(self.soup),
                                   "waiting": counts["waiting"],
                                   "consumed": counts["consumed"]})
        outstanding = counts["waiting"]
        self.fail += outstanding
        core = l1_core(self.observed)
        return {
            "arm": self.arm, "budget": self.budget, "seed": self.seed,
            "reactions": self.reactions, "ok": self.ok, "fail": self.fail,
            "success_rate": self.ok / self.reactions,
            "closure": self.closed / max(1, self.ok),
            "distinct": len({m.hash for m in self.soup}),
            "census": len(self.soup),
            "survivors": sorted({m.hash.hex() for m in self.soup
                                 if m.hash not in sg.GENESIS}),
            "mean_cost": statistics.mean(self.costs) if self.costs else 0,
            "median_cost": statistics.median(self.costs) if self.costs else 0,
            "l0": sorted({c.hex() for a, b, c in self.observed if a == b == c}),
            "core_size": len(core),
            "core": sorted(h.hex() for h in core),
            "trace": self.trace,
            "checked": self.checked, "mismatches": self.mismatches,
            "oracle_unfinished": self.oracle_unfinished,
            "poisoned": self.poisoned,
            "edges": self.observed if keep_edges else None,
            "ledger_ok": self.ledger_ok,
            "census_bound_ok": self.census_bound_ok,
            "census_counts_ok": self.census_counts_ok,
            "consumed_but_alive": self.consumed_but_alive,
            "pool_left": self.econ.pool,
            "endowment": self.econ.endowment,
            "census_counts": counts,
            "born": len(self.individuals),
            "rs_fired": self.rs_fired,
            "rs_genesis": self.rs_genesis,
            "rs_atp": self.rs_atp,
            "rs_zsize_mean": (self.rs_zsize_sum / self.rs_fired
                              if self.rs_fired else 0),
            "rs_zsize_max": self.rs_zsize_max,
            "consumed_deaths": self.consumed,
            "blocked_events": self.blocked_events,
            "waits_outstanding": outstanding,
            "wake_events": self.wake_events,
            "atp_while_waiting": self.atp_while_waiting,
            "atp_transferred": self.atp_transferred,
            "transfer_mismatches": self.transfer_mismatches,
            "material_shortfalls": self.material_shortfalls,
            "material_freed": self.material_freed,
            "material_created": self.material_created,
            "book1_violations": len(self.book1_violations),
            "book1_violating_actions": self.book1_violating_actions,
            "settled_at_birth": sorted(self.settled_at_birth),
            "window_success": {str(w): window_success(self.settled_at_birth,
                                                      self.reactions, w)
                               for w in C.SENSITIVITY_WINDOWS},
        }


def window_success(settled_at_birth, reactions, window):
    """D79/D80: fraction of the reactions STARTED in the last `window` that ever
    reached a normal form. A reaction that parked and resumed later is a success
    in the window it was born in; one still parked at the end is not."""
    lo = reactions - window
    return sum(1 for i in settled_at_birth if i >= lo) / window


def run_soup(arm, budget, seed, reactions=None, capacity=None, probe=False,
             sample_check=0, keep_edges=False, observe=False):
    s = Soup(arm, budget, seed,
             reactions if reactions is not None else C.REACTIONS,
             capacity if capacity is not None else C.CAPACITY, probe,
             observe=observe)
    return s.run(sample_check=sample_check, keep_edges=keep_edges)


# ---------- controls ----------
C3_FIELDS = ("ok", "fail", "success_rate", "closure", "distinct", "mean_cost",
             "median_cost", "core_size", "core", "l0", "poisoned", "pool_left",
             "endowment")


def control_c0():
    """C0 (D84) — `_next_redex` is the oracle's own dispatch.

    Every prediction is checked against what `step5` actually did, in both
    directions: the predicted action must fully determine the oracle's new term
    AND the oracle's price. A mirror that missed an R-S would silently leave Arm
    M charging Book I for a duplication; a mirror that invented one would charge
    the floor for something that is not a duplication."""
    store = fresh_store()
    limits = sg.DEFAULT_LIMITS
    checked = {"force": 0, "ref": 0, "I": 0, "K": 0, "S": 0}
    bad = []
    for e in C.build():
        t = ("thunk", al.put_term(e["term"], store))
        stats = {"fetches": 0}
        for _ in range(400):
            pred = al._next_redex(t)
            try:
                r = sg.step5(t, 10 ** 7, store, stats, limits)
            except (sg.BudgetExhausted, sg.Unresolved, sg.ResourceFault):
                break
            if r is None:
                if pred is not None:
                    bad.append((e["name"], "oracle stopped, mirror did not"))
                break
            if pred is None:
                bad.append((e["name"], "mirror stopped, oracle did not"))
                break
            kind, path, payload = pred
            node = t
            for step in path:
                node = node[step]
            if kind == "force":
                want = sg.force(payload, store, dict(stats), limits)
                cost = sg.size(want)
            elif kind == "ref":
                want, cost = ("thunk", node[1]), 1
            elif kind == "I":
                want, cost = node[2], 1
            elif kind == "K":
                want, cost = node[1][2], 1
            else:
                x, y, z = payload
                want = ("app", ("app", x, z), ("app", y, z))
                cost = 1 + sg.size(z)
            if al._replace_at(t, path, want) != r[0] or cost != r[1]:
                bad.append((e["name"], f"mirror predicted {kind} at {path}"))
                break
            checked[kind] += 1
            t = r[0]
    return checked, bad


def controls():
    out = []

    checked, bad = control_c0()
    out.append((f"C0 the redex mirror is the oracle's dispatch: "
                f"{checked['S']} R-S, {checked['force']} force, {checked['I']} "
                f"R-I, {checked['K']} R-K, {checked['ref']} R-R agree exactly "
                f"({len(bad)} disagreements)", not bad))

    a, b, c = b"a", b"b", b"c"
    out.append((f"C0b the core algorithm closes a closed pair "
                f"({len(l1_core([(a, b, a), (b, a, b)]))}) and returns nothing "
                f"on an open chain ({len(l1_core([(a, b, c)]))})",
                l1_core([(a, b, a), (b, a, b)]) == {a, b}
                and l1_core([(a, b, c)]) == set()))

    out.append((f"C5 the corpus is ALIFE-EXP-001's, fingerprint "
                f"{C.fingerprint()}",
                C.fingerprint() == C.INHERITED_FINGERPRINT))

    # C3 — Arm E against ALIFE-EXP-007's committed receipt, all three seeds.
    frozen = C.exp007_frozen()
    armE = {s: run_soup("E", C.ATP_PER_REACTION, s, probe=True, sample_check=25)
            for s in C.SEEDS}
    diffs = []
    for s in C.SEEDS:
        ref = frozen["result"]["primary"][str(s)]
        for f in C3_FIELDS:
            if armE[s][f] != ref[f]:
                diffs.append(f"seed {s} {f}: {armE[s][f]!r} != {ref[f]!r}")
    out.append((f"C3 Arm E reproduces ALIFE-EXP-007's frozen receipt on all "
                f"{len(C.SEEDS)} shared seeds across {len(C3_FIELDS)} recorded "
                f"fields ({len(diffs)} differences)", not diffs))
    if diffs:
        for d in diffs[:6]:
            out.append((f"   C3 detail: {d}", False))

    # C0c (D87) — the hook is the identity when it prices nothing.
    armEg = {s: run_soup("E", C.ATP_PER_REACTION, s, probe=True, observe=True)
             for s in C.SEEDS}
    volatile = ("checked", "mismatches", "oracle_unfinished", "rs_fired",
                "rs_genesis", "rs_atp", "rs_zsize_mean", "rs_zsize_max")
    ident = [str(s) for s in C.SEEDS
             if {k: v for k, v in armE[s].items() if k not in volatile}
             != {k: v for k, v in armEg[s].items() if k not in volatile}]
    out.append((f"C0c Arm E driven THROUGH the pricing hook at Book I's own "
                f"price is byte-identical to Arm E on the oracle's untouched "
                f"dispatch, all {len(C.SEEDS)} seeds ({len(ident)} divergences) "
                f"- so the hook re-prices one rule rather than perturbing the "
                f"loop", not ident))
    for s in C.SEEDS:
        for f in ("rs_fired", "rs_genesis", "rs_atp", "rs_zsize_mean",
                  "rs_zsize_max"):
            armE[s][f] = armEg[s][f]

    armM = {s: run_soup("M", C.ATP_PER_REACTION, s, sample_check=25)
            for s in C.SEEDS}

    # C1 — the ledger, every tick, both arms, including the consumed-transfer.
    led = all(r["ledger_ok"] for r in list(armE.values()) + list(armM.values()))
    tm = sum(r["transfer_mismatches"] for r in armM.values())
    out.append((f"C1 the ATP ledger balanced on every tick of both arms, and "
                f"every consumed body's reservoir landed in its duplicator the "
                f"same tick ({tm} transfer mismatches; "
                f"{sum(r['atp_transferred'] for r in armM.values())} ATP moved "
                f"in total - see DECISIONS.md D77)", led and tm == 0))

    # C2 — consumption actually fires. Fail-closed.
    cons = {s: armM[s]["consumed_deaths"] for s in C.SEEDS}
    out.append((f"C2 consumption fired in Arm M: "
                f"{', '.join(str(cons[s]) for s in C.SEEDS)} consumed deaths "
                f"(floor {C.C2_MIN_CONSUMED} per seed)",
                all(v >= C.C2_MIN_CONSUMED for v in cons.values())))

    # C4 — determinism, both arms, every seed, full length, run twice.
    det = []
    sampled = ("checked", "mismatches", "oracle_unfinished")
    for arm in C.ARMS:
        base = armE if arm == "E" else armM
        for s in C.SEEDS:
            again = run_soup(arm, C.ATP_PER_REACTION, s, observe=(arm == "E"))
            first = {k: v for k, v in base[s].items() if k not in sampled}
            second = {k: v for k, v in again.items() if k not in sampled}
            if first != second:
                det.append(f"{arm}/{s}: "
                           + ",".join(sorted(k for k in first
                                             if first[k] != second.get(k))))
    out.append((f"C4 every arm x seed run twice gives an identical receipt "
                f"({len(det)} divergences)", not det))

    # C6 — waiting spends nothing, and does not change the answer.
    waited = sum(r["atp_while_waiting"] for r in armM.values())
    mism = sum(r["mismatches"] for r in armM.values())
    unfin = sum(r["oracle_unfinished"] for r in armM.values())
    ckd = sum(r["checked"] for r in armM.values())
    out.append((f"C6 waiting spent {waited} ATP across Arm M, and {ckd - mism}"
                f"/{ckd} sampled Arm M products equal the oracle's own normal "
                f"form ({unfin} the oracle could not finish at {ORACLE_BUDGET} "
                f"ATP)", waited == 0 and mism == 0))

    # C7 — census accounting is total.
    tot = []
    for arm, runs in (("E", armE), ("M", armM)):
        for s in C.SEEDS:
            r = runs[s]
            cc = r["census_counts"]
            if sum(cc.values()) != r["born"] or cc["alive"] != r["census"]:
                tot.append(f"{arm}/{s} counts")
            if not r["census_counts_ok"]:
                tot.append(f"{arm}/{s} per-tick counts")
            if r["consumed_but_alive"] or not r["census_bound_ok"]:
                tot.append(f"{arm}/{s} bound")
    shortfalls = sum(r["material_shortfalls"] for r in armM.values())
    out.append((f"C7 every individual ever alive is settled, starved, waiting, "
                f"culled or consumed, the counts reconcile on every tick, no "
                f"consumed body appears alive, and every consumed body carried "
                f"at least the material its copy created ({len(tot)} "
                f"reconciliation failures, {shortfalls} material shortfalls)",
                not tot and shortfalls == 0))

    # C8 — saturation is reported.
    sat = {f"M/{s}": {"waits_outstanding": armM[s]["waits_outstanding"],
                      "transfer_overflow_guards": 0,
                      "faults": armM[s]["census_counts"]["faulted"],
                      "unresolved": armM[s]["census_counts"]["unresolved"]}
           for s in C.SEEDS}
    for s in C.SEEDS:
        sat[f"E/{s}"] = {"waits_outstanding": armE[s]["waits_outstanding"],
                         "transfer_overflow_guards": 0,
                         "faults": armE[s]["census_counts"]["faulted"],
                         "unresolved": armE[s]["census_counts"]["unresolved"]}
    out.append((f"C8 saturation reported: waits outstanding at the final tick "
                f"{[armM[s]['waits_outstanding'] for s in C.SEEDS]} in Arm M, "
                f"{[armE[s]['waits_outstanding'] for s in C.SEEDS]} in Arm E; "
                f"transfer overflow guards 0 (D77)", True))

    return all(ok for _, ok in out), out, {"E": armE, "M": armM}, sat


# ---------- nulls (D85) ----------
def core_nulls(runs):
    """EXP-008's two chance models, the same code path for both arms, twenty
    draws. Preregistered here so that any organization-flavored observation is
    already scored — D50's defect was that it was not."""
    out = {}
    for arm in C.ARMS:
        cell = {}
        for s in C.SEEDS:
            edges = [(i, a, b, c)
                     for i, (a, b, c) in enumerate(runs[arm][s]["edges"])]
            stat = (lambda e: len(l1_core([(a, b, c) for _, a, b, c in e])))
            full = N.sample(edges, stat, "shuffle_products",
                            draws=C.NULL_DRAWS, seed=s)
            local = N.sample(edges, stat, "shuffle_local", draws=C.NULL_DRAWS,
                             seed=s + 1, window=C.NULL_LOCAL_WINDOW,
                             total=len(edges))
            cell[str(s)] = {
                "core_observed": runs[arm][s]["core_size"],
                "full_shuffle_max": full["max"], "full_shuffle_mean": full["mean"],
                "locality_max": local["max"], "locality_mean": local["mean"],
                "draws": C.NULL_DRAWS, "window": C.NULL_LOCAL_WINDOW,
            }
        out[arm] = cell
    return out


# ---------- measurement ----------
def measure():
    # Arm E is driven through the hook at Book I's own price so that the receipt
    # can report how much duplication the ENERGY arm does. C0c is what licenses
    # that: it is the same run either way.
    runs = {arm: {s: run_soup(arm, C.ATP_PER_REACTION, s, keep_edges=True,
                              observe=(arm == "E"))
                  for s in C.SEEDS} for arm in C.ARMS}
    nulls = core_nulls(runs)
    for arm in C.ARMS:
        for s in C.SEEDS:
            runs[arm][s]["edges"] = None
    primary = {arm: {str(s): runs[arm][s] for s in C.SEEDS} for arm in C.ARMS}
    return {"primary": primary, "nulls": nulls, "scores": score(primary)}


def score(primary):
    w = str(C.FINAL_WINDOW)
    h1, h2c, h2d, h3 = {}, {}, {}, {}
    for s in C.SEEDS:
        e, m = primary["E"][str(s)], primary["M"][str(s)]
        h1[str(s)] = jaccard(e["survivors"], m["survivors"])
        h2c[str(s)] = {"E": e["census"], "M": m["census"],
                       "smaller": m["census"] < e["census"]}
        h2d[str(s)] = {"E": e["distinct"], "M": m["distinct"],
                       "fewer": m["distinct"] < e["distinct"]}
        h3[str(s)] = {"E": e["window_success"][w], "M": m["window_success"][w],
                      "delta": m["window_success"][w] - e["window_success"][w]}
    h1_hits = sum(1 for v in h1.values() if v is not None and v < C.H1_OVERLAP_MAX)
    h2c_hits = sum(1 for v in h2c.values() if v["smaller"])
    h2d_hits = sum(1 for v in h2d.values() if v["fewer"])
    h3_hits = sum(1 for v in h3.values() if v["delta"] >= C.H3_MARGIN)
    return {
        "H1": {"overlap": h1, "seeds_below": h1_hits,
               "required": C.H1_MIN_SEEDS,
               "verdict": "HOLDS" if h1_hits >= C.H1_MIN_SEEDS else "FAILS"},
        "H2": {"census": h2c, "distinct": h2d,
               "census_seeds": h2c_hits, "distinct_seeds": h2d_hits,
               "required_census": C.H2_CENSUS_SEEDS,
               "required_distinct": C.H2_DISTINCT_SEEDS,
               "verdict": "HOLDS" if (h2c_hits >= C.H2_CENSUS_SEEDS
                                      and h2d_hits >= C.H2_DISTINCT_SEEDS)
                          else "FAILS"},
        "H3": {"window": C.FINAL_WINDOW, "rates": h3, "seeds_clearing": h3_hits,
               "required": C.H3_MIN_SEEDS, "margin": C.H3_MARGIN,
               "verdict": "HOLDS" if h3_hits >= C.H3_MIN_SEEDS else "FAILS"},
    }


def summarize(result):
    p, sc = result["primary"], result["scores"]
    print(f"{'arm':>4s} {'seed':>10s} {'success':>8s} {'census':>7s} "
          f"{'distinct':>9s} {'closure':>8s} {'core':>5s} {'mean cost':>10s} "
          f"{'consumed':>9s} {'waits':>6s}")
    for arm in C.ARMS:
        for s in C.SEEDS:
            r = p[arm][str(s)]
            print(f"{arm:>4s} {s:>10d} {100 * r['success_rate']:>7.1f}% "
                  f"{r['census']:>7d} {r['distinct']:>9d} {r['closure']:>8.3f} "
                  f"{r['core_size']:>5d} {r['mean_cost']:>10.1f} "
                  f"{r['consumed_deaths']:>9d} {r['waits_outstanding']:>6d}")

    print(f"\nH1 (Jaccard of non-genesis survivors E vs M below "
          f"{C.H1_OVERLAP_MAX} in >= {C.H1_MIN_SEEDS} of 3)")
    for s in C.SEEDS:
        v = sc["H1"]["overlap"][str(s)]
        print(f"   seed {s}: {'undefined (both empty, D82)' if v is None else f'{v:.4f}'}")
    print(f"   -> {sc['H1']['seeds_below']}/3 seeds -> {sc['H1']['verdict']}")

    print(f"\nH2 (M's living census strictly smaller in 3 of 3, and strictly "
          f"fewer distinct hashes in >= 2 of 3)")
    for s in C.SEEDS:
        c, d = sc["H2"]["census"][str(s)], sc["H2"]["distinct"][str(s)]
        print(f"   seed {s}: census E={c['E']} M={c['M']} "
              f"{'smaller' if c['smaller'] else 'NOT smaller'}; "
              f"distinct E={d['E']} M={d['M']} "
              f"{'fewer' if d['fewer'] else 'NOT fewer'}")
    print(f"   -> census {sc['H2']['census_seeds']}/3, distinct "
          f"{sc['H2']['distinct_seeds']}/3 -> {sc['H2']['verdict']}")

    print(f"\nH3 (final-{C.FINAL_WINDOW}-reaction success rate in M exceeds E by "
          f">= {100 * C.H3_MARGIN:.0f} points in >= {C.H3_MIN_SEEDS} of 3, D79)")
    for s in C.SEEDS:
        r = sc["H3"]["rates"][str(s)]
        print(f"   seed {s}: E={100 * r['E']:.1f}% M={100 * r['M']:.1f}% "
              f"delta {100 * r['delta']:+.1f} points")
    print(f"   -> {sc['H3']['seeds_clearing']}/3 seeds -> {sc['H3']['verdict']}")
    print(f"   sensitivity (scores nothing): windows "
          f"{list(C.SENSITIVITY_WINDOWS)}")
    for s in C.SEEDS:
        deltas = [p["M"][str(s)]["window_success"][str(w)]
                  - p["E"][str(s)]["window_success"][str(w)]
                  for w in C.SENSITIVITY_WINDOWS]
        print(f"     seed {s}: " + "  ".join(f"{100 * d:+.1f}" for d in deltas))

    print("\nNULLS — the L1-core of each arm against both ALIFE-EXP-008 chance "
          f"models, {C.NULL_DRAWS} draws, same code path (D85)\n")
    print(f"{'arm':>4s} {'seed':>10s} {'core':>6s} {'full-shuffle max':>18s} "
          f"{'locality max':>14s}")
    for arm in C.ARMS:
        for s in C.SEEDS:
            n = result["nulls"][arm][str(s)]
            print(f"{arm:>4s} {s:>10d} {n['core_observed']:>6d} "
                  f"{n['full_shuffle_max']:>18d} {n['locality_max']:>14d}")

    print("\nECONOMY AND CENSUS")
    print(f"{'arm':>4s} {'seed':>10s} {'R-S fired':>10s} {'genesis':>8s} "
          f"{'consumed':>9s} {'blocked':>8s} {'wakes':>7s} {'ATP moved':>10s} "
          f"{'Book I viol.':>13s}")
    for arm in C.ARMS:
        for s in C.SEEDS:
            r = p[arm][str(s)]
            print(f"{arm:>4s} {s:>10d} {r['rs_fired']:>10d} "
                  f"{r['rs_genesis']:>8d} {r['consumed_deaths']:>9d} "
                  f"{r['blocked_events']:>8d} {r['wake_events']:>7d} "
                  f"{r['atp_transferred']:>10d} {r['book1_violations']:>13d}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--record", action="store_true")
    ap.add_argument("--controls", action="store_true",
                    help="run the controls and stop")
    args = ap.parse_args()

    C.build()
    ok, results, _, sat = controls()
    for name, passed in results:
        print(("OK  " if passed else "FAIL"), name)
    if not ok:
        print("\nALIFE-EXP-010: CONTROLS FAILED - nothing measured, "
              "nothing recorded")
        return 1
    if args.controls:
        print("\nEXP-010-CONTROLS: ALL PASS")
        return 0

    result = measure()
    print()
    summarize(result)

    prov = al.provenance()
    receipt = {
        "experiment": "ALIFE-EXP-010",
        "corpus_fingerprint": C.fingerprint(),
        "inherited_from": ["ALIFE-EXP-001", "ALIFE-EXP-007", "ALIFE-EXP-009"],
        "frame": {"arms": list(C.ARMS), "capacity": C.CAPACITY,
                  "reactions": C.REACTIONS,
                  "atp_per_reaction": C.ATP_PER_REACTION,
                  "slice_atp": C.SLICE_ATP, "seeds": list(C.SEEDS),
                  "matter_price": C.MATTER_PRICE,
                  "final_window": C.FINAL_WINDOW,
                  "sensitivity_windows": list(C.SENSITIVITY_WINDOWS),
                  "h1_overlap_max": C.H1_OVERLAP_MAX,
                  "h1_min_seeds": C.H1_MIN_SEEDS,
                  "h2_census_seeds": C.H2_CENSUS_SEEDS,
                  "h2_distinct_seeds": C.H2_DISTINCT_SEEDS,
                  "h3_margin": C.H3_MARGIN, "h3_min_seeds": C.H3_MIN_SEEDS,
                  "c2_min_consumed": C.C2_MIN_CONSUMED,
                  "null_draws": C.NULL_DRAWS,
                  "null_local_window": C.NULL_LOCAL_WINDOW},
        "provenance": {
            "sigma_alife_version": prov["sigma_alife_version"],
            "sigma_glyph_requirement": prov["sigma_glyph_requirement"],
            "oracle_sha256": prov["oracle_sha256"],
            "python": ".".join(prov["python"].split(".")[:2]),
            "platform": platform.python_implementation(),
        },
        "controls": {name: passed for name, passed in results},
        "saturation": sat,
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
