from functools import lru_cache
from typing import List
import secrets

from pydantic import Field, AliasChoices
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_env: str = Field(default="development")
    database_url: str = Field(default="sqlite:///./workout.db")
    jwt_secret: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        validation_alias=AliasChoices("SECRET_KEY", "JWT_SECRET"),
    )
    jwt_algorithm: str = Field(
        default="HS256",
        validation_alias=AliasChoices("ALGORITHM", "JWT_ALGORITHM"),
    )
    access_token_exp_minutes: int = Field(
        default=15,
        validation_alias=AliasChoices("ACCESS_TOKEN_EXPIRE_MINUTES", "ACCESS_TOKEN_EXP_MINUTES"),
    )
    refresh_token_exp_days: int = Field(
        default=7,
        validation_alias=AliasChoices("REFRESH_TOKEN_EXPIRE_DAYS", "REFRESH_TOKEN_EXP_DAYS"),
    )
    cors_allow_origins: List[str] = Field(default_factory=lambda: ["*"])

    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
    }


@lru_cache()
def get_settings() -> "Settings":
    return Settings()


settings = get_settings()


