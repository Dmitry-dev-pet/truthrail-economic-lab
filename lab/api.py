"""Local-only HTTP API for a pinned, independent reproduction of Anthropic's
Economic Scenarios for Transformative AI. US conditional scenarios; not forecasts.
No AI inference, authentication provider, telemetry, or runtime network required.
"""
from __future__ import annotations

from dataclasses import asdict, replace
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
import json
import math
import os

from . import __version__

UPSTREAM_DIR = Path(os.environ.get("LAB_UPSTREAM_DIR", "/opt/opa-model"))
HOME = Path(__file__).resolve().parent.parent / "ui" / "index.html"
SOURCE = "https://github.com/fhoces/opa-ai-macro-econ-scenarios"
PAPER = "https://www.anthropic.com/institute/econ-scenarios"
COMMIT = "d4703b6ae0d19dca08fbde11a25c218fa4c7b7a6"
PRESETS = ("modest", "substantial", "extreme")
# Seven published scenario dials, bounded to avoid pathological inputs.
BOUNDS = {
    "m_2030": (0.14, 0.95),
    "d_2030": (0.10, 1.0),
    "a_2030": (0.0, 2.0),
    "psi": (0.0, 1.0),
    "rho": (0.0, 1.0),
    "mu": (0.001, 1.0),
    "theta_H": (0.001, 1.0),
}
FIXED_BOUNDS = {"eps": (0.5, 10.0), "xi": (0.0, 1.0)}

def validate_payload(payload):
    if not isinstance(payload, dict):
        raise ValueError("Body must be a JSON object")
    if set(payload) - {"scenario", "parameters", "fixed"}:
        raise ValueError("Unknown top-level keys")
    selected = payload.get("scenario", "substantial")
    if selected not in PRESETS or not isinstance(selected, str):
        raise ValueError("Unknown scenario")
    params = payload.get("parameters", {})
    fixed = payload.get("fixed", {})
    if not isinstance(params, dict) or not isinstance(fixed, dict):
        raise ValueError("parameters and fixed must be objects")
    def check(group, allowed):
        if set(group) - set(allowed):
            raise ValueError("Unsupported parameter")
        result = {}
        for key, value in group.items():
            low, high = allowed[key]
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(key + " must be a number")
            value = float(value)
            if not math.isfinite(value) or not low <= value <= high:
                raise ValueError(key + " is out of range")
            result[key] = value
        return result
    return selected, check(params, BOUNDS), check(fixed, FIXED_BOUNDS)

def _model():
    from aiscen import Fixed, SCENARIOS, simulate
    from aiscen.report import table3_column
    return Fixed, SCENARIOS, simulate, table3_column

def presets():
    Fixed, SCENARIOS, _, _ = _model()
    f = Fixed()
    return {
        "model_commit": COMMIT, "paper": PAPER,
        "presets": {
            name: {
                "m_2030": s.m_2030, "d_2030": s.d_2030,
                "a_2030": s.a_anchor + s.g_a * (f.t_target - f.t_anchor),
                "psi": s.psi, "rho": s.rho, "mu": s.mu,
                "theta_H": s.theta_H,
            }
            for name in PRESETS for s in (SCENARIOS[name],)
        },
        "bounds": {k: {"min": v[0], "max": v[1]} for k,v in BOUNDS.items()},
        "fixed_defaults": {k: getattr(f,k) for k in FIXED_BOUNDS},
        "fixed_bounds": {k: {"min": v[0], "max": v[1]} for k,v in FIXED_BOUNDS.items()},
    }

def compute(payload):
    selected, params, fixed_params = validate_payload(payload)
    Fixed, SCENARIOS, simulate, table3_column = _model()
    fixed = replace(Fixed(), **fixed_params)
    scenario = SCENARIOS[selected]
    overrides = {k:v for k,v in params.items() if k != "a_2030"}
    if "a_2030" in params:
        a = params["a_2030"]
        if a <= scenario.a_anchor:
            overrides["a_anchor"], overrides["g_a"] = a, 0.0
        else:
            overrides["g_a"] = (a - scenario.a_anchor) / (fixed.t_target - fixed.t_anchor)
    scenario = replace(scenario, **overrides)
    result = simulate.run(fixed, scenario)
    figures = table3_column(result)
    measures = {
        "gdp_gain_pct": "GDP, pct above no-AI",
        "labor_share_pct": "Labor share, pct of income",
        "unemployment_total_pct": "Unemployment rate, all workers, pct",
        "unemployment_sensitive_pct": "Unemployment rate, cognitive, pct",
        "wage_gain_pct": "Average wage, pct above no-AI",
    }
    summary = {k: round(figures[name], 6) for k,name in measures.items()}
    path = []
    for m in result.months:
        path.append({
            "year": round(m.t,6),
            "gdp_gain_pct": round(math.expm1(m.dlnY)*100,6),
            "labor_share_pct": round(m.s_L*100,6),
            "unemployment_total_pct": round(m.u_rate*100,6),
            "unemployment_sensitive_pct": round(m.u_rate_C*100,6),
            "wage_gain_pct": round(math.expm1(m.dlnw_avg)*100,6),
        })
    return {
        "metadata": {
            "version": __version__, "geography": "USA",
            "nature": "Conditional economic scenarios, not forecasts",
            "source": SOURCE, "source_tag": "v1.0",
            "source_commit": COMMIT, "paper": PAPER,
            "data_note": "Anthropic Economic Index MCP is not an input.",
        },
        "inputs": {
            "scenario": selected, "overrides": params,
            "parameters": asdict(scenario), "fixed": asdict(fixed),
        },
        "summary_2030": summary,
        "table3_2030": {k.strip(): round(v,6) for k,v in figures.items()},
        "path": path,
    }

class Handler(SimpleHTTPRequestHandler):
    server_version = "TruthrailEconomicLab/0.1"
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(UPSTREAM_DIR), **kwargs)
    def send_json(self, status, obj):
        data = json.dumps(obj, ensure_ascii=False, allow_nan=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(data)
    def do_GET(self):
        path = urlsplit(self.path).path
        if path in ("/health", "/api/health"):
            return self.send_json(HTTPStatus.OK, {"status":"ok", "version":__version__, "commit":COMMIT})
        if path == "/api/presets":
            try:
                return self.send_json(HTTPStatus.OK, presets())
            except Exception:
                return self.send_json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error":"Model unavailable"})
        if path in ("/", "/index.html"):
            data = HOME.read_bytes()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            return self.wfile.write(data)
        if path == "/explorer":
            self.send_response(HTTPStatus.MOVED_PERMANENTLY)
            self.send_header("Location", "/explorer/")
            self.end_headers()
            return
        if path.startswith("/api/"):
            return self.send_json(HTTPStatus.NOT_FOUND, {"error":"Unknown endpoint"})
        return super().do_GET()
    def do_POST(self):
        path = urlsplit(self.path).path
        if path not in ("/api/run", "/api/experiment"):
            return self.send_json(HTTPStatus.NOT_FOUND, {"error":"Unknown endpoint"})
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length < 1 or length > 16384:
                raise ValueError("Invalid request length")
            payload = json.loads(self.rfile.read(length))
            if path == "/api/experiment":
                from .experiment import run_experiment
                result = run_experiment(payload)
            else:
                result = compute(payload)
            return self.send_json(HTTPStatus.OK, result)
        except (ValueError, TypeError) as exc:
            return self.send_json(HTTPStatus.BAD_REQUEST, {"error":str(exc)})
        except Exception:
            return self.send_json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error":"Model execution failed"})

def main():
    host = os.environ.get("LAB_LISTEN_HOST", "0.0.0.0")
    port = int(os.environ.get("LAB_LISTEN_PORT", "8000"))
    ThreadingHTTPServer((host,port), Handler).serve_forever()

if __name__ == "__main__":
    main()
