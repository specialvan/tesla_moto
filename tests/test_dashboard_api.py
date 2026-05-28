from pathlib import Path
import json
import subprocess
import sys
from http.server import ThreadingHTTPServer
from threading import Thread
from urllib.error import HTTPError
from urllib.request import urlopen

from sim.dashboard_api import (
    DashboardRequestHandler,
    ROI_ENERGY_CONVERSION_KWH_PER_100KM_PER_KW,
    _new_dashboard_server,
    build_api_schema_payload,
    build_dashboard_payload,
)


ROOT = Path(__file__).resolve().parents[1]


def test_dashboard_payload_exposes_frontend_contract():
    payload = build_dashboard_payload(ROOT)

    assert payload["meta"]["title"] == "可控磁通量电机客户数据看板"
    assert payload["meta"]["source"] == "backend-api"
    assert payload["maturity"] == {
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
    assert len(payload["paretoFront"]) == 7
    assert len(payload["cycleRows"]) == 21
    assert len(payload["ironLossRows"]) >= 8
    assert any(row["freqOutOfRange"] for row in payload["ironLossRows"])
    assert len(payload["algorithmRows"]) == 6
    assert len(payload["deliveryItems"]) == 4


def test_dashboard_schema_object_keys_only_describe_object_rows():
    payload = build_dashboard_payload(ROOT)
    endpoints = {item["path"]: item for item in build_api_schema_payload()["endpoints"]}

    for collection, keys in endpoints["/api/dashboard"]["responseObjectKeys"].items():
        value = payload[collection]
        if isinstance(value, list):
            first_row = value[0]
            assert isinstance(first_row, dict), collection
            assert set(keys).issubset(first_row.keys())
        else:
            assert isinstance(value, dict), collection
            assert set(keys).issubset(value.keys())


def test_dashboard_payload_uses_experiment_files():
    payload = build_dashboard_payload(ROOT)

    winner = payload["paretoFront"][0]
    assert winner["candidate"] == "hybrid_excitation_if_plus_20"
    assert winner["label"] == "混合励磁 +20"
    assert winner["loss"] == 4468.317

    launch_rows = [
        row for row in payload["cycleRows"] if row["cycle"] == "launch_peak_torque"
    ]
    assert len(launch_rows) == 7
    assert any(
        row["candidate"] == "variable_flux_psi70" and row["feasibleWeight"] == 0
        for row in launch_rows
    )


def test_dashboard_http_server_serves_api_and_page_from_project_root(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    server = ThreadingHTTPServer(("127.0.0.1", 0), DashboardRequestHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        base_url = f"http://127.0.0.1:{server.server_port}"
        with urlopen(f"{base_url}/api/dashboard", timeout=5) as response:
            assert response.status == 200
            assert response.headers["Content-Type"] == "application/json; charset=utf-8"
            body = response.read().decode("utf-8")

        assert "hybrid_excitation_if_plus_20" in body
        assert "backend-api" in body

        with urlopen(f"{base_url}/controllable_flux_motor_kb.html", timeout=5) as response:
            assert response.status == 200
            page = response.read().decode("utf-8")

        assert 'id="app-dashboard"' in page
        assert 'fetch("/api/dashboard"' in page
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_dashboard_http_server_exposes_runtime_health_for_frontend_integration():
    server = ThreadingHTTPServer(("127.0.0.1", 0), DashboardRequestHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        with urlopen(
            f"http://127.0.0.1:{server.server_port}/api/health", timeout=5
        ) as response:
            assert response.status == 200
            assert response.headers["Content-Type"] == "application/json; charset=utf-8"
            payload = json.loads(response.read().decode("utf-8"))

        assert payload == {
            "status": "ok",
            "source": "backend-api",
            "schemaVersion": 1,
            "page": "controllable_flux_motor_kb.html",
            "pageAvailable": True,
            "counts": {
                "paretoFront": 7,
                "cycleRows": 21,
                "ironLossRows": len(build_dashboard_payload(ROOT)["ironLossRows"]),
                "algorithmRows": 6,
                "deliveryItems": 4,
            },
        }
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_dashboard_http_server_exposes_api_schema_contract():
    server = ThreadingHTTPServer(("127.0.0.1", 0), DashboardRequestHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        with urlopen(f"http://127.0.0.1:{server.server_port}/api/schema", timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))

        assert response.status == 200
        assert response.headers["Content-Type"] == "application/json; charset=utf-8"
        assert payload["source"] == "backend-api"
        assert payload["schemaVersion"] == 1
        endpoints = {item["path"]: item for item in payload["endpoints"]}
        assert set(endpoints) == {
            "/api/dashboard",
            "/api/health",
            "/api/schema",
            "/api/scenario-state",
            "/api/decision-pack",
            "/api/session-snapshot",
            "/api/customer-brief",
            "/api/design-spec",
        }
        assert endpoints["/api/dashboard"]["methods"] == ["GET"]
        assert endpoints["/api/dashboard"]["responseObjectKeys"] == {
            "maturity": [
                "engineering_validated",
                "physics_model_validated",
                "production_release_allowed",
                "production_drawing_ready",
                "manufacturing_release_ready",
                "model_maturity",
                "required_evidence",
                "not_allowed_claims",
            ],
            "paretoFront": ["candidate", "label", "meanScore", "feasible", "loss", "family", "color"],
            "cycleRows": ["candidate", "cycle", "feasibleWeight", "copperLoss", "score"],
            "ironLossRows": ["speed", "targetFeasible", "ironLoss", "efficiency", "freqOutOfRange"],
        }
        assert endpoints["/api/dashboard"]["responseTupleLengths"] == {
            "algorithmRows": 4,
            "deliveryItems": 2,
        }
        assert endpoints["/api/health"]["methods"] == ["GET"]
        assert endpoints["/api/health"]["responseObjectKeys"] == {
            "counts": [
                "paretoFront",
                "cycleRows",
                "ironLossRows",
                "algorithmRows",
                "deliveryItems",
            ]
        }
        assert endpoints["/api/schema"]["methods"] == ["GET"]
        assert endpoints["/api/scenario-state"]["methods"] == ["GET", "DELETE"]
        assert endpoints["/api/scenario-state"]["responseKeys"] == [
            "source",
            "schemaVersion",
            "stateAvailable",
            "stateSource",
            "state",
        ]
        assert endpoints["/api/scenario-state"]["responseObjectKeys"] == {
            "state": ["candidate", "businessAssumptions", "weights"]
        }
        assert endpoints["/api/decision-pack"]["methods"] == ["GET", "POST"]
        assert endpoints["/api/session-snapshot"]["methods"] == ["GET", "POST", "DELETE"]
        assert endpoints["/api/session-snapshot"]["requestStateKeys"] == [
            "candidate",
            "businessAssumptions",
            "weights",
            "decisionPack",
            "apiSyncLog",
        ]
        assert endpoints["/api/session-snapshot"]["responseKeys"] == [
            "source",
            "schemaVersion",
            "snapshotAvailable",
            "snapshot",
            "metadata",
        ]
        assert endpoints["/api/session-snapshot"]["metadataKeys"] == [
            "snapshotId",
            "createdAt",
            "updatedAt",
            "source",
            "schemaVersion",
            "apiContractVersion",
        ]
        assert endpoints["/api/session-snapshot"]["responseObjectKeys"] == {
            "snapshot": [
                "candidate",
                "businessAssumptions",
                "weights",
                "decisionPack",
                "apiSyncLog",
                "metadata",
            ]
        }
        assert endpoints["/api/customer-brief"]["methods"] == ["GET", "POST"]
        assert endpoints["/api/customer-brief"]["requestStateKeys"] == [
            "candidate",
            "businessAssumptions",
            "weights",
        ]
        assert endpoints["/api/customer-brief"]["responseKeys"] == [
            "source",
            "schemaVersion",
            "candidate",
            "brief",
            "decisionPack",
        ]
        assert endpoints["/api/customer-brief"]["responseObjectKeys"] == {
            "decisionPack": [
                "source",
                "schemaVersion",
                "selected",
                "gains",
                "businessCase",
                "weights",
                "ranking",
            ]
        }
        assert endpoints["/api/design-spec"]["methods"] == ["GET"]
        assert endpoints["/api/design-spec"]["responseKeys"] == [
            "source",
            "schemaVersion",
            "file",
            "spec",
        ]
        assert endpoints["/api/design-spec"]["responseObjectKeys"] == {
            "spec": [
                "name",
                "product",
                "page",
                "design_system",
                "audience",
                "tokens",
                "components",
            ]
        }
        assert "candidate" in endpoints["/api/decision-pack"]["requestStateKeys"]
        assert endpoints["/api/decision-pack"]["getQueryKeys"] == [
            "candidate",
            "production",
            "mileage",
            "energyPrice",
            "validationInvestment",
            "urban_low_speed",
            "highway_high_speed",
            "launch_peak_torque",
        ]
        assert endpoints["/api/decision-pack"]["postJson"] == {
            "requiredKeys": ["candidate", "businessAssumptions", "weights"],
            "businessAssumptionKeys": ["production", "mileage", "energyPrice", "validationInvestment"],
            "weightKeys": ["urban_low_speed", "highway_high_speed", "launch_peak_torque"],
        }
        assert endpoints["/api/decision-pack"]["responseObjectKeys"] == {
            "selected": ["candidate", "label", "family", "meanScore", "weightedCopperLossW", "feasible"],
            "gains": ["scoreGainPercent", "copperLossChangePercent", "feasibleCycles", "confidencePercent"],
            "businessCase": [
                "assumptions",
                "conversionKwhPer100kmPerKw",
                "perVehicleAnnualSavingYuan",
                "fleetAnnualSavingYuan",
                "paybackMonths",
            ],
            "weights": ["urban_low_speed", "highway_high_speed", "launch_peak_torque"],
            "ranking": ["candidate", "label", "family", "simulatedScore", "simulatedFeasible", "rank"],
            "maturity": [
                "engineering_validated",
                "physics_model_validated",
                "production_release_allowed",
                "production_drawing_ready",
                "manufacturing_release_ready",
                "model_maturity",
                "required_evidence",
                "not_allowed_claims",
            ],
        }
        assert payload["frontendRequiredPaths"] == [
            "/api/dashboard",
            "/api/health",
            "/api/schema",
            "/api/scenario-state",
            "/api/decision-pack",
            "/api/session-snapshot",
            "/api/customer-brief",
            "/api/design-spec",
        ]
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_dashboard_api_schema_report_matches_runtime_contract():
    schema_path = ROOT / "reports" / "dashboard-api-schema.json"

    assert schema_path.exists()
    assert json.loads(schema_path.read_text(encoding="utf-8")) == build_api_schema_payload()


def test_dashboard_api_responses_include_dev_origin_headers():
    server = ThreadingHTTPServer(("127.0.0.1", 0), DashboardRequestHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        with urlopen(f"http://127.0.0.1:{server.server_port}/api/dashboard", timeout=5) as response:
            response.read()

        assert response.headers["Access-Control-Allow-Origin"] == "http://127.0.0.1"
        assert response.headers["Access-Control-Allow-Methods"] == "GET, POST, DELETE, OPTIONS"
        assert response.headers["Access-Control-Allow-Headers"] == "Accept, Content-Type"
        assert response.headers["Cache-Control"] == "no-store"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_dashboard_api_options_preflight_exposes_frontend_contract():
    import urllib.request

    server = ThreadingHTTPServer(("127.0.0.1", 0), DashboardRequestHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        request = urllib.request.Request(
            f"http://127.0.0.1:{server.server_port}/api/decision-pack",
            method="OPTIONS",
        )
        with urlopen(request, timeout=5) as response:
            body = response.read()

        assert response.status == 204
        assert body == b""
        assert response.headers["Access-Control-Allow-Origin"] == "http://127.0.0.1"
        assert response.headers["Access-Control-Allow-Methods"] == "GET, POST, DELETE, OPTIONS"
        assert response.headers["Access-Control-Allow-Headers"] == "Accept, Content-Type"
        assert response.headers["Cache-Control"] == "no-store"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_dashboard_api_rejects_oversized_post_body():
    import urllib.request

    server = ThreadingHTTPServer(("127.0.0.1", 0), DashboardRequestHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        request = urllib.request.Request(
            f"http://127.0.0.1:{server.server_port}/api/decision-pack",
            data=(b"{" + b" " * 70000 + b"}"),
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        try:
            with urlopen(request, timeout=5):
                raise AssertionError("expected HTTP 413")
        except HTTPError as error:
            body = error.read().decode("utf-8")
            assert error.code == 413
            assert "request body too large" in body
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_dashboard_api_rejects_invalid_content_length():
    import http.client

    server = ThreadingHTTPServer(("127.0.0.1", 0), DashboardRequestHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        conn = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
        conn.request(
            "POST",
            "/api/decision-pack",
            body=b"{}",
            headers={"Content-Type": "application/json", "Content-Length": "invalid"},
        )
        response = conn.getresponse()
        body = response.read().decode("utf-8")
        conn.close()

        assert response.status == 400
        assert "Content-Length must be an integer" in body
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_dashboard_http_server_serves_backend_decision_pack_export():
    server = ThreadingHTTPServer(("127.0.0.1", 0), DashboardRequestHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        with urlopen(
            f"http://127.0.0.1:{server.server_port}/api/decision-pack", timeout=5
        ) as response:
            assert response.status == 200
            assert response.headers["Content-Type"] == "application/json; charset=utf-8"
            payload = json.loads(response.read().decode("utf-8"))

        assert payload["source"] == "backend-api"
        assert payload["schemaVersion"] == 1
        assert payload["dashboard"] == "controllable_flux_motor_kb.html"
        assert payload["selected"]["candidate"] == "hybrid_excitation_if_plus_20"
        assert payload["selected"]["weightedCopperLossW"] == 4468.317
        assert payload["gains"]["feasibleCycles"] == 3
        assert payload["businessCase"]["assumptions"]["production"] == 50000
        assert ROI_ENERGY_CONVERSION_KWH_PER_100KM_PER_KW == 0.12
        assert payload["businessCase"]["conversionKwhPer100kmPerKw"] == 0.12
        assert payload["businessCase"]["perVehicleAnnualSavingYuan"] == 4.91
        assert payload["businessCase"]["fleetAnnualSavingYuan"] == 245442.96
        assert payload["businessCase"]["paybackMonths"] == 88.0
        assert payload["maturity"]["engineering_validated"] is False
        assert payload["maturity"]["production_release_allowed"] is False
        assert "engineering release" in payload["maturity"]["not_allowed_claims"]
        assert len(payload["ranking"]) == 5
        assert payload["ranking"][0]["candidate"] == "hybrid_excitation_if_plus_20"
        assert "EXP-010 weighted efficiency Pareto" in payload["evidence"]
        assert "量产实机收益承诺" in payload["disclaimer"]
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_dashboard_decision_pack_uses_query_params_for_selected_scenario():
    server = ThreadingHTTPServer(("127.0.0.1", 0), DashboardRequestHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        query = (
            "candidate=baseline&production=10000&mileage=30000&energyPrice=1.5"
            "&validationInvestment=60&urban_low_speed=10&highway_high_speed=80"
            "&launch_peak_torque=10"
        )
        with urlopen(
            f"http://127.0.0.1:{server.server_port}/api/decision-pack?{query}",
            timeout=5,
        ) as response:
            assert response.status == 200
            payload = json.loads(response.read().decode("utf-8"))

        assert payload["selected"]["candidate"] == "baseline"
        assert payload["businessCase"]["assumptions"] == {
            "production": 10000,
            "mileage": 30000,
            "energyPrice": 1.5,
            "validationInvestment": 60,
        }
        assert payload["weights"] == {
            "urban_low_speed": 10.0,
            "highway_high_speed": 80.0,
            "launch_peak_torque": 10.0,
        }
        assert payload["businessCase"]["fleetAnnualSavingYuan"] == 0
        assert payload["businessCase"]["paybackMonths"] is None
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_dashboard_decision_pack_rejects_out_of_bounds_query_values():
    server = ThreadingHTTPServer(("127.0.0.1", 0), DashboardRequestHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        try:
            with urlopen(
                f"http://127.0.0.1:{server.server_port}/api/decision-pack?production=-1",
                timeout=5,
            ):
                raise AssertionError("expected HTTP 400")
        except HTTPError as error:
            body = error.read().decode("utf-8")
            assert error.code == 400
            assert "production must be between 5000 and 200000" in body

        try:
            with urlopen(
                f"http://127.0.0.1:{server.server_port}/api/decision-pack?urban_low_speed=-1",
                timeout=5,
            ):
                raise AssertionError("expected HTTP 400")
        except HTTPError as error:
            body = error.read().decode("utf-8")
            assert error.code == 400
            assert "urban_low_speed must be between 0 and 100" in body
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_dashboard_customer_brief_uses_posted_frontend_state():
    import urllib.request

    server = ThreadingHTTPServer(("127.0.0.1", 0), DashboardRequestHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        body = json.dumps(
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
        request = urllib.request.Request(
            f"http://127.0.0.1:{server.server_port}/api/customer-brief",
            data=body,
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        with urlopen(request, timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))

        assert response.status == 200
        assert payload["source"] == "backend-api"
        assert payload["schemaVersion"] == 1
        assert payload["candidate"] == "winding_series_torque"
        assert payload["decisionPack"]["selected"]["candidate"] == "winding_series_torque"
        assert payload["decisionPack"]["businessCase"]["assumptions"]["production"] == 120000
        assert "winding_series_torque" in payload["brief"]
        assert "120,000" in payload["brief"]
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_dashboard_design_spec_api_serves_opendesign_report():
    server = ThreadingHTTPServer(("127.0.0.1", 0), DashboardRequestHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        with urlopen(
            f"http://127.0.0.1:{server.server_port}/api/design-spec",
            timeout=5,
        ) as response:
            payload = json.loads(response.read().decode("utf-8"))

        assert response.status == 200
        assert payload["source"] == "backend-api"
        assert payload["schemaVersion"] == 1
        assert payload["file"] == "reports/open_design_dashboard_spec.json"
        assert payload["spec"]["name"] == "open_design_dashboard_spec"
        assert payload["spec"]["product"] == "customer_dashboard"
        assert payload["spec"]["visual_direction"]["tone"] == "premium black-gold engineering dashboard"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_dashboard_decision_pack_accepts_posted_frontend_state():
    import urllib.request

    server = ThreadingHTTPServer(("127.0.0.1", 0), DashboardRequestHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        body = json.dumps(
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
        request = urllib.request.Request(
            f"http://127.0.0.1:{server.server_port}/api/decision-pack",
            data=body,
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        with urlopen(request, timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))

        assert response.status == 200
        assert response.headers["Content-Type"] == "application/json; charset=utf-8"
        assert payload["source"] == "backend-api"
        assert payload["selected"]["candidate"] == "winding_series_torque"
        assert payload["businessCase"]["assumptions"] == {
            "production": 120000,
            "mileage": 22000,
            "energyPrice": 1.25,
            "validationInvestment": 240,
        }
        assert payload["weights"] == {
            "urban_low_speed": 75.0,
            "highway_high_speed": 15.0,
            "launch_peak_torque": 10.0,
        }
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_dashboard_decision_pack_rejects_out_of_bounds_posted_state():
    import urllib.request

    server = ThreadingHTTPServer(("127.0.0.1", 0), DashboardRequestHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        body = json.dumps(
            {
                "candidate": "winding_series_torque",
                "businessAssumptions": {"validationInvestment": -20},
                "weights": {"urban_low_speed": 40},
            }
        ).encode("utf-8")
        request = urllib.request.Request(
            f"http://127.0.0.1:{server.server_port}/api/decision-pack",
            data=body,
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        try:
            with urlopen(request, timeout=5):
                raise AssertionError("expected HTTP 400")
        except HTTPError as error:
            body_text = error.read().decode("utf-8")
            assert error.code == 400
            assert "validationInvestment must be between 20 and 1000" in body_text
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_dashboard_session_snapshot_accepts_posted_frontend_state_and_roundtrips():
    import urllib.request

    server = ThreadingHTTPServer(("127.0.0.1", 0), DashboardRequestHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    snapshot = {
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
        "decisionPack": {
            "source": "backend-api",
            "selected": {"candidate": "winding_series_torque"},
            "businessCase": {"assumptions": {"production": 120000}},
        },
        "apiSyncLog": {
            "/api/dashboard": {"ok": True, "message": "loaded"},
            "/api/decision-pack": {"ok": True, "message": "POST"},
        },
    }
    try:
        request = urllib.request.Request(
            f"http://127.0.0.1:{server.server_port}/api/session-snapshot",
            data=json.dumps(snapshot).encode("utf-8"),
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        with urlopen(request, timeout=5) as response:
            post_payload = json.loads(response.read().decode("utf-8"))

        assert response.status == 200
        assert post_payload["source"] == "backend-api"
        assert post_payload["schemaVersion"] == 1
        assert post_payload["snapshotAvailable"] is True
        assert post_payload["snapshot"]["candidate"] == "winding_series_torque"
        assert post_payload["snapshot"]["decisionPack"]["source"] == "backend-api"
        assert post_payload["snapshot"]["apiSyncLog"]["/api/decision-pack"]["message"] == "POST"
        assert post_payload["metadata"]["source"] == "backend-api"
        assert post_payload["metadata"]["schemaVersion"] == 1
        assert post_payload["metadata"]["apiContractVersion"] == 1
        assert post_payload["metadata"]["snapshotId"].startswith("dashboard-session-")
        assert post_payload["metadata"]["createdAt"].endswith("Z")
        assert post_payload["metadata"]["updatedAt"] == post_payload["metadata"]["createdAt"]
        assert post_payload["snapshot"]["metadata"] == post_payload["metadata"]

        with urlopen(
            f"http://127.0.0.1:{server.server_port}/api/session-snapshot",
            timeout=5,
        ) as response:
            get_payload = json.loads(response.read().decode("utf-8"))

        assert get_payload == post_payload
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_dashboard_session_snapshot_rejects_unknown_candidate():
    import urllib.request

    server = ThreadingHTTPServer(("127.0.0.1", 0), DashboardRequestHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        request = urllib.request.Request(
            f"http://127.0.0.1:{server.server_port}/api/session-snapshot",
            data=json.dumps({"candidate": "missing"}).encode("utf-8"),
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        try:
            with urlopen(request, timeout=5):
                raise AssertionError("expected HTTP 400")
        except HTTPError as error:
            body = error.read().decode("utf-8")
            assert error.code == 400
            assert '"error": "dashboard_request_invalid"' in body
            assert "unknown candidate: missing" in body
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_dashboard_session_snapshot_can_restore_from_persistent_file(tmp_path):
    import urllib.request

    snapshot_path = tmp_path / "dashboard-session-snapshot.json"
    first_server = ThreadingHTTPServer(("127.0.0.1", 0), DashboardRequestHandler)
    first_server.dashboard_session_snapshot_path = snapshot_path
    first_thread = Thread(target=first_server.serve_forever, daemon=True)
    first_thread.start()

    snapshot = {
        "candidate": "winding_series_torque",
        "businessAssumptions": {"production": 120000, "energyPrice": 1.25},
        "weights": {"urban_low_speed": 75},
        "decisionPack": {
            "source": "backend-api",
            "selected": {"candidate": "winding_series_torque"},
        },
        "apiSyncLog": {"/api/decision-pack": {"ok": True, "message": "POST"}},
    }
    try:
        request = urllib.request.Request(
            f"http://127.0.0.1:{first_server.server_port}/api/session-snapshot",
            data=json.dumps(snapshot).encode("utf-8"),
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        with urlopen(request, timeout=5) as response:
            response.read()
    finally:
        first_server.shutdown()
        first_server.server_close()
        first_thread.join(timeout=5)

    assert snapshot_path.exists()

    second_server = ThreadingHTTPServer(("127.0.0.1", 0), DashboardRequestHandler)
    second_server.dashboard_session_snapshot_path = snapshot_path
    second_thread = Thread(target=second_server.serve_forever, daemon=True)
    second_thread.start()
    try:
        with urlopen(
            f"http://127.0.0.1:{second_server.server_port}/api/session-snapshot",
            timeout=5,
        ) as response:
            payload = json.loads(response.read().decode("utf-8"))

        assert response.status == 200
        assert payload["snapshotAvailable"] is True
        assert payload["snapshot"]["candidate"] == "winding_series_torque"
        assert payload["snapshot"]["businessAssumptions"]["production"] == 120000
        assert payload["snapshot"]["weights"]["urban_low_speed"] == 75.0
        assert payload["snapshot"]["apiSyncLog"]["/api/decision-pack"]["message"] == "POST"
        assert payload["metadata"]["snapshotId"].startswith("dashboard-session-")
        assert payload["metadata"] == payload["snapshot"]["metadata"]
    finally:
        second_server.shutdown()
        second_server.server_close()
        second_thread.join(timeout=5)


def test_dashboard_session_snapshot_ignores_invalid_persistent_file(tmp_path):
    snapshot_path = tmp_path / "dashboard-session-snapshot.json"
    snapshot_path.write_text(
        json.dumps({"candidate": "missing", "apiSyncLog": []}),
        encoding="utf-8",
    )
    server = ThreadingHTTPServer(("127.0.0.1", 0), DashboardRequestHandler)
    server.dashboard_session_snapshot_path = snapshot_path
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        with urlopen(
            f"http://127.0.0.1:{server.server_port}/api/session-snapshot",
            timeout=5,
        ) as response:
            payload = json.loads(response.read().decode("utf-8"))

        assert response.status == 200
        assert payload == {
            "source": "backend-api",
            "schemaVersion": 1,
            "snapshotAvailable": False,
            "snapshot": None,
            "metadata": None,
        }
        assert not snapshot_path.exists()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_dashboard_session_snapshot_delete_clears_memory_and_persisted_snapshot(tmp_path):
    import urllib.request

    snapshot_path = tmp_path / "dashboard-session-snapshot.json"
    server = ThreadingHTTPServer(("127.0.0.1", 0), DashboardRequestHandler)
    server.dashboard_session_snapshot_path = snapshot_path
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    snapshot = {
        "candidate": "winding_series_torque",
        "businessAssumptions": {"production": 120000},
        "weights": {"urban_low_speed": 75},
        "decisionPack": {"source": "backend-api", "selected": {"candidate": "winding_series_torque"}},
        "apiSyncLog": {"/api/session-snapshot": {"ok": True, "message": "saved"}},
    }
    try:
        post_request = urllib.request.Request(
            f"http://127.0.0.1:{server.server_port}/api/session-snapshot",
            data=json.dumps(snapshot).encode("utf-8"),
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        with urlopen(post_request, timeout=5) as response:
            response.read()

        assert snapshot_path.exists()

        delete_request = urllib.request.Request(
            f"http://127.0.0.1:{server.server_port}/api/session-snapshot",
            method="DELETE",
        )
        with urlopen(delete_request, timeout=5) as response:
            delete_payload = json.loads(response.read().decode("utf-8"))

        assert response.status == 200
        assert delete_payload == {
            "source": "backend-api",
            "schemaVersion": 1,
            "snapshotAvailable": False,
            "snapshot": None,
            "metadata": None,
        }
        assert not snapshot_path.exists()

        with urlopen(
            f"http://127.0.0.1:{server.server_port}/api/session-snapshot",
            timeout=5,
        ) as response:
            get_payload = json.loads(response.read().decode("utf-8"))

        assert get_payload == delete_payload
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_dashboard_server_helper_configures_persistent_session_snapshot(tmp_path):
    state_path = tmp_path / "dashboard-scenario-state.json"
    snapshot_path = tmp_path / "dashboard-session-snapshot.json"
    server = _new_dashboard_server("127.0.0.1", 0, state_path, snapshot_path)
    try:
        assert server.dashboard_state_path == state_path
        assert server.dashboard_session_snapshot_path == snapshot_path
    finally:
        server.server_close()


def test_dashboard_scenario_state_persists_last_posted_frontend_state():
    import urllib.request

    server = ThreadingHTTPServer(("127.0.0.1", 0), DashboardRequestHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    state = {
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
    try:
        request = urllib.request.Request(
            f"http://127.0.0.1:{server.server_port}/api/decision-pack",
            data=json.dumps(state).encode("utf-8"),
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        with urlopen(request, timeout=5) as response:
            response.read()

        with urlopen(f"http://127.0.0.1:{server.server_port}/api/scenario-state", timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))

        assert response.status == 200
        assert payload["source"] == "backend-api"
        assert payload["schemaVersion"] == 1
        assert payload["stateAvailable"] is True
        assert payload["stateSource"] == "memory"
        assert payload["state"] == state
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_dashboard_scenario_state_delete_clears_memory_and_persisted_state(tmp_path):
    import urllib.request

    state_path = tmp_path / "dashboard-scenario-state.json"
    server = ThreadingHTTPServer(("127.0.0.1", 0), DashboardRequestHandler)
    server.dashboard_state_path = state_path
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    state = {
        "candidate": "winding_series_torque",
        "businessAssumptions": {"production": 120000, "energyPrice": 1.25},
        "weights": {"urban_low_speed": 75},
    }
    try:
        post_request = urllib.request.Request(
            f"http://127.0.0.1:{server.server_port}/api/decision-pack",
            data=json.dumps(state).encode("utf-8"),
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        with urlopen(post_request, timeout=5) as response:
            response.read()

        assert state_path.exists()

        delete_request = urllib.request.Request(
            f"http://127.0.0.1:{server.server_port}/api/scenario-state",
            method="DELETE",
        )
        with urlopen(delete_request, timeout=5) as response:
            delete_payload = json.loads(response.read().decode("utf-8"))

        assert response.status == 200
        assert delete_payload == {
            "source": "backend-api",
            "schemaVersion": 1,
            "stateAvailable": False,
            "stateSource": "cleared",
            "state": None,
        }
        assert not state_path.exists()

        with urlopen(
            f"http://127.0.0.1:{server.server_port}/api/scenario-state",
            timeout=5,
        ) as response:
            get_payload = json.loads(response.read().decode("utf-8"))

        assert get_payload["stateAvailable"] is False
        assert get_payload["stateSource"] == "none"
        assert get_payload["state"] is None
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_dashboard_scenario_state_is_isolated_per_server_instance():
    import urllib.request

    first_server = ThreadingHTTPServer(("127.0.0.1", 0), DashboardRequestHandler)
    first_thread = Thread(target=first_server.serve_forever, daemon=True)
    first_thread.start()
    second_server = ThreadingHTTPServer(("127.0.0.1", 0), DashboardRequestHandler)
    second_thread = Thread(target=second_server.serve_forever, daemon=True)
    second_thread.start()

    try:
        state = {
            "candidate": "winding_series_torque",
            "businessAssumptions": {"production": 120000},
            "weights": {"urban_low_speed": 75},
        }
        request = urllib.request.Request(
            f"http://127.0.0.1:{first_server.server_port}/api/decision-pack",
            data=json.dumps(state).encode("utf-8"),
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        with urlopen(request, timeout=5) as response:
            response.read()

        with urlopen(
            f"http://127.0.0.1:{first_server.server_port}/api/scenario-state",
            timeout=5,
        ) as response:
            first_payload = json.loads(response.read().decode("utf-8"))
        with urlopen(
            f"http://127.0.0.1:{second_server.server_port}/api/scenario-state",
            timeout=5,
        ) as response:
            second_payload = json.loads(response.read().decode("utf-8"))

        assert first_payload["state"]["candidate"] == "winding_series_torque"
        assert second_payload["state"] is None
    finally:
        first_server.shutdown()
        first_server.server_close()
        first_thread.join(timeout=5)
        second_server.shutdown()
        second_server.server_close()
        second_thread.join(timeout=5)


def test_dashboard_scenario_state_can_restore_from_persistent_file(tmp_path):
    import urllib.request

    state_path = tmp_path / "dashboard-scenario-state.json"
    first_server = ThreadingHTTPServer(("127.0.0.1", 0), DashboardRequestHandler)
    first_server.dashboard_state_path = state_path
    first_thread = Thread(target=first_server.serve_forever, daemon=True)
    first_thread.start()

    state = {
        "candidate": "winding_series_torque",
        "businessAssumptions": {"production": 120000, "energyPrice": 1.25},
        "weights": {"urban_low_speed": 75},
    }
    try:
        request = urllib.request.Request(
            f"http://127.0.0.1:{first_server.server_port}/api/decision-pack",
            data=json.dumps(state).encode("utf-8"),
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        with urlopen(request, timeout=5) as response:
            response.read()
    finally:
        first_server.shutdown()
        first_server.server_close()
        first_thread.join(timeout=5)

    second_server = ThreadingHTTPServer(("127.0.0.1", 0), DashboardRequestHandler)
    second_server.dashboard_state_path = state_path
    second_thread = Thread(target=second_server.serve_forever, daemon=True)
    second_thread.start()
    try:
        with urlopen(
            f"http://127.0.0.1:{second_server.server_port}/api/scenario-state",
            timeout=5,
        ) as response:
            payload = json.loads(response.read().decode("utf-8"))

        assert response.status == 200
        assert payload["stateAvailable"] is True
        assert payload["stateSource"] == "persisted"
        assert payload["state"]["candidate"] == "winding_series_torque"
        assert payload["state"]["businessAssumptions"]["production"] == 120000
        assert payload["state"]["businessAssumptions"]["energyPrice"] == 1.25
        assert payload["state"]["weights"]["urban_low_speed"] == 75.0
    finally:
        second_server.shutdown()
        second_server.server_close()
        second_thread.join(timeout=5)


def test_dashboard_scenario_state_ignores_corrupt_persistent_file(tmp_path):
    state_path = tmp_path / "dashboard-scenario-state.json"
    state_path.write_text("{not valid json", encoding="utf-8")
    server = ThreadingHTTPServer(("127.0.0.1", 0), DashboardRequestHandler)
    server.dashboard_state_path = state_path
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        with urlopen(
            f"http://127.0.0.1:{server.server_port}/api/scenario-state",
            timeout=5,
        ) as response:
            payload = json.loads(response.read().decode("utf-8"))

        assert response.status == 200
        assert payload == {
            "source": "backend-api",
            "schemaVersion": 1,
            "stateAvailable": False,
            "stateSource": "none",
            "state": None,
        }
        assert not state_path.exists()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_dashboard_scenario_state_ignores_persistent_file_with_unknown_candidate(tmp_path):
    state_path = tmp_path / "dashboard-scenario-state.json"
    state_path.write_text(
        json.dumps(
            {
                "candidate": "missing",
                "businessAssumptions": {"production": 120000},
                "weights": {"urban_low_speed": 75},
            }
        ),
        encoding="utf-8",
    )
    server = ThreadingHTTPServer(("127.0.0.1", 0), DashboardRequestHandler)
    server.dashboard_state_path = state_path
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        with urlopen(
            f"http://127.0.0.1:{server.server_port}/api/scenario-state",
            timeout=5,
        ) as response:
            payload = json.loads(response.read().decode("utf-8"))

        assert response.status == 200
        assert payload == {
            "source": "backend-api",
            "schemaVersion": 1,
            "stateAvailable": False,
            "stateSource": "none",
            "state": None,
        }
        assert not state_path.exists()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_dashboard_scenario_state_ignores_persistent_file_with_invalid_state_shapes(tmp_path):
    state_path = tmp_path / "dashboard-scenario-state.json"
    state_path.write_text(
        json.dumps(
            {
                "candidate": "winding_series_torque",
                "businessAssumptions": ["production", 120000],
                "weights": ["urban_low_speed", 75],
            }
        ),
        encoding="utf-8",
    )
    server = ThreadingHTTPServer(("127.0.0.1", 0), DashboardRequestHandler)
    server.dashboard_state_path = state_path
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        with urlopen(
            f"http://127.0.0.1:{server.server_port}/api/scenario-state",
            timeout=5,
        ) as response:
            payload = json.loads(response.read().decode("utf-8"))

        assert response.status == 200
        assert payload == {
            "source": "backend-api",
            "schemaVersion": 1,
            "stateAvailable": False,
            "stateSource": "none",
            "state": None,
        }
        assert not state_path.exists()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_dashboard_scenario_state_ignores_persistent_file_with_non_finite_numbers(tmp_path):
    state_path = tmp_path / "dashboard-scenario-state.json"
    state_path.write_text(
        json.dumps(
            {
                "candidate": "winding_series_torque",
                "businessAssumptions": {"production": "NaN"},
                "weights": {"urban_low_speed": "Infinity"},
            }
        ),
        encoding="utf-8",
    )
    server = ThreadingHTTPServer(("127.0.0.1", 0), DashboardRequestHandler)
    server.dashboard_state_path = state_path
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        with urlopen(
            f"http://127.0.0.1:{server.server_port}/api/scenario-state",
            timeout=5,
        ) as response:
            payload = json.loads(response.read().decode("utf-8"))

        assert response.status == 200
        assert payload == {
            "source": "backend-api",
            "schemaVersion": 1,
            "stateAvailable": False,
            "stateSource": "none",
            "state": None,
        }
        assert not state_path.exists()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_dashboard_scenario_state_ignores_persistent_file_with_out_of_bounds_numbers(tmp_path):
    state_path = tmp_path / "dashboard-scenario-state.json"
    state_path.write_text(
        json.dumps(
            {
                "candidate": "winding_series_torque",
                "businessAssumptions": {"production": -1},
                "weights": {"urban_low_speed": 40},
            }
        ),
        encoding="utf-8",
    )
    server = ThreadingHTTPServer(("127.0.0.1", 0), DashboardRequestHandler)
    server.dashboard_state_path = state_path
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        with urlopen(
            f"http://127.0.0.1:{server.server_port}/api/scenario-state",
            timeout=5,
        ) as response:
            payload = json.loads(response.read().decode("utf-8"))

        assert response.status == 200
        assert payload == {
            "source": "backend-api",
            "schemaVersion": 1,
            "stateAvailable": False,
            "stateSource": "none",
            "state": None,
        }
        assert not state_path.exists()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_dashboard_decision_pack_post_returns_json_error_when_backend_fails():
    import urllib.request

    server = ThreadingHTTPServer(("127.0.0.1", 0), DashboardRequestHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        request = urllib.request.Request(
            f"http://127.0.0.1:{server.server_port}/api/decision-pack?smokeFail=1",
            data=json.dumps({"candidate": "baseline"}).encode("utf-8"),
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        try:
            with urlopen(request, timeout=5):
                raise AssertionError("expected HTTP 500")
        except HTTPError as error:
            body = error.read().decode("utf-8")
            assert error.code == 500
            assert error.headers["Content-Type"] == "application/json; charset=utf-8"
            assert '"error": "dashboard_payload_unavailable"' in body
            assert "intentional smoke failure" in body
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_dashboard_decision_pack_failed_post_does_not_mutate_scenario_state():
    import urllib.request

    server = ThreadingHTTPServer(("127.0.0.1", 0), DashboardRequestHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    baseline_state = {
        "candidate": "baseline",
        "businessAssumptions": {"production": 10000},
        "weights": {"urban_low_speed": 40},
    }
    failing_state = {
        "candidate": "missing",
        "businessAssumptions": {"production": 120000},
        "weights": {"urban_low_speed": 75},
    }
    try:
        request = urllib.request.Request(
            f"http://127.0.0.1:{server.server_port}/api/decision-pack",
            data=json.dumps(baseline_state).encode("utf-8"),
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        with urlopen(request, timeout=5) as response:
            response.read()

        request = urllib.request.Request(
            f"http://127.0.0.1:{server.server_port}/api/decision-pack",
            data=json.dumps(failing_state).encode("utf-8"),
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        try:
            with urlopen(request, timeout=5):
                raise AssertionError("expected HTTP 400")
        except HTTPError as error:
            assert error.code == 400

        with urlopen(
            f"http://127.0.0.1:{server.server_port}/api/scenario-state",
            timeout=5,
        ) as response:
            payload = json.loads(response.read().decode("utf-8"))

        assert payload["state"]["candidate"] == "baseline"
        assert payload["state"]["businessAssumptions"]["production"] == 10000
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_dashboard_decision_pack_rejects_unknown_candidate():
    server = ThreadingHTTPServer(("127.0.0.1", 0), DashboardRequestHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        try:
            with urlopen(
                f"http://127.0.0.1:{server.server_port}/api/decision-pack?candidate=missing",
                timeout=5,
            ):
                raise AssertionError("expected HTTP 400")
        except HTTPError as error:
            body = error.read().decode("utf-8")
            assert error.code == 400
            assert error.headers["Content-Type"] == "application/json; charset=utf-8"
            assert '"error": "dashboard_request_invalid"' in body
            assert "unknown candidate: missing" in body
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_dashboard_http_server_returns_json_error_when_payload_build_fails(monkeypatch):
    def broken_payload(_root):
        raise FileNotFoundError("missing experiment data")

    monkeypatch.setattr("sim.dashboard_api.build_dashboard_payload", broken_payload)
    server = ThreadingHTTPServer(("127.0.0.1", 0), DashboardRequestHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        with urlopen(f"http://127.0.0.1:{server.server_port}/api/dashboard", timeout=5):
            raise AssertionError("expected HTTP 500")
    except HTTPError as error:
        body = error.read().decode("utf-8")
        assert error.code == 500
        assert error.headers["Content-Type"] == "application/json; charset=utf-8"
        assert '"error": "dashboard_payload_unavailable"' in body
        assert "missing experiment data" in body
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_dashboard_cli_smoke_runs_real_frontend_backend_check():
    result = subprocess.run(
        [sys.executable, "-m", "sim.dashboard_api", "--smoke"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=15,
    )

    assert result.returncode == 0, result.stderr
    assert "dashboard_api=200" in result.stdout
    assert "health_api=200" in result.stdout
    assert "schema_api=200" in result.stdout
    assert "schema_report=ok" in result.stdout
    assert "decision_pack_api=200" in result.stdout
    assert "decision_pack_post_api=200 selected=winding_series_torque" in result.stdout
    assert "scenario_state_api=200 available=True source=memory" in result.stdout
    assert "scenario_state_clear_api=200 available=False" in result.stdout
    assert "scenario_state_read_after_clear_api=200 available=False source=none" in result.stdout
    assert "session_snapshot_api=200 available=False" in result.stdout
    assert "session_snapshot_post_api=200 available=True candidate=winding_series_torque" in result.stdout
    assert "session_snapshot_read_api=200 available=True candidate=winding_series_torque" in result.stdout
    assert "session_snapshot_clear_api=200 available=False" in result.stdout
    assert "customer_brief_api=200" in result.stdout
    assert "customer_brief_post_api=200 candidate=winding_series_torque" in result.stdout
    assert "design_spec_api=200 file=reports/open_design_dashboard_spec.json" in result.stdout
    assert "html=200" in result.stdout
    assert "frontend_fetch_contract=ok" in result.stdout
    assert "frontend_fetch_contract=endpoints=8" in result.stdout
    assert "frontend_session_snapshot_contract=ok" in result.stdout


def test_dashboard_dev_script_exposes_smoke_and_serve_commands():
    script = ROOT / "scripts" / "dashboard_dev.py"

    assert script.exists()
    result = subprocess.run(
        [sys.executable, str(script), "--help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )

    assert result.returncode == 0, result.stderr
    assert "smoke" in result.stdout
    assert "serve" in result.stdout
    assert "browser-interaction" in result.stdout


def test_dashboard_dev_script_runs_real_integration_smoke_suite():
    script = ROOT / "scripts" / "dashboard_dev.py"

    result = subprocess.run(
        [sys.executable, str(script), "smoke", "--quick"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=90,
    )

    assert result.returncode == 0, result.stderr
    assert result.stderr == ""
    assert "dashboard_dev_smoke=ok" in result.stdout
    assert "schema_report=ok" in result.stdout
    assert "browser_interaction=ok" in result.stdout


def test_dashboard_cli_browser_smoke_runs_page_in_headless_browser():
    result = subprocess.run(
        [sys.executable, "-m", "sim.dashboard_api", "--browser-smoke"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )

    assert result.returncode == 0, result.stderr
    assert "browser_page=ok" in result.stdout
    assert "api_status=connected" in result.stdout
    assert "health_panel=runtime-counts" in result.stdout


def test_dashboard_cli_browser_interaction_smoke_runs_real_page_events():
    result = subprocess.run(
        [sys.executable, "-m", "sim.dashboard_api", "--browser-interaction-smoke"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )

    assert result.returncode == 0, result.stderr
    assert "browser_interaction=ok" in result.stdout
    assert "candidate_click=ok" in result.stdout
    assert "weight_input=ok" in result.stdout
    assert "scenario_restore=ok" in result.stdout
    assert "scenario_clear=ok" in result.stdout
    assert "api_sync_log=ok" in result.stdout
    assert "session_snapshot=ok" in result.stdout
    assert "session_snapshot_metadata=ok" in result.stdout
    assert "session_snapshot_clear=ok" in result.stdout
    assert "refresh_click=ok" in result.stdout
    assert "customer_brief_export=ok" in result.stdout
    assert "decision_pack_export=ok" in result.stdout
    assert "decision_pack_candidate=winding_series_torque" in result.stdout
    assert "decision_pack_weight_urban=75" in result.stdout
    assert "decision_pack_production=120000" in result.stdout
    assert "decision_pack_energy_price=1.25" in result.stdout
    assert "decision_pack_transport=POST" in result.stdout
    assert "clipboard_source=backend-api" in result.stdout
    assert "clipboard_business_case=ok" in result.stdout
    assert "design_spec_runtime_fetch=ok" in result.stdout
    assert "design_spec_export=ok" in result.stdout
    assert "design_spec_file=reports/open_design_dashboard_spec.json" in result.stdout
    assert "design_spec_clipboard_product=customer_dashboard" in result.stdout


def test_dashboard_cli_browser_error_smoke_verifies_frontend_fallback():
    result = subprocess.run(
        [sys.executable, "-m", "sim.dashboard_api", "--browser-error-smoke"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )

    assert result.returncode == 0, result.stderr
    assert "browser_error=ok" in result.stdout
    assert "dashboard_fallback=ok" in result.stdout
    assert "health_fallback=ok" in result.stdout
    assert "decision_pack_fallback=ok" in result.stdout
    assert "fallback_clipboard_source=local" in result.stdout


def test_dashboard_cli_browser_contract_smoke_rejects_bad_decision_pack_payload():
    result = subprocess.run(
        [sys.executable, "-m", "sim.dashboard_api", "--browser-contract-smoke"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )

    assert result.returncode == 0, result.stderr
    assert "browser_contract=ok" in result.stdout
    assert "dashboard_payload_schema_rejected=ok" in result.stdout
    assert "health_payload_schema_rejected=ok" in result.stdout
    assert "schema_payload_schema_rejected=ok" in result.stdout
    assert "decision_pack_contract_fallback=ok" in result.stdout
    assert "customer_brief_contract_fallback=ok" in result.stdout
    assert "design_spec_contract_fallback=ok" in result.stdout
    assert "scenario_state_schema_rejected=ok" in result.stdout
    assert "session_snapshot_save_schema_rejected=ok" in result.stdout
    assert "session_snapshot_clear_schema_rejected=ok" in result.stdout
    assert "session_snapshot_schema_rejected=ok" in result.stdout
    assert "contract_clipboard_source=local" in result.stdout


def test_dashboard_cli_browser_screenshot_smoke_captures_desktop_and_mobile():
    result = subprocess.run(
        [sys.executable, "-m", "sim.dashboard_api", "--browser-screenshot-smoke"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=40,
    )

    assert result.returncode == 0, result.stderr
    assert result.stderr == ""
    assert "screenshot_desktop=ok" in result.stdout
    assert "screenshot_mobile=ok" in result.stdout
    assert "png_pixels=nonblank" in result.stdout
    assert (ROOT / "reports" / "dashboard-smoke-desktop.png").exists()
    assert (ROOT / "reports" / "dashboard-smoke-mobile.png").exists()
