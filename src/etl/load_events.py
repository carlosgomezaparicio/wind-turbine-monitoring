import pandas as pd
from db_connection import engine

STATUS_FILES = {
    "WT01": "Status_Penmanshiel_01_2020-01-01_-_2021-01-01_1042.csv",
    "WT02": "Status_Penmanshiel_02_2020-01-01_-_2021-01-01_1043.csv",
    "WT04": "Status_Penmanshiel_04_2020-01-01_-_2021-01-01_1044.csv",
    "WT05": "Status_Penmanshiel_05_2020-01-01_-_2021-01-01_1045.csv",
    "WT06": "Status_Penmanshiel_06_2020-01-01_-_2021-01-01_1046.csv",
    "WT07": "Status_Penmanshiel_07_2020-01-01_-_2021-01-01_1047.csv",
    "WT08": "Status_Penmanshiel_08_2020-01-01_-_2021-01-01_1048.csv",
    "WT09": "Status_Penmanshiel_09_2020-01-01_-_2021-01-01_1049.csv",
    "WT10": "Status_Penmanshiel_10_2020-01-01_-_2021-01-01_1050.csv",
}

EVENTS_COLUMN_MAP = {
    "Timestamp start": "ts_start",
    "Timestamp end": "ts_end",
    "Status": "status",
    "Code": "code",
    "Message": "message",
    "Comment": "comment",
    "Service contract category": "service_contract_category",
    "IEC category": "iec_category",
}


def load_events(turbine_id: str, filename: str) -> None:
    path = f"data/raw/{filename}"
    df = pd.read_csv(path, skiprows=9)

    df = df[list(EVENTS_COLUMN_MAP.keys())].rename(columns=EVENTS_COLUMN_MAP)
    df["turbine_id"] = turbine_id

    df["ts_start"] = pd.to_datetime(df["ts_start"])
    df["ts_end"] = df["ts_end"].replace("-", pd.NA)
    df["ts_end"] = pd.to_datetime(df["ts_end"])

    df.to_sql("events", engine, if_exists="append", index=False)
    print(f"Loaded {len(df)} events for {turbine_id}.")


if __name__ == "__main__":
    for turbine_id, filename in STATUS_FILES.items():
        load_events(turbine_id, filename)