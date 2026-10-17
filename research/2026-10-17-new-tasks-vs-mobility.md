# Second predeclared hypothesis study: new tasks versus occupational mobility

**Date:** 2026-10-17. **Model:** independently reproduced conditional
U.S. macroeconomic scenarios to 2030. These are *not* forecasts,
empirical estimates, or causal policy effects.

## Audit trail and source

- Owner-approved study submitted through the existing GitHub connector:
  [Economic Lab issue #9](https://github.com/Dmitry-dev-pet/truthrail-economic-lab/issues/9).
- Exact owner issue title: `[econ] experiment`.
- Public issue body: `{"research":"new_tasks_vs_mobility","scenario":"substantial"}`.
- [Complete computed and published results](https://github.com/Dmitry-dev-pet/truthrail-economic-lab/issues/9#issuecomment-6233148899).
- The unchanged, prereviewed hypothesis catalogue and directional tests:
  [PR #6](https://github.com/Dmitry-dev-pet/truthrail-economic-lab/pull/6).
- Pre-computation plan fingerprint (SHA-256):
  `ee9373b153584ab33c9b43ec3f5b72b085a3801725ce45f1d077a8e155146c25`.
- Independently reproduced source: `fhoces/opa-ai-macro-econ-scenarios`
  tag `v1.0`, commit `d4703b6ae0d19dca08fbde11a25c218fa4c7b7a6`.
- Compute environment: GitHub-hosted Linux, *not* the user's Mac or the
  unverified local Docker interface. No LLM provider, new MCP, tunnel,
  private credentials or continuous background service.

## Research question, hypothesis and alternative

**Question:** Are new human labor tasks and cross-occupation mobility different
buffers against displacement by AI?

**Predeclared model hypothesis:** Reinstatement of new human tasks will increase
the share of national income going to workers; easier transitions between
occupations will reduce unemployment in AI-sensitive professions.

**Alternative:** One or both directional relationships fail to hold across the
three controlled levels of the other parameter.

In this model:

- `rho` governs creation of new human tasks within AI-sensitive occupations.
- `mu` governs ease of moving into another occupation group.
- These are **different economic mechanisms**; a worker moving to another
  occupation is not equivalent to the emergence of a new task.

The experiment holds the `substantial` scenario's other assumptions fixed,
with `rho = [0.00, 0.25, 0.50]` and `mu = [0.04, 0.08, 0.17]`.
There are nine 3×3 cells and one unmodified preset baseline: **10 model evaluations**.
Parameter values were selected in reviewed source code **before**
these outputs were calculated. They are assumptions, not real-world measurements.

## Predeclared directional checks

Each test uses the **highest minus lowest** chosen value of one axis
while holding the other axis at each of its three levels.
The reporting threshold is 0.02 percentage points; this is a numerical
criterion, not a statistical significance level.

| Prediction fixed before running | Held-axis values | Highest-minus-lowest change | Within-grid outcome |
|---|---|---|---|
| Higher `rho` → greater labor income share | `mu = 0.04 / 0.08 / 0.17` | +3.323 / +3.346 / +3.366 pp | Consistent at all three levels |
| Higher `mu` → lower unemployment, AI-sensitive | `rho = 0.00 / 0.25 / 0.50` | −2.020 / −1.474 / −0.949 pp | Consistent at all three levels |

For completeness, the original (unmodified) `substantial` preset baseline was:
GDP gain vs no AI **+8.283%**, labor income share **56.096%**, unemployment
(all workers) **4.529%**, unemployment (AI-sensitive workers) **4.498%**,
and average wage gain vs no AI **+2.137%**.

## Full model results, United States 2030

GDP and wage gains below are **relative to the model's no-AI counterfactual**,
not annual growth rates. Labor share and unemployment are percentage levels.

| rho | mu | GDP gain vs no AI | Labor income share | Unemployment, all | AI-sensitive unemployment | Average wage gain |
|---:|---:|---:|---:|---:|---:|---:|
| 0.000 | 0.040 | +9.307% | 54.455% | 5.459% | 6.236% | +1.103% |
| 0.000 | 0.080 | +9.926% | 54.418% | 4.906% | 5.217% | +1.022% |
| 0.000 | 0.170 | +10.442% | 54.388% | 4.441% | 4.216% | +0.953% |
| 0.250 | 0.040 | +7.862% | 56.120% | 4.915% | 5.255% | +2.193% |
| 0.250 | 0.080 | +8.283% | 56.096% | 4.529% | 4.498% | +2.137% |
| 0.250 | 0.170 | +8.613% | 56.077% | 4.227% | 3.781% | +2.094% |
| 0.500 | 0.040 | +6.355% | 57.778% | 4.442% | 4.364% | +3.191% |
| 0.500 | 0.080 | +6.595% | 57.764% | 4.217% | 3.869% | +3.158% |
| 0.500 | 0.170 | +6.772% | 57.754% | 4.052% | 3.415% | +3.137% |

## Interpretation: complementary outcomes, different trade-offs

**New human tasks** (`rho: 0 → 0.5` at `mu=0.08`):

- Labor share **+3.346 percentage points**, 54.418% → 57.764%.
- AI-sensitive unemployment **−1.348 percentage points**, 5.217% → 3.869%.
- Average wage gain above no-AI **+2.136 percentage points**, 1.022% → 3.158%.
- Incremental GDP gain above no-AI **−3.331 percentage points**, 9.926% → 6.595%.

**Worker mobility** (`mu: 0.04 → 0.17` at `rho=0.25`):

- AI-sensitive unemployment **−1.474 percentage points**, 5.255% → 3.781%.
- GDP gain above no-AI **+0.751 percentage points**, 7.862% → 8.613%.
- Labor share **−0.043 percentage points**, 56.120% → 56.077%.
- Average wage gain above no-AI **−0.099 percentage points**, 2.193% → 2.094%.

**Interaction to investigate, not claim as law:** the modeled
unemployment-reducing effect of improving mobility from 0.04 to 0.17
is smaller when more new tasks are already available:
−2.020 points at `rho=0` versus −0.949 points at `rho=0.5`.
The two mechanisms may partially substitute for each other on this
particular outcome in the sampled scenarios.

At every tested combination, model GDP still stands above its no-AI
counterfactual: a *smaller AI-related GDP gain* is not the same claim as
a shrinking real-world economy.

## Limitations and possible follow-up

These are conditional **within-model** comparisons, not evidence that
specific real-world retraining, employment, education or industrial
policies would produce these effects. They cannot establish the probability
of a scenario, the speed at which new jobs really appear, statistical
significance, or country-specific outcomes for Portugal.

Anthropic Economic Index observed use of Claude is **not used** to calibrate
the macroeconomic model; its automation terminology measures something
different from `psi`, `rho` and `mu`.

A future *separately approved* model study could test sensitivity to the
other preset scenarios or to a wider but finite parameter grid. This
record does not authorize any additional runs or Mac execution.
