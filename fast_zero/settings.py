from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int


# Instância única usada no projeto todo. Os valores vêm das variáveis de
# ambiente / .env, por isso o Pyright não os vê como argumentos.
settings = Settings()  # pyright: ignore[reportCallIssue]
