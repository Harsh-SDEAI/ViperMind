from fastapi import APIRouter
from app.api.api_v1.endpoints import auth, users, agents, curriculum, lessons, assessments, progress, remedial, dashboard, personalization

api_router = APIRouter()

# Include authentication routes
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

# Include user management routes
api_router.include_router(users.router, prefix="/users", tags=["users"])

# Include AI agent routes
api_router.include_router(agents.router, prefix="/agents", tags=["ai-agents"])

# Include curriculum routes
api_router.include_router(curriculum.router, prefix="/curriculum", tags=["curriculum"])

# Include lesson routes
api_router.include_router(lessons.router, prefix="/lessons", tags=["lessons"])

# Include assessment routes
api_router.include_router(assessments.router, prefix="/assessments", tags=["assessments"])

# Include progress routes
api_router.include_router(progress.router, prefix="/progress", tags=["progress"])

# Include remedial content routes
api_router.include_router(remedial.router, prefix="/remedial", tags=["remedial"])

# Include dashboard routes
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])

# Include personalization routes
api_router.include_router(personalization.router, prefix="/personalization", tags=["personalization"])

@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "message": "ViperMind API is running"}