CREATE TABLE turbines (
    turbine_id CHAR(4) PRIMARY KEY,
    manufacturer VARCHAR(50),
    model VARCHAR(50)
);

CREATE TABLE readings (
    turbine_id CHAR(4) NOT NULL,
    ts DATETIME2 NOT NULL,
    wind_speed_avg REAL,
    wind_speed_std REAL,
    power_avg REAL,
    power_std REAL,
    gear_oil_temp REAL,
    gen_bearing_front_temp REAL,
    gen_bearing_rear_temp REAL,
    front_bearing_temp REAL,
    rear_bearing_temp REAL,
    nacelle_temp REAL,
    pitch_angle_a REAL,
    pitch_angle_b REAL,
    pitch_angle_c REAL,
    PRIMARY KEY (turbine_id, ts),
    FOREIGN KEY (turbine_id) REFERENCES turbines(turbine_id)
);

CREATE TABLE events (
    event_id INT IDENTITY(1,1) PRIMARY KEY,
    turbine_id CHAR(4) NOT NULL,
    ts_start DATETIME2 NOT NULL,
    ts_end DATETIME2 NULL,
    status VARCHAR(50),
    code INT,
    message VARCHAR(200),
    comment VARCHAR(200),
    service_contract_category VARCHAR(100),
    iec_category VARCHAR(100),
    FOREIGN KEY (turbine_id) REFERENCES turbines(turbine_id)
);