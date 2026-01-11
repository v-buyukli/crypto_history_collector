# Crypto History Collector

FastAPI application for collecting historical cryptocurrency exchange data.

## Running with Docker (Recommended)

The easiest way to run the application is with Docker. Make sure you have Docker and Docker Compose installed.

1.  **Clone the repository.**
2.  **Build and run the services:**
    ```bash
    docker compose up --build
    ```

This will start both the backend and frontend services.

## Local Development Setup

If you prefer to run the application locally without Docker, follow these steps.

1.  **Clone the repository and create a virtual environment.**
2.  **Install dependencies using Poetry.**
3.  **Run the services:**

    *   **Backend (FastAPI):**
        ```bash
        poetry run uvicorn src.main:app --reload
        ```

    *   **Frontend (Streamlit):**
        ```bash
        poetry run streamlit run src/ui/streamlit_app.py
        ```

## Links

Once the application is running, you can access the services at the following URLs:

### Backend API
- **API Info**: http://localhost:8000/
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Status**: http://localhost:8000/api/status

### Frontend UI
- **Streamlit App**: http://localhost:8501
