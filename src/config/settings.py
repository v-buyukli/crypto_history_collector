"""Application configuration settings."""

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Environment
    ENVIRONMENT: str = "development"

    # FastAPI settings
    FASTAPI_HOST: str = "localhost"
    FASTAPI_PORT: int = 8000
    FASTAPI_SCHEME: str = "http"

    # Streamlit settings
    STREAMLIT_HOST: str = "localhost"
    STREAMLIT_PORT: int = 8501
    STREAMLIT_SCHEME: str = "http"

    @computed_field  # type: ignore[misc]
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT == "production"

    @computed_field  # type: ignore[misc]
    @property
    def fastapi_url(self) -> str:
        """Get FastAPI base URL with proper scheme."""
        return f"{self.FASTAPI_SCHEME}://{self.FASTAPI_HOST}:{self.FASTAPI_PORT}"

    @computed_field  # type: ignore[misc]
    @property
    def streamlit_url(self) -> str:
        """Get Streamlit base URL with proper scheme."""
        return f"{self.STREAMLIT_SCHEME}://{self.STREAMLIT_HOST}:{self.STREAMLIT_PORT}"


settings = Settings()
