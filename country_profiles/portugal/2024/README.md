# Portugal calibration feasibility audit — base year 2024

**Date:** 2026-10-17 · **Country:** Portugal (`PT`) · **State: AUDIT ONLY — NOT A CALIBRATED OR RUNNABLE COUNTRY MODEL**

This is a country-transfer feasibility study of the independent reproduction
of *Economic Scenarios for Transformative AI*. **It does not forecast Portugal's
employment, GDP, wages or AI adoption.** It does not replace or alter U.S.
model calculations, create a Portugal `Fixed()` or `Scenario()` object,
publish a Portuguese 2030 scenario, deploy Docker, or authorize Mac execution.

The precise baseline is:
[original `aiscen/params.py` at v1.0 / `d4703b6`](https://github.com/fhoces/opa-ai-macro-econ-scenarios/blob/d4703b6ae0d19dca08fbde11a25c218fa4c7b7a6/aiscen/params.py).
The [machine-readable field audit](calibration_audit.json) enumerates **all 37
default-bearing primitive parameters** from that source (26 `Fixed` + 11
`Scenario`), including computational conventions. The additional required `Scenario.name`
is only a string identifier and is excluded from the numeric/Boolean
parameter count. Derived Python
properties such as `s_C0` and `l_C0` are **not** additional free inputs.

## Initial decision

**Conditionally feasible for a *prototype*, not yet feasible to claim a
nationally calibrated forecast.**

- The governing equations can initially remain as implemented and
  an alternative country-specific parameter object could ultimately be
  supplied **after** source/definition checks.
- The C/N occupation partition, monthly hiring/separation dynamics,
  capital supply and baseline wage/income accounting are critical.
  Substituting only the national unemployment rate will not replicate
  Portugal's institutions or macroeconomic structure.
- Portugal is a relatively small open economy integrated with EU/EA
  labor and capital markets. Whether the model's capital-supply
  and labor-force closures are structurally appropriate requires
  a separate scientific review, not merely a change of constants.

## What the model needs and what we can actually obtain

| Model concept | Source for Portugal | Readiness and obstacle |
|---|---|---|
| Baseline jobless share `U_bar` | INE annual 2024 labor force statistics | **Candidate:** 6.4% unemployment, but must reconcile model's baseline search-pool concept, age universe and 2024 definition |
| Employment in AI-sensitive `C` group `cog_share` | Eurostat EU-LFS ISCO-08 by occupation (`lfsa_egais`) | **Blocked on crosswalk:** ISCO group shares are not directly the model's C/N split; exposure to generative AI also is a different measure |
| Labor income share `s_L0` | European Commission AMECO `ameco_chapter07-06` adjusted wage share | **Source identified, value not yet adopted:** validate treatment of self-employment, product taxes, denominator and capital share before assigning |
| Labor-force trend `n` | INE / Eurostat multi-year LFS | **Estimate required:** labor-force growth rather than one-year growth of *employment* |
| R&D share and trend `iota_R0`, `g_iota` | National R&D accounts, INE/Eurostat, AMECO as available | **Definition check:** GERD in GDP is not automatically identical to the model's innovation-input concept |
| Job quits and group separations `q_bar_ann`, `q_resp_share`, `q_rel_C`, `q_rel_N` | Restricted longitudinal EU-LFS / national administrative microdata | **Serious blocker:** E↔U↔I status transitions alone do not measure quits to another employer or C↔N specific separations |
| Normal mobility `mu_bar` and scenario mobility `mu` | Occupation-resolved longitudinal worker transitions | **Serious blocker:** `mu` is a cross-group search-efficiency discount, not directly the observed percentage changing jobs |
| Vacancy fill `fill_bar`, posting speed `theta_H` | Eurostat JVS + hires / vacancy-duration records | **Serious blocker:** a vacancy **stock/rate** is not monthly vacancies filled |
| Capital depreciation/returns `delta`, `r_bar` | AMECO national accounts and capital stocks | **Requires mapping:** capital income / net capital stock / investment conventions |
| Capital supply elasticity `eps` | Cross-border investment / capital-market research | **Structural review:** closed-economy closure may be a poor fit for Portugal in euro area |
| Job matching curvature and wage rigidity `iota_match`, `xi` | Research literature / longitudinal microdata | **Requires estimation or declared cross-country transfer**, not a national data series |
| Other structural assumptions (`sigma`, ideas parameters) | Research literature; sensitivity analysis | **Explicit hypotheses** until validated for Portugal |
| Future AI paths (`m,d,a,psi,rho,mu,theta_H`) | Scenario assumptions / task-level evidence | **Do not relabel** observed AI enterprise use as task diffusion or automation |

### Observations gathered, **not** assigned to the model

- **2024 INE annual employment:** 5,112,300 employed, 351,100
  unemployed, annual average unemployment rate **6.4%**.
  [INE via Portugal's economic statistics portal](https://estatistica.dgeconomia.gov.pt/estatisticas-do-emprego-ine-14/).
- **2025 follow-up:** annual average unemployment **6.0%**;
  a *different year*, not a 2024 base-year substitute.
  [INE 2025 via DGE](https://estatistica.dgeconomia.gov.pt/estatisticas-do-emprego-ine-18/).
- **2024 gross R&D expenditure:** approximately **1.72% of GDP**
  (provisional), [Eurostat/INE via PORDATA](https://www.pordata.pt/en/europe/expenditure%2Bin%2Bresearch%2Band%2Bdevelopment%2Bactivities%2B%28r%2Bd%29%2Bas%2Ba%2Bpercentage%2Bof%2Bgdp%2Bby%2Bsector%2Bof%2Bperformance-1674).
  This is contextual evidence, **not an adopted value** of `iota_R0`:
  the model's research-input concept needs separate verification.
- **2025 enterprise AI adoption:** **11.5%** of enterprises in the
  surveyed universe reported AI use.
  [Statistics Portugal / INE releases](https://ine.pt/xportal/xmain?DESTAQUESpagenumber=1&DESTAQUEStema=5414257&DESTAQUEStipo=ea&selTab=tab0&xlang=en&xpgid=ine_destaques&xpid=INE).
  This is *neither* `m_anchor` nor `d_anchor`: enterprise adoption
  is not task-level AI reach or diffusion.

Everything in the machine-readable audit has `portugal_model_value: null`.
The observations above are **contextual evidence** or **candidates**,
not promoted to model parameters.

## Field coverage and calibration status

| Bucket | Input count | Meaning |
|---|---:|---|
| Direct national statistic candidate (not adopted) | 5 | Requires a definitional conversion or source value |
| National occupational mapping required | 1 | `cog_share` must be derived from a reviewed C/N crosswalk |
| Specialized estimation required | 10 | Labor flows, jobs, wage dynamics, innovation and returns |
| Structural model review required | 5 | An assumption may not transport across countries |
| Common calendar / numerical conventions | 5 | Preserve as conventions in comparable exercises |
| Unobserved scenarios or technology-path assumptions | 11 | Future scenarios, not historical observations |
| **Total** | **37** | 26 fixed + 11 scenario fields |

See every field and reason in [`calibration_audit.json`](calibration_audit.json).

## Sources discovered

- [INE 2024 employment/unemployment](https://estatistica.dgeconomia.gov.pt/estatisticas-do-emprego-ine-14/) (annual).
- [INE 2025 employment/unemployment](https://estatistica.dgeconomia.gov.pt/estatisticas-do-emprego-ine-18/) (context).
- [Eurostat `lfsa_egais` employed persons by ISCO occupation](https://ec.europa.eu/eurostat/databrowser/product/view/lfsa_egais); available through 2025.
- [Eurostat EU-LFS longitudinal transitions metadata](https://ec.europa.eu/eurostat/cache/metadata/EN/lfsi_long_esms.htm):
  quarterly **employment, unemployment and inactivity** flows, not
  necessarily the occupation-to-occupation transition matrix needed here.
  Portugal has a dedicated INE methodology in these metadata.
- [Eurostat EU-LFS scientific microdata](https://ec.europa.eu/eurostat/web/microdata/european-union-labour-force-survey):
  restricted access and linkage/anonymization limitations.
- [Eurostat job vacancy data](https://ec.europa.eu/eurostat/databrowser/product/view/jvs_q_r21)
  (vacancy stock/rate, not monthly filling).
- [AMECO adjusted wage share `ameco_chapter07-06`](https://webgate.ec.europa.eu/ecfin/redisstat/databrowser/explore/all/AMECO?display=card&lang=en&sort=category),
  [AMECO capital and income tables](https://economy-finance.ec.europa.eu/economic-research-and-databases/economic-databases/ameco-database/download-annual-data-set-macro-economic-database-ameco_en).

All of these are **source candidates**; their published series have different
year, population, accounting, sampling and coverage conventions.
No automated table-to-model ingestion exists yet.

## Controlled next steps

1. Reproduce a 2024 labor-force baseline from INE and map the
   associated unemployment/population denominator (2025 data only as
   an external plausibility check).
2. Download the 2024 AMECO adjusted wage-share **numeric series**,
   documenting self-employment and income-accounting definitions.
3. Define and review an ISCO occupation-to-C/N concordance,
   including sensitivity bands and the impact of ISCO aggregation.
4. Determine which monthly separation, hiring, job mobility and
   vacancy-filling inputs can be estimated from national sources;
   list those still unidentifiable with public series.
5. Scientifically review the capital-supply closure and cross-border
   labor dynamics for a small open euro-area economy.
6. Build a **distinct experimental Portugal calibration profile**
   with explicit provenance and uncertainty only when the crucial
   targets are resolved. Require validation of original U.S.
   results and Portuguese baseline accounting before enabling
   even illustrative 2030 scenario calculations.
7. Do not publish "Portugal GDP +X%" / "jobs lost" as a
   forecast or directly copy US scenario dials as PT estimates.

**Go/no-go condition:** The audit is **NOT READY** for numerical
Portugal model execution. The first deliverable is a traceable source
and calibration map, not a country forecast.

## Execution and safety boundary

No changes to `lab.api`, `aiscen`, `mac-access`, VPS, Cloudflare,
OAuth, GitHub-hosted owner experiment routes, model tokens or local
Docker. All U.S. tests and previously verified U.S. scenario runs
must remain unchanged. Future PT execution will require a separately
reviewed model-selection API and an explicit country-profile
readiness gate; unspecified model parameters must **fail closed**
instead of silently inheriting American calibration.
