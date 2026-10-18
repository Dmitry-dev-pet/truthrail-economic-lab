# First phenomenological extension: output demand, productivity and labor-hours response

**Research date:** 18 October 2026  
**Data:** U.S. BLS official *as-published* detailed service industry tables, 2022–2025  
**Status:** empirical, exploratory, reproducible, *negative out-of-period prediction result*  
**Not:** a causal AI-employment estimate, a forecast of the 2030 U.S. economy, or a calibration of Anthropic's task-reinstatement ratio rho.

## Research question

Will **last year's real-output-per-hour productivity growth** help forecast **this year's inflation-adjusted output growth**, beyond the previous year's output growth? If so, is the extra signal sufficiently reliable to improve a forecast of **labor-hours change** as a secondary outcome?

This tests one possible demand-expansion signal; it does **not** test whether AI itself improved productivity, changed prices, generated new products or caused employment changes.

## Why this is different from validating an identity

For real sectoral output Q, annual hours H, and output per hour A, the definition is:

```text
A = Q / H
(1 + growth_H) = (1 + growth_Q) / (1 + growth_A)
```

Plugging *observed contemporaneous* output and productivity back into the formula only verifies arithmetic. To prevent that circularity, this study first forecasts **next-year Q and A independently using lagged data**, then translates *those two predictions* into next-year hours H and evaluates against **unseen 2025 outcomes**. Lagged A is still not an instrument for an exogenous productivity shock or a measure of automation.

## Official sources and research population

The following original BLS *Table 1: Recent labor productivity, unit labor costs, and related data* releases were inspected and frozen:
- 2022 annual: https://www.bls.gov/news.release/archives/prin2_06292023.htm
- 2023 annual: https://www.bls.gov/news.release/archives/prin2_06272024.htm
- 2024 annual: https://www.bls.gov/news.release/archives/prin2_06262025.htm
- 2025 annual: https://www.bls.gov/news.release/prin2.htm

The 2023 news release explicitly warns about errors in **tables 2 and 3**, not table 1. This study uses *only table 1* from each publication, and explicitly excludes unsupported, coded-as-missing entries.

The [frozen numeric panel](data/2026-10-18-bls-service-output-hours-2022-25.json) contains **112 industry-year observations for 28 unique 2017 NAICS codes (2022–2025)**. All 28 codes appear in all four annual sources; overlapping published aggregate and child codes are excluded, e.g. parent publishing, telecommunications, or general freight groups are not double-counted with their detailed children. Inclusion is determined by publication availability, **not a random U.S. industry sample**. Industries vary vastly in worker counts and statistical precision; models here weight each included industry equally.

Variables:
- **Real output %**: annual percent growth of *real sectoral production*, not direct final-demand purchases or GDP.
- **Hours %**: annual growth in total labor hours worked by all persons.
- **Productivity %**: annual growth in real output per hour, linked mechanically to Q and H by construction.
- **Employment thousands**: covered industry-level employment, recorded for context, **not** the dependent variable in this experiment.

**Vintage problem:** publications are separate historical release vintages. Their underlying years can be revised in subsequent releases. For example, 2024 results published in 2025 were subsequently updated in the 2026 report. This is a panel of official *as-released percentage changes*, not a fully harmonized revised annual time series. **Nor is this a real-time Jan 1 forecast:** the previous calendar year's annual detailed-industry numbers are generally released in the middle of the following year.

## Plan fixed before any model estimation

[Plan and scientific guardrails](data/2026-10-18-lagged-productivity-research-plan.json) were committed before fitting. Each forecast uses only last-year industry outcomes. Training observations: **2023 and 2024 across 28 industries = 56**. Holdout: **2025 across all 28 industries**, not included in fitting. The study contains:

- **Persistence**: forecast output growth Q(t) from Q(t−1), no fit.
- **M0**: ordinary least-squares pooled regression `q_t = c + β q_(t-1)`.
- **M1**: pooled regression `q_t = c + β q_(t-1) + γ a_(t-1)`.
- **Secondary hours prediction**: forecast A(t) from a separately fitted autoregression on A(t−1), combine with M0 or M1 *predicted* Q(t) using the productivity identity, compare with the naive persistence of H(t−1).

No sector fixed effects: only two annual training dates per industry, so there is too little support to estimate rich sector dynamics. No structural or behavioral assumptions about firms' pricing, product demand elasticities, or AI productivity shocks were fitted.

## Holdout: 2025 real-output forecast

| Model | Training RMSE, pp | **2025 RMSE, pp** | 2025 MAE, pp |
|---|---:|---:|---:|
| Simple last-year output persistence | — | **4.329** | **3.607** |
| M0: fitted output autoregression | 5.077 | 4.795 | 3.958 |
| M1: output autoregression **+ lagged productivity** | 5.071 | 4.745 | 3.934 |

M1 improves M0's RMSE by **0.050 percentage points**, but the entirely unfitted persistence benchmark remains **0.416 pp more accurate than M1**. Fitted coefficients are:

```text
M0  predicted output growth = 0.167833 + 0.321500 × previous output growth
M1  predicted output growth = 0.217781 + 0.295194 × previous output growth
                                 + 0.054867 × previous productivity growth
```

The sign of the M1 lag-productivity coefficient is positive on this sample, but **cannot be read as a causal response of output to productivity**. The small improvement from M0 to M1 is not sufficient evidence for that mechanism.

For fixed fitted models, resampling the 28 industry predictions with replacement (2,000 draws; deterministic seed) gives an approximate **M0 RMSE − M1 RMSE** diagnostic spread of **−0.026 to +0.117 pp**, spanning zero. This is **not** a full confidence interval under correct independence assumptions; sectors share shocks and are selected rather than randomly sampled.

## Independent outcome: 2025 labor-hours forecast

| Model | **2025 hours-growth RMSE, pp** |
|---|---:|
| Previous-year **hours-growth persistence** | **4.068** |
| M0 forecast output + separately forecast productivity → hours | 4.128 |
| M1 forecast output + separately forecast productivity → hours | 4.150 |

The extra predictor **does not improve the prediction of labor demand measured as total hours**. All three predictions were generated from pre-2025 inputs; the output/hours identity was never scored against its own contemporaneous components.

## Useful direct measurement: four output / hours regimes in 2025

Within the deliberately selected 28 *non-overlapping* detailed industries:

| Observable direction | Number of industries |
|---|---:|
| Real output up; total hours up | **11** |
| Real output up; total hours down | **7** |
| Real output down; total hours up | **6** |
| Real output down; total hours down | **4** |

This is a **2025 descriptive classification**, not an AI impact estimate.

Examples (2025 percentage change, BLS table 1):
- **Software publishers (NAICS 5112):** real output **+12.1%**, labor productivity **+12.9%**, hours **−0.7%**. M1 forecasts only ~**+1.55%** output from preceding 2024 data, missing the subsequent jump.
- **Commercial banking (52211):** real output **+2.9%**, productivity **+3.2%**, hours **−0.3%**.
- **Full-service restaurants (722511):** output **+3.9%**, productivity **+4.5%**, hours **−0.6%**.
- **Engineering services (54133):** output **+2.6%**, productivity **−0.2%**, hours **+2.8%**.

Different combinations appear in the same year. Some sectors expand output with fewer hours; in others increased real output is associated with *more* hours. Neither outcome can be attributed to AI from this dataset.

## Scientific evaluation and next research gate

**Not found:** a stable, validated phenomelogical relationship in which last-year productivity predicts next-year additional real demand or labor-hours. The optimistic macro scenario's `rho=1` remains **an assumption**, not explained or estimated here.

**Found:** it is now practical to reproduce one of the economy's important measurement blocks (real output, worker hours and per-hour productivity), and to *demonstrate* that adding a plausible predictor can fail despite fit improving inside the training sample. The model should remain simple until new data add real explanatory power.

To investigate whether AI-driven cost reductions **generate genuine incremental paid demand**, future work needs variables outside the identity:
1. sector-specific real price / deflator series and quantity response (to estimate **price elasticity of demand** under careful identification), preferably using consistently revised BLS/BEA annual panels;
2. longer matched industry histories, independent exogenous shocks or suitable natural experiments to separate demand from productivity shocks;
3. task-level changes and company investments sufficiently detailed to link *new human tasks* to **paid labor hours**;
4. only then a trial extension `rho(t)=f(observed conditions)`, **as a separate reviewed model**, not an overwrite of the pinned U.S. reproduction.

The [BTOS/CES prior research](https://github.com/Dmitry-dev-pet/truthrail-economic-lab/issues/33) provides evidence on broad firm adoption and payroll employment, but its industrial and temporal granularity differs. **Do not merge the 2026 biweekly adoption rates into the 2025 detailed-industry productivity panel as if they are directly matched observations.**

## Reproduce

```bash
python -m ops.productivity_output_demand > productivity-output-demand-receipt.json
python -m unittest discover -s tests -v
```

Offline standard-library script; source data, plan, coefficients, all 28 holdout outcomes/predictions, error summaries and source SHA-256 digests contained in the machine-readable receipt.

**No** alteration of the pinned upstream mathematical model, 2030 scenarios, Portugal `runnable:false`, existing workflows, production API, GitHub owner-only issue permissions, VPS, MCP, Mac, Cloudflare, secrets or deployments.
