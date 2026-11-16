from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env"
    )

    database_url: str
    secret_token: str
    jwt_algorithm: str
    access_token_ttl: int
    refresh_token_ttl: int

settings = Settings()   # pyright: ignore[reportCallIssue]