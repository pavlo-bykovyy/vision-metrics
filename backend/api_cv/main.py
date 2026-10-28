import os
from fastapi import FastAPI
import asyncio
from contextlib import asynccontextmanager

from shared.utils.cors import setup_cors
from api_cv.routers import ai_models, evaluations
from shared.routers import auth, system, datasets

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


app = FastAPI(
    title="VisionMetrics CV API",
    description="API for analyzing concrete structures")

setup_cors(app)

app.include_router(auth.router)
app.include_router(system.router)
app.include_router(datasets.router)
app.include_router(ai_models.router)
app.include_router(evaluations.router)

@app.get("/")
def root():
    return {"status": "ok", "message": "CV API is working"}


