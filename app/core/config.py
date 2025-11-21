from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENVIRONMENT: str = "dev"
    APP_NAME: str = "fastapi template project"
    DEBUG: bool = True
    # mysql
    MYSQL_URL: str = "mysql+pymysql://root:123456789@localhost:3306/test_db?charset=utf8mb4"
    CORS_ORIGINS: str = "*"

    # openai
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_MODEL: str = "gpt-3.5-turbo"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

settings = Settings()
