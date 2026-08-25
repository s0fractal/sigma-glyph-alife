#!/usr/bin/env python3
"""Σ-GLYPH ALife substrate — ATP-limited populations on the Book I machine.

NON-NORMATIVE. Nothing here changes Book I, Book II, Book III, or any released
Σ-GLYPH contract. This module is a *consumer* of the Book I oracle
(`impl/sigma_glyph.py` in s0fractal/sigma-glyph, pinned `>=0.6.7,<0.7.0`); it
adds population bookkeeping on top of the oracle's priced step and claims
nothing about the oracle it did not check.

WHAT IT REUSES AND WHAT IT DOES NOT
-----------------------------------
Book I's `eval_hash` is *total over canonical outcomes*: when the budget runs
out it returns `DISSONANCE(ATP Exhausted)` and the partial configuration is
gone. That contract is right for a check engine — a run either produced an
answer or it did not — and it is the wrong contract for a population, where
"ran out of ATP" must leave a body behind that can be resumed when food
arrives. So this module does NOT call `eval_hash` in the population loop. It
drives the same priced action, `sigma_glyph.step5`, in its own loop and keeps
the term at the point where the budget stopped it (`STARVED`).

That is a deliberate deviation and it is bounded to exactly one thing: the
outcome on exhaustion. Every action, its cost, the store, the fences, and the
genesis axioms are the oracle's. `tests/alife_differential.py` holds the driver
to that: run whole (one slice, full budget) it must agree with `eval_hash` on
result hash and on ATP spent, for every corpus term at every budget, with the
exhaustion outcome mapped `STARVED -> DISSONANCE(ATP Exhausted)` and
`UNRESOLVED -> DISSONANCE(Unresolved Reference)`.

THE BOUND, AND WHY SLICING DOES NOT WEAKEN IT
---------------------------------------------
Book I proves `size <= spent + 1` from a root thunk (`SizeBound.lean`,
`EvalMachine.evalHash_peak_size`). Resumption starts from a materialized term
of size `s0` rather than a thunk of size 1, so the honest per-agent statement is

    size(t) <= s0 + spent          (s0 = 1 for an agent born as a root thunk)

and it composes across slices, because `spent` accumulates and the per-action
premise (`Δsize <= cost - 1`) is a property of the action, not of the call that
performed it. `proofs/Population.lean` proves that composition and the
population sum that follows from it; `reduce_slice(..., probe=True)` checks the
same inequality against live traces at every action.

STATUS: DRAFT / EXPERIMENTAL. Policies below (rebates, transfers, culling,
crossover) are *policy*, not spec: they are one defensible choice each, chosen
to be deterministic and cheap to check, and none of them is proved to have any
biological or economic property. Where a rule is a heuristic it says so.
"""
import hashlib
import importlib.util
import math
import os
import sys
from collections import Counter
from pathlib import Path

__version__ = "0.1.0"

# ---------- Book I oracle ----------
SIGMA_GLYPH_REQ = ">=0.6.7,<0.7.0"


def load_sigma():
    """Load the Book I oracle. Search order (first hit wins):
      1. $SIGMA_GLYPH/sigma_glyph.py    — explicit override, the same environment
         variable the warrant CLI uses for the same job;
      2. an installed `sigma_glyph` module — a released wheel;
      3. ../sigma-glyph/impl/sigma_glyph.py — the sibling checkout, which is how
         this repository sits next to its dependency in a working tree;
      4. ~/Projects/sigma-glyph/impl/sigma_glyph.py — the conventional location.
    Returns (module, source, sha256-of-the-bytes-loaded). The digest goes into
    every receipt: a population number is a claim about the oracle that produced
    it, and "sigma-glyph 0.6.7" names a release, not the bytes on this disk.
    """
    candidates = []
    if os.environ.get("SIGMA_GLYPH"):
        candidates.append(Path(os.environ["SIGMA_GLYPH"]) / "sigma_glyph.py")
    here = Path(__file__).resolve()
    candidates.append(here.parents[2] / "sigma-glyph" / "impl" / "sigma_glyph.py")
    candidates.append(Path.home() / "Projects/sigma-glyph/impl" / "sigma_glyph.py")

    def _digest(path):
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()

    if os.environ.get("SIGMA_GLYPH") is None:
        try:                                   # 2: an installed wheel
            import sigma_glyph as mod          # noqa: PLC0415
            return mod, "installed:" + mod.__file__, _digest(mod.__file__)
        except ImportError:
            pass
    for path in candidates:
        if not path.exists():
            continue
        spec = importlib.util.spec_from_file_location("sigma_glyph", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod, str(path), _digest(path)
    raise ImportError(
        "the Σ-GLYPH Book I oracle was not found. Install `sigma-glyph"
        f"{SIGMA_GLYPH_REQ}`, or set SIGMA_GLYPH to the impl/ directory of a "
        "checkout (e.g. SIGMA_GLYPH=~/Projects/sigma-glyph/impl)")


sg, ORACLE_SOURCE, ORACLE_DIGEST = load_sigma()

# ---------- Agent status ----------
LIVE = "live"              # budget remains and the term is not in normal form
NORMAL = "normal"          # normal form reached — settled, Book I §3.4
STARVED = "starved"        # reservoir empty, term preserved at the stopping point
UNRESOLVED = "unresolved"  # demanded a hash the store does not hold
FAULT = "fault"            # local ResourceFault: non-canonical, an implementation limit
ARCHIVED = "archived"      # culled; the term stays in the CAS, the agent stops running
RUNNABLE = (LIVE, STARVED)


class Agent:
    """(term, reservoir, lineage) over a shared content-addressed store.

    `term` is a Book I term in the oracle's own representation; it starts as the
    root thunk `("thunk", root)` and is replaced in place by each priced action.
    `atp` is the *remaining* reservoir and `spent` what this agent has burned;
    `atp + spent` is what it has ever held, and the sum of that over a population
    plus the commons pool is invariant (see `Economy`).
    """
    __slots__ = ("aid", "root", "term", "atp", "spent", "status", "lineage",
                 "born", "s0", "stats", "peak")

    def __init__(self, aid, root, atp, lineage=(), born=0):
        self.aid = aid
        self.root = root
        self.term = ("thunk", root)
        self.atp = atp
        self.spent = 0
        self.status = LIVE
        self.lineage = tuple(lineage)
        self.born = born
        self.s0 = 1                    # a root thunk is size 1 (hash-leaf model)
        self.stats = {"fetches": 0}    # per LIFETIME, not per slice — see reduce_slice
        self.peak = 1

    @property
    def size(self):
        return sg.size(self.term)

    @property
    def hash(self):
        return sg.term_hash(self.term)

    def bound_holds(self):
        """The per-agent memory bound, in the form resumption leaves it in."""
        return self.size <= self.s0 + self.spent

    def __repr__(self):
        return (f"<Agent {self.aid} {self.status} size={self.size} "
                f"atp={self.atp} spent={self.spent}>")


# ---------- The driver: Book I's priced action, our loop ----------
def reduce_slice(agent, store, slice_atp, limits=None, probe=False, memo=None):
    """Spend up to `min(slice_atp, agent.atp)` on this agent and return what was
    spent. Sets `agent.status`; leaves `agent.term` at the stopping point.

    Mirrors `sigma_glyph.eval_hash`'s loop action for action — the 256-step
    in-flight fence, the normal-form fence, the recursion-limit handling — and
    differs in exactly one place: an unaffordable action leaves the term alone
    and reports STARVED instead of returning DISSONANCE(ATP Exhausted).

    Two smaller differences, both deliberate and both stated because a fence
    that quietly means something else is worse than no fence: `max_store_fetches`
    is counted over the agent's LIFETIME (a lazy resumable agent would otherwise
    reset the fence on every slice), and a slice boundary is not an outcome — if
    the slice ends with reservoir left, the agent stays LIVE.

    `probe=True` asserts the memory bound after every action, which is this
    repository's live-trace half of the Population.lean argument. It is O(size)
    per action; the experiments turn it on, the population loop does not.

    `memo` is an optional `Memo`. When the machine's next action is a force of a
    hash whose normal form is known, the normal form is installed instead, priced
    by `memo.price`. A hit that the remaining budget cannot afford is SKIPPED
    rather than fatal — the plain force costs at most 4, so an agent is never
    starved by the existence of a shortcut it could not buy.
    """
    limits = limits or sg.DEFAULT_LIMITS
    if agent.status not in RUNNABLE:
        return 0
    budget = min(slice_atp, agent.atp)
    spent = 0
    steps = 0
    old_rl = sys.getrecursionlimit()
    sys.setrecursionlimit(max(old_rl, 3 * limits["max_node_depth"] + 2000))

    def _settle(status):
        agent.atp -= spent
        agent.spent += spent
        agent.status = status
        agent.peak = max(agent.peak, sg.size(agent.term))
        return spent

    try:
        while True:
            steps += 1
            if steps % 256 == 0:
                sg.resource_check(agent.term, limits)
            if memo is not None:
                act = _next_action(agent.term)
                if act is not None and act[0] == "force":
                    entry = memo.lookup(act[1])
                    if entry is None:
                        memo.misses += 1
                    else:
                        nf, first_spent = entry
                        cost = memo.price(nf)
                        if cost <= budget - spent:
                            agent.term = _replace_at(agent.term, act[2], nf)
                            spent += cost
                            memo.hits += 1
                            memo.paid += cost
                            memo.avoided += max(0, first_spent - cost)
                            if probe:
                                assert sg.size(agent.term) <= agent.s0 + agent.spent + spent, (
                                    f"MEMORY BOUND VIOLATED by a memo hit: agent "
                                    f"{agent.aid} size {sg.size(agent.term)} > s0 "
                                    f"{agent.s0} + spent {agent.spent + spent}")
                                agent.peak = max(agent.peak, sg.size(agent.term))
                            continue
            try:
                r = sg.step5(agent.term, budget - spent, store, agent.stats, limits)
            except sg.BudgetExhausted:
                # Either the slice ended or the reservoir did. Only the second is
                # an outcome; the first is this module's own bookkeeping and must
                # not be visible to the agent as starvation. When the whole
                # reservoir was on the table the two coincide; otherwise ask the
                # oracle the counterfactual — would the FULL reservoir have
                # afforded this action? — on a throwaway `stats` so the probe
                # does not spend the agent's fetch fence. `step5` reads the store
                # and returns a new term; it mutates nothing else, which is what
                # makes the counterfactual free to ask.
                if budget >= agent.atp:
                    return _settle(STARVED)
                try:
                    sg.step5(agent.term, agent.atp - spent, store,
                             dict(agent.stats), limits)
                except sg.BudgetExhausted:
                    return _settle(STARVED)
                except (sg.Unresolved, sg.ResourceFault):
                    pass          # not this slice's outcome to report
                return _settle(LIVE)
            except sg.Unresolved:
                return _settle(UNRESOLVED)
            if r is None:
                sg.resource_check(agent.term, limits)
                return _settle(NORMAL)
            agent.term, cost = r[0], r[1]
            spent += cost
            if probe:
                assert sg.size(agent.term) <= agent.s0 + agent.spent + spent, (
                    f"MEMORY BOUND VIOLATED: agent {agent.aid} size "
                    f"{sg.size(agent.term)} > s0 {agent.s0} + spent "
                    f"{agent.spent + spent}")
                agent.peak = max(agent.peak, sg.size(agent.term))
    except sg.ResourceFault:
        return _settle(FAULT)
    finally:
        sys.setrecursionlimit(old_rl)


def outcome_hash(agent):
    """The agent's state as Book I would have reported it from a single
    `eval_hash` call — the mapping the differential test is written against."""
    if agent.status == STARVED:
        return sg.term_hash(("dis", sg.R_ATP))
    if agent.status == UNRESOLVED:
        return sg.term_hash(("dis", sg.R_UNRES))
    return agent.hash


# ---------- Memoization: what it costs to make sharing pay ----------
# Book I charges every agent for every materialization, so two agents holding the
# same subterm pay for it twice: sharing is a MEMORY phenomenon there and never an
# energy one. That is why ALIFE-EXP-001 found no gradient toward sharing and why
# the founding proposal had to invent a rebate to manufacture one.
#
# A content-addressed store can do better without inventing anything: one hash has
# exactly one normal form (Book I determinism), so a normal form written back into
# the store is a FUNCTION, not a cache heuristic. What it may cost is not a free
# choice either — see `Memo.derived_price`.
#
# THIS IS NOT BOOK I. A memoizing evaluator returns a different `atp_spent` for the
# same (hash, budget) than the reference oracle does, so it would fail Book I
# conformance, which pins spend exactly. That collision is the subject of the need
# packet in needs/; nothing here proposes a change to Book I.


def _next_action(t, path=()):
    """Mirror of `step5`'s dispatch: which action the machine will take next.

    Returns `("force", hash, path)` when the next action materializes a thunk,
    `("rule", None, ())` when it fires I/K/S or unwraps a REF, or None at a normal
    form. It exists so a memo hit lands exactly where the machine actually
    DEMANDED the hash — installing a normal form anywhere else would still be
    sound (confluence), but it would buy structure the run never asked for and the
    ATP figures would stop meaning what they say.

    Held to `step5` by control M1 in `tests/alife_memo.py`, in the direction that
    matters: every predicted force is a real force. The other direction is left
    unchecked and stated — a mirror that missed a force would make the memo too
    timid, never too greedy.
    """
    k = t[0]
    if k == "thunk":
        return None if t[1] in sg.GENESIS else ("force", t[1], path)
    if k == "ref":
        return ("rule", None, ())
    if k != "app":
        return None
    f, a = t[1], t[2]
    if sg.glyph_eq(f, sg.I_H):                                   # R-I
        return ("rule", None, ())
    if f[0] == "app":
        if sg.glyph_eq(f[1], sg.K_H):                            # R-K
            return ("rule", None, ())
        if f[1][0] == "app" and sg.glyph_eq(f[1][1], sg.S_H):    # R-S
            return ("rule", None, ())
    left = _next_action(f, path + (1,))
    return left if left is not None else _next_action(a, path + (2,))


def _replace_at(t, path, node):
    if not path:
        return node
    if path[0] == 1:
        return ("app", _replace_at(t[1], path[1:], node), t[2])
    return ("app", t[1], _replace_at(t[2], path[1:], node))


class Memo:
    """NodeHash -> its normal form, with the price of installing one.

    THE PRICE IS FORCED, not chosen. Book I's §3.4 invariant rests on one
    per-action premise: an action grows the term by at most `cost - 1`. Installing
    a normal form of size k in place of a thunk of size 1 grows the term by k - 1,
    so any price below k breaks the premise and with it `size <= spent + 1` — and
    a price of exactly k makes the inequality TIGHT, which no other action in the
    machine does. `Memo(price=lambda nf: 1)` is therefore not a cheaper policy, it
    is an unsound one, and ALIFE-EXP-002 runs it as a control to watch the bound
    break rather than asserting that it would.

    What memoization buys is the WORK, not the space: an agent skips every action
    inside the reduction and still prepays the size of what it receives. In a
    size-priced machine, memoization can refund time and never space.
    """

    @staticmethod
    def derived_price(nf):
        return sg.size(nf)

    def __init__(self, price=None):
        self.nf = {}
        self.price = price or Memo.derived_price
        self.hits = 0
        self.misses = 0
        self.paid = 0            # ATP spent on hits
        self.avoided = 0         # ATP the same work cost the first time round

    def learn(self, root, term, spent):
        """Record a normal form. Only ever called with a run that REACHED one:
        a starved or unresolved agent knows nothing about the normal form of its
        root. A hash whose normal form is itself (a bare genesis thunk) is not
        recorded — it saves nothing and installing it would spin."""
        if term == ("thunk", root) or root in self.nf:
            return
        self.nf[root] = (term, spent)

    def lookup(self, h):
        entry = self.nf.get(h)
        return entry if entry else None


# ---------- CAS traffic ----------
def put_term(t, store):
    """Write every materialized node of `t` into the store and return its hash.
    Thunks are already addresses and are written by whoever materialized them.
    This is what makes the population DAG *shared*: two agents that reduce to
    structurally equal subterms land on one entry, by construction rather than
    by a de-duplication pass."""
    if t[0] == "thunk":
        return t[1]
    if t[0] == "app":
        put_term(t[1], store)
        put_term(t[2], store)
    return store.put(sg.term_bytes(t))


def node_census(t, counter=None):
    """Return (hash, counter) where `counter` maps NodeHash -> occurrences over
    the whole term, thunks included: a thunk IS the address of the node it
    stands for, so an unforced child and the materialized node it points at are
    the same CAS address and must not be counted as two.

    Bottom-up, so the whole census costs O(size) hashes rather than the O(size²)
    a naive `term_hash` per subterm would."""
    counter = Counter() if counter is None else counter
    if t[0] == "thunk":
        counter[t[1]] += 1
        return t[1], counter
    if t[0] == "app":
        lh, _ = node_census(t[1], counter)
        rh, _ = node_census(t[2], counter)
        h = sg.node_hash(sg.ser(sg.APPLY, sg.F_LEFT | sg.F_RIGHT, left=lh, right=rh))
    elif t[0] == "ref":
        # A materialized REF is TWO addresses, exactly as the hash-leaf size
        # model prices it (`size` counts 2: the node and the target thunk). The
        # target is a genuine CAS address that other agents can share, so
        # counting only the node would both understate sharing and put this
        # census permanently one node below `size` per REF — which is how this
        # line came to be written: `tests/alife_conservation.py` P5 caught the
        # first version claiming the two agreed "by construction" when they did
        # not.
        counter[t[1]] += 1
        h = sg.node_hash(sg.term_bytes(t))
    else:
        h = sg.node_hash(sg.term_bytes(t))
    counter[h] += 1
    return h, counter


def population_census(agents):
    """Occurrence counter over every agent's term. Total = Σ size, because the
    census counts one entry per node occurrence and `size` counts one per node
    (a materialized REF counts 2 in the size model — node plus target thunk —
    and 2 here too). The agreement is a CHECKED property, not an assumed one:
    `tests/alife_conservation.py` P5 asserts it on every tick of every run."""
    counter = Counter()
    for a in agents:
        node_census(a.term, counter)
    return counter


# ---------- Metrics ----------
def sharing_factor(agents):
    """Σ node occurrences / distinct CAS addresses. 1.0 means nothing is shared;
    N means the population is N copies of one structure. This is a property of
    the term multiset alone — no store, no order, no policy — which is why it is
    the metric the experiments are preregistered against."""
    c = population_census(agents)
    unique = len(c)
    total = sum(c.values())
    return (total / unique) if unique else 0.0, total, unique


def atp_efficiency(agents):
    """Normal forms per ATP burned. Zero spend is reported as None, not as
    infinity or as zero: nothing was purchased, so there is no rate."""
    spent = sum(a.spent for a in agents)
    if spent == 0:
        return None
    return sum(1 for a in agents if a.status == NORMAL) / spent


def shape(t, depth=3):
    """Structure of the top `depth` levels, atoms erased. Two agents with the
    same shape may hold entirely different terms; this is a coarse descriptor
    for the diversity metric and nothing else."""
    if t[0] != "app":
        return {"thunk": "h", "lit": "l", "ref": "r", "dis": "x"}[t[0]]
    if depth <= 0:
        return "*"
    return "(" + shape(t[1], depth - 1) + shape(t[2], depth - 1) + ")"


def structural_diversity(agents, depth=3):
    """Shannon entropy (bits) over term shapes. 0 = every agent looks alike."""
    if not agents:
        return 0.0
    c = Counter(shape(a.term, depth) for a in agents)
    n = sum(c.values())
    return -sum((k / n) * math.log2(k / n) for k in c.values())


def resilience(agents):
    """Fraction of a population that is still runnable — LIVE or STARVED but
    holding a term. An archived or faulted agent is not resilient; a settled one
    is not at risk, so it counts as survived."""
    if not agents:
        return 0.0
    alive = sum(1 for a in agents if a.status in (LIVE, STARVED, NORMAL))
    return alive / len(agents)


# ---------- Economy ----------
class Economy:
    """ATP bookkeeping with an explicit commons pool.

    Rebates in the original proposal were minted: an agent that shared structure
    was to be *granted* ATP. Minting breaks conservation, and with it every bound
    that is stated against a total. Here every grant comes out of `pool` and
    every tax goes back into it, so

        pool + Σ agent.atp + Σ agent.spent  =  endowment

    holds at every step and is asserted, not assumed (`check`)."""

    def __init__(self, pool):
        self.pool = pool
        self.endowment = pool

    def endow(self, agent, amount):
        """Move `amount` from the pool into a new agent's reservoir."""
        return self.grant(agent, amount)

    def grant(self, agent, amount):
        amount = max(0, min(amount, self.pool))
        self.pool -= amount
        agent.atp += amount
        return amount

    def collect(self, agent, amount):
        amount = max(0, min(amount, agent.atp))
        agent.atp -= amount
        self.pool += amount
        return amount

    def check(self, agents):
        held = sum(a.atp + a.spent for a in agents)
        return self.pool + held == self.endowment


def conservative_transfer(donor, recipient, amount):
    """Move ATP between two agents, never below the donor's reserve.

    Reserve = `size(donor.term) + 1`. HEURISTIC, and named as one: it is *not*
    what keeps the population bound true. The population bound (Population.lean,
    `population_peak_size`) depends only on the TOTAL, so any transfer that
    conserves ATP preserves it — a donor may give everything away and no memory
    bound is threatened. What the reserve buys is per-agent predictability: an
    agent that keeps `size + 1` can still afford to be looked at, and a rule that
    lets donors strip themselves to zero makes starvation an artifact of the
    matching order rather than of the economy. Returns the amount moved."""
    reserve = sg.size(donor.term) + 1
    give = max(0, min(amount, donor.atp - reserve))
    donor.atp -= give
    recipient.atp += give
    return give


# ---------- Reproduction (policy; Phase 3 surface) ----------
def crossover(parent_a, parent_b, store, rng):
    """Splice a subterm of B into A at a randomly chosen node of A.

    Content addressing does the work: the graft is a *hash*, so the child shares
    the donated structure with its parent rather than copying it. Returns the
    child's root hash, or None when A has no graftable node (a leaf).

    Mutation and selection are NOT modelled here; this is the operator, not an
    evolutionary algorithm, and nothing below claims the operator is a good one.
    """
    positions = []

    def walk(t, path):
        if t[0] == "app":
            positions.append(path)
            walk(t[1], path + (1,))
            walk(t[2], path + (2,))

    walk(parent_a.term, ())
    if not positions:
        return None
    path = positions[rng.randrange(len(positions))]
    graft = ("thunk", sg.term_hash(parent_b.term))
    put_term(parent_b.term, store)

    def rebuild(t, path):
        if not path:
            return graft
        if path[0] == 1:
            return ("app", rebuild(t[1], path[1:]), t[2])
        return ("app", t[1], rebuild(t[2], path[1:]))

    child = rebuild(parent_a.term, path)
    return put_term(child, store)


# ---------- Population ----------
class Population:
    """One tick = reduce, share, interact, cull. Deterministic given the seed:
    every phase that could depend on iteration order sorts by agent id first."""

    def __init__(self, store, agents, economy, rng, slice_atp=64,
                 rebate_rate=0.0, transfers=False, probe=False, memo=None):
        self.store = store
        self.agents = list(agents)
        self.economy = economy
        self.rng = rng
        self.slice_atp = slice_atp
        self.rebate_rate = rebate_rate
        self.transfers = transfers
        self.probe = probe
        self.memo = memo
        self.tick = 0
        self.history = []
        self.archived = []

    # -- phase 1
    def phase_reduce(self):
        """One slice per runnable agent, with escalation.

        A slice smaller than the next action's cost buys nothing — the agent
        comes back LIVE having spent zero, and a fixed slice would livelock the
        population in silence. So a slice that bought nothing is doubled, up to
        the agent's whole reservoir, until it either buys an action or the
        reservoir itself proves too small (STARVED). The slice is therefore a
        FLOOR on what an agent may attempt in a tick, not a cap on what it may
        spend: one R-S over a large argument costs `1 + size(z)` and no smaller
        number can be charged for it.
        """
        spent = 0
        for a in sorted(self.agents, key=lambda x: x.aid):
            if a.status not in RUNNABLE:
                continue
            budget = self.slice_atp
            while True:
                got = reduce_slice(a, self.store, budget, probe=self.probe,
                                   memo=self.memo)
                spent += got
                if got or a.status != LIVE:
                    break
                budget = min(a.atp, max(1, budget * 2))
            if self.memo is not None and a.status == NORMAL:
                # Only a run that REACHED a normal form knows one. A starved or
                # unresolved agent has an opinion about its own root and no more.
                self.memo.learn(a.root, a.term, a.spent)
        for a in self.agents:
            put_term(a.term, self.store)
        return spent

    # -- phase 2
    def phase_share(self):
        """Rebate agents in proportion to the structure they hold in common with
        somebody else, out of the commons pool. `rebate_rate = 0` disables it,
        which is the default and what the ALIFE-EXP-001 baseline runs: a rebate
        is a selection pressure, and switching it on while measuring what
        structure does on its own would measure the pressure instead."""
        if self.rebate_rate <= 0 or self.economy.pool <= 0:
            return 0
        census = population_census(self.agents)
        shared = {h for h, n in census.items() if n > 1}
        granted = 0
        for a in sorted(self.agents, key=lambda x: x.aid):
            if a.status not in RUNNABLE:
                continue
            _, own = node_census(a.term)
            overlap = sum(n for h, n in own.items() if h in shared)
            granted += self.economy.grant(a, int(self.rebate_rate * overlap))
        return granted

    # -- phase 3
    def phase_interact(self):
        """Pair the richest runnable agents with the poorest and let the
        conservative rule decide what actually moves."""
        if not self.transfers:
            return 0
        runnable = [a for a in self.agents if a.status in RUNNABLE]
        if len(runnable) < 2:
            return 0
        runnable.sort(key=lambda a: (a.atp, a.aid))
        moved = 0
        lo, hi = 0, len(runnable) - 1
        while lo < hi:
            need = max(0, self.slice_atp - runnable[lo].atp)
            moved += conservative_transfer(runnable[hi], runnable[lo], need)
            lo += 1
            hi -= 1
        return moved

    # -- phase 4
    def phase_cull(self):
        """A starved agent is archived, not deleted: its term stays in the CAS
        and its lineage stays in `archived`, so a population's history remains
        reconstructible from the store it ran on."""
        culled = 0
        for a in self.agents:
            if a.status == STARVED:
                # Residual dust — a reservoir too small to afford the agent's
                # next action — returns to the commons rather than vanishing
                # with the body. Deleting it would break conservation quietly,
                # which is the failure mode the whole ledger exists to catch.
                self.economy.collect(a, a.atp)
                a.status = ARCHIVED
                self.archived.append(a)
                culled += 1
        return culled

    def metrics(self):
        factor, total, unique = sharing_factor(self.agents)
        return {
            "tick": self.tick,
            "agents": len(self.agents),
            "live": sum(1 for a in self.agents if a.status == LIVE),
            "normal": sum(1 for a in self.agents if a.status == NORMAL),
            "starved": sum(1 for a in self.agents if a.status == STARVED),
            "archived": sum(1 for a in self.agents if a.status == ARCHIVED),
            "unresolved": sum(1 for a in self.agents if a.status == UNRESOLVED),
            "fault": sum(1 for a in self.agents if a.status == FAULT),
            "sharing_factor": factor,
            "nodes_total": total,
            "nodes_unique": unique,
            "atp_spent": sum(a.spent for a in self.agents),
            "atp_held": sum(a.atp for a in self.agents),
            "atp_pool": self.economy.pool,
            "atp_efficiency": atp_efficiency(self.agents),
            "diversity_bits": structural_diversity(self.agents),
            "resilience": resilience(self.agents),
            "peak_sum": sum(a.peak for a in self.agents),
        }

    def step(self, cull=True):
        self.phase_reduce()
        self.phase_share()
        self.phase_interact()
        if cull:
            self.phase_cull()
        self.tick += 1
        assert self.economy.check(self.agents), "ATP CONSERVATION VIOLATED"
        assert self.population_bound_holds(), "POPULATION MEMORY BOUND VIOLATED"
        m = self.metrics()
        self.history.append(m)
        return m

    def population_bound_holds(self):
        """Σ size <= Σ s0 + Σ spent — the sum form of the per-agent bound, and
        the statement `proofs/Population.lean` proves from the Book I premise."""
        return (sum(a.size for a in self.agents)
                <= sum(a.s0 for a in self.agents)
                + sum(a.spent for a in self.agents))


def provenance():
    """What produced a number here. Goes into every receipt this repo writes."""
    return {
        "sigma_alife_version": __version__,
        "sigma_glyph_requirement": SIGMA_GLYPH_REQ,
        "oracle_source": ORACLE_SOURCE,
        "oracle_sha256": ORACLE_DIGEST,
        "python": sys.version.split()[0],
    }


# ---------- Self-test ----------
def run_tests():  # NOSONAR python:S3776
    """Linear self-test; each assertion stays visible in execution order."""
    import random as _random

    ok = []

    def chk(name, cond):
        ok.append(bool(cond))
        print(("OK  " if cond else "FAIL"), name)

    A = lambda l, r: ("app", l, r)
    IG, KG, SG_ = ("lit", sg.sha(b"I")), ("lit", sg.sha(b"K")), ("lit", sg.sha(b"S"))

    store = sg.Store()
    for b in (sg.I_BYTES, sg.K_BYTES, sg.S_BYTES):
        store.put(b)

    def put_tree(t):
        return put_term(t, store)

    chk("oracle loaded and pinned by digest", len(ORACLE_DIGEST) == 64)

    # --- the driver run whole must be the oracle
    ik = put_tree(A(IG, KG))
    skki = put_tree(A(A(A(SG_, KG), KG), IG))
    for root, budget in ((ik, 4), (ik, 3), (ik, 0), (skki, 100), (skki, 11), (skki, 12)):
        a = Agent("d", root, budget)
        reduce_slice(a, store, budget)
        r, spent = sg.eval_hash(root, budget, store)
        chk(f"driver == eval_hash (budget {budget}, root {root.hex()[:6]})",
            outcome_hash(a) == sg.term_hash(r) and a.spent == spent)

    # --- slicing changes nothing but the number of calls
    whole = Agent("w", skki, 100)
    reduce_slice(whole, store, 100)
    stalled = Agent("stall", skki, 100)
    reduce_slice(stalled, store, 1)
    chk("a slice too small for one action buys nothing and says LIVE, not STARVED",
        stalled.status == LIVE and stalled.spent == 0 and stalled.atp == 100)
    sliced = Agent("s", skki, 100)
    slice_atp, stalls = 1, 0
    while sliced.status == LIVE:
        got = reduce_slice(sliced, store, slice_atp)
        if got == 0 and sliced.status == LIVE:      # escalate, as Population does
            stalls += 1
            slice_atp = min(sliced.atp, slice_atp * 2)
    chk("sliced to the smallest affordable action, the run is the whole run",
        sliced.status == NORMAL and whole.status == NORMAL and stalls > 0
        and sliced.hash == whole.hash and sliced.spent == whole.spent)

    # --- the bound survives resumption
    probed = Agent("p", skki, 100)
    while probed.status == LIVE:
        reduce_slice(probed, store, 2, probe=True)
    chk("memory bound holds at every action across slices", probed.bound_holds())

    # --- sporulation: starve, then feed, and land where an unstarved run lands
    spore = Agent("spore", skki, 5)
    reduce_slice(spore, store, 5)
    chk("starvation keeps the term (not DISSONANCE) and reports STARVED",
        spore.status == STARVED and spore.term[0] != "dis")
    dormant_hash, dust, before = spore.hash, spore.atp, spore.spent
    reduce_slice(spore, store, dust)
    chk("residual dust buys nothing: starved means the NEXT action is unaffordable",
        spore.spent == before and spore.status == STARVED and dust < 3)
    spore.atp += 100 - spore.spent - dust
    spore.status = LIVE
    reduce_slice(spore, store, 100)
    chk("dormant agent resumes to the unstarved normal form",
        spore.status == NORMAL and spore.hash == whole.hash
        and spore.spent == whole.spent)
    chk("dormancy preserved a term, not a placeholder",
        dormant_hash != sg.term_hash(("dis", sg.R_ATP)))

    # --- an unresolved reference is an outcome, not a crash
    ghost = sg.sha(b"ghost-node-that-is-not-in-any-store")
    gh = put_tree(A(IG, ("ref", ghost)))
    g = Agent("g", gh, 100)
    reduce_slice(g, store, 100)
    r, spent = sg.eval_hash(gh, 100, store)
    chk("unresolved: driver == eval_hash",
        outcome_hash(g) == sg.term_hash(r) and g.spent == spent
        and g.status == UNRESOLVED)

    # --- census / sharing
    _, c1 = node_census(A(IG, KG))
    chk("census counts every node occurrence (I·K = 3)", sum(c1.values()) == 3)
    twins = [Agent(f"t{i}", ik, 0) for i in range(4)]
    factor, total, unique = sharing_factor(twins)
    chk("four identical root thunks share one address", (factor, total, unique) == (4.0, 4, 1))
    for t in twins:
        reduce_slice(t, store, 3)          # force the root: same action, same bytes
    factor, total, unique = sharing_factor(twins)
    chk("four identical materialized terms still share every address",
        factor == 4.0 and unique * 4 == total)
    mixed = [Agent("a", ik, 0), Agent("b", skki, 0)]
    factor, _, _ = sharing_factor(mixed)
    chk("two different root thunks share nothing", factor == 1.0)

    # --- economy
    econ = Economy(1000)
    pop_agents = [Agent(f"e{i}", skki, 0) for i in range(4)]
    for a in pop_agents:
        econ.endow(a, 50)
    chk("endowment moves ATP, it does not mint it",
        econ.pool == 800 and econ.check(pop_agents))
    pop = Population(store, pop_agents, econ, _random.Random(20260825),
                     slice_atp=8, rebate_rate=0.5, transfers=True)
    for _ in range(6):
        m = pop.step()
    chk("conservation holds after six ticks with rebates and transfers",
        econ.check(pop.agents))
    chk("population bound holds after six ticks", pop.population_bound_holds())
    chk("population settled inside its endowment",
        m["normal"] == 4 and m["atp_spent"] <= 1000)

    # --- transfers respect the reserve
    rich, poor = Agent("rich", skki, 100), Agent("poor", skki, 0)
    reduce_slice(rich, store, 6)
    moved = conservative_transfer(rich, poor, 10_000)
    chk("a donor never goes below size + 1", rich.atp >= rich.size + 1 and moved > 0)
    broke = Agent("broke", skki, 1)
    chk("a donor with nothing to spare gives nothing",
        conservative_transfer(broke, poor, 10) == 0)

    # --- crossover grafts by hash
    pa, pb = Agent("pa", skki, 100), Agent("pb", ik, 100)
    reduce_slice(pa, store, 6)
    reduce_slice(pb, store, 3)
    child_root = crossover(pa, pb, store, _random.Random(7))
    chk("crossover writes a resolvable child into the store",
        child_root is not None and store.get(child_root) is not None)
    child = Agent("child", child_root, 200, lineage=("pa", "pb"))
    reduce_slice(child, store, 200)
    chk("the child is a term the oracle can evaluate",
        child.status in (NORMAL, STARVED, UNRESOLVED)
        and outcome_hash(child) == sg.term_hash(sg.eval_hash(child_root, 200, store)[0]))

    # --- metrics that must not lie about an empty measurement
    chk("no spend means no efficiency rate, not zero",
        atp_efficiency([Agent("z", ik, 10)]) is None)
    chk("identical agents have zero diversity",
        structural_diversity(twins) == 0.0)

    passed = all(ok)
    print(f"\nALIFE: {'ALL PASS' if passed else 'FAILURES PRESENT'} "
          f"({sum(ok)}/{len(ok)})")
    print(f"oracle: {ORACLE_SOURCE}")
    print(f"oracle sha256: {ORACLE_DIGEST}")
    return passed


if __name__ == "__main__":
    sys.exit(0 if run_tests() else 1)
