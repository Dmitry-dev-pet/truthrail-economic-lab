# Truthrail Economic Lab

Reproducible local research environment for the 2026 Anthropic Institute working paper
[Economic Scenarios for Transformative AI](https://www.anthropic.com/institute/econ-scenarios).

The core is the independent, MIT-licensed Python implementation by
[Fernando Hoces de la Guardia](https://github.com/fhoces/opa-ai-macro-econ-scenarios),
**not** official Anthropic source. Build is locked to v1.0 / commit
d4703b6ae0d19dca08fbde11a25c218fa4c7b7a6.

## Architecture

- Local Docker service (standard-library Python, no GPU or neural inference).
- Russian-language UI on http://127.0.0.1:8765/
- Upstream interactive explorer with **4,374 precomputed combinations** at http://127.0.0.1:8765/explorer/
- Local API for on-demand 2030 scenarios. No authentication because the port is deliberately loopback-only.
- Results include provenance and monthly paths for 2024–2030.

## Runtime

The Mac needs a working Docker engine. No runtime internet or API key is necessary
after the first Docker image build. Build downloads the pinned public model once.
A reviewed Mac execution route is required for unattended installation; the
GitHub connector alone can commit repository files but cannot invoke local Docker.

For operator reference only:

    docker compose up --build -d
    open http://127.0.0.1:8765/

Stop with: docker compose down

**Alfred should not ask the user to run these manually.** A separately
authorized existing Mac route must execute deployment when available.
Do not substitute a new public proxy or tunnel for this localhost-only service.

## API

- GET /api/health
- GET /api/presets
- POST /api/run

Examples of JSON bodies:

    {"scenario":"extreme"}
    {"scenario":"substantial","parameters":{"psi":0.85,"rho":0.1,"mu":0.06},"fixed":{"eps":6,"xi":0.75}}

Supported seven scenario assumptions: m_2030, d_2030, a_2030, psi,
rho, mu, theta_H. Sensitivity parameters: eps, xi.
The gain dial `a_2030` uses the independent explorer's convention:
when target gain exceeds the preset's mid-2026 anchor the gain grows linearly,
otherwise it remains flat. Unmodified preset runs preserve their original trajectories.

Responses contain `summary_2030`, `table3_2030`, monthly `path`, and full model-input provenance.

## Scientific limitation

This is a United States economic model. Its seven scenario dials are
assumptions rather than measurements of AI progress. Do **not** use it to
predict Portugal's wages or jobs. Anthropic Economic Index MCP measures observed
Claude task usage separately; it does not calibrate this macroeconomic model.

No GitHub-hosted CI is included, to avoid paid Actions minutes.


## No-Docker Mac verification (prepared, not activated)

The dedicated Mac runner has a Docker CLI but no independently verified,
runner-owned Docker Engine. As a safer first experiment, this repository also
provides a **fixed, no-Docker mathematical verification Action** at
`ops/mac/economic_lab_verify/action.yml` plus the read-only package preflight
`ops/mac/action.yml`. The package:

- clones one public mathematical reproduction at tag `v1.0`, verifies the
  exact commit before import, and executes in a temporary credential-free
  Python subprocess;
- computes the **modest, substantial and extreme** USA scenarios and checks
  their GDP outcomes against the authors' published Table 3, within a declared
  numerical tolerance;
- returns a bounded JSON receipt with GDP, labor share and unemployment;
- installs nothing on the Mac, does not start a server, does not touch
  Docker or user credentials, and cleans up temporary files.

This is **not deployed merely because the Action exists**. It must be bound
to an approved immutable GitHub SHA in the reviewed `mac-access` control
plane, admitted by owner-only gate and reported through existing GitHub
operations. The separate interactive local Docker API and UI remain
unverified until an isolated, authorized engine is available.

The published table's consistency check is numerical reproducibility, not
evidence that the future will follow any of these conditional scenarios.
