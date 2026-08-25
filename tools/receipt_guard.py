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
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MIN_DRAWS = 20
NULL_KEYS = ("null", "shuffled", "chance")


def has_draws(obj):
    """Does a draw count of at least MIN_DRAWS live anywhere inside this value?
    The first version only looked in the SAME object, so a receipt that named its
    nulls at the top and declared the draws per cell — which is where the number
    belongs — was reported as an offender. The rule is: the count has to be
    findable from the thing it describes, not adjacent to its name."""
    if isinstance(obj, dict):
        d = obj.get("null_draws", obj.get("draws"))
        if isinstance(d, int) and d >= MIN_DRAWS:
            return True
        return any(has_draws(v) for v in obj.values())
    if isinstance(obj, list):
        return any(has_draws(v) for v in obj)
    return False


def offenders(obj, path=""):
    """Yield (path, reason) for every named null with no sampling behind it."""
    if isinstance(obj, dict):
        named = [k for k in obj
                 if any(t in k.lower() for t in NULL_KEYS)
                 and not k.lower().endswith("draws")]
        for k in named:
            if has_draws(obj) or has_draws(obj[k]):
                continue
            d = obj.get("null_draws", obj.get("draws"))
            why = (f"`{k}` with only {d} draws" if d is not None
                   else f"`{k}` with no draw count")
            yield path or "<root>", why
        for k, v in obj.items():
            yield from offenders(v, f"{path}.{k}" if path else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from offenders(v, f"{path}[{i}]")


def main():
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
