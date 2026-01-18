# 1. Base Image
FROM python:3.12-slim

# 2. Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=false
ENV PYTHONPATH /app

# 3. Set working directory
WORKDIR /app

# 4. Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 5. Install poetry
RUN pip install poetry

# 6. Copy dependency files
COPY poetry.lock pyproject.toml ./

# 7. Install dependencies
RUN poetry install --only main --no-root

# 8. Copy source code
COPY src/ ./src/

# 9. Copy alembic for migrations
COPY alembic.ini ./
COPY alembic/ ./alembic/

# 10. Copy and setup entrypoint
COPY entrypoint.sh ./
RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
