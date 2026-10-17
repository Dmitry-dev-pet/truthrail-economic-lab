# Empirical probe: does industry AI adoption lead employment changes?

**Date:** 2026-10-17. **Status:** complete exploratory, reproducible aggregate-data audit; **not a causal study, not a forecast of the U.S. labor market, and not an estimation of Anthropic model `rho`.**

## Research question and primary decision

After changes in survey methodology in November 2025, does a publicly observed **industry AI-use share** provide additional information about **next-wave firm-reported changes in number of employees** beyond recent employment and revenue movements?

**Result: no useful forecast improvement in this small initial test.** Adding current AI adoption *worsens* the holdout root-mean-square error of an already weak sector-level forecasting regression, while the increase in AI adoption over the prior four weeks makes only a tiny difference. A **naive persistence forecast is substantially better than all three regression specifications**. This does **not** demonstrate that AI has no effect on labor demand.

## Original source and sampling

- [Census Business Trends and Outlook Survey (BTOS)](https://www.census.gov/hfp/btos/), core questions. Documentation: [BTOS Data](https://www.census.gov/data/experimental-data-products/business-trends-and-outlook-survey.html), [downloads](https://www.census.gov/hfp/btos/data_downloads).
- Public time-stamped API: `https://www.census.gov/hfp/btos/api/periods/{period}/data/naics2/{sector}`, for each exact period/sector listed in the [frozen, machine-readable extract](data/2026-10-17-btos-sector-lag-panel.json).
- The AI-use question was **reworded on 17 November 2025**, from AI in production of goods/services to AI in *any business function*. Earlier waves must not be naively pooled with these observations. The first retained collection is 17–30 November 2025; the last ends **4 October 2026**.
- **Ten purposively selected NAICS2 sectors:** construction (23), manufacturing (31), wholesale (42), retail (44), transportation and warehousing (48), information (51), finance and insurance (52), professional/technical services (54), health care/social assistance (62), accommodation/food services (72).
- **Twelve public biweekly collections, sampled once every four weeks:** period IDs `88,90,92,94,96,98,100,102,104,106,108,110`. **120** sector × time records; zero missing for five variables used below. All ten sectors receive equal analytical weight, *not* Census survey population weights; this mean is **not** a U.S. national adoption rate.
- **AI(t):** weighted percentage of businesses in an industry reporting current AI use in a business function over the previous two weeks.
- **E(t):** percentage of businesses reporting increased paid employees over the previous two weeks **minus** percentage reporting decreased employees. Unit: **percentage points of firm incidence**. E is *not* the change in total jobs, net hires, vacancies, employment growth or labor demand.
- **R(t):** same signed firm-incidence balance for changes in business revenue over the previous two weeks. Standard errors from the API are archived in the full extract.

As a descriptive sanity check, the **unweighted average of ten industry adoption shares** rises from **18.57%** at the first observation to **25.48%** at the last. The Information industry changes from **41.0% to 50.2%**. Neither comparison estimates a causal impact on employment.

## Reproducible held-out comparison

For each sector, use the next available sample wave to predict E(t+1), roughly **four weeks** after the observed predictor wave. For equal sample coverage, changes in AI are computed from the previous wave, so the training design starts in the second available period.

The pre-specified *simple comparison* has:

- **M0**: sector intercepts, linear sample-period trend, E(t), R(t).
- **M1**: M0 plus the level of AI(t).
- **M2**: M0 plus the four-week change in AI(t).
- **Naive benchmark**: E(t+1) = E(t), without fitted coefficients.

All models use identical sector/time sample and the same target. **70 training records** (t=1 through 7), with the latest **30 held out** (t=8 through 10, targets in periods 106,108,110). These are repeated **aggregate sector observations**, **not** 100 independent firms. No individual source firms, tasks, earnings or employee headcounts are linked.

| Method | Train RMSE (pp) | Holdout RMSE (pp) | Holdout MAE (pp) |
|---|---:|---:|---:|
| Naive E(t) persistence | — | **1.589** | **1.183** |
| M0: without AI | 1.366 | 2.575 | 2.262 |
| M1: plus AI level | 1.358 | 2.610 | 2.225 |
| M2: plus AI four-week change | 1.366 | 2.560 | 2.251 |

An industry-block resampling diagnostic on the **fixed holdout errors** (2,000 resamples; M0 minus M1 RMSE, *positive* means M1 improves) gives an approximate **−0.16 to +0.11 pp** range, median about **−0.03 pp**. This is neither a causal confidence interval nor full sampling/model-estimation uncertainty. It simply shows the small relative holdout difference is not robust to which sectors are represented.

The fitted regression models extrapolate later employment-balance changes poorly and are beaten by persistence. Their AI coefficients should **not** be interpreted as effects of an additional 1% AI adoption on the number of jobs.

## Scientific limitations and interpretation

1. The outcome is *the difference between two shares of firms reporting directional changes in employee count*. It ignores magnitudes and is not a numerical measure of total sector employment or demand for labor.
2. With **one wave per four weeks**, late 2025–October 2026, the sample spans less than one annual cycle and cannot meaningfully separate trend, seasonality, business cycle, delayed investment effects and implementation lags. The fitted linear trend is especially vulnerable to extrapolation.
3. The ten sectors were chosen deliberately, not randomly. Their equal-weight average should not be mistaken for the official nationally representative aggregate or a reliable cross-section of all U.S. employment.
4. Published weighted survey proportions have sampling error and changing firm samples. The regression shown is unweighted and does not propagate sampling errors in both dependent and independent variables; industry/time clustering remains.
5. Regression-level comparison is **exploratory predictive association**, not a causal identification design. No adjustment for endogeneity, selection, heterogeneous AI use within industry, differential staffing changes, or omitted demand shocks.
6. Published company-level data on AI-created vs AI-replaced task **counts** and new paid jobs are insufficient for calibrating `rho`; this audit **does not** use Anthropic Economic Index usage counts as a task-reinstatement estimate.

## Reproduce

```bash
python -m ops.btos_lag_study > btos-lead-lag-receipt.json
python -m unittest discover -s tests -v
```

The script uses only Python's standard library and the exact frozen JSON observations from the published Census API; it has **no network calls**. It reports source, data-byte SHA-256, exact selected dates and sectors, train/holdout counts, prediction metrics and block-resampling diagnostic. Changes to this file or the data require explicit reviewed changes in GitHub. It does **not** touch model equations, Portugal country profile, deployment, or credentials.

## Research consequence

The appropriate inference is **we have not established a short-horizon sector-level predictive signal from current aggregate AI use to directional headcount-change incidence**. Do not treat the sign of a regression coefficient as proof of AI displacing or reinstating jobs. The next stronger test should align adoption data with independent **monthly sector employee headcounts or hires/job postings**, cover longer lags, account for seasonality and investigate heterogeneity inside industries. The first version should remain independent of the original U.S. Anthropic-derived structural model.

Related roadmap: [Issue #33](https://github.com/Dmitry-dev-pet/truthrail-economic-lab/issues/33).
