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

---

## 2026-08-25 — ALIFE-EXP-006, the theorem finally used

**D45. The power condition went into the preregistration, not the harness.** D42's
lesson, applied: the document fixes a 25–75% settle band for the equal arm and
says the run is UNADJUDICATED outside it, and the total was chosen blind by
running that arm alone. It landed at 73% — inside, and close enough to the edge to
be worth saying.

**D46. Every threshold was a number before the harness existed.** D41's lesson:
"≥ 8 agents", "doubles between 2 and 32 pulses", "25–75%". EXP-005 showed what
happens otherwise — its implementer had to invent `2×` and seven-fewer-settlers,
and said so. With no second model available for this one, numeric thresholds were
the only compensation on offer.

**D47. Integer division nearly produced a finding.** *Correction.* The allocator
wrote `budget // n`; at 32 pulses that is `62 // 64 = 0`, so every agent received
nothing and the equal arm settled 0 of 64. The first grid showed a dramatic
collapse at fine granularity that would have been reported as a result about
pulse size. It was a division. Fixed by distributing the remainder, and the
concentration policies now pass leftover down the order after an agent settles,
which is what the preregistration had said and the code had not done.

**D48. A settled agent returns its unspent ATP at the end of a pulse.** Not
specified in the preregistration; decided here and applied identically in every
arm, because otherwise a policy that settles agents early is penalised by ATP
frozen inside them.

**D49. H3's explanation is post hoc and labelled.** The premium plateaus because
the resuming arm hits the budget ceiling — 47 of 64 is all 2000 ATP can settle —
while the restarting arm degrades monotonically (25, 21, 20, 16, 16). That reading
was formed after seeing the numbers. The preregistered statement was about the
gap; the gap does not grow; H3 fails.

---

## 2026-08-25 — ALIFE-EXP-007, where every criterion was met and none survived

**D50. The preregistration required a null for one metric and not for the other
two.** *Correction, and the pattern is now three for three.* EXP-007 conditioned
its closure hypothesis on diversity — a null of sorts — and preregistered nothing
for the L1-core or for the cross-budget overlap. All three criteria came back
green; post-hoc nulls then refuted the core (a shuffled graph of the same density
scores higher), showed the overlap statistic to be uninformative (the soups
overlap even less than the cores), and reproduced 85–97% of the closure by
shuffling the product order. *Practice adopted:* **every statistic that can be
met by chance gets its chance model named in the preregistration, beside the
threshold.** ALIFE-EXP-001 needed a null and had one; EXP-004 needed one and had
one; this needed three and had none.

**D51. The nulls went into the harness and the receipt, not into a scratch
script.** They were found with a throwaway probe and would have stayed there. A
null that is not replayable is an assertion, and this repository has spent five
experiments learning not to make those.

**D52. The exemption for the slow replay is named, not blanket.** The soup replay
is a ten-minute job and now runs in its own path-filtered workflow, on the
sigma-glyph exp-004 precedent. `tools/test-all.sh` would have reported it as a
skip and exited non-zero, and the lazy fix — `ALLOW_SKIPS=1` in CI — would have
swallowed a missing `lean` or an unreachable validator with it. `EXP007_ELSEWHERE`
exempts exactly one surface, because another job covers exactly that one.

**D53. Reported honestly rather than kept.** Three green criteria are the first
time this repository has had a positive result to lose by looking harder. It
looked, and the result says "not established, artifact, uninformative" in its own
scorecard. What survives is narrower and worth more: a closure statistic and an
L1-core over a bounded high-turnover soup are met by chance, and anyone measuring
organization that way — including this repository an hour earlier — needs the
shuffled-graph null beside the number.

---

## 2026-08-26 — ALIFE-EXP-008, and the rule D50 was missing

**D54. One permutation is not a null.** *Correction, and it reversed a result.*
EXP-008 drew a single shuffle per window. It came back empty everywhere, H1 held,
and a positive result was written and nearly shipped. Twenty draws and a
worst-case statistic reversed it. The expensive part of these experiments is the
soup — ten minutes; a permutation and a peel are milliseconds. *Practice adopted,
extending D50:* **a chance model must be sampled, not consulted once**, and the
number of draws goes in the receipt beside the statistic.

**D55. A stronger null is a different claim, and the weak one is nearly free to
beat.** A complete shuffle destroys every structure at once, so anything at all
clears it. EXP-008's preregistered null was that, and H1 holds against it. A null
that preserves temporal locality — same recent products, only *who made what*
destroyed — matches or beats the observed set at 6 of 7 windows. The honest report
carries both, and says which was preregistered. *Open, and named:* neither is
obviously the right chance model, and a degree-preserving rewiring would be a
third answer.

**D56. The harness chose a window on the data, against the document that
forbade it.** *Correction.* It took the window maximising the observed set —
listed in the preregistration under "what would make this experiment worthless" —
and picked one where the null already scored 16. Replaced first by a null-driven
rule, which collapsed under a sampled null, and finally by no selection at all:
the whole curve is scored against both models, as the document said from the
start. Writing the rule down did not stop me implementing its opposite; only
re-reading the document against the code did.

**D57. Two positive results died in two experiments, both to nulls, both post
hoc.** EXP-007 met three criteria and lost all three; EXP-008 met its first and
lost it to a stronger chance model. Neither null was preregistered. That is now
the single most reliable way this repository finds its own errors, and the least
preregistered part of its method.

---

## 2026-08-26 — paying down D57

**D58. The chance models are infrastructure now, not per-experiment code.**
`impl/sigma_nulls.py` holds three, each destroying exactly one thing and holding
the rest fixed — which pair made what (everywhere / only within a window), and
when a reaction happened. `tests/alife_nulls.py` checks what each one *preserves*,
because a null that quietly destroys more than it advertises makes any statistic
significant. Every model returns a sampled distribution; none returns a graph.

**D59. A spelling rule beats a good intention.** `tools/receipt_guard.py` walks
every committed receipt, finds every key that names a null, and demands a draw
count of at least 20 reachable from it. It cannot tell a good chance model from a
bad one and does not pretend to; it can tell that nobody sampled one, which is the
error that actually happened, twice.

It found three things on its first run:
  * **ALIFE-EXP-001's nulls were single draws**, in a published receipt. Sampled
    now, and the verdict got *stronger*: the settled population sits below the
    size-matched null's minimum over twenty draws, so H2's failure never depended
    on which draw was reported.
  * **ALIFE-EXP-007's nulls were single draws too.** Its two headline verdicts
    survive sampling; its closure residual does not — it falls from
    +0.012…+0.065 to −0.008…+0.044, so a number this repository published as
    "consistently positive across four cells" is not.
  * **ALIFE-EXP-003 was calling a control arm a null.** The `s = 0` colony is a
    deterministic arm, not a chance model. Renamed `no_library`; no number moved.
    The guard was right to ask what the word meant.

**D60. The guard was wrong first, and was fixed rather than exempted.** Its first
version looked for the draw count in the same object as the null's *name*, so a
receipt that declares draws per cell — which is where the number belongs — was
reported as an offender. Loosening a guard to fit a receipt is how guards die; the
rule is now "findable from the thing it describes", which is what it should have
said.

**D61. CI was sized to the measurement, not the measurement to CI.** The soup
replay job was cancelled at its 30-minute limit. The cost is not the nulls —
twenty draws over the whole grid are under a second — it is the reactions priced
at 3000 ATP, at 101 seconds per soup, three seeds in each of two experiments. The
two replays are separate jobs now, running in parallel, with a 45-minute limit
each. Trimming the corpus or the budget sweep would have been changing a result to
fit a runner.

---

## 2026-08-26 — filed

**D62. DA-SIGMA-0002 is filed, on a branch, unmerged.** s0fractal authorized the
filing and asked explicitly that it not be merged, so it goes through review:
[s0fractal/sigma-glyph#25](https://github.com/s0fractal/sigma-glyph/pull/25),
`needs/da-sigma-0002-memo-pricing` → `master`.

How, and what was checked:

  * **On a worktree, never on their checkout.** sigma-glyph was sitting on
    `spec/adr-009-candidate`; a branch checkout there would have moved somebody
    else's working tree. A temporary worktree from `origin/master` left it
    untouched, and was removed afterwards.
  * **Branched from the exact revision the packet names.** `origin/master` is
    `d3f1b51`, which is the manifest's `target.revision` and this repository's own
    `SIGMA_GLYPH_PIN`. The packet is filed against the commit it was measured on.
  * **The reproducer was run inside their checkout**, against their
    `impl/sigma_glyph.py` (SHA-256 `413d1f98…`, the digest the packet cites), and
    printed `DA-SIGMA-0002: REPRODUCED`.
  * **Their CI validated it**: `test`, `lean`, `cross-repo`, SonarCloud and
    GitGuardian all pass on the PR, and their `test` job runs the pinned
    `needs@v0` validator over the packet.
  * **Nothing claims review or adoption.** The commit says in as many words that
    no gate was run, no roster saw it, and merging would record demand and routing
    only. The disposition stays `untriaged` — that field is theirs to write, not
    mine, and writing it would be the false-provenance failure their `AGENTS.md`
    exists to prevent.

**D63. Two polling loops of mine had been spinning for two and a half hours.**
*Correction, in my own housekeeping.* `until grep -q "oracle:" <file>; do sleep 30;
done` waits forever when the run it watches dies with a traceback instead of
printing that marker — which is exactly what happened twice while EXP-008's
harness was being fixed. Later loops match `oracle:|Traceback`; the two survivors
were killed. A wait condition that only recognises success is a hang with a
schedule.

**D64. I filed a question about a specification without reading the section that
answers it.** *Correction, and the most embarrassing one here.* DA-SIGMA-0002
asked whether Book I permits reusing a result. §3.4's last sentence says it does:
sharing MAY be used in execution, the reported ATP MUST match tree accounting. I
had read §3.4 — the memory bound and the seven priced actions are copied into
`proofs/Population.lean` from it — and stopped at the part I needed.

The failure mode is specific enough to name: **I searched for the word and
concluded from its absence.** "Memoization" does not appear in Book I, so I
reported that the specification never discusses it. What the specification
discusses is *sharing*, in the accounting section, in one normative line. A
grep-shaped absence is not a spec-shaped absence. *Practice adopted:* before
claiming a specification is silent, read the section that owns the contract end
to end, and quote the sentence that would have said it.

Found by an external review (Codex), verified by me against the pinned revision
before anything was written. Corrected on top of the filed commit rather than by
force-push: the wrong version stays readable at `2dc2a4e`, because an error that
vanishes from the history is an error nobody can learn from.

**D65. A reproducer whose verdict does not depend on its numbers is a press
release.** The filed fixture's success predicate read `broke > 0 and diverged` and
ignored every measurement. The same review mutated the arm carrying the packet's
central claim so that it *contradicted* the packet, and the script still printed
`REPRODUCED` and exited 0; a comment appended to the oracle changed the digest and
it reported success against a machine it was not measuring. Both are now caught
and both are demonstrable in reverse. This repository already had the rule for
its own harnesses — every experiment scores against pinned values — and did not
apply it to the one artifact it sent to somebody else.

---

## 2026-08-26 — a survey from Grok, and what was left of it

**D66. Half of a research survey was already done, and saying so is the useful
part.** Grok proposed seven directions. Checked against what is committed:

  * *"formalize in Lean: any redistribution preserving total ATP preserves the
    population bound"* — that is `transfer_preserves_bound`, proved on day one,
    and `ALIFE-ADR-002 §7` is about why its triviality is the point.
  * *"introduce heredity with mutation plus ATP selection"* — that is
    ALIFE-EXP-002 Part B, which found the degenerate attractor: selection for
    settling cheaply drives mean term size to 2.8–3.4 nodes, the SKI equivalent
    of breeding for the empty program.
  * *"resumption gives ~3× more settled agents"* — the best case. Measured:
    1.52× at 2 pulses, 2.35× at 8, 2.94× at 32. The range is the finding; the
    maximum is a headline.
  * *"automatic generation of null models"* — `impl/sigma_nulls.py` and
    `tools/receipt_guard.py`, D58–D60.
  * *"toxins and antibodies — terms that lower another agent's ATP on apply"* —
    not expressible. A term cannot touch another agent's reservoir: ATP is
    bookkeeping outside the machine. It could be built as an economy *policy*,
    and calling it a property of terms would misdescribe the substrate.

What was genuinely open and cheap: the ceiling's decomposition, which two
independent reviews raised and which needed **no new measurement at all** —
the receipts were on disk. Done as `analysis-001`, and labelled *descriptive*:
no hypotheses, no preregistration, no nulls, because it takes no measurement.
Gated anyway, since it states numbers about this repository's own results and
nothing else would notice a receipt moving underneath it.

**D67. The finding worth keeping from it.** The two halves of the slack are not
two views of one thing. Across an alphabet sweep the morphological factor moves
30 points and the metabolic factor moves 4; over a single run the morphological
factor freezes after the first tick while the metabolic one decays monotonically
to 16.6%. An operator sizing memory from the theorem overpays about 16×, of which
roughly 6× is budget that never became structure and 2.6× is structure held more
than once — the first a property of the terms, the second of the alphabet. They
should be estimated separately, and until now they were multiplied together.

---

## 2026-08-26 — ALIFE-EXP-009

**D68. Preregister the CEILING of a statistic, not only a threshold on it.**
*Correction, and the third of its family.* EXP-009's H1 asked for ≥ 30 recovered
agents, chosen from a blind probe saying 51 agents block. Nobody asked how many of
those 51 could settle *even with the hash present* — and before a delivery bug was
found, that ceiling was 17. H1 could not have held at any magnitude of the real
effect. EXP-005 preregistered a budget at which its H2 could not be true (D42) and
EXP-006 nearly did the same. *Practice adopted:* every numeric threshold gets the
maximum attainable value of its statistic computed beside it, in the
preregistration, and a threshold above the ceiling is a defect in the document.

**D69. An exact-value hypothesis caught a defect a soft one would have hidden.**
H3 demanded **exactly 0** ATP spent while waiting, because Book I says a failed
resolve is not charged. The first run reported 432, which cannot happen — and it
was real: the environment was delivering the withheld term's ROOT NODE and not the
term, so an agent forced the arrived `APPLY` for 3 ATP, got two thunks whose bytes
had never been stored, and blocked again on a child. Twenty-eight charged retries,
every one of which had changed the term. A threshold like "waiting is cheap" would
have passed and shipped the bug with the result.

**D70. The engine's default was not changed, and that is the decision.** Treating
`UNRESOLVED` as terminal discards agents Book I calls waiting — measured: 45 of
64, recoverable for 337 ATP. The fix is one line. It is **opt-in**
(`Population(..., wait_on_unresolved=True)`) and `RUNNABLE` is untouched, because
flipping the default would change every experiment already committed here and
silently move seven receipts. An unattractive default that keeps the record
honest beats a better one that rewrites it. New work should pass `True`.

---

## 2026-08-26 — re-checking the three unadjudicated verdicts

**D71. "No power" here never meant "not enough machine", and the record now says
so.** s0fractal asked whether the three UNADJUDICATED verdicts could be
re-checked now that the work runs on an M4 Pro with 48 GB. They could not have
been caused by hardware: peak resident memory of the heaviest run in this
repository is **25 MB** and the full grid finishes in seconds. Power here is a
property of the *design* — whether the frame could have shown an effect at all —
and each of the three failed for a design reason:

  * **EXP-002 H2** — the memo fired ONCE on the preregistered corpus, because a
    memo is keyed by what agents ask for and those agents never asked for each
    other's addresses. Nothing to compare.
  * **EXP-005 H2** — the preregistered budget was chosen so that everyone settles,
    and the manipulation cost 0.08% (D42). Already answered post hoc by that
    experiment's own addendum: it binds between 25 and 62 ATP per agent.
  * **EXP-008 H3** — no self-maintaining set survived the stronger null, so there
    was nothing to price.

**D72. More machine did buy one real thing: scale.** Only EXP-008's H3 was
plausibly a *length* problem rather than a design one, so it was re-run at ten
times the reactions and four times the seeds — 242 s of CPU in 23 s of wall clock
across twelve workers, which is what the extra cores are actually for. The verdict
does not move (**0 of 84 cells** clear the locality-preserving null; the observed
set is zero nearly everywhere), and the negative is now ten times longer and four
times wider.

What the scale run found instead is better than the verdict it failed to change:
**the chemistry prices itself out of its own budget.** Reaction success falls from
54% to 16% while the per-reaction budget never changes — products accumulate
structure, the next reaction has to reduce a bigger term, and 200 ATP stops
affording it. Five of twelve seeds end below the eight-hash diversity floor
EXP-007 preregistered, two of them at *two* surviving molecules; seven hold
between 20 and 46. And one seed falls to six molecules while its success rate
*rises* to 93.7% — a cheap cycle that found an attractor it can afford, which is
what an organisation would look like here, and which the self-maintenance metric
scores zero because those molecules are not producing each other.

The successor question is sharper than the one it replaces: any long-run
organisation in this chemistry has to be made of reactions that stay affordable,
so the test is a budget that scales with the soup — not more seeds.

**D73. EXP-002's H2 was adjudicated without taking a measurement.** Its own
post-hoc `composite` arm fired the memo 41 times, and the committed receipt
already held everything needed: occupancy 2.74% → 2.88%, tighter by 1.05×, by the
mechanism H2 named — the ceiling falls because the memo spends less. Recorded as
an addendum that reads the receipt rather than a re-run, and labelled post hoc,
one arm, one seed.

---

## 2026-08-26 — ALIFE-EXP-010, what the preregistration did not say

Recorded **before** the measurement ran, per the ALIFE-EXP-005 arrangement. The
preregistration (`experiments/ALIFE-EXP-010-…-preregistration.md`, committed
2a3ff65) says of itself that if it is not enough, that is a defect in it. These
are the places it was not enough, and what the harness did instead. D77 is the
one the RESULT has to carry as a correction rather than a choice.

**D74. An "individual" is a molecule-life, because EXP-007 has no other census.**
The prereg is written in the vocabulary of a population — living molecules,
death-causes, a census that reconciles — and the arm it pins as Arm E is
EXP-007's soup, which is a list of 64 *hashes* plus 1000 throwaway reaction
agents. Neither of those alone is a census. The harness unifies them: one
**individual** is one molecule-life. The 64 founders are born alive at tick 0;
each reaction is born as a root thunk, and a reaction that settles *becomes* the
living molecule its product names. The soup is therefore a list of individuals
rather than of hashes, with positions preserved exactly so that `rng.choice` and
`rng.randrange` consume the same randomness EXP-007 consumed (C3 would not
survive otherwise). C7's partition — alive, consumed, culled, starved, waiting,
faulted, unresolved — is over individuals and is checked to be a partition on
every tick of both arms.

**D75. A consumption eats the earliest-born copy.** The soup can hold several
individuals with the same hash; the prereg requires "at least one" and does not
say which. Lowest birth index, for two reasons: it is deterministic without
drawing on the RNG, which C4 needs, and eating the youngest would preferentially
consume the molecule just made, which is a different chemistry from the one being
priced.

**D76. "Not the substrate itself" is read as "a different individual from the
reacting agent".** A running reaction is not a member of the soup, so every soup
molecule carrying the demanded hash is a different individual and qualifies.
Note what this does *not* do: EXP-007's reactants are not consumed by their
reaction, in either arm. K&M consume reactants; this substrate does not, and the
prereg's own last bullet already says Arm M is K&M-inspired pricing inside this
substrate rather than their reactor.

**D77. The consumed individual's reservoir is zero here, so the transfer clause
is inoperative — and this is the one instruction that could not be honoured as
written.** EXP-007 endows a reaction, and returns its unspent remainder to the
commons the instant it settles (`econ.collect`). A molecule sitting in the soup
therefore holds no ATP at all, and "the consumed individual's remaining ATP
transfers in full to the duplicating agent" moves 0 every time. Giving molecules
a reservoir means not collecting — which moves `pool_left`, one of the frozen
EXP-007 numbers C3 requires Arm E to reproduce *exactly* — and doing it in Arm M
alone would be a second difference between the arms, which the prereg forbids in
the same paragraph. The two constraints cannot both be met, so C3 wins and the
transfer is implemented as a real code path that is measured and always moves
zero. The consequence for the design's stated reasoning is that
`transfer_preserves_bound` is cited for a redistribution that does not occur;
conservation in Arm M is preserved for the more boring reason that nothing moves.
The RESULT reports this as a correction, not as a detail.

**D78. Which bound Arm M keeps, and why the engine's probe is not asked to
assert it.** Book I's per-agent bound `size <= s0 + spent` is a corollary of
`Δsize <= cost - 1`, a property of Book I's *price*. Matter-priced `R-S` charges
the floor and grows the term by `size(z) - 1`, so it breaks that premise for any
`z` larger than a leaf — deterministically, not occasionally. What survives is
the **matter** statement, which is the one the arm is actually about: the body
consumed leaves the census carrying at least as much material as the copy adds.
Checked two ways in both arms, every event and every tick — (a) per consumption,
`size(consumed) >= size(z)`, which holds because a soup molecule is a normal form
or a founder and so is fully materialized while the `z` inside the agent may
still be part thunk; (b) per tick, the census bound
`Σ size(alive) + size(running) <= Σ s0 + Σ spent`. The Book I per-agent
violations are *counted* and reported rather than suppressed: they are the
expected consequence of the arm, and a receipt that showed zero because nobody
looked would be the bookkeeping bug the prereg warns about, in reverse. The
engine's `probe` asserts the Book I bound over a gated action exactly as it does
over every other one — so Arm M must run with `probe=False`, which is the
honest form of the statement, and Arm E keeps the probe on every action it
takes.

**D79. H3's "final window" is the last 100 reactions.** The prereg names a
final-window success rate and never sizes the window. 100 is EXP-007's own trace
granularity, the smallest window its frozen receipt can express, and it was fixed
before any Arm M number existed. The last 200 and last 400 are reported beside it
as a sensitivity and score nothing.

**D80. A reaction's success is attributed to the reaction that started it.** A
matter-blocked reaction that resumes three hundred reactions later and settles
counts as a success in the window it was *born* in; one still parked at the end
counts as not-successful. Attributing it to the window it finished in would put a
window's numerator and its denominator on different populations.

**D81. Blocked agents are woken by address, not by polling.** Parked agents are
indexed by the hash they wait on and woken the moment a molecule with that hash
enters the soup. This is equivalent to retrying everyone on every reaction — a
retry that finds nothing spends nothing and changes nothing, which is exactly
what C6 measures — and three orders of magnitude cheaper. Waking order is birth
order and draws no randomness.

**D82. A Jaccard over two empty survivor sets is undefined and does not help
H1.** EXP-007's helper returns 1.0 for an empty union, which would be a claim.
H1 asks for overlap < 0.5 in at least 2 of 3 seeds; a seed where neither arm has
one non-genesis survivor has no overlap to report. It is reported as undefined
and does not count toward the 2-of-3 in either direction. Fail-closed, the C2
principle applied to a metric.

**D83. C6's "uninterrupted evaluation" is the oracle's own normal form.** A
rerun of Arm M without waiting is not available — a block is a fact about the
census at one instant, not a switch — so the reference for a resumed agent's
answer is `sigma_glyph.eval_hash` on the same root against the final store at a
budget large enough to finish. That is stronger than the rerun the prereg
imagines: it says the matter arm's answers are Book I's answers, which is the
property EXP-009 established and the one that matters here.

**D84. C0, a control the preregistration does not have.** The whole arm rests on
one new mirror, `sigma_alife._next_redex`, agreeing with the oracle about which
action is next. A mirror that was wrong would re-price something that is not an
`R-S`, or miss `R-S` entirely, and every number in the receipt would be a bug
wearing a hypothesis. C0 runs the corpus through both and requires every
predicted `R-S` to be a real `R-S` fired by the oracle at the oracle's own price,
and every non-`R-S` prediction to leave the oracle's action alone. Controls are
additive: one the prereg did not think of is not a deviation from it.

**D85. The organization statistic is scored against both nulls up front, not
when it becomes tempting.** The prereg preregisters EXP-008's two nulls so that a
post-hoc organization observation can be scored immediately — D50's defect being
that it could not be. So the L1-core of each arm is computed and scored against
`shuffle_products` and `shuffle_local` for *both* arms by the same code path, at
20 draws, and the receipt carries the result whether or not the RESULT says
anything about it.

**D86. The engine gained one hook, `reduce_slice(..., duplication_gate=...)`,
and one status, `BLOCKED`.** The alternative was a second driver inside the
harness, which is what ALIFE-EXP-009 did for its one-bit arm and what would be
wrong here: EXP-009's arm changed the *scheduler*, this one changes a *price*
inside the reduction loop, and a copied loop would make "identical in every
respect except the pricing of duplication" true only to the extent the copy
stayed faithful. The hook is inert unless passed — `BLOCKED` is not in
`RUNNABLE`, no existing caller supplies a gate, and the 29/29 gate, the
differential suite, the conservation suite, the memo suite and the nulls suite
are all green before and after. `BLOCKED` is kept distinct from `UNRESOLVED` on
purpose: an unresolved agent waits on the STORE and a blocked one on the CENSUS,
and merging them would make EXP-009's measurement unreadable.

**D87. C0c, the second control the preregistration does not have: the hook has
to be falsifiable.** D86 put a pricing hook inside the shared reduction loop, and
"the arms differ in one price" is then a claim about that hook rather than about
the design. So the hook takes a second gate that prices `R-S` at Book I's own
`1 + size(z)` and always affords — the identity on the chemistry — and C0c
requires Arm E driven *through* it to produce a receipt identical to Arm E on the
oracle's untouched dispatch, on all three seeds. C3 then says the ungated Arm E
is EXP-007, C0c says the gated path is the ungated path, and C0 says the mirror
is the oracle's own dispatch; the three together are what let Arm M's numbers be
about a price. It also supplies the only honest way to count how many
duplications the *energy* arm performs, which is the denominator every Arm M
statement is implicitly against.

---

## 2026-08-26 — ALIFE-EXP-010 after an adversarial review

Codex reviewed `97bc847` and returned CHANGES REQUESTED
([`reviews/codex-2026-08-26.md`](reviews/codex-2026-08-26.md)). Two of its
findings were verified independently before it was committed. The
preregistration author owns the design-level defects — compound intervention,
attractor language — in `reviews/claude-fable-2026-08-26-exp010-response.md`.
These four are the harness's, and none of them moves a verdict: H1 HOLDS, H2
FAILS, H3 FAILS, exactly as scored. What moves is the descriptive numbers and
what they are called.

**D88. `waiting` is a third terminal outcome, and H3's window is reported as an
interval.** The first harness folded every outstanding wait into `fail`, which
made a reaction that is *unresolved at the observation horizon* indistinguishable
from one that starved. It is also arm-specific censoring: Arm E has no parked
state at all, and inside Arm M a reaction born at 950 has had fifty reactions to
be woken while one born at 100 had nine hundred. The receipt now carries
`terminal_settled`, `terminal_failed` and `terminal_waiting` separately, and
`window_outcomes` splits every window three ways with a `[rate_lower,
rate_upper]` interval — the lower end being the preregistered statistic and the
upper end the rate that would obtain if every outstanding wait were eventually
answered. **The preregistered scoring is untouched and H3 still fails 1 of 3.**
The interval is reported beside it because the sentence "M's success rate is
lower" is only honest with the censoring in view. The word "permanent" is gone
from the RESULT: nothing here ran the environment forward to show a copy can
never arrive, and "permanent" is a reachability claim.

**D89. Three ATP quantities, named apart, because the first receipt reported one
of them under the others' name.** The withdrawn 0.8%–7.0% figure divided
`rs_atp` — R-S spend over *every* reaction — by `ok × mean_cost`, which is the
spend of the *settled* reactions only. Numerator and denominator were over
different populations. The receipt now emits `spent_total`, `spend_settled`,
`spend_failed`, `spend_parked`, `held_terminal` and the identity
`pool + held + spent = endowment` (control **C9**, which is new and can fail),
and reports two estimands rather than one:

  * **R-S share of spend** — `rs_atp / spent_total`: what this arm charged for
    duplication as a fraction of everything the colony spent;
  * **counterfactual price saving** — `(rs_book_i_atp − rs_floor_atp) /
    spent_total`: the price intervention itself, evaluated on *one arm's own
    trace*. It is not recoverable from the difference of the two arms' totals,
    because the arms take different trajectories, and the first RESULT's
    cross-arm reasoning was wrong for that reason and not only arithmetically.

Both counterfactual prices are functions of `size(z)`, so `rs_zsize_hist`
carries the per-event pair the review asked for in full, without putting 1858
rows in a receipt.

**D90. Victim-hash multiplicity is recorded, and it refutes the mechanism the
first RESULT proposed.** "Eating a duplicate spends redundancy, not population"
was an explanation with no measurement under it: the gate proved only that *some*
living body carried the demanded hash, never how many. Every consumption now
records how many living bodies carried it the instant before — after is
`before − 1` by construction — and the answer is that **74.7%, 77.2% and 90.3%
of consumptions ate the last living copy of that hash.** The redundancy story is
not merely unmeasured, it is contradicted by its own event-level statistic. The
fuller mediation Codex specifies (the counterfactual cull that would have
occurred) is left to the successor and named as left, not done; product novelty
is already in the receipt as `1 − closure`.

**D91. ALIFE-EXP-010 replays in both profiles of `test-all.sh`, and three guards
gained the negative controls they never had.** The experiment sat in the
repository with no replay behind it: the advertised matrix was green while its
headline could rot. It costs about half a minute, so it is **not** behind
`RUN_SLOW` — the ten-minute soups are the only replays that get to be optional,
and a cheap experiment hiding behind an expensive one's exemption is how a
coverage hole is made. Also:

  * `tools/receipt_guard.py` searched arbitrary siblings for a draw count, so
    one unrelated subtree with `draws: 20` licensed every null beside it,
    including one drawn once. Codex supplied the reproducer. The rule now binds
    a count to the null it describes or to that null's own parent, never to a
    sibling, and `--self-test` runs four mutations (deletion, undersampling,
    the borrowed sibling, a nested small count) and two clean cases. All
    fourteen committed receipts still pass, so the fix has no false positives.
  * `tests/receipt_identity_guard.py` is new and states the thing the review
    said in prose: a shape guard cannot see a changed result. Six scored-field
    mutations — a flipped verdict, H3's seed count raised to its threshold, the
    withdrawn ATP share put back — must be invisible to the shape guard and
    caught by the identity diff.
  * `tests/exit_status_guard.py` resolved the oracle path only as written, and
    `ORACLE_SOURCE` is normally relative, so its throwaway tree under `/tmp`
    could not find `SizeBound.lean` and the guard printed FAILURES PRESENT on a
    repository whose every gate was green. One `.resolve()`. It is why the
    canonical command was not terminal, and the canonical command is now
    documented at the top of `test-all.sh`.

---

## 2026-08-27 — ALIFE-EXP-011, what its preregistration left to the harness

Recorded before the measurement was recorded, per the ALIFE-EXP-005 arrangement.
The preregistration
([`experiments/ALIFE-EXP-011-does-food-help-preregistration.md`](experiments/ALIFE-EXP-011-does-food-help-preregistration.md),
`a1ef892`) delegates one number explicitly and leaves five things implicit.

**D92. The budget is 32 ATP per agent, chosen from a dry run that read nothing
but starvation counts.** The preregistration says "budgets chosen so that a
preregistered fraction of agents starve mid-run" and permits the dry run to
observe starvation counts only. Both halves were fixed in `corpus.py` before the
dry run ran: a pinned sweep `(8, 12, 16, 24, 32, 48, 64, 96, 128, 256)` and the
rule *take the budget whose ever-starved fraction is closest to 0.50, ties toward
the smaller*. The sweep came back 85.9%, 85.9%, 75.0%, 56.2%, **46.9%**, 26.6%,
15.6%, 12.5%, 6.2%, 0.0%, so 32 wins. The whole sweep is in the receipt, and
`--dry-run` prints starvation counts and nothing else — no survival, no feeding,
no ATP — so re-running it cannot leak a hypothesis.

**D93. The commons needs a reserve, because ALIFE-EXP-001 left it empty.**
EXP-001 builds `Economy(3000 × 64)` and endows every agent, so its pool is zero
and `phase_share` cannot grant anything at all. An experiment about feeding needs
something to feed from: the economy here is `Economy(budget × 64 + 200 000)`.
The reserve is far above any plausible draw, and if it ever bound, C2 fails
closed — a grant truncated by an empty commons is exactly an insufficient one,
and the harness counts truncations separately for that reason.

**D94. Arm (a) runs the engine's rebate at rate 1.0; arms (b) and (c) run it at
zero.** Arm (a) is "the existing `phase_share` path where it fires naturally", so
it must actually be switched on — a rate of 1.0 grants one ATP per shared node
occurrence an agent holds, comfortably above a next action's price, so arm (a)
cannot fail for want of generosity. Arms (b) and (c) turn the rebate off so their
feeding is exactly the forced grant and H1 is adjudicated on that and nothing
else. `transfers` is off in every arm: the preregistration's arms name
`phase_share`, and leaving `phase_interact` on would add a second uncontrolled
feeding path to a three-arm design.

**D95. Arm (c)'s cull-free window is `phase_cull` returning without culling on a
tick where feeding happened — which is `step(cull=False)` for exactly that
tick.** The preregistration asks for feeding "applied in a tick where cull is
skipped (`step(cull=False)`) before the agent's next `phase_reduce`", and the
harness cannot know in advance which ticks those are, because the feeding happens
inside `step`. So the decision is made inside the tick, by the arm's own policy
object, and the engine's `step` is called identically in all three arms. A
consequence, stated rather than discovered later: in arm (c) feeding happens on
every tick, so the cull never runs at all — 24 cull-free ticks of 24. That is
what the arm is, and it is why H3 is a control-by-contrast and not a finding.

**D96. The three pinned seeds cannot differ in this frame, and the RESULT says
so.** `Population` draws on its RNG in exactly two places: `phase_interact`'s
pairing and `crossover`. Transfers are off and nothing reproduces, so every arm
returns byte-identical numbers on all three seeds. They are pinned by the
preregistration and are run and reported, but they are one sample presented three
times, not three samples. Reporting them as agreement across seeds would be the
kind of sentence this repository exists to not write.

**D97. "Fires a further priced action" is `spent` strictly increasing after the
agent's first feeding, and a next-action price is asked of the oracle without
buying it.** `sg.step5(term, 10**9, store, dict(stats), limits)` returns the
action and its exact cost and mutates nothing but the throwaway `stats` — the
same counterfactual `reduce_slice` already asks itself when a slice ends. An
agent with no next action at any budget (a normal form, an unresolved reference)
is not fed in the forced arms and is not part of H1's population: H1 is about
food, and there is nothing such an agent could buy.

---

## 2026-08-27 — fixing what ALIFE-EXP-011 measured

The measurement is committed (`10b4bc3`); this is the fix, and per the
preregistration the RESULT stays the *before* and the regression suite is the
*after*, with neither edited to meet the other.

**D98. `phase_cull` re-tests starvation instead of trusting a status set two
phases earlier.** Of the three mechanisms the preregistration allowed —
reviving grants, a cull exemption for fed-this-tick agents, a reordered
schedule — none is quite right, and the fourth is:

  * *reviving grants* puts a scheduler decision inside `Economy.grant`, which is
    a ledger, and would revive an agent on one ATP whether or not one ATP buys
    anything;
  * *exempting fed-this-tick agents* is bookkeeping about how the ATP arrived,
    and would miss any future phase that moves ATP by another route;
  * *reordering* is strictly worse: cull-then-feed archives the starving agent
    before anybody can reach it.

`STARVED` means "the next action costs more than the reservoir holds". That is a
claim about a reservoir, and two phases of a commons economy run between the
`phase_reduce` that made the claim and the `phase_cull` that acts on it. So the
cull asks the oracle whether the claim is still true — `step5` on a throwaway
`stats`, the same counterfactual `reduce_slice` already asks itself when a slice
ends — and returns the agent to `LIVE` when it is not. It is independent of how
the ATP arrived, so the transfer path and the rebate path are both fixed, and so
is any path added later. Only `BudgetExhausted` counts as still starving: a next
action that is unresolved or that faults is not a budget question, and archiving
on it would be ALIFE-EXP-009's mistake in a second place.

The flag `recheck_affordability_before_cull` defaults to the fix. It exists for
exactly one caller — ALIFE-EXP-011's harness, which is the before measurement and
pins it to `False` in code, so its receipt keeps reproducing the schedule it
measured rather than depending on a default. **No committed receipt moves:** every
experiment in the repository runs `step(cull=False)` or drives `phase_reduce`
directly, verified by grep before the change; only `tests/alife_conservation.py`
culls, and it asserts properties rather than numbers.

**D99. The rebate's "shared" is decided by distinct holders, and the occurrence
statistic is kept as a named alternative rather than deleted.** `phase_share`'s
docstring has promised "structure they hold in common with somebody else" since
it was written, and the code asked `population_census`, which counts
*occurrences* — so an agent holding one hash twice made that hash "shared" with
nobody and collected a sharing rebate for repeating itself (ChatGPT's review).
Given the choice of fixing the code or the docstring, the code: the docstring
states the policy's intent, the intent is the defensible one, and enshrining an
accident because it is what shipped is how a policy becomes a bug with tenure.

What is *paid* stays occurrence-weighted over the agent's own term — an agent
holding a genuinely shared address five times holds five nodes of common
structure. Which addresses qualify is an inter-agent question; how much of one an
agent holds is not, and only the first was wrong.

`rebate_basis="occurrences"` restores the old statistic. It is not a legacy
shim: self-repetition is a real and different pressure, the review says so, and
ALIFE-EXP-011's arm (a) is a measurement of a colony that ran under it — pinned
in that harness for the same reason as D98. **Receipt check:** `rebate_rate` is
non-zero in exactly two places in the repository, `tests/alife_conservation.py`
(randomized, no frozen numbers) and ALIFE-EXP-011 arm (a); every experiment
constructs its population with the 0.0 default, EXP-001 included. The change
moves EXP-011's arm (a) by 2 ATP a seed, which is why that harness pins it, and
moves nothing else.

**D100. The regression suite is its own file, and every property in it has a
negative control.** `tests/alife_refeed.py` implements the review's script
literally (R1), the same-tick version that actually isolates the bug (R2,
transfer path; R3, rebate path), the check that the cull still culls (R4), and
the rebate's inter-agent property (R5). R2, R3 and R5 each re-run on the
pre-2026-08-27 policy and demand the property FAIL — a regression test nobody has
watched go red is a regression test nobody has watched, and this whole bug
existed under a green randomized suite.

R1 needed one honest adjustment. The review's script says "transfer enough for
the next action"; that buys exactly one action, after which the agent starves
again on the *next* one and the cull is right to take it. Feeding an agent enough
for one action and then archiving it for being unable to afford a second is not
the bug — it is R4. So R1 transfers enough to reach a normal form, which is what
the script means by "gets to run", and R2/R3 carry the discrimination. R1 passes
on both policies and is labelled as not discriminating.

The R3 fixture is searched rather than asserted: a colony of unrelated random
terms shares nothing after reduction, so the rebate correctly grants nothing and
an R3 written on it would have passed while feeding zero — the ALIFE-EXP-002
defect inside a regression test. It searches seeds and budgets for a colony where
the rebate actually feeds a starving agent more than its next action costs, over
a corpus of `S x_i y_i z` sharing one `z`, and fails closed if none exists.

---

## 2026-08-27 — ALIFE-EXP-012, the factorial's missing choices

Recorded before the measurement ran, per the ALIFE-EXP-005 arrangement. The
preregistration
([`experiments/ALIFE-EXP-012-the-currency-factorial-preregistration.md`](experiments/ALIFE-EXP-012-the-currency-factorial-preregistration.md),
`28b139a`) delegates one piece of engineering explicitly — "the engine change
this requires is the harness author's to design and record" — and leaves five
things implicit.

**D101. Counter-based randomness is a substrate facility, not a harness trick,
and it is deliberately NOT a `random.Random` drop-in.** ALIFE-EXP-010 compared
arms whose RNG streams diverged the moment their histories did: one arm culled a
molecule, drew one more number from a shared stream, and every later draw in that
arm was a different number from its counterpart's. Codex named the consequence —
a cross-arm difference is then part manipulation and part re-seeded noise, and no
analysis afterwards can separate them.

`impl/sigma_alife.py` gains `CounterRandom`, whose `below(n, index, event)` is a
pure function of `(seed, index, event)`: reaction 300's reactant choice is the
same number whatever happened at reaction 299, in this arm or any other. It is a
**pure addition** — nothing existing calls it, and 29/29, the differential,
conservation, memo, nulls and refeed suites are green before and after.

The tempting design was a `random.Random` work-alike with `.choice` and
`.randrange`, so existing loops need no edit. That is exactly the wrong shape:
the key IS the mechanism, and a signature that hides it lets any call site
silently go back to being position-dependent. So the keys are in the signature
and every call site has to say what it is drawing for.

`StreamRandom` has the identical signature and **ignores** the keys, drawing from
a positional `random.Random`. It has two jobs: replaying a legacy stream-ordered
run without a second copy of the loop (C-compat), and being the negative control
for C-RNG — a decorrelation property is only worth asserting if something
visibly lacks it.

**D102. The key vocabulary, and the one place a key needs a sub-index.** The
chemistry draws three kinds of number: two reactant choices per reaction
(`reactant_a`, `reactant_b`) and a cull victim on capacity overflow. Reactant
keys are `(seed, i, "reactant_a"|"reactant_b")`.

A cull is not once-per-reaction. A settled reaction can wake parked agents whose
own products append and overflow the soup again, all within reaction `i`, so the
cull key carries an occurrence index: `cull:0`, `cull:1`, … reset each reaction.
That index depends on history *within* the reaction, which is unavoidable and is
not the property under test: Codex's requirement is that an event in one arm not
shift any **later** draw, and reaction `i+1`'s keys are untouched by how many
culls reaction `i` needed. Stated here rather than discovered by a reader.

**D103. C-RNG compares draw WORDS, not draw outcomes, and carries its own
negative control.** Two arms legitimately have different soup lengths, so the
same key can yield a different *index* while the randomness behind it is
identical — comparing outcomes would fail a correct implementation. So the
control compares the raw 64-bit word each key produces, which is a function of
the key alone.

The test: run a cell, run it again with one reaction (300 of 600) forced to
starve where it settled, confirm the histories genuinely diverge, and require
every shared key's word to be bit-identical **before and after** the
perturbation. Counter mode: 827/827 before, 771/771 after. Then the same
comparison under `StreamRandom`, which must FAIL: 25/652 after. It runs
**first**, and the harness returns before touching any other control if either
half fails — the preregistration says no cross-arm comparison is valid without
it, so a receipt that recorded one anyway would be the thing rule 6 exists to
prevent.

**D104. C-compat is arm BF in stream mode against EXP-007's frozen receipt, and
the "documented D98/D99 deltas" turn out to be zero — measured, not assumed.**
The preregistration allows BF to differ from EXP-007 by the D98/D99 fix. It does
not: EXP-007's chemistry drives `reduce_slice` directly, with no `phase_cull` and
no rebate, so neither fix can reach it — and `tools/test-all.sh` replaying
EXP-007 green after the fix already said so. C-compat turns that into a number by
running BF with `StreamRandom` (EXP-007's draw order) and demanding all 13
recorded fields match on the three shared seeds. Any divergence is a harness bug,
which is what the preregistration asks for; the counter-keyed measurement then
runs on a harness one control has pinned to a committed receipt.

**D105. The gate arithmetic, and a sign convention stated so it cannot be read
backwards.** Per outcome: five per-seed values per cell, a cell mean, and a cell
spread (max − min). Effects are computed from the cell means —
`price = mean(BF,BM) − mean(FF,FM)`, `matter = mean(BF,FF) − mean(BM,FM)`,
`interaction = (BF − BM) − (FF − FM)` — and all three draw on all four cells, so
each outcome has **one** gate: the largest of the four spreads. An effect is
claimable iff its absolute value exceeds that gate.

The convention is **Book-minus-floor** for price and **free-minus-consume** for
matter. So X2's "sign is positive for M" means the matter effect is **negative**:
M being more diverse makes `free − consume` negative. The harness names that
inversion in code (`diversity_favours_m = value < 0`) because a factorial's
signs are exactly the thing a reader mis-reads.

**D106. What the four cells do to Book I's memory bound is measured in every
cell and reported, not gated.** `size ≤ s0 + spent` follows from
`Δsize ≤ cost − 1`, a property of Book I's *price*, so both floor arms abandon
the premise by construction. FM can still keep the *matter* statement — the
consumed body leaves the census carrying at least the material the copy adds —
but **FF has neither**: it charges the floor and consumes nothing, so nothing
leaves the census to offset a copy. FF is the cell of this factorial with no
resource law at all. Per-action violations are counted in every cell (the first
draft counted them only where a body paid, which read a spurious zero for FF and
was fixed before any receipt), and the count is a result, not a control failure.

**D107. C-fire(matter) FAILS, on the strict reading, and the strict reading is
the right one.** The preregistration asks for "≥ 50 consumption events per seed"
in BM and FM. Two readings are available: per cell (each of BM and FM, each
seed) or per seed summed across both M arms. The looser one passes every cell —
which is precisely why it is not chosen. The strict reading is what
ALIFE-EXP-010's C2 said in almost the same words ("at least 50 `consumed` deaths
per seed in Arm M"), this control cites that lesson by name, and a threshold
re-read after seeing the data is not a threshold.

Under the strict reading it fails in **3 of 10 M cells**: BM/20260827 = 46,
FM/20260825 = 22, FM/20260827 = 46. So no receipt is written and no RESULT.md
exists. Rule 6: a receipt beside a failure is worse than none.

**It is not a harness bug, and the accounting proves it.** In every one of the
ten M cells, `consumed + blocked` equals `R-S fired − R-S on genesis`, exactly:

| cell | R-S | on genesis (free) | eligible | consumed | blocked |
|---|---:|---:|---:|---:|---:|
| BM/20260825 | 452 | 376 | 76 | 52 | 24 |
| BM/20260827 | 417 | 319 | 98 | **46** | 52 |
| FM/20260825 | 488 | 443 | 45 | **22** | 23 |
| FM/20260827 | 419 | 321 | 98 | **46** | 52 |
| FM/20260829 | 634 | 376 | 258 | 190 | 68 |

Every eligible duplication is accounted as either a consumption or a wait. The
mechanism is wired correctly and fires between 22 and 190 times per cell; what
is small is the **eligible population**. Between 65% and 91% of duplications in
this chemistry duplicate a genesis atom, which the preregistered rule makes free
— the same laziness ALIFE-EXP-010 measured, where `size(z)` averaged 1.1–1.7 and
duplication governed ~1% of spend. The floor of 50 was set against EXP-010's
counts (194/101/62 on three seeds), and those came from a *correlated* stream;
decorrelating the draws — the entire point of this experiment — moves the
trajectories, and three of the new ones do not reach it.

**There is no legitimate knob.** The preregistration pins the chemistry and
parameters to EXP-007's verbatim (1000 reactions, 200 ATP), the five seeds, and
the corpus. Lengthening the run, raising the budget or reseeding would all be
choosing a frame after seeing that the committed one failed. The factorial's
numbers exist and are reproducible from the committed harness; they are **not
adjudicated**, X1/X2/X3 are **not scored**, and nothing is recorded.

**What a successor needs.** Either a chemistry where non-genesis duplication is
common — the enforced-copy-pricing regime EXP-010's response already names, where
`z` is materialized rather than an address — or a preregistered floor set against
the *eligible* population rather than the raw event count. The second is cheap
and would have caught this at design time: "≥ 50 consumption events per seed" is
a claim about a denominator nobody wrote down.

**D108. A defect C-compat caught in this session's own engine addition.**
`StreamRandom.word()` returned `getrandbits(64)`, so logging a draw *consumed* a
draw: any run that recorded its randomness ran on a different stream from one
that did not. C-compat found it immediately — arm BF settled 768 reactions where
EXP-007's frozen receipt says 629, a 139-reaction gap that no policy in this
experiment could explain. `word()` now returns a function of the stream position
that advances nothing, and C-compat passes on all three shared seeds across all
13 recorded fields. Named here because it was found by a preregistered control
doing exactly its job, and because "the observer consumed the thing it observed"
is a defect class worth having a name for in a repository full of instruments.
