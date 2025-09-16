from dotenv import load_dotenv
load_dotenv()  # Load environment variables

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.api_v1.api import api_router

app = FastAPI(
    title="ViperMind API",
    description="AI-powered Python tutoring platform",
    version="1.0.0"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "ViperMind API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ViperMind API"}

@app.options("/{full_path:path}")
async def options_handler():
    return {"message": "OK"}