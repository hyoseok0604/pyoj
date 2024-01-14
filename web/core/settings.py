from pydantic import AmqpDsn, PostgresDsn, RedisDsn, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    postgres_uri: PostgresDsn
    redis_uri: RedisDsn
    rabbitmq_uri: AmqpDsn
    session_key: SecretStr

    env: str = "production"


settings = Settings()  # type: ignore
