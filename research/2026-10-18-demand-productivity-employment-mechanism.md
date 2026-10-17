# Market demand, productivity and paid work: the first phenomenological mechanism

**Date:** 2026-10-18. **Status:** a reproducible *illustrative* partial-equilibrium mechanism plus a 2025 BLS accounting audit. **Not an AI impact estimate, not a new macroeconomic forecast, not an independent empirical validation, and not a calibration of Anthropic `rho`.** Original U.S. structural model and the Portugal audit remain unchanged.

## Research question

How can better productivity coexist with **more**, **unchanged** or **fewer** labor hours, when customers and firms respond to prices? What needs to be observed before such a mechanism is empirically estimated, rather than simply asserted?

## First separation: identity versus behavioral hypothesis

With real industry output `Q`, labor hours worked `H`, output per hour `A=Q/H`, number of workers `N`, and average hours per worker `h=H/N`, we have the accounting identities:

```
H = Q / A
N = Q / (A*h)
delta log N = delta log Q - delta log A - delta log h
```

These are useful decompositions but **cannot be validated as a theory** by regressing one accounting component on the others. BLS's reported labor productivity is **constructed** from real output divided by total hours worked. `H` and `N` are not interchangeable: changes in working time per worker, self-employment and population coverage matter.

## Second separation: a hypothetical market response

Add one deliberately simplified **testable candidate**, not a fact about U.S. demand. For a positive productivity improvement `A1/A0`, let:

```
P1/P0 = (A1/A0)^(-tau)                          0 <= tau <= 1
Q1/Q0 = (1+g_D) * (P1/P0)^(-epsilon)           epsilon >= 0
H1/H0 = (Q1/Q0)/(A1/A0)
N1/N0 = (H1/H0)/(h1/h0)
```

`P` is the output price, `tau` a **hypothesized pass-through of productivity to price** (not directly observed cost pass-through), `epsilon` the absolute value of a constant price elasticity of demand, `g_D` an autonomous demand shift at the same prices (possibly new markets, higher income, quality, etc.), and `h` annual hours per worker. All products and market shares are assumed comparable; no cross-industry transfers, markups, supply constraints or input-price dynamics are explicitly modeled. The price and demand equations here are **behavioral assumptions**, unlike the accounting identity.

For no exogenous demand change and unchanged hours per worker, the number of workers is preserved if and only if **`epsilon * tau = 1`**; it rises for a product above 1 and falls below 1. With exogenous demand shifts or hours-per-worker changes, the threshold moves. This does **not** mean observed outcomes identify `epsilon` and `tau` separately.

### Fixed numeric illustrations, not fitted predictions

All rows hold productivity improvement at **10%**, price-response parameter `tau=0.8`, autonomous real demand growth = 0, and average annual hours per worker unchanged. These are **user-editable model hypotheses**, not estimates:

| Elasticity `epsilon` | Implied price | Implied real output | Implied labor hours / workers |
|---:|---:|---:|---:|
| 0.50 | -7.34% | +3.89% | **-5.56%** |
| 1.25 | -7.34% | +10.00% | **0.00%** |
| 2.00 | -7.34% | +16.47% | **+5.88%** |

Under these simplifying assumptions it is *plausible in the model* that market demand responds enough to absorb productivity gains. It is **not guaranteed in reality**; the price elasticity, price-setting, non-price quality, capital investment, firm entry, wages and composition must be studied.

## 2025 BLS observations: distinct combinations already exist

[Service-industry 2025 BLS Table 1](https://www.bls.gov/news.release/prin2.t01.htm) (26 August 2026) and [Manufacturing 2025 BLS release](https://www.bls.gov/news.release/prin.htm) (24 June 2026) contain the output, labor productivity and hours-worked changes for ten **deliberately selected** NAICS industries reproduced in [machine-readable source snapshot](data/2026-10-18-bls-output-productivity-hours-2025.json). This is *not* a probability sample, nor were the values provided by a measured AI shock.

| Sector | Real output | Labor productivity | Total hours |
|---|---:|---:|---:|
| Software publishers (5112) | +12.1% | +12.9% | -0.7% |
| Gambling (7132) | +11.2% | +2.7% | +8.3% |
| Engineering services (54133) | +2.6% | -0.2% | +2.8% |
| Commercial banking (52211) | +2.9% | +3.2% | -0.3% |
| Wireless telecoms (517312) | +4.1% | +8.8% | -4.3% |
| Other transportation equipment (3369) | -2.3% | +14.9% | -15.0% |

Across all ten frozen rows, `100*((1+output_growth/100)/(1+productivity_growth/100)-1)` agrees with BLS-reported hours change within **0.031 percentage points**. **This is merely a rounding and transcription sanity check on a definitional identity**. It cannot independently verify the behavioral price or demand functions, and the strong changes are **not evidence AI caused them**. BLS labor productivity itself can move due to capital intensity, organization, workforce mix, offshoring and other non-AI factors.

## What must be independently estimated

1. **Output prices:** matched industry output price indexes (BLS detailed output deflators or BEA gross-output indexes). Distinguish producer prices from consumer prices; do not replace these with general CPI.
2. **Real output and demand shifts:** BLS industry sectoral-output indexes or BEA gross-output real quantity indexes, plus separately sourced consumer incomes/spending, business purchases, product quality and new-product entry to model autonomous market expansion. Observed production `Q` is *not identical to a directly observed unconstrained demand curve*.
3. **Productivity and work:** harmonized industry output-per-hour, hours and jobs. CES payroll employees from previous Economic Lab work are not automatically consistent with BLS productivity's all-worker hours and annual output measures.
4. **Identification:** prices, productivity and output are jointly endogenous; simply regressing Q on P estimates neither price demand elasticity nor price pass-through causally. Need credible exogenous price/cost changes, instruments, events, market heterogeneity, or carefully justified modeling assumptions. Prefer held-out data and sensitivity analysis rather than a calibrated coefficient without identification.
5. **AI-specific mechanism:** firm AI adoption, *task displacement*, newly remunerated human tasks, capital investment and employer hiring must eventually be measured separately. The model's aggregate demand shift `g_D` and empirical price elasticity are **not** Anthropic `rho`, the ratio of human task reinstatement to automated tasks. They must never be relabeled as such.

The dataset covers one annual observation per industry in 2025, so **no independent price elasticity is estimated** in this PR; it would be methodologically false to infer structural parameter values. The appropriate next research task is to assemble aligned, *multiple-year*, separate **price and quantity** series and define a credible design before any fit. All tests in this PR are identity/algorithm safeguards, not a finding about the strength of market responses.

## Reproduce without Docker or new services

```bash
python -m ops.demand_productivity_mechanism
python -m unittest tests.test_demand_productivity_mechanism -v
```

Both commands use only frozen public source rows and Python standard library. They do not modify the Anthropic-derived mathematical model, existing GitHub issue workflow, Mac, VPS, MCP, or Portuguese country settings. Related previous short-run association studies: [Issue #33](https://github.com/Dmitry-dev-pet/truthrail-economic-lab/issues/33), [PR #34](https://github.com/Dmitry-dev-pet/truthrail-economic-lab/pull/34), [PR #35](https://github.com/Dmitry-dev-pet/truthrail-economic-lab/pull/35).
