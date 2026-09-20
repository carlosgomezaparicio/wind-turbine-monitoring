from fastapi import FastAPI

from schemas import ReadingInput, ScoreResponse
from scoring import score_reading

app = FastAPI(
    title="Wind Turbine Anomaly Detection API",
    description="Scores incoming SCADA readings for anomalies using an Isolation Forest "
    "trained on Penmanshiel wind farm data (see notebooks/03_model_training.ipynb).",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/readings/score", response_model=ScoreResponse)
def score(reading: ReadingInput) -> ScoreResponse:
    return score_reading(reading)
