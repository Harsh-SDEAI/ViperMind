"""
Comprehensive monitoring and logging system for ViperMind.
"""

import logging
import json
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
from app.core.cache import cache_manager, CacheKeys

class AlertLevel(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class SystemMetric:
    name: str
    value: float
    unit: str
    timestamp: datetime
    tags: Dict[str, str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value,
            "unit": self.unit,
            "timestamp": self.timestamp.isoformat(),
            "tags": self.tags or {}
        }

@dataclass
class ErrorEvent:
    error_id: str
    error_type: str
    error_code: str
    message: str
    severity: str
    timestamp: datetime
    context: Dict[str, Any]
    resolved: bool = False
    resolution_time: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "error_id": self.error_id,
            "error_type": self.error_type,
            "error_code": self.error_code,
            "message": self.message,
            "severity": self.severity,
            "timestamp": self.timestamp.isoformat(),
            "context": self.context,
            "resolved": self.resolved,
            "resolution_time": self.resolution_time.isoformat() if self.resolution_time else None
        }

@dataclass
class Alert:
    alert_id: str
    level: AlertLevel
    title: str
    description: str
    timestamp: datetime
    acknowledged: bool = False
    resolved: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class SystemMonitor:
    """Monitors system health and performance metrics."""
    
    def __init__(self):
        self.logger = logging.getLogger("vipermind.monitor")
        self.metrics_history: List[SystemMetric] = []
        self.error_events: List[ErrorEvent] = []
        self.alerts: List[Alert] = []
        self.max_history_size = 10000
        
        # Thresholds for alerts
        self.thresholds = {
            "api_response_time": {"warning": 2.0, "critical": 5.0},
            "database_query_time": {"warning": 1.0, "critical": 3.0},
            "ai_response_time": {"warning": 10.0, "critical": 30.0},
            "error_rate": {"warning": 0.05, "critical": 0.1},  # 5% and 10%
            "memory_usage": {"warning": 80.0, "critical": 90.0},  # percentage
            "cpu_usage": {"warning": 80.0, "critical": 90.0},  # percentage
        }
    
    def record_metric(self, name: str, value: float, unit: str, tags: Dict[str, str] = None):
        """Record a system metric."""
        metric = SystemMetric(
            name=name,
            value=value,
            unit=unit,
            timestamp=datetime.utcnow(),
            tags=tags or {}
        )
        
        self.metrics_history.append(metric)
        
        # Maintain history size
        if len(self.metrics_history) > self.max_history_size:
            self.metrics_history = self.metrics_history[-self.max_history_size:]
        
        # Check for threshold violations
        self._check_thresholds(metric)
        
        # Cache recent metrics
        cache_key = cache_manager._generate_key(CacheKeys.ANALYTICS, f"metric:{name}")
        recent_metrics = self.get_recent_metrics(name, minutes=60)
        cache_manager.set(cache_key, [m.to_dict() for m in recent_metrics], 3600)
    
    def record_error(self, error_id: str, error_type: str, error_code: str, 
                    message: str, severity: str, context: Dict[str, Any]):
        """Record an error event."""
        error_event = ErrorEvent(
            error_id=error_id,
            error_type=error_type,
            error_code=error_code,
            message=message,
            severity=severity,
            timestamp=datetime.utcnow(),
            context=context
        )
        
        self.error_events.append(error_event)
        
        # Maintain history size
        if len(self.error_events) > self.max_history_size:
            self.error_events = self.error_events[-self.max_history_size:]
        
        # Check error rate
        self._check_error_rate()
        
        # Log the error
        self.logger.error(f"Error recorded: {error_event.to_dict()}")
    
    def create_alert(self, level: AlertLevel, title: str, description: str) -> str:
        """Create a system alert."""
        alert_id = f"alert_{int(time.time())}_{len(self.alerts)}"
        
        alert = Alert(
            alert_id=alert_id,
            level=level,
            title=title,
            description=description,
            timestamp=datetime.utcnow()
        )
        
        self.alerts.append(alert)
        
        # Log the alert
        log_level = {
            AlertLevel.INFO: logging.INFO,
            AlertLevel.WARNING: logging.WARNING,
            AlertLevel.ERROR: logging.ERROR,
            AlertLevel.CRITICAL: logging.CRITICAL
        }
        
        self.logger.log(log_level[level], f"ALERT [{level.value.upper()}]: {title} - {description}")
        
        return alert_id
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert."""
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                return True
        return False
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert."""
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.resolved = True
                return True
        return False
    
    def get_recent_metrics(self, name: str, minutes: int = 60) -> List[SystemMetric]:
        """Get recent metrics for a specific metric name."""
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        return [
            metric for metric in self.metrics_history
            if metric.name == name and metric.timestamp > cutoff_time
        ]
    
    def get_recent_errors(self, minutes: int = 60) -> List[ErrorEvent]:
        """Get recent error events."""
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        return [
            error for error in self.error_events
            if error.timestamp > cutoff_time
        ]
    
    def get_active_alerts(self) -> List[Alert]:
        """Get active (unresolved) alerts."""
        return [alert for alert in self.alerts if not alert.resolved]
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health status."""
        recent_errors = self.get_recent_errors(60)
        active_alerts = self.get_active_alerts()
        
        # Calculate error rate
        total_requests = len(self.get_recent_metrics("api_response_time", 60))
        error_rate = len(recent_errors) / max(total_requests, 1)
        
        # Determine overall health status
        critical_alerts = [a for a in active_alerts if a.level == AlertLevel.CRITICAL]
        error_alerts = [a for a in active_alerts if a.level == AlertLevel.ERROR]
        
        if critical_alerts:
            status = "critical"
        elif error_alerts or error_rate > 0.1:
            status = "degraded"
        elif len(active_alerts) > 0 or error_rate > 0.05:
            status = "warning"
        else:
            status = "healthy"
        
        return {
            "status": status,
            "error_rate": error_rate,
            "active_alerts": len(active_alerts),
            "critical_alerts": len(critical_alerts),
            "recent_errors": len(recent_errors),
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def _check_thresholds(self, metric: SystemMetric):
        """Check if metric violates thresholds and create alerts."""
        if metric.name not in self.thresholds:
            return
        
        thresholds = self.thresholds[metric.name]
        
        if metric.value >= thresholds.get("critical", float('inf')):
            self.create_alert(
                AlertLevel.CRITICAL,
                f"Critical {metric.name}",
                f"{metric.name} is {metric.value}{metric.unit}, exceeding critical threshold"
            )
        elif metric.value >= thresholds.get("warning", float('inf')):
            self.create_alert(
                AlertLevel.WARNING,
                f"High {metric.name}",
                f"{metric.name} is {metric.value}{metric.unit}, exceeding warning threshold"
            )
    
    def _check_error_rate(self):
        """Check error rate and create alerts if necessary."""
        recent_errors = self.get_recent_errors(60)
        total_requests = len(self.get_recent_metrics("api_response_time", 60))
        
        if total_requests > 0:
            error_rate = len(recent_errors) / total_requests
            
            if error_rate >= 0.1:  # 10%
                self.create_alert(
                    AlertLevel.CRITICAL,
                    "High Error Rate",
                    f"Error rate is {error_rate:.2%}, exceeding critical threshold"
                )
            elif error_rate >= 0.05:  # 5%
                self.create_alert(
                    AlertLevel.WARNING,
                    "Elevated Error Rate",
                    f"Error rate is {error_rate:.2%}, exceeding warning threshold"
                )

class HealthChecker:
    """Performs health checks on system components."""
    
    def __init__(self, monitor: SystemMonitor):
        self.monitor = monitor
        self.logger = logging.getLogger("vipermind.health")
    
    async def check_database_health(self) -> Dict[str, Any]:
        """Check database connectivity and performance."""
        try:
            from app.db.session import engine
            
            start_time = time.time()
            
            # Simple connectivity test
            with engine.connect() as conn:
                result = conn.execute("SELECT 1")
                result.fetchone()
            
            response_time = time.time() - start_time
            
            self.monitor.record_metric("database_health_check", response_time, "seconds")
            
            return {
                "status": "healthy",
                "response_time": response_time,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.monitor.record_error(
                f"db_health_{int(time.time())}",
                "database_error",
                "DB_HEALTH_CHECK_FAILED",
                str(e),
                "critical",
                {"component": "database"}
            )
            
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def check_redis_health(self) -> Dict[str, Any]:
        """Check Redis connectivity and performance."""
        try:
            start_time = time.time()
            
            # Test Redis connectivity
            cache_manager.redis_client.ping()
            
            response_time = time.time() - start_time
            
            self.monitor.record_metric("redis_health_check", response_time, "seconds")
            
            return {
                "status": "healthy",
                "response_time": response_time,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.monitor.record_error(
                f"redis_health_{int(time.time())}",
                "cache_error",
                "REDIS_HEALTH_CHECK_FAILED",
                str(e),
                "warning",
                {"component": "redis"}
            )
            
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def check_ai_service_health(self) -> Dict[str, Any]:
        """Check AI service availability."""
        try:
            from app.agents.tools.openai_tool import OpenAITool
            
            start_time = time.time()
            
            # Simple AI service test
            openai_tool = OpenAITool()
            result = openai_tool.run("test_connection")
            
            response_time = time.time() - start_time
            
            self.monitor.record_metric("ai_service_health_check", response_time, "seconds")
            
            return {
                "status": "healthy" if result.get("success") else "degraded",
                "response_time": response_time,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.monitor.record_error(
                f"ai_health_{int(time.time())}",
                "ai_service_error",
                "AI_HEALTH_CHECK_FAILED",
                str(e),
                "warning",
                {"component": "ai_service"}
            )
            
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def run_full_health_check(self) -> Dict[str, Any]:
        """Run comprehensive health check on all components."""
        health_results = {
            "overall_status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {}
        }
        
        # Check all components
        components = {
            "database": self.check_database_health,
            "redis": self.check_redis_health,
            "ai_service": self.check_ai_service_health
        }
        
        unhealthy_count = 0
        degraded_count = 0
        
        for component_name, check_func in components.items():
            try:
                result = await check_func()
                health_results["components"][component_name] = result
                
                if result["status"] == "unhealthy":
                    unhealthy_count += 1
                elif result["status"] == "degraded":
                    degraded_count += 1
                    
            except Exception as e:
                health_results["components"][component_name] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }
                unhealthy_count += 1
        
        # Determine overall status
        if unhealthy_count > 0:
            health_results["overall_status"] = "unhealthy"
        elif degraded_count > 0:
            health_results["overall_status"] = "degraded"
        
        return health_results

# Global monitor instance
system_monitor = SystemMonitor()
health_checker = HealthChecker(system_monitor)