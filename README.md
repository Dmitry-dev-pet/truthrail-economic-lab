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
- POST /api/experiment (bounded two-axis comparison; local API only)
- GET /api/hypotheses (predeclared proposal catalogue; local API only)
- POST /api/research (one bounded hypothesis-guided study; local API only)

Examples of JSON bodies:

    {"scenario":"extreme"}
    {"scenario":"substantial","parameters":{"psi":0.85,"rho":0.1,"mu":0.06},"fixed":{"eps":6,"xi":0.75}}

Supported seven scenario assumptions: m_2030, d_2030, a_2030, psi,
rho, mu, theta_H. Sensitivity parameters: eps, xi.
The gain dial `a_2030` uses the independent explorer's convention:
when target gain exceeds the preset's mid-2026 anchor the gain grows linearly,
otherwise it remains flat. Unmodified preset runs preserve their original trajectories.

Responses contain `summary_2030`, `table3_2030`, monthly `path`, and full model-input provenance.

### Compare assumptions systematically

The existing single-scenario `/api/run` remains unchanged. The new
`/api/experiment` accepts **exactly two** scenario parameters with 2–5
distinct values each (maximum 25 cells). Each calculation starts from the
same named preset and permitted fixed/baseline overrides. The result includes
the unmodified baseline, 2030 metrics for every cell, percentage-point
differences versus that baseline, all assumptions and the pinned source SHA.

Example request (localhost only):

```json
{
  "scenario": "substantial",
  "axes": {"psi": [0.25, 0.5, 0.75], "mu": [0.03, 0.06, 0.12]}
}
```

Here `psi` is the model's automation-share assumption and `mu` controls
worker movement across occupations. **Neither axis directly models the
creation of entirely new types of tasks.** Do not describe changes in `mu`
as new-task creation. The supplied numbers are illustrative assumptions,
not estimated future values or measurements from the Anthropic Economic Index.

The same fixed 3×3 demonstration is available as the zero-argument
`python -m lab.experiment` command in a prepared local Python environment
with the pinned upstream model installed. This demo does not deploy a
service or grant Mac execution rights. The new API and demo are source-level
changes until separately tested/deployed on the target Mac; the existing
`[mac] economic-lab-verify` command is unchanged and still runs only its
original three published scenarios.

### Ask Alfred for a bounded experiment without deploying the Mac app

The public repository supports an optional, **owner-only** GitHub issue command:

- Exact issue title: `[econ] experiment`
- Issue body: JSON for `/api/experiment`, for example
  `{"scenario":"substantial","axes":{"psi":[0.25,0.5,0.75],"mu":[0.03,0.06,0.12]}}`.
- A GitHub-hosted, ten-minute-bounded job verifies the public upstream model's
  immutable SHA, computes at most 25 cells and posts the resulting table as
  an issue comment. Alfred can create/read that issue through its existing
  authorized GitHub connector; the user needs no shell commands.
- Only an issue **opened by the repository owner** with the **exact title**
  admits computation. Issue bodies are parsed as bounded JSON **data**,
  never used as shell commands, URLs, paths or executable code.
- Issue contents and outputs are **public**. Never put secrets or personal
  information in an economic experiment issue.
- The model-computation job has only `contents:read` permission. A separate
  hosted reporting job receives narrowly scoped `issues:write` permission
  and reads a bounded one-day result artifact.
  No Mac runner, Docker engine, privileged daemon, tunnel or LLM is involved.

This route is a GitHub-backed chat workaround, **not** a low-latency direct
MCP connection to the Mac and not a replacement for the separate local web
interface. The existing `mac-access` fixed verification remains unchanged.

### Let Alfred propose and test hypotheses

An owner-created issue with the existing exact title `[econ] experiment` may
now contain **one bounded research request** in place of explicit numerical
axes:

```json
{"research":"auto"}
```

This invokes a documented, deterministic research planner that evaluates
**candidate questions before running any model** and then computes only its
highest-priority, predeclared test:

1. `new_tasks_vs_automation` — reinstatement of new human tasks (`rho`)
   versus the automation share (`psi`).
2. `new_tasks_vs_mobility` — new tasks versus workers' ease of switching
   occupations (`mu`).
3. `automation_vs_mobility` — re-examination of a previously explored
   relationship.

Alfred may instead select any one listed candidate in the issue body, e.g.
`{"research":"new_tasks_vs_mobility","scenario":"substantial"}`. The plan
captures each testable directional prediction, an alternative, the numerical
threshold, the exact tested parameter values, source commit, fixed priority
rubric and SHA-256 fingerprint **before** any model execution. The model
evaluates 1 preset baseline plus **9 sampled combinations**; the report
shows every cell and whether each prediction holds at all three controlled
levels, is opposite, or is mixed/inconclusive.

This is **hypothesis selection from a transparent, curated catalogue**,
not open-ended autonomous scientific discovery: no extra model calls, new
hypotheses, provider tokens, recurring agent loop or unreviewed task
execution. Novel ideas outside the catalogue should be discussed and added
in reviewed source changes first. Candidate scores express a research
priority, never the probability that a hypothesis is true.

`GET /api/hypotheses` returns the catalogue; `POST /api/research` runs a
single bounded research request once the **separately authorized local**
web service is actually deployed. Both are source features, not evidence
that the Docker API is running on Mac.

`rho` has a different role from `mu`: it measures new labor tasks per
automated task; `mu` describes ease of moving to a different occupation.
We study their conditional effects **inside the U.S. model**, not whether
real-world policies, surveys or workers will behave accordingly. Outputs
are model sensitivity results, not empirical validation or statistical
tests.

## License and attribution

This repository's original application wrapper, API, UI, tests and documentation
are licensed under [MIT](LICENSE). The independently implemented mathematical
model is fetched separately from the
[fhoces/opa-ai-macro-econ-scenarios](https://github.com/fhoces/opa-ai-macro-econ-scenarios)
repository, under its own MIT license. See [NOTICE.md](NOTICE.md) for attribution
and the distinction between the independent implementation and the Anthropic
Institute research paper. The license here does not assert ownership of the
paper, its model, third-party datasets or other upstream materials.

## Scientific limitation

This is a United States economic model. Its seven scenario dials are
assumptions rather than measurements of AI progress. Do **not** use it to
predict Portugal's wages or jobs. Anthropic Economic Index MCP measures observed
Claude task usage separately; it does not calibrate this macroeconomic model.

Public-repository GitHub Actions CI validates the pinned mathematical model and local code; this is distinct from the owner-reviewed Mac execution route and uses no LLM tokens.


## Verified one-shot Mac reproduction (not local API deployment)

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

The original exact fixed three-scenario Action **ran and passed** on the
non-admin Mac M4 via reviewed `mac-access` issue
[#234](https://github.com/Dmitry-dev-pet/mac-access/issues/234) and
[Actions run #38983405178](https://github.com/Dmitry-dev-pet/mac-access/actions/runs/38983405178).
Its binding remains pinned to the old immutable Action version; adding the
research planner does not expand that Mac authorization. The interactive
Docker API/UI remains **unverified and not deployed** until the dedicated
runner has an isolated, authorized engine. The owner-only GitHub issue
research workflow runs on hosted Linux, not on the Mac.

The published table's consistency check is numerical reproducibility, not
evidence that the future will follow any of these conditional scenarios.
