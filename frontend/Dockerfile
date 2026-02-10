FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /frontend

WORKDIR /frontend

RUN pip install poetry

COPY pyproject.toml ./

RUN poetry install --only main --no-root

COPY app/ ./app/
COPY static/ ./static/
COPY .streamlit/ ./.streamlit/

CMD ["poetry", "run", "streamlit", "run", "app/streamlit_app.py"]
