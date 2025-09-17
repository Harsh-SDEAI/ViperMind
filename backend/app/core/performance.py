"""
Performance monitoring and optimization utilities.
"""
import time
import functools
import logging
from typing import Any, Callable, Dict, Optional
from contextlib import contextmanager
from app.core.cache import cache_manager, CacheKeys
import psutil
import asyncio

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Monitor and track performance metrics."""
    
    def __init__(self):
        self.metrics = {}
        self.thresholds = {
            'api_response_time': 2.0,  # seconds
            'database_query_time': 1.0,  # seconds
            'ai_response_time': 10.0,  # seconds
            'memory_usage': 80.0,  # percentage
            'cpu_usage': 80.0,  # percentage
        }
    
    def record_metric(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Record a performance metric."""
        timestamp = time.time()
        
        if name not in self.metrics:
            self.metrics[name] = []
        
        self.metrics[name].append({
            'value': value,
            'timestamp': timestamp,
            'tags': tags or {}
        })
        
        # Keep only last 1000 entries per metric
        if len(self.metrics[name]) > 1000:
            self.metrics[name] = self.metrics[name][-1000:]
        
        # Check thresholds
        if name in self.thresholds and value > self.thresholds[name]:
            logger.warning(f"Performance threshold exceeded for {name}: {value} > {self.thresholds[name]}")
    
    def get_metrics_summary(self, name: str, window_minutes: int = 60) -> Dict[str, float]:
        """Get summary statistics for a metric within a time window."""
        if name not in self.metrics:
            return {}
        
        cutoff_time = time.time() - (window_minutes * 60)
        recent_values = [
            m['value'] for m in self.metrics[name] 
            if m['timestamp'] > cutoff_time
        ]
        
        if not recent_values:
            return {}
        
        return {
            'count': len(recent_values),
            'avg': sum(recent_values) / len(recent_values),
            'min': min(recent_values),
            'max': max(recent_values),
            'p95': sorted(recent_values)[int(len(recent_values) * 0.95)] if len(recent_values) > 1 else recent_values[0]
        }
    
    def get_system_metrics(self) -> Dict[str, float]:
        """Get current system performance metrics."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_usage': cpu_percent,
                'memory_usage': memory.percent,
                'memory_available_gb': memory.available / (1024**3),
                'disk_usage': disk.percent,
                'disk_free_gb': disk.free / (1024**3)
            }
        except Exception as e:
            logger.error(f"Failed to get system metrics: {e}")
            return {}


# Global performance monitor instance
perf_monitor = PerformanceMonitor()


def measure_time(metric_name: str, tags: Optional[Dict[str, str]] = None):
    """Decorator to measure execution time of functions."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                execution_time = time.time() - start_time
                perf_monitor.record_metric(metric_name, execution_time, tags)
                
                if execution_time > 5.0:  # Log slow operations
                    logger.warning(f"Slow operation detected: {func.__name__} took {execution_time:.2f}s")
        
        return wrapper
    return decorator


def measure_async_time(metric_name: str, tags: Optional[Dict[str, str]] = None):
    """Decorator to measure execution time of async functions."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                execution_time = time.time() - start_time
                perf_monitor.record_metric(metric_name, execution_time, tags)
                
                if execution_time > 5.0:
                    logger.warning(f"Slow async operation detected: {func.__name__} took {execution_time:.2f}s")
        
        return wrapper
    return decorator


@contextmanager
def measure_block(metric_name: str, tags: Optional[Dict[str, str]] = None):
    """Context manager to measure execution time of code blocks."""
    start_time = time.time()
    try:
        yield
    finally:
        execution_time = time.time() - start_time
        perf_monitor.record_metric(metric_name, execution_time, tags)


class DatabaseQueryOptimizer:
    """Optimize database queries and track performance."""
    
    @staticmethod
    def optimize_query_with_cache(query_key: str, query_func: Callable, ttl: int = 300):
        """Execute query with caching optimization."""
        
        # Try cache first
        cache_key = cache_manager._generate_key(CacheKeys.ANALYTICS, f"query:{query_key}")
        cached_result = cache_manager.get(cache_key)
        
        if cached_result is not None:
            perf_monitor.record_metric('database_query_time', 0.001, {'source': 'cache'})
            return cached_result
        
        # Execute query with timing
        start_time = time.time()
        try:
            result = query_func()
            query_time = time.time() - start_time
            
            # Cache the result
            cache_manager.set(cache_key, result, ttl)
            
            # Record metrics
            perf_monitor.record_metric('database_query_time', query_time, {'source': 'database'})
            
            return result
            
        except Exception as e:
            query_time = time.time() - start_time
            perf_monitor.record_metric('database_query_time', query_time, {'source': 'database', 'error': True})
            raise


class AIResponseOptimizer:
    """Optimize AI agent responses with caching and performance tracking."""
    
    @staticmethod
    def optimize_ai_call(context_key: str, ai_func: Callable, ttl: int = 3600):
        """Execute AI call with caching and performance optimization."""
        
        # Try cache first
        cache_key = cache_manager._generate_key(CacheKeys.AI_CONTEXT, context_key)
        cached_result = cache_manager.get(cache_key)
        
        if cached_result is not None:
            perf_monitor.record_metric('ai_response_time', 0.001, {'source': 'cache'})
            return cached_result
        
        # Execute AI call with timing
        start_time = time.time()
        try:
            result = ai_func()
            response_time = time.time() - start_time
            
            # Cache successful results
            if result and not result.get('error'):
                cache_manager.set(cache_key, result, ttl)
            
            # Record metrics
            perf_monitor.record_metric('ai_response_time', response_time, {'source': 'openai'})
            
            return result
            
        except Exception as e:
            response_time = time.time() - start_time
            perf_monitor.record_metric('ai_response_time', response_time, {'source': 'openai', 'error': True})
            raise


def optimize_memory_usage():
    """Perform memory optimization tasks."""
    try:
        import gc
        
        # Force garbage collection
        collected = gc.collect()
        
        # Get memory info
        memory_info = psutil.virtual_memory()
        
        logger.info(f"Memory optimization: collected {collected} objects, "
                   f"memory usage: {memory_info.percent}%")
        
        # Record metric
        perf_monitor.record_metric('memory_usage', memory_info.percent)
        
        return {
            'objects_collected': collected,
            'memory_percent': memory_info.percent,
            'memory_available_gb': memory_info.available / (1024**3)
        }
        
    except Exception as e:
        logger.error(f"Memory optimization failed: {e}")
        return {}


def get_performance_report() -> Dict[str, Any]:
    """Generate a comprehensive performance report."""
    try:
        report = {
            'timestamp': time.time(),
            'system_metrics': perf_monitor.get_system_metrics(),
            'api_performance': perf_monitor.get_metrics_summary('api_response_time'),
            'database_performance': perf_monitor.get_metrics_summary('database_query_time'),
            'ai_performance': perf_monitor.get_metrics_summary('ai_response_time'),
            'cache_stats': {
                'redis_connected': cache_manager.redis_client is not None,
                'cache_hit_rate': _calculate_cache_hit_rate(),
            }
        }
        
        return report
        
    except Exception as e:
        logger.error(f"Failed to generate performance report: {e}")
        return {'error': str(e)}


def _calculate_cache_hit_rate() -> float:
    """Calculate cache hit rate from metrics."""
    try:
        db_metrics = perf_monitor.metrics.get('database_query_time', [])
        ai_metrics = perf_monitor.metrics.get('ai_response_time', [])
        
        # Count cache hits vs database/AI calls
        cache_hits = 0
        total_calls = 0
        
        for metric in db_metrics[-100:]:  # Last 100 calls
            total_calls += 1
            if metric.get('tags', {}).get('source') == 'cache':
                cache_hits += 1
        
        for metric in ai_metrics[-100:]:
            total_calls += 1
            if metric.get('tags', {}).get('source') == 'cache':
                cache_hits += 1
        
        return (cache_hits / total_calls * 100) if total_calls > 0 else 0.0
        
    except Exception:
        return 0.0


# Middleware for automatic performance monitoring
class PerformanceMiddleware:
    """FastAPI middleware for automatic performance monitoring."""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        start_time = time.time()
        
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                response_time = time.time() - start_time
                
                # Record API response time
                path = scope.get("path", "unknown")
                method = scope.get("method", "unknown")
                
                perf_monitor.record_metric(
                    'api_response_time',
                    response_time,
                    {'path': path, 'method': method}
                )
            
            await send(message)
        
        await self.app(scope, receive, send_wrapper)