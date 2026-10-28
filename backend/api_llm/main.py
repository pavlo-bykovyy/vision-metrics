from fastapi import FastAPI

from shared.utils.cors import setup_cors
from api_llm.routers import (
    lora_adapters,
    lora_evaluations,
    lora_results,
    active_models,
    chat_api,
    judges,
    base_evaluations,
    judge_task_runs
)
from shared.routers import auth, system, datasets


app = FastAPI(
    title="VisionMetrics LLM API",
    description="API for local text generation"
)

setup_cors(app)

app.include_router(auth.router)
app.include_router(system.router)
app.include_router(datasets.router)
app.include_router(lora_adapters.router)
app.include_router(lora_evaluations.router)
app.include_router(lora_results.router)
app.include_router(active_models.router)
app.include_router(chat_api.router)
app.include_router(judges.router)
app.include_router(base_evaluations.router)
app.include_router(judge_task_runs.router)

@app.get("/")
def root():
    return {"status": "ok", "message": "LLM API is working"}