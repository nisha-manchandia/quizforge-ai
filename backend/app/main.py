from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.v1 import ping
from app.api.v1 import auth
from app.api.v1 import quizzes

app = FastAPI(
    title=settings.app_name,
    description="AI-powered real-time quiz platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ping.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(quizzes.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "Welcome to QuizForge AI",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}