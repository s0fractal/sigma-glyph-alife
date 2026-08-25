# Agent & contributor conduct

This repository is a **consumer** of Σ-GLYPH and a **research** repository. Those
two facts set its rules: it must never speak for its dependency, and it must
never let a hypothesis it likes borrow the authority of a theorem it has.

## What it inherits from sigma-glyph, unchanged

sigma-glyph's `AGENTS.md` exists because an assisting agent once ran the green
suites, committed to `master`, and stamped `Reviewed-by: … (2-of-3 roster)` on
work no roster had seen. Three of its rules apply here in full:

1. **Never assert review or roster authority.** A trailer claiming a gate, a
   review or an adoption that did not happen is false provenance. No agent is a
   roster member and none can self-grant that authority.
2. **An "independent gate" means adversarial hunting by a fresh reviewer — not
   running the green suites.** Green is necessary and never sufficient. Every
   real finding in this repository so far arrived while everything was green:
   the REF census was one node short of `size` (caught by a property, not by a
   suite), and the first experiment contradicted the hypothesis it was built to
   support.
3. **Record provenance honestly.** State exactly what was validated and what was
   not. Do not upgrade "the suites are green" into "gated", "self-audited" into
   "reviewed", or "the corpus was committed first" into "preregistered by an
   independent party".

**Hard-to-reverse or outward-facing actions** — pushing, publishing, depositing,
submitting, creating a remote — need explicit human authorization for that
specific action. Approval of one step is not approval of the next.

## What is deliberately lighter here

sigma-glyph forbids committing to `master` because `master` there is a normative
specification under threshold-warrant governance. Nothing here is normative and
nothing here is under warrant, so ordinary DRAFT work lands on `master` in this
repository. That is the *entire* governance difference, and it is not a licence
for anything in the section above.

## Rules this repository adds

4. **Never edit the copied premise.** `Acc` and `Step` in `proofs/Population.lean`
   are a verbatim copy of sigma-glyph's `SizeBound.lean`. If the guard reports
   drift, re-copy the original and re-check every theorem. Editing the copy to
   make the guard green makes every theorem here a statement about a machine
   nobody runs.

5. **Never call something proved that is only checked.** This repository has
   exactly eleven theorems and they are listed in `proofs/README.md`. The Python
   driver's agreement with Book I is *tested*. The economy policies are *neither*.
   Any sentence that blurs those three belongs in a different repository.

6. **The receipt comes after the controls.** `measure.py` writes `results.json`
   only when every preregistered control has passed. A receipt beside a failure
   is worse than none, because it looks exactly like a receipt beside a success.

7. **Hypotheses before harnesses.** New experiments get an
   `ALIFE-EXP-nnn-*-preregistration.md` and a pinned corpus committed *before*
   the code that measures them, and a `RESULT.md` that names its own corrections
   rather than quietly absorbing them. `experiments/alife-exp-001/RESULT.md` is
   the template, including its second paragraph, which states the real strength
   of its own provenance.

8. **A null model, or no claim.** Sharing rises trivially when terms shrink and
   when bodies are culled from the census. Any claim about structure must be
   reported against a null that could have produced it by accident.

9. **`ALIFE-` identifiers.** Decisions are `ALIFE-ADR-nnn`, experiments are
   `ALIFE-EXP-nnn`. sigma-glyph has its own `ADR-nnn` and `EXP-nnn` and a
   `MAP.md` that resolves them; two repositories minting into one namespace
   break exactly the thing that map is for.

10. **The oracle is bytes, not a version string.** Every receipt records the
    SHA-256 of the `sigma_glyph.py` that produced it. "sigma-glyph 0.6.7" names a
    release; the digest names what ran.
