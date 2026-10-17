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
- No execution or deployment should be claimed without observed evidence from the target runtime.

## Development
- Python standard library only, with the upstream pinned model fetched during Docker build.
- Run tests in image build. Keep source and parameter provenance.
- For changes: run validation, propose a PR when appropriate, preserve security boundary.
- User explicitly wants no copy-paste, manual git, or manual Docker steps; use already-reviewed control planes where authorized.
