from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "QuizForge AI"
    debug: bool = False
    secret_key: str = "changethisinproduction"
    database_url: str = "postgresql://postgres.nfrzfkxjvpwwryvpvqvt:Nikita%25400225MAN@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    openai_api_key: str = ""
    gemini_api_key: str = ""
    redis_url: str = "rediss://default:gQAAAAAAAlURAAIgcDJjYTJhMTg4ZDUyNWU0ZWE3YmZhYWY4ZmMwNWQ5M2ZiNQ@modern-sparrow-152849.upstash.io:6379"
    frontend_url: str = "https://nisha-manchandia.github.io"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()