# Truthrail Economic Lab / AGENTS.md

## Purpose
A small reproducible **US economic research sandbox**. It is not a US employment forecast, not a Portugal model, and not an official Anthropic code release.

## Source of truth
- Repo: Dmitry-dev-pet/truthrail-economic-lab
- Upstream independent model: fhoces/opa-ai-macro-econ-scenarios, v1.0, commit d4703b6ae0d19dca08fbde11a25c218fa4c7b7a6
- Scientific paper: https://www.anthropic.com/institute/econ-scenarios
- Observed Anthropic Economic Index usage data is **separate**. Do not feed index country usage metrics into macroeconomic assumptions as if calibrated.
- Model parameters are assumptions; always attach source version and parameters to any reported scenario.

## Runtime boundaries
- Docker runs on the operator's Mac on demand, **not** an always-on VPS service.
- Compose binds only to 127.0.0.1:8765, with no authentication. Never expose it publicly or add a tunnel without a separate review.
- No LLM/GPU/OpenCode/AGY calls or scheduled token-using jobs are needed. The existing public-repository GitHub-hosted workflow may run pinned, no-secret numerical checks on PRs and main; it does not target the Mac, authorize project deployment or use model-provider credentials. Private Mac execution remains solely under reviewed mac-access admission.
- Use reviewed existing Truthrail routes; do not add a new MCP simply to call localhost.
- The public hosted `[econ] experiment` issue route accepts only owner-opened exact-title issues, bounded JSON numeric axes (maximum 25 cells), and never executes issue text as commands. Computation runs in a separate `contents:read` job; only the isolated `issues:write` report job can comment, using a bounded short-retention artifact. It never reaches the Mac or local API.
- Issue bodies and posted results on this public repository are public; do not include private/user data.
- Research requests are strictly `{"research":"auto"}` or an allowlisted `research` id with an optional named US scenario. `lab.research.prepare` ranks **predeclared** candidate hypotheses without executing simulations, records every predicted direction and a SHA-256 plan fingerprint, then `run_research` runs one nine-cell grid plus baseline. Never add a general natural-language-to-code, issue-body script, unbounded self-iteration, external LLM request or scheduled science agent.
- The `rho` parameter represents reinstatement of new labor tasks per automated task, distinct from occupational transition efficiency `mu`. State that model results are scenario sensitivities, not economic forecasts or independent empirical tests. A score is an internal research priority, not probability. Claims about "confirmation" must always be scoped "consistent within the tested model grid".
- Keep the existing `[econ] experiment` route fully backward-compatible with explicit two-axis grids; hypothesis studies use the same hosted Linux calculate/report isolation. New Mac actions need separate owner-reviewed immutable mac-access authority.

- Owner issues may also request the separately reviewed **one-factor-at-a-time sensitivity** study, with the **entire issue body restricted to** `{"analysis":"sensitivity","scenario":"modest|substantial|extreme"}` (use one exact scenario value). `lab.sensitivity.prepare_sensitivity` fixes nine named parameters, a 10%-of-bound-window endpoint pair per input, original preset baseline, SHA-256 plan fingerprint, and a hard limit of 19 mathematical model evaluations for one scenario. Do not permit caller-defined axes, ranges, code, secrets, runtime paths or loops in this mode; do not silently schedule the other scenarios.
- Rank numerical impacts **separately for each of the five observed metrics** by the absolute endpoint difference in percentage points. Treat the comparisons as sensitivities to *chosen mathematical bounds*, **not** estimates of empirical uncertainty, causal influence, likely future economic outcomes, or model parameter elasticities. Note that one-factor-at-a-time runs do not detect interactions and boundary cases shift the window to keep its width fixed.

- No execution or deployment should be claimed without observed evidence from the target runtime.

## Country transfer readiness

- `country_profiles/portugal/2024/` is **AUDIT ONLY**, not a Portugal model or route.
- The `soc2010_isco08_crosswalk_audit.json` is **classification-only**. All **1,125** code pairs and occupation titles in its CSV exactly match a separately GitHub-hosted BLS-branded Excel copy, as recorded in `independent_xls_vs_csv_verification_2024.json`; this does **not** demonstrate equality with the current official BLS-hosted XLS bytes. Its many-to-many SOC↔ISCO links are **not** job counts or employment weights. Even identified unambiguous code groups cannot set `cog_share` without matched coverage for the 2024 Portuguese employed-person population. Never mix employer-only `Quadros de Pessoal` counts with the national Eurostat/INE denominator without a separately verified coverage adjustment. The original `aiscen` equations and U.S. `Fixed()` / `Scenario()` defaults are unchanged.
- Official `lfsa_egai2d` Portugal 2024 **two-digit employment weights are now available**, and the original one-digit data are preserved. The provisional 2010 SOC ↔ ISCO mirror remains unverified; its 2-digit classification gives approximately 37.19% C-only, 46.44% mixed and 16.37% N-only civilian employment **code coverage**, NOT calibrated C/N population shares or trustworthy error intervals. Flag low-reliability cells and retain missing `OC63` as null. Do not assign `cog_share` until verified official BLS mapping and finer 3-/4-digit within-mixed-group employment weights exist.
- Twenty-six ISCO 4-digit codes already have SOC connections to **both** model C and N: 4-digit headcounts alone will not fully disambiguate them. The Portugal country profile stays `runnable:false`, and source-to-code consistency is **not** empirical calibration of AI exposure.
- A [dated detailed occupational source audit](country_profiles/portugal/2024/detailed_occupation_and_mobility_sources.json) documents Brighter Future / `Quadros de Pessoal` data on employer-only workers. The QP-based ~3.65m workers in enterprises (2024) cannot stand in for the 5.1123m Eurostat all-employed population. The **15.5% observed occupational switching across 2020–2022 among workers present in both periods** must NEVER be plugged into `mu_bar` or `mu`: it is neither 2024, monthly, C/N-specific nor equivalent to a search-efficiency discount. Undated or overlapping occupation-profile listings are not a validated 2024 CPP/ISCO4 population table.
- Before PT calculations, reconcile definitions for national accounts labor share, ISCO occupational C/N split, baseline search pool, hires/quits, job-finding and cross-group worker mobility; evaluate euro-area capital flows and migration as possible structural departures.
- Never use INE annual unemployment, enterprise AI uptake, GERD expenditure, or Eurostat vacancy-stock ratios as automatic equivalents of `U_bar`, `d_anchor`, `iota_R0`, or `fill_bar`. Every dataset/estimate needs units, reference dates, transformations and evidence, and all essential unsourced inputs must fail closed.
- Do not add `country="PT"` to existing numerical entry points, or label U.S. or mixed-input outputs as Portugal. Review an explicit country-selection contract and independent validation before authorizing any national scenario calculation.

## Development
- Python standard library only, with the upstream pinned model fetched during Docker build.
- Run tests in image build. Keep source and parameter provenance.
- For changes: run validation, propose a PR when appropriate, preserve security boundary.
- User explicitly wants no copy-paste, manual git, or manual Docker steps; use already-reviewed control planes where authorized.
