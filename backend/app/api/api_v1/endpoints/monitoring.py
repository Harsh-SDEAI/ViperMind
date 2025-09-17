"""
Monitoring and health check API endpoints.
"""

from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime, timedelta
from app.core.monitoring import system_monitor, health_checker
from app.core.auth import get_current_active_user
from app.models.user import User
from pydantic import BaseModel

router = APIRouter()

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    components: Dict[str, Any]

class MetricsResponse(BaseModel):
    metrics: List[Dict[str, Any]]
    summary: Dict[str, Any]

class AlertsResponse(BaseModel):
    alerts: List[Dict[str, Any]]
    total_count: int
    active_count: int

@router.get("/health", response_model=HealthResponse)
async def get_system_health():
    """Get comprehensive system health status."""
    try:
        health_status = await health_checker.run_full_health_check()
        return HealthResponse(**health_status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@router.get("/health/quick")
async def get_quick_health():
    """Get quick health status without detailed checks."""
    try:
        health_status = system_monitor.get_system_health()
        return health_status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quick health check failed: {str(e)}")

@router.get("/metrics", response_model=MetricsResponse)
async def get_system_metrics(
    metric_name: str = Query(None, description="Filter by metric name"),
    minutes: int = Query(60, description="Time window in minutes"),
    current_user: User = Depends(get_current_active_user)
):
    """Get system metrics for monitoring."""
    try:
        if metric_name:
            metrics = system_monitor.get_recent_metrics(metric_name, minutes)
        else:
            # Get all recent metrics
            cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
            metrics = [
                metric for metric in system_monitor.metrics_history
                if metric.timestamp > cutoff_time
            ]
        
        # Calculate summary statistics
        summary = {}
        if metrics:
            values = [m.value for m in metrics]
            summary = {
                "count": len(values),
                "avg": sum(values) / len(values),
                "min": min(values),
                "max": max(values),
                "latest": values[-1] if values else None
            }
        
        return MetricsResponse(
            metrics=[m.to_dict() for m in metrics],
            summary=summary
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")

@router.get("/alerts", response_model=AlertsResponse)
async def get_system_alerts(
    active_only: bool = Query(True, description="Show only active alerts"),
    current_user: User = Depends(get_current_active_user)
):
    """Get system alerts."""
    try:
        if active_only:
            alerts = system_monitor.get_active_alerts()
        else:
            alerts = system_monitor.alerts
        
        return AlertsResponse(
            alerts=[a.to_dict() for a in alerts],
            total_count=len(system_monitor.alerts),
            active_count=len(system_monitor.get_active_alerts())
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get alerts: {str(e)}")

@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Acknowledge a system alert."""
    try:
        success = system_monitor.acknowledge_alert(alert_id)
        if not success:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        return {"success": True, "message": "Alert acknowledged"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to acknowledge alert: {str(e)}")

@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Resolve a system alert."""
    try:
        success = system_monitor.resolve_alert(alert_id)
        if not success:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        return {"success": True, "message": "Alert resolved"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to resolve alert: {str(e)}")

@router.get("/errors")
async def get_recent_errors(
    minutes: int = Query(60, description="Time window in minutes"),
    current_user: User = Depends(get_current_active_user)
):
    """Get recent error events."""
    try:
        errors = system_monitor.get_recent_errors(minutes)
        
        return {
            "errors": [e.to_dict() for e in errors],
            "count": len(errors),
            "time_window_minutes": minutes
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get errors: {str(e)}")

@router.get("/performance")
async def get_performance_summary(
    current_user: User = Depends(get_current_active_user)
):
    """Get performance summary across all metrics."""
    try:
        # Get recent metrics for key performance indicators
        api_metrics = system_monitor.get_recent_metrics("api_response_time", 60)
        db_metrics = system_monitor.get_recent_metrics("database_query_time", 60)
        ai_metrics = system_monitor.get_recent_metrics("ai_response_time", 60)
        
        def calculate_stats(metrics):
            if not metrics:
                return {"count": 0, "avg": 0, "min": 0, "max": 0, "p95": 0}
            
            values = [m.value for m in metrics]
            values.sort()
            
            return {
                "count": len(values),
                "avg": sum(values) / len(values),
                "min": min(values),
                "max": max(values),
                "p95": values[int(len(values) * 0.95)] if len(values) > 1 else values[0]
            }
        
        return {
            "api_performance": calculate_stats(api_metrics),
            "database_performance": calculate_stats(db_metrics),
            "ai_performance": calculate_stats(ai_metrics),
            "system_health": system_monitor.get_system_health(),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance summary: {str(e)}")

@router.get("/status")
async def get_service_status():
    """Get basic service status (public endpoint)."""
    try:
        health = system_monitor.get_system_health()
        
        return {
            "service": "ViperMind API",
            "status": health["status"],
            "timestamp": health["last_updated"],
            "version": "1.0.0"  # You can make this dynamic
        }
        
    except Exception as e:
        return {
            "service": "ViperMind API",
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }