# Crypto History Collector

FastAPI application for collecting historical cryptocurrency exchange data.

## Setup & Run

- clone repository
- create and activate virtual environment (poetry)
- `poetry install`

### Backend (FastAPI)
```bash
poetry run uvicorn src.main:app --reload
```

### Frontend (Streamlit)
```bash
poetry run streamlit run src/ui/streamlit_app.py
```

## Links

### Backend API
- **API Info**: http://localhost:8000/
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Status**: http://localhost:8000/api/status

### Frontend UI
- **Streamlit App**: http://localhost:8501

## Notes

- Backend и Frontend запускаются независимо
- Запустите оба сервиса в разных терминалах
- Backend должен быть запущен, если Frontend обращается к API
