from collections import deque
from dataclasses import dataclass, field


@dataclass
class TurbineHistory:
    last_wind_speed_avg: float | None = None
    last_power_avg: float | None = None
    # holds the anomaly flag (bool) of the last 2 scored readings, used for the
    # 3-in-a-row persistence rule (see docs/03_model_training.ipynb conclusions)
    recent_anomalies: deque[bool] = field(default_factory=lambda: deque(maxlen=2))


class TurbineHistoryStore:
    """In-memory per-turbine state.

    Not thread-safe and not persisted across restarts. Fine for a single-instance
    demo API; a real deployment would back this with Redis or a database table
    so state survives restarts and works across multiple API instances.
    """

    def __init__(self) -> None:
        self._turbines: dict[str, TurbineHistory] = {}

    def get(self, turbine_id: str) -> TurbineHistory:
        if turbine_id not in self._turbines:
            self._turbines[turbine_id] = TurbineHistory()
        return self._turbines[turbine_id]


store = TurbineHistoryStore()
