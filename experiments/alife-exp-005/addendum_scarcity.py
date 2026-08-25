#!/usr/bin/env python3
"""ADDENDUM to ALIFE-EXP-005, by the author of its preregistration.

NOT part of the preregistered design, and not the harness author's work. It exists
because the preregistration contradicted itself, and the contradiction is mine:

  corpus.py    ATP_PER_AGENT = 3000  # "as EXP-001: enough that everyone settles"
  the document H2: "materially fewer agents reach a normal form at the same budget"

A budget chosen so that every agent settles cannot host a hypothesis that fewer
will. Enforced copy pricing costs 151 ATP more across 64 agents — 2.4 each,
against a reservoir of 3000, or 0.08%. H2 could not have been true, so its
recorded verdict of FAILS is wrong: the correct reading is UNDERPOWERED, by
exactly the rule this repository enforces elsewhere (ALIFE-EXP-002 D20, EXP-003
control C7) and failed to apply to its own document.

This addendum runs the same two arms at budgets where the difference could bind,
and reports where it does. It is post hoc and is labelled so wherever it appears.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "impl"))

import corpus as C  # noqa: E402
import measure as M  # noqa: E402  — the harness author's arms, reused unchanged
import sigma_alife as al  # noqa: E402

sg = al.sg

# EXP-003's scarcity levels, per agent, plus the preregistered budget for anchor.
PER_AGENT = (9, 14, 18, 25, 31, 43, 62, C.ATP_PER_AGENT)


def run(per_agent, mode):
    """Reuse the harness author's own arm, unchanged, at a different budget. The
    addendum questions the preregistration, not the implementation — reproducing
    its arms here would be a second thing to get wrong."""
    r = M.run_arm(C.build(), mode, atp_per_agent=per_agent)
    agents = r["agents"]
    assert r["economy_ok"] and r["bound_ok"], "conservation or bound failed"
    return {
        "settled": sum(1 for a in agents if a.status == al.NORMAL),
        "atp_spent": sum(a.spent for a in agents),
        "settled_ids": sorted(a.aid for a in agents if a.status == al.NORMAL),
    }


def main():
    record = "--record" in sys.argv
    rows = []
    print("ADDENDUM (post hoc, not preregistered) — where copy pricing binds\n")
    print(f"{'ATP/agent':>10s} {'book settled':>13s} {'copy settled':>13s} "
          f"{'Δ':>4s} {'book ATP':>9s} {'copy ATP':>9s}")
    for per in PER_AGENT:
        a = run(per, "shadow")
        b = run(per, "enforced")
        d = b["settled"] - a["settled"]
        rows.append({"atp_per_agent": per, "book": a, "copy": b, "delta": d})
        print(f"{per:>10d} {a['settled']:>10d}/64 {b['settled']:>10d}/64 "
              f"{d:>+4d} {a['atp_spent']:>9d} {b['atp_spent']:>9d}")
    binding = [r for r in rows if r["delta"] != 0]
    print()
    if binding:
        worst = min(binding, key=lambda r: r["delta"])
        print(f"H2 restated (post hoc): enforced copy pricing costs settlers at "
              f"{len(binding)} of {len(rows)} budgets tested; worst is "
              f"{worst['delta']:+d} at {worst['atp_per_agent']} ATP/agent.")
        print("The discount is capability, not accounting — but only where a "
              "colony is poor enough for 5.4% to matter.")
    else:
        print("H2 restated (post hoc): no budget tested changes the settled count. "
              "The discount is accounting at every scarcity level here, which is a "
              "stronger negative than the preregistered arm could produce.")
    if record:
        (HERE / "addendum_scarcity.json").write_text(
            json.dumps({"addendum": "post hoc, by the preregistration author",
                        "rows": rows}, indent=2, sort_keys=True) + "\n")
        print(f"\nrecorded {HERE / 'addendum_scarcity.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
