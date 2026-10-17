# Economic Lab: Which model assumptions matter most in numerical sensitivity?

**Date:** 2026-10-17. **Status:** Completed owner-requested calculations
in the three named U.S. 2030 scenarios. **57 model evaluations**:
19 per scenario, consisting of one unchanged baseline and two endpoints
for each of nine predeclared model inputs.

## Research question and method

Which allowed input assumptions have the largest **numerical effect**
on model results when varied one by one?

The analysis implementation was reviewed and merged via
[PR #14](https://github.com/Dmitry-dev-pet/truthrail-economic-lab/pull/14) before any of these
owner-issued requests. It uses independent macroeconomic model
`fhoces/opa-ai-macro-econ-scenarios` tag `v1.0` pinned at
`d4703b6ae0d19dca08fbde11a25c218fa4c7b7a6`.

Each model input is varied by **one interval whose width is 10% of
the implemented permissible range**. All other model inputs remain
at the named preset. The interval includes the preset's original
value; if the preset is close to a limit, the interval shifts
inside the legal range rather than shrinking. Accordingly, the
low-to-high contrast may be **one-sided** with respect to the
baseline. This is a finite-difference comparison, *not*
a derivative, elasticity or estimate of plausible uncertainty.

Studied parameters: scenario assumptions `m_2030` (tasks reached),
`d_2030` (AI adoption), `a_2030` (productivity gain),
`psi` (labor-replacing share), `rho` (new human tasks),
`mu` (worker mobility) and `theta_H` (vacancy creation);
and structural model inputs `eps` and `xi`.
The labels are shorthand for model dials, not observational estimates.

Only predeclared **absolute changes in percentage points**
are used for ranking, with a **separate ranking per outcome**:
GDP above a no-AI counterfactual, labor income share, all-worker
unemployment, AI-sensitive unemployment, and average wage gain
above no AI.

## Audit records and plan fingerprints

| Scenario | Public owner-issued computation | Frozen SHA-256 plan |
|---|---|---|
| Умеренный | [Issue #16](https://github.com/Dmitry-dev-pet/truthrail-economic-lab/issues/16#issuecomment-6233434919) | `8f43d1ca3b874d1456bca5cd42816926fd6a18e270846b521351948d0067176d` |
| Существенный | [Issue #15](https://github.com/Dmitry-dev-pet/truthrail-economic-lab/issues/15#issuecomment-6233430955) | `fec7a947c0a7e65514a2833dd38cd250d5d0d14e0c74e8e4da4a4e02c17d958d` |
| Экстремальный | [Issue #17](https://github.com/Dmitry-dev-pet/truthrail-economic-lab/issues/17#issuecomment-6233438639) | `e35bbce70df318638c7186b92ca70ff79c17d0f03c03f81c0fb3fc3b614cfa4b` |

Each exact-title `[econ] experiment` issue contained only the JSON
`{"analysis":"sensitivity","scenario":"<name>"}`. Computation
occurred on public GitHub-hosted Linux under a read-only token;
an isolated, narrowly authorized reporting job published the
complete results in the issue. No new MCP, Mac deployment, Docker
daemon, AGY, provider token, VPS workload or continuous monitor
was introduced.

## Largest numerical responses in each preset

Positive/negative changes show whether the output increased or
decreased as the named parameter moved from the sampled low
endpoint to the high endpoint. They are **percentage points**.

| Model outcome | Modest | Substantial | Extreme |
|---|---|---|---|
| GDP gain above no AI | `d_2030` (+0.684 pp) | `m_2030` (+2.178 pp) | `mu` (+12.493 pp) |
| Labor income share | `d_2030` (-0.263 pp) | `m_2030` (-1.061 pp) | `m_2030` (-2.525 pp) |
| All unemployment | `d_2030` (+0.059 pp) | `mu` (-0.761 pp) | `mu` (-7.897 pp) |
| AI-sensitive unemployment | `d_2030` (+0.087 pp) | `mu` (-1.537 pp) | `mu` (-11.727 pp) |
| Average wage gain above no AI | `a_2030` (+0.673 pp) | `a_2030` (+2.106 pp) | `a_2030` (+6.054 pp) |

**Qualitative findings limited to these bounds:** In the
moderate case, task adoption / exposure dominates most
level outcomes; as the assumptions become more extreme,
`mu` becomes the dominant numerical lever for unemployment
and even the incremental GDP gain. The output gain from AI
is not equivalent to calendar-year economic growth.
`a_2030` produces the largest observed wage-gain response
in all three presets, but the size of that result also
depends on its chosen 0.2 numerical window.

For the extreme preset, `mu` starts at just **0.04**, near
its implemented lower bound of **0.001**, so the fixed-width
interval is shifted to `0.001–0.10090`. That asymmetry
and nonlinear model behavior are important qualifications
to its large **−11.727 pp** AI-sensitive unemployment
response and **+12.493 pp** GDP-gain response.

## Full signed high-minus-low sensitivity table

**Each row is one numeric parameter contrast**, not a new
three-scenario forecast. Entries are changes in **percentage
points**, with baseline values and explicit low/high endpoints
shown. The original issue receipts also round outcome changes
to three decimals; the simulation internally used higher precision.

### Умеренный (modest)

**Unmodified original preset:** GDP gain vs no AI: 1.605%, Labor income share: 59.413%, Unemployment, all: 3.860%, Unemployment, AI-sensitive: 2.914%, Wage gain vs no AI: 0.689%

| Parameter | Type | Original | Tested endpoints (low → high) | GDP gain | Labor share | All unemployment | AI-sensitive unemployment | Wage gain |
|---|---|---:|---|---:|---:|---:|---:|---:|
| `m_2030` | scenario | 0.20000 | 0.15950 → 0.24050 | +0.616 | -0.236 | +0.053 | +0.078 | +0.276 |
| `d_2030` | scenario | 0.20000 | 0.15500 → 0.24500 | +0.684 | -0.263 | +0.059 | +0.087 | +0.307 |
| `a_2030` | scenario | 0.30000 | 0.20000 → 0.40000 | +0.508 | +0.090 | +0.014 | +0.021 | +0.673 |
| `psi` | scenario | 0.50000 | 0.45000 → 0.55000 | +0.113 | -0.106 | +0.007 | +0.011 | -0.058 |
| `rho` | scenario | 0.50000 | 0.45000 → 0.55000 | -0.157 | +0.147 | -0.010 | -0.016 | +0.080 |
| `mu` | scenario | 0.17000 | 0.12005 → 0.21995 | +0.047 | -0.003 | -0.043 | -0.074 | +0.000 |
| `theta_H` | scenario | 0.10000 | 0.05005 → 0.14995 | +0.060 | -0.003 | -0.059 | -0.043 | -0.010 |
| `eps` | structural | 3.00000 | 2.52500 → 3.47500 | +0.067 | +0.039 | +0.002 | +0.002 | +0.134 |
| `xi` | structural | 0.50000 | 0.45000 → 0.55000 | -0.013 | +0.001 | +0.013 | +0.012 | +0.003 |

### Существенный (substantial)

**Unmodified original preset:** GDP gain vs no AI: 8.283%, Labor income share: 56.096%, Unemployment, all: 4.529%, Unemployment, AI-sensitive: 4.498%, Wage gain vs no AI: 2.137%

| Parameter | Type | Original | Tested endpoints (low → high) | GDP gain | Labor share | All unemployment | AI-sensitive unemployment | Wage gain |
|---|---|---:|---|---:|---:|---:|---:|---:|
| `m_2030` | scenario | 0.30000 | 0.25950 → 0.34050 | +2.178 | -1.061 | +0.383 | +0.732 | +0.572 |
| `d_2030` | scenario | 0.40000 | 0.35500 → 0.44500 | +1.824 | -0.885 | +0.310 | +0.595 | +0.472 |
| `a_2030` | scenario | 0.44800 | 0.34800 → 0.54800 | +1.343 | +0.426 | +0.053 | +0.100 | +2.106 |
| `psi` | scenario | 0.75000 | 0.70000 → 0.80000 | +0.491 | -0.490 | +0.099 | +0.193 | -0.313 |
| `rho` | scenario | 0.25000 | 0.20000 → 0.30000 | -0.666 | +0.669 | -0.139 | -0.270 | +0.427 |
| `mu` | scenario | 0.08000 | 0.03005 → 0.12995 | +0.831 | -0.048 | -0.761 | -1.537 | -0.110 |
| `theta_H` | scenario | 0.25000 | 0.20005 → 0.29995 | +0.174 | -0.010 | -0.160 | -0.164 | -0.024 |
| `eps` | structural | 3.00000 | 2.52500 → 3.47500 | +0.440 | +0.236 | +0.024 | +0.036 | +0.867 |
| `xi` | structural | 0.50000 | 0.45000 → 0.55000 | -0.133 | +0.008 | +0.133 | +0.199 | +0.038 |

### Экстремальный (extreme)

**Unmodified original preset:** GDP gain vs no AI: 32.422%, Labor income share: 45.211%, Unemployment, all: 11.864%, Unemployment, AI-sensitive: 17.889%, Wage gain vs no AI: 9.651%

| Parameter | Type | Original | Tested endpoints (low → high) | GDP gain | Labor share | All unemployment | AI-sensitive unemployment | Wage gain |
|---|---|---:|---|---:|---:|---:|---:|---:|
| `m_2030` | scenario | 0.50000 | 0.45950 → 0.54050 | +6.084 | -2.525 | +1.749 | +3.324 | +1.176 |
| `d_2030` | scenario | 0.60000 | 0.55500 → 0.64500 | +5.323 | -2.320 | +1.854 | +3.468 | +1.233 |
| `a_2030` | scenario | 0.80000 | 0.70000 → 0.90000 | +3.834 | +1.111 | +0.137 | +0.250 | +6.054 |
| `psi` | scenario | 0.90000 | 0.85000 → 0.95000 | +1.256 | -1.560 | +0.860 | +1.614 | -1.577 |
| `rho` | scenario | 0.00000 | 0.00000 → 0.10000 | -1.707 | +2.088 | -1.151 | -2.134 | +1.992 |
| `mu` | scenario | 0.04000 | 0.00100 → 0.10090 | +12.493 | -0.746 | -7.897 | -11.727 | -1.161 |
| `theta_H` | scenario | 0.50000 | 0.45005 → 0.54995 | +0.167 | -0.010 | -0.101 | -0.137 | -0.008 |
| `eps` | structural | 3.00000 | 2.52500 → 3.47500 | +2.688 | +0.964 | +0.194 | +0.358 | +4.796 |
| `xi` | structural | 0.50000 | 0.45000 → 0.55000 | -0.711 | +0.042 | +0.821 | +1.508 | +0.622 |

## Methodological limitations

1. Comparing **equal fractions of implemented parameter bounds**
   does **not** compare equally plausible economic changes. The
   bounds themselves are modeling choices.
2. The three scenario presets also differ in other parameter
   assumptions. Cross-scenario changes in sensitivity magnitude
   are not isolated causal attributions.
3. One-factor-at-a-time analysis does not identify **interactions**:
   two inputs changed simultaneously may behave differently.
4. Large effects near a hard bound, notably `mu` in the
   extreme scenario, may reflect asymmetry/nonlinearity and cannot
   be extrapolated to effects of actual job-mobility policies.
5. The 2030 U.S. conditional macroeconomic scenarios are not
   economic forecasts, policy impact estimates, significance
   tests, calibrated uncertainty bands, or results for Portugal.
6. The Anthropic Economic Index MCP measures observed Claude
   task use and is not an input to or validation of these
   macroeconomic sensitivity calculations.
7. All reported results were sampled with the same pinned
   independent mathematical code version, not with official
   Anthropic-provided proprietary simulation code.

**Next hypothesis, not yet authorized to execute:** Verify
whether the ranking is robust to *different numerical window
widths*, and only then assess selected two-way interactions.
Do not schedule or run either automatically.
