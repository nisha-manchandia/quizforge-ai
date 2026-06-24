from pydantic_settings import BaseSettings
class Settings(BaseSettings):
    app_name: str = "QuizForge AI"
    debug: bool = False
    secret_key: str = "changethisinproduction"
    database_url: str = "postgresql://postgres:password@localhost:5432/quizforge"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    openai_api_key: str = ""

    class Config:
        env_file = ".env"

settings = Settings()