from pathlib import Path

import joblib
import pandas as pd

from schemas import ReadingInput, ScoreResponse
from store import store

#must match the column order the model was trained on in 03_model_training.ipynb
FEATURE_COLUMNS = [
    "wind_speed_avg",
    "power_residual",
    "power_residual_pct",
    "power_avg_delta",
    "wind_speed_avg_delta",
    "gear_oil_temp",
    "gen_bearing_front_temp",
    "gen_bearing_rear_temp",
    "nacelle_temp",
]

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
model = joblib.load(_PROJECT_ROOT / "models" / "isolation_forest.joblib")
power_curve = pd.read_parquet(_PROJECT_ROOT / "data" / "processed" / "power_curve_reference.parquet")


def _expected_power(turbine_id: str, wind_speed_avg: float) -> float:
    """Look up expected power for this turbine and wind speed bin.

    Mirrors the binning in sql/features.sql (0.5 m/s bins). Falls back to the
    nearest available bin for that turbine if the exact bin has no training data,
    which happens at wind speed extremes (see 04_anomaly_validation.ipynb: this is
    exactly the condition that produces most of the model's false positives).
    """
    wind_speed_bin = round(wind_speed_avg / 0.5) * 0.5
    turbine_curve = power_curve[power_curve["turbine_id"] == turbine_id]

    exact_match = turbine_curve[turbine_curve["wind_speed_bin"] == wind_speed_bin]
    if not exact_match.empty:
        return exact_match["expected_power"].iloc[0]

    nearest_idx = (turbine_curve["wind_speed_bin"] - wind_speed_bin).abs().idxmin()
    return turbine_curve.loc[nearest_idx, "expected_power"]


def score_reading(reading: ReadingInput) -> ScoreResponse:
    history = store.get(reading.turbine_id)

    expected_power = _expected_power(reading.turbine_id, reading.wind_speed_avg)
    power_residual = reading.power_avg - expected_power
    power_residual_pct = power_residual / expected_power if expected_power else 0.0

    #the model needs the previous reading to compute deltas, so the first
    #reading of a turbine (or after an API restart) can't be scored yet
    insufficient_history = history.last_wind_speed_avg is None

    if insufficient_history:
        anomaly = False
        anomaly_score = float("nan")
        persistent = False
    else:
        features = pd.DataFrame([{
            "wind_speed_avg": reading.wind_speed_avg,
            "power_residual": power_residual,
            "power_residual_pct": power_residual_pct,
            "power_avg_delta": reading.power_avg - history.last_power_avg,
            "wind_speed_avg_delta": reading.wind_speed_avg - history.last_wind_speed_avg,
            "gear_oil_temp": reading.gear_oil_temp,
            "gen_bearing_front_temp": reading.gen_bearing_front_temp,
            "gen_bearing_rear_temp": reading.gen_bearing_rear_temp,
            "nacelle_temp": reading.nacelle_temp,
        }])[FEATURE_COLUMNS]

        anomaly = bool(model.predict(features)[0] == -1)
        anomaly_score = float(model.decision_function(features)[0])
        persistent = anomaly and len(history.recent_anomalies) == 2 and all(history.recent_anomalies)

        history.recent_anomalies.append(anomaly)

    history.last_wind_speed_avg = reading.wind_speed_avg
    history.last_power_avg = reading.power_avg

    return ScoreResponse(
        turbine_id=reading.turbine_id,
        ts=reading.ts,
        anomaly=anomaly,
        anomaly_score=anomaly_score,
        anomaly_persistent=persistent,
        insufficient_history=insufficient_history,
    )
