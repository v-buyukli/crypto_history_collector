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

# 4. Install poetry
RUN pip install poetry

# 5. Copy dependency files
COPY poetry.lock pyproject.toml ./

# 6. Install dependencies
RUN poetry install --only main --no-root

# 7. Copy source code
COPY src/ ./src/
