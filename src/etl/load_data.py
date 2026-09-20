import pandas as pd
from sqlalchemy.exc import IntegrityError
from db_connection import engine

TURBINE_FILES = {python src/etl/load_data.py
    "WT02": "Turbine_Data_Penmanshiel_02_2020-01-01_-_2021-01-01_1043.csv",
    "WT04": "Turbine_Data_Penmanshiel_04_2020-01-01_-_2021-01-01_1044.csv",
    "WT05": "Turbine_Data_Penmanshiel_05_2020-01-01_-_2021-01-01_1045.csv",
    "WT06": "Turbine_Data_Penmanshiel_06_2020-01-01_-_2021-01-01_1046.csv",
    "WT07": "Turbine_Data_Penmanshiel_07_2020-01-01_-_2021-01-01_1047.csv",
    "WT08": "Turbine_Data_Penmanshiel_08_2020-01-01_-_2021-01-01_1048.csv",
    "WT09": "Turbine_Data_Penmanshiel_09_2020-01-01_-_2021-01-01_1049.csv",
    "WT10": "Turbine_Data_Penmanshiel_10_2020-01-01_-_2021-01-01_1050.csv",
}

COLUMN_MAP = {
    "Date and time": "ts",
    "Wind speed (m/s)": "wind_speed_avg",
    "Wind speed, Standard deviation (m/s)": "wind_speed_std",
    "Power (kW)": "power_avg",
    "Power, Standard deviation (kW)": "power_std",
    "Gear oil temperature (°C)": "gear_oil_temp",
    "Generator bearing front temperature (°C)": "gen_bearing_front_temp",
    "Generator bearing rear temperature (°C)": "gen_bearing_rear_temp",
    "Front bearing temperature (°C)": "front_bearing_temp",
    "Rear bearing temperature (°C)": "rear_bearing_temp",
    "Nacelle temperature (°C)": "nacelle_temp",
    "Blade angle (pitch position) A (°)": "pitch_angle_a",
    "Blade angle (pitch position) B (°)": "pitch_angle_b",
    "Blade angle (pitch position) C (°)": "pitch_angle_c",
}


def load_turbine(turbine_id: str, filename: str) -> None:
    path = f"data/raw/{filename}"
    df = pd.read_csv(path, skiprows=9)
    df.columns = df.columns.str.replace("# ", "", regex=False)

    df = df[list(COLUMN_MAP.keys())].rename(columns=COLUMN_MAP)
    df["turbine_id"] = turbine_id
    df["ts"] = pd.to_datetime(df["ts"])

    with engine.begin() as conn:
        try:
            conn.exec_driver_sql(
                "INSERT INTO turbines (turbine_id, manufacturer, model) VALUES (?, ?, ?)",
                (turbine_id, "Senvion", "MM82"),
            )
        except IntegrityError:
            pass  # turbine already registered, e.g. WT01 from the earlier test run

    df.to_sql("readings", engine, if_exists="append", index=False)
    print(f"Loaded {len(df)} rows for {turbine_id}.")


if __name__ == "__main__":
    for turbine_id, filename in TURBINE_FILES.items():
        load_turbine(turbine_id, filename)