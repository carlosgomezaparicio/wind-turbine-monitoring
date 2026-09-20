import pytest

from scoring import _expected_power, score_reading
from schemas import ReadingInput


def _reading(turbine_id, ts, wind_speed_avg=8.0, power_avg=780.0, **overrides):
    defaults = dict(
        turbine_id=turbine_id,
        ts=ts,
        wind_speed_avg=wind_speed_avg,
        power_avg=power_avg,
        gear_oil_temp=50.0,
        gen_bearing_front_temp=40.0,
        gen_bearing_rear_temp=40.0,
        nacelle_temp=20.0,
    )
    defaults.update(overrides)
    return ReadingInput(**defaults)


def test_expected_power_exact_bin_match():
    #WT04 at 8.0 m/s has real training data for this exact bin
    expected = _expected_power("WT04", 8.0)
    assert expected == pytest.approx(780.209763, rel=1e-4)


def test_expected_power_falls_back_to_nearest_bin():
    #WT04 has no data at the 26.5 bin (see 04_anomaly_validation.ipynb: sparse at
    #wind speed extremes), so it must fall back to the nearest bin it does have (25.5)
    expected = _expected_power("WT04", 26.5)
    assert expected == pytest.approx(1060.100429, rel=1e-4)


#real turbine IDs are required: _expected_power looks each one up in
#power_curve_reference.parquet, and an unknown ID has no curve to fall back on.
#Each test below uses a turbine ID that no other test touches, since the
#in-memory store (store.py) is a module-level singleton shared across the
#whole test session, not reset between tests.


def test_first_reading_is_stored_not_scored():
    reading = _reading("WT01", "2020-01-01T00:00:00")
    result = score_reading(reading)

    assert result.insufficient_history is True
    assert result.anomaly is False
    assert result.anomaly_persistent is False


def test_second_reading_uses_history_to_score():
    turbine_id = "WT02"
    score_reading(_reading(turbine_id, "2020-01-01T00:00:00", wind_speed_avg=8.0, power_avg=780.0))
    result = score_reading(_reading(turbine_id, "2020-01-01T00:10:00", wind_speed_avg=8.1, power_avg=800.0))

    assert result.insufficient_history is False
    #a real number now, not NaN
    assert result.anomaly_score == result.anomaly_score


def test_turbines_have_independent_history():
    #scoring one turbine must not affect another turbine's stored history
    score_reading(_reading("WT05", "2020-01-01T00:00:00"))
    result = score_reading(_reading("WT06", "2020-01-01T00:00:00"))

    assert result.insufficient_history is True


def test_extreme_power_deviation_is_flagged_anomalous():
    turbine_id = "WT07"
    #normal reading matching the power curve at 8 m/s
    score_reading(_reading(turbine_id, "2020-01-01T00:00:00", wind_speed_avg=8.0, power_avg=780.0))
    #same wind speed, wildly higher power than the curve expects
    result = score_reading(_reading(turbine_id, "2020-01-01T00:10:00", wind_speed_avg=8.0, power_avg=5000.0))

    assert result.anomaly is True
