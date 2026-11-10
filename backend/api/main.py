from fastapi import FastAPI

from shared.utils.cors import setup_cors
from shared.routers import auth, system, datasets

# CV
from api_cv.routers import ai_models, evaluations

# LLM
from api_llm.routers import (
    lora_adapters,
    lora_evaluations,
    lora_results,
    active_models,
    chat_api,
    judges,
    base_evaluations,
    judge_task_runs,
    attacks,
)

app = FastAPI(
    title="VisionMetrics API",
    description="API for concrete structure analysis (CV) and local text generation (LLM)",
)

setup_cors(app)

# shared
app.include_router(auth.router)
app.include_router(system.router)
app.include_router(datasets.router)

# CV
app.include_router(ai_models.router)
app.include_router(evaluations.router)

# LLM
app.include_router(lora_adapters.router)
app.include_router(lora_evaluations.router)
app.include_router(lora_results.router)
app.include_router(active_models.router)
app.include_router(chat_api.router)
app.include_router(judges.router)
app.include_router(base_evaluations.router)
app.include_router(judge_task_runs.router)
app.include_router(attacks.router)


@app.get("/")
def root():
    return {"status": "ok", "message": "VisionMetrics API is working"}