# Decisions

Every judgment call made in this repository, with what was rejected and what
would overturn it. It exists because the work is done by an agent at speed, and
speed hides reasoning: a reader who disagrees with an outcome should be able to
find the sentence where the outcome was chosen rather than reverse-engineer it
from the code.

**Split with `proposals/`:** an `ALIFE-ADR-nnn` is a full document for a decision
that shapes the repository. This file is the *log* — every call, including the
small ones and the wrong ones, one entry each, with a pointer where a document
exists. Entries are appended, never edited away; a decision that turns out badly
gets a new entry saying so, above the old one.

Author of every entry below: Claude (Opus 5), working under s0fractal's
direction. Nothing here was reviewed by a second party.

---

## 2026-08-25 — founding

**D1. A new repository, not an extension of `sigma-glyph`.** Accepted from the
founding proposal §6 as written. Added reason it did not give: this repository
must be free to be *wrong in public* — its first experiment refutes its own
founding hypothesis, which is a normal week in research and an incident in a
specification. → `ALIFE-ADR-001 §1`. *Overturned by:* the substrate stabilizing
enough that Book I would want it normatively; then it moves, it does not merge.

**D2. Identifiers carry an `ALIFE-` prefix.** The proposal numbered its
experiments `exp-005…` continuing sigma-glyph's sequence from a different
repository. sigma-glyph's `MAP.md` exists to resolve one cited identifier to one
document; two repositories minting into one namespace break exactly that.
Directory *shapes* still mirror sigma-glyph exactly. → `ALIFE-ADR-001 §2`.

**D3. `impl/sigma_alife.py`, one module, not `src/population.py` + friends.**
Follows sigma-glyph's flat layout for its stated reason: the file you read is the
file that runs. The "morphogenesis module" the proposal wanted is four functions
and lives beside the population it measures. → `ALIFE-ADR-001 §3`.

**D4. The population loop drives `step5`, not `eval_hash`.** Book I's exhaustion
outcome discards the partial term, which makes a resumable agent unbuildable.
Rejected alternative: accept `eval_hash` and drop RQ3 (sporulation) as
unimplementable — that would have thrown away the one capability this substrate
has that no other ALife platform does. The deviation is fenced by a differential
and by `resumption_bound`. → `ALIFE-ADR-001 §5`. *Overturned by:* Book I growing
a resumable outcome, at which point the driver should be deleted, not kept.

**D5. A slice that buys nothing is doubled, not fatal.** A slice smaller than the
next action's cost makes no progress, and a fixed slice livelocks a population in
silence. Rejected: a new `STALLED` status — it added a state to every caller for
a condition `spent == 0` already expresses.

**D6. `STARVED` means "the next action is unaffordable", not "the reservoir is
empty".** An agent can hold change too small to buy anything. Its dust returns to
the commons on culling rather than vanishing with the body, because a ledger that
loses ATP quietly is the failure mode the ledger exists to catch.

**D7. A materialized REF counts 2 in the census, not 1.** *This entry is a
correction.* The first version counted the node and not its target, so the census
sat one address below `size` on every REF while a docstring claimed the two
agreed "by construction". Caught by property P5, not by a suite. The size model
prices a REF at 2 — node plus target thunk — and the target is a real CAS address
other agents can share.

**D8. Rebates move ATP out of a commons pool; nothing is minted.** The proposal's
§4.3 would have created ATP from a sharing measurement. Every bound stated
against a total dies quietly the moment that happens, so the ledger is asserted
every tick and a negative control watches minted ATP get caught.

**D9. Lean proves `ReachFrom a b` (arbitrary start), not `Reach` (fixed start).**
Book I's form is recovered as the special case. Proving the general form first is
what makes D4 legitimate: an interrupted run must be bounded like an
uninterrupted one, or the sliced driver is not entitled to Book I's guarantee.

**D10. The proposal's "Conservative Transfer Safety" theorem was not proved; a
weaker hypothesis was.** The population bound mentions no per-agent reservoir, so
*any* conserving transfer preserves it, including one that strips a donor to
zero. The donor reserve survives as a heuristic for per-agent predictability and
is labelled as one. → `ALIFE-ADR-001 §7`.

**D11. `premise_guard.py` is weaker than sigma-glyph's `proof_guard.py`, and says
so.** It pins source text; the real one pins elaborated types against the kernel
environment. Rejected: porting the real guard now — it needs a `lake` build and a
second proof front to justify it. The scope limit is written in the file, in
`proofs/README.md`, and in the README.

**D12. Published public on GitHub.** s0fractal authorized "залий на гітхаб".
Public chosen without asking because `sigma-glyph` is public and this
repository's own `pyproject.toml` and README already declared the public URL.
*Overturned by:* one word.

**D13. CI pins sigma-glyph at `d3f1b51` (its `master`), not at the local
checkout's branch head.** The two are byte-identical on both consumed surfaces —
`impl/sigma_glyph.py` and `proofs/SizeBound.lean` — and `master` is the ref in
force. What would justify moving the pin is written above the pin.

**D14. The Lean guard fails on lean *diagnostics*, not on any output.** *This
entry is a correction, found by CI on the first push.* The first version failed
on any bytes at all, which is green on a machine whose toolchain is installed and
red on a fresh runner where `elan` downloads Lean inside that very subprocess. A
guard that calls the installer an unsoundness gets silenced rather than read.
Fixing it exposed dead code: the `sorry` test compared against straight quotes
where Lean 4.31 writes backticks, so that string had never matched anything.

**D15. Commit hygiene slip, corrected before pushing.** *This entry is a
correction.* `git add -A` swept the EXP-002 corpus and preregistration into the
engine commit, and in this repository commit order is the evidence that a corpus
was fixed before its hypotheses. Reset and re-committed in order. Nothing had
been pushed.

---

## 2026-08-25 — choosing ALIFE-EXP-002

**D16. The announced rebate economy was dropped in favour of memoization.**
→ `ALIFE-ADR-002`. Two reasons, in order of weight:

1. A rebate is a pressure hand-designed to reward the quantity being measured.
   Its result is knowable in advance and says more about the designer than the
   substrate.
2. A probe answered the question underneath it: **in Book I, sharing buys
   nothing.** The same hash evaluated twice by two agents costs `10/10`,
   `106/106`, `3981/3981` ATP. Sharing is a memory phenomenon there and never an
   energy one, so no population living on it has a gradient toward sharing to
   begin with, and a rebate is a coat of paint over that.

*Rejected alternatives, with reasons:* **drought/sporulation (RQ3)** — already
proved (`resumption_bound`) and differentially checked, so running it would dress
a theorem as a result; **evolutionary pressure on structure (RQ4)** — has no
mechanism until sharing costs something, so it belongs after this one, not
before.

**D17. The memo hook uses a mirror of `step5`'s dispatch.** A hit must land where
the machine actually demanded a hash. *Rejected:* (a) reimplementing the
evaluator inside this repository — it would make the differential a comparison
with our own copy; (b) installing normal forms eagerly wherever they appear — it
buys structure the run never asked for and the ATP figures stop meaning what they
say. The mirror is held to the machine by control M1 in one direction only, and
the unchecked direction is stated in the code, in the test output and in the
preregistration: a mirror that missed a force would make the memo timid, never
greedy.

**D18. The memo learns whole-agent normal forms only.** Sub-term memoization —
the version in which anastomosis would not need lineage — is not implemented,
because the machine never announces that a subterm reached a normal form, and
learning one needs either speculative evaluation nobody has priced or a
reimplementation of the evaluator (see D17). This is the single largest
limitation of EXP-002 and it is where a successor should start.

**D19. In Part B a child inherits the parent's ROOT, not its current term.** The
preregistration did not fix this and it decides whether the experiment can show
anything: a phenotype graft inherits a hash no memo has an entry for. Both arms
use the root, so it biases neither — but it was chosen by the author after the
fact and is named in the result.

**D20. The generational frame was corrected twice, both times *before* looking at
what H3 would say.** *This entry is a correction.* The committed frame
(tax 400) extinguishes the population in generation 0; the first repair
(tax 200) runs but lets the memo save 0.15% of the ATP flow, so both arms end
with the identical population and H3 cannot differ. The frame was re-chosen while
looking only at turnover, saving fraction and survivor-set overlap — deliberately
never at the sharing comparison. The condition is now machine-checked: **control
C7** refuses to adjudicate H3 on any run where the two arms end with the same
survivors.

**D21. The `composite` arm is post hoc and labelled everywhere it appears.**
Written after Part A measured essentially nothing, to separate "memoization does
not work" from "nothing in this population demands another agent's address". It
is in the table with an asterisk, in the receipt, in `measure.py`'s docstring and
in the result.

**D22. H1 and H3 are reported as FAILING against their preregistered criteria**,
even though H3 is in the predicted direction on two seeds of three and H1's
mechanism demonstrably works once a demand path exists. Rejected: restating the
criteria to fit. The interesting finding — sharing pays only where lineage
creates demand — is reported as what it is, a post-hoc explanation supported by
two unregistered arms, and not as a hypothesis that was confirmed.

**D23. The need packet for sigma-glyph is prepared here and NOT filed upstream.**
Pushing a branch and opening a PR against a governed repository is a distinct
outward-facing action from publishing this one, and s0fractal authorized the
second, not the first. The packet is complete and validated against
`decision-archaeology.need@v0`; filing it takes one word.

---

## 2026-08-25 — ALIFE-EXP-003

**D24. The experiment I announced last turn does not exist.** I proposed "memo hit
rate against mutation distance" and then checked whether it could fire before
building it. It cannot: a point mutation changes the hash of every node on the
path to the root and leaves the sibling subtrees alone, so a descendant demands
its own new root (never memoized) and surviving subterm hashes (which a memo
keyed by whole-agent roots does not hold). Measured: hits at distance 1, 2, 4, 8
were 2, 1, 0, 0 out of 8 — and the non-zero ones were mutations that happened to
replace an atom with the same atom. There is no gradient of genetic distance to
measure, only a binary: an agent either demands a known root or it does not.
Proposing an experiment and then killing it with a five-minute probe is cheaper
than preregistering it, so the probe is the rule and not the exception.

**D25. The library is funded by the COLONY, not by the agent that missed.**
Charging the first agent to demand a hash for deriving it makes that agent
subsidise everyone after it, and a substrate whose costs depend on arrival order
cannot be reasoned about. A colony-funded reservoir turns the mechanism question
into an economic one — *is this worth funding* — which is the question worth
asking and the one EXP-003 measures. → `ALIFE-EXP-003`.

**D26. `Memo.learn` no longer trusts its caller.** *This entry is a correction.*
Every call site guarded on `status == NORMAL`; the first thing that did not was
my own throwaway probe, which filed the DISSONANCE of an unresolved run. It would
have served that to every agent that asked afterwards. The guard moved into
`learn`: a term with an action left is refused, and so are `DISSONANCE(ATP
Exhausted)` and `DISSONANCE(Unresolved Reference)` — those are functions of a
budget and of a store, not of the hash. `DISSONANCE(Invalid Object)` is a function
of the bytes and is allowed. An API whose soundness depends on remembering to
check is a bug with a delay.

**D27. The library debits its reservoir up front.** *This entry is a correction.*
A fill can trigger a fill; the worker held a view of the reservoir and the outer
assignment overwrote what the nested one had booked, so the ledger lost ATP. The
consequence of the fix is stated in the code rather than discovered later: a fill
that has drawn the whole reservoir leaves nothing for a nested fill, so the
librarian does not file recursively. Subterms are filed when an agent demands
them directly.

**D28. `s = 0` means no memoization at all**, not a memo with an empty reservoir.
The second would have quietly included EXP-002's donation mechanism in the null
and understated the library. The donation mechanism is measured separately as the
`donation-only` diagnostic, which is **not** in the preregistration and is
labelled everywhere it appears. It produced 30 entries and 0 hits — EXP-002's
negative, reproduced in a different harness at a different scarcity.

**D29. The one tuned number was chosen blind, before any arm ran.** EXP-002 had to
learn this by wasting two frames (D20); here the scarcity level was picked by
running the `s = 0` arm alone and taking a level inside a 40–70% settle band, with
no library arm computed or guessed at, and two further levels preregistered so no
conclusion rests on one economy. Applying a lesson before the fact is the only
evidence that it was learned.

**D30. H3's verdict was not softened to fit.** *This entry is a correction.* My
summary code scored H3 as holding because the last delta exceeded the first. The
preregistration says the advantage *increases* with population size; +2, +7, +4
does not increase. The check is monotone now and H3 reads FAILS, in the
repository's first experiment that had a positive result to protect.

**D31. Agents count their own memo hits.** Added specifically so a colony-level
win can be *traced* rather than inferred: of the agents that settled in a library
arm and not in the null, 4 of 4, 10 of 10, 14 of 14 and 13 of 13 had bought at
least one memo install. Without that column the result would have been a
correlation between an arm and a count, with budget granularity as an untested
rival explanation.

**D32. No venue targets, no schedule.** s0fractal, 2026-08-25: these are our
experiments and they are not attached to anything. `ALIFE-ADR-001 §9` already
declined the founding proposal's 16-week plan and venue table as "a promise
nothing can check"; this makes it a standing direction rather than a one-time
rejection. Publish when there is something worth publishing, or do not.

---

## 2026-08-25 — after an external review (Claude Fable 5)

The review read the repository and returned eight criticisms. Six are acted on
below; the two that are not are named with reasons, because a review answered
selectively and silently is a review not answered.

**D33. The pricing claim was wrong by one, and it was published everywhere.**
*This entry is a correction, and the largest so far.* "Any price below `size(nf)`
breaks the memory bound" appeared in an ADR, two preregistrations, the README, the
engine, the test suite and a need packet about to be filed upstream. It is false
at `size(nf) − 1`: measured at the boundary, `k − 1` gives 0 violations of 60 and
`k − 2` gives 26. The claim had been generalized from a single measurement at a
flat price of 1 without ever checking where the boundary was.

The implemented number does not change and the reason does. Book I keeps two
things that differ by one: the **theorem** needs `Δsize ≤ Δcost` (floor `k − 1`),
and every **row** of §3.4 satisfies the stronger `Δsize ≤ cost − 1`, which a memo
install keeps exactly when the price is at least `k`, tightly at `k`. Both are
machine-checked now (`memo_discipline`, `memo_below_floor_breaks`) rather than
argued in prose. Preregistrations carry a correction note and their text stands;
ADR-002 carries an amendment. *Overturned by:* nothing — it is arithmetic, now
pinned.

**D34. A memo install is a constructor of the model now.** The review's sharpest
point: until this, the library arm of EXP-003 ran on a machine `Population.lean`
did not describe, with a runtime probe as the only thing behind its numbers.
`StepM` extends `Step` with the memo action; the population layer is stated over
the extended machine; `reachFrom_reachM` keeps Book I's own results as the
special case so nothing about Book I silently widened.

**D35. The guard pinned signatures and was blind to what they meant.**
*Correction.* Generalizing `Agent.run` from `ReachFrom` to `ReachM` changed what
`population_peak_size` asserts while leaving every pinned string identical. It
now pins all 26 declarations whole — structures, inductives, defs and proof
bodies — and a control confirms the narrowing is caught.

**D36. `sharing_factor` counts the alphabet, and the finding survived being told
so.** The review argued that EXP-001's headline could not be distinguished from
"reduction consumes the alphabet". Correct, and demonstrable: three agents that
all reduced to the leaf `I` score a perfect 3.0. ALIFE-EXP-004 was written to
kill the claim — H2 states that the drop *vanishes* under a metric that counts
only `APPLY` nodes and excludes genesis — and it did not: the drop survives in
10/10 seeds at every alphabet fraction, pairwise structural overlap falls with
it, and the dose-response the alphabet story predicts is absent. The objection
was right about the metric and wrong about the result, and both halves are in the
result document.

**D37. "Sharing buys nothing in Book I" was too broad.** The review pointed out
that `R-S` charges `1 + size(z)` on the *current materialization*, so duplicating
an unforced argument costs 2 rather than the size of the tree behind it —
verified: 2 against 14 for a 13-node argument. Laziness plus addressing is a
sharing discount that already exists in Book I. The claim should have been
"*reusing another agent's completed work* buys nothing", and measuring the
discount that does exist is now the first open question in the README.

**D38. Positioning exists now.** `RELATED.md`, naming AlChemy (Fontana & Buss)
and Combinatory Chemistry (Kruszewski & Mikolov) as the nearest ancestors, what
is different here (content addressing, a proved rather than bookkept resource
law, spec-fixed prices), and what they have that this does not (emergence — and
their answer to the degenerate attractor this repository walked into is better
than shaping a fitness function). Written from abstracts, and says so.

**D39. Not acted on: multi-model role separation.** The review's best
methodological suggestion — one model writes the preregistration, a *different*
one writes the harness seeing only that document — is right, and it is the only
available fix for this repository's weakest provenance claim. It is not done
because this session cannot spawn other agents. It needs s0fractal to route the
next preregistration to a different model. Recorded so it is not quietly dropped.

**D40. Not acted on: the EXP-003 arms never exercise resumption.** The review is
correct that reservoirs of 23–31 ATP against a slice floor of 32 mean every agent
gets its whole reservoir in one slice — verified. EXP-003 is not about
resumption, so this is a limitation rather than a defect, and it is now in that
result's limitations. What it does mean: no experiment here has yet exercised the
one capability the substrate proved.

---

## 2026-08-25 — ALIFE-EXP-005, written by two models

**D41. The role separation was executed, and it worked as advertised.** D39 said
the fix for this repository's weakest provenance claim needed s0fractal to route a
preregistration to a different model. Done: the EXP-005 preregistration is mine,
the harness is Codex's, written from the committed document and the engine API
without contact. Its yield was **seven underdefinitions found before any number
existed** — including the two that decide verdicts, since "wide margin" and
"materially fewer" were left numeric-free and the harness author had to fix `2×`
and seven-fewer-settlers himself. A preregistration whose thresholds are invented
by its implementer is not preregistering those thresholds. *Practice adopted:*
every hypothesis gets a number, in the document, before it is filed.

**D42. I preregistered a hypothesis my own frame made unfalsifiable.**
*Correction, and the sharpest of the session.* `ATP_PER_AGENT = 3000` was chosen
"as EXP-001: enough that everyone settles", and H2 then asked whether fewer would
settle. Enforced copy pricing costs 0.08% more per agent at that budget. H2's
verdict is UNDERPOWERED, not FAILS. This repository added control C7 to two
experiments precisely to stop this, after wasting two frames on it in EXP-002, and
then walked into it in a document it wrote three days later. *Practice adopted:*
the power condition is not a control inside a harness — it belongs in the
preregistration, next to the hypothesis it protects.

**D43. The delivered result was not rewritten.** Codex's `RESULT.md` keeps its
text and its scorecard; the correction is a marked review note beside the row it
corrects, plus an addendum below, both attributed. Rewriting another author's
verdict in place would destroy the only evidence that the separation happened.

**D44. The addendum reuses the harness rather than reimplementing it.**
`addendum_scarcity.py` calls `measure.run_arm` at other budgets. Reimplementing
the arms would have put a second thing between the question and the answer, and
the addendum questions the preregistration, not the implementation. Its numbers
were verified first: an independently written R-S detector reproduces the
harness's counts exactly, family by family.
