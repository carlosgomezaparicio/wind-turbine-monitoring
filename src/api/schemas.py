from datetime import datetime

from pydantic import BaseModel


class ReadingInput(BaseModel):

    turbine_id: str
    ts: datetime
    wind_speed_avg: float
    wind_speed_std: float | None = None
    power_avg: float
    power_std: float | None = None
    gear_oil_temp: float
    gen_bearing_front_temp: float
    gen_bearing_rear_temp: float
    front_bearing_temp: float | None = None
    rear_bearing_temp: float | None = None
    nacelle_temp: float
    pitch_angle_a: float | None = None
    pitch_angle_b: float | None = None
    pitch_angle_c: float | None = None


class ScoreResponse(BaseModel):
    turbine_id: str
    ts: datetime
    anomaly: bool
    anomaly_score: float
    anomaly_persistent: bool
    insufficient_history: bool
