# Robustness across three AI economic scenarios: new tasks × mobility

**Date:** 2026-10-17. **Study status:** all three scenario runs completed;
30 model evaluations total (3 scenario baselines + 27 parameter cells).
US macroeconomic model *through 2030*, not a prediction of employment
in the United States or Portugal.

**Pinned independent code:** `fhoces/opa-ai-macro-econ-scenarios`,
tag `v1.0`, commit `d4703b6ae0d19dca08fbde11a25c218fa4c7b7a6`.
The work used existing owner-only GitHub issues and **GitHub-hosted Linux**,
not Mac Docker, another MCP, another LLM or an unbounded background agent.

## Question and unchanged ex-ante plan

Do the two already-reviewed directional model hypotheses persist across
`modest`, `substantial` and `extreme` presets?

1. Higher `rho` (new human tasks per automated task) raises the labor
   share, at each fixed level of `mu`.
2. Higher `mu` (ease of moving to a different occupation) reduces
   unemployment among AI-sensitive workers, at each fixed `rho`.

The original hypothesis and numerical criterion were fixed **before**
the first source experiment in
[PR #6](https://github.com/Dmitry-dev-pet/truthrail-economic-lab/pull/6).
Every run used `rho=[0.00,0.25,0.50]`,
`mu=[0.04,0.08,0.17]`, the same
0.02 percentage-point directional threshold and the same
`new_tasks_vs_mobility` catalogue entry. The other assumptions
are those of each respective published preset.

## Sources and plan hashes

| Preset | Original owner-computed issue | Pre-computation SHA-256 plan fingerprint |
|---|---|---|
| Умеренный | [#11](https://github.com/Dmitry-dev-pet/truthrail-economic-lab/issues/11) | `a300f7de8cbb1afc10650c1106dc77e412d4ade847ca9d690cbc65487a16cf9a` |
| Существенный | [#9](https://github.com/Dmitry-dev-pet/truthrail-economic-lab/issues/9) | `ee9373b153584ab33c9b43ec3f5b72b085a3801725ce45f1d077a8e155146c25` |
| Экстремальный | [#12](https://github.com/Dmitry-dev-pet/truthrail-economic-lab/issues/12) | `8bfab0f362fb952de920e938d92993d41e041be36a537094613248f4ec46c6ee` |

## All six preregistered directional tests

Each cell compares the **highest minus lowest** tested value of the
named parameter at each controlled level of the other parameter,
measured in percentage points (pp). Both predictions held
consistently at every tested level; this is **not** a statistical
significance test or empirical validation.

| Preset | `rho↑` labor-share effect at `mu=0.04 / 0.08 / 0.17` | `mu↑` AI-sensitive unemployment effect at `rho=0 / 0.25 / 0.5` |
|---|---|---|
| Умеренный | +0.733 / +0.734 / +0.734 pp | -0.258 / -0.206 / -0.157 pp |
| Существенный | +3.323 / +3.346 / +3.366 pp | -2.020 / -1.474 / -0.949 pp |
| Экстремальный | +10.330 / +10.463 / +10.593 pp | -7.621 / -5.624 / -3.760 pp |

## Consistent-point contrasts (different from original preset baselines)

For comparability, `rho:0→0.5` is measured at fixed `mu=0.08`,
and `mu:0.04→0.17` is measured at fixed `rho=0.25`.
All deltas are **percentage points**; GDP refers to the
incremental level relative to a no-AI counterfactual, not
growth in calendar year 2030.

| Preset | New tasks: labor share | New tasks: AI-sensitive unemployment | New tasks: GDP gain | Mobility: AI-sensitive unemployment | Mobility: GDP gain | Mobility: labor share |
|---|---:|---:|---:|---:|---:|---:|
| Умеренный | +0.734 | -0.128 | -0.777 | -0.205 | +0.089 | -0.005 |
| Существенный | +3.346 | -1.348 | -3.331 | -1.474 | +0.751 | -0.043 |
| Экстремальный | +10.463 | -7.367 | -11.622 | -5.623 | +4.643 | -0.253 |

**Interpretation, confined to this model:** creating more new labor
tasks raises workers' share of income and reduces joblessness
but reduces the *additional GDP gain attributed to AI*.
Easier mobility reduces AI-sensitive joblessness and raises
the additional AI-related GDP gain, with smaller or negative
effects on labor share. Both mechanisms become numerically
more influential across these particular moderate-to-extreme
preset comparisons. Their effects on unemployment partly
substitute in each of the sampled grids: higher `rho`
is associated with a smaller *additional* reduction from
increasing `mu`.

## Original baselines (do not confuse with a universal grid center)

- **Умеренный:** GDP gain vs no AI: 1.605%, Labor income share: 59.413%, Unemployment, all: 3.860%, Unemployment, AI-sensitive: 2.914%, Wage gain vs no AI: 0.689%
- **Существенный:** GDP gain vs no AI: 8.283%, Labor income share: 56.096%, Unemployment, all: 4.529%, Unemployment, AI-sensitive: 4.498%, Wage gain vs no AI: 2.137%
- **Экстремальный:** GDP gain vs no AI: 32.422%, Labor income share: 45.211%, Unemployment, all: 11.864%, Unemployment, AI-sensitive: 17.889%, Wage gain vs no AI: 9.651%

The original preset occupies different coordinates in each grid
(`modest`: `rho=0.5,mu=0.17`; `substantial`:
`rho=0.25,mu=0.08`; `extreme`: `rho=0,mu=0.04`).
This is why the standardized contrasts above compare the **same**
pairs within each preset, rather than differences against
three incomparable preset baselines.

## Full model output: all 27 combinations

GDP and average-wage gain values are % **relative to the modeled
no-AI counterfactual**; labor share and unemployment are percentage
levels, not percentage-point changes.

### Умеренный — [original computation](https://github.com/Dmitry-dev-pet/truthrail-economic-lab/issues/11)

| ρ | μ | GDP gain | Labor share | Unemployment all | Unemployment AI-sensitive | Wage gain |
|---:|---:|---:|---:|---:|---:|---:|
| 0.000 | 0.040 | 2.287% | 58.684% | 4.005% | 3.255% | 0.281% |
| 0.000 | 0.080 | 2.334% | 58.681% | 3.962% | 3.128% | 0.278% |
| 0.000 | 0.170 | 2.390% | 58.678% | 3.911% | 2.997% | 0.277% |
| 0.250 | 0.040 | 1.909% | 59.051% | 3.967% | 3.160% | 0.488% |
| 0.250 | 0.080 | 1.946% | 59.049% | 3.932% | 3.062% | 0.486% |
| 0.250 | 0.170 | 1.998% | 59.046% | 3.885% | 2.955% | 0.485% |
| 0.500 | 0.040 | 1.526% | 59.417% | 3.933% | 3.071% | 0.690% |
| 0.500 | 0.080 | 1.557% | 59.415% | 3.904% | 3.000% | 0.689% |
| 0.500 | 0.170 | 1.605% | 59.413% | 3.860% | 2.914% | 0.689% |

### Существенный — [original computation](https://github.com/Dmitry-dev-pet/truthrail-economic-lab/issues/9)

| ρ | μ | GDP gain | Labor share | Unemployment all | Unemployment AI-sensitive | Wage gain |
|---:|---:|---:|---:|---:|---:|---:|
| 0.000 | 0.040 | 9.307% | 54.455% | 5.459% | 6.236% | 1.103% |
| 0.000 | 0.080 | 9.926% | 54.418% | 4.906% | 5.217% | 1.022% |
| 0.000 | 0.170 | 10.442% | 54.388% | 4.441% | 4.216% | 0.953% |
| 0.250 | 0.040 | 7.862% | 56.120% | 4.915% | 5.255% | 2.193% |
| 0.250 | 0.080 | 8.283% | 56.096% | 4.529% | 4.498% | 2.137% |
| 0.250 | 0.170 | 8.613% | 56.077% | 4.227% | 3.781% | 2.094% |
| 0.500 | 0.040 | 6.355% | 57.778% | 4.442% | 4.364% | 3.191% |
| 0.500 | 0.080 | 6.595% | 57.764% | 4.217% | 3.869% | 3.158% |
| 0.500 | 0.170 | 6.772% | 57.754% | 4.052% | 3.415% | 3.137% |

### Экстремальный — [original computation](https://github.com/Dmitry-dev-pet/truthrail-economic-lab/issues/12)

| ρ | μ | GDP gain | Labor share | Unemployment all | Unemployment AI-sensitive | Wage gain |
|---:|---:|---:|---:|---:|---:|---:|
| 0.000 | 0.040 | 32.422% | 45.211% | 11.864% | 17.889% | 9.651% |
| 0.000 | 0.080 | 35.959% | 45.004% | 9.576% | 14.278% | 9.274% |
| 0.000 | 0.170 | 39.412% | 44.807% | 7.262% | 10.269% | 8.832% |
| 0.250 | 0.040 | 27.934% | 50.413% | 9.132% | 12.873% | 14.265% |
| 0.250 | 0.080 | 30.312% | 50.282% | 7.457% | 10.141% | 14.012% |
| 0.250 | 0.170 | 32.577% | 50.160% | 5.816% | 7.250% | 13.731% |
| 0.500 | 0.040 | 22.899% | 55.541% | 6.832% | 8.779% | 17.730% |
| 0.500 | 0.080 | 24.337% | 55.467% | 5.725% | 6.911% | 17.567% |
| 0.500 | 0.170 | 25.650% | 55.400% | 4.695% | 5.019% | 17.403% |

## Scientific and infrastructure limitations

- This compares **assumed** scenario conditions in an independent
  reproducible mathematical model, not observed labor outcomes.
- Scenario presets differ in other input assumptions as well:
  variation in effect size cannot be attributed to a single
  underlying cause or treated as a general law.
- Conditional model consistency is **not** a causal policy estimate,
  probability assessment, statistical significance test or forecast.
- The independent Anthropic Economic Index MCP is **not** a
  calibrated input to this macroeconomic study.
- Table cells are rounded to 0.001, so arithmetic differences
  can differ from full-precision model tests by 0.001 pp.
- This was a **one-time user-requested** cross-scenario study,
  no unattended next experiments, model-provider API use,
  VPS process, new MCP or Mac authority.

