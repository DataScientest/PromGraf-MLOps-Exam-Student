from evidently import Report, Dataset, DataDefinition, Regression
from evidently.metrics import MAE, RMSE, R2Score
from evidently.presets import DataDriftPreset

from fastapi import FastAPI, HTTPException, Response, Request
from pydantic import BaseModel, Field

from prometheus_client import Counter, Histogram, generate_latest, CollectorRegistry, Gauge


# --- Logging Configuration ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Bike Sharing Predictor API",
    description="API for predicting bike sharing demand with MLOps monitoring.",
    version="1.0.0"
)

# --- Prometheus Metrics Definitions ---



# --- Global Variables for Model and Data ---
TARGET = 'cnt'
PREDICTION = 'prediction'
NUM_FEATS = ['temp', 'atemp', 'hum', 'windspeed', 'mnth', 'hr', 'weekday']
CAT_FEATS = ['season', 'holiday', 'workingday', 'weathersit']


# --- Data Ingestion and Preparation Functions ---


# --- Pydantic Models for API Input/Output ---
class BikeSharingInput(BaseModel):
    temp: float = Field(..., example=0.24)
    atemp: float = Field(..., example=0.2879)
    hum: float = Field(..., example=0.81)
    windspeed: float = Field(..., example=0.0)
    mnth: int = Field(..., example=1)
    hr: int = Field(..., example=0)
    weekday: int = Field(..., example=6)
    season: int = Field(..., example=1)
    holiday: int = Field(..., example=0)
    workingday: int = Field(..., example=0)
    weathersit: int = Field(..., example=1)
    dteday: datetime.date = Field(..., example="2011-01-01", description="Date of the record in YYYY-MM-DD format.")

# --- API Endpoints ---
@app.get("/")
async def read_root():
    return {"message": "Welcome to the Bike Sharing Predictor API. Use /predict to get bike counts or /evaluate to run drift reports."}
