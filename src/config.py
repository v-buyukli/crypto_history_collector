from dotenv import load_dotenv
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    FASTAPI_HOST: str = Field(default="localhost")
    FASTAPI_PORT: int = Field(default=8000)
    FASTAPI_SCHEME: str = Field(default="http")

    STREAMLIT_HOST: str = Field(default="localhost")
    STREAMLIT_PORT: int = Field(default=8501)
    STREAMLIT_SCHEME: str = Field(default="http")

    model_config = SettingsConfigDict()

    @computed_field
    @property
    def fastapi_url(self) -> str:
        return f"{self.FASTAPI_SCHEME}://{self.FASTAPI_HOST}:{self.FASTAPI_PORT}"


settings = Settings()
