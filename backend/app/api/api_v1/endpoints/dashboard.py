"""
Dashboard API endpoints for ViperMind
"""

from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.auth import get_current_active_user
from app.db.base import get_db
from app.models.user import User
from app.services.analytics import AnalyticsService

router = APIRouter()

@router.get("/")
def get_user_dashboard(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get comprehensive dashboard data for the current user"""
    
    try:
        analytics_service = AnalyticsService(db)
        dashboard_data = analytics_service.get_user_dashboard_data(str(current_user.id))
        
        if "error" in dashboard_data:
            raise HTTPException(status_code=404, detail=dashboard_data["error"])
        
        return dashboard_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating dashboard: {str(e)}")

@router.get("/stats")
def get_user_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get user statistics summary"""
    
    try:
        analytics_service = AnalyticsService(db)
        dashboard_data = analytics_service.get_user_dashboard_data(str(current_user.id))
        
        # Return just the stats portion
        return {
            "overall_stats": dashboard_data.get("overall_stats", {}),
            "achievements": dashboard_data.get("achievements", {}),
            "performance_trends": dashboard_data.get("performance_trends", {})
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting user stats: {str(e)}")

@router.get("/insights")
def get_learning_insights(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get AI-generated learning insights and recommendations"""
    
    try:
        analytics_service = AnalyticsService(db)
        dashboard_data = analytics_service.get_user_dashboard_data(str(current_user.id))
        
        return {
            "learning_insights": dashboard_data.get("learning_insights", []),
            "recommendations": dashboard_data.get("recommendations", [])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting insights: {str(e)}")

@router.get("/activity")
def get_recent_activity(
    days: int = 7,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get recent learning activity"""
    
    try:
        analytics_service = AnalyticsService(db)
        dashboard_data = analytics_service.get_user_dashboard_data(str(current_user.id))
        
        return {
            "recent_activity": dashboard_data.get("recent_activity", []),
            "days": days
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting activity: {str(e)}")