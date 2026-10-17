# Experiment: automation × worker reallocation (17 October 2026)

**Status:** computed and checked in [GitHub Actions run #39020078176](https://github.com/Dmitry-dev-pet/truthrail-economic-lab/actions/runs/39020078176), job `verify`.
This was a **public-repository GitHub-hosted Linux CI** run; it was not a new
Mac execution or a deployment of the local Docker web app.

## Question and reproducible setup

How does the pinned US macroeconomic model respond when we independently vary
its automation assumption (`psi`) and workers' movement between occupations
(`mu`)? Start from `SCENARIOS["substantial"]` and the default `Fixed()`
values, changing only the two named assumptions.

- Model: independent `fhoces/opa-ai-macro-econ-scenarios`, tag `v1.0`,
  commit `d4703b6ae0d19dca08fbde11a25c218fa4c7b7a6`.
- Runner: `python -m lab.experiment` with the pinned upstream package on the
  Python path. Reproduction also occurs through `POST /api/experiment`
  once the local API is separately deployed.
- Automation axis `psi`: `[0.25, 0.50, 0.75]`.
- Occupational movement axis `mu`: `[0.03, 0.06, 0.12]`.
- Total model runs: **10** (one original substantial baseline + nine changed combinations).
- Anthropic Economic Index metrics are **not** used as model inputs.

## Observed conditional 2030 results

Values below are model outputs from the CI log, rounded to four decimals.
GDP gain is the percentage difference relative to the model's *no-AI
counterfactual*, not annual GDP growth. Other quantities are percentages.

| psi | mu | GDP gain vs no AI | Labor income share | Unemployment, all | Unemployment, AI-sensitive |
|---:|---:|---:|---:|---:|---:|
| 0.25 | 0.03 | +5.5336% | 58.5503% | 4.3409% | 4.1674% |
| 0.25 | 0.06 | +5.7104% | 58.5404% | 4.1734% | 3.7913% |
| 0.25 | 0.12 | +5.8526% | 58.5324% | 4.0395% | 3.4329% |
| 0.50 | 0.03 | +6.6322% | 57.3426% | 4.6837% | 4.8311% |
| 0.50 | 0.06 | +6.9302% | 57.3255% | 4.4062% | 4.2739% |
| 0.50 | 0.12 | +7.1759% | 57.3116% | 4.1773% | 3.7376% |
| 0.75 | 0.03 | +7.6850% | 56.1308% | 5.0763% | 5.5502% |
| 0.75 | 0.06 | +8.1151% | 56.1058% | 4.6837% | 4.8120% |
| 0.75 | 0.12 | +8.4842% | 56.0844% | 4.3448% | 4.0862% |

The reference scenario in the calculation is the **original published
substantial preset**, not necessarily the central `psi=0.50, mu=0.06` cell.
Always compare model deltas against the baseline returned by the experiment
runner rather than silently choosing the middle cell.

## What we can infer (within this model)

1. At fixed `mu=0.03`, increasing `psi` from 0.25 to 0.75 raises the
   calculated GDP gain by **2.1514 percentage points**, while the labor
   income share falls by **2.4195 points** and unemployment among
   AI-sensitive workers rises by **1.3828 points**.
2. At fixed `psi=0.75`, increasing `mu` from 0.03 to 0.12 increases GDP
   gain by **0.7992 percentage points** and reduces unemployment among
   AI-sensitive workers by **1.4640 points**.
3. The model does **not** make `mu` a measure of newly invented human tasks.
   New-task creation cannot be inferred from this experiment. Nor does
   this establish causal effects of real-world retraining policies.

All observations are **conditional assumptions for the United States**, not
forecasts, causal policy estimates, measured real-world automation rates,
or estimates for Portugal. Their purpose is to compare model mechanisms,
not to predict the probability of each scenario.

## Audit trail

- Pinned base-model Mac smoke (three *published* scenarios, not this grid):
  [mac-access #234](https://github.com/Dmitry-dev-pet/mac-access/issues/234).
- Nine-cell numerical verification:
  [Economic Lab CI #39020078176](https://github.com/Dmitry-dev-pet/truthrail-economic-lab/actions/runs/39020078176).
- Implementation and strict input validation: `lab/experiment.py`.
- The existing owner-reviewed Mac command continues to point to the
  *old* immutable source SHA. This file does not authorize remote execution.
