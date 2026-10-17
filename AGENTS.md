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
- The public hosted `[econ] experiment` issue route accepts only owner-opened exact-title issues, bounded JSON numeric axes (maximum 25 cells), and never executes issue text as commands. Computation has no reporting token; only the final comment step may write to issues. It never reaches the Mac or local API.
- Issue bodies and posted results on this public repository are public; do not include private/user data.
- No execution or deployment should be claimed without observed evidence from the target runtime.

## Development
- Python standard library only, with the upstream pinned model fetched during Docker build.
- Run tests in image build. Keep source and parameter provenance.
- For changes: run validation, propose a PR when appropriate, preserve security boundary.
- User explicitly wants no copy-paste, manual git, or manual Docker steps; use already-reviewed control planes where authorized.
