FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /frontend
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /frontend

RUN pip install poetry

COPY pyproject.toml poetry.lock ./

RUN poetry install --only main --no-root

COPY app/ ./app/
COPY static/ ./static/
COPY .streamlit/ ./.streamlit/

CMD ["poetry", "run", "streamlit", "run", "app/streamlit_app.py"]
