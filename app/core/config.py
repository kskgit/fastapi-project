from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Database
    database_url: str = Field(
        default="postgresql://fastapi_user:fastapi_password@localhost:5432/fastapi_db",
        description="Database connection URL",
    )

    # App
    app_name: str = Field(default="FastAPI Project", description="Application name")
    debug: bool = Field(default=False, description="Debug mode")

    # Server
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


settings = Settings()
