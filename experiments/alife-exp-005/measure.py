#!/usr/bin/env python3
"""Measure Book I's R-S address-sharing discount.

Check-only by default. ``--record`` writes ``results.json`` only after all seven
preregistered controls pass. Harness choices left open by the preregistration
were fixed in ``DECISIONS.md`` before this file was run.
"""
import argparse
import json
import math
import platform
import statistics
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "impl"))

import corpus as C  # noqa: E402
import sigma_alife as al  # noqa: E402

sg = al.sg


def fresh_store():
    store = sg.Store()
    for buf in (sg.I_BYTES, sg.K_BYTES, sg.S_BYTES):
        store.put(buf)
    return store


@dataclass(frozen=True)
class DeepValue:
    value: int
    saturated: bool = False


class DeepSizer:
    """Capped, hash-memoized tree expansion; occurrences remain multiplicative."""

    def __init__(self, store, cap=C.DEEP_SIZE_CAP):
        self.store = store
        self.cap = cap
        self.memo = {}
        self.visiting = set()

    def _sum(self, *parts):
        if any(p.saturated for p in parts):
            return DeepValue(self.cap, True)
        total = sum(p.value for p in parts)
        if total > self.cap:
            return DeepValue(self.cap, True)
        return DeepValue(total, False)

    def hash(self, node_hash):
        if node_hash in self.memo:
            return self.memo[node_hash]
        if node_hash in self.visiting:
            return DeepValue(self.cap, True)
        self.visiting.add(node_hash)
        try:
            buf = sg.GENESIS.get(node_hash)
            if buf is None:
                buf = self.store.get(node_hash)
            node = sg.deser(buf) if buf is not None else None
            if node is None or node["op"] in (sg.LITERAL, sg.DISSONANCE):
                out = DeepValue(1)
            elif node["op"] == sg.REF:
                out = self._sum(DeepValue(1), self.hash(node["atom"]))
            else:
                out = self._sum(DeepValue(1), self.hash(node["left"]),
                                self.hash(node["right"]))
            self.memo[node_hash] = out
            return out
        finally:
            self.visiting.remove(node_hash)

    def term(self, term):
        kind = term[0]
        if kind == "thunk":
            return self.hash(term[1])
        if kind == "app":
            return self._sum(DeepValue(1), self.term(term[1]),
                             self.term(term[2]))
        if kind == "ref":
            return self._sum(DeepValue(1), self.hash(term[1]))
        return DeepValue(1)


def next_action(term):
    """Describe the action ``step5`` will attempt without forcing a thunk."""
    kind = term[0]
    if kind == "thunk":
        return None if term[1] in sg.GENESIS else ("force",)
    if kind == "ref":
        return ("R-R",)
    if kind != "app":
        return None

    function, argument = term[1], term[2]
    if sg.glyph_eq(function, sg.I_H):
        return ("R-I",)
    if function[0] == "app" and sg.glyph_eq(function[1], sg.K_H):
        return ("R-K",)
    if (function[0] == "app" and function[1][0] == "app"
            and sg.glyph_eq(function[1][1], sg.S_H)):
        return ("R-S", argument)
    return next_action(function) or next_action(argument)


class Tracker:
    def __init__(self, entries, mode):
        self.mode = mode
        self.family = {e["name"]: e["family"] for e in entries}
        self.book_spent = Counter()
        self.events = defaultdict(list)
        self.pricing_attempts = Counter()
        self.saturated_attempts = Counter()

    def attempt(self, aid, saturated):
        self.pricing_attempts[aid] += 1
        self.saturated_attempts[aid] += bool(saturated)

    def fired(self, aid, book_price, copy_price, saturated):
        self.events[aid].append({
            "book_price": book_price,
            "copy_price": copy_price,
            "excess": copy_price - book_price,
            "saturated": saturated,
        })


def priced_step(term, remaining, store, stats, sizer, mode, tracker=None,
                aid=None):
    """Call the oracle step, replacing only an enforced R-S charge."""
    action = next_action(term)
    is_rs = action is not None and action[0] == "R-S"
    deep = None
    copy_price = None
    if is_rs and mode != "off":
        deep = sizer.term(action[1])
        copy_price = 1 + deep.value
        if tracker is not None:
            tracker.attempt(aid, deep.saturated)
        if mode == "enforced" and copy_price > remaining:
            raise sg.BudgetExhausted()

    result = sg.step5(term, remaining, store, stats, sg.DEFAULT_LIMITS)
    if result is None:
        return None
    new_term, book_price = result
    charged = copy_price if is_rs and mode == "enforced" else book_price
    if tracker is not None:
        tracker.book_spent[aid] += book_price
        if is_rs and mode != "off":
            expected = 1 + sg.size(action[1])
            if book_price != expected:
                raise AssertionError(
                    f"R-S detector disagrees with oracle: {book_price} != {expected}")
            tracker.fired(aid, book_price, copy_price, deep.saturated)
    return new_term, charged


def reduce_slice(agent, store, slice_atp, sizer, mode, tracker, probe=True):
    """The repository driver with one pricing hook around the oracle action."""
    if agent.status not in al.RUNNABLE:
        return 0
    budget = min(slice_atp, agent.atp)
    spent = 0
    steps = 0
    limits = sg.DEFAULT_LIMITS
    old_rl = sys.getrecursionlimit()
    sys.setrecursionlimit(max(old_rl, 3 * limits["max_node_depth"] + 2000))

    def settle(status):
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
            try:
                result = priced_step(agent.term, budget - spent, store,
                                     agent.stats, sizer, mode, tracker, agent.aid)
            except sg.BudgetExhausted:
                if budget >= agent.atp:
                    return settle(al.STARVED)
                try:
                    # Same slice-boundary counterfactual as al.reduce_slice.
                    # It is deliberately not counted as a pricing attempt.
                    priced_step(agent.term, agent.atp - spent, store,
                                dict(agent.stats), sizer, mode)
                except sg.BudgetExhausted:
                    return settle(al.STARVED)
                except (sg.Unresolved, sg.ResourceFault):
                    pass
                return settle(al.LIVE)
            except sg.Unresolved:
                return settle(al.UNRESOLVED)
            if result is None:
                sg.resource_check(agent.term, limits)
                return settle(al.NORMAL)
            agent.term, cost = result
            spent += cost
            if probe:
                if sg.size(agent.term) > agent.s0 + agent.spent + spent:
                    raise AssertionError(
                        f"MEMORY BOUND VIOLATED: {agent.aid} size "
                        f"{sg.size(agent.term)} > {agent.s0 + agent.spent + spent}")
                agent.peak = max(agent.peak, sg.size(agent.term))
    except sg.ResourceFault:
        return settle(al.FAULT)
    finally:
        sys.setrecursionlimit(old_rl)


def run_arm(entries, mode, atp_per_agent=C.ATP_PER_AGENT, ticks=C.TICKS):
    store = fresh_store()
    economy = al.Economy(atp_per_agent * len(entries))
    agents = []
    for entry in entries:
        root = al.put_term(entry["term"], store)
        agent = al.Agent(entry["name"], root, 0)
        economy.endow(agent, atp_per_agent)
        agents.append(agent)
    tracker = Tracker(entries, mode)
    sizer = DeepSizer(store)
    economy_ok = True
    bound_ok = True
    elapsed = 0
    for _ in range(ticks):
        if not any(a.status in al.RUNNABLE and a.atp > 0 for a in agents):
            break
        for agent in sorted(agents, key=lambda a: a.aid):
            if agent.status not in al.RUNNABLE or agent.atp == 0:
                continue
            attempt = C.SLICE_ATP
            while True:
                got = reduce_slice(agent, store, attempt, sizer, mode, tracker)
                if got or agent.status != al.LIVE:
                    break
                attempt = min(agent.atp, max(1, attempt * 2))
        for agent in agents:
            al.put_term(agent.term, store)
        elapsed += 1
        economy_ok = economy_ok and economy.check(agents)
        bound_ok = bound_ok and (
            sum(a.size for a in agents)
            <= sum(a.s0 for a in agents) + sum(a.spent for a in agents))
    return {
        "mode": mode, "store": store, "economy": economy, "agents": agents,
        "tracker": tracker, "ticks": elapsed,
        "economy_ok": economy_ok, "bound_ok": bound_ok,
    }


def distribution(events):
    excesses = sorted((e["excess"] for e in events), reverse=True)
    count = len(excesses)
    total = sum(excesses)
    top_n = max(1, math.ceil(count / 10)) if count else 0
    top_share = sum(excesses[:top_n]) / total if total else None
    majority_n = 0
    if total:
        cumulative = 0
        for majority_n, value in enumerate(excesses, 1):
            cumulative += value
            if 2 * cumulative > total:
                break
    return {
        "max": max(excesses) if excesses else None,
        "median": statistics.median(excesses) if excesses else None,
        "top_decile_n": top_n,
        "top_decile_share": top_share,
        "strict_majority_n": majority_n,
        "strict_majority_share_of_firings": majority_n / count if count else None,
    }


def aggregate(run, aids):
    agents = [a for a in run["agents"] if a.aid in aids]
    tracker = run["tracker"]
    events = [event for aid in aids for event in tracker.events[aid]]
    book_atp = sum(tracker.book_spent[aid] for aid in aids)
    excess = sum(event["excess"] for event in events)
    if run["mode"] == "enforced":
        copy_atp = sum(a.spent for a in agents)
    else:
        copy_atp = book_atp + excess
    return {
        "agents": len(agents),
        "settled": sum(a.status == al.NORMAL for a in agents),
        "settled_ids": sorted(a.aid for a in agents if a.status == al.NORMAL),
        "starved": sum(a.status == al.STARVED for a in agents),
        "live": sum(a.status == al.LIVE for a in agents),
        "unresolved": sum(a.status == al.UNRESOLVED for a in agents),
        "fault": sum(a.status == al.FAULT for a in agents),
        "book_atp": book_atp,
        "copy_atp": copy_atp,
        "copy_to_book_ratio": copy_atp / book_atp if book_atp else None,
        "excess_atp": excess,
        "r_s_firings": len(events),
        "pricing_attempts": sum(tracker.pricing_attempts[aid] for aid in aids),
        "saturated_pricing_attempts": sum(
            tracker.saturated_attempts[aid] for aid in aids),
        "saturated_firings": sum(event["saturated"] for event in events),
        "excess_distribution": distribution(events),
    }


def build_result(entries, shadow, enforced):
    families = sorted({e["family"] for e in entries})
    ids_by_family = {
        family: {e["name"] for e in entries if e["family"] == family}
        for family in families
    }
    all_ids = {e["name"] for e in entries}
    out = {
        "families": {
            family: {
                "arm_a_shadow": aggregate(shadow, ids_by_family[family]),
                "arm_b_enforced": aggregate(enforced, ids_by_family[family]),
            } for family in families
        },
        "population": {
            "arm_a_shadow": aggregate(shadow, all_ids),
            "arm_b_enforced": aggregate(enforced, all_ids),
        },
    }

    arm_a = out["population"]["arm_a_shadow"]
    arm_b = out["population"]["arm_b_enforced"]
    majority_share = arm_a["excess_distribution"][
        "strict_majority_share_of_firings"]
    h1_margin = arm_a["copy_to_book_ratio"] is not None \
        and arm_a["copy_to_book_ratio"] >= 2.0
    h1_concentrated = majority_share is not None and majority_share < 0.10

    material = math.ceil(0.10 * len(entries))
    settled_delta = arm_a["settled"] - arm_b["settled"]

    family_excess = {
        family: out["families"][family]["arm_a_shadow"]["excess_atp"]
        for family in families
    }
    max_value, min_value = max(family_excess.values()), min(family_excess.values())
    max_families = sorted(k for k, v in family_excess.items() if v == max_value)
    min_families = sorted(k for k, v in family_excess.items() if v == min_value)
    drop = family_excess["drop"]
    dup = family_excess["dup"]
    gap = (dup / drop) if drop else None
    gap_holds = dup > 0 if drop == 0 else gap >= 2.0

    out["hypotheses"] = {
        "H1": {
            "holds": h1_margin and h1_concentrated,
            "wide_margin_at_least_2x": h1_margin,
            "strict_majority_from_fewer_than_10pct": h1_concentrated,
        },
        "H2": {
            "holds": settled_delta >= material,
            "settled_delta": settled_delta,
            "material_threshold": material,
            "same_settled_ids": arm_a["settled_ids"] == arm_b["settled_ids"],
        },
        "H3": {
            "holds": max_families == ["dup"] and min_families == ["drop"]
            and gap_holds,
            "family_excess_atp": family_excess,
            "maximum_families": max_families,
            "minimum_families": min_families,
            "dup_to_drop_ratio": gap,
            "zero_drop_positive_dup": drop == 0 and dup > 0,
        },
    }
    return out


def no_rs_control():
    ig, kg, sglyph = C.EXP1.IG, C.EXP1.KG, C.EXP1.SG
    terms = [ig, ("app", ig, kg), ("app", ("app", kg, ig), sglyph)]
    entries = [{"family": "control", "name": f"no-rs-{i}", "term": term}
               for i, term in enumerate(terms)]
    plain = run_arm(entries, "off", atp_per_agent=100, ticks=8)
    shadow = run_arm(entries, "shadow", atp_per_agent=100, ticks=8)
    p_agents = {a.aid: a for a in plain["agents"]}
    s_agents = {a.aid: a for a in shadow["agents"]}
    same = all(
        p_agents[aid].spent == s_agents[aid].spent
        and p_agents[aid].hash == s_agents[aid].hash
        for aid in p_agents)
    no_firings = not any(shadow["tracker"].events.values())
    return same and no_firings


def known_discount_control():
    """Reproduce the preregistration's 13-node thunk: Book 2, copy 14."""
    z = C.EXP1.IG
    for leaf in (C.EXP1.KG, C.EXP1.SG, C.EXP1.IG,
                 C.EXP1.KG, C.EXP1.SG, C.EXP1.IG):
        z = ("app", z, leaf)
    term = ("app", ("app", ("app", C.EXP1.SG, C.EXP1.IG),
                    C.EXP1.IG), z)
    entry = {"family": "control", "name": "known-13", "term": term}
    run = run_arm([entry], "shadow", atp_per_agent=200, ticks=8)
    events = run["tracker"].events[entry["name"]]
    return (sg.size(z) == 13 and bool(events)
            and events[0]["book_price"] == 2
            and events[0]["copy_price"] == 14)


def saturation_control():
    store = fresh_store()
    node = sg.I_H
    for _ in range(30):
        node = store.put(sg.ser(sg.APPLY, sg.F_LEFT | sg.F_RIGHT,
                                left=node, right=node))
    got = DeepSizer(store).hash(node)
    return got.value == C.DEEP_SIZE_CAP and got.saturated


def controls(entries, plain, shadow, enforced, result):
    out = []
    shadow_events = [event for events in shadow["tracker"].events.values()
                     for event in events]
    out.append((
        f"C1 shadow never undercharges across {len(shadow_events)} firings; "
        "the 13-node thunk is 2 vs 14",
        bool(shadow_events) and all(
            e["copy_price"] >= e["book_price"] for e in shadow_events)
        and known_discount_control()))

    out.append(("C2 no R-S means exactly no price difference", no_rs_control()))

    p_agents = {a.aid: a for a in plain["agents"]}
    s_agents = {a.aid: a for a in shadow["agents"]}
    c3 = all(
        p_agents[aid].hash == s_agents[aid].hash
        and p_agents[aid].status == s_agents[aid].status
        and p_agents[aid].spent == s_agents[aid].spent
        for aid in p_agents)
    out.append(("C3 Arm A shadow leaves every result hash and Book-I ATP unchanged",
                c3))

    oracle_store = fresh_store()
    roots = {e["name"]: al.put_term(e["term"], oracle_store) for e in entries}
    c4 = True
    checked = 0
    for agent in enforced["agents"]:
        if agent.status != al.NORMAL:
            continue
        expected, _ = sg.eval_hash(roots[agent.aid], C.ATP_PER_AGENT, oracle_store)
        checked += 1
        c4 = c4 and agent.hash == sg.term_hash(expected)
    out.append((f"C4 all {checked} Arm-B settlers reach the Book-I answer", c4))

    c5 = all(run["economy_ok"] and run["bound_ok"]
             and run["economy"].check(run["agents"])
             for run in (shadow, enforced))
    out.append(("C5 conservation and the population memory bound hold in both arms",
                c5))

    fingerprint = C.fingerprint(entries)
    out.append((f"C6 corpus fingerprint is {fingerprint}",
                fingerprint == C.INHERITED_FINGERPRINT))

    aggregates = [result["population"][arm]
                  for arm in ("arm_a_shadow", "arm_b_enforced")]
    for family in result["families"].values():
        aggregates.extend(family.values())
    fields_present = all(
        isinstance(a.get("saturated_pricing_attempts"), int)
        and isinstance(a.get("saturated_firings"), int)
        for a in aggregates)
    out.append(("C7 synthetic saturation hits the cap and every aggregate reports it",
                saturation_control() and fields_present))
    return all(passed for _, passed in out), out


def summarize(result):
    print(f"{'run':10s} {'arm':9s} {'book':>8s} {'copy':>8s} {'ratio':>7s} "
          f"{'R-S':>5s} {'sat':>5s} {'settled':>9s}")
    rows = list(result["families"].items()) + [("POPULATION", result["population"])]
    for name, arms in rows:
        for label, key in (("shadow", "arm_a_shadow"),
                           ("enforced", "arm_b_enforced")):
            r = arms[key]
            ratio = f"{r['copy_to_book_ratio']:.3f}" if r["copy_to_book_ratio"] else "n/a"
            print(f"{name:10s} {label:9s} {r['book_atp']:8d} {r['copy_atp']:8d} "
                  f"{ratio:>7s} {r['r_s_firings']:5d} "
                  f"{r['saturated_firings']:5d} {r['settled']:4d}/{r['agents']:<4d}")
    print()
    for name in ("H1", "H2", "H3"):
        h = result["hypotheses"][name]
        print(f"{name}: {'HOLDS' if h['holds'] else 'FAILS'}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--record", action="store_true")
    args = parser.parse_args()

    entries = C.build()
    # Controls deliberately reuse the complete runs they validate; no hidden
    # second trajectory is substituted between validation and the receipt.
    plain = run_arm(entries, "off")
    shadow = run_arm(entries, "shadow")
    enforced = run_arm(entries, "enforced")
    result = build_result(entries, shadow, enforced)
    ok, control_results = controls(entries, plain, shadow, enforced, result)
    for name, passed in control_results:
        print(("OK  " if passed else "FAIL"), name)
    if not ok:
        print("\nALIFE-EXP-005: CONTROLS FAILED — nothing reported, nothing recorded")
        return 1

    print()
    summarize(result)
    provenance = al.provenance()
    receipt = {
        "experiment": "ALIFE-EXP-005",
        "corpus_fingerprint": C.fingerprint(entries),
        "inherited_from": "ALIFE-EXP-001",
        "frame": {
            "agents": len(entries), "families": sorted(C.EXP1.BUILDERS),
            "atp_per_agent": C.ATP_PER_AGENT, "slice_atp": C.SLICE_ATP,
            "ticks": C.TICKS, "seed": C.SEED,
            "deep_size_cap": C.DEEP_SIZE_CAP,
        },
        "decisions": "DECISIONS.md D1-D7",
        "provenance": {
            "sigma_alife_version": provenance["sigma_alife_version"],
            "sigma_glyph_requirement": provenance["sigma_glyph_requirement"],
            "oracle_sha256": provenance["oracle_sha256"],
            "python": ".".join(provenance["python"].split(".")[:2]),
            "platform": platform.python_implementation(),
        },
        "controls": {name: passed for name, passed in control_results},
        "result": result,
    }
    print(f"\noracle: {provenance['oracle_source']}  "
          f"(sha256 {provenance['oracle_sha256'][:16]}…)")
    if args.record:
        (HERE / "results.json").write_text(
            json.dumps(receipt, indent=2, sort_keys=True) + "\n")
        print(f"recorded {HERE / 'results.json'}")
    else:
        print("(check-only; pass --record to write results.json)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
