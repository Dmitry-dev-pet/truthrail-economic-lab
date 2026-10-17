# Joint effects of new tasks and worker mobility

**Date:** 2026-10-17. **Scope:** descriptive post-processing of the previously
examined U.S. model grids. This is not a newly preregistered hypothesis,
an empirical policy evaluation, or a forecast.

## Source and reproduction

The existing `new_tasks_vs_mobility` catalogue study was reproduced unchanged
for `modest`, `substantial` and `extreme`: three baselines and 27 parameter
cells, **30 model evaluations**. The axes are exactly the published
`rho=[0,0.25,0.5]` and `mu=[0.04,0.08,0.17]`.

- [Prior three-scenario report](2026-10-17-three-scenario-rho-mu-robustness.md).
- Independent model: [fhoces/opa-ai-macro-econ-scenarios](https://github.com/fhoces/opa-ai-macro-econ-scenarios),
  `v1.0`, commit `d4703b6ae0d19dca08fbde11a25c218fa4c7b7a6`.
- Lab source: `13dee3c0aa0f76a3a91f6dd9cae1bfe5eeb84171`.
- [Complete inputs, outputs and descriptive analysis plan](data/2026-10-17-rho-mu-interaction.json).
- Analysis-plan SHA-256: `d0fdf1ad705d2b9aac315960974eb4377c365203106e3647811439cf4a953240`.

The calculation ran directly in the current OpenAI task execution environment
with Python 3.12.14. The 30 simulations and post-processing took approximately
**0.59 seconds**, excluding source retrieval, environment preparation and
interpretation. No experiment workflow, Docker daemon, external LLM, credential
or Mac operation was dispatched. Any subsequent PR CI is a separate validation.

The plan fingerprint was written before this reproduction, but the original
published grid outcomes were already known. It records an auditable descriptive
calculation, not an outcome-blind scientific preregistration.

## Fixed contrasts

Let `y(rho,mu)` be unemployment among AI-sensitive workers in 2030, expressed
as a percentage level.

The common **grid anchor** is `rho=0,mu=0.04`, not each preset's original
baseline. Change new-task reinstatement to `rho=0.5`, mobility to `mu=0.17`,
or both, leaving every other assumption at its named preset.

```text
R_tasks = y(0,0.04) - y(0.5,0.04)
R_mobility = y(0,0.04) - y(0,0.17)
R_joint = y(0,0.04) - y(0.5,0.17)
Interaction = y(0.5,0.17) - y(0.5,0.04) - y(0,0.17) + y(0,0.04)
            = R_tasks + R_mobility - R_joint
```

All reductions and interactions are **percentage points**, not relative
percent changes. A positive interaction here means the joint reduction is
smaller than the sum of the two reductions measured separately at the same
anchor. It does not mean either intervention increases unemployment.

## Four-corner results

Every number in the following table is a percentage level of modeled
AI-sensitive unemployment.

| Preset | Grid anchor | More new tasks only | Easier mobility only | Both |
|---|---:|---:|---:|---:|
| Modest | 3.255123 | 3.070860 | 2.997141 | 2.913978 |
| Substantial | 6.235765 | 4.363626 | 4.216232 | 3.414762 |
| Extreme | 17.889406 | 8.778989 | 10.268789 | 5.018878 |

| Preset | Tasks reduction, pp | Mobility reduction, pp | Sum if additive, pp | Actual joint reduction, pp | Interaction, pp |
|---|---:|---:|---:|---:|---:|
| Modest | 0.184263 | 0.257982 | 0.442245 | 0.341145 | 0.101100 |
| Substantial | 1.872139 | 2.019533 | 3.891672 | 2.821003 | 1.070669 |
| Extreme | 9.110417 | 7.620617 | 16.731034 | 12.870528 | 3.860506 |

For the substantial preset, improving mobility reduces unemployment by
**2.019533 pp** when `rho=0`, but by **0.948864 pp** when `rho=0.5`.
Both changes together still outperform either change on its own.

## Economic interpretation and limits

The same four-corner pattern appears in all three already examined grids:
the two mechanisms partly substitute for one another **on this unemployment
metric and these finite endpoints**.

A mechanism-based interpretation is that reinstating human tasks retains
labor demand in AI-sensitive occupations, reducing the remaining pressure
for movement to other occupation groups. This interpretation is consistent
with the code's separate task-demand and cross-group search mechanisms;
the contrast itself does not identify a causal mediation share or a
real-world retraining effect.

The mechanisms are not equivalent for other outcomes. At these paired
endpoints, more new tasks raise workers' income share while the joint
GDP gain above the no-AI counterfactual is smaller than at the common grid
anchor. In the substantial preset that GDP gap changes from **9.306538%**
to **6.772100%**; this is a smaller *AI-related increment*, not evidence
of an absolute recession.

Limitations:

- The pattern is descriptive post-processing of known simulated results.
  It does not provide a new independent test or statistical significance.
- Contrasts are finite endpoint comparisons, not derivatives, elasticities,
  globally valid interactions, probabilities or estimated policy impacts.
- The API rounds outputs to six decimals; arithmetic was checked within
  0.00001 pp. Source report tables round to three decimals.
- Other assumptions differ across the three presets. Comparing interaction
  magnitudes across presets does not isolate one causal driver.
- `rho` and `mu` are model parameters; no observed policy or national
  parameter calibration was introduced.
- Portugal remains audit-only and non-runnable. Anthropic Economic Index
  usage data remain separate from these macroeconomic calculations.

The referenced JSON preserves each full resolved preset and fixed-input
record, all grid cells, existing directional checks, and the descriptive
contrast definition.
