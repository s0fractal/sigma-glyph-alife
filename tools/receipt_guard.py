#!/usr/bin/env python3
"""Every null in every receipt must say how many times it was drawn.

Two experiments here reported chance models drawn ONCE. In ALIFE-EXP-008 that
single draw came back empty, a positive result was written, and twenty draws
reversed it (`DECISIONS.md` D54). In ALIFE-EXP-007 the same defect sat in a
published receipt and went unnoticed because its verdicts happened to survive.

A number labelled "null" without a draw count beside it is a coin flip presented
as a control, so this walks every committed receipt, finds every key that names a
null, and demands a `null_draws` (or `draws`) of at least MIN_DRAWS in the same
object. It is a spelling rule, deliberately: it cannot tell a good chance model
from a bad one, and it can tell that nobody sampled one.

Usage:  python3 tools/receipt_guard.py
        python3 tools/receipt_guard.py --self-test   (the negative controls)
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MIN_DRAWS = 20
NULL_KEYS = ("null", "shuffled", "chance")


def declared_draws(obj):
    """Every draw count declared anywhere INSIDE this value, in document order.

    Returns a list rather than a boolean, because "is there a big enough number
    somewhere" and "is every number here big enough" are different questions and
    the first version asked the wrong one. See `offenders`.
    """
    out = []
    if isinstance(obj, dict):
        for key in ("null_draws", "draws"):
            if isinstance(obj.get(key), int):
                out.append(obj[key])
        for v in obj.values():
            out += declared_draws(v)
    elif isinstance(obj, list):
        for v in obj:
            out += declared_draws(v)
    return out


def own_draws(obj):
    """The draw count this object declares for itself, or None. This is the
    "explicitly defined parent schema" case: a cell that names several nulls and
    states one `null_draws` beside them describes all of them."""
    if not isinstance(obj, dict):
        return None
    for key in ("null_draws", "draws"):
        if isinstance(obj.get(key), int):
            return obj[key]
    return None


def offenders(obj, path=""):
    """Yield (path, reason) for every named null with no sampling behind it.

    A BOOLEAN IS NOT A NULL STATISTIC. A receipt's `controls` block maps each
    control's own sentence to whether it passed, so a control *named* after the
    null it checks — ALIFE-EXP-012d's `C-null`, which verifies that the
    permutation preserves what it claims — is a key containing "null" whose value
    is `True`. It is not a statistic and there is no draw count that could
    describe it. Flagging it was this guard reading its own vocabulary in the
    wrong grammar. Nothing is weakened: a null statistic is a number or a
    structure, never a pass/fail flag, so no real offender can hide behind a
    boolean.

    THE LOCALITY RULE, and the bug it is a fix for. The first version asked
    `has_draws(obj)` — does a draw count of at least MIN_DRAWS live anywhere
    inside the CONTAINING dictionary — which let one unrelated sibling license
    every null beside it. Codex's review supplied the reproducer:

        offenders({"null_a": {"draws": 1}, "unrelated": {"draws": 20}})  ->  []

    A guard whose stated rule is locality and whose implementation searches
    arbitrary siblings is worse than no guard, because it reads as enforcement.
    The rule now binds a count to the null it describes:

      * every draw count declared inside the named null's own value must be at
        least MIN_DRAWS, and there must be at least one of them; or
      * if that value declares none — a null reported as a bare number, which is
        the common case — the count comes from the named null's OWN parent
        object and from nowhere else.

    A sibling subtree is never consulted."""
    if isinstance(obj, dict):
        named = [k for k in obj
                 if any(t in k.lower() for t in NULL_KEYS)
                 and not k.lower().endswith("draws")
                 and not isinstance(obj[k], bool)]
        for k in named:
            inside = declared_draws(obj[k])
            if inside:
                if min(inside) >= MIN_DRAWS:
                    continue
                yield (path or "<root>",
                       f"`{k}` with only {min(inside)} draws")
                continue
            d = own_draws(obj)
            if d is not None and d >= MIN_DRAWS:
                continue
            why = (f"`{k}` with only {d} draws" if d is not None
                   else f"`{k}` with no draw count")
            yield path or "<root>", why
        for k, v in obj.items():
            yield from offenders(v, f"{path}.{k}" if path else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from offenders(v, f"{path}[{i}]")


# ---------- negative controls ----------
# A guard with no failing case is a guard nobody has seen fail. Each mutation
# below is a way a receipt has actually been wrong, or — for the third — a way
# this guard WAS wrong until Codex's review of 2026-08-26.
MUTATIONS = (
    ("deletion: a named null with no draw count at all",
     {"core_shuffled": 12}),
    ("undersampling: the ALIFE-EXP-008 defect, one draw",
     {"core_shuffled": 12, "null_draws": 1}),
    ("unrelated sibling: a draw count that describes something else",
     {"null_a": {"draws": 1}, "unrelated": {"draws": MIN_DRAWS}}),
    ("nested undersampling: a big count at the top, a small one in a cell",
     {"nulls": {"draws": MIN_DRAWS, "cell": {"chance_max": 3, "draws": 2}}}),
    ("a numeric named null still fails when only a boolean sits beside it",
     {"null_statistic": 7, "some_control_passed": True}),
)
CLEAN = (
    ("a null with its own count", {"core_shuffled": 12, "null_draws": MIN_DRAWS}),
    ("a null whose cells carry the count",
     {"nulls": {"a": {"chance_max": 3, "draws": MIN_DRAWS}}}),
    ("a control NAMED after a null, whose value is a pass/fail flag",
     {"controls": {"C-null the permutation preserves the multiset": True,
                   "C-null(seeding) a draw is a function of its index": True}}),
)


def self_test():
    """Every mutation must be caught and every clean case must pass."""
    ok = True
    for why, doc in MUTATIONS:
        found = list(offenders(doc))
        print(("OK  " if found else "FAIL"), f"caught - {why}")
        ok = ok and bool(found)
    for why, doc in CLEAN:
        found = list(offenders(doc))
        print(("OK  " if not found else "FAIL"), f"passed - {why}")
        ok = ok and not found
    print(f"\nRECEIPT-GUARD-SELFTEST: {'ALL PASS' if ok else 'FAILURES PRESENT'} "
          f"({len(MUTATIONS)} mutations, {len(CLEAN)} clean cases)")
    return 0 if ok else 1


def main():
    if "--self-test" in sys.argv:
        return self_test()
    receipts = sorted(ROOT.glob("experiments/*/results.json")) + \
        sorted(ROOT.glob("experiments/*/*.json"))
    seen, bad = set(), []
    for r in receipts:
        if r in seen:
            continue
        seen.add(r)
        try:
            data = json.loads(r.read_text())
        except json.JSONDecodeError as exc:
            bad.append((r, "<unparseable>", str(exc)))
            continue
        found = list(offenders(data))
        rel = r.relative_to(ROOT)
        if found:
            for where, why in found[:4]:
                bad.append((rel, where, why))
            print(f"FAIL {rel}: {len(found)} null(s) without {MIN_DRAWS} draws")
        else:
            print(f"OK   {rel}")
    print(f"\nRECEIPT-GUARD: {'ALL PASS' if not bad else 'FAILURES PRESENT'} "
          f"({len(seen)} receipts, minimum {MIN_DRAWS} draws)")
    for rel, where, why in bad[:8]:
        print(f"  {rel}: {where} {why}")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
