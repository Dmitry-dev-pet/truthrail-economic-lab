# Follow-up: AI diffusion and *actual U.S. payroll employment* by industry

**Research date:** 17 October 2026. **Status:** held-out exploratory diagnostic with a plan frozen before the model fit. This is a **non-causal** short-horizon predictive exercise, **not** a nationally representative estimate of employment effects, not a true real-time vintage backtest, and not a calibration of AI-induced task reinstatement `rho`.

## Why this follow-up was needed

[The prior BTOS industry audit](2026-10-17-btos-industry-lag.md) used an indicator that was not the number of people employed: the share of firms reporting a recent increase in employee count, minus the share reporting a decrease. A firm's yes/no answer does not quantify changes in the number of jobs.

This second audit instead studies monthly changes in the **actual number of payroll employees** collected and published by the U.S. Bureau of Labor Statistics (BLS). It retains *the same ten sectors*, but the BLS survey and the Census BTOS survey are different statistical populations.

## Source data and exact matching

- **BTOS:** [Frozen 120 sector-wave observations](data/2026-10-17-btos-sector-lag-panel.json), Census [official sector API](https://www.census.gov/hfp/btos/api/periods/90/data/naics2/51), from the November 17, 2025 change to the AI question through October 4, 2026.
- **BLS CES:** [Frozen 210 industry-month observations](data/2026-10-17-bls-ces-sector-employment.json), **10 monthly seasonally adjusted payroll-employee count series (thousands of workers)** for January 2025–September 2026, obtained from [BLS Public Data API v2](https://www.bls.gov/developers/api_signature_v2.htm).
- **Preset methodology:** [plan frozen before fitting](data/2026-10-17-btos-bls-lag-plan.json).
- **Reproduction script:** [`ops/btos_bls_payroll_lag.py`](../ops/btos_bls_payroll_lag.py) – Python standard library only.
- **Source cutoff:** September 2026 is the latest available payroll month as of this research date. The October 2026 BLS payroll release is scheduled for **6 November 2026**. August and September are marked preliminary in the frozen API.
- **Important vintage warning:** the downloaded BLS series contain values revised *as of* 17 October 2026. Using current-revised data for older forecast origins is **not a true real-time vintage evaluation**. A proper economic forecasting test would retain historical BLS publication vintages, not only the original dates.

BLS sector code mapping:

| BTOS code | Industry | BLS seasonally adjusted CES series |
|---|---|---|
| 23 | Construction | `CES2000000001` |
| 31 | Manufacturing (broad 31–33) | `CES3000000001` |
| 42 | Wholesale | `CES4142000001` |
| 44 | Retail (broad 44–45) | `CES4200000001` |
| 48 | Transportation and warehousing (broad 48–49) | `CES4300000001` |
| 51 | Information | `CES5000000001` |
| 52 | Finance and insurance | `CES5552000001` |
| 54 | Professional, scientific and technical services | `CES6054000001` |
| 62 | Health care and social assistance | `CES6562000001` |
| 72 | Accommodation and food services | `CES7072000001` |

The 31, 44 and 48 BTOS strata are labeled by abbreviated NAICS codes; confirm their broad industry aggregation against the corresponding CES universe before any stronger inference. BLS CES excludes some types of employment that are not counted consistently with BTOS. **The monthly payroll series describes payroll employment, not job vacancies, net hires, or employers' labor-demand schedules.**

## Predeclared temporal and statistical protocol

For each BTOS wave with a known **collection END calendar month** `c`, assign the AI-use share and firm's revenue-response balance to that month. Do **not** use any BLS month beyond September 2026. Define:

- **Outcome:** `100 × (CES[c+1] / CES[c] - 1)`: the actual percentage growth in *seasonally adjusted payroll employees* between the collection-end month and the next calendar month.
- **Last broadly available payroll growth at the survey origin:** `100 × (CES[c-1] / CES[c-2] - 1)`. This is available at the origin under ordinary BLS release timing; no `CES[c]` or `CES[c+1]` is used as a predictor.
- **BTOS revenue balance:** percentage of firms reporting higher revenue **minus** percentage reporting lower revenue. This is not sales growth in dollars.
- **AI predictors:** current BTOS share reporting use of AI in any business function, or the change in that share from the preceding sampled wave (four weeks earlier).

Take waves `90,92,94,96,98,100,102,104,106`, yielding 9 waves × 10 sectors = **90** sector-month observations. **Training:** waves 90–100, 60 rows, with future payroll outcomes January–June 2026. **Chronological holdout:** waves 102–106, 30 rows, with July–September 2026 outcomes.

Compare identical train/test rows:
- Persistence: predict future monthly job growth from the last broadly released monthly growth (no fitting).
- **M0:** sector intercepts, last available BLS monthly payroll growth, BTOS revenue balance.
- **M1:** M0 plus current BTOS percentage using AI.
- **M2:** M0 plus the four-week change in BTOS AI-use percentage.

Ordinary least squares in the small predetermined design; **no** predictor selection after seeing holdout errors. Training period has only six independent monthly dates, however, and the sector shocks are correlated: do not treat the 60 rows as independent draws.

## Results: AI metrics add only a vanishingly small predictive gain

| Model | Train RMSE, pp | **Holdout RMSE, pp** | Holdout MAE, pp |
|---|---:|---:|---:|
| Persistence | — | 0.20028 | 0.14027 |
| M0: sector, lagged payroll, revenue, *no AI* | 0.22184 | **0.15855** | 0.10806 |
| M1: baseline plus *AI-use level* | 0.22184 | **0.15817** | 0.10763 |
| M2: baseline plus *four-week change in AI use* | 0.22038 | **0.15785** | 0.10252 |

Unlike the earlier survey-incidence outcome, all three regressions beat the simple persistence benchmark on this *payroll-growth* target. But the reduction in M0 RMSE from adding AI-use level is only about **0.00038 percentage points** (from 0.15855 to 0.15817). The AI-change metric reduces it by about **0.00070 percentage points**. These are very small increments compared with the error of the regression itself.

A 2,000-draw **fixed-forecast sector block resampling diagnostic** for `M0 RMSE minus M1 RMSE` gives an approximate range **−0.00030 to +0.00099 pp**, median approximately **+0.00041 pp**. This diagnostic is neither a causal interval nor a valid full uncertainty assessment with only ten non-random sectors and six training dates.

### Descriptive difference in payroll employment: November 2025 to September 2026

| BLS employment industry | Change in payroll job count |
|---|---:|
| Information (51) | **−3.83%** (2,848.0k → 2,739.0k) |
| Finance/insurance (52) | **−1.35%** |
| Professional/technical services (54) | **+0.49%** |
| Manufacturing (31–33) | **+0.47%** |
| Health care/social assistance (62) | **+1.75%** |

The examples have very different employment paths; the panel does **not** establish whether AI caused any of them. Firms may be adopting AI because staffing conditions have changed, and industry revenue and employment may respond to other shocks.

## Major limits and acceptance decision

1. **Very short time window.** Only six dates for fitting, three for checking the forecast, and less than a year after the AI-questionnaire change. No meaningful six- or twelve-month causal or structural lag is identified.
2. **Not a natural experiment.** Industry adoption is endogenous to management choices, business demand and worker availability. Correlations do not identify a change in labor demand caused by AI.
3. **Sector aggregates mask individuals.** No linkage of firms, workers, tasks, pay, vacancies or training episodes. CES payroll totals omit self-employment; matching to Census employer-response shares is imperfect.
4. **Forecast vintages.** Although the chronological predictors are intentionally restricted to months normally available at forecast time, retrospective CES estimates are revised by October 2026. Not a genuine real-time backtest.
5. **Sampling and sector definition.** Ten purposefully chosen sectors, correlated outcomes, publication errors and revisions. OLS does not incorporate source sampling errors, and only CES (not BTOS) is seasonally adjusted.
6. **No evidence about `rho`.** Both "AI firms report creating new tasks" and "employment grew/contracted" can occur without identifying the number of new paid tasks relative to those automated. Do not invent an empirical value for the original U.S. macro-model reinstatement rate.

**Acceptance:** matched source data retrieved; planned one-month held-out study executed; ***no robust useful new predictive signal*** from the adoption metrics found in this limited public aggregate panel. The fitted coefficients are **not** policy elasticities or causal effects. Next scientific step, before new model equations, would be longer time series, source-vintage payroll releases, occupation/job-vacancy or hires data, and an identification strategy. Otherwise explicitly stop rather than overclaim.

## Reproduce offline

```bash
python -m ops.btos_bls_payroll_lag > bls-payroll-lag-receipt.json
python -m unittest discover -s tests -v
```

Requires only frozen repo JSON and standard Python, no external network. Nothing changes the original U.S. mathematical equations, Portugal's `runnable:false` status, authorized runners, Mac, VPS, Cloudflare, MCP, secrets, or CI permissions. This branch is stacked on the earlier [PR #34](https://github.com/Dmitry-dev-pet/truthrail-economic-lab/pull/34). Related research [Issue #33](https://github.com/Dmitry-dev-pet/truthrail-economic-lab/issues/33).
