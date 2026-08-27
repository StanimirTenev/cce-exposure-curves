# From Q-Day to Exposure Curves

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22126410.svg)](https://doi.org/10.5281/zenodo.22126410)

A capability-conditioned framework for post-quantum migration under uncertain arrival.

This repository holds the paper, the LaTeX source, and the single script that produces every
number and every figure in it.

**Preprint. Not peer reviewed.**

## What the paper argues

Quantum risk is usually reported as a readiness snapshot: what fraction of an estate has been
migrated today. A snapshot cannot identify exposure, because two estates with identical readiness
can face different exposure depending on when a capability arrives and what was still vulnerable
when it did.

The paper defines exposure as an expectation taken at the random arrival of a specified
capability, adds harvest-now-decrypt-later as a stock and a flow with a confidentiality shelf
life, bounds what an adversary can actually decrypt with a work budget, and proves four
properties of the resulting objective:

1. **Snapshot insufficiency.** Equal readiness at an assessment date does not imply equal exposure.
2. **Earlier protection weakly reduces future HNDL exposure**, strictly under stated conditions.
3. **No universal static priority score.** No ordering built only on a system's present
   criticality minimises the objective for all capability distributions, shelf lives, emission
   rates, durations, and weights.
4. **Quantum-work monotonicity.** Raising the work per recovered unit cannot increase realisable
   archived value.

Property 3 is the practically useful one: it says a migration order has to be argued against
measured exposure, not asserted from a criticality register.

## What is not claimed

The case study is synthetic. Its inputs are illustrative normalised units, it is not calibrated
to any organisation, and its capability distributions are scenario inputs rather than estimates
of real-world arrival. The reported percentage reductions apply to the separable
unlimited-throughput benchmark, not to realised compromise and not to the finite-budget
objective. The novelty claim is about the combination of ingredients in one objective, and is
stated as such.

## Reproducing

```
python3 code/analysis_model.py     # table, historical component, budget curve, all five figures
python3 code/verify_claims.py      # re-runs the model and checks 43 numbers against the built PDF
```

No dependencies beyond Python and Matplotlib. No random sampling: the results are deterministic.

`verify_claims.py` exists because a paper that states numbers its own script does not produce is
the failure this framework is about. It reads the text of the built PDF and asserts that every
figure in the results table, the historical component, the budget curve, and every percentage is
one the model actually returns. It exits non-zero if any is missing.

## A note on this revision

The script that produced the earlier revision was lost. This one was rebuilt from the
specification printed in the paper and checked against the published numbers, and the
reconstruction turned up two places where the computation did not follow the equations: exposure
from a capability already present at the assessment date, and decryptability when the capability
preceded capture. In both cases the computation was the defensible reading and the equations were
too narrow, so the equations were corrected rather than the numbers. The headline figures moved
by less than 0.3%. The four properties were unaffected.

## Layout

```
paper/     PDF, LaTeX source, figures
code/      analysis_model.py, verify_claims.py
results/   results.csv, inputs.json
```

## Licence

Paper, figures and text: CC BY 4.0. Code: MIT (see `code/LICENSE`).

## Citing

Cite the concept DOI to point at whichever revision is current:

> Tenev, S. (2026). *From Q-Day to Exposure Curves: A Capability-Conditioned Framework for
> Post-Quantum Migration Under Uncertain Arrival.* https://doi.org/10.5281/zenodo.22126410

To pin this revision specifically, use the R9 DOI: https://doi.org/10.5281/zenodo.22126411

Machine-readable metadata is in `CITATION.cff`.
