"""Fixed, no-secret mathematical reproduction of US AI scenarios.

This reviewed on-demand package does not use Docker, SSH, provider tokens or a
privileged daemon. Public third-party model source is checked at an exact commit
before numerical execution in a separate, credential-free Python process.
"""
from __future__ import annotations

import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile

SOURCE_URL = "https://github.com/fhoces/opa-ai-macro-econ-scenarios.git"
UPSTREAM_TAG = "v1.0"
UPSTREAM_SHA = "d4703b6ae0d19dca08fbde11a25c218fa4c7b7a6"
PAPER_URL = "https://www.anthropic.com/institute/econ-scenarios"
PUBLISHED_GDP_GAINS = {"modest": 1.6, "substantial": 8.3, "extreme": 32.4}


def compute(model_dir: Path) -> dict:
    """Runs only in an isolated Python child with a sanitized environment."""
    sys.path.insert(0, str(model_dir))
    from aiscen import Fixed, SCENARIOS, simulate
    from aiscen.report import table3_column
    summary = {}
    for name, published in PUBLISHED_GDP_GAINS.items():
        values = table3_column(simulate.run(Fixed(), SCENARIOS[name]))
        gain = values["GDP, pct above no-AI"]
        if not math.isfinite(gain) or abs(gain - published) > 0.3:
            raise ValueError("Reproduction differs from the published scenario")
        summary[name] = {
            "gdp_above_no_ai_pct": round(gain, 3),
            "labor_income_share_pct": round(values["Labor share, pct of income"], 3),
            "unemployment_overall_pct": round(values["Unemployment rate, all workers, pct"], 3),
            "unemployment_ai_sensitive_pct": round(values["Unemployment rate, cognitive, pct"], 3),
        }
        if not all(math.isfinite(v) for v in summary[name].values()):
            raise ValueError("Invalid numerical output")
    return {
        "operation": "economic-lab-verify",
        "verified": True,
        "verification": {"status": "verified", "scope": "published_2030_table3_reproduction"},
        "source_commit": UPSTREAM_SHA,
        "source_tag": UPSTREAM_TAG,
        "paper": PAPER_URL,
        "country": "USA",
        "conditional_scenarios_not_forecasts": True,
        "uses_anthropic_economic_index_as_input": False,
        "scenarios": summary,
    }


def run() -> dict:
    """Exact public revision, no user-controlled arguments or runtime credentials."""
    work_root = Path(os.environ.get("RUNNER_TEMP", "/tmp"))
    with tempfile.TemporaryDirectory(prefix="truthrail-econ-", dir=work_root) as tmp:
        source = Path(tmp) / "source"
        clean_env = {
            "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
            "HOME": tmp,
            "TMPDIR": tmp,
            "LANG": "C",
            "GIT_CONFIG_GLOBAL": "/dev/null",
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_TERMINAL_PROMPT": "0",
            "GIT_ASKPASS": "/usr/bin/false",
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONNOUSERSITE": "1",
        }
        try:
            subprocess.run(
                ["git", "-c", "credential.helper=", "clone",
                 "--depth", "1", "--branch", UPSTREAM_TAG, SOURCE_URL, str(source)],
                env=clean_env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                check=True, timeout=120,
            )
            revision = subprocess.run(
                ["git", "-C", str(source), "rev-parse", "HEAD"],
                env=clean_env, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                check=True, timeout=15, text=True,
            ).stdout.strip()
            if revision != UPSTREAM_SHA:
                raise ValueError("Pinned source commit mismatch")
            child = subprocess.run(
                [sys.executable, "-I", str(Path(__file__).resolve()),
                 "--compute", str(source)],
                env=clean_env, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                check=True, timeout=45, text=True,
            )
            if len(child.stdout) > 8192:
                raise ValueError("Receipt too large")
            result = json.loads(child.stdout)
            if result.get("verified") is not True:
                raise ValueError("Numerical cross-check failed")
            return result
        except (subprocess.SubprocessError, OSError, ValueError, json.JSONDecodeError):
            raise SystemExit("Economic Lab verification failed; no sensitive output") from None


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--compute":
        print(json.dumps(compute(Path(sys.argv[2])), separators=(",", ":"), allow_nan=False))
    elif len(sys.argv) == 1:
        print(json.dumps(run(), separators=(",", ":"), allow_nan=False))
    else:
        raise SystemExit("Unsupported Economic Lab verification arguments")
