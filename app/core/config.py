from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "fastapi template project"
    DEBUG: bool = True
    # mysql
    MYSQL_URL: str = "mysql+pymysql://root:123456789@localhost:3306/test_db?charset=utf8mb4"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

settings = Settings()
