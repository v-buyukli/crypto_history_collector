from dotenv import load_dotenv
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


load_dotenv()


class Settings(BaseSettings):
    # FastAPI
    FASTAPI_HOST: str = Field(default="localhost")
    FASTAPI_PORT: int = Field(default=8000)
    FASTAPI_SCHEME: str = Field(default="http")

    # Streamlit
    STREAMLIT_HOST: str = Field(default="localhost")
    STREAMLIT_PORT: int = Field(default=8501)
    STREAMLIT_SCHEME: str = Field(default="http")

    # PostgreSQL
    POSTGRES_USER: str = Field(default="postgres")
    POSTGRES_PASSWORD: str = Field(default="postgres")
    POSTGRES_DB: str = Field(default="crypto_history")
    POSTGRES_HOST: str = Field(default="localhost")
    POSTGRES_PORT: int = Field(default=5432)

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @computed_field
    @property
    def fastapi_url(self) -> str:
        return f"{self.FASTAPI_SCHEME}://{self.FASTAPI_HOST}:{self.FASTAPI_PORT}"

    @computed_field
    @property
    def database_url(self) -> str:
        return f"postgresql+pg8000://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"  # noqa: E501


settings = Settings()
