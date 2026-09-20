from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def _payload(turbine_id, ts, wind_speed_avg=8.0, power_avg=780.0):
    return {
        "turbine_id": turbine_id,
        "ts": ts,
        "wind_speed_avg": wind_speed_avg,
        "power_avg": power_avg,
        "gear_oil_temp": 50.0,
        "gen_bearing_front_temp": 40.0,
        "gen_bearing_rear_temp": 40.0,
        "nacelle_temp": 20.0,
    }


#real turbine IDs, each used only once across the whole test session, for the
#same reason explained in tests/test_scoring.py (shared in-memory store).


def test_score_first_reading_is_insufficient_history():
    response = client.post("/readings/score", json=_payload("WT08", "2020-01-01T00:00:00"))

    assert response.status_code == 200
    body = response.json()
    assert body["insufficient_history"] is True
    assert body["anomaly"] is False


def test_score_second_reading_returns_full_result():
    turbine_id = "WT09"
    client.post("/readings/score", json=_payload(turbine_id, "2020-01-01T00:00:00", wind_speed_avg=8.0, power_avg=780.0))
    response = client.post(
        "/readings/score",
        json=_payload(turbine_id, "2020-01-01T00:10:00", wind_speed_avg=8.1, power_avg=800.0),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["insufficient_history"] is False
    assert "anomaly_score" in body


def test_score_rejects_missing_required_field():
    #fails validation before reaching store logic, so the turbine ID here
    #does not need to be unique like the ones above
    incomplete_payload = _payload("WT10", "2020-01-01T00:00:00")
    del incomplete_payload["wind_speed_avg"]

    response = client.post("/readings/score", json=incomplete_payload)

    assert response.status_code == 422
