-- Reference power curve: average expected power per turbine and wind speed bin (0.5 m/s bins)
CREATE VIEW power_curve_reference AS
SELECT
    turbine_id,
    ROUND(wind_speed_avg / 0.5, 0) * 0.5 AS wind_speed_bin,
    AVG(power_avg) AS expected_power
FROM readings
WHERE wind_speed_avg IS NOT NULL AND power_avg IS NOT NULL
GROUP BY turbine_id, ROUND(wind_speed_avg / 0.5, 0) * 0.5;

-- Final features view: power curve residual, moving averages and deltas, plus temperatures
-- Note: an earlier version added an is_downtime column here via a correlated EXISTS against events,
-- but it was too costly to run on the free tier. Downtime flagging was moved to pandas (merge_asof)
-- in 03_model_training.ipynb instead.
CREATE VIEW features AS
SELECT
    r.turbine_id,
    r.ts,
    r.wind_speed_avg,
    r.power_avg,
    ref.expected_power,
    r.power_avg - ref.expected_power AS power_residual,
    (r.power_avg - ref.expected_power) / NULLIF(ref.expected_power, 0) AS power_residual_pct,
    AVG(r.power_avg) OVER (
        PARTITION BY r.turbine_id ORDER BY r.ts
        ROWS BETWEEN 5 PRECEDING AND CURRENT ROW
    ) AS power_avg_moving_6,
    r.power_avg - LAG(r.power_avg) OVER (
        PARTITION BY r.turbine_id ORDER BY r.ts
    ) AS power_avg_delta,
    AVG(r.wind_speed_avg) OVER (
        PARTITION BY r.turbine_id ORDER BY r.ts
        ROWS BETWEEN 5 PRECEDING AND CURRENT ROW
    ) AS wind_speed_avg_moving_6,
    r.wind_speed_avg - LAG(r.wind_speed_avg) OVER (
        PARTITION BY r.turbine_id ORDER BY r.ts
    ) AS wind_speed_avg_delta,
    r.gear_oil_temp,
    r.gen_bearing_front_temp,
    r.gen_bearing_rear_temp,
    r.front_bearing_temp,
    r.rear_bearing_temp,
    r.nacelle_temp
FROM readings r
JOIN power_curve_reference ref
    ON r.turbine_id = ref.turbine_id
    AND ROUND(r.wind_speed_avg / 0.5, 0) * 0.5 = ref.wind_speed_bin;