#!/usr/bin/env python3
"""A generic shape guard cannot see a changed result. This proves it, and proves
what can.

`tools/receipt_guard.py` is a SPELLING rule: it checks that every named null
says how many times it was drawn. It says nothing about whether the numbers in a
receipt are the numbers the harness derives — and for eleven days ALIFE-EXP-010
was in the repository with no replay behind it, so the generic guard was the only
thing looking at its receipt (Codex review, 2026-08-26, [BLOCKER] #2).

Each mutation below changes a SCORED field — a verdict, a consumption count, a
corrected estimand — while leaving the document a perfectly well-formed receipt.
Two assertions per mutation:

  1. the generic guard does NOT catch it. That is not a defect in that guard; it
     is what "a digest/shape guard is not a replay" means, stated as a test
     rather than as a sentence in a review;
  2. the identity comparator DOES catch it — the same `--record`-then-diff step
     `tools/test-all.sh` runs, exercised here on temporary files so a crash can
     never leave a mutated receipt in the working tree.

A guard nobody has watched fail is a guard nobody has watched.

Usage:  python3 tests/receipt_identity_guard.py
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import receipt_guard as RG  # noqa: E402

# How `measure.py --record` serializes. A mutation the identity check cannot see
# through this serializer is not a mutation of the receipt.
def canonical(doc):
    return json.dumps(doc, indent=2, sort_keys=True) + "\n"


EXP010 = "experiments/alife-exp-010/results.json"
MUTATIONS = (
    (EXP010, ("result", "scores", "H2", "verdict"), "HOLDS",
     "a preregistered verdict flipped"),
    (EXP010, ("result", "scores", "H3", "seeds_clearing"), 2,
     "H3's seed count raised to the threshold"),
    (EXP010, ("result", "primary", "M", "20260825", "consumed_deaths"), 9999,
     "the currency's own event count"),
    (EXP010, ("result", "primary", "E", "20260825", "rs_share_of_spend"), 0.0279,
     "the withdrawn ATP share put back"),
    (EXP010, ("result", "primary", "M", "20260825", "consumed_last_copy"), 0,
     "the consumption-mediation statistic zeroed"),
    ("experiments/alife-exp-007/results.json",
     ("result", "primary", "20260825", "core_size"), 3,
     "a frozen receipt Arm E is scored against"),
)


def at(doc, path):
    for k in path[:-1]:
        doc = doc[k]
    return doc


def diff_catches(committed, mutated):
    """`git diff --exit-code`, the comparator `tools/test-all.sh` uses, on two
    temporary files. Returns True when it reports a difference."""
    with tempfile.TemporaryDirectory() as d:
        a, b = Path(d) / "committed.json", Path(d) / "derived.json"
        a.write_text(committed)
        b.write_text(mutated)
        r = subprocess.run(["git", "diff", "--no-index", "--exit-code",
                            str(a), str(b)], capture_output=True, text=True)
        return r.returncode != 0


def main():
    ok = True
    checked = 0
    for rel, path, value, why in MUTATIONS:
        src = ROOT / rel
        if not src.exists():
            print("FAIL", f"{rel} is missing")
            ok = False
            continue
        raw = src.read_text()
        doc = json.loads(raw)
        parent = at(doc, path)
        if path[-1] not in parent:
            print("FAIL", f"{rel}: no field {'.'.join(map(str, path))} to mutate")
            ok = False
            continue
        before = parent[path[-1]]
        if before == value:
            print("FAIL", f"{rel}: {'.'.join(map(str, path))} already {value!r} "
                          f"— the mutation would change nothing")
            ok = False
            continue
        parent[path[-1]] = value
        mutated = canonical(doc)

        blind = not list(RG.offenders(doc))
        caught = diff_catches(canonical(json.loads(raw)), mutated)
        label = f"{rel.split('/')[1]}: {why} ({'.'.join(map(str, path))})"
        print(("OK  " if blind else "FAIL"),
              f"the shape guard is blind to it — {label}")
        print(("OK  " if caught else "FAIL"),
              f"the identity diff catches it — {label}")
        ok = ok and blind and caught
        checked += 1

    # And the identity comparator must not cry wolf: an unmutated receipt is
    # identical to itself through the same serializer.
    raw = (ROOT / EXP010).read_text()
    quiet = not diff_catches(canonical(json.loads(raw)), canonical(json.loads(raw)))
    print(("OK  " if quiet else "FAIL"),
          "the identity diff is silent on an unmutated receipt")
    ok = ok and quiet

    # The committed receipt must ALSO be byte-identical to its own canonical
    # serialization — otherwise `--record` and the guard disagree about what the
    # file is, and every diff above would be testing the serializer.
    same = raw == canonical(json.loads(raw))
    print(("OK  " if same else "FAIL"),
          "the committed receipt is exactly what `--record` would write")
    ok = ok and same

    print(f"\nRECEIPT-IDENTITY-GUARD: {'ALL PASS' if ok else 'FAILURES PRESENT'} "
          f"({checked} scored-field mutations)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
