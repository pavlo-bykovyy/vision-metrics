# vision-metrics

A comprehensive system for evaluating Computer Vision models and LLMs (including LoRA adapters and adversarial attack scenarios). The project uses Docker containerization to manage the APIs, background workers (Celery), the database, and the message broker (Redis).

## 🛠 Prerequisites

To deploy and develop locally, you will need the following installed on your machine:

* [Docker](https://docs.docker.com/get-docker/)
* [Docker Compose](https://docs.docker.com/compose/install/)

---

## Host Directory Setup

Before starting the containers or uploading files, create the required directories on the host machine to ensure data persistence for models, datasets, and cache:

```bash
sudo mkdir -p /mnt/data/visionmetrics/uploaded_models
sudo mkdir -p /mnt/data/visionmetrics/extracted_datasets
sudo mkdir -p /mnt/data/visionmetrics/model_cache

sudo chmod -R 777 /mnt/data/visionmetrics
```

---

## Quick Start

**1. Build the base image**

Before the first run, or after changing system dependencies, build the base Docker image:

```bash
sudo docker compose --profile setup build base_image
```

**2. Start the containers**

Build and start all services in detached mode:

```bash
sudo docker compose up -d --build
```

Once completed, the APIs, Celery workers, database, and Redis will be up and running.

---

## 🗄️ Database Migrations (Alembic)

Database schema changes are managed with Alembic. All commands must be executed inside the `visionmetrics_api` container.

**Generate a new migration (autogenerate)**

Whenever you change the database models, generate a new migration:

```bash
docker exec -it visionmetrics_api alembic revision --autogenerate -m "describe_your_changes_here"
```

For the very first setup (or after a full rebuild), use a message such as `"initial_setup"`.

**Apply migrations**

```bash
docker exec -it visionmetrics_api alembic upgrade head
```

**Sync migrations to your local machine**

Migration files are generated inside the container, so copy them to the host to commit them to Git:

```bash
docker cp visionmetrics_api:/app/migrations/versions/. ./backend/migrations/versions/
```

---

## 🔧 Useful Commands

**Clear the Redis cache / flush Celery queues**

To purge all pending background tasks or clear the cache entirely:

```bash
docker exec -it visionmetrics_redis redis-cli flushall
```

---

Ось оновлений розділ документації, куди акуратно інтегровано нові інструкції для збирання ізольованого тестового образу та запуску через чистий `docker`:

```markdown
## 🧪 Running Tests (`pytest`)

Unit and regression tests are located in `backend/api_llm/tests/`. They use an isolated in-memory SQLite database (`conftest.py`) and temporary directories, so they do **not** require a running PostgreSQL, Redis, or GPU instance.

### Option 1: Run inside the Docker container
If the stack is running via Docker Compose:

```bash
docker exec -it visionmetrics_api pytest api_llm/tests/ -v

```

Or in a one-off container without starting the full stack:

```bash
docker compose run --rm -v ./backend:/app api pytest api_llm/tests/ -v

```

### Option 2: Run via a dedicated test image (Standalone Docker)

From the repository root, you can build an isolated test image that does not touch `visionmetrics_base_image:latest` or your compose dev images:

```bash
# 1. Build base with dev dependencies (pytest)
docker build -f backend/Dockerfile.base --target dev \
    -t visionmetrics_base_image:test backend

# 2. Build API image on top of it
docker build -f backend/Dockerfile.api \
    --build-context visionmetrics_base_image:latest=docker-image://visionmetrics_base_image:test \
    -t visionmetrics_api:test backend

# 3. Run tests
docker run --rm -v "$PWD/backend:/app" visionmetrics_api:test \
    pytest api_llm/tests/ -v

```

> **How it works:** `--build-context base_image=...` replaces `FROM base_image` in `Dockerfile.api` with the freshly built `:test` image, mirroring how Compose handles `additional_contexts`.

### Option 3: Run locally on the host (Python virtual environment)

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/config/requirements_base.txt -r backend/config/requirements_api.txt

PYTHONPATH=backend pytest backend/api_llm/tests/ -v

```

### Running a specific test file or test case

```bash
# Run only attack & evaluation regression tests
PYTHONPATH=backend pytest backend/api_llm/tests/test_attacks_and_evaluation.py -v

# Run only chat ModelManager tests (Docker example)
docker run --rm -v "$PWD/backend:/app" visionmetrics_api:test \
    pytest api_llm/tests/test_model_manager.py -v

```

### Docker Test Tips & Nuances

* **Code Mount (`-v`):** Without `-v`, tests run against the static code baked into the image during build time (`COPY . .`). With `-v`, your current local code is mounted directly, meaning you only need to rebuild the image if your requirements change.
* **Fast Rebuilds:** After the initial run, Step 1 is almost instantaneous (`CACHED`) as long as `requirements_base*.txt` remain unchanged.
* **Environment Variables:** If your tests require variables from `.env.*` files, pass them directly into `docker run`:
```bash
docker run --rm --env-file .env.shared --env-file .env.api -v "$PWD/backend:/app" visionmetrics_api:test pytest api_llm/tests/ -v

```


## Project Structure

The backend follows a layered architecture: HTTP handling, business logic, background workers, and domain logic each live in their own place.

```
backend/
├── shared/                          # Code shared by api_cv and api_llm
│   ├── database.py                  # Engine, SessionLocal, Base
│   ├── models.py                    # SQLAlchemy ORM models
│   ├── enums.py
│   ├── dtos.py
│   └── utils/
│
├── api_cv/                          # Computer Vision API
│
└── api_llm/                         # LLM API
    ├── main.py                      # FastAPI app, router registration
    ├── celery_app.py                # Single source of Celery config and task routing
    ├── queues.py                    # Constants for Celery task and queue names
    │
    ├── routers/                     # HTTP layer only: parse request, call service, return response
    │   ├── attacks.py
    │   ├── lora_adapters.py
    │   ├── judges.py
    │   └── ...
    │
    ├── schemas/                     # Pydantic request/response models
    │   └── attacks.py
    │
    ├── services/                    # Business logic invoked by routers
    │   ├── attack_service.py
    │   ├── evaluation_queue_service.py   # Dispatching tasks to Celery
    │   ├── judge_task_runs_services.py
    │   └── ...
    │
    ├── workers/                     # Thin Celery tasks: engine.dispose() + call domain logic
    │   ├── attacks/
    │   │   ├── attack_worker.py # attack.generate
    │   │   └── judge_worker.py      # attack.judge
    │   └── ...                      # llm.evaluation, llm.judge.evaluation, chat.generate_text
    │
    ├── attacks/                     # Attack domain logic (no HTTP, no Celery)
    │   ├── attack_library.py        # Scenario generation (intents, techniques, languages)
    │   └── attack_scoring.py        # Canary check, judge prompt, ASR aggregation
    ├── evaluation/                  # Generation, inference, result building
    ├── judge/                       # LLM-as-a-Judge: inference, model loading, task logic
    ├── lora/                        # LoRA adapter loading and management
    ├── base_model/                  # Base model handling
    └── datasets/                    # Dataset reading and parsing (JSONL, CSV)
```

### Layer responsibilities

| Layer | Location | Responsibility |
|---|---|---|
| HTTP | `routers/`, `schemas/` | Request validation and response shaping. No business logic. |
| Business logic | `services/` | Orchestration: DB operations, validation, task dispatching. |
| Background tasks | `workers/` | Thin Celery wrappers. They call domain logic and handle infrastructure errors. |
| Domain logic | `attacks/`, `evaluation/`, `judge/`, `lora/`, `datasets/` | Core algorithms. Independent of HTTP and Celery. |
| Shared | `shared/` | ORM models, enums, DTOs, and utilities used by all services. |

---

## Celery Tasks and Queues

All task and queue names are defined once in `api_llm/queues.py` and routed in `api_llm/celery_app.py`. Do not hardcode them elsewhere.

| Task | Queue | Purpose |
|---|---|---|
| `llm.evaluation` | `llm_tasks` | Text generation for a dataset or prompt |
| `llm.judge.evaluation` | `judge_tasks` | LLM-as-a-Judge scoring for regular evaluations |
| `attack.generate` | `attack_generation_tasks` | Generating model responses to attack prompts |
| `attack.judge` | `attack_judge_tasks` | Canary check, LLM-judge scoring, and ASR computation |
| `chat.generate_text` | `chat_tasks` | Chat completions |

Each queue must have a worker listening to it, for example:

```bash
celery -A api_llm.celery_app worker -Q attack_generation_tasks -c 1
celery -A api_llm.celery_app worker -Q attack_judge_tasks -c 1
```

Tasks sent to a queue without a running worker will remain pending in Redis.

### Attack evaluation flow

1. `POST /attacks/datasets` generates a JSONL dataset of attack scenarios (intent × technique × language).
2. `POST /attacks/runs` creates an evaluation task and dispatches `attack.generate`, followed by one `attack.judge` task per selected judge.
3. `GET /attacks/runs/{task_id}/summary` returns the Attack Success Rate (ASR), overall and broken down by metric category, attack technique, and language.