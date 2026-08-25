<!--
PROVENANCE OF THIS FILE — added on filing, not part of the document.

This is the research proposal exactly as it was received on 2026-08-25, written
by Kimi (Moonshot AI) at s0fractal's request and handed to this repository as
its starting point. It is filed VERBATIM below the line: nothing in it has been
corrected, and several things in it are wrong (the Book I API names it imports
do not exist; its Theorem 3 is not the theorem that matters; its file layout is
not the layout this repository uses).

Those are not defects to be silently patched in someone else's document. What
was decided differently, and why, is recorded in
`ALIFE-ADR-001-substrate-is-a-consumer.md`, which cites this file by section.
Read this one for the programme; read the ADR for what the repository does.
-->

# Proposal: Σ-GLYPH as a Substrate for Artificial Life
## ATP-Limited Population Dynamics on Content-Addressed Combinator Graphs

**Version:** 0.1.0-draft  
**Date:** 2026-08-25  
**Authors:** [Author] + AI collaborators  
**Foundation:** Σ-GLYPH v0.6.7 (Zenodo DOI 10.5281/zenodo.22069651)

---

## 1. Executive Summary

This proposal outlines a research program at the intersection of **Artificial Life (ALife)**, **unconventional computation**, and **formally verified runtimes**. We propose to use the Σ-GLYPH content-addressed combinator machine — with its machine-proven invariant `size ≤ atp + 1` and deterministic settling theorem — as a substrate for population-based digital life experiments.

Unlike traditional ALife platforms (Tierra, Avida, cellular automata) that rely on ad-hoc resource limits or heuristic timers, Σ-GLYPH provides a **mathematically grounded resource model** where both work and peak memory are priced by a single integer budget (ATP). This creates a rare opportunity to build ALife systems where resource dynamics are not merely simulated but **theorem-guarded**.

**Key innovation:** We treat the content-addressed DAG (CAS) not merely as a data structure, but as a **shared ecological substrate** where distinct combinator terms (agents) compete for ATP, share sub-structures (anastomosis), and leave deterministic traces upon resource exhaustion.

---

## 2. Problem Statement & Motivation

### 2.1 The Resource Problem in Digital Life

Most ALife systems face a fundamental tension:
- **Unbounded growth** leads to memory exhaustion and loss of experimental control.
- **Artificial caps** (fixed instruction limits, periodic culling) introduce observer bias and break metabolic metaphors.
- **Heuristic garbage collection** is non-deterministic and non-reproducible across implementations.

### 2.2 The Formal Methods Gap

Formal verification communities (Lean, Coq, TLA+) have produced rigorous resource models, but these are rarely connected to evolutionary or emergent phenomena. Conversely, ALife produces fascinating emergent behavior that is nearly impossible to verify formally.

### 2.3 Why Σ-GLYPH Bridges the Gap

Σ-GLYPH Book I provides:
1. **Deterministic evaluation** — no hidden state, no GC non-determinism.
2. **Content-addressed sharing** — SHA-256 identity means sub-term sharing is structural, not incidental.
3. **Proven memory bound** — `EvalMachine.evalHash_peak_size` guarantees no agent can exceed its ATP budget.
4. **Settling theorem** — `evalHash_settles` guarantees graceful halt on resource exhaustion (no crashes, no hangs).

These properties make Σ-GLYPH an ideal **"digital physics"** for ALife: agents operate under laws that are not merely programmed but **proven**.

---

## 3. Research Questions

### RQ1: DAG Morphogenesis & Anastomosis
> How does the topology of a shared content-addressed graph evolve under ATP-limited population dynamics, and what emergent sharing structures arise?

**Hypothesis:** As population density increases, the sharing factor (ratio of total redexes to unique CAS nodes) grows super-linearly, creating emergent "mycelial" network structures that reduce per-agent ATP costs.

### RQ2: ATP Diffusion & Local Metabolism
> Can we define a local ATP-transfer semantics between neighboring redexes that preserves the global memory bound while enabling metabolic coupling?

**Hypothesis:** A conservative ATP-transfer rule (where donors retain at least `size + 1` budget) preserves the Σ-GLYPH invariant while allowing symbiotic relationships between agents.

### RQ3: Sporulation & Resilience
> Does the settling theorem enable viable "dormancy" cycles where agent populations survive total ATP drought and reactivate upon resource renewal?

**Hypothesis:** Agents in settled configurations retain structural integrity and can resume reduction upon ATP injection with bounded reactivation cost.

### RQ4: Evolutionary Pressure on Combinator Structure
> Under ATP competition, do certain combinator structures (e.g., Church numerals, fixed-point combinators) exhibit selective advantage?

**Hypothesis:** Term structures with higher sharing potential and lower redex density will dominate under scarce ATP, while "fast-burning" structures will dominate under abundance.

---

## 4. Methodology

### 4.1 Experimental Architecture

```
┌─────────────────────────────────────────────┐
│  ALIFE SUBSTRATE (new repository)           │
│  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Population  │  │ ATP Economy Engine  │  │
│  │ Manager     │──│ (diffusion, taxes)  │  │
│  └──────┬──────┘  └─────────────────────┘  │
│         │                                   │
│         ▼                                   │
│  ┌─────────────────────────────────────┐   │
│  │ Σ-GLYPH Core (sigma-glyph >=0.6.7)  │   │
│  │  - Content-addressed DAG            │   │
│  │  - Hash-thunk evaluator             │   │
│  │  - ATP accounting                   │   │
│  └─────────────────────────────────────┘   │
│         │                                   │
│         ▼                                   │
│  ┌─────────────────────────────────────┐   │
│  │ Formal Verification Layer (Lean 4)  │   │
│  │  - Population invariants            │   │
│  │  - ATP conservation lemmas          │   │
│  └─────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

### 4.2 Agent Model

An **agent** is a tuple:
```
Agent := (Term_hash, ATP_budget, Position, Lineage)
```

Where:
- `Term_hash` — content-addressed SKI term (Book I canonical bytes)
- `ATP_budget` — non-negative integer, local resource reservoir
- `Position` — coordinate in an abstract interaction graph (optional, Book II wave semantics)
- `Lineage` — provenance chain for evolutionary tracking

### 4.3 Population Dynamics

**Step 1: Reduction Phase**
Each agent executes `evalHash(term, atp=min(ATP_budget, ATP_step_limit))`.
- If normal form reached: agent becomes **dormant** (settled).
- If ATP exhausted: agent enters **stasis** (preserves configuration).
- If unresolved reference: agent is **marked for repair/mutation**.

**Step 2: Sharing Phase**
The population DAG is analyzed for shared sub-terms. Agents with common sub-terms receive ATP rebates proportional to sharing savings (incentive for structural convergence).

**Step 3: Interaction Phase** (optional)
Agents within interaction radius may:
- Transfer ATP (conservative rule: donor must satisfy `donor_ATP > donor_size + 1`)
- Exchange sub-terms (crossover at shared CAS nodes)
- Spawn offspring (replicate with mutation, paying ATP cost)

**Step 4: Culling Phase**
Agents with `ATP = 0` and non-settled configuration are archived (not deleted — provenance preserved in CAS).

### 4.4 Metrics

| Metric | Definition | Connection to Σ-GLYPH |
|--------|-----------|----------------------|
| **Sharing Factor** | `Σ redexes / unique CAS nodes` | Direct measure of CAS efficiency |
| **ATP Efficiency** | `normal_forms / total_ATP_consumed` | Productivity per resource unit |
| **Network Density** | Graph density of shared sub-term DAG | Emergent topology |
| **Settling Time** | Steps to `evalHash_settles` | Deterministic halt guarantee |
| **Resilience Index** | Fraction of population surviving ATP drought | Sporulation hypothesis |
| **Structural Diversity** | Shannon entropy of term shapes | Evolutionary pressure |

---

## 5. Formal Verification Component

### 5.1 Target Theorems (Lean 4)

**Theorem 1: Population Memory Bound**
```lean
theorem population_peak_size (agents : List Agent) (total_atp : Nat) :
  sum (map peak_size agents) ≤ total_atp + length agents
```
*Proof strategy:* Direct extension of `evalHash_peak_size` with independence assumption. For shared agents, tighter bound via CAS sharing lemma.

**Theorem 2: ATP Conservation**
```lean
theorem atp_conservation (before after : Population) :
  total_atp before = total_atp after + atp_consumed during_step
```
*Proof strategy:* Bookkeeping invariant on the economy engine.

**Theorem 3: Conservative Transfer Safety**
```lean
theorem safe_transfer (donor recipient : Agent) (amount : Nat) :
  donor.atp > donor.peak_size + 1 →
  (donor' := donor { atp := donor.atp - amount }).peak_size ≤ donor'.atp + 1
```
*Proof strategy:* Monotonicity of `peak_size` with respect to ATP reduction.

### 5.2 Differential Testing

Following Σ-GLYPH methodology:
- Population simulator runs against reference oracle on seeded populations.
- Fuzzer generates random agent populations and verifies ATP conservation.
- Cross-implementation checks if substrate is reimplemented (e.g., Rust parallel version).

---

## 6. Repository Architecture Decision

### Recommended: New Repository

**Repository:** `s0fractal/sigma-glyph-alife` (or similar)

**Rationale:**
- **Governance separation:** Σ-GLYPH core maintains its 2-of-3 threshold warrant governance; ALife experiments evolve under lighter process (DRAFT → EXPERIMENTAL → PUBLISHED).
- **Dependency clarity:** Explicit `sigma-glyph>=0.6.7` in `pyproject.toml`; Book I remains normative foundation.
- **CI separation:** Long-running Monte Carlo simulations don't block core conformance checks.
- **Audience separation:** ALife researchers need not understand SKI reduction details; formal methods researchers need not install visualization stack.

**Interface Contract:**
```python
# sigma_glyph_alife/population.py
from sigma_glyph import eval_hash, serialize, validate

class Agent:
    def __init__(self, term_hash: bytes, atp: int, ...):
        # Invariant: atp >= 0, term_hash is canonical Book I bytes
        ...
```

### Alternative: In-Repo Extension

If federation governance accepts:
- Place under `experiments/exp-005-alife-substrate/`
- Mark all ALife code as NON-NORMATIVE
- Do not modify Books I–III or GOV-anchors
- Risk: scope creep into core spec; harder for external ALife researchers to discover

---

## 7. Implementation Plan

### Phase 1: Foundation (Weeks 1–4)
- [ ] Set up repository with `sigma-glyph` dependency
- [ ] Implement `Agent` and `Population` classes
- [ ] Implement single-step reduction loop (Book I integration)
- [ ] Basic metrics: sharing factor, ATP efficiency
- [ ] Unit tests: ATP conservation on deterministic populations

### Phase 2: DAG Morphogenesis (Weeks 5–8)
- [ ] Population generator: random closed λ-terms (reuse existing fuzzer)
- [ ] Sharing analysis: build CAS overlap graph
- [ ] Experiments: vary N (population size) and ATP_total, measure sharing factor
- [ ] Visualization: DAG topology evolution
- [ ] **Deliverable:** Working paper on anastomosis in content-addressed graphs

### Phase 3: ATP Economy (Weeks 9–12)
- [ ] Implement ATP transfer rules (conservative + osmotic variants)
- [ ] Implement mutation/crossover at CAS nodes
- [ ] Run evolutionary experiments: 100+ generations
- [ ] Measure structural diversity and selective pressure
- [ ] **Deliverable:** Draft of Theorem 3 (Conservative Transfer Safety) in Lean

### Phase 4: Formal Integration (Weeks 13–16)
- [ ] Complete Lean proofs for Population Memory Bound and ATP Conservation
- [ ] Differential testing: population simulator vs. reference oracle
- [ ] Preregistered experiment: sporulation under ATP drought (inspired by exp-004)
- [ ] **Deliverable:** Submission to ALife / UCNC / Complex Systems

---

## 8. Target Venues

| Venue | Deadline | Fit |
|-------|----------|-----|
| **ALife 2027** | ~Jan 2027 | Primary target; strong ALife community, open to unconventional substrates |
| **UCNC 2027** | ~Mar 2027 | Perfect fit: unconventional computation + natural computation |
| **Complex Systems** | Rolling | Deep theoretical follow-up on DAG morphogenesis |
| **ACM Onward!** | ~Jun 2027 | Bold paradigm angle: "theorem-guarded artificial life" |
| **IEEE TETC** | Rolling | Systems-oriented follow-up on verified substrate engineering |

---

## 9. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Lean proofs for population invariants prove intractable | Medium | High | Start with "paper proof" + property-based testing; formalize only core conservation lemmas |
| Population simulations too slow for meaningful evolution | Medium | Medium | Profile and optimize; consider Rust extension for population engine (Book I remains Python/Lean) |
| ALife reviewers find formal methods angle irrelevant | Low | Medium | Frame as "rigorous digital physics" — ALife community values substrate novelty (e.g., Lenia, SMC) |
| Σ-GLYPH core API changes break substrate | Low | High | Pin to `>=0.6.7,<0.7.0`; maintain compatibility tests |
| Emergent behavior is trivial/boring | Medium | High | Preregister hypotheses; use structural diversity metrics; compare against null models (random ATP allocation) |

---

## 10. Relation to Σ-GLYPH Ecosystem

This proposal respects the **spec-first, multi-model reviewed, machine-verifiable** ethos of Σ-GLYPH:
- All experiments are reproducible from committed code.
- Hypotheses are preregistered (following exp-004 precedent).
- Metrics are defined before experiments run.
- Formal claims are scoped: we prove what we can, test what we can't, and explicitly document the boundary.

The ALife substrate is a **consumer** of Σ-GLYPH, not a modifier. It demonstrates that the core invariants (determinism, content addressing, ATP bounding) are not merely theoretical curiosities but **enabling infrastructure** for a new class of reproducible, resource-aware artificial life systems.

---

## 11. Next Steps

1. **Decision:** Author approves proposal and selects repository strategy (new vs. in-repo).
2. **Bootstrap:** Initialize repository, set up CI, pin `sigma-glyph` dependency.
3. **Phase 1 kickoff:** Implement `Agent` + `Population` skeleton with Book I integration.
4. **First experiment:** Reproduce sharing factor measurement on 100-term population (1-week sprint).

---

*"A claim that arrives with a check attached is worth exactly as much as your ability to run the check yourself."*  
— Σ-GLYPH motto, extended to population dynamics.
