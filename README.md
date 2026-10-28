# vision-metrics

A comprehensive system for evaluating Computer Vision models. This project utilizes Docker containerization to manage the API, background workers (Celery), database, and message broker (Redis).

## 🛠 Prerequisites

To deploy and develop locally, you will need the following installed on your machine:
* [Docker](https://docs.docker.com/get-docker/)
* [Docker Compose](https://docs.docker.com/compose/install/)

---

## 🚀 Quick Start

The following commands will help you build and start all the necessary services.

**1. Build the base image:**
Before running the project for the first time, or if you modify system dependencies, build the base Docker image:
```bash
sudo docker compose --profile setup build base_image

```

**2. Start the containers:**
Build and start all services in detached (background) mode:

```bash
sudo docker compose up -d --build

```

*Once completed, your API, Celery workers, Database, and Redis will be up and running.*

---

## 🗄️ Database Migrations (Alembic)

We use Alembic to manage database schema changes. All commands must be executed inside the `visionmetrics_api_cv` container.

**Generate a new migration (Autogenerate):**
Whenever you update your database models, generate a new migration file:

```bash
docker exec -it visionmetrics_api_cv alembic revision --autogenerate -m "describe_your_changes_here"

```

*(Note: For the very first setup, use `-m "initial_setup"`).*

**Apply migrations:**
To update your database to the latest schema version, run:

```bash
docker exec -it visionmetrics_api_cv alembic upgrade head

```

**Sync migrations to your local machine:**
Because the migration files are generated inside the Docker container, you must copy them to your local host to commit them to your Git history:

```bash
docker cp visionmetrics_api_cv:/app/migrations/versions/. ./backend/migrations/versions/

```


## 🔧 Useful Commands

**Clear Redis Cache / Flush Celery Queues:**
If you ever need to purge all pending background tasks or clear the cache entirely, you can flush the Redis database using this command:

```bash
docker exec -it visionmetrics_redis redis-cli flushall

```


docker exec -it visionmetrics_api_cv alembic revision --autogenerate -m "Initial migration after rebuild"


## 📁 Host Directory Setup

Before starting the containers or uploading files, you need to create the necessary directories on your host machine to ensure proper data persistence for models, datasets, and cache.

Run the following commands to create these folders and grant the necessary read/write permissions:

```bash
sudo mkdir -p /mnt/data/visionmetrics/uploaded_models
sudo mkdir -p /mnt/data/visionmetrics/extracted_datasets
sudo mkdir -p /mnt/data/visionmetrics/model_cache

sudo chmod -R 777 /mnt/data/visionmetrics
```