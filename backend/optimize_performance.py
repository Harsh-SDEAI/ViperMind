#!/usr/bin/env python3
"""
Performance optimization script for ViperMind backend.
Run this script to apply all performance optimizations.
"""

import sys
import os
import logging
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.db.optimization import (
    run_full_optimization,
    refresh_materialized_views,
    optimize_database_settings
)
from app.core.cache import cache_manager
from app.core.performance import optimize_memory_usage, get_performance_report

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Run complete performance optimization."""
    
    logger.info("Starting ViperMind performance optimization...")
    
    try:
        # 1. Database optimization
        logger.info("Step 1: Optimizing database...")
        run_full_optimization()
        logger.info("✓ Database optimization completed")
        
        # 2. Refresh materialized views
        logger.info("Step 2: Refreshing materialized views...")
        refresh_materialized_views()
        logger.info("✓ Materialized views refreshed")
        
        # 3. Test Redis connection
        logger.info("Step 3: Testing Redis cache connection...")
        if cache_manager.redis_client:
            cache_manager.redis_client.ping()
            logger.info("✓ Redis cache connection successful")
        else:
            logger.warning("⚠ Redis cache not available")
        
        # 4. Memory optimization
        logger.info("Step 4: Optimizing memory usage...")
        memory_stats = optimize_memory_usage()
        logger.info(f"✓ Memory optimization completed: {memory_stats}")
        
        # 5. Generate performance report
        logger.info("Step 5: Generating performance report...")
        report = get_performance_report()
        
        print("\n" + "="*60)
        print("PERFORMANCE OPTIMIZATION SUMMARY")
        print("="*60)
        
        if 'system_metrics' in report:
            metrics = report['system_metrics']
            print(f"CPU Usage: {metrics.get('cpu_usage', 0):.1f}%")
            print(f"Memory Usage: {metrics.get('memory_usage', 0):.1f}%")
            print(f"Available Memory: {metrics.get('memory_available_gb', 0):.1f} GB")
            print(f"Disk Usage: {metrics.get('disk_usage', 0):.1f}%")
            print(f"Free Disk Space: {metrics.get('disk_free_gb', 0):.1f} GB")
        
        if 'cache_stats' in report:
            cache_stats = report['cache_stats']
            print(f"Redis Connected: {cache_stats.get('redis_connected', False)}")
            print(f"Cache Hit Rate: {cache_stats.get('cache_hit_rate', 0):.1f}%")
        
        print("\n✓ Performance optimization completed successfully!")
        
        # Recommendations
        print("\nRECOMMENDations:")
        if report.get('system_metrics', {}).get('memory_usage', 0) > 80:
            print("- Consider increasing available memory")
        if report.get('system_metrics', {}).get('cpu_usage', 0) > 80:
            print("- Consider scaling to more CPU cores")
        if not report.get('cache_stats', {}).get('redis_connected', False):
            print("- Set up Redis for improved caching performance")
        
        print("- Run this optimization script regularly for best performance")
        print("- Monitor performance metrics in production")
        
    except Exception as e:
        logger.error(f"Performance optimization failed: {e}")
        print(f"\n❌ Optimization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()