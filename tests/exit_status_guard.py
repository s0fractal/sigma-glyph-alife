#!/usr/bin/env python3
"""Every gate in this repository must put its verdict in the EXIT STATUS.

sigma-glyph's precedent: `impl/sigma_glyph.py` once called `run_tests()`, threw
the boolean away, printed FAILURES PRESENT and exited 0 — so every gate that
grepped stdout caught it and `python -m sigma_glyph && ./anything` reported
success on a failing oracle. The same mistake is one `return` away here.

This substitutes a failing verdict into each entry point, in a throwaway copy of
the tree, and demands a non-zero exit; then runs the real thing and demands zero.
A mutation that does not apply is a hard failure, not a skip: a guard that
silently stopped mutating would pass forever.
"""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "impl"))
import sigma_alife as al  # noqa: E402

# entry point -> (argv tail, marker on stdout, the verdict to break)
CASES = {
    "impl/sigma_alife.py": ([], "ALIFE: ALL PASS",
                            ("    passed = all(ok)", "    passed = False")),
    "tests/alife_differential.py": (["--terms", "8"], "ALIFE-DIFFERENTIAL: ALL AGREE",
                                    ("    ok, (cases, exercised) = run(args.terms, args.seed)",
                                     "    ok, (cases, exercised) = False, (0, {'starved-then-fed': 1})")),
    "tests/alife_conservation.py": (["--runs", "2", "--ticks", "2"],
                                    "ALIFE-CONSERVATION: ALL PASS",
                                    ("    failures = []", "    failures = ['injected']")),
    "tests/alife_memo.py": (["--terms", "12"], "ALIFE-MEMO: ALL PASS",
                            ("    passed = all(ok)", "    passed = False")),
    "tests/alife_nulls.py": ([], "ALIFE-NULLS: ALL PASS",
                            ("    passed = all(ok)", "    passed = False")),
    "proofs/premise_guard.py": ([], "PREMISE-GUARD: ALL PASS",
                                ("    failures, skips = [], []",
                                 "    failures, skips = ['injected'], []")),
    # Added 2026-08-26 after Codex's review: both of these ARE gates — one is
    # the receipt guard's own negative controls, the other is the proof that a
    # changed result is caught by something. A gate that reports its verdict
    # only on stdout is the exact defect this file exists for.
    "tools/receipt_guard.py": (["--self-test"], "RECEIPT-GUARD-SELFTEST: ALL PASS",
                               ("    ok = True", "    ok = False")),
    "tests/receipt_identity_guard.py": ([], "RECEIPT-IDENTITY-GUARD: ALL PASS",
                                        ("    ok = True", "    ok = False")),
}


def run(tree, rel, argv, env):
    return subprocess.run([sys.executable, str(tree / rel)] + argv,
                          capture_output=True, text=True, env=env, cwd=str(tree))


def main():
    env = dict(os.environ)
    # The throwaway copy has no sibling sigma-glyph checkout above it, so the
    # oracle has to be named explicitly — the same variable the loader documents.
    # RESOLVED, not as written. `ORACLE_SOURCE` is normally a RELATIVE path
    # (`../sigma-glyph/impl/sigma_glyph.py`, the sibling checkout), and the
    # throwaway tree lives under /tmp where that resolves to nothing — so the
    # premise guard reported a missing SizeBound.lean and this file printed
    # FAILURES PRESENT on a repository whose every gate was green. Codex's
    # review asked for one canonical command that is terminal; a guard that
    # cannot find its own dependency is one of the reasons it was not.
    sigma = Path(al.ORACLE_SOURCE.replace("installed:", "")).resolve().parent
    env["SIGMA_GLYPH"] = str(sigma)
    env["SIGMA_GLYPH_PROOFS"] = str(sigma.parent / "proofs")

    ok = []
    with tempfile.TemporaryDirectory() as tmp:
        tree = Path(tmp) / "tree"
        shutil.copytree(ROOT, tree, ignore=shutil.ignore_patterns(
            ".git", "__pycache__", "*.pyc"))
        for rel, (argv, marker, (old, new)) in CASES.items():
            src = (tree / rel).read_text()
            if old not in src:
                print("FAIL", f"{rel}: the injected verdict `{old.strip()}` is no "
                              f"longer in the file — this guard stopped guarding it")
                ok.append(False)
                continue

            good = run(tree, rel, argv, env)
            passed = good.returncode == 0 and marker in good.stdout
            print(("OK   " if passed else "FAIL "),
                  f"{rel}: passing run exits 0 and prints its marker")
            if not passed:
                print(good.stdout[-2000:], good.stderr[-2000:])
            ok.append(passed)

            (tree / rel).write_text(src.replace(old, new))
            bad = run(tree, rel, argv, env)
            failed = bad.returncode != 0
            print(("OK   " if failed else "FAIL "),
                  f"{rel}: a failing verdict exits non-zero "
                  f"(got {bad.returncode})")
            ok.append(failed)
            (tree / rel).write_text(src)

    print(f"\nEXIT-STATUS-GUARD: {'ALL PASS' if all(ok) else 'FAILURES PRESENT'} "
          f"({sum(ok)}/{len(ok)})")
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
