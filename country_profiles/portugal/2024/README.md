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

## New: Portugal occupation headcounts with auditable classification scenarios

The [Eurostat 2024 ISCO-08 snapshot](isco_occupation_snapshot.json) is a
frozen, dimension-filtered download of the **official** Eurostat statistics
API `lfsa_egais`, `geo=PT`, `time=2024`, `sex=T`,
`age=Y_GE15`, `wstatus=EMP`, `unit=THS_PER`.
The archived response reflects Eurostat's **10 September 2026** update.
Counts are **thousands of employed persons**:

| ISCO major group | 2024 thousands | Preliminary mapping to US paper's SOC C/N partition |
|---|---:|---|
| OC1 — Managers | 309.8 | C candidate |
| OC2 — Professionals | 1,178.3 | C candidate |
| OC3 — Technicians and associate professionals | 590.8 | **Mixed/needs fine-grained crosswalk** |
| OC4 — Clerical support workers | 478.0 | C candidate |
| OC5 — Service **and** sales workers | 928.3 | **Mixed:** sales vs personal/protective services must be split |
| OC6 — Skilled agricultural / forestry / fishery | 115.8 | Primarily N candidate |
| OC7 — Craft and related trades | 656.2 | Primarily N candidate |
| OC8 — Plant / machine operators and assemblers | 403.8 | Primarily N candidate |
| OC9 — Elementary occupations | 429.1 | Predominantly N candidate; detailed sales exceptions may exist |
| OC0 — Armed forces | 22.3 | Treat separately from civilian CPS reference |
| **TOTAL** | **5,112.3** | Sum of rounded major groups may differ by 0.1 thousand |

**How the original paper defines C:** SOC 2010 major groups **11–29,
41 and 43**, covering management, professional, sales and office work
(see [reproduction's labor-market discussion](https://econ-ark.github.io/econ-scenarios/reproduction-appendix/)
and [BLS SOC–ISCO crosswalk](https://www.bls.gov/soc/ISCO_SOC_Crosswalk_process.pdf)).
ISCO is not a direct one-to-one substitute for U.S. SOC.

The three **heuristic classification sensitivity examples**, using
Eurostat's entire all-employed denominator and, separately, an
approximate *civilian-only* denominator that excludes the 22.3 thousand
armed-forces workers, are:

| Inclusions | Thousand people | Share of Eurostat total | Share of provisional civilian employment |
|---|---:|---:|---:|
| ISCO 1 + 2 + 4 | 1,966.1 | 38.46% | 38.63% |
| ISCO 1 + 2 + 3 + 4 | 2,556.9 | 50.01% | 50.23% |
| ISCO 1 + 2 + 3 + 4 + 5 | 3,485.2 | 68.17% | 68.47% |

The provisional civilian denominator is **5,090.0 thousand**,
`5,112.3 - 22.3`. Excluding armed forces improves comparison
to the CPS's civilian frame but is *not* a complete harmonization
of age, employment or institutional definitions.

**These are intentionally coarse mapping examples, not a
calibrated value for `cog_share`, and not a formal statistical
lower/upper confidence interval.** ISCO 3 and 5 contain mixed
groups; ISCO 5 includes personal services that the paper excludes
while sales professions within ISCO 5 are included. A defensible
mapping requires detailed ISCO codes and weighted U.S. SOC
2010 ↔ ISCO-08 correspondence, with special handling for
one-to-many mappings. The public `lfsa_egais` endpoint exposes
only 1-digit groups. The more detailed scientific EU-LFS files
include **3-digit ISCO**, but require research authorization.

All three group fractions are stored as experimental alternatives
in [`isco_occupation_snapshot.json`](isco_occupation_snapshot.json);
**none** is assigned to the Portugal `Fixed.cog_share` parameter.

## New: observed labor-market status flows are not occupational mobility

The [Eurostat 2024 annual flows snapshot](lfs_annual_status_flows.json),
extracted from `lfsi_long_a`, `geo=PT`, `time=2024`,
`sex=T` (updated 5 August 2026), contains the complete
**9-flow transition matrix** between employed (E),
unemployed (U) and inactive (I). Published transitions include:

| Initial status → final status | Persons, thousands | Percent of initial-status group |
|---|---:|---:|
| E → E | 4,739 | 94.5% |
| E → U | 120 | 2.4% |
| E → I | 157 | 3.1% |
| U → E | 148 | 42.2% |
| U → U | 123 | 35.0% |
| U → I | 80 | 22.8% |
| I → E | 196 | 7.4% |
| I → U | 108 | 4.1% |
| I → I | 2,356 | 88.6% |

The rates and population counts represent annual linked
EU-LFS estimates; they are **not automatically monthly rates**.
Among people classified E→E are both persons who kept the
same occupation and those who moved between professions.
As a result, **the C→N and N→C occupational transition
probabilities cannot be recovered from this 9-cell matrix**.
They are also conceptually different from `mu_bar`, which
represents a search-efficiency discount, not a raw fraction
of people who change occupation.

Eurostat's [scientific EU-LFS microdata](https://ec.europa.eu/eurostat/web/microdata/european-union-labour-force-survey)
preserves 3-digit ISCO values but **re-generates household identifiers
by quarter**, preventing ordinary linkage of individual respondents
across waves. Nationally linked INE microdata or other longitudinal
administrative data and permission to access them would be needed
to recover occupational transitions or group-level hire/quit rates.
The official [Eurostat flow methodology](https://ec.europa.eu/eurostat/cache/metadata/en/lfsi_long_esms.htm)
notes specific Portuguese INE flow estimates.

**The Portugal country profile remains audit-only**; the snapshot
does not set `mu_bar`, `mu`, `q_rel_C`, `q_rel_N`,
`q_bar_ann` or `fill_bar`. The existing
U.S. mathematical replication is unchanged.

## Finer SOC↔ISCO mapping discovered — classification only

The original American model's group C uses **SOC-2010 major groups
11–29, 41, 43**. The [U.S. BLS publishes an official
ISCO-08 ↔ SOC-2010 crosswalk](https://www.bls.gov/soc/soccrosswalks.htm)
as a legacy `XLS` workbook
([file URL](https://www.bls.gov/soc/ISCO_SOC_Crosswalk.xls)).
That official link is verified, but its binary contents **have not been
independently parsed in this audit**.

An [independent public CSV representation](https://github.com/danielruss/codingsystems/blob/main/isco2008_soc2010.csv)
has been processed solely as a **provisional map of occupation codes**.
The frozen mapping summary is [`soc2010_isco08_crosswalk_audit.json`](soc2010_isco08_crosswalk_audit.json).
Its provenance includes the exact GitHub blob SHA, 1,125
unweighted crosswalk relations across 43 ISCO-08 two-digit
sub-major groups, and **two problematic source rows using three-digit
rather than four-digit ISCO codes** (`211` and `315`).

The derived code-level classification is:

| Sub-major ISCO group category in the mirror | Number of 2-digit groups |
|---|---:|
| Every linked SOC major belongs to paper group C | 13 |
| Every linked SOC major belongs to group N | 13 |
| Mixed or ambiguous C/N links | 17 |
| **Total** | **43** |

**The 13 / 13 / 17 figures count occupational CODE groups, not people.**
They do not provide Portugal's `cog_share`: some 4-digit occupations
have SOC matches in both C and N, and these many-to-many relationships
carry no employment weights.

Examples from the mirror: ISCO **35** (ICT technicians) links to C;
ISCO **31** (engineering and related associate professionals)
links to C and N; ISCO **52** (sales workers) has mainly C mappings
but exceptions, so it cannot automatically all be placed in C;
ISCO **53** (personal care) is mainly N but contains exceptions.
These are conditional statements about *this unverified code list*,
not authoritative conversion probabilities.

### Official all-employed employment counts at two-digit ISCO resolution

**This was the key missing dataset.** Eurostat
[`lfsa_egai2d`](https://dgs-p.eige.europa.eu/data/view?code=ta_wrklab_lab_employ_gen__lfsa_egai2d)
publishes [official two-digit ISCO employment data for Portugal 2024](https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/lfsa_egai2d?geo=PT&time=2024&unit=THS_PER&sex=T&age=Y_GE15),
`geo=PT`, `time=2024`, `age=Y_GE15`, `sex=T`,
`unit=THS_PER`; the source was updated **10 September 2026**.

The data are archived with exact source dimensions and reliability
flags in [`isco_two_digit_employment_2024.json`](isco_two_digit_employment_2024.json).
All **43 ISCO-08 two-digit sub-major groups** are present in the response,
with one sub-major value (`OC63`) **missing** and **not imputed**.
The 2024 total is **5,112.3 thousand employed people**, reconciling with
the independently retrieved 1-digit Eurostat and INE series.
Independent major/minor subtotals differ by at most **0.1 thousand**
as expected for rounded survey figures. Eurostat marks several
small cells as `u` (low reliability), notably some armed-forces
units and `OC95`.

This dataset **does** cover the same all-employed statistical
universe as the one-digit Eurostat totals. Therefore the missing
two-digit population weighting is now resolved without needing to
substitute employer-only statistics from `Quadros de Pessoal`.

Examples of Portuguese **2024 employment counts**, not model
group classifications:

| ISCO two-digit code | Workers, thousands | Provisional 2010-SOC mapping issue |
|---|---:|---|
| 31 Science and engineering associate professionals | 125.0 | Mixed C/N links |
| 33 Business and administration associate professionals | 279.6 | Mixed C/N links |
| 35 ICT technicians | 51.0 | C-only links in provisional mapping |
| 52 Sales workers | 374.3 | Mixed C/N links |
| 53 Personal care workers | 235.7 | Mixed C/N links |

### Weighted classification ambiguity — still not a national calibration

The [new occupation-weighted review](soc_isco_employment_weighted_review_2024.json)
combines **official Eurostat worker counts** with a
**third-party, unverified CSV representation** of the BLS
SOC↔ISCO mapping. It does *not* validate that CSV against the
[official BLS XLS file](https://www.bls.gov/soc/ISCO_SOC_Crosswalk.xls)
and does not produce a Portuguese model `Fixed.cog_share`.

| Conditional grouping of 2-digit codes under the unverified mirror | Workers, thousands | % of provisional civilian employment |
|---|---:|---:|
| Codes whose links all go to C | 1,892.8 | 37.19% |
| Codes with both C and N links (ambiguous) | 2,363.6 | 46.44% |
| Codes whose links all go to N, excluding military | 833.4 | 16.37% |

The provisional civilian denominator is **5,090.0 thousand**
(the all-employed total minus 22.3 thousand military workers).
The reported percentages have survey rounding residuals and a
suppressed `OC63` cell. Most importantly, almost **half of
employment lies in mixed 2-digit occupations**; even a complete
two-digit national table does not identify how workers are
distributed among C and N *within* those groups.

**These are conditional classification coverage categories, not
employment shares reliably assigned to C/N, not statistical
confidence bounds, and certainly not the share of jobs exposed
to automation.** A finer-grained 3-/4-digit employed-person
distribution and verified official crosswalk are still needed
to constrain the within-group allocations.

The December 2025
[DGCP/GEP `Quadros de Pessoal 2024` publication](https://www.dgcp.mtsss.gov.pt/sinteses-/-publicacoes?p_r_p_564233524_categoryId=11339&p_r_p_564233524_resetCur=true)
includes [2024 Excel tables](https://www.dgcp.mtsss.gov.pt/documents/10182/10928/qp2024pub.xlsx/02732373-1bae-4348-93af-74bb1bf7c8ec),
but its worker universe is **employer-reported employees**, not
all people employed (including self-employed and workers outside
covered establishments). The workbook contents and coverage
weights were not extracted/validated here; those counts must
not silently be combined with the all-employed LFS denominator.

Scientific EU-LFS microdata offer more detailed ISCO codes but
require research access and may not permit individual longitudinal
linkage. Those restrictions remain relevant for later steps,
especially estimating **inter-occupation worker mobility**.

**Readiness remains unchanged:** `cog_share=null`, all 37 Portuguese
model input values remain unset, and `runnable:false`.
No Portuguese scenario calculation was performed.

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
3. Use the verified 2024 national *two-digit* employed-person
   weights from `lfsa_egai2d` and independently verify the original
   BLS binary `ISCO_SOC_Crosswalk.xls` against the unverified
   CSV mirror. Then seek finer 3-/4-digit Portuguese employment
   counts for the numerous mixed 2-digit groups (about 46.44%
   of provisional civilian employment); resolve the 2 short
   mirror codes, missing OC63 and low-reliability flags.
   Never import employer-only QP weights without checking
   coverage and denominators.
4. Keep the official 2024 nine-status annual E/U/I flows as
   **context**. Identify permissioned, linkable 2024 INE/national
   datasets for occupational C↔N transitions and group-specific
   hiring, quitting and vacancy-filling rates. Scientific EU-LFS
   household pseudonyms cannot be used to link quarters.
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
