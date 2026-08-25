# ALIFE-EXP-003 — is a colony better off funding a library than its agents?

**Preregistration. No measurement has been taken** except the scarcity probe
reported below, which reports one arm and is described so it cannot be re-sold as
a result. Non-normative: nothing here changes Book I or any released Σ-GLYPH
contract.

## Where the question comes from

ALIFE-EXP-002 ended on a limitation, not on a hypothesis: the memo it measured
learns **whole-agent normal forms**, so it fires only where lineage hands one
agent another's root hash. Its result names the alternative and why it was not
taken — memoize the *subterms agents actually demand*, which needs somebody to
pay for reducing a hash the moment it is first asked for.

Charging that to the agent who missed is the wrong answer: the first agent to
want a thing would subsidise everyone after it, and a substrate whose costs
depend on arrival order is not one anybody can reason about. So the colony pays,
out of a reservoir the agents did not get. That turns a mechanism question into
an economic one, which is the question worth asking:

> Given a fixed amount of ATP, is a colony better off spending some of it on a
> shared library than on its own agents?

**A prior worth stating, because it points the other way.** In a small unpriced
check (24 agents, generous budgets) the library cost 998 ATP to file 19 entries
and saved the agents 434. It lost money. Whether it wins under *scarcity* — where
an agent that cannot afford to derive a term can still afford `size(nf)` to buy
one — is exactly what is open.

## What is already decided, and will not be claimed as a finding

- **The price of a hit is `size(nf)`**, forced by Book I §3.4 and reproduced as a
  control in EXP-002 and in `needs/DA-SIGMA-0002`. Not revisited here.
- **A library changes no answers.** Book I determinism makes a hash's normal form
  a function; `learn` refuses anything that is not one, and refuses the two
  DISSONANCEs that are functions of a budget or a store rather than of the hash.
  Checked as control C1, not reported as a result.
- **A demand-filled library files things nobody asks for twice.** That waste is
  arithmetic — some hashes are demanded once — and the experiment reports its
  size rather than discovering its existence.

## What is genuinely open

**H1 — a library can pay.** There is a share `s > 0` of the colony's ATP that
yields strictly more settled agents than `s = 0`, at the same total ATP.
*Falsifier:* settled agents fall monotonically as `s` rises — the library never
pays on this corpus, and demand-filled memoization is a net loss whenever the
colony is poor enough for it to matter.

**H2 — and it can be overfunded.** The best share is interior: at large `s` the
agents are too poor to use what the library files. *Falsifier:* the maximum sits
at an endpoint.

**H3 — the advantage grows with redundancy.** At a fixed per-agent budget and a
fixed share of 0.25, the library's advantage over `s = 0` increases with
population size, because more agents demand the same subterm hashes.
*Falsifier:* no dependence on N, which would mean the library is serving
repetition inside single agents rather than overlap between them — the same
distinction that decided ALIFE-EXP-002.

## Design

- Corpus: EXP-001's 64 terms, pinned at `53cc6da80f66d220`.
- **Every arm has the same total ATP.** Share `s` to the library's reservoir, the
  remaining `(1 − s)` split equally among agents. `s = 0` is the null and must
  reproduce a plain no-memo run exactly.
- Shares `0, 0.1, 0.25, 0.5, 0.75`, at three scarcity levels `1200, 2000, 2800`,
  all fixed in `corpus.py` before this document.
- The library is filled **on demand only** — never pre-warmed. It learns what
  agents actually ask for, in the order they ask.
- H3: population sizes `16, 32, 64` at a fixed per-agent budget of 31 ATP and a
  fixed share of 0.25 — the share is preregistered rather than read off whichever
  arm wins.
- Reported per arm: settled agents, ATP spent by agents and by the library,
  entries filed, fills that failed, hits, **entries filed and never bought
  again**, and the settled population's sharing factor.

### The one tuned number, and how it was chosen

A colony that settles everything unaided cannot be helped, and one too poor to
settle anything cannot either. The scarcity level was chosen by running the
`s = 0` arm **alone** and taking a level inside a 40–70% settle band:

```
600 → 9/64   900 → 12/64   1200 → 21/64   1600 → 30/64
2000 → 33/64   2800 → 39/64   4000 → 53/64
```

`2000` (52%). No arm with a library was computed, inspected or guessed at while
choosing it, and two further levels are preregistered so that no conclusion rests
on one economy. This is the same discipline EXP-002 arrived at the hard way after
two dead frames, now applied before the fact instead of after.

## Controls, each of which must pass before a number is recorded

1. **C1 — no answer moves.** Every agent that reaches a normal form reaches the
   one `sigma_glyph.eval_hash` reaches, in every arm.
2. **C2 — the ledger balances with the library counted as a holder**, at every
   arm, and fails when it is left out of the sum.
3. **C3 — the bound holds** at every action of every agent and every librarian
   run (`probe=True`).
4. **C4 — `s = 0` is exactly a no-memo run**: same settled count, same ATP, same
   terms as a plain run at the same total.
5. **C5 — the library is not free.** Its spend is on the ledger, and the sum of
   agent ATP plus library ATP equals the colony's endowment in every arm.
6. **C6 — the corpus is EXP-001's**, by fingerprint.
7. **C7 — power.** At least one arm must differ from `s = 0` in settled agents.
   If no share changes anything, H1 is reported **UNDERPOWERED** and not scored
   either way — the rule EXP-002 had to learn by wasting two frames.

## What would make this experiment worthless

- Reporting a win at a share whose total ATP is not equal to the null's.
- Reading H3's share off the winning arm instead of the preregistered 0.25.
- Reporting settled agents without the library's own spend beside them: a colony
  that settles more agents while burning more ATP has not found anything.
- Any claim that Book I permits, intends or forbids this. That question is
  `needs/DA-SIGMA-0002` and is not decided by an experiment.
