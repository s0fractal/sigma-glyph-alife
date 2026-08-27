#!/usr/bin/env python3
"""A starving agent that is fed gets to run — the property ALIFE-EXP-011 measured
the absence of.

ChatGPT's review of `006b9bb` found that `phase_share` and `phase_interact` can
put ATP in a `STARVED` agent's reservoir, neither of them changes its status, and
`phase_cull` — later in the same tick — collects the ATP and archives the body.
ALIFE-EXP-011 measured what that cost on the reviewed engine: 0 of 168 fed agents
ever ran again, and 1056 of 1056 granted ATP was buried the same tick.

The randomized conservation suite could not see it. It checks the ledger, the
bound, the dust and determinism; "a refed starving agent gets to run" is none of
those, and every experiment in the repository that measured resumption ran with
`cull=False`, so seven receipts sat on top of this path without touching it.

  R1  the review's script, literally: starve, transfer enough, step(cull=True),
      and the agent is not archived and has made progress.
  R2  the SAME TICK version, which is the actual bug: the agent starves inside
      `phase_reduce`, is fed by `phase_interact` in that tick, and meets
      `phase_cull` before it has ever run on the new ATP.
  R3  R2 through the rebate path instead of the transfer path.
  R4  the cull still culls: an agent that genuinely cannot afford its next action
      is still archived, and its dust still returns to the commons.
  R5  the rebate pays for structure held in common with SOMEBODY ELSE, not for an
      agent repeating a subterm inside itself.

R2, R3 and R5 each carry a negative control that puts the engine back on the
pre-2026-08-27 policy and demands the property FAIL. A regression test nobody has
watched go red is a regression test nobody has watched.

Usage:  python3 tests/alife_refeed.py
"""
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import terms as corpus  # noqa: E402

al = corpus.al
sg = corpus.sg

SEED = 20260827


def fresh_store():
    st = sg.Store()
    for b in (sg.I_BYTES, sg.K_BYTES, sg.S_BYTES):
        st.put(b)
    return st


def colony(seed, n, poor_atp, rich_atp, pool, **popkw):
    """One agent deliberately too poor to finish, the rest rich enough to feed
    it, and a commons with something in it."""
    rng = random.Random(seed)
    store = fresh_store()
    roots = corpus.install(corpus.generate(rng, n), store)
    econ = al.Economy(pool + poor_atp + rich_atp * (n - 1))
    agents = []
    for i, root in enumerate(roots):
        a = al.Agent(f"a{i:03d}", root, 0)
        econ.endow(a, poor_atp if i == 0 else rich_atp)
        agents.append(a)
    pop = al.Population(store, agents, econ, random.Random(seed), **popkw)
    return pop, agents[0]


def next_price(agent, store):
    try:
        r = sg.step5(agent.term, 10 ** 9, store, dict(agent.stats),
                     sg.DEFAULT_LIMITS)
    except (sg.BudgetExhausted, sg.Unresolved, sg.ResourceFault):
        return None
    return None if r is None else r[1]


def sharing_colony(seed, poor_atp, rich_atp, pool, **popkw):
    """Six agents over ONE shared argument: `S x_i y_i z` with the same `z` for
    everybody. R-S copies `z`, so an agent that gets far enough materializes
    structure its neighbours also hold — which is the only condition under which
    the rebate has anything to pay for. A colony of unrelated random terms shares
    nothing after reduction and the rebate correctly grants nothing, which is a
    fact about the corpus and not about the schedule."""
    rng = random.Random(seed)
    store = fresh_store()
    z = corpus.ski(rng, 3)
    terms = [("app", ("app", ("app", corpus.SG, corpus.ski(rng, 2)),
                      corpus.ski(rng, 2)), z) for _ in range(6)]
    roots = corpus.install(terms, store)
    econ = al.Economy(pool + poor_atp + rich_atp * (len(roots) - 1))
    agents = []
    for i, root in enumerate(roots):
        a = al.Agent(f"s{i:03d}", root, 0)
        econ.endow(a, poor_atp if i == 0 else rich_atp)
        agents.append(a)
    return al.Population(store, agents, econ, random.Random(seed), **popkw), agents[0]


def find_rebate_fixture(recheck):
    """A (seed, budget) at which agent 0 starves in tick 0 AND the rebate then
    feeds it more than its next action costs. Searched, so the fixture cannot
    quietly stop being one — an R3 that passed because nothing was ever fed
    would be the ALIFE-EXP-002 defect in a test."""
    for seed in range(SEED, SEED + 12):
        for poor in (3, 6, 10, 16, 24, 32, 48, 64, 96):
            pop, a = sharing_colony(seed, poor, 4000, 4000, slice_atp=32,
                                    rebate_rate=2.0,
                                    recheck_affordability_before_cull=recheck)
            pop.phase_reduce()
            if a.status != al.STARVED:
                continue
            price = next_price(a, pop.store)
            if price is None:
                continue
            before = a.atp
            pop.phase_share()
            if a.atp - before > price:
                return seed, poor
    return None, None


def rebate_tick(seed, poor, recheck):
    """One tick: agent 0 starves in `phase_reduce`, the rebate feeds it in
    `phase_share`, and `phase_cull` gets its turn."""
    pop, a = sharing_colony(seed, poor, 4000, 4000, slice_atp=32,
                            rebate_rate=2.0,
                            recheck_affordability_before_cull=recheck)
    pop.phase_reduce()
    assert a.status == al.STARVED, "fixture: agent 0 did not starve"
    before = a.atp
    price = next_price(a, pop.store)
    pop.phase_share()
    fed = a.atp - before
    pop.phase_cull()
    pop.tick += 1
    return pop, a, fed, price


def find_starver(recheck, transfers=False, rebate=0.0):
    """A seed where agent 0 really does end `phase_reduce` of tick 0 starving.
    Searched rather than asserted, so the fixture cannot quietly stop being one."""
    for seed in range(SEED, SEED + 40):
        pop, a = colony(seed, 6, 3, 4000, 4000, slice_atp=32,
                        transfers=transfers, rebate_rate=rebate,
                        recheck_affordability_before_cull=recheck)
        pop.phase_reduce()
        if a.status == al.STARVED and next_price(a, pop.store) is not None:
            return seed
    return None


def same_tick(seed, recheck, transfers=False, rebate=0.0):
    """One tick of the default schedule, on a colony whose agent 0 starves in it.
    Returns (agent, granted-in-that-tick, population)."""
    pop, a = colony(seed, 6, 3, 4000, 4000, slice_atp=32,
                    transfers=transfers, rebate_rate=rebate,
                    recheck_affordability_before_cull=recheck)
    pop.phase_reduce()
    assert a.status == al.STARVED, "fixture: agent 0 did not starve"
    before = a.atp
    price = next_price(a, pop.store)
    granted = pop.phase_share() if rebate else 0
    moved = pop.phase_interact() if transfers else 0
    fed = a.atp - before
    pop.phase_cull()
    pop.tick += 1
    return pop, a, fed, price, granted + moved


def main():  # NOSONAR python:S3776
    ok = []

    def chk(name, cond):
        ok.append((name, bool(cond)))

    # ---- R1: the review's script, literally --------------------------------
    seed = find_starver(recheck=True)
    chk("fixture: a seed exists where agent 0 starves in tick 0",
        seed is not None)
    pop, a = colony(seed, 6, 3, 4000, 4000, slice_atp=32,
                    transfers=False, rebate_rate=0.0)
    pop.phase_reduce()
    price = next_price(a, pop.store)
    donor = max((x for x in pop.agents if x is not a), key=lambda x: x.atp)
    # "Enough for its next action" buys exactly one action, after which the agent
    # starves again on the NEXT one and the cull is right to take it — that case
    # is R4's, not this one. The script's intent is that food is not confiscated
    # before it can be used, so the transfer here is enough to carry the agent to
    # a normal form.
    moved = al.conservative_transfer(donor, a, 4000)
    spent_before = a.spent
    pop.step(cull=True)
    chk(f"R1 starve -> transfer {moved} ATP (next action costs {price}) -> "
        f"step(cull=True): the agent is not ARCHIVED (status {a.status})",
        a.status != al.ARCHIVED)
    chk(f"R1 ... and it made progress ({spent_before} -> {a.spent} spent)",
        a.spent > spent_before)

    # ---- R2: the same tick, transfer path ----------------------------------
    seed = find_starver(recheck=True, transfers=True)
    pop, a, fed, price, moved = same_tick(seed, recheck=True, transfers=True)
    chk(f"R2 fixture: the tick fed the starving agent {fed} ATP against a "
        f"next-action price of {price}", fed > price)
    chk(f"R2 fed inside the tick by phase_interact, the agent survives "
        f"phase_cull (status {a.status}, {pop.revived} revived)",
        a.status != al.ARCHIVED)
    spent_at_cull = a.spent
    pop.step(cull=True)
    chk(f"R2 ... and fires a priced action in the next tick "
        f"({spent_at_cull} -> {a.spent} spent)", a.spent > spent_at_cull)

    pop_b, a_b, fed_b, price_b, _ = same_tick(seed, recheck=False,
                                              transfers=True)
    chk(f"R2-control on the pre-2026-08-27 policy the same {fed_b} ATP is "
        f"granted and the agent is buried in the same tick "
        f"(status {a_b.status}, atp {a_b.atp})",
        a_b.status == al.ARCHIVED and a_b.atp == 0)

    # ---- R3: the same tick, rebate path ------------------------------------
    seed, poor = find_rebate_fixture(recheck=True)
    chk("R3 fixture: a colony exists where the rebate feeds a starving agent "
        f"more than its next action costs (seed {seed}, budget {poor})",
        seed is not None)
    pop, a, fed, price = rebate_tick(seed, poor, recheck=True)
    chk(f"R3 fixture: the rebate fed the starving agent {fed} ATP against a "
        f"next-action price of {price}", fed > price)
    chk(f"R3 fed inside the tick by phase_share, the agent survives phase_cull "
        f"(status {a.status})", a.status != al.ARCHIVED)
    spent_at_cull = a.spent
    pop.step(cull=True)
    chk(f"R3 ... and fires a priced action in the next tick "
        f"({spent_at_cull} -> {a.spent} spent)", a.spent > spent_at_cull)

    pop_b, a_b, fed_b, _ = rebate_tick(seed, poor, recheck=False)
    chk(f"R3-control on the pre-2026-08-27 policy the rebate's {fed_b} ATP is "
        f"collected by the cull in the same tick (status {a_b.status}, "
        f"atp {a_b.atp})", a_b.status == al.ARCHIVED and a_b.atp == 0)

    # ---- R4: the cull still culls -------------------------------------------
    pop, a = colony(SEED, 6, 3, 4000, 0, slice_atp=32,
                    transfers=False, rebate_rate=0.0)
    pop.phase_reduce()
    starving = [x for x in pop.agents if x.status == al.STARVED]
    pool_before = pop.economy.pool
    dust = sum(x.atp for x in starving)
    culled = pop.phase_cull()
    chk(f"R4 an agent that still cannot afford its next action is archived "
        f"({culled} of {len(starving)} starving)",
        starving and culled == len(starving)
        and all(x.status == al.ARCHIVED for x in starving))
    chk(f"R4 ... and its dust returns to the commons "
        f"({pool_before} + {dust} = {pop.economy.pool})",
        pop.economy.pool == pool_before + dust)
    chk("R4 ... and the archived term is still resolvable in the store",
        all(pop.store.get(sg.term_hash(x.term)) is not None
            or x.term[0] == "thunk" for x in starving))

    # ---- R5: the rebate is about somebody else ------------------------------
    def rebate_for(terms, basis):
        store = fresh_store()
        econ = al.Economy(10_000)
        agents = []
        for i, t in enumerate(terms):
            a_ = al.Agent(f"r{i}", al.put_term(t, store), 0)
            a_.term = t                      # materialized, as after a reduction
            econ.endow(a_, 1)
            agents.append(a_)
        pop_ = al.Population(store, agents, econ, random.Random(0),
                             rebate_rate=1.0, rebate_basis=basis)
        return pop_.phase_share()

    x = ("lit", sg.sha(b"exp011-x"))
    y = ("lit", sg.sha(b"exp011-y"))
    z = ("lit", sg.sha(b"exp011-z"))
    alone = [("app", x, x), ("app", y, z)]       # A holds x twice, nobody else
    together = [("app", x, y), ("app", x, z)]    # A and B each hold x once

    chk(f"R5 an agent repeating a subterm inside itself is not sharing: "
        f"rebate {rebate_for(alone, 'holders')}",
        rebate_for(alone, "holders") == 0)
    chk(f"R5 two agents holding one address between them are: "
        f"rebate {rebate_for(together, 'holders')}",
        rebate_for(together, "holders") > 0)
    chk(f"R5-control the pre-2026-08-27 occurrence statistic pays the lone "
        f"self-repeater {rebate_for(alone, 'occurrences')}",
        rebate_for(alone, "occurrences") > 0)

    prov = al.provenance()
    for name, passed in ok:
        print(("OK  " if passed else "FAIL"), name)
    print(f"oracle sha256: {prov['oracle_sha256']}")
    passed = all(p for _, p in ok)
    print(f"\nALIFE-REFEED: {'ALL PASS' if passed else 'FAILURES PRESENT'} "
          f"({sum(p for _, p in ok)}/{len(ok)})")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
