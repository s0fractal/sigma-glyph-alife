# Related work, and what is actually new here

Written after an external review (Claude Fable 5, 2026-08-25) pointed out that
this repository had no literature positioning at all, which makes its novelty
unreadable: a reader cannot tell whether "λ-terms as agents in an artificial
chemistry" is new (it is not) or whether anything about the substrate is (it is).

**Caveat, stated first.** What follows is written from the abstracts and
summaries of these works, not from a close reading of the papers. It is a map for
orientation inside this repository, and every comparison below should be checked
against the primary sources before it is repeated anywhere that matters.

## The two closest ancestors

### AlChemy — Fontana & Buss, 1994

λ-calculus expressions as molecules. Pairs of randomly sampled expressions are
joined by function application, evaluated, and the result is added back to the
population; the population is kept bounded by discarding expressions at random.
From that, a hierarchy of *organizations* emerges: **L0**, expressions that
compute themselves; **L1**, sets in which every expression is computed by others
in the same set — the analogue of an autocatalytic set; and **L2**, interactions
between L1 organizations. A recent reappraisal is
[*Self-Organization in Computation & Chemistry: Return to AlChemy*](https://arxiv.org/pdf/2408.12137).

### Combinatory Chemistry — Kruszewski & Mikolov, ALIFE 2020

An algorithmic artificial chemistry built on **combinatory logic** — the same
computational substrate this repository uses — with very few rules, a tabula rasa
initial state, and **conservation laws that replicate natural resource
constraints**. A single run with no external intervention discovers emergent
patterns that acquire constituents from the environment and decompose them, in a
way the authors compare to biological metabolism. Expanded in
[*Emergence of Self-Reproducing Metabolisms as Recursive Algorithms in an
Artificial Chemistry*](https://arxiv.org/pdf/2103.08245) (Artificial Life, 2022).

This is the nearest neighbour by a wide margin: combinators, conservation,
resource constraints, emergent metabolism.

## What is different here

Not the substrate — combinators as an artificial chemistry is theirs. Three
things about the *machine* underneath:

1. **Molecules are content-addressed.** Two agents holding equal structure hold
   one object, by construction, because identity is a SHA-256 of canonical bytes.
   In an artificial chemistry over expression *copies*, "the same molecule twice"
   is two molecules; here it is one address with two references. That is what
   makes anastomosis a measurable quantity at all — and ALIFE-EXP-001 and -004
   are about what evaluation does to it.
2. **The resource law is a theorem, not a bookkeeping rule.** Combinatory
   Chemistry conserves atom counts by construction. Σ-GLYPH prices every action
   with one integer and *proves* that peak memory is bounded by it
   (`size ≤ spent + 1`, machine-checked). This repository extends that proof to
   interruption, to populations, and — since ALIFE-EXP-003 — to a machine with a
   memo action in it. A resource model you can prove things about is a different
   object from one you can only run.
3. **Every action has a spec-fixed price.** "What does this operation cost" is not
   a modelling choice here; it is Book I §3.4. That is what turned the memo
   question into an arithmetic one with two floors rather than a tuning knob —
   and into a question for Book I's owners (`needs/DA-SIGMA-0002`) rather than a
   parameter in a paper.

## What they have that this does not

**Emergence.** Both ancestors start from an undifferentiated state and get
self-reproduction, organizations, metabolism. This repository hand-builds its
populations and measures resource dynamics on them. Its one evolutionary arm
(ALIFE-EXP-002 Part B) walked straight into the classic degenerate attractor:
with fitness = "settle cheaply", selection drives mean term size to 2.8–3.4
nodes, which is the SKI equivalent of breeding for the empty program.

Their answer to that is instructive and better than the obvious one: rather than
shaping a fitness function, Combinatory Chemistry imposes **conservation laws**
and lets structure be what survives them. A substrate that already conserves ATP
by construction is well placed to try the same thing, and that is a more
promising direction than inventing a task for agents to be good at.

## Reading order for someone arriving here

1. `README.md` — what the substrate is, and the three results.
2. `experiments/alife-exp-001/RESULT.md` then `alife-exp-004/RESULT.md` — a claim
   and the adversarial replication that tried to kill it.
3. `proofs/README.md` — what is proved, what is only checked, and the difference.
4. `needs/DA-SIGMA-0002-memo-pricing/` — the one question this work sends back to
   the specification it consumes.

Sources: [Combinatory Chemistry (arXiv:2003.07916)](https://arxiv.org/pdf/2003.07916),
[Emergence of Self-Reproducing Metabolisms (arXiv:2103.08245)](https://arxiv.org/pdf/2103.08245),
[Return to AlChemy (arXiv:2408.12137)](https://arxiv.org/pdf/2408.12137).
