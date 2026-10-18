# First self-selected model discovery: 2030 unemployment remembers AI diffusion history

**Research date:** 18 October 2026. **Scope:** independent reproducible implementation of Anthropic Institute's *Economic Scenarios for Transformative AI*; conditional **U.S. numerical experiment only**, **not** an empirical test or forecast.

## Why this question arose

Inspection of the original pinned monthly equations (reproduction at `d4703b6ae0d19dca08fbde11a25c218fa4c7b7a6`) suggested an omitted dimension of earlier Economic Lab parameter sweeps: previous research varied 2030 technology or labor-market coefficients, but workers, vacancies, quits and hires are stocks and flows updated **monthly**. Hence 2030 labor-market outcomes need not be determined by AI technology **in 2030 alone**. This question was selected from the mathematical implementation, not from an observed target result.

**Question:** if two simulated economies reach identical 2030 AI task reach, adoption, per-task productivity and `psi/rho/mu/theta_H`, do different **paths** for AI adoption change their 2030 unemployment and production?

An independently reviewed Math/AI outcome is **conditional model sensitivity**, not evidence that frontloading real-world AI adoption is a beneficial policy.

## Source integrity and hypotheses

- Snapshot of Economic Lab: `e020a4573bd8ad4ede933d05435b92869ca0ee2d` (owner-source artifact Issue #31).
- Independently reimplemented mathematical code: `fhoces/opa-ai-macro-econ-scenarios`, tag `v1.0`, SHA `d4703b6ae0d19dca08fbde11a25c218fa4c7b7a6`. **Not official Anthropic source.**
- [Primary research protocol](data/2026-10-18-adoption-timing-plan.json) committed before the numerical evaluation, commit `facfe73892267a308c2cc499a95ae8127ce8b089`; additionally frozen local full-protocol SHA-256: `e9c8a5bc5c085356537aedd8159dfb7ba3d5498e166a4600539b7b4111a67cd2`.
- Original `SUBSTANTIAL` preset, `Fixed()`, 2030 `m=0.30,d=0.40,a=0.448,psi=0.75,rho=0.25,mu=0.08,theta_H=0.25`, unchanged.
- **H1:** earlier reach/diffusion reduces unemployment among AI-sensitive workers in 2030, conditional on fixed 2030 technology (substantive criterion >0.05 percentage points).
- **H2:** earlier diffusion increases the additional AI-related GDP increment in 2030 (>0.05 pp).

The original model defines `m,d` using logistic time paths, with published mid-2026 anchor `m_anchor=0.14,d_anchor=0.10` and 2030 endpoints `m_2030=0.30,d_2030=0.40`. Preplanned grid is `m_anchor=[0.07,0.14,0.21]` × `d_anchor=[0.05,0.10,0.20]`: exactly **9** model runs. All eight alternative paths have exactly identical technology and labor market coefficients at 2030, but the changed mid-2026 anchors also alter the implied **2024–2026 history**. This is an unavoidable confound in that initial test and motivated falsification controls.

## Preplanned initial grid: a genuine model-internal timing effect

| 2030 | Later anchors (0.07,0.05) | Published anchors (0.14,0.10) | Earlier anchors (0.21,0.20) |
|---|---:|---:|---:|
| GDP gain vs no-AI, **%** | **7.776** | 8.283 | **8.896** |
| All-worker unemployment, **%** | **4.956** | 4.529 | **4.070** |
| AI-sensitive unemployment, **%** | **5.236** | 4.498 | **3.680** |
| Labor share, **% of income** | 56.126 | 56.096 | 56.061 |
| Average wage vs no-AI, **%** | 2.230 | 2.137 | 2.106 |

The preplanned H1 and H2 directional conditions both hold. The early-minus-late differences at fixed 2030 AI: **−1.556 pp cognitive unemployment**, **−0.886 pp overall unemployment**, **+1.120 pp additional GDP**. Meanwhile labor income share and mean wage are *slightly lower* in the earlier case. Thus the model does not say every worker benefits.

**Critical validity caveat:** the prior logistic time paths are not identical at 2024 for these scenarios. The experiment alone cannot separate better adjustment timing from an altered pre-model history.

## Falsification control 1: identical history until mid-2026

After seeing the above result, a control was explicitly designed and stored as **post hoc**; it is not an independent blind preregistered hypothesis. The intervention now changes only the *calendar shape* of `m,d` **between 2026.5 and 2030**, not the original `Fixed()`, `SUBSTANTIAL`, the 2024–2026.5 technology history, or **any monthly employment/capital/ideas equation**.

Define `s=(t-2026.5)/(2030-2026.5)` for the interior interval; evaluate original logistic `m,d` at the reparameterized time `2026.5+3.5*(s+alpha*s*(1-s))`. Three values: `alpha=-0.75,0,+0.75`. Exactly **3** new simulations. `alpha=0` is the published substantial scenario.

Front minus late:
- Cognitive unemployment **−1.679 pp** (2030 levels **3.572 vs 5.251%**).
- Overall unemployment **−0.979 pp** (**3.989 vs 4.969%**).
- Additional GDP gain **+1.097 pp** (**8.889 vs 7.792%**).

The effect survived matching the entire model's **early history**. But this first warp also changes the **instantaneous speed of adoption at the 2030 endpoint**: differences could be caused partly by the endpoint adoption rate, not solely by internal labor-market history.

## Falsification control 2: identical initial history AND endpoint adoption speed

A more rigorous, also explicitly **post-hoc**, falsification design matches:
- the **complete original history through 2026.5** (including initial states),
- exact levels of `m,d,a` at 2026.5 and 2030,
- the **derivatives of `m,d` at both endpoints**.

Use the smooth clock warp `tau(s)=s + alpha*s^2*(1-s)^2`, for `alpha=-2.5,0,+2.5`, applied only for `2026.5 < t < 2030`. It remains increasing; both endpoint derivatives are `d tau/ds = 1`. The original equations are not edited; only the exogenous AI trajectory between fixed endpoints is changed. This is an alternative scientific time-profile scenario, **not** one of the paper's official logistic paths.

| 2030 | Later profile | Original substantial | Earlier profile |
|---|---:|---:|---:|
| Additional GDP vs no-AI, **%** | **7.965** | 8.283 | **8.651** |
| Total unemployment, **%** | **4.814** | 4.529 | **4.203** |
| AI-sensitive unemployment, **%** | **4.989** | 4.498 | **3.933** |
| Labor share, **% of income** | 56.115 | 56.096 | 56.075 |
| Mean wage vs no-AI, **%** | 2.156 | 2.137 | 2.118 |
| Ideas stock uplift vs no-AI, **%** | 0.1680 | 0.1980 | 0.2347 |

**Result:** even at equal final adoption levels **and equal final adoption velocities**, frontloading the *intervening history* is associated with **−1.056 pp AI-sensitive unemployment**, **−0.611 pp total unemployment**, **+0.686 pp additional GDP**, and slightly lower labor share and wage gain.

### What economic state carries the history?

Crucially, at 2030 the model's **frictionless desired employment in the AI-sensitive sector** is the same in both paths (`l_C*=0.57158`, labor-force-normalized), because it depends on the identical 2030 technology and fixed coefficients. Yet the realized **employment and unemployment stocks differ**:

| Labor-force-normalized AI-sensitive state at 2030 | Later profile | Earlier profile |
|---|---:|---:|
| Realized employed `l_C` | 0.57262 | 0.57654 |
| Searching/unemployed `U_C` | 0.03006 | 0.02360 |
| AI-sensitive unemployment rate | 4.989% | 3.933% |

The matching block in `aiscen/simulate.py` updates monthly vacancies, hires, separations, effective cross-sector search and unemployment stocks. Those state variables retain past shocks, even when instantaneous 2030 technology **and technology growth speed** are equal.

Time-path snapshots show a striking reversal:

| Year | Early-profile AI-sensitive unemployment | Late-profile |
|---|---:|---:|
| mid-2026 | 3.022% | 3.022% |
| 2028 | **3.755%** | 3.072% |
| 2029 | **3.821%** | 3.717% |
| 2030 | **3.933%** | **4.989%** |

Earlier adoption is **initially more disruptive**, but delayed adoption postpones the labor-market disruption. This is a *timing/displacement adjustment tradeoff*, not proof that AI-related unemployment eventually disappears: even earlier-profile unemployment is above the no-AI labor-market baseline for these worker categories.

The model's endogenous **ideas stock** also remembers the full GDP history, adding a separate route for later GDP to differ. The experiments do not isolate causal contributions of ideas feedback, matching friction and structural production to the GDP difference; such decomposition would require another explicitly reviewed design.

## Scientific boundary

**What was learned:** a falsifiable within-model hypothesis emerged by inspecting the equations, survived the original preplanned 3×3 experiment and two progressively stricter post-hoc controls. Same terminal AI technology (and in control 2, same terminal growth rates) does **not** imply same employment states or final GDP.

**What was NOT learned:** whether faster *real-world* AI adoption is a good policy, actual probability of any technology trajectory, future U.S./Portuguese jobless rates, causal labor-market employment impacts, or estimated AI task reinstatement `rho`. All wage/worker protection outcomes remain **model assumptions and calculations**, not observations.

The two controls were intentionally selected after results were seen, so they are transparent *mechanistic robustness probes* rather than independently preregistered confirmations.

No new agent process, MCP, server, Docker deployment, GitHub Actions workflow, LLM provider, data ingestion or permanent runner was created.

## How to reproduce

Use the same pinned independent upstream math implementation with `PYTHONPATH` set to the local `aiscen` source. Then from the repository root:

```bash
python -m ops.research_adoption_timing > adoption-timing-receipt.json
python -m unittest discover -s tests -v
```

The reproduction code [`ops/research_adoption_timing.py`](../ops/research_adoption_timing.py) takes all inputs from the [pre-execution plan](data/2026-10-18-adoption-timing-plan.json) and the [explicit post-hoc controls](data/2026-10-18-adoption-timing-controls.json), verifies terminal levels and initial labor stocks, and outputs full precision outcomes/path snapshots. Three sets of **9 + 3 + 3 = 15** evaluations are bounded and have no production side effects.

The project already includes an offline source-packaging procedure; input model equations remain pinned. A GitHub PR CI check is separate validation of source consistency, not empirical validation of the economic mechanisms.
