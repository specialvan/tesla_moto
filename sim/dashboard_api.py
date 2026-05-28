"""Local dashboard API for the customer-facing motor data board."""

from __future__ import annotations

import argparse
import base64
import csv
import json
import math
import re
import socket
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen
from PIL import Image
from urllib.parse import parse_qs, urlparse


CANDIDATE_META = {
    "hybrid_excitation_if_plus_20": ("混合励磁 +20", "混合励磁", "#2563eb"),
    "baseline": ("基线方案", "内置式永磁同步电机基线", "#0e7490"),
    "winding_series_torque": ("串联增矩", "绕组重构", "#15803d"),
    "hybrid_excitation_if_minus_20": ("混合励磁 -20", "混合励磁", "#7c3aed"),
    "winding_parallel_speed": ("并联高速", "绕组重构", "#b45309"),
    "variable_flux_psi70": ("磁链 70%", "可变磁链", "#be123c"),
    "variable_flux_psi55": ("磁链 55%", "可变磁链", "#db2777"),
}

PROJECT_ROOT = Path(__file__).resolve().parents[1]
API_CONTRACT_VERSION = 1
MAX_POST_BYTES = 65536
LOCAL_CORS_ORIGIN = "http://127.0.0.1"
IRON_LOSS_FREQ_MAX_HZ = 400.0

ENGINEERING_MATURITY_CONTRACT = {
    "engineering_validated": False,
    "physics_model_validated": False,
    "production_release_allowed": False,
    "production_drawing_ready": False,
    "manufacturing_release_ready": False,
    "model_maturity": "proxy_simulation_only",
    "required_evidence": ["FEA", "HIL", "bench", "material", "thermal"],
    "not_allowed_claims": [
        "engineering release",
        "production release",
        "manufacturing release",
        "validated hardware savings",
    ],
}

BROWSER_CANDIDATES = [
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
]

ALGORITHM_ROWS = [
    [
        "MTPA / 弱磁 / MTPV",
        "输入 Vdc、Imax、Ld/Lq、ψf 与转速转矩边界，输出 id/iq 轨迹。",
        "控制器轨迹表、弱磁裕度图、标定 LUT。",
        "高速不掉扭矩，电压裕度可解释",
    ],
    [
        "非线性磁链 LUT 插值",
        "输入 λd/λq 查表、温度维度和边界裁剪规则。",
        "磁链查表模块、插值保护、外推告警。",
        "饱和区转矩预测更贴近实机",
    ],
    [
        "加权工况帕累托评分",
        "输入客户工况权重、可达点、铜耗和候选方案族。",
        "方案排序、收益变化图、客户汇报摘要。",
        "让方案选择从经验转为数据排序",
    ],
    [
        "Bertotti 铁耗估算",
        "输入频率、磁密峰值和三项铁耗系数，输出高速铁耗趋势。",
        "铁耗扫描曲线、高速风险阈值、材料复核清单。",
        "提前暴露高速效率风险",
    ],
    [
        "安全边界判定",
        "输入电压椭圆、电流圆、退磁和峰值工况约束。",
        "可达性雷达、风险灯号、保护策略入口。",
        "避免只看效率而忽略可靠性",
    ],
    [
        "控制 LUT 生成",
        "输入最优轨迹和约束边界，输出候选控制查表数据。",
        "JSON LUT 草案、标定版本草案、台架回灌计划。",
        "把算法变成可复核的软件验证材料",
    ],
]

DELIVERY_ITEMS = [
    ["方案收益页", "展示优化前后评分、铜耗、峰值可达性和高速风险。"],
    ["控制算法包", "包含 MTPA、弱磁、MTPV 与控制 LUT 生成接口。"],
    ["数据证据包", "包含实验 CSV、参数 JSON、模型限制和复核说明。"],
    ["验证路线图", "明确有限元、硬件在环、台架和保护策略的下一步任务。"],
]


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _float(value: str | None) -> float | None:
    if value in (None, ""):
        return None
    return float(value)


def _bool(value: str | None) -> bool:
    return str(value).lower() == "true"


def _build_pareto(root: Path) -> list[dict[str, Any]]:
    summary = _read_json(
        root / "experiments/exp_010_weighted_efficiency_pareto/summary.json"
    )
    rows = []
    for item in summary["pareto_front"]:
        label, family, color = CANDIDATE_META[item["candidate"]]
        rows.append(
            {
                "candidate": item["candidate"],
                "label": label,
                "meanScore": item["mean_score"],
                "feasible": item["min_feasible_weight"],
                "loss": item["sum_weighted_copper_loss_w"],
                "family": family,
                "color": color,
            }
        )
    return rows


def _build_cycles(root: Path) -> list[dict[str, Any]]:
    rows = _read_csv(
        root
        / "experiments/exp_010_weighted_efficiency_pareto/weighted_efficiency_pareto_results.csv"
    )
    return [
        {
            "candidate": row["candidate"],
            "cycle": row["cycle"],
            "feasibleWeight": _float(row["feasible_weight"]),
            "copperLoss": _float(row["weighted_copper_loss_w"]),
            "score": _float(row["score"]),
        }
        for row in rows
    ]


def _build_iron_loss(root: Path) -> list[dict[str, Any]]:
    rows = _read_csv(root / "experiments/exp_011_iron_loss/iron_loss_sweep_results.csv")
    sampled = []
    for row in rows:
        speed = _float(row["speed_rpm"])
        freq_hz = _float(row["freq_hz"])
        is_valid_freq = freq_hz is not None and freq_hz <= IRON_LOSS_FREQ_MAX_HZ
        if speed is None or (speed % 1000 != 0 and is_valid_freq):
            continue
        sampled.append(
            {
                "speed": speed,
                "targetFeasible": _bool(row["min_current_target_feasible"]),
                "ironLoss": _float(row["min_current_target_iron_loss_w"]),
                "efficiency": _float(row["min_current_target_efficiency_pct"]),
                "freqOutOfRange": bool(freq_hz is not None and freq_hz > IRON_LOSS_FREQ_MAX_HZ),
            }
        )
    return sampled


def build_dashboard_payload(root: Path | str | None = None) -> dict[str, Any]:
    project_root = Path(root) if root is not None else Path.cwd()
    project_root = project_root.resolve()
    return {
        "meta": {
            "title": "可控磁通量电机客户数据看板",
            "source": "backend-api",
            "schemaVersion": 1,
        },
        "maturity": dict(ENGINEERING_MATURITY_CONTRACT),
        "paretoFront": _build_pareto(project_root),
        "cycleRows": _build_cycles(project_root),
        "ironLossRows": _build_iron_loss(project_root),
        "algorithmRows": ALGORITHM_ROWS,
        "deliveryItems": DELIVERY_ITEMS,
    }


def build_health_payload(root: Path | str | None = None) -> dict[str, Any]:
    project_root = Path(root) if root is not None else Path.cwd()
    project_root = project_root.resolve()
    dashboard = build_dashboard_payload(project_root)
    return {
        "status": "ok",
        "source": dashboard["meta"]["source"],
        "schemaVersion": dashboard["meta"]["schemaVersion"],
        "page": "controllable_flux_motor_kb.html",
        "pageAvailable": (project_root / "controllable_flux_motor_kb.html").exists(),
        "counts": {
            "paretoFront": len(dashboard["paretoFront"]),
            "cycleRows": len(dashboard["cycleRows"]),
            "ironLossRows": len(dashboard["ironLossRows"]),
            "algorithmRows": len(dashboard["algorithmRows"]),
            "deliveryItems": len(dashboard["deliveryItems"]),
        },
    }


def build_api_schema_payload() -> dict[str, Any]:
    endpoints = [
        {
            "path": "/api/dashboard",
            "methods": ["GET"],
            "responseKeys": ["meta", "maturity", "paretoFront", "cycleRows", "ironLossRows", "algorithmRows", "deliveryItems"],
            "responseObjectKeys": {
                "maturity": list(ENGINEERING_MATURITY_CONTRACT.keys()),
                "paretoFront": ["candidate", "label", "meanScore", "feasible", "loss", "family", "color"],
                "cycleRows": ["candidate", "cycle", "feasibleWeight", "copperLoss", "score"],
                "ironLossRows": ["speed", "targetFeasible", "ironLoss", "efficiency", "freqOutOfRange"],
            },
            "responseTupleLengths": {
                "algorithmRows": 4,
                "deliveryItems": 2,
            },
        },
        {
            "path": "/api/health",
            "methods": ["GET"],
            "responseKeys": ["status", "source", "schemaVersion", "page", "pageAvailable", "counts"],
            "responseObjectKeys": {
                "counts": [
                    "paretoFront",
                    "cycleRows",
                    "ironLossRows",
                    "algorithmRows",
                    "deliveryItems",
                ],
            },
        },
        {
            "path": "/api/schema",
            "methods": ["GET"],
            "responseKeys": ["source", "schemaVersion", "endpoints", "frontendRequiredPaths"],
        },
        {
            "path": "/api/scenario-state",
            "methods": ["GET", "DELETE"],
            "responseKeys": ["source", "schemaVersion", "stateAvailable", "stateSource", "state"],
            "responseObjectKeys": {
                "state": ["candidate", "businessAssumptions", "weights"],
            },
        },
        {
            "path": "/api/decision-pack",
            "methods": ["GET", "POST"],
            "requestStateKeys": ["candidate", "businessAssumptions", "weights"],
            "getQueryKeys": [
                "candidate",
                *DEFAULT_BUSINESS_ASSUMPTIONS.keys(),
                *DEFAULT_WEIGHTS.keys(),
            ],
            "postJson": {
                "requiredKeys": ["candidate", "businessAssumptions", "weights"],
                "businessAssumptionKeys": list(DEFAULT_BUSINESS_ASSUMPTIONS.keys()),
                "weightKeys": list(DEFAULT_WEIGHTS.keys()),
            },
            "responseKeys": ["source", "schemaVersion", "selected", "gains", "businessCase", "weights", "ranking", "maturity"],
            "responseObjectKeys": {
                "selected": ["candidate", "label", "family", "meanScore", "weightedCopperLossW", "feasible"],
                "gains": ["scoreGainPercent", "copperLossChangePercent", "feasibleCycles", "confidencePercent"],
                "businessCase": [
                    "assumptions",
                    "conversionKwhPer100kmPerKw",
                    "perVehicleAnnualSavingYuan",
                    "fleetAnnualSavingYuan",
                    "paybackMonths",
                ],
                "weights": list(DEFAULT_WEIGHTS.keys()),
                "ranking": ["candidate", "label", "family", "simulatedScore", "simulatedFeasible", "rank"],
                "maturity": list(ENGINEERING_MATURITY_CONTRACT.keys()),
            },
        },
        {
            "path": "/api/session-snapshot",
            "methods": ["GET", "POST", "DELETE"],
            "requestStateKeys": [
                "candidate",
                "businessAssumptions",
                "weights",
                "decisionPack",
                "apiSyncLog",
            ],
            "responseKeys": ["source", "schemaVersion", "snapshotAvailable", "snapshot", "metadata"],
            "responseObjectKeys": {
                "snapshot": [
                    "candidate",
                    "businessAssumptions",
                    "weights",
                    "decisionPack",
                    "apiSyncLog",
                    "metadata",
                ],
            },
            "metadataKeys": [
                "snapshotId",
                "createdAt",
                "updatedAt",
                "source",
                "schemaVersion",
                "apiContractVersion",
            ],
        },
        {
            "path": "/api/customer-brief",
            "methods": ["GET", "POST"],
            "requestStateKeys": ["candidate", "businessAssumptions", "weights"],
            "responseKeys": ["source", "schemaVersion", "candidate", "brief", "decisionPack"],
            "responseObjectKeys": {
                "decisionPack": [
                    "source",
                    "schemaVersion",
                    "selected",
                    "gains",
                    "businessCase",
                    "weights",
                    "ranking",
                ],
            },
        },
        {
            "path": "/api/design-spec",
            "methods": ["GET"],
            "responseKeys": ["source", "schemaVersion", "file", "spec"],
            "responseObjectKeys": {
                "spec": [
                    "name",
                    "product",
                    "page",
                    "design_system",
                    "audience",
                    "tokens",
                    "components",
                ],
            },
        },
    ]
    return {
        "source": "backend-api",
        "schemaVersion": 1,
        "endpoints": endpoints,
        "frontendRequiredPaths": [item["path"] for item in endpoints],
    }


def _candidate_cycle_rows(
    cycle_rows: list[dict[str, Any]], candidate: str
) -> list[dict[str, Any]]:
    return [row for row in cycle_rows if row["candidate"] == candidate]


def _weighted_ranking(
    dashboard: dict[str, Any], weights: dict[str, float]
) -> list[dict[str, Any]]:
    ranking = []
    total_weight = sum(weights.values()) or 1.0
    for candidate in dashboard["paretoFront"]:
        rows = _candidate_cycle_rows(dashboard["cycleRows"], candidate["candidate"])
        weighted_score = 0.0
        weighted_feasible = 0.0
        for row in rows:
            weight = weights.get(row["cycle"], 0.0) / total_weight
            weighted_score += (row["score"] or 0.0) * weight
            weighted_feasible += (row["feasibleWeight"] or 0.0) * weight
        ranking.append(
            {
                "candidate": candidate["candidate"],
                "label": candidate["label"],
                "family": candidate["family"],
                "simulatedScore": round(weighted_score, 4),
                "simulatedFeasible": round(weighted_feasible, 4),
            }
        )
    ranking.sort(key=lambda item: item["simulatedScore"], reverse=True)
    for index, item in enumerate(ranking, start=1):
        item["rank"] = index
    return ranking


DEFAULT_WEIGHTS = {
    "urban_low_speed": 40.0,
    "highway_high_speed": 35.0,
    "launch_peak_torque": 25.0,
}

DEFAULT_BUSINESS_ASSUMPTIONS = {
    "production": 50000,
    "mileage": 15000,
    "energyPrice": 0.8,
    "validationInvestment": 180,
}

ROI_ENERGY_CONVERSION_KWH_PER_100KM_PER_KW = 0.12

QUERY_VALUE_BOUNDS = {
    "production": (5000.0, 200000.0),
    "mileage": (5000.0, 50000.0),
    "energyPrice": (0.3, 2.0),
    "validationInvestment": (20.0, 1000.0),
    "urban_low_speed": (0.0, 100.0),
    "highway_high_speed": (0.0, 100.0),
    "launch_peak_torque": (0.0, 100.0),
}

def _query_value(query: dict[str, list[str]], key: str) -> str | None:
    values = query.get(key)
    return values[0] if values else None


def _query_float(
    query: dict[str, list[str]], key: str, default: float | int
) -> float | int:
    value = _query_value(query, key)
    if value in (None, ""):
        return default
    parsed = float(value)
    if not math.isfinite(parsed):
        raise ValueError(f"{key} must be finite")
    bounds = QUERY_VALUE_BOUNDS.get(key)
    if bounds is not None:
        lower, upper = bounds
        if parsed < lower or parsed > upper:
            raise ValueError(f"{key} must be between {lower:g} and {upper:g}")
    return parsed


def _frontend_state_to_query(state: dict[str, Any]) -> dict[str, list[str]]:
    query: dict[str, list[str]] = {}
    candidate = state.get("candidate")
    if candidate not in (None, ""):
        query["candidate"] = [str(candidate)]
    business = state.get("businessAssumptions") or {}
    if not isinstance(business, dict):
        raise ValueError("businessAssumptions must be an object")
    weights = state.get("weights") or {}
    if not isinstance(weights, dict):
        raise ValueError("weights must be an object")
    for key in DEFAULT_BUSINESS_ASSUMPTIONS:
        if key in business:
            query[key] = [str(business[key])]
    for key in DEFAULT_WEIGHTS:
        if key in weights:
            query[key] = [str(weights[key])]
    return query


def _normalize_frontend_state(state: dict[str, Any]) -> dict[str, Any]:
    query = _frontend_state_to_query(state)
    return {
        "candidate": _query_value(query, "candidate") or "hybrid_excitation_if_plus_20",
        "businessAssumptions": {
            key: _query_float(query, key, default)
            for key, default in DEFAULT_BUSINESS_ASSUMPTIONS.items()
        },
        "weights": {
            key: float(_query_float(query, key, default))
            for key, default in DEFAULT_WEIGHTS.items()
        },
    }


def build_scenario_state_payload(
    state: dict[str, Any] | None, state_source: str = "none"
) -> dict[str, Any]:
    return {
        "source": "backend-api",
        "schemaVersion": 1,
        "stateAvailable": state is not None,
        "stateSource": state_source if state is not None else "none",
        "state": state,
    }


def build_session_snapshot_payload(snapshot: dict[str, Any] | None) -> dict[str, Any]:
    metadata = snapshot.get("metadata") if snapshot else None
    return {
        "source": "backend-api",
        "schemaVersion": 1,
        "snapshotAvailable": snapshot is not None,
        "snapshot": snapshot,
        "metadata": metadata,
    }


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _normalize_snapshot_metadata(metadata: Any | None = None) -> dict[str, Any]:
    now = _utc_timestamp()
    existing = metadata if isinstance(metadata, dict) else {}
    snapshot_id = existing.get("snapshotId")
    if not isinstance(snapshot_id, str) or not snapshot_id.startswith("dashboard-session-"):
        snapshot_id = f"dashboard-session-{now.replace(':', '').replace('-', '').replace('Z', '')}"
    created_at = existing.get("createdAt")
    if not isinstance(created_at, str) or not created_at.endswith("Z"):
        created_at = now
    updated_at = existing.get("updatedAt")
    if not isinstance(updated_at, str) or not updated_at.endswith("Z"):
        updated_at = created_at
    return {
        "snapshotId": snapshot_id,
        "createdAt": created_at,
        "updatedAt": updated_at,
        "source": "backend-api",
        "schemaVersion": 1,
        "apiContractVersion": API_CONTRACT_VERSION,
    }


def _normalize_session_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    state = _normalize_frontend_state(snapshot)
    dashboard = build_dashboard_payload(PROJECT_ROOT)
    candidates = {item["candidate"] for item in dashboard["paretoFront"]}
    if state["candidate"] not in candidates:
        raise ValueError(f"unknown candidate: {state['candidate']}")
    decision_pack = snapshot.get("decisionPack") or {}
    if not isinstance(decision_pack, dict):
        raise ValueError("decisionPack must be an object")
    api_sync_log = snapshot.get("apiSyncLog") or {}
    if not isinstance(api_sync_log, dict):
        raise ValueError("apiSyncLog must be an object")
    return {
        **state,
        "decisionPack": decision_pack,
        "apiSyncLog": api_sync_log,
        "metadata": _normalize_snapshot_metadata(snapshot.get("metadata")),
    }


def _scenario_state_path(server: Any) -> Path | None:
    value = getattr(server, "dashboard_state_path", None)
    return Path(value) if value else None


def _session_snapshot_path(server: Any) -> Path | None:
    value = getattr(server, "dashboard_session_snapshot_path", None)
    return Path(value) if value else None


def _load_persisted_scenario_state(server: Any) -> tuple[dict[str, Any] | None, str]:
    path = _scenario_state_path(server)
    if path is None or not path.exists():
        return None, "none"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return None, "none"
        state = _normalize_frontend_state(data)
        dashboard = build_dashboard_payload(PROJECT_ROOT)
        candidates = {item["candidate"] for item in dashboard["paretoFront"]}
        if state["candidate"] not in candidates:
            raise ValueError(f"unknown persisted candidate: {state['candidate']}")
        return state, "persisted"
    except (OSError, json.JSONDecodeError, ValueError):
        try:
            path.unlink()
        except OSError:
            pass
        return None, "none"


def _current_scenario_state(server: Any) -> tuple[dict[str, Any] | None, str]:
    if getattr(server, "dashboard_scenario_state_cleared", False):
        return None, "none"
    state = getattr(server, "dashboard_scenario_state", None)
    if state is not None:
        return state, "memory"
    state, source = _load_persisted_scenario_state(server)
    if state is not None:
        setattr(server, "dashboard_scenario_state", state)
    return state, source


def _save_scenario_state(server: Any, state: dict[str, Any]) -> None:
    if hasattr(server, "dashboard_scenario_state_cleared"):
        delattr(server, "dashboard_scenario_state_cleared")
    setattr(server, "dashboard_scenario_state", state)
    path = _scenario_state_path(server)
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(state, ensure_ascii=False, indent=2, allow_nan=False),
        encoding="utf-8",
    )


def _load_persisted_session_snapshot(server: Any) -> dict[str, Any] | None:
    path = _session_snapshot_path(server)
    if path is None or not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("session snapshot must be an object")
        return _normalize_session_snapshot(data)
    except (OSError, json.JSONDecodeError, ValueError):
        try:
            path.unlink()
        except OSError:
            pass
        return None


def _current_session_snapshot(server: Any) -> dict[str, Any] | None:
    snapshot = getattr(server, "dashboard_session_snapshot", None)
    if snapshot is not None:
        return snapshot
    snapshot = _load_persisted_session_snapshot(server)
    if snapshot is not None:
        setattr(server, "dashboard_session_snapshot", snapshot)
    return snapshot


def _save_session_snapshot(server: Any, snapshot: dict[str, Any]) -> None:
    setattr(server, "dashboard_session_snapshot", snapshot)
    path = _session_snapshot_path(server)
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2, allow_nan=False),
        encoding="utf-8",
    )


def _clear_session_snapshot(server: Any) -> None:
    if hasattr(server, "dashboard_session_snapshot"):
        delattr(server, "dashboard_session_snapshot")
    path = _session_snapshot_path(server)
    if path is None:
        return
    try:
        path.unlink()
    except FileNotFoundError:
        pass


def _clear_scenario_state(server: Any) -> None:
    setattr(server, "dashboard_scenario_state_cleared", True)
    if hasattr(server, "dashboard_scenario_state"):
        delattr(server, "dashboard_scenario_state")
    path = _scenario_state_path(server)
    if path is None:
        return
    try:
        path.unlink()
    except FileNotFoundError:
        pass


def _new_dashboard_server(
    host: str,
    port: int,
    state_path: Path | None = None,
    snapshot_path: Path | None = None,
) -> ThreadingHTTPServer:
    server = ThreadingHTTPServer((host, port), DashboardRequestHandler)
    if state_path is not None:
        server.dashboard_state_path = state_path
    if snapshot_path is not None:
        server.dashboard_session_snapshot_path = snapshot_path
    return server


def _json_response(handler: SimpleHTTPRequestHandler, status: int, payload: dict[str, Any]) -> None:
    body = json.dumps(payload, ensure_ascii=False, allow_nan=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def build_decision_pack_payload(
    root: Path | str | None = None,
    query: dict[str, list[str]] | None = None,
) -> dict[str, Any]:
    project_root = Path(root) if root is not None else Path.cwd()
    dashboard = build_dashboard_payload(project_root.resolve())
    query = query or {}
    selected_candidate = _query_value(query, "candidate") or dashboard["paretoFront"][0]["candidate"]
    selected = next(
        (
            item
            for item in dashboard["paretoFront"]
            if item["candidate"] == selected_candidate
        ),
        None,
    )
    if selected is None:
        raise ValueError(f"unknown candidate: {selected_candidate}")
    baseline = next(item for item in dashboard["paretoFront"] if item["candidate"] == "baseline")
    selected_rows = _candidate_cycle_rows(dashboard["cycleRows"], selected["candidate"])
    weights = {
        key: float(_query_float(query, key, default))
        for key, default in DEFAULT_WEIGHTS.items()
    }
    score_gain = ((selected["meanScore"] - baseline["meanScore"]) / baseline["meanScore"]) * 100
    loss_gain = ((selected["loss"] - baseline["loss"]) / baseline["loss"]) * 100
    feasible_cycles = sum(1 for row in selected_rows if row["feasibleWeight"] == 1)
    saved_watts = baseline["loss"] - selected["loss"]
    assumptions = {
        key: _query_float(query, key, default)
        for key, default in DEFAULT_BUSINESS_ASSUMPTIONS.items()
    }
    per_vehicle_annual_saving = (
        max(saved_watts, 0)
        / 1000
        * ROI_ENERGY_CONVERSION_KWH_PER_100KM_PER_KW
        * assumptions["mileage"]
        / 100
        * assumptions["energyPrice"]
    )
    fleet_annual_saving = per_vehicle_annual_saving * assumptions["production"]
    investment_yuan = assumptions["validationInvestment"] * 10000
    payback_months = investment_yuan / fleet_annual_saving * 12 if fleet_annual_saving else None
    return {
        "source": "backend-api",
        "schemaVersion": dashboard["meta"]["schemaVersion"],
        "dashboard": "controllable_flux_motor_kb.html",
        "theme": "premium black-gold engineering dashboard",
        "selected": {
            "candidate": selected["candidate"],
            "label": selected["label"],
            "family": selected["family"],
            "meanScore": selected["meanScore"],
            "weightedCopperLossW": selected["loss"],
            "feasible": selected["feasible"],
        },
        "gains": {
            "scoreGainPercent": round(score_gain, 2),
            "copperLossChangePercent": round(loss_gain, 2),
            "feasibleCycles": feasible_cycles,
            "confidencePercent": 80,
        },
        "businessCase": {
            "assumptions": assumptions,
            "conversionKwhPer100kmPerKw": ROI_ENERGY_CONVERSION_KWH_PER_100KM_PER_KW,
            "perVehicleAnnualSavingYuan": round(per_vehicle_annual_saving, 2),
            "fleetAnnualSavingYuan": round(fleet_annual_saving, 2),
            "paybackMonths": round(payback_months, 2) if payback_months else None,
        },
        "maturity": dict(ENGINEERING_MATURITY_CONTRACT),
        "weights": weights,
        "ranking": _weighted_ranking(dashboard, weights)[:5],
        "evidence": [
            "EXP-010 weighted efficiency Pareto",
            "EXP-011 iron loss sweep",
            "wiki research plan",
            "OpenDesign black-gold handoff",
        ],
        "disclaimer": "仅用于客户方案筛选和早期决策，不代表量产实机收益承诺。",
    }
def build_customer_brief_payload(
    root: Path | str | None = None,
    query: dict[str, list[str]] | None = None,
) -> dict[str, Any]:
    decision_pack = build_decision_pack_payload(root, query)
    selected = decision_pack["selected"]
    business_case = decision_pack["businessCase"]
    assumptions = business_case["assumptions"]
    candidate = selected["candidate"]
    production = f"{int(assumptions['production']):,}"
    payback = business_case["paybackMonths"]
    payback_text = f"{payback} months" if payback is not None else "not yet positive"
    brief = " ".join(
        [
            f"Recommended candidate: {selected['label']} ({candidate}).",
            f"Scenario production: {production} vehicles/year.",
            f"Score gain: {decision_pack['gains']['scoreGainPercent']}% vs baseline.",
            f"Fleet annual saving: {business_case['fleetAnnualSavingYuan']:,} yuan.",
            f"Payback: {payback_text}.",
            "Evidence scope: dashboard simulation API, not engineering release validation.",
        ]
    )
    return {
        "source": "backend-api",
        "schemaVersion": decision_pack["schemaVersion"],
        "candidate": candidate,
        "brief": brief,
        "decisionPack": decision_pack,
    }


def build_design_spec_payload(root: Path | str | None = None) -> dict[str, Any]:
    project_root = Path(root) if root is not None else PROJECT_ROOT
    relative_path = Path("reports") / "open_design_dashboard_spec.json"
    spec_path = project_root / relative_path
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    return {
        "source": "backend-api",
        "schemaVersion": 1,
        "file": relative_path.as_posix(),
        "spec": spec,
    }


class DashboardRequestHandler(SimpleHTTPRequestHandler):
    server_version = "TeslaMotoDashboardAPI/1.0"

    def __init__(self, *args: Any, directory: str | None = None, **kwargs: Any) -> None:
        super().__init__(*args, directory=directory or str(PROJECT_ROOT), **kwargs)

    def end_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", LOCAL_CORS_ORIGIN)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Accept, Content-Type")
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/__browser_interaction_smoke":
            body = build_browser_interaction_smoke_page().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if parsed.path == "/__browser_error_smoke":
            body = build_browser_error_smoke_page().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if parsed.path == "/__browser_contract_smoke":
            body = build_browser_contract_smoke_page().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if parsed.path in {"/api/dashboard", "/api/health", "/api/schema", "/api/decision-pack", "/api/scenario-state", "/api/session-snapshot", "/api/customer-brief", "/api/design-spec"}:
            status = 200
            try:
                query = parse_qs(parsed.query)
                if _query_value(query, "smokeFail") == "1":
                    raise RuntimeError("intentional smoke failure")
                if parsed.path == "/api/health":
                    payload = build_health_payload(PROJECT_ROOT)
                elif parsed.path == "/api/schema":
                    payload = build_api_schema_payload()
                elif parsed.path == "/api/decision-pack":
                    payload = build_decision_pack_payload(PROJECT_ROOT, query)
                elif parsed.path == "/api/customer-brief":
                    payload = build_customer_brief_payload(PROJECT_ROOT, query)
                elif parsed.path == "/api/design-spec":
                    payload = build_design_spec_payload(PROJECT_ROOT)
                elif parsed.path == "/api/scenario-state":
                    scenario_state, state_source = _current_scenario_state(self.server)
                    payload = build_scenario_state_payload(scenario_state, state_source)
                elif parsed.path == "/api/session-snapshot":
                    payload = build_session_snapshot_payload(_current_session_snapshot(self.server))
                else:
                    payload = build_dashboard_payload(PROJECT_ROOT)
            except ValueError as exc:
                status = 400
                payload = {
                    "error": "dashboard_request_invalid",
                    "message": str(exc),
                }
            except Exception as exc:  # pragma: no cover - exercised through HTTP tests
                status = 500
                payload = {
                    "error": "dashboard_payload_unavailable",
                    "message": str(exc),
                }
            _json_response(self, status, payload)
            return
        super().do_GET()

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path not in {"/api/decision-pack", "/api/session-snapshot", "/api/customer-brief"}:
            self.send_error(404)
            return
        status = 200
        try:
            query = parse_qs(parsed.query)
            if _query_value(query, "smokeFail") == "1":
                raise RuntimeError("intentional smoke failure")
            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError as exc:
                raise ValueError("Content-Length must be an integer") from exc
            if length > MAX_POST_BYTES:
                _json_response(
                    self,
                    413,
                    {
                        "error": "dashboard_request_too_large",
                        "message": f"request body too large; limit is {MAX_POST_BYTES} bytes",
                    },
                )
                return
            raw_body = self.rfile.read(length).decode("utf-8") if length else "{}"
            state = json.loads(raw_body)
            if not isinstance(state, dict):
                raise ValueError("request body must be a JSON object")
            if parsed.path == "/api/session-snapshot":
                snapshot = _normalize_session_snapshot(state)
                _save_session_snapshot(self.server, snapshot)
                _json_response(self, status, build_session_snapshot_payload(snapshot))
                return
            scenario_state = _normalize_frontend_state(state)
            if parsed.path == "/api/customer-brief":
                payload = build_customer_brief_payload(
                    PROJECT_ROOT,
                    _frontend_state_to_query(scenario_state),
                )
                _json_response(self, status, payload)
                return
            payload = build_decision_pack_payload(
                PROJECT_ROOT,
                _frontend_state_to_query(scenario_state),
            )
            _save_scenario_state(self.server, scenario_state)
        except (json.JSONDecodeError, ValueError) as exc:
            status = 400
            payload = {
                "error": "dashboard_request_invalid",
                "message": str(exc),
            }
        except Exception as exc:  # pragma: no cover - exercised through HTTP tests
            status = 500
            payload = {
                "error": "dashboard_payload_unavailable",
                "message": str(exc),
            }
        _json_response(self, status, payload)

    def do_DELETE(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path not in {"/api/scenario-state", "/api/session-snapshot"}:
            self.send_error(404)
            return
        if parsed.path == "/api/session-snapshot":
            _clear_session_snapshot(self.server)
            _json_response(self, 200, build_session_snapshot_payload(None))
            return
        _clear_scenario_state(self.server)
        _json_response(
            self,
            200,
            {
                "source": "backend-api",
                "schemaVersion": 1,
                "stateAvailable": False,
                "stateSource": "cleared",
                "state": None,
            },
        )


class QuietDashboardRequestHandler(DashboardRequestHandler):
    """Request handler for one-shot browser smokes with clean stderr."""

    def log_message(self, format: str, *args: Any) -> None:
        return

    def copyfile(self, source: Any, outputfile: Any) -> None:
        try:
            super().copyfile(source, outputfile)
        except (BrokenPipeError, ConnectionAbortedError, ConnectionResetError):
            return


def build_browser_interaction_smoke_page() -> str:
    return r"""
<!doctype html>
<html lang="zh-CN">
<head><meta charset="utf-8"><title>browser interaction smoke</title></head>
<body>
  <pre id="result">pending</pre>
  <iframe id="target" style="width:1280px;height:900px"></iframe>
  <script>
    const result = document.getElementById("result");
    const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
    async function waitFor(predicate, label) {
      if (label === "dashboard fallback") {
        predicate = () => document.getElementById("target").contentDocument
          .getElementById("api-status")?.classList.contains("offline");
      }
      if (label === "health fallback") {
        predicate = () => document.getElementById("target").contentDocument
          .getElementById("health-grid")?.textContent.includes("离线回退");
      }
      if (label === "candidate click") {
        predicate = () => document.getElementById("target").contentDocument
          .querySelector('[data-demo-candidate="winding_series_torque"]')?.classList.contains("active");
      }
      const started = Date.now();
      while (Date.now() - started < 8000) {
        if (predicate()) return;
        await sleep(100);
      }
      throw new Error(`timeout:${label}`);
    }
    async function runSmoke() {
      const frame = document.getElementById("target");
      frame.src = "/controllable_flux_motor_kb.html";
      await waitFor(() => frame.contentWindow
        && frame.contentDocument?.readyState === "complete"
        && typeof frame.contentWindow.loadDecisionPack === "function"
        && frame.contentDocument.querySelector('[data-demo-candidate="winding_series_torque"]'), "iframe ready");
      const win = frame.contentWindow;
      let clipboardText = "";
      Object.defineProperty(win.navigator, "clipboard", {
        configurable: true,
        value: { writeText: async text => { clipboardText = text; } }
      });
      const originalFetch = win.fetch.bind(win);
      const decisionRequests = [];
      const snapshotRequests = [];
      const briefRequests = [];
      const designSpecRequests = [];
      win.fetch = (input, init = {}) => {
        const url = typeof input === "string" ? input : input.url;
        if (url === "/api/decision-pack" || url.startsWith("/api/decision-pack?")) {
          decisionRequests.push({ url, method: init.method || "GET", body: init.body || "" });
        }
        if (url === "/api/session-snapshot") {
          snapshotRequests.push({ url, method: init.method || "GET", body: init.body || "" });
        }
        if (url === "/api/customer-brief") {
          briefRequests.push({ url, method: init.method || "GET", body: init.body || "" });
        }
        if (url === "/api/design-spec") {
          designSpecRequests.push({ url, method: init.method || "GET", body: init.body || "" });
        }
        return originalFetch(input, init);
      };
      const doc = frame.contentDocument;
      await waitFor(() => !doc.getElementById("api-status")?.classList.contains("offline"), "api connected");
      await waitFor(() => {
        const log = doc.getElementById("api-sync-log")?.textContent || "";
        return log.includes("/api/design-spec") && log.includes("reports/open_design_dashboard_spec.json");
      }, "design spec runtime fetch");

      const targetCandidate = doc.querySelector('[data-demo-candidate="winding_series_torque"]');
      targetCandidate.click();
      await waitFor(
        () => doc.querySelector('[data-demo-candidate="winding_series_torque"]')?.classList.contains("active"),
        "candidate click"
      );

      const urban = doc.querySelector('[data-weight-input="urban_low_speed"]');
      urban.value = "75";
      urban.dispatchEvent(new Event("input", { bubbles: true }));
      await waitFor(() => doc.getElementById("weight-urban_low_speed")?.textContent === "75%", "weight input");

      const production = doc.querySelector('[data-business-input="production"]');
      production.value = "120000";
      production.dispatchEvent(new Event("input", { bubbles: true }));
      const energyPrice = doc.querySelector('[data-business-input="energyPrice"]');
      energyPrice.value = "1.25";
      energyPrice.dispatchEvent(new Event("input", { bubbles: true }));
      await waitFor(() => doc.getElementById("biz-production-label")?.textContent.includes("120"), "production input");
      await waitFor(() => doc.getElementById("biz-price-label")?.textContent.includes("1.25"), "energy price input");

      const refresh = doc.getElementById("refresh-data");
      refresh.click();
      await waitFor(() => !doc.getElementById("api-status")?.classList.contains("offline"), "refresh click");
      await waitFor(() => doc.getElementById("health-grid")?.children.length > 0, "health counts");

      const decisionPack = await win.loadDecisionPack();
      if (decisionPack.source !== "backend-api" || decisionPack.selected.candidate !== "winding_series_torque") {
        throw new Error("decision pack export did not use backend API state");
      }
      if (decisionPack.weights.urban_low_speed !== 75) {
        throw new Error("decision pack export did not include UI weight input");
      }
      if (decisionPack.businessCase?.assumptions?.production !== 120000) {
        throw new Error("decision pack export did not include UI production input");
      }
      if (decisionPack.businessCase?.assumptions?.energyPrice !== 1.25) {
        throw new Error("decision pack export did not include UI energy price input");
      }
      win.recordApiSync("/api/session-snapshot-history", true, "saved-log-marker");
      await waitFor(() => {
        const log = doc.getElementById("api-sync-log")?.textContent || "";
        return log.includes("/api/dashboard")
          && log.includes("/api/health")
          && log.includes("/api/schema")
          && log.includes("/api/scenario-state")
          && log.includes("/api/decision-pack")
          && log.includes("POST");
      }, "api sync diagnostics");
      const postedDecisionState = decisionRequests.find(request => request.method === "POST");
      if (!postedDecisionState) {
        throw new Error("decision pack API was not called with POST state");
      }
      const postedBody = JSON.parse(postedDecisionState.body);
      if (postedBody.candidate !== "winding_series_torque" || postedBody.businessAssumptions?.production !== 120000) {
        throw new Error("decision pack POST body did not include UI state");
      }
      doc.getElementById("export-decision-pack").click();
      await waitFor(() => clipboardText.includes("winding_series_torque"), "decision pack clipboard");
      const clipboardPack = JSON.parse(clipboardText);
      if (clipboardPack.source !== "backend-api") {
        throw new Error("clipboard decision pack was not copied from backend API");
      }
      if (clipboardPack.businessCase?.assumptions?.production !== 120000) {
        throw new Error("clipboard decision pack missing business case assumptions");
      }
      doc.getElementById("export-brief").click();
      await waitFor(() => clipboardText.includes("Evidence scope: dashboard simulation API"), "customer brief clipboard");
      const postedBriefState = briefRequests.find(request => request.method === "POST");
      if (!postedBriefState) {
        throw new Error("customer brief API was not called with POST state");
      }
      const postedBriefBody = JSON.parse(postedBriefState.body);
      if (postedBriefBody.candidate !== "winding_series_torque" || postedBriefBody.businessAssumptions?.production !== 120000) {
        throw new Error("customer brief POST body did not include UI state");
      }
      doc.getElementById("export-design-spec").click();
      await waitFor(() => clipboardText.includes("open_design_dashboard_spec"), "design spec clipboard");
      const clipboardDesignSpec = JSON.parse(clipboardText);
      if (clipboardDesignSpec.source !== "backend-api" || clipboardDesignSpec.file !== "reports/open_design_dashboard_spec.json") {
        throw new Error("design spec export did not use backend API payload");
      }
      if (clipboardDesignSpec.spec?.product !== "customer_dashboard") {
        throw new Error("design spec export missing customer dashboard spec");
      }
      doc.getElementById("save-session-snapshot").click();
      await waitFor(() => snapshotRequests.some(request => request.method === "POST"), "session snapshot POST");
      const postedSnapshot = JSON.parse(snapshotRequests.find(request => request.method === "POST").body);
      if (postedSnapshot.candidate !== "winding_series_torque" || postedSnapshot.decisionPack?.selected?.candidate !== "winding_series_torque") {
        throw new Error("session snapshot POST body did not include current UI and decision pack state");
      }
      if (!postedSnapshot.apiSyncLog?.["/api/decision-pack"] || !postedSnapshot.apiSyncLog?.["/api/dashboard"]) {
        throw new Error("session snapshot POST body did not include API sync log");
      }
      const snapshotResponse = await originalFetch("/api/session-snapshot", { headers: { "Accept": "application/json" } });
      if (!snapshotResponse.ok) throw new Error(`session snapshot GET ${snapshotResponse.status}`);
      const savedSnapshot = await snapshotResponse.json();
      if (!savedSnapshot.snapshotAvailable || savedSnapshot.snapshot?.candidate !== "winding_series_torque") {
        throw new Error("session snapshot GET did not return saved UI state");
      }
      if (!savedSnapshot.metadata?.snapshotId || savedSnapshot.snapshot?.metadata?.snapshotId !== savedSnapshot.metadata.snapshotId) {
        throw new Error("session snapshot GET did not return backend audit metadata");
      }
      await waitFor(() => {
        const status = doc.getElementById("session-snapshot-status")?.textContent || "";
        return status.includes("winding_series_torque") && status.includes(savedSnapshot.metadata.snapshotId);
      }, "session snapshot metadata status");

      doc.getElementById("clear-scenario-state").click();
      await waitFor(() => {
        const status = doc.getElementById("scenario-state-status")?.textContent || "";
        const log = doc.getElementById("api-sync-log")?.textContent || "";
        return status.includes("none") && log.includes("/api/scenario-state") && log.includes("cleared");
      }, "scenario clear before session restore");
      const clearedStateResponse = await originalFetch("/api/scenario-state", { headers: { "Accept": "application/json" } });
      if (!clearedStateResponse.ok) throw new Error(`scenario state GET after clear ${clearedStateResponse.status}`);
      const clearedState = await clearedStateResponse.json();
      if (clearedState.stateAvailable || clearedState.state !== null) {
        throw new Error("scenario state remained available after clear");
      }

      frame.src = "/controllable_flux_motor_kb.html?reload=1";
      await waitFor(() => frame.contentWindow
        && frame.contentWindow.location.search === "?reload=1"
        && frame.contentDocument?.readyState === "complete"
        && typeof frame.contentWindow.loadDecisionPack === "function"
        && frame.contentDocument.querySelector('[data-demo-candidate="winding_series_torque"]'), "iframe reload ready");
      const reloadedDoc = frame.contentDocument;
      await waitFor(
        () => reloadedDoc.querySelector('[data-demo-candidate="winding_series_torque"]')?.classList.contains("active"),
        "session snapshot restore candidate"
      );
      await waitFor(() => reloadedDoc.getElementById("weight-urban_low_speed")?.textContent === "75%", "session snapshot restore weight");
      await waitFor(() => reloadedDoc.getElementById("biz-production-label")?.textContent.includes("120"), "session snapshot restore production");
      await waitFor(() => {
        const log = reloadedDoc.getElementById("api-sync-log")?.textContent || "";
        return log.includes("/api/session-snapshot")
          && log.includes("winding_series_torque")
          && log.includes("restored: saved-log-marker");
      }, "session snapshot restore log");
      await waitFor(() => {
        const status = reloadedDoc.getElementById("session-snapshot-status")?.textContent || "";
        return status.includes("winding_series_torque") && status.includes(savedSnapshot.metadata.snapshotId);
      }, "session snapshot restore metadata status");
      reloadedDoc.getElementById("clear-session-snapshot").click();
      await waitFor(() => {
        const log = reloadedDoc.getElementById("api-sync-log")?.textContent || "";
        return log.includes("/api/session-snapshot") && log.includes("cleared");
      }, "session snapshot clear status");
      const clearedSnapshotResponse = await originalFetch("/api/session-snapshot", { headers: { "Accept": "application/json" } });
      if (!clearedSnapshotResponse.ok) throw new Error(`session snapshot GET after clear ${clearedSnapshotResponse.status}`);
      const clearedSnapshot = await clearedSnapshotResponse.json();
      if (clearedSnapshot.snapshotAvailable || clearedSnapshot.snapshot !== null) {
        throw new Error("session snapshot remained available after clear");
      }

      frame.src = "/controllable_flux_motor_kb.html?reload=2";
      await waitFor(() => frame.contentWindow
        && frame.contentWindow.location.search === "?reload=2"
        && frame.contentDocument?.readyState === "complete"
        && typeof frame.contentWindow.loadDecisionPack === "function"
        && frame.contentDocument.querySelector('[data-demo-candidate="hybrid_excitation_if_plus_20"]'), "iframe second reload ready");
      const clearedDoc = frame.contentDocument;
      await waitFor(
        () => clearedDoc.querySelector('[data-demo-candidate="hybrid_excitation_if_plus_20"]')?.classList.contains("active"),
        "scenario clear candidate"
      );
      await waitFor(() => clearedDoc.getElementById("weight-urban_low_speed")?.textContent === "40%", "scenario clear weight");
      await waitFor(() => clearedDoc.getElementById("biz-production-label")?.textContent.includes("50"), "scenario clear production");

      result.textContent = "browser_interaction=ok\n"
        + "candidate_click=ok\n"
        + "weight_input=ok\n"
        + "scenario_restore=ok\n"
        + "scenario_clear=ok\n"
        + "api_sync_log=ok\n"
        + "session_snapshot=ok\n"
        + "session_snapshot_metadata=ok\n"
        + "session_snapshot_clear=ok\n"
        + "refresh_click=ok\n"
        + "customer_brief_export=ok\n"
        + "decision_pack_export=ok\n"
        + `decision_pack_candidate=${decisionPack.selected.candidate}\n`
        + `decision_pack_weight_urban=${decisionPack.weights.urban_low_speed}\n`
        + `decision_pack_production=${decisionPack.businessCase.assumptions.production}\n`
        + `decision_pack_energy_price=${decisionPack.businessCase.assumptions.energyPrice}\n`
        + `decision_pack_transport=${postedDecisionState.method}\n`
        + `clipboard_source=${clipboardPack.source}\n`
        + "clipboard_business_case=ok\n"
        + "design_spec_runtime_fetch=ok\n"
        + "design_spec_export=ok\n"
        + `design_spec_file=${clipboardDesignSpec.file}\n`
        + `design_spec_clipboard_product=${clipboardDesignSpec.spec.product}`;
    }
    runSmoke().catch(error => {
      result.textContent = `browser_interaction=failed\n${error.stack || error.message}`;
    });
  </script>
</body>
</html>
"""


def build_browser_error_smoke_page() -> str:
    return r"""
<!doctype html>
<html lang="zh-CN">
<head><meta charset="utf-8"><title>browser error smoke</title></head>
<body>
  <pre id="result">pending</pre>
  <iframe id="target" style="width:1280px;height:900px"></iframe>
  <script>
    const result = document.getElementById("result");
    const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
    async function waitFor(predicate, label) {
      const started = Date.now();
      while (Date.now() - started < 8000) {
        if (predicate()) return;
        await sleep(100);
      }
      throw new Error(`timeout:${label}`);
    }
    async function runSmoke() {
      const frame = document.getElementById("target");
      frame.src = "/controllable_flux_motor_kb.html";
      await waitFor(() => frame.contentWindow
        && frame.contentDocument?.readyState === "complete"
        && typeof frame.contentWindow.loadRuntimeData === "function", "iframe ready");
      const win = frame.contentWindow;
      let clipboardText = "";
      Object.defineProperty(win.navigator, "clipboard", {
        configurable: true,
        value: { writeText: async text => { clipboardText = text; } }
      });
      const originalFetch = win.fetch.bind(win);
      win.fetch = (input, init) => {
        const url = typeof input === "string" ? input : input.url;
        if (url === "/api/dashboard" || url === "/api/health" || url.startsWith("/api/decision-pack")) {
          const separator = url.includes("?") ? "&" : "?";
          return originalFetch(`${url}${separator}smokeFail=1`, init);
        }
        return originalFetch(input, init);
      };
      await win.loadRuntimeData();
      win.renderAll();
      const doc = frame.contentDocument;
      await waitFor(() => doc.getElementById("api-status")?.classList.contains("offline"), "dashboard fallback");
      await waitFor(() => doc.getElementById("health-grid")?.children.length >= 5, "health fallback");
      await waitFor(() => doc.getElementById("winner-name")?.textContent.trim().length > 0, "fallback render");
      doc.getElementById("export-decision-pack").click();
      await waitFor(() => clipboardText.includes("businessCase"), "decision fallback clipboard");
      const fallbackPack = JSON.parse(clipboardText);
      if (fallbackPack.source === "backend-api") {
        throw new Error("decision pack fallback unexpectedly used backend API");
      }
      if (!fallbackPack.businessCase?.assumptions) {
        throw new Error("decision pack fallback missing business case");
      }
      result.textContent = "browser_error=ok\n"
        + "dashboard_fallback=ok\n"
        + "health_fallback=ok\n"
        + "decision_pack_fallback=ok\n"
        + "fallback_clipboard_source=local";
    }
    runSmoke().catch(error => {
      result.textContent = `browser_error=failed\n${error.stack || error.message}`;
    });
  </script>
</body>
</html>
"""


def build_browser_contract_smoke_page() -> str:
    return r"""
<!doctype html>
<html lang="zh-CN">
<head><meta charset="utf-8"><title>browser contract smoke</title></head>
<body>
  <pre id="result">pending</pre>
  <iframe id="target" style="width:1280px;height:900px"></iframe>
  <script>
    const result = document.getElementById("result");
    const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
    async function waitFor(predicate, label) {
      const started = Date.now();
      while (Date.now() - started < 8000) {
        if (predicate()) return;
        await sleep(100);
      }
      throw new Error(`timeout:${label}`);
    }
    async function runSmoke() {
      const frame = document.getElementById("target");
      frame.src = "/controllable_flux_motor_kb.html";
      await waitFor(() => frame.contentWindow
        && frame.contentDocument?.readyState === "complete"
        && typeof frame.contentWindow.loadDecisionPack === "function", "iframe ready");
      const win = frame.contentWindow;
      let clipboardText = "";
      Object.defineProperty(win.navigator, "clipboard", {
        configurable: true,
        value: { writeText: async text => { clipboardText = text; } }
      });
      const originalFetch = win.fetch.bind(win);
      let rejectDashboardOnce = true;
      let rejectHealthOnce = true;
      win.fetch = (input, init) => {
        const url = typeof input === "string" ? input : input.url;
        if (url === "/api/dashboard" && rejectDashboardOnce) {
          rejectDashboardOnce = false;
          return Promise.resolve(new Response(JSON.stringify({
            meta: { source: "backend-api", schemaVersion: 999 },
            paretoFront: null,
            cycleRows: null,
          }), {
            status: 200,
            headers: { "Content-Type": "application/json" }
          }));
        }
        if (url === "/api/health" && rejectHealthOnce) {
          rejectHealthOnce = false;
          return Promise.resolve(new Response(JSON.stringify({
            status: "ok",
            counts: null,
          }), {
            status: 200,
            headers: { "Content-Type": "application/json" }
          }));
        }
        if (url === "/api/decision-pack" || url.startsWith("/api/decision-pack?")) {
          return Promise.resolve(new Response(JSON.stringify({
            source: "backend-api",
            schemaVersion: 999,
            selected: null,
          }), {
            status: 200,
            headers: { "Content-Type": "application/json" }
          }));
        }
        if (url === "/api/customer-brief") {
          return Promise.resolve(new Response(JSON.stringify({
            source: "backend-api",
            schemaVersion: 999,
            candidate: null,
          }), {
            status: 200,
            headers: { "Content-Type": "application/json" }
          }));
        }
        if (url === "/api/scenario-state") {
          return Promise.resolve(new Response(JSON.stringify({
            source: "backend-api",
            schemaVersion: 999,
            stateAvailable: true,
            state: { candidate: "winding_series_torque" },
          }), {
            status: 200,
            headers: { "Content-Type": "application/json" }
          }));
        }
        if (url === "/api/session-snapshot" && init?.method === "POST") {
          return Promise.resolve(new Response(JSON.stringify({
            source: "backend-api",
            schemaVersion: 999,
            snapshotAvailable: true,
            snapshot: null,
          }), {
            status: 200,
            headers: { "Content-Type": "application/json" }
          }));
        }
        if (url === "/api/session-snapshot" && init?.method === "DELETE") {
          return Promise.resolve(new Response(JSON.stringify({
            source: "backend-api",
            schemaVersion: 999,
            snapshotAvailable: true,
          }), {
            status: 200,
            headers: { "Content-Type": "application/json" }
          }));
        }
        if (url === "/api/design-spec") {
          return Promise.resolve(new Response(JSON.stringify({
            source: "backend-api",
            schemaVersion: 999,
            file: "reports/open_design_dashboard_spec.json",
            spec: null,
          }), {
            status: 200,
            headers: { "Content-Type": "application/json" }
          }));
        }
        return originalFetch(input, init);
      };
      const doc = frame.contentDocument;
      await waitFor(() => !doc.getElementById("api-status")?.classList.contains("offline"), "api connected");
      await win.loadDashboardData();
      await waitFor(() => doc.getElementById("api-status")?.classList.contains("offline"), "dashboard payload schema rejected");
      const dashboardLog = doc.getElementById("api-sync-log")?.textContent || "";
      if (!dashboardLog.includes("/api/dashboard") || !dashboardLog.includes("error")) {
        throw new Error("incompatible dashboard payload rejection was not surfaced");
      }
      await win.loadBackendHealth();
      const healthLog = doc.getElementById("api-sync-log")?.textContent || "";
      if (win.eval("backendHealth") !== null) {
        throw new Error("incompatible health payload was accepted");
      }
      if (!healthLog.includes("/api/health") || !healthLog.includes("error")) {
        throw new Error("incompatible health payload rejection was not surfaced");
      }
      doc.getElementById("export-decision-pack").click();
      await waitFor(() => clipboardText.includes("businessCase"), "contract fallback clipboard");
      const pack = JSON.parse(clipboardText);
      if (pack.source === "backend-api") {
        throw new Error("incompatible decision pack payload was accepted");
      }
      if (pack.schemaVersion !== 1 || !pack.businessCase?.assumptions) {
        throw new Error("local decision pack fallback missing schema contract");
      }
      doc.getElementById("export-brief").click();
      await waitFor(() => clipboardText.includes("推荐方案"), "customer brief contract fallback clipboard");
      if (clipboardText.includes("Evidence scope: dashboard simulation API")) {
        throw new Error("incompatible customer brief payload was accepted");
      }
      doc.getElementById("export-design-spec").click();
      await waitFor(() => clipboardText.includes("customer_dashboard"), "design spec contract fallback clipboard");
      const designSpec = JSON.parse(clipboardText);
      if (designSpec.source === "backend-api") {
        throw new Error("incompatible design spec payload was accepted");
      }
      if (designSpec.schemaVersion !== 1 || designSpec.spec?.product !== "customer_dashboard") {
        throw new Error("local design spec fallback missing schema contract");
      }
      await win.loadScenarioState();
      const scenarioStatus = doc.getElementById("scenario-state-status")?.textContent || "";
      const scenarioLog = doc.getElementById("api-sync-log")?.textContent || "";
      if (!doc.querySelector('[data-demo-candidate="hybrid_excitation_if_plus_20"]')?.classList.contains("active")) {
        throw new Error("incompatible scenario state mutated the selected candidate");
      }
      if (!scenarioStatus.includes("none") || !scenarioLog.includes("/api/scenario-state") || !scenarioLog.includes("error")) {
        throw new Error("incompatible scenario state rejection was not surfaced");
      }
      doc.getElementById("save-session-snapshot").click();
      await waitFor(() => {
        const log = doc.getElementById("api-sync-log")?.textContent || "";
        return log.includes("/api/session-snapshot") && log.includes("error");
      }, "session snapshot save schema rejected");
      const snapshotStatus = doc.getElementById("session-snapshot-status")?.textContent || "";
      if (!snapshotStatus.includes("none")) {
        throw new Error("incompatible session snapshot save updated status");
      }
      doc.getElementById("clear-session-snapshot").click();
      await waitFor(() => {
        const log = doc.getElementById("api-sync-log")?.textContent || "";
        return log.includes("/api/session-snapshot") && log.includes("error");
      }, "session snapshot clear schema rejected");
      const clearedSnapshotStatus = doc.getElementById("session-snapshot-status")?.textContent || "";
      if (!clearedSnapshotStatus.includes("none")) {
        throw new Error("incompatible session snapshot clear updated status");
      }
      const schemaWin = frame.contentWindow;
      const schemaOriginalFetch = schemaWin.fetch.bind(schemaWin);
      let rejectSchemaOnce = true;
      schemaWin.fetch = async (input, init) => {
        const url = typeof input === "string" ? input : input.url;
        const response = await schemaOriginalFetch(input, init);
        if (url === "/api/schema") {
          const payload = await response.clone().json();
          if (rejectSchemaOnce) {
            rejectSchemaOnce = false;
            return new Response(JSON.stringify({
              source: "backend-api",
              schemaVersion: 999,
              endpoints: [],
            }), {
              status: 200,
              headers: { "Content-Type": "application/json" }
            });
          }
          payload.endpoints = payload.endpoints.map(endpoint => endpoint.path === "/api/session-snapshot"
            ? { ...endpoint, methods: ["GET", "POST"] }
            : endpoint);
          return new Response(JSON.stringify(payload), {
            status: 200,
            headers: { "Content-Type": "application/json" }
          });
        }
        return response;
      };
      await schemaWin.loadBackendSchema();
      if (schemaWin.eval("backendSchema") !== null) {
        throw new Error("incompatible schema payload was accepted");
      }
      const schemaPayloadLog = doc.getElementById("api-sync-log")?.textContent || "";
      if (!schemaPayloadLog.includes("/api/schema") || !schemaPayloadLog.includes("error")) {
        throw new Error("incompatible schema payload rejection was not surfaced");
      }
      await schemaWin.loadBackendSchema();
      if (schemaWin.eval("backendSchema") !== null) {
        throw new Error("incompatible session snapshot schema was accepted");
      }
      schemaWin.renderDeliveryHealth();
      const schemaDoc = frame.contentDocument;
      await waitFor(() => schemaDoc.getElementById("health-grid")?.textContent.includes("pending"), "session schema rejected");
      result.textContent = "browser_contract=ok\n"
        + "dashboard_payload_schema_rejected=ok\n"
        + "health_payload_schema_rejected=ok\n"
        + "schema_payload_schema_rejected=ok\n"
        + "decision_pack_contract_fallback=ok\n"
        + "customer_brief_contract_fallback=ok\n"
        + "design_spec_contract_fallback=ok\n"
        + "scenario_state_schema_rejected=ok\n"
        + "session_snapshot_save_schema_rejected=ok\n"
        + "session_snapshot_clear_schema_rejected=ok\n"
        + "session_snapshot_schema_rejected=ok\n"
        + "contract_clipboard_source=local";
    }
    runSmoke().catch(error => {
      result.textContent = `browser_contract=failed\n${error.stack || error.message}`;
    });
  </script>
</body>
</html>
"""


def run_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    state_path = PROJECT_ROOT / "reports" / "dashboard-scenario-state.json"
    snapshot_path = PROJECT_ROOT / "reports" / "dashboard-session-snapshot.json"
    server = _new_dashboard_server(host, port, state_path, snapshot_path)
    print(f"Dashboard API running at http://{host}:{port}/")
    print(f"Dashboard page: http://{host}:{port}/controllable_flux_motor_kb.html")
    print(f"Scenario state: {state_path}")
    print(f"Session snapshot: {snapshot_path}")
    server.serve_forever()


def run_smoke_check(host: str = "127.0.0.1") -> int:
    server = ThreadingHTTPServer((host, 0), QuietDashboardRequestHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://{host}:{server.server_port}"
    try:
        with urlopen(f"{base_url}/api/dashboard", timeout=5) as response:
            dashboard = json.loads(response.read().decode("utf-8"))
            print(
                "dashboard_api="
                f"{response.status} pareto={len(dashboard['paretoFront'])} "
                f"cycles={len(dashboard['cycleRows'])}"
            )

        with urlopen(f"{base_url}/api/health", timeout=5) as response:
            health = json.loads(response.read().decode("utf-8"))
            print(
                "health_api="
                f"{response.status} status={health['status']} "
                f"pageAvailable={health['pageAvailable']}"
            )

        with urlopen(f"{base_url}/api/schema", timeout=5) as response:
            schema = json.loads(response.read().decode("utf-8"))
            print(
                "schema_api="
                f"{response.status} endpoints={len(schema['endpoints'])} "
                f"version={schema['schemaVersion']}"
            )
        schema_report = PROJECT_ROOT / "reports" / "dashboard-api-schema.json"
        if json.loads(schema_report.read_text(encoding="utf-8")) != schema:
            raise RuntimeError("dashboard API schema report is out of sync")
        print(f"schema_report=ok path={schema_report}")

        with urlopen(f"{base_url}/api/decision-pack", timeout=5) as response:
            decision_pack = json.loads(response.read().decode("utf-8"))
            print(
                "decision_pack_api="
                f"{response.status} selected={decision_pack['selected']['candidate']} "
                f"ranking={len(decision_pack['ranking'])}"
            )

        frontend_state = json.dumps(
            {
                "candidate": "winding_series_torque",
                "businessAssumptions": {
                    "production": 120000,
                    "mileage": 22000,
                    "energyPrice": 1.25,
                    "validationInvestment": 240,
                },
                "weights": {
                    "urban_low_speed": 75,
                    "highway_high_speed": 15,
                    "launch_peak_torque": 10,
                },
            }
        ).encode("utf-8")
        request = Request(
            f"{base_url}/api/decision-pack",
            data=frontend_state,
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        with urlopen(request, timeout=5) as response:
            decision_pack_post = json.loads(response.read().decode("utf-8"))
            print(
                "decision_pack_post_api="
                f"{response.status} selected={decision_pack_post['selected']['candidate']} "
                f"production={decision_pack_post['businessCase']['assumptions']['production']}"
            )

        with urlopen(f"{base_url}/api/scenario-state", timeout=5) as response:
            scenario_state = json.loads(response.read().decode("utf-8"))
            print(
                "scenario_state_api="
                f"{response.status} available={scenario_state['stateAvailable']} "
                f"source={scenario_state['stateSource']}"
            )

        request = Request(f"{base_url}/api/scenario-state", method="DELETE")
        with urlopen(request, timeout=5) as response:
            scenario_state_clear = json.loads(response.read().decode("utf-8"))
            print(
                "scenario_state_clear_api="
                f"{response.status} available={scenario_state_clear['stateAvailable']}"
            )

        with urlopen(f"{base_url}/api/scenario-state", timeout=5) as response:
            scenario_state_read_after_clear = json.loads(response.read().decode("utf-8"))
            print(
                "scenario_state_read_after_clear_api="
                f"{response.status} available={scenario_state_read_after_clear['stateAvailable']} "
                f"source={scenario_state_read_after_clear['stateSource']}"
            )

        with urlopen(f"{base_url}/api/session-snapshot", timeout=5) as response:
            session_snapshot = json.loads(response.read().decode("utf-8"))
            print(
                "session_snapshot_api="
                f"{response.status} available={session_snapshot['snapshotAvailable']}"
            )

        snapshot_state = json.dumps(
            {
                "candidate": "winding_series_torque",
                "businessAssumptions": {
                    "production": 120000,
                    "mileage": 22000,
                    "energyPrice": 1.25,
                    "validationInvestment": 240,
                },
                "weights": {
                    "urban_low_speed": 75,
                    "highway_high_speed": 15,
                    "launch_peak_torque": 10,
                },
                "decisionPack": decision_pack_post,
                "apiSyncLog": {
                    "/api/decision-pack": {"ok": True, "message": "POST"},
                    "/api/dashboard": {"ok": True, "message": "loaded"},
                },
            }
        ).encode("utf-8")
        request = Request(
            f"{base_url}/api/session-snapshot",
            data=snapshot_state,
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        with urlopen(request, timeout=5) as response:
            session_snapshot_post = json.loads(response.read().decode("utf-8"))
            print(
                "session_snapshot_post_api="
                f"{response.status} available={session_snapshot_post['snapshotAvailable']} "
                f"candidate={session_snapshot_post['snapshot']['candidate']} "
                f"metadata={session_snapshot_post['metadata']['snapshotId']}"
            )

        with urlopen(f"{base_url}/api/session-snapshot", timeout=5) as response:
            session_snapshot_read = json.loads(response.read().decode("utf-8"))
            print(
                "session_snapshot_read_api="
                f"{response.status} available={session_snapshot_read['snapshotAvailable']} "
                f"candidate={session_snapshot_read['snapshot']['candidate']} "
                f"metadata={session_snapshot_read['metadata']['snapshotId']}"
            )

        request = Request(f"{base_url}/api/session-snapshot", method="DELETE")
        with urlopen(request, timeout=5) as response:
            session_snapshot_clear = json.loads(response.read().decode("utf-8"))
            print(
                "session_snapshot_clear_api="
                f"{response.status} available={session_snapshot_clear['snapshotAvailable']}"
            )

        with urlopen(f"{base_url}/api/customer-brief", timeout=5) as response:
            customer_brief = json.loads(response.read().decode("utf-8"))
            print(
                "customer_brief_api="
                f"{response.status} candidate={customer_brief['candidate']} "
                f"briefChars={len(customer_brief['brief'])}"
            )

        request = Request(
            f"{base_url}/api/customer-brief",
            data=frontend_state,
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        with urlopen(request, timeout=5) as response:
            customer_brief_post = json.loads(response.read().decode("utf-8"))
            print(
                "customer_brief_post_api="
                f"{response.status} candidate={customer_brief_post['candidate']} "
                f"production={customer_brief_post['decisionPack']['businessCase']['assumptions']['production']}"
            )

        with urlopen(f"{base_url}/api/design-spec", timeout=5) as response:
            design_spec = json.loads(response.read().decode("utf-8"))
            print(
                "design_spec_api="
                f"{response.status} file={design_spec['file']} "
                f"product={design_spec['spec']['product']}"
            )

        with urlopen(f"{base_url}/controllable_flux_motor_kb.html", timeout=5) as response:
            page = response.read().decode("utf-8")
            frontend_paths = schema["frontendRequiredPaths"]
            missing_frontend_paths = [path for path in frontend_paths if path not in page]
            has_session_snapshot_fetch = 'fetch("/api/session-snapshot"' in page
            has_session_snapshot_button = 'id="save-session-snapshot"' in page
            print(f"html={response.status} bytes={len(page.encode('utf-8'))}")

        if missing_frontend_paths:
            raise RuntimeError(
                f"frontend fetch contract missing paths: {missing_frontend_paths}"
            )
        print("frontend_fetch_contract=ok")
        print(f"frontend_fetch_contract=endpoints={len(frontend_paths)}")
        if not has_session_snapshot_fetch or not has_session_snapshot_button:
            raise RuntimeError("frontend session snapshot contract missing")
        print("frontend_session_snapshot_contract=ok")
        return 0
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def find_browser_executable() -> Path:
    for candidate in BROWSER_CANDIDATES:
        if candidate.exists():
            return candidate
    raise FileNotFoundError("Chrome or Edge executable was not found")


def _smoke_result_text(dom: str) -> str:
    match = re.search(r'<pre id="result">(?P<result>.*?)</pre>', dom, re.S)
    if match is None:
        raise RuntimeError("browser smoke result element not found")
    return match.group("result")


def _free_local_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _json_request(url: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"} if data is not None else {}
    request = __import__("urllib.request").request.Request(url, data=data, headers=headers)
    with urlopen(request, timeout=5) as response:
        return json.loads(response.read().decode("utf-8"))


def _run_headless_result_page(browser: Path, page_url: str, timeout_s: float = 20.0) -> str:
    debug_port = _free_local_port()
    with tempfile.TemporaryDirectory(prefix="tesla-moto-browser-") as user_data_dir:
        process = subprocess.Popen(
            [
                str(browser),
                "--headless=new",
                "--disable-gpu",
                "--no-first-run",
                "--disable-background-networking",
                "--remote-allow-origins=*",
                f"--user-data-dir={user_data_dir}",
                f"--remote-debugging-port={debug_port}",
                page_url,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        try:
            deadline = time.time() + timeout_s
            websocket_url = None
            while time.time() < deadline and websocket_url is None:
                try:
                    tabs = _json_request(f"http://127.0.0.1:{debug_port}/json")
                    for tab in tabs:
                        if tab.get("url") == page_url:
                            websocket_url = tab["webSocketDebuggerUrl"]
                            break
                except (URLError, ConnectionError, TimeoutError, OSError):
                    pass
                if websocket_url is None:
                    time.sleep(0.1)
            if websocket_url is None:
                raise RuntimeError("headless browser debugging endpoint not ready")

            import websocket  # type: ignore

            ws = websocket.create_connection(websocket_url, timeout=5)
            try:
                message_id = 0

                def call(method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
                    nonlocal message_id
                    message_id += 1
                    ws.send(json.dumps({"id": message_id, "method": method, "params": params or {}}))
                    while True:
                        message = json.loads(ws.recv())
                        if message.get("id") == message_id:
                            if "error" in message:
                                raise RuntimeError(message["error"])
                            return message.get("result", {})

                call("Runtime.enable")
                expression = "document.getElementById('result')?.textContent || ''"
                while time.time() < deadline:
                    result = call("Runtime.evaluate", {"expression": expression, "returnByValue": True})
                    value = result.get("result", {}).get("value", "")
                    if value and value != "pending":
                        return value
                    time.sleep(0.1)
                raise RuntimeError("headless browser smoke result timed out")
            finally:
                ws.close()
        finally:
            process.terminate()
            try:
                process.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.communicate(timeout=5)


def _with_headless_tab(browser: Path, page_url: str, callback, timeout_s: float = 20.0) -> Any:
    debug_port = _free_local_port()
    with tempfile.TemporaryDirectory(prefix="tesla-moto-browser-") as user_data_dir:
        process = subprocess.Popen(
            [
                str(browser),
                "--headless=new",
                "--disable-gpu",
                "--no-first-run",
                "--disable-background-networking",
                "--remote-allow-origins=*",
                f"--user-data-dir={user_data_dir}",
                f"--remote-debugging-port={debug_port}",
                page_url,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        try:
            deadline = time.time() + timeout_s
            websocket_url = None
            while time.time() < deadline and websocket_url is None:
                try:
                    tabs = _json_request(f"http://127.0.0.1:{debug_port}/json")
                    for tab in tabs:
                        if tab.get("url") == page_url:
                            websocket_url = tab["webSocketDebuggerUrl"]
                            break
                except (URLError, ConnectionError, TimeoutError, OSError):
                    pass
                if websocket_url is None:
                    time.sleep(0.1)
            if websocket_url is None:
                raise RuntimeError("headless browser debugging endpoint not ready")
            import websocket  # type: ignore

            ws = websocket.create_connection(websocket_url, timeout=5)
            try:
                message_id = 0

                def call(method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
                    nonlocal message_id
                    message_id += 1
                    ws.send(json.dumps({"id": message_id, "method": method, "params": params or {}}))
                    while True:
                        message = json.loads(ws.recv())
                        if message.get("id") == message_id:
                            if "error" in message:
                                raise RuntimeError(message["error"])
                            return message.get("result", {})

                call("Runtime.enable")
                call("Page.enable")
                return callback(call, deadline)
            finally:
                ws.close()
        finally:
            process.terminate()
            try:
                process.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.communicate(timeout=5)


def _assert_nonblank_png(path: Path, expected_size: tuple[int, int]) -> None:
    with Image.open(path) as image:
        if image.size != expected_size:
            raise RuntimeError(f"unexpected screenshot size {path}: {image.size}")
        rgb = image.convert("RGB")
        step_x = max(1, image.size[0] // 32)
        step_y = max(1, image.size[1] // 32)
        samples = [rgb.getpixel((x, y)) for x in range(0, image.size[0], step_x) for y in range(0, image.size[1], step_y)]
        if len(set(samples)) < 8:
            raise RuntimeError(f"screenshot appears blank: {path}")


def _capture_dashboard_screenshot(browser: Path, page_url: str, output: Path, width: int, height: int) -> None:
    def callback(call, deadline):
        call(
            "Emulation.setDeviceMetricsOverride",
            {
                "width": width,
                "height": height,
                "deviceScaleFactor": 1,
                "mobile": width < 700,
            },
        )
        call("Page.navigate", {"url": page_url})
        expression = """
        (() => {
          const status = document.getElementById('api-status');
          const health = document.getElementById('health-grid');
          const winner = document.getElementById('winner-name');
          return Boolean(
            status && !status.classList.contains('offline') &&
            health && health.children.length > 0 &&
            winner && winner.textContent.trim().length > 0
          );
        })()
        """
        while time.time() < deadline:
            result = call("Runtime.evaluate", {"expression": expression, "returnByValue": True})
            if result.get("result", {}).get("value") is True:
                break
            time.sleep(0.1)
        else:
            raise RuntimeError("dashboard did not connect before screenshot")
        screenshot = call("Page.captureScreenshot", {"format": "png", "fromSurface": True})
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(base64.b64decode(screenshot["data"]))
        _assert_nonblank_png(output, (width, height))

    _with_headless_tab(browser, page_url, callback, timeout_s=25.0)


def run_browser_smoke_check(host: str = "127.0.0.1") -> int:
    browser = find_browser_executable()
    server = ThreadingHTTPServer((host, 0), QuietDashboardRequestHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://{host}:{server.server_port}"
    page_url = f"{base_url}/controllable_flux_motor_kb.html"
    try:
        with tempfile.TemporaryDirectory(prefix="tesla-moto-browser-") as user_data_dir:
            result = subprocess.run(
                [
                    str(browser),
                    "--headless=new",
                    "--disable-gpu",
                    "--no-first-run",
                    "--disable-background-networking",
                    f"--user-data-dir={user_data_dir}",
                    "--virtual-time-budget=6000",
                    "--dump-dom",
                    page_url,
                ],
                capture_output=True,
                encoding="utf-8",
                errors="replace",
                check=False,
                timeout=20,
            )
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or "headless browser failed")
        dom = result.stdout
        checks = {
            "connected": "api-status" in dom and "接口已连接" in dom,
            "health": "health-grid" in dom and "/api/health" in dom,
            "dashboard": "hybrid_excitation_if_plus_20" in dom,
        }
        if not all(checks.values()):
            raise RuntimeError(f"browser smoke failed checks: {checks}")
        print(f"browser_page=ok url={page_url}")
        print("api_status=connected")
        print("health_panel=runtime-counts")
        return 0
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def run_browser_interaction_smoke_check(host: str = "127.0.0.1") -> int:
    browser = find_browser_executable()
    server = ThreadingHTTPServer((host, 0), QuietDashboardRequestHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    page_url = f"http://{host}:{server.server_port}/__browser_interaction_smoke"
    try:
        dom = _run_headless_result_page(browser, page_url, timeout_s=25.0)
        required = [
            "browser_interaction=ok",
            "candidate_click=ok",
            "weight_input=ok",
            "scenario_restore=ok",
            "scenario_clear=ok",
            "api_sync_log=ok",
            "session_snapshot=ok",
            "session_snapshot_metadata=ok",
            "session_snapshot_clear=ok",
            "refresh_click=ok",
            "customer_brief_export=ok",
            "decision_pack_export=ok",
            "decision_pack_candidate=winding_series_torque",
            "decision_pack_weight_urban=75",
            "decision_pack_production=120000",
            "decision_pack_energy_price=1.25",
            "decision_pack_transport=POST",
            "clipboard_source=backend-api",
            "clipboard_business_case=ok",
            "design_spec_runtime_fetch=ok",
            "design_spec_export=ok",
            "design_spec_file=reports/open_design_dashboard_spec.json",
            "design_spec_clipboard_product=customer_dashboard",
        ]
        missing = [item for item in required if item not in dom]
        if missing:
            raise RuntimeError(
                f"browser interaction smoke missing {missing}; result: {dom}"
            )
        print("browser_interaction=ok")
        print("candidate_click=ok")
        print("weight_input=ok")
        print("scenario_restore=ok")
        print("scenario_clear=ok")
        print("api_sync_log=ok")
        print("session_snapshot=ok")
        print("session_snapshot_metadata=ok")
        print("session_snapshot_clear=ok")
        print("refresh_click=ok")
        print("customer_brief_export=ok")
        print("decision_pack_export=ok")
        print("decision_pack_candidate=winding_series_torque")
        print("decision_pack_weight_urban=75")
        print("decision_pack_production=120000")
        print("decision_pack_energy_price=1.25")
        print("decision_pack_transport=POST")
        print("clipboard_source=backend-api")
        print("clipboard_business_case=ok")
        print("design_spec_runtime_fetch=ok")
        print("design_spec_export=ok")
        print("design_spec_file=reports/open_design_dashboard_spec.json")
        print("design_spec_clipboard_product=customer_dashboard")
        return 0
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def run_browser_error_smoke_check(host: str = "127.0.0.1") -> int:
    browser = find_browser_executable()
    server = ThreadingHTTPServer((host, 0), QuietDashboardRequestHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    page_url = f"http://{host}:{server.server_port}/__browser_error_smoke"
    try:
        dom = _run_headless_result_page(browser, page_url, timeout_s=25.0)
        required = [
            "browser_error=ok",
            "dashboard_fallback=ok",
            "health_fallback=ok",
            "decision_pack_fallback=ok",
            "fallback_clipboard_source=local",
        ]
        missing = [item for item in required if item not in dom]
        if missing:
            raise RuntimeError(f"browser error smoke missing {missing}; result: {dom}")
        for item in required:
            print(item)
        return 0
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def run_browser_contract_smoke_check(host: str = "127.0.0.1") -> int:
    browser = find_browser_executable()
    server = ThreadingHTTPServer((host, 0), QuietDashboardRequestHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    page_url = f"http://{host}:{server.server_port}/__browser_contract_smoke"
    try:
        dom = _run_headless_result_page(browser, page_url, timeout_s=25.0)
        required = [
            "browser_contract=ok",
            "dashboard_payload_schema_rejected=ok",
            "health_payload_schema_rejected=ok",
            "schema_payload_schema_rejected=ok",
            "decision_pack_contract_fallback=ok",
            "customer_brief_contract_fallback=ok",
            "design_spec_contract_fallback=ok",
            "scenario_state_schema_rejected=ok",
            "session_snapshot_save_schema_rejected=ok",
            "session_snapshot_clear_schema_rejected=ok",
            "session_snapshot_schema_rejected=ok",
            "contract_clipboard_source=local",
        ]
        missing = [item for item in required if item not in dom]
        if missing:
            raise RuntimeError(f"browser contract smoke missing {missing}; result: {dom}")
        for item in required:
            print(item)
        return 0
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def run_browser_screenshot_smoke_check(host: str = "127.0.0.1") -> int:
    browser = find_browser_executable()
    server = ThreadingHTTPServer((host, 0), QuietDashboardRequestHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    page_url = f"http://{host}:{server.server_port}/controllable_flux_motor_kb.html"
    desktop = PROJECT_ROOT / "reports" / "dashboard-smoke-desktop.png"
    mobile = PROJECT_ROOT / "reports" / "dashboard-smoke-mobile.png"
    try:
        _capture_dashboard_screenshot(browser, page_url, desktop, 1440, 1100)
        _capture_dashboard_screenshot(browser, page_url, mobile, 390, 900)
        print(f"screenshot_desktop=ok path={desktop}")
        print(f"screenshot_mobile=ok path={mobile}")
        print("png_pixels=nonblank")
        return 0
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve dashboard HTML and API.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument(
        "--smoke",
        action="store_true",
        help="Run a one-shot frontend/backend HTTP integration smoke check.",
    )
    parser.add_argument(
        "--browser-smoke",
        action="store_true",
        help="Run a one-shot headless browser integration smoke check.",
    )
    parser.add_argument(
        "--browser-interaction-smoke",
        action="store_true",
        help="Run a one-shot headless browser interaction smoke check.",
    )
    parser.add_argument(
        "--browser-error-smoke",
        action="store_true",
        help="Run a one-shot headless browser error-state smoke check.",
    )
    parser.add_argument(
        "--browser-contract-smoke",
        action="store_true",
        help="Run a one-shot headless browser API schema-contract smoke check.",
    )
    parser.add_argument(
        "--browser-screenshot-smoke",
        action="store_true",
        help="Run a one-shot headless browser screenshot smoke check.",
    )
    args = parser.parse_args()
    if args.smoke:
        raise SystemExit(run_smoke_check(args.host))
    if args.browser_smoke:
        raise SystemExit(run_browser_smoke_check(args.host))
    if args.browser_interaction_smoke:
        raise SystemExit(run_browser_interaction_smoke_check(args.host))
    if args.browser_error_smoke:
        raise SystemExit(run_browser_error_smoke_check(args.host))
    if args.browser_contract_smoke:
        raise SystemExit(run_browser_contract_smoke_check(args.host))
    if args.browser_screenshot_smoke:
        raise SystemExit(run_browser_screenshot_smoke_check(args.host))
    run_server(args.host, args.port)


if __name__ == "__main__":
    main()
