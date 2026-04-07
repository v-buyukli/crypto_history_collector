# Crypto History Collector

FastAPI application for collecting historical cryptocurrency OHLCV data (klines/candles) from exchanges into a PostgreSQL database.

**Supported exchanges:** Binance, Bybit
**Supported market types:** spot, futures
**Supported timeframes:** 1h, 4h, 1d

## Running with Docker

1. **Clone the repository.**
2. **Create `.env` from the example:**
    ```bash
    cp .env.example .env
    ```
    Edit `.env` if needed.
3. **Build and run the services:**
    ```bash
    docker compose up --build
    ```

This will start the database, backend, and frontend services.

## Access

| Service | URL |
|---------|-----|
| Backend API info | http://localhost:8000/ |
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| Streamlit frontend | http://localhost:8501 |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/symbols` | List symbols from database |
| POST | `/api/v1/symbols/sync` | Sync symbols from exchange API |
| POST | `/api/v1/klines/import` | Import historical klines from exchange API |
