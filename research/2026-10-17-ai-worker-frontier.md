# Economic Lab: can 2030 AI growth coexist with workers' protection?

**Date:** 2026-10-17. **Geography:** United States only. **Status:** completed
*conditional numerical model exploration*, **not a forecast or policy impact study**.

## Question and success criteria

Within one pinned implementation of *Economic Scenarios for Transformative AI*,
can the modeled U.S. economy in 2030 meet these three simultaneous conditions,
relative to the **no-AI counterfactual** rather than the original `substantial`
preset? **(1)** GDP at least 5% above no AI; **(2)** overall unemployment no
higher than the no-AI steady-state **3.8%**; **(3)** labor share at least the
no-AI **60%**. A separate, stricter diagnostic asks whether unemployment among
AI-sensitive (`C`) workers also remains no higher than its no-AI model rate
**2.818167%**. The 5% target is a research convention, not an estimated threshold.

This model reports GDP **percent above no AI**; this is not the annual GDP
growth rate. Labor share and unemployment are percentage *levels*, not percent
differences. The criterion does not ensure that all occupations or households
are better off, even when `C` unemployment also meets its threshold.

## Sources, execution and planned first scan

- Independent MIT-licensed model: `fhoces/opa-ai-macro-econ-scenarios`, tag `v1.0`,
  commit `d4703b6ae0d19dca08fbde11a25c218fa4c7b7a6`. This is not original
  Anthropic source and should not be described as an Anthropic prediction.
- Economic Lab source snapshot restored from owner-requested GitHub artifact
  [Issue #31](https://github.com/Dmitry-dev-pet/truthrail-economic-lab/issues/31),
  commit `e020a4573bd8ad4ede933d05435b92869ca0ee2d`. Both source archive
  checksums passed before any calculations; the standard 53 source tests passed.
- Primary scan plan, saved **before running its grid**:
  [`2026-10-17-ai-worker-frontier-plan.json`](data/2026-10-17-ai-worker-frontier-plan.json).
  SHA-256 of exact plan bytes:
  `4a0b9c38bca154f75cfdcfdd4c1fa834c983f83ef554ef56c7e689cd98a79302`.
- Original `substantial` technology path held fixed:
  `m_2030=0.30`, `d_2030=0.40`, `a_2030=0.448` (approximately).
  Original structural `Fixed()` inputs retained. Scan only `psi` (automation
  share) = `{0.25,0.50,0.75,0.90}`, `rho` (new human tasks per automated task)
  = `{0,0.25,0.50,0.75,1}`, `mu` (cross-group job-search efficiency)
  = `{0.04,0.08,0.17,0.34}`, and `theta_H` (job posting response)
  = `{0.10,0.25,0.50}`: exactly **240 cells**.
- **64** pre-seeded continuous off-grid samples over the stated parameter box
  were checked for numerical discretization only (seed `20261017`). These are
  *not* independent validation data or a probability sample of future worlds.

## Stage 1: fixed-productivity search did not find a solution

**Zero of 240** predeclared grid cells met all three conditions; **zero of 64**
off-grid numerical checks did either. This is not proof of impossibility.
Among grid cells that **did** retain both labor-share and overall-unemployment
thresholds, the largest modeled GDP gain was **4.180164%**:

| `psi` | `rho` | `mu` | `theta_H` | GDP vs no AI | Labor share | All unemployment | C unemployment |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.25 | 1.00 | 0.34 | 0.50 | +4.180164% | 60.180296% | 3.756159% | 2.826975% |

This finding concerns the fixed 2030 gain `a_2030≈0.448` and **these** 240
combinations, not every mathematically or economically possible scenario.

## Stage 2: explicitly post-hoc expansion of the productivity path

After seeing the null result and probing a few illustrative cases, the
investigation **adaptively changed** one more assumption: 2030 per-task *log*
productivity gain `a_2030` from the preset's ≈0.448 to **0.55**, **0.65** or
**0.80**, repeating the same 240 combinations at each value. This makes **720
extra model evaluations**. They are **exploratory**, not preregistered, and
must not be presented as independent confirmation of a previously specified
hypothesis. `m_2030`, `d_2030` and the rest of `Fixed()` remained unchanged.

| Added 2030 `a` | Cells | Meet three criteria | Also protect `C` unemployment |
|---:|---:|---:|---:|
| 0.55 | 240 | 1 | 0 |
| 0.65 | 240 | 2 | 0 |
| 0.80 | 240 | 7 | 1 |
| **Total** | **720** | **10** | **1** |

**Illustrative four-criterion solution (one of tested cells):**

| Assumed `psi`, `rho`, `mu`, `theta_H`, `a_2030` | GDP above no AI | Labor share | All unemployment | C unemployment | Average wage above no AI |
|---|---:|---:|---:|---:|---:|
| `0.75, 1.00, 0.34, 0.50, 0.80` | **5.165800%** | **61.753835%** | **3.748529%** | **2.797059%** | **8.210343%** |

An alternative gives higher GDP **7.173721%** at
`psi=0.75,rho=0.75,mu=0.34,theta_H=0.50,a_2030=0.80`, retaining
labor share **60.098391%** and overall unemployment **3.779991%**;
but `C` unemployment is **2.895206%**, *above* its no-AI 2.818167%.
Thus the three headline tests can mask worse outcomes for a subgroup.

The extra `a_2030=0.80` is **not** the original `extreme` preset: only
per-task gain is raised; task reach and diffusion stay `substantial`.
The favorable example also assumes exceptionally strong new-task reinstatement
(`rho=1`), more efficient cross-occupation matching (`mu=0.34` versus original
`substantial` `0.08`), and higher posting response (`theta_H=0.50` versus
original `0.25`). Those are chosen inputs, **not observed outcomes or
estimates of realistic policy effects**.

## Reproduce and scrutinize

With the pinned `aiscen` package importable and the repository checked out:

```bash
PYTHONPATH="$PWD:$PWD/../upstream" python ops/feasibility_scan.py
PYTHONPATH="$PWD:$PWD/../upstream" python ops/feasibility_scan.py --all > full-receipt.json
python -m unittest discover -s tests -q
```

For the restored owner snapshot, adjust `PYTHONPATH` to point to the actual
restored `upstream` directory. The script never fetches URLs, runs code from
Issue bodies, changes any model equation, or invokes Mac/Docker/VPS/MCP.
The `--all` output preserves **every** evaluated assumption and all five
2030 outcomes, not just successful cells. The exact full JSON receipt
produced in the recorded temporary environment has SHA-256:
`f0df744fe3800fc38e1764d490467cf06b982177b25ad3ccf8feed4b7260e165`.
The code and plan are versioned here; the full receipt can be regenerated.

The restored source plus three new lightweight regression tests passed
**56/56**. This is a reproducible **model-internal** calculation, not an
empirical out-of-sample validation. The feasibility counts depend on chosen
thresholds, sampling grid, original US structural coefficients and fixed
technology assumptions; there is no claim of exhaustive global optimization
or statistically likely futures. No Portugal 2030 simulation was made.

## Next research question

The first adaptive step found a *conditional possibility*, not a policy recipe.
To investigate whether it is robust, predeclare **new** held-out parameter
ranges or a new technology trajectory; assess whether the favorable region
has meaningful volume, including subgroup unemployment and workers' real
income. Inspect the underlying equations to explain why increased per-task
AI gains can restore GDP growth under high task reinstatement. Do not treat
re-searching this same grid as an independent test.
