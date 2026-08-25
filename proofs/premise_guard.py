#!/usr/bin/env python3
"""Guard for proofs/Population.lean.

Two things can make this file's theorems worthless without making `lean` say a
word about it, and this guard is aimed at exactly those two:

  G1 — DRIFT. `Acc` and `Step` in Population.lean are a copy of the accounting
       model in sigma-glyph's proofs/SizeBound.lean. If the original changes a
       cost, a shrink hypothesis or a constructor and the copy does not, every
       theorem here still compiles and stops being about Book I. The copy is
       compared token by token against the original and any difference is a hard
       failure — the fix is to re-copy and re-check, never to edit the copy.

  G2 — VACUITY AND ESCAPE HATCHES. `lean` exits 0 on a file whose proofs are
       `sorry`ed (it is a warning), and `theorem t : True := trivial` is green
       forever. The guarded theorems' signatures are pinned by digest, and the
       metaprogramming and axiom routes are denied outright.

SCOPE, stated so it is not mistaken for its neighbour: this is a WEAKER guard
than sigma-glyph's proofs/proof_guard.py. That one loads the compiled `.olean`
as data and pins each theorem's ELABORATED type against the kernel environment;
this one pins SOURCE TEXT, which a sufficiently determined notation or
delaborator trick could dress up. It is what a repository with one core-only
Lean file and no `lake` build can honestly enforce today. If this repository
grows a second proof front, port the real guard rather than extending this one.

Usage:
  python3 proofs/premise_guard.py            # check
  python3 proofs/premise_guard.py --record   # rewrite the pins (review the diff)
Env:
  SIGMA_GLYPH_PROOFS  — the proofs/ directory of a sigma-glyph checkout
                        (default: ../sigma-glyph/proofs, then
                        ~/Projects/sigma-glyph/proofs)
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
POPULATION = HERE / "Population.lean"
PINS = HERE / "theorem_pins.json"

GUARDED = [
    "step_delta", "step_spent", "bound_from", "spent_mono", "ReachFrom.trans",
    "resumption_bound", "memory_bound_from_thunk", "totalBirth_ones",
    "population_peak_size", "population_peak_size_thunks",
    "transfer_preserves_bound",
]

# Denied outright. `sorry` has no word boundary after it (`sorryAx`), so the
# pattern must not rely on one — the mistake sigma-glyph's guard was killed by
# in its first round.
DENY = [
    (r"sorry", "sorry / sorryAx"),
    (r"\badmit\b", "admit"),
    (r"\baxiom\b", "axiom declaration"),
    (r"native_decide", "native_decide"),
    (r"implemented_by", "@[implemented_by]"),
    (r"@\[extern", "@[extern]"),
    (r"\b(macro|elab|syntax|run_cmd|unsafe|attribute)\b", "metaprogramming"),
    (r"^\s*import\b", "import (these are core-Lean-only proofs)"),
    (r"^\s*#", "# command"),
]


def strip_comments(src):
    """Blank out block and line comments, and fail closed on the two states this
    simple stripper cannot honestly claim to model: an unterminated block
    comment (which is how `def blind : String := "/-"` blinded sigma-glyph's
    guard in its round-2 review) and any string literal surviving in the code,
    which this file has none of and should never grow one."""
    out, i, depth = [], 0, 0
    while i < len(src):
        if src.startswith("/-", i):
            depth += 1
            i += 2
        elif src.startswith("-/", i) and depth:
            depth -= 1
            i += 2
        elif depth:
            out.append("\n" if src[i] == "\n" else " ")
            i += 1
        elif src.startswith("--", i):
            j = src.find("\n", i)
            i = len(src) if j < 0 else j
        else:
            out.append(src[i])
            i += 1
    text = "".join(out)
    if depth:
        raise SystemExit("GUARD: unterminated block comment in Population.lean — "
                         "a `/-` inside a string literal is exactly how a text "
                         "guard gets blinded. Review by hand.")
    if '"' in text:
        raise SystemExit("GUARD: a string literal survives in Population.lean code; "
                         "this stripper does not model those. Review by hand.")
    return text


def normalize(text):
    return " ".join(text.split())


def extract_block(src, header):
    """The declaration beginning with `header`, up to the next top-level
    declaration keyword."""
    start = src.index(header)
    rest = src[start + len(header):]
    stop = len(rest)
    for kw in ("\nstructure ", "\ninductive ", "\ntheorem ", "\ndef ", "\nnamespace ",
               "\nend ", "\n/--"):
        j = rest.find(kw)
        if 0 <= j < stop:
            stop = j
    return normalize(header + rest[:stop])


def extract_signature(src, name):
    """A guarded theorem's signature: everything from its name up to `:=` or
    `by`, whichever ends the statement — the part a vacuous rewrite would have
    to change."""
    m = re.search(r"\btheorem\s+" + re.escape(name) + r"\b", src)
    if not m:
        raise SystemExit(f"GUARD: guarded theorem `{name}` is not in Population.lean")
    rest = src[m.start():]
    end = len(rest)
    for token in (":=", "\ntheorem ", "\ndef ", "\nend "):
        j = rest.find(token)
        if 0 <= j < end:
            end = j
    return normalize(rest[:end])


def sigma_proofs_dir():
    if os.environ.get("SIGMA_GLYPH_PROOFS"):
        return Path(os.environ["SIGMA_GLYPH_PROOFS"])
    for cand in (HERE.parents[1] / "sigma-glyph" / "proofs",
                 Path.home() / "Projects/sigma-glyph/proofs"):
        if cand.exists():
            return cand
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--record", action="store_true")
    args = ap.parse_args()

    src_raw = POPULATION.read_text()
    src = strip_comments(src_raw)
    failures, skips = [], []

    # G2a — denylist
    for pattern, label in DENY:
        m = re.search(pattern, src, re.M)
        if m:
            line = src[:m.start()].count("\n") + 1
            failures.append(f"denied construct `{label}` at Population.lean:{line}")

    # G2b — every theorem in the file must be guarded. A theorem nobody pinned
    # is a theorem whose statement can be rewritten in silence, and "it was not
    # on the list" is how the list stops covering the file it is about.
    declared = set(re.findall(r"\btheorem\s+([A-Za-z_][\w.']*)", src))
    for name in sorted(declared - set(GUARDED)):
        failures.append(f"theorem `{name}` is declared but not in GUARDED — pin it "
                        f"or delete it")
    for name in sorted(set(GUARDED) - declared):
        failures.append(f"guarded theorem `{name}` is not declared in Population.lean")

    # G2c — pinned signatures
    signatures = {name: extract_signature(src, name) for name in GUARDED}
    digests = {n: hashlib.sha256(s.encode()).hexdigest() for n, s in signatures.items()}

    # G1 — the copied premise
    sgp = sigma_proofs_dir()
    premise = {}
    if sgp is None:
        skips.append("sigma-glyph proofs not found — set SIGMA_GLYPH_PROOFS to "
                     "the proofs/ directory of a checkout. The copied premise "
                     "was NOT compared against its original.")
    else:
        orig = strip_comments((sgp / "SizeBound.lean").read_text())
        for header in ("structure Acc where", "inductive Step : Acc → Acc → Prop where"):
            ours = extract_block(src, header)
            theirs = extract_block(orig, header)
            premise[header] = hashlib.sha256(theirs.encode()).hexdigest()
            if ours != theirs:
                failures.append(
                    f"PREMISE DRIFT in `{header}`:\n"
                    f"  sigma-glyph: {theirs}\n"
                    f"  here:        {ours}")

    if args.record:
        PINS.write_text(json.dumps({
            "_README": [
                "Pins for proofs/premise_guard.py. `statements` is the SHA-256 of",
                "each guarded theorem's normalized source signature; `premise` is",
                "the SHA-256 of the sigma-glyph blocks the model was copied from.",
                "A pin changing is not a defect — it is a claim changing, and it",
                "must be reviewed as one.",
            ],
            "statements": digests,
            "premise": premise,
        }, indent=2, sort_keys=True) + "\n")
        print("recorded", PINS)
        return 0

    if not PINS.exists():
        failures.append("no theorem_pins.json — run with --record and review it")
    else:
        pins = json.loads(PINS.read_text())
        for name, dig in digests.items():
            want = pins.get("statements", {}).get(name)
            if want is None:
                failures.append(f"theorem `{name}` is guarded but not pinned")
            elif want != dig:
                failures.append(f"STATEMENT CHANGED: `{name}`\n  now: {signatures[name]}")
        for name in pins.get("statements", {}):
            if name not in digests:
                failures.append(f"pin for `{name}` has no guarded theorem")
        for header, dig in premise.items():
            want = pins.get("premise", {}).get(header)
            if want != dig:
                failures.append(f"the pinned ORIGINAL of `{header}` moved: "
                                f"sigma-glyph's SizeBound.lean is not the file this "
                                f"copy was checked against")

    # G3 — lean itself, if it is here
    if shutil.which("lean"):
        r = subprocess.run(["lean", str(POPULATION)], capture_output=True, text=True)
        out = r.stdout + r.stderr
        # A LEAN DIAGNOSTIC is a line in lean's `file:line:col: severity` form.
        # Everything else on those streams belongs to the launcher, not to the
        # proof: `elan` downloads and installs a toolchain on first use and says
        # so, in the middle of this very subprocess. The first version of this
        # check failed on *any* output, which was green on a machine whose
        # toolchain was already installed and red in CI on the first run — a
        # guard that reports the installer as an unsound proof is a guard that
        # will be silenced rather than read.
        diagnostics = [ln for ln in out.splitlines()
                       if re.search(r"\.lean:\d+:\d+: (error|warning)", ln)]
        if r.returncode != 0:
            failures.append(f"lean rejected Population.lean:\n{out}")
        elif "sorry" in out:
            failures.append(f"lean accepted it, with sorries:\n{out}")
        elif diagnostics:
            failures.append("lean emitted diagnostics where none were expected:\n"
                            + "\n".join(diagnostics))
        elif out.strip():
            # Not a failure, but never silent: an operator reading a green
            # verdict should still see what else spoke during it.
            print("note: non-diagnostic output while checking the proofs "
                  f"(launcher, not lean):\n{out.strip()}")
    else:
        skips.append("`lean` is not on PATH — the proofs were NOT checked, only "
                     "their text. Install elan to include them.")

    for f in failures:
        print("FAIL", f)
    for s in skips:
        print("SKIP", s)
    if failures:
        print("PREMISE-GUARD: FAILURES PRESENT")
        return 1
    if skips:
        print("PREMISE-GUARD: NOT COMPLETE — a skipped surface is not a passed one")
        return 2
    print(f"PREMISE-GUARD: ALL PASS ({len(GUARDED)} theorems pinned, premise "
          f"identical to sigma-glyph SizeBound.lean, lean green with no sorries)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
