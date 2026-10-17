# First outcome-blind hypothesis study: new human tasks versus automation

**Date:** 2026-10-17. **Scope:** hypothetical U.S. macroeconomic model
through 2030. This is **not** a forecast, policy-impact estimate or empirical
verification of any relationship.

## Immutable audit trail

1. The research planner, three candidate hypotheses, scores, directional
   criteria and full grid were reviewed/merged in
   [PR #6](https://github.com/Dmitry-dev-pet/truthrail-economic-lab/pull/6)
   **before** the new experiment was requested.
2. The user-authorized GitHub issue
   [#7](https://github.com/Dmitry-dev-pet/truthrail-economic-lab/issues/7)
   supplied only the bounded public JSON `{"research":"auto"}`.
3. The unchanged owner-only hosted GitHub workflow posted the complete
   numerical result in [its audited issue comment](https://github.com/Dmitry-dev-pet/truthrail-economic-lab/issues/7#issuecomment-6232486454).
4. The independent mathematical source is pinned to
   `fhoces/opa-ai-macro-econ-scenarios` v1.0 at
   `d4703b6ae0d19dca08fbde11a25c218fa4c7b7a6`.
5. SHA-256 fingerprint of the fixed, **pre-computation** plan:
   `fff542fde935ec128b87417fa3514045725f2f2e107eb44163af045a7849abe2`.

## What Alfred proposed and chose

The planner evaluated no model outputs when ranking the catalogue.
The declared priority rubric was
`previously_untested_mechanism + worker_relevance + controlled_contrast`:

| Predeclared candidate | Priority |
|---|---:|
| `new_tasks_vs_automation` | 9 |
| `new_tasks_vs_mobility` | 8 |
| `automation_vs_mobility` | 7 |

The first was selected. Its model hypothesis was that, **holding the extent
of automation constant**, creating more human labor tasks in affected
occupations would improve worker outcomes. The rival possibility was that
this improvement would not hold consistently across automation levels.

The chosen model parameters were `psi = [0.50, 0.75, 0.90]` and
`rho = [0.00, 0.25, 0.50]`. They are experimental assumptions, not real
observations. The original `substantial` scenario is the baseline.
There are nine grid cells plus one baseline, i.e. **ten** mathematical runs.

- `psi`: share of AI-performed task instances that replace labor rather
  than assist workers;
- `rho`: number of new AI-sensitive **human labor tasks** for each
  task automated;
- `mu` (not varied here): ease of moving into another occupation.
  It is **not** task creation.

## Predeclared tests and observed outcomes

Each prediction was evaluated as the effect of changing a parameter from
its lowest to highest listed value at **every** level of the other parameter.
A magnitude below 0.02 percentage points is treated as too small to
distinguish from a near-zero effect in this numerical audit.

| Fixed parameter levels | Predicted change | Observed high-minus-low effect | Within-grid status |
|---|---|---|---|
| `psi = 0.50 / 0.75 / 0.90` | Higher `rho` raises labor income share | +2.221 / +3.346 / +4.026 pp | Consistent at all 3 |
| `psi = 0.50 / 0.75 / 0.90` | Higher `rho` lowers AI-sensitive unemployment | −0.808 / −1.348 / −1.708 pp | Consistent at all 3 |
| `rho = 0.00 / 0.25 / 0.50` | Higher `psi` lowers labor income share | −2.867 / −1.959 / −1.062 pp | Consistent at all 3 |

All numbers above were reported in the actual
[owner-requested issue](https://github.com/Dmitry-dev-pet/truthrail-economic-lab/issues/7),
not fabricated from the predeclared hypotheses.

### Full GDP and worker-outcome grid

GDP and average wage gains are relative to a U.S. no-AI counterfactual,
**not annual GDP or wage growth rates**. Unemployment and labor share are
percentage levels.

| psi | rho | GDP gain vs no AI | Labor share | All unemployment | AI-sensitive unemployment | Average wage gain |
|---:|---:|---:|---:|---:|---:|---:|
| 0.500 | 0.000 | 8.165% | 56.207% | 4.514% | 4.467% | 2.208% |
| 0.500 | 0.250 | 7.043% | 57.319% | 4.301% | 4.040% | 2.895% |
| 0.500 | 0.500 | 5.898% | 58.427% | 4.121% | 3.659% | 3.543% |
| 0.750 | 0.000 | 9.926% | 54.418% | 4.906% | 5.217% | 1.022% |
| 0.750 | 0.250 | 8.283% | 56.096% | 4.529% | 4.498% | 2.137% |
| 0.750 | 0.500 | 6.595% | 57.764% | 4.217% | 3.869% | 3.158% |
| 0.900 | 0.000 | 10.961% | 53.339% | 5.170% | 5.712% | 0.257% |
| 0.900 | 0.250 | 9.016% | 55.360% | 4.683% | 4.796% | 1.657% |
| 0.900 | 0.500 | 7.009% | 57.365% | 4.281% | 4.004% | 2.921% |

**A trade-off revealed by the model:** at constant `psi = 0.75`,
increasing new-task reinstatement `rho` from 0 to 0.5 raises the
model's labor share by **3.346 percentage points** and its average wage
gain by **2.136 points**, while lowering AI-sensitive unemployment by
**1.348 points**. At the same time, the model's **GDP gain above the no-AI
path decreases by 3.331 percentage points**, from 9.926% to 6.595%.
Thus, higher output and a larger share received by workers need not coincide
in this specific model.

## Interpretation and next question

Within the selected 3x3 U.S. model grid, all three fixed directional
hypotheses are consistent with the simulated numbers. This says nothing
about how likely any parameter combination is in reality, whether new tasks
will actually appear, or which intervention would create them. No statistical
significance, independent data fitting, country-specific forecasts or causal
policy validation were performed. Anthropic Economic Index data were **not**
used to calibrate the model.

A possible next question for Alfred, **only on a new user request**:
How does `rho` (new tasks inside AI-sensitive occupations) interact with
`mu` (easier transitions between professions), and can that change the
GDP versus labor-outcome trade-off? This is a separate predeclared candidate
and should not auto-run unattended.

No Mac execution, Docker API deployment, new MCP, provider account or
unbounded background work was introduced by this issue experiment.
