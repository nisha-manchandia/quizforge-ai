from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "QuizForge AI"
    debug: bool = False
    secret_key: str = "changethisinproduction"
    database_url: str = "postgresql://postgres:password@localhost:5432/quizforge"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    openai_api_key: str = ""
    gemini_api_key: str = ""
    redis_url: str = "redis://localhost:6379"
    frontend_url: str = "http://localhost:5173"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()