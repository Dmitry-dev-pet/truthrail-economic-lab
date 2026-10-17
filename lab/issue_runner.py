"""Sanitized economic experiment report for exact owner-created GitHub issues.

The issue workflow is a public-repository computation path, not a Mac control plane.
Input is JSON model assumptions only, with no paths, URLs, secrets or commands.
"""
from __future__ import annotations

import json
import os

from .experiment import run_experiment

MAX_ISSUE_BYTES = 4096
METRICS = (
    ("gdp_gain_pct", "GDP gain vs no AI"),
    ("labor_share_pct", "Labor income share"),
    ("unemployment_total_pct", "Unemployment, all"),
    ("unemployment_sensitive_pct", "Unemployment, AI-sensitive"),
    ("wage_gain_pct", "Wage gain vs no AI"),
)


def format_report(result):
    assumptions = result["assumptions"]
    baseline = result["baseline"]["summary_2030"]
    axes = list(assumptions["axes"])
    if len(axes) != 2:
        raise ValueError("Invalid grid output")
    meta = result["metadata"]
    lines = [
        "### Economic Lab · verified calculation (USA, 2030)",
        "",
        f'**Preset:** `{assumptions["scenario"]}` · **model evaluations:** {meta["model_runs"]} '
        f'· **upstream commit:** `{meta["source_commit"]}`',
        "",
        "Economic Index data were not used as model inputs. The values are conditional model outputs, **not forecasts**.",
        "",
        "**Unmodified baseline:** " + ", ".join(
            f'{label}: {baseline[key]:.3f}%' for key, label in METRICS
        ),
        "",
        f'| `{axes[0]}` | `{axes[1]}` | ' + " | ".join(label + " (%)" for _, label in METRICS) + " |",
        "|---:|---:|" + "---:|" * len(METRICS),
    ]
    for cell in result["cells"]:
        x = cell["coordinates"]
        y = cell["summary_2030"]
        lines.append(
            f'| {x[axes[0]]:.3f} | {x[axes[1]]:.3f} | ' +
            " | ".join(f'{y[key]:.3f}' for key, _ in METRICS) + " |"
        )
    lines.extend([
        "",
        "Each row changes only the two displayed parameters relative to the named preset; the table's center is not automatically the baseline.",
        "`mu` is mobility between occupations, not a direct measure of new-task creation.",
        "No Mac access, Docker, LLM or third-party model-provider credentials were used.",
    ])
    return "\n".join(lines)


def report_from_issue_body(text):
    if not isinstance(text, str) or not 0 < len(text.encode("utf-8")) <= MAX_ISSUE_BYTES:
        raise ValueError("Issue body must contain at most 4096 bytes of JSON")
    try:
        request = json.loads(text)
    except json.JSONDecodeError:
        raise ValueError("Issue body is not JSON") from None
    return format_report(run_experiment(request))


def main():
    text = os.environ.get("ECON_ISSUE_JSON", "")
    try:
        print(report_from_issue_body(text))
    except ValueError as exc:
        print(f"### Economic Lab · request rejected\n\n{exc}\n\nOnly bounded JSON scenario parameters are accepted. No code was executed from the issue body.")
        raise SystemExit(2) from None
    except Exception:
        print("### Economic Lab · calculation failed\n\nThe pinned public model could not be evaluated. No raw trace or secrets are published.")
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
